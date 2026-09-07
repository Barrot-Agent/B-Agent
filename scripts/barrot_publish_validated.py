#!/usr/bin/env python3

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MANIFEST = (
    ROOT
    / ".barrot"
    / "repository_identity.json"
)


def run(*args):

    result = subprocess.run(
        list(args),
        cwd=ROOT,
        text=True,
    )

    return result.returncode


def capture(*args):

    return subprocess.run(
        list(args),
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def main():

    if not MANIFEST.exists():

        print(
            "MISSING REPOSITORY MANIFEST"
        )

        raise SystemExit(1)

    identity = json.loads(
        MANIFEST.read_text(
            encoding="utf-8"
        )
    )

    branch = identity.get(
        "current_branch"
    )

    if not branch:

        branch_result = capture(
            "git",
            "branch",
            "--show-current",
        )

        branch = (
            branch_result.stdout
            .strip()
        )

    if not branch:

        print(
            "NO ACTIVE BRANCH"
        )

        raise SystemExit(1)

    message = (
        "Barrot validated evolution update"
    )

    if len(sys.argv) > 1:

        message = " ".join(
            sys.argv[1:]
        )

    status = capture(
        "git",
        "status",
        "--short",
    )

    if status.stdout.strip():

        print(
            "COMMITTING VALIDATED CHANGES"
        )

        if run(
            "git",
            "add",
            "-A",
        ) != 0:

            raise SystemExit(1)

        commit = subprocess.run(
            [
                "git",
                "commit",
                "-m",
                message,
            ],
            cwd=ROOT,
            text=True,
        )

        if commit.returncode != 0:

            print(
                "COMMIT FAILED"
            )

            raise SystemExit(1)

    else:

        print(
            "NO UNCOMMITTED CHANGES"
        )

    remotes = identity.get(
        "remotes",
        {}
    )

    if not remotes:

        print(
            "NO CONFIGURED REMOTES"
        )

        raise SystemExit(1)

    failures = 0

    for remote in remotes:

        print()
        print(
            "PUSHING:",
            remote,
        )

        result = run(
            "git",
            "push",
            remote,
            branch,
        )

        if result != 0:

            failures += 1

    print()

    if failures:

        print(
            "REMOTE PUBLISH FAILED"
        )

        raise SystemExit(1)

    print(
        "ALL CONFIGURED REMOTES PUSHED"
    )


if __name__ == "__main__":
    main()
