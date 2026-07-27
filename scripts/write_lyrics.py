#!/usr/bin/env python3
"""
BARROT-Ω LYRICS WRITER — real, free, zero new dependencies. Uses the same
Groq brain as everything else. Writes lyrics to a theme, optionally
matching a given style brief (e.g. one already produced by make_track.py
for a generated instrumental, so the words actually fit the music).
"""

import json
import os
import sys
import time
import urllib.request

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
MODEL = os.environ.get("BRAIN_MODEL", "").strip() or "llama-3.3-70b-versatile"
THEME = os.environ.get("LYRICS_THEME", "").strip()
STYLE = os.environ.get("LYRICS_STYLE", "").strip()

MUSIC_DIR = "music"
LOG_PATH = os.path.join(MUSIC_DIR, "lyrics_log.jsonl")


def groq_ask(prompt):
    body = json.dumps(
        {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 700,
            "temperature": 0.85,
        }
    ).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {GROQ_KEY}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["choices"][0]["message"]["content"].strip()


def build_prompt(theme, style):
    parts = [
        f"Write original song lyrics on this theme: {theme}\n" if theme
        else "Write original song lyrics on a theme of your choosing.\n"
    ]
    if style:
        parts.append(f"They need to fit this instrumental style: {style}\n")
    parts.append(
        "Structure: verse, pre-chorus (optional), chorus, second verse, "
        "chorus, bridge, final chorus. Label each section clearly "
        "([Verse 1], [Chorus], etc). Real, specific imagery - no generic "
        "filler lines. Write only the lyrics, no commentary before or after."
    )
    return "\n".join(parts)


def main():
    if not GROQ_KEY:
        sys.exit("GROQ_API_KEY not set")
    os.makedirs(MUSIC_DIR, exist_ok=True)

    print(f"Theme: {THEME or '(unspecified - Barrot will choose)'}")
    if STYLE:
        print(f"Style to fit: {STYLE}")

    lyrics = groq_ask(build_prompt(THEME, STYLE))
    print("\n" + lyrics + "\n")

    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    filename = f"lyrics_{ts}.txt"
    dest = os.path.join(MUSIC_DIR, filename)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(lyrics)

    record = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "theme": THEME,
        "style": STYLE,
        "filename": filename,
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")

    print(f"Saved to {dest}")
    print(f"Logged to {LOG_PATH}")


if __name__ == "__main__":
    main()
