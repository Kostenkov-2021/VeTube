"""Tests for update.extractor module."""

import os
import zipfile
from unittest.mock import patch, MagicMock

import pytest

from update.extractor import extract


class TestExtract:
    def test_extracts_all_files(self, tmp_path):
        zip_path = str(tmp_path / "test.zip")
        dest = str(tmp_path / "out")
        os.makedirs(dest)

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("file1.txt", "content1")
            zf.writestr("file2.txt", "content2")

        extract(zip_path, dest)
        assert os.path.isfile(os.path.join(dest, "file1.txt"))
        assert os.path.isfile(os.path.join(dest, "file2.txt"))

    def test_progress_callback(self, tmp_path):
        zip_path = str(tmp_path / "test.zip")
        dest = str(tmp_path / "out")
        os.makedirs(dest)

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("a.txt", "aaa")
            zf.writestr("b.txt", "bbb")
            zf.writestr("c.txt", "ccc")

        callback = MagicMock()
        extract(zip_path, dest, progress_callback=callback)
        assert callback.call_count == 3
        callback.assert_any_call(1, 3)
        callback.assert_any_call(2, 3)
        callback.assert_any_call(3, 3)

    def test_bad_zip_file_cleans_up(self, tmp_path):
        zip_path = str(tmp_path / "bad.zip")
        with open(zip_path, "wb") as f:
            f.write(b"not a zip file")
        dest = str(tmp_path / "out")
        os.makedirs(dest)

        with pytest.raises(zipfile.BadZipFile):
            extract(zip_path, dest)

    @patch("update.extractor.zipfile.ZipFile")
    def test_permission_error_cleans_up(self, mock_zipfile_cls, tmp_path):
        dest = str(tmp_path / "out")
        os.makedirs(dest)

        mock_member = MagicMock()
        mock_zf = MagicMock()
        mock_zf.infolist.return_value = [mock_member, mock_member]
        mock_zf.extract.side_effect = [None, PermissionError("locked")]
        mock_zf.__enter__ = MagicMock(return_value=mock_zf)
        mock_zf.__exit__ = MagicMock(return_value=False)
        mock_zipfile_cls.return_value = mock_zf

        with pytest.raises(PermissionError):
            extract("fake.zip", dest)

    @patch("update.extractor.zipfile.ZipFile")
    def test_os_error_cleans_up(self, mock_zipfile_cls, tmp_path):
        dest = str(tmp_path / "out")
        os.makedirs(dest)

        mock_member = MagicMock()
        mock_zf = MagicMock()
        mock_zf.infolist.return_value = [mock_member]
        mock_zf.extract.side_effect = OSError("disk full")
        mock_zf.__enter__ = MagicMock(return_value=mock_zf)
        mock_zf.__exit__ = MagicMock(return_value=False)
        mock_zipfile_cls.return_value = mock_zf

        with pytest.raises(OSError):
            extract("fake.zip", dest)

    @patch("update.extractor.zipfile.ZipFile")
    @patch("update.extractor.shutil.rmtree")
    def test_partial_extraction_cleanup(self, mock_rmtree, mock_zipfile_cls, tmp_path):
        dest = str(tmp_path / "out")
        os.makedirs(dest)

        mock_member = MagicMock()
        mock_zf = MagicMock()
        mock_zf.infolist.return_value = [mock_member]
        mock_zf.extract.side_effect = OSError("fail")
        mock_zf.__enter__ = MagicMock(return_value=mock_zf)
        mock_zf.__exit__ = MagicMock(return_value=False)
        mock_zipfile_cls.return_value = mock_zf

        with pytest.raises(OSError):
            extract("fake.zip", dest)
        mock_rmtree.assert_called_once_with(dest, ignore_errors=True)
