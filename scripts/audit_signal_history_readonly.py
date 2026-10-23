#!/usr/bin/env python3
"""Read-only descriptive audit of legacy signal history; does not estimate predictive skill."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HISTORY_PATH = ROOT / "web" / "signal_history.jsonl"


def valid_price(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
        and value > 0
    )


def audit_history_text(text):
    records = []
    parse_errors = 0
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
            if not isinstance(item, dict):
                parse_errors += 1
                continue
            records.append(item)
        except (ValueError, TypeError):
            parse_errors += 1

    checked = [r for r in records if r.get("checked") is True]
    unchecked = [r for r in records if r.get("checked") is not True]
    evaluation_keys = ("checked_at", "evaluated_at", "price_at_check_timestamp")
    target_time_keys = ("target_timestamp", "outcome_timestamp")
    target_price_keys = ("target_price", "price_at_evaluation", "price_at_check")
    missing_eval = sum(not any(r.get(k) for k in evaluation_keys) for r in checked)

    fixed_horizon_candidates = 0
    for record in checked:
        has_eval_time = any(record.get(k) for k in evaluation_keys)
        has_target_time = any(record.get(k) for k in target_time_keys)
        has_target_price = any(valid_price(record.get(k)) for k in target_price_keys)
        horizon = record.get("horizon_seconds")
        has_horizon = (
            isinstance(horizon, (int, float))
            and not isinstance(horizon, bool)
            and math.isfinite(float(horizon))
            and horizon > 0
        )
        if (
            has_eval_time
            and has_target_time
            and has_target_price
            and valid_price(record.get("price_at_emission"))
            and has_horizon
        ):
            fixed_horizon_candidates += 1

    return {
        "schema_version": 2,
        "record_count": len(records),
        "parse_errors": parse_errors,
        "checked_count": len(checked),
        "unchecked_count": len(unchecked),
        "legacy_correct_labels": sum(r.get("correct") is True for r in checked),
        "legacy_incorrect_or_missing_labels": sum(r.get("correct") is not True for r in checked),
        "checked_missing_evaluation_timestamp": missing_eval,
        "invalid_emission_price_count": sum(
            not valid_price(r.get("price_at_emission")) for r in records
        ),
        "fixed_horizon_candidate_count": fixed_horizon_candidates,
        "accuracy_pct": None,
        "skill_status": (
            "NOT_ESTIMABLE_MISSING_EVALUATION_TIMESTAMPS"
            if checked and missing_eval == len(checked)
            else "NOT_ESTIMABLE_REQUIRES_HORIZON_AND_PRICE_PROVENANCE"
        ),
        "source_mutated": False,
        "note": "Descriptive audit only. Legacy labels are not fixed-horizon skill estimates.",
    }


def main():
    raw = HISTORY_PATH.read_text(encoding="utf-8") if HISTORY_PATH.exists() else ""
    print(json.dumps(audit_history_text(raw), indent=2))


if __name__ == "__main__":
    main()
