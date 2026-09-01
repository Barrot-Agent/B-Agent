"""Core structured models for Code-as-World."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class FrameObservation:
    """A single sampled video frame."""

    frame_index: int
    timestamp_seconds: float
    source_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class VideoObservation:
    """Structured metadata describing a video observation."""

    source_path: str
    frame_count: int
    fps: float
    duration_seconds: float
    sampled_frames: list[FrameObservation] = field(
        default_factory=list,
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_path": self.source_path,
            "frame_count": self.frame_count,
            "fps": self.fps,
            "duration_seconds": self.duration_seconds,
            "sampled_frames": [
                frame.to_dict()
                for frame in self.sampled_frames
            ],
        }
