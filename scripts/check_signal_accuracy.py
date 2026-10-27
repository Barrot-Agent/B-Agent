#!/usr/bin/env python3
"""Safely retire the legacy variable-horizon accuracy metric.

The old evaluator compared historical signals with a later current price at
variable delays and rewrote source history. That result is not fixed-horizon
forecast skill. This replacement never mutates history and reports
NOT_EVALUATED until an immutable fixed-horizon forecast ledger is configured.
It preserves any prior legacy accuracy summary as explicitly NOT_COMPARABLE.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

HISTORY_PATH = Path("web/signal_history.jsonl")
SUMMARY_PATH = Path("web/signal_accuracy.json")
LEGACY_REASON = (
    "Legacy variable-horizon evaluation used later current prices and mutable "
    "outcomes; it is not calibrated fixed-horizon forecast skill."
)


def _load_entries():
    if not HISTORY_PATH.exists():
        return []
    entries = []
    with HISTORY_PATH.open(encoding="utf-8") as source_file:
        for line in source_file:
            try:
                entry = json.loads(line)
            except (json.JSONDecodeError, TypeError):
                continue
            if isinstance(entry, dict):
                entries.append(entry)
    return entries


def _load_previous_summary():
    try:
        value = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return {}
    return value if isinstance(value, dict) else {}


def _preserve_legacy_metric(previous):
    existing = previous.get("legacy_metric")
    if isinstance(existing, dict):
        checked = existing.get("checked_count")
        correct = existing.get("correct_count")
        accuracy = existing.get("accuracy_pct")
        if (
            isinstance(checked, int) and not isinstance(checked, bool)
            and isinstance(correct, int) and not isinstance(correct, bool)
            and isinstance(accuracy, (int, float)) and not isinstance(accuracy, bool)
        ):
            metric = dict(existing)
            metric["validity"] = "NOT_COMPARABLE"
            metric["reason"] = metric.get("reason") or LEGACY_REASON
            return metric

    checked = previous.get("checked_count")
    correct = previous.get("correct_count")
    accuracy = previous.get("accuracy_pct")
    if (
        isinstance(checked, int) and not isinstance(checked, bool)
        and isinstance(correct, int) and not isinstance(correct, bool)
        and isinstance(accuracy, (int, float)) and not isinstance(accuracy, bool)
    ):
        return {
            "checked_count": checked,
            "correct_count": correct,
            "accuracy_pct": accuracy,
            "validity": "NOT_COMPARABLE",
            "reason": LEGACY_REASON,
        }
    return None


def main():
    legacy_entries = _load_entries()
    previous = _load_previous_summary()
    legacy_metric = _preserve_legacy_metric(previous)
    summary = {
        "status": "NOT_EVALUATED",
        "checked_count": 0,
        "correct_count": 0,
        "accuracy_pct": None,
        "legacy_history_rows": len(legacy_entries),
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "reason": (
            "No validated immutable fixed-horizon forecast ledger is configured. "
            "Legacy history is preserved unchanged."
        ),
    }
    if legacy_metric is not None:
        summary["legacy_metric"] = legacy_metric
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary))
    return summary


if __name__ == "__main__":
    main()
