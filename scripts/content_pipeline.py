#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
TIMEOUT = float(os.getenv("CONTENT_HTTP_TIMEOUT", "60"))
KB_PATH = Path("ping-pongings/knowledge-base/log.jsonl")
FRONTIER_RECS_PATH = Path("ping-pongings/knowledge-base/upgrade_recommendations.jsonl")
COOCCURRENCE_PATH = Path("ping-pongings/knowledge-base/entity_cooccurrence.json")
OUT_DIR = Path("content")


def _call_groq(messages):
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        return ""
    headers = {"Authorization": f"******", "Content-Type": "application/json"}
    payload = {"model": DEFAULT_GROQ_MODEL, "messages": messages, "temperature": 0.6}
    try:
        r = requests.post(GROQ_ENDPOINT, headers=headers, json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        print(f"[content_pipeline] groq call failed: {exc}")
        return ""


def _load_recent_entries(limit=200):
    if not KB_PATH.exists():
        return []
    lines = KB_PATH.read_text(encoding="utf-8").splitlines()
    entries = []
    for line in lines[-limit:]:
        try:
            entries.append(json.loads(line))
        except Exception:
            continue
    return entries


def _load_frontier_context(limit=3):
    """Load the most recent frontier upgrade recommendations."""
    if not FRONTIER_RECS_PATH.exists():
        return []
    lines = FRONTIER_RECS_PATH.read_text(encoding="utf-8").splitlines()
    recs = []
    for line in lines[-limit:]:
        try:
            recs.append(json.loads(line))
        except Exception:
            continue
    return recs


def _load_cooccurrence_context(top_n=5):
    """Load the top co-occurring entity pairs from cross-analysis."""
    if not COOCCURRENCE_PATH.exists():
        return []
    try:
        data = json.loads(COOCCURRENCE_PATH.read_text(encoding="utf-8"))
        pairs = data.get("top_pairs", []) or data.get("pairs", [])
        return pairs[:top_n]
    except Exception:
        return []


def _pick_topic(entries):
    return [e for e in entries if e.get("distilled")][-6:]


def _build_prompt(topic_entries, frontier_recs, cooccurrence_pairs):
    lines = []
    for e in topic_entries:
        d = e.get("distill", {}) or {}
        lines.append(f"- {e.get('title', '')}: {d.get('one_line', '')}")
    context = "\n".join(lines) if lines else "No recent high-signal entries found."

    frontier_block = ""
    if frontier_recs:
        rec_lines = []
        for rec in frontier_recs:
            summary = rec.get("recommendation") or rec.get("summary") or str(rec)[:120]
            rec_lines.append(f"- {summary}")
        frontier_block = "\n\nFrontier upgrade signals (from research pillar):\n" + "\n".join(rec_lines)

    cooccurrence_block = ""
    if cooccurrence_pairs:
        pair_lines = [
            f"- {p}" if isinstance(p, str)
            else f"- {p.get('pair', p)}: {p.get('count', '')}"
            for p in cooccurrence_pairs
        ]
        cooccurrence_block = "\n\nTrending entity co-occurrences (from cross-analysis pillar):\n" + "\n".join(pair_lines)

    system = (
        "You are Barrot, drafting a short original article (400-600 words) "
        "for a crypto/fintech audience. Write entirely in your own words, "
        "no quoted material, no invented statistics. Plain markdown, one "
        "H1 title, no throat-clearing intro."
    )
    user = (
        f"Recent high-signal source material:\n{context}"
        f"{frontier_block}"
        f"{cooccurrence_block}"
        f"\n\nDraft the article."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def main():
    entries = _load_recent_entries()
    topic_entries = _pick_topic(entries)
    frontier_recs = _load_frontier_context()
    cooccurrence_pairs = _load_cooccurrence_context()

    if frontier_recs:
        print(f"[content_pipeline] injecting {len(frontier_recs)} frontier recommendation(s)")
    if cooccurrence_pairs:
        print(f"[content_pipeline] injecting {len(cooccurrence_pairs)} co-occurrence pair(s)")

    draft = _call_groq(_build_prompt(topic_entries, frontier_recs, cooccurrence_pairs))
    if not draft:
        print("[content_pipeline] no draft produced, exiting")
        return
    OUT_DIR.mkdir(exist_ok=True)
    slug = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    out_path = OUT_DIR / f"{slug}.md"
    out_path.write_text(draft, encoding="utf-8")
    print(f"[content_pipeline] wrote {out_path}")


if __name__ == "__main__":
    main()
