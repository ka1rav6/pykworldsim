"""
Plugin system example — register a custom system at runtime.

Run:
    python examples/plugin_example.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pykworldsim import World, Simulation, Position, Velocity, MovementSystem
from pykworldsim.core.systems.base_system import BaseSystem
from pykworldsim.plugins import PluginRegistry
from pykworldsim.utils import configure_logging

configure_logging("INFO")


# ── Define a custom system ─────────────────────────────────────────────
class BoundaryWrapSystem(BaseSystem):
    """Wraps entity positions toroidally within a rectangular boundary."""

    def __init__(self, width: float = 100.0, height: float = 100.0) -> None:
        super().__init__()
        self.width = width
        self.height = height

    def update(self, dt: float) -> None:
        for entity, (pos,) in self.world.get_components(Position):
            pos.x %= self.width
            pos.y %= self.height


# ── Register the plugin ────────────────────────────────────────────────
PluginRegistry.register("BoundaryWrapSystem", BoundaryWrapSystem)
print(f"Registered plugins: {PluginRegistry.list_names()}")

# ── Build world and use the plugin ────────────────────────────────────
world = World(name="toroidal-world")
world.register_system(MovementSystem())
world.register_system(BoundaryWrapSystem(width=50.0, height=50.0))

e = world.create_entity()
world.add_component(e, Position(x=45.0, y=45.0))
world.add_component(e, Velocity(dx=10.0, dy=10.0))

print(f"\nStarting position: ({world.get_component(e, Position).x}, "
      f"{world.get_component(e, Position).y})")

sim = Simulation(world, seed=0)
sim.run(steps=5, dt=1.0)

pos = world.get_component(e, Position)
print(f"After 5 steps:     ({pos.x:.3f}, {pos.y:.3f})  [wrapped toroidally]")
print("\nPlugin example complete ✓")
