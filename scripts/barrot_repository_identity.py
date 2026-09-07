#!/usr/bin/env python3

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MANIFEST = (
    ROOT
    / ".barrot"
    / "repository_identity.json"
)


def now():
    return datetime.now(
        timezone.utc
    ).isoformat()


def git(*args):
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    return {
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def main():

    remote_result = git(
        "remote",
        "-v",
    )

    remotes = {}

    if remote_result["returncode"] == 0:

        for line in (
            remote_result["stdout"]
            .splitlines()
        ):

            parts = line.split()

            if len(parts) >= 2:

                name = parts[0]
                url = parts[1]

                remotes.setdefault(
                    name,
                    []
                )

                if url not in remotes[name]:

                    remotes[name].append(
                        url
                    )

    branch_result = git(
        "branch",
        "--show-current",
    )

    repository_result = git(
        "rev-parse",
        "--show-toplevel",
    )

    status_result = git(
        "status",
        "--short",
    )

    identity = {
        "schema_version": 1,
        "updated_at": now(),
        "local_path": str(ROOT),
        "repository_name": ROOT.name,
        "git_repository_root": (
            repository_result["stdout"]
        ),
        "current_branch": (
            branch_result["stdout"]
        ),
        "remotes": remotes,
        "working_tree_dirty": bool(
            status_result["stdout"]
        ),
        "push_policy": {
            "require_validation": True,
            "push_all_configured_remotes": True,
            "verify_remote_after_push": True,
        },
    }

    MANIFEST.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    MANIFEST.write_text(
        json.dumps(
            identity,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            identity,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
