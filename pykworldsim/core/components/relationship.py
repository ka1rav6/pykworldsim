"""Relationship component — directed bond between entities."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class Relationship:
    target_id: int = -1
    kind: str = "friend"
    strength: float = 0.5
    interactions: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {"target_id": self.target_id, "kind": self.kind,
                "strength": self.strength, "interactions": self.interactions}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Relationship":
        return cls(target_id=int(d.get("target_id",-1)), kind=str(d.get("kind","friend")),
                   strength=float(d.get("strength",0.5)),
                   interactions=int(d.get("interactions",0)))
