"""Regression tests for the shared network manager imports."""

from importlib import import_module

from utils.network import network_manager


def test_language_updater_imports_without_startup_setup_network():
    module = import_module("servicios.language_updater")

    assert module.network is network_manager
