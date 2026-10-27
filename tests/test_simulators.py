"""Unit tests for DevOpsHeroCLI simulators and mission evaluators."""
from __future__ import annotations

import unittest

from devopsherocli.engine.executor import CommandExecutor, EnvironmentState
from devopsherocli.models import Mission, UserProgress
from devopsherocli.tracks import ALL_TRACKS, get_next_mission


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
        self.assertIn("Created symlink", enable_out)
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
        self.executor.execute_command_string("tar -czvf /tmp/app-backup.tar.gz /app")
        node = self.state.linux._get_node("/tmp/app-backup.tar.gz")
        self.assertIsNotNone(node)

        # Test uptime
        up_out = self.executor.execute_command_string("uptime")
        self.assertIn("load average", up_out)

    def test_git_commands(self):
        # Test git init
        init_out = self.executor.execute_command_string("git init")
        self.assertIn("Initialized empty Git repository", init_out)
        self.assertTrue(self.state.git.is_repo)

        # Test git status
        self.state.git.untracked_files.add("main.py")
        status_out = self.executor.execute_command_string("git status")
        self.assertIn("main.py", status_out)

        # Test git add
        self.executor.execute_command_string("git add .")
        self.assertIn("main.py", self.state.git.staged_files)

        # Test git commit
        commit_out = self.executor.execute_command_string('git commit -m "feat: initial app"')
        self.assertIn("feat: initial app", commit_out)
        self.assertEqual(len(self.state.git.commits), 1)

        # Test git branch and checkout
        self.executor.execute_command_string("git checkout -b feature/login")
        self.assertEqual(self.state.git.current_branch, "feature/login")

        # Test git remote
        self.executor.execute_command_string("git remote add origin https://github.com/org/repo.git")
        self.assertIn("origin", self.state.git.remotes)

        # Test git tag
        self.executor.execute_command_string("git tag v1.0.0")
        self.assertIn("v1.0.0", self.state.git.tags)

    def test_aws_commands(self):
        # Test aws sts get-caller-identity
        sts_out = self.executor.execute_command_string("aws sts get-caller-identity")
        self.assertIn("123456789012", sts_out)

        # Test aws s3 ls
        s3_ls = self.executor.execute_command_string("aws s3 ls")
        self.assertIn("company-app-artifacts", s3_ls)

        # Test aws s3 mb
        self.executor.execute_command_string("aws s3 mb s3://new-test-bucket")
        self.assertIn("new-test-bucket", self.state.aws.buckets)

        # Test aws ec2 describe-instances
        ec2_out = self.executor.execute_command_string("aws ec2 describe-instances")
        self.assertIn("i-0a1b2c3d4e5f67890", ec2_out)

        # Test aws ec2 start-instances
        self.executor.execute_command_string("aws ec2 start-instances --instance-ids i-0f9e8d7c6b5a43210")
        self.assertEqual(self.state.aws.instances["i-0f9e8d7c6b5a43210"].state, "running")

        # Test aws iam list-users
        iam_out = self.executor.execute_command_string("aws iam list-users")
        self.assertIn("devops-hero", iam_out)

    def test_terraform_commands(self):
        # Test terraform init
        init_out = self.executor.execute_command_string("terraform init")
        self.assertIn("Terraform has been successfully initialized", init_out)
        self.assertTrue(self.state.terraform.initialized)

        # Test terraform fmt
        fmt_out = self.executor.execute_command_string("terraform fmt")
        self.assertIn("main.tf", fmt_out)

        # Test terraform validate
        val_out = self.executor.execute_command_string("terraform validate")
        self.assertIn("Success! The configuration is valid", val_out)

        # Test terraform plan
        plan_out = self.executor.execute_command_string("terraform plan")
        self.assertIn("Plan: 2 to add", plan_out)

        # Test terraform apply
        apply_out = self.executor.execute_command_string("terraform apply -auto-approve")
        self.assertIn("Apply complete", apply_out)
        self.assertIn("aws_s3_bucket.app_storage", self.state.terraform.state_resources)

        # Test terraform state list
        state_list = self.executor.execute_command_string("terraform state list")
        self.assertIn("aws_s3_bucket.app_storage", state_list)

        # Test terraform output
        out_val = self.executor.execute_command_string("terraform output")
        self.assertIn("vpc_id", out_val)


