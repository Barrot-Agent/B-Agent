"""CLI entrypoint for Code-as-World MuJoCo generation."""

from __future__ import annotations

import argparse

from barrot_agent.autonomy.code_as_world.mujoco_generator import (
    generate_physics_program,
)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "world",
        help="Path to world.json",
    )

    parser.add_argument(
        "--output",
        default=(
            "data/autonomy/code_as_world/"
            "world.xml"
        ),
        help="Output MuJoCo XML path",
    )

    args = parser.parse_args()

    program = generate_physics_program(
        args.world,
        args.output,
    )

    print(
        "MUJOCO PROGRAM GENERATION COMPLETE"
    )
    print(
        f"OBJECTS: {program.object_count}"
    )
    print(
        f"PROGRAM: {program.output_path}"
    )


if __name__ == "__main__":
    main()
