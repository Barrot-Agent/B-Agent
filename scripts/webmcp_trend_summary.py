#!/usr/bin/env python3
"""
BARROT-Ω WEBMCP TREND SUMMARY — aggregates the raw webmcp_trend_log.jsonl
into a digest: candidate tool ideas ranked by how often real discourse
surfaced them, grouped by claim type, with example sources. This is what
the getWebMCPTrendDigest WebMCP tool actually serves - a summary, not a
raw dump of every ingested item.
Pure aggregation over existing distilled entries. No new infrastructure.
"""

import json
import os
from collections import Counter, defaultdict

KB_DIR = "ping-pongings/knowledge-base"
LOG_PATH = os.path.join(KB_DIR, "webmcp_trend_log.jsonl")
OUT_PATH = os.path.join(KB_DIR, "webmcp_trend_summary.json")


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
    entries = load_jsonl(LOG_PATH)
    distilled = [e for e in entries if e.get("distilled") and e.get("distill")]

    claim_type_counts = Counter()
    tool_idea_counts = Counter()
    tool_idea_examples = defaultdict(list)

    for e in distilled:
        d = e["distill"]
        claim_type_counts[d.get("claim_type", "unknown")] += 1
        idea = d.get("candidate_tool_idea")
        if idea:
            idea_norm = idea.strip()
            tool_idea_counts[idea_norm] += 1
            if len(tool_idea_examples[idea_norm]) < 2:
                tool_idea_examples[idea_norm].append(
                    {
                        "title": e.get("title", "")[:100],
                        "url": e.get("url", ""),
                        "claim_type": d.get("claim_type"),
                        "concrete_claim": d.get("concrete_claim", ""),
                    }
                )

    ranked_ideas = [
        {
            "candidate_tool_idea": idea,
            "times_surfaced": count,
            "examples": tool_idea_examples[idea],
        }
        for idea, count in tool_idea_counts.most_common()
    ]

    out = {
        "generated_from": {
            "total_entries": len(entries),
            "distilled_entries": len(distilled),
        },
        "claim_type_breakdown": dict(claim_type_counts),
        "ranked_candidate_tool_ideas": ranked_ideas,
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    web_path = os.path.join("web", os.path.basename(OUT_PATH))
    os.makedirs("web", exist_ok=True)
    with open(web_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"Distilled entries: {len(distilled)}/{len(entries)}")
    print(f"Claim type breakdown: {dict(claim_type_counts)}")
    print(f"\nRanked candidate tool ideas ({len(ranked_ideas)} unique):")
    for r in ranked_ideas[:10]:
        print(f"  {r['times_surfaced']}x  {r['candidate_tool_idea']}")
    print(f"\nWritten to {OUT_PATH}")


if __name__ == "__main__":
    main()
