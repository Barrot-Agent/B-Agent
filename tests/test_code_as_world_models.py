from barrot_agent.autonomy.code_as_world.models import (
    FrameObservation,
    VideoObservation,
)


def test_observation_serialization() -> None:
    frame = FrameObservation(
        frame_index=10,
        timestamp_seconds=0.5,
        source_path="/tmp/video.mp4",
    )

    observation = VideoObservation(
        source_path="/tmp/video.mp4",
        frame_count=100,
        fps=20.0,
        duration_seconds=5.0,
        sampled_frames=[frame],
    )

    data = observation.to_dict()

    assert data["frame_count"] == 100
    assert data["sampled_frames"][0]["frame_index"] == 10
