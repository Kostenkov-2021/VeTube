"""Tests for relaunching the right executable after a cross-version update.

Covers the two failures proven on 2026-08-22 while rehearsing the 3.94 -> 3.95
update against a real 3.94 install: the finalizer relaunched the requester's
outdated run_main_window.exe (still on disk because updates never delete), and
_wait_for_process_exit mistook a terminated process for a live one whenever any
other handle to it survived.
"""

import sys
from unittest.mock import patch

import pytest

from update.bootstrap_fix import (
    EXIT_SUCCESS,
    _finalize_bootstrap,
    _resolve_app_executable,
    _wait_for_process_exit,
)


def test_resolve_prefers_packaged_app_over_outdated_exe(tmp_path):
    (tmp_path / "VeTube.exe").write_bytes(b"new app")

    resolved = _resolve_app_executable(str(tmp_path), str(tmp_path / "run_main_window.exe"))

    assert resolved == str(tmp_path / "VeTube.exe")


def test_resolve_keeps_requested_exe_when_packaged_app_is_absent(tmp_path):
    requested = str(tmp_path / "run_main_window.exe")

    assert _resolve_app_executable(str(tmp_path), requested) == requested


def test_resolve_keeps_canonical_exe_untouched(tmp_path):
    requested = str(tmp_path / "VeTube.exe")

    assert _resolve_app_executable(str(tmp_path), requested) == requested


def test_finalize_relaunches_packaged_app_for_legacy_requester(tmp_path):
    destination = tmp_path / "destination"
    destination.mkdir()
    active = destination / "bootstrap.exe"
    staged = destination / "bootstrap.next.exe"
    active.write_bytes(b"old")
    staged.write_bytes(b"new")
    (destination / "VeTube.exe").write_bytes(b"app")
    legacy_exe = destination / "run_main_window.exe"
    legacy_exe.write_bytes(b"old app")

    with patch("update.bootstrap_fix._wait_for_process_exit", return_value=True), patch(
        "update.bootstrap_fix._launch_executable", return_value=True
    ) as launch:
        result = _finalize_bootstrap(
            42, str(destination), str(legacy_exe), str(active), str(staged)
        )

    assert result == EXIT_SUCCESS
    launch.assert_called_once_with(str(destination / "VeTube.exe"))


def test_main_legacy_path_relaunches_packaged_app(tmp_path):
    from update import bootstrap_fix

    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    destination.mkdir()
    (source / "VERSION").write_text("3.95", encoding="utf-8")
    (destination / "VeTube.exe").write_bytes(b"new app")
    legacy_exe = destination / "run_main_window.exe"
    legacy_exe.write_bytes(b"old app")
    argv = ["bootstrap.exe", "42", str(source), str(destination), str(legacy_exe)]

    with patch.object(sys, "argv", argv), patch.object(bootstrap_fix, "kill_process"), patch.object(
        bootstrap_fix.time, "sleep"
    ), patch.object(bootstrap_fix, "_launch_executable", return_value=True) as launch, pytest.raises(
        SystemExit
    ) as error:
        bootstrap_fix.main()

    assert error.value.code == EXIT_SUCCESS
    launch.assert_called_once_with(str(destination / "VeTube.exe"))


def test_wait_for_process_exit_detects_terminated_process_with_live_handle():
    # OpenProcess succeeds (someone still holds a handle to the dead process)
    # but WaitForSingleObject reports WAIT_OBJECT_0: the process HAS exited.
    kernel32 = type(
        "Kernel32",
        (),
        {
            "OpenProcess": staticmethod(lambda *_args: 1),
            "WaitForSingleObject": staticmethod(lambda *_args: 0),
            "CloseHandle": staticmethod(lambda *_args: None),
        },
    )()
    windll = type("WinDll", (), {"kernel32": kernel32})()

    with patch("update.bootstrap_fix.ctypes.windll", windll), patch(
        "update.bootstrap_fix.time.monotonic", side_effect=[0, 1]
    ), patch("update.bootstrap_fix.time.sleep"):
        assert _wait_for_process_exit(42, timeout=30) is True


def test_wait_for_process_exit_still_waits_for_running_process():
    WAIT_TIMEOUT = 0x102
    kernel32 = type(
        "Kernel32",
        (),
        {
            "OpenProcess": staticmethod(lambda *_args: 1),
            "WaitForSingleObject": staticmethod(lambda *_args: WAIT_TIMEOUT),
            "CloseHandle": staticmethod(lambda *_args: None),
        },
    )()
    windll = type("WinDll", (), {"kernel32": kernel32})()

    with patch("update.bootstrap_fix.ctypes.windll", windll), patch(
        "update.bootstrap_fix.time.monotonic", side_effect=[0, 1, 31]
    ), patch("update.bootstrap_fix.time.sleep"):
        assert _wait_for_process_exit(42, timeout=30) is False
