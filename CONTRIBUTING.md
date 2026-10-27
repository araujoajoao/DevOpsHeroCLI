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

## 🚀 Abrindo o Pull Request

1. Envie seus commits para o seu fork:
   ```bash
   git push origin feat/nome-da-sua-branch
   ```
2. Acesse o repositório oficial no GitHub e clique em **New Pull Request**.
3. Preencha o modelo do Pull Request detalhando o que foi feito e os testes realizados.
4. Aguarde a validação automática do GitHub Actions CI (Ubuntu e macOS em Python 3.9 a 3.13).
5. Após aprovação e CI verde, o PR será incorporado à branch `main` via merge seguro.
