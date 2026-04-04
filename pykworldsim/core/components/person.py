"""Person component — models an individual agent in the simulation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Person:
    """
    Data component representing a person/individual agent.

    Attributes
    ----------
    name:       Display name.
    age:        Age in simulation years.
    health:     Health score 0-100.
    happiness:  Happiness score 0-100.
    energy:     Energy score 0-100 (depletes with actions).
    traits:     Arbitrary string traits (e.g. "curious", "introverted").
    """

    name: str = "Unknown"
    age: float = 0.0
    health: float = 100.0
    happiness: float = 50.0
    energy: float = 100.0
    traits: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "age": self.age,
            "health": self.health,
            "happiness": self.happiness,
            "energy": self.energy,
            "traits": list(self.traits),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Person":
        return cls(
            name=str(data.get("name", "Unknown")),
            age=float(data.get("age", 0.0)),
            health=float(data.get("health", 100.0)),
            happiness=float(data.get("happiness", 50.0)),
            energy=float(data.get("energy", 100.0)),
            traits=list(data.get("traits", [])),
        )

    def __repr__(self) -> str:
        return (
            f"Person(name={self.name!r}, age={self.age:.1f}, "
            f"health={self.health:.1f}, happiness={self.happiness:.1f})"
        )
