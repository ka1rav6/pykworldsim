"""Logging configuration."""
from __future__ import annotations
import logging, sys

def configure_logging(level: str | int = "INFO",
                      fmt: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                      stream=sys.stderr) -> None:
    """Configure the pykworldsim root logger."""
    numeric = level if isinstance(level, int) else getattr(logging, level.upper(), logging.INFO)
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter(fmt))
    root = logging.getLogger("pykworldsim")
    root.setLevel(numeric)
    root.handlers.clear()
    root.addHandler(handler)
