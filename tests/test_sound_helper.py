"""Regression tests: the app must START without an audio device.

VeTube 3.93 died on startup inside the winget validation VMs (no sound card)
with "UnboundLocalError: cannot access local variable 'output'" in
sound_helper.__init__: when Output() failed with any BASS code other than 14
("already initialized"), the else branch left `output` unassigned and the next
line used it.  Seen in the moderator's screenshot on microsoft/winget-pkgs
#409149.  The fix makes the player come up muted instead: no output, empty
device list, playback and device selection become no-ops.
"""

from unittest.mock import patch

import pytest

from sound_lib.main import BassError

from helpers import sound_helper as helpers_sound
from players import sound_helper as players_sound


def _output_sin_tarjeta():
    """Output double that always fails like a machine without audio."""

    class OutputSinTarjeta:
        def __init__(self, device=-1):
            raise BassError(23, "IllegalDevice")

        @staticmethod
        def free():
            raise AssertionError("free() must not be called on a code-23 failure")

    return OutputSinTarjeta


def _output_ya_inicializado():
    """Output double whose first init raises code 14, then works."""

    class OutputYaInicializado:
        intentos = 0
        liberado = False

        def __init__(self, device=-1):
            type(self).intentos += 1
            if type(self).intentos == 1:
                raise BassError(14, "Already initialized")

        @classmethod
        def free(cls):
            cls.liberado = True

        def start(self):
            pass

        def get_device_names(self):
            return ["Altavoces"]

        def get_device(self):
            return 1

    return OutputYaInicializado


@pytest.mark.parametrize(
    ("module", "cls_name"),
    [(players_sound, "SoundPlayer"), (helpers_sound, "playsound")],
)
def test_arranca_sin_dispositivo_de_audio(module, cls_name):
    """No sound card: the constructor must survive and come up muted."""
    with patch.object(module, "Output", _output_sin_tarjeta()):
        player = getattr(module, cls_name)()
    assert player.output is None
    assert player.devicenames == []
    assert player.sound is None


@pytest.mark.parametrize(
    ("module", "cls_name", "play_name"),
    [(players_sound, "SoundPlayer", "play"), (helpers_sound, "playsound", "playsound")],
)
def test_sin_audio_reproducir_es_silencioso(module, cls_name, play_name):
    """Muted mode: playing must be a quiet no-op, not a crash."""
    with patch.object(module, "Output", _output_sin_tarjeta()):
        player = getattr(module, cls_name)()
    getattr(player, play_name)("sounds/default/msj.mp3")
    assert player.sound is None


@pytest.mark.parametrize(
    ("module", "cls_name"),
    [(players_sound, "SoundPlayer"), (helpers_sound, "playsound")],
)
def test_sin_audio_setdevice_es_silencioso(module, cls_name):
    """Muted mode: selecting a device must not raise (Ajustes calls it)."""
    with patch.object(module, "Output", _output_sin_tarjeta()):
        player = getattr(module, cls_name)()
    player.setdevice(1)
    assert player.device == 1


def test_sin_audio_toggle_y_release_no_revientan():
    """Muted mode: media helpers guard the never-created stream."""
    with patch.object(players_sound, "Output", _output_sin_tarjeta()):
        player = players_sound.SoundPlayer()
    player.toggle_player()
    player.release()


@pytest.mark.parametrize(
    ("module", "cls_name"),
    [(players_sound, "SoundPlayer"), (helpers_sound, "playsound")],
)
def test_codigo_14_sigue_reintentando(module, cls_name):
    """Code 14 keeps its historical behaviour: free, retry, working player."""
    doble = _output_ya_inicializado()
    with patch.object(module, "Output", doble):
        player = getattr(module, cls_name)()
    assert doble.liberado
    assert doble.intentos == 2
    assert player.output is not None
    assert player.devicenames == ["Altavoces"]


def test_sin_audio_fijar_dispositivo_lector_no_revienta():
    """Muted mode: fijar_dispositivo_lector must not index the empty list.

    Found by the PR #130 code review: setup.py clamps config["dispositivo"] to
    1 even for an empty device list, and fijar_dispositivo_lector then does
    nombres_dispositivos[0] on [] -> IndexError, reached at startup whenever
    the configured engine is piper/kokoro (with a model) or edge.  The muted
    fix must cover that path too, or a user with broken audio and one of those
    engines still dies at startup.
    """
    from utils import app_utilitys

    with (
        patch.object(app_utilitys, "player") as fake_player,
        patch.object(app_utilitys, "reader") as fake_reader,
    ):
        fake_player.devicenames = []
        app_utilitys.fijar_dispositivo_lector()
    fake_reader._lector.set_device.assert_not_called()


def test_con_audio_fijar_dispositivo_lector_sigue_fijando():
    """Normal mode keeps its behaviour: the configured device is applied."""
    from utils import app_utilitys

    with (
        patch.object(app_utilitys, "player") as fake_player,
        patch.object(app_utilitys, "reader") as fake_reader,
        patch.dict(app_utilitys.config, {"dispositivo": 1}),
    ):
        fake_player.devicenames = ["Altavoces"]
        app_utilitys.fijar_dispositivo_lector()
    fake_reader._lector.set_device.assert_called_once()


@pytest.mark.parametrize(
    ("module", "cls_name"),
    [(players_sound, "SoundPlayer"), (helpers_sound, "playsound")],
)
def test_codigo_14_y_reintento_fallido_arranca_mudo(module, cls_name):
    """Code 14 followed by a failing retry must still come up muted."""

    class OutputSiempre14:
        def __init__(self, device=-1):
            raise BassError(14, "Already initialized")

        @staticmethod
        def free():
            pass

    with patch.object(module, "Output", OutputSiempre14):
        player = getattr(module, cls_name)()
    assert player.output is None
    assert player.devicenames == []
