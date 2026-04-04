"""Location component — models a named place in the world."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Location:
    """
    Data component representing a named location or city.

    Attributes
    ----------
    name:       Display name of the place.
    x:          World-space X coordinate.
    y:          World-space Y coordinate.
    population: Current population count.
    city_type:  Category string, e.g. "city", "village", "landmark".
    amenities:  List of available amenities (e.g. "hospital", "market").
    """

    name: str = "Unnamed"
    x: float = 0.0
    y: float = 0.0
    population: int = 0
    city_type: str = "city"
    amenities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "population": self.population,
            "city_type": self.city_type,
            "amenities": list(self.amenities),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Location":
        return cls(
            name=str(data.get("name", "Unnamed")),
            x=float(data.get("x", 0.0)),
            y=float(data.get("y", 0.0)),
            population=int(data.get("population", 0)),
            city_type=str(data.get("city_type", "city")),
            amenities=list(data.get("amenities", [])),
        )

    def __repr__(self) -> str:
        return (
            f"Location(name={self.name!r}, type={self.city_type!r}, "
            f"population={self.population})"
        )
