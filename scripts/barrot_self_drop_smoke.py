#!/usr/bin/env python3
"""
Barrot Self-Drop Smoke Test

Purpose:
    Prove that Barrot's Termux-side runtime can generate a bundle,
    place it into the controlled self-drop inbox, execute only the
    generated smoke bundle, and record deterministic evidence.

This test intentionally performs NO repository mutation.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(".barrot/self_drop")
INBOX = ROOT / "inbox"
OUTBOX = ROOT / "outbox"
EVIDENCE_ROOT = ROOT / "evidence"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")


def main() -> int:
    stamp = utc_stamp()
    run_dir = EVIDENCE_ROOT / stamp
    run_dir.mkdir(parents=True, exist_ok=True)

    bundle = INBOX / f"barrot_generated_smoke_{stamp}.sh"
    result_file = OUTBOX / f"barrot_generated_smoke_{stamp}.result"

    payload = """#!/data/data/com.termux/files/usr/bin/bash
set -eu
printf '%s\\n' 'BARROT_SELF_GENERATED_BUNDLE_EXECUTED=TRUE'
printf 'TERMUX_SHELL=%s\\n' "${SHELL:-unknown}"
printf 'PYTHON=%s\\n' "$(python --version 2>&1)"
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

    result_file.write_text(
        completed.stdout + completed.stderr
    )

    evidence = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "bundle": str(bundle),
        "bundle_sha256": bundle_hash,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "self_generated": True,
        "repository_mutation": False,
    }

    evidence_path = run_dir / "evidence.json"
    evidence_path.write_text(json.dumps(evidence, indent=2))

    ok = (
        completed.returncode == 0
        and "BARROT_SELF_GENERATED_BUNDLE_EXECUTED=TRUE"
        in completed.stdout
    )

    print(f"BUNDLE_CREATED={'PASS' if bundle.exists() else 'FAIL'}")
    print(f"SHA256_EVIDENCE={'PASS' if len(bundle_hash) == 64 else 'FAIL'}")
    print(f"BUNDLE_EXECUTION={'PASS' if completed.returncode == 0 else 'FAIL'}")
    print(
        "SELF_GENERATED_MARKER="
        + (
            "PASS"
            if "BARROT_SELF_GENERATED_BUNDLE_EXECUTED=TRUE"
            in completed.stdout
            else "FAIL"
        )
    )
    print(f"EVIDENCE={evidence_path}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
