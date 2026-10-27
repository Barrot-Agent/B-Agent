#!/usr/bin/env python3

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

LIVE_CYCLE = (
    ROOT
    / "scripts"
    / "barrot_live_code_cycle.py"
)

EVOLUTION = (
    ROOT
    / "scripts"
    / "barrot_code_evolution.py"
)

MEMORY = (
    ROOT
    / "ping-pongings"
    / "knowledge-base"
    / "barrot_evolution_bridge.jsonl"
)


def now():

    return datetime.now(
        timezone.utc
    ).isoformat()


def run(command):

    return subprocess.run(
        command,
        cwd=ROOT,
        shell=True,
        text=True,
        capture_output=True,
    )


def record(episode):

    MEMORY.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with MEMORY.open(
        "a",
        encoding="utf-8",
    ) as file:

        file.write(
            json.dumps(episode)
            + "\n"
        )


def main():

    goal = " ".join(
        sys.argv[1:]
    ).strip()

    if not goal:

        goal = (
            "repository awareness "
            "and autonomous code repair"
        )

    print()
    print(
        "BARROT EVOLUTION BRIDGE"
    )

    print(
        "GOAL:",
        goal,
    )

    print()
    print(
        "PHASE 1: EVOLUTION CONTEXT"
    )

    evolution = run(
        f"python3 scripts/barrot_code_evolution.py "
        f"{goal!r}"
    )

    print(
        evolution.stdout
    )

    if evolution.returncode != 0:

        print(
            evolution.stderr
        )

        raise SystemExit(
            "Evolution context failed."
        )

    print(
        "PHASE 2: LIVE CODE CYCLE"
    )

    live_cycle = run(
        "python3 "
        "scripts/barrot_live_code_cycle.py"
    )

    print(
        live_cycle.stdout
    )

    if live_cycle.returncode != 0:

        print(
            live_cycle.stderr
        )

        episode = {
            "timestamp": now(),
            "goal": goal,
            "evolution_success": True,
            "live_cycle_success": False,
            "validated": False,
        }

        record(
            episode
        )

        raise SystemExit(
            "Live code cycle failed."
        )

    episode = {
        "timestamp": now(),
        "goal": goal,
        "evolution_success": True,
        "live_cycle_success": True,
        "validated": True,
    }

    record(
        episode
    )

    print()
    print(
        "BARROT EVOLUTION BRIDGE VALIDATED"
    )


if __name__ == "__main__":
    main()
