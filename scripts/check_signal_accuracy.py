#!/usr/bin/env python3
"""Fail-closed signal evaluation status until a fixed-horizon ledger exists.

The legacy evaluator compared signals with a later live price at variable
elapsed horizons and rewrote historical signal rows. That metric is not a
valid out-of-sample forecast-skill estimate. This script deliberately performs
no market-data request and never mutates signal_history.jsonl.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

HISTORY_PATH = Path("web/signal_history.jsonl")
SUMMARY_PATH = Path("web/signal_accuracy.json")


def _read_previous_summary() -> dict[str, Any]:
    try:
        value = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _preserve_legacy_metric(previous: dict[str, Any]) -> dict[str, Any] | None:
    existing = previous.get("legacy_metric")
    if isinstance(existing, dict):
        return existing

    keys = ("checked_count", "correct_count", "accuracy_pct")
    if not any(key in previous for key in keys):
        return None

    return {
        "status": "NOT_COMPARABLE",
        "reason": (
            "Legacy result used variable elapsed horizons and a later live price; "
            "historical rows were mutable, so this is not fixed-horizon out-of-sample skill."
        ),
        **{key: previous.get(key) for key in keys},
    }


def build_summary(previous: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "2.0",
        "status": "NOT_EVALUATED",
        "metric_status": "NOT_COMPARABLE",
        "checked_count": 0,
        "correct_count": 0,
        "accuracy_pct": None,
        "reason": (
            "A fixed-horizon, timestamped forecast/outcome ledger with leakage "
            "controls and immutable outcomes is required before forecast skill "
            "can be measured. No live market data was queried."
        ),
        "legacy_metric": _preserve_legacy_metric(previous),
        "evaluation_protocol": {
            "status": "NOT_IMPLEMENTED",
            "target": "XRP/USD return and direction",
            "horizon_seconds": None,
            "data_cutoff_utc": None,
            "requirements": [
                "immutable forecast timestamp and data cutoff",
                "predeclared fixed horizon and target definition",
                "point-in-time features with leakage prevention",
                "baseline comparison and walk-forward evaluation",
                "probability calibration and uncertainty reporting",
                "recorded outcome after the horizon closes",
            ],
        },
    }


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main() -> None:
    previous = _read_previous_summary()
    summary = build_summary(previous)
    _atomic_write(SUMMARY_PATH, summary)
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
