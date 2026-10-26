#!/usr/bin/env python3
"""Safely retire the legacy variable-horizon accuracy metric.

The old evaluator compared every historical signal to the current price after a
variable delay and rewrote the source history in place. Those results are not
fixed-horizon forecast skill. This replacement is read-only with respect to the
history ledger and explicitly reports NOT_EVALUATED until a validated,
immutable fixed-horizon forecast ledger is configured.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

HISTORY_PATH = Path("web/signal_history.jsonl")
SUMMARY_PATH = Path("web/signal_accuracy.json")


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


def main():
    legacy_entries = _load_entries()
    summary = {
        "status": "NOT_EVALUATED",
        "checked_count": 0,
        "correct_count": 0,
        "accuracy_pct": None,
        "legacy_history_rows": len(legacy_entries),
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "reason": (
            "Legacy history uses variable elapsed horizons and mutable outcome "
            "fields; it is not valid fixed-horizon forecast evaluation. "
            "No calibrated fixed-horizon forecast ledger is configured."
        ),
    }
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary))
    return summary


if __name__ == "__main__":
    main()
