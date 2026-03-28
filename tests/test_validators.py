"""Tests for src/fenestr/validators.py."""

import pytest

from fenestr.exceptions import InvalidURLError
from fenestr.validators import (
    extract_video_id,
    is_https,
    is_valid_url,
    is_youtube_url,
)


# ---------------------------------------------------------------------------
# is_https
# ---------------------------------------------------------------------------


class TestIsHttps:
    def test_https_returns_true(self) -> None:
        assert is_https("https://example.com") is True

    def test_http_returns_false(self) -> None:
        assert is_https("http://example.com") is False

    def test_no_scheme_returns_false(self) -> None:
        assert is_https("example.com") is False

    def test_empty_string_returns_false(self) -> None:
        assert is_https("") is False

    def test_ftp_returns_false(self) -> None:
        assert is_https("ftp://files.example.com") is False


# ---------------------------------------------------------------------------
# is_valid_url
# ---------------------------------------------------------------------------


class TestIsValidUrl:
    def test_valid_https_url(self) -> None:
        assert is_valid_url("https://example.com/page") is True

    def test_https_with_path_and_query(self) -> None:
        assert is_valid_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is True

    def test_http_rejected(self) -> None:
        assert is_valid_url("http://example.com") is False

    def test_no_netloc_rejected(self) -> None:
        assert is_valid_url("https://") is False

    def test_plain_string_rejected(self) -> None:
        assert is_valid_url("not-a-url") is False

    def test_empty_string_rejected(self) -> None:
        assert is_valid_url("") is False

    def test_https_ip_address(self) -> None:
        assert is_valid_url("https://192.168.1.1/path") is True


# ---------------------------------------------------------------------------
# is_youtube_url
# ---------------------------------------------------------------------------


class TestIsYoutubeUrl:
    @pytest.mark.parametrize(
        "url",
        [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
        ],
    )
    def test_youtube_urls_recognised(self, url: str) -> None:
        assert is_youtube_url(url) is True

    def test_non_youtube_domain(self) -> None:
        assert is_youtube_url("https://vimeo.com/123456") is False

    def test_example_com(self) -> None:
        assert is_youtube_url("https://example.com") is False

    def test_http_youtube(self) -> None:
        # HTTP YouTube URLs are still identified as YouTube hosts
        assert is_youtube_url("http://www.youtube.com/watch?v=abc12345678") is True

    def test_empty_string(self) -> None:
        assert is_youtube_url("") is False


# ---------------------------------------------------------------------------
# extract_video_id
# ---------------------------------------------------------------------------


class TestExtractVideoId:
    def test_watch_url(self) -> None:
        assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_watch_url_no_www(self) -> None:
        assert extract_video_id("https://youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_short_url(self) -> None:
        assert extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_embed_url(self) -> None:
        assert extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_watch_url_with_extra_params(self) -> None:
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30&list=PLxyz"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_invalid_url_raises(self) -> None:
        with pytest.raises(InvalidURLError):
            extract_video_id("https://example.com/notayoutube")

    def test_empty_string_raises(self) -> None:
        with pytest.raises(InvalidURLError):
            extract_video_id("")

    def test_short_id_raises(self) -> None:
        # IDs shorter than 11 chars are invalid
        with pytest.raises(InvalidURLError):
            extract_video_id("https://youtu.be/short")

    def test_invalid_url_error_carries_url(self) -> None:
        bad = "https://example.com/bad"
        with pytest.raises(InvalidURLError) as exc_info:
            extract_video_id(bad)
        assert exc_info.value.url == bad
