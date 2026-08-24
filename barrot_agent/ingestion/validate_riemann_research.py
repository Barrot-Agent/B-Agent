#!/usr/bin/env python3
"""
Barrot Ω — Conservative Riemann Research Validation

Adds cross-record consistency and source provenance signals without
promoting publications or computational results to established proof.
"""

from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "research" / "riemann_hypothesis_harvest.json"

def utcnow():
    return datetime.now(timezone.utc).isoformat()

def main():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    records = data.get("records", [])

    for record in records:
        source = record.get("source", "")
        verification = record.get("verification_status",
                                  "unverified_candidate")

        record["validation"] = {
            "validated_by": "barrot_conservative_validation",
            "validated_at": utcnow(),
            "source_present": bool(source),
            "metadata_complete": bool(
                record.get("title") and record.get("url")
            ),
            "independent_mathematical_verification": False,
            "corroboration_status": "source_metadata_only",
        }

        # Never upgrade proof status automatically.
        record["verification_status"] = verification

    data["cross_source_validation"] = {
        "status": "metadata_validation_complete",
        "independent_mathematical_verification": False,
        "rule": (
            "Automated validation checks metadata and provenance only. "
            "Mathematical truth requires independent expert verification."
        ),
        "validated_at": utcnow(),
    }

    data["statistics"]["validation"] = {
        "records_checked": len(records),
        "metadata_complete": sum(
            1 for r in records
            if r.get("validation", {}).get("metadata_complete")
        ),
        "independently_verified": 0,
    }

    SOURCE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"Validated {len(records)} Riemann research records.")

if __name__ == "__main__":
    main()
