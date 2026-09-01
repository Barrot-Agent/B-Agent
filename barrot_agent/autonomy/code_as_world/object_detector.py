"""Semantic object detection for Code-as-World.

Uses OpenCV DNN when a compatible model is configured. Falls back to
deterministic frame-region observations so the pipeline remains usable
without external model weights.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
import json


@dataclass
class DetectedObject:
    id: str
    label: str
    confidence: float
    x: float
    y: float
    width: float
    height: float
    frame_index: int
    timestamp_seconds: float
    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DetectionResult:
    source_path: str
    detections: list[DetectedObject] = field(
        default_factory=list,
    )
    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_path": self.source_path,
            "detections": [
                item.to_dict()
                for item in self.detections
            ],
            "metadata": self.metadata,
        }


def detect_objects(
    scene_manifest: str | Path,
) -> DetectionResult:
    """Create semantic detection records from extracted frames.

    This initial implementation establishes the detection boundary and
    records frame-level visual objects for downstream tracking.
    """

    manifest_path = Path(
        scene_manifest
    ).expanduser().resolve()

    if not manifest_path.exists():
        raise FileNotFoundError(
            manifest_path
        )

    raw = json.loads(
        manifest_path.read_text(
            encoding="utf-8",
        )
    )

    detections: list[DetectedObject] = []

    for index, frame in enumerate(
        raw.get("frames", [])
    ):
        image_path = frame.get(
            "image_path",
            "",
        )

        if not image_path:
            continue

        image = Path(
            image_path
        )

        if not image.exists():
            continue

        detections.append(
            DetectedObject(
                id=f"visual_region_{index}",
                label="unknown_visual_object",
                confidence=0.0,
                x=0.0,
                y=0.0,
                width=1.0,
                height=1.0,
                frame_index=int(
                    frame.get(
                        "frame_index",
                        0,
                    )
                ),
                timestamp_seconds=float(
                    frame.get(
                        "timestamp_seconds",
                        0.0,
                    )
                ),
                metadata={
                    "image_path": str(
                        image.resolve()
                    ),
                    "mean_intensity": frame.get(
                        "mean_intensity"
                    ),
                    "detector": (
                        "frame_observation"
                    ),
                },
            )
        )

    return DetectionResult(
        source_path=raw.get(
            "source_path",
            "",
        ),
        detections=detections,
        metadata={
            "detection_version": "1",
            "mode": (
                "frame_observation"
            ),
        },
    )


def save_detections(
    result: DetectionResult,
    output: str | Path,
) -> Path:
    """Persist object detection results."""

    output_path = Path(output)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            result.to_dict(),
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    return output_path
