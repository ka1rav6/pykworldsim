"""Tests for built-in ECS systems."""
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
from pykworldsim.core.systems.physics import PhysicsSystem
from pykworldsim.core.systems.social import SocialSystem
from pykworldsim.core.systems.event import EventSystem


# ── MovementSystem ────────────────────────────────────────────────────

def test_movement_updates_position() -> None:
    w = World()
    w.register_system(MovementSystem())
    e = w.create_entity()
    w.add_component(e, Position(x=0.0, y=0.0))
    w.add_component(e, Velocity(dx=3.0, dy=-1.0))
    w.update(dt=2.0)
    pos = w.get_component(e, Position)
    assert abs(pos.x - 6.0) < 1e-9
    assert abs(pos.y - -2.0) < 1e-9


def test_movement_skips_entities_without_velocity() -> None:
    w = World()
    w.register_system(MovementSystem())
    e = w.create_entity()
    w.add_component(e, Position(x=5.0, y=5.0))
    # no Velocity
    w.update(dt=1.0)
    pos = w.get_component(e, Position)
    assert pos.x == 5.0 and pos.y == 5.0


def test_movement_multiple_entities() -> None:
    w = World()
    w.register_system(MovementSystem())
    entities = []
    for i in range(5):
        e = w.create_entity()
        w.add_component(e, Position(x=float(i), y=0.0))
        w.add_component(e, Velocity(dx=1.0, dy=0.0))
        entities.append(e)
    w.update(dt=1.0)
    for i, e in enumerate(entities):
        pos = w.get_component(e, Position)
        assert abs(pos.x - (i + 1)) < 1e-9


def test_disabled_system_skipped() -> None:
    w = World()
    ms = MovementSystem()
    ms.enabled = False
    w.register_system(ms)
    e = w.create_entity()
    w.add_component(e, Position(x=0.0, y=0.0))
    w.add_component(e, Velocity(dx=10.0, dy=0.0))
    w.update(dt=1.0)
    pos = w.get_component(e, Position)
    assert pos.x == 0.0  # not moved


# ── PhysicsSystem ─────────────────────────────────────────────────────

def test_physics_applies_gravity() -> None:
    w = World()
    w.register_system(PhysicsSystem(gravity=10.0))
    e = w.create_entity()
    w.add_component(e, Position(x=0.0, y=0.0))
    w.add_component(e, Velocity(dx=0.0, dy=0.0))
    w.update(dt=1.0)
    vel = w.get_component(e, Velocity)
    assert abs(vel.dy - 10.0) < 1e-9


def test_physics_boundary_bounce_floor() -> None:
    w = World()
    w.register_system(PhysicsSystem(gravity=0.0, bounds=(0, 0, 100, 100), restitution=1.0))
    e = w.create_entity()
    w.add_component(e, Position(x=50.0, y=105.0))  # beyond y_max=100
    w.add_component(e, Velocity(dx=0.0, dy=5.0))
    w.update(dt=0.0)
    pos = w.get_component(e, Position)
    vel = w.get_component(e, Velocity)
    assert pos.y == 100.0
    assert vel.dy < 0  # bounced upward


def test_physics_boundary_bounce_wall() -> None:
    w = World()
    w.register_system(PhysicsSystem(gravity=0.0, bounds=(0, 0, 100, 100), restitution=1.0))
    e = w.create_entity()
    w.add_component(e, Position(x=-5.0, y=50.0))  # beyond x_min=0
    w.add_component(e, Velocity(dx=-3.0, dy=0.0))
    w.update(dt=0.0)
    pos = w.get_component(e, Position)
    vel = w.get_component(e, Velocity)
    assert pos.x == 0.0
    assert vel.dx > 0  # bounced right


# ── SocialSystem ──────────────────────────────────────────────────────

def test_social_ages_person(person_entity) -> None:
    world, e = person_entity
    person_before = world.get_component(e, Person)
    age_before = person_before.age
    world.update(dt=1.0)
    assert person_before.age > age_before


def test_social_depletes_energy(person_entity) -> None:
    world, e = person_entity
    person = world.get_component(e, Person)
    energy_before = person.energy
    world.update(dt=1.0)
    assert person.energy < energy_before


def test_social_goal_progresses(person_entity) -> None:
    world, e = person_entity
    goal = world.get_component(e, Goal)
    assert goal.progress == 0.0
    world.update(dt=1.0)
    assert goal.progress > 0.0


def test_social_goal_completes(person_entity) -> None:
    world, e = person_entity
    goal = world.get_component(e, Goal)
    goal.priority = 200.0  # huge priority → fast completion
    world.update(dt=1.0)
    assert goal.completed


def test_social_relationship_drifts(social_world: World) -> None:
    e = social_world.create_entity()
    social_world.add_component(e, Relationship(strength=1.0))
    social_world.update(dt=100.0)
    rel = social_world.get_component(e, Relationship)
    assert rel.strength < 1.0  # drifted toward neutral


# ── EventSystem ───────────────────────────────────────────────────────

def test_event_fires_at_scheduled_tick() -> None:
    w = World()
    es = EventSystem()
    w.register_system(es)

    fired = []
    es.register_handler("social", lambda world, entity, event: fired.append(event.name))

    e = w.create_entity()
    w.add_component(e, Event(name="party", event_type="social", tick_scheduled=3))

    sim = Simulation(w, seed=0)
    sim.run(steps=5)

    assert "party" in fired


def test_event_not_fired_before_scheduled_tick() -> None:
    w = World()
    es = EventSystem()
    w.register_system(es)

    fired = []
    es.register_handler("social", lambda world, entity, event: fired.append(event.name))

    e = w.create_entity()
    w.add_component(e, Event(name="future_party", event_type="social", tick_scheduled=10))

    sim = Simulation(w, seed=0)
    sim.run(steps=5)

    assert "future_party" not in fired


def test_event_resolved_after_firing() -> None:
    w = World()
    es = EventSystem()
    w.register_system(es)

    e = w.create_entity()
    ev = Event(name="once", event_type="generic", tick_scheduled=1)
    w.add_component(e, ev)

    sim = Simulation(w, seed=0)
    sim.run(steps=3)

    assert ev.resolved


def test_event_default_handler_boosts_happiness() -> None:
    w = World()
    es = EventSystem()
    w.register_system(es)

    e = w.create_entity()
    person = Person(happiness=50.0)
    w.add_component(e, person)
    w.add_component(e, Event(name="celebration", event_type="social", tick_scheduled=1))

    sim = Simulation(w, seed=0)
    sim.run(steps=2)

    assert person.happiness > 50.0
