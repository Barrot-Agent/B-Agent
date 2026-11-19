"""Ask Barrot to build the repository knowledge bundle autonomously."""

from __future__ import annotations

from pathlib import Path

from barrot_agent.barrot_brain import BarrotBrain
from barrot_agent.orchestration.autonomous_actions import BarrotActionLoop


def main() -> None:
    brain = BarrotBrain()

    loop = BarrotActionLoop(
        brain=brain,
        workspace=".",
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
        raise SystemExit(
            "BARROT_KNOWLEDGE_BUILD_FAILED"
        )

    
    knowledge_files = [
        Path("barrot_agent/knowledge/__init__.py"),
        Path("barrot_agent/knowledge/knowledge_store.py"),
    ]

    missing = [
        str(item)
        for item in knowledge_files
        if not item.exists()
    ]

    if missing:
        raise SystemExit(
            "BARROT_KNOWLEDGE_BUILD_INCOMPLETE: "
            + ", ".join(missing)
        )

    print("\nBARROT_KNOWLEDGE_BUILD_OK")



if __name__ == "__main__":
    main()
