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

    async def test_app_powershell_easter_egg_mode(self):
        import os
        from unittest.mock import patch

        with patch.dict(os.environ, {"DEVOPSHERO_SHELL": "powershell"}):
            app = DevOpsHeroApp()
            app.progress = UserProgress(storage_path=self.storage_file)
            async with app.run_test() as pilot:
                await pilot.pause()
                tab_label = app.query_one("#lbl-term-tab-title")
                status_badge = app.query_one("#lbl-term-status-badge")
                self.assertIn("pwsh", str(tab_label.render()))
                self.assertIn("PowerShell", str(status_badge.render()))
                self.assertTrue(app.is_running)

    async def test_app_mouse_clicks_and_navigation(self):
        from textual.widgets import Label
        app = DevOpsHeroApp()
        app.progress = UserProgress(storage_path=self.storage_file)
        async with app.run_test(size=(120, 35)) as pilot:
            await pilot.pause()

            # Click track in sidebar
            await pilot.click("#nav-track-git")
            await pilot.pause()
            self.assertEqual(app.progress.current_track_id, "git")

            # Click tip action pill in sidebar
            await pilot.click("#btn-sidebar-tip")
            await pilot.pause()
            self.assertTrue(app.show_tip)

            # Click solution action pill in sidebar
            await pilot.click("#btn-sidebar-solution")
            await pilot.pause()
            self.assertTrue(app.solution_used)

            # Click console home in sidebar
            await pilot.click("#nav-console-home")
            await pilot.pause()
            self.assertEqual(app.current_view, "console_home")

            # Click terminal lab in sidebar
            await pilot.click("#nav-terminal-lab")
            await pilot.pause()
            self.assertEqual(app.current_view, "terminal_lab")

            # Click first mission in tree
            tree = app.query_one("#box-missions-list")
            lbl = tree.query(Label).first()
            await pilot.click(lbl)
            await pilot.pause()
            self.assertTrue(app.is_running)

            # Click prompt focuses terminal input
            await pilot.click("#term-prompt")
            await pilot.pause()
            self.assertTrue(app.query_one("#term-input").has_focus)


if __name__ == "__main__":
    unittest.main()
