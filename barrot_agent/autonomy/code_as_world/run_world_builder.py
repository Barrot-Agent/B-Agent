"""CLI entrypoint for Code-as-World world construction."""

from __future__ import annotations

import argparse

from barrot_agent.autonomy.code_as_world.world_builder import (
    build_world,
    save_world,
)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "scene_manifest",
        help="Path to scenes.json",
    )

    parser.add_argument(
        "--output",
        default=(
            "data/autonomy/code_as_world/"
            "world.json"
        ),
    )

    args = parser.parse_args()

    world = build_world(
        args.scene_manifest
    )

    output = save_world(
        world,
        args.output,
    )

    print(
        "WORLD REPRESENTATION COMPLETE"
    )
    print(
        f"STATES: {len(world.states)}"
    )

    object_count = sum(
        len(state.objects)
        for state in world.states
    )

    print(
        f"OBJECTS: {object_count}"
    )
    print(
        f"WORLD: {output}"
    )


if __name__ == "__main__":
    main()
