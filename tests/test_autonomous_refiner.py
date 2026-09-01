import json

from barrot_agent.autonomy.code_as_world.autonomous_refiner import (
    plan_refinement,
)


def test_refinement_accepts_valid_world(
    tmp_path,
) -> None:
    validation = (
        tmp_path / "validation.json"
    )

    validation.write_text(
        json.dumps(
            {
                "passed": True,
                "metrics": [],
            }
        ),
        encoding="utf-8",
    )

    plan = plan_refinement(
        validation
    )

    assert plan.passed is True
    assert len(plan.actions) == 1
    assert (
        plan.actions[0].action
        == "accept_world"
    )


def test_refinement_detects_object_error(
    tmp_path,
) -> None:
    validation = (
        tmp_path / "validation.json"
    )

    validation.write_text(
        json.dumps(
            {
                "passed": False,
                "metrics": [
                    {
                        "name": (
                            "object_count_error"
                        ),
                        "value": 2.0,
                        "threshold": 0.0,
                        "passed": False,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    plan = plan_refinement(
        validation
    )

    assert plan.passed is False
    assert len(plan.actions) == 1
    assert (
        plan.actions[0].action
        == "rebuild_object_mapping"
    )
