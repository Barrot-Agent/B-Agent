"""
Game Loop - Main game loop with fixed/variable timestep and frame pacing.

Implements:
- Fixed timestep for deterministic physics/game logic
- Variable timestep for rendering
- Frame pacing with sleep/wake scheduling
- Performance profiling per loop stage
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional


class LoopMode(Enum):
    """Game loop timing mode."""
    FIXED = auto()      # Fixed delta time (deterministic)
    VARIABLE = auto()   # Variable delta time
    HYBRID = auto()     # Fixed update + variable render


@dataclass
class GameLoopConfig:
    """Configuration for the game loop."""
    mode: LoopMode = LoopMode.HYBRID
    target_fps: float = 60.0
    fixed_timestep: float = 1.0 / 60.0
    max_frame_time: float = 0.25    # Clamp large deltas to prevent spiral of death
    max_updates_per_frame: int = 5  # Prevent infinite catch-up
    sleep_granularity_ms: float = 1.0


@dataclass
class FrameStats:
    """Statistics for a single frame."""
    frame_number: int = 0
    delta_time: float = 0.0
    fps: float = 0.0
    update_time_ms: float = 0.0
    render_time_ms: float = 0.0
    total_time_ms: float = 0.0
    accumulated_lag: float = 0.0


class GameLoop:
    """
    Production game loop with precise timing and profiling.

    Implements the semi-fixed timestep pattern:
    - Physics/game logic runs at a fixed rate
    - Rendering runs as fast as possible
    - Interpolation factor passed to renderer for smooth visuals
    """

    def __init__(self, config: Optional[GameLoopConfig] = None):
        self.config = config or GameLoopConfig()
        self._running = False
        self._paused = False
        self._frame_count = 0
        self._accumulated_time = 0.0
        self._last_time = 0.0
        self._fps_samples: List[float] = []

        # Callbacks
        self._on_update: Optional[Callable[[float], None]] = None
        self._on_render: Optional[Callable[[float], None]] = None
        self._on_fixed_update: Optional[Callable[[float], None]] = None
        self._on_frame_start: Optional[Callable[[], None]] = None
        self._on_frame_end: Optional[Callable[[FrameStats], None]] = None

    def on_update(self, callback: Callable[[float], None]) -> None:
        """Set the per-frame update callback (receives delta_time)."""
        self._on_update = callback

    def on_fixed_update(self, callback: Callable[[float], None]) -> None:
        """Set the fixed timestep update callback."""
        self._on_fixed_update = callback

    def on_render(self, callback: Callable[[float], None]) -> None:
        """Set the render callback (receives interpolation alpha)."""
        self._on_render = callback

    def on_frame_end(self, callback: Callable[[FrameStats], None]) -> None:
        """Set a callback called at the end of each frame with stats."""
        self._on_frame_end = callback

    def start(self) -> None:
        """Start the game loop."""
        self._running = True
        self._last_time = time.perf_counter()
        self._accumulated_time = 0.0

    def stop(self) -> None:
        """Stop the game loop."""
        self._running = False

    def pause(self) -> None:
        """Pause the game loop (skips updates but not rendering)."""
        self._paused = True

    def resume(self) -> None:
        """Resume the game loop."""
        self._paused = False
        self._last_time = time.perf_counter()  # Reset time to avoid accumulated lag

    def tick(self) -> FrameStats:
        """
        Execute one iteration of the game loop.

        Returns statistics for this frame. Call this in your own loop.
        """
        now = time.perf_counter()
        frame_time = min(now - self._last_time, self.config.max_frame_time)
        self._last_time = now
        self._frame_count += 1

        stats = FrameStats(frame_number=self._frame_count)
        stats.delta_time = frame_time

        if self._on_frame_start:
            self._on_frame_start()

        update_start = time.perf_counter()

        if not self._paused:
            if self.config.mode == LoopMode.FIXED:
                # Fixed timestep: run update exactly once
                if self._on_update:
                    self._on_update(self.config.fixed_timestep)
                if self._on_fixed_update:
                    self._on_fixed_update(self.config.fixed_timestep)

            elif self.config.mode == LoopMode.HYBRID:
                # Accumulate time and run fixed updates as needed
                self._accumulated_time += frame_time
                updates = 0
                while (
                    self._accumulated_time >= self.config.fixed_timestep
                    and updates < self.config.max_updates_per_frame
                ):
                    if self._on_fixed_update:
                        self._on_fixed_update(self.config.fixed_timestep)
                    self._accumulated_time -= self.config.fixed_timestep
                    updates += 1

            else:  # VARIABLE
                if self._on_update:
                    self._on_update(frame_time)

        stats.update_time_ms = (time.perf_counter() - update_start) * 1000.0
        stats.accumulated_lag = self._accumulated_time

        # Render with interpolation alpha
        render_start = time.perf_counter()
        if self._on_render:
            alpha = self._accumulated_time / max(self.config.fixed_timestep, 1e-8)
            self._on_render(alpha)
        stats.render_time_ms = (time.perf_counter() - render_start) * 1000.0
        stats.total_time_ms = stats.update_time_ms + stats.render_time_ms

        # FPS calculation
        self._fps_samples.append(frame_time)
        if len(self._fps_samples) > 60:
            self._fps_samples.pop(0)
        avg_frame = sum(self._fps_samples) / len(self._fps_samples)
        stats.fps = 1.0 / max(avg_frame, 1e-8)

        # Frame pacing: sleep if running too fast
        target_frame_time = 1.0 / max(self.config.target_fps, 1.0)
        elapsed = time.perf_counter() - now
        if elapsed < target_frame_time:
            sleep_time = target_frame_time - elapsed
            if sleep_time > 0.001:
                time.sleep(sleep_time)

        if self._on_frame_end:
            self._on_frame_end(stats)

        return stats

    def run(self, max_frames: Optional[int] = None) -> None:
        """Run the game loop until stopped or max_frames reached."""
        self.start()
        while self._running:
            self.tick()
            if max_frames and self._frame_count >= max_frames:
                break
        self.stop()

    def get_frame_count(self) -> int:
        return self._frame_count

    def is_running(self) -> bool:
        return self._running

    def get_average_fps(self) -> float:
        if not self._fps_samples:
            return 0.0
        avg = sum(self._fps_samples) / len(self._fps_samples)
        return 1.0 / max(avg, 1e-8)
