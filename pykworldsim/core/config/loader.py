"""ConfigLoader — parse YAML/JSON world configs and build live World+Simulation."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Plain-data config descriptors
# ---------------------------------------------------------------------------

@dataclass
class EntityConfig:
    """Configuration descriptor for a single entity."""
    position: dict[str, float] | None = None
    velocity: dict[str, float] | None = None
    person: dict[str, Any] | None = None
    location: dict[str, Any] | None = None
    job: dict[str, Any] | None = None
    goal: dict[str, Any] | None = None
    relationship: dict[str, Any] | None = None


@dataclass
class SystemConfig:
    """Configuration descriptor for a system entry."""
    type: str = "MovementSystem"
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class SimulationConfig:
    """Top-level simulation parameters."""
    steps: int = 100
    dt: float = 1.0
    seed: int | None = None


@dataclass
class WorldConfig:
    """Fully parsed representation of a world configuration file."""
    name: str = "world"
    entities: list[EntityConfig] = field(default_factory=list)
    systems: list[SystemConfig] = field(default_factory=list)
    simulation: SimulationConfig = field(default_factory=SimulationConfig)
    log_level: str = "INFO"


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

class ConfigLoader:
    """
    Load :class:`WorldConfig` objects from YAML or JSON files and build
    live :class:`~pykworldsim.core.world.World` /
    :class:`~pykworldsim.core.simulation.Simulation` pairs.

    Examples
    --------
    >>> cfg = ConfigLoader.load("examples/config.yaml")
    >>> world, sim = ConfigLoader.build(cfg)
    >>> sim.run(steps=cfg.simulation.steps, dt=cfg.simulation.dt)
    """

    @staticmethod
    def load(path: str | Path) -> WorldConfig:
        """
        Parse *path* (YAML or JSON) into a :class:`WorldConfig`.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        ValueError
            If the file extension is unsupported.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Config not found: {path}")

        suffix = path.suffix.lower()
        if suffix in {".yaml", ".yml"}:
            try:
                import yaml  # type: ignore[import-untyped]
            except ImportError as exc:
                raise ImportError("Install pyyaml: pip install pyyaml") from exc
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
        entities: list[EntityConfig] = []
        for e in raw.get("entities", []):
            entities.append(
                EntityConfig(
                    position=e.get("position"),
                    velocity=e.get("velocity"),
                    person=e.get("person"),
                    location=e.get("location"),
                    job=e.get("job"),
                    goal=e.get("goal"),
                    relationship=e.get("relationship"),
                )
            )

        systems: list[SystemConfig] = []
        for s in raw.get("systems", []):
            if isinstance(s, str):
                systems.append(SystemConfig(type=s))
            else:
                systems.append(
                    SystemConfig(
                        type=s.get("type", "MovementSystem"),
                        params=s.get("params", {}),
                    )
                )

        sim_raw = raw.get("simulation", {})
        sim_cfg = SimulationConfig(
            steps=int(sim_raw.get("steps", 100)),
            dt=float(sim_raw.get("dt", 1.0)),
            seed=sim_raw.get("seed"),
        )

        return WorldConfig(
            name=str(raw.get("name", "world")),
            entities=entities,
            systems=systems,
            simulation=sim_cfg,
            log_level=str(raw.get("log_level", "INFO")),
        )

    @staticmethod
    def build(config: WorldConfig):  # type: ignore[return]
        """
        Instantiate a World and Simulation from *config*.

        Returns
        -------
        tuple[World, Simulation]
        """
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
        from pykworldsim.core.systems.event import EventSystem
        from pykworldsim.plugins.registry import PluginRegistry

        logging.basicConfig(level=getattr(logging, config.log_level, logging.INFO))

        world = World(name=config.name)

        # Built-in system map + plugin-registered systems
        plugin_systems = PluginRegistry.all_systems()
        system_map: dict[str, Any] = {
            "MovementSystem": MovementSystem,
            "PhysicsSystem": PhysicsSystem,
            "SocialSystem": SocialSystem,
            "EventSystem": EventSystem,
            **plugin_systems,
        }

        for sys_cfg in config.systems:
            sys_cls = system_map.get(sys_cfg.type)
            if sys_cls is None:
                logger.warning("Unknown system %r — skipping.", sys_cfg.type)
                continue
            instance = sys_cls(**sys_cfg.params) if sys_cfg.params else sys_cls()
            world.register_system(instance)

        if not config.systems:
            world.register_system(MovementSystem())

        # Build entities and attach components
        component_builders: dict[str, tuple[type, type]] = {
            "position": (Position, Position),
            "velocity": (Velocity, Velocity),
            "person":   (Person, Person),
            "location": (Location, Location),
            "job":      (Job, Job),
            "goal":     (Goal, Goal),
            "relationship": (Relationship, Relationship),
        }

        for ecfg in config.entities:
            e = world.create_entity()
            for attr, (comp_cls, _) in component_builders.items():
                raw_data = getattr(ecfg, attr)
                if raw_data is not None:
                    world.add_component(e, comp_cls.from_dict(raw_data))  # type: ignore[attr-defined]

        sim = Simulation(world, seed=config.simulation.seed)
        logger.info("Built world %r with %d entities.", config.name, len(world.entities))
        return world, sim
