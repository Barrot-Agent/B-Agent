import json

from barrot_agent.autonomy.code_as_world.object_tracker import (
    track_objects,
)


def test_track_objects_across_frames(tmp_path) -> None:
    detections = tmp_path / "detections.json"

    detections.write_text(
        json.dumps(
            {
                "source_path": "/tmp/video.mp4",
                "detections": [
                    {
                        "id": "a",
                        "label": "unknown_visual_object",
                        "frame_index": 0,
                        "timestamp_seconds": 0.0,
                        "x": 0.10,
                        "y": 0.10,
                        "width": 0.2,
                        "height": 0.2,
                    },
                    {
                        "id": "b",
                        "label": "unknown_visual_object",
                        "frame_index": 1,
                        "timestamp_seconds": 1.0,
                        "x": 0.20,
                        "y": 0.10,
                        "width": 0.2,
                        "height": 0.2,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    result = track_objects(
        detections
    )

    assert len(result.tracks) == 1

    track = result.tracks[0]

    assert len(track.points) == 2
    assert track.points[1].velocity_x == 0.1
