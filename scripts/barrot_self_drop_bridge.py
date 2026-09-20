#!/usr/bin/env python3
"""
Barrot Self-Drop Bridge

Controlled boundary between Barrot's autonomous task layer and Termux.

The bridge:
  1. receives a structured Barrot task request,
  2. validates the request,
  3. creates a deterministic bundle,
  4. hashes the bundle,
  5. records provenance/evidence,
  6. executes only the generated bundle,
  7. records execution evidence.

This first version deliberately limits autonomous execution to a
declared allowlisted action: writing a marker/evidence result.

It does NOT:
  - reset the repository
  - clean the worktree
  - modify arbitrary repository files
  - git push
  - execute arbitrary commands supplied by a task request
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(".barrot/self_drop")
INBOX = ROOT / "inbox"
OUTBOX = ROOT / "outbox"
EVIDENCE = ROOT / "evidence"
REQUESTS = ROOT / "requests"

ALLOWED_ACTIONS = {"SELF_DROP_PROBE"}


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail(message: str) -> int:
    print(f"SELF_DROP_BRIDGE=FAIL")
    print(f"REASON={message}")
    return 1


def main() -> int:
    if len(sys.argv) != 2:
        return fail("expected exactly one JSON task request")

    try:
        request = json.loads(sys.argv[1])
    except json.JSONDecodeError as exc:
        return fail(f"invalid JSON: {exc}")

    if not isinstance(request, dict):
        return fail("task request must be an object")

    action = request.get("action")
    if action not in ALLOWED_ACTIONS:
        return fail(f"action not allowlisted: {action!r}")

    task_id = request.get("task_id")
    if not isinstance(task_id, str) or not task_id.strip():
        return fail("task_id is required")

    task_id = "".join(
        c if c.isalnum() or c in "-_" else "_"
        for c in task_id
    )

    now = stamp()
    evidence_dir = EVIDENCE / now
    evidence_dir.mkdir(parents=True, exist_ok=True)

    INBOX.mkdir(parents=True, exist_ok=True)
    OUTBOX.mkdir(parents=True, exist_ok=True)
    REQUESTS.mkdir(parents=True, exist_ok=True)

    request_path = REQUESTS / f"{task_id}_{now}.json"
    request_path.write_text(
        json.dumps(request, indent=2, sort_keys=True)
    )

    bundle = INBOX / f"barrot_autonomous_{task_id}_{now}.sh"
    result = OUTBOX / f"barrot_autonomous_{task_id}_{now}.result"

    # IMPORTANT:
    # The request cannot supply shell code.
    # The bridge itself constructs the only executable payload.
    payload = f"""#!/data/data/com.termux/files/usr/bin/bash
set -eu

printf '%s\\n' 'BARROT_AUTONOMOUS_SELF_DROP=TRUE'
printf 'BARROT_TASK_ID=%s\\n' '{task_id}'
printf 'BARROT_ACTION=%s\\n' 'SELF_DROP_PROBE'
printf 'BARROT_EXECUTED_AT=%s\\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf '%s\\n' 'BARROT_AUTONOMOUS_SELF_DROP_COMPLETE=TRUE'
"""

    bundle.write_text(payload)
    bundle.chmod(0o700)

    bundle_hash = sha256(bundle)

    completed = subprocess.run(
        ["bash", str(bundle)],
        cwd=Path.cwd(),
        text=True,
        capture_output=True,
        timeout=30,
    )

    combined = completed.stdout + completed.stderr
    result.write_text(combined)

    evidence = {
        "schema": "barrot.self_drop.bridge.v1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "task_id": task_id,
        "action": action,
        "request": request,
        "request_file": str(request_path),
        "generated_bundle": str(bundle),
        "bundle_sha256": bundle_hash,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "result_file": str(result),
        "autonomous_generation": True,
        "repository_mutation": False,
        "arbitrary_shell_input": False,
    }

    evidence_path = evidence_dir / "evidence.json"
    evidence_path.write_text(json.dumps(evidence, indent=2))

    success = (
        completed.returncode == 0
        and "BARROT_AUTONOMOUS_SELF_DROP=TRUE" in completed.stdout
        and "BARROT_AUTONOMOUS_SELF_DROP_COMPLETE=TRUE"
        in completed.stdout
    )

    print(f"REQUEST_ACCEPTED={'PASS' if action in ALLOWED_ACTIONS else 'FAIL'}")
    print("AUTONOMOUS_BUNDLE_GENERATION=PASS")
    print(f"SHA256_EVIDENCE={'PASS' if len(bundle_hash) == 64 else 'FAIL'}")
    print(
        "TERMUX_EXECUTION="
        + ("PASS" if completed.returncode == 0 else "FAIL")
    )
    print(
        "AUTONOMOUS_MARKER="
        + (
            "PASS"
            if "BARROT_AUTONOMOUS_SELF_DROP=TRUE" in completed.stdout
            else "FAIL"
        )
    )
    print(
        "COMPLETION_MARKER="
        + (
            "PASS"
            if "BARROT_AUTONOMOUS_SELF_DROP_COMPLETE=TRUE"
            in completed.stdout
            else "FAIL"
        )
    )
    print(f"EVIDENCE={evidence_path}")

    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
