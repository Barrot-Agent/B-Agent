#!/usr/bin/env python3
"""Write Barrot's next-upgrade roadmap from the capability parity matrix."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from barrot_agent.roadmap import roadmap_to_dict


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("barrot_upgrade_roadmap.json"),
        help="Output JSON path",
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    roadmap = roadmap_to_dict()
    args.output.write_text(
        json.dumps(roadmap, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(roadmap['items'])} roadmap items to {args.output}")


if __name__ == "__main__":
    main()
