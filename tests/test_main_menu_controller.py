"""Regression tests for the main menu controller."""

from unittest.mock import MagicMock, patch

from controller.menus import main_menu_controller


def test_guardar_persists_selected_beta_channel_without_overwriting_it():
    """Saving settings keeps Beta in the complete configuration payload."""
    config = {
        "idioma": main_menu_controller.codes[0],
        "speed": 0,
        "tono": 0,
        "volume": 0,
        "sapi": False,
        "voz": 0,
        "update_channel": "stable",
    }
    dialog = MagicMock()
    dialog.choice_traducir.GetSelection.return_value = -1
    dialog.choice_language.GetSelection.return_value = 0
    dialog.choice_canal.GetSelection.return_value = 1
    dialog.check_backup.IsChecked.return_value = False
    dialog.choice_moneditas.GetStringSelection.return_value = "Por defecto"
    controller = main_menu_controller.MainMenuController.__new__(
        main_menu_controller.MainMenuController
    )
    controller.config_dialog = dialog

    with (
        patch.object(main_menu_controller.data_store, "config", config),
        patch.object(main_menu_controller.data_store, "motor_de_interfaz", return_value="edge"),
        patch.object(main_menu_controller.fajustes, "guardarConfiguracion") as save,
        patch.object(main_menu_controller.app_utilitys, "fijar_dispositivo_lector"),
        patch.object(main_menu_controller.reader._leer, "list_voices", return_value=[]),
        patch.object(main_menu_controller.reader._lector, "list_voices", return_value=[]),
    ):
        controller.guardar()

    save.assert_called_once_with(config)
    assert save.call_args.args[0]["update_channel"] == "beta"
