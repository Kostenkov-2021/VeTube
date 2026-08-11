# -*- coding: utf-8 -*-
"""Update orchestrator — wires foundation modules into the update flow."""

import logging
import os
import sys
import tempfile
import threading
from pathlib import Path

import httpx
import wx
from packaging.version import Version

from globals.paths import BASE_DIR, BOOTSTRAP_EXE
from update import github_client
from update.backup import cleanup_backup, create_backup, restore_backup
from update.bootstrap import launch_bootstrap
from update.downloader import download
from update.extractor import extract
from update.verifier import verify
from update.wxUpdater import available_update_dialog, progress_callback, update_finished

logger = logging.getLogger(__name__)

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


def _read_version() -> str:
    """Read version from pyproject.toml at runtime."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return data["project"]["version"]
    except Exception:
        logger.exception("Failed to read version from pyproject.toml")
        return "0.0.0"


VERSION: str = _read_version()

buscando: bool = False


def do_update(is_manual: bool = False) -> None:
    """Check for updates and install if available.

    Args:
        is_manual: True when triggered by the user (shows errors),
            False for auto-check (silent on failure).
    """
    global buscando
    if buscando:
        return
    buscando = True

    def _check_and_notify() -> None:
        global buscando
        try:
            release = github_client.get_latest_release()

            if release is None:
                if is_manual:
                    wx.CallAfter(
                        wx.MessageBox,
                        _("No se pudo comprobar actualizaciones. Verifica tu conexión."),
                        _("Error"),
                        wx.ICON_ERROR,
                    )
                return

            current = Version(VERSION)
            latest = Version(release.version)

            if latest <= current:
                if is_manual:
                    wx.CallAfter(
                        wx.MessageBox,
                        _("Al parecer tienes la última versión del programa"),
                        _("Información"),
                        wx.ICON_INFORMATION,
                    )
                return

            def _on_user_choice() -> None:
                if available_update_dialog(release.version, release.description):
                    threading.Thread(
                        target=_install_update,
                        args=(release,),
                        daemon=True,
                    ).start()

            wx.CallAfter(_on_user_choice)

        except Exception:
            logger.exception("Error during update check")
            if is_manual:
                wx.CallAfter(
                    wx.MessageBox,
                    _("Error al comprobar actualizaciones."),
                    _("Error"),
                    wx.ICON_ERROR,
                )
        finally:
            buscando = False

    threading.Thread(target=_check_and_notify, daemon=True).start()


def _install_update(release: github_client.ReleaseInfo) -> None:
    """Download, verify, backup, extract, and launch bootstrap.

    Args:
        release: ReleaseInfo from github_client.
    """
    base_path = tempfile.mkdtemp()
    zip_path = os.path.join(base_path, release.zip_name)
    extract_path = os.path.join(base_path, "update")
    install_dir = str(BASE_DIR)
    backup_path: str | None = None

    try:
        logger.info("Starting update to v%s", release.version)

        download(release.zip_url, zip_path, progress_callback=progress_callback)

        checksum_content = _fetch_checksum(release.checksum_url)
        if checksum_content is None:
            raise RuntimeError("Failed to fetch checksum file")

        if not verify(zip_path, checksum_content, release.zip_name):
            raise RuntimeError("SHA256 verification failed")

        backup_path = create_backup(install_dir, VERSION)

        extract(zip_path, extract_path)

        exe_path = sys.executable if getattr(sys, "frozen", False) else str(BASE_DIR / "run_main_window.py")
        bootstrap_exe = str(BOOTSTRAP_EXE)

        exit_code = launch_bootstrap(
            bootstrap_exe=bootstrap_exe,
            pid=os.getpid(),
            source_dir=extract_path,
            dest_dir=install_dir,
            exe_path=exe_path,
        )

        if exit_code == 0:
            cleanup_backup(backup_path)
            update_finished()
            logger.info("Update installed successfully")
        else:
            logger.error("Bootstrap exited with code %d, restoring backup", exit_code)
            restore_backup(backup_path, install_dir)

    except Exception:
        logger.exception("Update failed")
        if backup_path and os.path.isdir(backup_path):
            try:
                restore_backup(backup_path, install_dir)
            except Exception:
                logger.exception("Failed to restore backup")


def _fetch_checksum(checksum_url: str) -> str | None:
    """Download the .sha256 checksum file content.

    Args:
        checksum_url: URL to the checksum file.

    Returns:
        Raw text content, or None on failure.
    """
    try:
        with httpx.Client(follow_redirects=True, timeout=30) as client:
            response = client.get(checksum_url)
            response.raise_for_status()
            return response.text
    except httpx.HTTPError:
        logger.exception("Failed to fetch checksum from '%s'", checksum_url)
        return None
