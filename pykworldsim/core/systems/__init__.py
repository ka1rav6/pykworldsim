"""Built-in ECS systems."""
from pykworldsim.core.systems.base_system import BaseSystem
from pykworldsim.core.systems.movement import MovementSystem
from pykworldsim.core.systems.physics import PhysicsSystem
from pykworldsim.core.systems.social import SocialSystem
from pykworldsim.core.systems.event import EventSystem

__all__ = [
    "BaseSystem",
    "MovementSystem",
    "PhysicsSystem",
    "SocialSystem",
    "EventSystem",
]
