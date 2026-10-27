"""Virtual Linux Engine: Filesystem, Processes, and POSIX Commands."""
from __future__ import annotations

import posixpath
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class VNode:
    name: str
    is_dir: bool = False
    content: str = ""
    perms: str = "-rw-r--r--"
    owner: str = "devops"
    group: str = "devops"
    children: Dict[str, VNode] = field(default_factory=dict)


@dataclass
class VProcess:
    pid: int
    user: str
    cpu: float
    mem: float
    command: str
    status: str = "S"  # S = Sleeping, R = Running, Z = Zombie


class LinuxSimulator:
    """Simulates a Linux shell environment with in-memory VFS and processes."""

    def __init__(self):
        self.root = VNode(name="", is_dir=True, perms="drwxr-xr-x", owner="root", group="root")
        self.cwd = "/home/devops"
        self.processes: Dict[int, VProcess] = {}
        self.env: Dict[str, str] = {
            "USER": "devops",
            "HOME": "/home/devops",
            "SHELL": "/bin/bash",
            "PATH": "/usr/local/bin:/usr/bin:/bin",
            "TERM": "xterm-256color",
        }
        self.reset_default_state()

    def reset_default_state(self):
        """Builds standard Linux directory hierarchy and starter files."""
        self.root.children.clear()
        self.cwd = "/home/devops"
        self.processes.clear()

        # Skeleton dirs
        for d in ["/bin", "/etc", "/var", "/var/log", "/home", "/home/devops", "/app", "/tmp", "/usr/bin"]:  # nosec B108
            self._mkdir_p(d)

        # Starter files
        self._write_file("/etc/hostname", "ops-lab-node1\n")
        self._write_file("/etc/os-release", 'NAME="Ubuntu"\nVERSION="24.04 LTS (Noble Numbat)"\nID=ubuntu\n')
        self._write_file(
            "/home/devops/welcome.txt",
            "Bem-vindo ao DevOpsHeroCLI!\nPratique comandos reais de DevOps aqui.\nUse 'help' para ver os atalhos.\n",
        )
        self._write_file(
            "/var/log/syslog",
            "Oct 26 10:00:01 ops-lab systemd[1]: Started Daily apt upgrade activities.\n"
            "Oct 26 10:14:22 ops-lab dockerd[1200]: Daemon has completed initialization\n"
            "Oct 26 10:15:00 ops-lab kernel: [    0.000000] Linux version 6.8.0-generic\n"
            "Oct 26 10:20:18 ops-lab app[3452]: [ERROR] Database connection failed at port 5432\n"
            "Oct 26 10:20:19 ops-lab app[3452]: [INFO] Retrying connection in 5s...\n",
        )

        # Starter processes
        self.processes = {
            1: VProcess(pid=1, user="root", cpu=0.0, mem=0.2, command="/sbin/init"),
            412: VProcess(pid=412, user="root", cpu=0.1, mem=1.1, command="/usr/bin/dockerd"),
            850: VProcess(pid=850, user="datadog", cpu=0.8, mem=2.4, command="/opt/datadog-agent/bin/agent/agent run"),
            1337: VProcess(pid=1337, user="devops", cpu=94.2, mem=18.5, command="python3 -m rogue_miner --threads 8"),
            2048: VProcess(pid=2048, user="postgres", cpu=0.2, mem=4.8, command="/usr/lib/postgresql/15/bin/postgres"),
        }

        # Starter systemd services
        self.services = {
            "nginx": {
                "desc": "A high performance web server and a reverse proxy server",
                "status": "active (running)",
                "enabled": False,
                "pid": 1120,
                "restarts": 0,
            },
            "postgresql": {
                "desc": "PostgreSQL RDBMS server",
                "status": "active (running)",
                "enabled": True,
                "pid": 2048,
                "restarts": 0,
            },
            "cron": {
                "desc": "Regular background program processing daemon",
                "status": "active (running)",
                "enabled": True,
                "pid": 320,
                "restarts": 0,
            },
            "datadog-agent": {
                "desc": "Datadog Agent",
                "status": "active (running)",
                "enabled": True,
                "pid": 850,
                "restarts": 0,
            },
            "ssh": {
                "desc": "OpenBSD Secure Shell server",
                "status": "active (running)",
                "enabled": True,
                "pid": 600,
                "restarts": 0,
            },
        }

        # Starter crontab
        self.crontab_entries = [
            "0 2 * * * /usr/local/bin/backup-db.sh",
            "*/15 * * * * /opt/monitoring/healthcheck.sh",
        ]

        # Starter users
        self.users = {
            "root": {"uid": 0, "gid": 0, "home": "/root", "shell": "/bin/bash", "groups": ["root"]},
            "devops": {"uid": 1000, "gid": 1000, "home": "/home/devops", "shell": "/bin/bash", "groups": ["devops", "sudo", "docker"]},
            "postgres": {"uid": 1001, "gid": 1001, "home": "/var/lib/postgresql", "shell": "/bin/bash", "groups": ["postgres"]},
        }

    def _resolve_path(self, path: str) -> str:
        if not path:
            return self.cwd
        path = path.strip()
        if path.startswith("~"):
            path = posixpath.join("/home/devops", path[1:].lstrip("/"))
        if not path.startswith("/"):
            path = posixpath.join(self.cwd, path)
        return posixpath.normpath(path)

    def _get_node(self, path: str) -> Optional[VNode]:
        norm = self._resolve_path(path)
        if norm == "/":
            return self.root
        parts = [p for p in norm.split("/") if p]
        curr = self.root
        for part in parts:
            if not curr.is_dir or part not in curr.children:
                return None
            curr = curr.children[part]
        return curr

    def _mkdir_p(self, path: str, perms: str = "drwxr-xr-x", owner: str = "devops", group: str = "devops") -> VNode:
        norm = self._resolve_path(path)
        if norm == "/":
            return self.root
        parts = [p for p in norm.split("/") if p]
        curr = self.root
        for part in parts:
            if part not in curr.children:
                curr.children[part] = VNode(name=part, is_dir=True, perms=perms, owner=owner, group=group)
            curr = curr.children[part]
        return curr

    def _write_file(self, path: str, content: str, mode: str = "w", perms: str = "-rw-r--r--") -> VNode:
        norm = self._resolve_path(path)
        parent_dir = posixpath.dirname(norm)
        filename = posixpath.basename(norm)
        parent_node = self._mkdir_p(parent_dir)

        if filename in parent_node.children:
            node = parent_node.children[filename]
            if mode == "a":
                node.content += content
            else:
                node.content = content
        else:
            node = VNode(name=filename, is_dir=False, content=content, perms=perms, owner="devops", group="devops")
            parent_node.children[filename] = node
        return node

    # Shell commands implementation
    def pwd(self, args: List[str]) -> str:
        return self.cwd

    def cd(self, args: List[str]) -> str:
        target = args[0] if args else "/home/devops"
        norm = self._resolve_path(target)
        node = self._get_node(norm)
        if not node:
            return f"cd: {target}: No such file or directory"
        if not node.is_dir:
            return f"cd: {target}: Not a directory"
        self.cwd = norm
        return ""

    def ls(self, args: List[str]) -> str:
        show_all = any(a in ["-a", "-la", "-al", "-lha", "-lah"] for a in args)
        long_format = any(a in ["-l", "-la", "-al", "-lh", "-lha", "-lah"] for a in args)

        target_paths = [a for a in args if not a.startswith("-")]
        target = target_paths[0] if target_paths else self.cwd
        node = self._get_node(target)
        if not node:
            return f"ls: cannot access '{target}': No such file or directory"

        if not node.is_dir:
            if long_format:
                return f"{node.perms} 1 {node.owner} {node.group} {len(node.content):>6} Oct 26 12:00 {node.name}"
            return node.name

        entries = sorted(node.children.keys())
        if show_all:
            entries = [".", ".."] + entries

        if not entries:
            return ""

        if long_format:
            lines = [f"total {len(node.children) * 4}"]
            for name in entries:
                if name == ".":
                    perms, size = "drwxr-xr-x", 4096
                    owner, group = node.owner, node.group
                elif name == "..":
                    perms, size = "drwxr-xr-x", 4096
                    owner, group = "root", "root"
                else:
                    child = node.children[name]
                    perms = child.perms
                    size = 4096 if child.is_dir else len(child.content)
                    owner, group = child.owner, child.group

                # Format name with color indicator
                disp_name = f"[bold cyan]{name}/[/]" if (name in [".", ".."] or node.children.get(name, node).is_dir) else name
                lines.append(f"{perms} 1 {owner:<8} {group:<8} {size:>6} Oct 26 12:00 {disp_name}")
            return "\n".join(lines)
        else:
            items = []
            for name in entries:
                if name in node.children and node.children[name].is_dir:
                    items.append(f"[bold cyan]{name}/[/]")
                else:
                    items.append(name)
            return "  ".join(items)

    def mkdir(self, args: List[str]) -> str:
        if not args:
            return "mkdir: missing operand"
        parents = "-p" in args
        targets = [a for a in args if not a.startswith("-")]
        if not targets:
            return "mkdir: missing operand"

        for target in targets:
            norm = self._resolve_path(target)
            parent_dir = posixpath.dirname(norm)
            basename = posixpath.basename(norm)
            pnode = self._get_node(parent_dir)
            if not pnode:
                if parents:
                    self._mkdir_p(norm)
                else:
                    return f"mkdir: cannot create directory '{target}': No such file or directory"
            else:
                if basename in pnode.children:
                    if not parents:
                        return f"mkdir: cannot create directory '{target}': File exists"
                else:
                    pnode.children[basename] = VNode(name=basename, is_dir=True, perms="drwxr-xr-x")
        return ""

    def touch(self, args: List[str]) -> str:
        if not args:
            return "touch: missing file operand"
        for target in args:
            if target.startswith("-"):
                continue
            norm = self._resolve_path(target)
            node = self._get_node(norm)
            if not node:
                self._write_file(norm, "")
        return ""

    def cat(self, args: List[str]) -> str:
        if not args:
            return ""
        outputs = []
        for target in args:
            if target.startswith("-"):
                continue
            node = self._get_node(target)
            if not node:
                return f"cat: {target}: No such file or directory"
            if node.is_dir:
                return f"cat: {target}: Is a directory"
            outputs.append(node.content.rstrip("\n"))
        return "\n".join(outputs)

    def head(self, args: List[str]) -> str:
        n = 10
        files = []
        i = 0
        while i < len(args):
            if args[i] == "-n" and i + 1 < len(args):
                try:
                    n = int(args[i + 1])
                except ValueError:
                    pass
                i += 2
            elif args[i].startswith("-n"):
                try:
                    n = int(args[i][2:])
                except ValueError:
                    pass
                i += 1
            else:
                files.append(args[i])
                i += 1
        if not files:
            return "head: missing file"
        node = self._get_node(files[0])
        if not node or node.is_dir:
            return f"head: cannot open '{files[0]}': No such file"
        lines = node.content.splitlines()[:n]
        return "\n".join(lines)

    def tail(self, args: List[str]) -> str:
        n = 10
        files = []
        i = 0
        while i < len(args):
            if args[i] in ["-n"] and i + 1 < len(args):
                try:
                    n = int(args[i + 1])
                except ValueError:
                    pass
                i += 2
            elif args[i].startswith("-n"):
                try:
                    n = int(args[i][2:])
                except ValueError:
                    pass
                i += 1
            elif args[i] in ["-f", "--follow"]:
                i += 1
            else:
                files.append(args[i])
                i += 1
        if not files:
            return "tail: missing file"
        node = self._get_node(files[0])
        if not node or node.is_dir:
            return f"tail: cannot open '{files[0]}': No such file"
        lines = node.content.splitlines()[-n:]
        return "\n".join(lines)

    def grep(self, args: List[str], pipe_input: Optional[str] = None) -> str:
        ignore_case = "-i" in args
        invert = "-v" in args
        pos_args = [a for a in args if not a.startswith("-")]

        if not pos_args:
            return "grep: search pattern required"
        pattern = pos_args[0]
        text = ""

        if len(pos_args) > 1:
            node = self._get_node(pos_args[1])
            if not node or node.is_dir:
                return f"grep: {pos_args[1]}: No such file"
            text = node.content
        elif pipe_input is not None:
            text = pipe_input
        else:
            return ""

        flags = re.IGNORECASE if ignore_case else 0
        regex = re.compile(re.escape(pattern), flags)

        matching_lines = []
        for line in text.splitlines():
            is_match = bool(regex.search(line))
            if invert:
                is_match = not is_match
            if is_match:
                # Highlight match
                if not invert and not ignore_case:
                    line_hl = line.replace(pattern, f"[bold red]{pattern}[/]")
                elif not invert:
                    line_hl = regex.sub(lambda m: f"[bold red]{m.group(0)}[/]", line)
                else:
                    line_hl = line
                matching_lines.append(line_hl)

        return "\n".join(matching_lines)

    def rm(self, args: List[str]) -> str:
        if not args:
            return "rm: missing operand"
        recursive = any(a in ["-r", "-rf", "-fr", "-R"] for a in args)
        targets = [a for a in args if not a.startswith("-")]

        for target in targets:
            norm = self._resolve_path(target)
            if norm == "/":
                return "rm: it is dangerous to operate recursively on '/'"
            parent_dir = posixpath.dirname(norm)
            basename = posixpath.basename(norm)
            pnode = self._get_node(parent_dir)
            if not pnode or basename not in pnode.children:
                if "-f" not in args and "-rf" not in args:
                    return f"rm: cannot remove '{target}': No such file or directory"
                continue
            child = pnode.children[basename]
            if child.is_dir and not recursive:
                return f"rm: cannot remove '{target}': Is a directory"
            del pnode.children[basename]
        return ""

    def cp(self, args: List[str]) -> str:
        targets = [a for a in args if not a.startswith("-")]
        if len(targets) < 2:
            return "cp: missing destination file operand"
        src_path, dst_path = targets[0], targets[1]
        src_node = self._get_node(src_path)
        if not src_node:
            return f"cp: cannot stat '{src_path}': No such file or directory"
        if src_node.is_dir:
            return f"cp: -r not specified; omitting directory '{src_path}'"

        dst_norm = self._resolve_path(dst_path)
        dst_node = self._get_node(dst_norm)
        if dst_node and dst_node.is_dir:
            dst_norm = posixpath.join(dst_norm, src_node.name)

        self._write_file(dst_norm, src_node.content, perms=src_node.perms)
        return ""

    def mv(self, args: List[str]) -> str:
        targets = [a for a in args if not a.startswith("-")]
        if len(targets) < 2:
            return "mv: missing destination file operand"
        src_path, dst_path = targets[0], targets[1]
        src_norm = self._resolve_path(src_path)
        src_node = self._get_node(src_norm)
        if not src_node:
            return f"mv: cannot stat '{src_path}': No such file or directory"

        src_parent = self._get_node(posixpath.dirname(src_norm))
        src_name = posixpath.basename(src_norm)

        dst_norm = self._resolve_path(dst_path)
        dst_node = self._get_node(dst_norm)
        if dst_node and dst_node.is_dir:
            dst_norm = posixpath.join(dst_norm, src_name)

        dst_parent = self._mkdir_p(posixpath.dirname(dst_norm))
        dst_name = posixpath.basename(dst_norm)
        src_node.name = dst_name
        dst_parent.children[dst_name] = src_node

        if src_parent and src_name in src_parent.children:
            del src_parent.children[src_name]
        return ""

    def chmod(self, args: List[str]) -> str:
        if len(args) < 2:
            return "chmod: missing operand"
        mode_str, target = args[0], args[1]
        node = self._get_node(target)
        if not node:
            return f"chmod: cannot access '{target}': No such file or directory"

        # Basic octal support: 755, 644, 600, 777
        octal_map = {
            "755": "rwxr-xr-x",
            "644": "rw-r--r--",
            "600": "rw-------",
            "700": "rwx------",
            "777": "rwxrwxrwx",
            "+x": "rwxr-xr-x",
        }
        prefix = "d" if node.is_dir else "-"
        if mode_str in octal_map:
            node.perms = prefix + octal_map[mode_str]
        elif mode_str.isdigit() and len(mode_str) == 3:
            node.perms = f"{prefix}rw-r--r--"
        return ""

    def chown(self, args: List[str]) -> str:
        if len(args) < 2:
            return "chown: missing operand"
        spec, target = args[0], args[1]
        node = self._get_node(target)
        if not node:
            return f"chown: cannot access '{target}': No such file or directory"
        parts = spec.split(":")
        node.owner = parts[0]
        if len(parts) > 1:
            node.group = parts[1]
        return ""

    def ps(self, args: List[str]) -> str:
        lines = [f"{'USER':<10} {'PID':>6} {'%CPU':>5} {'%MEM':>5} {'STAT':>5} {'COMMAND'}"]
        for p in sorted(self.processes.values(), key=lambda x: x.pid):
            lines.append(f"{p.user:<10} {p.pid:>6} {p.cpu:>5.1f} {p.mem:>5.1f} {p.status:>5} {p.command}")
        return "\n".join(lines)

    def kill(self, args: List[str]) -> str:
        if not args:
            return "kill: usage: kill [-s sigspec | -n signum | -sigspec] pid | jobspec ... or kill -l [sigspec]"
        pids = []
        for a in args:
            if not a.startswith("-"):
                try:
                    pids.append(int(a))
                except ValueError:
                    pass
        if not pids:
            return "kill: pid required"
        for pid in pids:
            if pid in self.processes:
                del self.processes[pid]
            else:
                return f"kill: ({pid}) - No such process"
        return ""

    def df(self, args: List[str]) -> str:
        return (
            "Filesystem     1K-blocks      Used Available Use% Mounted on\n"
            "/dev/root       30364964   5892408  24455824  20% /\n"
            "tmpfs            4032128         0   4032128   0% /dev/shm\n"
            "/dev/nvme0n1p1    523248      6216    517032   2% /boot/efi"
        )

    def free(self, args: List[str]) -> str:
        return (
            "               total        used        free      shared  buff/cache   available\n"
            "Mem:            8192        2410        3580          48        2202        5480\n"
            "Swap:           2048           0        2048"
        )

    def curl(self, args: List[str]) -> str:
        if not args:
            return "curl: try 'curl --help' for more information"
        if "-I" in args or "--head" in args:
            return (
                "HTTP/1.1 200 OK\n"
                "Server: nginx/1.25.4\n"
                "Date: Sun, 26 Oct 2026 21:50:00 GMT\n"
                "Content-Type: text/html\n"
                "Content-Length: 615\n"
                "Connection: keep-alive"
            )
        return (
            "<!DOCTYPE html>\n<html>\n<head><title>Welcome to Nginx</title></head>\n"
            "<body><h1>DevOpsHeroCLI Web Server Running!</h1></body>\n</html>"
        )

    # --- Sysadmin Basic Handlers ---

    def systemctl(self, args: List[str]) -> str:
        if not args:
            return "systemctl [command] [name...]"
        action = args[0]
        services = args[1:] if len(args) > 1 else []

        if action == "status":
            if not services:
                return "systemctl status requires service name"
            sname = services[0].replace(".service", "")
            if sname not in self.services:
                return f"Unit {sname}.service could not be found."
            svc = self.services[sname]
            st_color = "[bold green]active (running)[/]" if "active" in svc["status"] else "[bold red]inactive (dead)[/]"
            en_str = "enabled" if svc["enabled"] else "disabled"
            return (
                f"● {sname}.service - {svc['desc']}\n"
                f"     Loaded: loaded (/lib/systemd/system/{sname}.service; {en_str}; vendor preset: enabled)\n"
                f"     Active: {st_color} since Sun 2026-10-26 21:00:00 UTC; 45min ago\n"
                f"   Main PID: {svc['pid']} ({sname})\n"
                f"      Tasks: 4 (limit: 9481)\n"
                f"     Memory: 24.2M\n"
                f"        CPU: 180ms\n"
                f"     CGroup: /system.slice/{sname}.service\n"
                f"             └─{svc['pid']} /usr/sbin/{sname}"
            )
        elif action == "restart":
            if not services:
                return "systemctl restart requires service name"
            sname = services[0].replace(".service", "")
            if sname in self.services:
                self.services[sname]["status"] = "active (running)"
                self.services[sname]["restarts"] += 1
                return ""
            return f"Failed to restart {sname}.service: Unit not found."
        elif action == "stop":
            if not services:
                return "systemctl stop requires service name"
            sname = services[0].replace(".service", "")
            if sname in self.services:
                self.services[sname]["status"] = "inactive (dead)"
                return ""
            return f"Unit {sname}.service not found."
        elif action == "start":
            if not services:
                return "systemctl start requires service name"
            sname = services[0].replace(".service", "")
            if sname in self.services:
                self.services[sname]["status"] = "active (running)"
                return ""
            return f"Unit {sname}.service not found."
        elif action == "enable":
            if not services:
                return "systemctl enable requires service name"
            sname = services[0].replace(".service", "")
            if sname in self.services:
                self.services[sname]["enabled"] = True
                return (
                    f"Created symlink /etc/systemd/system/multi-user.target.wants/{sname}.service → "
                    f"/lib/systemd/system/{sname}.service."
                )
            return f"Unit {sname}.service not found."
        return f"Unknown systemctl command '{action}'"

    def journalctl(self, args: List[str]) -> str:
        sname = "system"
        if "-u" in args:
            idx = args.index("-u")
            if idx + 1 < len(args):
                sname = args[idx + 1].replace(".service", "")
        return (
            f"-- Boot 45bf13c8e768407bb06399a9b6c0e5a1 --\n"
            f"Oct 26 21:00:01 ops-lab systemd[1]: Starting {sname}.service...\n"
            f"Oct 26 21:00:02 ops-lab {sname}[1120]: Server listening on 0.0.0.0:80\n"
            f"Oct 26 21:00:02 ops-lab systemd[1]: Started {sname}.service.\n"
            f"Oct 26 21:15:30 ops-lab {sname}[1120]: Configuration reloaded successfully"
        )

    def crontab(self, args: List[str]) -> str:
        if "-l" in args:
            if not self.crontab_entries:
                return "no crontab for devops"
            return "# m h  dom mon dow   command\n" + "\n".join(self.crontab_entries)
        return "crontab [-l | -r | -e]"

    def useradd(self, args: List[str]) -> str:
        if not args:
            return "useradd: missing username"
        username = args[-1]
        shell = "/bin/sh"
        if "-s" in args:
            idx = args.index("-s")
            if idx + 1 < len(args):
                shell = args[idx + 1]

        uid = max([u["uid"] for u in self.users.values()]) + 1
        self.users[username] = {
            "uid": uid,
            "gid": uid,
            "home": f"/home/{username}",
            "shell": shell,
            "groups": [username],
        }
        if "-m" in args or "--create-home" in args:
            self._mkdir_p(f"/home/{username}")
        return ""

    def usermod(self, args: List[str]) -> str:
        if len(args) < 2:
            return "usermod: invalid arguments"
        username = args[-1]
        if username not in self.users:
            return f"usermod: user '{username}' does not exist"

        if "-aG" in args:
            idx = args.index("-aG")
            if idx + 1 < len(args):
                group = args[idx + 1]
                if group not in self.users[username]["groups"]:
                    self.users[username]["groups"].append(group)
        elif "-G" in args:
            idx = args.index("-G")
            if idx + 1 < len(args):
                group = args[idx + 1]
                if group not in self.users[username]["groups"]:
                    self.users[username]["groups"].append(group)
        return ""

    def ss(self, args: List[str]) -> str:
        return (
            f"{'Netid':<6} {'State':<12} {'Recv-Q':<8} {'Send-Q':<8} {'Local Address:Port':<24} {'Peer Address:Port':<20} Process\n"
            f"{'tcp':<6} {'LISTEN':<12} {'0':<8} {'128':<8} {'0.0.0.0:22':<24} {'0.0.0.0:*':<20} users:((\"sshd\",pid=600,fd=3))\n"
            f"{'tcp':<6} {'LISTEN':<12} {'0':<8} {'511':<8} {'0.0.0.0:80':<24} {'0.0.0.0:*':<20} users:((\"nginx\",pid=1120,fd=6))\n"
            f"{'tcp':<6} {'LISTEN':<12} {'0':<8} {'128':<8} {'127.0.0.1:5432':<24} {'0.0.0.0:*':<20} users:((\"postgres\",pid=2048,fd=4))\n"
            f"{'udp':<6} {'UNCONN':<12} {'0':<8} {'0':<8} {'127.0.0.1:8125':<24} {'0.0.0.0:*':<20} users:((\"datadog-agent\",pid=850,fd=8))\n"
            f"{'tcp':<6} {'LISTEN':<12} {'0':<8} {'128':<8} {'127.0.0.1:8126':<24} {'0.0.0.0:*':<20} users:((\"trace-agent\",pid=852,fd=5))"
        )

    def tar(self, args: List[str]) -> str:
        if not args:
            return "tar: You must specify one of the '-Acdtrux' options"
        flags = args[0]
        pos_args = [a for a in args[1:] if not a.startswith("-")]

        if "c" in flags:  # Create
            if len(pos_args) < 2:
                return "tar: missing archive or target"
            archive_path, target_dir = pos_args[0], pos_args[1]
            self._write_file(archive_path, f"[TAR GZIP ARCHIVE: {target_dir}]\n", perms="-rw-r--r--")
            return f"Archived {target_dir} into {archive_path}"
        elif "t" in flags:  # List
            return "app/\napp/config.env\napp/logs/\napp/logs/access.log"
        elif "x" in flags:  # Extract
            return "Extracted archive successfully."
        return "tar: invalid option"

    def uptime(self, args: List[str]) -> str:
        return " 21:55:12 up 45 days, 4:18,  2 users,  load average: 0.15, 0.22, 0.18"
