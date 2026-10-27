"""Datadog Observability learning track missions."""
from __future__ import annotations

from typing import Tuple

from devopsherocli.engine.executor import EnvironmentState
from devopsherocli.models import Mission, Track


def check_dd01(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if cmd.strip().startswith("datadog-agent status") or cmd.strip().startswith("agent status"):
        return True, "Relatório completo do Datadog Agent analisado! Collector, DogStatsD, Logs e APM validados."
    return False, "Execute o comando de status do agente para visualizar a telemetria."


def check_dd02(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if "datadog-agent health" in cmd or "agent health" in cmd:
        return True, "Excelente! Todos os processos internos do Agent (Collector, Forwarder, APM) estão saudáveis."
    return False, "Execute o health check do agente para validar a resposta dos serviços."


def check_dd03(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if "datadog-agent version" in cmd or "agent version" in cmd:
        return True, "Versão do Agent 7.55.0 auditada com sucesso!"
    return False, "Consulte a versão instalada do Agent."


def check_dd04(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if "datadog-agent check disk" in cmd or "agent check disk" in cmd:
        return True, "Check de disco executado! Métricas system.disk.used e tags de dispositivo coletadas."
    return False, "Execute sob demanda a verificação do check de disco."


def check_dd05(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if "datadog-agent check docker" in cmd or "agent check docker" in cmd:
        return True, "Integração Docker validada! Métricas de containers, uso de CPU e memória recolhidas."
    return False, "Execute sob demanda a verificação do check de Docker no Agent."


def check_dd06(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if ("datadog-agent flare" in cmd or "agent flare" in cmd) and "984521" in cmd:
        return True, "Flare gerado e transmitido para o time de suporte Datadog com todos os logs criptografados!"
    return False, "Gere o pacote flare associando ao caso de suporte 984521."


def check_dd07(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if state.env_vars.get("DD_ENV") == "production":
        return True, "Tag unificada de ambiente (DD_ENV=production) configurada! Agora traces, logs e métricas estão correlacionados."
    return False, "Configure a variável de ambiente DD_ENV com o valor 'production'."


def check_dd08(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if state.env_vars.get("DD_SERVICE") == "payment-api":
        return True, "Nome do serviço padronizado (DD_SERVICE=payment-api)! Facilita a visualização no APM Service Catalog."
    return False, "Configure a variável de ambiente DD_SERVICE com o valor 'payment-api'."


def check_dd09(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if state.env_vars.get("DD_VERSION") == "2.0.1":
        return True, "Versão do release rastreada (DD_VERSION=2.0.1)! Fundamental para monitorar regressões pós-deploy."
    return False, "Configure a variável de ambiente DD_VERSION com o valor '2.0.1'."


def check_dd10(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if "datadog-agent config" in cmd or "agent config" in cmd:
        return True, "Parabéns! Você concluiu a trilha de Observabilidade com Datadog!"
    return False, "Exiba a configuração em execução do Datadog Agent."


DATADOG_TRACK = Track(
    id="datadog",
    name="Datadog Observabilidade",
    icon="🐕",
    description="Aprenda a operar o Datadog Agent, executar checks, gerar flares e configurar tags unificadas.",
    missions=[
        Mission(
            id="datadog-01",
            track_id="datadog",
            title="Diagnóstico Geral do Datadog Agent",
            difficulty="Iniciante",
            xp=100,
            context="O dashboard corporativo no Datadog não está exibindo as métricas do novo servidor. Precisamos validar se o Agent local está rodando.",
            objective="Gere o relatório geral de telemetria do Datadog Agent para auditar os checks coletores, APM, DogStatsD e logs.",
            tip="Use 'datadog-agent status'.",
            solution="datadog-agent status",
            check_completion=check_dd01,
        ),
        Mission(
            id="datadog-02",
            track_id="datadog",
            title="Health Check dos Sub-Serviços",
            difficulty="Iniciante",
            xp=100,
            context="O monitor de infraestrutura precisa de uma verificação rápida de integridade para confirmar que todos os sub-serviços estão respondendo.",
            objective="Verifique a integridade e saúde operacional de todos os sub-serviços do Agent.",
            tip="Use 'datadog-agent health'.",
            solution="datadog-agent health",
            check_completion=check_dd02,
        ),
        Mission(
            id="datadog-03",
            track_id="datadog",
            title="Auditoria de Versão do Agent",
            difficulty="Iniciante",
            xp=100,
            context="A equipe de segurança exigiu certificar que todos os agentes estejam no mínimo na versão 7.50+.",
            objective="Consulte a versão exata e o commit do binário do Datadog Agent instalado no sistema.",
            tip="Use 'datadog-agent version'.",
            solution="datadog-agent version",
            check_completion=check_dd03,
        ),
        Mission(
            id="datadog-04",
            track_id="datadog",
            title="Check de Disco Sob Demanda",
            difficulty="Intermediário",
            xp=120,
            context="Antes de reiniciar o agente, queremos testar se o coletor do check de disco está extraindo as partições corretamente.",
            objective="Execute sob demanda a coleta de métricas do check de disco ('disk') para auditar o espaço das partições.",
            tip="Use 'datadog-agent check disk'.",
            solution="datadog-agent check disk",
            check_completion=check_dd04,
        ),
        Mission(
            id="datadog-05",
            track_id="datadog",
            title="Validando a Integração Docker",
            difficulty="Intermediário",
            xp=120,
            context="O coletor precisa ler as estatísticas do socket do Docker localmente para mapear contêineres e imagens.",
            objective="Execute o check do Docker no Agent para validar a leitura das métricas e contêineres do socket local.",
            tip="Use 'datadog-agent check docker'.",
            solution="datadog-agent check docker",
            check_completion=check_dd05,
        ),
        Mission(
            id="datadog-06",
            track_id="datadog",
            title="Gerando um Datadog Flare para Suporte",
            difficulty="Intermediário",
            xp=140,
            context="Você abriu um ticket no suporte da Datadog (#984521) solicitando ajuda em uma anomalia de rede. O suporte pediu um Flare para análise de logs criptografados.",
            objective="Gere e envie o pacote de diagnóstico completo (flare) associando ao número de caso de suporte '984521'.",
            tip="Use 'datadog-agent flare --case-id 984521'.",
            solution="datadog-agent flare --case-id 984521",
            check_completion=check_dd06,
        ),
        Mission(
            id="datadog-07",
            track_id="datadog",
            title="Unified Service Tagging: DD_ENV",
            difficulty="Iniciante",
            xp=110,
            context="A melhor prática da Datadog exige as três tags primordiais (env, service, version) para correlação entre APM e logs.",
            objective="Configure a tag unificada de ambiente da aplicação, exportando a variável correspondente para 'production'.",
            tip="Use 'export DD_ENV=production'.",
            solution="export DD_ENV=production",
            check_completion=check_dd07,
        ),
        Mission(
            id="datadog-08",
            track_id="datadog",
            title="Unified Service Tagging: DD_SERVICE",
            difficulty="Iniciante",
            xp=110,
            context="Para agrupar métricas e logs no APM Catalog, precisamos definir o nome padronizado do serviço.",
            objective="Configure o nome do serviço no APM exportando a variável de identificação do serviço para 'payment-api'.",
            tip="Use 'export DD_SERVICE=payment-api'.",
            solution="export DD_SERVICE=payment-api",
            check_completion=check_dd08,
        ),
        Mission(
            id="datadog-09",
            track_id="datadog",
            title="Unified Service Tagging: DD_VERSION",
            difficulty="Iniciante",
            xp=110,
            context="Para o Datadog correlacionar picos de erro a uma versão específica lançada pós-deploy.",
            objective="Rastreie a versão da aplicação no Datadog exportando a variável de versão para '2.0.1'.",
            tip="Use 'export DD_VERSION=2.0.1'.",
            solution="export DD_VERSION=2.0.1",
            check_completion=check_dd09,
        ),
        Mission(
            id="datadog-10",
            track_id="datadog",
            title="Auditoria de Configurações em Execução",
            difficulty="Iniciante",
            xp=100,
            context="Para fechar o checklist de homologação, queremos exibir a configuração final consolidada do Agent.",
            objective="Exiba no terminal a configuração consolidada em tempo de execução do Datadog Agent.",
            tip="Use 'datadog-agent config'.",
            solution="datadog-agent config",
            check_completion=check_dd10,
        ),
    ],
)
