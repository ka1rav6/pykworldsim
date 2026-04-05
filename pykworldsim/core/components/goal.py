"""Goal component — motivation / objective."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class Goal:
    description: str = ""
    priority: float = 5.0
    progress: float = 0.0
    completed: bool = False
    goal_type: str = "generic"

    def to_dict(self) -> dict[str, Any]:
        return {"description": self.description, "priority": self.priority,
                "progress": self.progress, "completed": self.completed,
                "goal_type": self.goal_type}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Goal":
        return cls(description=str(d.get("description","")),
                   priority=float(d.get("priority",5)),
                   progress=float(d.get("progress",0)),
                   completed=bool(d.get("completed",False)),
                   goal_type=str(d.get("goal_type","generic")))
