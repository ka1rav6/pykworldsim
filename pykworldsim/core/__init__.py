"""Core ECS primitives — lazy imports to avoid circular dependency."""
from __future__ import annotations

def __getattr__(name: str):
    if name == "World":
        from pykworldsim.core.world import World
        return World
    if name == "Entity":
        from pykworldsim.core.entity import Entity
        return Entity
    if name == "Simulation":
        from pykworldsim.core.simulation import Simulation
        return Simulation
    raise AttributeError(f"module 'pykworldsim.core' has no attribute {name!r}")

__all__ = ["World", "Entity", "Simulation"]
