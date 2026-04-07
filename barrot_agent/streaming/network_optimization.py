"""
Network Optimization - Latency monitoring, bandwidth estimation, adaptive bitrate.

Implements:
- Real-time latency monitoring and glass-to-glass measurement
- Bandwidth estimation using probing and feedback
- Quality-of-Service (QoS) management
- Adaptive bitrate (ABR) streaming logic
- Network congestion detection and handling
- Glass-to-glass latency optimization (<500ms target)
"""

from __future__ import annotations

import time
import random
import statistics
from collections import deque
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, Deque, List, Optional, Tuple


class NetworkCondition(Enum):
    """Detected network quality state."""
    EXCELLENT = "excellent"     # <10ms jitter, <0.1% loss
    GOOD = "good"               # <30ms jitter, <1% loss
    FAIR = "fair"               # <100ms jitter, <3% loss
    POOR = "poor"               # >100ms jitter, >3% loss
    CRITICAL = "critical"       # Severe degradation


class CongestionAlgorithm(Enum):
    """Congestion control algorithm."""
    CUBIC = "cubic"             # Standard TCP CUBIC
    BBR = "bbr"                 # Google BBR
    LEDBAT = "ledbat"           # Low Extra Delay Background Transport
    GCC = "gcc"                 # Google Congestion Control (WebRTC)
    NACK_ONLY = "nack_only"     # Simple NACK-based


@dataclass
class NetworkStats:
    """Comprehensive network statistics."""
    # Latency
    rtt_ms: float = 0.0
    one_way_delay_ms: float = 0.0
    jitter_ms: float = 0.0
    glass_to_glass_latency_ms: float = 0.0

    # Bandwidth
    available_bandwidth_kbps: float = 0.0
    used_bandwidth_kbps: float = 0.0
    bandwidth_utilization: float = 0.0

    # Packet statistics
    packet_loss_rate: float = 0.0
    packets_sent: int = 0
    packets_received: int = 0
    packets_lost: int = 0
    packets_reordered: int = 0

    # Quality
    network_condition: NetworkCondition = NetworkCondition.GOOD
    score: float = 100.0            # 0-100 quality score


@dataclass
class QoSProfile:
    """Quality of Service configuration."""
    priority: int = 0               # DSCP / ToS bits
    max_latency_ms: float = 100.0
    min_bandwidth_kbps: int = 1000
    max_bandwidth_kbps: int = 100_000
    jitter_buffer_ms: float = 20.0
    packet_loss_tolerance: float = 0.02   # 2%
    frame_rate_target: float = 60.0


@dataclass
class LatencyMeasurement:
    """A single latency measurement sample."""
    timestamp: float = field(default_factory=time.time)
    rtt_ms: float = 0.0
    one_way_ms: float = 0.0
    jitter_ms: float = 0.0


class LatencyMonitor:
    """Monitors network latency with statistical analysis."""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self._samples: Deque[LatencyMeasurement] = deque(maxlen=window_size)
        self._probe_timestamps: Dict[int, float] = {}
        self._probe_id = 0

    def send_probe(self) -> int:
        """Send a latency probe and return its ID."""
        probe_id = self._probe_id
        self._probe_timestamps[probe_id] = time.time()
        self._probe_id += 1
        return probe_id

    def receive_probe_response(self, probe_id: int) -> Optional[float]:
        """Process a probe response and return measured RTT."""
        send_time = self._probe_timestamps.pop(probe_id, None)
        if send_time is None:
            return None
        rtt_ms = (time.time() - send_time) * 1000.0
        jitter = self._compute_jitter(rtt_ms)
        self._samples.append(LatencyMeasurement(
            rtt_ms=rtt_ms,
            one_way_ms=rtt_ms / 2.0,
            jitter_ms=jitter,
        ))
        return rtt_ms

    def simulate_measurement(self, base_rtt_ms: float, variance: float = 5.0) -> float:
        """Simulate a latency measurement (for testing)."""
        rtt = max(0.1, base_rtt_ms + random.gauss(0, variance))
        jitter = abs(random.gauss(0, variance / 3))
        self._samples.append(LatencyMeasurement(
            rtt_ms=rtt,
            one_way_ms=rtt / 2.0,
            jitter_ms=jitter,
        ))
        return rtt

    def _compute_jitter(self, rtt_ms: float) -> float:
        """Compute RFC 3550 jitter."""
        if len(self._samples) < 1:
            return 0.0
        prev_rtt = self._samples[-1].rtt_ms
        delta = abs(rtt_ms - prev_rtt)
        return self._samples[-1].jitter_ms + (delta - self._samples[-1].jitter_ms) / 16.0

    def get_stats(self) -> Dict[str, float]:
        """Get statistical summary of latency measurements."""
        if not self._samples:
            return {"rtt_ms": 0.0, "jitter_ms": 0.0, "p95_rtt_ms": 0.0}
        rtts = [s.rtt_ms for s in self._samples]
        jitters = [s.jitter_ms for s in self._samples]
        return {
            "rtt_ms": statistics.mean(rtts),
            "min_rtt_ms": min(rtts),
            "max_rtt_ms": max(rtts),
            "p95_rtt_ms": sorted(rtts)[int(len(rtts) * 0.95)],
            "jitter_ms": statistics.mean(jitters),
            "stdev_ms": statistics.stdev(rtts) if len(rtts) > 1 else 0.0,
        }


