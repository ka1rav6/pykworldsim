"""EventSystem — fires scheduled events and resolves them."""
from __future__ import annotations

import logging

from pykworldsim.core.systems.base_system import BaseSystem
from pykworldsim.core.components.event import Event
from pykworldsim.core.components.person import Person

logger = logging.getLogger(__name__)


class EventSystem(BaseSystem):
    """
    Processes :class:`~pykworldsim.core.components.event.Event` components.

    Each tick the system:

    1. Finds all unresolved events whose ``tick_scheduled`` ≤ current tick.
    2. Dispatches them to registered handlers (or the default handler).
    3. Marks them ``resolved = True``.

    Custom handlers
    ---------------
    Register a handler with::

        event_system.register_handler("job_offer", my_handler_fn)

    A handler has the signature ``(world, entity, event) -> None``.
    """

    def __init__(self) -> None:
        super().__init__()
        self._tick: int = 0
        self._handlers: dict[str, list] = {}

    def register_handler(self, event_type: str, handler) -> None:  # type: ignore[type-arg]
        """Register *handler* for events of *event_type*."""
        self._handlers.setdefault(event_type, []).append(handler)
        logger.debug("Registered handler for event_type=%r", event_type)

    def update(self, dt: float) -> None:
        self._tick += 1

        for entity, (event,) in self.world.get_components(Event):
            if event.resolved:
                continue
            if self._tick < event.tick_scheduled:
                continue

            logger.info(
                "Firing event %r (type=%r) on %r",
                event.name, event.event_type, entity,
            )

            handlers = self._handlers.get(event.event_type, [])
            if handlers:
                for h in handlers:
                    h(self.world, entity, event)
            else:
                self._default_handler(entity, event)

            event.resolved = True

    def _default_handler(self, entity, event: Event) -> None:
        """Default: log the event; apply happiness boost if entity has Person."""
        logger.info("Default handler: event=%r entity=%r", event.name, entity)
        if self.world.has_component(entity, Person):
            person = self.world.get_component(entity, Person)
            # Positive social events boost happiness
            if event.event_type == "social":
                person.happiness = min(100.0, person.happiness + 10.0)
            elif event.event_type == "economic":
                person.happiness = min(100.0, person.happiness + 5.0)
