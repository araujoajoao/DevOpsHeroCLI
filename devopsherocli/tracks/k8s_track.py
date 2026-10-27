"""Kubernetes learning track missions."""
from __future__ import annotations

from typing import Tuple

from devopsherocli.engine.executor import EnvironmentState
from devopsherocli.models import Mission, Track


def check_k01(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if cmd.strip().startswith("kubectl get nodes") or cmd.strip().startswith("kubectl get no"):
        return True, "Sensacional! Você verificou que o cluster possui nós prontos (Ready) para trabalho."
    return False, "Execute o comando para listar os nós do cluster."


def check_k02(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if "web-pod" in state.k8s.pods:
        return True, "Pod criado com sucesso! O Kubelet já agendou o pod e ele está em estado Running."
    return False, "O pod 'web-pod' não foi criado com a imagem solicitada."


def check_k03(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if "kubectl get pods" in cmd and ("-A" in cmd or "--all-namespaces" in cmd):
        return True, "Excelente! Você descobriu os pods de sistema fundamentais (como CoreDNS e o Datadog Agent)."
    return False, "Liste os pods de todos os namespaces usando o comando apropriado."


def check_k04(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if "backend-api" in state.k8s.deployments:
        d = state.k8s.deployments["backend-api"]
        if d.replicas >= 3:
            return True, "Deployment criado com 3 réplicas! O ReplicaSet garante resiliência e auto-recuperação."
    return False, "Crie o deployment 'backend-api' com 3 réplicas."


def setup_backend_deploy(state: EnvironmentState):
    if "backend-api" not in state.k8s.deployments:
        state.k8s.execute(["create", "deployment", "backend-api", "--image=nginx:alpine", "--replicas=3"])


def setup_web_pod(state: EnvironmentState):
    if "web-pod" not in state.k8s.pods:
        state.k8s.execute(["run", "web-pod", "--image=nginx:alpine"])


def check_k05(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    d = state.k8s.deployments.get("backend-api")
    if d and d.replicas == 5:
        return True, "Escalabilidade elástica na prática! O cluster agora gerencia 5 réplicas ativas."
    return False, "Escale o deployment para conter 5 réplicas."


def check_k06(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if "backend-api" in state.k8s.services:
        return True, "Service criado! O tráfego interno agora é balanceado entre os pods do deployment."
    return False, "Exponha o deployment na porta 80."


def check_k07(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if "app-config" in state.k8s.configmaps:
        if state.k8s.configmaps["app-config"].get("DB_HOST") == "postgres-cluster":
            return True, "ConfigMap criado com sucesso! As variáveis agora podem ser injetadas de forma desacoplada."
    return False, "Crie o ConfigMap 'app-config' com a chave literal DB_HOST=postgres-cluster."


def check_k08(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if "kubectl describe pod" in cmd and ("web-pod" in cmd or "coredns" in cmd or "datadog" in cmd):
        return True, "Diagnóstico completo! A seção de eventos (Events) é essencial para auditar agendamento e pull de imagem."
    return False, "Inspecione os detalhes completos e eventos do pod 'web-pod'."


def check_k09(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if "kubectl logs" in cmd and ("web-pod" in cmd or "coredns" in cmd or "datadog" in cmd):
        return True, "Logs extraídos com sucesso do contêiner dentro do pod!"
    return False, "Obtenha os logs do pod 'web-pod'."


def check_k10(state: EnvironmentState, cmd: str, out: str) -> Tuple[bool, str]:
    if "web-pod" not in state.k8s.pods:
        return True, "Pod deletado e recursos liberados no worker node!"
    return False, "O pod 'web-pod' ainda existe. Remova-o do cluster."


K8S_TRACK = Track(
    id="k8s",
    name="Kubernetes Orquestração",
    icon="☸️",
    description="Aprenda a operar clusters, Pods, Deployments, Services e ConfigMaps.",
    missions=[
        Mission(
            id="k8s-01",
            track_id="k8s",
            title="Explorando os Nós do Cluster",
            difficulty="Iniciante",
            xp=100,
            context="Você acabou de receber o kubeconfig da infraestrutura e precisa validar a saúde e capacidade do cluster.",
            objective="Liste todos os nós do cluster para confirmar se estão com status 'Ready'.",
            tip="Use 'kubectl get nodes'.",
            solution="kubectl get nodes",
            check_completion=check_k01,
        ),
        Mission(
            id="k8s-02",
            track_id="k8s",
            title="Criando seu Primeiro Pod",
            difficulty="Iniciante",
            xp=100,
            context="Para validar o tráfego de rede entre nós, precisamos rodar um pod simples com Nginx.",
            objective="Crie um pod autônomo com o nome 'web-pod' utilizando a imagem 'nginx:alpine'.",
            tip="Use 'kubectl run web-pod --image=nginx:alpine'.",
            solution="kubectl run web-pod --image=nginx:alpine",
            check_completion=check_k02,
        ),
        Mission(
            id="k8s-03",
            track_id="k8s",
            title="Visão Geral em Todos os Namespaces",
            difficulty="Iniciante",
            xp=110,
            context="Por padrão, o kubectl só mostra os pods do namespace 'default'. Queremos auditar os pods de monitoramento e sistema em todo o cluster.",
            objective="Liste os pods existentes em todos os namespaces do cluster.",
            tip="Use a opção '-A' (ou '--all-namespaces'): 'kubectl get pods -A'.",
            solution="kubectl get pods -A",
            check_completion=check_k03,
        ),
        Mission(
            id="k8s-04",
            track_id="k8s",
            title="Deployments com Réplicas",
            difficulty="Intermediário",
            xp=130,
            context="Pods individuais não possuem auto-cura se o nó falhar. Precisamos de um Deployment para gerenciar o ciclo de vida e réplicas.",
            objective="Crie um deployment chamado 'backend-api' utilizando a imagem 'nginx:alpine' com 3 réplicas.",
            tip="Use 'kubectl create deployment backend-api --image=nginx:alpine --replicas=3'.",
            solution="kubectl create deployment backend-api --image=nginx:alpine --replicas=3",
            check_completion=check_k04,
        ),
        Mission(
            id="k8s-05",
            track_id="k8s",
            title="Escalando Aplicações Sob Demanda",
            difficulty="Intermediário",
            xp=120,
            context="O tráfego aumentou e precisamos escalar a capacidade do 'backend-api' de 3 para 5 réplicas imediatamente.",
            objective="Escale a quantidade de réplicas do deployment 'backend-api' para 5 instâncias.",
            tip="Use 'kubectl scale deployment backend-api --replicas=5'.",
            solution="kubectl scale deployment backend-api --replicas=5",
            initial_setup=setup_backend_deploy,
            check_completion=check_k05,
        ),
        Mission(
            id="k8s-06",
            track_id="k8s",
            title="Expondo com Kubernetes Services",
            difficulty="Intermediário",
            xp=130,
            context="Os pods têm IPs efêmeros que mudam ao reiniciar. Precisamos de um Service com balanceador interno para rotear requisições.",
            objective="Exponha o deployment 'backend-api' através de um Service na porta 80.",
            tip="Use 'kubectl expose deployment backend-api --port=80 --target-port=80'.",
            solution="kubectl expose deployment backend-api --port=80 --target-port=80",
            initial_setup=setup_backend_deploy,
            check_completion=check_k06,
        ),
        Mission(
            id="k8s-07",
            track_id="k8s",
            title="Desacoplando Configurações (ConfigMaps)",
            difficulty="Intermediário",
            xp=120,
            context="Nunca coloque credenciais ou endpoints hardcoded na imagem do contêiner. Devem ser injetados via ConfigMap.",
            objective="Crie um ConfigMap chamado 'app-config' contendo a chave literal 'DB_HOST=postgres-cluster'.",
            tip="Use 'kubectl create configmap app-config --from-literal=DB_HOST=postgres-cluster'.",
            solution="kubectl create configmap app-config --from-literal=DB_HOST=postgres-cluster",
            check_completion=check_k07,
        ),
        Mission(
            id="k8s-08",
            track_id="k8s",
            title="Troubleshooting de Pods",
            difficulty="Iniciante",
            xp=100,
            context="Um dos pods parece instável. Precisamos inspecionar os eventos detalhados para entender o ciclo de vida.",
            objective="Inspecione os detalhes completos e eventos recentes do pod 'web-pod'.",
            tip="Use 'kubectl describe pod web-pod'.",
            solution="kubectl describe pod web-pod",
            initial_setup=setup_web_pod,
            check_completion=check_k08,
        ),
        Mission(
            id="k8s-09",
            track_id="k8s",
            title="Coleta de Logs de Pods",
            difficulty="Iniciante",
            xp=100,
            context="Precisamos validar se a inicialização do contêiner dentro do pod ocorreu sem erros.",
            objective="Exiba os logs gerados pelo pod 'web-pod'.",
            tip="Use 'kubectl logs web-pod'.",
            solution="kubectl logs web-pod",
            initial_setup=setup_web_pod,
            check_completion=check_k09,
        ),
        Mission(
            id="k8s-10",
            track_id="k8s",
            title="Deletando Recursos com Segurança",
            difficulty="Iniciante",
            xp=100,
            context="O teste temporário terminou e precisamos desalocar o pod 'web-pod' para liberar memória nos nós.",
            objective="Remova o pod 'web-pod' do cluster.",
            tip="Use 'kubectl delete pod web-pod'.",
            solution="kubectl delete pod web-pod",
            initial_setup=setup_web_pod,
            check_completion=check_k10,
        ),
    ],
)
