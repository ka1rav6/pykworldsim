import random
from dataclasses import dataclass
from typing import Optional, Callable


@dataclass
class Event:
    """A world event that fires probabilistically or on demand."""
    Name: str
    Probability: float = 0.05          # per-year probability
    Effect: Optional[Callable] = None  # fn(world, year) → None
    Description: str = ""
    IsGlobal: bool = True              # True = affects everyone; False = individual

    def ShouldTrigger(self) -> bool:
        return random.random() < self.Probability

    def Fire(self, World, Year: int):
        Msg = f"[Year {Year}] EVENT: {self.Name}"
        if self.Description:
            Msg += f" — {self.Description}"
        World.Log.append(Msg)
        if self.Effect:
            self.Effect(World, Year)

    def __str__(self):
        Scope = "Global" if self.IsGlobal else "Local"
        return f"Event: {self.Name} ({self.Probability*100:.1f}%) - {Scope}"
