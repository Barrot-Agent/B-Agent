#!/usr/bin/env python3

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MEMORY = (
    ROOT
    / "ping-pongings"
    / "knowledge-base"
    / "barrot_code_learning.jsonl"
)


def now():
    return datetime.now(timezone.utc).isoformat()


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
        "stdout": result.stdout[-12000:],
        "stderr": result.stderr[-12000:],
    }


def learn_from_result(result):

    MEMORY.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    episode = {
        "timestamp": now(),
        "command": result["command"],
        "success": (
            result["returncode"] == 0
        ),
        "returncode": result["returncode"],
        "stderr": result["stderr"],
    }

    with MEMORY.open(
        "a",
        encoding="utf-8",
    ) as f:
        f.write(
            json.dumps(episode)
            + "\n"
        )

    return episode


def main():

    checks = [
        "python3 scripts/barrot_repo_recall.py",
        "python3 scripts/barrot_connectome_memory.py",
        "python3 -m pytest -q",
    ]

    results = []

    for command in checks:

        result = run(command)

        episode = learn_from_result(
            result
        )

        results.append(
            episode
        )

        print()
        print(
            "COMMAND:",
            command
        )

        print(
            "SUCCESS:",
            episode["success"]
        )

    successful = sum(
        1
        for result in results
        if result["success"]
    )

    print()
    print(
        "BARROT RECURSIVE CODING CYCLE COMPLETE"
    )

    print(
        "SUCCESSFUL CHECKS:",
        successful,
        "/",
        len(results),
    )


if __name__ == "__main__":
    main()
