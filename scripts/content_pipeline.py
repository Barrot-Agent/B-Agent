#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
TIMEOUT = float(os.getenv("CONTENT_HTTP_TIMEOUT", "60"))
KB_PATH = Path("ping-pongings/knowledge-base/log.jsonl")
OUT_DIR = Path("content")


def _call_groq(messages):
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        return ""
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
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


def _pick_topic(entries):
    return [e for e in entries if e.get("distilled")][-6:]


def _build_prompt(topic_entries):
    lines = []
    for e in topic_entries:
        d = e.get("distill", {}) or {}
        lines.append(f"- {e.get('title', '')}: {d.get('one_line', '')}")
    context = "\n".join(lines) if lines else "No recent high-signal entries found."
    system = (
        "You are Barrot, drafting a short original article (400-600 words) "
        "for a crypto/fintech audience. Write entirely in your own words, "
        "no quoted material, no invented statistics. Plain markdown, one "
        "H1 title, no throat-clearing intro."
    )
    user = f"Recent high-signal source material:\n{context}\n\nDraft the article."
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def main():
    entries = _load_recent_entries()
    topic_entries = _pick_topic(entries)
    draft = _call_groq(_build_prompt(topic_entries))
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
