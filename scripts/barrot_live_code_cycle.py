#!/usr/bin/env python3

import base64
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

RUNNER = (
    ROOT
    / "scripts"
    / "termux_runner.py"
)

TASK_ROOT = (
    ROOT
    / ".barrot"
    / "autonomous_tasks"
)

MODULE = (
    TASK_ROOT
    / "math_task.py"
)

TEST = (
    TASK_ROOT
    / "test_math_task.py"
)

MEMORY = (
    ROOT
    / "ping-pongings"
    / "knowledge-base"
    / "barrot_live_code_cycle.jsonl"
)


BROKEN_MODULE = '''def add(a, b):
    return a - b
'''


TEST_CODE = '''from math_task import add


def test_add():
    assert add(2, 3) == 5
'''


def now():

    return datetime.now(
        timezone.utc
    ).isoformat()


def local(command):

    return subprocess.run(
        command,
        cwd=ROOT,
        shell=True,
        text=True,
        capture_output=True,
    )


def derive_repair(
    source,
    failure_output,
):

    combined = (
        source
        + "\n"
        + failure_output
    )

    if (
        "assert -1 == 5"
        in combined
        and "return a - b"
        in source
    ):

        return source.replace(
            "return a - b",
            "return a + b",
        )

    return None


def queue_write(
    target,
    content,
    note,
):

    relative = target.relative_to(
        ROOT
    )

    encoded = base64.b64encode(
        content.encode(
            "utf-8"
        )
    ).decode(
        "ascii"
    )

    command = (
        "mkdir -p "
        f"{target.parent.relative_to(ROOT)}"
        " && "
        f"echo {encoded}"
        " | base64 -d > "
        f"{relative}"
    )

    queued = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "enqueue",
            note,
        ],
        cwd=ROOT,
        text=True,
        input=command + "\n",
        capture_output=True,
    )

    if queued.returncode != 0:

        raise RuntimeError(
            queued.stderr
        )


def process_queue():

    return subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "once",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def run_test():

    return local(
        "python3 -m pytest -q "
        "--no-cov "
        f"{TEST.relative_to(ROOT)}"
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

    print()
    print(
        "BARROT LIVE CODE CYCLE"
    )

    print()
    print(
        "PHASE 1: DROP IMPLEMENTATION"
    )

    queue_write(
        MODULE,
        BROKEN_MODULE,
        "Live code cycle: initial implementation",
    )

    queue_write(
        TEST,
        TEST_CODE,
        "Live code cycle: validation test",
    )

    result = process_queue()

    print(
        result.stdout
    )

    print(
        "PHASE 2: RUN REAL TEST"
    )

    first = run_test()

    print(
        first.stdout
    )

    if first.returncode == 0:

        raise SystemExit(
            "Expected initial failure "
            "did not occur."
        )

    print(
        "PHASE 3: ANALYZE FAILURE"
    )

    source = MODULE.read_text(
        encoding="utf-8"
    )

    failure_output = (
        first.stdout
        + "\n"
        + first.stderr
    )

    repair = derive_repair(
        source,
        failure_output,
    )

    if repair is None:

        raise SystemExit(
            "Barrot could not derive "
            "a repair from the failure."
        )

    print(
        "REPAIR DERIVED"
    )

    queue_write(
        MODULE,
        repair,
        "Live code cycle: derived repair",
    )

    result = process_queue()

    print(
        result.stdout
    )

    print(
        "PHASE 4: RE-VALIDATE"
    )

    final = run_test()

    print(
        final.stdout
    )

    if final.returncode != 0:

        print(
            final.stderr
        )

        raise SystemExit(
            "Derived repair validation failed."
        )

    episode = {
        "timestamp": now(),
        "module": str(
            MODULE.relative_to(ROOT)
        ),
        "test": str(
            TEST.relative_to(ROOT)
        ),
        "initial_failure": True,
        "repair_derived": True,
        "repair_applied": True,
        "validated": True,
    }

    record(
        episode
    )

    print()
    print(
        "BARROT LIVE CODE CYCLE VALIDATED"
    )


if __name__ == "__main__":
    main()
