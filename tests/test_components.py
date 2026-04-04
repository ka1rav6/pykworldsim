"""Tests for all built-in ECS components."""
from __future__ import annotations

from pykworldsim.core.components.position import Position
from pykworldsim.core.components.velocity import Velocity
from pykworldsim.core.components.person import Person
from pykworldsim.core.components.location import Location
from pykworldsim.core.components.job import Job
from pykworldsim.core.components.goal import Goal
from pykworldsim.core.components.relationship import Relationship
from pykworldsim.core.components.event import Event


# ── Position ──────────────────────────────────────────────────────────

def test_position_defaults() -> None:
    p = Position()
    assert p.x == 0.0 and p.y == 0.0


def test_position_mutable() -> None:
    p = Position(x=1.0, y=2.0)
    p.x += 10.0
    assert p.x == 11.0


def test_position_serialise_roundtrip() -> None:
    p = Position(x=3.5, y=-7.25)
    assert Position.from_dict(p.to_dict()) == p


# ── Velocity ──────────────────────────────────────────────────────────

def test_velocity_defaults() -> None:
    v = Velocity()
    assert v.dx == 0.0 and v.dy == 0.0


def test_velocity_serialise_roundtrip() -> None:
    v = Velocity(dx=2.0, dy=-0.5)
    assert Velocity.from_dict(v.to_dict()) == v


# ── Person ────────────────────────────────────────────────────────────

def test_person_defaults() -> None:
    p = Person()
    assert p.name == "Unknown"
    assert p.health == 100.0
    assert p.happiness == 50.0
    assert p.energy == 100.0
    assert p.traits == []


def test_person_serialise_roundtrip() -> None:
    p = Person(name="Alice", age=30.0, traits=["curious"])
    p2 = Person.from_dict(p.to_dict())
    assert p2.name == "Alice"
    assert p2.age == 30.0
    assert p2.traits == ["curious"]


def test_person_traits_are_copied() -> None:
    traits = ["brave"]
    p = Person(traits=traits)
    d = p.to_dict()
    d["traits"].append("extra")
    assert p.traits == ["brave"]


# ── Location ─────────────────────────────────────────────────────────

def test_location_defaults() -> None:
    loc = Location()
    assert loc.name == "Unnamed"
    assert loc.population == 0


def test_location_serialise_roundtrip() -> None:
    loc = Location(name="Delhi", x=28.6, y=77.2, population=20_000_000, city_type="megacity")
    loc2 = Location.from_dict(loc.to_dict())
    assert loc2.name == "Delhi"
    assert loc2.population == 20_000_000


# ── Job ───────────────────────────────────────────────────────────────

def test_job_defaults() -> None:
    j = Job()
    assert j.title == "Unemployed"
    assert j.salary == 0.0


def test_job_serialise_roundtrip() -> None:
    j = Job(title="Pilot", salary=9000.0, satisfaction=85.0)
    j2 = Job.from_dict(j.to_dict())
    assert j2.title == "Pilot"
    assert j2.salary == 9000.0


# ── Goal ──────────────────────────────────────────────────────────────

def test_goal_defaults() -> None:
    g = Goal()
    assert not g.completed
    assert g.progress == 0.0


def test_goal_serialise_roundtrip() -> None:
    g = Goal(description="Run a marathon", priority=9.0, progress=50.0)
    g2 = Goal.from_dict(g.to_dict())
    assert g2.description == "Run a marathon"
    assert g2.progress == 50.0


# ── Relationship ──────────────────────────────────────────────────────

def test_relationship_defaults() -> None:
    r = Relationship()
    assert r.target_id == -1
    assert r.kind == "friend"


def test_relationship_serialise_roundtrip() -> None:
    r = Relationship(target_id=5, kind="rival", strength=-0.7, interactions=12)
    r2 = Relationship.from_dict(r.to_dict())
    assert r2.target_id == 5
    assert r2.kind == "rival"
    assert abs(r2.strength - -0.7) < 1e-9


# ── Event ─────────────────────────────────────────────────────────────

def test_event_defaults() -> None:
    e = Event()
    assert e.name == "unnamed_event"
    assert not e.resolved


def test_event_serialise_roundtrip() -> None:
    e = Event(
        name="birthday",
        event_type="social",
        tick_scheduled=10,
        participants=[1, 2, 3],
        payload={"gift": "book"},
    )
    e2 = Event.from_dict(e.to_dict())
    assert e2.name == "birthday"
    assert e2.participants == [1, 2, 3]
    assert e2.payload == {"gift": "book"}
