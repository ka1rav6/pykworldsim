"""
Social simulation — people, jobs, goals, events, EventBus.

Run: python examples/social_simulation.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pykworldsim import (World, Simulation, Person, Location, Job, Goal,
                          Relationship, EventComponent, SocialSystem, EventSystem, Position)
from pykworldsim.utils import configure_logging

configure_logging("WARNING")

world = World(name="earth")
world.register_system(SocialSystem(age_rate=0.05, energy_decay=0.3, happiness_decay=0.05))
world.register_system(EventSystem())

# Subscribe to goal completion via EventBus
completed_goals = []
world.events.subscribe("goal_completed", lambda d: completed_goals.append(d["description"]))

# Locations
delhi = world.create_entity()
world.add_component(delhi, Location(name="Delhi", population=20_000_000, city_type="megacity"))
world.add_component(delhi, Position(x=28.6, y=77.2))

# People
alice = world.create_entity()
world.add_component(alice, Person(name="Alice", age=28.0, happiness=65.0, energy=90.0, traits=["ambitious"]))
world.add_component(alice, Job(title="Engineer", salary=8000.0, satisfaction=75.0))
world.add_component(alice, Goal(description="Get promoted", priority=9.0, goal_type="economic"))

bob = world.create_entity()
world.add_component(bob, Person(name="Bob", age=35.0, happiness=50.0, energy=70.0))
world.add_component(bob, Job(title="Artist", salary=3000.0, satisfaction=90.0))
world.add_component(bob, Goal(description="Finish painting", priority=7.0))

carol = world.create_entity()
world.add_component(carol, Person(name="Carol", age=22.0, happiness=80.0, energy=100.0))
world.add_component(carol, Goal(description="Graduate", priority=10.0))

# Relationships
rel_e = world.create_entity()
world.add_component(rel_e, Relationship(target_id=bob.id, kind="friend", strength=0.8))

# Scheduled events
ev1 = world.create_entity()
world.add_component(ev1, Person(name="_holder"))
world.add_component(ev1, EventComponent(name="Birthday", event_type="social", tick_scheduled=5, participants=[alice.id]))

ev2 = world.create_entity()
world.add_component(ev2, Person(name="_holder"))
world.add_component(ev2, EventComponent(name="Promotion", event_type="economic", tick_scheduled=15, participants=[alice.id]))

alice_p = world.get_component(alice, Person)
bob_p   = world.get_component(bob,   Person)
carol_p = world.get_component(carol, Person)

print(f"\n{'═'*60}\n  🌍 EARTH — Social Simulation (pykworldsim v3)\n{'═'*60}")
print(f"  BEFORE:\n    Alice  → age={alice_p.age:.1f}  happiness={alice_p.happiness:.1f}  energy={alice_p.energy:.1f}")
print(f"    Bob    → age={bob_p.age:.1f}  happiness={bob_p.happiness:.1f}  energy={bob_p.energy:.1f}")
print(f"    Carol  → age={carol_p.age:.1f}  happiness={carol_p.happiness:.1f}  energy={carol_p.energy:.1f}")

sim = Simulation(world, seed=2024)
sim.run(steps=20, dt=1.0)

print(f"  AFTER (tick {sim.tick}):")
print(f"    Alice  → age={alice_p.age:.1f}  happiness={alice_p.happiness:.1f}  energy={alice_p.energy:.1f}")
print(f"    Bob    → age={bob_p.age:.1f}  happiness={bob_p.happiness:.1f}  energy={bob_p.energy:.1f}")
print(f"    Carol  → age={carol_p.age:.1f}  happiness={carol_p.happiness:.1f}  energy={carol_p.energy:.1f}")

print(f"\n  GOALS:")
for name, e in [("Alice", alice), ("Bob", bob), ("Carol", carol)]:
    g = world.get_component(e, Goal)
    status = "✓ DONE" if g.completed else f"{g.progress:.1f}%"
    print(f"    {name:6s} → '{g.description}'  [{status}]")

if completed_goals:
    print(f"\n  Completed via EventBus: {completed_goals}")

report = world.generate_report()
print(f"\n  Report: {report['entity_count']} entities, types: {report['component_types']}")
print(f"{'═'*60}\n")
