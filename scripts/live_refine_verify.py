#!/usr/bin/env python3
"""Run the deterministic offline refinement pipeline against the large audit document.

No provider credentials, network access, or external transfer are used.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from barrot_agent.refinement import (  # noqa: E402
    HeuristicRefiner,
    RefinementPipeline,
    audit_document,
    segment_document,
)


def main() -> int:
    source_path = REPO_ROOT / "barrot_capability_audit.json"
    if not source_path.is_file():
        print(f"BLOCKED: missing source document: {source_path}", file=sys.stderr)
        return 2
    source = json.loads(source_path.read_text(encoding="utf-8"))
    audit = audit_document(source)
    slots = segment_document(source)
    print(f"SOURCE: {source_path.name}")
    print(f"AUDIT: chars={audit.total_chars} sections={len(slots)} "
          f"needs_segmentation={audit.needs_segmentation}")
    refiners = [HeuristicRefiner(), HeuristicRefiner("heuristic-2")]
    print(f"POOL: {[r.name for r in refiners]}")
    pipe = RefinementPipeline(
        refiners, ledger=None,
        data_classification="public_documentation")
    started = time.time()
    result = pipe.run(
        source,
        objective="normalize spacing and remove duplicate derived entries",
        source_identity="barrot_capability_audit.json",
        force=True,
    )
    print(f"RESULT: disposition={result['disposition']} "
          f"elapsed={time.time() - started:.2f}s")
    print(f"VERIFICATION: {result.get('verification', {})}")
    return 0 if result.get("disposition") == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
