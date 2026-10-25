#!/usr/bin/env python3
"""Read-only, fixed-horizon evaluator for explicitly issued XRP forecasts.

Legacy sentiment scores are not price forecasts. This script never mutates
web/signal_history.jsonl and never substitutes a current price for a missing
horizon-aligned outcome. Outcome snapshots must be appended as separate JSONL
records with verified event timestamps.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HISTORY_PATH = ROOT / "web" / "signal_history.jsonl"
OUTCOME_LEDGER_PATH = ROOT / "web" / "forecast_evaluation.jsonl"
SUMMARY_PATH = ROOT / "web" / "signal_accuracy.json"
TARGET_DEFINITION = "xrp_usd_return_positive_at_horizon"
DEFAULT_TOLERANCE_SECONDS = 300
BASELINE_PROBABILITY = 0.5


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _parse_aware_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    return dt if dt.tzinfo is not None and dt.utcoffset() is not None else None


def _load_jsonl(path: Path) -> tuple[list[dict[str, Any]], int]:
    """Read JSONL without rewriting it; count malformed/non-object records."""
    if not path.exists():
        return [], 0
    records: list[dict[str, Any]] = []
    malformed = 0
    with path.open("r", encoding="utf-8") as stream:
        for raw in stream:
            if not raw.strip():
                continue
            try:
                value = json.loads(raw)
            except json.JSONDecodeError:
                malformed += 1
                continue
            if not isinstance(value, dict):
                malformed += 1
                continue
            records.append(value)
    return records, malformed


def _valid_forecast(record: dict[str, Any]) -> tuple[bool, str | None]:
    if record.get("record_type", "forecast") != "forecast":
        return False, "not_forecast_record"
    if record.get("forecast_status") != "ISSUED":
        return False, "forecast_not_issued"
    if record.get("forecast_contract_version") != 1:
        return False, "unsupported_or_missing_contract_version"
    if not isinstance(record.get("forecast_id"), str) or not record["forecast_id"].strip():
        return False, "missing_forecast_id"
    if record.get("target_definition") != TARGET_DEFINITION:
        return False, "unsupported_target_definition"
    horizon = record.get("horizon_seconds")
    if not isinstance(horizon, int) or isinstance(horizon, bool) or horizon <= 0:
        return False, "invalid_horizon"
    probability = record.get("probability")
    if not _finite_number(probability) or not 0.0 <= float(probability) <= 1.0:
        return False, "invalid_probability"
    issued_dt = _parse_aware_datetime(record.get("issued_at_utc"))
    cutoff_dt = _parse_aware_datetime(record.get("data_cutoff_utc"))
    if issued_dt is None or cutoff_dt is None:
        return False, "invalid_or_naive_timestamp"
    if cutoff_dt > issued_dt:
        return False, "data_cutoff_after_issue"
    if not _finite_number(record.get("price_at_issue")) or float(record["price_at_issue"]) <= 0:
        return False, "invalid_price_at_issue"
    price_dt = _parse_aware_datetime(record.get("price_at_issue_timestamp_utc"))
    if price_dt is None:
        return False, "invalid_price_event_timestamp"
    if price_dt > cutoff_dt or price_dt > issued_dt:
        return False, "price_event_after_data_cutoff_or_issue"
    price_staleness = record.get("price_staleness_tolerance_seconds", 300)
    if not isinstance(price_staleness, int) or isinstance(price_staleness, bool) or price_staleness < 0:
        return False, "invalid_price_staleness_tolerance"
    if issued_dt.timestamp() - price_dt.timestamp() > price_staleness:
        return False, "stale_price_at_issue"
    if not isinstance(record.get("price_source_id"), str) or not record["price_source_id"].strip():
        return False, "missing_price_source_id"
    if not isinstance(record.get("assumptions"), list) or not record["assumptions"] or not all(isinstance(x, str) and x.strip() for x in record["assumptions"]):
        return False, "missing_assumptions"
    if not isinstance(record.get("alternatives"), list) or not record["alternatives"] or not all(isinstance(x, str) and x.strip() for x in record["alternatives"]):
        return False, "missing_alternatives"
    if not isinstance(record.get("source_ids"), list) or not record["source_ids"] or not all(isinstance(x, str) and x.strip() for x in record["source_ids"]):
        return False, "missing_source_lineage"
    if record["price_source_id"] not in record["source_ids"]:
        return False, "price_source_not_in_source_lineage"
    if not isinstance(record.get("model_version"), str) or not record["model_version"].strip():
        return False, "missing_model_version"
    tolerance = record.get("outcome_tolerance_seconds", DEFAULT_TOLERANCE_SECONDS)
    if not isinstance(tolerance, int) or isinstance(tolerance, bool) or tolerance < 0:
        return False, "invalid_outcome_tolerance"
    return True, None


def _valid_outcome(record: dict[str, Any]) -> tuple[bool, str | None]:
    if record.get("record_type") != "outcome":
        return False, "not_outcome_record"
    if not isinstance(record.get("forecast_id"), str) or not record["forecast_id"].strip():
        return False, "missing_forecast_id"
    if not _finite_number(record.get("outcome_price")) or float(record["outcome_price"]) <= 0:
        return False, "invalid_outcome_price"
    if not _finite_number(record.get("observed_at_unix")) or float(record["observed_at_unix"]) <= 0:
        return False, "invalid_outcome_timestamp"
    if record.get("timestamp_quality") != "verified_event_time":
        return False, "outcome_timestamp_not_verified_event_time"
    if not isinstance(record.get("source_id"), str) or not record["source_id"].strip():
        return False, "missing_outcome_source_id"
    return True, None


def _read_evaluation_ids(path: Path) -> set[str]:
    records, _ = _load_jsonl(path)
    return {
        str(record["forecast_id"])
        for record in records
        if record.get("record_type") == "evaluation" and isinstance(record.get("forecast_id"), str)
    }


def _valid_evaluation(record: dict[str, Any]) -> tuple[bool, str | None]:
    if record.get("record_type") != "evaluation":
        return False, "not_evaluation_record"
    if not isinstance(record.get("forecast_id"), str) or not record["forecast_id"].strip():
        return False, "missing_forecast_id"
    if record.get("target_definition") != TARGET_DEFINITION:
        return False, "unsupported_target_definition"
    horizon = record.get("horizon_seconds")
    if not isinstance(horizon, int) or isinstance(horizon, bool) or horizon <= 0:
        return False, "invalid_horizon"
    issued_dt = _parse_aware_datetime(record.get("issued_at_utc"))
    cutoff_dt = _parse_aware_datetime(record.get("data_cutoff_utc"))
    if issued_dt is None or cutoff_dt is None or cutoff_dt > issued_dt:
        return False, "invalid_evaluation_timestamps"
    probability = record.get("probability")
    if not _finite_number(probability) or not 0.0 <= float(probability) <= 1.0:
        return False, "invalid_evaluation_probability"
    outcome = record.get("outcome")
    if isinstance(outcome, bool) or outcome not in (0, 1):
        return False, "invalid_binary_outcome"
    observed = record.get("outcome_observed_at_unix")
    tolerance = record.get("outcome_tolerance_seconds")
    if not _finite_number(observed):
        return False, "invalid_evaluation_outcome_timestamp"
    if not isinstance(tolerance, int) or isinstance(tolerance, bool) or tolerance < 0:
        return False, "invalid_evaluation_tolerance"
    target_end = issued_dt.timestamp() + horizon
    if abs(float(observed) - target_end) > tolerance:
        return False, "evaluation_outcome_outside_horizon"
    baseline_probability = record.get("baseline_probability")
    if not _finite_number(baseline_probability) or not math.isclose(float(baseline_probability), BASELINE_PROBABILITY, abs_tol=1e-12):
        return False, "invalid_baseline_probability"
    expected_brier = (float(probability) - int(outcome)) ** 2
    expected_baseline_brier = (BASELINE_PROBABILITY - int(outcome)) ** 2
    if not _finite_number(record.get("brier_score")) or not math.isclose(float(record["brier_score"]), expected_brier, rel_tol=0.0, abs_tol=1e-9):
        return False, "brier_score_mismatch"
    if not _finite_number(record.get("baseline_brier_score")) or not math.isclose(float(record["baseline_brier_score"]), expected_baseline_brier, rel_tol=0.0, abs_tol=1e-9):
        return False, "baseline_brier_score_mismatch"
    if not isinstance(record.get("outcome_source_id"), str) or not record["outcome_source_id"].strip():
        return False, "missing_outcome_source_id"
    if not isinstance(record.get("model_version"), str) or not record["model_version"].strip():
        return False, "missing_model_version"
    return True, None


def _evaluate_pair(forecast: dict[str, Any], outcome: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    valid_f, reason_f = _valid_forecast(forecast)
    if not valid_f:
        return None, reason_f
    valid_o, reason_o = _valid_outcome(outcome)
    if not valid_o:
        return None, reason_o
    if forecast["forecast_id"] != outcome["forecast_id"]:
        return None, "forecast_id_mismatch"
    issued_dt = _parse_aware_datetime(forecast["issued_at_utc"])
    assert issued_dt is not None
    target_end = issued_dt.timestamp() + forecast["horizon_seconds"]
    observed = float(outcome["observed_at_unix"])
    tolerance = int(forecast.get("outcome_tolerance_seconds", DEFAULT_TOLERANCE_SECONDS))
    if abs(observed - target_end) > tolerance:
        return None, "outcome_outside_horizon_tolerance"
    y = 1 if float(outcome["outcome_price"]) > float(forecast["price_at_issue"]) else 0
    p = float(forecast["probability"])
    brier = (p - y) ** 2
    baseline_brier = (BASELINE_PROBABILITY - y) ** 2
    return {
        "record_type": "evaluation",
        "forecast_id": forecast["forecast_id"],
        "target_definition": TARGET_DEFINITION,
        "horizon_seconds": forecast["horizon_seconds"],
        "issued_at_utc": forecast["issued_at_utc"],
        "data_cutoff_utc": forecast["data_cutoff_utc"],
        "outcome_observed_at_unix": observed,
        "outcome_source_id": outcome["source_id"],
        "outcome_tolerance_seconds": tolerance,
        "model_version": forecast["model_version"],
        "probability": p,
        "outcome": y,
        "brier_score": brier,
        "baseline_probability": BASELINE_PROBABILITY,
        "baseline_brier_score": baseline_brier,
        "beats_baseline": brier < baseline_brier,
    }, None


def build_summary(
    history: list[dict[str, Any]],
    outcomes: list[dict[str, Any]],
    evaluations: list[dict[str, Any]],
    malformed_history: int = 0,
    malformed_outcomes: int = 0,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    forecasts: dict[str, dict[str, Any]] = {}
    conflicting_forecast_ids: set[str] = set()
    invalid_forecasts = 0
    legacy_records = 0
    for record in history:
        if record.get("record_type", "legacy_signal") == "outcome":
            continue
        ok, _ = _valid_forecast(record)
        if ok:
            fid = record["forecast_id"]
            if fid in conflicting_forecast_ids:
                continue
            if fid in forecasts and forecasts[fid] != record:
                invalid_forecasts += 1
                forecasts.pop(fid, None)
                conflicting_forecast_ids.add(fid)
            else:
                forecasts[fid] = record
        else:
            legacy_records += 1

    outcomes_by_id: dict[str, list[dict[str, Any]]] = {}
    invalid_outcomes = 0
    for record in outcomes:
        ok, _ = _valid_outcome(record)
        if not ok:
            invalid_outcomes += 1
            continue
        outcomes_by_id.setdefault(record["forecast_id"], []).append(record)

    valid_existing_evaluations: list[dict[str, Any]] = []
    invalid_evaluation_records = 0
    for record in evaluations:
        ok, _ = _valid_evaluation(record)
        if ok:
            valid_existing_evaluations.append(record)
        elif record.get("record_type") == "evaluation":
            invalid_evaluation_records += 1
    existing_ids = {str(record["forecast_id"]) for record in valid_existing_evaluations}
    new_evaluations: list[dict[str, Any]] = []
    ambiguous_outcomes = 0
    unmatched_outcomes = 0
    for fid, forecast in forecasts.items():
        if fid in existing_ids:
            continue
        candidates = outcomes_by_id.get(fid, [])
        if not candidates:
            continue
        signatures = {
            (float(o["outcome_price"]), float(o["observed_at_unix"]), o["source_id"])
            for o in candidates
        }
        if len(signatures) != 1:
            ambiguous_outcomes += 1
            continue
        evaluation, reason = _evaluate_pair(forecast, candidates[0])
        if evaluation is None:
            if reason == "outcome_outside_horizon_tolerance":
                unmatched_outcomes += 1
            continue
        new_evaluations.append(evaluation)

    evaluation_by_id: dict[str, dict[str, Any]] = {}
    conflicting_evaluation_ids: set[str] = set()
    for record in valid_existing_evaluations + new_evaluations:
        fid = record.get("forecast_id")
        if record.get("record_type") != "evaluation" or not isinstance(fid, str):
            continue
        if fid in conflicting_evaluation_ids:
            continue
        if fid in evaluation_by_id and evaluation_by_id[fid] != record:
            evaluation_by_id.pop(fid, None)
            conflicting_evaluation_ids.add(fid)
            continue
        evaluation_by_id[fid] = record
    all_evaluations = list(evaluation_by_id.values())
    scores = [float(e["brier_score"]) for e in all_evaluations if _finite_number(e.get("brier_score"))]
    baselines = [float(e["baseline_brier_score"]) for e in all_evaluations if _finite_number(e.get("baseline_brier_score"))]
    issued_count = len(forecasts)
    evaluated_count = len(scores)
    if evaluated_count:
        mean_brier = sum(scores) / evaluated_count
        mean_baseline = sum(baselines) / len(baselines) if baselines else None
        skill = 1.0 - mean_brier / mean_baseline if mean_baseline and mean_baseline > 0 else None
        status = "EVALUATED"
    elif issued_count:
        mean_brier = None
        mean_baseline = None
        skill = None
        status = "WAITING_FOR_HORIZON_ALIGNED_OUTCOMES"
    else:
        mean_brier = None
        mean_baseline = None
        skill = None
        status = "NOT_ISSUED"

    summary = {
        "status": status,
        "forecast_status": "NOT_ISSUED" if issued_count == 0 else ("ISSUED" if evaluated_count else "ISSUED_AWAITING_OUTCOME"),
        "checked_count": evaluated_count,
        "correct_count": None,
        "accuracy_pct": None,
        "mean_brier_score": mean_brier,
        "baseline_probability": BASELINE_PROBABILITY,
        "mean_baseline_brier_score": mean_baseline,
        "brier_skill_score_vs_0_5_baseline": skill,
        "issued_forecast_records_seen": issued_count,
        "legacy_or_invalid_signal_records_seen": legacy_records,
        "invalid_forecast_duplicates": invalid_forecasts,
        "conflicting_evaluation_ids": len(conflicting_evaluation_ids),
        "invalid_evaluation_records": invalid_evaluation_records,
        "invalid_outcome_records": invalid_outcomes,
        "ambiguous_outcome_sets": ambiguous_outcomes,
        "outcomes_outside_horizon_tolerance": unmatched_outcomes,
        "malformed_history_lines": malformed_history,
        "malformed_outcome_lines": malformed_outcomes,
        "method_note": (
            "Legacy sentiment scores are not price forecasts. Only explicit forecast-contract v1 records "
            "with verified event-time outcomes at the declared fixed horizon are scored. No current-price "
            "substitution; source history is read-only; accuracy_pct is intentionally null."
        ),
    }
    return summary, new_evaluations


def main() -> int:
    history, bad_history = _load_jsonl(HISTORY_PATH)
    outcomes, bad_outcomes = _load_jsonl(ROOT / "web" / "forecast_outcome_snapshots.jsonl")
    evaluations, bad_evals = _load_jsonl(OUTCOME_LEDGER_PATH)
    summary, new_evaluations = build_summary(history, outcomes, evaluations, bad_history, bad_outcomes + bad_evals)

    OUTCOME_LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    if new_evaluations:
        with OUTCOME_LEDGER_PATH.open("a", encoding="utf-8") as stream:
            for record in new_evaluations:
                stream.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")

    # Recompute summary including newly appended records.
    prior, _ = _load_jsonl(OUTCOME_LEDGER_PATH)
    summary, _ = build_summary(history, outcomes, prior, bad_history, bad_outcomes + bad_evals)
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
