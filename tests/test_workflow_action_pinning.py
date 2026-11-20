"""Require immutable references for every active GitHub Actions dependency."""
from __future__ import annotations

import re
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIRECTORY = REPOSITORY_ROOT / ".github" / "workflows"
USES_LINE = re.compile(r"^\s*(?:-\s*)?uses:\s*([^\s#]+)", re.MULTILINE)
FULL_COMMIT_REFERENCE = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")
IMAGE_DIGEST_REFERENCE = re.compile(r"^docker://\S+@sha256:[0-9a-f]{64}$")


def test_active_workflow_actions_use_immutable_references() -> None:
    """Mutable tags can change code without a repository commit or review."""
    workflow_files = sorted(
        [*WORKFLOW_DIRECTORY.glob("*.yml"), *WORKFLOW_DIRECTORY.glob("*.yaml")]
    )
    assert workflow_files, "No active GitHub Actions workflow files were found."

    unpinned: list[str] = []
    for workflow_path in workflow_files:
        text = workflow_path.read_text(encoding="utf-8")
        for match in USES_LINE.finditer(text):
            reference = match.group(1)
            if reference.startswith("./"):
                continue
            if FULL_COMMIT_REFERENCE.fullmatch(reference):
                continue
            if IMAGE_DIGEST_REFERENCE.fullmatch(reference):
                continue
            line_number = text.count("\n", 0, match.start()) + 1
            unpinned.append(f"{workflow_path.relative_to(REPOSITORY_ROOT)}:{line_number}: {reference}")

    assert not unpinned, (
        "Every active external GitHub Action must be pinned to a full commit SHA "
        "or container digest; mutable references found:\n" + "\n".join(unpinned)
    )
