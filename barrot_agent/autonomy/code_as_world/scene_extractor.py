"""Scene extraction for Code-as-World."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
import json


@dataclass
class ExtractedFrame:
    frame_index: int
    timestamp_seconds: float
    image_path: str
    mean_intensity: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Scene:
    scene_index: int
    start_frame: int
    end_frame: int
    start_time: float
    end_time: float
    representative_frame: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SceneExtraction:
    source_path: str
    fps: float
    frames: list[ExtractedFrame] = field(default_factory=list)
    scenes: list[Scene] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_path": self.source_path,
            "fps": self.fps,
            "frames": [
                frame.to_dict()
                for frame in self.frames
            ],
            "scenes": [
                scene.to_dict()
                for scene in self.scenes
            ],
        }


def extract_scenes(
    source: str | Path,
    output_dir: str | Path,
    sample_every: int = 30,
    scene_threshold: float = 25.0,
) -> SceneExtraction:
    """Extract sampled frames and detect coarse scene transitions."""

    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError(
            "OpenCV is required. Install opencv-python."
        ) from exc

    source_path = Path(source).expanduser().resolve()
    output_path = Path(output_dir)

    if not source_path.exists():
        raise FileNotFoundError(source_path)

    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    capture = cv2.VideoCapture(
        str(source_path)
    )

    if not capture.isOpened():
        raise RuntimeError(
            f"Unable to open video: {source_path}"
        )

    try:
        fps = float(
            capture.get(cv2.CAP_PROP_FPS)
        )

        if sample_every < 1:
            sample_every = 1

        frames: list[ExtractedFrame] = []

        previous_mean: float | None = None
        scene_boundaries: list[int] = []

        frame_index = 0

        while True:
            ok, frame = capture.read()

            if not ok:
                break

            if frame_index % sample_every == 0:
                gray = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2GRAY,
                )

                mean_intensity = float(
                    gray.mean()
                )

                image_name = (
                    f"frame_{frame_index:08d}.jpg"
                )

                image_file = (
                    output_path / image_name
                )

                cv2.imwrite(
                    str(image_file),
                    frame,
                )

                timestamp = (
                    frame_index / fps
                    if fps > 0
                    else 0.0
                )

                frames.append(
                    ExtractedFrame(
                        frame_index=frame_index,
                        timestamp_seconds=timestamp,
                        image_path=str(
                            image_file.resolve()
                        ),
                        mean_intensity=mean_intensity,
                    )
                )

                if previous_mean is not None:
                    difference = abs(
                        mean_intensity
                        - previous_mean
                    )

                    if difference >= scene_threshold:
                        scene_boundaries.append(
                            len(frames) - 1
                        )

                previous_mean = mean_intensity

            frame_index += 1

        scenes = build_scenes(
            frames,
            scene_boundaries,
        )

        return SceneExtraction(
            source_path=str(source_path),
            fps=fps,
            frames=frames,
            scenes=scenes,
        )

    finally:
        capture.release()


def build_scenes(
    frames: list[ExtractedFrame],
    boundaries: list[int],
) -> list[Scene]:
    """Convert frame boundaries into structured scenes."""

    if not frames:
        return []

    starts = [0] + boundaries
    scenes: list[Scene] = []

    for scene_index, start in enumerate(starts):
        end = (
            starts[scene_index + 1] - 1
            if scene_index + 1 < len(starts)
            else len(frames) - 1
        )

        first = frames[start]
        last = frames[end]

        scenes.append(
            Scene(
                scene_index=scene_index,
                start_frame=first.frame_index,
                end_frame=last.frame_index,
                start_time=first.timestamp_seconds,
                end_time=last.timestamp_seconds,
                representative_frame=first.image_path,
            )
        )

    return scenes


def save_scene_manifest(
    extraction: SceneExtraction,
    output: str | Path,
) -> Path:
    """Persist structured scene extraction."""

    output_path = Path(output)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            extraction.to_dict(),
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    return output_path
