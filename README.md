# 🌍 pykworldsim v3

> **Production-grade ECS world simulation framework.**  
> Simulate people, cities, relationships, jobs, goals, and events with a clean, fast, fully-tested Entity-Component-System engine.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![Version](https://img.shields.io/badge/version-3.0.0-purple.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-pytest-orange.svg)](tests/)

---

## ✨ What's new in v3

| Feature | Detail |
|---|---|
| ⚡ **Inverted-index QueryEngine** | O(smallest-set) lookups — no full entity scans |
| 🔒 **Staged mutation queues** | `stage_add_component` / `destroy_entity` safe during iteration |
| 🎲 **Injected RNG** | `sim.rng = random.Random(seed)` — fully deterministic |
| 📡 **EventBus** | `emit()` / `subscribe()` — systems talk via events, not direct calls |
| 🔃 **System priority ordering** | `system.priority` — lower runs first, sorted automatically |
| 🪝 **Lifecycle hooks** | `on_add` / `on_remove` via `EntityRegistry` + EventBus |
| 📸 **Snapshot / Replay** | `sim.take_snapshot("label")` / `sim.restore_snapshot("label")` |
| 🔌 **Plugin registry** | Register custom systems by class or dotted import path |
| ⚙️ **Config: world.size + count** | `count: N` spawns N identical entities; `world.size` wired |
| 🖥️ **CLI overrides** | `--steps --dt --seed --debug` override config file values |

---

## 📦 Installation

```bash
# From PyPI
pip install pykworldsim

# From source (dev extras)
git clone https://github.com/ka1rav6/pykworldsim
cd pykworldsim
pip install -e ".[dev]"
```

---

## 🚀 Quick Start

### Physics

```python
from pykworldsim import World, Simulation, Position, Velocity, MovementSystem
from pykworldsim.core.systems.physics import PhysicsSystem

world = World(name="demo")
world.register_system(PhysicsSystem(gravity=9.81, bounds=(0, 0, 100, 100)))
world.register_system(MovementSystem())

e = world.create_entity()
world.add_component(e, Position(x=10.0, y=0.0))
world.add_component(e, Velocity(dx=2.0, dy=0.0))

sim = Simulation(world, seed=42)
sim.run(steps=100, dt=0.1)
print(world.get_component(e, Position))
```

### Social world

```python
from pykworldsim import (World, Simulation, Person, Job, Goal,
                          SocialSystem, EventSystem, EventComponent)

world = World(name="society")
world.register_system(SocialSystem())
world.register_system(EventSystem())

# React to goal completion via EventBus
world.events.subscribe("goal_completed",
    lambda d: print(f"Goal done: {d['description']}"))

alice = world.create_entity()
world.add_component(alice, Person(name="Alice", age=28.0, happiness=65.0))
world.add_component(alice, Job(title="Engineer", salary=8000.0, satisfaction=75.0))
world.add_component(alice, Goal(description="Get promoted", priority=9.0))

sim = Simulation(world, seed=2024)
sim.run(steps=20, dt=1.0)
p = world.get_component(alice, Person)
print(f"Alice: age={p.age:.1f}, happiness={p.happiness:.1f}")
```

### Deterministic RNG

```python
sim = Simulation(world, seed=42)
# All randomness in systems must use sim.rng (not global random)
value = sim.rng.random()   # deterministic across runs
```

### Snapshot / Replay

```python
sim.run(steps=50, dt=0.1)
sim.take_snapshot("checkpoint")      # save state
sim.run(steps=50, dt=0.1)           # advance further
sim.restore_snapshot("checkpoint")  # roll back
```

### Staged mutations (safe during iteration)

```python
class SpawnSystem(BaseSystem):
    def update(self, world, dt):
        for entity, (pos,) in world.get_entities_with(Position):
            if some_condition:
                new_e = world.create_entity()
                # Stage the component — applied after all systems finish
                world.stage_add_component(new_e, Position(x=0.0, y=0.0))
```

---

## 🖥️ CLI

```bash
# Basic run
pykworldsim run examples/config.yaml

# Override config values
pykworldsim run examples/config.yaml --steps 200 --dt 0.05 --seed 99 --debug

# Save final state
pykworldsim run examples/config.yaml --save output.json

# Inspect a saved world
pykworldsim inspect output.json

# Load a custom plugin
pykworldsim run config.yaml --plugin mypackage.systems.MySystem

# List registered plugins
pykworldsim plugins
```

---

## ⚙️ YAML / JSON Config

```yaml
name: my-world
log_level: INFO

world:
  size: 200.0

simulation:
  steps: 100
  dt: 0.1
  seed: 42

systems:
  - type: MovementSystem
  - type: SocialSystem
    params:
      age_rate: 0.05
      energy_decay: 0.3
  - type: PhysicsSystem
    params:
      gravity: 9.81
      bounds: [0, 0, 200, 200]

entities:
  # Single entity
  - position: {x: 0.0, y: 0.0}
    velocity:  {dx: 5.0, dy: 2.0}

  # Spawn 10 identical entities
  - position: {x: 50.0, y: 50.0}
    velocity:  {dx: 1.0, dy: 0.0}
    count: 10

  # Person with job + goal
  - person:   {name: Alice, age: 28.0, happiness: 65.0, energy: 90.0}
    job:      {title: Engineer, salary: 8000.0, satisfaction: 75.0}
    goal:     {description: "Get promoted", priority: 9.0}
    position: {x: 25.0, y: 25.0}
```

---

## 📡 EventBus

Systems communicate via events, never direct calls:

```python
# Subscribe anywhere
world.events.subscribe("goal_completed", lambda d: print(d))
world.events.subscribe("entity_created", lambda d: log(d["entity"]))
world.events.subscribe("entity_destroyed", lambda d: cleanup(d["entity"]))

# Emit immediately
world.events.emit("custom_event", {"key": "value"})

# Emit deferred (safe inside system.update — dispatched after tick)
world.events.emit_deferred("score_changed", {"delta": +10})

# Built-in events
# "entity_created"   → {"entity": Entity}
# "entity_destroyed" → {"entity": Entity}
# "goal_completed"   → {"entity": Entity, "description": str}
```

---

## 🔌 Plugin System

```python
from pykworldsim.core.systems.base_system import BaseSystem
from pykworldsim.plugins import PluginRegistry

class BoundaryWrapSystem(BaseSystem):
    priority: int = 15   # runs after MovementSystem(10), before SocialSystem(20)

    def __init__(self, width=100.0, height=100.0):
        super().__init__()
        self.width = width
        self.height = height

    def update(self, world, dt):
        for entity, (pos,) in world.get_entities_with(Position):
            pos.x %= self.width
            pos.y %= self.height

# Register by class
PluginRegistry.register("BoundaryWrapSystem", BoundaryWrapSystem)

# Register by dotted path (for CLI --plugin flag)
PluginRegistry.register_from_path("mypackage.systems.BoundaryWrapSystem")
```

---

## 🏗️ Architecture

```
pykworldsim/
├── core/
│   ├── entity.py          Thread-safe registry + lifecycle hooks (on_add/on_remove)
│   ├── world.py           ECS container — staged queues, query engine, EventBus
│   ├── simulation.py      Deterministic loop — injected RNG, snapshot/replay
│   ├── query.py           Inverted-index QueryEngine — O(smallest-set) lookups
│   ├── events.py          EventBus — emit/subscribe, immediate + deferred dispatch
│   ├── components/
│   │   ├── position.py       2-D coordinate
│   │   ├── velocity.py       2-D velocity
│   │   ├── person.py         Individual agent
│   │   ├── location.py       Named place / city
│   │   ├── relationship.py   Directed bond
│   │   ├── job.py            Occupation
│   │   ├── goal.py           Motivation / objective
│   │   └── event_component.py  Scheduled occurrence
│   ├── systems/
│   │   ├── base_system.py    Abstract base — priority + update(world, dt) contract
│   │   ├── movement.py       priority=10 — pos += vel × dt
│   │   ├── physics.py        priority=5  — gravity + boundary bounce
│   │   ├── social.py         priority=20 — ageing, energy, happiness, goals
│   │   └── event_system.py   priority=1  — scheduled event dispatch
│   └── config/
│       └── loader.py         YAML/JSON → World + Simulation
├── plugins/
│   └── registry.py           Dynamic system registration
├── utils/
│   └── logging.py            Structured logging helper
└── cli.py                    Typer CLI — run/inspect/plugins + all overrides
```

### ECS contract

| Concept | Role | Rule |
|---|---|---|
| **Entity** | Opaque integer ID | Carries no data |
| **Component** | `@dataclass` — data only | No logic; implements `to_dict` / `from_dict` |
| **System** | `update(world, dt)` | Uses `world.get_entities_with(...)` only — never touches world internals |
| **World** | Container + staged queue | Applies mutations after all systems finish |
| **EventBus** | Pub/sub messaging | Systems emit, never call each other directly |

### System execution order (default priorities)

```
tick N:
  EventSystem     priority=1   (fire scheduled events first)
  PhysicsSystem   priority=5   (apply gravity/forces)
  MovementSystem  priority=10  (integrate velocity → position)
  SocialSystem    priority=20  (age, happiness, goals)
  → _flush_staged()            (apply deferred adds/removes/destroys)
  → events.flush()             (dispatch deferred EventBus messages)
```

---

## 🧪 Tests

```bash
pip install -e ".[dev]"

pytest                                  # all tests
pytest --cov=pykworldsim               # with coverage
pytest tests/test_simulation.py -v     # single file
pytest -k "test_determinism"           # filter by name
```

Test modules:

| File | Covers |
|---|---|
| `test_entity.py` | Entity creation, lifecycle hooks, thread safety |
| `test_query.py` | QueryEngine — add/get/has/remove/query |
| `test_events.py` | EventBus — emit/subscribe/deferred/flush |
| `test_world.py` | World — staged queues, priority ordering, report |
| `test_simulation.py` | Lifecycle, determinism, injected RNG, snapshot |
| `test_systems.py` | All 4 systems + system contract |
| `test_save_load.py` | Serialisation, ConfigLoader, edge cases |
| `test_plugins.py` | PluginRegistry — register/unregister/path |

---

## 📄 License

MIT © Kairav Dutta

# NOTE:
I have majorly used AI to create this. The idea and the way of implementation is original.