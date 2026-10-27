"""Virtual Docker Engine: Images, Containers, Volumes, and Networks."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DockerImage:
    repository: str
    tag: str
    image_id: str
    created: str
    size: str


@dataclass
class DockerContainer:
    id: str
    name: str
    image: str
    command: str
    status: str  # "Up 2 minutes", "Exited (0) 5 minutes ago", "Created"
    is_running: bool = True
    ports: str = ""
    env: Dict[str, str] = field(default_factory=dict)
    volumes: List[str] = field(default_factory=list)
    network: str = "bridge"
    logs: List[str] = field(default_factory=list)


class DockerSimulator:
    """Simulates Docker CLI commands and container lifecycle in-memory."""

    def __init__(self):
        self.images: Dict[str, DockerImage] = {}
        self.containers: Dict[str, DockerContainer] = {}
        self.networks: Dict[str, dict] = {}
        self.volumes: Dict[str, dict] = {}
        self.reset_default_state()

    def reset_default_state(self):
        self.images = {
            "nginx:alpine": DockerImage("nginx", "alpine", "a1b2c3d4e5f6", "2 weeks ago", "23.4MB"),
            "postgres:15": DockerImage("postgres", "15", "b2c3d4e5f6a1", "3 weeks ago", "379MB"),
            "redis:7-alpine": DockerImage("redis", "7-alpine", "c3d4e5f6a1b2", "1 month ago", "32.1MB"),
            "node:20-alpine": DockerImage("node", "20-alpine", "d4e5f6a1b2c3", "5 days ago", "180MB"),
            "datadog/agent:latest": DockerImage("datadog/agent", "latest", "e5f6a1b2c3d4", "3 days ago", "850MB"),
        }

        self.networks = {
            "bridge": {"id": "11aa22bb33cc", "driver": "bridge", "scope": "local"},
            "host": {"id": "44dd55ee66ff", "driver": "host", "scope": "local"},
            "none": {"id": "778899aabbcc", "driver": "null", "scope": "local"},
        }

        self.volumes = {
            "db_data": {"driver": "local", "scope": "local"},
        }

        self.containers = {
            "7c24a91f03b2": DockerContainer(
                id="7c24a91f03b2",
                name="postgres-db",
                image="postgres:15",
                command='docker-entrypoint.sh "postgres"',
                status="Up 45 minutes",
                is_running=True,
                ports="0.0.0.0:5432->5432/tcp",
                network="bridge",
                logs=[
                    "PostgreSQL Database directory appears to contain a database; Skipping initialization",
                    "server starting",
                    "listening on IPv4 address '0.0.0.0', port 5432",
                    "database system is ready to accept connections",
                ],
            )
        }

    def _generate_id(self) -> str:
        return "".join(random.choices("0123456789abcdef", k=12))

    def _find_container(self, name_or_id: str) -> Optional[DockerContainer]:
        for c in self.containers.values():
            if c.name == name_or_id or c.id.startswith(name_or_id):
                return c
        return None

    def execute(self, args: List[str]) -> str:
        if not args:
            return self.help([])
        subcmd = args[0]
        subargs = args[1:]

        handlers = {
            "ps": self.ps,
            "run": self.run,
            "stop": self.stop,
            "start": self.start,
            "restart": self.restart,
            "rm": self.rm,
            "logs": self.logs,
            "exec": self.docker_exec,
            "images": self.docker_images,
            "pull": self.pull,
            "rmi": self.rmi,
            "build": self.build,
            "network": self.network,
            "volume": self.volume,
            "stats": self.stats,
            "version": self.version,
            "help": self.help,
            "--help": self.help,
        }

        handler = handlers.get(subcmd)
        if handler:
            return handler(subargs)
        return f"docker: '{subcmd}' is not a docker command. See 'docker --help'"

    def version(self, args: List[str]) -> str:
        return (
            "Client: Docker Engine - Community\n"
            " Version:           27.0.3\n"
            " API version:       1.46\n"
            " Go version:        go1.22.4\n"
            " OS/Arch:           linux/amd64\n\n"
            "Server: Docker Engine - Community\n"
            " Engine:\n"
            "  Version:          27.0.3\n"
            "  API version:      1.46 (minimum version 1.24)\n"
            "  Operating System: Ubuntu 24.04 LTS"
        )

    def help(self, args: List[str]) -> str:
        return (
            "Usage:  docker [OPTIONS] COMMAND\n\n"
            "Management Commands:\n"
            "  container   Manage containers\n"
            "  image       Manage images\n"
            "  network     Manage networks\n"
            "  volume      Manage volumes\n\n"
            "Commands:\n"
            "  build       Build an image from a Dockerfile\n"
            "  exec        Execute a command in a running container\n"
            "  images      List images\n"
            "  logs        Fetch the logs of a container\n"
            "  ps          List containers\n"
            "  pull        Download an image from a registry\n"
            "  rm          Remove one or more containers\n"
            "  rmi         Remove one or more images\n"
            "  run         Create and run a new container from an image\n"
            "  start       Start one or more stopped containers\n"
            "  stats       Display a live stream of container(s) resource usage statistics\n"
            "  stop        Stop one or more running containers"
        )

    def ps(self, args: List[str]) -> str:
        show_all = "-a" in args or "--all" in args
        target_list = list(self.containers.values())
        if not show_all:
            target_list = [c for c in target_list if c.is_running]

        if not target_list:
            return f"{'CONTAINER ID':<14} {'IMAGE':<20} {'COMMAND':<20} {'CREATED':<15} {'STATUS':<20} {'PORTS':<25} {'NAMES'}"

        lines = [f"{'CONTAINER ID':<14} {'IMAGE':<20} {'COMMAND':<20} {'CREATED':<15} {'STATUS':<20} {'PORTS':<25} {'NAMES'}"]
        for c in target_list:
            cmd_trunc = (c.command[:17] + "...") if len(c.command) > 20 else c.command
            status_color = "[bold green]" + c.status + "[/]" if c.is_running else "[dim]" + c.status + "[/]"
            lines.append(f"{c.id:<14} {c.image:<20} {cmd_trunc:<20} {'Just now':<15} {status_color:<29} {c.ports:<25} {c.name}")
        return "\n".join(lines)

    def run(self, args: List[str]) -> str:
        detach = "-d" in args or "--detach" in args
        name: Optional[str] = None
        ports: List[str] = []
        volumes: List[str] = []
        network: str = "bridge"
        env: Dict[str, str] = {}
        image_name: Optional[str] = None
        custom_cmd: List[str] = []

        i = 0
        while i < len(args):
            arg = args[i]
            if arg in ["-d", "--detach"]:
                detach = True
                i += 1
            elif arg == "--name" and i + 1 < len(args):
                name = args[i + 1]
                i += 2
            elif arg in ["-p", "--publish"] and i + 1 < len(args):
                ports.append(args[i + 1])
                i += 2
            elif arg in ["-v", "--volume"] and i + 1 < len(args):
                volumes.append(args[i + 1])
                i += 2
            elif arg in ["-e", "--env"] and i + 1 < len(args):
                env_spec = args[i + 1]
                if "=" in env_spec:
                    k, v = env_spec.split("=", 1)
                    env[k] = v
                i += 2
            elif arg == "--network" and i + 1 < len(args):
                network = args[i + 1]
                i += 2
            elif arg.startswith("-"):
                i += 1
            else:
                if image_name is None:
                    image_name = arg
                else:
                    custom_cmd.append(arg)
                i += 1

        if not image_name:
            return "docker run: requires at least 1 image argument"

        # Check image availability
        full_image = image_name if ":" in image_name else f"{image_name}:latest"
        if full_image not in self.images and image_name not in self.images:
            # Auto-pull image simulation
            self.images[full_image] = DockerImage(
                repository=image_name.split(":")[0],
                tag=image_name.split(":")[1] if ":" in image_name else "latest",
                image_id=self._generate_id(),
                created="Just now",
                size="45MB",
            )

        cid = self._generate_id()
        cname = name or f"nervous_{random.choice(['curie', 'hopper', 'turing', 'ritchie', 'lovelace'])}"

        # Check duplicate container name
        if self._find_container(cname):
            return f"docker: Error response from daemon: Conflict. The container name \"/{cname}\" is already in use by container \"{self._find_container(cname).id}\"."

        port_str = ", ".join([f"0.0.0.0:{p}->{p.split(':')[1] if ':' in p else p}/tcp" for p in ports])
        cmd_str = " ".join(custom_cmd) or "/docker-entrypoint.sh"

        logs = [
            f"Container {cname} initialized",
            f"Running with image {full_image}",
        ]
        if "nginx" in full_image:
            logs.append("Configuration complete; ready for connections on port 80")
        elif "redis" in full_image:
            logs.append("Ready to accept connections tcp")

        container = DockerContainer(
            id=cid,
            name=cname,
            image=full_image,
            command=cmd_str,
            status="Up 1 second",
            is_running=True,
            ports=port_str,
            env=env,
            volumes=volumes,
            network=network,
            logs=logs,
        )
        self.containers[cid] = container

        if detach:
            return cid
        else:
            return "\n".join(logs)

    def stop(self, args: List[str]) -> str:
        if not args:
            return "docker stop requires at least 1 container argument"
        output = []
        for a in args:
            c = self._find_container(a)
            if not c:
                return f"Error response from daemon: No such container: {a}"
            c.is_running = False
            c.status = "Exited (0) Just now"
            output.append(c.name)
        return "\n".join(output)

    def start(self, args: List[str]) -> str:
        if not args:
            return "docker start requires at least 1 container argument"
        output = []
        for a in args:
            c = self._find_container(a)
            if not c:
                return f"Error response from daemon: No such container: {a}"
            c.is_running = True
            c.status = "Up 1 second"
            output.append(c.name)
        return "\n".join(output)

    def restart(self, args: List[str]) -> str:
        self.stop(args)
        return self.start(args)

    def rm(self, args: List[str]) -> str:
        force = "-f" in args or "--force" in args
        targets = [a for a in args if not a.startswith("-")]
        if not targets:
            return "docker rm requires at least 1 container argument"
        output = []
        for t in targets:
            c = self._find_container(t)
            if not c:
                return f"Error response from daemon: No such container: {t}"
            if c.is_running and not force:
                return f"Error response from daemon: You cannot remove a running container {c.id}. Stop the container before attempting removal or force remove."
            del self.containers[c.id]
            output.append(c.name)
        return "\n".join(output)

    def logs(self, args: List[str]) -> str:
        tail = 100
        targets = []
        i = 0
        while i < len(args):
            if args[i] == "--tail" and i + 1 < len(args):
                try:
                    tail = int(args[i + 1])
                except ValueError:
                    pass
                i += 2
            elif args[i] in ["-f", "--follow"]:
                i += 1
            else:
                targets.append(args[i])
                i += 1

        if not targets:
            return "docker logs requires at least 1 argument."
        c = self._find_container(targets[0])
        if not c:
            return f"Error response from daemon: No such container: {targets[0]}"
        return "\n".join(c.logs[-tail:])

    def docker_exec(self, args: List[str]) -> str:
        pos_args = [a for a in args if not a.startswith("-")]
        if len(pos_args) < 2:
            return "docker exec: requires container and command"
        c = self._find_container(pos_args[0])
        if not c:
            return f"Error response from daemon: No such container: {pos_args[0]}"
        if not c.is_running:
            return f"Error response from daemon: Container {c.id} is not running"

        cmd = " ".join(pos_args[1:])
        if cmd in ["env", "printenv"]:
            lines = [f"{k}={v}" for k, v in c.env.items()]
            lines.extend(["HOSTNAME=" + c.id[:12], "SHLVL=1", "HOME=/root", "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"])
            return "\n".join(lines)
        elif cmd in ["sh", "bash"]:
            return f"Connected to {c.name} container shell (/bin/sh). Type commands to interact."
        elif "cat" in cmd:
            return "app configuration file inside container content: { \"ready\": true }"
        return f"Executing '{cmd}' in container {c.name}... [OK]"

    def docker_images(self, args: List[str]) -> str:
        lines = [f"{'REPOSITORY':<25} {'TAG':<15} {'IMAGE ID':<15} {'CREATED':<18} {'SIZE'}"]
        for img in self.images.values():
            lines.append(f"{img.repository:<25} {img.tag:<15} {img.image_id:<15} {img.created:<18} {img.size}")
        return "\n".join(lines)

    def pull(self, args: List[str]) -> str:
        if not args:
            return "docker pull requires at least 1 argument"
        name = args[0]
        full_name = name if ":" in name else f"{name}:latest"
        parts = full_name.split(":")
        img_id = self._generate_id()
        self.images[full_name] = DockerImage(parts[0], parts[1], img_id, "Just now", "42.8MB")
        return (
            f"Using default tag: {parts[1]}\n"
            f"{parts[1]}: Pulling from library/{parts[0]}\n"
            "a2abf6c4d29d: Pull complete\n"
            "Digest: sha256:7f08e434f603c40d048454b8ec80fa19574d6b63d9\n"
            f"Status: Downloaded newer image for {full_name}"
        )

    def rmi(self, args: List[str]) -> str:
        targets = [a for a in args if not a.startswith("-")]
        if not targets:
            return "docker rmi requires at least 1 argument"
        output = []
        for t in targets:
            found = False
            for k in list(self.images.keys()):
                if k == t or self.images[k].image_id.startswith(t):
                    del self.images[k]
                    output.append(f"Untagged: {k}\nDeleted: sha256:{t}")
                    found = True
                    break
            if not found:
                return f"Error response from daemon: No such image: {t}"
        return "\n".join(output)

    def build(self, args: List[str]) -> str:
        tag = "custom-app:latest"
        if "-t" in args:
            idx = args.index("-t")
            if idx + 1 < len(args):
                tag = args[idx + 1]
        img_id = self._generate_id()
        parts = tag.split(":") if ":" in tag else [tag, "latest"]
        self.images[tag] = DockerImage(parts[0], parts[1], img_id, "Just now", "89.2MB")
        return (
            f"[+] Building 2.1s (6/6) FINISHED\n"
            f" => [internal] load build definition from Dockerfile\n"
            f" => [1/3] FROM docker.io/library/alpine:latest\n"
            f" => [2/3] RUN apk add --no-cache curl ca-certificates\n"
            f" => [3/3] COPY . /app\n"
            f" => exporting to image\n"
            f" => => naming to docker.io/library/{tag}\n"
            f"Successfully built {img_id}\n"
            f"Successfully tagged {tag}"
        )

    def network(self, args: List[str]) -> str:
        if not args or args[0] == "ls":
            lines = [f"{'NETWORK ID':<15} {'NAME':<20} {'DRIVER':<10} {'SCOPE'}"]
            for name, net in self.networks.items():
                lines.append(f"{net['id']:<15} {name:<20} {net['driver']:<10} {net['scope']}")
            return "\n".join(lines)
        if args[0] == "create" and len(args) > 1:
            net_name = args[1]
            if net_name in self.networks:
                return f"Error response from daemon: network with name {net_name} already exists"
            self.networks[net_name] = {"id": self._generate_id(), "driver": "bridge", "scope": "local"}
            return self.networks[net_name]["id"]
        if args[0] == "inspect" and len(args) > 1:
            net_name = args[1]
            if net_name not in self.networks:
                return f"Error: No such network: {net_name}"
            import json
            return json.dumps([{"Name": net_name, "Driver": "bridge", "Scope": "local"}], indent=2)
        return "docker network [create|ls|inspect|rm] [OPTIONS]"

    def volume(self, args: List[str]) -> str:
        if not args or args[0] == "ls":
            lines = [f"{'DRIVER':<12} {'VOLUME NAME'}"]
            for name, vol in self.volumes.items():
                lines.append(f"{vol['driver']:<12} {name}")
            return "\n".join(lines)
        if args[0] == "create" and len(args) > 1:
            vname = args[1]
            self.volumes[vname] = {"driver": "local", "scope": "local"}
            return vname
        return "docker volume [create|ls|inspect|rm] [OPTIONS]"

    def stats(self, args: List[str]) -> str:
        lines = [f"{'CONTAINER ID':<14} {'NAME':<15} {'CPU %':<8} {'MEM USAGE / LIMIT':<22} {'MEM %':<8} {'NET I/O'}"]
        for c in self.containers.values():
            if c.is_running:
                lines.append(f"{c.id:<14} {c.name:<15} {'0.15%':<8} {'24.8MiB / 8GiB':<22} {'0.30%':<8} {'1.2kB / 850B'}")
        return "\n".join(lines)
