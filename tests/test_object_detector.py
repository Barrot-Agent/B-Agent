import json

from barrot_agent.autonomy.code_as_world.object_detector import (
    detect_objects,
)


def test_detect_objects(tmp_path) -> None:
    frame = tmp_path / "frame.jpg"
    frame.write_bytes(b"placeholder")

    manifest = tmp_path / "scenes.json"

    manifest.write_text(
        json.dumps(
            {
                "source_path": "/tmp/video.mp4",
                "frames": [
                    {
                        "frame_index": 0,
                        "timestamp_seconds": 0.0,
                        "image_path": str(frame),
                        "mean_intensity": 10.0,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = detect_objects(
        manifest
    )

    assert len(result.detections) == 1
    assert (
        result.detections[0].frame_index
        == 0
    )
