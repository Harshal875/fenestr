"""Tests for src/fenestr/youtube.py."""

from unittest.mock import MagicMock, patch

import pytest

from fenestr.exceptions import InvalidURLError, UnsupportedPlatformError
from fenestr.youtube import render_youtube, render_youtube_playlist

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_VALID_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
_VIDEO_ID = "dQw4w9WgXcQ"
_EMBED_BASE = f"https://www.youtube.com/embed/{_VIDEO_ID}"


def _make_html_mocks():
    """Return (mock_display, mock_html_cls, mock_html_instance)."""
    mock_html_instance = MagicMock()
    mock_html_cls = MagicMock(return_value=mock_html_instance)
    mock_display = MagicMock()
    return mock_display, mock_html_cls, mock_html_instance


def _get_rendered_src(mock_html_cls: MagicMock) -> str:
    """Extract the src attribute value from the HTML string passed to HTML()."""
    html_str: str = mock_html_cls.call_args[0][0]
    # src="..." is always present in our iframe template
    start = html_str.index('src="') + 5
    end = html_str.index('"', start)
    return html_str[start:end]


# ---------------------------------------------------------------------------
# render_youtube — happy path
# ---------------------------------------------------------------------------


class TestRenderYoutube:
    def test_renders_standard_watch_url(self) -> None:
        mock_display, mock_html_cls, mock_html_instance = _make_html_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(HTML=mock_html_cls, display=mock_display),
            },
        ):
            render_youtube(_VALID_URL)

        assert _get_rendered_src(mock_html_cls) == _EMBED_BASE
        mock_display.assert_called_once_with(mock_html_instance)

    def test_renders_short_url(self) -> None:
        mock_display, mock_html_cls, _ = _make_html_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(HTML=mock_html_cls, display=mock_display),
            },
        ):
            render_youtube("https://youtu.be/dQw4w9WgXcQ")

        assert _get_rendered_src(mock_html_cls) == _EMBED_BASE

    def test_custom_dimensions_in_html(self) -> None:
        mock_display, mock_html_cls, _ = _make_html_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(HTML=mock_html_cls, display=mock_display),
            },
        ):
            render_youtube(_VALID_URL, width=1280, height=720)

        html_str: str = mock_html_cls.call_args[0][0]
        assert 'width="1280"' in html_str
        assert 'height="720"' in html_str

    def test_iframe_has_allow_attributes(self) -> None:
        mock_display, mock_html_cls, _ = _make_html_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(HTML=mock_html_cls, display=mock_display),
            },
        ):
            render_youtube(_VALID_URL)

        html_str: str = mock_html_cls.call_args[0][0]
        assert "allow=" in html_str
        assert "encrypted-media" in html_str
        assert "allowfullscreen" in html_str

    def test_autoplay_appends_query_param(self) -> None:
        mock_display, mock_html_cls, _ = _make_html_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(HTML=mock_html_cls, display=mock_display),
            },
        ):
            render_youtube(_VALID_URL, autoplay=True)

        assert _get_rendered_src(mock_html_cls) == _EMBED_BASE + "?autoplay=1"

    def test_autoplay_false_no_query_param(self) -> None:
        mock_display, mock_html_cls, _ = _make_html_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(HTML=mock_html_cls, display=mock_display),
            },
        ):
            render_youtube(_VALID_URL, autoplay=False)

        assert "autoplay" not in _get_rendered_src(mock_html_cls)

    def test_embed_url_format(self) -> None:
        mock_display, mock_html_cls, _ = _make_html_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(HTML=mock_html_cls, display=mock_display),
            },
        ):
            render_youtube("https://www.youtube.com/embed/dQw4w9WgXcQ")

        assert _get_rendered_src(mock_html_cls) == _EMBED_BASE


# ---------------------------------------------------------------------------
# render_youtube — error cases
# ---------------------------------------------------------------------------


class TestRenderYoutubeErrors:
    def test_invalid_url_raises(self) -> None:
        with pytest.raises(InvalidURLError):
            render_youtube("https://example.com/video")

    def test_non_url_string_raises(self) -> None:
        with pytest.raises(InvalidURLError):
            render_youtube("not-a-url")

    def test_empty_string_raises(self) -> None:
        with pytest.raises(InvalidURLError):
            render_youtube("")

    def test_missing_ipython_raises_unsupported_platform(self) -> None:
        with patch.dict("sys.modules", {"IPython": None, "IPython.display": None}):
            with pytest.raises(UnsupportedPlatformError):
                render_youtube(_VALID_URL)

    def test_unusual_width_logs_warning(self) -> None:
        mock_display, mock_html_cls, _ = _make_html_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(HTML=mock_html_cls, display=mock_display),
            },
        ):
            with patch("fenestr.youtube._logger") as mock_logger:
                render_youtube(_VALID_URL, width=50)
                mock_logger.warning.assert_called()

    def test_unusual_height_logs_warning(self) -> None:
        mock_display, mock_html_cls, _ = _make_html_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(HTML=mock_html_cls, display=mock_display),
            },
        ):
            with patch("fenestr.youtube._logger") as mock_logger:
                render_youtube(_VALID_URL, height=9999)
                mock_logger.warning.assert_called()


# ---------------------------------------------------------------------------
# render_youtube_playlist
# ---------------------------------------------------------------------------


class TestRenderYoutubePlaylist:
    _PLAYLIST_ID = "PLxxxxxxxxxxxxxxxx"
    _PLAYLIST_EMBED = f"https://www.youtube.com/embed/videoseries?list={_PLAYLIST_ID}"

    def test_renders_playlist(self) -> None:
        mock_display, mock_html_cls, mock_html_instance = _make_html_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(HTML=mock_html_cls, display=mock_display),
            },
        ):
            render_youtube_playlist(self._PLAYLIST_ID)

        assert _get_rendered_src(mock_html_cls) == self._PLAYLIST_EMBED
        mock_display.assert_called_once_with(mock_html_instance)

    def test_custom_dimensions(self) -> None:
        mock_display, mock_html_cls, _ = _make_html_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(HTML=mock_html_cls, display=mock_display),
            },
        ):
            render_youtube_playlist(self._PLAYLIST_ID, width=1280, height=720)

        html_str: str = mock_html_cls.call_args[0][0]
        assert 'width="1280"' in html_str
        assert 'height="720"' in html_str

    def test_empty_playlist_id_raises(self) -> None:
        with pytest.raises(InvalidURLError):
            render_youtube_playlist("")

    def test_whitespace_playlist_id_raises(self) -> None:
        with pytest.raises(InvalidURLError):
            render_youtube_playlist("   ")

    def test_missing_ipython_raises_unsupported_platform(self) -> None:
        with patch.dict("sys.modules", {"IPython": None, "IPython.display": None}):
            with pytest.raises(UnsupportedPlatformError):
                render_youtube_playlist(self._PLAYLIST_ID)
