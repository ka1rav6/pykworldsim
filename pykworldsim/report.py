from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .world import World


class Report:
    """Analytics and reporting on a simulated world."""

    def __init__(self, World: "World"):
        self.World = World

    def _AlivePeople(self):
        return [P for P in self.World.People if P.IsAlive]

    def TopHappiest(self, N: int = 5) -> List[dict]:
        """Return the N happiest people."""
        Alive = self._AlivePeople()
        Sorted = sorted(Alive, key=lambda P: P.LifeSatisfaction, reverse=True)
        return [P.Summary() for P in Sorted[:N]]

    def MostConnected(self, N: int = 5) -> List[dict]:
        """Return the N most socially connected people."""
        Alive = self._AlivePeople()
        Sorted = sorted(Alive,
                        key=lambda P: P._CountRelationshipsByType(["friend", "close_friend", "partner"]),
                        reverse=True)
        return [P.Summary() for P in Sorted[:N]]

    def Wealthiest(self, N: int = 5) -> List[dict]:
        Alive = self._AlivePeople()
        return [P.Summary() for P in sorted(Alive, key=lambda P: P.Savings, reverse=True)[:N]]

    def Unemployed(self) -> List[dict]:
        Alive = self._AlivePeople()
        return [P.Summary() for P in Alive if P.Job is None and P.Age >= 18]

    def AverageHappiness(self) -> float:
        Alive = self._AlivePeople()
        if not Alive:
            return 0.0
        return round(sum(P.LifeSatisfaction for P in Alive) / len(Alive), 3)

    def AverageIncome(self) -> float:
        Employed = [P for P in self._AlivePeople() if P.Income > 0]
        if not Employed:
            return 0.0
        return round(sum(P.Income for P in Employed) / len(Employed), 2)

    def GiniCoefficient(self) -> float:
        """Measure income inequality (0=perfect equality, 1=maximum inequality)."""
        Incomes = sorted([P.Income for P in self._AlivePeople() if P.Income > 0])
        N = len(Incomes)
        if N == 0:
            return 0.0
        TotalIncome = sum(Incomes)
        if TotalIncome == 0:
            return 0.0
        CumulativeSum = sum((2 * (I + 1) - N - 1) * Incomes[I] for I in range(N))
        return round(CumulativeSum / (N * TotalIncome), 4)

    def PopulationStats(self) -> dict:
        All = self.World.People
        Alive = self._AlivePeople()
        return {
            "TotalEverSimulated": len(All),
            "CurrentlyAlive": len(Alive),
            "Deceased": len(All) - len(Alive),
            "AverageAge": round(sum(P.Age for P in Alive) / len(Alive), 1) if Alive else 0,
            "Couples": sum(1 for P in Alive if P.RomanticPartner is not None) // 2,
            "TotalChildren": sum(len(P.Children) for P in Alive),
        }

    def PrintSummary(self):
        print("=" * 55)
        print(f"  WORLD REPORT — Year {self.World.CurrentYear}")
        print("=" * 55)
        Stats = self.PopulationStats()
        for K, V in Stats.items():
            print(f"  {K:<28} {V}")
        print(f"  {'AverageHappiness':<28} {self.AverageHappiness()}")
        print(f"  {'AverageIncome':<28} ${self.AverageIncome():,.0f}")
        print(f"  {'GiniCoefficient':<28} {self.GiniCoefficient()}")
        print()
        print("  Top 3 Happiest:")
        for P in self.TopHappiest(3):
            print(f"    • {P['Name']} — satisfaction={P['LifeSatisfaction']}")
        print()
        print("  Most Connected:")
        for P in self.MostConnected(3):
            print(f"    • {P['Name']} — friends={P['Friends']}")
        print("=" * 55)
