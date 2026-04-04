"""Simulation — deterministic, pausable simulation loop over a World."""

from __future__ import annotations

import logging
import random
from enum import Enum, auto
from typing import Callable, Iterator

from pykworldsim.core.world import World

logger = logging.getLogger(__name__)


class SimulationState(Enum):
    """Lifecycle states of a :class:`Simulation`."""
    IDLE    = auto()
    RUNNING = auto()
    PAUSED  = auto()
    STOPPED = auto()


class Simulation:
    """
    Controls the stepping and lifecycle of a :class:`~pykworldsim.core.world.World`.

    Parameters
    ----------
    world:
        The world to simulate.
    seed:
        Integer seed for :mod:`random`. ``None`` → non-deterministic.

    Examples
    --------
    >>> sim = Simulation(world, seed=42)
    >>> sim.run(steps=100, dt=0.016)
    """

    def __init__(self, world: World, seed: int | None = None) -> None:
        self._world: World = world
        self._seed: int | None = seed
        self._state: SimulationState = SimulationState.IDLE
        self._tick: int = 0
        self._elapsed: float = 0.0
        self._step_callbacks: list[Callable[["Simulation"], None]] = []

        if seed is not None:
            random.seed(seed)
            logger.info("Simulation seeded with %d", seed)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def world(self) -> World:
        return self._world

    @property
    def tick(self) -> int:
        """Number of steps executed so far."""
        return self._tick

    @property
    def elapsed(self) -> float:
        """Cumulative simulated time."""
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
        """Pause the simulation. Raises ``RuntimeError`` if not running."""
        if self._state != SimulationState.RUNNING:
            raise RuntimeError("Cannot pause: simulation is not running.")
        self._state = SimulationState.PAUSED
        logger.info("Paused at tick %d", self._tick)

    def resume(self) -> None:
        """Resume a paused simulation. Raises ``RuntimeError`` if not paused."""
        if self._state != SimulationState.PAUSED:
            raise RuntimeError("Cannot resume: simulation is not paused.")
        self._state = SimulationState.RUNNING
        logger.info("Resumed at tick %d", self._tick)

    def stop(self) -> None:
        """Permanently stop the simulation."""
        self._state = SimulationState.STOPPED
        logger.info("Stopped at tick %d", self._tick)

    def reset(self) -> None:
        """Reset tick/elapsed counters; world state is preserved."""
        self._tick = 0
        self._elapsed = 0.0
        self._state = SimulationState.IDLE
        if self._seed is not None:
            random.seed(self._seed)
        logger.info("Simulation reset")

    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------

    def on_step(self, callback: Callable[["Simulation"], None]) -> None:
        """Register *callback* to be called after every :meth:`step`."""
        self._step_callbacks.append(callback)

    # ------------------------------------------------------------------
    # Stepping
    # ------------------------------------------------------------------

    def step(self, dt: float = 1.0) -> None:
        """
        Advance the simulation by a single tick.

        Raises
        ------
        RuntimeError
            If the simulation is paused or stopped.
        """
        if self._state == SimulationState.PAUSED:
            raise RuntimeError("Simulation is paused. Call resume() first.")
        if self._state == SimulationState.STOPPED:
            raise RuntimeError("Simulation is stopped. Create a new instance.")

        self._state = SimulationState.RUNNING
        self._world.update(dt)
        self._tick += 1
        self._elapsed += dt

        for cb in self._step_callbacks:
            cb(self)

        logger.debug("Tick %d | elapsed=%.4f", self._tick, self._elapsed)

    def run(self, steps: int, dt: float = 1.0) -> None:
        """Execute *steps* consecutive ticks of size *dt*."""
        logger.info("Running %d steps × dt=%.4f (world=%r)", steps, dt, self._world.name)
        for _ in range(steps):
            if self._state == SimulationState.STOPPED:
                break
            self.step(dt)
        logger.info("Done: tick=%d elapsed=%.4f", self._tick, self._elapsed)

    def iter_steps(self, steps: int, dt: float = 1.0) -> Iterator["Simulation"]:
        """
        Generator that yields *self* after each tick.

        Useful for per-tick inspection or visualisation::

            for sim in simulation.iter_steps(100, dt=0.1):
                print(sim.tick)
        """
        for _ in range(steps):
            if self._state == SimulationState.STOPPED:
                return
            self.step(dt)
            yield self

    def __repr__(self) -> str:
        return (
            f"Simulation(state={self._state.name}, "
            f"tick={self._tick}, elapsed={self._elapsed:.4f})"
        )
