"""
QueryEngine — O(1) per-type lookup, no repeated full-entity scans.

Architecture
------------
Maintains an inverted index: ``{component_type → set(entity_id)}``.
Intersection of these sets gives entities that own ALL queried types
in time proportional to the smallest matching set, not the total entity count.
"""
from __future__ import annotations

from typing import Any, Iterator, Type, TypeVar

from pykworldsim.core.entity import Entity

C = TypeVar("C")


class QueryEngine:
    """
    Efficient component query engine backed by per-type inverted index sets.

    Used internally by :class:`~pykworldsim.core.world.World`.

    Examples
    --------
    >>> engine = QueryEngine()
    >>> engine.index(Position, entity_id=0, instance=Position(1.0, 2.0))
    >>> engine.query(Position)  # → yields (Entity(0), [Position(1.0, 2.0)])
    """

    def __init__(self) -> None:
        # { ComponentType → { entity_id → component_instance } }
        self._store: dict[type, dict[int, Any]] = {}
        # { ComponentType → set(entity_id) }  — inverted index for fast intersection
        self._index: dict[type, set[int]] = {}

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def add(self, entity: Entity, component: Any) -> None:
        """Store *component* for *entity* and update the index."""
        ctype = type(component)
        self._store.setdefault(ctype, {})[entity.id] = component
        self._index.setdefault(ctype, set()).add(entity.id)

    def remove(self, entity: Entity, component_type: Type[C]) -> None:
        """Remove the *component_type* record for *entity*.

        Raises
        ------
        KeyError
            If the component does not exist on *entity*.
        """
        store = self._store.get(component_type)
        if store is None or entity.id not in store:
            raise KeyError(
                f"{entity!r} has no component {component_type.__name__!r}."
            )
        del store[entity.id]
        self._index[component_type].discard(entity.id)

    def remove_all(self, entity: Entity) -> None:
        """Remove every component belonging to *entity* from all stores."""
        for ctype, store in self._store.items():
            if entity.id in store:
                del store[entity.id]
                self._index[ctype].discard(entity.id)

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get(self, entity: Entity, component_type: Type[C]) -> C:
        """
        Retrieve the *component_type* instance for *entity*.

        Raises
        ------
        KeyError
            If missing.
        """
        try:
            return self._store[component_type][entity.id]  # type: ignore[return-value]
        except KeyError:
            raise KeyError(
                f"{entity!r} has no component {component_type.__name__!r}."
            )

    def has(self, entity: Entity, component_type: type) -> bool:
        """Return ``True`` if *entity* owns a *component_type* component."""
        idx = self._index.get(component_type)
        return idx is not None and entity.id in idx

    def query(
        self, *component_types: type
    ) -> Iterator[tuple[Entity, list[Any]]]:
        """
        Yield ``(entity, [comp1, comp2, …])`` for every entity that owns
        **all** of *component_types* simultaneously.

        Uses inverted-index intersection — no full entity scan.
        Safe to call during entity destruction (iterates a snapshot).
        """
        if not component_types:
            return

        # Start from the smallest set — minimises intersection work
        sorted_types = sorted(
            component_types,
            key=lambda ct: len(self._index.get(ct, set())),
        )
        primary_type = sorted_types[0]
        candidate_ids: frozenset[int] = frozenset(
            self._index.get(primary_type, set())
        )  # snapshot

        for eid in candidate_ids:
            if all(
                eid in self._index.get(ct, set())
                for ct in sorted_types[1:]
            ):
                entity = Entity(id=eid)
                comps = [self._store[ct][eid] for ct in component_types]
                yield entity, comps

    def component_types(self) -> list[type]:
        """Return all component types currently tracked."""
        return list(self._store.keys())

    def store_for(self, component_type: Type[C]) -> dict[int, C]:
        """Return the raw ``{entity_id: instance}`` store for *component_type*."""
        return self._store.get(component_type, {})  # type: ignore[return-value]
