"""CLI entrypoint for the complete Code-as-World pipeline."""

from __future__ import annotations

import argparse

from barrot_agent.autonomy.code_as_world.pipeline import (
    run_pipeline,
)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "video",
        help="Input video path",
    )

    parser.add_argument(
        "--output-dir",
        default=(
            "data/autonomy/code_as_world/run"
        ),
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

    args = parser.parse_args()

    result = run_pipeline(
        video=args.video,
        output_dir=args.output_dir,
        sample_every=args.sample_every,
        scene_threshold=args.threshold,
    )

    print("CODE-AS-WORLD PIPELINE COMPLETE")
    print(f"PASSED: {result.passed}")

    for stage in result.stages:
        print(
            f"{stage.name}: "
            f"{stage.status}"
        )

    for name, path in result.outputs.items():
        print(f"{name}: {path}")

    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
