class Job:
    """A job that can be held by a person."""

    def __init__(self, Role: str, Salary: float = 50000,
                 Prestige: float = 0.5, StressLevel: float = 0.4,
                 SkillRequired: float = 0.3, Industry: str = "general"):
        self.Role = Role
        self.Salary = Salary
        self.Prestige = max(0.0, min(1.0, Prestige))
        self.StressLevel = max(0.0, min(1.0, StressLevel))
        self.SkillRequired = max(0.0, min(1.0, SkillRequired))
        self.Industry = Industry
        self.Holder = None
        self.Location = str(None)

    def IsAvailable(self) -> bool:
        return self.Holder is None

    def Assign(self, Person):
        self.Holder = Person

    def Vacate(self):
        self.Holder = None

    def AnnualSalary(self, Year: int = 0) -> float:
        """Salary grows slightly with experience."""
        return self.Salary * (1.02 ** Year)

    def __repr__(self):
        Status = f"held by {self.Holder.Name}" if self.Holder else "available"
        return f"Job({self.Role}, salary={self.Salary:,.0f}, {Status})"
