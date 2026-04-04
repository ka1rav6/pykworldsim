"""Tests for World ECS container."""
from __future__ import annotations

import pytest

from pykworldsim.core.world import World
from pykworldsim.core.entity import Entity
from pykworldsim.core.components.position import Position
from pykworldsim.core.components.velocity import Velocity
from pykworldsim.core.components.person import Person
from pykworldsim.core.systems.movement import MovementSystem


def test_create_entity(world: World) -> None:
    e = world.create_entity()
    assert world.is_alive(e)


def test_multiple_entities_unique_ids(world: World) -> None:
    ids = {world.create_entity().id for _ in range(10)}
    assert len(ids) == 10


def test_add_get_component(world: World) -> None:
    e = world.create_entity()
    world.add_component(e, Position(x=3.0, y=4.0))
    pos = world.get_component(e, Position)
    assert pos.x == 3.0
    assert pos.y == 4.0


def test_has_component_false_before_add(world: World) -> None:
    e = world.create_entity()
    assert not world.has_component(e, Position)


def test_has_component_true_after_add(world: World) -> None:
    e = world.create_entity()
    world.add_component(e, Position())
    assert world.has_component(e, Position)


def test_remove_component(world: World) -> None:
    e = world.create_entity()
    world.add_component(e, Position())
    world.remove_component(e, Position)
    assert not world.has_component(e, Position)


def test_remove_missing_component_raises(world: World) -> None:
    e = world.create_entity()
    with pytest.raises(KeyError):
        world.remove_component(e, Position)


def test_get_missing_component_raises(world: World) -> None:
    e = world.create_entity()
    with pytest.raises(KeyError):
        world.get_component(e, Position)


def test_add_component_to_dead_entity_raises(world: World) -> None:
    e = world.create_entity()
    world.destroy_entity(e)
    world._flush_destroy_queue()
    with pytest.raises(KeyError):
        world.add_component(e, Position())


def test_destroy_entity_deferred(world: World) -> None:
    e = world.create_entity()
    world.destroy_entity(e)
    # Still alive before flush
    assert world.is_alive(e)
    world._flush_destroy_queue()
    assert not world.is_alive(e)


def test_destroy_removes_all_components(world: World) -> None:
    e = world.create_entity()
    world.add_component(e, Position())
    world.add_component(e, Velocity())
    world.destroy_entity(e)
    world._flush_destroy_queue()
    # Stores should be empty
    assert e.id not in world._components.get(Position, {})
    assert e.id not in world._components.get(Velocity, {})


def test_get_components_single_match(world: World) -> None:
    e = world.create_entity()
    world.add_component(e, Position(x=1.0, y=2.0))
    world.add_component(e, Velocity(dx=3.0, dy=4.0))
    results = list(world.get_components(Position, Velocity))
    assert len(results) == 1
    entity, (pos, vel) = results[0]
    assert entity == e
    assert pos.x == 1.0
    assert vel.dx == 3.0


def test_get_components_partial_match_excluded(world: World) -> None:
    e1 = world.create_entity()
    world.add_component(e1, Position())  # no velocity

    e2 = world.create_entity()
    world.add_component(e2, Position())
    world.add_component(e2, Velocity())

    results = list(world.get_components(Position, Velocity))
    ids = [ent.id for ent, _ in results]
    assert e1.id not in ids
    assert e2.id in ids


def test_get_components_empty_returns_nothing(world: World) -> None:
    results = list(world.get_components(Position))
    assert results == []


def test_entities_snapshot(world: World) -> None:
    e1 = world.create_entity()
    e2 = world.create_entity()
    snap = world.entities
    assert e1 in snap and e2 in snap


def test_register_system(world: World) -> None:
    # MovementSystem was already registered in fixture
    assert any(isinstance(s, MovementSystem) for s in world.systems)


def test_unregister_system(world: World) -> None:
    world.unregister_system(MovementSystem)
    assert not any(isinstance(s, MovementSystem) for s in world.systems)


def test_simulate_alias(world: World) -> None:
    """world.Simulate() must work for backward compat with original repo."""
    e = world.create_entity()
    world.add_component(e, Position(x=0.0, y=0.0))
    world.add_component(e, Velocity(dx=5.0, dy=0.0))
    world.Simulate(dt=1.0)
    pos = world.get_component(e, Position)
    assert abs(pos.x - 5.0) < 1e-9


def test_generate_report(world: World) -> None:
    e = world.create_entity()
    world.add_component(e, Position(x=1.0, y=2.0))
    report = world.generate_report()
    assert report["world"] == "test-world"
    assert report["entity_count"] == 1
    assert "Position" in report["component_types"]


def test_world_repr(world: World) -> None:
    r = repr(world)
    assert "test-world" in r
