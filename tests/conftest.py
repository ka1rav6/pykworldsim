"""Shared pytest fixtures for pykworldsim tests."""
from __future__ import annotations

import pytest

from pykworldsim.core.world import World
from pykworldsim.core.simulation import Simulation
from pykworldsim.core.components.position import Position
from pykworldsim.core.components.velocity import Velocity
from pykworldsim.core.components.person import Person
from pykworldsim.core.components.job import Job
from pykworldsim.core.components.goal import Goal
from pykworldsim.core.components.relationship import Relationship
from pykworldsim.core.components.event import Event
from pykworldsim.core.systems.movement import MovementSystem
from pykworldsim.core.systems.social import SocialSystem
from pykworldsim.core.systems.event import EventSystem


@pytest.fixture
def world() -> World:
    """Bare world with MovementSystem registered."""
    w = World(name="test-world")
    w.register_system(MovementSystem())
    return w


@pytest.fixture
def social_world() -> World:
    """World with SocialSystem registered."""
    w = World(name="social-world")
    w.register_system(SocialSystem())
    return w


@pytest.fixture
def populated_world(world: World):
    """World with one entity carrying Position + Velocity."""
    e = world.create_entity()
    world.add_component(e, Position(x=0.0, y=0.0))
    world.add_component(e, Velocity(dx=1.0, dy=2.0))
    return world, e


@pytest.fixture
def sim(world: World) -> Simulation:
    """Deterministic Simulation seeded at 0."""
    return Simulation(world, seed=0)


@pytest.fixture
def person_entity(social_world: World):
    """Social world with one full-featured Person entity."""
    e = social_world.create_entity()
    social_world.add_component(e, Person(name="Alice", age=25.0, happiness=60.0, energy=80.0))
    social_world.add_component(e, Job(title="Engineer", salary=5000.0, satisfaction=70.0))
    social_world.add_component(e, Goal(description="Learn Python", priority=8.0))
    return social_world, e
