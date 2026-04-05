"""EventSystem — fires scheduled EventComponent events via the EventBus."""
from __future__ import annotations
import logging
from typing import TYPE_CHECKING
from pykworldsim.core.systems.base_system import BaseSystem
from pykworldsim.core.components.event_component import EventComponent
from pykworldsim.core.components.person import Person
if TYPE_CHECKING:
    from pykworldsim.core.world import World

logger = logging.getLogger(__name__)

class EventSystem(BaseSystem):
    """Processes scheduled EventComponent components and dispatches via EventBus."""
    priority: int = 1

    def __init__(self) -> None:
        super().__init__()
        self._tick: int = 0

    def update(self, world: "World", dt: float) -> None:
        self._tick += 1
        for entity, (event,) in world.get_entities_with(EventComponent):
            if event.resolved or self._tick < event.tick_scheduled:
                continue
            logger.info("Firing event %r (type=%r) on %r", event.name, event.event_type, entity)
            world.events.emit(event.event_type, {
                "entity": entity, "event": event, "world": world
            })
            if world.has_component(entity, Person):
                person = world.get_component(entity, Person)
                if event.event_type == "social":
                    person.happiness = min(100.0, person.happiness + 10.0)
                elif event.event_type == "economic":
                    person.happiness = min(100.0, person.happiness + 5.0)
            event.resolved = True
