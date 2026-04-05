"""
pykworldsim v3 — Production-grade ECS world simulation framework.

Quick start::

    from pykworldsim import World, Simulation, Position, Velocity, MovementSystem
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
from pykworldsim.core.events import EventBus
from pykworldsim.core.components.position import Position
from pykworldsim.core.components.velocity import Velocity
from pykworldsim.core.components.person import Person
from pykworldsim.core.components.location import Location
from pykworldsim.core.components.relationship import Relationship
from pykworldsim.core.components.job import Job
from pykworldsim.core.components.goal import Goal
from pykworldsim.core.components.event_component import EventComponent
from pykworldsim.core.systems.movement import MovementSystem
from pykworldsim.core.systems.physics import PhysicsSystem
from pykworldsim.core.systems.social import SocialSystem
from pykworldsim.core.systems.event_system import EventSystem
from pykworldsim.plugins.registry import PluginRegistry

__all__ = [
    "World","Entity","Simulation","SimulationState","EventBus",
    "Position","Velocity","Person","Location","Relationship","Job","Goal","EventComponent",
    "MovementSystem","PhysicsSystem","SocialSystem","EventSystem","PluginRegistry",
]
__version__ = "3.0.0"
__author__  = "Kairav Dutta"
