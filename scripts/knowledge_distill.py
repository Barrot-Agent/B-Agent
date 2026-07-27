#!/usr/bin/env python3
"""
BARROT-Ω KNOWLEDGE DISTILL — turns raw ingested headlines into signal-relevant
insight. Reads log.jsonl entries not yet distilled, sends each through Groq to
extract sentiment/catalyst/relevance/entities, writes the distilled fields back.
Also runs a free VADER lexicon cross-check (crypto-augmented) against the
same text and flags agreement/disagreement with the Groq read - a secondary
signal, never a replacement; if VADER fails for any reason, distillation
proceeds using Groq alone.
Honest: if the brain fails on an entry, that entry is left undistilled, not faked.
"""

import json, os, sys, urllib.request

try:
    from vader_check import vader_check, agrees_with
    _VADER_OK = True
except Exception:
    _VADER_OK = False

KB_DIR = "ping-pongings/knowledge-base"
LOG_PATH = os.path.join(KB_DIR, "log.jsonl")
KEY = os.environ.get("GROQ_API_KEY", "")
MODEL = os.environ.get("BRAIN_MODEL", "").strip() or "llama-3.3-70b-versatile"


def ask(prompt):
    body = json.dumps(
        {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 300,
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
        f"Headline: {e['title']}\nSummary: {e.get('summary','')}\n\n"
        'Reply with JSON ONLY, no prose: {"sentiment": one of '
        '[bullish,bearish,neutral], "catalyst": short phrase or null, '
        '"xrp_relevance": number 0.0-1.0, "entities": array of up to 5 '
        "key named entities mentioned (people, organizations, tickers, "
        'protocols - not generic words), "one_line": one sentence on why '
        "it matters for an XRP trading signal}"
    )


def parse(raw):
    a, b = raw.find("{"), raw.rfind("}")
    if a == -1 or b == -1:
        raise ValueError("no json")
    d = json.loads(raw[a : b + 1])
    if d.get("sentiment") not in ("bullish", "bearish", "neutral"):
        raise ValueError("bad sentiment")
    d["xrp_relevance"] = max(0.0, min(float(d.get("xrp_relevance", 0)), 1.0))
    entities = d.get("entities", [])
    if not isinstance(entities, list):
        entities = []
    d["entities"] = [str(x).strip() for x in entities if str(x).strip()][:5]
    return d


def add_vader_check(d, text):
    if not _VADER_OK:
        return d
    try:
        v = vader_check(text)
        d["vader_sentiment"] = v["vader_sentiment"]
        d["vader_compound"] = v["vader_compound"]
        d["vader_agrees"] = agrees_with(d["sentiment"], v)
    except Exception:
        pass
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
            text = f"{e['title']} {e.get('summary','')}"
            d = add_vader_check(d, text)
            e["distill"] = d
            e["distilled"] = True
            done += 1
            ents = ", ".join(d["entities"]) or "none"
            vtag = ""
            if "vader_sentiment" in d:
                mark = "agree" if d["vader_agrees"] else "DISAGREE"
                vtag = f" | vader: {d['vader_sentiment']} ({mark})"
            print(f"  [{d['sentiment']}] {e['title'][:60]} | entities: {ents}{vtag}")
        except Exception as ex:
            print(f"  skip (brain/parse fail): {e['title'][:50]} — {ex}")

    with open(LOG_PATH, "w") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")
    print(f"Distilled {done}/{len(todo)} pending entries.")


if __name__ == "__main__":
    main()
