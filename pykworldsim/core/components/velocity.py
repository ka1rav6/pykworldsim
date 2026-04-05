"""Velocity component."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class Velocity:
    """2-D velocity (units/second)."""
    dx: float = 0.0
    dy: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {"dx": self.dx, "dy": self.dy}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Velocity":
        return cls(dx=float(d["dx"]), dy=float(d["dy"]))

    def __repr__(self) -> str:
        return f"Velocity(dx={self.dx:.4f}, dy={self.dy:.4f})"
