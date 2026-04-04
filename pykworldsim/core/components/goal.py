"""Goal component — models an entity's current motivation or objective."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Goal:
    """
    Data component representing a single active goal for an entity.

    Attributes
    ----------
    description: Human-readable goal description.
    priority:    Priority 0-10 (higher = more urgent).
    progress:    Completion progress 0-100.
    completed:   Whether the goal has been achieved.
    goal_type:   Category: "social", "economic", "survival", "exploration", etc.
    """

    description: str = ""
    priority: float = 5.0
    progress: float = 0.0
    completed: bool = False
    goal_type: str = "generic"

    def to_dict(self) -> dict[str, Any]:
        return {
            "description": self.description,
            "priority": self.priority,
            "progress": self.progress,
            "completed": self.completed,
            "goal_type": self.goal_type,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Goal":
        return cls(
            description=str(data.get("description", "")),
            priority=float(data.get("priority", 5.0)),
            progress=float(data.get("progress", 0.0)),
            completed=bool(data.get("completed", False)),
            goal_type=str(data.get("goal_type", "generic")),
        )

    def __repr__(self) -> str:
        return (
            f"Goal({self.description!r}, priority={self.priority}, "
            f"progress={self.progress:.1f}%, completed={self.completed})"
        )
