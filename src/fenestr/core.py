"""Core public API for the fenestr library."""

from typing import Optional

from fenestr.logger import get_logger
from fenestr.site import render_html, render_site
from fenestr.validators import is_youtube_url
from fenestr.youtube import render_youtube

_logger = get_logger()


class Fenestr:
    """Unified fenestr interface with configurable defaults.

    Args:
        default_width: Default IFrame width in pixels for all render calls.
            Defaults to ``800``.
        default_height: Default IFrame height in pixels for all render calls.
            Defaults to ``450``.

    Examples:
        >>> f = Fenestr(default_width=1000, default_height=600)
        >>> f.show("https://docs.python.org")
        >>> f.youtube("https://youtu.be/dQw4w9WgXcQ", autoplay=True)
    """

    def __init__(self, default_width: int = 800, default_height: int = 450) -> None:
        self.default_width = default_width
        self.default_height = default_height

    def _resolve(self, width: Optional[int], height: Optional[int]) -> tuple:
        return (
            width if width is not None else self.default_width,
            height if height is not None else self.default_height,
        )

    def show(self, url: str, width: Optional[int] = None, height: Optional[int] = None) -> None:
        """Render a URL automatically — detects YouTube and dispatches accordingly.

        Args:
            url: Any supported URL (YouTube or general HTTPS website).
            width: Override the instance default width.
            height: Override the instance default height.

        Examples:
            >>> f.show("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            >>> f.show("https://docs.python.org", width=1200)
        """
        w, h = self._resolve(width, height)
        if is_youtube_url(url):
            _logger.debug("show(): detected YouTube URL, delegating to render_youtube")
            render_youtube(url, width=w, height=h)
        else:
            _logger.debug("show(): non-YouTube URL, delegating to render_site")
            render_site(url, width=w, height=h)

    def youtube(
        self,
        url: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        autoplay: bool = False,
    ) -> None:
        """Render a YouTube video inside a Jupyter Notebook cell.

        Args:
            url: A YouTube video URL.
            width: Override the instance default width.
            height: Override the instance default height.
            autoplay: When ``True`` the video starts automatically.

        Examples:
            >>> f.youtube("https://youtu.be/dQw4w9WgXcQ")
            >>> f.youtube("https://youtu.be/dQw4w9WgXcQ", autoplay=True)
        """
        w, h = self._resolve(width, height)
        render_youtube(url, width=w, height=h, autoplay=autoplay)

    def site(self, url: str, width: Optional[int] = None, height: Optional[int] = None) -> None:
        """Render a website inside a Jupyter Notebook cell.

        Args:
            url: An HTTPS URL to embed.
            width: Override the instance default width.
            height: Override the instance default height.

        Examples:
            >>> f.site("https://example.com")
        """
        w, h = self._resolve(width, height)
        render_site(url, width=w, height=h)

    def html(self, content: str, width: Optional[int] = None, height: Optional[int] = None) -> None:
        """Render a raw HTML string inside a Jupyter Notebook cell.

        Args:
            content: HTML markup to display.
            width: Override the instance default width.
            height: Override the instance default height.

        Examples:
            >>> f.html("<h1>Hello from fenestr!</h1>")
        """
        w, h = self._resolve(width, height)
        render_html(content, width=w, height=h)


# ---------------------------------------------------------------------------
# Module-level default instance — powers the top-level convenience functions
# ---------------------------------------------------------------------------

_default = Fenestr()


def show(url: str, width: Optional[int] = None, height: Optional[int] = None) -> None:
    """Render a URL automatically — detects YouTube and dispatches accordingly.

    Args:
        url: Any supported URL (YouTube or general HTTPS website).
        width: IFrame width in pixels. Defaults to ``800``.
        height: IFrame height in pixels. Defaults to ``450``.

    Examples:
        >>> import fenestr
        >>> fenestr.show("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        >>> fenestr.show("https://pytorch.org/docs")
    """
    _default.show(url, width=width, height=height)


def youtube(
    url: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    autoplay: bool = False,
) -> None:
    """Render a YouTube video inside a Jupyter Notebook cell.

    Args:
        url: A YouTube video URL.
        width: IFrame width in pixels. Defaults to ``800``.
        height: IFrame height in pixels. Defaults to ``450``.
        autoplay: When ``True`` the video starts automatically.

    Examples:
        >>> fenestr.youtube("https://youtu.be/dQw4w9WgXcQ", autoplay=True)
    """
    _default.youtube(url, width=width, height=height, autoplay=autoplay)


def site(url: str, width: Optional[int] = None, height: Optional[int] = None) -> None:
    """Render a website inside a Jupyter Notebook cell.

    Args:
        url: An HTTPS URL to embed.
        width: IFrame width in pixels. Defaults to ``900``.
        height: IFrame height in pixels. Defaults to ``600``.

    Examples:
        >>> fenestr.site("https://example.com")
    """
    _default.site(url, width=width, height=height)


def html(content: str, width: Optional[int] = None, height: Optional[int] = None) -> None:
    """Render a raw HTML string inside a Jupyter Notebook cell.

    Args:
        content: HTML markup to display.
        width: IFrame width in pixels. Defaults to ``900``.
        height: IFrame height in pixels. Defaults to ``400``.

    Examples:
        >>> fenestr.html("<h1>Hello!</h1>")
    """
    _default.html(content, width=width, height=height)
