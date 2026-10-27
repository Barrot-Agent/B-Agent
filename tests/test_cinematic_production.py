from barrot_agent.cinematic import (
    ProductionPipeline,
    ContinuityEngine,
    StoryBible,
)


def test_story_bible_preserves_locked_facts():
    bible = StoryBible()
    bible.set_fact("hero_origin", "Bronx", locked=True)

    try:
        bible.set_fact("hero_origin", "Mars")
        assert False, "Expected locked fact protection"
    except ValueError:
        pass


def test_continuity_engine_detects_conflict():
    engine = ContinuityEngine()
    engine.record("scene-1", "Hero", "location", "New York")

    conflict = engine.check(
        "scene-2",
        "Hero",
        "location",
        "Tokyo",
    )

    assert conflict is not None
    assert conflict.established_value == "New York"


def test_continuity_ledger_integrity():
    engine = ContinuityEngine()
    engine.record("scene-1", "Hero", "injury", "none")
    engine.record("scene-2", "Hero", "injury", "arm injured")

    assert engine.verify_integrity() is True


def test_production_pipeline_creates_project_and_scenes(tmp_path):
    pipeline = ProductionPipeline(str(tmp_path))

    project = pipeline.start_project(
        "Dark Legion",
        "A hero defends Earth from an interdimensional invasion.",
    )

    assert project.name == "Dark Legion"

    scene = pipeline.add_scene(
        number=1,
        title="The Arrival",
        location="New York",
        time_of_day="Night",
        purpose="Introduce the threat",
        characters=["Hero"],
        action="A dimensional rift opens above the city.",
        continuity_assertions=[
            {
                "subject": "Hero",
                "attribute": "location",
                "value": "New York",
            }
        ],
    )

    assert scene.number == 1
    assert pipeline.continuity.verify_integrity() is True


def test_pipeline_blocks_unexplained_continuity_conflict(tmp_path):
    pipeline = ProductionPipeline(str(tmp_path))
    pipeline.start_project("Continuity Test", "Test premise")

    pipeline.add_scene(
        number=1,
        title="Scene One",
        location="New York",
        time_of_day="Day",
        purpose="Setup",
        continuity_assertions=[
            {"subject": "Hero", "attribute": "location", "value": "New York"}
        ],
    )

    try:
        pipeline.add_scene(
            number=2,
            title="Scene Two",
            location="Tokyo",
            time_of_day="Day",
            purpose="Conflict",
            continuity_assertions=[
                {"subject": "Hero", "attribute": "location", "value": "Tokyo"}
            ],
        )
        assert False, "Expected continuity conflict"
    except ValueError as error:
        assert "Continuity conflict" in str(error)


def test_shot_director_creates_generation_ready_shot(tmp_path):
    pipeline = ProductionPipeline(str(tmp_path))
    pipeline.start_project("Shot Test", "Test premise")

    scene = pipeline.add_scene(
        number=1,
        title="Opening",
        location="City",
        time_of_day="Night",
        purpose="Opening",
    )

    shot = pipeline.add_shot(
        scene_id=scene.scene_id,
        number=1,
        framing="Wide",
        camera_movement="Slow aerial push-in",
        action="The hero stands beneath a dimensional rift.",
        lighting="Lightning and city lights",
    )

    assert "Wide shot" in pipeline.shots.generation_prompt(shot)
