"""CLI entrypoint for temporal object tracking."""

from __future__ import annotations

import argparse

from barrot_agent.autonomy.code_as_world.object_tracker import (
    save_tracks,
    track_objects,
)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "detections",
        help="Path to detections.json",
    )

    parser.add_argument(
        "--output",
        default=(
            "data/autonomy/code_as_world/"
            "tracks.json"
        ),
    )

    parser.add_argument(
        "--max-distance",
        type=float,
        default=0.25,
    )

    args = parser.parse_args()

    result = track_objects(
        args.detections,
        max_distance=args.max_distance,
    )

    output = save_tracks(
        result,
        args.output,
    )

    print("OBJECT TRACKING COMPLETE")
    print(f"TRACKS: {len(result.tracks)}")
    print(f"MANIFEST: {output}")


if __name__ == "__main__":
    main()
