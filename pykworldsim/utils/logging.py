"""Logging configuration helpers."""
from __future__ import annotations

import logging
import sys


def configure_logging(
    level: str | int = "INFO",
    fmt: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
) -> None:
    """
    Configure the ``pykworldsim`` logger.

    Parameters
    ----------
    level:  Log level string (``"DEBUG"``, ``"INFO"``, …) or integer.
    fmt:    Log format string.
    stream: Output stream (default: ``sys.stderr``).

    Examples
    --------
    >>> from pykworldsim.utils import configure_logging
    >>> configure_logging("DEBUG")
    """
    numeric = (
        level if isinstance(level, int)
        else getattr(logging, level.upper(), logging.INFO)
    )
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter(fmt))
    root = logging.getLogger("pykworldsim")
    root.setLevel(numeric)
    root.handlers.clear()
    root.addHandler(handler)
