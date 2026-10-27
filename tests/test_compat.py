"""Unit tests for DevOpsHeroCLI cross-platform compatibility and PowerShell detection."""
from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch

from devopsherocli.compat import (
    _get_parent_process_name,
    ensure_utf8_encoding,
    get_platform_info,
    get_powershell_humor_message,
    is_linux,
    is_macos,
    is_powershell,
    is_windows,
    is_wsl,
)


class TestCrossPlatformCompatibility(unittest.TestCase):

    def test_os_detection_functions(self):
        # One of these must match the running OS
        self.assertIn(sys.platform, ("darwin", "linux", "win32"))
        if sys.platform == "darwin":
            self.assertTrue(is_macos())
            self.assertFalse(is_windows())
        elif sys.platform.startswith("linux"):
            self.assertTrue(is_linux())
            self.assertFalse(is_macos())
            self.assertFalse(is_windows())
        elif sys.platform == "win32":
            self.assertTrue(is_windows())
            self.assertFalse(is_macos())
            self.assertFalse(is_linux())

    def test_wsl_detection(self):
        with patch.dict(os.environ, {"WSL_DISTRO_NAME": "Ubuntu"}):
            with patch("devopsherocli.compat.is_linux", return_value=True):
                self.assertTrue(is_wsl())

        with patch.dict(os.environ, {}, clear=True):
            with patch("devopsherocli.compat.is_linux", return_value=False):
                self.assertFalse(is_wsl())

    def test_is_powershell_detection_via_override(self):
        with patch.dict(os.environ, {"DEVOPSHERO_SHELL": "powershell"}):
            self.assertTrue(is_powershell())

        with patch.dict(os.environ, {"DEVOPSHERO_SHELL": "pwsh"}):
            self.assertTrue(is_powershell())

    def test_is_powershell_detection_via_env_vars(self):
        with patch.dict(os.environ, {"POWERSHELL_DISTRIBUTION_CHANNEL": "PSGallery"}, clear=True):
            self.assertTrue(is_powershell())

        with patch.dict(os.environ, {"PSExecutionPolicyPreference": "RemoteSigned"}, clear=True):
            self.assertTrue(is_powershell())

    def test_is_powershell_detection_via_shell_path(self):
        with patch.dict(os.environ, {"SHELL": "/usr/local/bin/pwsh"}, clear=True):
            self.assertTrue(is_powershell())

    def test_is_powershell_detection_via_parent_process(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch("devopsherocli.compat._get_parent_process_name", return_value="powershell.exe"):
                self.assertTrue(is_powershell())

            with patch("devopsherocli.compat._get_parent_process_name", return_value="pwsh"):
                self.assertTrue(is_powershell())

            with patch("devopsherocli.compat._get_parent_process_name", return_value="bash"):
                self.assertFalse(is_powershell())

    def test_powershell_humor_message(self):
        plain_msg = get_powershell_humor_message(plain=True)
        self.assertIn("PowerShell", plain_msg)
        self.assertIn("terminal", plain_msg.lower())
        self.assertIn("windows", plain_msg.lower())

        rich_msg = get_powershell_humor_message(plain=False)
        self.assertIn("[bold #ffd60a]", rich_msg)
        self.assertIn("PowerShell", rich_msg)

    def test_get_platform_info(self):
        info = get_platform_info()
        self.assertIn("os", info)
        self.assertIn("is_wsl", info)
        self.assertIn("is_powershell", info)
        self.assertIn("terminal", info)
        self.assertIn("python_version", info)
        self.assertIn("encoding", info)

    def test_ensure_utf8_encoding_runs_safely(self):
        # Must execute without throwing exceptions on any OS
        ensure_utf8_encoding()

    def test_parent_process_name_discovery(self):
        # Should return a string without error
        parent = _get_parent_process_name()
        self.assertIsInstance(parent, str)


if __name__ == "__main__":
    unittest.main()
