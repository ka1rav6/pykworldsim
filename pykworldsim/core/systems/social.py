"""SocialSystem — models happiness, energy decay, ageing, and relationship drift."""
from __future__ import annotations

import logging
import random

from pykworldsim.core.systems.base_system import BaseSystem
from pykworldsim.core.components.person import Person
from pykworldsim.core.components.relationship import Relationship
from pykworldsim.core.components.job import Job
from pykworldsim.core.components.goal import Goal

logger = logging.getLogger(__name__)


class SocialSystem(BaseSystem):
    """
    Advances the social state of Person entities each tick.

    Effects per tick
    ----------------
    * **Ageing** — ``person.age += dt * age_rate``
    * **Energy decay** — energy depletes from work hours; recovers during rest.
    * **Job satisfaction → happiness** — high satisfaction raises happiness.
    * **Relationship drift** — strength drifts slightly towards 0 if no interaction.
    * **Goal progress** — active goals slowly advance.

    Parameters
    ----------
    age_rate:       Simulation years advanced per unit of elapsed time.
    energy_decay:   Energy lost per tick (offset by job hours).
    happiness_decay: Base happiness lost per tick (offset by job satisfaction).
    """

    def __init__(
        self,
        age_rate: float = 0.01,
        energy_decay: float = 0.5,
        happiness_decay: float = 0.1,
    ) -> None:
        super().__init__()
        self.age_rate = age_rate
        self.energy_decay = energy_decay
        self.happiness_decay = happiness_decay

    def update(self, dt: float) -> None:
        self._update_persons(dt)
        self._update_relationships(dt)
        self._update_goals(dt)

    def _update_persons(self, dt: float) -> None:
        for entity, (person,) in self.world.get_components(Person):
            # Ageing
            person.age += self.age_rate * dt

            # Energy decay, clamped [0, 100]
            person.energy = max(0.0, min(100.0, person.energy - self.energy_decay * dt))

            # Happiness decay offset by job satisfaction
            job_bonus = 0.0
            if self.world.has_component(entity, Job):
                job = self.world.get_component(entity, Job)
                job_bonus = (job.satisfaction - 50.0) * 0.01
            person.happiness = max(
                0.0,
                min(100.0, person.happiness - self.happiness_decay * dt + job_bonus * dt),
            )

            # Low energy hits happiness
            if person.energy < 20.0:
                person.happiness = max(0.0, person.happiness - 0.2 * dt)

            logger.debug(
                "%r %s: age=%.2f energy=%.1f happiness=%.1f",
                entity, person.name, person.age, person.energy, person.happiness,
            )

    def _update_relationships(self, dt: float) -> None:
        for entity, (rel,) in self.world.get_components(Relationship):
            # Drift towards neutral when not interacting
            if rel.strength > 0:
                rel.strength = max(0.0, rel.strength - 0.001 * dt)
            elif rel.strength < 0:
                rel.strength = min(0.0, rel.strength + 0.001 * dt)

    def _update_goals(self, dt: float) -> None:
        for entity, (goal,) in self.world.get_components(Goal):
            if goal.completed:
                continue
            # Progress ticks forward; rate proportional to priority
            rate = goal.priority * 0.5
            goal.progress = min(100.0, goal.progress + rate * dt)
            if goal.progress >= 100.0:
                goal.completed = True
                logger.info("%r completed goal: %r", entity, goal.description)
