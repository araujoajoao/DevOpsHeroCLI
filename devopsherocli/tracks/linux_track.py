"""Linux learning track missions."""
from __future__ import annotations

from typing import Tuple

from devopsherocli.engine.executor import EnvironmentState
from devopsherocli.models import Mission, Track


def setup_m05(state: EnvironmentState):
    state.linux._write_file("/home/devops/id_rsa", "-----BEGIN OPENSSH PRIVATE KEY-----\nb3BlbnNzaC1rZXktdjE...\n", perms="-rw-r--r--")


def check_m01(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if cmd.strip() == "pwd":
        return True, "Excelente! Você confirmou o caminho do diretório atual de trabalho (/home/devops)."
    return False, "Execute o comando que exibe o caminho do diretório atual de trabalho."


def check_m02(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    tokens = cmd.strip().split()
    if tokens and tokens[0] == "ls":
        has_a = any("a" in t for t in tokens[1:] if t.startswith("-"))
        has_l = any("l" in t for t in tokens[1:] if t.startswith("-"))
        if has_a and has_l:
            return True, "Perfeito! Você listou detalhadamente todos os arquivos, inclusive os arquivos ocultos (. e ..)."
    return False, "Liste os arquivos em formato detalhado e incluindo os arquivos ocultos."


def check_m03(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    node = state.linux._get_node("/app/logs/access.log")
    if node is not None:
        return True, "Perfeito! A estrutura '/app/logs' e o arquivo 'access.log' foram criados."
    return False, "O arquivo '/app/logs/access.log' ainda não foi criado."


def check_m04(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if "ERROR" in out and "grep" in cmd:
        return True, "Muito bem! Você filtrou os logs com sucesso e isolou a falha de banco de dados."
    return False, "Filtre as mensagens do arquivo buscando pelo termo de erro indicado."


def check_m05(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    node = state.linux._get_node("/home/devops/id_rsa")
    if node and node.perms == "-rw-------":
        return True, "Segurança garantida! A chave privada agora tem permissão restrita 600."
    return False, "A permissão da chave deve permitir somente leitura e escrita pelo proprietário."


def check_m06(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if 1337 not in state.linux.processes:
        return True, "Sensacional! O processo minerador que sobrecarregava a CPU foi eliminado."
    return False, "O processo 1337 ainda está ativo. Localize-o e encerre-o."


def check_m07(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    node = state.linux._get_node("/app/.env")
    if node and "ENV=production" in node.content:
        return True, "Conteúdo gravado com sucesso no arquivo /app/.env utilizando redirecionamento!"
    return False, "O arquivo /app/.env deve conter exatamente a linha indicada."


def check_m08(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    node = state.linux._get_node("/app/logs/syslog.bak")
    if node:
        return True, "Cópia de segurança criada com sucesso em /app/logs/syslog.bak!"
    return False, "Copie o arquivo de log para o destino de backup indicado."


def check_m09(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if cmd.strip().startswith("df"):
        return True, "Auditoria de espaço em disco em formato legível concluída!"
    return False, "Execute o comando que exibe o uso de disco das partições em formato legível."


def check_m10(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if "curl" in cmd and ("localhost" in cmd or "127.0.0.1" in cmd):
        return True, "Cabeçalhos de resposta HTTP obtidos com sucesso do servidor local!"
    return False, "Faça uma requisição ao servidor local solicitando apenas os cabeçalhos de resposta."


LINUX_TRACK = Track(
    id="linux",
    name="Linux Essencial",
    icon="🐧",
    description="Domine o terminal Linux, navegação no sistema, permissões, processos e manipulação de arquivos.",
    missions=[
        Mission(
            id="linux-01",
            track_id="linux",
            title="Diretório de Trabalho Atual",
            difficulty="Iniciante",
            xp=100,
            context="Você acabou de acessar o servidor de produção da empresa através de uma sessão remota. Antes de realizar qualquer alteração, você precisa se situar no sistema de arquivos.",
            objective="Descubra e exiba no terminal o caminho absoluto do diretório atual onde você está situado.",
            tip="O comando para imprimir o diretório de trabalho atual (Print Working Directory) é 'pwd'.",
            solution="pwd",
            check_completion=check_m01,
        ),
        Mission(
            id="linux-02",
            track_id="linux",
            title="Listagem Detalhada e Ocultos",
            difficulty="Iniciante",
            xp=100,
            context="Agora que você já sabe onde está, a equipe precisa verificar quais arquivos existem na pasta, incluindo possíveis arquivos de configuração ocultos iniciados por ponto.",
            objective="Liste todos os arquivos do diretório atual em formato longo e detalhado, revelando também os arquivos ocultos.",
            tip="O comando 'ls' com as opções '-l' (long format) e '-a' (all/ocultos) atende a esse objetivo: 'ls -la'.",
            solution="ls -la",
            check_completion=check_m02,
        ),
        Mission(
            id="linux-03",
            track_id="linux",
            title="Criando Pastas e Arquivos",
            difficulty="Iniciante",
            xp=100,
            context="A equipe de desenvolvimento precisa de um local centralizado para guardar logs da API.",
            objective="Crie a estrutura de diretórios '/app/logs' e dentro dela crie um arquivo vazio com o nome 'access.log'.",
            tip="Crie o diretório com 'mkdir -p /app/logs' e gere o arquivo vazio com 'touch /app/logs/access.log'.",
            solution="mkdir -p /app/logs && touch /app/logs/access.log",
            check_completion=check_m03,
        ),
        Mission(
            id="linux-04",
            track_id="linux",
            title="Investigação de Logs com Filtro",
            difficulty="Iniciante",
            xp=120,
            context="O suporte abriu um chamado informando que a aplicação parou de responder às 10h. O log do sistema contém centenas de linhas e precisamos isolar o erro.",
            objective="Filtre e exiba apenas as mensagens de erro no arquivo '/var/log/syslog' que contenham a palavra 'ERROR'.",
            tip="Utilize o comando 'grep' para filtrar ocorrências de texto: 'grep ERROR /var/log/syslog'.",
            solution="grep ERROR /var/log/syslog",
            check_completion=check_m04,
        ),
        Mission(
            id="linux-05",
            track_id="linux",
            title="Permissões de Segurança de Chaves",
            difficulty="Iniciante",
            xp=120,
            context="Uma chave SSH privada foi colocada em '/home/devops/id_rsa', porém o cliente SSH recusa a conexão porque as permissões estão abertas a outros usuários.",
            objective="Altere as permissões do arquivo '/home/devops/id_rsa' para que apenas o proprietário tenha permissão de leitura e escrita.",
            tip="A representação octal para leitura e escrita exclusivas do dono é 600: 'chmod 600 id_rsa'.",
            solution="chmod 600 id_rsa",
            initial_setup=setup_m05,
            check_completion=check_m05,
        ),
        Mission(
            id="linux-06",
            track_id="linux",
            title="Caça aos Processos Maliciosos",
            difficulty="Intermediário",
            xp=150,
            context="O alerta de infraestrutura disparou indicando 100% de CPU. Há um processo suspeito não autorizado consumindo os recursos da máquina.",
            objective="Inspecione a lista de processos do sistema, localize o processo de alta CPU com PID 1337 e encerre-o imediatamente.",
            tip="Liste os processos com 'ps aux' e envie o sinal de finalização com 'kill 1337'.",
            solution="kill 1337",
            check_completion=check_m06,
        ),
        Mission(
            id="linux-07",
            track_id="linux",
            title="Redirecionamento de Saída",
            difficulty="Iniciante",
            xp=100,
            context="Antes de iniciar a aplicação, precisamos gravar o arquivo de variáveis de ambiente com o apontamento para produção.",
            objective="Grave exatamente o conteúdo 'ENV=production' dentro do arquivo '/app/.env' utilizando redirecionamento de fluxo no terminal.",
            tip="Utilize 'echo' com o operador de redirecionamento '>': 'echo \"ENV=production\" > /app/.env'.",
            solution="echo \"ENV=production\" > /app/.env",
            check_completion=check_m07,
        ),
        Mission(
            id="linux-08",
            track_id="linux",
            title="Backup de Arquivos do Sistema",
            difficulty="Iniciante",
            xp=100,
            context="Antes de reiniciar o nó, é recomendável manter uma cópia estática do arquivo de log do sistema para auditoria posterior.",
            objective="Copie o arquivo '/var/log/syslog' criando uma cópia em '/app/logs/syslog.bak'.",
            tip="O utilitário de cópia de arquivos é 'cp': 'cp /var/log/syslog /app/logs/syslog.bak'.",
            solution="cp /var/log/syslog /app/logs/syslog.bak",
            check_completion=check_m08,
        ),
        Mission(
            id="linux-09",
            track_id="linux",
            title="Diagnóstico de Armazenamento",
            difficulty="Iniciante",
            xp=100,
            context="O time de operações solicitou um levantamento rápido do espaço em disco ocupado e livre nas partições do servidor.",
            objective="Exiba o relatório de uso de disco de todas as partições do sistema em formato legível para humanos.",
            tip="O utilitário 'df' com o parâmetro '-h' (human-readable) exibe os tamanhos em megabytes/gigabytes: 'df -h'.",
            solution="df -h",
            check_completion=check_m09,
        ),
        Mission(
            id="linux-10",
            track_id="linux",
            title="Inspeção de Resposta HTTP",
            difficulty="Intermediário",
            xp=120,
            context="Precisamos checar se o servidor web local está ativo e respondendo na porta padrão 8080 sem baixar o corpo completo da página.",
            objective="Faça uma requisição ao endereço 'http://localhost:8080' solicitando exclusivamente os cabeçalhos de resposta HTTP.",
            tip="Com 'curl', a flag '-I' (ou '--head') traz apenas o cabeçalho HTTP: 'curl -I http://localhost:8080'.",
            solution="curl -I http://localhost:8080",
            check_completion=check_m10,
        ),
    ],
)
