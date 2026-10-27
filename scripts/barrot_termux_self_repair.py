#!/usr/bin/env python3

import base64
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

TARGET = (
    ROOT
    / ".barrot"
    / "practice"
    / "barrot_self_repair.py"
)

MEMORY = (
    ROOT
    / "ping-pongings"
    / "knowledge-base"
    / "barrot_termux_self_repair.jsonl"
)

RUNNER = (
    ROOT
    / "scripts"
    / "termux_runner.py"
)


BROKEN_CODE = '''#!/usr/bin/env python3

print("BARROT SELF-REPAIR PRACTICE")

raise RuntimeError(
    "INTENTIONAL PRACTICE FAILURE"
)
'''


FIXED_CODE = '''#!/usr/bin/env python3

print("BARROT SELF-REPAIR PRACTICE")
print("FAILURE DETECTED")
print("PATCH APPLIED")
print("SELF-REPAIR SUCCESSFUL")
'''


def now():

    return datetime.now(
        timezone.utc
    ).isoformat()


def run(*args, input_text=None):

    return subprocess.run(
        list(args),
        cwd=ROOT,
        text=True,
        input=input_text,
        capture_output=True,
    )


def record(data):

    MEMORY.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with MEMORY.open(
        "a",
        encoding="utf-8",
    ) as file:

        file.write(
            json.dumps(data)
            + "\n"
        )


def queue_write(code, note):

    encoded = base64.b64encode(
        code.encode(
            "utf-8"
        )
    ).decode(
        "ascii"
    )

    relative_target = TARGET.relative_to(
        ROOT
    )

    command = (
        "mkdir -p "
        f"{TARGET.parent.relative_to(ROOT)}"
        " && "
        f"echo {encoded}"
        " | base64 -d > "
        f"{relative_target}"
    )

    result = run(
        sys.executable,
        str(RUNNER),
        "enqueue",
        note,
        input_text=command + "\n",
    )

    if result.returncode != 0:

        raise RuntimeError(
            result.stderr
        )

    return result.stdout


def process_queue():

    result = run(
        sys.executable,
        str(RUNNER),
        "once",
    )

    return result


def execute_target():

    relative_target = TARGET.relative_to(
        ROOT
    )

    return run(
        "python3",
        str(relative_target),
    )


def main():

    print()
    print(
        "BARROT TERMUX SELF-REPAIR"
    )

    print()
    print(
        "PHASE 1: DROPPING PRACTICE CODE"
    )

    queue_write(
        BROKEN_CODE,
        "Barrot self-repair practice: initial version",
    )

    queued = process_queue()

    print(
        queued.stdout
    )

    print(
        "PHASE 2: TESTING GENERATED CODE"
    )

    first_run = execute_target()

    failure_detected = (
        first_run.returncode != 0
    )

    if not failure_detected:

        raise SystemExit(
            "Expected practice failure "
            "was not detected."
        )

    print(
        "FAILURE DETECTED"
    )

    print(
        first_run.stderr
    )

    print(
        "PHASE 3: APPLYING REPAIR"
    )

    queue_write(
        FIXED_CODE,
        "Barrot self-repair practice: corrected version",
    )

    repaired = process_queue()

    print(
        repaired.stdout
    )

    print(
        "PHASE 4: VALIDATING REPAIR"
    )

    final_run = execute_target()

    if final_run.returncode != 0:

        print(
            final_run.stderr
        )

        raise SystemExit(
            "Self-repair validation failed."
        )

    print(
        final_run.stdout
    )

    episode = {
        "timestamp": now(),
        "target": str(
            TARGET.relative_to(
                ROOT
            )
        ),
        "initial_failure": True,
        "repair_applied": True,
        "validated": True,
    }

    record(
        episode
    )

    print(
        "BARROT SELF-REPAIR VALIDATED"
    )


if __name__ == "__main__":
    main()
