#!/usr/bin/env python3
"""
DevOpsHeroCLI - AI Pull Request Reviewer
Audits code changes across all languages for:
- 🔒 AppSec (OWASP Top 10, Secrets, Injections, Privilege Escalation)
- 📐 Code Quality & Best Practices (Clean Code, Idiomatic Patterns, Error Handling)
- 🌿 Git & GitHub Standards (Conventional Commits, Scope Integrity, Documentation)

Supports Google Gemini API (Free tier) and OpenAI API.
"""

import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import List, Optional

COMMENT_TAG = "<!-- devopshero-ai-reviewer -->"


def get_pr_diff(base_ref: str) -> str:
    """Extracts git diff against the target base branch."""
    # Ensure base ref is fetched
    try:
        subprocess.run(["git", "fetch", "origin", base_ref, "--depth=100"], check=False, capture_output=True)
    except Exception:
        pass

    diff_targets = [
        f"origin/{base_ref}...HEAD",
        f"origin/{base_ref}",
        "HEAD~1",
        "HEAD",
    ]

    for target in diff_targets:
        try:
            cmd = ["git", "diff", target]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            if res.stdout.strip():
                return res.stdout
        except Exception:
            continue

    return ""


def get_commit_messages(base_ref: str) -> List[str]:
    """Gets list of commit messages in this PR."""
    try:
        res = subprocess.run(
            ["git", "log", f"origin/{base_ref}..HEAD", "--oneline"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [line.strip() for line in res.stdout.splitlines() if line.strip()]
    except Exception:
        return []


def build_system_prompt() -> str:
    return """Você é o **DevOpsHero AI Code Reviewer**, um Engenheiro Principal Especialista em AppSec, SRE e Arquitetura de Software.
Sua missão é realizar uma revisão de código de nível sênior em Pull Requests, avaliando com rigor:

1. 🔒 **SEGURANÇA (AppSec / DevSecOps - Prioridade Máxima)**:
   - Detecção de credenciais, chaves de API, senhas ou tokens expostos.
   - Injeção de comandos (Shell injection), SQL Injection, Path Traversal e Execução insegura de subprocessos.
   - Permissões excessivas (ex: arquivos com chmod 777, contêineres rodando como root desnecessariamente).
   - Inseguranças de rede, deserialização perigosa e pacotes maliciosos.

2. 📐 **QUALIDADE DE CÓDIGO E BOAS PRÁTICAS (Qualquer Linguagem)**:
   - Padrões idiomáticos (Python, Bash/Shell, PowerShell, Go, JavaScript/TypeScript, Dockerfile, Terraform, YAML/K8s).
   - Tratamento adequado de erros e exceções (sem catch-all silencioso).
   - Vazamentos de memória, descritores de arquivos abertos e race conditions.
   - Limpeza e legibilidade (Clean Code e manutenibilidade).

3. 🌿 **CONFORMIDADE GIT & GITHUB**:
   - Respeito ao padrão Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`).
   - Tamanho e escopo do PR (alertar se houver alterações não relacionadas ao objetivo).
   - Prevenção de inclusão acidental de binários pesados, logs ou arquivos temporários.

---
**FORMATO DA RESPOSTA (GitHub Markdown Obrigatório)**:

### 🚦 Veredito Geral
Escolha **um**:
- `✅ APROVADO (LGTM)`: Se o código estiver limpo, seguro e bem testado.
- `⚠️ APROVADO COM RESSALVAS`: Se houver melhorias de estilo ou otimizações menores sem risco de segurança.
- `🚨 REPROVADO / ALTERAÇÕES NECESSÁRIAS`: Se houver qualquer vulnerabilidade de segurança, bug grave ou quebra de boas práticas críticas.

### 🛡️ Auditoria de Segurança (AppSec)
- [Status de segredos e credenciais]
- [Status de injeções e execução segura]
- [Status de permissões e controle de acesso]

### 💡 Análise de Código & Boas Práticas
(Para cada ponto relevante, mencione o arquivo, a linha aproximada e sugira uma melhoria clara com bloco de código antes/depois se aplicável).

### 📋 Checklist de Governança
- [ ] **Conventional Commits**: [Conforme / Não Conforme]
- [ ] **Zero Credenciais Expostas**: [OK / ALERTA]
- [ ] **Testes e Validação**: [Coberto / Ausente]

*Seja construtivo, didático, técnico e direto.*
"""


def call_gemini(api_key: str, prompt: str) -> Optional[str]:
    """Calls Google Gemini API (supports gemini-1.5-flash and gemini-2.0-flash)."""
    models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 4096,
            },
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"]
        except Exception as e:
            print(f"DEBUG: Gemini model {model} attempt failed: {e}", file=sys.stderr)
            continue
    return None


def call_openai(api_key: str, prompt: str) -> Optional[str]:
    """Calls OpenAI Chat Completions API as alternative fallback."""
    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 4096,
    }
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content")
    except Exception as e:
        print(f"DEBUG: OpenAI request failed: {e}", file=sys.stderr)
    return None


