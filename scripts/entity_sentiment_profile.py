#!/usr/bin/env python3
"""
BARROT-Ω ENTITY SENTIMENT PROFILER — aggregates sentiment for each named
entity across all distilled XRP and BTC entries: how often it appears
alongside bullish/bearish/neutral coverage, and a net sentiment score.
Pure aggregation over existing distilled entries. No new infrastructure.
"""

import json
import os
from collections import defaultdict

KB_DIR = "ping-pongings/knowledge-base"
XRP_LOG = os.path.join(KB_DIR, "log.jsonl")
BTC_LOG = os.path.join(KB_DIR, "log_btc.jsonl")
OUT_PATH = os.path.join(KB_DIR, "entity_sentiment_profile.json")

SENTIMENT_WEIGHT = {"bullish": 1.0, "neutral": 0.0, "bearish": -1.0}


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


def main():
    xrp_entries = load_jsonl(XRP_LOG)
    btc_entries = load_jsonl(BTC_LOG)
    all_entries = [(e, "XRP") for e in xrp_entries] + [(e, "BTC") for e in btc_entries]

    profiles = defaultdict(lambda: {
        "bullish": 0, "neutral": 0, "bearish": 0,
        "assets_seen_in": set(), "example_headlines": [],
    })

    for e, asset in all_entries:
        d = e.get("distill", {})
        sentiment = d.get("sentiment")
        if sentiment not in SENTIMENT_WEIGHT:
            continue
        for ent in d.get("entities", []):
            ent_norm = ent.strip()
            if not ent_norm:
                continue
            p = profiles[ent_norm]
            p[sentiment] += 1
            p["assets_seen_in"].add(asset)
            if len(p["example_headlines"]) < 3:
                p["example_headlines"].append(e.get("title", "")[:100])

    results = []
    for entity, p in profiles.items():
        total = p["bullish"] + p["neutral"] + p["bearish"]
        net_score = (p["bullish"] - p["bearish"]) / total if total else 0.0
        results.append(
            {
                "entity": entity,
                "total_mentions": total,
                "bullish": p["bullish"],
                "neutral": p["neutral"],
                "bearish": p["bearish"],
                "net_sentiment_score": round(net_score, 3),
                "assets_seen_in": sorted(p["assets_seen_in"]),
                "example_headlines": p["example_headlines"],
            }
        )

    results.sort(key=lambda r: r["total_mentions"], reverse=True)

    out = {
        "generated_from": {"xrp_entries": len(xrp_entries), "btc_entries": len(btc_entries)},
        "unique_entities_profiled": len(results),
        "entities": results,
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    web_path = os.path.join("web", os.path.basename(OUT_PATH))
    os.makedirs("web", exist_ok=True)
    with open(web_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"Unique entities profiled: {len(results)}")
    print("\nTop 10 by mention volume:")
    for r in results[:10]:
        print(f"  {r['total_mentions']:3d}x  {r['entity']:25s} net_sentiment={r['net_sentiment_score']:+.2f} "
              f"(B:{r['bullish']} N:{r['neutral']} Be:{r['bearish']})")
    print(f"\nWritten to {OUT_PATH}")


if __name__ == "__main__":
    main()
