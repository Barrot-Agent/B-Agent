"""CLI entrypoint for object detection."""

from __future__ import annotations

import argparse

from barrot_agent.autonomy.code_as_world.object_detector import (
    detect_objects,
    save_detections,
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
            "detections.json"
        ),
    )

    args = parser.parse_args()

    result = detect_objects(
        args.scene_manifest
    )

    output = save_detections(
        result,
        args.output,
    )

    print("OBJECT DETECTION COMPLETE")
    print(
        f"DETECTIONS: "
        f"{len(result.detections)}"
    )
    print(f"MANIFEST: {output}")


if __name__ == "__main__":
    main()
