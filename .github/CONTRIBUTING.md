# 🤝 Guia de Contribuição — DevOpsHeroCLI

Obrigado pelo interesse em contribuir com o **DevOpsHeroCLI**! Para manter a qualidade, estabilidade e segurança do projeto, seguimos rigorosas boas práticas de Git e desenvolvimento de software.

---

## 🛡️ Regras de Proteção de Branches

A branch `main` é estritamente **protegida** contra pushes diretos e force-pushes (`git push --force`). Qualquer contribuição ou alteração deve obrigatoriamente seguir o fluxo de **Pull Request (PR)**.

- ❌ **Proibido**: Fazer commits ou deploy direto na branch `main`.
- ❌ **Proibido**: Fazer force-push (`git push -f`) ou reescrever histórico público.
- ✅ **Obrigatório**: Criar uma branch temática (`feature/...` ou `fix/...`).
- ✅ **Obrigatório**: Passar por todos os testes automatizados do CI antes do merge.

---

## 🌿 Fluxo de Trabalho Git (Git Flow / Trunk-Based)

### 1. Criar um Fork e Clonar
Faça um fork do repositório no GitHub para sua conta pessoal e clone localmente:
```bash
git clone https://github.com/<seu-usuario>/DevOpsHeroCLI.git
cd DevOpsHeroCLI
git remote add upstream https://github.com/araujoajoao/DevOpsHeroCLI.git
```

### 2. Sincronizar com a Upstream
Antes de iniciar qualquer tarefa, certifique-se de que sua branch `main` local está atualizada:
```bash
git checkout main
git pull upstream main
```

### 3. Criar uma Branch Temática
Nomeie sua branch de acordo com o padrão do Conventional Commits:
```bash
# Para novas funcionalidades, trilhas ou mecânicas:
git checkout -b feat/nome-da-funcionalidade

# Para correção de bugs e simuladores:
git checkout -b fix/descricao-do-bug

# Para documentação e tutoriais:
git checkout -b docs/nome-da-mudanca
```

---

## ✍️ Padrão de Mensagens de Commit (Conventional Commits)

Escreva mensagens claras, objetivas e em minúsculas com prefixo semântico:

- `feat:` Introdução de uma nova trilha, missão, simulador ou recurso visual.
- `fix:` Correção de comportamento inesperado em algum simulador ou tela.
- `docs:` Alterações na documentação (`README.md`, `CONTRIBUTING.md`, etc.).
- `style:` Ajustes puramente visuais, formatação de código ou regras CSS/TCSS.
- `refactor:` Refatoração interna de código sem alteração no comportamento externo.
- `test:` Adição ou correção de suítes de testes unitários.
- `ci:` Modificações nos workflows de CI/CD do GitHub Actions.

**Exemplo:**
```bash
git commit -m "feat(docker): add docker volume prune simulator command"
```

---

## 🧪 Validação Local de Testes

Antes de abrir um Pull Request, execute toda a suíte de testes unitários localmente para garantir que nenhuma regressão foi introduzida:

```bash
# Executar a suíte de testes com Python:
python3 -m unittest discover tests

# Ou via Makefile:
make test
```

Todos os testes devem passar com status `OK`.

---

## 🛠️ Ambiente de Desenvolvimento (build local)

> Usuários finais não precisam de nada desta seção: o [README](../README.md) tem apenas os links diretos de download. Esta seção é para quem desenvolve o projeto.

