#!/usr/bin/env python3
"""
BARROT-Ω ENTITY SENTIMENT PROFILER.

This is an all-available-log aggregation of article-level sentiment for items
that mention an entity. It is NOT sentiment toward the entity and is NOT a
current or predictive feature. Inputs are not time-filtered, deduplicated or
source-independence weighted; the output declares those limitations.
"""

import json
import os
from collections import defaultdict
from datetime import datetime, timezone

KB_DIR = "ping-pongings/knowledge-base"
XRP_LOG = os.path.join(KB_DIR, "log.jsonl")
BTC_LOG = os.path.join(KB_DIR, "log_btc.jsonl")
OUT_PATH = os.path.join(KB_DIR, "entity_sentiment_profile.json")

SENTIMENT_WEIGHT = {"bullish": 1.0, "neutral": 0.0, "bearish": -1.0}
SCORE_SEMANTICS = (
    "Article-level sentiment of records containing this entity; it does not "
    "measure the article's sentiment toward the entity."
)
PIPELINE_SEMANTICS = (
    "XRP/BTC identify the input log file, not verified exclusive asset exposure."
)


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
            except Exception:
                pass
    return out


def _score(counts):
    total = sum(counts.values())
    if not total:
        return 0.0
    weighted = sum(SENTIMENT_WEIGHT[key] * counts.get(key, 0) for key in SENTIMENT_WEIGHT)
    return round(weighted / total, 3)


def build_profile(xrp_entries, btc_entries, generated_at=None):
    """Build a descriptive all-log profile; never imply current or entity-specific sentiment."""
    now = generated_at or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("generated_at must be timezone-aware")
    generated_at_utc = now.astimezone(timezone.utc).isoformat()

    profiles = defaultdict(lambda: {
        "bullish": 0,
        "neutral": 0,
        "bearish": 0,
        "pipelines_seen_in": set(),
        "pipeline_counts": defaultdict(lambda: {"bullish": 0, "neutral": 0, "bearish": 0}),
        "example_headlines": [],
    })

    for entry, pipeline in (
        [(e, "XRP") for e in xrp_entries] + [(e, "BTC") for e in btc_entries]
    ):
        distill = entry.get("distill") or {}
        sentiment = distill.get("sentiment")
        if sentiment not in SENTIMENT_WEIGHT:
            continue
        for entity in distill.get("entities", []):
            entity_name = str(entity).strip()
            if not entity_name:
                continue
            item = profiles[entity_name]
            item[sentiment] += 1
            item["pipelines_seen_in"].add(pipeline)
            item["pipeline_counts"][pipeline][sentiment] += 1
            if len(item["example_headlines"]) < 3:
                item["example_headlines"].append(str(entry.get("title", ""))[:100])

    results = []
    for entity, item in profiles.items():
        counts = {key: item[key] for key in SENTIMENT_WEIGHT}
        total = sum(counts.values())
        pipeline_breakdown = {}
        for pipeline, pipeline_counts in sorted(item["pipeline_counts"].items()):
            pipeline_total = sum(pipeline_counts.values())
            pipeline_breakdown[pipeline] = {
                **pipeline_counts,
                "total_mentions": pipeline_total,
                "net_article_sentiment_score": _score(pipeline_counts),
            }
        pipelines = sorted(item["pipelines_seen_in"])
        results.append({
            "entity": entity,
            "total_mentions": total,
            **counts,
            "net_sentiment_score": _score(counts),
            "score_semantics": SCORE_SEMANTICS,
            "pipelines_seen_in": pipelines,
            # Compatibility alias; values are pipeline labels, not verified asset exposure.
            "assets_seen_in": pipelines,
            "pipeline_breakdown": pipeline_breakdown,
            "example_headlines": item["example_headlines"],
        })

    results.sort(key=lambda row: row["total_mentions"], reverse=True)
    return {
        "generated_at_utc": generated_at_utc,
        "time_scope": "ALL_AVAILABLE_LOG_ENTRIES",
        "input_timestamp_filter": "NONE",
        "deduplication": "NONE",
        "source_independence_adjusted": False,
        "feature_eligibility": "EXPLORATORY_ONLY_NOT_PREDICTIVE",
        "score_semantics": SCORE_SEMANTICS,
        "pipeline_label_semantics": PIPELINE_SEMANTICS,
        "generated_from": {"xrp_entries": len(xrp_entries), "btc_entries": len(btc_entries)},
        "unique_entities_profiled": len(results),
        "entities": results,
    }


def main():
    result = build_profile(load_jsonl(XRP_LOG), load_jsonl(BTC_LOG))
    os.makedirs(KB_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    web_path = os.path.join("web", os.path.basename(OUT_PATH))
    os.makedirs("web", exist_ok=True)
    with open(web_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Unique entities profiled: {result['unique_entities_profiled']}")
    print("Top 10 by article co-occurrence volume:")
    for row in result["entities"][:10]:
        print(
            f"  {row['total_mentions']:3d}x  {row['entity']:25s} "
            f"article_sentiment={row['net_sentiment_score']:+.2f} "
            f"(B:{row['bullish']} N:{row['neutral']} Be:{row['bearish']})"
        )
    print(f"\nWritten to {OUT_PATH}; exploratory-only, all available log entries.")


if __name__ == "__main__":
    main()
