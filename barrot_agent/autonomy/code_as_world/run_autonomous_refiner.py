"""CLI entrypoint for autonomous Code-as-World refinement."""

from __future__ import annotations

import argparse

from barrot_agent.autonomy.code_as_world.autonomous_refiner import (
    plan_refinement,
    save_refinement_plan,
)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--validation",
        default=(
            "data/autonomy/code_as_world/"
            "validation.json"
        ),
    )

    parser.add_argument(
        "--output",
        default=(
            "data/autonomy/code_as_world/"
            "refinement_plan.json"
        ),
    )

    args = parser.parse_args()

    plan = plan_refinement(
        args.validation,
    )

    output = save_refinement_plan(
        plan,
        args.output,
    )

    print("AUTONOMOUS REFINEMENT PLAN COMPLETE")
    print(f"VALIDATION PASSED: {plan.passed}")
    print(
        f"ACTIONS: {len(plan.actions)}"
    )

    for action in plan.actions:
        print(
            f"{action.iteration}: "
            f"{action.action}"
        )

    print(f"PLAN: {output}")


if __name__ == "__main__":
    main()
