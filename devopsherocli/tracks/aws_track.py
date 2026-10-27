"""Track 7: AWS Cloud CLI (10 missions)."""
from __future__ import annotations

from devopsherocli.engine.executor import EnvironmentState
from devopsherocli.models import Mission, Track


def _setup_aws_default(state: EnvironmentState):
    state.aws.reset_default_state()


def check_aws_sts(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 3 and tokens[0] == "aws" and tokens[1] == "sts" and tokens[2] in ["get-caller-identity", "get_caller_identity"]:
        return True, "Identidade e Account ID verificados via AWS STS!"
    return False, "Consulte sua identidade de chamador usando o serviço STS da AWS."


def check_aws_s3_ls(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 3 and tokens[0] == "aws" and tokens[1] == "s3" and tokens[2] == "ls":
        return True, "Buckets e objetos S3 listados com sucesso!"
    return False, "Exiba os buckets disponíveis no serviço Amazon S3."


def check_aws_s3_mb(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 4 and tokens[0] == "aws" and tokens[1] == "s3" and tokens[2] == "mb":
        return True, "Bucket S3 criado com sucesso na sua conta AWS!"
    return False, "Crie um novo bucket S3 usando o subcomando dedicado do S3."


def check_aws_s3_cp(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 5 and tokens[0] == "aws" and tokens[1] == "s3" and tokens[2] == "cp":
        return True, "Arquivo copiado com sucesso para o bucket S3!"
    return False, "Transfira o arquivo local para o destino no bucket S3."


def check_aws_ec2_describe(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 3 and tokens[0] == "aws" and tokens[1] == "ec2" and tokens[2] in ["describe-instances", "describe_instances"]:
        return True, "Instâncias EC2 e seus estados inspecionados!"
    return False, "Consulte a lista e os detalhes das instâncias EC2 da sua VPC."


def check_aws_ec2_start(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 3 and tokens[0] == "aws" and tokens[1] == "ec2" and tokens[2] == "start-instances":
        return True, "Instância EC2 iniciada com sucesso!"
    return False, "Inicie a instância EC2 que se encontra em estado parado."


def check_aws_ec2_stop(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 3 and tokens[0] == "aws" and tokens[1] == "ec2" and tokens[2] == "stop-instances":
        return True, "Instância EC2 interrompida para contenção de custos!"
    return False, "Interrompa a instância EC2 desejada para evitar cobranças indevidas."


def check_aws_iam_list_users(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 3 and tokens[0] == "aws" and tokens[1] == "iam" and tokens[2] == "list-users":
        return True, "Usuários do IAM auditados com sucesso!"
    return False, "Liste os usuários IAM registrados na conta AWS."


def check_aws_iam_create_user(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 3 and tokens[0] == "aws" and tokens[1] == "iam" and tokens[2] == "create-user":
        return True, "Novo usuário de serviço criado no AWS IAM!"
    return False, "Crie um novo usuário no serviço IAM passando o nome do usuário."


def check_aws_lambda_list(state: EnvironmentState, cmd: str, out: str):
    tokens = cmd.strip().split()
    if len(tokens) >= 3 and tokens[0] == "aws" and tokens[1] == "lambda" and tokens[2] == "list-functions":
        return True, "Funções serverless AWS Lambda inspecionadas!"
    return False, "Liste as funções Lambda implementadas na sua região AWS."


AWS_MISSIONS: list[Mission] = [
    Mission(
        id="aws_01",
        track_id="aws",
        title="Auditoria de Identidade e Conta AWS",
        difficulty="Iniciante",
        xp=100,
        context="Antes de executar operações em nuvem, você precisa validar em qual conta AWS e com qual ARN de usuário suas credenciais estão ativas.",
        objective="Consulte sua identidade atual de execução na AWS usando o serviço STS.",
        tip="O Security Token Service possui o subcomando 'get-caller-identity'.",
        solution="aws sts get-caller-identity",
        initial_setup=_setup_aws_default,
        check_completion=check_aws_sts,
    ),
    Mission(
        id="aws_02",
        track_id="aws",
        title="Listagem de Buckets no Amazon S3",
        difficulty="Iniciante",
        xp=100,
        context="A equipe de infraestrutura precisa levantar todos os buckets de armazenamento de objetos criados na conta.",
        objective="Liste todos os buckets disponíveis no serviço Amazon S3.",
        tip="O subcomando de listagem rápida de buckets no S3 é 'ls'.",
        solution="aws s3 ls",
        initial_setup=_setup_aws_default,
        check_completion=check_aws_s3_ls,
    ),
    Mission(
        id="aws_03",
        track_id="aws",
        title="Criando Bucket para Backups",
        difficulty="Iniciante",
        xp=120,
        context="Um novo serviço de arquivamento requer um bucket S3 exclusivo para retenção de relatórios de auditoria.",
        objective="Crie um novo bucket S3 nomeado 's3://company-db-backups-2026'.",
        tip="O subcomando 'mb' (make bucket) cria novos repositórios de objetos no Amazon S3.",
        solution="aws s3 mb s3://company-db-backups-2026",
        initial_setup=_setup_aws_default,
        check_completion=check_aws_s3_mb,
    ),
    Mission(
        id="aws_04",
        track_id="aws",
        title="Upload de Artefato para o S3",
        difficulty="Iniciante",
        xp=120,
        context="O pacote de release gerado localmente precisa ser disponibilizado no repositório de artefatos em nuvem.",
        objective="Faça o upload do arquivo local 'release.tar.gz' para o bucket 's3://company-app-artifacts/'.",
        tip="Use o subcomando 'cp' informando o arquivo local e o URI do S3 de destino.",
        solution="aws s3 cp release.tar.gz s3://company-app-artifacts/",
        initial_setup=_setup_aws_default,
        check_completion=check_aws_s3_cp,
    ),
    Mission(
        id="aws_05",
        track_id="aws",
        title="Auditoria de Instâncias EC2",
        difficulty="Iniciante",
        xp=110,
        context="Durante um plantão de suporte, você precisa levantar quais servidores virtuais estão em execução ou parados.",
        objective="Descreva o status de todas as instâncias EC2 presentes na região.",
        tip="O subcomando do serviço EC2 para consultar instâncias é 'describe-instances'.",
        solution="aws ec2 describe-instances",
        initial_setup=_setup_aws_default,
        check_completion=check_aws_ec2_describe,
    ),
    Mission(
        id="aws_06",
        track_id="aws",
        title="Iniciando Servidor de Processamento Batch",
        difficulty="Intermediário",
        xp=130,
        context="A fila de processamento aumentou e você precisa reativar o worker de staging 'i-0f9e8d7c6b5a43210' que estava desligado.",
        objective="Inicie a instância EC2 com o ID 'i-0f9e8d7c6b5a43210'.",
        tip="Utilize o subcomando 'start-instances' passando a flag '--instance-ids'.",
        solution="aws ec2 start-instances --instance-ids i-0f9e8d7c6b5a43210",
        initial_setup=_setup_aws_default,
        check_completion=check_aws_ec2_start,
    ),
    Mission(
        id="aws_07",
        track_id="aws",
        title="Contenção de Custos: Parando Servidores Ociosos",
        difficulty="Intermediário",
        xp=120,
        context="Ao final do expediente, instâncias de teste devem ser desligadas para evitar custos desnecessários.",
        objective="Interrompa a instância EC2 'i-0a1b2c3d4e5f67890'.",
        tip="O subcomando para parar instâncias preservando os volumes EBS é 'stop-instances'.",
        solution="aws ec2 stop-instances --instance-ids i-0a1b2c3d4e5f67890",
        initial_setup=_setup_aws_default,
        check_completion=check_aws_ec2_stop,
    ),
    Mission(
        id="aws_08",
        track_id="aws",
        title="Auditoria de Acesso: Usuários do IAM",
        difficulty="Iniciante",
        xp=110,
        context="O time de compliance exige uma lista consolidada de todas as identidades de usuários cadastradas no AWS IAM.",
        objective="Liste todos os usuários cadastrados no Identity and Access Management (IAM).",
        tip="O subcomando do IAM para listar identidades é 'list-users'.",
        solution="aws iam list-users",
        initial_setup=_setup_aws_default,
        check_completion=check_aws_iam_list_users,
    ),
    Mission(
        id="aws_09",
        track_id="aws",
        title="Provisionando Usuário de Serviço no IAM",
        difficulty="Intermediário",
        xp=130,
        context="Uma nova esteira de CI/CD precisa de uma conta de serviço dedicada para publicar releases.",
        objective="Crie um novo usuário no IAM com o nome de usuário 'github-actions-deployer'.",
        tip="Utilize 'create-user' passando a flag '--user-name'.",
        solution="aws iam create-user --user-name github-actions-deployer",
        initial_setup=_setup_aws_default,
        check_completion=check_aws_iam_create_user,
    ),
    Mission(
        id="aws_10",
        track_id="aws",
        title="Inventário de Microsserviços Serverless Lambda",
        difficulty="Intermediário",
        xp=120,
        context="A aplicação processa webhooks assíncronos e você precisa listar as funções serverless ativas no cluster.",
        objective="Liste todas as funções AWS Lambda criadas no ambiente.",
        tip="O serviço lambda disponibiliza o subcomando 'list-functions'.",
        solution="aws lambda list-functions",
        initial_setup=_setup_aws_default,
        check_completion=check_aws_lambda_list,
    ),
]

AWS_TRACK = Track(
    id="aws",
    name="AWS Cloud & Infraestrutura",
    icon="☁️",
    description="Gerencie serviços essenciais da AWS (S3, EC2, IAM, Lambda e STS) direto pela linha de comando.",
    missions=AWS_MISSIONS,
)
