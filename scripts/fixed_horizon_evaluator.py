#!/usr/bin/env python3
"""Fixed-horizon diagnostic for Barrot signal history; no network calls or input mutation."""
from __future__ import annotations
import argparse, bisect, hashlib, json, math
from datetime import datetime, timezone
from pathlib import Path


LABELS = ("bearish", "flat", "bullish")


def number(value):
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return value if math.isfinite(value) else None


def timestamp(row):
    n = number(row.get("generated_at_unix"))
    if n is not None and n > 0:
        return n
    raw = row.get("timestamp")
    if not isinstance(raw, str):
        return None
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return dt.timestamp() if dt.tzinfo is not None else None
    except (ValueError, OverflowError, OSError):
        return None


def utc(ts):
    return datetime.fromtimestamp(ts, timezone.utc).isoformat()


def label_return(pct, band):
    return "bullish" if pct > band else "bearish" if pct < -band else "flat"


def label_score(score, bear, bull):
    return "bearish" if score < bear else "bullish" if score > bull else "flat"


def exclusion(row):
    status = str(row.get("signal_status", "")).lower()
    basis = str(row.get("score_basis", "")).lower()
    source = str(row.get("source", "")).lower()
    if status == "unavailable" or basis == "unavailable_placeholder":
        return "unavailable"
    if status == "news_only" or basis == "news_only":
        return "news_only"
    if row.get("model_available") is False:
        return "model_unavailable"
    if "sentiment unavailable" in source or "provider_failed" in source:
        return "legacy_provider_failure"
    score = number(row.get("score"))
    if score is None or not 0 <= score <= 100:
        return "invalid_score"
    return None


def metrics(rows, key):
    actual_counts = {k: 0 for k in LABELS}
    pred_counts = {k: 0 for k in LABELS}
    cm = {a: {p: 0 for p in LABELS} for a in LABELS}
    for row in rows:
        a, p = row["actual_label"], row[key]
        actual_counts[a] += 1
        pred_counts[p] += 1
        cm[a][p] += 1
    n = len(rows)
    acc = sum(cm[k][k] for k in LABELS) / n if n else None
    recalls = [cm[k][k] / actual_counts[k] for k in LABELS if actual_counts[k]]
    return {
        "n": n,
        "accuracy": round(acc, 6) if acc is not None else None,
        "balanced_accuracy": round(sum(recalls) / len(recalls), 6) if recalls else None,
        "actual_counts": actual_counts,
        "predicted_counts": pred_counts,
        "confusion_matrix": cm,
    }


