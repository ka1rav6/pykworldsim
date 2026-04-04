"""Position component — 2-D spatial coordinate."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class Position:
    """Mutable 2-D position in world-space.

    Attributes
    ----------
    x: Horizontal coordinate.
    y: Vertical coordinate.
    """
    x: float = 0.0
    y: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {"x": self.x, "y": self.y}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Position":
        return cls(x=float(data["x"]), y=float(data["y"]))

    def __repr__(self) -> str:
        return f"Position(x={self.x:.4f}, y={self.y:.4f})"
