"""BaseSystem — abstract base with priority ordering and world-query contract."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pykworldsim.core.world import World

logger = logging.getLogger(__name__)


class BaseSystem(ABC):
    """
    Abstract base for all ECS systems.

    Contract (v3)
    -------------
    ``update(world, dt)`` receives the **World** object and uses
    ``world.get_entities_with(...)`` to query only the entities it
    needs. Systems **never** access world internals directly.

    Ordering
    --------
    Systems are sorted by :attr:`priority` before each tick.
    Lower value = runs earlier. Default is ``0``.

    Attributes
    ----------
    priority: int
        Execution order. Lower = earlier. Default ``0``.
    enabled: bool
        Set ``False`` to skip this system without unregistering it.
    """

    # Class-level default; override in subclass or set on instance
    priority: int = 0

    def __init__(self) -> None:
        self._world: "World | None" = None
        self.enabled: bool = True

    @property
    def world(self) -> "World":
        if self._world is None:
            raise RuntimeError(
                f"{type(self).__name__} has not been registered with a World yet."
            )
        return self._world

    @world.setter
    def world(self, value: "World") -> None:
        self._world = value

    @abstractmethod
    def update(self, world: "World", dt: float) -> None:
        """
        Execute one tick of logic.

        Parameters
        ----------
        world:
            The world — use ``world.get_entities_with(...)`` to query.
        dt:
            Simulated time delta.
        """

    def on_register(self) -> None:
        """Called once when the system is added to a world."""

    def on_unregister(self) -> None:
        """Called once when the system is removed from a world."""

    def __repr__(self) -> str:
        return f"{type(self).__name__}(priority={self.priority}, enabled={self.enabled})"
