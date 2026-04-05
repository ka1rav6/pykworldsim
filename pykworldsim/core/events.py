"""
EventBus — lightweight publish/subscribe event system.

Systems communicate via events, never via direct calls.

Usage
-----
::

    bus = EventBus()

    # Subscribe
    bus.subscribe("entity_died", lambda data: print(data))

    # Emit (dispatched immediately)
    bus.emit("entity_died", {"entity_id": 3, "cause": "starvation"})

    # Deferred emit (queued, flushed at end of tick)
    bus.emit_deferred("score_changed", {"delta": +10})
    bus.flush()   # called by Simulation after each tick
"""
from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Callable

logger = logging.getLogger(__name__)

Handler = Callable[[dict[str, Any]], None]


class EventBus:
    """
    Thread-safe publish/subscribe event bus.

    Supports both **immediate** dispatch and **deferred** (end-of-tick) dispatch.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)
        self._deferred: list[tuple[str, dict[str, Any]]] = []

    # ------------------------------------------------------------------
    # Subscription
    # ------------------------------------------------------------------

    def subscribe(self, event_name: str, handler: Handler) -> None:
        """
        Register *handler* to be called when *event_name* is emitted.

        Parameters
        ----------
        event_name: Arbitrary string key.
        handler:    Callable accepting a single ``dict`` payload argument.
        """
        self._handlers[event_name].append(handler)
        logger.debug("Subscribed to %r", event_name)

    def unsubscribe(self, event_name: str, handler: Handler) -> None:
        """Remove *handler* from *event_name* subscribers. Silent if not found."""
        handlers = self._handlers.get(event_name, [])
        try:
            handlers.remove(handler)
        except ValueError:
            pass

    # ------------------------------------------------------------------
    # Emission
    # ------------------------------------------------------------------

    def emit(self, event_name: str, data: dict[str, Any] | None = None) -> None:
        """
        Immediately dispatch *event_name* to all registered handlers.

        Parameters
        ----------
        event_name: Event identifier.
        data:       Payload dict passed to each handler.
        """
        payload = data or {}
        logger.debug("Emit %r → %d handlers", event_name, len(self._handlers[event_name]))
        for handler in list(self._handlers[event_name]):  # snapshot for safety
            handler(payload)

    def emit_deferred(self, event_name: str, data: dict[str, Any] | None = None) -> None:
        """
        Queue *event_name* for dispatch at the next :meth:`flush` call.

        Use this when emitting from inside a system update to avoid
        handler re-entrancy issues.
        """
        self._deferred.append((event_name, data or {}))

    def flush(self) -> None:
        """Dispatch all deferred events in FIFO order, then clear the queue."""
        pending = self._deferred[:]
        self._deferred.clear()
        for event_name, payload in pending:
            self.emit(event_name, payload)

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    def subscriber_count(self, event_name: str) -> int:
        """Return the number of handlers subscribed to *event_name*."""
        return len(self._handlers.get(event_name, []))

    def clear(self) -> None:
        """Remove all subscriptions and pending deferred events."""
        self._handlers.clear()
        self._deferred.clear()
