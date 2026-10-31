#!/usr/bin/env python3
"""
BARROT-Ω ENTITY CO-OCCURRENCE.

Counts entity pairs across all available XRP and BTC pipeline log entries.
Pipeline labels describe the source log, not verified exclusive asset exposure.
No time filtering, deduplication or source-independence adjustment is applied.
"""

import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
from itertools import combinations

KB_DIR = "ping-pongings/knowledge-base"
XRP_LOG = os.path.join(KB_DIR, "log.jsonl")
BTC_LOG = os.path.join(KB_DIR, "log_btc.jsonl")
OUT_PATH = os.path.join(KB_DIR, "entity_cooccurrence.json")
PIPELINE_SEMANTICS = "XRP/BTC identify the input log file, not verified exclusive asset exposure."


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


def build_cooccurrence(xrp_entries, btc_entries, generated_at=None):
    now = generated_at or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("generated_at must be timezone-aware")
    generated_at_utc = now.astimezone(timezone.utc).isoformat()

    pair_counts = Counter()
    pair_pipeline_counts = defaultdict(lambda: Counter())
    pair_context = defaultdict(list)

    for entry, pipeline in (
        [(e, "XRP") for e in xrp_entries] + [(e, "BTC") for e in btc_entries]
    ):
        distill = entry.get("distill") or {}
        entities = sorted(set(str(value).strip() for value in distill.get("entities", []) if str(value).strip()))
        if len(entities) < 2:
            continue
        for left, right in combinations(entities, 2):
            pair = (left, right)
            pair_counts[pair] += 1
            pair_pipeline_counts[pair][pipeline] += 1
            if len(pair_context[pair]) < 2:
                pair_context[pair].append({
                    "title": str(entry.get("title", ""))[:100],
                    "pipeline_asset": pipeline,
                    # Compatibility alias; see pipeline_label_semantics.
                    "asset": pipeline,
                })

    pairs = []
    for (left, right), count in pair_counts.most_common():
        pairs.append({
            "entity_a": left,
            "entity_b": right,
            "cooccurrence_count": count,
            "pipeline_counts": dict(sorted(pair_pipeline_counts[(left, right)].items())),
            "example_headlines": pair_context[(left, right)],
        })

    return {
        "generated_at_utc": generated_at_utc,
        "time_scope": "ALL_AVAILABLE_LOG_ENTRIES",
        "input_timestamp_filter": "NONE",
        "deduplication": "NONE",
        "source_independence_adjusted": False,
        "feature_eligibility": "EXPLORATORY_ONLY_NOT_PREDICTIVE",
        "pipeline_label_semantics": PIPELINE_SEMANTICS,
        "generated_from": {"xrp_entries": len(xrp_entries), "btc_entries": len(btc_entries)},
        "unique_pairs_found": len(pairs),
        "pairs": pairs,
    }


def main():
    result = build_cooccurrence(load_jsonl(XRP_LOG), load_jsonl(BTC_LOG))
    os.makedirs(KB_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    web_path = os.path.join("web", os.path.basename(OUT_PATH))
    os.makedirs("web", exist_ok=True)
    with open(web_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Unique entity pairs found: {result['unique_pairs_found']}")
    print("Top 10 co-occurring entity pairs:")
    for row in result["pairs"][:10]:
        print(f"  {row['cooccurrence_count']:3d}x  {row['entity_a']} <-> {row['entity_b']}")
    print(f"\nWritten to {OUT_PATH}; exploratory-only, all available log entries.")


if __name__ == "__main__":
    main()
