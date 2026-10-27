#!/usr/bin/env python3
"""
BARROT-Ω APEX LATTICE AUDIT SUMMARY — runs one real apex_lattice analysis
cycle against this repo and persists a compact summary for the
getBarrotAudit WebMCP tool.

SAFETY: explicitly passes github_token=None regardless of what's in the
environment, so PR creation is guaranteed to stay in "draft" mode (local
doc only, no real GitHub PR submitted) even though GitHub Actions
auto-populates GITHUB_TOKEN/GITHUB_REPOSITORY for every workflow run.
This script's only job is producing a read-only findings summary.
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from apex_lattice.cycle import CycleManager

KB_DIR = "ping-pongings/knowledge-base"
OUT_PATH = os.path.join(KB_DIR, "apex_audit_summary.json")
HISTORY_PATH = os.path.join(KB_DIR, "apex_audit_history.jsonl")


def main():
    os.makedirs(KB_DIR, exist_ok=True)

    mgr = CycleManager(
        repo_root=Path("."),
        base_dir=Path("."),
        github_token=None,
        github_repo=None,
    )
    summary = mgr.run_once()

    with open(HISTORY_PATH, "a") as f:
        f.write(json.dumps(summary, default=str) + "\n")

    out = {
        "note": (
            "Real static-analysis audit of this repo's own codebase, run "
            "by Barrot's apex_lattice pipeline. No PRs are opened by this "
            "process - findings_count/recommendations_count are counts "
            "only, not the full detail."
        ),
        "latest_cycle": {
            "cycle_id": summary.get("cycle_id"),
            "completed_at": summary.get("completed_at"),
            "analyzers_run": summary.get("analyzers_run"),
            "findings_count": summary.get("findings_count"),
            "recommendations_count": summary.get("recommendations_count"),
        },
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    web_path = os.path.join("web", os.path.basename(OUT_PATH))
    os.makedirs("web", exist_ok=True)
    with open(web_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
