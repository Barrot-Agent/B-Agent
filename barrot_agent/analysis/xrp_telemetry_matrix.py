#!/usr/bin/env python3
"""Evidence-gated XRP snapshot renderer; no live fetches, hard-coded signals, or trading."""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

MAX_MARKET_SKEW_SECONDS = 60
MIN_WALK_FORWARD_SAMPLES = 30


class SnapshotValidationError(ValueError):
    """Raised when a research snapshot fails its evidence contract."""


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise SnapshotValidationError(f"{field} must be a non-empty string")
    return value.strip()


def _utc(value, field):
    if not isinstance(value, str) or not value:
        raise SnapshotValidationError(f"{field} must be a UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SnapshotValidationError(f"{field} is not ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise SnapshotValidationError(f"{field} must include a UTC timezone")
    return parsed.astimezone(timezone.utc)


def _number(value, field, minimum=None, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise SnapshotValidationError(f"{field} must be a finite number")
    value = float(value)
    if minimum is not None and value < minimum:
        raise SnapshotValidationError(f"{field} must be >= {minimum}")
    if maximum is not None and value > maximum:
        raise SnapshotValidationError(f"{field} must be <= {maximum}")
    return value


def validate_snapshot(snapshot):
    if not isinstance(snapshot, dict) or snapshot.get("schema_version") != "1.0":
        raise SnapshotValidationError("snapshot must be an object with schema_version '1.0'")
    _text(snapshot.get("snapshot_id"), "snapshot_id")
    captured = _utc(snapshot.get("captured_at_utc"), "captured_at_utc")
    cutoff = _utc(snapshot.get("data_cutoff_utc"), "data_cutoff_utc")
    if cutoff > captured:
        raise SnapshotValidationError("data_cutoff_utc cannot be later than captured_at_utc")

    sources = snapshot.get("sources", [])
    if not isinstance(sources, list):
        raise SnapshotValidationError("sources must be a list")
    source_ids, groups = set(), set()
    for i, source in enumerate(sources):
        if not isinstance(source, dict):
            raise SnapshotValidationError(f"sources[{i}] must be an object")
        sid = _text(source.get("source_id"), f"sources[{i}].source_id")
        _text(source.get("publisher"), f"sources[{i}].publisher")
        if not _text(source.get("url"), f"sources[{i}].url").startswith("https://"):
            raise SnapshotValidationError(f"sources[{i}].url must use HTTPS")
        groups.add(_text(source.get("independence_group"), f"sources[{i}].independence_group"))
        _text(source.get("evidence_class"), f"sources[{i}].evidence_class")
        if _utc(source.get("retrieved_at_utc"), f"sources[{i}].retrieved_at_utc") > captured:
            raise SnapshotValidationError(f"sources[{i}] is later than captured_at_utc")
        if sid in source_ids:
            raise SnapshotValidationError(f"duplicate source_id: {sid}")
        source_ids.add(sid)

    observations = snapshot.get("market_observations", [])
    if not isinstance(observations, list):
        raise SnapshotValidationError("market_observations must be a list")
    venues, times = set(), []
    for i, obs in enumerate(observations):
        if not isinstance(obs, dict):
            raise SnapshotValidationError(f"market_observations[{i}] must be an object")
        _text(obs.get("symbol"), f"market_observations[{i}].symbol")
        venues.add(_text(obs.get("venue"), f"market_observations[{i}].venue"))
        sid = _text(obs.get("source_id"), f"market_observations[{i}].source_id")
        if sid not in source_ids:
            raise SnapshotValidationError(f"market_observations[{i}] references unknown source_id {sid}")
        _number(obs.get("price"), f"market_observations[{i}].price", 0.00000001)
        ts = _utc(obs.get("timestamp_utc"), f"market_observations[{i}].timestamp_utc")
        if ts > cutoff:
            raise SnapshotValidationError(f"market_observations[{i}] is later than data_cutoff_utc")
        times.append(ts)

    forecast = snapshot.get("forecast")
    if not isinstance(forecast, dict):
        raise SnapshotValidationError("forecast must be an object")
    status = forecast.get("status")
    if status == "NOT_ISSUED":
        _text(forecast.get("reason"), "forecast.reason")
        return {"sources": len(source_ids), "groups": groups, "observations": len(observations), "venues": venues}
    if status != "ISSUED":
        raise SnapshotValidationError("forecast.status must be NOT_ISSUED or ISSUED")

    _text(forecast.get("target"), "forecast.target")
    _text(forecast.get("horizon"), "forecast.horizon")
    _text(forecast.get("model_version"), "forecast.model_version")
    _number(forecast.get("probability"), "forecast.probability", 0, 1)
    _number(forecast.get("confidence"), "forecast.confidence", 0, 1)
    if forecast.get("data_cutoff_utc") != snapshot.get("data_cutoff_utc"):
        raise SnapshotValidationError("forecast.data_cutoff_utc must match snapshot data_cutoff_utc")
    for field in ("assumptions", "alternatives"):
        values = forecast.get(field)
        if not isinstance(values, list) or not values:
            raise SnapshotValidationError(f"forecast.{field} must be a non-empty list")
        for i, value in enumerate(values):
            _text(value, f"forecast.{field}[{i}]")
    if len(groups) < 2:
        raise SnapshotValidationError("ISSUED forecast requires at least two independent source groups")
    if len(venues) < 2 or len(times) < 2:
        raise SnapshotValidationError("ISSUED forecast requires at least two venues")
    if (max(times) - min(times)).total_seconds() > MAX_MARKET_SKEW_SECONDS:
        raise SnapshotValidationError("market observations exceed synchronization window")

    ev = forecast.get("evaluation")
    if not isinstance(ev, dict):
        raise SnapshotValidationError("ISSUED forecast requires evaluation evidence")
    samples = ev.get("walk_forward_samples")
    if isinstance(samples, bool) or not isinstance(samples, int) or samples < MIN_WALK_FORWARD_SAMPLES:
        raise SnapshotValidationError(f"walk_forward_samples must be >= {MIN_WALK_FORWARD_SAMPLES}")
    if ev.get("out_of_sample") is not True or ev.get("leakage_check") != "passed" or ev.get("drift_status") != "stable":
        raise SnapshotValidationError("out-of-sample, leakage and drift checks must all pass")
    if _number(ev.get("model_brier_score"), "model_brier_score", 0) >= _number(ev.get("baseline_brier_score"), "baseline_brier_score", 0):
        raise SnapshotValidationError("model Brier score must beat the baseline")
    if _number(ev.get("model_log_loss"), "model_log_loss", 0) >= _number(ev.get("baseline_log_loss"), "baseline_log_loss", 0):
        raise SnapshotValidationError("model log loss must beat the baseline")
    calibration = _number(ev.get("calibration_error"), "calibration_error", 0)
    tolerance = _number(ev.get("calibration_tolerance"), "calibration_tolerance", 0.00000001, 1)
    if calibration > tolerance:
        raise SnapshotValidationError("calibration error exceeds declared tolerance")
    _text(ev.get("evaluation_artifact_id"), "evaluation_artifact_id")
    if not _text(ev.get("evaluation_run_url"), "evaluation_run_url").startswith("https://"):
        raise SnapshotValidationError("evaluation_run_url must use HTTPS")
    outcome = forecast.get("outcome")
    if not isinstance(outcome, dict) or outcome.get("status") not in {"PENDING", "RESOLVED"}:
        raise SnapshotValidationError(f"forecast.outcome.status must be PENDING or RESOLVED")
    if outcome.get("status") == "RESOLVED":
        _utc(outcome.get("resolved_at_utc"), "outcome.resolved_at_utc")
        _number(outcome.get("observed_value"), "outcome.observed_value"))
        if not isinstance(outcome.get("scoring"), dict):
            raise SnapshotValidationError("resolved outcome requires scoring")
    return {"sources": len(source_ids), "groups": groups, "observations": len(observations), "venues": venues}


def render_report(snapshot):
    summary = validate_snapshot(snapshot)
    forecast = snapshot["forecast"]
    lines = [
        "# XRP Evidence Report", "",
        f"- Snapshot: `{snapshot['snapshot_id']}`",
        f"- Captured: {snapshot['captured_at_utc']}",
        f"- Data cutoff: {snapshot['data_cutoff_utc']}",
        f"- Sources: {summary['sources']} across {len(summary['groups])} independence groups",
        f"- Market observations: {summary['observations']} across {len(summary['venues'])} venues", "",
        f"## Forecast status: {forecast['status']}", "",
    ]
    if forecast["status"] == "NOT_ISSUED":
        lines += [f"Reason: {forecast['reason']}", "", "No directional forecast or trading recommendation was issued."]
    else:
        ev = forecast["evaluation"]
        lines += [
            "**Research-only forecast. Not a trading instruction.**", "",
            f"- Target: {forecast['target']}", f"- Horizon: {forecast['horizon']}",
            f"- Probability: {forecast['probability]}:.4f", f"- Confidence: {forecast['confidence']}:.4f",
            f"- Model version: {forecast['model_version']}",
            f"- Walk-forward samples: {ev['walk_forward_samples']}",
            f"- Brier model/baseline: {ev['model_brier_score']} / {ev['baseline_brier_score']}",
            f"- Log-loss model/baseline: {ev['model_log_loss']} / {ev['baseline_log_loss']}",
            f"- Calibration error/tolerance: {ev['calibration_error']} / {ev['calibration_tolerance']}",
            f"- Outcome: {forecast['outcome']['status']}", "", "### Assumptions",
            *[f"- {x}" for x in forecast["assumptions"]], "", "### Alternatives",
            *[f"- {x}" for x in forecast["alternatives"]], "",
            f"Evaluation evidence: {ev['evaluation_run_url']}",
        ]
    return "\n".join(lines) + "\n"


def write_report(report, output_path):
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x", encoding="utf-8") as handle:
        handle.write(report)
    return destination


def main(argv=None):
    parser = argparse.ArgumentParser(description="Render a captured XRP evidence snapshot; no live fetch or trading.")
    parser.add_argument("--input", required=True, help="Captured JSON evidence snapshot")
    parser.add_argument("--output", required=True, help="New report path; existing files are never overwritten")
    args = parser.parse_args(argv)
    try:
        snapshot = json.loads(Path(args.input).read_text(encoding="utf-8"))
        destination = write_report(render_report(snapshot), args.output)
    except (OSError, json.JSONDecodeError, SnapshotValidationError) as exc:
        print(f"XRP evidence report not written: {exc}", file=sys.stderr)
        return 2
    print(f"Evidence report written: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
