#!/usr/bin/env python3
"""
BARROT-Ω WEBMCP TREND DISTILL — turns raw ingested discourse entries into
grounded notes about what real people are actually asking for, complaining
about, or building around agent-website interaction.

Instructs the model to report only what the source actually says, and to
label opinion/marketing content honestly instead of dressing it up as a
finding. This is the honest version of "anticipate future WebMCP tools":
synthesis of real public discourse, never invented demand.

If the brain fails on an entry, that entry is left undistilled, not faked.
"""

import json, os, sys, urllib.request

KB_DIR = "ping-pongings/knowledge-base"
LOG_PATH = os.path.join(KB_DIR, "webmcp_trend_log.jsonl")
KEY = os.environ.get("GROQ_API_KEY", "")
MODEL = os.environ.get("BRAIN_MODEL", "").strip() or "llama-3.3-70b-versatile"


def ask(prompt):
    body = json.dumps(
        {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 350,
            "temperature": 0.1,
        }
    ).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["choices"][0]["message"]["content"]


def build_prompt(e):
    return (
        f"Title: {e['title']}\nSummary: {e.get('summary','')}\n\n"
        "This is a news item or article about WebMCP, agentic browsing, or "
        "AI agents interacting with websites. Reply with JSON ONLY, no prose: "
        '{"claim_type": one of [feature_request, pain_point, '
        'proposed_spec_change, product_announcement, opinion_or_hype], '
        '"concrete_claim": one sentence stating exactly what is said - a '
        "specific request, complaint, spec change, or product, never a vague "
        'generality, "candidate_tool_idea": a short phrase naming a specific '
        "concrete WebMCP tool category this suggests, or null if there isn't "
        "one}. If the source is speculation, marketing copy, or opinion with "
        "no concrete request/change/product, set claim_type to "
        "opinion_or_hype and say so plainly in concrete_claim."
    )


def parse(raw):
    a, b = raw.find("{"), raw.rfind("}")
    if a == -1 or b == -1:
        raise ValueError("no json")
    d = json.loads(raw[a : b + 1])
    valid_types = {
        "feature_request",
        "pain_point",
        "proposed_spec_change",
        "product_announcement",
        "opinion_or_hype",
    }
    if d.get("claim_type") not in valid_types:
        raise ValueError("bad claim_type")
    return d


def main():
    if not KEY:
        sys.exit("GROQ_API_KEY not set")
    if not os.path.exists(LOG_PATH):
        sys.exit("no log to distill")
    with open(LOG_PATH) as f:
        entries = [json.loads(l) for l in f if l.strip()]

    todo = [e for e in entries if not e.get("distilled")]
    if not todo:
        print("All entries already distilled.")
        return

    done = 0
    for e in todo:
        try:
            d = parse(ask(build_prompt(e)))
            e["distill"] = d
            e["distilled"] = True
            done += 1
            print(f"  [{d['claim_type']}] {e['title'][:60]}")
        except Exception as ex:
            print(f"  skip (brain/parse fail): {e['title'][:50]} - {ex}")

    with open(LOG_PATH, "w") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")
    print(f"Distilled {done}/{len(todo)} pending entries.")


if __name__ == "__main__":
    main()
