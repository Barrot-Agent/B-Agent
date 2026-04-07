"""
Component Registry - Type registration, pool management, and component composition.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Type, TypeVar

T = TypeVar("T")


@dataclass
class ComponentMeta:
    """Metadata for a registered component type."""
    component_type: type
    name: str
    size_bytes: int = 0
    pool_size: int = 1000
    is_tag: bool = False     # Tag components have no data


class ComponentPool:
    """Object pool for efficient component allocation."""

    def __init__(self, component_type: type, pool_size: int = 1000):
        self.component_type = component_type
        self.pool_size = pool_size
        self._free: List[Any] = []
        self._allocated: int = 0

    def acquire(self, **kwargs: Any) -> Any:
        """Acquire a component instance from the pool."""
        if self._free:
            obj = self._free.pop()
            # Reset object if it has a reset method
            if hasattr(obj, "reset"):
                obj.reset()
            return obj
        self._allocated += 1
        try:
            return self.component_type(**kwargs)
        except TypeError:
            return self.component_type()

    def release(self, component: Any) -> None:
        """Return a component to the pool."""
        if len(self._free) < self.pool_size:
            self._free.append(component)

    def get_stats(self) -> Dict[str, int]:
        return {"allocated": self._allocated, "free": len(self._free)}


class ComponentRegistry:
    """
    Central registry for component types with pooling and queries.

    Manages:
    - Component type registration with metadata
    - Object pools for allocation efficiency
    - Component dependency tracking
    - Composition pattern support
    """

    def __init__(self):
        self._types: Dict[str, ComponentMeta] = {}
        self._pools: Dict[type, ComponentPool] = {}
        self._dependencies: Dict[type, Set[type]] = {}
        self._type_map: Dict[type, ComponentMeta] = {}

    def register(
        self,
        component_type: type,
        pool_size: int = 1000,
        is_tag: bool = False,
        requires: Optional[List[type]] = None,
    ) -> ComponentMeta:
        """Register a component type."""
        name = component_type.__name__
        meta = ComponentMeta(
            component_type=component_type,
            name=name,
            pool_size=pool_size,
            is_tag=is_tag,
        )
        self._types[name] = meta
        self._type_map[component_type] = meta
        self._pools[component_type] = ComponentPool(component_type, pool_size)
        if requires:
            self._dependencies[component_type] = set(requires)
        return meta

    def acquire(self, component_type: Type[T], **kwargs: Any) -> T:
        """Acquire a component from its pool."""
        pool = self._pools.get(component_type)
        if pool:
            return pool.acquire(**kwargs)
        return component_type(**kwargs)

    def release(self, component: Any) -> None:
        """Release a component back to its pool."""
        pool = self._pools.get(type(component))
        if pool:
            pool.release(component)

    def get_dependencies(self, component_type: type) -> Set[type]:
        """Get the required component types for a given component."""
        return self._dependencies.get(component_type, set())

    def is_registered(self, component_type: type) -> bool:
        """Check if a component type is registered."""
        return component_type in self._type_map

    def get_all_types(self) -> List[ComponentMeta]:
        """Return all registered component types."""
        return list(self._types.values())

    def get_pool_stats(self) -> Dict[str, Dict[str, int]]:
        """Return pool statistics for all registered components."""
        return {
            name: self._pools[meta.component_type].get_stats()
            for name, meta in self._types.items()
            if meta.component_type in self._pools
        }
