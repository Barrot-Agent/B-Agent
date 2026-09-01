from barrot_agent.autonomy.code_as_world.scene_extractor import (
    ExtractedFrame,
    build_scenes,
)


def test_build_scenes_single_scene() -> None:
    frames = [
        ExtractedFrame(
            frame_index=0,
            timestamp_seconds=0.0,
            image_path="frame0.jpg",
            mean_intensity=10.0,
        ),
        ExtractedFrame(
            frame_index=30,
            timestamp_seconds=1.0,
            image_path="frame30.jpg",
            mean_intensity=12.0,
        ),
    ]

    scenes = build_scenes(
        frames,
        [],
    )

    assert len(scenes) == 1
    assert scenes[0].start_frame == 0
    assert scenes[0].end_frame == 30


def test_build_scenes_boundary() -> None:
    frames = [
        ExtractedFrame(
            frame_index=0,
            timestamp_seconds=0.0,
            image_path="frame0.jpg",
            mean_intensity=10.0,
        ),
        ExtractedFrame(
            frame_index=30,
            timestamp_seconds=1.0,
            image_path="frame30.jpg",
            mean_intensity=90.0,
        ),
    ]

    scenes = build_scenes(
        frames,
        [1],
    )

    assert len(scenes) == 2
    assert scenes[1].start_frame == 30
