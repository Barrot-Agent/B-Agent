import json

from barrot_agent.autonomy.code_as_world.simulation_validator import (
    validate_simulation,
)


def test_validate_simulation(tmp_path) -> None:
    world = tmp_path / "world.json"
    xml = tmp_path / "world.xml"

    world.write_text(
        json.dumps(
            {
                "states": [
                    {
                        "objects": [
                            {
                                "id": "object_1",
                            }
                        ]
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    xml.write_text(
        """<mujoco model="test">
<worldbody>
<body name="object_1">
<geom type="box" size="1 1 1"/>
</body>
</worldbody>
</mujoco>
""",
        encoding="utf-8",
    )

    result = validate_simulation(
        xml,
        world_manifest=world,
    )

    assert result.passed is True
    assert (
        result.metadata[
            "generated_objects"
        ]
        == 1
    )
