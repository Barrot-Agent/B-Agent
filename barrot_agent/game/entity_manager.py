"""
Entity Manager - Entity lifecycle, prefab instantiation, batch operations.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set
from .ecs_system import Entity, EntityRegistry


@dataclass
class EntityTemplate:
    """Template definition for creating entities with pre-defined components."""
    name: str
    components: List[Any] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    children: List["EntityTemplate"] = field(default_factory=list)


class EntityManager:
    """
    High-level entity lifecycle management with prefab instantiation.

    Provides:
    - Named entity creation with templates
    - Tag-based entity queries
    - Batch create/destroy operations
    - Parent-child hierarchy management
    """

    def __init__(self, registry: EntityRegistry):
        self._registry = registry
        self._named_entities: Dict[str, Entity] = {}
        self._entity_tags: Dict[int, Set[str]] = {}
        self._tag_index: Dict[str, Set[int]] = {}
        self._children: Dict[int, List[Entity]] = {}
        self._parent: Dict[int, Entity] = {}
        self._on_create: List[Callable] = []
        self._on_destroy: List[Callable] = []

    def create(self, name: Optional[str] = None) -> Entity:
        """Create a new entity, optionally with a name."""
        entity = self._registry.create_entity()
        if name:
            self._named_entities[name] = entity
        for cb in self._on_create:
            cb(entity)
        return entity

    def create_from_template(self, template: EntityTemplate) -> Entity:
        """Instantiate an entity from a template."""
        entity = self.create(template.name if template.name else None)
        for comp in template.components:
            self._registry.add_component(entity, comp)
        for tag in template.tags:
            self.add_tag(entity, tag)
        for child_template in template.children:
            child = self.create_from_template(child_template)
            self.set_parent(child, entity)
        return entity

    def destroy(self, entity: Entity) -> None:
        """Destroy an entity and all its children."""
        # Destroy children first
        for child in self._children.get(int(entity), [])[:]:
            self.destroy(child)

        # Remove from name map
        for name, ent in list(self._named_entities.items()):
            if ent == entity:
                del self._named_entities[name]
                break

        # Remove tags
        for tag in self._entity_tags.get(int(entity), set()):
            if tag in self._tag_index:
                self._tag_index[tag].discard(int(entity))

        # Remove parent ref
        parent = self._parent.pop(int(entity), None)
        if parent is not None and int(parent) in self._children:
            try:
                self._children[int(parent)].remove(entity)
            except ValueError:
                pass

        self._entity_tags.pop(int(entity), None)
        self._children.pop(int(entity), None)

        for cb in self._on_destroy:
            cb(entity)
        self._registry.destroy_entity(entity)

    def get_by_name(self, name: str) -> Optional[Entity]:
        """Find an entity by name."""
        return self._named_entities.get(name)

    def add_tag(self, entity: Entity, tag: str) -> None:
        """Add a tag to an entity."""
        self._entity_tags.setdefault(int(entity), set()).add(tag)
        self._tag_index.setdefault(tag, set()).add(int(entity))

    def remove_tag(self, entity: Entity, tag: str) -> None:
        """Remove a tag from an entity."""
        self._entity_tags.get(int(entity), set()).discard(tag)
        self._tag_index.get(tag, set()).discard(int(entity))

    def get_by_tag(self, tag: str) -> List[Entity]:
        """Get all entities with a specific tag."""
        return [Entity(eid) for eid in self._tag_index.get(tag, set())]

    def set_parent(self, entity: Entity, parent: Entity) -> None:
        """Set the parent of an entity."""
        self._parent[int(entity)] = parent
        self._children.setdefault(int(parent), []).append(entity)

    def get_children(self, entity: Entity) -> List[Entity]:
        """Get all children of an entity."""
        return self._children.get(int(entity), []).copy()

    def create_batch(self, count: int, template: Optional[EntityTemplate] = None) -> List[Entity]:
        """Create multiple entities at once."""
        if template:
            return [self.create_from_template(template) for _ in range(count)]
        return [self.create() for _ in range(count)]

    def destroy_batch(self, entities: List[Entity]) -> None:
        """Destroy multiple entities at once."""
        for entity in entities:
            self.destroy(entity)

    def on_entity_created(self, callback: Callable) -> None:
        """Register a callback for entity creation events."""
        self._on_create.append(callback)

    def on_entity_destroyed(self, callback: Callable) -> None:
        """Register a callback for entity destruction events."""
        self._on_destroy.append(callback)
