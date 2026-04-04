"""Job component — models an occupation or role assigned to an entity."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Job:
    """
    Data component representing an entity's occupation.

    Attributes
    ----------
    title:       Job title, e.g. "Engineer", "Teacher", "Merchant".
    employer_id: Entity ID of the employer location/organisation (-1 = unemployed).
    salary:      Income per simulation tick.
    satisfaction: Job satisfaction score 0-100.
    hours:        Hours worked per tick.
    """

    title: str = "Unemployed"
    employer_id: int = -1
    salary: float = 0.0
    satisfaction: float = 50.0
    hours: float = 8.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "employer_id": self.employer_id,
            "salary": self.salary,
            "satisfaction": self.satisfaction,
            "hours": self.hours,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Job":
        return cls(
            title=str(data.get("title", "Unemployed")),
            employer_id=int(data.get("employer_id", -1)),
            salary=float(data.get("salary", 0.0)),
            satisfaction=float(data.get("satisfaction", 50.0)),
            hours=float(data.get("hours", 8.0)),
        )

    def __repr__(self) -> str:
        return f"Job(title={self.title!r}, salary={self.salary:.2f})"
