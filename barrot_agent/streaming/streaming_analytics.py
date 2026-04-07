"""
Streaming Analytics - Quality metrics, bitrate tracking, and stream health reporting.

Implements:
- Real-time bitrate tracking and visualization
- Latency measurement (glass-to-glass)
- Packet loss analysis
- Frame rate monitoring
- Visual quality metrics (PSNR, SSIM)
- Stream health scoring and reporting
"""

from __future__ import annotations

import math
import time
import statistics
from collections import deque
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Deque, Dict, List, Optional, Tuple


class StreamHealth(Enum):
    """Overall stream health classification."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class StreamMetrics:
    """Point-in-time stream quality metrics."""
    timestamp: float = field(default_factory=time.time)
    # Bitrate
    video_bitrate_kbps: float = 0.0
    audio_bitrate_kbps: float = 0.0
    total_bitrate_kbps: float = 0.0
    # Latency
    encode_latency_ms: float = 0.0
    decode_latency_ms: float = 0.0
    network_latency_ms: float = 0.0
    glass_to_glass_ms: float = 0.0
    # Frame stats
    fps: float = 0.0
    dropped_frames: int = 0
    total_frames: int = 0
    drop_rate: float = 0.0
    # Packet stats
    packet_loss_rate: float = 0.0
    jitter_ms: float = 0.0
    # Quality scores
    psnr_db: float = 0.0
    ssim: float = 0.0
    vmaf: float = 0.0
    # Health
    health: StreamHealth = StreamHealth.HEALTHY
    health_score: float = 100.0


@dataclass
class BitrateWindow:
    """Rolling window for bitrate calculation."""
    bytes_total: int = 0
    start_time: float = field(default_factory=time.time)
    samples: Deque[Tuple[float, int]] = field(
        default_factory=lambda: deque(maxlen=1000)
    )  # (timestamp, bytes)

    def record(self, bytes_count: int) -> None:
        """Record bytes transmitted."""
        self.bytes_total += bytes_count
        self.samples.append((time.time(), bytes_count))

    def get_bitrate_kbps(self, window_s: float = 1.0) -> float:
        """Get bitrate over the last window_s seconds."""
        now = time.time()
        cutoff = now - window_s
        window_bytes = sum(b for t, b in self.samples if t >= cutoff)
        return window_bytes * 8 / window_s / 1000.0


class PSNRCalculator:
    """Computes PSNR (Peak Signal-to-Noise Ratio) between frames."""

    @staticmethod
    def compute(
        original: bytes, compressed: bytes, max_value: float = 255.0
    ) -> float:
        """
        Compute PSNR in dB.

        Higher is better. Typical values:
        - > 40 dB: Very good
        - 30-40 dB: Good
        - < 30 dB: Noticeable artifacts
        """
        if len(original) != len(compressed) or len(original) == 0:
            return 0.0

        n = len(original)
        mse = sum(
            (original[i] - compressed[i]) ** 2 for i in range(min(n, 10000))
        ) / min(n, 10000)

        if mse == 0:
            return float("inf")
        return 20 * math.log10(max_value) - 10 * math.log10(mse)


class SSIMCalculator:
    """Computes SSIM (Structural Similarity Index) between frames."""

    _C1 = (0.01 * 255) ** 2
    _C2 = (0.03 * 255) ** 2

    def compute_patch(
        self,
        patch_x: List[float],
        patch_y: List[float],
    ) -> float:
        """Compute SSIM for an image patch."""
        n = len(patch_x)
        if n == 0 or len(patch_y) != n:
            return 1.0

        mu_x = sum(patch_x) / n
        mu_y = sum(patch_y) / n
        sigma_x2 = sum((v - mu_x) ** 2 for v in patch_x) / n
        sigma_y2 = sum((v - mu_y) ** 2 for v in patch_y) / n
        sigma_xy = sum((patch_x[i] - mu_x) * (patch_y[i] - mu_y) for i in range(n)) / n

        numerator = (2 * mu_x * mu_y + self._C1) * (2 * sigma_xy + self._C2)
        denominator = (mu_x ** 2 + mu_y ** 2 + self._C1) * (sigma_x2 + sigma_y2 + self._C2)
        return numerator / max(denominator, 1e-8)

    def compute(
        self, original: bytes, compressed: bytes, patch_size: int = 64
    ) -> float:
        """Compute mean SSIM over sampled patches."""
        if len(original) == 0 or len(compressed) != len(original):
            return 1.0

        ssim_values = []
        step = max(1, len(original) // (patch_size * 4))
        for start in range(0, len(original) - patch_size, step):
            patch_x = [float(original[i]) for i in range(start, start + patch_size)]
            patch_y = [float(compressed[i]) for i in range(start, start + patch_size)]
            ssim_values.append(self.compute_patch(patch_x, patch_y))

        return statistics.mean(ssim_values) if ssim_values else 1.0


class FrameRateMonitor:
    """Tracks frame rate with configurable measurement windows."""

    def __init__(self, window_s: float = 1.0):
        self.window_s = window_s
        self._timestamps: Deque[float] = deque()
        self._dropped: int = 0
        self._total: int = 0

    def record_frame(self, dropped: bool = False) -> None:
        """Record a frame presentation event."""
        now = time.time()
        self._timestamps.append(now)
        self._total += 1
        if dropped:
            self._dropped += 1

        # Remove old timestamps
        cutoff = now - self.window_s
        while self._timestamps and self._timestamps[0] < cutoff:
            self._timestamps.popleft()

    def get_fps(self) -> float:
        """Get the current frame rate."""
        if len(self._timestamps) < 2:
            return 0.0
        span = self._timestamps[-1] - self._timestamps[0]
        if span <= 0:
            return 0.0
        return (len(self._timestamps) - 1) / span

    def get_drop_rate(self) -> float:
        """Get the frame drop rate (0.0 - 1.0)."""
        if self._total == 0:
            return 0.0
        return self._dropped / self._total


class PacketLossAnalyzer:
    """Analyzes packet loss patterns and severity."""

    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self._received: Deque[bool] = deque(maxlen=window_size)
        self._burst_threshold = 3
        self._loss_count = 0
        self._total_count = 0

    def record_packet(self, received: bool) -> None:
        """Record whether a packet was received or lost."""
        self._received.append(received)
        self._total_count += 1
        if not received:
            self._loss_count += 1

    def get_loss_rate(self) -> float:
        """Get the current packet loss rate."""
        if not self._received:
            return 0.0
        lost = sum(1 for r in self._received if not r)
        return lost / len(self._received)

    def get_burst_loss_count(self) -> int:
        """Count the number of burst loss events."""
        bursts = 0
        consecutive = 0
        for received in self._received:
            if not received:
                consecutive += 1
                if consecutive == self._burst_threshold:
                    bursts += 1
            else:
                consecutive = 0
        return bursts

    def get_stats(self) -> Dict[str, Any]:
        """Return packet loss statistics."""
        return {
            "loss_rate": self.get_loss_rate(),
            "burst_events": self.get_burst_loss_count(),
            "total_packets": self._total_count,
            "lost_packets": self._loss_count,
        }


class StreamHealthScorer:
    """Computes an overall stream health score."""

    @staticmethod
    def compute_score(metrics: StreamMetrics) -> Tuple[float, StreamHealth]:
        """
        Compute a 0-100 health score from stream metrics.

        Returns (score, health_classification).
        """
        score = 100.0

        # Latency penalties
        if metrics.glass_to_glass_ms > 500:
            score -= 30
        elif metrics.glass_to_glass_ms > 200:
            score -= 15
        elif metrics.glass_to_glass_ms > 100:
            score -= 5

        # Packet loss penalties
        if metrics.packet_loss_rate > 0.05:
            score -= 30
        elif metrics.packet_loss_rate > 0.01:
            score -= 15
        elif metrics.packet_loss_rate > 0.001:
            score -= 5

        # Frame drop penalties
        if metrics.drop_rate > 0.1:
            score -= 20
        elif metrics.drop_rate > 0.02:
            score -= 10

        # PSNR quality
        if 0 < metrics.psnr_db < 30:
            score -= 15
        elif 30 <= metrics.psnr_db < 35:
            score -= 5

        # Jitter
        if metrics.jitter_ms > 50:
            score -= 10
        elif metrics.jitter_ms > 20:
            score -= 5

        score = max(0.0, min(100.0, score))

        if score >= 80:
            health = StreamHealth.HEALTHY
        elif score >= 60:
            health = StreamHealth.DEGRADED
        elif score >= 40:
            health = StreamHealth.POOR
        else:
            health = StreamHealth.CRITICAL

        return score, health


class StreamingAnalytics:
    """
    Comprehensive streaming analytics and quality monitoring system.

    Tracks all aspects of stream quality including:
    - Bitrate utilization and trends
    - Latency at each pipeline stage
    - Visual quality metrics (PSNR, SSIM)
    - Packet loss patterns
    - Frame rate stability
    - Overall health scoring
    """

    def __init__(self, report_interval_s: float = 5.0):
        self.report_interval_s = report_interval_s
        self._video_bitrate = BitrateWindow()
        self._audio_bitrate = BitrateWindow()
        self._fps_monitor = FrameRateMonitor()
        self._loss_analyzer = PacketLossAnalyzer()
        self._psnr_calc = PSNRCalculator()
        self._ssim_calc = SSIMCalculator()
        self._health_scorer = StreamHealthScorer()
        self._current_metrics = StreamMetrics()
        self._metrics_history: List[StreamMetrics] = []
        self._last_report_time = time.time()
        self._latency_samples: Deque[float] = deque(maxlen=100)

    def record_video_bytes(self, byte_count: int) -> None:
        """Record video bytes transmitted."""
        self._video_bitrate.record(byte_count)

    def record_audio_bytes(self, byte_count: int) -> None:
        """Record audio bytes transmitted."""
        self._audio_bitrate.record(byte_count)

    def record_frame(self, dropped: bool = False) -> None:
        """Record a frame presentation event."""
        self._fps_monitor.record_frame(dropped)

    def record_packet(self, received: bool) -> None:
        """Record a packet received/lost event."""
        self._loss_analyzer.record_packet(received)

    def record_latency(
        self,
        encode_ms: float,
        network_ms: float,
        decode_ms: float,
    ) -> None:
        """Record latency measurements for each pipeline stage."""
        g2g = encode_ms + network_ms + decode_ms
        self._latency_samples.append(g2g)
        self._current_metrics.encode_latency_ms = encode_ms
        self._current_metrics.network_latency_ms = network_ms
        self._current_metrics.decode_latency_ms = decode_ms
        self._current_metrics.glass_to_glass_ms = g2g

    def compute_visual_quality(
        self,
        original: bytes,
        encoded: bytes,
    ) -> Dict[str, float]:
        """Compute PSNR and SSIM quality metrics."""
        psnr = self._psnr_calc.compute(original, encoded)
        ssim = self._ssim_calc.compute(original, encoded)
        self._current_metrics.psnr_db = psnr if psnr != float("inf") else 60.0
        self._current_metrics.ssim = ssim
        return {"psnr_db": self._current_metrics.psnr_db, "ssim": ssim}

    def update(self) -> StreamMetrics:
        """Update all metrics and return current state."""
        # Update bitrate
        self._current_metrics.video_bitrate_kbps = (
            self._video_bitrate.get_bitrate_kbps()
        )
        self._current_metrics.audio_bitrate_kbps = (
            self._audio_bitrate.get_bitrate_kbps()
        )
        self._current_metrics.total_bitrate_kbps = (
            self._current_metrics.video_bitrate_kbps
            + self._current_metrics.audio_bitrate_kbps
        )

        # Update frame rate
        self._current_metrics.fps = self._fps_monitor.get_fps()
        self._current_metrics.drop_rate = self._fps_monitor.get_drop_rate()

        # Update packet loss
        self._current_metrics.packet_loss_rate = (
            self._loss_analyzer.get_loss_rate()
        )

        # Compute health score
        score, health = self._health_scorer.compute_score(self._current_metrics)
        self._current_metrics.health_score = score
        self._current_metrics.health = health
        self._current_metrics.timestamp = time.time()

        # Store in history
        now = time.time()
        if now - self._last_report_time >= self.report_interval_s:
            self._metrics_history.append(
                StreamMetrics(**vars(self._current_metrics))
            )
            if len(self._metrics_history) > 1000:
                self._metrics_history.pop(0)
            self._last_report_time = now

        return self._current_metrics

    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive stream quality report."""
        metrics = self.update()
        latency_list = list(self._latency_samples)

        return {
            "summary": {
                "health": metrics.health.value,
                "health_score": round(metrics.health_score, 1),
                "fps": round(metrics.fps, 1),
                "bitrate_kbps": round(metrics.total_bitrate_kbps, 1),
                "glass_to_glass_ms": round(metrics.glass_to_glass_ms, 1),
            },
            "quality": {
                "psnr_db": round(metrics.psnr_db, 2),
                "ssim": round(metrics.ssim, 4),
                "vmaf": round(metrics.vmaf, 1),
            },
            "network": {
                "packet_loss_rate": round(metrics.packet_loss_rate, 4),
                "jitter_ms": round(metrics.jitter_ms, 2),
                "avg_latency_ms": round(
                    statistics.mean(latency_list) if latency_list else 0.0, 1
                ),
                "p95_latency_ms": round(
                    sorted(latency_list)[int(len(latency_list) * 0.95)]
                    if len(latency_list) >= 20
                    else 0.0,
                    1,
                ),
            },
            "frames": {
                "total": metrics.total_frames,
                "dropped": metrics.dropped_frames,
                "drop_rate": round(metrics.drop_rate, 4),
            },
            "history_length": len(self._metrics_history),
        }

    def get_current_metrics(self) -> StreamMetrics:
        """Return the current metrics snapshot."""
        return self._current_metrics

    def get_history(self) -> List[StreamMetrics]:
        """Return metrics history."""
        return self._metrics_history.copy()
