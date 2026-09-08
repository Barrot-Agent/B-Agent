#!/usr/bin/env python3
"""
BARROT-Ω TERMUX LEARNING LOOP -- reviews real execution history from
termux_runner.py and derives concrete lessons for future task generation.
SAFETY BOUNDARY: cannot modify Barrot's own code. Code changes still go
through git + barrot-gated-merge.yml -- only what future tasks should
avoid/check gets updated here, in plain text.
"""

import os, json, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
QUEUE_PATH = Path("ping-pongings/knowledge-base/termux_tasks.jsonl")
LESSONS_PATH = Path("ping-pongings/knowledge-base/termux_lessons.md")


def call_groq(prompt, max_tokens=1200):
    body = json.dumps({
        "model": "openai/gpt-oss-120b",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json",
                 "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.load(r)["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        print(f"Groq HTTP {e.code}: {e.read().decode()[:300]}")
        return None


def load_recent_tasks(limit=20):
    if not QUEUE_PATH.exists():
        return []
    entries = []
    with open(QUEUE_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    finished = [e for e in entries if e.get("status") in ("done", "failed")]
    return finished[-limit:]


def summarize_for_prompt(tasks):
    lines = []
    for t in tasks:
        outcome = t["status"]
        note = t.get("note", "")
        last_result = t.get("results", [])[-1] if t.get("results") else {}
        err = last_result.get("stderr", "")[:300]
        lines.append(f"- [{outcome}] {note}: {err if err else 'no error'}")
    return "\n".join(lines)


def derive_lessons(tasks):
    if not tasks:
        return None
    prompt = f"""Real execution history from termux_runner.py (Barrot's local
command-execution log on the actual device):

{summarize_for_prompt(tasks)}

Identify concrete, checkable patterns: repeated failure causes, commands
that are risky or redundant, real gaps in what gets checked before a
command runs. Do NOT propose code changes -- only propose changes to HOW
future tasks should be written (e.g. "always check X exists before Y",
"avoid pattern Z, it fails when...").

Output ONLY JSON: {{"lessons": ["concrete lesson 1", "concrete lesson 2", ...]}}"""
    response = call_groq(prompt)
    if not response:
        return None
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        return json.loads(response[start:end]).get("lessons", [])
    except Exception:
        print(f"Failed to parse lessons. Raw: {response[:300]}")
        return None


def append_lessons(lessons):
    LESSONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    existing = LESSONS_PATH.read_text() if LESSONS_PATH.exists() else "# Termux Execution Lessons\n\n"
    new_section = f"\n## {stamp}\n" + "\n".join(f"- {l}" for l in lessons) + "\n"
    LESSONS_PATH.write_text(existing + new_section)
    print(f"Appended {len(lessons)} lesson(s) to {LESSONS_PATH}")


if __name__ == "__main__":
    if not GROQ_KEY:
        print("GROQ_API_KEY not set")
        raise SystemExit(1)
    tasks = load_recent_tasks()
    if not tasks:
        print("No finished tasks to learn from yet.")
        raise SystemExit(0)
    lessons = derive_lessons(tasks)
    if lessons:
        append_lessons(lessons)
    else:
        print("No lessons derived this cycle.")
