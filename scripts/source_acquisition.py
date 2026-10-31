#!/usr/bin/env python3

from pathlib import Path
import argparse
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent

cleaned = []

for entry in sys.path:
    try:
        resolved = Path(entry or os.getcwd()).resolve()
    except Exception:
        cleaned.append(entry)
        continue

    if resolved == SCRIPTS:
        continue

    cleaned.append(entry)

sys.path[:] = [str(ROOT)] + [
    entry
    for entry in cleaned
    if entry != str(ROOT)
]

from barrot_agent.sources.source_acquisition import (
    SourceAcquisitionPlanner,
)


DEFAULT_PLAN = (
    ROOT
    / ".barrot"
    / "source_acquisition"
    / "plan.json"
)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--plan",
        default=str(DEFAULT_PLAN),
    )

    parser.add_argument(
        "command",
        choices=[
            "summary",
            "needs",
            "targets",
            "gaps",
        ],
    )

    args = parser.parse_args()

    planner = SourceAcquisitionPlanner(args.plan)

    if args.command == "summary":
        output = planner.summary()

    elif args.command == "needs":
        output = [
            item.__dict__
            for item in planner.list_needs()
        ]

    elif args.command == "targets":
        output = [
            item.__dict__
            for item in planner.list_targets()
        ]

    else:
        output = planner.gaps()

    print(
        json.dumps(
            output,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
