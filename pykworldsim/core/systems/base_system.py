"""BaseSystem — abstract base class every ECS system must subclass."""
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

    A system holds **no entity-specific state**. It queries the
    :class:`~pykworldsim.core.world.World` for entities that own its
    required components, then transforms those components in place.

    Subclasses **must** implement :meth:`update`.

    Attributes
    ----------
    enabled:
        Set ``False`` to skip this system each tick without unregistering it.
    """

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
    def update(self, dt: float) -> None:
        """Execute one tick of logic. *dt* is the simulated time delta."""

    def on_register(self) -> None:
        """Called once when the system is added to a world. Override for setup."""

    def on_unregister(self) -> None:
        """Called once when the system is removed from a world."""

    def __repr__(self) -> str:
        return f"{type(self).__name__}(enabled={self.enabled})"
