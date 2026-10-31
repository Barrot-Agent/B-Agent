#!/usr/bin/env python3
"""
BARROT-Ω SENTIMENT SHIFT DETECTOR — compares relevance-weighted sentiment
between two adjacent time windows (default: last 24h vs the 24h before that)
per asset, using the same weighting logic as emit_signal.py. Flags a
meaningful shift if the two windows' scores differ by more than a threshold.
Pure arithmetic over existing distilled entries. No new infrastructure.
"""

import json
import os
from datetime import datetime, timezone, timedelta

KB_DIR = "ping-pongings/knowledge-base"
OUT_PATH = os.path.join(KB_DIR, "sentiment_shift.json")
SHIFT_THRESHOLD = 15  # points on the 0-100 scale emit_signal.py uses

ASSETS = {
    "XRP": {"log": os.path.join(KB_DIR, "log.jsonl"), "relevance_field": "xrp_relevance"},
    "BTC": {"log": os.path.join(KB_DIR, "log_btc.jsonl"), "relevance_field": "btc_relevance"},
}


def load_jsonl(path):
    if not os.path.exists(path):
        return []
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out


def window_score(entries, relevance_field, start, end):
    """Same relevance-weighted scoring as emit_signal.py's _news_score,
    restricted to entries whose ingested_at falls in [start, end)."""
    num = den = 0.0
    used = 0
    for e in entries:
        d = e.get("distill", {})
        if not e.get("distilled") or not d:
            continue
        w = float(d.get(relevance_field, 0) or 0)
        if w <= 0:
            continue
        try:
            ts = datetime.fromisoformat(e.get("ingested_at", "").replace("Z", "+00:00"))
        except Exception:
            continue
        if not (start <= ts < end):
            continue
        s = {"bullish": 1.0, "neutral": 0.0, "bearish": -1.0}.get(d.get("sentiment"), 0.0)
        num += s * w
        den += w
        used += 1
    if den == 0:
        return None, used
    return int(round((num / den + 1) * 50)), used


def main():
    now = datetime.now(timezone.utc)
    recent_start = now - timedelta(hours=24)
    prior_start = now - timedelta(hours=48)

    results = {}
    for asset, cfg in ASSETS.items():
        entries = load_jsonl(cfg["log"])
        recent_score, recent_n = window_score(entries, cfg["relevance_field"], recent_start, now)
        prior_score, prior_n = window_score(entries, cfg["relevance_field"], prior_start, recent_start)

        shift = None
        flagged = False
        if recent_score is not None and prior_score is not None:
            shift = recent_score - prior_score
            flagged = abs(shift) >= SHIFT_THRESHOLD

        results[asset] = {
            "recent_24h_score": recent_score,
            "recent_24h_entries": recent_n,
            "prior_24h_score": prior_score,
            "prior_24h_entries": prior_n,
            "shift": shift,
            "significant_shift": flagged,
        }

    out = {
        "generated_at": now.isoformat(),
        "shift_threshold": SHIFT_THRESHOLD,
        "assets": results,
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    web_path = os.path.join("web", os.path.basename(OUT_PATH))
    os.makedirs("web", exist_ok=True)
    with open(web_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    for asset, r in results.items():
        if r["shift"] is None:
            print(f"{asset}: insufficient data in one or both windows "
                  f"(recent n={r['recent_24h_entries']}, prior n={r['prior_24h_entries']})")
        else:
            flag = " *** SIGNIFICANT SHIFT ***" if r["significant_shift"] else ""
            print(f"{asset}: prior={r['prior_24h_score']} -> recent={r['recent_24h_score']} "
                  f"(shift={r['shift']:+d}){flag}")
    print(f"\nWritten to {OUT_PATH}")


if __name__ == "__main__":
    main()
