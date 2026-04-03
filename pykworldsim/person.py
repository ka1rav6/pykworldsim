import random
import math
from typing import Dict, List, Optional, Any
from .goal import Goal
from .relationship import Relationship


class Person:
    """
    A simulated person with traits, goals, internal state, and social connections.
    All variable names use PascalCase.
    """

    _IdCounter = 0

    # Default trait distributions if not specified
    _DefaultTraitRanges: Dict[str, tuple] = {
        "Openness":          (0.2, 0.9),
        "Conscientiousness": (0.2, 0.9),
        "Extraversion":      (0.1, 0.9),
        "Agreeableness":     (0.2, 0.9),
        "Neuroticism":       (0.1, 0.8),
        "Ambition":          (0.1, 0.9),
        "Intelligence":      (0.2, 0.9),
        "SocialSkill":       (0.2, 0.9),
        "Creativity":        (0.1, 0.9),
        "RiskTolerance":     (0.1, 0.9),
        "Discipline":        (0.1, 0.9),
    }

    def __init__(self, Name: str, Age: int = 20,
                 Traits: Optional[Dict[str, float]] = None,
                 Location: Optional[Any] = None):
        Person._IdCounter += 1
        self.Id = Person._IdCounter
        self.Name = Name
        self.Age = Age
        self.Location = Location
        self.IsAlive = True

        # --- Traits (static-ish personality) ---
        self.Traits: Dict[str, float] = {}
        for TraitName, (Lo, Hi) in self._DefaultTraitRanges.items():
            self.Traits[TraitName] = round(random.uniform(Lo, Hi), 3)
        if Traits:
            for K, V in Traits.items():
                NormKey = self._NormalizeTraitKey(K)
                self.Traits[NormKey] = max(0.0, min(1.0, float(V)))

        # --- Internal state (dynamic) ---
        self.Mood = random.uniform(0.4, 0.7)
        self.Energy = random.uniform(0.5, 0.9)
        self.Stress = random.uniform(0.1, 0.4)
        self.Motivation = random.uniform(0.4, 0.8)
        self.LifeSatisfaction = random.uniform(0.3, 0.7)

        # --- Life metrics ---
        self.Income = 0.0
        self.Savings = 0.0
        self.Status = random.uniform(0.1, 0.4)
        self.Education = random.uniform(0.1, 0.4)
        self.SkillLevel = random.uniform(0.1, 0.4)
        self.HasDegree = False

        # --- Social ---
        self.Relationships: Dict[int, Relationship] = {}  # Other person's Id → Relationship
        self.RomanticPartner: Optional["Person"] = None
        self.Children: List["Person"] = []
        self.Parents: List["Person"] = []

        # --- Goals ---
        self.Goals: List[Goal] = []
        self._GenerateInitialGoals()

        # --- Career ---
        self.Job: Optional[Any] = None
        self.YearsAtCurrentJob: int = 0
        self.CareerHistory: List[str] = []

        # --- Life log ---
        self.LifeLog: List[str] = []

        # --- Tracking ---
        self.HappinessHistory: List[float] = []
        self.IncomeHistory: List[float] = []
        self.YearBorn: int = 0  # Set by World

    # ------------------------------------------------------------------
    # Trait normalization
    # ------------------------------------------------------------------
    def _NormalizeTraitKey(self, Key: str) -> str:
        """Normalise user-supplied trait keys to PascalCase canonical names."""
        Mapping = {
            "openness": "Openness",
            "conscientiousness": "Conscientiousness",
            "extraversion": "Extraversion",
            "agreeableness": "Agreeableness",
            "neuroticism": "Neuroticism",
            "ambition": "Ambition",
            "intelligence": "Intelligence",
            "socialskill": "SocialSkill",
            "social": "SocialSkill",
            "creativity": "Creativity",
            "risktolerance": "RiskTolerance",
            "risk": "RiskTolerance",
            "discipline": "Discipline",
        }
        return Mapping.get(Key.lower().replace("_", ""), Key)

    # ------------------------------------------------------------------
    # Goals
    # ------------------------------------------------------------------
    def _GenerateInitialGoals(self):
        Ambition = self.Traits.get("Ambition", 0.5)
        Social = self.Traits.get("SocialSkill", 0.5)
        if Ambition > 0.6:
            self.Goals.append(Goal("GetJob", Priority=0.9))
            self.Goals.append(Goal("GetPromotion", Priority=0.7))
            self.Goals.append(Goal("EarnMoney", Priority=0.7))
        else:
            self.Goals.append(Goal("GetJob", Priority=0.6))
        if Social > 0.5:
            self.Goals.append(Goal("MakeFriends", Priority=0.7))
        if self.Traits.get("Openness", 0.5) > 0.6:
            self.Goals.append(Goal("ImproveSkills", Priority=0.5))
        self.Goals.append(Goal("FindPartner", Priority=round(random.uniform(0.3, 0.8), 2)))

    def AddGoal(self, GoalType: str, Priority: float = 0.5):
        self.Goals.append(Goal(GoalType, Priority))

    # ------------------------------------------------------------------
    # Core simulation tick
    # ------------------------------------------------------------------
    def Tick(self, Year: int, World: Any):
        if not self.IsAlive:
            return
        self.Age += 1
        self._UpdateInternalState()
        self._MakeDecisions(Year, World)
        self._UpdateGoals(Year)
        self._CheckMortality(Year, World)
        self.HappinessHistory.append(round(self.LifeSatisfaction, 3))
        self.IncomeHistory.append(round(self.Income, 2))

    # ------------------------------------------------------------------
    # Internal state update
    # ------------------------------------------------------------------
    def _UpdateInternalState(self):
        Neuroticism = self.Traits.get("Neuroticism", 0.4)
        Extraversion = self.Traits.get("Extraversion", 0.5)
        FriendCount = self._CountRelationshipsByType(["friend", "close_friend", "partner"])

        # Mood fluctuates; neuroticism increases variance
        MoodShift = random.gauss(0, 0.08 * (0.5 + Neuroticism))
        self.Mood = max(0.0, min(1.0, self.Mood + MoodShift))

        # Stress from job and lack of money
        JobStress = self.Job.StressLevel if self.Job else 0.1
        FinancialStress = max(0.0, 0.5 - min(1.0, self.Savings / 20000)) * 0.3
        self.Stress = max(0.0, min(1.0, JobStress * 0.6 + FinancialStress + random.uniform(-0.05, 0.05)))

        # Energy: discipline and sleep patterns
        Discipline = self.Traits.get("Discipline", 0.5)
        self.Energy = max(0.1, min(1.0, Discipline * 0.5 + random.uniform(0.1, 0.4)))

        # Motivation: goal progress and mood
        ActiveGoals = [G for G in self.Goals if not G.Achieved]
        GoalFactor = 0.5 if not ActiveGoals else min(1.0, sum(G.Priority for G in ActiveGoals) / len(ActiveGoals))
        self.Motivation = max(0.1, min(1.0, GoalFactor * 0.6 + self.Mood * 0.4))

        # Life satisfaction: multi-factor
        SocialFactor = min(1.0, FriendCount / 5.0) * Extraversion
        CareerFactor = (self.Job.Prestige if self.Job else 0.0) * self.Traits.get("Ambition", 0.5)
        FinanceFactor = min(1.0, self.Savings / 50000) * 0.3
        PartnerFactor = 0.15 if self.RomanticPartner else 0.0
        BaseSatisfaction = (SocialFactor * 0.3 + CareerFactor * 0.25 +
                            FinanceFactor + self.Mood * 0.2 + PartnerFactor)
        self.LifeSatisfaction = max(0.0, min(1.0,
            self.LifeSatisfaction * 0.7 + BaseSatisfaction * 0.3))

        # Savings accumulate from income minus cost of living
        if self.Income > 0:
            LivingCost = (self.Location.CostOfLiving * 30000 if self.Location else 20000)
            AnnualSavings = max(0, self.Income - LivingCost) * random.uniform(0.2, 0.6)
            self.Savings += AnnualSavings

    # ------------------------------------------------------------------
    # Decision engine
    # ------------------------------------------------------------------
    def _MakeDecisions(self, Year: int, World: Any):
        # Prioritise highest-priority unachieved goal
        ActiveGoals = sorted([G for G in self.Goals if not G.Achieved],
                             key=lambda G: G.Priority, reverse=True)
        if not ActiveGoals:
            return

        TopGoal = ActiveGoals[0]

        if TopGoal.GoalType == "GetJob" and self.Job is None:
            self._SeekJob(Year, World)
        elif TopGoal.GoalType == "GetPromotion" and self.Job is not None:
            self._SeekPromotion(Year, World)
        elif TopGoal.GoalType == "MakeFriends":
            self._Socialize(Year, World)
        elif TopGoal.GoalType == "FindPartner" and self.RomanticPartner is None:
            self._SeekPartner(Year, World)
        elif TopGoal.GoalType == "EarnMoney":
            self._OptimiseCareer(Year, World)
        elif TopGoal.GoalType == "ImproveSkills":
            self._ImproveSkills(Year, World)
        elif TopGoal.GoalType == "MoveCity":
            self._ConsiderMoving(Year, World)

        # Always do a little socialising
        if random.random() < self.Traits.get("Extraversion", 0.5):
            self._Socialize(Year, World, Intensity="light")

    def _SeekJob(self, Year: int, World: Any):
        AvailableJobs = [J for J in World.Jobs if J.IsAvailable() and
                         J.SkillRequired <= self.SkillLevel + 0.2 and 
                         (J.Location is None or self.Location is None or J.Location == self.Location)]
        if not AvailableJobs:
            return
        # Pick best paying job within skill reach
        BestJob = max(AvailableJobs, key=lambda J: J.Salary * (1 + self.Traits.get("Ambition", 0.5)))
        Chance = 0.3 + self.SkillLevel * 0.4 + self.Traits.get("Intelligence", 0.5) * 0.2
        if random.random() < Chance:
            BestJob.Assign(self)
            self.Job = BestJob
            self.Income = BestJob.Salary
            self.YearsAtCurrentJob = 0
            self.CareerHistory.append(f"Year {Year}: Got job as {BestJob.Role} (${BestJob.Salary:,.0f})")
            self.LifeLog.append(f"Year {Year}: Started working as a {BestJob.Role}")
            World.Log.append(f"{self.Name} got a job as {BestJob.Role}")

    def _SeekPromotion(self, Year: int, World: Any):
        if not self.Job or self.YearsAtCurrentJob < 2:
            return
        PromotionChance = (self.Traits.get("Ambition", 0.5) * 0.3 +
                           self.SkillLevel * 0.3 +
                           self.Traits.get("Conscientiousness", 0.5) * 0.2 +
                           random.uniform(0, 0.2))
        if random.random() < PromotionChance * 0.4:
            Raise = self.Income * random.uniform(0.10, 0.25)
            self.Income += Raise
            self.Job.Salary += Raise
            self.Status = min(1.0, self.Status + 0.05)
            self.LifeLog.append(f"Year {Year}: Got promoted! Now earning ${self.Income:,.0f}")
            World.Log.append(f"{self.Name} received a promotion (now ${self.Income:,.0f}/yr)")
        self.YearsAtCurrentJob += 1

    def _Socialize(self, Year: int, World: Any, Intensity: str = "normal"):
        Candidates = [P for P in World.People
                      if P.Id != self.Id and P.IsAlive and
                      (P.Location == self.Location or random.random() < 0.1)]
        if not Candidates:
            return
        NumMeet = 1 if Intensity == "light" else random.randint(1, 3)
        for _ in range(NumMeet):
            if not Candidates:
                break
            Other = random.choice(Candidates)
            Candidates.remove(Other)
            Context = random.choice(["casual", "party", "work", "support"])
            self._InteractWith(Other, Context, Year, World)

    def _InteractWith(self, Other: "Person", Context: str, Year: int, World: Any):
        # Get or create relationship
        if Other.Id not in self.Relationships:
            Rel = Relationship(self, Other)
            Rel.YearMet = Year
            Rel.RecordEvent(Year, "met", f"{self.Name} met {Other.Name}")
            self.Relationships[Other.Id] = Rel
            Other.Relationships[self.Id] = Rel
            World.Log.append(f"{self.Name} met {Other.Name}")

        Rel = self.Relationships[Other.Id]
        Rel.Interact(Context=Context, Year=Year)

        # Romantic spark: if both single and good chemistry
        if (self.RomanticPartner is None and Other.RomanticPartner is None and
                Rel.Strength > 0.5 and Rel.Trust > 0.4 and
                random.random() < 0.08 * self.Traits.get("Extraversion", 0.5)):
            self._StartRomance(Other, Year, World)

    def _StartRomance(self, Other: "Person", Year: int, World: Any):
        self.RomanticPartner = Other
        Other.RomanticPartner = self
        Rel = self.Relationships[Other.Id]
        Rel.IsRomantic = True
        Rel.Attraction = min(1.0, Rel.Attraction + random.uniform(0.3, 0.5))
        Rel.UpdateType()
        self.LifeLog.append(f"Year {Year}: Started a romantic relationship with {Other.Name}")
        World.Log.append(f"{self.Name} and {Other.Name} started a romantic relationship ❤️")

        # Maybe start a family
        if (random.random() < 0.25 and self.Age < 40 and Other.Age < 40 and
                self.Savings > 5000 and Other.Savings > 5000):
            self._HaveChild(Other, Year, World)

    def _HaveChild(self, Partner: "Person", Year: int, World: Any):
        ChildName = f"Child_of_{self.Name}"
        # Inherit blended traits
        BlendedTraits = {}
        for Trait in self.Traits:
            MyVal = self.Traits.get(Trait, 0.5)
            PartnerVal = Partner.Traits.get(Trait, 0.5)
            # Weighted blend with small mutation
            Inherited = (MyVal + PartnerVal) / 2 + random.gauss(0, 0.08)
            BlendedTraits[Trait] = max(0.0, min(1.0, Inherited))

        Child = Person(Name=ChildName, Age=0, Traits=BlendedTraits, Location=self.Location)
        Child.YearBorn = Year
        Child.Parents = [self, Partner]
        self.Children.append(Child)
        Partner.Children.append(Child)
        World.AddPerson(Child)
        self.LifeLog.append(f"Year {Year}: Had a child with {Partner.Name}")
        World.Log.append(f"{self.Name} and {Partner.Name} welcomed a child 👶")

    def _SeekPartner(self, Year: int, World: Any):
        # Delegate to socialise — romance emerges from interactions
        self._Socialize(Year, World)

    def _OptimiseCareer(self, Year: int, World: Any):
        if self.Job is None:
            self._SeekJob(Year, World)
        else:
            # Look for better-paying job
            BetterJobs = [J for J in World.Jobs if J.IsAvailable() and
                          J.Salary > self.Income * 1.15 and
                          J.SkillRequired <= self.SkillLevel + 0.1]
            if BetterJobs and random.random() < 0.3 * self.Traits.get("RiskTolerance", 0.5):
                self.Job.Vacate()
                NewJob = max(BetterJobs, key=lambda J: J.Salary)
                NewJob.Assign(self)
                self.Job = NewJob
                self.Income = NewJob.Salary
                self.YearsAtCurrentJob = 0
                World.Log.append(f"{self.Name} switched to a better-paying job as {NewJob.Role}")

    def _ImproveSkills(self, Year: int, World: Any):
        GainRate = self.Traits.get("Openness", 0.5) * 0.05 + self.Traits.get("Discipline", 0.5) * 0.05
        self.SkillLevel = min(1.0, self.SkillLevel + GainRate + random.uniform(0, 0.03))
        if not self.HasDegree and self.Age < 28 and random.random() < 0.2:
            self.HasDegree = True
            self.Education = min(1.0, self.Education + 0.3)
            self.LifeLog.append(f"Year {Year}: Earned a university degree")
            World.Log.append(f"{self.Name} earned a degree 🎓")

    def _ConsiderMoving(self, Year: int, World: Any):
        if not World.Locations or random.random() > self.Traits.get("RiskTolerance", 0.5) * 0.3:
            return
        BetterLocations = [L for L in World.Locations
                           if L != self.Location and L.OpportunityLevel > (self.Location.OpportunityLevel if self.Location else 0.5)]
        if BetterLocations:
            NewLoc = random.choice(BetterLocations)
            if self.Location:
                self.Location.RemoveResident(self)
            self.Location = NewLoc
            NewLoc.AddResident(self)
            self.LifeLog.append(f"Year {Year}: Moved to {NewLoc.Name}")
            World.Log.append(f"{self.Name} moved to {NewLoc.Name}")

    # ------------------------------------------------------------------
    # Goal updates
    # ------------------------------------------------------------------
    def _UpdateGoals(self, Year: int):
        for Goal in self.Goals:
            if Goal.Achieved:
                continue
            if Goal.GoalType == "GetJob":
                Delta = 0.5 if self.Job else random.uniform(-0.02, 0.05)
            elif Goal.GoalType == "GetPromotion":
                Delta = 0.1 if (self.Job and self.YearsAtCurrentJob >= 2) else 0.0
            elif Goal.GoalType == "MakeFriends":
                FriendCount = self._CountRelationshipsByType(["friend", "close_friend"])
                Delta = min(0.1, FriendCount * 0.05)
            elif Goal.GoalType == "FindPartner":
                Delta = 0.5 if self.RomanticPartner else 0.0
            elif Goal.GoalType == "EarnMoney":
                Delta = min(0.1, self.Income / 200000)
            elif Goal.GoalType == "ImproveSkills":
                Delta = self.SkillLevel * 0.1
            elif Goal.GoalType == "StartFamily":
                Delta = 0.5 if self.Children else 0.0
            else:
                Delta = random.uniform(0, 0.03)

            Achieved = Goal.UpdateProgress(Delta)
            if Achieved:
                Goal.YearAchieved = Year
                self.LifeLog.append(f"Year {Year}: Achieved goal — {Goal.GoalType}!")
                self.LifeSatisfaction = min(1.0, self.LifeSatisfaction + 0.1)
                # Create a new stretch goal
                self._AddStretchGoal(Goal.GoalType)

    def _AddStretchGoal(self, AchievedGoalType: str):
        StretchMap = {
            "GetJob": "GetPromotion",
            "GetPromotion": "EarnMoney",
            "MakeFriends": "SocializeMore",
            "FindPartner": "StartFamily",
            "ImproveSkills": "BuildBusiness",
            "EarnMoney": "IncreaseStatus",
        }
        NextGoal = StretchMap.get(AchievedGoalType)
        if NextGoal and not any(G.GoalType == NextGoal for G in self.Goals):
            self.Goals.append(Goal(NextGoal, Priority=0.7))

    # ------------------------------------------------------------------
    # Mortality
    # ------------------------------------------------------------------
    def _CheckMortality(self, Year: int, World: Any):
        if self.Age < 40:
            BaseDeathChance = 0.002
        elif self.Age < 60:
            BaseDeathChance = 0.005
        elif self.Age < 80:
            BaseDeathChance = 0.02
        else:
            BaseDeathChance = 0.08

        StressModifier = self.Stress * 0.005
        if random.random() < BaseDeathChance + StressModifier:
            self.IsAlive = False
            self.LifeLog.append(f"Year {Year}: Died at age {self.Age}")
            World.Log.append(f"💀 {self.Name} passed away at age {self.Age}")
            if self.Job:
                self.Job.Vacate()
                self.Job = None
            if self.RomanticPartner:
                self.RomanticPartner.RomanticPartner = None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _CountRelationshipsByType(self, Types: list) -> int:
        return sum(1 for Rel in self.Relationships.values() if Rel.RelationshipType in Types)

    def GetRelationship(self, Other: "Person") -> "Relationship | None":
        return self.Relationships.get(Other.Id)

    def Summary(self) -> dict:
        return {
            "Name": self.Name,
            "Age": self.Age,
            "Alive": self.IsAlive,
            "Job": self.Job.Role if self.Job else "Unemployed",
            "Income": round(self.Income, 2),
            "Savings": round(self.Savings, 2),
            "LifeSatisfaction": round(self.LifeSatisfaction, 3),
            "Friends": self._CountRelationshipsByType(["friend", "close_friend"]),
            "Partner": self.RomanticPartner.Name if self.RomanticPartner else None,
            "Children": len(self.Children),
            "GoalsAchieved": sum(1 for G in self.Goals if G.Achieved),
        }

    def __repr__(self):
        Status = f"{'alive' if self.IsAlive else 'deceased'}, age={self.Age}"
        Job = self.Job.Role if self.Job else "unemployed"
        return f"Person({self.Name}, {Status}, job={Job}, happiness={self.LifeSatisfaction:.2f})"

    def __str__(self):
        Status = f"{'Alive' if self.IsAlive else 'Deceased'}, Age {self.Age}"
        JobStr = f", Job: {self.Job.Role}" if self.Job else ", Unemployed"
        PartnerStr = f", Partner: {self.RomanticPartner.Name}" if self.RomanticPartner else ""
        return f"{self.Name} ({Status}{JobStr}{PartnerStr})"
