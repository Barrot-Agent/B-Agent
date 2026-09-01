import json
import xml.etree.ElementTree as ET

from barrot_agent.autonomy.code_as_world.mujoco_generator import (
    generate_physics_program,
)
from barrot_agent.autonomy.code_as_world.mujoco_validator import (
    validate_mujoco_xml,
)


def test_generate_mujoco_program(tmp_path) -> None:
    world_path = tmp_path / "world.json"
    output_path = tmp_path / "world.xml"

    world_path.write_text(
        json.dumps(
            {
                "states": [
                    {
                        "time_seconds": 0.0,
                        "objects": [
                            {
                                "id": "box_one",
                                "kind": "box",
                                "position": {
                                    "x": 0.0,
                                    "y": 0.0,
                                    "z": 1.0,
                                },
                                "size": {
                                    "x": 1.0,
                                    "y": 2.0,
                                    "z": 3.0,
                                },
                                "mass": 2.0,
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    program = generate_physics_program(
        world_path,
        output_path,
    )

    assert program.object_count == 1
    assert output_path.exists()

    root = ET.parse(
        output_path
    ).getroot()

    assert root.tag == "mujoco"
    assert validate_mujoco_xml(
        output_path
    )
