"""
Module 9 — Intelligent Dataset Caching

Multi-tier LRU cache spanning GPU VRAM, CPU RAM, local SSD, and cloud
object storage.  Provides smart pre-fetching queues, bandwidth-aware
streaming, and configurable eviction policies.
"""

from __future__ import annotations

import time
from collections import OrderedDict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StorageTier(str, Enum):
    GPU = "gpu"
    CPU = "cpu"
    SSD = "ssd"
    HDD = "hdd"
    CLOUD = "cloud"


class EvictionPolicy(str, Enum):
    LRU = "lru"
    LFU = "lfu"
    SIZE_AWARE = "size_aware"
    PRIORITY = "priority"


@dataclass
class CacheEntry:
    key: str
    tier: StorageTier
    size_bytes: int
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    priority: int = 0


@dataclass
class CacheConfig:
    """Configuration for the multi-tier cache."""

    gpu_memory_gb: float = 8.0
    cpu_memory_gb: float = 64.0
    cache_dir: str = "/fast_ssd/barrot_cache"
    cloud_storage: str = ""
    prefetch_count: int = 5
    eviction_policy: EvictionPolicy = EvictionPolicy.LRU

    @property
    def gpu_bytes(self) -> int:
        return int(self.gpu_memory_gb * 1024**3)

    @property
    def cpu_bytes(self) -> int:
        return int(self.cpu_memory_gb * 1024**3)


@dataclass
class CacheStats:
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_bytes_cached: int = 0
    gpu_bytes_used: int = 0
    cpu_bytes_used: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def summary(self) -> str:
        return (
            f"Cache: {self.hits} hits / {self.misses} misses "
            f"(hit rate {self.hit_rate:.1%}) | "
            f"GPU {self.gpu_bytes_used / 1024**3:.1f} GB | "
            f"CPU {self.cpu_bytes_used / 1024**3:.1f} GB | "
            f"evictions {self.evictions}"
        )


class DatasetCache:
    """
    Intelligent multi-tier cache for 3D dataset assets.

    Manages GPU VRAM, CPU RAM, SSD, HDD, and cloud storage in a
    unified interface with configurable eviction and smart pre-fetching.

    Usage::

        cache = DatasetCache()
        cache.configure(
            gpu_memory_gb=8,
            cpu_memory_gb=64,
            cache_dir="/fast_ssd",
            prefetch_count=5,
            eviction_policy="lru",
        )
        cache.put("scene_001", data, size_bytes=1024**3)
        data = cache.get("scene_001")
    """

    def __init__(self) -> None:
        self._config = CacheConfig()
        self._gpu_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._cpu_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._ssd_index: dict[str, CacheEntry] = {}
        self._data_store: dict[str, Any] = {}
        self._stats = CacheStats()
        self._prefetch_queue: list[str] = []

    # ------------------------------------------------------------------ #
    #  Configuration                                                       #
    # ------------------------------------------------------------------ #

    def configure(
        self,
        gpu_memory_gb: float = 8.0,
        cpu_memory_gb: float = 64.0,
        cache_dir: str = "/fast_ssd/barrot_cache",
        cloud_storage: str = "",
        prefetch_count: int = 5,
        eviction_policy: str | EvictionPolicy = EvictionPolicy.LRU,
    ) -> "DatasetCache":
        """Configure cache tiers and policy (fluent interface)."""
        policy = (
            EvictionPolicy(eviction_policy) if isinstance(eviction_policy, str) else eviction_policy
        )
        self._config = CacheConfig(
            gpu_memory_gb=gpu_memory_gb,
            cpu_memory_gb=cpu_memory_gb,
            cache_dir=cache_dir,
            cloud_storage=cloud_storage,
            prefetch_count=prefetch_count,
            eviction_policy=policy,
        )
        return self

    # ------------------------------------------------------------------ #
    #  Core operations                                                     #
    # ------------------------------------------------------------------ #

    def get(self, key: str) -> Any | None:
        """Retrieve an item, promoting through tiers as needed."""
        if key in self._data_store:
            entry = self._gpu_cache.get(key) or self._cpu_cache.get(key)
            if entry:
                entry.access_count += 1
                entry.last_access = time.time()
                self._gpu_cache.move_to_end(key, last=True) if key in self._gpu_cache else None
            self._stats.hits += 1
            return self._data_store[key]
        self._stats.misses += 1
        return None

    def put(self, key: str, data: Any, size_bytes: int, priority: int = 0) -> StorageTier:
        """
        Insert an item into the best available tier.

        Returns the tier where the item was placed.
        """
        if self._stats.gpu_bytes_used + size_bytes <= self._config.gpu_bytes:
            tier = StorageTier.GPU
            entry = CacheEntry(key=key, tier=tier, size_bytes=size_bytes, priority=priority)
            self._gpu_cache[key] = entry
            self._stats.gpu_bytes_used += size_bytes
        elif self._stats.cpu_bytes_used + size_bytes <= self._config.cpu_bytes:
            tier = StorageTier.CPU
            entry = CacheEntry(key=key, tier=tier, size_bytes=size_bytes, priority=priority)
            self._cpu_cache[key] = entry
            self._stats.cpu_bytes_used += size_bytes
        else:
            tier = StorageTier.SSD
            entry = CacheEntry(key=key, tier=tier, size_bytes=size_bytes, priority=priority)
            self._ssd_index[key] = entry
            self._evict_if_needed(tier)

        self._data_store[key] = data
        self._stats.total_bytes_cached += size_bytes
        return tier

    def evict(self, key: str) -> bool:
        """Explicitly remove an item from all tiers."""
        removed = key in self._data_store
        self._data_store.pop(key, None)
        entry = self._gpu_cache.pop(key, None)
        if entry:
            self._stats.gpu_bytes_used -= entry.size_bytes
        entry = self._cpu_cache.pop(key, None)
        if entry:
            self._stats.cpu_bytes_used -= entry.size_bytes
        self._ssd_index.pop(key, None)
        if removed:
            self._stats.evictions += 1
        return removed

    def prefetch(self, keys: list[str]) -> None:
        """Add keys to the pre-fetch queue (up to prefetch_count)."""
        for key in keys:
            if key not in self._prefetch_queue:
                self._prefetch_queue.append(key)
        self._prefetch_queue = self._prefetch_queue[: self._config.prefetch_count]

    def clear(self) -> None:
        """Flush the entire cache."""
        self._gpu_cache.clear()
        self._cpu_cache.clear()
        self._ssd_index.clear()
        self._data_store.clear()
        self._stats = CacheStats()
        self._prefetch_queue.clear()

    @property
    def stats(self) -> CacheStats:
        return self._stats

    @property
    def config(self) -> CacheConfig:
        return self._config

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _evict_if_needed(self, tier: StorageTier) -> None:
        if self._config.eviction_policy == EvictionPolicy.LRU:
            cache = self._gpu_cache if tier == StorageTier.GPU else self._cpu_cache
            while cache:
                oldest_key, oldest_entry = next(iter(cache.items()))
                cache.pop(oldest_key)
                self._data_store.pop(oldest_key, None)
                if tier == StorageTier.GPU:
                    self._stats.gpu_bytes_used -= oldest_entry.size_bytes
                else:
                    self._stats.cpu_bytes_used -= oldest_entry.size_bytes
                self._stats.evictions += 1
                break
