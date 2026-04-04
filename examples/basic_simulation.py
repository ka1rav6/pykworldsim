"""
Basic simulation example — physics entities with position and velocity.

Run:
    python examples/basic_simulation.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pykworldsim import World, Simulation, Position, Velocity, MovementSystem
from pykworldsim.core.systems.physics import PhysicsSystem
from pykworldsim.utils import configure_logging

configure_logging("INFO")

# ── 1. Create world ────────────────────────────────────────────────────
world = World(name="physics-demo")

# ── 2. Register systems (order matters: physics first, then movement) ──
world.register_system(PhysicsSystem(gravity=9.81, bounds=(0, 0, 100, 100), restitution=0.8))
world.register_system(MovementSystem())

# ── 3. Spawn entities ──────────────────────────────────────────────────
spawn_data = [
    ("Ball-A",  10.0,  5.0,  3.0,  0.0),
    ("Ball-B",  50.0,  0.0,  0.5,  2.0),
    ("Ball-C",  80.0, 90.0, -1.5,  0.3),
]

entities = {}
for name, x, y, dx, dy in spawn_data:
    e = world.create_entity()
    world.add_component(e, Position(x=x, y=y))
    world.add_component(e, Velocity(dx=dx, dy=dy))
    entities[e] = name

print(f"\n{'─'*55}")
print(f"  World: '{world.name}'  |  Entities: {len(entities)}")
print(f"{'─'*55}")

# ── 4. Run with a per-tick callback ────────────────────────────────────
sim = Simulation(world, seed=42)

@sim.on_step
def log_progress(s: Simulation) -> None:
    if s.tick % 10 == 0:
        print(f"  Tick {s.tick:>4d}  elapsed={s.elapsed:.2f}s")

sim.run(steps=50, dt=0.1)

# ── 5. Print final state ───────────────────────────────────────────────
print(f"\n{'─'*55}")
print("  Final entity states:")
print(f"{'─'*55}")
for e, name in entities.items():
    pos = world.get_component(e, Position)
    vel = world.get_component(e, Velocity)
    print(f"  [{name}]  pos=({pos.x:7.3f}, {pos.y:7.3f})  "
          f"vel=({vel.dx:6.3f}, {vel.dy:6.3f})")

# ── 6. Save and reload ─────────────────────────────────────────────────
save_path = "/tmp/basic_world.json"
world.save(save_path)
restored = World.load(save_path)
print(f"\n  Saved → '{save_path}'")
print(f"  Restored world '{restored.name}' with {len(restored.entities)} entities ✓")
print(f"{'─'*55}\n")
