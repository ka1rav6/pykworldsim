"""Tests for Entity, EntityRegistry, and lifecycle hooks."""
from __future__ import annotations
import pytest
from pykworldsim.core.entity import Entity, EntityRegistry


def test_sequential_ids():
    reg = EntityRegistry()
    ids = [reg.create().id for _ in range(5)]
    assert ids == list(range(5))

def test_is_alive_after_create():
    reg = EntityRegistry()
    e = reg.create()
    assert reg.is_alive(e)

def test_destroy():
    reg = EntityRegistry()
    e = reg.create()
    reg.destroy(e)
    assert not reg.is_alive(e)

def test_double_destroy_raises():
    reg = EntityRegistry()
    e = reg.create()
    reg.destroy(e)
    with pytest.raises(KeyError):
        reg.destroy(e)

def test_entity_frozen():
    e = Entity(0)
    with pytest.raises((AttributeError, TypeError)):
        e.id = 99  # type: ignore[misc]

def test_entity_hashable():
    assert Entity(0) == Entity(0)
    assert hash(Entity(0)) == hash(Entity(0))

def test_alive_ids_snapshot_immutable():
    reg = EntityRegistry()
    e0 = reg.create(); e1 = reg.create()
    snap = reg.alive_ids
    reg.destroy(e0)
    assert 0 in snap  # snapshot must not change

def test_reset():
    reg = EntityRegistry()
    reg.create(); reg.create()
    reg.reset()
    assert len(reg.alive_ids) == 0
    assert reg.create().id == 0

def test_on_create_hook():
    reg = EntityRegistry()
    created = []
    reg.add_on_create(lambda e: created.append(e.id))
    e = reg.create()
    assert e.id in created

def test_on_destroy_hook():
    reg = EntityRegistry()
    destroyed = []
    reg.add_on_destroy(lambda e: destroyed.append(e.id))
    e = reg.create()
    reg.destroy(e)
    assert e.id in destroyed

def test_multiple_registries_independent():
    r1 = EntityRegistry(); r2 = EntityRegistry()
    e1 = r1.create(); e2 = r2.create()
    assert e1.id == e2.id == 0
    r1.destroy(e1)
    assert r2.is_alive(e2)
