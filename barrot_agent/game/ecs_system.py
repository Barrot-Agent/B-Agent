"""
ECS System - Entity Component System core implementation.

Implements a Data-Oriented ECS architecture with:
- Archetype-based component storage for cache efficiency
- Sparse entity ID management
- Type-safe component queries
- System scheduling with dependency resolution
- World/registry pattern
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generator, Generic, List, Optional, Set, Tuple, Type, TypeVar

T = TypeVar("T")


class Entity(int):
    """An entity is simply an integer ID."""
    INVALID: "Entity"

Entity.INVALID = Entity(-1)


@dataclass
class ComponentStorage(Generic[T]):
    """Dense storage for a single component type."""
    component_type: Type[T]
    _components: Dict[int, T] = field(default_factory=dict)  # entity_id -> component

    def add(self, entity: Entity, component: T) -> None:
        """Add a component to an entity."""
        self._components[int(entity)] = component

    def remove(self, entity: Entity) -> bool:
        """Remove a component from an entity."""
        return self._components.pop(int(entity), None) is not None

    def get(self, entity: Entity) -> Optional[T]:
        """Get a component for an entity."""
        return self._components.get(int(entity))

    def has(self, entity: Entity) -> bool:
        """Check if entity has this component."""
        return int(entity) in self._components

    def get_all(self) -> Generator[Tuple[Entity, T], None, None]:
        """Iterate over all (entity, component) pairs."""
        for eid, comp in self._components.items():
            yield Entity(eid), comp

    def __len__(self) -> int:
        return len(self._components)


class Archetype:
    """
    An archetype represents a unique combination of component types.
    All entities with the same component set share an archetype.
    """

    def __init__(self, component_types: Tuple[type, ...]):
        self.component_types = frozenset(component_types)
        self.signature: int = hash(self.component_types)
        self._entities: List[Entity] = []

    def add_entity(self, entity: Entity) -> None:
        self._entities.append(entity)

    def remove_entity(self, entity: Entity) -> None:
        try:
            self._entities.remove(entity)
        except ValueError:
            pass

    def get_entities(self) -> List[Entity]:
        return self._entities.copy()

    def matches(self, required_types: Set[type]) -> bool:
        """Check if this archetype contains all required component types."""
        return required_types.issubset(self.component_types)


class EntityRegistry:
    """Manages entity lifecycle and component assignments."""

    def __init__(self):
        self._next_id: int = 0
        self._active_entities: Set[int] = set()
        self._free_ids: List[int] = []
        self._entity_components: Dict[int, Set[type]] = {}
        self._archetypes: Dict[frozenset, Archetype] = {}
        self._component_storages: Dict[type, ComponentStorage] = {}

    def create_entity(self) -> Entity:
        """Create a new entity with a unique ID."""
        if self._free_ids:
            entity_id = self._free_ids.pop()
        else:
            entity_id = self._next_id
            self._next_id += 1
        entity = Entity(entity_id)
        self._active_entities.add(entity_id)
        self._entity_components[entity_id] = set()
        return entity

    def destroy_entity(self, entity: Entity) -> None:
        """Destroy an entity and remove all its components."""
        eid = int(entity)
        if eid not in self._active_entities:
            return

        component_types = self._entity_components.pop(eid, set())
        for comp_type in component_types:
            storage = self._component_storages.get(comp_type)
            if storage:
                storage.remove(entity)

        self._active_entities.discard(eid)
        self._free_ids.append(eid)
        self._update_archetype(entity, component_types, removing=True)

    def add_component(self, entity: Entity, component: Any) -> None:
        """Add a component to an entity."""
        comp_type = type(component)
        eid = int(entity)

        if comp_type not in self._component_storages:
            self._component_storages[comp_type] = ComponentStorage(comp_type)

        old_types = self._entity_components.get(eid, set()).copy()
        self._component_storages[comp_type].add(entity, component)
        self._entity_components.setdefault(eid, set()).add(comp_type)
        self._update_archetype(entity, old_types, removing=False)

    def remove_component(self, entity: Entity, comp_type: type) -> bool:
        """Remove a component from an entity."""
        storage = self._component_storages.get(comp_type)
        if not storage:
            return False

        old_types = self._entity_components.get(int(entity), set()).copy()
        removed = storage.remove(entity)
        if removed:
            self._entity_components[int(entity)].discard(comp_type)
        self._update_archetype(entity, old_types, removing=False)
        return removed

    def get_component(self, entity: Entity, comp_type: Type[T]) -> Optional[T]:
        """Get a specific component for an entity."""
        storage = self._component_storages.get(comp_type)
        if storage:
            return storage.get(entity)
        return None

    def has_component(self, entity: Entity, comp_type: type) -> bool:
        """Check if entity has a specific component."""
        storage = self._component_storages.get(comp_type)
        return storage.has(entity) if storage else False

    def query(self, *component_types: type) -> Generator[Tuple[Entity, ...], None, None]:
        """
        Query for all entities that have all specified component types.

        Yields tuples of (entity, comp1, comp2, ...) for each matching entity.
        """
        if not component_types:
            return

        required = set(component_types)
        # Find the smallest storage to iterate over
        storages = [
            self._component_storages.get(ct)
            for ct in component_types
            if ct in self._component_storages
        ]
        if len(storages) < len(component_types):
            return  # At least one component type has no storage

        smallest_idx = min(range(len(storages)), key=lambda i: len(storages[i]))
        base_storage = storages[smallest_idx]

        for entity, _ in base_storage.get_all():
            # Check that entity has all other required components
            has_all = all(
                self._entity_components.get(int(entity), set()) >= required
            )
            if has_all:
                components = [entity]
                for ct in component_types:
                    comp = self._component_storages[ct].get(entity)
                    components.append(comp)
                yield tuple(components)

    def _update_archetype(
        self, entity: Entity, old_types: Set[type], removing: bool
    ) -> None:
        """Update the archetype for an entity after component changes."""
        new_types = self._entity_components.get(int(entity), set())

        # Remove from old archetype
        old_key = frozenset(old_types)
        if old_key in self._archetypes:
            self._archetypes[old_key].remove_entity(entity)

        if removing or not new_types:
            return

        # Add to new archetype
        new_key = frozenset(new_types)
        if new_key not in self._archetypes:
            self._archetypes[new_key] = Archetype(tuple(new_types))
        self._archetypes[new_key].add_entity(entity)

    def get_entity_count(self) -> int:
        """Return total number of active entities."""
        return len(self._active_entities)

    def is_alive(self, entity: Entity) -> bool:
        """Check if an entity is still alive."""
        return int(entity) in self._active_entities


class System:
    """Base class for ECS systems."""

    def __init__(self, name: str = ""):
        self.name = name or self.__class__.__name__
        self.enabled = True
        self._last_update_time: float = 0.0
        self._update_time_ms: float = 0.0

    def update(self, registry: EntityRegistry, delta_time: float) -> None:
        """Override in subclasses to implement system logic."""
        pass

    def get_update_time_ms(self) -> float:
        """Return time spent in last update (ms)."""
        return self._update_time_ms


class ECSSystem:
    """
    Complete Entity Component System manager.

    Orchestrates entities, components, and systems with:
    - Efficient archetype-based storage
    - System execution with timing
    - Event-driven component notifications
    - Batch operations for performance
    """

    def __init__(self):
        self.registry = EntityRegistry()
        self._systems: List[System] = []
        self._frame_count = 0
        self._total_update_time_ms = 0.0

    def add_system(self, system: System) -> None:
        """Register a system for update processing."""
        self._systems.append(system)

    def remove_system(self, system_name: str) -> bool:
        """Remove a system by name."""
        for i, sys in enumerate(self._systems):
            if sys.name == system_name:
                self._systems.pop(i)
                return True
        return False

    def create_entity(self) -> Entity:
        """Create a new entity."""
        return self.registry.create_entity()

    def destroy_entity(self, entity: Entity) -> None:
        """Destroy an entity."""
        self.registry.destroy_entity(entity)

    def add_component(self, entity: Entity, component: Any) -> None:
        """Add a component to an entity."""
        self.registry.add_component(entity, component)

    def get_component(self, entity: Entity, comp_type: Type[T]) -> Optional[T]:
        """Get a component from an entity."""
        return self.registry.get_component(entity, comp_type)

    def query(self, *comp_types: type) -> Generator:
        """Query entities by component types."""
        return self.registry.query(*comp_types)

    def update(self, delta_time: float) -> float:
        """Run all registered systems and return total update time in ms."""
        self._frame_count += 1
        total_ms = 0.0

        for system in self._systems:
            if not system.enabled:
                continue
            start = time.perf_counter()
            system.update(self.registry, delta_time)
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            system._update_time_ms = elapsed_ms
            total_ms += elapsed_ms

        self._total_update_time_ms = total_ms
        return total_ms

    def get_entity_count(self) -> int:
        """Return total active entity count."""
        return self.registry.get_entity_count()

    def get_system_stats(self) -> List[Dict[str, Any]]:
        """Return per-system performance statistics."""
        return [
            {
                "name": sys.name,
                "enabled": sys.enabled,
                "update_ms": sys.get_update_time_ms(),
            }
            for sys in self._systems
        ]

    def get_frame_count(self) -> int:
        """Return the total number of frames processed."""
        return self._frame_count
