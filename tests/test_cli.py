"""Unit tests for DevOpsHeroCLI CLI commands and entrypoints."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from devopsherocli.cli import list_tracks, main, show_stats, verify_missions
from devopsherocli.models import UserProgress


class TestDevOpsHeroCLI(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.storage_file = Path(self.tmp_dir.name) / "progress.json"

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_show_stats_output(self):
        storage_file = self.storage_file

        def mock_init(obj):
            obj.storage_path = storage_file
            obj.xp = 350
            obj.streak = 2
            obj.max_streak = 5
            obj.completed_missions = {"linux-01"}
            obj.current_track_id = "linux"
            obj.current_mission_id = "linux-02"
            obj.command_history = []

        with patch.object(UserProgress, "__init__", mock_init):
            show_stats()

    def test_list_tracks_output(self):
        list_tracks()

    def test_verify_missions_command(self):
        result = verify_missions()
        self.assertTrue(result)

    def test_cli_main_stats(self):
        with patch.object(sys, "argv", ["devopsherocli", "stats"]):
            main()

    def test_cli_main_list(self):
        with patch.object(sys, "argv", ["devopsherocli", "list"]):
            main()

    def test_cli_main_verify(self):
        with patch.object(sys, "argv", ["devopsherocli", "verify"]):
            main()

    def test_cli_main_reset(self):
        with patch.object(sys, "argv", ["devopsherocli", "reset"]):
            main()

    def test_cli_main_doctor(self):
        with patch.object(sys, "argv", ["devopsherocli", "doctor"]):
            main()


if __name__ == "__main__":
    unittest.main()
