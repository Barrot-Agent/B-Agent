#!/usr/bin/env python3
"""
Barrot Self-Drop Controller Adapter.

This adapter provides a narrow, explicit integration boundary between
Barrot's controller/tool layer and the already-tested self-drop bridge.

It deliberately exposes only SELF_DROP_PROBE.

It does not:
  * accept arbitrary shell commands;
  * modify arbitrary repository files;
  * git commit;
  * git push;
  * reset/clean/stash the worktree.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


BRIDGE = Path("scripts/barrot_self_drop_bridge.py")
ALLOWED_ACTION = "SELF_DROP_PROBE"


class SelfDropControllerAdapter:
    name = "self_drop"
    actions = frozenset({ALLOWED_ACTION})

    def can_handle(self, action: str) -> bool:
        return action in self.actions

    def dispatch(self, task_id: str, action: str) -> dict:
        if not self.can_handle(action):
            raise ValueError(f"unsupported self-drop action: {action}")

        if not task_id or not isinstance(task_id, str):
            raise ValueError("task_id must be a non-empty string")

        if not BRIDGE.exists():
            raise FileNotFoundError(str(BRIDGE))

        request = {
            "task_id": task_id,
            "action": action,
        }

        completed = subprocess.run(
            [
                sys.executable,
                str(BRIDGE),
                json.dumps(request, sort_keys=True),
            ],
            text=True,
            capture_output=True,
            timeout=60,
        )

        # The bridge writes authoritative execution evidence to disk.
        # Expose that evidence to the controller instead of assuming that
        # the bridge's human-readable summary is the executed bundle stdout.
        evidence_path = None
        for line in completed.stdout.splitlines():
            if line.startswith("EVIDENCE="):
                evidence_path = line.split("=", 1)[1].strip()
                break

        evidence = {}
        if evidence_path:
            evidence_file = Path(evidence_path)
            if evidence_file.exists():
                evidence = json.loads(evidence_file.read_text())

        return {
            "adapter": self.name,
            "action": action,
            "task_id": task_id,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "execution_stdout": evidence.get("stdout", ""),
            "execution_stderr": evidence.get("stderr", ""),
            "evidence_path": evidence_path,
            "bundle_sha256": evidence.get("bundle_sha256"),
            "repository_mutation": evidence.get(
                "repository_mutation"
            ),
            "arbitrary_shell_input": evidence.get(
                "arbitrary_shell_input"
            ),
            "success": (
                completed.returncode == 0
                and evidence.get("returncode") == 0
            ),
        }


def main() -> int:
    adapter = SelfDropControllerAdapter()

    if len(sys.argv) != 3:
        print("usage: barrot_self_drop_controller_adapter.py TASK_ID ACTION")
        return 2

    task_id, action = sys.argv[1], sys.argv[2]

    try:
        result = adapter.dispatch(task_id, action)
    except Exception as exc:
        print(json.dumps({
            "success": False,
            "error": str(exc),
        }, indent=2))
        return 1

    print(json.dumps(result, indent=2))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
