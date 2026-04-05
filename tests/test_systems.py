"""Tests for all built-in systems."""
from __future__ import annotations
import pytest
from pykworldsim.core.world import World
from pykworldsim.core.simulation import Simulation
from pykworldsim.core.components.position import Position
from pykworldsim.core.components.velocity import Velocity
from pykworldsim.core.components.person import Person
from pykworldsim.core.components.goal import Goal
from pykworldsim.core.components.relationship import Relationship
from pykworldsim.core.components.event_component import EventComponent
from pykworldsim.core.systems.movement import MovementSystem
from pykworldsim.core.systems.physics import PhysicsSystem
from pykworldsim.core.systems.social import SocialSystem
from pykworldsim.core.systems.event_system import EventSystem


# ── Movement ──────────────────────────────────────────────────────────
def test_movement_updates_position():
    w = World(); w.register_system(MovementSystem())
    e = w.create_entity()
    w.add_component(e, Position(x=0.0, y=0.0))
    w.add_component(e, Velocity(dx=3.0, dy=-1.0))
    w.update(dt=2.0)
    pos = w.get_component(e, Position)
    assert abs(pos.x - 6.0) < 1e-9 and abs(pos.y - -2.0) < 1e-9

def test_movement_skips_without_velocity():
    w = World(); w.register_system(MovementSystem())
    e = w.create_entity(); w.add_component(e, Position(x=5.0, y=5.0))
    w.update(dt=1.0)
    pos = w.get_component(e, Position)
    assert pos.x == 5.0 and pos.y == 5.0

def test_disabled_system_skipped():
    w = World()
    ms = MovementSystem(); ms.enabled = False
    w.register_system(ms)
    e = w.create_entity()
    w.add_component(e, Position(x=0.0, y=0.0))
    w.add_component(e, Velocity(dx=10.0, dy=0.0))
    w.update(dt=1.0)
    assert w.get_component(e, Position).x == 0.0

def test_movement_priority_lower_than_physics():
    assert MovementSystem.priority > PhysicsSystem.priority

# ── Physics ───────────────────────────────────────────────────────────
def test_physics_gravity():
    w = World(); w.register_system(PhysicsSystem(gravity=10.0))
    e = w.create_entity()
    w.add_component(e, Position()); w.add_component(e, Velocity())
    w.update(dt=1.0)
    assert abs(w.get_component(e, Velocity).dy - 10.0) < 1e-9

def test_physics_bounce_floor():
    w = World(); w.register_system(PhysicsSystem(gravity=0.0, bounds=(0,0,100,100), restitution=1.0))
    e = w.create_entity()
    w.add_component(e, Position(x=50.0, y=105.0))
    w.add_component(e, Velocity(dx=0.0, dy=5.0))
    w.update(dt=0.0)
    assert w.get_component(e, Position).y == 100.0
    assert w.get_component(e, Velocity).dy < 0

def test_physics_bounce_wall():
    w = World(); w.register_system(PhysicsSystem(gravity=0.0, bounds=(0,0,100,100), restitution=1.0))
    e = w.create_entity()
    w.add_component(e, Position(x=-5.0, y=50.0))
    w.add_component(e, Velocity(dx=-3.0, dy=0.0))
    w.update(dt=0.0)
    assert w.get_component(e, Position).x == 0.0
    assert w.get_component(e, Velocity).dx > 0

# ── Social ────────────────────────────────────────────────────────────
def test_social_ages_person(person_entity):
    world, e = person_entity; age_before = world.get_component(e, Person).age
    world.update(dt=1.0)
    assert world.get_component(e, Person).age > age_before

def test_social_depletes_energy(person_entity):
    world, e = person_entity; energy_before = world.get_component(e, Person).energy
    world.update(dt=1.0)
    assert world.get_component(e, Person).energy < energy_before

def test_social_goal_progresses(person_entity):
    world, e = person_entity; world.update(dt=1.0)
    assert world.get_component(e, Goal).progress > 0.0

def test_social_goal_completes(person_entity):
    world, e = person_entity
    world.get_component(e, Goal).priority = 500.0
    world.update(dt=1.0)
    assert world.get_component(e, Goal).completed

def test_social_goal_completion_emits_event(person_entity):
    world, e = person_entity
    events_received = []
    world.events.subscribe("goal_completed", lambda d: events_received.append(d))
    world.get_component(e, Goal).priority = 500.0
    world.update(dt=1.0)
    world.events.flush()
    assert len(events_received) > 0

def test_social_relationship_drifts(social_world):
    e = social_world.create_entity()
    social_world.add_component(e, Relationship(strength=1.0))
    social_world.update(dt=100.0)
    assert social_world.get_component(e, Relationship).strength < 1.0

# ── EventSystem ───────────────────────────────────────────────────────
def test_event_fires_at_tick():
    w = World(); es = EventSystem(); w.register_system(es)
    fired = []
    w.events.subscribe("social", lambda d: fired.append(d["event"].name))
    e = w.create_entity()
    w.add_component(e, EventComponent(name="party", event_type="social", tick_scheduled=2))
    Simulation(w, seed=0).run(steps=5)
    assert "party" in fired

def test_event_not_fired_before_scheduled():
    w = World(); es = EventSystem(); w.register_system(es)
    fired = []
    w.events.subscribe("social", lambda d: fired.append(1))
    e = w.create_entity()
    w.add_component(e, EventComponent(name="future", event_type="social", tick_scheduled=10))
    Simulation(w, seed=0).run(steps=5)
    assert fired == []

def test_event_resolved_after_firing():
    w = World(); es = EventSystem(); w.register_system(es)
    e = w.create_entity()
    ev = EventComponent(name="once", event_type="generic", tick_scheduled=1)
    w.add_component(e, ev)
    Simulation(w, seed=0).run(steps=3)
    assert ev.resolved

def test_event_default_handler_boosts_happiness():
    w = World(); w.register_system(EventSystem())
    e = w.create_entity()
    p = Person(happiness=50.0)
    w.add_component(e, p)
    w.add_component(e, EventComponent(name="party", event_type="social", tick_scheduled=1))
    Simulation(w, seed=0).run(steps=2)
    assert p.happiness > 50.0

def test_system_receives_world_query():
    """System update(world, dt) contract — must use world.get_entities_with."""
    calls = []
    from pykworldsim.core.systems.base_system import BaseSystem
    class ProbeSystem(BaseSystem):
        def update(self, world, dt):
            for entity, (pos,) in world.get_entities_with(Position):
                calls.append(entity.id)
    w = World(); w.register_system(ProbeSystem())
    e = w.create_entity(); w.add_component(e, Position())
    w.update(dt=1.0)
    assert e.id in calls