### CLI (Python 3.9+)
```bash
./dh            # Linux / macOS / WSL: cria o .venv e roda a TUI a partir do código-fonte
.\dh.ps1        # Windows PowerShell (ou dh.bat no CMD)
make test       # Suíte de testes
make verify     # Autoteste das 80 missões
```
O `./dh` recria o `.venv` se estiver quebrado (ex.: copiado de outro SO) e, no Debian/Ubuntu sem `python3-venv`, usa o [`uv`](https://docs.astral.sh/uv/) quando disponível.

### Instaladores
| Comando | Saída | Requisito |
|---|---|---|
| `make deb` | `dist/DevOpsHero.deb` | Python 3 |
| `make dmg` | `dist/DevOpsHero.dmg` | macOS (Swift, `iconutil`, `hdiutil`) + Pillow |
| `make icons` | `assets/DevOpsHero.icns` / `.ico` a partir de `assets/icon.svg` | macOS + Pillow |
| `make install-linux` | Atalho no menu e `dh` no PATH | Linux |
| `scripts\install_windows.ps1` | Atalhos na Área de Trabalho e Menu Iniciar | Windows |
| `make docker` | Contêiner isolado (`docker/`) | Docker |

### Apps mobile
| Projeto | Rodar | Validar |
|---|---|---|
| `devopshero-mobile` (Expo SDK 58) | `make mobile` · `npx expo run:android` · `make mobile-ios` | `npm run typecheck` · `npx expo-doctor` · `npm run export:check` |
| `devopshero-ios-swiftui` | `make swift` (Xcode) | `xcodebuild -scheme DevOpsHero -sdk iphonesimulator build` |

Depois de alterar as trilhas da CLI, sincronize as missões dos dois apps:
```bash
.venv/bin/python devopshero-mobile/scripts/export_mobile_dataset.py
```

Builds para as lojas usam o EAS (`devopshero-mobile/eas.json`): perfil `preview` (APK interno / simulador iOS) e `production` (AAB para Google Play, IPA para App Store). A publicação nas lojas ainda está em andamento.

### Publicando uma versão
1. Atualize a versão em `devopsherocli/__init__.py` e `pyproject.toml` (um teste garante que são iguais).
2. `git tag vX.Y.Z && git push origin vX.Y.Z`
3. O workflow [`release.yml`](workflows/release.yml) confere a tag, roda os testes, gera e **testa a instalação** do `.deb` (Ubuntu), `.dmg` (macOS) e `.zip` (Windows) e publica tudo no GitHub Release com `SHA256SUMS.txt`.

### Segredos
Este é um projeto de aprendizado: **nenhuma chave, token ou credencial** (ex.: Datadog API/APP key, AWS) pode entrar no repositório, e o projeto é publicado **somente** neste GitHub. O job `Secret scan (gitleaks)` do CI varre todo o histórico em cada push e PR.

---

## 🚀 Abrindo o Pull Request

1. Envie seus commits para o seu fork:
   ```bash
   git push origin feat/nome-da-sua-branch
   ```
2. Acesse o repositório oficial no GitHub e clique em **New Pull Request**.
3. Preencha o modelo do Pull Request detalhando o que foi feito e os testes realizados.
4. Aguarde a validação automática do **GitHub Actions CI** (Ubuntu, macOS e Windows em Python 3.9 a 3.13).
5. O **DevOpsHero AI Reviewer** irá auditar automaticamente seu PR quanto a segurança (OWASP/AppSec), boas práticas e padrões Git.
6. Após aprovação e CI verde, o PR será incorporado à branch `main` via merge seguro.

---

## 🤖 Revisão Automática por IA (DevOpsHero AI Reviewer)

Todos os Pull Requests abertos no repositório contam com uma esteira de auditoria automatizada por IA (via Google Gemini ou OpenAI):

- 🔒 **AppSec**: Varredura de credenciais expostas, injeções de comando/SQL/Path Traversal e permissões indevidas.
- 📐 **Qualidade de Código**: Verificação de boas práticas, tipagem, tratamento de exceções e legibilidade em qualquer linguagem.
- 🌿 **Padrões Git**: Validação de Conventional Commits e escopo de alterações.

> **Nota para Mantenedores**: Para ativar o revisor de IA com custo zero (plano gratuito), basta gerar uma chave em [Google AI Studio](https://aistudio.google.com/app/apikey) e cadastrá-la nos Secrets do repositório (`Settings` ➔ `Secrets and variables` ➔ `Actions`) com o nome **`GEMINI_API_KEY`**.
