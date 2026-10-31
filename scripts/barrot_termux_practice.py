#!/usr/bin/env python3

import base64
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

TARGET = (
    ROOT
    / ".barrot"
    / "practice"
    / "barrot_generated_practice.py"
)

RUNNER = (
    ROOT
    / "scripts"
    / "termux_runner.py"
)

CODE = '''#!/usr/bin/env python3

print("BARROT GENERATED THIS CODE")
print("TERMUX EXECUTION PRACTICE SUCCESSFUL")
'''


def run(*args, input_text=None):

    return subprocess.run(
        list(args),
        cwd=ROOT,
        text=True,
        input=input_text,
        capture_output=True,
    )


def main():

    TARGET.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    encoded = base64.b64encode(
        CODE.encode(
            "utf-8"
        )
    ).decode(
        "ascii"
    )

    relative_target = TARGET.relative_to(
        ROOT
    )

    write_command = (
        "mkdir -p "
        f"{TARGET.parent.relative_to(ROOT)}"
        " && "
        f"echo {encoded}"
        " | base64 -d > "
        f"{relative_target}"
    )

    validate_command = (
        f"python3 {relative_target}"
    )

    payload = (
        write_command
        + "\n"
        + validate_command
        + "\n"
    )

    queued = run(
        sys.executable,
        str(RUNNER),
        "enqueue",
        "Barrot autonomous code-drop practice",
        input_text=payload,
    )

    print(
        queued.stdout
    )

    if queued.returncode != 0:

        print(
            queued.stderr
        )

        raise SystemExit(
            queued.returncode
        )

    executed = run(
        sys.executable,
        str(RUNNER),
        "once",
    )

    print(
        executed.stdout
    )

    if executed.returncode != 0:

        print(
            executed.stderr
        )

        raise SystemExit(
            executed.returncode
        )

    if not TARGET.exists():

        raise SystemExit(
            "Practice failed: file was not created."
        )

    verification = run(
        "python3",
        str(
            relative_target
        ),
    )

    if verification.returncode != 0:

        print(
            verification.stderr
        )

        raise SystemExit(
            "Practice failed: generated code "
            "did not execute."
        )

    print(
        verification.stdout
    )

    print(
        "BARROT TERMUX PRACTICE COMPLETE"
    )


if __name__ == "__main__":
    main()
