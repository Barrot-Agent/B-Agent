#!/usr/bin/env python3
"""
Barrot Ω — Riemann Research Quality Gate

Assigns metadata-quality signals without determining mathematical truth.
No score can upgrade a claim to an established mathematical result.
"""

from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "research" / "riemann_hypothesis_harvest.json"


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def quality_score(record):
    score = 0
    if record.get("title"):
        score += 20
    if record.get("authors"):
        score += 20
    if record.get("published"):
        score += 15
    if record.get("url"):
        score += 20
    if record.get("summary"):
        score += 15
    if record.get("source"):
        score += 10
    return score


def main():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    records = data.get("records", [])

    for record in records:
        score = quality_score(record)
        record["quality_gate"] = {
            "checked_at": utcnow(),
            "metadata_quality_score": score,
            "status": "metadata_complete" if score >= 80 else "metadata_partial",
            "mathematical_truth_assessment": False,
            "rule": (
                "Metadata quality measures record completeness only and "
                "does not assess whether a mathematical claim is correct."
            ),
        }

    data["quality_gate_policy"] = {
        "purpose": "metadata_quality_only",
        "mathematical_verification": False,
        "records_checked": len(records),
        "checked_at": utcnow(),
    }

    SOURCE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Quality gate checked {len(records)} records.")


if __name__ == "__main__":
    main()
