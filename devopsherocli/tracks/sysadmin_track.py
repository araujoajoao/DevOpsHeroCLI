"""Sysadmin Basic learning track missions."""
from __future__ import annotations

from typing import Tuple

from devopsherocli.engine.executor import EnvironmentState
from devopsherocli.models import Mission, Track


def check_sys01(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if "systemctl status" in cmd and "nginx" in cmd:
        return True, "Excelente! Você inspecionou o status do Nginx, PID principal e consumo de memória."
    return False, "Execute 'systemctl status nginx' para inspecionar o serviço."


def check_sys02(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if "systemctl restart" in cmd and "postgresql" in cmd:
        return True, "Serviço PostgreSQL reiniciado com sucesso! Novas configurações ativadas."
    return False, "Execute 'systemctl restart postgresql'."


def check_sys03(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if state.linux.services.get("nginx", {}).get("enabled") is True:
        return True, "Symlink multi-user.target criado! O Nginx agora iniciará no boot do servidor."
    return False, "Habilite o serviço para inicialização no boot com 'systemctl enable nginx'."


def check_sys04(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if cmd.strip().startswith("ss") or cmd.strip().startswith("netstat"):
        return True, "Portas em modo LISTEN mapeadas com sucesso (22 SSH, 80 HTTP, 5432 Postgres, 8125 DogStatsD)."
    return False, "Use 'ss -tulpn' ou 'netstat -tuln' para auditar os sockets ativos."


def check_sys05(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if "deployer" in state.linux.users:
        u = state.linux.users["deployer"]
        if "/home/deployer" in u["home"]:
            return True, "Usuário 'deployer' criado com diretório home e shell definidos!"
    return False, "Crie o usuário com 'useradd -m -s /bin/bash deployer'."


def check_sys06(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if "crontab -l" in cmd:
        return True, "Rotinas agendadas no cron auditadas com sucesso!"
    return False, "Execute 'crontab -l' para listar as tarefas periódicas configuradas."


def check_sys07(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    node = state.linux._get_node("/tmp/app-backup.tar.gz")  # nosec B108 - simulated path
    if node is not None:
        return True, "Arquivo compactado .tar.gz gerado com sucesso em /tmp/app-backup.tar.gz!"
    return False, "Gere o arquivo com 'tar -czvf /tmp/app-backup.tar.gz /app'."


def check_sys08(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if "journalctl" in cmd and ("nginx" in cmd or "-u" in cmd):
        return True, "Logs do journald do systemd auditados com sucesso!"
    return False, "Execute 'journalctl -u nginx' para ver os logs do serviço."


def check_sys09(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if cmd.strip() == "uptime":
        return True, "Uptime e Load Average analisados com sucesso!"
    return False, "Execute 'uptime' para verificar o tempo de atividade da máquina."


def setup_sys10(state: EnvironmentState):
    if "deployer" not in state.linux.users:
        state.linux.users["deployer"] = {
            "uid": 1002,
            "gid": 1002,
            "home": "/home/deployer",
            "shell": "/bin/bash",
            "groups": ["deployer"],
        }
        state.linux._mkdir_p("/home/deployer")


def check_sys10(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    deployer = state.linux.users.get("deployer")
    if deployer and "sudo" in deployer.get("groups", []):
        return True, "Privilégios administrativos concedidos! O usuário 'deployer' agora pertence ao grupo sudo."
    return False, "Adicione o usuário ao grupo sudo com 'usermod -aG sudo deployer'."


SYSADMIN_TRACK = Track(
    id="sysadmin",
    name="Sysadmin Básico",
    icon="🛠️",
    description="Aprenda administração de servidores: systemd, serviços, usuários, crontab, sockets e backups.",
    missions=[
        Mission(
            id="sysadmin-01",
            track_id="sysadmin",
            title="Diagnóstico de Serviços (systemctl)",
            difficulty="Iniciante",
            xp=100,
            context="O proxy reverso parece instável. Você precisa verificar se o serviço do Nginx está ativo e funcionando.",
            objective="Inspecione o status do serviço usando `systemctl status nginx`.",
            tip="Use `systemctl status nginx`.",
            solution="systemctl status nginx",
            check_completion=check_sys01,
        ),
        Mission(
            id="sysadmin-02",
            track_id="sysadmin",
            title="Reiniciando Serviços Críticos",
            difficulty="Iniciante",
            xp=100,
            context="O DBA alterou os limites de conexão do PostgreSQL e solicitou o reinício gracioso do daemon.",
            objective="Reinicie o serviço do PostgreSQL usando `systemctl restart postgresql`.",
            tip="Use `systemctl restart postgresql`.",
            solution="systemctl restart postgresql",
            check_completion=check_sys02,
        ),
        Mission(
            id="sysadmin-03",
            track_id="sysadmin",
            title="Habilitando Serviço no Boot",
            difficulty="Iniciante",
            xp=110,
            context="Se a máquina virtual reiniciar após um patch de segurança, o Nginx precisa subir automaticamente.",
            objective="Habilite o serviço do Nginx para iniciar automaticamente no boot.",
            tip="Use `systemctl enable nginx`.",
            solution="systemctl enable nginx",
            check_completion=check_sys03,
        ),
        Mission(
            id="sysadmin-04",
            track_id="sysadmin",
            title="Auditoria de Portas e Sockets",
            difficulty="Iniciante",
            xp=120,
            context="Antes de liberar o firewall, o time de segurança quer um relatório de todas as portas TCP e UDP em modo LISTEN.",
            objective="Exiba os sockets em escuta no servidor usando `ss -tulpn`.",
            tip="Use `ss -tulpn` ou `netstat -tuln`.",
            solution="ss -tulpn",
            check_completion=check_sys04,
        ),
        Mission(
            id="sysadmin-05",
            track_id="sysadmin",
            title="Criação de Usuário de Sistema",
            difficulty="Intermediário",
            xp=120,
            context="A esteira de CI/CD precisa de uma conta de serviço chamada `deployer` com diretório home e shell `/bin/bash`.",
            objective="Crie o usuário `deployer` com a flag `-m` (home) e `-s /bin/bash`.",
            tip="Use `useradd -m -s /bin/bash deployer`.",
            solution="useradd -m -s /bin/bash deployer",
            check_completion=check_sys05,
        ),
        Mission(
            id="sysadmin-06",
            track_id="sysadmin",
            title="Auditoria do Agendador Crontab",
            difficulty="Iniciante",
            xp=100,
            context="Precisamos checar quais scripts de rotina estão programados para rodar automaticamente no servidor.",
            objective="Liste as entradas de agendamento do usuário atual com `crontab -l`.",
            tip="Use `crontab -l`.",
            solution="crontab -l",
            check_completion=check_sys06,
        ),
        Mission(
            id="sysadmin-07",
            track_id="sysadmin",
            title="Compactação de Diretórios com Tar",
            difficulty="Intermediário",
            xp=130,
            context="Antes da migração de versão, precisamos empacotar todo o diretório `/app` em um arquivo compactado `.tar.gz`.",
            objective="Crie um arquivo tar.gz do diretório `/app` salvando em `/tmp/app-backup.tar.gz`.",
            tip="Use `tar -czvf /tmp/app-backup.tar.gz /app`.",
            solution="tar -czvf /tmp/app-backup.tar.gz /app",
            check_completion=check_sys07,
        ),
        Mission(
            id="sysadmin-08",
            track_id="sysadmin",
            title="Auditoria de Logs com Journalctl",
            difficulty="Iniciante",
            xp=110,
            context="O serviço do Nginx teve um reload recente. Precisamos verificar os registros do journald.",
            objective="Inspecione os logs do systemd filtrados pela unit do Nginx (`-u nginx`).",
            tip="Use `journalctl -u nginx`.",
            solution="journalctl -u nginx",
            check_completion=check_sys08,
        ),
        Mission(
            id="sysadmin-09",
            track_id="sysadmin",
            title="Uptime e Carga da Máquina",
            difficulty="Iniciante",
            xp=100,
            context="O time quer saber há quanto tempo o host está ativo sem reiniciar e qual o Load Average atual.",
            objective="Execute o comando `uptime`.",
            tip="Digite `uptime` no terminal.",
            solution="uptime",
            check_completion=check_sys09,
        ),
        Mission(
            id="sysadmin-10",
            track_id="sysadmin",
            title="Privilégios Administrativos (Sudo)",
            difficulty="Intermediário",
            xp=120,
            context="Para que o usuário `deployer` possa reiniciar serviços, adicione-o ao grupo suplementar `sudo`.",
            objective="Adicione o usuário `deployer` ao grupo `sudo` usando `usermod -aG sudo deployer`.",
            tip="Use `usermod -aG sudo deployer`.",
            solution="usermod -aG sudo deployer",
            initial_setup=setup_sys10,
            check_completion=check_sys10,
        ),
    ],
)
