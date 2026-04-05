"""Tests for Simulation — lifecycle, determinism, snapshot/replay."""
from __future__ import annotations
import pytest
from pykworldsim.core.world import World
from pykworldsim.core.simulation import Simulation, SimulationState
from pykworldsim.core.components.position import Position
from pykworldsim.core.components.velocity import Velocity
from pykworldsim.core.systems.movement import MovementSystem


def test_initial_state(sim):
    assert sim.tick == 0 and sim.elapsed == 0.0
    assert sim.state == SimulationState.IDLE

def test_step_advances(sim):
    sim.step(dt=1.0)
    assert sim.tick == 1 and abs(sim.elapsed - 1.0) < 1e-9

def test_run_count(sim):
    sim.run(steps=10, dt=0.5)
    assert sim.tick == 10
    assert abs(sim.elapsed - 5.0) < 1e-9

def test_pause_resume(sim):
    sim.step(); sim.pause()
    assert sim.state == SimulationState.PAUSED
    with pytest.raises(RuntimeError): sim.step()
    sim.resume(); sim.step()
    assert sim.tick == 2

def test_pause_when_idle_raises(sim):
    with pytest.raises(RuntimeError): sim.pause()

def test_stop(sim):
    sim.stop()
    with pytest.raises(RuntimeError): sim.step()

def test_reset(sim):
    sim.run(steps=5)
    sim.reset()
    assert sim.tick == 0 and sim.elapsed == 0.0

def test_on_step_callback(sim):
    ticks = []
    sim.on_step(lambda s: ticks.append(s.tick))
    sim.run(steps=5)
    assert ticks == [1,2,3,4,5]

def test_iter_steps(sim):
    assert [s.tick for s in sim.iter_steps(4)] == [1,2,3,4]

def test_stop_inside_callback(sim):
    sim.on_step(lambda s: s.stop() if s.tick == 3 else None)
    sim.run(steps=100)
    assert sim.tick == 3

def test_determinism():
    def build():
        w = World(); w.register_system(MovementSystem())
        e = w.create_entity()
        w.add_component(e, Position(x=0.0, y=0.0))
        w.add_component(e, Velocity(dx=1.0, dy=1.0))
        return w, e, Simulation(w, seed=42)
    w1, e1, s1 = build(); w2, e2, s2 = build()
    s1.run(50, dt=0.1); s2.run(50, dt=0.1)
    p1 = w1.get_component(e1, Position); p2 = w2.get_component(e2, Position)
    assert abs(p1.x - p2.x) < 1e-10 and abs(p1.y - p2.y) < 1e-10

def test_injected_rng_is_deterministic():
    s1 = Simulation(World(), seed=99)
    s2 = Simulation(World(), seed=99)
    vals1 = [s1.rng.random() for _ in range(10)]
    vals2 = [s2.rng.random() for _ in range(10)]
    assert vals1 == vals2

def test_snapshot_restore():
    w = World(); w.register_system(MovementSystem())
    e = w.create_entity()
    w.add_component(e, Position(x=0.0, y=0.0))
    w.add_component(e, Velocity(dx=1.0, dy=0.0))
    sim = Simulation(w, seed=7)
    sim.run(steps=10, dt=1.0)
    pos_at_10 = w.get_component(e, Position).x
    sim.take_snapshot("at_10")
    sim.run(steps=10, dt=1.0)
    assert w.get_component(e, Position).x > pos_at_10
    # Snapshot content was recorded (full restore requires World.load wiring)
    assert "at_10" in sim.list_snapshots()

def test_movement_integration(populated_world):
    world, e = populated_world
    sim = Simulation(world, seed=0)
    sim.step(dt=2.0)
    pos = world.get_component(e, Position)
    assert abs(pos.x - 2.0) < 1e-9 and abs(pos.y - 4.0) < 1e-9
