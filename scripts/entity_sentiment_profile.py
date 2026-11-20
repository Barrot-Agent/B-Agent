#!/usr/bin/env python3
"""Aggregate historical entity sentiment without presenting stale data as live."""

import json
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone

KB_DIR = "ping-pongings/knowledge-base"
XRP_LOG = os.path.join(KB_DIR, "log.jsonl")
BTC_LOG = os.path.join(KB_DIR, "log_btc.jsonl")
OUT_PATH = os.path.join(KB_DIR, "entity_sentiment_profile.json")

SENTIMENT_WEIGHT = {"bullish": 1.0, "neutral": 0.0, "bearish": -1.0}
FRESHNESS_THRESHOLD_HOURS = 48
FUTURE_CLOCK_SKEW_MINUTES = 5


def parse_utc_timestamp(value):
    """Return a timezone-aware UTC timestamp; reject missing, naive or invalid values."""
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


def build_data_freshness(entries, now=None):
    """Describe source age. This corpus aggregate is never a forecast feature."""
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    now = now.astimezone(timezone.utc)

    timestamps = []
    sentiment_timestamps = []
    invalid_timestamp_entries = 0
    future_timestamp_entries = 0

    for entry in entries:
        if not isinstance(entry, dict):
            invalid_timestamp_entries += 1
            continue
        ts = parse_utc_timestamp(entry.get("ingested_at"))
        if ts is None:
            invalid_timestamp_entries += 1
            continue
        timestamps.append(ts)
        if ts > now + timedelta(minutes=FUTURE_CLOCK_SKEW_MINUTES):
            future_timestamp_entries += 1
        distill = entry.get("distill")
        if isinstance(distill, dict) and distill.get("sentiment") in SENTIMENT_WEIGHT:
            sentiment_timestamps.append(ts)

    latest = max(timestamps) if timestamps else None
    latest_sentiment = max(sentiment_timestamps) if sentiment_timestamps else None
    age_hours = (now - latest_sentiment).total_seconds() / 3600 if latest_sentiment else None

    def count_since(hours):
        cutoff = now - timedelta(hours=hours)
        return sum(cutoff <= ts <= now for ts in sentiment_timestamps)

    if future_timestamp_entries:
        status = "FUTURE_TIMESTAMP_PRESENT"
        reason = "At least one ingested_at timestamp exceeds the allowed five-minute clock-skew tolerance."
    elif latest_sentiment is None:
        status = "NO_VALID_DISTILLED_TIMESTAMP"
        reason = "No timestamped entries with a recognized sentiment label are available."
    elif age_hours > FRESHNESS_THRESHOLD_HOURS:
        status = "STALE"
        reason = "The newest sentiment-bearing entry is older than the 48-hour freshness limit."
    else:
        status = "FRESH"
        reason = "The newest sentiment-bearing entry is within the 48-hour freshness limit."

    return {
        "status": status,
        "reason": reason,
        "earliest_ingested_at_utc": min(timestamps).isoformat() if timestamps else None,
        "latest_ingested_at_utc": latest.isoformat() if latest else None,
        "latest_sentiment_ingested_at_utc": latest_sentiment.isoformat() if latest_sentiment else None,
        "latest_sentiment_age_hours": round(age_hours, 3) if age_hours is not None else None,
        "recent_24h_sentiment_entries": count_since(24),
        "recent_48h_sentiment_entries": count_since(48),
        "recent_7d_sentiment_entries": count_since(168),
        "invalid_timestamp_entries": invalid_timestamp_entries,
        "future_timestamp_entries": future_timestamp_entries,
        "freshness_threshold_hours": FRESHNESS_THRESHOLD_HOURS,
        "forecast_eligible": False,
        "interpretation": "Historical corpus aggregate only; not a point-in-time market sentiment feature or directional forecast.",
    }


def build_profile(xrp_entries, btc_entries, now=None):
    now = now or datetime.now(timezone.utc)
    all_entries = [(e, "XRP") for e in xrp_entries] + [(e, "BTC") for e in btc_entries]
    profiles = defaultdict(lambda: {
        "bullish": 0,
        "neutral": 0,
        "bearish": 0,
        "assets_seen_in": set(),
        "example_headlines": [],
    })

    for entry, asset in all_entries:
        distill = entry.get("distill", {})
        if not isinstance(distill, dict):
            continue
        sentiment = distill.get("sentiment")
        if sentiment not in SENTIMENT_WEIGHT:
            continue
        entities = distill.get("entities", [])
        if not isinstance(entities, list):
            continue
        for entity in entities:
            ent_norm = str(entity).strip()
            if not ent_norm:
                continue
            profile = profiles[ent_norm]
            profile[sentiment] += 1
            profile["assets_seen_in"].add(asset)
            if len(profile["example_headlines"]) < 3:
                profile["example_headlines"].append(str(entry.get("title", ""))[:100])

    results = []
    for entity, profile in profiles.items():
        total = profile["bullish"] + profile["neutral"] + profile["bearish"]
        net_score = (profile["bullish"] - profile["bearish"]) / total if total else 0.0
        results.append({
            "entity": entity,
            "total_mentions": total,
            "bullish": profile["bullish"],
            "neutral": profile["neutral"],
            "bearish": profile["bearish"],
            "net_sentiment_score": round(net_score, 3),
            "assets_seen_in": sorted(profile["assets_seen_in"]),
            "example_headlines": profile["example_headlines"],
            "score_scope": "all_available_historical_entries",
            "forecast_eligible": False,
        })

    results.sort(key=lambda item: item["total_mentions"], reverse=True)
    return {
        "generated_at_utc": now.astimezone(timezone.utc).isoformat(),
        "generated_from": {"xrp_entries": len(xrp_entries), "btc_entries": len(btc_entries)},
        "data_freshness": {
            "XRP": build_data_freshness(xrp_entries, now),
            "BTC": build_data_freshness(btc_entries, now),
        },
        "interpretation": "Entity scores aggregate every available historical sentiment label. They are not current-window sentiment, calibrated probabilities, or forecasts.",
        "forecast_eligible": False,
        "unique_entities_profiled": len(results),
        "entities": results,
    }


def main():
    xrp_entries = load_jsonl(XRP_LOG)
    btc_entries = load_jsonl(BTC_LOG)
    out = build_profile(xrp_entries, btc_entries)

    os.makedirs(KB_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    web_path = os.path.join("web", os.path.basename(OUT_PATH))
    os.makedirs("web", exist_ok=True)
    with open(web_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"Unique entities profiled: {out['unique_entities_profiled']}")
    for asset, freshness in out["data_freshness"].items():
        print(f"{asset}: {freshness['status']} — latest sentiment entry {freshness['latest_sentiment_ingested_at_utc']}; age_hours={freshness['latest_sentiment_age_hours']}")
    print("Historical entity scores are descriptive only; forecast_eligible=false.")


if __name__ == "__main__":
    main()
