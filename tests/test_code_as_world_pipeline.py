from barrot_agent.autonomy.code_as_world.pipeline import (
    PipelineResult,
    PipelineStage,
)


def test_pipeline_result_serialization() -> None:
    result = PipelineResult(
        source_path="/tmp/video.mp4",
        passed=True,
        stages=[
            PipelineStage(
                name="test",
                status="implemented",
            )
        ],
        outputs={
            "world": "/tmp/world.json",
        },
    )

    data = result.to_dict()

    assert data["passed"] is True
    assert data["stages"][0]["name"] == "test"
    assert data["outputs"]["world"] == "/tmp/world.json"
