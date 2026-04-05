"""EventComponent — scheduled occurrence (renamed from Event to avoid clash with EventBus)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class EventComponent:
    name: str = "unnamed"
    event_type: str = "generic"
    tick_scheduled: int = 0
    duration: int = 0
    participants: list[int] = field(default_factory=list)
    resolved: bool = False
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "event_type": self.event_type,
                "tick_scheduled": self.tick_scheduled, "duration": self.duration,
                "participants": list(self.participants),
                "resolved": self.resolved, "payload": dict(self.payload)}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "EventComponent":
        return cls(name=str(d.get("name","unnamed")),
                   event_type=str(d.get("event_type","generic")),
                   tick_scheduled=int(d.get("tick_scheduled",0)),
                   duration=int(d.get("duration",0)),
                   participants=list(d.get("participants",[])),
                   resolved=bool(d.get("resolved",False)),
                   payload=dict(d.get("payload",{})))
