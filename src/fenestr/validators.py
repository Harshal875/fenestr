"""URL validation helpers for the fenestr library."""

import re
import urllib.parse
from typing import Optional

from fenestr.exceptions import InvalidURLError
from fenestr.logger import get_logger

_logger = get_logger()

_YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "youtu.be", "www.youtu.be"}

# Matches the 11-character base64url video ID
_VIDEO_ID_RE = re.compile(r"[A-Za-z0-9_-]{11}")


def is_https(url: str) -> bool:
    """Return ``True`` if *url* uses the ``https`` scheme.

    Args:
        url: The URL string to check.

    Returns:
        ``True`` for ``https://`` URLs, ``False`` for everything else.

    Examples:
        >>> is_https("https://example.com")
        True
        >>> is_https("http://example.com")
        False
    """
    return urllib.parse.urlparse(url).scheme == "https"


def is_valid_url(url: str) -> bool:
    """Return ``True`` if *url* is a well-formed, HTTPS URL.

    Checks that the scheme is ``https`` and that a non-empty network
    location (host) is present.

    Args:
        url: The URL string to validate.

    Returns:
        ``True`` when both conditions are satisfied.

    Examples:
        >>> is_valid_url("https://example.com/page")
        True
        >>> is_valid_url("http://example.com")
        False
        >>> is_valid_url("not-a-url")
        False
    """
    try:
        parsed = urllib.parse.urlparse(url)
        return parsed.scheme == "https" and bool(parsed.netloc)
    except ValueError:
        _logger.debug("urlparse raised ValueError for input: %r", url)
        return False


def is_youtube_url(url: str) -> bool:
    """Return ``True`` if *url* points to a YouTube video.

    Supported formats:

    - ``https://www.youtube.com/watch?v=VIDEO_ID``
    - ``https://youtube.com/watch?v=VIDEO_ID``
    - ``https://youtu.be/VIDEO_ID``
    - ``https://www.youtube.com/embed/VIDEO_ID``

    Args:
        url: The URL string to check.

    Returns:
        ``True`` when *url* belongs to a recognised YouTube host.

    Examples:
        >>> is_youtube_url("https://youtu.be/dQw4w9WgXcQ")
        True
        >>> is_youtube_url("https://example.com")
        False
    """
    try:
        host = urllib.parse.urlparse(url).netloc.lower()
        return host in _YOUTUBE_HOSTS
    except ValueError:
        return False


def extract_video_id(url: str) -> str:
    """Extract the YouTube video ID from *url*.

    Handles the following URL patterns:

    - ``watch?v=VIDEO_ID`` query parameter
    - ``/embed/VIDEO_ID`` path segment
    - ``youtu.be/VIDEO_ID`` short-link path

    Args:
        url: A YouTube URL string.

    Returns:
        The 11-character video ID string.

    Raises:
        InvalidURLError: If no valid video ID can be extracted from *url*.

    Examples:
        >>> extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> extract_video_id("https://youtu.be/dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
    """
    video_id: Optional[str] = None
    try:
        parsed = urllib.parse.urlparse(url)
        host = parsed.netloc.lower()
        query = urllib.parse.parse_qs(parsed.query)
        path_parts = [p for p in parsed.path.split("/") if p]

        if "v" in query:
            # watch?v=VIDEO_ID  (any YouTube host)
            video_id = query["v"][0]
        elif host in _YOUTUBE_HOSTS:
            # /embed/VIDEO_ID  →  path_parts == ["embed", "<id>"]
            # youtu.be/VIDEO_ID  →  path_parts == ["<id>"]
            if len(path_parts) >= 2 and path_parts[0] == "embed":
                video_id = path_parts[1]
            elif len(path_parts) == 1 and host in {"youtu.be", "www.youtu.be"}:
                video_id = path_parts[0]
    except ValueError:
        pass

    if video_id and _VIDEO_ID_RE.fullmatch(video_id):
        _logger.debug("Extracted video ID %r from %r", video_id, url)
        return video_id

    _logger.debug("Could not extract video ID from %r", url)
    raise InvalidURLError(
        f"Could not extract a valid YouTube video ID from URL: {url!r}",
        url=url,
    )
