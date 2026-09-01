"""CLI entrypoint for Code-as-World video observation."""

from __future__ import annotations

import argparse

from barrot_agent.autonomy.code_as_world.video_observer import (
    observe_video,
    save_observation,
)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "video",
        help="Path to the input video",
    )

    parser.add_argument(
        "--sample-every",
        type=int,
        default=30,
    )

    parser.add_argument(
        "--output",
        default=(
            "data/autonomy/code_as_world/"
            "observation.json"
        ),
    )

    args = parser.parse_args()

    observation = observe_video(
        args.video,
        sample_every=args.sample_every,
    )

    output = save_observation(
        observation,
        args.output,
    )

    print("CODE-AS-WORLD OBSERVATION COMPLETE")
    print(f"SOURCE: {observation.source_path}")
    print(f"FRAMES: {observation.frame_count}")
    print(f"FPS: {observation.fps}")
    print(
        "DURATION: "
        f"{observation.duration_seconds:.3f}s"
    )
    print(
        "SAMPLED FRAMES: "
        f"{len(observation.sampled_frames)}"
    )
    print(f"MANIFEST: {output}")


if __name__ == "__main__":
    main()
