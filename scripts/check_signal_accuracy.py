#!/usr/bin/env python3
"""Emit a fail-closed evaluation status; do not score legacy forecasts.

The historical signal log has no validated fixed-horizon contract, immutable
data-cutoff guarantee, or independent outcome attestation. The previous
accuracy percentage is therefore not a valid model-performance measure.
This compatibility entry point intentionally performs no network access and
does not modify the legacy history or summary files.
"""
from __future__ import annotations

import json


def build_status() -> dict:
    return {
        "schema_version": "barrot.signal-evaluation-status.v1",
        "status": "BLOCKED_NO_VALIDATED_FIXED_HORIZON_DATA",
        "forecast_issuance": "BLOCKED",
        "evaluation_executed": False,
        "paper_trading": "NOT_STARTED",
        "legacy_history_file": "web/signal_history.jsonl",
        "legacy_summary_file": "web/legacy/signal_accuracy_unvalidated.json",
        "legacy_summary_validity": "UNVALIDATED_VARIABLE_HORIZON",
        "legacy_files_modified": False,
        "reason": (
            "Legacy records are scored at the first run after a 24-hour minimum, "
            "not at a fixed horizon; they do not establish an immutable source "
            "snapshot, target contract, probability calibration, or independently "
            "attested outcome. The historical accuracy percentage must not be "
            "used as a prediction-engine performance claim."
        ),
        "required_forecast_fields": [
            "forecast_id",
            "issued_at_utc",
            "data_cutoff_utc",
            "target",
            "horizon_seconds",
            "assumptions",
            "probability_or_confidence",
            "alternative_hypotheses",
            "source_snapshot_ids",
            "outcome_measurement_utc",
            "observed_outcome",
            "evaluation_version",
        ],
        "required_evaluation_controls": [
            "immutable point-in-time feature snapshots",
            "fixed-horizon walk-forward evaluation",
            "leakage prevention",
            "baseline comparisons",
            "probability calibration",
            "uncertainty and drift monitoring",
            "independent evaluation attestation",
            "shadow or paper evaluation before any real-money use",
        ],
    }


def main() -> None:
    print(json.dumps(build_status(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
