"""Logging configuration for the fenestr library."""

import logging

_LOGGER_NAME = "fenestr"

_logger = logging.getLogger(_LOGGER_NAME)
_logger.addHandler(logging.NullHandler())
_logger.setLevel(logging.WARNING)


def get_logger() -> logging.Logger:
    """Return the fenestr library logger.

    Returns:
        The configured ``logging.Logger`` instance named ``"fenestr"``.
        By default it uses a ``NullHandler`` so it never emits output
        unless the calling application configures handlers itself.
    """
    return _logger


def set_debug_mode(enabled: bool) -> None:
    """Toggle DEBUG-level logging for the fenestr library.

    Args:
        enabled: When ``True``, sets the logger level to ``DEBUG``.
            When ``False``, resets it to ``WARNING``.
    """
    _logger.setLevel(logging.DEBUG if enabled else logging.WARNING)
