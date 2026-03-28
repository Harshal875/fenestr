"""Website rendering helpers for the fenestr library."""

import urllib.parse

from fenestr.exceptions import InvalidURLError, UnsupportedPlatformError
from fenestr.logger import get_logger
from fenestr.validators import is_https, is_valid_url

_logger = get_logger()

KNOWN_BLOCKED: frozenset = frozenset(
    [
        "google.com",
        "stackoverflow.com",
        "github.com",
        "medium.com",
        "twitter.com",
        "facebook.com",
    ]
)

_MIN_DIM = 200
_MAX_DIM = 3000


def _warn_dimensions(width: int, height: int) -> None:
    if width < _MIN_DIM or width > _MAX_DIM:
        _logger.warning("Unusual width value: %d (expected %d–%d)", width, _MIN_DIM, _MAX_DIM)
    if height < _MIN_DIM or height > _MAX_DIM:
        _logger.warning("Unusual height value: %d (expected %d–%d)", height, _MIN_DIM, _MAX_DIM)


def _display_iframe(src: str, width: int, height: int) -> None:
    """Lazy-import IPython and render an IFrame."""
    try:
        from IPython.display import IFrame, display  # type: ignore[import]
    except ImportError as exc:
        raise UnsupportedPlatformError(
            "IPython is required to render content in a Jupyter notebook. "
            "Install it with: pip install ipython"
        ) from exc

    try:
        display(IFrame(src=src, width=width, height=height))
    except Exception as exc:  # noqa: BLE001
        raise UnsupportedPlatformError(
            "Failed to render IFrame — are you running inside a Jupyter notebook?"
        ) from exc


def render_site(url: str, width: int = 900, height: int = 600) -> None:
    """Render a website inside a Jupyter Notebook cell using an IFrame.

    Only ``https://`` URLs are accepted. If the target domain is known to
    block iframe embedding the function still attempts to render but logs a
    warning to inform the user that a blank frame is a server-side restriction.

    Args:
        url: The full HTTPS URL of the website to embed.
        width: IFrame width in pixels. Defaults to ``900``.
        height: IFrame height in pixels. Defaults to ``600``.

    Raises:
        InvalidURLError: If *url* is malformed or uses the ``http://`` scheme.
        UnsupportedPlatformError: If IPython is unavailable or the code is not
            running inside a Jupyter environment.

    Examples:
        >>> render_site("https://example.com")
        >>> render_site("https://docs.python.org", width=1200, height=800)
    """
    if not is_https(url) or not is_valid_url(url):
        raise InvalidURLError(
            f"Only well-formed https:// URLs are supported. Got: {url!r}",
            url=url,
        )

    netloc = urllib.parse.urlparse(url).netloc.lower()
    host = netloc[4:] if netloc.startswith("www.") else netloc
    if host in KNOWN_BLOCKED:
        _logger.warning(
            "⚠️ fenestr: %s may block iframe embedding. "
            "If you see a blank frame, this is a server-side restriction "
            "unrelated to fenestr.",
            host,
        )

    _warn_dimensions(width, height)
    _logger.debug("Rendering site %r", url)
    _display_iframe(url, width, height)


def render_html(html_content: str, width: int = 900, height: int = 400) -> None:
    """Render a raw HTML string directly inside a Jupyter Notebook cell.

    Useful for embedding locally-constructed HTML snippets without needing
    a remote URL.

    Args:
        html_content: The HTML markup string to display.
        width: Display width in pixels (passed to the enclosing container).
            Defaults to ``900``.
        height: Display height in pixels. Defaults to ``400``.

    Raises:
        UnsupportedPlatformError: If IPython is unavailable or the code is not
            running inside a Jupyter environment.

    Examples:
        >>> render_html("<h1>Hello from fenestr!</h1>")
        >>> render_html("<p style='color:red'>Warning</p>", width=600, height=100)
    """
    try:
        from IPython.display import HTML, display  # type: ignore[import]
    except ImportError as exc:
        raise UnsupportedPlatformError(
            "IPython is required to render HTML in a Jupyter notebook. "
            "Install it with: pip install ipython"
        ) from exc

    _warn_dimensions(width, height)
    _logger.debug("Rendering raw HTML (%d chars)", len(html_content))

    try:
        display(HTML(html_content))
    except Exception as exc:  # noqa: BLE001
        raise UnsupportedPlatformError(
            "Failed to render HTML — are you running inside a Jupyter notebook?"
        ) from exc
