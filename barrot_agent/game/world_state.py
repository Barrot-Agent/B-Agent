"""
World State - Game world representation, spatial partitioning, chunk loading.

Implements:
- Chunk-based world with streaming loading/unloading
- Octree spatial partitioning for efficient queries
- Persistent state serialization
- Multiplayer delta synchronization
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, List, Optional, Set, Tuple


@dataclass
class WorldChunk:
    """A spatial chunk of the game world."""
    chunk_x: int = 0
    chunk_z: int = 0
    chunk_size: float = 64.0
    is_loaded: bool = False
    entities: List[int] = field(default_factory=list)
    static_data: Dict[str, Any] = field(default_factory=dict)
    dirty: bool = False
    load_time: float = 0.0

    @property
    def world_origin(self) -> Tuple[float, float, float]:
        return (self.chunk_x * self.chunk_size, 0.0, self.chunk_z * self.chunk_size)

    def contains(self, pos: Tuple[float, float, float]) -> bool:
        ox, _, oz = self.world_origin
        return ox <= pos[0] < ox + self.chunk_size and oz <= pos[2] < oz + self.chunk_size


@dataclass
class OctreeNode:
    """A node in a spatial octree."""
    bounds_min: Tuple[float, float, float] = (-100.0, -100.0, -100.0)
    bounds_max: Tuple[float, float, float] = (100.0, 100.0, 100.0)
    objects: List[int] = field(default_factory=list)
    children: List[Optional["OctreeNode"]] = field(default_factory=lambda: [None] * 8)
    max_objects: int = 8
    depth: int = 0
    max_depth: int = 8

    def is_leaf(self) -> bool:
        return all(c is None for c in self.children)

    def contains_point(self, pos: Tuple[float, float, float]) -> bool:
        return (
            self.bounds_min[0] <= pos[0] <= self.bounds_max[0]
            and self.bounds_min[1] <= pos[1] <= self.bounds_max[1]
            and self.bounds_min[2] <= pos[2] <= self.bounds_max[2]
        )

    def _child_index(self, pos: Tuple[float, float, float]) -> int:
        cx = (self.bounds_min[0] + self.bounds_max[0]) / 2
        cy = (self.bounds_min[1] + self.bounds_max[1]) / 2
        cz = (self.bounds_min[2] + self.bounds_max[2]) / 2
        idx = 0
        if pos[0] > cx:
            idx |= 1
        if pos[1] > cy:
            idx |= 2
        if pos[2] > cz:
            idx |= 4
        return idx

    def insert(self, obj_id: int, pos: Tuple[float, float, float]) -> bool:
        if not self.contains_point(pos):
            return False
        if self.is_leaf() and (len(self.objects) < self.max_objects or self.depth >= self.max_depth):
            self.objects.append(obj_id)
            return True
        # Subdivide if needed
        if self.is_leaf():
            self._subdivide()
        idx = self._child_index(pos)
        if self.children[idx]:
            return self.children[idx].insert(obj_id, pos)
        return False

    def _subdivide(self) -> None:
        cx = (self.bounds_min[0] + self.bounds_max[0]) / 2
        cy = (self.bounds_min[1] + self.bounds_max[1]) / 2
        cz = (self.bounds_min[2] + self.bounds_max[2]) / 2
        for i in range(8):
            mn = (
                self.bounds_min[0] if not (i & 1) else cx,
                self.bounds_min[1] if not (i & 2) else cy,
                self.bounds_min[2] if not (i & 4) else cz,
            )
            mx = (
                cx if not (i & 1) else self.bounds_max[0],
                cy if not (i & 2) else self.bounds_max[1],
                cz if not (i & 4) else self.bounds_max[2],
            )
            self.children[i] = OctreeNode(
                bounds_min=mn, bounds_max=mx,
                depth=self.depth + 1, max_depth=self.max_depth
            )

    def query_sphere(
        self, center: Tuple[float, float, float], radius: float
    ) -> List[int]:
        """Query all objects within a sphere."""
        # Check AABB-sphere intersection
        closest = (
            max(self.bounds_min[0], min(center[0], self.bounds_max[0])),
            max(self.bounds_min[1], min(center[1], self.bounds_max[1])),
            max(self.bounds_min[2], min(center[2], self.bounds_max[2])),
        )
        dist_sq = sum((closest[i] - center[i]) ** 2 for i in range(3))
        if dist_sq > radius * radius:
            return []

        results = list(self.objects)
        for child in self.children:
            if child:
                results.extend(child.query_sphere(center, radius))
        return results


class ChunkManager:
    """Manages world chunk loading, unloading, and streaming."""

    def __init__(self, chunk_size: float = 64.0, load_radius: int = 4):
        self.chunk_size = chunk_size
        self.load_radius = load_radius
        self._chunks: Dict[Tuple[int, int], WorldChunk] = {}

    def _pos_to_chunk(self, pos: Tuple[float, float, float]) -> Tuple[int, int]:
        return (int(pos[0] // self.chunk_size), int(pos[2] // self.chunk_size))

    def update_origin(self, camera_pos: Tuple[float, float, float]) -> Dict[str, int]:
        """Load/unload chunks based on camera position."""
        center = self._pos_to_chunk(camera_pos)
        loaded = unloaded = 0

        # Determine which chunks should be loaded
        desired: Set[Tuple[int, int]] = set()
        for dx in range(-self.load_radius, self.load_radius + 1):
            for dz in range(-self.load_radius, self.load_radius + 1):
                if dx * dx + dz * dz <= self.load_radius * self.load_radius:
                    desired.add((center[0] + dx, center[1] + dz))

        # Load new chunks
        for key in desired - set(self._chunks.keys()):
            chunk = WorldChunk(chunk_x=key[0], chunk_z=key[1], chunk_size=self.chunk_size)
            chunk.is_loaded = True
            chunk.load_time = time.time()
            self._chunks[key] = chunk
            loaded += 1

        # Unload distant chunks
        for key in set(self._chunks.keys()) - desired:
            self._chunks[key].is_loaded = False
            del self._chunks[key]
            unloaded += 1

        return {"loaded": loaded, "unloaded": unloaded, "active": len(self._chunks)}

    def get_chunk_at(self, pos: Tuple[float, float, float]) -> Optional[WorldChunk]:
        key = self._pos_to_chunk(pos)
        return self._chunks.get(key)

    def get_loaded_chunks(self) -> List[WorldChunk]:
        return [c for c in self._chunks.values() if c.is_loaded]


class WorldState:
    """
    Complete game world state with spatial partitioning and chunk streaming.

    Manages:
    - Octree-based spatial queries
    - Chunk streaming based on camera position
    - World state serialization for save/load
    - Multiplayer delta state tracking
    """

    def __init__(
        self,
        world_bounds: float = 4096.0,
        chunk_size: float = 64.0,
    ):
        self.world_bounds = world_bounds
        self._octree = OctreeNode(
            bounds_min=(-world_bounds / 2,) * 3,
            bounds_max=(world_bounds / 2,) * 3,
        )
        self._chunk_manager = ChunkManager(chunk_size)
        self._entity_positions: Dict[int, Tuple[float, float, float]] = {}
        self._persistent_state: Dict[str, Any] = {}
        self._dirty_keys: Set[str] = set()
        self._time_of_day: float = 6.0  # 0-24 hour format
        self._world_time: float = 0.0

    def register_entity(self, entity_id: int, position: Tuple[float, float, float]) -> None:
        """Register an entity's position in the spatial index."""
        self._entity_positions[entity_id] = position
        self._octree.insert(entity_id, position)

    def update_entity_position(
        self, entity_id: int, position: Tuple[float, float, float]
    ) -> None:
        """Update an entity's world position."""
        self._entity_positions[entity_id] = position

    def query_nearby_entities(
        self, center: Tuple[float, float, float], radius: float
    ) -> List[int]:
        """Query entities within a radius of a point."""
        return self._octree.query_sphere(center, radius)

    def update_streaming(self, camera_pos: Tuple[float, float, float]) -> Dict[str, int]:
        """Update chunk streaming based on camera position."""
        return self._chunk_manager.update_origin(camera_pos)

    def set_persistent(self, key: str, value: Any) -> None:
        """Store a persistent world state value."""
        self._persistent_state[key] = value
        self._dirty_keys.add(key)

    def get_persistent(self, key: str, default: Any = None) -> Any:
        """Retrieve a persistent world state value."""
        return self._persistent_state.get(key, default)

    def update(self, delta_time: float) -> None:
        """Advance world time and simulation."""
        self._world_time += delta_time
        self._time_of_day = (self._time_of_day + delta_time / 120.0) % 24.0  # 2-min day

    def get_dirty_state(self) -> Dict[str, Any]:
        """Get state keys that changed since last sync (for multiplayer)."""
        dirty = {k: self._persistent_state[k] for k in self._dirty_keys if k in self._persistent_state}
        self._dirty_keys.clear()
        return dirty

    def serialize(self) -> Dict[str, Any]:
        """Serialize the world state for saving."""
        return {
            "world_time": self._world_time,
            "time_of_day": self._time_of_day,
            "persistent_state": dict(self._persistent_state),
            "entity_count": len(self._entity_positions),
        }

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Load world state from serialized data."""
        self._world_time = data.get("world_time", 0.0)
        self._time_of_day = data.get("time_of_day", 6.0)
        self._persistent_state = data.get("persistent_state", {})
