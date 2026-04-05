"""Location component — named place."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class Location:
    name: str = "Unnamed"
    x: float = 0.0
    y: float = 0.0
    population: int = 0
    city_type: str = "city"
    amenities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "x": self.x, "y": self.y,
                "population": self.population, "city_type": self.city_type,
                "amenities": list(self.amenities)}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Location":
        return cls(name=str(d.get("name","Unnamed")), x=float(d.get("x",0)),
                   y=float(d.get("y",0)), population=int(d.get("population",0)),
                   city_type=str(d.get("city_type","city")),
                   amenities=list(d.get("amenities",[])))
