"""Temporal object tracking for Code-as-World."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
import json
import math


@dataclass
class TrackPoint:
    frame_index: int
    timestamp_seconds: float
    x: float
    y: float
    width: float
    height: float
    velocity_x: float = 0.0
    velocity_y: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ObjectTrack:
    track_id: str
    label: str
    points: list[TrackPoint] = field(
        default_factory=list,
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "track_id": self.track_id,
            "label": self.label,
            "points": [
                point.to_dict()
                for point in self.points
            ],
        }


@dataclass
class TrackingResult:
    source_path: str
    tracks: list[ObjectTrack] = field(
        default_factory=list,
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_path": self.source_path,
            "tracks": [
                track.to_dict()
                for track in self.tracks
            ],
        }


def _distance(
    left: TrackPoint,
    right: dict[str, Any],
) -> float:
    return math.hypot(
        left.x - float(right.get("x", 0.0)),
        left.y - float(right.get("y", 0.0)),
    )


def track_objects(
    detections_path: str | Path,
    max_distance: float = 0.25,
) -> TrackingResult:
    """Connect detections across frames into temporal tracks."""

    path = Path(
        detections_path
    ).expanduser().resolve()

    raw = json.loads(
        path.read_text(
            encoding="utf-8",
        )
    )

    detections = sorted(
        raw.get("detections", []),
        key=lambda item: (
            int(item.get("frame_index", 0)),
            str(item.get("id", "")),
        ),
    )

    tracks: list[ObjectTrack] = []
    counter = 0

    for detection in detections:
        label = str(
            detection.get(
                "label",
                "unknown_visual_object",
            )
        )

        best_track: ObjectTrack | None = None
        best_distance: float | None = None

        for track in tracks:
            if track.label != label:
                continue

            if not track.points:
                continue

            last = track.points[-1]

            if int(
                detection.get(
                    "frame_index",
                    0,
                )
            ) <= last.frame_index:
                continue

            distance = _distance(
                last,
                detection,
            )

            if (
                distance <= max_distance
                and (
                    best_distance is None
                    or distance < best_distance
                )
            ):
                best_track = track
                best_distance = distance

        point = TrackPoint(
            frame_index=int(
                detection.get(
                    "frame_index",
                    0,
                )
            ),
            timestamp_seconds=float(
                detection.get(
                    "timestamp_seconds",
                    0.0,
                )
            ),
            x=float(
                detection.get(
                    "x",
                    0.0,
                )
            ),
            y=float(
                detection.get(
                    "y",
                    0.0,
                )
            ),
            width=float(
                detection.get(
                    "width",
                    1.0,
                )
            ),
            height=float(
                detection.get(
                    "height",
                    1.0,
                )
            ),
        )

        if best_track is None:
            counter += 1

            best_track = ObjectTrack(
                track_id=f"track_{counter}",
                label=label,
            )

            tracks.append(
                best_track
            )
        elif best_track.points:
            previous = best_track.points[-1]

            delta_time = (
                point.timestamp_seconds
                - previous.timestamp_seconds
            )

            if delta_time > 0:
                point.velocity_x = (
                    point.x - previous.x
                ) / delta_time

                point.velocity_y = (
                    point.y - previous.y
                ) / delta_time

        best_track.points.append(
            point
        )

    return TrackingResult(
        source_path=str(
            raw.get(
                "source_path",
                "",
            )
        ),
        tracks=tracks,
    )


def save_tracks(
    result: TrackingResult,
    output: str | Path,
) -> Path:
    """Persist temporal tracking results."""

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
