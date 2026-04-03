import random
import pickle
import copy
from typing import List, Optional, Dict, Any, Callable

from .person import Person
from .relationship import Relationship
from .location import Location
from .job import Job
from .event import Event
from .report import Report


class World:
    """
    The main simulation container.
    Manages people, locations, jobs, events, and the simulation loop.
    """

    def __init__(self, Seed: Optional[int] = None):
        if Seed is not None:
            random.seed(Seed)
        self.Seed = Seed
        self.People: List[Person] = []
        self.Locations: List[Location] = []
        self.Jobs: List[Job] = []
        self.Events: List[Event] = []
        self.Log: List[str] = []
        self.CurrentYear: int = 0
        self.YearHistory: Dict[int, dict] = {}  # Snapshot per year
        self.Report: Report = Report(self)

        # Feature flags
        self._EconomyEnabled: bool = False
        self._RelationshipsEnabled: bool = True
        self._CultureEnabled: bool = False

        # Default world setup
        self._SetupDefaultWorld()

    # ------------------------------------------------------------------
    # Setup helpers
    # ------------------------------------------------------------------
    def _SetupDefaultWorld(self):
        """Create sensible defaults so the world is usable out of the box."""
        # Locations
        CityA = Location("Metropolis", "city", OpportunityLevel=0.8, CostOfLiving=0.7, PopulationDensity=0.9)
        CityB = Location("Riverside", "suburb", OpportunityLevel=0.5, CostOfLiving=0.4, PopulationDensity=0.5)
        self.AddLocation(CityA)
        self.AddLocation(CityB)

        # Default jobs
        DefaultJobs = [
            Job("Software Engineer", Salary=95000, Prestige=0.7, StressLevel=0.5, SkillRequired=0.6, Industry="tech"),
            Job("Software Engineer", Salary=90000, Prestige=0.7, StressLevel=0.5, SkillRequired=0.6, Industry="tech"),
            Job("Doctor", Salary=180000, Prestige=0.9, StressLevel=0.8, SkillRequired=0.85, Industry="health"),
            Job("Teacher", Salary=50000, Prestige=0.6, StressLevel=0.5, SkillRequired=0.45, Industry="education"),
            Job("Teacher", Salary=48000, Prestige=0.6, StressLevel=0.5, SkillRequired=0.45, Industry="education"),
            Job("Artist", Salary=35000, Prestige=0.4, StressLevel=0.3, SkillRequired=0.3, Industry="creative"),
            Job("Entrepreneur", Salary=70000, Prestige=0.65, StressLevel=0.7, SkillRequired=0.5, Industry="business"),
            Job("Entrepreneur", Salary=65000, Prestige=0.65, StressLevel=0.7, SkillRequired=0.5, Industry="business"),
            Job("Nurse", Salary=60000, Prestige=0.65, StressLevel=0.65, SkillRequired=0.5, Industry="health"),
            Job("Accountant", Salary=65000, Prestige=0.55, StressLevel=0.45, SkillRequired=0.5, Industry="finance"),
            Job("Accountant", Salary=62000, Prestige=0.55, StressLevel=0.45, SkillRequired=0.5, Industry="finance"),
            Job("Retail Worker", Salary=28000, Prestige=0.2, StressLevel=0.35, SkillRequired=0.1, Industry="retail"),
            Job("Retail Worker", Salary=27000, Prestige=0.2, StressLevel=0.35, SkillRequired=0.1, Industry="retail"),
            Job("Retail Worker", Salary=26000, Prestige=0.2, StressLevel=0.35, SkillRequired=0.1, Industry="retail"),
            Job("Lawyer", Salary=120000, Prestige=0.8, StressLevel=0.75, SkillRequired=0.75, Industry="law"),
            Job("Scientist", Salary=80000, Prestige=0.75, StressLevel=0.5, SkillRequired=0.7, Industry="research"),
            Job("Chef", Salary=42000, Prestige=0.45, StressLevel=0.55, SkillRequired=0.35, Industry="food"),
            Job("Chef", Salary=40000, Prestige=0.45, StressLevel=0.55, SkillRequired=0.35, Industry="food"),
            Job("Manager", Salary=75000, Prestige=0.65, StressLevel=0.6, SkillRequired=0.55, Industry="business"),
            Job("Manager", Salary=72000, Prestige=0.65, StressLevel=0.6, SkillRequired=0.55, Industry="business"),
        ]
        for J in DefaultJobs:
            J.Location = CityA.Name
            self.AddJob(J)

        # Refill jobs that are taken each year
        self._BaseJobTemplates = DefaultJobs

    def _RefillJobs(self):
        """Add new job openings each year to reflect economic churn."""
        for Template in self._BaseJobTemplates:
            if all(J.Role != Template.Role or not J.IsAvailable() for J in self.Jobs):
                # All copies are filled; create a new opening
                if random.random() < 0.3:
                    NewJob = Job(Template.Role, Template.Salary, Template.Prestige,
                                 Template.StressLevel, Template.SkillRequired, Template.Industry)
                    NewJob.Location = Template.Location
                    self.Jobs.append(NewJob)

    # ------------------------------------------------------------------
    # Public API: Add entities
    # ------------------------------------------------------------------
    def AddPerson(self, Person: Person) -> Person:
        Person.YearBorn = self.CurrentYear
        if not Person.Location and self.Locations:
            Person.Location = random.choice(self.Locations)
            Person.Location.AddResident(Person)
        self.People.append(Person)
        return Person

    def AddLocation(self, Location: Location) -> Location:
        self.Locations.append(Location)
        return Location

    def AddJob(self, Job: Job) -> Job:
        self.Jobs.append(Job)
        return Job

    def AddEvent(self, Name: str, Probability: float = 0.05,
                 Description: str = "", Effect: Optional[Callable] = None,
                 IsGlobal: bool = True) -> Event:
        Ev = Event(Name=Name, Probability=Probability,
                   Description=Description, Effect=Effect, IsGlobal=IsGlobal)
        self.Events.append(Ev)
        return Ev

    # ------------------------------------------------------------------
    # Convenience builders
    # ------------------------------------------------------------------
    def CreatePerson(self, Name: str, Age: int = 20,
                     Traits: Optional[dict] = None,
                     Location: Optional[Location] = None) -> Person:
        P = Person(Name=Name, Age=Age, Traits=Traits, Location=Location)
        return self.AddPerson(P)

    def CreateJob(self, Role: str, Salary: float = 50000,
                  Prestige: float = 0.5, StressLevel: float = 0.4,
                  SkillRequired: float = 0.3, Industry: str = "general") -> Job:
        J = Job(Role=Role, Salary=Salary, Prestige=Prestige,
                StressLevel=StressLevel, SkillRequired=SkillRequired, Industry=Industry)
        return self.AddJob(J)

    def CreateLocation(self, Name: str, LocationType: str = "city",
                       OpportunityLevel: float = 0.5,
                       CostOfLiving: float = 0.5,
                       PopulationDensity: float = 0.5) -> Location:
        L = Location(Name=Name, LocationType=LocationType,
                     OpportunityLevel=OpportunityLevel,
                     CostOfLiving=CostOfLiving,
                     PopulationDensity=PopulationDensity)
        return self.AddLocation(L)

    # ------------------------------------------------------------------
    # Population helpers
    # ------------------------------------------------------------------
    def Populate(self, Count: int, AgeRange: tuple = (18, 35)) -> List[Person]:
        """Add Count randomly generated people."""
        FirstNames = [
            "Aarav", "Riya", "Priya", "Arjun", "Sneha", "Rohan", "Ananya",
            "Vikram", "Meera", "Kiran", "Aditya", "Deepa", "Rahul", "Shreya",
            "Akash", "Pooja", "Nikhil", "Kavya", "Sanjay", "Divya",
            "Liam", "Emma", "Noah", "Olivia", "Ethan", "Sophia", "Mason",
            "Isabella", "Lucas", "Mia", "Oliver", "Ava", "James", "Charlotte",
            "Aiden", "Amelia", "Logan", "Harper", "Jack", "Evelyn",
        ]
        Used: List[str] = [P.Name for P in self.People]
        Added = []
        for _ in range(Count):
            Candidates = [N for N in FirstNames if N not in Used]
            if not Candidates:
                Candidates = [f"Person_{len(self.People) + 1}"]
            Name = random.choice(Candidates)
            Used.append(Name)
            Age = random.randint(AgeRange[0], AgeRange[1])
            P = Person(Name=Name, Age=Age)
            self.AddPerson(P)
            Added.append(P)
        return Added

    # ------------------------------------------------------------------
    # Feature toggles
    # ------------------------------------------------------------------
    def EnableEconomy(self):
        self._EconomyEnabled = True

    def EnableRelationships(self):
        self._RelationshipsEnabled = True

    def EnableCulture(self):
        self._CultureEnabled = True

    # ------------------------------------------------------------------
    # Interaction
    # ------------------------------------------------------------------
    def Interact(self, PersonA: Person, PersonB: Person, Context: str = "casual"):
        """Manually trigger an interaction between two people."""
        PersonA._InteractWith(PersonB, Context, self.CurrentYear, self)

    # ------------------------------------------------------------------
    # Policy / scenario testing
    # ------------------------------------------------------------------
    def SetPolicy(self, PolicyName: str, **Kwargs):
        """Apply a named policy to the world."""
        if PolicyName == "universal_basic_income":
            Amount = Kwargs.get("Amount", 1000)
            for P in self.People:
                if P.IsAlive:
                    P.Income = max(P.Income, Amount)
            self.Log.append(f"Policy: Universal Basic Income of ${Amount}/yr applied")
        elif PolicyName == "economic_boom":
            for J in self.Jobs:
                J.Salary *= 1.15
            self.Log.append("Policy: Economic boom — all salaries +15%")
        elif PolicyName == "recession":
            for P in self.People:
                if P.IsAlive and P.Job:
                    if random.random() < 0.2:
                        P.Job.Vacate()
                        P.Job = None
                        P.Income = 0
            self.Log.append("Policy: Recession — 20% unemployment spike")
        else:
            self.Log.append(f"Policy: {PolicyName} applied (custom)")

    # ------------------------------------------------------------------
    # Main simulate loop
    # ------------------------------------------------------------------
    def Simulate(self, Years: int = 10, Verbose: bool = True):
        """Run the simulation for the given number of years."""
        StartYear = self.CurrentYear
        EndYear = StartYear + Years

        for Year in range(StartYear, EndYear):
            self.CurrentYear = Year
            if Verbose:
                print(f"  Simulating year {Year}…", end="\r")

            # Refill job market
            self._RefillJobs()

            # Tick all living people
            for P in list(self.People):  # copy so births mid-loop don't cause issues
                if P.IsAlive:
                    P.Tick(Year, self)

            # Relationship decay for inactive pairs
            if self._RelationshipsEnabled:
                self._ProcessRelationshipDecay()

            # Fire world events
            for Ev in self.Events:
                if Ev.ShouldTrigger():
                    Ev.Fire(self, Year)

            # Annual snapshot
            self.YearHistory[Year] = {
                "AliveCount": sum(1 for P in self.People if P.IsAlive),
                "AverageHappiness": self.Report.AverageHappiness(),
                "AverageIncome": self.Report.AverageIncome(),
                "GiniCoefficient": self.Report.GiniCoefficient(),
            }

        self.CurrentYear = EndYear
        if Verbose:
            print(f"\n  ✓ Simulation complete ({Years} years).")

    def _ProcessRelationshipDecay(self):
        """Decay relationships that weren't interacted with this year."""
        Seen = set()
        for P in self.People:
            if not P.IsAlive:
                continue
            for OtherId, Rel in list(P.Relationships.items()):
                Key = tuple(sorted([P.Id, OtherId]))
                if Key not in Seen:
                    Seen.add(Key)
                    # Only decay non-family, non-partner relationships
                    if not Rel.IsFamily and not Rel.IsRomantic:
                        Rel.Decay(Rate=random.uniform(0.01, 0.04))

    # ------------------------------------------------------------------
    # Monte Carlo
    # ------------------------------------------------------------------
    def RunMonteCarlo(self, Years: int = 10, Runs: int = 10) -> List[dict]:
        """Run the same setup multiple times; returns per-run summaries."""
        OriginalState = pickle.dumps(self)
        Results = []
        for RunIdx in range(Runs):
            ClonedWorld = pickle.loads(OriginalState)
            # Different random seed per run
            random.seed(RunIdx if self.Seed is None else self.Seed + RunIdx)
            ClonedWorld.Simulate(Years=Years, Verbose=False)
            Results.append({
                "Run": RunIdx,
                "AverageHappiness": ClonedWorld.Report.AverageHappiness(),
                "AverageIncome": ClonedWorld.Report.AverageIncome(),
                "GiniCoefficient": ClonedWorld.Report.GiniCoefficient(),
                "PopulationStats": ClonedWorld.Report.PopulationStats(),
            })
        # Restore original state
        Restored = pickle.loads(OriginalState)
        self.__dict__.update(Restored.__dict__)
        return Results

    # ------------------------------------------------------------------
    # Save / Load
    # ------------------------------------------------------------------
    def Save(self, FilePath: str):
        with open(FilePath, "wb") as F:
            pickle.dump(self, F)
        print(f"World saved to {FilePath}")

    @staticmethod
    def Load(FilePath: str) -> "World":
        with open(FilePath, "rb") as F:
            W = pickle.load(F)
        print(f"World loaded from {FilePath}")
        return W

    # ------------------------------------------------------------------
    # Narrative / story engine
    # ------------------------------------------------------------------
    def GetNarrative(self, LastN: int = 20) -> str:
        """Return recent world events as a readable story."""
        Lines = self.Log[-LastN:]
        return "\n".join(Lines)

    def GetPersonStory(self, Target: Person) -> str:
        """Return a person's life story."""
        Lines = [f"📖 The story of {Target.Name}:"]
        for Entry in Target.LifeLog:
            Lines.append(f"  {Entry}")
        if not Target.LifeLog:
            Lines.append("  No notable events yet.")
        return "\n".join(Lines)

    # ------------------------------------------------------------------
    # Visualisation (text-based)
    # ------------------------------------------------------------------
    def PlotHappiness(self):
        """ASCII timeline of average world happiness."""
        if not self.YearHistory:
            print("No history yet. Run Simulate() first.")
            return
        print("\n  Average Happiness Over Time")
        print("  " + "─" * 40)
        for Year, Snap in sorted(self.YearHistory.items()):
            H = Snap["AverageHappiness"]
            Bars = int(H * 30)
            print(f"  {Year:4d} │{'█' * Bars}{' ' * (30 - Bars)}│ {H:.3f}")
        print("  " + "─" * 40)

    def PlotInequality(self):
        """ASCII chart of Gini coefficient over time."""
        if not self.YearHistory:
            print("No history yet. Run Simulate() first.")
            return
        print("\n  Income Inequality (Gini Coefficient)")
        print("  " + "─" * 40)
        for Year, Snap in sorted(self.YearHistory.items()):
            G = Snap["GiniCoefficient"]
            Bars = int(G * 30)
            print(f"  {Year:4d} │{'█' * Bars}{' ' * (30 - Bars)}│ {G:.3f}")
        print("  " + "─" * 40)

    def SocialGraph(self):
        """Print a text summary of the social network."""
        print("\n  Social Network")
        print("  " + "─" * 40)
        for P in self.People:
            if not P.IsAlive:
                continue
            Friends = []
            for OId, Rel in P.Relationships.items():
                if Rel.RelationshipType in ("friend", "close_friend"):
                    Other = self._PersonById(OId)
                    if Other is not None:
                        Friends.append(Other.Name)
            print(f"  {P.Name}: {', '.join(Friends) if Friends else 'no close friends'}")
        print("  " + "─" * 40)

    def _PersonById(self, PersonId: int) -> Optional[Person]:
        for P in self.People:
            if P.Id == PersonId:
                return P
        return None

    # ------------------------------------------------------------------
    # Repr
    # ------------------------------------------------------------------
    def __repr__(self):
        Alive = sum(1 for P in self.People if P.IsAlive)
        return (f"World(year={self.CurrentYear}, people={len(self.People)}, "
                f"alive={Alive}, jobs={len(self.Jobs)}, locations={len(self.Locations)})")

    def __str__(self):
        return f"World (Year {self.CurrentYear}): {sum(1 for P in self.People if P.IsAlive)} people alive, {len(self.Jobs)} jobs."

    def generateReport(self) -> str:
        """Generates and returns a proper string report of the world state."""
        return self.Report.GetFullReportString()
