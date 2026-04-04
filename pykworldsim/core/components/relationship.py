"""Relationship component — models a connection between two entities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Relationship:
    """
    Data component encoding a directed relationship from the owner entity
    to a *target* entity.

    Attributes
    ----------
    target_id:   Entity ID of the other party.
    kind:        Relationship type: "friend", "family", "colleague", "rival", etc.
    strength:    Float in [-1, 1]. Positive = positive bond; negative = hostility.
    interactions: Total number of recorded interactions.
    """

    target_id: int = -1
    kind: str = "friend"
    strength: float = 0.5
    interactions: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "kind": self.kind,
            "strength": self.strength,
            "interactions": self.interactions,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Relationship":
        return cls(
            target_id=int(data.get("target_id", -1)),
            kind=str(data.get("kind", "friend")),
            strength=float(data.get("strength", 0.5)),
            interactions=int(data.get("interactions", 0)),
        )

    def __repr__(self) -> str:
        return (
            f"Relationship(target={self.target_id}, kind={self.kind!r}, "
            f"strength={self.strength:.2f})"
        )
