"""MovementSystem — integrates Velocity into Position, priority=10."""
from __future__ import annotations
import logging
from typing import TYPE_CHECKING
from pykworldsim.core.systems.base_system import BaseSystem
from pykworldsim.core.components.position import Position
from pykworldsim.core.components.velocity import Velocity
if TYPE_CHECKING:
    from pykworldsim.core.world import World

logger = logging.getLogger(__name__)

class MovementSystem(BaseSystem):
    """Applies pos += vel * dt for all entities with Position + Velocity."""
    priority: int = 10

    def update(self, world: "World", dt: float) -> None:
        for entity, (pos, vel) in world.get_entities_with(Position, Velocity):
            pos.x += vel.dx * dt
            pos.y += vel.dy * dt
            logger.debug("%r pos=(%.3f, %.3f)", entity, pos.x, pos.y)
