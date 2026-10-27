"""Track 6: Git Controle de Versão (10 missions)."""
from __future__ import annotations

from devopsherocli.engine.executor import EnvironmentState
from devopsherocli.models import Mission, Track


def _setup_git_dirty(state: EnvironmentState):
    state.git.is_repo = True
    state.git.branches = {"main"}
    state.git.current_branch = "main"
    state.git.untracked_files = {"app.py", "requirements.txt", ".env.example"}


def _setup_git_staged(state: EnvironmentState):
    state.git.is_repo = True
    state.git.branches = {"main"}
    state.git.current_branch = "main"
    state.git.staged_files = {"app.py", "Dockerfile"}


def _setup_git_with_history(state: EnvironmentState):
    state.git.is_repo = True
    state.git.branches = {"main"}
    state.git.current_branch = "main"
    if not state.git.commits:
        state.git.execute(["commit", "-m", "chore: initial commit with base app structure"])


def _setup_git_branch_merge(state: EnvironmentState):
    state.git.is_repo = True
    state.git.branches = {"main", "feature/auth-service"}
    state.git.current_branch = "main"


def _setup_git_dirty_stash(state: EnvironmentState):
    state.git.is_repo = True
    state.git.branches = {"main"}
    state.git.current_branch = "main"
    state.git.unstaged_files = {"config.py"}


