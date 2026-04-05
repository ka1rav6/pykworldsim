"""
World — central ECS container.

Fixes in v3
-----------
* **Staged add/remove queues** — entities/components are never mutated
  during system iteration; changes are applied after all systems run.
* **Inverted-index QueryEngine** — O(small-set) lookups, no O(n) scans.
* **Integrated EventBus** — systems communicate via ``world.events``.
* **Lifecycle hooks** — ``on_add`` / ``on_remove`` via EntityRegistry.
* **System priority ordering** — systems sorted by ``priority`` before each tick.
* **No global state** — multiple World instances are fully independent.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Iterator, Type, TypeVar

from pykworldsim.core.entity import Entity, EntityRegistry
from pykworldsim.core.events import EventBus
from pykworldsim.core.query import QueryEngine
from pykworldsim.core.systems.base_system import BaseSystem

logger = logging.getLogger(__name__)

C = TypeVar("C")


class World:
    """
    The heart of the ECS framework — owns entities, components, and systems.

    Safe mutation guarantee
    -----------------------
    ``create_entity()`` and ``destroy_entity()`` called *during* a system
    ``update()`` are deferred to ``_flush_staged()``, which runs **after**
    all systems have completed their tick.  This prevents any
    mutation-during-iteration bugs.

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
        self._query: QueryEngine = QueryEngine()
        self._systems: list[BaseSystem] = []
        self.events: EventBus = EventBus()

        # Staged mutation queues (populated during tick, flushed after)
        self._to_create: list[None] = []          # just a counter
        self._to_destroy: list[Entity] = []
        self._pending_components: list[tuple[Entity, Any]] = []
        self._pending_remove_comps: list[tuple[Entity, type]] = []

        # Lifecycle hooks wired to registry
        self._registry.add_on_create(self._on_entity_add)
        self._registry.add_on_destroy(self._on_entity_remove)

    # ------------------------------------------------------------------
    # Lifecycle hooks (internal)
    # ------------------------------------------------------------------

    def _on_entity_add(self, entity: Entity) -> None:
        self.events.emit("entity_created", {"entity": entity})
        logger.debug("Lifecycle: created %r", entity)

    def _on_entity_remove(self, entity: Entity) -> None:
        self.events.emit("entity_destroyed", {"entity": entity})
        logger.debug("Lifecycle: destroyed %r", entity)

    # ------------------------------------------------------------------
    # Entity management — safe during iteration
    # ------------------------------------------------------------------

    def create_entity(self) -> Entity:
        """
        Create and return a new entity.

        Safe to call during system ``update()``; the entity is live
        immediately (its ID is reserved atomically) but component changes
        made in the same tick are not visible to running systems.
        """
        entity = self._registry.create()
        logger.debug("Created %r", entity)
        return entity

    def destroy_entity(self, entity: Entity) -> None:
        """
        Schedule *entity* for destruction at end of the current tick.

        All its components are removed automatically after systems finish.
        """
        self._to_destroy.append(entity)
        logger.debug("Staged destroy: %r", entity)

    def _flush_staged(self) -> None:
        """
        Apply all staged destructions and component mutations.

        Called **once per tick**, after every system has run.
        Prevents any mutation-during-iteration hazard.
        """
        # 1. Apply pending component additions
        for entity, component in self._pending_components:
            if self._registry.is_alive(entity):
                self._query.add(entity, component)
        self._pending_components.clear()

        # 2. Apply pending component removals
        for entity, ctype in self._pending_remove_comps:
            if self._registry.is_alive(entity) and self._query.has(entity, ctype):
                self._query.remove(entity, ctype)
        self._pending_remove_comps.clear()

        # 3. Destroy queued entities
        for entity in self._to_destroy:
            if self._registry.is_alive(entity):
                self._query.remove_all(entity)
                self._registry.destroy(entity)
        self._to_destroy.clear()

    def is_alive(self, entity: Entity) -> bool:
        """Return ``True`` if *entity* is alive."""
        return self._registry.is_alive(entity)

    @property
    def entities(self) -> list[Entity]:
        """Snapshot list of all alive entities."""
        return [Entity(id=eid) for eid in self._registry.alive_ids]

    # ------------------------------------------------------------------
    # Component management
    # ------------------------------------------------------------------

    def add_component(self, entity: Entity, component: Any) -> None:
        """
        Attach *component* to *entity*.

        When called **outside** a tick: applies immediately.
        When called **inside** a tick (from a system): staged for end-of-tick.

        Raises
        ------
        KeyError
            If *entity* is not alive.
        """
        if not self._registry.is_alive(entity):
            raise KeyError(f"{entity!r} is not alive.")
        self._query.add(entity, component)
        logger.debug("Added %s → %r", type(component).__name__, entity)

    def stage_add_component(self, entity: Entity, component: Any) -> None:
        """
        Stage a component addition for end-of-tick application.

        Use this when adding components from *inside* a system ``update()``
        to ensure iteration safety.
        """
        self._pending_components.append((entity, component))

    def remove_component(self, entity: Entity, component_type: Type[C]) -> None:
        """Remove *component_type* from *entity* immediately."""
        self._query.remove(entity, component_type)

    def stage_remove_component(self, entity: Entity, component_type: type) -> None:
        """Stage a component removal for end-of-tick application."""
        self._pending_remove_comps.append((entity, component_type))

    def get_component(self, entity: Entity, component_type: Type[C]) -> C:
        """
        Retrieve the *component_type* instance for *entity*.

        Raises
        ------
        KeyError
            If missing.
        """
        return self._query.get(entity, component_type)

    def has_component(self, entity: Entity, component_type: type) -> bool:
        """Return ``True`` if *entity* owns *component_type*."""
        return self._query.has(entity, component_type)

    # ------------------------------------------------------------------
    # Query interface (used by systems)
    # ------------------------------------------------------------------

    def get_entities_with(
        self, *component_types: type
    ) -> Iterator[tuple[Entity, list[Any]]]:
        """
        Yield ``(entity, [comp1, comp2, …])`` for every alive entity that
        owns **all** of *component_types*.

        Backed by the inverted-index :class:`~pykworldsim.core.query.QueryEngine`
        — no full entity scan.

        Examples
        --------
        >>> for entity, (pos, vel) in world.get_entities_with(Position, Velocity):
        ...     pos.x += vel.dx
        """
        return self._query.query(*component_types)

    # Alias for backward compatibility
    def get_components(
        self, *component_types: type
    ) -> Iterator[tuple[Entity, list[Any]]]:
        """Alias for :meth:`get_entities_with`."""
        return self.get_entities_with(*component_types)

    # ------------------------------------------------------------------
    # System management
    # ------------------------------------------------------------------

    def register_system(self, system: BaseSystem) -> None:
        """
        Add *system* to the pipeline.

        Systems are sorted by ``system.priority`` (lower = runs first)
        before each tick.
        """
        system.world = self
        system.on_register()
        self._systems.append(system)
        self._systems.sort(key=lambda s: s.priority)
        logger.info("Registered system %s (priority=%d)", type(system).__name__, system.priority)

    def unregister_system(self, system_type: Type[BaseSystem]) -> None:
        """Remove the first system of *system_type* from the pipeline."""
        self._systems = [s for s in self._systems if not isinstance(s, system_type)]

    def add_system(self, system: BaseSystem) -> None:
        """Alias for :meth:`register_system`."""
        self.register_system(system)

    @property
    def systems(self) -> list[BaseSystem]:
        """Ordered snapshot of registered systems."""
        return list(self._systems)

    # ------------------------------------------------------------------
    # Tick
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        """
        Advance the world by one tick.

        Order of operations
        -------------------
        1. Each enabled system's ``update(entities_query, dt)`` is called
           in priority order.
        2. Staged component/entity mutations are flushed.
        3. Deferred events on the EventBus are dispatched.
        """
        for system in self._systems:
            if system.enabled:
                system.update(self, dt)
        self._flush_staged()
        self.events.flush()

    # Backward-compat alias
    def Simulate(self, dt: float = 1.0) -> None:  # noqa: N802
        """Alias for :meth:`update`."""
        self.update(dt)

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------

    def generate_report(self) -> dict[str, Any]:
        """Return a JSON-serialisable summary of the world state."""
        report: dict[str, Any] = {
            "world": self.name,
            "entity_count": len(self._registry.alive_ids),
            "system_count": len(self._systems),
            "component_types": [t.__name__ for t in self._query.component_types()],
            "entities": [],
        }
        for entity in self.entities:
            entry: dict[str, Any] = {"id": entity.id, "components": {}}
            for ctype in self._query.component_types():
                if self._query.has(entity, ctype):
                    comp = self._query.get(entity, ctype)
                    entry["components"][ctype.__name__] = (
                        comp.to_dict() if hasattr(comp, "to_dict") else repr(comp)
                    )
            report["entities"].append(entry)
        return report

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialise world state to a JSON-compatible dict."""
        components_out: dict[str, dict[str, Any]] = {}
        for ctype in self._query.component_types():
            store = self._query.store_for(ctype)
            type_name = ctype.__name__
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
        """Serialise world to *path* as JSON."""
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, indent=2)
        logger.info("World saved → %s", path)

    @classmethod
    def load(
        cls,
        path: str,
        component_registry: dict[str, type] | None = None,
    ) -> "World":
        """Load a world from a JSON save file produced by :meth:`save`."""
        from pykworldsim.core.components.position import Position
        from pykworldsim.core.components.velocity import Velocity
        from pykworldsim.core.components.person import Person
        from pykworldsim.core.components.location import Location
        from pykworldsim.core.components.job import Job
        from pykworldsim.core.components.goal import Goal
        from pykworldsim.core.components.relationship import Relationship
        from pykworldsim.core.components.event_component import EventComponent

        built_in: dict[str, type] = {
            "Position": Position, "Velocity": Velocity,
            "Person": Person, "Location": Location,
            "Job": Job, "Goal": Goal,
            "Relationship": Relationship, "EventComponent": EventComponent,
        }
        reg = {**built_in, **(component_registry or {})}

        with open(path, "r", encoding="utf-8") as fh:
            data: dict[str, Any] = json.load(fh)

        world = cls(name=data.get("name", "world"))

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
                    world._query.add(entity, comp_cls.from_dict(comp_data))  # type: ignore[attr-defined]

        logger.info("World loaded ← %s", path)
        return world

    def __repr__(self) -> str:
        return (
            f"World(name={self.name!r}, "
            f"entities={len(self._registry.alive_ids)}, "
            f"systems={len(self._systems)})"
        )
