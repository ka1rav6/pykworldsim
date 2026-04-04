"""Tests for Entity and EntityRegistry."""
from __future__ import annotations

import pytest

from pykworldsim.core.entity import Entity, EntityRegistry


def test_entity_creation() -> None:
    reg = EntityRegistry()
    e = reg.create()
    assert isinstance(e, Entity)
    assert e.id == 0
    assert reg.is_alive(e)


def test_entity_sequential_ids() -> None:
    reg = EntityRegistry()
    ids = [reg.create().id for _ in range(5)]
    assert ids == list(range(5))


def test_entity_is_alive_after_create() -> None:
    reg = EntityRegistry()
    e = reg.create()
    assert reg.is_alive(e)


def test_entity_destroy() -> None:
    reg = EntityRegistry()
    e = reg.create()
    reg.destroy(e)
    assert not reg.is_alive(e)


def test_entity_double_destroy_raises() -> None:
    reg = EntityRegistry()
    e = reg.create()
    reg.destroy(e)
    with pytest.raises(KeyError):
        reg.destroy(e)


def test_entity_hashable_and_equal() -> None:
    e1 = Entity(0)
    e2 = Entity(0)
    assert e1 == e2
    assert hash(e1) == hash(e2)


def test_entity_different_ids_not_equal() -> None:
    assert Entity(0) != Entity(1)


def test_entity_frozen() -> None:
    e = Entity(0)
    with pytest.raises((AttributeError, TypeError)):
        e.id = 99  # type: ignore[misc]


def test_alive_ids_snapshot() -> None:
    reg = EntityRegistry()
    e0 = reg.create()
    e1 = reg.create()
    ids = reg.alive_ids
    assert 0 in ids and 1 in ids
    reg.destroy(e0)
    # Snapshot must not be mutated
    assert 0 in ids


def test_registry_reset() -> None:
    reg = EntityRegistry()
    reg.create()
    reg.create()
    reg.reset()
    assert len(reg.alive_ids) == 0
    e = reg.create()
    assert e.id == 0


def test_multiple_registries_independent() -> None:
    r1 = EntityRegistry()
    r2 = EntityRegistry()
    e1 = r1.create()
    e2 = r2.create()
    assert e1.id == e2.id == 0
    r1.destroy(e1)
    assert r2.is_alive(e2)