def build_report(entries, *, horizon_hours=24.0, tolerance_minutes=45.0,
                 bearish_threshold=40.0, bullish_threshold=60.0,
                 neutral_band_pct=0.5, generated_at_utc=None):
    if horizon_hours <= 0:
        raise ValueError("horizon_hours must be positive")
    if tolerance_minutes < 0 or tolerance_minutes >= horizon_hours * 60:
        raise ValueError("tolerance_minutes must be >= 0 and less than horizon")
    if not 0 <= bearish_threshold < bullish_threshold <= 100:
        raise ValueError("thresholds must satisfy 0 <= bearish < bullish <= 100")
    if neutral_band_pct < 0:
        raise ValueError("neutral_band_pct must be non-negative")

    obs_by_ts, quality = {}, {"invalid_timestamp_or_price": 0, "duplicate_timestamps": 0}
    for i, row in enumerate(entries):
        ts, price = timestamp(row), number(row.get("price_at_emission"))
        if ts is None or price is None or price <= 0:
            quality["invalid_timestamp_or_price"] += 1
            continue
        if ts in obs_by_ts:
            quality["duplicate_timestamps"] += 1
            continue
        obs_by_ts[ts] = {"ts": ts, "price": price, "index": i}
    obs = sorted(obs_by_ts.values(), key=lambda x: x["ts"])
    times = [x["ts"] for x in obs]

    counts = {
        "eligible_signals": 0, "excluded_unavailable": 0, "excluded_news_only": 0,
        "excluded_model_unavailable": 0, "excluded_legacy_provider_failure": 0,
        "excluded_invalid_score": 0, "unmatched_horizon": 0,
        "outcome_observation_already_used": 0,
    }
    key_map = {
        "unavailable": "excluded_unavailable", "news_only": "excluded_news_only",
        "model_unavailable": "excluded_model_unavailable",
        "legacy_provider_failure": "excluded_legacy_provider_failure",
        "invalid_score": "excluded_invalid_score",
    }
    signals = []
    for i, row in enumerate(entries):
        reason = exclusion(row)
        if reason:
            counts[key_map[reason]] += 1
            continue
        ts, price, score = timestamp(row), number(row.get("price_at_emission")), number(row.get("score"))
        if ts is None or price is None or price <= 0 or score is None:
            counts["excluded_invalid_score"] += 1
            continue
        signals.append({
            "ts": ts, "price": price, "score": score,
            "pred": label_score(score, bearish_threshold, bullish_threshold),
            "index": i,
            "sha256": hashlib.sha256(json.dumps(row, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        })
    signals.sort(key=lambda x: (x["ts"], x["index"]))
    counts["eligible_signals"] = len(signals)

    horizon = horizon_hours * 3600
    tolerance = tolerance_minutes * 60
    used, samples = set(), []
    for s in signals:
        target = s["ts"] + horizon
        lo, hi = bisect.bisect_left(times, target - tolerance), bisect.bisect_right(times, target + tolerance)
        candidates = [o for o in obs[lo:hi] if o["ts"] > s["ts"]]
        candidates.sort(key=lambda o: (abs(o["ts"] - target), o["ts"]))
        chosen = next((o for o in candidates if o["ts"] not in used), None)
        if chosen is None:
            counts["outcome_observation_already_used" if candidates else "unmatched_horizon"] += 1
            continue
        used.add(chosen["ts"])
        ret = (chosen["price"] / s["price"] - 1) * 100
        samples.append({
            "issued_at_utc": utc(s["ts"]), "target_at_utc": utc(target),
            "outcome_observed_at_utc": utc(chosen["ts"]),
            "actual_horizon_hours": round((chosen["ts"] - s["ts"]) / 3600, 6),
            "target_offset_minutes": round((chosen["ts"] - target) / 60, 3),
            "issue_price": s["price"], "outcome_price": chosen["price"],
            "forward_return_pct": round(ret, 6),
            "predicted_label": s["pred"], "actual_label": label_return(ret, neutral_band_pct),
            "score": s["score"], "input_record_sha256": s["sha256"],
        })

    split = int(len(samples) * 0.7)
    holdout = samples[split:] if len(samples) >= 5 else []
    for i, row in enumerate(samples):
        issue_ts = datetime.fromisoformat(row["issued_at_utc"]).timestamp()
        matured = [
            x["actual_label"] for x in samples[:i]
            if datetime.fromisoformat(x["outcome_observed_at_utc"]).timestamp() <= issue_ts
        ]
        freq = {k: matured.count(k) for k in LABELS}
        top = max(freq.values()) if matured else 0
        winners = [k for k, v in freq.items() if v == top] if matured else ["flat"]
        row["expanding_matured_label_majority_baseline"] = (
            "flat" if "flat" in winners else sorted(winners)[0]
        )
        row["always_flat_baseline"] = "flat"

    holdout = samples[split:] if len(samples) >= 5 else []
    now = generated_at_utc or datetime.now(timezone.utc).isoformat()
    return {
        "schema_version": 1, "status": "diagnostic_only",
        "generated_at_utc": now,
        "data_cutoff_utc": utc(obs[-1]["ts"]) if obs else None,
        "input": {
            "records_seen": len(entries), "price_observations": len(obs),
            "first_price_observation_utc": utc(obs[0]["ts"]) if obs else None,
            "last_price_observation_utc": utc(obs[-1]["ts"]) if obs else None,
            "quality_counts": quality, "matching_counts": counts,
        },
        "method": {
            "horizon_hours": horizon_hours, "tolerance_minutes": tolerance_minutes,
            "score_rule": f"score < {bearish_threshold}: bearish; score > {bullish_threshold}: bullish; otherwise flat",
            "outcome_rule": f"forward return > {neutral_band_pct}%: bullish; < -{neutral_band_pct}%: bearish; otherwise flat",
            "split": "chronological first 70% / final 30%; no holdout reported with fewer than 5 matched samples",
            "baseline": "always-flat plus expanding majority using only prior outcomes observed by the current issue time",
            "timestamp_limit": "price_at_emission has no separate provider quote timestamp; generated_at_unix may precede price retrieval slightly",
            "integrity_limit": "legacy signal_history.jsonl is mutable; row hashes identify observed input rows but do not reconstruct immutable originals",
            "dependence_limit": "overlapping hourly signals are not independent; each future price observation is used at most once",
            "probability_calibration": "not computed: sentiment score/confidence are not validated direction probabilities",
        },
        "all_matched_samples": len(samples),
        "chronological_holdout": {
            "n": len(holdout), "minimum_samples_for_interpretation": 30,
            "sample_size_warning": len(holdout) < 30,
            "score_rule": metrics(holdout, "predicted_label"),
            "always_flat_baseline": metrics(holdout, "always_flat_baseline"),
            "expanding_matured_label_majority_baseline": metrics(holdout, "expanding_matured_label_majority_baseline"),
        },
        "calibration": {"status": "not_computed", "brier_score": None, "log_loss": None},
        "samples": samples,
        "production_gate": {
            "passed": False,
            "reasons": [
                "Diagnostic only; immutable point-in-time input store is absent.",
                "Price quote timestamps are not recorded separately.",
                "No calibrated price-direction probabilities or validated out-of-sample skill.",
                "Main signal emitter still encodes provider failure as zero until PR #1130 is integrated.",
            ],
        },
    }


def load_jsonl(path):
    rows, invalid = [], 0
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                invalid += 1
                continue
            if isinstance(row, dict):
                rows.append(row)
            else:
                invalid += 1
    return rows, invalid


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--history", type=Path, default=Path("web/signal_history.jsonl"))
    p.add_argument("--output", type=Path, default=Path("web/fixed_horizon_evaluation.json"))
    p.add_argument("--horizon-hours", type=float, default=24)
    p.add_argument("--tolerance-minutes", type=float, default=45)
    p.add_argument("--bearish-threshold", type=float, default=40)
    p.add_argument("--bullish-threshold", type=float, default=60)
    p.add_argument("--neutral-band-pct", type=float, default=0.5)
    a = p.parse_args()
    if not a.history.is_file():
        p.error(f"history file does not exist: {a.history}")
    rows, invalid = load_jsonl(a.history)
    report = build_report(rows, horizon_hours=a.horizon_hours, tolerance_minutes=a.tolerance_minutes,
                          bearish_threshold=a.bearish_threshold, bullish_threshold=a.bullish_threshold,
                          neutral_band_pct=a.neutral_band_pct)
    report["input"]["invalid_json_lines"] = invalid
    a.output.parent.mkdir(parents=True, exist_ok=True)
    tmp = a.output.with_suffix(a.output.suffix + ".tmp")
    tmp.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    tmp.replace(a.output)
    print(json.dumps({
        "status": report["status"], "matched": report["all_matched_samples"],
        "holdout_n": report["chronological_holdout"]["n"],
        "sample_size_warning": report["chronological_holdout"]["sample_size_warning"],
        "production_gate_passed": report["production_gate"]["passed"], "output": str(a.output)
    }, indent=2))


if __name__ == "__main__":
    main()
