"""Velocity component — 2-D velocity vector."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class Velocity:
    """Mutable 2-D velocity (units per second).

    Attributes
    ----------
    dx: Horizontal component (positive = right).
    dy: Vertical component (positive = down by convention).
    """
    dx: float = 0.0
    dy: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {"dx": self.dx, "dy": self.dy}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Velocity":
        return cls(dx=float(data["dx"]), dy=float(data["dy"]))

    def __repr__(self) -> str:
        return f"Velocity(dx={self.dx:.4f}, dy={self.dy:.4f})"