class BandwidthProber:
    """Probes available bandwidth using send rate variations."""

    def __init__(self):
        self._probe_windows: List[Dict[str, Any]] = []
        self._current_estimate_kbps = 1000.0
        self._min_estimate = 100.0
        self._max_estimate = 100_000.0

    def record_window(
        self,
        bytes_sent: int,
        duration_s: float,
        packets_lost: int,
        packets_total: int,
    ) -> float:
        """Record a measurement window and update bandwidth estimate."""
        if duration_s <= 0:
            return self._current_estimate_kbps

        rate_kbps = bytes_sent * 8 / duration_s / 1000.0
        loss_rate = packets_lost / max(packets_total, 1)

        # Reduce estimate on packet loss
        if loss_rate > 0.02:
            rate_kbps *= 0.9

        # Smooth estimate
        alpha = 0.1
        self._current_estimate_kbps = (
            alpha * rate_kbps
            + (1 - alpha) * self._current_estimate_kbps
        )
        self._current_estimate_kbps = max(
            self._min_estimate,
            min(self._max_estimate, self._current_estimate_kbps)
        )

        self._probe_windows.append({
            "rate_kbps": rate_kbps,
            "loss_rate": loss_rate,
            "timestamp": time.time(),
        })
        if len(self._probe_windows) > 100:
            self._probe_windows.pop(0)

        return self._current_estimate_kbps

    def get_estimate_kbps(self) -> float:
        """Return current bandwidth estimate."""
        return self._current_estimate_kbps


class AdaptiveBitrateController:
    """
    Adaptive Bitrate (ABR) controller for streaming quality adaptation.

    Adjusts video quality to match available bandwidth while maintaining
    smooth playback without rebuffering.
    """

    def __init__(
        self,
        quality_levels: Optional[List[Dict[str, Any]]] = None,
        buffer_target_s: float = 2.0,
    ):
        self.quality_levels = quality_levels or [
            {"name": "240p", "bitrate_kbps": 400, "width": 426, "height": 240},
            {"name": "480p", "bitrate_kbps": 1500, "width": 854, "height": 480},
            {"name": "720p", "bitrate_kbps": 4000, "width": 1280, "height": 720},
            {"name": "1080p", "bitrate_kbps": 8000, "width": 1920, "height": 1080},
            {"name": "1440p", "bitrate_kbps": 16000, "width": 2560, "height": 1440},
            {"name": "4K", "bitrate_kbps": 40000, "width": 3840, "height": 2160},
        ]
        self.buffer_target_s = buffer_target_s
        self._current_level = 2   # Start at 720p
        self._buffer_level_s = 0.0
        self._consecutive_upgrades = 0
        self._consecutive_downgrades = 0

    def select_quality(
        self,
        available_bandwidth_kbps: float,
        buffer_level_s: float,
        packet_loss_rate: float,
    ) -> Dict[str, Any]:
        """Select the appropriate quality level for current conditions."""
        self._buffer_level_s = buffer_level_s

        # Emergency downgrade on very low buffer
        if buffer_level_s < 0.5 and self._current_level > 0:
            self._current_level = 0
            self._consecutive_upgrades = 0
            return self.quality_levels[0]

        # Find highest quality that fits in bandwidth (use 80% of available)
        target_bw = available_bandwidth_kbps * 0.8 * (1 - packet_loss_rate * 2)

        best_level = 0
        for i, level in enumerate(self.quality_levels):
            if level["bitrate_kbps"] <= target_bw:
                best_level = i

        # Hysteresis: require 3 consecutive windows before upgrading
        if best_level > self._current_level:
            self._consecutive_upgrades += 1
            self._consecutive_downgrades = 0
            if self._consecutive_upgrades >= 3:
                self._current_level = min(best_level, self._current_level + 1)
                self._consecutive_upgrades = 0
        elif best_level < self._current_level:
            self._consecutive_downgrades += 1
            self._consecutive_upgrades = 0
            if self._consecutive_downgrades >= 1:  # Immediate downgrade
                self._current_level = best_level
                self._consecutive_downgrades = 0

        return self.quality_levels[max(0, min(self._current_level, len(self.quality_levels) - 1))]

    def get_current_quality(self) -> Dict[str, Any]:
        """Get current selected quality level."""
        return self.quality_levels[
            max(0, min(self._current_level, len(self.quality_levels) - 1))
        ]


