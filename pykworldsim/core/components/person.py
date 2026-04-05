"""Person component — individual agent."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class Person:
    name: str = "Unknown"
    age: float = 0.0
    health: float = 100.0
    happiness: float = 50.0
    energy: float = 100.0
    traits: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "age": self.age, "health": self.health,
                "happiness": self.happiness, "energy": self.energy, "traits": list(self.traits)}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Person":
        return cls(name=str(d.get("name","Unknown")), age=float(d.get("age",0)),
                   health=float(d.get("health",100)), happiness=float(d.get("happiness",50)),
                   energy=float(d.get("energy",100)), traits=list(d.get("traits",[])))

    def __repr__(self) -> str:
        return f"Person(name={self.name!r}, age={self.age:.1f}, happiness={self.happiness:.1f})"