def post_github_comment(github_token: str, repo: str, pr_number: int, comment_body: str) -> None:
    """Posts or updates comment on the GitHub PR."""
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "DevOpsHero-AI-Reviewer",
    }

    # Tag comment with hidden watermark to allow in-place updates
    full_comment = f"{COMMENT_TAG}\n## 🤖 DevOpsHero AI — Revisão de Código & Segurança\n\n{comment_body}\n\n---\n*Revisão automática gerada por IA com foco em AppSec, Clean Code e Boas Práticas.*"

    # Search for existing comment
    comments_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    existing_comment_id = None

    try:
        req = urllib.request.Request(comments_url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            comments = json.loads(resp.read().decode("utf-8"))
            for c in comments:
                if COMMENT_TAG in c.get("body", ""):
                    existing_comment_id = c.get("id")
                    break
    except Exception as e:
        print(f"Warning: Failed to fetch existing comments: {e}", file=sys.stderr)

    if existing_comment_id:
        # Update existing comment
        update_url = f"https://api.github.com/repos/{repo}/issues/comments/{existing_comment_id}"
        payload = json.dumps({"body": full_comment}).encode("utf-8")
        req = urllib.request.Request(update_url, data=payload, headers=headers, method="PATCH")
        try:
            with urllib.request.urlopen(req, timeout=20):
                print(f"Successfully updated AI review comment #{existing_comment_id}")
                return
        except Exception as e:
            print(f"Warning: Failed to update comment #{existing_comment_id}: {e}", file=sys.stderr)

    # Post new comment
    payload = json.dumps({"body": full_comment}).encode("utf-8")
    req = urllib.request.Request(comments_url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20):
            print("Successfully posted new AI review comment on PR.")
    except Exception as e:
        print(f"Error posting comment to GitHub: {e}", file=sys.stderr)


def main() -> None:
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    github_token = os.getenv("GITHUB_TOKEN", "").strip()
    repo = os.getenv("GITHUB_REPOSITORY", "").strip()
    pr_number_str = os.getenv("PR_NUMBER", "").strip()
    base_ref = os.getenv("GITHUB_BASE_REF", "main").strip() or "main"
    pr_title = os.getenv("PR_TITLE", "").strip()
    pr_author = os.getenv("PR_AUTHOR", "").strip()

    if not gemini_key and not openai_key:
        print("\n" + "=" * 70)
        print("ℹ️  [DevOpsHero AI Reviewer] Nenhuma chave de IA detectada.")
        print("   Para habilitar a auditoria automática de PRs 100% gratuita:")
        print("   1. Gere uma chave em: https://aistudio.google.com/app/apikey")
        print("   2. No GitHub, vá em: Settings -> Secrets and variables -> Actions")
        print("   3. Adicione o secret: GEMINI_API_KEY")
        print("=" * 70 + "\n")
        sys.exit(0)

    if not github_token or not repo or not pr_number_str:
        print("Skipping: Required GitHub context (token, repo, pr_number) missing.")
        sys.exit(0)

    try:
        pr_number = int(pr_number_str)
    except ValueError:
        print(f"Invalid PR number: {pr_number_str}")
        sys.exit(0)

    diff = get_pr_diff(base_ref)
    if not diff:
        print("No diff found for review.")
        sys.exit(0)

    # Limit diff size to ~100k chars to fit safely within token limits
    max_diff_len = 100000
    truncated_notice = ""
    if len(diff) > max_diff_len:
        diff = diff[:max_diff_len]
        truncated_notice = "\n*(Diff truncado para os primeiros 100.000 caracteres)*\n"

    commits = get_commit_messages(base_ref)
    commits_summary = "\n".join(f"- {c}" for c in commits) if commits else "(Não foi possível obter commits individuais)"

    user_prompt = f"""
Por favor, analise as alterações deste Pull Request:

**Repositório**: {repo}
**PR #{pr_number}**: {pr_title}
**Autor**: @{pr_author}
**Branch Alvo**: {base_ref}

**Commits neste PR**:
{commits_summary}

**Diff do Código**:
```diff
{diff}
```
{truncated_notice}

Realize a auditoria rigorosa de Segurança (AppSec), Boas Práticas e Padrões Git de acordo com suas diretrizes.
"""

    review_text = None
    if gemini_key:
        print("Calling Google Gemini AI for PR code review...")
        review_text = call_gemini(gemini_key, f"{build_system_prompt()}\n\n{user_prompt}")

    if not review_text and openai_key:
        print("Calling OpenAI API for PR code review...")
        review_text = call_openai(openai_key, user_prompt)

    if not review_text:
        print("Failed to generate AI review from available providers.", file=sys.stderr)
        sys.exit(1)

    print("Posting review comment to GitHub PR...")
    post_github_comment(github_token, repo, pr_number, review_text)


if __name__ == "__main__":
    main()
