#!/usr/bin/env python3
"""
Build a read-only Riemann research corpus for Barrot's A2A Worker.

Only structured harvested records are exported. This builder never promotes
a publication or computational result to mathematical proof status.
"""

from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "research" / "riemann_hypothesis_harvest.json"
OUTPUT = ROOT / "a2a" / "riemann_research_corpus.js"

ALLOWED_CLASSES = {
    "established_result",
    "computational_evidence",
    "published_claim",
    "conjecture_or_hypothesis",
    "barrot_research_lead",
}


def main():
    payload = {
        "domain": "Riemann Hypothesis",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "read_only": True,
        "evidence_policy": {
            "rule": (
                "No publication, computational result, conjecture, claim, "
                "or model output is treated as a proof without independent "
                "mathematical validation."
            ),
            "classes": sorted(ALLOWED_CLASSES),
        },
        "statistics": {},
        "records": [],
    }

    if SOURCE.exists():
        try:
            source = json.loads(SOURCE.read_text(encoding="utf-8"))
            for record in source.get("records", []):
                evidence_class = record.get("evidence_class", "barrot_research_lead")
                if evidence_class not in ALLOWED_CLASSES:
                    evidence_class = "barrot_research_lead"

                payload["records"].append(
                    {
                        "id": record.get("id", ""),
                        "title": record.get("title", ""),
                        "authors": record.get("authors", []),
                        "published": record.get("published", ""),
                        "source": record.get("source", ""),
                        "url": record.get("url", ""),
                        "summary": record.get("summary", ""),
                        "evidence_class": evidence_class,
                        "verification_status": record.get(
                            "verification_status", "unverified_candidate"
                        ),
                    }
                )
        except Exception as exc:
            payload["build_error"] = type(exc).__name__

    payload["records"].sort(
        key=lambda r: r.get("published", ""),
        reverse=True,
    )

    payload["statistics"] = {
        "total_records": len(payload["records"]),
        "by_evidence_class": {
            kind: sum(1 for record in payload["records"] if record["evidence_class"] == kind)
            for kind in sorted(ALLOWED_CLASSES)
        },
    }

    OUTPUT.write_text(
        "// AUTO-GENERATED. DO NOT EDIT MANUALLY.\n"
        "export const RIEMANN_RESEARCH_CORPUS = "
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + ";\n",
        encoding="utf-8",
    )

    print(f"A2A corpus built: {payload['statistics']['total_records']} records")


if __name__ == "__main__":
    main()
