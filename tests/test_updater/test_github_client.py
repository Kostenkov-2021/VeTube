"""Tests for update.github_client module."""

import time
from unittest.mock import MagicMock, patch

import pytest

from update import github_client
from update.github_client import (
    CACHE_TTL_SECONDS,
    ReleaseInfo,
    ReleaseLookupStatus,
    _parse_release,
    _ReleaseCache,
    clear_cache,
    get_latest_release,
)


@pytest.fixture(autouse=True)
def _clear_cache_between_tests():
    clear_cache()
    yield
    clear_cache()


def _make_release(tag="v3.95", prerelease=False, with_assets=True):
    release = {
        "tag_name": tag,
        "prerelease": prerelease,
        "body": "Release notes",
        "assets": [],
    }
    if with_assets:
        release["assets"] = [
            {
                "name": "VeTube.zip",
                "browser_download_url": "https://example.com/VeTube.zip",
            },
            {
                "name": "VeTube.zip.sha256",
                "browser_download_url": "https://example.com/VeTube.zip.sha256",
            },
        ]
    return release


class TestParseRelease:
    def test_valid_release(self):
        release = _make_release()
        info = _parse_release(release)
        assert info is not None
        assert info.tag == "v3.95"
        assert info.version == "3.95"
        assert info.zip_url == "https://example.com/VeTube.zip"
        assert info.checksum_url == "https://example.com/VeTube.zip.sha256"
        assert info.zip_name == "VeTube.zip"

    def test_missing_zip_asset(self):
        release = _make_release(with_assets=False)
        release["assets"] = [
            {
                "name": "VeTube.zip.sha256",
                "browser_download_url": "https://example.com/VeTube.zip.sha256",
            },
        ]
        assert _parse_release(release) is None

    def test_missing_checksum_asset(self):
        release = _make_release(with_assets=False)
        release["assets"] = [
            {
                "name": "VeTube.zip",
                "browser_download_url": "https://example.com/VeTube.zip",
            },
        ]
        assert _parse_release(release) is None

    def test_checksum_must_match_zip(self):
        release = _make_release(with_assets=False)
        release["assets"] = [
            {"name": "vetube-v3.95.zip", "browser_download_url": "zip"},
            {"name": "vetube-v3.94.zip.sha256", "browser_download_url": "wrong"},
            {"name": "vetube-v3.95.zip.sha256", "browser_download_url": "checksum"},
        ]
        info = _parse_release(release)
        assert info is not None
        assert info.zip_url == "zip"
        assert info.checksum_url == "checksum"

    def test_invalid_version_is_ignored(self):
        assert _parse_release(_make_release("not-a-version")) is None

    def test_empty_tag(self):
        assert _parse_release({"tag_name": "", "assets": []}) is None


class TestReleaseCache:
    def test_is_fresh_when_empty(self):
        cache = _ReleaseCache()
        assert not cache.is_fresh()

    def test_is_fresh_after_store(self):
        cache = _ReleaseCache()
        info = ReleaseInfo("v1", "1", False, "", "", "", "")
        cache.store(info, "etag123")
        assert cache.is_fresh()

    def test_is_stale_after_ttl(self):
        cache = _ReleaseCache()
        info = ReleaseInfo("v1", "1", False, "", "", "", "")
        cache.store(info, "etag123")
        cache.timestamp = time.time() - CACHE_TTL_SECONDS - 1
        assert not cache.is_fresh()


