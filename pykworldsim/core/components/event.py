"""Event component — models a time-based occurrence attached to an entity."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Event:
    """
    Data component representing a scheduled or active event.

    Attributes
    ----------
    name:           Event name (e.g. "birthday", "job_offer", "disaster").
    event_type:     Category: "social", "economic", "environmental", "personal".
    tick_scheduled: Simulation tick at which this event fires.
    duration:       How many ticks the event lasts (0 = instantaneous).
    participants:   Entity IDs involved in this event.
    resolved:       Whether the event has been processed.
    payload:        Arbitrary extra data for the event handler.
    """

    name: str = "unnamed_event"
    event_type: str = "generic"
    tick_scheduled: int = 0
    duration: int = 0
    participants: list[int] = field(default_factory=list)
    resolved: bool = False
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "event_type": self.event_type,
            "tick_scheduled": self.tick_scheduled,
            "duration": self.duration,
            "participants": list(self.participants),
            "resolved": self.resolved,
            "payload": dict(self.payload),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Event":
        return cls(
            name=str(data.get("name", "unnamed_event")),
            event_type=str(data.get("event_type", "generic")),
            tick_scheduled=int(data.get("tick_scheduled", 0)),
            duration=int(data.get("duration", 0)),
            participants=list(data.get("participants", [])),
            resolved=bool(data.get("resolved", False)),
            payload=dict(data.get("payload", {})),
        )

    def __repr__(self) -> str:
        return (
            f"Event(name={self.name!r}, type={self.event_type!r}, "
            f"tick={self.tick_scheduled}, resolved={self.resolved})"
        )
