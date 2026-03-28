"""Tests for src/fenestr/site.py."""

from unittest.mock import MagicMock, patch

import pytest

from fenestr.exceptions import InvalidURLError, UnsupportedPlatformError
from fenestr.site import KNOWN_BLOCKED, render_html, render_site

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_VALID_URL = "https://example.com"


def _make_ipython_mocks():
    mock_iframe_instance = MagicMock()
    mock_iframe_cls = MagicMock(return_value=mock_iframe_instance)
    mock_html_instance = MagicMock()
    mock_html_cls = MagicMock(return_value=mock_html_instance)
    mock_display = MagicMock()
    return mock_iframe_cls, mock_html_cls, mock_iframe_instance, mock_html_instance, mock_display


# ---------------------------------------------------------------------------
# render_site — happy path
# ---------------------------------------------------------------------------


class TestRenderSite:
    def test_renders_valid_https_url(self) -> None:
        mock_iframe_cls, _, mock_iframe_instance, _, mock_display = _make_ipython_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(IFrame=mock_iframe_cls, display=mock_display),
            },
        ):
            render_site(_VALID_URL)

        mock_iframe_cls.assert_called_once_with(src=_VALID_URL, width=900, height=600)
        mock_display.assert_called_once_with(mock_iframe_instance)

    def test_custom_dimensions(self) -> None:
        mock_iframe_cls, _, _, _, mock_display = _make_ipython_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(IFrame=mock_iframe_cls, display=mock_display),
            },
        ):
            render_site(_VALID_URL, width=1200, height=800)

        mock_iframe_cls.assert_called_once_with(src=_VALID_URL, width=1200, height=800)

    def test_url_passed_unchanged_to_iframe(self) -> None:
        url = "https://docs.python.org/3/library/index.html"
        mock_iframe_cls, _, _, _, mock_display = _make_ipython_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(IFrame=mock_iframe_cls, display=mock_display),
            },
        ):
            render_site(url)

        assert mock_iframe_cls.call_args[1]["src"] == url


# ---------------------------------------------------------------------------
# render_site — KNOWN_BLOCKED warning
# ---------------------------------------------------------------------------


class TestRenderSiteBlockedDomains:
    @pytest.mark.parametrize("domain", list(KNOWN_BLOCKED))
    def test_known_blocked_domain_logs_warning(self, domain: str) -> None:
        url = f"https://www.{domain}"
        mock_iframe_cls, _, _, _, mock_display = _make_ipython_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(IFrame=mock_iframe_cls, display=mock_display),
            },
        ):
            with patch("fenestr.site._logger") as mock_logger:
                render_site(url)
                # At least one warning call should mention the domain
                warning_calls = [str(c) for c in mock_logger.warning.call_args_list]
                assert any(domain in msg for msg in warning_calls)

    def test_known_blocked_domain_still_renders(self) -> None:
        mock_iframe_cls, _, mock_iframe_instance, _, mock_display = _make_ipython_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(IFrame=mock_iframe_cls, display=mock_display),
            },
        ):
            render_site("https://github.com")

        mock_display.assert_called_once()

    def test_unknown_domain_no_warning(self) -> None:
        mock_iframe_cls, _, _, _, mock_display = _make_ipython_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(IFrame=mock_iframe_cls, display=mock_display),
            },
        ):
            with patch("fenestr.site._logger") as mock_logger:
                render_site(_VALID_URL)
                mock_logger.warning.assert_not_called()


# ---------------------------------------------------------------------------
# render_site — error cases
# ---------------------------------------------------------------------------


class TestRenderSiteErrors:
    def test_http_url_raises(self) -> None:
        with pytest.raises(InvalidURLError):
            render_site("http://example.com")

    def test_malformed_url_raises(self) -> None:
        with pytest.raises(InvalidURLError):
            render_site("not-a-url")

    def test_empty_string_raises(self) -> None:
        with pytest.raises(InvalidURLError):
            render_site("")

    def test_missing_ipython_raises_unsupported_platform(self) -> None:
        with patch.dict("sys.modules", {"IPython": None, "IPython.display": None}):
            with pytest.raises(UnsupportedPlatformError):
                render_site(_VALID_URL)

    def test_unusual_dimensions_log_warning(self) -> None:
        mock_iframe_cls, _, _, _, mock_display = _make_ipython_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(IFrame=mock_iframe_cls, display=mock_display),
            },
        ):
            with patch("fenestr.site._logger") as mock_logger:
                render_site(_VALID_URL, width=50, height=9999)
                assert mock_logger.warning.call_count >= 2


# ---------------------------------------------------------------------------
# render_html
# ---------------------------------------------------------------------------


class TestRenderHtml:
    def test_renders_html_string(self) -> None:
        _, mock_html_cls, _, mock_html_instance, mock_display = _make_ipython_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(HTML=mock_html_cls, display=mock_display),
            },
        ):
            render_html("<h1>Hello</h1>")

        mock_html_cls.assert_called_once_with("<h1>Hello</h1>")
        mock_display.assert_called_once_with(mock_html_instance)

    def test_empty_html_string_allowed(self) -> None:
        _, mock_html_cls, _, _, mock_display = _make_ipython_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(HTML=mock_html_cls, display=mock_display),
            },
        ):
            render_html("")

        mock_html_cls.assert_called_once_with("")

    def test_custom_dimensions_accepted(self) -> None:
        _, mock_html_cls, _, mock_html_instance, mock_display = _make_ipython_mocks()
        with patch.dict(
            "sys.modules",
            {
                "IPython": MagicMock(),
                "IPython.display": MagicMock(HTML=mock_html_cls, display=mock_display),
            },
        ):
            render_html("<p>test</p>", width=600, height=100)

        mock_display.assert_called_once_with(mock_html_instance)

    def test_missing_ipython_raises_unsupported_platform(self) -> None:
        with patch.dict("sys.modules", {"IPython": None, "IPython.display": None}):
            with pytest.raises(UnsupportedPlatformError):
                render_html("<p>test</p>")


# ---------------------------------------------------------------------------
# KNOWN_BLOCKED constant
# ---------------------------------------------------------------------------


class TestKnownBlocked:
    def test_is_frozenset(self) -> None:
        assert isinstance(KNOWN_BLOCKED, frozenset)

    def test_contains_expected_domains(self) -> None:
        expected = {"google.com", "stackoverflow.com", "github.com"}
        assert expected.issubset(KNOWN_BLOCKED)
