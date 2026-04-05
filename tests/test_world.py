"""Tests for World — staged queues, query interface, system ordering."""
from __future__ import annotations
import pytest
from pykworldsim.core.world import World
from pykworldsim.core.components.position import Position
from pykworldsim.core.components.velocity import Velocity
from pykworldsim.core.systems.movement import MovementSystem
from pykworldsim.core.systems.base_system import BaseSystem


def test_create_entity(world):
    e = world.create_entity()
    assert world.is_alive(e)

def test_add_get_component(world):
    e = world.create_entity()
    world.add_component(e, Position(x=3.0, y=4.0))
    assert world.get_component(e, Position).x == 3.0

def test_has_component(world):
    e = world.create_entity()
    assert not world.has_component(e, Position)
    world.add_component(e, Position())
    assert world.has_component(e, Position)

def test_remove_component(world):
    e = world.create_entity()
    world.add_component(e, Position())
    world.remove_component(e, Position)
    assert not world.has_component(e, Position)

def test_get_missing_raises(world):
    e = world.create_entity()
    with pytest.raises(KeyError):
        world.get_component(e, Position)

def test_add_to_dead_entity_raises(world):
    e = world.create_entity()
    world.destroy_entity(e)
    world._flush_staged()
    with pytest.raises(KeyError):
        world.add_component(e, Position())

def test_destroy_deferred(world):
    e = world.create_entity()
    world.destroy_entity(e)
    assert world.is_alive(e)   # still alive before flush
    world._flush_staged()
    assert not world.is_alive(e)

def test_stage_add_component(world):
    e = world.create_entity()
    world.stage_add_component(e, Position(x=5.0, y=6.0))
    assert not world.has_component(e, Position)  # not yet visible
    world._flush_staged()
    assert world.get_component(e, Position).x == 5.0

def test_stage_remove_component(world):
    e = world.create_entity()
    world.add_component(e, Position())
    world.stage_remove_component(e, Position)
    assert world.has_component(e, Position)   # not yet removed
    world._flush_staged()
    assert not world.has_component(e, Position)

def test_get_entities_with(world):
    e = world.create_entity()
    world.add_component(e, Position(x=1.0, y=2.0))
    world.add_component(e, Velocity(dx=3.0, dy=4.0))
    results = list(world.get_entities_with(Position, Velocity))
    assert len(results) == 1
    assert results[0][0] == e

def test_system_priority_ordering():
    order = []
    class SystemA(BaseSystem):
        priority = 20
        def update(self, world, dt): order.append("A")
    class SystemB(BaseSystem):
        priority = 5
        def update(self, world, dt): order.append("B")
    class SystemC(BaseSystem):
        priority = 10
        def update(self, world, dt): order.append("C")
    w = World()
    w.register_system(SystemA()); w.register_system(SystemB()); w.register_system(SystemC())
    w.update(dt=1.0)
    assert order == ["B", "C", "A"]  # sorted by priority

def test_simulate_alias(world):
    e = world.create_entity()
    world.add_component(e, Position(x=0.0, y=0.0))
    world.add_component(e, Velocity(dx=5.0, dy=0.0))
    world.Simulate(dt=1.0)
    assert abs(world.get_component(e, Position).x - 5.0) < 1e-9

def test_event_bus_on_create():
    w = World()
    created = []
    w.events.subscribe("entity_created", lambda d: created.append(d["entity"].id))
    e = w.create_entity()
    assert e.id in created

def test_event_bus_on_destroy():
    w = World()
    destroyed = []
    w.events.subscribe("entity_destroyed", lambda d: destroyed.append(d["entity"].id))
    e = w.create_entity()
    w.destroy_entity(e)
    w._flush_staged()
    assert e.id in destroyed

def test_generate_report(world):
    e = world.create_entity()
    world.add_component(e, Position(x=1.0, y=2.0))
    r = world.generate_report()
    assert r["entity_count"] == 1
    assert "Position" in r["component_types"]
