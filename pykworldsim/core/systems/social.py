"""SocialSystem — ageing, energy, happiness, relationship drift, goal progress."""
from __future__ import annotations
import logging
from typing import TYPE_CHECKING
from pykworldsim.core.systems.base_system import BaseSystem
from pykworldsim.core.components.person import Person
from pykworldsim.core.components.relationship import Relationship
from pykworldsim.core.components.job import Job
from pykworldsim.core.components.goal import Goal
if TYPE_CHECKING:
    from pykworldsim.core.world import World

logger = logging.getLogger(__name__)

class SocialSystem(BaseSystem):
    """Simulates ageing, energy decay, happiness, relationships, and goals."""
    priority: int = 20

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

    def update(self, world: "World", dt: float) -> None:
        self._update_persons(world, dt)
        self._update_relationships(world, dt)
        self._update_goals(world, dt)

    def _update_persons(self, world: "World", dt: float) -> None:
        for entity, (person,) in world.get_entities_with(Person):
            person.age += self.age_rate * dt
            person.energy = max(0.0, min(100.0, person.energy - self.energy_decay * dt))
            job_bonus = 0.0
            if world.has_component(entity, Job):
                job = world.get_component(entity, Job)
                job_bonus = (job.satisfaction - 50.0) * 0.01
            person.happiness = max(0.0, min(100.0,
                person.happiness - self.happiness_decay * dt + job_bonus * dt))
            if person.energy < 20.0:
                person.happiness = max(0.0, person.happiness - 0.2 * dt)

    def _update_relationships(self, world: "World", dt: float) -> None:
        for entity, (rel,) in world.get_entities_with(Relationship):
            if rel.strength > 0:
                rel.strength = max(0.0, rel.strength - 0.001 * dt)
            elif rel.strength < 0:
                rel.strength = min(0.0, rel.strength + 0.001 * dt)

    def _update_goals(self, world: "World", dt: float) -> None:
        for entity, (goal,) in world.get_entities_with(Goal):
            if goal.completed:
                continue
            goal.progress = min(100.0, goal.progress + goal.priority * 0.5 * dt)
            if goal.progress >= 100.0:
                goal.completed = True
                world.events.emit_deferred(
                    "goal_completed",
                    {"entity": entity, "description": goal.description}
                )
                logger.info("%r completed goal: %r", entity, goal.description)
