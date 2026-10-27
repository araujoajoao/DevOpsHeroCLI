"""Unit tests for DevOpsHeroCLI simulators and mission evaluators."""
from __future__ import annotations

import unittest
from devopsherocli.engine.executor import CommandExecutor, EnvironmentState
from devopsherocli.tracks import ALL_TRACKS, get_mission, get_next_mission
from devopsherocli.models import UserProgress


class TestDevOpsHeroEngine(unittest.TestCase):

    def setUp(self):
        self.state = EnvironmentState()
        self.executor = CommandExecutor(self.state)

    def test_linux_commands(self):
        # Test pwd
        out = self.executor.execute_command_string("pwd")
        self.assertEqual(out, "/home/devops")

        # Test mkdir and touch
        self.executor.execute_command_string("mkdir -p /app/logs && touch /app/logs/access.log")
        node = self.state.linux._get_node("/app/logs/access.log")
        self.assertIsNotNone(node)

        # Test pipe and grep
        out = self.executor.execute_command_string("cat /var/log/syslog | grep ERROR")
        self.assertIn("ERROR", out)

        # Test process kill
        self.assertIn(1337, self.state.linux.processes)
        self.executor.execute_command_string("kill 1337")
        self.assertNotIn(1337, self.state.linux.processes)

        # Test redirect
        self.executor.execute_command_string("echo \"ENV=production\" > /app/.env")
        env_node = self.state.linux._get_node("/app/.env")
        self.assertIsNotNone(env_node)
        self.assertIn("ENV=production", env_node.content)

    def test_docker_commands(self):
        # Test docker run
        out = self.executor.execute_command_string("docker run -d --name web-server -p 8080:80 nginx:alpine")
        self.assertTrue(len(out) >= 12)
        c = self.state.docker._find_container("web-server")
        self.assertIsNotNone(c)
        self.assertTrue(c.is_running)

        # Test docker ps
        ps_out = self.executor.execute_command_string("docker ps")
        self.assertIn("web-server", ps_out)

        # Test docker logs
        logs_out = self.executor.execute_command_string("docker logs web-server")
        self.assertIn("Container web-server initialized", logs_out)

        # Test docker stop
        self.executor.execute_command_string("docker stop web-server")
        self.assertFalse(c.is_running)

        # Test docker network
        self.executor.execute_command_string("docker network create backend-net")
        self.assertIn("backend-net", self.state.docker.networks)

        # Test docker rm
        self.executor.execute_command_string("docker rm -f web-server")
        self.assertIsNone(self.state.docker._find_container("web-server"))

    def test_kubernetes_commands(self):
        # Test kubectl get nodes
        nodes_out = self.executor.execute_command_string("kubectl get nodes")
        self.assertIn("k8s-control-plane", nodes_out)
        self.assertIn("Ready", nodes_out)

        # Test kubectl run
        run_out = self.executor.execute_command_string("kubectl run web-pod --image=nginx:alpine")
        self.assertIn("pod/web-pod created", run_out)
        self.assertIn("web-pod", self.state.k8s.pods)

        # Test kubectl create deployment
        deploy_out = self.executor.execute_command_string("kubectl create deployment backend-api --image=nginx:alpine --replicas=3")
        self.assertIn("deployment.apps/backend-api created", deploy_out)
        self.assertIn("backend-api", self.state.k8s.deployments)

        # Test kubectl scale
        scale_out = self.executor.execute_command_string("kubectl scale deployment backend-api --replicas=5")
        self.assertIn("scaled", scale_out)
        self.assertEqual(self.state.k8s.deployments["backend-api"].replicas, 5)

        # Test kubectl expose
        svc_out = self.executor.execute_command_string("kubectl expose deployment backend-api --port=80 --target-port=80")
        self.assertIn("service/backend-api exposed", svc_out)
        self.assertIn("backend-api", self.state.k8s.services)

    def test_datadog_commands(self):
        # Test datadog-agent status
        status_out = self.executor.execute_command_string("datadog-agent status")
        self.assertIn("Agent (v7.55.0)", status_out)
        self.assertIn("DogStatsD", status_out)
        self.assertIn("APM Agent", status_out)

        # Test datadog-agent health
        health_out = self.executor.execute_command_string("datadog-agent health")
        self.assertIn("Agent is HEALTHY", health_out)

        # Test check disk
        check_out = self.executor.execute_command_string("datadog-agent check disk")
        self.assertIn("system.disk.total", check_out)

        # Test flare
        flare_out = self.executor.execute_command_string("datadog-agent flare --case-id 12345")
        self.assertIn("Flare uploaded to Datadog Support", flare_out)

        # Test export tags
        self.executor.execute_command_string("export DD_ENV=production")
        self.assertEqual(self.state.env_vars["DD_ENV"], "production")

    def test_sysadmin_commands(self):
        # Test systemctl status
        status_out = self.executor.execute_command_string("systemctl status nginx")
        self.assertIn("nginx.service", status_out)

        # Test systemctl restart
        self.executor.execute_command_string("systemctl restart postgresql")
        self.assertEqual(self.state.linux.services["postgresql"]["restarts"], 1)

        # Test systemctl enable
        enable_out = self.executor.execute_command_string("systemctl enable nginx")
        self.assertTrue(self.state.linux.services["nginx"]["enabled"])

        # Test ss socket inspection
        ss_out = self.executor.execute_command_string("ss -tulpn")
        self.assertIn("LISTEN", ss_out)
        self.assertIn(":80", ss_out)

        # Test useradd
        self.executor.execute_command_string("useradd -m -s /bin/bash deployer")
        self.assertIn("deployer", self.state.linux.users)

        # Test usermod
        self.executor.execute_command_string("usermod -aG sudo deployer")
        self.assertIn("sudo", self.state.linux.users["deployer"]["groups"])

        # Test tar
        tar_out = self.executor.execute_command_string("tar -czvf /tmp/app-backup.tar.gz /app")
        node = self.state.linux._get_node("/tmp/app-backup.tar.gz")
        self.assertIsNotNone(node)

        # Test uptime
        up_out = self.executor.execute_command_string("uptime")
        self.assertIn("load average", up_out)


class TestMissionsValidation(unittest.TestCase):

    def test_all_tracks_have_missions(self):
        self.assertEqual(len(ALL_TRACKS), 5)
        for t in ALL_TRACKS:
            self.assertEqual(len(t.missions), 10)
            for m in t.missions:
                self.assertIsNotNone(m.check_completion)
                self.assertTrue(m.xp > 0)
                self.assertTrue(len(m.solution) > 0)

    def test_progress_advancement(self):
        m1 = get_mission("linux", "linux-01")
        nxt = get_next_mission("linux", "linux-01")
        self.assertIsNotNone(nxt)
        self.assertEqual(nxt, ("linux", "linux-02"))


if __name__ == "__main__":
    unittest.main()