def check_git_init(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 2 and tokens[0] == "git" and tokens[1] == "init":
        return state.git.is_repo, "Repositório Git inicializado com sucesso!"
    return False, "Utilize o comando de inicialização do Git para versionar o projeto."


def check_git_status(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 2 and tokens[0] == "git" and tokens[1] == "status":
        return True, "Status do repositório e árvore de trabalho inspecionado!"
    return False, "Consulte o status do repositório para verificar alterações."


def check_git_add(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 2 and tokens[0] == "git" and tokens[1] == "add":
        return len(state.git.staged_files) > 0, "Arquivos adicionados à staging area com sucesso!"
    return False, "Adicione os arquivos pendentes à área de staging."


def check_git_commit(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 2 and tokens[0] == "git" and tokens[1] == "commit" and ("-m" in tokens or "-am" in tokens):
        return len(state.git.commits) > 0, "Commit registrado no histórico do repositório!"
    return False, "Grave as alterações preparadas registrando um commit com mensagem."


def check_git_log(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 2 and tokens[0] == "git" and tokens[1] == "log":
        return True, "Histórico de commits inspecionado com sucesso!"
    return False, "Exiba o histórico de commits do repositório."


def check_git_branch_create(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if tokens and tokens[0] == "git":
        if "checkout" in tokens and "-b" in tokens:
            return True, "Nova branch criada e ativada!"
        elif "switch" in tokens and ("-c" in tokens or "-C" in tokens):
            return True, "Nova branch criada e ativada!"
        elif "branch" in tokens and len(tokens) >= 3:
            return True, "Nova branch criada!"
    return False, "Crie ou mude para uma nova branch de funcionalidade."


def check_git_merge(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 3 and tokens[0] == "git" and tokens[1] == "merge":
        return True, "Branch mesclada à branch principal com sucesso!"
    return False, "Mescle a branch secundária de funcionalidade na branch principal."


def check_git_remote_add(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 4 and tokens[0] == "git" and tokens[1] == "remote" and tokens[2] == "add":
        return "origin" in state.git.remotes, "Repositório remoto 'origin' adicionado com sucesso!"
    return False, "Adicione um apontamento remoto de origem (origin) ao repositório."


def check_git_stash(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 2 and tokens[0] == "git" and tokens[1] == "stash":
        return True, "Modificações locais guardadas temporariamente no stash!"
    return False, "Guarde as alterações pendentes no stash para limpar a árvore de trabalho."


def check_git_tag(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 3 and tokens[0] == "git" and tokens[1] == "tag":
        return len(state.git.tags) > 0, "Tag de versão criada com sucesso!"
    return False, "Crie uma tag de versão para marcar o release da aplicação."


GIT_MISSIONS: list[Mission] = [
    Mission(
        id="git_01",
        track_id="git",
        title="Inicializando o Repositório de Código",
        difficulty="Iniciante",
        xp=100,
        context="Você acabou de entrar em um novo projeto e precisa começar a versionar o código-fonte da aplicação no diretório atual.",
        objective="Inicialize um repositório Git limpo no diretório de trabalho.",
        tip="O comando para criar um repositório vazio no diretório atual é 'git init'.",
        solution="git init",
        check_completion=check_git_init,
    ),
    Mission(
        id="git_02",
        track_id="git",
        title="Inspecionando o Estado da Árvore de Trabalho",
        difficulty="Iniciante",
        xp=100,
        context="Arquivos foram criados e modificados por outros membros do time e você precisa verificar quais estão rastreados ou pendentes.",
        objective="Verifique o estado atual do repositório, identificando arquivos não rastreados.",
        tip="O comando de status mostra o branch atual e o estado dos arquivos.",
        solution="git status",
        initial_setup=_setup_git_dirty,
        check_completion=check_git_status,
    ),
    Mission(
        id="git_03",
        track_id="git",
        title="Adicionando Arquivos à Área de Staging",
        difficulty="Iniciante",
        xp=110,
        context="Novos arquivos foram implementados e precisam ser preparados para inclusão no próximo commit do projeto.",
        objective="Prepare todos os arquivos pendentes movendo-os para a área de staging.",
        tip="Você pode preparar todos os arquivos de uma vez passando o ponto '.' como alvo do comando de adição.",
        solution="git add .",
        initial_setup=_setup_git_dirty,
        check_completion=check_git_add,
    ),
    Mission(
        id="git_04",
        track_id="git",
        title="Gravando o Primeiro Commit da Aplicação",
        difficulty="Iniciante",
        xp=120,
        context="Os arquivos já estão na staging area e você precisa criar um ponto de restauração oficial no histórico com mensagem descritiva.",
        objective="Grave um commit com uma mensagem explicando as alterações realizadas.",
        tip="Utilize a flag '-m' para passar o texto explicativo do commit diretamente.",
        solution='git commit -m "feat: initial commit"',
        initial_setup=_setup_git_staged,
        check_completion=check_git_commit,
    ),
    Mission(
        id="git_05",
        track_id="git",
        title="Auditoria do Histórico de Commits",
        difficulty="Iniciante",
        xp=100,
        context="A equipe de segurança precisa auditar os últimos commits aplicados para identificar autores e mensagens de entrega.",
        objective="Exiba o histórico de commits do repositório atual.",
        tip="O comando de histórico do Git é 'git log'.",
        solution="git log",
        initial_setup=_setup_git_with_history,
        check_completion=check_git_log,
    ),
    Mission(
        id="git_06",
        track_id="git",
        title="Isolamento em Branch de Feature",
        difficulty="Intermediário",
        xp=130,
        context="Para não alterar a branch principal diretamente, você deve criar uma branch isolada para implementar o módulo de autenticação.",
        objective="Crie e mude imediatamente para uma nova branch chamada 'feature/auth-service'.",
        tip="O comando checkout com a flag '-b' ou o comando switch com a flag '-c' criam e ativam uma branch simultaneamente.",
        solution="git checkout -b feature/auth-service",
        initial_setup=_setup_git_with_history,
        check_completion=check_git_branch_create,
    ),
    Mission(
        id="git_07",
        track_id="git",
        title="Mesclando Branches com Merge",
        difficulty="Intermediário",
        xp=140,
        context="O desenvolvimento na branch secundária 'feature/auth-service' foi finalizado e aprovado no code review.",
        objective="Estando na branch principal, mescle as alterações da branch 'feature/auth-service'.",
        tip="O comando para integrar alterações de outra branch no branch ativo é 'git merge <nome-da-branch>'.",
        solution="git merge feature/auth-service",
        initial_setup=_setup_git_branch_merge,
        check_completion=check_git_merge,
    ),
    Mission(
        id="git_08",
        track_id="git",
        title="Vinculando Repositório Remoto",
        difficulty="Intermediário",
        xp=120,
        context="Você precisa conectar seu repositório local ao servidor central no GitHub para sincronizar código com a equipe.",
        objective="Adicione um repositório remoto denominado 'origin' apontando para 'https://github.com/empresa/app.git'.",
        tip="Utilize o subcomando 'remote add' com o nome e a URL desejada.",
        solution="git remote add origin https://github.com/empresa/app.git",
        initial_setup=_setup_git_with_history,
        check_completion=check_git_remote_add,
    ),
    Mission(
        id="git_09",
        track_id="git",
        title="Guardando Alterações Temporárias no Stash",
        difficulty="Intermediário",
        xp=130,
        context="Você está no meio de uma alteração e precisa trocar de contexto urgente sem fazer um commit incompleto.",
        objective="Guarde as alterações pendentes no stash temporário deixando a árvore de trabalho limpa.",
        tip="O comando 'stash' salva o estado de trabalho sem criar um commit definitivo.",
        solution="git stash",
        initial_setup=_setup_git_dirty_stash,
        check_completion=check_git_stash,
    ),
    Mission(
        id="git_10",
        track_id="git",
        title="Criando Tag de Release para Produção",
        difficulty="Intermediário",
        xp=140,
        context="O pipeline de deploy precisa de uma tag de versão imutável para disparar a publicação do pacote v1.0.0 em produção.",
        objective="Crie uma tag de versão nomeada 'v1.0.0' no commit atual.",
        tip="O comando 'git tag <nome>' cria um marcador de versão estático.",
        solution="git tag v1.0.0",
        initial_setup=_setup_git_with_history,
        check_completion=check_git_tag,
    ),
]

GIT_TRACK = Track(
    id="git",
    name="Git Controle de Versão",
    icon="🌿",
    description="Domine branching, commits, histórico, merge, stash e tags como um profissional.",
    missions=GIT_MISSIONS,
)
