"""ConfigLoader — YAML/JSON → World + Simulation."""
from __future__ import annotations
import json, logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

@dataclass
class EntityConfig:
    position: dict[str, float] | None = None
    velocity: dict[str, float] | None = None
    person: dict[str, Any] | None = None
    location: dict[str, Any] | None = None
    job: dict[str, Any] | None = None
    goal: dict[str, Any] | None = None
    relationship: dict[str, Any] | None = None
    count: int = 1

@dataclass
class SystemConfig:
    type: str = "MovementSystem"
    params: dict[str, Any] = field(default_factory=dict)

@dataclass
class SimulationConfig:
    steps: int = 100
    dt: float = 1.0
    seed: int | None = None

@dataclass
class WorldConfig:
    name: str = "world"
    size: float = 100.0
    entities: list[EntityConfig] = field(default_factory=list)
    systems: list[SystemConfig] = field(default_factory=list)
    simulation: SimulationConfig = field(default_factory=SimulationConfig)
    log_level: str = "INFO"


class ConfigLoader:
    """Load WorldConfig from YAML/JSON and build live World+Simulation pairs."""

    @staticmethod
    def load(path: str | Path) -> WorldConfig:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Config not found: {path}")
        suffix = path.suffix.lower()
        if suffix in {".yaml", ".yml"}:
            try:
                import yaml  # type: ignore[import-untyped]
            except ImportError as exc:
                raise ImportError("pip install pyyaml") from exc
            with path.open("r", encoding="utf-8") as fh:
                raw: dict[str, Any] = yaml.safe_load(fh) or {}
        elif suffix == ".json":
            with path.open("r", encoding="utf-8") as fh:
                raw = json.load(fh)
        else:
            raise ValueError(f"Unsupported config format: {suffix!r}")
        return ConfigLoader._parse(raw)

    @staticmethod
    def _parse(raw: dict[str, Any]) -> WorldConfig:
        world_raw = raw.get("world", {})
        entities: list[EntityConfig] = []
        for e in raw.get("entities", []):
            entities.append(EntityConfig(
                position=e.get("position"),
                velocity=e.get("velocity"),
                person=e.get("person"),
                location=e.get("location"),
                job=e.get("job"),
                goal=e.get("goal"),
                relationship=e.get("relationship"),
                count=int(e.get("count", 1)),
            ))
        systems: list[SystemConfig] = []
        for s in raw.get("systems", []):
            if isinstance(s, str):
                systems.append(SystemConfig(type=s))
            else:
                systems.append(SystemConfig(type=s.get("type","MovementSystem"),
                                            params=s.get("params",{})))
        sim_raw = raw.get("simulation", {})
        sim_cfg = SimulationConfig(
            steps=int(sim_raw.get("steps", 100)),
            dt=float(sim_raw.get("dt", 1.0)),
            seed=sim_raw.get("seed"),
        )
        return WorldConfig(
            name=str(raw.get("name", "world")),
            size=float(world_raw.get("size", 100.0)),
            entities=entities,
            systems=systems,
            simulation=sim_cfg,
            log_level=str(raw.get("log_level", "INFO")),
        )

    @staticmethod
    def build(config: WorldConfig):  # type: ignore[return]
        from pykworldsim.core.world import World
        from pykworldsim.core.simulation import Simulation
        from pykworldsim.core.components.position import Position
        from pykworldsim.core.components.velocity import Velocity
        from pykworldsim.core.components.person import Person
        from pykworldsim.core.components.location import Location
        from pykworldsim.core.components.job import Job
        from pykworldsim.core.components.goal import Goal
        from pykworldsim.core.components.relationship import Relationship
        from pykworldsim.core.systems.movement import MovementSystem
        from pykworldsim.core.systems.physics import PhysicsSystem
        from pykworldsim.core.systems.social import SocialSystem
        from pykworldsim.core.systems.event_system import EventSystem
        from pykworldsim.plugins.registry import PluginRegistry

        logging.basicConfig(level=getattr(logging, config.log_level, logging.INFO))
        world = World(name=config.name)

        system_map: dict[str, Any] = {
            "MovementSystem": MovementSystem,
            "PhysicsSystem": PhysicsSystem,
            "SocialSystem": SocialSystem,
            "EventSystem": EventSystem,
            **PluginRegistry.all_systems(),
        }
        for sc in config.systems:
            cls = system_map.get(sc.type)
            if cls is None:
                logger.warning("Unknown system %r — skipping.", sc.type)
                continue
            world.register_system(cls(**sc.params) if sc.params else cls())
        if not config.systems:
            world.register_system(MovementSystem())

        component_builders = {
            "position": Position, "velocity": Velocity, "person": Person,
            "location": Location, "job": Job, "goal": Goal,
            "relationship": Relationship,
        }
        for ecfg in config.entities:
            for _ in range(ecfg.count):
                e = world.create_entity()
                for attr, cls in component_builders.items():
                    raw_data = getattr(ecfg, attr)
                    if raw_data is not None:
                        world.add_component(e, cls.from_dict(raw_data))  # type: ignore[attr-defined]

        sim = Simulation(world, seed=config.simulation.seed)
        logger.info("Built world %r with %d entities.", config.name, len(world.entities))
        return world, sim
