"""
Social simulation example — people, jobs, goals, relationships, and events.

Demonstrates the full domain model from the original pykworldsim repo
rebuilt on top of the ECS architecture.

Run:
    python examples/social_simulation.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pykworldsim import (
    World, Simulation,
    Person, Location, Relationship, Job, Goal,
    SocialSystem, EventSystem,
)
from pykworldsim.core.components.event import Event
from pykworldsim.core.components.position import Position
from pykworldsim.utils import configure_logging

configure_logging("WARNING")   # quiet for demo; change to INFO to see internals

# ── 1. World setup ─────────────────────────────────────────────────────
world = World(name="earth")
world.register_system(SocialSystem(age_rate=0.05, energy_decay=0.3, happiness_decay=0.05))
world.register_system(EventSystem())

# ── 2. Create city locations ───────────────────────────────────────────
delhi = world.create_entity()
world.add_component(delhi, Location(name="Delhi", x=28.6, y=77.2,
                                    population=20_000_000, city_type="megacity",
                                    amenities=["hospital", "university", "market"]))
world.add_component(delhi, Position(x=28.6, y=77.2))

mumbai = world.create_entity()
world.add_component(mumbai, Location(name="Mumbai", x=19.1, y=72.9,
                                     population=12_000_000, city_type="megacity",
                                     amenities=["port", "hospital", "market"]))
world.add_component(mumbai, Position(x=19.1, y=72.9))

# ── 3. Create people ───────────────────────────────────────────────────
alice = world.create_entity()
world.add_component(alice, Person(name="Alice", age=28.0, happiness=65.0,
                                  energy=90.0, traits=["ambitious", "curious"]))
world.add_component(alice, Job(title="Software Engineer", employer_id=delhi.id,
                               salary=8000.0, satisfaction=75.0, hours=8.0))
world.add_component(alice, Goal(description="Get promoted", priority=9.0,
                                goal_type="economic"))
world.add_component(alice, Position(x=28.6, y=77.2))

bob = world.create_entity()
world.add_component(bob, Person(name="Bob", age=35.0, happiness=50.0,
                                energy=70.0, traits=["relaxed", "creative"]))
world.add_component(bob, Job(title="Artist", employer_id=mumbai.id,
                             salary=3000.0, satisfaction=90.0, hours=6.0))
world.add_component(bob, Goal(description="Finish painting series", priority=7.0,
                              goal_type="personal"))
world.add_component(bob, Position(x=19.1, y=72.9))

carol = world.create_entity()
world.add_component(carol, Person(name="Carol", age=22.0, happiness=80.0,
                                  energy=100.0, traits=["social", "optimistic"]))
world.add_component(carol, Job(title="Student", satisfaction=60.0, hours=5.0))
world.add_component(carol, Goal(description="Graduate with honours", priority=10.0,
                                goal_type="economic"))

# ── 4. Create relationships ────────────────────────────────────────────
alice_bob_rel = world.create_entity()
world.add_component(alice_bob_rel, Relationship(target_id=bob.id, kind="friend",
                                                strength=0.8, interactions=42))

carol_alice_rel = world.create_entity()
world.add_component(carol_alice_rel, Relationship(target_id=alice.id, kind="colleague",
                                                  strength=0.5, interactions=10))

# ── 5. Schedule events ─────────────────────────────────────────────────
birthday_event = world.create_entity()
world.add_component(birthday_event, Event(
    name="Alice's Birthday", event_type="social",
    tick_scheduled=5, participants=[alice.id, bob.id, carol.id],
    payload={"gift": "book"},
))
world.add_component(birthday_event, Person(name="_event_holder"))  # owner entity

promotion_event = world.create_entity()
world.add_component(promotion_event, Event(
    name="Alice Promotion", event_type="economic",
    tick_scheduled=15, participants=[alice.id],
))
world.add_component(promotion_event, Person(name="_event_holder"))

# ── 6. Run simulation ──────────────────────────────────────────────────
sim = Simulation(world, seed=2024)

print(f"\n{'═'*60}")
print(f"  🌍  {world.name.upper()} — Social Simulation")
print(f"{'═'*60}")
print(f"  People : Alice, Bob, Carol")
print(f"  Cities : Delhi, Mumbai")
print(f"  Events : Birthday (tick 5), Promotion (tick 15)")
print(f"{'─'*60}")

# Snapshot starting state
alice_person = world.get_component(alice, Person)
bob_person   = world.get_component(bob,   Person)
carol_person = world.get_component(carol, Person)

print(f"\n  BEFORE (tick 0):")
for name, p in [("Alice", alice_person), ("Bob", bob_person), ("Carol", carol_person)]:
    print(f"    {name:6s} → age={p.age:.1f}  happiness={p.happiness:.1f}  energy={p.energy:.1f}")

sim.run(steps=20, dt=1.0)

print(f"\n  AFTER (tick {sim.tick}):")
for name, p in [("Alice", alice_person), ("Bob", bob_person), ("Carol", carol_person)]:
    print(f"    {name:6s} → age={p.age:.1f}  happiness={p.happiness:.1f}  energy={p.energy:.1f}")

# Goal completion
alice_goal = world.get_component(alice, Goal)
bob_goal   = world.get_component(bob,   Goal)
carol_goal = world.get_component(carol, Goal)
print(f"\n  GOALS:")
for name, g in [("Alice", alice_goal), ("Bob", bob_goal), ("Carol", carol_goal)]:
    status = "✓ DONE" if g.completed else f"{g.progress:.1f}%"
    print(f"    {name:6s} → '{g.description}'  [{status}]")

# Generate report
print(f"\n{'─'*60}")
report = world.generate_report()
print(f"  World report: {report['entity_count']} entities, "
      f"component types: {report['component_types']}")
print(f"{'═'*60}\n")
