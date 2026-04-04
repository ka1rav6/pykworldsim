"""Entity — lightweight, immutable, thread-safe identifier."""

from __future__ import annotations

import threading
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Entity:
    """
    An immutable, hashable integer identifier for an ECS entity.

    Entities carry **no data**; all state lives in components stored in
    :class:`~pykworldsim.core.world.World`.

    Attributes
    ----------
    id:
        Unique non-negative integer assigned at creation time.
    """

    id: int

    def __repr__(self) -> str:
        return f"Entity({self.id})"


class EntityRegistry:
    """
    Thread-safe factory and lifecycle manager for :class:`Entity` objects.

    Each :class:`~pykworldsim.core.world.World` owns exactly one registry.
    """

    def __init__(self) -> None:
        self._lock: threading.Lock = threading.Lock()
        self._next_id: int = 0
        self._alive: set[int] = set()

    def create(self) -> Entity:
        """Allocate and register a new :class:`Entity`."""
        with self._lock:
            eid = self._next_id
            self._next_id += 1
            self._alive.add(eid)
            return Entity(id=eid)

    def destroy(self, entity: Entity) -> None:
        """
        Mark *entity* as destroyed.

        Raises
        ------
        KeyError
            If *entity* is not alive.
        """
        with self._lock:
            if entity.id not in self._alive:
                raise KeyError(f"{entity!r} is not alive.")
            self._alive.discard(entity.id)

    def is_alive(self, entity: Entity) -> bool:
        """Return ``True`` if *entity* has not been destroyed."""
        return entity.id in self._alive

    @property
    def alive_ids(self) -> frozenset[int]:
        """Snapshot of all currently-alive entity IDs (thread-safe)."""
        with self._lock:
            return frozenset(self._alive)

    def reset(self) -> None:
        """Destroy all entities and reset the ID counter to zero."""
        with self._lock:
            self._alive.clear()
            self._next_id = 0
