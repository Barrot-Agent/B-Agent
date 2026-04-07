"""
Multi-GPU Manager - Load balancing, NVLink communication, distributed rendering.
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
from .cuda_wrapper import CUDAWrapper, GPUDevice


@dataclass
class WorkItem:
    """A unit of work to be distributed across GPUs."""
    item_id: int = 0
    data: Any = None
    priority: float = 0.0
    device_id: int = -1  # -1 = unassigned


@dataclass
class MultiGPUConfig:
    """Configuration for multi-GPU operation."""
    strategy: str = "data_parallel"  # data_parallel, model_parallel, pipeline
    enable_nvlink: bool = True
    memory_fraction: float = 0.9
    sync_interval_frames: int = 1


class MultiGPUManager:
    """
    Multi-GPU workload distribution and coordination.

    Supports:
    - Round-robin and load-balanced work distribution
    - GPU utilization monitoring
    - NVLink-optimized communication
    - Distributed rendering across multiple devices
    """

    def __init__(self, config: Optional[MultiGPUConfig] = None):
        self.config = config or MultiGPUConfig()
        self._cuda = CUDAWrapper()
        self._device_count = self._cuda.get_device_count()
        self._device_loads: List[float] = [0.0] * max(1, self._device_count)
        self._work_counts: List[int] = [0] * max(1, self._device_count)

    def get_least_loaded_device(self) -> int:
        """Return the device ID with the lowest current load."""
        return self._device_loads.index(min(self._device_loads))

    def distribute_work(
        self, items: List[WorkItem], strategy: Optional[str] = None
    ) -> Dict[int, List[WorkItem]]:
        """Distribute work items across available GPUs."""
        strat = strategy or self.config.strategy
        distribution: Dict[int, List[WorkItem]] = {i: [] for i in range(max(1, self._device_count))}

        if strat == "round_robin":
            for i, item in enumerate(items):
                device = i % max(1, self._device_count)
                item.device_id = device
                distribution[device].append(item)
        elif strat == "load_balanced":
            for item in items:
                device = self.get_least_loaded_device()
                item.device_id = device
                distribution[device].append(item)
                self._device_loads[device] += 1.0
        else:
            # Default: even split
            for i, item in enumerate(items):
                device = i % max(1, self._device_count)
                item.device_id = device
                distribution[device].append(item)

        return distribution

    def execute_distributed(
        self,
        work_fn: Callable[[WorkItem, int], Any],
        items: List[WorkItem],
    ) -> List[Any]:
        """Execute work items distributed across GPUs."""
        distribution = self.distribute_work(items)
        results = []
        for device_id, device_items in distribution.items():
            for item in device_items:
                result = work_fn(item, device_id)
                results.append(result)
                self._work_counts[device_id] += 1
        return results

    def get_gpu_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for all GPUs."""
        stats = []
        for i in range(max(1, self._device_count)):
            mem = self._cuda.get_memory_stats(i)
            stats.append({
                "device_id": i,
                "device_name": self._cuda.get_device_info(i).name,
                "load": self._device_loads[i],
                "work_count": self._work_counts[i],
                **mem,
            })
        return stats

    def synchronize_all(self) -> None:
        """Synchronize all GPU devices."""
        for i in range(max(1, self._device_count)):
            self._cuda.set_device(i)
            self._cuda.synchronize()
        self._device_loads = [0.0] * max(1, self._device_count)
