#!/usr/bin/env python3

import base64
import json
import shutil
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

REGISTRY = (
    ROOT
    / ".barrot"
    / "target_registry.json"
)

MEMORY = (
    ROOT
    / "ping-pongings"
    / "knowledge-base"
    / "barrot_controlled_repair.jsonl"
)

BACKUP_ROOT = (
    ROOT
    / ".barrot"
    / "backups"
)


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


def load_registry():

    if not REGISTRY.exists():

        raise RuntimeError(
            "Target registry not found: "
            + str(
                REGISTRY
            )
        )

    return json.loads(
        REGISTRY.read_text(
            encoding="utf-8"
        )
    )


def find_target(target_id):

    registry = load_registry()

    for target in registry.get(
        "targets",
        [],
    ):

        if (
            target.get("id")
            == target_id
        ):

            return target

    return None


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
        "echo "
        f"{encoded}"
        " | base64 -d > "
        f"{relative}"
    )

    queued = run(
        sys.executable,
        str(RUNNER),
        "enqueue",
        note,
        input_text=command + "\n",
    )

    if queued.returncode != 0:

        raise RuntimeError(
            queued.stderr
        )

    processed = run(
        sys.executable,
        str(RUNNER),
        "once",
    )

    if processed.returncode != 0:

        raise RuntimeError(
            processed.stderr
        )

    return processed


def backup(target):

    BACKUP_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    backup_path = (
        BACKUP_ROOT
        / (
            target.name
            + "."
            + now().replace(
                ":",
                "-"
            )
            + ".bak"
        )
    )

    shutil.copy2(
        target,
        backup_path,
    )

    return backup_path


def restore(
    backup_path,
    target,
):

    shutil.copy2(
        backup_path,
        target,
    )


def validate(tests):

    command = [
        "python3",
        "-m",
        "pytest",
        "-q",
        "--no-cov",
        *tests,
    ]

    return run(
        *command
    )


def main():

    if len(sys.argv) < 2:

        raise SystemExit(
            "usage: "
            "barrot_controlled_repair.py "
            "<target-id>"
        )

    target_id = (
        sys.argv[1]
    )

    config = find_target(
        target_id
    )

    if config is None:

        raise SystemExit(
            "TARGET ID NOT FOUND: "
            + target_id
        )

    if not config.get(
        "enabled",
        False,
    ):

        raise SystemExit(
            "TARGET DISABLED: "
            + target_id
        )

    if config.get(
        "mode"
    ) != "controlled":

        raise SystemExit(
            "TARGET MODE NOT PERMITTED"
        )

    target_relative = (
        config["path"]
    )

    tests = (
        config.get(
            "tests",
            [],
        )
    )

    if not tests:

        raise SystemExit(
            "TARGET HAS NO VALIDATION TESTS"
        )

    target = (
        ROOT
        / target_relative
    )

    if not target.exists():

        raise SystemExit(
            "TARGET NOT FOUND: "
            + target_relative
        )

    print()
    print(
        "BARROT CONTROLLED REPAIR"
    )

    print(
        "TARGET ID:",
        target_id,
    )

    print(
        "TARGET:",
        target_relative,
    )

    print(
        "TESTS:"
    )

    for test in tests:

        print(
            "-",
            test,
        )

    original = target.read_text(
        encoding="utf-8"
    )

    backup_path = backup(
        target
    )

    print(
        "BACKUP CREATED:",
        backup_path.relative_to(
            ROOT
        ),
    )

    candidate = original.replace(
        "return a + b",
        "return a - b",
    )

    if candidate == original:

        raise SystemExit(
            "No controlled mutation "
            "available for target."
        )

    print(
        "APPLYING CONTROLLED CHANGE"
    )

    queue_write(
        target,
        candidate,
        "Controlled repair: "
        + target_id,
    )

    result = validate(
        tests
    )

    print(
        result.stdout
    )

    if result.returncode == 0:

        status = "validated"

        print(
            "CHANGE VALIDATED"
        )

    else:

        status = "rolled_back"

        print(
            "VALIDATION FAILED"
        )

        print(
            "ROLLING BACK"
        )

        restore(
            backup_path,
            target,
        )

        restored = validate(
            tests
        )

        print(
            restored.stdout
        )

        if restored.returncode != 0:

            raise SystemExit(
                "ROLLBACK VALIDATION FAILED"
            )

        print(
            "ROLLBACK VALIDATED"
        )

    episode = {
        "timestamp": now(),
        "target_id": target_id,
        "target": target_relative,
        "tests": tests,
        "backup": str(
            backup_path.relative_to(
                ROOT
            )
        ),
        "status": status,
    }

    record(
        episode
    )

    print()
    print(
        "BARROT CONTROLLED REPAIR COMPLETE"
    )

    print(
        "STATUS:",
        status,
    )


if __name__ == "__main__":
    main()
