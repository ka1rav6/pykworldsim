# WorldSim

A Python library for simulating people, relationships, societies, and time.
All variables use PascalCase throughout.

## Installation

```python
# Place the worldsim/ folder in your project, then:
from worldsim import World, Person, Goal
```

## Quick Start

```python
from worldsim import World

World1 = World(Seed=42)

# Add named people with specific traits
Aarav = World1.CreatePerson("Aarav", Age=22, Traits={
    "Ambition": 0.9, "Intelligence": 0.8
})
Riya = World1.CreatePerson("Riya", Age=24, Traits={
    "SocialSkill": 0.9, "Extraversion": 0.85
})

# Fill with random people
World1.Populate(20, AgeRange=(18, 35))

# Run simulation
World1.Simulate(Years=20)

# Reports
World1.Report.PrintSummary()
World1.PlotHappiness()
World1.PlotInequality()
print(World1.GetPersonStory(Aarav))
```

## Traits (all PascalCase)
Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism,
Ambition, Intelligence, SocialSkill, Creativity, RiskTolerance, Discipline

## Goal Types
GetJob, GetPromotion, MakeFriends, FindPartner, ImproveSkills,
EarnMoney, IncreaseStatus, MoveCity, StartFamily, BuildBusiness,
SocializeMore, FindPurpose

## API Reference

```python
# World
World1 = World(Seed=42)
World1.CreatePerson(Name, Age, Traits={})
World1.CreateJob(Role, Salary, Prestige, StressLevel, SkillRequired, Industry)
World1.CreateLocation(Name, LocationType, OpportunityLevel, CostOfLiving, PopulationDensity)
World1.Populate(Count, AgeRange=(18, 35))
World1.AddEvent(Name, Probability, Description, Effect, IsGlobal)
World1.Simulate(Years=10, Verbose=True)
World1.SetPolicy("universal_basic_income", Amount=15000)
World1.SetPolicy("economic_boom")
World1.SetPolicy("recession")
World1.Interact(PersonA, PersonB, Context="party")
World1.RunMonteCarlo(Years=10, Runs=20)
World1.Save("world.pkl")
World1.Load("world.pkl")
World1.GetNarrative(LastN=30)
World1.GetPersonStory(Person)
World1.PlotHappiness()
World1.PlotInequality()
World1.SocialGraph()

# Report
World1.Report.PrintSummary()
World1.Report.TopHappiest(N=5)
World1.Report.MostConnected(N=5)
World1.Report.Wealthiest(N=5)
World1.Report.Unemployed()
World1.Report.AverageHappiness()
World1.Report.AverageIncome()
World1.Report.GiniCoefficient()
World1.Report.PopulationStats()
```
