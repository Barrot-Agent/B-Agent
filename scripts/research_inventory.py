#!/usr/bin/env python3
"""Inventory every stored record that touches the consciousness-bridge keywords.

The deep-research request asked for a cross-analysis of all database records on GR,
QM, consciousness, measurement, observer, decoherence, entanglement, time,
information theory, ternary, transformers, transistors, algorithms, logarithms.

This script does not interpret them. It counts them, names the files, and copies the
grade each record already carries. A record with no stored grade is counted as
UNGraded, never promoted. Output: data/research/inventory.json.

Usage: python3 scripts/research_inventory.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "research" / "inventory.json"

TERMS = [
    "general relativity",
    "quantum mechanics",
    "consciousness",
    "measurement",
    "observer",
    "decoherence",
    "entanglement",
    "time",
    "information theory",
    "ternary",
    "transformer",
    "transistor",
    "algorithm",
    "logarithm",
]


def flatten(value, path="") -> list[tuple[str, str]]:
    """Yield (path, text) for every string leaf, including dict keys in the path."""
    found: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            found.extend(flatten(child, f"{path}.{key}" if path else str(key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(flatten(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        found.append((path, value))
    return found


def main() -> int:
    hits: dict[str, dict] = {term: {"files": {}, "records": 0} for term in TERMS}
    graded: dict[str, int] = {}

    for path in sorted(DATA.rglob("*.json")):
        if path == OUT:
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        relative = str(path.relative_to(ROOT))
        records = payload.get("records") if isinstance(payload, dict) else None
        # Grade lookup only applies to files that actually carry TRACE-5 records.
        grades = {}
        if isinstance(records, list):
            for record in records:
                if isinstance(record, dict) and "id" in record and "status" in record:
                    grades[record["id"]] = record["status"]
                    graded[record["status"]] = graded.get(record["status"], 0) + 1
        for key, text in flatten(payload):
            lowered = text.lower()
            for term in TERMS:
                if term in lowered:
                    entry = hits[term]["files"].setdefault(relative, {"matches": 0, "grades": {}})
                    entry["matches"] += 1
                    hits[term]["records"] += 1
                    for record_id, status in grades.items():
                        if record_id and record_id in key:
                            entry["grades"][record_id] = status

    for term, entry in hits.items():
        entry["file_count"] = len(entry["files"])
        entry["files"] = dict(sorted(entry["files"].items(), key=lambda kv: -kv[1]["matches"])[:8])

    payload = {
        "method": "literal keyword scan over string leaves of every data/**/*.json",
        "built_at": "2026-11-17",
        "terms": TERMS,
        "files_scanned": len(list(DATA.rglob("*.json"))),
        "disclosure": (
            "A keyword hit is not evidence of a claim. It says a stored record mentions "
            "the term. Grades come only from records that already carry one."
        ),
        "grades_in_scanned_records": graded,
        "hits": hits,
        "zero_hit_terms": [term for term, entry in hits.items() if entry["records"] == 0],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({
        "files_scanned": payload["files_scanned"],
        "terms": {term: entry["records"] for term, entry in hits.items()},
        "zero_hit_terms": payload["zero_hit_terms"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
