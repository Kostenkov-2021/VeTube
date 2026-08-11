"""Tests for update.downloader module."""

from unittest.mock import patch, MagicMock

import pytest

from update.downloader import download


class TestDownload:
    @patch("update.downloader.httpx.Client")
    def test_writes_file_correctly(self, mock_client_cls, tmp_path):
        dest = str(tmp_path / "out.zip")
        chunks = [b"chunk1", b"chunk2", b"chunk3"]

        mock_response = MagicMock()
        mock_response.headers = {"content-length": "18"}
        mock_response.iter_bytes.return_value = chunks
        mock_response.raise_for_status = MagicMock()

        mock_stream = MagicMock()
        mock_stream.__enter__ = MagicMock(return_value=mock_response)
        mock_stream.__exit__ = MagicMock(return_value=False)

        mock_client = MagicMock()
        mock_client.stream.return_value = mock_stream
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = download("https://example.com/file.zip", dest)
        assert result == dest
        with open(dest, "rb") as f:
            assert f.read() == b"chunk1chunk2chunk3"

    @patch("update.downloader.httpx.Client")
    def test_progress_callback_called(self, mock_client_cls, tmp_path):
        dest = str(tmp_path / "out.zip")
        chunks = [b"a" * 100, b"b" * 200]

        mock_response = MagicMock()
        mock_response.headers = {"content-length": "300"}
        mock_response.iter_bytes.return_value = chunks
        mock_response.raise_for_status = MagicMock()

        mock_stream = MagicMock()
        mock_stream.__enter__ = MagicMock(return_value=mock_response)
        mock_stream.__exit__ = MagicMock(return_value=False)

        mock_client = MagicMock()
        mock_client.stream.return_value = mock_stream
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        callback = MagicMock()
        download("https://example.com/file.zip", dest, progress_callback=callback)
        assert callback.call_count == 2
        callback.assert_any_call(100, 300)
        callback.assert_any_call(300, 300)

    @patch("update.downloader.httpx.Client")
    def test_http_error_propagated(self, mock_client_cls, tmp_path):
        import httpx
        dest = str(tmp_path / "out.zip")

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=MagicMock()
        )

        mock_stream = MagicMock()
        mock_stream.__enter__ = MagicMock(return_value=mock_response)
        mock_stream.__exit__ = MagicMock(return_value=False)

        mock_client = MagicMock()
        mock_client.stream.return_value = mock_stream
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        with pytest.raises(httpx.HTTPStatusError):
            download("https://example.com/missing.zip", dest)
