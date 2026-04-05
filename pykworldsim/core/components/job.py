"""Job component — occupation."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class Job:
    title: str = "Unemployed"
    employer_id: int = -1
    salary: float = 0.0
    satisfaction: float = 50.0
    hours: float = 8.0

    def to_dict(self) -> dict[str, Any]:
        return {"title": self.title, "employer_id": self.employer_id,
                "salary": self.salary, "satisfaction": self.satisfaction, "hours": self.hours}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Job":
        return cls(title=str(d.get("title","Unemployed")),
                   employer_id=int(d.get("employer_id",-1)),
                   salary=float(d.get("salary",0)),
                   satisfaction=float(d.get("satisfaction",50)),
                   hours=float(d.get("hours",8)))
