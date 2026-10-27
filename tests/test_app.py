"""Unit and integration tests for DevOpsHeroCLI Textual App (TUI)."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from devopsherocli.app import DevOpsHeroApp
from devopsherocli.models import UserProgress


class TestDevOpsHeroAppTUI(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.storage_file = Path(self.tmp_dir.name) / "progress.json"

    async def asyncTearDown(self):
        self.tmp_dir.cleanup()

    async def test_app_mount_and_initial_state(self):
        app = DevOpsHeroApp()
        app.progress = UserProgress(storage_path=self.storage_file)
        async with app.run_test() as pilot:
            await pilot.pause()
            self.assertIsNotNone(app.current_mission)
            self.assertEqual(app.current_mission.id, "linux-01")
            self.assertFalse(app.show_tip)
            self.assertFalse(app.show_solution)

    async def test_app_execute_command_via_input(self):
        app = DevOpsHeroApp()
        app.progress = UserProgress(storage_path=self.storage_file)
        async with app.run_test() as pilot:
            await pilot.pause()
            # Submit command 'ls'
            await pilot.press("l", "s", "enter")
            await pilot.pause()
            self.assertTrue(len(app.progress.command_history) >= 1)
            self.assertEqual(app.progress.command_history[-1], "ls")

    async def test_app_action_tip_and_solution(self):
        app = DevOpsHeroApp()
        app.progress = UserProgress(storage_path=self.storage_file)
        async with app.run_test() as pilot:
            await pilot.pause()
            # Press F3 (tip)
            await pilot.press("f3")
            await pilot.pause()
            self.assertTrue(app.show_tip)
            self.assertEqual(app.tips_used, 1)

            # Press F4 (solution)
            await pilot.press("f4")
            await pilot.pause()
            self.assertTrue(app.show_solution)
            self.assertTrue(app.solution_used)
            self.assertEqual(app.progress.streak, 0)

    async def test_app_action_reset_lab(self):
        app = DevOpsHeroApp()
        app.progress = UserProgress(storage_path=self.storage_file)
        async with app.run_test() as pilot:
            await pilot.pause()
            app.tips_used = 3
            app.solution_used = True
            await pilot.press("f5")
            await pilot.pause()
            self.assertEqual(app.tips_used, 0)
            self.assertFalse(app.solution_used)

    async def test_app_completes_mission_and_advances(self):
        app = DevOpsHeroApp()
        app.progress = UserProgress(storage_path=self.storage_file)
        async with app.run_test() as pilot:
            await pilot.pause()
            init_xp = app.progress.xp
            # Mission linux-01 solution is 'pwd'
            await pilot.press("p", "w", "d", "enter")
            await pilot.pause()
            self.assertGreater(app.progress.xp, init_xp)
            self.assertIn("linux-01", app.progress.completed_missions)

    async def test_app_markup_escape_safety(self):
        app = DevOpsHeroApp()
        app.progress = UserProgress(storage_path=self.storage_file)
        async with app.run_test() as pilot:
            await pilot.pause()
            # Test that brackets or unclosed tags do not crash the RichLog
            for dangerous_cmd in ["echo [/]", "cat [foo", "echo [bold red]"]:
                for char in dangerous_cmd:
                    await pilot.press(char)
                await pilot.press("enter")
                await pilot.pause()
            self.assertTrue(app.is_running)


if __name__ == "__main__":
    unittest.main()
