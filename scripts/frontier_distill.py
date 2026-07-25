#!/usr/bin/env python3
"""
BARROT-Omega FRONTIER DIGEST DISTILL - turns raw ingested paper/article
entries into grounded, honest capability notes.

Instructs the model to report only what the source actually claims (a
benchmark number, a proposed method, a measured result) and to say so
plainly when something is opinion/hype rather than a result. This is the
honest version of "predict what's next": synthesis of real published
material, never invented future capability.

If the brain fails on an entry, that entry is left undistilled, not faked.
"""

import json, os, sys, urllib.request

KB_DIR = "ping-pongings/knowledge-base"
LOG_PATH = os.path.join(KB_DIR, "frontier_log.jsonl")
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
        "This is a research paper or news item about AI coding agents/models. "
        "Reply with JSON ONLY, no prose: "
        '{"claim_type": one of [benchmark_result, proposed_method, survey, '
        'opinion_or_hype, product_announcement], '
        '"concrete_claim": one sentence stating exactly what is claimed or '
        'measured - a real number, a named technique, or a named product, '
        'never a vague generality, '
        '"barrot_relevance": either a short phrase naming a specific concrete '
        "capability Barrot's apex_lattice could adopt, or null if there isn't one}. "
        "If the source is speculation, marketing copy, or an opinion piece with "
        "no measured result, set claim_type to opinion_or_hype and say so in "
        "concrete_claim - do not dress it up as a finding."
    )


def parse(raw):
    a, b = raw.find("{"), raw.rfind("}")
    if a == -1 or b == -1:
        raise ValueError("no json")
    d = json.loads(raw[a : b + 1])
    valid_types = {"benchmark_result", "proposed_method", "survey", "opinion_or_hype", "product_announcement"}
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
