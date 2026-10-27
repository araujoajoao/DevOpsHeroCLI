"""Docker learning track missions."""
from __future__ import annotations

from typing import Tuple

from devopsherocli.engine.executor import EnvironmentState
from devopsherocli.models import Mission, Track


def check_d01(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    c = state.docker._find_container("web-server")
    if c and c.is_running and "nginx" in c.image:
        return True, "Parabéns! O contêiner web-server está rodando com Nginx."
    return False, "O contêiner 'web-server' não está ativo com a imagem e portas solicitadas."


def check_d02(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if cmd.strip().startswith("docker ps"):
        return True, "Excelente! Você listou os contêineres e viu o status e portas expostas."
    return False, "Execute o comando para listar os contêineres ativos no daemon."


def check_d03(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if "docker logs" in cmd and "postgres-db" in cmd:
        return True, "Logs inspecionados com sucesso! Você obteve o histórico de inicialização do contêiner do banco."
    return False, "Obtenha os logs do contêiner 'postgres-db'."


def setup_web_server(state: EnvironmentState):
    if not state.docker._find_container("web-server"):
        state.docker.execute(["run", "-d", "--name", "web-server", "-p", "8080:80", "nginx:alpine"])


def check_d04(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if "docker exec" in cmd and "web-server" in cmd and "env" in cmd:
        return True, "Perfeito! Você executou uma instrução diretamente dentro do namespace do contêiner."
    return False, "Execute o utilitário de ambiente dentro do contêiner 'web-server'."


def check_d05(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    c = state.docker._find_container("web-server")
    if c and not c.is_running:
        return True, "Contêiner parado com sucesso via sinal SIGTERM!"
    return False, "O contêiner ainda está rodando. Interrompa a sua execução."


def check_d06(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if "backend-net" in state.docker.networks:
        return True, "Rede bridge 'backend-net' criada com sucesso! Agora os serviços podem se comunicar por DNS interno."
    return False, "A rede 'backend-net' ainda não existe no daemon."


def check_d07(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if "app_storage" in state.docker.volumes:
        return True, "Volume 'app_storage' criado! Dados persistirão mesmo se o contêiner for destruído."
    return False, "O volume 'app_storage' ainda não foi criado."


def check_d08(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if "docker build" in cmd and ("minha-api:v1" in cmd or "-t minha-api:v1" in cmd):
        return True, "Imagem gerada com sucesso e adicionada ao cache local de imagens!"
    return False, "Construa a imagem a partir do diretório atual atribuindo a tag solicitada."


def check_d09(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if cmd.strip() == "docker stats":
        return True, "Métricas de CPU, memória e tráfego de rede dos contêineres analisadas!"
    return False, "Abra o painel de estatísticas de consumo de recursos dos contêineres."


def check_d10(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    c = state.docker._find_container("web-server")
    if c is None:
        return True, "Contêiner removido com sucesso! O ambiente de desenvolvimento está limpo."
    return False, "O contêiner 'web-server' ainda existe. Remova-o do daemon."


DOCKER_TRACK = Track(
    id="docker",
    name="Docker & Contêineres",
    icon="🐳",
    description="Aprenda a criar, inspecionar, depurar e orquestrar contêineres Docker.",
    missions=[
        Mission(
            id="docker-01",
            track_id="docker",
            title="Seu Primeiro Contêiner",
            difficulty="Iniciante",
            xp=100,
            context="O time de produto solicitou a inicialização de um servidor web leve Nginx para atender requisições na porta 8080.",
            objective="Inicie um contêiner em segundo plano chamado 'web-server' com a imagem 'nginx:alpine', mapeando a porta 8080 do host para a porta 80 interna do contêiner.",
            tip="Use: 'docker run -d --name web-server -p 8080:80 nginx:alpine'.",
            solution="docker run -d --name web-server -p 8080:80 nginx:alpine",
            check_completion=check_d01,
        ),
        Mission(
            id="docker-02",
            track_id="docker",
            title="Inspecionando Contêineres Ativos",
            difficulty="Iniciante",
            xp=100,
            context="Você precisa auditar quais contêineres estão ativos no host e verificar as portas expostas por cada um.",
            objective="Exiba a lista de todos os contêineres que estão atualmente em execução no host.",
            tip="O comando para listar contêineres em execução é 'docker ps'.",
            solution="docker ps",
            check_completion=check_d02,
        ),
        Mission(
            id="docker-03",
            track_id="docker",
            title="Leitura de Logs de Contêiner",
            difficulty="Iniciante",
            xp=120,
            context="Recebemos um alerta sobre erros na conexão com o banco. Precisamos ver o que o contêiner do postgres está cuspindo no stdout.",
            objective="Inspecione e exiba as mensagens de log emitidas pelo contêiner 'postgres-db'.",
            tip="Use 'docker logs postgres-db'.",
            solution="docker logs postgres-db",
            check_completion=check_d03,
        ),
        Mission(
            id="docker-04",
            track_id="docker",
            title="Executando Comandos no Contêiner",
            difficulty="Intermediário",
            xp=130,
            context="Para validar a configuração injetada, precisamos inspecionar as variáveis de ambiente ativas dentro do contêiner.",
            objective="Execute a listagem das variáveis de ambiente ('env') dentro do contêiner ativo 'web-server' sem abrir uma sessão interativa manual.",
            tip="Use 'docker exec web-server env'.",
            solution="docker exec web-server env",
            initial_setup=setup_web_server,
            check_completion=check_d04,
        ),
        Mission(
            id="docker-05",
            track_id="docker",
            title="Parando um Serviço",
            difficulty="Iniciante",
            xp=100,
            context="Vamos aplicar uma atualização de segurança e precisamos parar o contêiner 'web-server' de forma graciosa.",
            objective="Interrompa a execução do contêiner 'web-server'.",
            tip="Use 'docker stop web-server'.",
            solution="docker stop web-server",
            initial_setup=setup_web_server,
            check_completion=check_d05,
        ),
        Mission(
            id="docker-06",
            track_id="docker",
            title="Isolamento com Redes Customizadas",
            difficulty="Intermediário",
            xp=120,
            context="Por padrão o Docker usa a rede bridge padrão, que não possui resolução automática de nomes por DNS. Precisamos de uma rede isolada para o backend.",
            objective="Crie uma nova rede de contêineres chamada 'backend-net'.",
            tip="Use 'docker network create backend-net'.",
            solution="docker network create backend-net",
            check_completion=check_d06,
        ),
        Mission(
            id="docker-07",
            track_id="docker",
            title="Garantindo Persistência com Volumes",
            difficulty="Intermediário",
            xp=120,
            context="Contêineres são efêmeros! Se o contêiner morrer, os uploads serão perdidos se não estiverem em um volume gerenciado.",
            objective="Crie um volume de armazenamento gerenciado chamado 'app_storage'.",
            tip="Use 'docker volume create app_storage'.",
            solution="docker volume create app_storage",
            check_completion=check_d07,
        ),
        Mission(
            id="docker-08",
            track_id="docker",
            title="Construindo Imagens com Dockerfile",
            difficulty="Intermediário",
            xp=140,
            context="O código fonte da nova API foi finalizado no diretório atual e precisamos empacotá-lo em uma imagem pronta para distribuição.",
            objective="Construa uma nova imagem a partir do Dockerfile do diretório atual, definindo a tag como 'minha-api:v1'.",
            tip="Use 'docker build -t minha-api:v1 .'.",
            solution="docker build -t minha-api:v1 .",
            check_completion=check_d08,
        ),
        Mission(
            id="docker-09",
            track_id="docker",
            title="Auditoria de Consumo de Recursos",
            difficulty="Iniciante",
            xp=110,
            context="O time de operações quer analisar o percentual de CPU e memória consumido pelos contêineres ativos.",
            objective="Abra a tabela de estatísticas em tempo real de consumo de recursos dos contêineres.",
            tip="O comando para estatísticas de consumo é 'docker stats'.",
            solution="docker stats",
            check_completion=check_d09,
        ),
        Mission(
            id="docker-10",
            track_id="docker",
            title="Faxina de Contêineres Órfãos",
            difficulty="Iniciante",
            xp=100,
            context="O contêiner 'web-server' já não é mais necessário e está ocupando recursos de nome no daemon.",
            objective="Exclua definitivamente o contêiner 'web-server'.",
            tip="Use 'docker rm -f web-server'.",
            solution="docker rm -f web-server",
            check_completion=check_d10,
        ),
    ],
)
