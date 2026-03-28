"""Tests for src/fenestr/core.py and the top-level fenestr package API."""

from unittest.mock import patch

import fenestr
from fenestr.core import Fenestr, html, show, site, youtube
from fenestr.exceptions import (
    FenestrError,
    InvalidURLError,
    RenderError,
    UnsupportedPlatformError,
)

# ---------------------------------------------------------------------------
# Shared URL fixtures
# ---------------------------------------------------------------------------

_YT_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
_SITE_URL = "https://example.com"


# ---------------------------------------------------------------------------
# Fenestr.__init__ defaults
# ---------------------------------------------------------------------------


class TestFenestrDefaults:
    def test_default_width_and_height(self) -> None:
        f = Fenestr()
        assert f.default_width == 800
        assert f.default_height == 450

    def test_custom_defaults(self) -> None:
        f = Fenestr(default_width=1280, default_height=720)
        assert f.default_width == 1280
        assert f.default_height == 720


# ---------------------------------------------------------------------------
# Fenestr._resolve
# ---------------------------------------------------------------------------


class TestFenestrResolve:
    def test_uses_instance_defaults_when_none(self) -> None:
        f = Fenestr(default_width=1000, default_height=500)
        assert f._resolve(None, None) == (1000, 500)

    def test_overrides_width_only(self) -> None:
        f = Fenestr(default_width=800, default_height=450)
        assert f._resolve(1280, None) == (1280, 450)

    def test_overrides_height_only(self) -> None:
        f = Fenestr(default_width=800, default_height=450)
        assert f._resolve(None, 720) == (800, 720)

    def test_overrides_both(self) -> None:
        f = Fenestr(default_width=800, default_height=450)
        assert f._resolve(1920, 1080) == (1920, 1080)


# ---------------------------------------------------------------------------
# Fenestr.show  — dispatch logic
# ---------------------------------------------------------------------------


class TestFenestrShow:
    def test_youtube_url_calls_render_youtube(self) -> None:
        f = Fenestr()
        with patch("fenestr.core.render_youtube") as mock_yt:
            f.show(_YT_URL)
            mock_yt.assert_called_once_with(_YT_URL, width=800, height=450)

    def test_non_youtube_url_calls_render_site(self) -> None:
        f = Fenestr()
        with patch("fenestr.core.render_site") as mock_site:
            f.show(_SITE_URL)
            mock_site.assert_called_once_with(_SITE_URL, width=800, height=450)

    def test_custom_dimensions_forwarded(self) -> None:
        f = Fenestr()
        with patch("fenestr.core.render_youtube") as mock_yt:
            f.show(_YT_URL, width=1280, height=720)
            mock_yt.assert_called_once_with(_YT_URL, width=1280, height=720)

    def test_instance_default_width_used(self) -> None:
        f = Fenestr(default_width=1000)
        with patch("fenestr.core.render_site") as mock_site:
            f.show(_SITE_URL)
            mock_site.assert_called_once_with(_SITE_URL, width=1000, height=450)


# ---------------------------------------------------------------------------
# Fenestr.youtube
# ---------------------------------------------------------------------------


class TestFenestrYoutube:
    def test_delegates_to_render_youtube(self) -> None:
        f = Fenestr()
        with patch("fenestr.core.render_youtube") as mock_yt:
            f.youtube(_YT_URL)
            mock_yt.assert_called_once_with(_YT_URL, width=800, height=450, autoplay=False)

    def test_autoplay_forwarded(self) -> None:
        f = Fenestr()
        with patch("fenestr.core.render_youtube") as mock_yt:
            f.youtube(_YT_URL, autoplay=True)
            mock_yt.assert_called_once_with(_YT_URL, width=800, height=450, autoplay=True)

    def test_custom_dimensions_forwarded(self) -> None:
        f = Fenestr(default_width=1000)
        with patch("fenestr.core.render_youtube") as mock_yt:
            f.youtube(_YT_URL, width=640, height=360)
            mock_yt.assert_called_once_with(_YT_URL, width=640, height=360, autoplay=False)


# ---------------------------------------------------------------------------
# Fenestr.site
# ---------------------------------------------------------------------------


class TestFenestrSite:
    def test_delegates_to_render_site(self) -> None:
        f = Fenestr()
        with patch("fenestr.core.render_site") as mock_site:
            f.site(_SITE_URL)
            mock_site.assert_called_once_with(_SITE_URL, width=800, height=450)

    def test_instance_defaults_used(self) -> None:
        f = Fenestr(default_width=900, default_height=600)
        with patch("fenestr.core.render_site") as mock_site:
            f.site(_SITE_URL)
            mock_site.assert_called_once_with(_SITE_URL, width=900, height=600)


# ---------------------------------------------------------------------------
# Fenestr.html
# ---------------------------------------------------------------------------


class TestFenestrHtml:
    def test_delegates_to_render_html(self) -> None:
        f = Fenestr()
        with patch("fenestr.core.render_html") as mock_html:
            f.html("<p>hi</p>")
            mock_html.assert_called_once_with("<p>hi</p>", width=800, height=450)

    def test_override_dimensions(self) -> None:
        f = Fenestr()
        with patch("fenestr.core.render_html") as mock_html:
            f.html("<p>hi</p>", width=600, height=200)
            mock_html.assert_called_once_with("<p>hi</p>", width=600, height=200)


# ---------------------------------------------------------------------------
# Module-level convenience functions
# ---------------------------------------------------------------------------


class TestModuleFunctions:
    def test_show_dispatches_youtube(self) -> None:
        with patch("fenestr.core.render_youtube") as mock_yt:
            show(_YT_URL)
            mock_yt.assert_called_once()

    def test_show_dispatches_site(self) -> None:
        with patch("fenestr.core.render_site") as mock_site:
            show(_SITE_URL)
            mock_site.assert_called_once()

    def test_youtube_function(self) -> None:
        with patch("fenestr.core.render_youtube") as mock_yt:
            youtube(_YT_URL, autoplay=True)
            mock_yt.assert_called_once_with(_YT_URL, width=800, height=450, autoplay=True)

    def test_site_function(self) -> None:
        with patch("fenestr.core.render_site") as mock_site:
            site(_SITE_URL, width=1200)
            mock_site.assert_called_once_with(_SITE_URL, width=1200, height=450)

    def test_html_function(self) -> None:
        with patch("fenestr.core.render_html") as mock_html:
            html("<b>bold</b>")
            mock_html.assert_called_once_with("<b>bold</b>", width=800, height=450)


# ---------------------------------------------------------------------------
# Top-level fenestr package public API
# ---------------------------------------------------------------------------


class TestPackagePublicApi:
    def test_version_string(self) -> None:
        assert fenestr.__version__ == "0.1.0"

    def test_fenestr_class_exported(self) -> None:
        assert fenestr.Fenestr is Fenestr

    def test_convenience_functions_exported(self) -> None:
        for name in ("show", "youtube", "site", "html"):
            assert hasattr(fenestr, name), f"fenestr.{name} not found"

    def test_exceptions_exported(self) -> None:
        for exc in (FenestrError, InvalidURLError, RenderError, UnsupportedPlatformError):
            assert hasattr(fenestr, exc.__name__)

    def test_all_list_complete(self) -> None:
        for symbol in fenestr.__all__:
            assert hasattr(fenestr, symbol), f"__all__ references missing symbol: {symbol}"
