"""Tests for update.bootstrap module."""

import sys
from unittest.mock import MagicMock, patch

from update.bootstrap import _build_args, _is_process_running, launch_bootstrap


class TestBuildArgs:
    def test_builds_correct_string(self):
        result = _build_args(1234, "C:\\source", "C:\\dest", "C:\\app.exe")
        assert result == '"1234" "C:\\source" "C:\\dest" "C:\\app.exe"'

    def test_handles_spaces_in_paths(self):
        result = _build_args(
            1, "C:\\my app\\src", "C:\\my app\\dst", "C:\\my app\\run.exe"
        )
        assert '"C:\\my app\\src"' in result
        assert '"C:\\my app\\dst"' in result


class TestIsProcessRunning:
    @patch("update.bootstrap.subprocess.run")
    def test_process_found(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="bootstrap.exe  1234  Console  1  1,000 K"
        )
        assert _is_process_running("bootstrap.exe") is True

    @patch("update.bootstrap.subprocess.run")
    def test_process_not_found(self, mock_run):
        mock_run.return_value = MagicMock(stdout="INFO: No tasks are running.")
        assert _is_process_running("bootstrap.exe") is False

    @patch("update.bootstrap.subprocess.run")
    def test_subprocess_error_returns_false(self, mock_run):
        import subprocess

        mock_run.side_effect = subprocess.SubprocessError("fail")
        assert _is_process_running("bootstrap.exe") is False


class TestLaunchBootstrap:
    @patch("update.bootstrap._is_process_running")
    @patch("update.bootstrap.time")
    def test_success_exit_code(self, mock_time, mock_is_running):
        mock_win32api = MagicMock()
        mock_win32api.ShellExecute.return_value = 100
        mock_win32con = MagicMock()
        mock_win32con.SW_SHOW = 1

        mock_is_running.side_effect = [True, False, False]
        mock_time.monotonic.side_effect = [0, 0.5, 1.0]
        mock_time.sleep = MagicMock()

        with patch.dict(
            sys.modules, {"win32api": mock_win32api, "win32con": mock_win32con}
        ):
            result = launch_bootstrap("bootstrap.exe", 1234, "src", "dst", "app.exe")
        assert result == 0

    @patch("update.bootstrap._is_process_running")
    @patch("update.bootstrap.time")
    def test_timeout_exit_code(self, mock_time, mock_is_running):
        mock_win32api = MagicMock()
        mock_win32api.ShellExecute.return_value = 100
        mock_win32con = MagicMock()
        mock_win32con.SW_SHOW = 1

        mock_is_running.return_value = True
        mock_time.monotonic.side_effect = [0, 10, 20, 31]
        mock_time.sleep = MagicMock()

        with patch.dict(
            sys.modules, {"win32api": mock_win32api, "win32con": mock_win32con}
        ):
            result = launch_bootstrap("bootstrap.exe", 1234, "src", "dst", "app.exe")
        assert result == -1

    def test_uac_denied_returns_cancelled(self):
        mock_win32api = MagicMock()
        mock_win32api.ShellExecute.side_effect = Exception("UAC denied")
        mock_win32con = MagicMock()
        mock_win32con.SW_SHOW = 1

        with patch.dict(
            sys.modules, {"win32api": mock_win32api, "win32con": mock_win32con}
        ):
            result = launch_bootstrap("bootstrap.exe", 1234, "src", "dst", "app.exe")
        assert result == 2

    def test_shell_execute_failure_returns_failure(self):
        mock_win32api = MagicMock()
        mock_win32api.ShellExecute.return_value = 5
        mock_win32con = MagicMock()
        mock_win32con.SW_SHOW = 1

        with patch.dict(
            sys.modules, {"win32api": mock_win32api, "win32con": mock_win32con}
        ):
            result = launch_bootstrap("bootstrap.exe", 1234, "src", "dst", "app.exe")
        assert result == 1
