"""Tests for update.verifier module."""

import hashlib

import pytest

from update.verifier import compute_sha256, parse_checksum_file, verify


@pytest.fixture
def sample_file(tmp_path):
    path = str(tmp_path / "test.zip")
    with open(path, "wb") as f:
        f.write(b"hello world")
    return path


@pytest.fixture
def sample_hash():
    return hashlib.sha256(b"hello world").hexdigest().lower()


class TestComputeSha256:
    def test_known_content(self, sample_file, sample_hash):
        assert compute_sha256(sample_file) == sample_hash

    def test_empty_file(self, tmp_path):
        path = str(tmp_path / "empty.bin")
        with open(path, "wb") as f:
            pass
        expected = hashlib.sha256(b"").hexdigest().lower()
        assert compute_sha256(path) == expected

    def test_returns_lowercase(self, sample_file):
        result = compute_sha256(sample_file)
        assert result == result.lower()


class TestParseChecksumFile:
    def test_valid_two_space_format(self):
        content = "abc123  VeTube.zip\ndef456  VeTube.zip.sha256\n"
        result = parse_checksum_file(content)
        assert result == {"VeTube.zip": "abc123", "VeTube.zip.sha256": "def456"}

    def test_single_space_format(self):
        content = "abc123 VeTube.zip\n"
        result = parse_checksum_file(content)
        assert result == {"VeTube.zip": "abc123"}

    def test_skips_blank_lines(self):
        content = "abc123  VeTube.zip\n\n\ndef456  other.zip\n"
        result = parse_checksum_file(content)
        assert len(result) == 2

    def test_skips_malformed_lines(self):
        content = "abc123  VeTube.zip\njust_one_token\n"
        result = parse_checksum_file(content)
        assert len(result) == 1
        assert "VeTube.zip" in result

    def test_hash_lowercased(self):
        content = "ABC123DEF  VeTube.zip\n"
        result = parse_checksum_file(content)
        assert result["VeTube.zip"] == "abc123def"

    def test_empty_content(self):
        assert parse_checksum_file("") == {}


class TestVerify:
    def test_matching_hashes(self, sample_file, sample_hash):
        checksum_content = f"{sample_hash}  test.zip\n"
        assert verify(sample_file, checksum_content, "test.zip") is True

    def test_mismatching_hashes(self, sample_file):
        checksum_content = "0000000000000000000000000000000000000000000000000000000000000000  test.zip\n"
        assert verify(sample_file, checksum_content, "test.zip") is False

    def test_case_insensitive_comparison(self, sample_file, sample_hash):
        checksum_content = f"{sample_hash.upper()}  test.zip\n"
        assert verify(sample_file, checksum_content, "test.zip") is True

    def test_filename_not_in_checksum(self, sample_file):
        checksum_content = "abc123  other.zip\n"
        assert verify(sample_file, checksum_content, "missing.zip") is False
