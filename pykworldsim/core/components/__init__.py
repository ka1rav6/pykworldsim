"""Built-in ECS components."""
from pykworldsim.core.components.position import Position
from pykworldsim.core.components.velocity import Velocity
from pykworldsim.core.components.person import Person
from pykworldsim.core.components.location import Location
from pykworldsim.core.components.relationship import Relationship
from pykworldsim.core.components.job import Job
from pykworldsim.core.components.goal import Goal
from pykworldsim.core.components.event import Event

__all__ = [
    "Position", "Velocity",
    "Person", "Location", "Relationship",
    "Job", "Goal", "Event",
]
