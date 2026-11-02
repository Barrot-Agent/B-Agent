"""Render captured XRP evidence only; never fetch, invent, recommend, or trade."""
from __future__ import annotations
import argparse, json, math, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

MIN_WALK_FORWARD_SAMPLES = 30
MAX_MARKET_SKEW_SECONDS = 60

class EvidenceError(ValueError):
    pass

def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise EvidenceError(f"{field} must be non-empty")
    return value.strip()

def _utc(value, field):
    try:
        dt = datetime.fromisoformat(_text(value, field).replace("Z", "+00:00"))
    except ValueError as exc:
        raise EvidenceError(f"{field} must be ISO-8601 UTC") from exc
    if dt.tzinfo is None or dt.utcoffset() != timedelta(0):
        raise EvidenceError(f"{field} must include a UTC timezone")
    return dt.astimezone(timezone.utc)

def _num(value, field, low=0, high=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise EvidenceError(f"{field} must be finite numeric")
    value = float(value)
    if value < low or (high is not None and value > high):
        raise EvidenceError(f"{field} is outside the permitted range")
    return value

def validate_snapshot(s):
    if not isinstance(s, dict) or s.get("schema_version") != "1.0":
        raise EvidenceError("snapshot must be an object with schema_version 1.0")
    _text(s.get("snapshot_id"), "snapshot_id")
    captured, cutoff = _utc(s.get("captured_at_utc"), "captured_at_utc"), _utc(s.get("data_cutoff_utc"), "data_cutoff_utc")
    if cutoff > captured:
        raise EvidenceError("data cutoff cannot follow capture time")
    sources = s.get("sources", [])
    if not isinstance(sources, list):
        raise EvidenceError("sources must be a list")
    ids, groups = set(), set()
    for i, src in enumerate(sources):
        if not isinstance(src, dict):
            raise EvidenceError(f"sources[{i}] must be an object")
        sid = _text(src.get("source_id"), f"sources[{i}].source_id")
        _text(src.get("publisher"), f"sources[{i}].publisher")
        if not _text(src.get("url"), f"sources[{i}].url").startswith("https://"):
            raise EvidenceError("source URLs must use HTTPS")
        groups.add(_text(src.get("independence_group"), f"sources[{i}].independence_group"))
        _text(src.get("evidence_class"), f"sources[{i}].evidence_class")
        if _utc(src.get("retrieved_at_utc"), f"sources[{i}].retrieved_at_utc") > captured:
            raise EvidenceError("source retrieval time follows snapshot capture")
        if sid in ids:
            raise EvidenceError(f"duplicate source_id: {sid}")
        ids.add(sid)
    observations = s.get("market_observations", [])
    if not isinstance(observations, list):
        raise EvidenceError("market_observations must be a list")
    venues, times, symbols = set(), [], set()
    for i, obs in enumerate(observations):
        if not isinstance(obs, dict):
            raise EvidenceError(f"market_observations[{i}] must be an object")
        symbols.add(_text(obs.get("symbol"), f"observations[{i}].symbol"))
        venues.add(_text(obs.get("venue"), f"observations[{i}].venue"))
        if _text(obs.get("source_id"), f"observations[{i}].source_id") not in ids:
            raise EvidenceError("market observation references unknown source_id")
        _num(obs.get("price"), f"observations[{i}].price", 0.00000001)
        ts = _utc(obs.get("timestamp_utc"), f"observations[{i}].timestamp_utc")
        if ts > cutoff:
            raise EvidenceError("market observation is later than data cutoff")
        times.append(ts)
    forecast = s.get("forecast")
    if not isinstance(forecast, dict):
        raise EvidenceError("forecast must be an object")
    status = forecast.get("status")
    if status == "NOT_ISSUED":
        _text(forecast.get("reason"), "forecast.reason")
        return {"sources": len(ids), "groups": groups, "observations": len(observations), "venues": venues}
    if status != "ISSUED":
        raise EvidenceError("forecast status must be NOT_ISSUED or ISSUED")
    for field in ("target", "horizon", "model_version"):
        _text(forecast.get(field), f"forecast.{field}")
    _num(forecast.get("probability"), "probability", 0, 1)
    _num(forecast.get("confidence"), "confidence", 0, 1)
    if forecast.get("data_cutoff_utc") != s.get("data_cutoff_utc"):
        raise EvidenceError("forecast cutoff must match snapshot cutoff")
    for field in ("assumptions", "alternatives"):
        values = forecast.get(field)
        if not isinstance(values, list) or not values:
            raise EvidenceError(f"forecast.{field} must be non-empty")
        for value in values:
            _text(value, field)
    if len(groups) < 2 or len(venues) < 2 or len(times) < 2:
        raise EvidenceError("ISSUED forecast requires two independent sources and two venues")
    if len(symbols) != 1 or (max(times) - min(times)).total_seconds() > MAX_MARKET_SKEW_SECONDS:
        raise EvidenceError("market observations exceed synchronization window or mix symbols")
    ev = forecast.get("evaluation")
    if not isinstance(ev, dict):
        raise EvidenceError("ISSUED forecast requires evaluation evidence")
    n = ev.get("walk_forward_samples")
    if isinstance(n, bool) or not isinstance(n, int) or n < MIN_WALK_FORWARD_SAMPLES:
        raise EvidenceError(f"walk_forward_samples must be at least {MIN_WALK_FORWARD_SAMPLES}")
    if ev.get("out_of_sample") is not True or ev.get("leakage_check") != "passed" or ev.get("drift_status") != "stable":
        raise EvidenceError("out-of-sample, leakage and drift checks must pass")
    if _num(ev.get("model_brier_score"), "model_brier_score") >= _num(ev.get("baseline_brier_score"), "baseline_brier_score"):
        raise EvidenceError("model Brier score must beat baseline")
    if _num(ev.get("model_log_loss"), "model_log_loss") >= _num(ev.get("baseline_log_loss"), "baseline_log_loss"):
        raise EvidenceError("model log loss must beat baseline")
    if _num(ev.get("calibration_error"), "calibration_error") > _num(ev.get("calibration_tolerance"), "calibration_tolerance", 0.00000001, 1):
        raise EvidenceError("calibration error exceeds tolerance")
    _text(ev.get("evaluation_artifact_id"), "evaluation_artifact_id")
    if not _text(ev.get("evaluation_run_url"), "evaluation_run_url").startswith("https://"):
        raise EvidenceError("evaluation run URL must use HTTPS")
    outcome = forecast.get("outcome")
    if not isinstance(outcome, dict) or outcome.get("status") not in {"PENDING", "RESOLVED"}:
        raise EvidenceError("forecast outcome must be PENDING or RESOLVED")
    if outcome["status"] == "RESOLVED":
        _utc(outcome.get("resolved_at_utc"), "outcome.resolved_at_utc")
        _num(outcome.get("observed_value"), "outcome.observed_value", low=-math.inf)
        if not isinstance(outcome.get("scoring"), dict):
            raise EvidenceError("resolved outcome requires scoring")
    return {"sources": len(ids), "groups": groups, "observations": len(observations), "venues": venues}

def render_report(s):
    summary = validate_snapshot(s)
    f = s["forecast"]
    lines = ["# XRP Evidence Report", "", f"- Snapshot: {s['snapshot_id']}", f"- Captured: {s['captured_at_utc']}", f"- Data cutoff: {s['data_cutoff_utc']}", f"- Sources: {summary['sources']} across {len(summary['groups'])} independence groups", f"- Market observations: {summary['observations']} across {len(summary['venues'])} venues", "", f"## Forecast status: {f['status']}", ""]
    if f["status"] == "NOT_ISSUED":
        lines += [f"Reason: {f['reason']}", "", "No directional forecast or trading recommendation was issued."]
    else:
        ev = f["evaluation"]
        lines += ["**Research-only forecast. Not a trading instruction.**", "", f"- Target: {f['target']}", f"- Horizon: {f['horizon']}", f"- Probability: {f['probability']:.4f}", f"- Confidence: {f['confidence']:.4f}", f"- Model: {f['model_version']}", f"- Walk-forward samples: {ev['walk_forward_samples']}", f"- Brier model/baseline: {ev['model_brier_score']} / {ev['baseline_brier_score']}", f"- Log-loss model/baseline: {ev['model_log_loss']} / {ev['baseline_log_loss']}", f"- Calibration error/tolerance: {ev['calibration_error']} / {ev['calibration_tolerance']}", f"- Outcome: {f['outcome']['status']}", "", "### Assumptions", *[f"- {x}" for x in f["assumptions"]], "", "### Alternatives", *[f"- {x}" for x in f["alternatives"]], "", f"Evaluation evidence: {ev['evaluation_run_url']}"]
    return "\n".join(lines) + "\n"

def write_report(report, output_path):
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(report)
    return path

def main(argv=None):
    parser = argparse.ArgumentParser(description="Render captured XRP evidence; no live fetches or trading.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True, help="New path; existing files are never overwritten")
    args = parser.parse_args(argv)
    try:
        snapshot = json.loads(Path(args.input).read_text(encoding="utf-8"))
        destination = write_report(render_report(snapshot), args.output)
    except (OSError, json.JSONDecodeError, EvidenceError) as exc:
        print(f"XRP evidence report not written: {exc}", file=sys.stderr)
        return 2
    print(f"Evidence report written: {destination}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
