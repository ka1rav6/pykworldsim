import random
from dataclasses import dataclass, field
from typing import List


@dataclass
class RelationshipEvent:
    Year: int
    EventType: str
    Description: str


class Relationship:
    """Tracks a directed relationship between two people."""

    Types = ["acquaintance", "friend", "close_friend", "rival", "partner", "family"]

    def __init__(self, PersonA: "Person", PersonB: "Person"):
        self.PersonA = PersonA
        self.PersonB = PersonB
        self.Strength = 0.1
        self.Trust = 0.3
        self.Attraction = 0.0
        self.Respect = 0.3
        self.RelationshipType = "acquaintance"
        self.History: List[RelationshipEvent] = []
        self.YearMet = None
        self.IsRomantic = False
        self.IsFamily = False

    def RecordEvent(self, Year: int, EventType: str, Description: str):
        self.History.append(RelationshipEvent(Year, EventType, Description))

    def UpdateType(self):
        if self.IsFamily:
            self.RelationshipType = "family"
        elif self.IsRomantic:
            self.RelationshipType = "partner"
        elif self.Strength < 0.2:
            self.RelationshipType = "acquaintance"
        elif self.Strength < 0.5:
            self.RelationshipType = "friend"
        elif self.Trust < 0.2:
            self.RelationshipType = "rival"
        else:
            self.RelationshipType = "close_friend"

    def Interact(self, Context: str = "casual", Year: int = 0):
        """Process an interaction and update relationship scores."""
        CompatibilityBonus = self._ComputeCompatibility()

        if Context == "party":
            StrengthDelta = random.uniform(0.02, 0.08) + CompatibilityBonus
            TrustDelta = random.uniform(-0.01, 0.03)
        elif Context == "work":
            StrengthDelta = random.uniform(0.01, 0.05) + CompatibilityBonus
            TrustDelta = random.uniform(0.01, 0.04)
            self.Respect = min(1.0, self.Respect + random.uniform(0.0, 0.03))
        elif Context == "conflict":
            StrengthDelta = random.uniform(-0.15, -0.03)
            TrustDelta = random.uniform(-0.12, -0.02)
            self.RecordEvent(Year, "conflict", f"{self.PersonA.Name} and {self.PersonB.Name} had a conflict")
        elif Context == "support":
            StrengthDelta = random.uniform(0.05, 0.15)
            TrustDelta = random.uniform(0.05, 0.10)
            self.RecordEvent(Year, "bonding", f"{self.PersonA.Name} supported {self.PersonB.Name}")
        else:
            StrengthDelta = random.uniform(0.01, 0.04) + CompatibilityBonus
            TrustDelta = random.uniform(0.0, 0.02)

        self.Strength = max(0.0, min(1.0, self.Strength + StrengthDelta))
        self.Trust = max(0.0, min(1.0, self.Trust + TrustDelta))
        self.UpdateType()

    def Decay(self, Rate: float = 0.02):
        """Relationships weaken without interaction."""
        self.Strength = max(0.0, self.Strength - Rate)
        self.UpdateType()

    def _ComputeCompatibility(self) -> float:
        A = self.PersonA.Traits
        B = self.PersonB.Traits
        Diff = sum(abs(A.get(K, 0.5) - B.get(K, 0.5)) for K in A if K in B)
        NumShared = sum(1 for K in A if K in B)
        if NumShared == 0:
            return 0.0
        return (1.0 - Diff / NumShared) * 0.05

    def __repr__(self):
        return (f"Relationship({self.PersonA.Name} ↔ {self.PersonB.Name}, "
                f"type={self.RelationshipType}, strength={self.Strength:.2f})")
