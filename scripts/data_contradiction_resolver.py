#!/usr/bin/env python3
"""Evidence-preserving contradiction report.

This tool detects conflicting records but never guesses which source is true.
All observations and minority objections remain intact until primary evidence
and independent corroboration support a human-reviewed resolution.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def build_conflict_report(dataset: Any) -> dict:
    if not isinstance(dataset, list):
        raise ValueError("TEST_DATA must be a JSON array")

    grouped: dict[str, list[dict]] = {}
    unresolved_records: list[dict] = []
    provenance_gaps: list[dict] = []

    for index, record in enumerate(dataset):
        if not isinstance(record, dict):
            unresolved_records.append({
                "index": index,
                "record": record,
                "reason": "record_is_not_a_json_object",
            })
            continue

        record_id = record.get("id")
        missing = [
            field for field in (
                "source_id",
                "source_url",
                "source_independence_group",
                "evidence_receipt_id",
                "source_event_time_utc",
            )
            if record.get(field) in (None, "")
        ]
        if missing:
            provenance_gaps.append({
                "index": index,
                "record_id": record_id if isinstance(record_id, str) else None,
                "missing_fields": missing,
                "record": record,
            })

        if not isinstance(record_id, str) or not record_id.strip():
            unresolved_records.append({
                "index": index,
                "record": record,
                "reason": "missing_stable_record_id",
            })
            continue

        grouped.setdefault(record_id, []).append(record)

    conflicts = []
    for record_id, observations in sorted(grouped.items()):
        distinct_values = {_canonical(item.get("value")) for item in observations}
        if len(distinct_values) <= 1:
            continue
        preserved = [dict(item) for item in observations]
        conflicts.append({
            "record_id": record_id,
            "resolution_status": "UNRESOLVED_PRIMARY_EVIDENCE_REQUIRED",
            "observation_count": len(preserved),
            "distinct_value_count": len(distinct_values),
            "observations": preserved,
            "minority_objections": preserved,
            "adjudication": None,
            "winner": None,
        })

    return {
        "schema_version": 1,
        "artifact_type": "evidence_preserving_contradiction_review",
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_record_count": len(dataset),
        "conflict_count": len(conflicts),
        "unresolved_record_count": len(unresolved_records),
        "provenance_gap_count": len(provenance_gaps),
        "source_records_preserved": True,
        "resolution_policy": (
            "No source is selected by an LLM or majority vote. Conflicts remain "
            "unresolved until primary evidence, event-time alignment, source "
            "independence and disconfirming evidence are reviewed."
        ),
        "conflicts": conflicts,
        "unresolved_records": unresolved_records,
        "provenance_gaps": provenance_gaps,
        "model_eligible": False,
        "forecast_status": "NOT_ISSUED",
    }


def main() -> int:
    raw = os.environ.get("TEST_DATA", "")
    if not raw:
        print("No TEST_DATA provided; no report written.")
        return 0
    try:
        dataset = json.loads(raw)
        report = build_conflict_report(dataset)
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Invalid contradiction-review input: {exc}") from None

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = Path(f"contradiction_review_{stamp}.json")
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Evidence-preserving contradiction report written: {output.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
