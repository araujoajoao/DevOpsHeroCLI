"""Versioning guards: single source of truth and update detection."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from devopsherocli import __version__
from devopsherocli.app import _extract_pyproject_version, _parse_version

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestVersioning(unittest.TestCase):

    def test_pyproject_matches_package_version(self):
        pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertEqual(_extract_pyproject_version(pyproject), __version__)

    def test_version_is_semver(self):
        self.assertRegex(__version__, r"^\d+\.\d+\.\d+$")

    def test_packagers_do_not_hardcode_version(self):
        deb = (REPO_ROOT / "scripts" / "build_linux_deb.py").read_text(encoding="utf-8")
        mac = (REPO_ROOT / "scripts" / "build_macos_app.sh").read_text(encoding="utf-8")
        self.assertNotRegex(deb, r"(?m)^Version:\s*\d")
        self.assertNotRegex(mac, r"<string>\d+\.\d+\.\d+</string>")

    def test_parse_version_ordering(self):
        self.assertGreater(_parse_version("v1.10.0"), _parse_version("1.9.9"))
        self.assertGreater(_parse_version("1.0.1"), _parse_version("1.0.0"))
        self.assertEqual(_parse_version("1.2.3rc1"), (1, 2, 3))

    def test_extract_ignores_other_version_keys(self):
        content = 'target-version = "py39"\nversion = "2.0.0"\n'
        self.assertEqual(_extract_pyproject_version(content), "2.0.0")
        self.assertFalse(re.match(r"\d", _extract_pyproject_version('target-version = "py39"\n') or "x"))


class TestUpdater(unittest.TestCase):

    def test_packaged_install_points_to_os_installer(self):
        from unittest.mock import patch

        from devopsherocli import updater

        with patch.object(updater, "is_git_checkout", return_value=False):
            for platform, suffix in (("darwin", ".dmg"), ("linux", ".deb"), ("win32", "-windows.zip")):
                with patch.object(updater.sys, "platform", platform):
                    result = updater.perform_update()
                    self.assertFalse(result.ok)
                    self.assertIn(f"releases/latest/download/DevOpsHero{suffix}", result.details)

    def test_pull_is_fast_forward_only(self):
        from unittest.mock import MagicMock, patch

        from devopsherocli import updater

        fake = MagicMock(returncode=0, stdout="Already up to date.\n", stderr="")
        with patch.object(updater, "is_git_checkout", return_value=True), \
                patch.object(updater.subprocess, "run", return_value=fake) as run:
            result = updater.perform_update()
        self.assertTrue(result.ok)
        self.assertIn("--ff-only", run.call_args_list[0].args[0])


if __name__ == "__main__":
    unittest.main()
