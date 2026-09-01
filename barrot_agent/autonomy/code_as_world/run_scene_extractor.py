"""CLI entrypoint for Code-as-World scene extraction."""

from __future__ import annotations

import argparse

from barrot_agent.autonomy.code_as_world.scene_extractor import (
    extract_scenes,
    save_scene_manifest,
)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "video",
        help="Input video path",
    )

    parser.add_argument(
        "--sample-every",
        type=int,
        default=30,
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=25.0,
    )

    parser.add_argument(
        "--frames-dir",
        default=(
            "data/autonomy/code_as_world/frames"
        ),
    )

    parser.add_argument(
        "--output",
        default=(
            "data/autonomy/code_as_world/"
            "scenes.json"
        ),
    )

    args = parser.parse_args()

    extraction = extract_scenes(
        source=args.video,
        output_dir=args.frames_dir,
        sample_every=args.sample_every,
        scene_threshold=args.threshold,
    )

    manifest = save_scene_manifest(
        extraction,
        args.output,
    )

    print("SCENE EXTRACTION COMPLETE")
    print(f"FRAMES: {len(extraction.frames)}")
    print(f"SCENES: {len(extraction.scenes)}")
    print(f"MANIFEST: {manifest}")


if __name__ == "__main__":
    main()
