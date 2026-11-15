#!/usr/bin/env python3
"""Compare adjacent sentiment windows with strict timestamp and sample gates."""

import json
import math
import os
from datetime import datetime, timedelta, timezone

KB_DIR = "ping-pongings/knowledge-base"
OUT_PATH = os.path.join(KB_DIR, "sentiment_shift.json")
SHIFT_THRESHOLD = 15
MIN_ENTRIES_PER_WINDOW = 5
FRESHNESS_THRESHOLD_HOURS = 48
FUTURE_CLOCK_SKEW_MINUTES = 5

ASSETS = {
    "XRP": {"log": os.path.join(KB_DIR, "log.jsonl"), "relevance_field": "xrp_relevance"},
    "BTC": {"log": os.path.join(KB_DIR, "log_btc.jsonl"), "relevance_field": "btc_relevance"},
}

SENTIMENT_SCORE = {"bullish": 1.0, "neutral": 0.0, "bearish": -1.0}


def parse_utc_timestamp(value):
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            return None
        return parsed.astimezone(timezone.utc)
    except (TypeError, ValueError, OverflowError):
        return None


def load_jsonl(path):
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                value = json.loads(line)
            except (TypeError, ValueError):
                continue
            if isinstance(value, dict):
                out.append(value)
    return out


def window_score(entries, relevance_field, start, end):
    """Return (score_0_100, count) from valid, relevant, timestamped entries."""
    numerator = denominator = 0.0
    used = 0
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("distilled"):
            continue
        distill = entry.get("distill", {})
        if not isinstance(distill, dict):
            continue
        weight_value = distill.get(relevance_field, 0)
        try:
            weight = float(weight_value or 0)
        except (TypeError, ValueError, OverflowError):
            continue
        if not math.isfinite(weight) or weight <= 0:
            continue
        timestamp = parse_utc_timestamp(entry.get("ingested_at"))
        if timestamp is None or not (start <= timestamp < end):
            continue
        sentiment = str(distill.get("sentiment", "")).strip().lower()
        if sentiment not in SENTIMENT_SCORE:
            continue
        numerator += SENTIMENT_SCORE[sentiment] * weight
        denominator += weight
        used += 1
    if denominator == 0:
        return None, used
    return int(round((numerator / denominator + 1) * 50)), used


def build_asset_result(entries, relevance_field, now=None):
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    now = now.astimezone(timezone.utc)
    recent_start = now - timedelta(hours=24)
    prior_start = now - timedelta(hours=48)
    recent_score, recent_n = window_score(entries, relevance_field, recent_start, now)
    prior_score, prior_n = window_score(entries, relevance_field, prior_start, recent_start)

    timestamps = [parse_utc_timestamp(e.get("ingested_at")) for e in entries if isinstance(e, dict)]
    timestamps = [ts for ts in timestamps if ts is not None]
    latest = max(timestamps) if timestamps else None
    age_hours = (now - latest).total_seconds() / 3600 if latest else None
    future_count = sum(ts > now + timedelta(minutes=FUTURE_CLOCK_SKEW_MINUTES) for ts in timestamps)

    if future_count:
        status = "FUTURE_TIMESTAMP_PRESENT"
        reason = "At least one source timestamp exceeds the five-minute clock-skew tolerance."
    elif latest is None:
        status = "NO_VALID_TIMESTAMP"
        reason = "No valid timezone-aware ingestion timestamps are available."
    elif age_hours > FRESHNESS_THRESHOLD_HOURS:
        status = "STALE_INPUT"
        reason = "The newest input is older than the 48-hour freshness limit."
    elif recent_n < MIN_ENTRIES_PER_WINDOW or prior_n < MIN_ENTRIES_PER_WINDOW:
        status = "INSUFFICIENT_SAMPLE"
        reason = "Both 24-hour windows require at least five relevant distilled entries."
    else:
        status = "COMPARISON_READY"
        reason = "Both windows meet the freshness and minimum-count gates; this remains descriptive, not predictive."

    shift = None
    if status == "COMPARISON_READY" and recent_score is not None and prior_score is not None:
        shift = recent_score - prior_score

    return {
        "status": status,
        "reason": reason,
        "latest_ingested_at_utc": latest.isoformat() if latest else None,
        "latest_input_age_hours": round(age_hours, 3) if age_hours is not None else None,
        "recent_24h_score": recent_score,
        "recent_24h_entries": recent_n,
        "prior_24h_score": prior_score,
        "prior_24h_entries": prior_n,
        "minimum_entries_per_window": MIN_ENTRIES_PER_WINDOW,
        "shift_threshold_points": SHIFT_THRESHOLD,
        "shift": shift,
        "significant_shift": shift is not None and abs(shift) >= SHIFT_THRESHOLD,
        "forecast_eligible": False,
        "interpretation": "Descriptive sentiment-window comparison only; not a calibrated probability or directional forecast.",
    }


def main():
    now = datetime.now(timezone.utc)
    results = {}
    for asset, config in ASSETS.items():
        entries = load_jsonl(config["log"])
        results[asset] = build_asset_result(entries, config["relevance_field"], now)

    out = {
        "generated_at": now.isoformat(),
        "freshness_threshold_hours": FRESHNESS_THRESHOLD_HOURS,
        "assets": results,
        "forecast_eligible": False,
    }
    os.makedirs(KB_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    web_path = os.path.join("web", os.path.basename(OUT_PATH))
    os.makedirs("web", exist_ok=True)
    with open(web_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    for asset, result in results.items():
        print(f"{asset}: {result['status']} — {result['reason']}")
        print(f"  recent={result['recent_24h_entries']} prior={result['prior_24h_entries']} shift={result['shift']}")
    print("Sentiment shift is descriptive only; forecast_eligible=false.")


if __name__ == "__main__":
    main()
