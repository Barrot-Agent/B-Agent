"""Ask Barrot to build the repository knowledge bundle autonomously."""

from __future__ import annotations

import argparse
import sys

from barrot_agent.barrot_brain import BarrotBrain
from barrot_agent.orchestration.autonomous_actions import BarrotActionLoop
from barrot_agent.orchestration.repository_repair_loop import assert_clean_feature_worktree


def _confirm(prompt: str, expected: str) -> None:
    answer = input(prompt).strip()
    if answer != expected:
        raise SystemExit("Operator confirmation did not match; no learning action was started.")


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="Build Barrot's local repository knowledge bundle")
    parser.add_argument(
        "--allow-external-inference",
        action="store_true",
        help="Authorize repository context to be sent to GitHub Models or Groq.",
    )
    parser.add_argument(
        "--allow-local-mutations",
        action="store_true",
        help="Authorize verified file creation/patches in a clean non-default feature worktree.",
    )
    args = parser.parse_args(argv)

    if not args.allow_external_inference:
        raise SystemExit("External inference is disabled; pass --allow-external-inference only after reviewing the provider/data-transfer scope.")
    if not args.allow_local_mutations:
        raise SystemExit("Local repository mutations are disabled; pass --allow-local-mutations only when a clean feature worktree is ready.")
    if not sys.stdin.isatty():
        raise SystemExit("Knowledge building requires an interactive terminal; unattended external inference and local mutation are disabled.")

    _confirm(
        "Type SEND REPOSITORY CONTEXT TO GITHUB MODELS OR GROQ to authorize external inference: ",
        "SEND REPOSITORY CONTEXT TO GITHUB MODELS OR GROQ",
    )
    _confirm(
        "Type ALLOW BARROT TO MODIFY THIS CLEAN FEATURE WORKTREE to authorize local changes: ",
        "ALLOW BARROT TO MODIFY THIS CLEAN FEATURE WORKTREE",
    )

    try:
        workspace = assert_clean_feature_worktree(".", default_branch="main")
    except ValueError as exc:
        raise SystemExit(f"Knowledge build blocked: {exc}") from exc

    brain = BarrotBrain(allow_external_inference=True)
    loop = BarrotActionLoop(
        brain=brain,
        workspace=str(workspace),
        max_attempts=3,
    )

    goal = """
Build a structured repository knowledge system for Barrot.

IMPORTANT:
A LIST_FILES action alone is NOT completion.
You MUST inspect relevant existing files using READ_FILE or SEARCH_TEXT
before deciding what to modify.
You MUST create the required knowledge files using WRITE_FILE or APPLY_PATCH.
You MUST verify the created files.

Required work:
1. Inspect the existing repository before modifying anything.
2. Create a barrot_agent/knowledge package if it does not exist.
3. Implement a persistent JSONL knowledge store.
4. Each knowledge record must include:
   - kind
   - subject
   - content
   - source
   - confidence
   - metadata
5. Implement deterministic SHA-256 fingerprinting.
6. Reject duplicate knowledge records.
7. Provide a read_all() method.
8. Export the public classes from barrot_agent/knowledge/__init__.py.
9. Add a small verification test if appropriate.
10. Compile and verify all modified Python files.

Rules:
- Use only supported autonomous actions.
- Inspect before modification.
- Make minimal changes.
- Do not modify secrets.
- Do not execute arbitrary shell commands.
- Do not claim success without verification.
"""

    result = loop.run(goal)

    print("\n=== BARROT KNOWLEDGE BUILD ===")
    print("SUCCESS:", result.success)
    print("ATTEMPTS:", result.attempts)

    for attempt in result.history:
        print("\nATTEMPT:", attempt.get("attempt"))
        for item in attempt.get("results", []):
            print(
                "ACTION:",
                item.get("action"),
                "SUCCESS:",
                item.get("success"),
            )
        print("OUTCOME:", attempt.get("outcome"))
        print("LEARNING:", attempt.get("learning"))

    if not result.success:
        raise SystemExit("BARROT_KNOWLEDGE_BUILD_FAILED")

    knowledge_files = [
        workspace / "barrot_agent/knowledge/__init__.py",
        workspace / "barrot_agent/knowledge/knowledge_store.py",
    ]
    missing = [str(item) for item in knowledge_files if not item.exists()]
    if missing:
        raise SystemExit("BARROT_KNOWLEDGE_BUILD_INCOMPLETE: " + ", ".join(missing))

    print("\nBARROT_KNOWLEDGE_BUILD_OK")
    print("REMOTE_PUBLISH: disabled; the primary mission does not authorize external publication.")


if __name__ == "__main__":
    main()
