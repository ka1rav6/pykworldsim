"""Tests for Simulation lifecycle, determinism, and hooks."""
from __future__ import annotations

import pytest

from pykworldsim.core.world import World
from pykworldsim.core.simulation import Simulation, SimulationState
from pykworldsim.core.components.position import Position
from pykworldsim.core.components.velocity import Velocity
from pykworldsim.core.systems.movement import MovementSystem


def test_initial_state(sim: Simulation) -> None:
    assert sim.tick == 0
    assert sim.elapsed == 0.0
    assert sim.state == SimulationState.IDLE


def test_step_advances_tick(sim: Simulation) -> None:
    sim.step(dt=1.0)
    assert sim.tick == 1


def test_step_accumulates_elapsed(sim: Simulation) -> None:
    sim.step(dt=0.5)
    sim.step(dt=0.5)
    assert abs(sim.elapsed - 1.0) < 1e-9


def test_run_correct_tick_count(sim: Simulation) -> None:
    sim.run(steps=25, dt=0.04)
    assert sim.tick == 25


def test_run_correct_elapsed(sim: Simulation) -> None:
    sim.run(steps=10, dt=0.1)
    assert abs(sim.elapsed - 1.0) < 1e-9


def test_state_becomes_running_on_step(sim: Simulation) -> None:
    sim.step()
    assert sim.state == SimulationState.RUNNING


def test_pause_sets_state(sim: Simulation) -> None:
    sim.step()
    sim.pause()
    assert sim.state == SimulationState.PAUSED


def test_pause_when_not_running_raises(sim: Simulation) -> None:
    with pytest.raises(RuntimeError):
        sim.pause()


def test_step_while_paused_raises(sim: Simulation) -> None:
    sim.step()
    sim.pause()
    with pytest.raises(RuntimeError):
        sim.step()


def test_resume_restores_running(sim: Simulation) -> None:
    sim.step()
    sim.pause()
    sim.resume()
    assert sim.state == SimulationState.RUNNING
    sim.step()
    assert sim.tick == 2


def test_resume_when_not_paused_raises(sim: Simulation) -> None:
    with pytest.raises(RuntimeError):
        sim.resume()


def test_stop_prevents_stepping(sim: Simulation) -> None:
    sim.stop()
    assert sim.state == SimulationState.STOPPED
    with pytest.raises(RuntimeError):
        sim.step()


def test_run_stops_early_if_stopped(sim: Simulation) -> None:
    call_count = [0]

    @sim.on_step
    def stopper(s: Simulation) -> None:
        call_count[0] += 1
        if s.tick == 3:
            s.stop()

    sim.run(steps=100)
    assert sim.tick == 3


def test_reset_clears_counters(sim: Simulation) -> None:
    sim.run(steps=10)
    sim.reset()
    assert sim.tick == 0
    assert sim.elapsed == 0.0
    assert sim.state == SimulationState.IDLE


def test_on_step_callback_fires_each_tick(sim: Simulation) -> None:
    recorded: list[int] = []
    sim.on_step(lambda s: recorded.append(s.tick))
    sim.run(steps=5)
    assert recorded == [1, 2, 3, 4, 5]


def test_multiple_callbacks(sim: Simulation) -> None:
    a: list[int] = []
    b: list[int] = []
    sim.on_step(lambda s: a.append(s.tick))
    sim.on_step(lambda s: b.append(s.tick))
    sim.run(steps=3)
    assert a == b == [1, 2, 3]


def test_iter_steps_yields_self(sim: Simulation) -> None:
    ticks = [s.tick for s in sim.iter_steps(5, dt=1.0)]
    assert ticks == [1, 2, 3, 4, 5]


def test_determinism_same_seed() -> None:
    def build():
        w = World()
        w.register_system(MovementSystem())
        e = w.create_entity()
        w.add_component(e, Position(x=0.0, y=0.0))
        w.add_component(e, Velocity(dx=1.0, dy=1.0))
        return w, e, Simulation(w, seed=42)

    w1, e1, s1 = build()
    w2, e2, s2 = build()
    s1.run(50, dt=0.1)
    s2.run(50, dt=0.1)

    p1 = w1.get_component(e1, Position)
    p2 = w2.get_component(e2, Position)
    assert abs(p1.x - p2.x) < 1e-10
    assert abs(p1.y - p2.y) < 1e-10


def test_movement_integration(populated_world) -> None:
    world, e = populated_world
    sim = Simulation(world, seed=0)
    sim.step(dt=2.0)
    pos = world.get_component(e, Position)
    # dx=1.0, dy=2.0, dt=2.0 → x=2.0, y=4.0
    assert abs(pos.x - 2.0) < 1e-9
    assert abs(pos.y - 4.0) < 1e-9