class TestMissionsValidation(unittest.TestCase):

    def test_all_tracks_have_missions(self):
        self.assertEqual(len(ALL_TRACKS), 8)
        for t in ALL_TRACKS:
            self.assertEqual(len(t.missions), 10)
            for m in t.missions:
                self.assertIsNotNone(m.check_completion)
                self.assertTrue(m.xp > 0)
                self.assertTrue(len(m.solution) > 0)

    def test_progress_advancement(self):
        nxt = get_next_mission("linux", "linux-01")
        self.assertIsNotNone(nxt)
        self.assertEqual(nxt, ("linux", "linux-02"))


class TestAntiCheatScoring(unittest.TestCase):

    def setUp(self):
        import tempfile
        from pathlib import Path
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.progress_file = Path(self.tmp_dir.name) / "test_progress.json"
        self.progress = UserProgress(storage_path=self.progress_file)
        self.mission = Mission(
            id="test-01",
            track_id="linux",
            title="Test Mission",
            difficulty="Iniciante",
            xp=100,
            context="Cenário de teste",
            objective="Teste objetivo",
            tip="Use teste",
            solution="teste",
        )

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_full_points_under_5s_no_tips(self):
        # 100% of base points ONLY if tips == 0 AND elapsed <= 5.0
        res = self.progress.award_mission(self.mission, elapsed_seconds=3.2, tips_used=0)
        self.assertEqual(res.xp, 100)
        self.assertEqual(res.factor, 1.0)
        self.assertTrue(res.is_ninja)
        self.assertIn("100% Ninja Reflex", res.tier_name)
        self.assertEqual(self.progress.streak, 1)

    def test_deduction_over_5s_no_tips(self):
        # > 5.0s without tips receives 70% of points (anti-cheat Google/AI deduction)
        res = self.progress.award_mission(self.mission, elapsed_seconds=8.5, tips_used=0)
        self.assertEqual(res.xp, 70)
        self.assertEqual(res.factor, 0.70)
        self.assertFalse(res.is_ninja)
        self.assertIn("Tempo > 5s", res.tier_name)

    def test_deduction_with_one_tip(self):
        # 1 tip reduces to 40%
        res = self.progress.award_mission(self.mission, elapsed_seconds=2.0, tips_used=1)
        self.assertEqual(res.xp, 40)
        self.assertEqual(res.factor, 0.40)
        self.assertFalse(res.is_ninja)
        self.assertIn("1 Dica Usada", res.tier_name)

    def test_deduction_with_two_tips(self):
        # 2 tips reduces to 20%
        res = self.progress.award_mission(self.mission, elapsed_seconds=4.0, tips_used=2)
        self.assertEqual(res.xp, 20)
        self.assertEqual(res.factor, 0.20)
        self.assertIn("2 Dicas Usadas", res.tier_name)

    def test_deduction_with_three_or_more_tips(self):
        # 3+ tips reduces to 10%
        res = self.progress.award_mission(self.mission, elapsed_seconds=1.5, tips_used=3)
        self.assertEqual(res.xp, 10)
        self.assertEqual(res.factor, 0.10)

    def test_solution_used_gives_zero_xp_and_breaks_streak(self):
        # Revealing solution gives 0 XP and resets streak
        self.progress.streak = 5
        res = self.progress.award_mission(self.mission, elapsed_seconds=1.0, tips_used=0, solution_used=True)
        self.assertEqual(res.xp, 0)
        self.assertEqual(self.progress.streak, 0)
        self.assertIn("Gabarito Revelado", res.tier_name)

    def test_streak_bonus_with_ninja_reflex(self):
        # Streak 3 (+20% bonus) + 100% ninja reflex
        self.progress.streak = 3
        res = self.progress.award_mission(self.mission, elapsed_seconds=4.0, tips_used=0)
        # 100 * 1.0 * 1.20 = 120 XP
        self.assertEqual(res.xp, 120)
        self.assertEqual(self.progress.streak, 4)

    def test_repeat_mission_awards_half_xp(self):
        # First completion
        res1 = self.progress.award_mission(self.mission, elapsed_seconds=2.0, tips_used=0)
        self.assertEqual(res1.xp, 100)
        self.assertFalse(res1.is_repeat)

        # Second completion awards half XP
        res2 = self.progress.award_mission(self.mission, elapsed_seconds=2.0, tips_used=0)
        self.assertEqual(res2.xp, 50)
        self.assertTrue(res2.is_repeat)

    def test_high_streak_caps_at_fifty_percent(self):
        self.progress.streak = 10
        self.assertEqual(self.progress.get_streak_bonus_pct(), 50)


