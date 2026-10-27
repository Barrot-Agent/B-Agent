#!/usr/bin/env python3

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LOG = (
    ROOT
    / "ping-pongings"
    / "knowledge-base"
    / "barrot_night_cycle.jsonl"
)


def now():

    return datetime.now(
        timezone.utc
    ).isoformat()


def run(command):

    result = subprocess.run(
        command,
        cwd=ROOT,
        shell=True,
        text=True,
        capture_output=True,
    )

    return {
        "command": command,
        "returncode": result.returncode,
        "success": result.returncode == 0,
        "stdout": result.stdout[-12000:],
        "stderr": result.stderr[-12000:],
    }


def record(entry):

    LOG.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with LOG.open(
        "a",
        encoding="utf-8",
    ) as file:

        file.write(
            json.dumps(entry)
            + "\n"
        )


def main():

    goal = " ".join(
        sys.argv[1:]
    ).strip()

    if not goal:

        print(
            "GOAL REQUIRED"
        )

        raise SystemExit(1)

    commands = [
        (
            "python3 "
            "scripts/barrot_repository_identity.py"
        ),
        (
            "python3 "
            "scripts/barrot_repository_guard.py"
        ),
        (
            "python3 "
            "scripts/barrot_repo_recall.py"
        ),
        (
            "python3 "
            "scripts/barrot_connectome_memory.py"
        ),
        (
            "python3 "
            "scripts/barrot_architecture_context.py "
            f'"{goal}"'
        ),
        (
            "python3 "
            "scripts/barrot_code_evolution.py "
            f'"{goal}"'
        ),
    ]

    episode = {
        "timestamp": now(),
        "goal": goal,
        "steps": [],
    }

    for command in commands:

        result = run(
            command
        )

        episode[
            "steps"
        ].append(
            result
        )

        print()
        print(
            "COMMAND:",
            command,
        )

        print(
            "SUCCESS:",
            result["success"],
        )

        if not result["success"]:

            print(
                result["stderr"][-4000:]
            )

            record(
                episode
            )

            print()
            print(
                "NIGHT CYCLE STOPPED"
            )

            raise SystemExit(1)

    record(
        episode
    )

    print()
    print(
        "BARROT NIGHT CYCLE COMPLETE"
    )


if __name__ == "__main__":
    main()
