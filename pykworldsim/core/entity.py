"""
Entity — immutable, hashable ID with thread-safe registry and lifecycle hooks.

Fixes implemented
-----------------
* Thread-safe allocation via ``threading.Lock``
* Lifecycle callbacks: ``on_add`` / ``on_remove``
* Alive-set is a ``frozenset`` snapshot — never mutated during iteration
"""
from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True, slots=True)
class Entity:
    """
    Immutable, hashable integer identifier for an ECS entity.

    Entities carry **no data**; all state lives in the component store
    inside :class:`~pykworldsim.core.world.World`.
    """

    id: int

    def __repr__(self) -> str:
        return f"Entity({self.id})"


# Lifecycle hook type
LifecycleHook = Callable[[Entity], None]


class EntityRegistry:
    """
    Thread-safe factory and lifecycle manager for :class:`Entity` objects.

    Lifecycle hooks
    ---------------
    Register callbacks that fire when entities are created or destroyed::

        registry.add_on_create(lambda e: print(f"created {e}"))
        registry.add_on_destroy(lambda e: print(f"destroyed {e}"))
    """

    def __init__(self) -> None:
        self._lock: threading.Lock = threading.Lock()
        self._next_id: int = 0
        self._alive: set[int] = set()
        self._on_create: list[LifecycleHook] = []
        self._on_destroy: list[LifecycleHook] = []

    # ------------------------------------------------------------------
    # Lifecycle hook registration
    # ------------------------------------------------------------------

    def add_on_create(self, hook: LifecycleHook) -> None:
        """Register *hook* to be called whenever a new entity is created."""
        self._on_create.append(hook)

    def add_on_destroy(self, hook: LifecycleHook) -> None:
        """Register *hook* to be called just before an entity is destroyed."""
        self._on_destroy.append(hook)

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def create(self) -> Entity:
        """Allocate and register a new :class:`Entity`, firing ``on_create`` hooks."""
        with self._lock:
            eid = self._next_id
            self._next_id += 1
            self._alive.add(eid)
            entity = Entity(id=eid)

        for hook in self._on_create:
            hook(entity)
        return entity

    def destroy(self, entity: Entity) -> None:
        """
        Destroy *entity*, firing ``on_destroy`` hooks first.

        Raises
        ------
        KeyError
            If *entity* is not alive.
        """
        with self._lock:
            if entity.id not in self._alive:
                raise KeyError(f"{entity!r} is not alive.")
            self._alive.discard(entity.id)

        for hook in self._on_destroy:
            hook(entity)

    def is_alive(self, entity: Entity) -> bool:
        """Return ``True`` if *entity* has not been destroyed."""
        return entity.id in self._alive

    @property
    def alive_ids(self) -> frozenset[int]:
        """Immutable snapshot of alive entity IDs — safe to use during iteration."""
        with self._lock:
            return frozenset(self._alive)

    def reset(self) -> None:
        """Destroy all entities and reset the ID counter (clears hooks too)."""
        with self._lock:
            self._alive.clear()
            self._next_id = 0
        self._on_create.clear()
        self._on_destroy.clear()
