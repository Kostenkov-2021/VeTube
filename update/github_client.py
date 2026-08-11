"""GitHub Releases API client with in-memory caching and ETag support."""

import logging
import time
from dataclasses import dataclass
from typing import Dict, Optional

import httpx

from update.channel import filter_releases, get_channel

logger = logging.getLogger(__name__)

RELEASES_URL = "https://api.github.com/repos/metalalchemist/VeTube/releases"
CACHE_TTL_SECONDS = 300
_USER_AGENT = "VeTube-Updater/1.0"


@dataclass
class ReleaseInfo:
    """Parsed release information from GitHub API."""

    tag: str
    version: str
    prerelease: bool
    description: str
    zip_url: str
    checksum_url: str
    zip_name: str


class _ReleaseCache:
    """In-memory cache with TTL and ETag support."""

    def __init__(self) -> None:
        self.data: Optional[ReleaseInfo] = None
        self.timestamp: float = 0
        self.etag: Optional[str] = None

    def is_fresh(self) -> bool:
        return self.data is not None and (time.time() - self.timestamp) < CACHE_TTL_SECONDS

    def store(self, release: Optional[ReleaseInfo], etag: Optional[str]) -> None:
        self.data = release
        self.timestamp = time.time()
        if etag:
            self.etag = etag


_cache = _ReleaseCache()


def _parse_release(release: dict) -> Optional[ReleaseInfo]:
    """Extract ReleaseInfo from a GitHub release dict.

    Returns None if required assets (zip + checksum) are missing.
    """
    tag = release.get("tag_name", "")
    if not tag:
        return None

    assets = release.get("assets", [])
    zip_url = ""
    zip_name = ""
    checksum_url = ""

    for asset in assets:
        name = asset.get("name", "")
        url = asset.get("browser_download_url", "")
        if name.endswith(".zip") and not zip_url:
            zip_url = url
            zip_name = name
        elif name.endswith(".sha256") and not checksum_url:
            checksum_url = url

    if not zip_url or not checksum_url:
        logger.debug("Release '%s' missing zip or checksum asset, skipping", tag)
        return None

    version = tag.lstrip("v")

    return ReleaseInfo(
        tag=tag,
        version=version,
        prerelease=release.get("prerelease", False),
        description=release.get("body", ""),
        zip_url=zip_url,
        checksum_url=checksum_url,
        zip_name=zip_name,
    )


def _fetch_releases(client: httpx.Client) -> tuple[list[dict], Optional[str], bool]:
    """Fetch releases from GitHub API.

    Returns:
        Tuple of (releases_list, etag, not_modified).
        If not_modified is True, releases_list is empty.
    """
    headers: Dict[str, str] = {"User-Agent": _USER_AGENT}
    if _cache.etag:
        headers["If-None-Match"] = _cache.etag

    response = client.get(RELEASES_URL, headers=headers, timeout=30)

    if response.status_code == 304:
        return [], None, True

    response.raise_for_status()
    etag = response.headers.get("ETag")
    return response.json(), etag, False


def get_latest_release(channel: Optional[str] = None) -> Optional[ReleaseInfo]:
    """Fetch latest release from GitHub API.

    Uses in-memory cache with 5-min TTL and ETag for conditional requests.

    Args:
        channel: 'stable' or 'beta'. Defaults to user preference.

    Returns:
        ReleaseInfo for the latest matching release, or None if no update
        available or on error.
    """
    if channel is None:
        channel = get_channel()

    if _cache.is_fresh():
        logger.debug("Returning cached release info")
        return _cache.data

    try:
        with httpx.Client() as client:
            releases, etag, not_modified = _fetch_releases(client)

            if not_modified:
                _cache.timestamp = time.time()
                return _cache.data

            filtered = filter_releases(releases, channel)
            if not filtered:
                logger.info("No releases found for channel '%s'", channel)
                _cache.store(None, etag)
                return None

            release_info = _parse_release(filtered[0])
            _cache.store(release_info, etag)
            return release_info

    except httpx.HTTPError:
        logger.exception("Failed to fetch releases from GitHub")
        return None
    except Exception:
        logger.exception("Unexpected error fetching releases")
        return None


def clear_cache() -> None:
    """Clear the release cache. Useful for forcing a fresh check."""
    _cache.data = None
    _cache.timestamp = 0
    _cache.etag = None
