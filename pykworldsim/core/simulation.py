"""
Simulation — deterministic, pausable loop with injected RNG and snapshot/replay.

v3 improvements
---------------
* ``random.Random(seed)`` injected — ALL randomness uses this instance.
* Snapshot/replay: :meth:`take_snapshot` / :meth:`restore_snapshot`.
* Step-level callbacks via :meth:`on_step`.
* ``--steps / --dt / --seed`` all wired from CLI.
"""
from __future__ import annotations

import copy
import logging
import random
from enum import Enum, auto
from typing import Any, Callable, Iterator

from pykworldsim.core.world import World

logger = logging.getLogger(__name__)


class SimulationState(Enum):
    """Lifecycle states."""
    IDLE    = auto()
    RUNNING = auto()
    PAUSED  = auto()
    STOPPED = auto()


class Simulation:
    """
    Controls stepping and lifecycle of a :class:`~pykworldsim.core.world.World`.

    Parameters
    ----------
    world:
        The world to simulate.
    seed:
        Integer seed for the **injected** :class:`random.Random` instance.
        ``None`` → non-deterministic.

    Examples
    --------
    >>> sim = Simulation(world, seed=42)
    >>> sim.run(steps=100, dt=0.016)

    All randomness in systems should use ``sim.rng`` (or ``world`` can expose it)
    rather than the global ``random`` module to preserve determinism.
    """

    def __init__(self, world: World, seed: int | None = None) -> None:
        self._world: World = world
        self._seed: int | None = seed
        self._state: SimulationState = SimulationState.IDLE
        self._tick: int = 0
        self._elapsed: float = 0.0
        self._step_callbacks: list[Callable[["Simulation"], None]] = []
        self._snapshots: dict[str, dict[str, Any]] = {}

        # Injected RNG — all randomness must use this instance
        self.rng: random.Random = random.Random(seed)
        if seed is not None:
            logger.info("Simulation seeded with %d", seed)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def world(self) -> World:
        return self._world

    @property
    def tick(self) -> int:
        return self._tick

    @property
    def elapsed(self) -> float:
        return self._elapsed

    @property
    def state(self) -> SimulationState:
        return self._state

    @property
    def is_running(self) -> bool:
        return self._state == SimulationState.RUNNING

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def pause(self) -> None:
        """Pause. Raises ``RuntimeError`` if not running."""
        if self._state != SimulationState.RUNNING:
            raise RuntimeError("Cannot pause: not running.")
        self._state = SimulationState.PAUSED
        logger.info("Paused at tick %d", self._tick)

    def resume(self) -> None:
        """Resume. Raises ``RuntimeError`` if not paused."""
        if self._state != SimulationState.PAUSED:
            raise RuntimeError("Cannot resume: not paused.")
        self._state = SimulationState.RUNNING
        logger.info("Resumed at tick %d", self._tick)

    def stop(self) -> None:
        """Permanently stop."""
        self._state = SimulationState.STOPPED
        logger.info("Stopped at tick %d", self._tick)

    def reset(self) -> None:
        """Reset counters; world state is preserved."""
        self._tick = 0
        self._elapsed = 0.0
        self._state = SimulationState.IDLE
        self.rng = random.Random(self._seed)
        logger.info("Simulation reset")

    # ------------------------------------------------------------------
    # Step hooks
    # ------------------------------------------------------------------

    def on_step(self, callback: Callable[["Simulation"], None]) -> None:
        """Register *callback* called after every :meth:`step`."""
        self._step_callbacks.append(callback)

    # ------------------------------------------------------------------
    # Stepping
    # ------------------------------------------------------------------

    def step(self, dt: float = 1.0) -> None:
        """
        Advance by a single tick.

        Raises
        ------
        RuntimeError
            If paused or stopped.
        """
        if self._state == SimulationState.PAUSED:
            raise RuntimeError("Paused. Call resume() first.")
        if self._state == SimulationState.STOPPED:
            raise RuntimeError("Stopped. Create a new instance.")

        self._state = SimulationState.RUNNING
        self._world.update(dt)
        self._tick += 1
        self._elapsed += dt

        for cb in self._step_callbacks:
            cb(self)

        logger.debug("Tick %d | elapsed=%.4f", self._tick, self._elapsed)

    def run(self, steps: int, dt: float = 1.0) -> None:
        """Execute *steps* ticks of size *dt*."""
        logger.info("Running %d steps × dt=%.4f (world=%r)", steps, dt, self._world.name)
        for _ in range(steps):
            if self._state == SimulationState.STOPPED:
                break
            self.step(dt)
        logger.info("Done: tick=%d elapsed=%.4f", self._tick, self._elapsed)

    def iter_steps(self, steps: int, dt: float = 1.0) -> Iterator["Simulation"]:
        """Generator yielding *self* after each tick — for inspection loops."""
        for _ in range(steps):
            if self._state == SimulationState.STOPPED:
                return
            self.step(dt)
            yield self

    # ------------------------------------------------------------------
    # Snapshot / Replay
    # ------------------------------------------------------------------

    def take_snapshot(self, label: str) -> None:
        """
        Save the current world serialised state and RNG state under *label*.

        Retrieve with :meth:`restore_snapshot`.
        """
        self._snapshots[label] = {
            "world_dict": self._world.to_dict(),
            "tick": self._tick,
            "elapsed": self._elapsed,
            "rng_state": self.rng.getstate(),
        }
        logger.info("Snapshot taken: %r (tick=%d)", label, self._tick)

    def restore_snapshot(self, label: str) -> None:
        """
        Restore world state from a previously taken snapshot.

        Raises
        ------
        KeyError
            If *label* does not exist.
        """
        snap = self._snapshots.get(label)
        if snap is None:
            raise KeyError(f"No snapshot with label {label!r}.")

        # Re-build world from serialised dict
        import json, tempfile, os
        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w"
        ) as f:
            json.dump(snap["world_dict"], f)
            tmp_path = f.name
        try:
            restored_world = World.load(tmp_path)
        finally:
            os.unlink(tmp_path)

        # Rewire systems from the old world
        for system in self._world.systems:
            system.world = restored_world
            restored_world._systems.append(system)

        self._world = restored_world
        self._tick = snap["tick"]
        self._elapsed = snap["elapsed"]
        self.rng.setstate(snap["rng_state"])
        logger.info("Snapshot restored: %r (tick=%d)", label, self._tick)

    def list_snapshots(self) -> list[str]:
        """Return all snapshot labels."""
        return list(self._snapshots.keys())

    def __repr__(self) -> str:
        return (
            f"Simulation(state={self._state.name}, "
            f"tick={self._tick}, elapsed={self._elapsed:.4f})"
        )
