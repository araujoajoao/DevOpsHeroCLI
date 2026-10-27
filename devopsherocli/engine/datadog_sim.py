"""Virtual Datadog Agent Engine: Agent status, checks, flare, metrics, and tags."""
from __future__ import annotations

import time
from typing import Dict, List, Optional


class DatadogSimulator:
    """Simulates the Datadog Agent CLI (datadog-agent) and observability environment."""

    def __init__(self):
        self.version_str = "7.55.0"
        self.commit = "8c34f21"
        self.site = "datadoghq.com"
        self.api_key = "********************************abcd"
        self.env_tags: Dict[str, str] = {
            "env": "production",
            "service": "payment-gateway",
            "version": "1.4.0",
        }
        self.active_checks = ["cpu", "disk", "network", "docker", "kubernetes_state_core"]
        self.logs_enabled = True
        self.apm_enabled = True
        self.dogstatsd_packets = 1420
        self.flares_generated: List[str] = []

    def execute(self, args: List[str], env_vars: Optional[Dict[str, str]] = None) -> str:
        if not args:
            return self.help([])

        subcmd = args[0]
        subargs = args[1:]

        # Sync any dynamic env vars
        if env_vars:
            if "DD_SITE" in env_vars:
                self.site = env_vars["DD_SITE"]
            if "DD_ENV" in env_vars:
                self.env_tags["env"] = env_vars["DD_ENV"]
            if "DD_SERVICE" in env_vars:
                self.env_tags["service"] = env_vars["DD_SERVICE"]
            if "DD_VERSION" in env_vars:
                self.env_tags["version"] = env_vars["DD_VERSION"]

        handlers = {
            "status": self.status,
            "version": self.version,
            "check": self.check,
            "flare": self.flare,
            "health": self.health,
            "config": self.config,
            "help": self.help,
            "--help": self.help,
        }

        handler = handlers.get(subcmd)
        if handler:
            return handler(subargs)
        return f"datadog-agent: unknown command '{subcmd}'. See 'datadog-agent --help'"

    def version(self, args: List[str]) -> str:
        return f"Agent {self.version_str} - Commit: {self.commit} - Serialization: 5.0.128 - Go: 1.22.4"

    def health(self, args: List[str]) -> str:
        return "Agent is HEALTHY\nAll sub-services (Collector, DogStatsD, Logs Agent, Trace Agent) are responding."

    def help(self, args: List[str]) -> str:
        return (
            "Usage: datadog-agent [command]\n\n"
            "Available Commands:\n"
            "  check         Run a specific check and print collected metrics\n"
            "  config        Print runtime configuration\n"
            "  flare         Collect and send a flare archive to Datadog Support\n"
            "  health        Check health status of the running Agent\n"
            "  status        Print current status of the Agent\n"
            "  version       Print the version number of the Agent"
        )

    def status(self, args: List[str]) -> str:
        tags_display = ", ".join([f"{k}:{v}" for k, v in self.env_tags.items()])
        return (
            "===================\n"
            "Agent (v7.55.0)\n"
            "===================\n\n"
            "  Status date: 2026-10-26 21:50:00 UTC\n"
            "  Agent start: 2026-10-26 20:00:00 UTC\n"
            "  Pid: 850\n"
            "  Go Version: go1.22.4\n"
            "  Python Version: 3.12.3\n"
            "  Build arch: amd64\n\n"
            "  Hostname: ops-lab-node1\n"
            f"  Datadog Site: {self.site}\n"
            f"  API Key: {self.api_key}\n"
            f"  Unified Service Tags: [bold cyan]{tags_display}[/]\n\n"
            "========= Collector =========\n"
            f"  Running Checks: [bold green]{len(self.active_checks)} checks[/]\n"
            "    - cpu (OK, 12 metrics collected)\n"
            "    - disk (OK, 8 metrics collected)\n"
            "    - network (OK, 14 metrics collected)\n"
            "    - docker (OK, 24 metrics collected, 2 containers monitored)\n"
            "    - kubernetes_state_core (OK, 38 metrics collected)\n\n"
            "========= DogStatsD =========\n"
            "  Event Listener: UDP on 127.0.0.1:8125\n"
            f"  Total Packets Received: {self.dogstatsd_packets}\n"
            "  Packet Drop Rate: 0.00%\n\n"
            "========= APM Agent =========\n"
            "  Trace Receiver: Listening on 127.0.0.1:8126\n"
            "  Status: [bold green]Running[/]\n"
            "  Traces received: 4,892\n"
            "  Traces sampled: 4,892\n\n"
            "========= Logs Agent =========\n"
            "  Reliable: true\n"
            "  Status: [bold green]Running[/]\n"
            "  1 source active (Docker container logs)\n"
            "  Bytes sent: 1.2 MB"
        )

    def check(self, args: List[str]) -> str:
        if not args:
            return "datadog-agent check: check name required (e.g. disk, cpu, docker, http_check)"
        check_name = args[0]
        ts = int(time.time())

        if check_name == "disk":
            return (
                f"=== Running Check: disk ===\n"
                f"Metrics:\n"
                f"  system.disk.total [gauge]: 31093723136 tags:[device:/dev/root,fstype:ext4] ts:{ts}\n"
                f"  system.disk.used  [gauge]: 6033825792  tags:[device:/dev/root,fstype:ext4] ts:{ts}\n"
                f"  system.disk.free  [gauge]: 25059897344 tags:[device:/dev/root,fstype:ext4] ts:{ts}\n"
                f"  system.disk.in_use [gauge]: 0.194      tags:[device:/dev/root,fstype:ext4] ts:{ts}\n"
                f"Check disk finished successfully! (0 errors, 4 metrics)"
            )
        elif check_name in ["cpu", "system"]:
            return (
                f"=== Running Check: cpu ===\n"
                f"Metrics:\n"
                f"  system.cpu.user   [gauge]: 14.2 tags:[host:ops-lab-node1] ts:{ts}\n"
                f"  system.cpu.system [gauge]: 3.8  tags:[host:ops-lab-node1] ts:{ts}\n"
                f"  system.cpu.idle   [gauge]: 82.0 tags:[host:ops-lab-node1] ts:{ts}\n"
                f"  system.cpu.iowait [gauge]: 0.0  tags:[host:ops-lab-node1] ts:{ts}\n"
                f"Check cpu finished successfully! (0 errors, 4 metrics)"
            )
        elif check_name == "docker":
            return (
                f"=== Running Check: docker ===\n"
                f"Metrics:\n"
                f"  docker.containers.running [gauge]: 2 ts:{ts}\n"
                f"  docker.containers.stopped [gauge]: 0 ts:{ts}\n"
                f"  docker.cpu.usage          [rate]:  0.42 tags:[container_name:postgres-db] ts:{ts}\n"
                f"  docker.mem.rss            [gauge]: 28434432 tags:[container_name:postgres-db] ts:{ts}\n"
                f"Check docker finished successfully! (0 errors, 4 metrics)"
            )
        return (
            f"=== Running Check: {check_name} ===\n"
            f"Collecting metrics for '{check_name}'...\n"
            f"  {check_name}.status [gauge]: 1.0 tags:[host:ops-lab-node1] ts:{ts}\n"
            f"Check {check_name} finished successfully! (0 errors, 1 metric)"
        )

    def flare(self, args: List[str]) -> str:
        case_id = "000000"
        if "--case-id" in args:
            idx = args.index("--case-id")
            if idx + 1 < len(args):
                case_id = args[idx + 1]

        flare_filename = f"/tmp/datadog-agent-flare-20261026-{case_id}.zip"  # nosec B108 - simulated path
        self.flares_generated.append(flare_filename)
        return (
            f"Collecting Agent logs, config files, and environment telemetry...\n"
            f"Archiving files into {flare_filename}...\n"
            f"[bold green]Success![/] Flare uploaded to Datadog Support for Case ID: {case_id}\n"
            f"Archive URL: https://flare.datadoghq.com/{case_id}/archive.zip"
        )

    def config(self, args: List[str]) -> str:
        return (
            f"api_key: {self.api_key}\n"
            f"site: {self.site}\n"
            f"env: {self.env_tags.get('env', 'production')}\n"
            f"service: {self.env_tags.get('service', 'payment-gateway')}\n"
            f"version: {self.env_tags.get('version', '1.4.0')}\n"
            f"logs_enabled: {str(self.logs_enabled).lower()}\n"
            "dogstatsd_port: 8125\n"
            "apm_config:\n"
            "  enabled: true\n"
            "  apm_non_local_traffic: true"
        )
