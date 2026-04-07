"""
GPU Performance Monitor - Utilization, memory, thermal, and bottleneck detection.
"""
from __future__ import annotations
import time
import math
import random
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, List, Optional
from collections import deque


@dataclass
class GPUMetrics:
    """Snapshot of GPU performance metrics."""
    device_id: int = 0
    timestamp: float = field(default_factory=time.time)
    gpu_utilization: float = 0.0       # Percent 0-100
    memory_used_mb: float = 0.0
    memory_total_mb: float = 8192.0
    memory_utilization: float = 0.0    # Percent
    temperature_c: float = 0.0
    power_draw_w: float = 0.0
    power_limit_w: float = 350.0
    clock_sm_mhz: float = 0.0
    clock_mem_mhz: float = 0.0
    fan_speed_pct: float = 0.0
    pcie_rx_mbps: float = 0.0
    pcie_tx_mbps: float = 0.0


class GPUPerformanceMonitor:
    """
    GPU performance monitoring with thermal management and bottleneck detection.

    Tracks:
    - GPU and memory utilization
    - Temperature and power
    - Clock frequencies
    - PCIe bandwidth
    - Performance bottleneck identification
    """

    THERMAL_THROTTLE_TEMP = 83.0
    CRITICAL_TEMP = 95.0

    def __init__(self, device_ids: Optional[List[int]] = None, sample_interval_ms: float = 100.0):
        self.device_ids = device_ids or [0]
        self.sample_interval_ms = sample_interval_ms
        self._history: Dict[int, Deque[GPUMetrics]] = {
            d: deque(maxlen=600) for d in self.device_ids
        }
        self._nvidia_smi_available = self._check_nvidia_smi()

    def _check_nvidia_smi(self) -> bool:
        try:
            import pynvml
            pynvml.nvmlInit()
            return True
        except Exception:
            return False

    def sample(self, device_id: int = 0) -> GPUMetrics:
        """Sample current GPU metrics."""
        if self._nvidia_smi_available:
            return self._sample_nvidia_smi(device_id)
        return self._sample_simulated(device_id)

    def _sample_nvidia_smi(self, device_id: int) -> GPUMetrics:
        """Sample via pynvml."""
        try:
            import pynvml
            handle = pynvml.nvmlDeviceGetHandleByIndex(device_id)
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0

            metrics = GPUMetrics(
                device_id=device_id,
                gpu_utilization=float(util.gpu),
                memory_used_mb=mem.used / (1024 ** 2),
                memory_total_mb=mem.total / (1024 ** 2),
                memory_utilization=mem.used / max(mem.total, 1) * 100.0,
                temperature_c=float(temp),
                power_draw_w=power,
            )
            self._history[device_id].append(metrics)
            return metrics
        except Exception:
            return self._sample_simulated(device_id)

    def _sample_simulated(self, device_id: int) -> GPUMetrics:
        """Return simulated metrics when hardware monitoring is unavailable."""
        t = time.time()
        metrics = GPUMetrics(
            device_id=device_id,
            gpu_utilization=50.0 + 30.0 * math.sin(t * 0.1),
            memory_used_mb=3000.0 + 500.0 * math.sin(t * 0.05),
            memory_total_mb=8192.0,
            memory_utilization=40.0,
            temperature_c=65.0 + 10.0 * math.sin(t * 0.03),
            power_draw_w=200.0 + 50.0 * math.sin(t * 0.07),
            power_limit_w=350.0,
            clock_sm_mhz=1800.0,
            clock_mem_mhz=9000.0,
        )
        metrics.memory_utilization = metrics.memory_used_mb / metrics.memory_total_mb * 100
        self._history[device_id].append(metrics)
        return metrics

    def get_average_metrics(self, device_id: int = 0, window_s: float = 5.0) -> GPUMetrics:
        """Return average metrics over the last window_s seconds."""
        history = self._history.get(device_id, deque())
        now = time.time()
        recent = [m for m in history if now - m.timestamp <= window_s]
        if not recent:
            return self.sample(device_id)

        def avg(attr: str) -> float:
            return sum(getattr(m, attr) for m in recent) / len(recent)

        return GPUMetrics(
            device_id=device_id,
            gpu_utilization=avg("gpu_utilization"),
            memory_used_mb=avg("memory_used_mb"),
            memory_total_mb=recent[0].memory_total_mb,
            temperature_c=avg("temperature_c"),
            power_draw_w=avg("power_draw_w"),
        )

    def detect_bottleneck(self, device_id: int = 0) -> str:
        """Identify the current performance bottleneck."""
        metrics = self.get_average_metrics(device_id)
        if metrics.gpu_utilization < 50 and metrics.memory_utilization > 90:
            return "memory_bandwidth"
        if metrics.temperature_c > self.THERMAL_THROTTLE_TEMP:
            return "thermal_throttling"
        if metrics.power_draw_w > metrics.power_limit_w * 0.95:
            return "power_limit"
        if metrics.gpu_utilization > 95:
            return "compute_bound"
        if metrics.memory_utilization > 90:
            return "memory_bound"
        return "none"

    def is_overheating(self, device_id: int = 0) -> bool:
        """Check if GPU temperature is critically high."""
        metrics = self.sample(device_id)
        return metrics.temperature_c >= self.CRITICAL_TEMP

    def get_report(self) -> Dict[str, Any]:
        """Generate a performance report for all monitored devices."""
        report = {}
        for device_id in self.device_ids:
            metrics = self.get_average_metrics(device_id)
            report[f"device_{device_id}"] = {
                "gpu_util_pct": round(metrics.gpu_utilization, 1),
                "memory_used_mb": round(metrics.memory_used_mb, 1),
                "temperature_c": round(metrics.temperature_c, 1),
                "power_w": round(metrics.power_draw_w, 1),
                "bottleneck": self.detect_bottleneck(device_id),
            }
        return report
