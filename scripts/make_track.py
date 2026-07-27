#!/usr/bin/env python3
"""
BARROT-Ω TRACK GENERATOR — real, minimal, honest.

Two real API calls, no invented capability:
1. Groq (Barrot's existing brain, free) turns a rough theme/mood into a
   proper music-style prompt for MusicGPT.
2. MusicGPT (paid, requires MUSICGPT_API_KEY) generates an instrumental
   track from that prompt, polled until complete, then downloaded -
   MusicGPT's audio_url is a signed URL valid only 1 day, so this script
   downloads the real file rather than just logging a URL that expires.

Usage: TRACK_THEME env var sets the theme (e.g. "late night highway drive,
melancholy but hopeful"). Falls back to a generic theme if unset.
"""

import json
import os
import sys
import time
import urllib.request

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
MUSICGPT_KEY = os.environ.get("MUSICGPT_API_KEY", "")
MODEL = os.environ.get("BRAIN_MODEL", "").strip() or "llama-3.3-70b-versatile"
THEME = os.environ.get("TRACK_THEME", "").strip() or "reflective, driving forward, cautious optimism"

MUSIC_DIR = "music"
LOG_PATH = os.path.join(MUSIC_DIR, "tracks_log.jsonl")

MUSICGPT_BASE = "https://api.musicgpt.com/api/public/v1"
POLL_INTERVAL = 10
POLL_TIMEOUT = 300


def groq_ask(prompt):
    body = json.dumps(
        {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 150,
            "temperature": 0.7,
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


def build_style_brief(theme):
    prompt = (
        f"Write a music style description (genre, tempo, instrumentation, mood) "
        f"for an INSTRUMENTAL track (no vocals) matching this theme: {theme}\n\n"
        "One or two sentences, concrete and specific - name a genre, a tempo "
        "range in BPM, and 2-3 instruments. No preamble, just the description."
    )
    return groq_ask(prompt)


def musicgpt_post(path, payload):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{MUSICGPT_BASE}{path}",
        data=body,
        headers={
            "Authorization": MUSICGPT_KEY,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def musicgpt_get_status(task_id):
    url = f"{MUSICGPT_BASE}/byId?conversionType=MUSIC_AI&task_id={task_id}"
    req = urllib.request.Request(url, headers={"Authorization": MUSICGPT_KEY})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def download(url, dest_path):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=60) as r:
        with open(dest_path, "wb") as f:
            f.write(r.read())


def main():
    if not GROQ_KEY:
        sys.exit("GROQ_API_KEY not set")
    if not MUSICGPT_KEY:
        sys.exit("MUSICGPT_API_KEY not set - add it as a GitHub secret first")

    os.makedirs(MUSIC_DIR, exist_ok=True)

    print(f"Theme: {THEME}")
    style_brief = build_style_brief(THEME)
    print(f"Barrot's style brief: {style_brief}")

    print("Submitting to MusicGPT...")
    submit = musicgpt_post(
        "/MusicAI",
        {
            "music_style": style_brief,
            "make_instrumental": True,
        },
    )
    if not submit.get("success"):
        sys.exit(f"MusicGPT submission failed: {submit}")
    task_id = submit["task_id"]
    eta = submit.get("eta", 60)
    print(f"Task {task_id} queued, ETA ~{eta}s")

    waited = 0
    result = None
    while waited < POLL_TIMEOUT:
        time.sleep(POLL_INTERVAL)
        waited += POLL_INTERVAL
        status = musicgpt_get_status(task_id)
        conv = status.get("conversion", {})
        state = conv.get("status", "UNKNOWN")
        print(f"  [{waited}s] status: {state}")
        if state == "COMPLETED":
            result = conv
            break
        if state in ("FAILED", "ERROR"):
            sys.exit(f"MusicGPT generation failed: {conv.get('status_msg')}")

    if not result:
        sys.exit(f"Timed out after {POLL_TIMEOUT}s waiting for completion")

    audio_url = result.get("audio_url")
    if not audio_url:
        sys.exit(f"No audio_url in completed result: {result}")

    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    filename = f"track_{ts}.mp3"
    dest = os.path.join(MUSIC_DIR, filename)
    print(f"Downloading {audio_url} -> {dest}")
    download(audio_url, dest)

    record = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "theme": THEME,
        "style_brief": style_brief,
        "task_id": task_id,
        "filename": filename,
        "title": result.get("title", ""),
        "conversion_cost": result.get("conversion_cost"),
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")

    print(f"\nDone. Saved to {dest}")
    print(f"Logged to {LOG_PATH}")


if __name__ == "__main__":
    main()
