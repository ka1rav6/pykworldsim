"""Tests for World serialisation and ConfigLoader."""
from __future__ import annotations
import json, os, tempfile
import pytest
from pykworldsim.core.world import World
from pykworldsim.core.components.position import Position
from pykworldsim.core.components.velocity import Velocity
from pykworldsim.core.components.person import Person
from pykworldsim.core.config.loader import ConfigLoader


def _tmp_json(data):
    f = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w")
    json.dump(data, f); f.close()
    return f.name


def test_save_load_roundtrip():
    w = World(name="saveable")
    e = w.create_entity()
    w.add_component(e, Position(x=5.0, y=10.0))
    w.add_component(e, Velocity(dx=1.5, dy=-2.5))
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f: path = f.name
    try:
        w.save(path); loaded = World.load(path)
        pos = loaded.get_component(e, Position); vel = loaded.get_component(e, Velocity)
        assert abs(pos.x - 5.0) < 1e-9 and abs(vel.dy - -2.5) < 1e-9
    finally:
        os.unlink(path)


def test_save_person():
    w = World(); e = w.create_entity()
    w.add_component(e, Person(name="Bob", age=40.0))
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f: path = f.name
    try:
        w.save(path); loaded = World.load(path)
        assert loaded.get_component(e, Person).name == "Bob"
    finally:
        os.unlink(path)


def test_world_name_preserved():
    w = World(name="my-world")
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f: path = f.name
    try:
        w.save(path); assert World.load(path).name == "my-world"
    finally:
        os.unlink(path)


def test_config_load_json():
    raw = {"name":"jw","simulation":{"steps":5,"dt":0.5,"seed":7},
           "entities":[{"position":{"x":1.0,"y":2.0},"velocity":{"dx":0.5,"dy":0.0}}]}
    path = _tmp_json(raw)
    try:
        cfg = ConfigLoader.load(path)
        assert cfg.name == "jw" and cfg.simulation.steps == 5 and len(cfg.entities) == 1
    finally:
        os.unlink(path)


def test_config_build_and_run():
    raw = {"name":"r","simulation":{"steps":5,"dt":0.1,"seed":0},
           "entities":[{"position":{"x":0.0,"y":0.0},"velocity":{"dx":2.0,"dy":0.0}}]}
    cfg = ConfigLoader._parse(raw)
    w, sim = ConfigLoader.build(cfg)
    sim.run(steps=cfg.simulation.steps, dt=cfg.simulation.dt)
    assert sim.tick == 5


def test_config_count_spawn():
    raw = {"name":"c","entities":[{"position":{"x":0.0,"y":0.0},"count":5}]}
    cfg = ConfigLoader._parse(raw)
    w, _ = ConfigLoader.build(cfg)
    assert len(w.entities) == 5


def test_config_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        ConfigLoader.load("/no/such/file.yaml")


def test_config_unsupported_ext_raises():
    with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f: path = f.name
    try:
        with pytest.raises(ValueError): ConfigLoader.load(path)
    finally:
        os.unlink(path)


def test_edge_case_empty_world():
    w = World()
    assert w.entities == []
    assert list(w.get_entities_with(Position)) == []


def test_edge_case_missing_component():
    w = World(); e = w.create_entity()
    with pytest.raises(KeyError): w.get_component(e, Position)


def test_edge_case_destroy_twice():
    w = World(); e = w.create_entity()
    w.destroy_entity(e); w._flush_staged()
    # Second destroy after flush should not raise — already gone
    w.destroy_entity(e); w._flush_staged()
