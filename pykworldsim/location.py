class Location:
    """A place in the world where people live, work, and interact."""

    def __init__(self, Name: str, LocationType: str = "city",
                 OpportunityLevel: float = 0.5,
                 CostOfLiving: float = 0.5,
                 PopulationDensity: float = 0.5):
        self.Name = Name
        self.LocationType = LocationType  # city, suburb, rural, campus
        self.OpportunityLevel = max(0.0, min(1.0, OpportunityLevel))
        self.CostOfLiving = max(0.0, min(1.0, CostOfLiving))
        self.PopulationDensity = max(0.0, min(1.0, PopulationDensity))
        self.Residents: list = []
        self.Jobs: list = []

    def AddResident(self, Person):
        if Person not in self.Residents:
            self.Residents.append(Person)

    def RemoveResident(self, Person):
        if Person in self.Residents:
            self.Residents.remove(Person)

    def AddJob(self, Job):
        self.Jobs.append(Job)

    def __repr__(self):
        return f"Location({self.Name}, type={self.LocationType}, residents={len(self.Residents)})"
