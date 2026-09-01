import json

from barrot_agent.autonomy.code_as_world.world_builder import (
    build_world,
)


def test_build_world(tmp_path) -> None:
    manifest = tmp_path / "scenes.json"

    manifest.write_text(
        json.dumps(
            {
                "source_path": (
                    "/tmp/video.mp4"
                ),
                "fps": 30.0,
                "scenes": [
                    {
                        "scene_index": 0,
                        "start_frame": 0,
                        "end_frame": 30,
                        "start_time": 0.0,
                        "end_time": 1.0,
                        "representative_frame": (
                            "/tmp/frame.jpg"
                        ),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    world = build_world(
        manifest
    )

    assert len(world.states) == 1

    state = world.states[0]

    assert len(state.objects) == 1
    assert (
        state.objects[0].kind
        == "scene_anchor"
    )

    assert (
        state.objects[0].metadata[
            "scene_index"
        ]
        == 0
    )
