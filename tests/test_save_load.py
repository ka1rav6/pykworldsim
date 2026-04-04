"""Tests for world serialisation (save/load) and config loader."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest

from pykworldsim.core.world import World
from pykworldsim.core.components.position import Position
from pykworldsim.core.components.velocity import Velocity
from pykworldsim.core.components.person import Person
from pykworldsim.core.config.loader import ConfigLoader, WorldConfig, SimulationConfig


# ── Helper ────────────────────────────────────────────────────────────

def tmp_json(data: dict) -> str:
    f = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w")
    json.dump(data, f)
    f.close()
    return f.name


# ── Save / Load ───────────────────────────────────────────────────────

def test_save_load_position_velocity() -> None:
    world = World(name="saveable")
    e = world.create_entity()
    world.add_component(e, Position(x=5.0, y=10.0))
    world.add_component(e, Velocity(dx=1.5, dy=-2.5))

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        world.save(path)
        loaded = World.load(path)
        pos = loaded.get_component(e, Position)
        vel = loaded.get_component(e, Velocity)
        assert abs(pos.x - 5.0) < 1e-9
        assert abs(pos.y - 10.0) < 1e-9
        assert abs(vel.dx - 1.5) < 1e-9
        assert abs(vel.dy - -2.5) < 1e-9
    finally:
        os.unlink(path)


def test_save_load_person() -> None:
    world = World(name="person-world")
    e = world.create_entity()
    world.add_component(e, Person(name="Bob", age=40.0, happiness=75.0))

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        world.save(path)
        loaded = World.load(path)
        p = loaded.get_component(e, Person)
        assert p.name == "Bob"
        assert p.age == 40.0
        assert p.happiness == 75.0
    finally:
        os.unlink(path)


def test_save_preserves_world_name() -> None:
    world = World(name="my-special-world")
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        world.save(path)
        loaded = World.load(path)
        assert loaded.name == "my-special-world"
    finally:
        os.unlink(path)


def test_save_json_structure() -> None:
    world = World(name="struct-test")
    e = world.create_entity()
    world.add_component(e, Position(x=1.0, y=2.0))

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        path = f.name
    try:
        world.save(path)
        with open(path) as fh:
            data = json.load(fh)
        assert data["name"] == "struct-test"
        assert "Position" in data["components"]
        assert str(e.id) in data["components"]["Position"]
    finally:
        os.unlink(path)


def test_save_multiple_entities() -> None:
    world = World(name="multi")
    for i in range(5):
        e = world.create_entity()
        world.add_component(e, Position(x=float(i), y=0.0))

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        world.save(path)
        loaded = World.load(path)
        assert len(loaded.entities) == 5
    finally:
        os.unlink(path)


# ── ConfigLoader ──────────────────────────────────────────────────────

def test_config_load_json() -> None:
    raw = {
        "name": "json-world",
        "simulation": {"steps": 20, "dt": 0.5, "seed": 7},
        "entities": [
            {"position": {"x": 1.0, "y": 2.0}, "velocity": {"dx": 0.5, "dy": 0.0}}
        ],
    }
    path = tmp_json(raw)
    try:
        cfg = ConfigLoader.load(path)
        assert cfg.name == "json-world"
        assert cfg.simulation.steps == 20
        assert cfg.simulation.seed == 7
        assert len(cfg.entities) == 1
    finally:
        os.unlink(path)


def test_config_build_creates_world_and_sim() -> None:
    raw = {
        "name": "built-world",
        "entities": [
            {"position": {"x": 0.0, "y": 0.0}, "velocity": {"dx": 1.0, "dy": 0.0}},
            {"person": {"name": "Carol", "age": 22.0}},
        ],
    }
    cfg = ConfigLoader._parse(raw)
    world, sim = ConfigLoader.build(cfg)
    assert world.name == "built-world"
    assert len(world.entities) == 2


def test_config_build_runs_simulation() -> None:
    raw = {
        "name": "runnable",
        "simulation": {"steps": 10, "dt": 0.1, "seed": 99},
        "entities": [
            {"position": {"x": 0.0, "y": 0.0}, "velocity": {"dx": 2.0, "dy": 0.0}}
        ],
    }
    cfg = ConfigLoader._parse(raw)
    world, sim = ConfigLoader.build(cfg)
    sim.run(steps=cfg.simulation.steps, dt=cfg.simulation.dt)
    assert sim.tick == 10


def test_config_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        ConfigLoader.load("/nonexistent/path/config.yaml")


def test_config_unsupported_extension_raises() -> None:
    with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
        path = f.name
    try:
        with pytest.raises(ValueError, match="Unsupported"):
            ConfigLoader.load(path)
    finally:
        os.unlink(path)
