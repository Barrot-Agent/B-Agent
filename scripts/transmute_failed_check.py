#!/usr/bin/env python3
"""Route a failed PR check to Barrot for a bounded, reviewable transmute patch."""

import json
import os
import subprocess

REPO = os.environ["GITHUB_REPOSITORY"]
PR = os.environ["PR_NUMBER"]


def gh(*args):
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def main():
    info = json.loads(gh("pr", "view", PR, "--repo", REPO, "--json", "title,labels,statusCheckRollup"))
    if any(label["name"] == "do-not-autopatch" for label in info["labels"]):
        return
    failed = [
        check
        for check in info.get("statusCheckRollup", [])
        if check.get("conclusion") in {"FAILURE", "CANCELLED", "TIMED_OUT"}
        and any(word in (check.get("name") or "").lower() for word in ("lint", "test"))
    ]
    if not failed:
        return
    if any(label["name"] == "transmute-attempted" for label in info["labels"]):
        return
    details = "\n".join(f"- `{check.get('name')}`: {check.get('detailsUrl', '')}" for check in failed)
    body = (
        f"## Failed PR checks for #{PR}\n\n{details}\n\n"
        "Use a bounded transmute patch: preserve existing content, change only the failing "
        "lint/test issue, run the relevant checks, and open a PR. Do not modify protected paths."
    )
    gh("issue", "create", "--repo", REPO, "--title", f"[Transmute] Repair failed checks for PR #{PR}", "--body", body, "--label", "barrot-task", "--label", "autogen")
    subprocess.run(["gh", "pr", "edit", PR, "--repo", REPO, "--add-label", "transmute-attempted"], check=False)


if __name__ == "__main__":
    main()
