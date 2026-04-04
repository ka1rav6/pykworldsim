"""
pykworldsim — ECS-based world simulation framework.

Simulates people, relationships, cities, jobs, goals, and events
using a clean Entity-Component-System architecture.

Quick start::

    from pykworldsim import World, Simulation
    from pykworldsim.core.components import Position, Velocity
    from pykworldsim.core.systems import MovementSystem

    world = World()
    world.register_system(MovementSystem())

    e = world.create_entity()
    world.add_component(e, Position(x=0.0, y=0.0))
    world.add_component(e, Velocity(dx=1.0, dy=0.5))

    sim = Simulation(world, seed=42)
    sim.run(steps=100, dt=0.1)
"""

from pykworldsim.core.world import World
from pykworldsim.core.entity import Entity
from pykworldsim.core.simulation import Simulation, SimulationState
from pykworldsim.core.components.position import Position
from pykworldsim.core.components.velocity import Velocity
from pykworldsim.core.components.person import Person
from pykworldsim.core.components.location import Location
from pykworldsim.core.components.relationship import Relationship
from pykworldsim.core.components.job import Job
from pykworldsim.core.components.goal import Goal
from pykworldsim.core.systems.movement import MovementSystem
from pykworldsim.core.systems.physics import PhysicsSystem
from pykworldsim.core.systems.social import SocialSystem
from pykworldsim.core.systems.event import EventSystem
from pykworldsim.plugins.registry import PluginRegistry

__all__ = [
    # Core ECS
    "World",
    "Entity",
    "Simulation",
    "SimulationState",
    # Components
    "Position",
    "Velocity",
    "Person",
    "Location",
    "Relationship",
    "Job",
    "Goal",
    # Systems
    "MovementSystem",
    "PhysicsSystem",
    "SocialSystem",
    "EventSystem",
    # Plugin
    "PluginRegistry",
]

__version__ = "2.0.0"
__author__  = "Kairav Dutta"
