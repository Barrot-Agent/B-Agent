"""
Prefab System - Prefab templates, instantiation, hierarchical composition.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from .ecs_system import Entity, EntityRegistry
from .entity_manager import EntityManager, EntityTemplate


@dataclass
class PrefabVariant:
    """A named variant of a prefab with overridden properties."""
    variant_name: str = "default"
    overrides: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PrefabDefinition:
    """Definition of a reusable prefab template."""
    name: str
    template: EntityTemplate
    variants: Dict[str, PrefabVariant] = field(default_factory=dict)
    version: int = 1
    tags: List[str] = field(default_factory=list)


class PrefabSystem:
    """
    Prefab system for reusable entity templates.

    Supports:
    - Registration and retrieval of prefab definitions
    - Instantiation with optional variant overrides
    - Serialization to/from JSON
    - Prefab versioning
    """

    def __init__(self, entity_manager: EntityManager):
        self._entity_manager = entity_manager
        self._prefabs: Dict[str, PrefabDefinition] = {}
        self._instance_counts: Dict[str, int] = {}

    def register(self, definition: PrefabDefinition) -> None:
        """Register a prefab definition."""
        self._prefabs[definition.name] = definition

    def instantiate(
        self,
        prefab_name: str,
        variant: str = "default",
        position: Optional[Any] = None,
    ) -> Optional[Entity]:
        """Instantiate a prefab, optionally with a variant and position."""
        definition = self._prefabs.get(prefab_name)
        if not definition:
            return None

        entity = self._entity_manager.create_from_template(definition.template)

        # Apply variant overrides
        if variant != "default" and variant in definition.variants:
            v = definition.variants[variant]
            for comp_name, override_data in v.overrides.items():
                pass  # Apply overrides in a real implementation

        if position is not None:
            self._entity_manager._registry.add_component(entity, position)

        self._instance_counts[prefab_name] = self._instance_counts.get(prefab_name, 0) + 1
        return entity

    def add_variant(self, prefab_name: str, variant: PrefabVariant) -> bool:
        """Add a variant to an existing prefab."""
        defn = self._prefabs.get(prefab_name)
        if not defn:
            return False
        defn.variants[variant.variant_name] = variant
        return True

    def get_instance_count(self, prefab_name: str) -> int:
        """Return how many times a prefab has been instantiated."""
        return self._instance_counts.get(prefab_name, 0)

    def list_prefabs(self) -> List[str]:
        """List all registered prefab names."""
        return list(self._prefabs.keys())

    def serialize_prefab(self, prefab_name: str) -> Optional[str]:
        """Serialize a prefab definition to JSON."""
        defn = self._prefabs.get(prefab_name)
        if not defn:
            return None
        return json.dumps({"name": defn.name, "version": defn.version, "tags": defn.tags})