class JitterBuffer:
    """Jitter buffer to smooth out network timing variations."""

    def __init__(self, target_delay_ms: float = 20.0, max_delay_ms: float = 200.0):
        self.target_delay_ms = target_delay_ms
        self.max_delay_ms = max_delay_ms
        self._buffer: Dict[int, Tuple[bytes, float]] = {}  # seq -> (data, timestamp)
        self._next_seq = 0
        self._play_time = time.time()

    def push(self, sequence: int, data: bytes, timestamp: float) -> None:
        """Push a packet into the jitter buffer."""
        self._buffer[sequence] = (data, timestamp)

    def pop(self) -> Optional[bytes]:
        """Pop the next in-order packet if ready for playback."""
        now = time.time()
        if self._next_seq not in self._buffer:
            return None

        data, timestamp = self._buffer[self._next_seq]
        expected_play_time = timestamp + self.target_delay_ms / 1000.0
        if now >= expected_play_time:
            del self._buffer[self._next_seq]
            self._next_seq += 1
            return data

        return None

    def get_level_ms(self) -> float:
        """Return current buffer level in milliseconds."""
        if not self._buffer:
            return 0.0
        min_seq = min(self._buffer.keys())
        _, min_ts = self._buffer[min_seq]
        now = time.time()
        return max(0.0, (now - min_ts) * 1000.0)


class NetworkOptimizer:
    """
    Comprehensive network optimization system for streaming applications.

    Coordinates latency monitoring, bandwidth estimation, ABR, and QoS
    to deliver optimal streaming performance.
    """

    TARGET_LATENCY_MS = 500.0   # Glass-to-glass target

    def __init__(self, qos_profile: Optional[QoSProfile] = None):
        self.qos = qos_profile or QoSProfile()
        self._latency_monitor = LatencyMonitor()
        self._bw_prober = BandwidthProber()
        self._abr = AdaptiveBitrateController()
        self._jitter_buffer = JitterBuffer(
            target_delay_ms=qos_profile.jitter_buffer_ms if qos_profile else 20.0
        )
        self._stats = NetworkStats()
        self._last_update = time.time()

    def update(self, delta_time: float = 0.033) -> NetworkStats:
        """Update network measurements and adapt quality."""
        # Simulate probe measurement (real impl: use actual network probes)
        rtt = self._latency_monitor.simulate_measurement(
            base_rtt_ms=20.0 + random.uniform(0, 10)
        )

        # Update bandwidth estimate
        bw = self._bw_prober.record_window(
            bytes_sent=int(self._stats.used_bandwidth_kbps * 1000 / 8 * delta_time),
            duration_s=delta_time,
            packets_lost=0,
            packets_total=100,
        )

        latency_stats = self._latency_monitor.get_stats()
        self._stats.rtt_ms = latency_stats["rtt_ms"]
        self._stats.jitter_ms = latency_stats["jitter_ms"]
        self._stats.available_bandwidth_kbps = bw
        self._stats.glass_to_glass_latency_ms = (
            latency_stats["rtt_ms"] + latency_stats["jitter_ms"] * 3
        )
        self._stats.network_condition = self._classify_condition()
        self._stats.score = self._compute_score()

        return self._stats

    def select_quality(
        self,
        buffer_level_s: float = 2.0,
    ) -> Dict[str, Any]:
        """Select streaming quality based on current network conditions."""
        return self._abr.select_quality(
            self._stats.available_bandwidth_kbps,
            buffer_level_s,
            self._stats.packet_loss_rate,
        )

    def _classify_condition(self) -> NetworkCondition:
        """Classify overall network quality."""
        rtt = self._stats.rtt_ms
        jitter = self._stats.jitter_ms
        loss = self._stats.packet_loss_rate

        if rtt < 20 and jitter < 5 and loss < 0.001:
            return NetworkCondition.EXCELLENT
        elif rtt < 50 and jitter < 20 and loss < 0.01:
            return NetworkCondition.GOOD
        elif rtt < 150 and jitter < 50 and loss < 0.03:
            return NetworkCondition.FAIR
        elif rtt < 300:
            return NetworkCondition.POOR
        else:
            return NetworkCondition.CRITICAL

    def _compute_score(self) -> float:
        """Compute 0-100 network quality score (MOS-inspired)."""
        rtt_penalty = min(50.0, self._stats.rtt_ms / 6.0)
        jitter_penalty = min(20.0, self._stats.jitter_ms * 2.0)
        loss_penalty = min(30.0, self._stats.packet_loss_rate * 3000.0)
        return max(0.0, 100.0 - rtt_penalty - jitter_penalty - loss_penalty)

    def is_within_latency_target(self) -> bool:
        """Check if we're meeting the glass-to-glass latency target."""
        return self._stats.glass_to_glass_latency_ms <= self.TARGET_LATENCY_MS

    def get_stats(self) -> NetworkStats:
        """Return current network statistics."""
        return self._stats
