"""CLI entrypoint for simulation validation."""

from __future__ import annotations

import argparse

from barrot_agent.autonomy.code_as_world.simulation_validator import (
    save_validation,
    validate_simulation,
)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "physics_program",
        help="Path to MuJoCo XML",
    )

    parser.add_argument(
        "--world",
        default=(
            "data/autonomy/code_as_world/"
            "world.json"
        ),
    )

    parser.add_argument(
        "--observation",
        default=None,
    )

    parser.add_argument(
        "--output",
        default=(
            "data/autonomy/code_as_world/"
            "validation.json"
        ),
    )

    args = parser.parse_args()

    validation = validate_simulation(
        physics_program=args.physics_program,
        world_manifest=args.world,
        observation_manifest=args.observation,
    )

    output = save_validation(
        validation,
        args.output,
    )

    print(
        "SIMULATION VALIDATION COMPLETE"
    )
    print(
        f"PASSED: {validation.passed}"
    )

    for metric in validation.metrics:
        print(
            f"{metric.name}: "
            f"{metric.value} "
            f"(passed={metric.passed})"
        )

    print(
        f"REPORT: {output}"
    )

    if not validation.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
