#!/usr/bin/env python3
"""
Barrot Ω — Riemann Research Corroboration Layer

Groups harvested research by normalized titles and tracks source diversity.
Corroboration is metadata-level evidence only and never establishes a
mathematical theorem or proof.
"""

from __future__ import annotations
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "research" / "riemann_hypothesis_harvest.json"

def utcnow():
    return datetime.now(timezone.utc).isoformat()

def normalize_title(title):
    return re.sub(r"[^a-z0-9]+", " ", (title or "").lower()).strip()

def main():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    records = data.get("records", [])

    groups = {}
    for record in records:
        key = normalize_title(record.get("title", ""))
        if key:
            groups.setdefault(key, []).append(record)

    for key, matches in groups.items():
        sources = sorted({r.get("source", "") for r in matches if r.get("source")})
        for record in matches:
            record["corroboration"] = {
                "checked_at": utcnow(),
                "matching_metadata_records": len(matches),
                "distinct_sources": sources,
                "source_count": len(sources),
                "status": (
                    "metadata_corroborated"
                    if len(sources) > 1
                    else "single_source_metadata"
                ),
                "mathematical_verification": False,
                "rule": (
                    "Metadata corroboration does not establish the truth "
                    "or validity of a mathematical claim."
                ),
            }

    data["corroboration_policy"] = {
        "level": "metadata_only",
        "mathematical_verification": False,
        "rule": (
            "Independent expert mathematical verification is required "
            "before any claim may be represented as established."
        ),
        "last_checked_at": utcnow(),
    }

    SOURCE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Corroboration checked for {len(records)} records.")

if __name__ == "__main__":
    main()
