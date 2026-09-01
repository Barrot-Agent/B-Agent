"""Video observation foundation for Code-as-World."""

from __future__ import annotations

from pathlib import Path
import json

from barrot_agent.autonomy.code_as_world.models import (
    FrameObservation,
    VideoObservation,
)


def observe_video(
    source: str | Path,
    sample_every: int = 30,
) -> VideoObservation:
    """
    Create a structured observation manifest.

    Uses OpenCV when available. The result intentionally contains
    observation metadata only. Scene interpretation is implemented
    in later capability phases.
    """

    source_path = Path(source).expanduser().resolve()

    if not source_path.exists():
        raise FileNotFoundError(source_path)

    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError(
            "OpenCV is required for video observation. "
            "Install opencv-python."
        ) from exc

    capture = cv2.VideoCapture(
        str(source_path),
    )

    if not capture.isOpened():
        raise RuntimeError(
            f"Unable to open video: {source_path}"
        )

    try:
        frame_count = int(
            capture.get(cv2.CAP_PROP_FRAME_COUNT)
        )

        fps = float(
            capture.get(cv2.CAP_PROP_FPS)
        )

        if fps <= 0:
            fps = 0.0
            duration_seconds = 0.0
        else:
            duration_seconds = frame_count / fps

        sampled_frames = []

        if sample_every < 1:
            sample_every = 1

        for frame_index in range(
            0,
            frame_count,
            sample_every,
        ):
            timestamp_seconds = (
                frame_index / fps
                if fps > 0
                else 0.0
            )

            sampled_frames.append(
                FrameObservation(
                    frame_index=frame_index,
                    timestamp_seconds=timestamp_seconds,
                    source_path=str(source_path),
                )
            )

        return VideoObservation(
            source_path=str(source_path),
            frame_count=frame_count,
            fps=fps,
            duration_seconds=duration_seconds,
            sampled_frames=sampled_frames,
        )

    finally:
        capture.release()


def save_observation(
    observation: VideoObservation,
    output: str | Path,
) -> Path:
    """Persist an observation manifest."""

    output_path = Path(output)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            observation.to_dict(),
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    return output_path
