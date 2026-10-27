"""Track 8: Terraform Infraestrutura como Código (10 missions)."""
from __future__ import annotations

from devopsherocli.engine.executor import EnvironmentState
from devopsherocli.models import Mission, Track


def _setup_tf_uninit(state: EnvironmentState):
    state.terraform.reset_default_state()
    state.terraform.initialized = False


def _setup_tf_initialized(state: EnvironmentState):
    state.terraform.reset_default_state()
    state.terraform.initialized = True


def check_tf_init(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 2 and tokens[0] == "terraform" and tokens[1] == "init":
        return state.terraform.initialized, "Diretório Terraform inicializado com providers e backend!"
    return False, "Inicialize o ambiente Terraform para instalar provedores e dependências."


def check_tf_fmt(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 2 and tokens[0] == "terraform" and tokens[1] == "fmt":
        return True, "Arquivos de manifesto HCL formatados conforme o padrão oficial!"
    return False, "Formate o código HCL para seguir as boas práticas de estilo do Terraform."


def check_tf_validate(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 2 and tokens[0] == "terraform" and tokens[1] == "validate":
        return True, "Sintaxe e consistência dos manifestos Terraform validadas com sucesso!"
    return False, "Valide a sintaxe e argumentos dos seus manifestos Terraform."


def check_tf_plan(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 2 and tokens[0] == "terraform" and tokens[1] == "plan":
        return True, "Plano de execução gerado com sucesso detalhando adições e alterações!"
    return False, "Gere o plano de execução para visualizar o que o Terraform pretende alterar."


def check_tf_apply(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 2 and tokens[0] == "terraform" and tokens[1] == "apply":
        return len(state.terraform.state_resources) >= 5, "Recursos provisionados na nuvem e registrados no estado!"
    return False, "Aplique as modificações para provisionar a infraestrutura declarada."


def check_tf_show(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 2 and tokens[0] == "terraform" and tokens[1] == "show":
        return True, "Estado atual da infraestrutura inspecionado em formato legível!"
    return False, "Exiba o conteúdo do arquivo de estado atual da infraestrutura."


def check_tf_state_list(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 3 and tokens[0] == "terraform" and tokens[1] == "state" and tokens[2] == "list":
        return True, "Inventário de identificadores de recursos no estado exibido com sucesso!"
    return False, "Liste todos os recursos atualmente gerenciados no arquivo de estado."


def check_tf_state_show(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 4 and tokens[0] == "terraform" and tokens[1] == "state" and tokens[2] == "show":
        return True, "Atributos do recurso inspecionados diretamente do estado!"
    return False, "Exiba os atributos e IDs de um recurso específico salvo no estado."


def check_tf_output(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 2 and tokens[0] == "terraform" and tokens[1] == "output":
        return True, "Valores de saída declarados (outputs) consultados com sucesso!"
    return False, "Consulte os valores de output gerados pela raiz do módulo."


def check_tf_destroy(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 2 and tokens[0] == "terraform" and tokens[1] == "destroy":
        return len(state.terraform.state_resources) == 0, "Infraestrutura descartada e estado limpo com sucesso!"
    return False, "Destrua os recursos provisionados para evitar custos residuais."


TERRAFORM_MISSIONS: list[Mission] = [
    Mission(
        id="tf_01",
        track_id="terraform",
        title="Inicializando o Projeto Terraform",
        difficulty="Iniciante",
        xp=100,
        context="Você baixou um novo repositório de Infraestrutura como Código (IaC) e precisa configurar o backend e baixar os provedores de nuvem.",
        objective="Inicialize o diretório de trabalho do Terraform instalando provedores necessários.",
        tip="O subcomando inicial do Terraform é 'init'.",
        solution="terraform init",
        initial_setup=_setup_tf_uninit,
        check_completion=check_tf_init,
    ),
    Mission(
        id="tf_02",
        track_id="terraform",
        title="Padronização de Código HCL com Fmt",
        difficulty="Iniciante",
        xp=100,
        context="Antes de abrir um Pull Request, é obrigatório formatar os arquivos de manifesto conforme o padrão oficial da HashiCorp.",
        objective="Reformatar todos os arquivos '.tf' do diretório atual de acordo com o padrão canônico.",
        tip="O comando para formatar arquivos de manifesto HCL é 'fmt'.",
        solution="terraform fmt",
        initial_setup=_setup_tf_initialized,
        check_completion=check_tf_fmt,
    ),
    Mission(
        id="tf_03",
        track_id="terraform",
        title="Validação Estática de Sintaxe e Tipos",
        difficulty="Iniciante",
        xp=110,
        context="A esteira de CI executa uma etapa de verificação para garantir que variáveis e argumentos obrigatórios estejam corretos sem tocar na nuvem.",
        objective="Valide a consistência interna e sintaxe dos manifestos Terraform.",
        tip="O subcomando que verifica a integridade estática dos manifestos é 'validate'.",
        solution="terraform validate",
        initial_setup=_setup_tf_initialized,
        check_completion=check_tf_validate,
    ),
    Mission(
        id="tf_04",
        track_id="terraform",
        title="Planejamento de Mudanças de Infraestrutura",
        difficulty="Intermediário",
        xp=120,
        context="Novos recursos (Bucket S3 e Instância EC2) foram declarados e você precisa prever o impacto exato antes de aplicar.",
        objective="Gere e analise o plano de execução demonstrando o que será criado, modificado ou destruído.",
        tip="O comando que calcula o diff entre o código e a nuvem é 'plan'.",
        solution="terraform plan",
        initial_setup=_setup_tf_initialized,
        check_completion=check_tf_plan,
    ),
    Mission(
        id="tf_05",
        track_id="terraform",
        title="Provisionando Recursos com Apply",
        difficulty="Intermediário",
        xp=140,
        context="O plano de execução foi aprovado pelo líder técnico e os recursos devem ser provisionados na conta em nuvem.",
        objective="Aplique as alterações declaradas para provisionar a infraestrutura e atualizar o estado.",
        tip="O comando que executa o provisionamento oficial é 'apply'. Pode ser usado com '-auto-approve'.",
        solution="terraform apply -auto-approve",
        initial_setup=_setup_tf_initialized,
        check_completion=check_tf_apply,
    ),
    Mission(
        id="tf_06",
        track_id="terraform",
        title="Inspecionando o Estado com Show",
        difficulty="Iniciante",
        xp=110,
        context="Para fins de documentação e diagnóstico, você precisa de uma visão legível de todos os atributos dos recursos no estado atual.",
        objective="Exiba o arquivo de estado em formato de texto legível.",
        tip="O subcomando para inspecionar o estado consolidado é 'show'.",
        solution="terraform show",
        initial_setup=_setup_tf_initialized,
        check_completion=check_tf_show,
    ),
    Mission(
        id="tf_07",
        track_id="terraform",
        title="Inventário de Recursos no Estado",
        difficulty="Iniciante",
        xp=110,
        context="Você precisa identificar rapidamente os identificadores de todos os recursos gerenciados para montar um script de auditoria.",
        objective="Liste apenas os nomes e identificadores dos recursos presentes no estado do Terraform.",
        tip="O subcomando 'state list' exibe uma lista limpa dos recursos gerenciados.",
        solution="terraform state list",
        initial_setup=_setup_tf_initialized,
        check_completion=check_tf_state_list,
    ),
    Mission(
        id="tf_08",
        track_id="terraform",
        title="Detalhamento Específico de Recurso no Estado",
        difficulty="Intermediário",
        xp=120,
        context="Você precisa extrair o ID e os parâmetros específicos da VPC principal sem abrir o arquivo JSON bruto de estado.",
        objective="Exiba os detalhes completos do recurso 'aws_vpc.main' diretamente do estado.",
        tip="Utilize o subcomando 'state show' informando o endereço do recurso.",
        solution="terraform state show aws_vpc.main",
        initial_setup=_setup_tf_initialized,
        check_completion=check_tf_state_show,
    ),
    Mission(
        id="tf_09",
        track_id="terraform",
        title="Consultando Valores de Saída (Outputs)",
        difficulty="Iniciante",
        xp=100,
        context="A aplicação frontend precisa saber o IP público da API e o ID da VPC provisionados para configurar suas variáveis de ambiente.",
        objective="Consulte e exiba todos os valores de saída (outputs) definidos no módulo raiz.",
        tip="O subcomando para listar variáveis de saída do Terraform é 'output'.",
        solution="terraform output",
        initial_setup=_setup_tf_initialized,
        check_completion=check_tf_output,
    ),
    Mission(
        id="tf_10",
        track_id="terraform",
        title="Destruição Limpa de Infraestrutura de Testes",
        difficulty="Intermediário",
        xp=130,
        context="Os testes de carga foram concluídos no ambiente efêmero e toda a infraestrutura deve ser completamente destruída.",
        objective="Destrua todos os recursos gerenciados pelo módulo para zerar custos de nuvem.",
        tip="O subcomando para encerrar e remover todos os recursos gerenciados é 'destroy'.",
        solution="terraform destroy -auto-approve",
        initial_setup=_setup_tf_initialized,
        check_completion=check_tf_destroy,
    ),
]

TERRAFORM_TRACK = Track(
    id="terraform",
    name="Terraform Infraestrutura como Código",
    icon="🏗️",
    description="Domine o ciclo completo de IaC: init, fmt, validate, plan, apply, state e outputs.",
    missions=TERRAFORM_MISSIONS,
)
