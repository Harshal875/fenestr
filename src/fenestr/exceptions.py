"""Custom exceptions for the fenestr library."""

from typing import Optional


class FenestrError(Exception):
    """Base exception for all fenestr errors.

    Args:
        message: Human-readable description of the error.
        url: The URL that caused the error, if applicable.
    """

    def __init__(self, message: str, url: Optional[str] = None) -> None:
        super().__init__(message)
        self.url = url


class InvalidURLError(FenestrError):
    """Raised when a URL is malformed or not supported by fenestr.

    Args:
        message: Human-readable description of the error.
        url: The invalid URL.
    """


class RenderError(FenestrError):
    """Raised when fenestr fails to render output into the notebook cell.

    Args:
        message: Human-readable description of the error.
        url: The URL that could not be rendered, if applicable.
    """


class UnsupportedPlatformError(FenestrError):
    """Raised when fenestr is used outside a Jupyter environment.

    Args:
        message: Human-readable description of the error.
        url: The URL that was requested, if applicable.
    """
