"""World — central ECS container owning entities, components, and systems."""

from __future__ import annotations

import json
import logging
from typing import Any, Iterator, Type, TypeVar

from pykworldsim.core.entity import Entity, EntityRegistry
from pykworldsim.core.systems.base_system import BaseSystem

logger = logging.getLogger(__name__)

C = TypeVar("C")


class World:
    """
    The heart of the ECS framework.

    Manages:

    * **Entities** — via an internal :class:`~pykworldsim.core.entity.EntityRegistry`.
    * **Components** — stored as ``{component_type: {entity_id: instance}}``.
    * **Systems** — ordered pipeline of :class:`~pykworldsim.core.systems.base_system.BaseSystem`.

    No global state. Safe to instantiate multiple worlds simultaneously.

    Examples
    --------
    >>> world = World(name="earth")
    >>> e = world.create_entity()
    >>> world.add_component(e, Position(x=1.0, y=2.0))
    >>> world.get_component(e, Position)
    Position(x=1.0000, y=2.0000)
    """

    def __init__(self, name: str = "world") -> None:
        self.name: str = name
        self._registry: EntityRegistry = EntityRegistry()
        self._components: dict[type, dict[int, Any]] = {}
        self._systems: list[BaseSystem] = []
        self._destroy_queue: list[Entity] = []

    # ------------------------------------------------------------------
    # Entities
    # ------------------------------------------------------------------

    def create_entity(self) -> Entity:
        """Create and return a new :class:`~pykworldsim.core.entity.Entity`."""
        entity = self._registry.create()
        logger.debug("Created %r", entity)
        return entity

    def destroy_entity(self, entity: Entity) -> None:
        """
        Schedule *entity* for destruction at end of current tick.

        Safe to call during iteration — actual removal is deferred.
        All components are removed automatically.
        """
        self._destroy_queue.append(entity)
        logger.debug("Queued %r for destruction", entity)

    def _flush_destroy_queue(self) -> None:
        """Flush deferred entity destructions (called once per tick)."""
        for entity in self._destroy_queue:
            if self._registry.is_alive(entity):
                self._remove_all_components(entity)
                self._registry.destroy(entity)
                logger.debug("Destroyed %r", entity)
        self._destroy_queue.clear()

    def is_alive(self, entity: Entity) -> bool:
        """Return ``True`` if *entity* has not been destroyed."""
        return self._registry.is_alive(entity)

    @property
    def entities(self) -> list[Entity]:
        """Snapshot list of all currently-alive entities."""
        return [Entity(id=eid) for eid in self._registry.alive_ids]

    # ------------------------------------------------------------------
    # Components
    # ------------------------------------------------------------------

    def add_component(self, entity: Entity, component: Any) -> None:
        """
        Attach *component* to *entity*.

        Raises
        ------
        KeyError
            If *entity* is not alive.
        """
        if not self._registry.is_alive(entity):
            raise KeyError(f"{entity!r} is not alive.")
        comp_type = type(component)
        self._components.setdefault(comp_type, {})[entity.id] = component
        logger.debug("Added %s to %r", comp_type.__name__, entity)

    def remove_component(self, entity: Entity, component_type: Type[C]) -> None:
        """
        Remove the *component_type* component from *entity*.

        Raises
        ------
        KeyError
            If the component does not exist on *entity*.
        """
        try:
            del self._components[component_type][entity.id]
        except KeyError:
            raise KeyError(
                f"{entity!r} has no component of type {component_type.__name__!r}."
            )

    def get_component(self, entity: Entity, component_type: Type[C]) -> C:
        """
        Retrieve the *component_type* component belonging to *entity*.

        Raises
        ------
        KeyError
            If the component does not exist.
        """
        try:
            return self._components[component_type][entity.id]  # type: ignore[return-value]
        except KeyError:
            raise KeyError(
                f"{entity!r} has no component {component_type.__name__!r}."
            )

    def has_component(self, entity: Entity, component_type: Type[C]) -> bool:
        """Return ``True`` if *entity* owns a *component_type* component."""
        return (
            component_type in self._components
            and entity.id in self._components[component_type]
        )

    def get_components(
        self, *component_types: type
    ) -> Iterator[tuple[Entity, list[Any]]]:
        """
        Yield ``(entity, [comp1, comp2, …])`` for every alive entity that
        owns **all** of the requested component types.

        Iterates a snapshot — safe to destroy/add entities inside the loop.

        Examples
        --------
        >>> for entity, (pos, vel) in world.get_components(Position, Velocity):
        ...     pos.x += vel.dx
        """
        if not component_types:
            return

        primary_type = min(
            component_types,
            key=lambda ct: len(self._components.get(ct, {})),
        )
        snapshot = list(self._components.get(primary_type, {}).items())

        for eid, _ in snapshot:
            entity = Entity(id=eid)
            if not self._registry.is_alive(entity):
                continue
            if all(
                ct in self._components and eid in self._components[ct]
                for ct in component_types
            ):
                comps = [self._components[ct][eid] for ct in component_types]
                yield entity, comps

    def _remove_all_components(self, entity: Entity) -> None:
        for store in self._components.values():
            store.pop(entity.id, None)

    def generate_report(self) -> dict[str, Any]:
        """
        Return a summary report of the world's current state.

        Compatible with the original repo's ``world.generate_report()`` API.
        """
        report: dict[str, Any] = {
            "world": self.name,
            "entity_count": len(self._registry.alive_ids),
            "system_count": len(self._systems),
            "component_types": [t.__name__ for t in self._components],
            "entities": [],
        }
        for entity in self.entities:
            entry: dict[str, Any] = {"id": entity.id, "components": {}}
            for comp_type, store in self._components.items():
                if entity.id in store:
                    comp = store[entity.id]
                    entry["components"][comp_type.__name__] = (
                        comp.to_dict() if hasattr(comp, "to_dict") else repr(comp)
                    )
            report["entities"].append(entry)
        return report

    # ------------------------------------------------------------------
    # Systems
    # ------------------------------------------------------------------

    def register_system(self, system: BaseSystem) -> None:
        """Append *system* to the ordered system pipeline."""
        system.world = self
        system.on_register()
        self._systems.append(system)
        logger.info("Registered system: %s", type(system).__name__)

    def unregister_system(self, system_type: Type[BaseSystem]) -> None:
        """Remove the first system of *system_type* from the pipeline."""
        before = len(self._systems)
        self._systems = [s for s in self._systems if not isinstance(s, system_type)]
        if len(self._systems) < before:
            logger.info("Unregistered system: %s", system_type.__name__)

    # Alias kept for compatibility with original repo usage
    def add_system(self, system: BaseSystem) -> None:
        """Alias for :meth:`register_system`."""
        self.register_system(system)

    @property
    def systems(self) -> list[BaseSystem]:
        """Read-only snapshot of registered systems."""
        return list(self._systems)

    # ------------------------------------------------------------------
    # Tick
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        """
        Advance the world by one tick.

        Calls each system in registration order, then flushes the destroy queue.
        """
        for system in self._systems:
            if system.enabled:
                system.update(dt)
        self._flush_destroy_queue()

    # Alias kept for original repo API compat
    def Simulate(self, dt: float = 1.0) -> None:  # noqa: N802
        """Alias for :meth:`update`. Maintains original repo API."""
        self.update(dt)

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialise world state to a JSON-compatible dictionary."""
        components_out: dict[str, dict[str, Any]] = {}
        for comp_type, store in self._components.items():
            type_name = comp_type.__name__
            components_out[type_name] = {}
            for eid, comp in store.items():
                if hasattr(comp, "to_dict"):
                    components_out[type_name][str(eid)] = comp.to_dict()
        return {
            "name": self.name,
            "entities": list(self._registry.alive_ids),
            "components": components_out,
        }

    def save(self, path: str) -> None:
        """Serialise world state to *path* as JSON."""
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, indent=2)
        logger.info("World saved → %s", path)

    @classmethod
    def load(
        cls,
        path: str,
        component_registry: dict[str, type] | None = None,
    ) -> "World":
        """
        Load a world from a JSON file produced by :meth:`save`.

        Parameters
        ----------
        path:
            Path to the JSON save file.
        component_registry:
            ``{"ClassName": ComponentClass}`` mapping used for deserialisation.
            Merged with the built-in types (Position, Velocity, Person, etc.).
        """
        from pykworldsim.core.components.position import Position
        from pykworldsim.core.components.velocity import Velocity
        from pykworldsim.core.components.person import Person
        from pykworldsim.core.components.location import Location
        from pykworldsim.core.components.job import Job
        from pykworldsim.core.components.goal import Goal
        from pykworldsim.core.components.relationship import Relationship

        built_in: dict[str, type] = {
            "Position": Position,
            "Velocity": Velocity,
            "Person": Person,
            "Location": Location,
            "Job": Job,
            "Goal": Goal,
            "Relationship": Relationship,
        }
        reg = {**built_in, **(component_registry or {})}

        with open(path, "r", encoding="utf-8") as fh:
            data: dict[str, Any] = json.load(fh)

        world = cls(name=data.get("name", "world"))

        # Re-create entities in ID order
        for eid in sorted(data.get("entities", [])):
            while world._registry._next_id <= eid:
                e = world._registry.create()
                if e.id < eid:
                    world._registry.destroy(e)

        for type_name, store in data.get("components", {}).items():
            comp_cls = reg.get(type_name)
            if comp_cls is None:
                logger.warning("Unknown component type %r — skipping.", type_name)
                continue
            for eid_str, comp_data in store.items():
                entity = Entity(id=int(eid_str))
                if world._registry.is_alive(entity) and hasattr(comp_cls, "from_dict"):
                    world.add_component(entity, comp_cls.from_dict(comp_data))

        logger.info("World loaded ← %s", path)
        return world

    def __repr__(self) -> str:
        return (
            f"World(name={self.name!r}, "
            f"entities={len(self._registry.alive_ids)}, "
            f"systems={len(self._systems)})"
        )