class TestAllEightyMissions(unittest.TestCase):

    def test_all_eighty_missions_isolated_execution(self):
        """Validates that every single one of the 80 missions passes in clean isolated state."""
        failed = []
        for track in ALL_TRACKS:
            for m in track.missions:
                executor = CommandExecutor()
                if m.initial_setup:
                    m.initial_setup(executor.state)
                out = executor.execute_command_string(m.solution)
                if m.check_completion:
                    ok, feedback = m.check_completion(executor.state, m.solution, out)
                    if not ok:
                        failed.append(f"[{track.id}] {m.id}: {m.solution} -> {feedback}")
        self.assertEqual(len(failed), 0, msg="\n".join(failed))

    def test_all_eighty_missions_sequential_execution(self):
        """Validates that every single track passes completely when played sequentially."""
        failed = []
        for track in ALL_TRACKS:
            executor = CommandExecutor()
            for m in track.missions:
                if m.initial_setup:
                    m.initial_setup(executor.state)
                out = executor.execute_command_string(m.solution)
                if m.check_completion:
                    ok, feedback = m.check_completion(executor.state, m.solution, out)
                    if not ok:
                        failed.append(f"Seq [{track.id}] {m.id}: {m.solution} -> {feedback}")
        self.assertEqual(len(failed), 0, msg="\n".join(failed))


class TestUserProgressStorageResilience(unittest.TestCase):

    def setUp(self):
        import tempfile
        from pathlib import Path
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.storage_file = Path(self.tmp_dir.name) / "progress.json"

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_save_and_reload(self):
        p1 = UserProgress(storage_path=self.storage_file)
        p1.xp = 450
        p1.streak = 4
        p1.max_streak = 7
        p1.completed_missions = {"linux-01", "linux-02", "git-01"}
        p1.save()

        # Reload in fresh instance
        p2 = UserProgress(storage_path=self.storage_file)
        self.assertEqual(p2.xp, 450)
        self.assertEqual(p2.streak, 4)
        self.assertEqual(p2.max_streak, 7)
        self.assertIn("git-01", p2.completed_missions)

    def test_corrupted_json_recovery(self):
        # Write invalid corrupted JSON
        with open(self.storage_file, "w", encoding="utf-8") as f:
            f.write("CORRUPTED NOT JSON {{{")

        # Loading should not raise exception, but fallback gracefully to defaults
        p = UserProgress(storage_path=self.storage_file)
        self.assertEqual(p.xp, 0)
        self.assertEqual(p.streak, 0)
        self.assertEqual(len(p.completed_missions), 0)

    def test_corrupted_types_recovery(self):
        # Write corrupted types in JSON
        import json
        with open(self.storage_file, "w", encoding="utf-8") as f:
            json.dump({"xp": "invalid", "streak": None, "completed_missions": 123}, f)

        # Loading should recover without crash
        p = UserProgress(storage_path=self.storage_file)
        self.assertEqual(p.xp, 0)
        self.assertEqual(p.streak, 0)


class TestCommandExecutorEdgeCases(unittest.TestCase):

    def setUp(self):
        self.state = EnvironmentState()
        self.executor = CommandExecutor(self.state)

    def test_empty_and_whitespace(self):
        self.assertEqual(self.executor.execute_command_string(""), "")
        self.assertEqual(self.executor.execute_command_string("   "), "")

    def test_command_chaining(self):
        self.executor.execute_command_string("mkdir -p /app/test && touch /app/test/a.txt")
        node = self.state.linux._get_node("/app/test/a.txt")
        self.assertIsNotNone(node)

    def test_append_redirect(self):
        self.executor.execute_command_string("echo line1 > /app/data.txt")
        self.executor.execute_command_string("echo line2 >> /app/data.txt")
        node = self.state.linux._get_node("/app/data.txt")
        self.assertIsNotNone(node)
        self.assertIn("line1", node.content)
        self.assertIn("line2", node.content)

    def test_syntax_error_quotes(self):
        out = self.executor.execute_command_string('echo "unclosed quote')
        self.assertIn("syntax error", out)

    def test_unknown_command(self):
        out = self.executor.execute_command_string("nonexistentcommand")
        self.assertIn("command not found", out)


class TestCliDiagnosticVerify(unittest.TestCase):

    def test_verify_all_missions_cli(self):
        from devopsherocli.cli import verify_missions
        self.assertTrue(verify_missions())


if __name__ == "__main__":
    unittest.main()
