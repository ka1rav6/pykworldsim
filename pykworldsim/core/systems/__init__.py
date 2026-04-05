"""Built-in ECS systems — lazy imports to break circular dependencies."""
from __future__ import annotations
from pykworldsim.core.systems.base_system import BaseSystem

def __getattr__(name: str):
    if name == "MovementSystem":
        from pykworldsim.core.systems.movement import MovementSystem
        return MovementSystem
    if name == "PhysicsSystem":
        from pykworldsim.core.systems.physics import PhysicsSystem
        return PhysicsSystem
    if name == "SocialSystem":
        from pykworldsim.core.systems.social import SocialSystem
        return SocialSystem
    if name == "EventSystem":
        from pykworldsim.core.systems.event_system import EventSystem
        return EventSystem
    raise AttributeError(f"module 'pykworldsim.core.systems' has no attribute {name!r}")

__all__ = ["BaseSystem", "MovementSystem", "PhysicsSystem", "SocialSystem", "EventSystem"]
