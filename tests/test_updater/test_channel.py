"""Tests for update.channel module."""

from unittest.mock import patch

import pytest

from update.channel import filter_releases, get_channel, set_channel


@pytest.fixture
def mock_config():
    with (
        patch("update.channel.leerConfiguracion") as leer,
        patch("update.channel.guardarConfiguracion") as guardar,
    ):
        leer.return_value = {}
        yield leer, guardar


class TestGetChannel:
    def test_returns_stable_when_key_missing(self, mock_config):
        leer, _ = mock_config
        leer.return_value = {}
        assert get_channel() == "stable"

    def test_returns_stable_when_invalid_value(self, mock_config):
        leer, _ = mock_config
        leer.return_value = {"update_channel": "nightly"}
        assert get_channel() == "stable"

    def test_returns_stable_when_set(self, mock_config):
        leer, _ = mock_config
        leer.return_value = {"update_channel": "stable"}
        assert get_channel() == "stable"

    def test_returns_beta_when_set(self, mock_config):
        leer, _ = mock_config
        leer.return_value = {"update_channel": "beta"}
        assert get_channel() == "beta"


class TestSetChannel:
    def test_writes_to_config(self, mock_config):
        leer, guardar = mock_config
        leer.return_value = {"existing_key": "value"}
        set_channel("beta")
        guardar.assert_called_once_with(
            {"existing_key": "value", "update_channel": "beta"}
        )

    def test_raises_for_invalid_channel(self, mock_config):
        _, guardar = mock_config
        with pytest.raises(ValueError, match="Invalid channel"):
            set_channel("nightly")
        guardar.assert_not_called()

    def test_accepts_stable(self, mock_config):
        _, guardar = mock_config
        set_channel("stable")
        guardar.assert_called_once()


class TestFilterReleases:
    @pytest.fixture
    def releases(self):
        return [
            {"tag_name": "v3.95", "prerelease": False},
            {"tag_name": "v3.96-beta1", "prerelease": True},
            {"tag_name": "v3.94", "prerelease": False},
            {"tag_name": "v4.0-rc1", "prerelease": True},
        ]

    def test_stable_excludes_prereleases(self, releases):
        result = filter_releases(releases, "stable")
        assert len(result) == 2
        assert [r["tag_name"] for r in result] == ["v3.95", "v3.94"]

    def test_beta_includes_all(self, releases):
        result = filter_releases(releases, "beta")
        assert len(result) == 4

    def test_stable_excludes_prerelease_flag_without_tag_suffix(self):
        releases = [{"tag_name": "v3.95", "prerelease": True}]
        assert filter_releases(releases, "stable") == []

    def test_empty_list(self):
        assert filter_releases([], "stable") == []
        assert filter_releases([], "beta") == []
