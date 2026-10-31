#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command):

    print()
    print(
        "RUNNING:",
        " ".join(command)
    )

    return subprocess.run(
        command,
        cwd=ROOT,
    ).returncode


def pytest_command(path):

    return [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        path,
        "--no-cov",
    ]


def main():

    paths = [
        Path(arg)
        for arg in sys.argv[1:]
    ]

    if not paths:

        print(
            "No explicit targets supplied."
        )

        print(
            "Running full validation without coverage gate."
        )

        code = run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "--no-cov",
            ]
        )

        raise SystemExit(code)

    commands = []

    for path in paths:

        if not path.is_absolute():

            path = ROOT / path

        if not path.exists():

            print(
                "SKIPPING MISSING TARGET:",
                path
            )

            continue

        relative = path.relative_to(
            ROOT
        )

        commands.append(
            pytest_command(
                str(relative)
            )
        )

    if not commands:

        print(
            "NO VALID TEST TARGETS FOUND"
        )

        raise SystemExit(1)

    failures = 0

    for command in commands:

        failures += (
            run(command) != 0
        )

    raise SystemExit(
        0
        if failures == 0
        else 1
    )


if __name__ == "__main__":
    main()
