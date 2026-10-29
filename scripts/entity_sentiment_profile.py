#!/usr/bin/env python3
"""Global descriptive entity sentiment plus target-asset relevance-weighted profiles."""
import json
import os
from collections import defaultdict

KB_DIR = "ping-pongings/knowledge-base"
XRP_LOG = os.path.join(KB_DIR, "log.jsonl")
BTC_LOG = os.path.join(KB_DIR, "log_btc.jsonl")
OUT_PATH = os.path.join(KB_DIR, "entity_sentiment_profile.json")
SENTIMENT_WEIGHT = {"bullish": 1.0, "neutral": 0.0, "bearish": -1.0}
ASSET_RELEVANCE_FIELD = {"XRP": "xrp_relevance", "BTC": "btc_relevance"}


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
                out.append(json.loads(line))
            except (json.JSONDecodeError, TypeError):
                continue
    return out


def relevance_weight(distill, field):
    try:
        return max(0.0, float(distill.get(field, 0) or 0))
    except (TypeError, ValueError):
        return 0.0


def build_entity_sentiment_profile(xrp_entries, btc_entries):
    all_entries = [(entry, "XRP") for entry in xrp_entries] + [(entry, "BTC") for entry in btc_entries]
    profiles = defaultdict(lambda: {"bullish": 0, "neutral": 0, "bearish": 0, "assets_seen_in": set(), "example_headlines": []})
    scoped = {asset: defaultdict(lambda: {"bullish": 0, "neutral": 0, "bearish": 0, "relevance_weight_sum": 0.0, "weighted_sentiment_sum": 0.0, "example_headlines": []}) for asset in ASSET_RELEVANCE_FIELD}

    for entry, asset in all_entries:
        distill = entry.get("distill", {})
        sentiment = distill.get("sentiment")
        if sentiment not in SENTIMENT_WEIGHT:
            continue
        weight = relevance_weight(distill, ASSET_RELEVANCE_FIELD[asset])
        for entity in distill.get("entities", []):
            normalized = entity.strip() if isinstance(entity, str) else ""
            if not normalized:
                continue
            global_profile = profiles[normalized]
            global_profile[sentiment] += 1
            global_profile["assets_seen_in"].add(asset)
            if len(global_profile["example_headlines"]) < 3:
                global_profile["example_headlines"].append(entry.get("title", "")[:100])
            if weight <= 0:
                continue
            profile = scoped[asset][normalized]
            profile[sentiment] += 1
            profile["relevance_weight_sum"] += weight
            profile["weighted_sentiment_sum"] += SENTIMENT_WEIGHT[sentiment] * weight
            if len(profile["example_headlines"]) < 3:
                profile["example_headlines"].append(entry.get("title", "")[:100])

    global_results = []
    for entity, profile in profiles.items():
        total = profile["bullish"] + profile["neutral"] + profile["bearish"]
        global_results.append({
            "entity": entity, "total_mentions": total,
            "bullish": profile["bullish"], "neutral": profile["neutral"], "bearish": profile["bearish"],
            "net_sentiment_score": round((profile["bullish"] - profile["bearish"]) / total, 3) if total else 0.0,
            "assets_seen_in": sorted(profile["assets_seen_in"]),
            "example_headlines": profile["example_headlines"],
        })
    global_results.sort(key=lambda result: result["total_mentions"], reverse=True)

    asset_results = {}
    for asset, entities in scoped.items():
        rows = []
        for entity, profile in entities.items():
            mentions = profile["bullish"] + profile["neutral"] + profile["bearish"]
            total_weight = profile["relevance_weight_sum"]
            weighted_score = ((profile["weighted_sentiment_sum"] / total_weight) + 1) * 50 if total_weight > 0 else None
            rows.append({
                "entity": entity,
                "eligible_mentions": mentions,
                "bullish_mentions": profile["bullish"],
                "neutral_mentions": profile["neutral"],
                "bearish_mentions": profile["bearish"],
                "relevance_weight_sum": round(total_weight, 6),
                "relevance_weighted_score_0_100": round(weighted_score, 3) if weighted_score is not None else None,
                "example_headlines": profile["example_headlines"],
            })
        rows.sort(key=lambda row: (-row["relevance_weight_sum"], row["entity"]))
        asset_results[asset] = rows

    return {
        "generated_from": {"xrp_entries": len(xrp_entries), "btc_entries": len(btc_entries)},
        "unique_entities_profiled": len(global_results),
        "entities": global_results,
        "asset_specific_profiles": asset_results,
    }


def main():
    out = build_entity_sentiment_profile(load_jsonl(XRP_LOG), load_jsonl(BTC_LOG))
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    web_path = os.path.join("web", os.path.basename(OUT_PATH))
    os.makedirs("web", exist_ok=True)
    with open(web_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"Unique entities profiled: {out['unique_entities_profiled']}")


if __name__ == "__main__":
    main()
