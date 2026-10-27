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


def git(*args):

    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def main():

    if not MANIFEST.exists():

        print(
            "REPOSITORY IDENTITY MISSING"
        )

        raise SystemExit(1)

    identity = json.loads(
        MANIFEST.read_text(
            encoding="utf-8"
        )
    )

    expected_root = identity.get(
        "git_repository_root"
    )

    actual = git(
        "rev-parse",
        "--show-toplevel",
    )

    if actual.returncode != 0:

        print(
            "NOT A GIT REPOSITORY"
        )

        raise SystemExit(1)

    actual_root = actual.stdout.strip()

    if (
        expected_root
        and expected_root != actual_root
    ):

        print(
            "REPOSITORY IDENTITY CONFLICT"
        )

        print(
            "EXPECTED:",
            expected_root,
        )

        print(
            "ACTUAL:",
            actual_root,
        )

        raise SystemExit(1)

    print(
        "REPOSITORY IDENTITY VERIFIED"
    )

    print(
        "NAME:",
        identity.get(
            "repository_name"
        )
    )

    print(
        "ROOT:",
        actual_root,
    )

    print(
        "BRANCH:",
        identity.get(
            "current_branch"
        )
    )

    print(
        "REMOTES:"
    )

    for name, urls in identity.get(
        "remotes",
        {}
    ).items():

        for url in urls:

            print(
                f"- {name}: {url}"
            )


if __name__ == "__main__":
    main()
