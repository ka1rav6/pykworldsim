"""Tests for QueryEngine — the inverted-index component store."""
from __future__ import annotations
import pytest
from pykworldsim.core.entity import Entity
from pykworldsim.core.query import QueryEngine
from pykworldsim.core.components.position import Position
from pykworldsim.core.components.velocity import Velocity


def make_engine():
    return QueryEngine(), Entity(0), Entity(1), Entity(2)


def test_add_and_get():
    eng = QueryEngine()
    e = Entity(0)
    eng.add(e, Position(x=3.0, y=4.0))
    assert eng.get(e, Position).x == 3.0

def test_has_true():
    eng = QueryEngine()
    e = Entity(0)
    eng.add(e, Position())
    assert eng.has(e, Position)

def test_has_false():
    eng = QueryEngine()
    assert not eng.has(Entity(0), Position)

def test_remove():
    eng = QueryEngine()
    e = Entity(0)
    eng.add(e, Position())
    eng.remove(e, Position)
    assert not eng.has(e, Position)

def test_remove_missing_raises():
    eng = QueryEngine()
    with pytest.raises(KeyError):
        eng.remove(Entity(0), Position)

def test_remove_all():
    eng = QueryEngine()
    e = Entity(0)
    eng.add(e, Position()); eng.add(e, Velocity())
    eng.remove_all(e)
    assert not eng.has(e, Position)
    assert not eng.has(e, Velocity)

def test_query_single_component():
    eng = QueryEngine()
    e = Entity(0)
    eng.add(e, Position(x=1.0, y=2.0))
    results = list(eng.query(Position))
    assert len(results) == 1
    assert results[0][0] == e

def test_query_multiple_components():
    eng = QueryEngine()
    e0 = Entity(0); e1 = Entity(1)
    eng.add(e0, Position()); eng.add(e0, Velocity())
    eng.add(e1, Position())  # no velocity
    results = list(eng.query(Position, Velocity))
    assert len(results) == 1
    assert results[0][0] == e0

def test_query_empty_world():
    eng = QueryEngine()
    assert list(eng.query(Position)) == []

def test_query_returns_snapshot_safe():
    """Mutating the store during query must not raise."""
    eng = QueryEngine()
    for i in range(5):
        e = Entity(i)
        eng.add(e, Position(x=float(i), y=0.0))
    count = 0
    for entity, (pos,) in eng.query(Position):
        count += 1
        eng.remove_all(Entity(99))  # harmless mutation
    assert count == 5
