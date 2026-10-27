"""Virtual Kubernetes Engine: Pods, Deployments, Services, ConfigMaps."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class K8sPod:
    name: str
    namespace: str
    image: str
    status: str = "Running"
    ready: str = "1/1"
    restarts: int = 0
    age: str = "10m"
    ip: str = "10.244.1.25"
    node: str = "k8s-worker-01"
    labels: Dict[str, str] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)


@dataclass
class K8sDeployment:
    name: str
    namespace: str
    image: str
    replicas: int = 1
    ready_replicas: int = 1
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class K8sService:
    name: str
    namespace: str
    type: str = "ClusterIP"
    cluster_ip: str = "10.96.42.108"
    external_ip: str = "<none>"
    ports: str = "80/TCP"


class KubernetesSimulator:
    """Simulates kubectl CLI commands and in-memory cluster state."""

    def __init__(self):
        self.pods: Dict[str, K8sPod] = {}
        self.deployments: Dict[str, K8sDeployment] = {}
        self.services: Dict[str, K8sService] = {}
        self.configmaps: Dict[str, Dict[str, str]] = {}
        self.secrets: Dict[str, Dict[str, str]] = {}
        self.namespaces: List[str] = ["default", "kube-system", "monitoring", "production"]
        self.reset_default_state()

    def reset_default_state(self):
        self.pods = {
            "coredns-6f6b679f8f-v8km9": K8sPod(
                name="coredns-6f6b679f8f-v8km9",
                namespace="kube-system",
                image="registry.k8s.io/coredns/coredns:v1.11.1",
                status="Running",
                ready="1/1",
                restarts=0,
                age="3d",
                node="k8s-control-plane",
            ),
            "datadog-agent-m7k42": K8sPod(
                name="datadog-agent-m7k42",
                namespace="monitoring",
                image="gcr.io/datadoghq/agent:7.55.0",
                status="Running",
                ready="1/1",
                restarts=0,
                age="2d",
                node="k8s-worker-01",
                labels={"app": "datadog-agent"},
                logs=["Starting Datadog Agent v7.55.0", "Checks runner initialized", "Forwarder listening on 0.0.0.0:8125"],
            ),
        }

        self.deployments = {}
        self.services = {
            "kubernetes": K8sService(
                name="kubernetes",
                namespace="default",
                type="ClusterIP",
                cluster_ip="10.96.0.1",
                ports="443/TCP",
            )
        }
        self.configmaps = {
            "kube-root-ca.crt": {"ca.crt": "-----BEGIN CERTIFICATE-----\nMIICyDCCAbCgAwIBAgIBADANBgkqhkiG9w0BAQs..."},
        }
        self.secrets = {}

    def execute(self, args: List[str]) -> str:
        if not args:
            return self.help([])
        cmd = args[0]
        subargs = args[1:]

        handlers = {
            "get": self.get,
            "describe": self.describe,
            "run": self.run,
            "create": self.create,
            "scale": self.scale,
            "expose": self.expose,
            "logs": self.logs,
            "exec": self.k8s_exec,
            "delete": self.delete,
            "rollout": self.rollout,
            "top": self.top,
            "version": self.version,
            "help": self.help,
            "--help": self.help,
        }

        handler = handlers.get(cmd)
        if handler:
            return handler(subargs)
        return f"error: unknown command \"{cmd}\" for \"kubectl\""

    def version(self, args: List[str]) -> str:
        return (
            "Client Version: v1.30.2\n"
            "Kustomize Version: v5.0.4-0.20230601165947-6ce0bd390ce3\n"
            "Server Version: v1.30.2\n"
            "Kubernetes Control Plane: https://10.96.0.1:6443"
        )

    def help(self, args: List[str]) -> str:
        return (
            "kubectl controls the Kubernetes cluster manager.\n\n"
            "Basic Commands (Beginner):\n"
            "  create        Create a resource from a file or from stdin\n"
            "  expose        Take a replication controller, service, deployment or pod and expose it as a new Kubernetes service\n"
            "  run           Run a particular image on the cluster\n"
            "  set           Set specific features on objects\n\n"
            "Basic Commands (Intermediate):\n"
            "  get           Display one or many resources\n"
            "  explain       Get documentation for a resource\n"
            "  edit          Edit a resource on the server\n"
            "  delete        Delete resources by filenames, stdin, resources and names, or by resources and label selector\n\n"
            "Troubleshooting and Debugging Commands:\n"
            "  describe      Show details of a specific resource or group of resources\n"
            "  logs          Print the logs for a container in a pod\n"
            "  exec          Execute a command in a container\n"
            "  top           Display resource (CPU/memory) usage"
        )

    def _parse_ns(self, args: List[str]) -> Tuple[str, List[str], bool]:
        ns = "default"
        all_ns = False
        filtered = []
        i = 0
        while i < len(args):
            if args[i] in ["-n", "--namespace"] and i + 1 < len(args):
                ns = args[i + 1]
                i += 2
            elif args[i] in ["-A", "--all-namespaces"]:
                all_ns = True
                i += 1
            else:
                filtered.append(args[i])
                i += 1
        return ns, filtered, all_ns

    def get(self, args: List[str]) -> str:
        ns, clean_args, all_ns = self._parse_ns(args)
        if not clean_args:
            return "error: You must specify the type of resource to get. e.g. pods, nodes, services"
        res_type = clean_args[0].lower()

        if res_type in ["nodes", "node", "no"]:
            return (
                f"{'NAME':<24} {'STATUS':<10} {'ROLES':<16} {'AGE':<8} {'VERSION'}\n"
                f"{'k8s-control-plane':<24} {'Ready':<10} {'control-plane':<16} {'3d':<8} {'v1.30.2'}\n"
                f"{'k8s-worker-01':<24} {'Ready':<10} {'<none>':<16} {'3d':<8} {'v1.30.2'}\n"
                f"{'k8s-worker-02':<24} {'Ready':<10} {'<none>':<16} {'3d':<8} {'v1.30.2'}"
            )

        if res_type in ["namespaces", "namespace", "ns"]:
            lines = [f"{'NAME':<20} {'STATUS':<10} {'AGE'}"]
            for n in self.namespaces:
                lines.append(f"{n:<20} {'Active':<10} {'3d'}")
            return "\n".join(lines)

        if res_type in ["pods", "pod", "po"]:
            pod_list = list(self.pods.values())
            if not all_ns:
                pod_list = [p for p in pod_list if p.namespace == ns]
            if not pod_list:
                return f"No resources found in {ns} namespace."

            if all_ns:
                lines = [f"{'NAMESPACE':<15} {'NAME':<32} {'READY':<8} {'STATUS':<14} {'RESTARTS':<10} {'AGE'}"]
                for p in pod_list:
                    status_fmt = f"[bold green]{p.status}[/]" if p.status == "Running" else f"[bold red]{p.status}[/]"
                    lines.append(f"{p.namespace:<15} {p.name:<32} {p.ready:<8} {status_fmt:<23} {p.restarts:<10} {p.age}")
            else:
                lines = [f"{'NAME':<32} {'READY':<8} {'STATUS':<14} {'RESTARTS':<10} {'AGE'}"]
                for p in pod_list:
                    status_fmt = f"[bold green]{p.status}[/]" if p.status == "Running" else f"[bold red]{p.status}[/]"
                    lines.append(f"{p.name:<32} {p.ready:<8} {status_fmt:<23} {p.restarts:<10} {p.age}")
            return "\n".join(lines)

        if res_type in ["deployments", "deployment", "deploy"]:
            deploys = list(self.deployments.values())
            if not all_ns:
                deploys = [d for d in deploys if d.namespace == ns]
            if not deploys:
                return f"No resources found in {ns} namespace."
            lines = [f"{'NAME':<24} {'READY':<10} {'UP-TO-DATE':<12} {'AVAILABLE':<12} {'AGE'}"]
            for d in deploys:
                lines.append(f"{d.name:<24} {f'{d.ready_replicas}/{d.replicas}':<10} {d.replicas:<12} {d.ready_replicas:<12} {'2m'}")
            return "\n".join(lines)

        if res_type in ["services", "service", "svc"]:
            svcs = list(self.services.values())
            if not all_ns:
                svcs = [s for s in svcs if s.namespace == ns]
            lines = [f"{'NAME':<20} {'TYPE':<16} {'CLUSTER-IP':<16} {'EXTERNAL-IP':<14} {'PORT(S)':<14} {'AGE'}"]
            for s in svcs:
                lines.append(f"{s.name:<20} {s.type:<16} {s.cluster_ip:<16} {s.external_ip:<14} {s.ports:<14} {'3d'}")
            return "\n".join(lines)

        if res_type in ["configmaps", "configmap", "cm"]:
            lines = [f"{'NAME':<25} {'DATA':<8} {'AGE'}"]
            for name, data in self.configmaps.items():
                lines.append(f"{name:<25} {len(data):<8} {'3d'}")
            return "\n".join(lines)

        return f"error: the server doesn't have a resource type \"{res_type}\""

    def run(self, args: List[str]) -> str:
        ns, clean_args, _ = self._parse_ns(args)
        if not clean_args:
            return "error: NAME is required for run"
        pod_name = clean_args[0]
        image = "nginx:alpine"
        port = "80"

        i = 1
        while i < len(clean_args):
            if clean_args[i].startswith("--image="):
                image = clean_args[i].split("=", 1)[1]
            elif clean_args[i] == "--image" and i + 1 < len(clean_args):
                image = clean_args[i + 1]
                i += 1
            elif clean_args[i].startswith("--port="):
                port = clean_args[i].split("=", 1)[1]
            elif clean_args[i] == "--port" and i + 1 < len(clean_args):
                port = clean_args[i + 1]
                i += 1
            i += 1

        pod = K8sPod(
            name=pod_name,
            namespace=ns,
            image=image,
            status="Running",
            ready="1/1",
            restarts=0,
            age="1s",
            ip=f"10.244.1.{random.randint(10, 99)}",
            labels={"run": pod_name},
            logs=[f"Starting {pod_name} container with image {image}", "Ready for requests."],
        )
        self.pods[pod_name] = pod
        return f"pod/{pod_name} created"

    def create(self, args: List[str]) -> str:
        ns, clean_args, _ = self._parse_ns(args)
        if not clean_args:
            return "error: resource type required"
        res_type = clean_args[0].lower()

        if res_type == "deployment":
            if len(clean_args) < 2:
                return "error: NAME is required for deployment"
            deploy_name = clean_args[1]
            image = "nginx:latest"
            replicas = 1

            i = 2
            while i < len(clean_args):
                if clean_args[i].startswith("--image="):
                    image = clean_args[i].split("=", 1)[1]
                elif clean_args[i] == "--image" and i + 1 < len(clean_args):
                    image = clean_args[i + 1]
                    i += 1
                elif clean_args[i].startswith("--replicas="):
                    replicas = int(clean_args[i].split("=", 1)[1])
                elif clean_args[i] == "--replicas" and i + 1 < len(clean_args):
                    replicas = int(clean_args[i + 1])
                    i += 1
                i += 1

            deploy = K8sDeployment(name=deploy_name, namespace=ns, image=image, replicas=replicas, ready_replicas=replicas)
            self.deployments[deploy_name] = deploy

            # Automatically create managed pods
            for _ in range(replicas):
                pod_rand_id = "".join(random.choices("0123456789abcdef", k=5))
                pname = f"{deploy_name}-{pod_rand_id}"
                self.pods[pname] = K8sPod(
                    name=pname,
                    namespace=ns,
                    image=image,
                    labels={"app": deploy_name},
                    logs=[f"Deployment pod {pname} started"],
                )
            return f"deployment.apps/{deploy_name} created"

        if res_type == "configmap":
            if len(clean_args) < 2:
                return "error: NAME is required for configmap"
            cm_name = clean_args[1]
            data = {}
            for a in clean_args[2:]:
                if a.startswith("--from-literal="):
                    lit = a.split("=", 1)[1]
                    if "=" in lit:
                        k, v = lit.split("=", 1)
                        data[k] = v
            self.configmaps[cm_name] = data
            return f"configmap/{cm_name} created"

        return f"error: unknown resource type \"{res_type}\""

    def scale(self, args: List[str]) -> str:
        ns, clean_args, _ = self._parse_ns(args)
        if len(clean_args) < 2:
            return "error: resource type and name required"
        target_name = clean_args[1]
        replicas = 1

        for a in clean_args:
            if a.startswith("--replicas="):
                try:
                    replicas = int(a.split("=")[1])
                except ValueError:
                    pass

        if target_name in self.deployments:
            d = self.deployments[target_name]
            d.replicas = replicas
            d.ready_replicas = replicas
            return f"deployment.apps/{target_name} scaled"
        return f"Error from server (NotFound): deployments.apps \"{target_name}\" not found"

    def expose(self, args: List[str]) -> str:
        ns, clean_args, _ = self._parse_ns(args)
        if len(clean_args) < 2:
            return "error: resource and name required"
        target_name = clean_args[1]
        port = "80"
        target_port = "80"
        svc_type = "ClusterIP"

        i = 2
        while i < len(clean_args):
            if clean_args[i].startswith("--port="):
                port = clean_args[i].split("=")[1]
            elif clean_args[i].startswith("--target-port="):
                target_port = clean_args[i].split("=")[1]
            elif clean_args[i].startswith("--type="):
                svc_type = clean_args[i].split("=")[1]
            i += 1

        svc = K8sService(
            name=target_name,
            namespace=ns,
            type=svc_type,
            cluster_ip=f"10.96.{random.randint(1, 250)}.{random.randint(1, 250)}",
            ports=f"{port}/{target_port}/TCP",
        )
        self.services[target_name] = svc
        return f"service/{target_name} exposed"

    def logs(self, args: List[str]) -> str:
        ns, clean_args, _ = self._parse_ns(args)
        if not clean_args:
            return "error: resource name required"
        name = clean_args[0]
        if name in self.pods:
            return "\n".join(self.pods[name].logs)
        for p in self.pods.values():
            if p.name.startswith(name):
                return "\n".join(p.logs)
        return f"Error from server (NotFound): pods \"{name}\" not found"

    def describe(self, args: List[str]) -> str:
        ns, clean_args, _ = self._parse_ns(args)
        if len(clean_args) < 2:
            return "error: resource type and name required"
        res_type, name = clean_args[0].lower(), clean_args[1]

        if res_type in ["pod", "pods"]:
            if name in self.pods:
                p = self.pods[name]
                return (
                    f"Name:         {p.name}\n"
                    f"Namespace:    {p.namespace}\n"
                    f"Priority:     0\n"
                    f"Node:         {p.node}/192.168.1.10\n"
                    f"Status:       {p.status}\n"
                    f"IP:           {p.ip}\n"
                    f"Containers:\n"
                    f"  {p.name}:\n"
                    f"    Image:          {p.image}\n"
                    f"    State:          Running\n"
                    f"    Ready:          True\n"
                    f"    Restart Count:  {p.restarts}\n"
                    f"Events:\n"
                    f"  Type    Reason     Age   From               Message\n"
                    f"  ----    ------     ----  ----               -------\n"
                    f"  Normal  Scheduled  1m    default-scheduler  Successfully assigned {p.namespace}/{p.name} to {p.node}\n"
                    f"  Normal  Pulled     1m    kubelet            Container image \"{p.image}\" already present on machine\n"
                    f"  Normal  Created    1m    kubelet            Created container {p.name}\n"
                    f"  Normal  Started    1m    kubelet            Started container {p.name}"
                )
            return f"Error from server (NotFound): pods \"{name}\" not found"

        return f"Describe output for {res_type}/{name} [OK]"

    def delete(self, args: List[str]) -> str:
        ns, clean_args, _ = self._parse_ns(args)
        if len(clean_args) < 2:
            return "error: resource type and name required"
        res_type, name = clean_args[0].lower(), clean_args[1]

        if res_type in ["pod", "pods"] and name in self.pods:
            del self.pods[name]
            return f"pod \"{name}\" deleted"
        if res_type in ["deployment", "deploy"] and name in self.deployments:
            del self.deployments[name]
            return f"deployment.apps \"{name}\" deleted"
        if res_type in ["service", "svc"] and name in self.services:
            del self.services[name]
            return f"service \"{name}\" deleted"
        return f"Error from server (NotFound): {res_type} \"{name}\" not found"

    def rollout(self, args: List[str]) -> str:
        if len(args) > 1 and args[0] == "status":
            return f"deployment \"{args[1]}\" successfully rolled out"
        return "rollout [status|restart|history] resource"

    def top(self, args: List[str]) -> str:
        if args and args[0] in ["pods", "pod"]:
            lines = [f"{'NAME':<32} {'CPU(cores)':<12} {'MEMORY(bytes)'}"]
            for p in self.pods.values():
                lines.append(f"{p.name:<32} {'12m':<12} {'24Mi'}")
            return "\n".join(lines)
        return (
            f"{'NAME':<24} {'CPU(cores)':<12} {'CPU%':<8} {'MEMORY(bytes)':<15} {'MEMORY%'}\n"
            f"{'k8s-control-plane':<24} {'245m':<12} {'12%':<8} {'1420Mi':<15} {'35%'}\n"
            f"{'k8s-worker-01':<24} {'180m':<12} {'9%':<8} {'980Mi':<15} {'24%'}\n"
            f"{'k8s-worker-02':<24} {'165m':<12} {'8%':<8} {'910Mi':<15} {'22%'}"
        )

    def k8s_exec(self, args: List[str]) -> str:
        return "Connected to pod container. Output: { status: 'healthy' }"
