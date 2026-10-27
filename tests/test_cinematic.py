import pytest

from barrot_agent.cinematic import ProductionPipeline


@pytest.mark.cinematic
def test_cinematic_project_pipeline(tmp_path):
    pipeline = ProductionPipeline(tmp_path / "projects")

    project = pipeline.start_project(
        "Dark Legion Prototype",
        "A hero confronts an interdimensional invasion.",
        {"genre": "superhero action"},
    )

    pipeline.characters.register(
        "Hero",
        {"status": "alive", "costume": "red"},
    )

    scene = pipeline.add_scene(
        number=1,
        title="Arrival",
        location="City",
        time_of_day="Night",
        purpose="Introduce the threat",
        characters=["Hero"],
        action="The hero arrives as the invasion begins.",
        continuity_assertions=[
            {"subject": "Hero", "attribute": "location", "value": "City"}
        ],
    )

    pipeline.add_shot(
        scene_id=scene.scene_id,
        number=1,
        framing="Wide",
        camera_movement="Crane down",
        action="The city skyline fractures with light.",
    )

    plan_path = pipeline.save_plan()
    plan = pipeline.export_plan()

    assert project.name == "Dark Legion Prototype"
    assert plan_path.exists()
    assert plan["project"]["name"] == "Dark Legion Prototype"
    assert pipeline.production_status()["scenes"] == 1
    assert pipeline.production_status()["shots"] == 1
    assert pipeline.production_status()["ledger_valid"] is True


@pytest.mark.cinematic
def test_continuity_conflict_rejects_scene(tmp_path):
    pipeline = ProductionPipeline(tmp_path / "projects")
    pipeline.start_project("Continuity Test", "Test continuity.")

    pipeline.add_scene(
        number=1,
        title="First",
        location="Lab",
        time_of_day="Day",
        purpose="Establish state",
        continuity_assertions=[
            {"subject": "Hero", "attribute": "location", "value": "Earth"}
        ],
    )

    with pytest.raises(ValueError, match="Continuity conflict"):
        pipeline.add_scene(
            number=2,
            title="Contradiction",
            location="Space",
            time_of_day="Day",
            purpose="Test conflict",
            continuity_assertions=[
                {"subject": "Hero", "attribute": "location", "value": "Mars"}
            ],
        )

    assert len(pipeline.scenes.scenes) == 1
