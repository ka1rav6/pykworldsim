"""PhysicsSystem — gravity + boundary bounce, priority=5."""
from __future__ import annotations
import logging
from typing import TYPE_CHECKING
from pykworldsim.core.systems.base_system import BaseSystem
from pykworldsim.core.components.position import Position
from pykworldsim.core.components.velocity import Velocity
if TYPE_CHECKING:
    from pykworldsim.core.world import World

logger = logging.getLogger(__name__)

class PhysicsSystem(BaseSystem):
    """Applies gravitational acceleration and optional rectangular boundary bouncing."""
    priority: int = 5

    def __init__(
        self,
        gravity: float = 9.81,
        bounds: tuple[float, float, float, float] | None = None,
        restitution: float = 0.8,
    ) -> None:
        super().__init__()
        self.gravity = gravity
        self.bounds = bounds
        self.restitution = restitution

    def update(self, world: "World", dt: float) -> None:
        for entity, (pos, vel) in world.get_entities_with(Position, Velocity):
            vel.dy += self.gravity * dt
            if self.bounds is not None:
                x_min, y_min, x_max, y_max = self.bounds
                if pos.x < x_min:
                    pos.x = x_min; vel.dx = abs(vel.dx) * self.restitution
                elif pos.x > x_max:
                    pos.x = x_max; vel.dx = -abs(vel.dx) * self.restitution
                if pos.y < y_min:
                    pos.y = y_min; vel.dy = abs(vel.dy) * self.restitution
                elif pos.y > y_max:
                    pos.y = y_max; vel.dy = -abs(vel.dy) * self.restitution
