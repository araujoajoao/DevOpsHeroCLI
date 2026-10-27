"""Unified command executor, piping, redirects, and state manager for DevOpsHeroCLI."""
from __future__ import annotations

import shlex
from dataclasses import dataclass, field
from typing import Dict, Optional

from devopsherocli.engine.aws_sim import AwsSimulator
from devopsherocli.engine.datadog_sim import DatadogSimulator
from devopsherocli.engine.docker_sim import DockerSimulator
from devopsherocli.engine.git_sim import GitSimulator
from devopsherocli.engine.k8s_sim import KubernetesSimulator
from devopsherocli.engine.linux_sim import LinuxSimulator
from devopsherocli.engine.terraform_sim import TerraformSimulator


@dataclass
class EnvironmentState:
    linux: LinuxSimulator = field(default_factory=LinuxSimulator)
    docker: DockerSimulator = field(default_factory=DockerSimulator)
    k8s: KubernetesSimulator = field(default_factory=KubernetesSimulator)
    datadog: DatadogSimulator = field(default_factory=DatadogSimulator)
    git: GitSimulator = field(default_factory=GitSimulator)
    aws: AwsSimulator = field(default_factory=AwsSimulator)
    terraform: TerraformSimulator = field(default_factory=TerraformSimulator)
    env_vars: Dict[str, str] = field(default_factory=dict)

    def reset_all(self):
        self.linux.reset_default_state()
        self.docker.reset_default_state()
        self.k8s.reset_default_state()
        self.datadog = DatadogSimulator()
        self.git.reset_default_state()
        self.aws.reset_default_state()
        self.terraform.reset_default_state()
        self.env_vars.clear()


class CommandExecutor:
    """Parses shell input, handles pipes & redirection, and executes in the simulated engines."""

    def __init__(self, state: Optional[EnvironmentState] = None):
        self.state = state or EnvironmentState()

    def execute_command_string(self, cmd_line: str) -> str:
        cmd_line = cmd_line.strip()
        if not cmd_line:
            return ""

        # Handle comments or multiple commands separated by &&
        if "&&" in cmd_line:
            parts = [p.strip() for p in cmd_line.split("&&")]
            outputs = []
            for part in parts:
                out = self.execute_command_string(part)
                if out:
                    outputs.append(out)
            return "\n".join(outputs)

        # Handle redirection: > or >>
        redirect_file = None
        append_mode = False
        if ">>" in cmd_line:
            cmd_part, file_part = cmd_line.split(">>", 1)
            cmd_line = cmd_part.strip()
            redirect_file = file_part.strip()
            append_mode = True
        elif ">" in cmd_line:
            cmd_part, file_part = cmd_line.split(">", 1)
            cmd_line = cmd_part.strip()
            redirect_file = file_part.strip()
            append_mode = False

        # Handle pipeline: cmd1 | cmd2
        if "|" in cmd_line:
            pipe_segments = [p.strip() for p in cmd_line.split("|")]
            prev_output: Optional[str] = None
            for seg in pipe_segments:
                prev_output = self._execute_single_command(seg, pipe_input=prev_output)
            final_output = prev_output or ""
        else:
            final_output = self._execute_single_command(cmd_line)

        # If redirect was requested, write to VFS
        if redirect_file:
            mode = "a" if append_mode else "w"
            self.state.linux._write_file(redirect_file, final_output + ("\n" if final_output else ""), mode=mode)
            return ""

        return final_output

    def _execute_single_command(self, cmd_line: str, pipe_input: Optional[str] = None) -> str:
        try:
            tokens = shlex.split(cmd_line)
        except ValueError as e:
            return f"syntax error: {e}"

        if not tokens:
            return ""

        prog = tokens[0]
        args = tokens[1:]

        # Handle environment export
        if prog == "export":
            for a in args:
                if "=" in a:
                    k, v = a.split("=", 1)
                    v = v.strip("\"'")
                    self.state.env_vars[k] = v
                    self.state.linux.env[k] = v
            return ""

        # Handle echo
        if prog == "echo":
            msg = " ".join(args).strip("\"'")
            return msg

        # Handle Docker commands
        if prog == "docker":
            return self.state.docker.execute(args)

        # Handle Kubernetes commands
        if prog == "kubectl":
            return self.state.k8s.execute(args)

        # Handle Datadog commands
        if prog in ["datadog-agent", "agent"]:
            return self.state.datadog.execute(args, env_vars=self.state.env_vars)

        # Handle Git commands
        if prog == "git":
            return self.state.git.execute(args)

        # Handle AWS CLI commands
        if prog == "aws":
            return self.state.aws.execute(args)

        # Handle Terraform commands
        if prog == "terraform":
            return self.state.terraform.execute(args)

        # Handle sudo wrapper
        if prog == "sudo":
            if not args:
                return "usage: sudo command"
            prog = args[0]
            args = args[1:]

        # Handle Linux POSIX & Sysadmin commands
        linux = self.state.linux
        if prog == "pwd":
            return linux.pwd(args)
        elif prog == "cd":
            return linux.cd(args)
        elif prog == "ls":
            return linux.ls(args)
        elif prog == "mkdir":
            return linux.mkdir(args)
        elif prog == "touch":
            return linux.touch(args)
        elif prog == "cat":
            if not args and pipe_input is not None:
                return pipe_input
            return linux.cat(args)
        elif prog == "head":
            return linux.head(args)
        elif prog == "tail":
            return linux.tail(args)
        elif prog == "grep":
            return linux.grep(args, pipe_input=pipe_input)
        elif prog == "rm":
            return linux.rm(args)
        elif prog == "cp":
            return linux.cp(args)
        elif prog == "mv":
            return linux.mv(args)
        elif prog == "chmod":
            return linux.chmod(args)
        elif prog == "chown":
            return linux.chown(args)
        elif prog == "ps":
            return linux.ps(args)
        elif prog == "kill":
            return linux.kill(args)
        elif prog == "df":
            return linux.df(args)
        elif prog == "free":
            return linux.free(args)
        elif prog == "curl":
            return linux.curl(args)
        elif prog == "systemctl":
            return linux.systemctl(args)
        elif prog == "journalctl":
            return linux.journalctl(args)
        elif prog == "crontab":
            return linux.crontab(args)
        elif prog == "useradd":
            return linux.useradd(args)
        elif prog == "usermod":
            return linux.usermod(args)
        elif prog in ["ss", "netstat"]:
            return linux.ss(args)
        elif prog == "tar":
            return linux.tar(args)
        elif prog == "uptime":
            return linux.uptime(args)
        elif prog == "ping":
            target = args[0] if args else "google.com"
            return (
                f"PING {target} (142.250.190.46): 56 data bytes\n"
                f"64 bytes from 142.250.190.46: icmp_seq=0 ttl=116 time=14.2 ms\n"
                f"64 bytes from 142.250.190.46: icmp_seq=1 ttl=116 time=13.8 ms\n"
                f"--- {target} ping statistics ---\n"
                f"2 packets transmitted, 2 packets received, 0.0% packet loss"
            )
        elif prog == "clear":
            return "\033[2J\033[H"
        elif prog in ["whoami", "id"]:
            return "uid=1000(devops) gid=1000(devops) groups=1000(devops),4(adm),27(sudo),999(docker)"
        elif prog == "hostname":
            return "ops-lab-node1"
        elif prog == "uname":
            return "Linux ops-lab-node1 6.8.0-generic #1 SMP PREEMPT_DYNAMIC x86_64 GNU/Linux"

        return f"bash: {prog}: command not found"
