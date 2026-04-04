"""PhysicsSystem — gravity and rectangular boundary bouncing."""
from __future__ import annotations

import logging

from pykworldsim.core.systems.base_system import BaseSystem
from pykworldsim.core.components.position import Position
from pykworldsim.core.components.velocity import Velocity

logger = logging.getLogger(__name__)


class PhysicsSystem(BaseSystem):
    """
    Applies gravitational acceleration and optional world-boundary bouncing.

    Parameters
    ----------
    gravity:     Downward acceleration (units/s²). Applied to ``dy`` each tick.
    bounds:      ``(x_min, y_min, x_max, y_max)`` bounding rectangle.
                 Pass ``None`` to disable boundary enforcement.
    restitution: Coefficient of restitution (0 = inelastic, 1 = elastic).

    Required components: Position, Velocity.
    """

    def __init__(
        self,
        gravity: float = 9.81,
        bounds: tuple[float, float, float, float] | None = None,
        restitution: float = 0.8,
    ) -> None:
        super().__init__()
        self.gravity: float = gravity
        self.bounds = bounds
        self.restitution: float = restitution

    def update(self, dt: float) -> None:
        for entity, (pos, vel) in self.world.get_components(Position, Velocity):
            vel.dy += self.gravity * dt

            if self.bounds is not None:
                x_min, y_min, x_max, y_max = self.bounds

                if pos.x < x_min:
                    pos.x = x_min
                    vel.dx = abs(vel.dx) * self.restitution
                elif pos.x > x_max:
                    pos.x = x_max
                    vel.dx = -abs(vel.dx) * self.restitution

                if pos.y < y_min:
                    pos.y = y_min
                    vel.dy = abs(vel.dy) * self.restitution
                elif pos.y > y_max:
                    pos.y = y_max
                    vel.dy = -abs(vel.dy) * self.restitution

            logger.debug("%r → vel=(%.4f, %.4f)", entity, vel.dx, vel.dy)
