"""MovementSystem — integrates Velocity into Position each tick."""
from __future__ import annotations

import logging

from pykworldsim.core.systems.base_system import BaseSystem
from pykworldsim.core.components.position import Position
from pykworldsim.core.components.velocity import Velocity

logger = logging.getLogger(__name__)


class MovementSystem(BaseSystem):
    """
    Applies linear integration: ``position += velocity * dt``.

    Required components: :class:`~pykworldsim.core.components.position.Position`,
    :class:`~pykworldsim.core.components.velocity.Velocity`.
    """

    def update(self, dt: float) -> None:
        for entity, (pos, vel) in self.world.get_components(Position, Velocity):
            pos.x += vel.dx * dt
            pos.y += vel.dy * dt
            logger.debug("%r → pos=(%.4f, %.4f)", entity, pos.x, pos.y)