class TestGetLatestRelease:
    @patch("update.github_client.httpx.Client")
    @patch("update.github_client.filter_releases")
    def test_stable_channel(self, mock_filter, mock_client_cls):
        releases = [
            _make_release("v3.95"),
            _make_release("v3.96-beta1", prerelease=True),
        ]
        mock_filter.return_value = [releases[0]]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = releases
        mock_response.headers = {"ETag": "etag1"}

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = get_latest_release(channel="stable")
        assert result is not None
        assert result.tag == "v3.95"
        mock_filter.assert_called_once_with(releases, "stable")

    @patch("update.github_client.httpx.Client")
    @patch("update.github_client.filter_releases")
    def test_beta_channel(self, mock_filter, mock_client_cls):
        releases = [_make_release("v3.96-beta1", prerelease=True)]
        mock_filter.return_value = releases

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = releases
        mock_response.headers = {"ETag": "etag2"}

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = get_latest_release(channel="beta")
        assert result is not None
        assert result.tag == "v3.96-beta1"

    @patch("update.github_client.httpx.Client")
    @patch(
        "update.github_client.filter_releases",
        side_effect=lambda releases, channel: (
            releases
            if channel == "beta"
            else [release for release in releases if not release["prerelease"]]
        ),
    )
    def test_cache_is_isolated_by_channel(self, mock_filter, mock_client_cls):
        stable = _make_release("v3.95")
        beta = _make_release("v3.96-beta1", prerelease=True)
        releases = [stable, beta]
        response = MagicMock(status_code=200, headers={"ETag": "etag"})
        response.json.return_value = releases
        client = MagicMock()
        client.get.return_value = response
        client.__enter__ = MagicMock(return_value=client)
        client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = client

        assert get_latest_release("stable").tag == "v3.95"
        assert get_latest_release("beta").tag == "v3.96-beta1"
        assert client.get.call_count == 2

    @patch("update.github_client.httpx.Client")
    @patch(
        "update.github_client.filter_releases",
        side_effect=lambda releases, channel: releases,
    )
    def test_selects_highest_valid_version_in_unsorted_response(
        self, mock_filter, mock_client_cls
    ):
        releases = [
            _make_release("v3.95"),
            _make_release("v3.97"),
            _make_release("v3.96"),
        ]
        releases.insert(1, _make_release("invalid-version"))
        response = MagicMock(status_code=200, headers={"ETag": "etag"})
        response.json.return_value = releases
        client = MagicMock()
        client.get.return_value = response
        client.__enter__ = MagicMock(return_value=client)
        client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = client

        result = get_latest_release("stable")
        assert result is not None
        assert result.tag == "v3.97"

    @patch("update.github_client.httpx.Client")
    @patch("update.github_client.filter_releases")
    def test_etag_cache_returns_cached(self, mock_filter, mock_client_cls):
        releases = [_make_release()]
        mock_filter.return_value = releases

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = releases
        mock_response.headers = {"ETag": "etag_cached"}

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result1 = get_latest_release(channel="stable")
        assert result1 is not None

        mock_response.status_code = 304
        mock_response.json.return_value = []
        mock_response.headers = {}

        result2 = get_latest_release(channel="stable")
        assert result2 is not None
        assert result2.tag == "v3.95"

    @patch("update.github_client.httpx.Client")
    def test_network_error_returns_none(self, mock_client_cls):
        import httpx

        mock_client = MagicMock()
        mock_client.get.side_effect = httpx.ConnectError("network down")
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        assert get_latest_release(channel="stable") is None

    @patch("update.github_client.httpx.Client")
    @patch("update.github_client.filter_releases", return_value=[])
    def test_successful_empty_lookup_has_explicit_status(
        self, mock_filter, mock_client_cls
    ):
        response = MagicMock(status_code=200, headers={"ETag": "etag_empty"})
        response.json.return_value = []
        client = MagicMock()
        client.get.return_value = response
        client.__enter__ = MagicMock(return_value=client)
        client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = client

        result = github_client.get_latest_release_result("stable")

        assert result.status is ReleaseLookupStatus.NO_COMPATIBLE_RELEASE
        assert result.release is None

    @patch("update.github_client.httpx.Client")
    def test_network_lookup_has_explicit_failure_status(self, mock_client_cls):
        import httpx

        client = MagicMock()
        client.get.side_effect = httpx.ConnectError("network down")
        client.__enter__ = MagicMock(return_value=client)
        client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = client

        result = github_client.get_latest_release_result("stable")

        assert result.status is ReleaseLookupStatus.FAILURE
        assert result.release is None

    @patch("update.github_client.httpx.Client")
    @patch("update.github_client.filter_releases")
    def test_no_releases_returns_none(self, mock_filter, mock_client_cls):
        mock_filter.return_value = []

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_response.headers = {"ETag": "etag_empty"}

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        assert get_latest_release(channel="stable") is None


class TestClearCache:
    def test_clears_all_fields(self):
        from update.github_client import _cache

        _cache.store(ReleaseInfo("v1", "1", False, "", "", "", ""), "etag")
        clear_cache()
        assert _cache.data is None
        assert _cache.timestamp == 0
        assert _cache.etag is None
