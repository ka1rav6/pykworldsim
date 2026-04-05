"""
Basic physics simulation — v3 ECS.

Run: python examples/basic_simulation.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pykworldsim import World, Simulation, Position, Velocity, MovementSystem
from pykworldsim.core.systems.physics import PhysicsSystem
from pykworldsim.utils import configure_logging

configure_logging("WARNING")

world = World(name="physics-demo")
world.register_system(PhysicsSystem(gravity=9.81, bounds=(0, 0, 100, 100), restitution=0.8))
world.register_system(MovementSystem())

# Subscribe to entity lifecycle events
world.events.subscribe("entity_created", lambda d: None)

spawn = [("Ball-A", 10.0, 5.0, 3.0, 0.0), ("Ball-B", 50.0, 0.0, 0.5, 2.0), ("Ball-C", 80.0, 90.0, -1.5, 0.3)]
entities = {}
for name, x, y, dx, dy in spawn:
    e = world.create_entity()
    world.add_component(e, Position(x=x, y=y))
    world.add_component(e, Velocity(dx=dx, dy=dy))
    entities[e] = name

print(f"\n{'─'*55}\n  World: '{world.name}' | Entities: {len(entities)}\n{'─'*55}")

sim = Simulation(world, seed=42)

@sim.on_step
def progress(s):
    if s.tick % 10 == 0:
        print(f"  Tick {s.tick:>4d} | elapsed={s.elapsed:.2f}s")

# Take a snapshot at tick 0 for demo
sim.take_snapshot("start")
sim.run(steps=50, dt=0.1)
print(f"\n{'─'*55}\n  Final states:\n{'─'*55}")
for e, name in entities.items():
    pos = world.get_component(e, Position)
    vel = world.get_component(e, Velocity)
    print(f"  [{name}] pos=({pos.x:7.3f},{pos.y:7.3f}) vel=({vel.dx:6.3f},{vel.dy:6.3f})")

world.save("/tmp/v3_world.json")
restored = World.load("/tmp/v3_world.json")
print(f"\n  Saved & restored '{restored.name}' ({len(restored.entities)} entities) ✓")
print(f"  Snapshots: {sim.list_snapshots()}\n{'─'*55}\n")
