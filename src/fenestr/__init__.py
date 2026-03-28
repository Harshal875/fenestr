"""fenestr — A window into the web.

Render YouTube videos and websites inside Jupyter Notebook cells.
"""

from fenestr.core import Fenestr, html, show, site, youtube
from fenestr.exceptions import (
    FenestrError,
    InvalidURLError,
    RenderError,
    UnsupportedPlatformError,
)

__version__ = "0.1.1"

__all__ = [
    # Class-based API
    "Fenestr",
    # Convenience functions
    "show",
    "youtube",
    "site",
    "html",
    # Exceptions
    "FenestrError",
    "InvalidURLError",
    "RenderError",
    "UnsupportedPlatformError",
    # Version
    "__version__",
]
