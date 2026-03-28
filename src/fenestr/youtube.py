"""YouTube rendering helpers for the fenestr library."""

from fenestr.exceptions import InvalidURLError, UnsupportedPlatformError
from fenestr.logger import get_logger
from fenestr.validators import extract_video_id, is_youtube_url

_logger = get_logger()

_MIN_DIM = 200
_MAX_DIM = 3000


def _warn_dimensions(width: int, height: int) -> None:
    if width < _MIN_DIM or width > _MAX_DIM:
        _logger.warning("Unusual width value: %d (expected %d–%d)", width, _MIN_DIM, _MAX_DIM)
    if height < _MIN_DIM or height > _MAX_DIM:
        _logger.warning("Unusual height value: %d (expected %d–%d)", height, _MIN_DIM, _MAX_DIM)


def _display_youtube_iframe(src: str, width: int, height: int) -> None:
    """Render a YouTube embed using HTML with required allow attributes."""
    try:
        from IPython.display import HTML, display  # type: ignore[import]
    except ImportError as exc:
        raise UnsupportedPlatformError(
            "IPython is required to render content in a Jupyter notebook. "
            "Install it with: pip install ipython"
        ) from exc

    iframe_html = (
        f'<iframe width="{width}" height="{height}" src="{src}" '
        'frameborder="0" '
        'allow="accelerometer; autoplay; clipboard-write; '
        'encrypted-media; gyroscope; picture-in-picture" '
        'allowfullscreen></iframe>'
    )
    try:
        display(HTML(iframe_html))  # type: ignore[no-untyped-call]
    except Exception as exc:  # noqa: BLE001
        raise UnsupportedPlatformError(
            "Failed to render iframe — are you running inside a Jupyter notebook?"
        ) from exc


def render_youtube(
    url: str,
    width: int = 800,
    height: int = 450,
    autoplay: bool = False,
) -> None:
    """Render a YouTube video inside a Jupyter Notebook cell.

    Args:
        url: A YouTube video URL in any supported format
            (``watch?v=``, ``youtu.be/``, ``/embed/``).
        width: IFrame width in pixels. Defaults to ``800``.
        height: IFrame height in pixels. Defaults to ``450``.
        autoplay: When ``True``, the video starts playing automatically.
            Defaults to ``False``.

    Raises:
        InvalidURLError: If *url* is not a recognised YouTube URL.
        UnsupportedPlatformError: If IPython is unavailable or the code
            is not running inside a Jupyter environment.

    Examples:
        >>> render_youtube("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        >>> render_youtube("https://youtu.be/dQw4w9WgXcQ", width=1280, height=720)
        >>> render_youtube("https://youtu.be/dQw4w9WgXcQ", autoplay=True)
    """
    if not is_youtube_url(url):
        raise InvalidURLError(f"Not a recognised YouTube URL: {url!r}", url=url)

    video_id = extract_video_id(url)
    embed_url = f"https://www.youtube.com/embed/{video_id}"
    if autoplay:
        embed_url += "?autoplay=1"

    _warn_dimensions(width, height)
    _logger.debug("Rendering YouTube video %r (autoplay=%s)", video_id, autoplay)
    _display_youtube_iframe(embed_url, width, height)


def render_youtube_playlist(
    playlist_id: str,
    width: int = 800,
    height: int = 450,
) -> None:
    """Render a YouTube playlist inside a Jupyter Notebook cell.

    Args:
        playlist_id: The YouTube playlist ID (the ``list=`` parameter value).
        width: IFrame width in pixels. Defaults to ``800``.
        height: IFrame height in pixels. Defaults to ``450``.

    Raises:
        InvalidURLError: If *playlist_id* is empty.
        UnsupportedPlatformError: If IPython is unavailable or the code
            is not running inside a Jupyter environment.

    Examples:
        >>> render_youtube_playlist("PLxxxxxxxxxxxxxxxx")
        >>> render_youtube_playlist("PLxxxxxxxxxxxxxxxx", width=1280, height=720)
    """
    if not playlist_id or not playlist_id.strip():
        raise InvalidURLError("playlist_id must be a non-empty string.")

    embed_url = f"https://www.youtube.com/embed/videoseries?list={playlist_id}"
    _warn_dimensions(width, height)
    _logger.debug("Rendering YouTube playlist %r", playlist_id)
    _display_youtube_iframe(embed_url, width, height)
