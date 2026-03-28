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


def _make_ipython_mocks():
    """Return (mock_display, mock_iframe_cls, mock_iframe_instance)."""
    mock_iframe_instance = MagicMock()
    mock_iframe_cls = MagicMock(return_value=mock_iframe_instance)
    mock_display = MagicMock()
    return mock_display, mock_iframe_cls, mock_iframe_instance


# ---------------------------------------------------------------------------
# render_youtube — happy path
# ---------------------------------------------------------------------------


class TestRenderYoutube:
    def test_renders_standard_watch_url(self) -> None:
        mock_display, mock_iframe_cls, mock_iframe_instance = _make_ipython_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(IFrame=mock_iframe_cls, display=mock_display),
            },
        ):
            render_youtube(_VALID_URL)

        mock_iframe_cls.assert_called_once_with(src=_EMBED_BASE, width=800, height=450)
        mock_display.assert_called_once_with(mock_iframe_instance)

    def test_renders_short_url(self) -> None:
        mock_display, mock_iframe_cls, mock_iframe_instance = _make_ipython_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(IFrame=mock_iframe_cls, display=mock_display),
            },
        ):
            render_youtube("https://youtu.be/dQw4w9WgXcQ")

        mock_iframe_cls.assert_called_once_with(src=_EMBED_BASE, width=800, height=450)

    def test_custom_dimensions(self) -> None:
        mock_display, mock_iframe_cls, _ = _make_ipython_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(IFrame=mock_iframe_cls, display=mock_display),
            },
        ):
            render_youtube(_VALID_URL, width=1280, height=720)

        mock_iframe_cls.assert_called_once_with(src=_EMBED_BASE, width=1280, height=720)

    def test_autoplay_appends_query_param(self) -> None:
        mock_display, mock_iframe_cls, _ = _make_ipython_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(IFrame=mock_iframe_cls, display=mock_display),
            },
        ):
            render_youtube(_VALID_URL, autoplay=True)

        expected_src = _EMBED_BASE + "?autoplay=1"
        mock_iframe_cls.assert_called_once_with(src=expected_src, width=800, height=450)

    def test_autoplay_false_no_query_param(self) -> None:
        mock_display, mock_iframe_cls, _ = _make_ipython_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(IFrame=mock_iframe_cls, display=mock_display),
            },
        ):
            render_youtube(_VALID_URL, autoplay=False)

        src = mock_iframe_cls.call_args[1]["src"]
        assert "autoplay" not in src

    def test_embed_url_format(self) -> None:
        mock_display, mock_iframe_cls, _ = _make_ipython_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(IFrame=mock_iframe_cls, display=mock_display),
            },
        ):
            render_youtube("https://www.youtube.com/embed/dQw4w9WgXcQ")

        src = mock_iframe_cls.call_args[1]["src"]
        assert src == _EMBED_BASE


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
        mock_display, mock_iframe_cls, _ = _make_ipython_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(IFrame=mock_iframe_cls, display=mock_display),
            },
        ):
            with patch("fenestr.youtube._logger") as mock_logger:
                render_youtube(_VALID_URL, width=50)
                mock_logger.warning.assert_called()

    def test_unusual_height_logs_warning(self) -> None:
        mock_display, mock_iframe_cls, _ = _make_ipython_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(IFrame=mock_iframe_cls, display=mock_display),
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
        mock_display, mock_iframe_cls, mock_iframe_instance = _make_ipython_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(IFrame=mock_iframe_cls, display=mock_display),
            },
        ):
            render_youtube_playlist(self._PLAYLIST_ID)

        mock_iframe_cls.assert_called_once_with(
            src=self._PLAYLIST_EMBED, width=800, height=450
        )
        mock_display.assert_called_once_with(mock_iframe_instance)

    def test_custom_dimensions(self) -> None:
        mock_display, mock_iframe_cls, _ = _make_ipython_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(IFrame=mock_iframe_cls, display=mock_display),
            },
        ):
            render_youtube_playlist(self._PLAYLIST_ID, width=1280, height=720)

        mock_iframe_cls.assert_called_once_with(
            src=self._PLAYLIST_EMBED, width=1280, height=720
        )

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
