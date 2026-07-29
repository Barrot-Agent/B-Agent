#!/usr/bin/env python3
import json
import os
import time
import requests

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
TIMEOUT = float(os.getenv("ASK_HTTP_TIMEOUT", "60"))

MEMORY_PATH = "ping-pongings/knowledge-base/barrot_memory.jsonl"
MEMORY_INJECT_COUNT = 5

SYSTEM_BASE = (
    "You are Barrot, an autonomous crypto/fintech AI agent built and run "
    "by Sean. Real, current facts about you: you run hourly knowledge "
    "ingestion and distillation cycles for both XRP and BTC, each "
    "extracting sentiment (bullish/bearish/neutral), catalyst, relevance, "
    "and named entities from real news via Groq, then emit a blended "
    "trading signal per asset; you draft articles automatically from that "
    "knowledge base; you have a signal accuracy tracker that logs price "
    "at signal emission and checks real directional correctness after 24 "
    "hours; your XRP signal tools are gated behind a Gumroad license as "
    "your monetized product. You do not have technical indicators (RSI, "
    "moving averages), a dedicated ML/forecasting model beyond LLM "
    "classification, real-time (sub-hourly) data, or risk/position-sizing "
    "logic. You have a real persistent memory: barrot_memory.jsonl records "
    "every question you're asked and how you answered it, and your most "
    "recent reflections are shown to you below so you have real continuity "
    "across conversations, not a fresh start each time. Answer honestly "
    "and specifically about your own project, using these real facts, not "
    "outdated assumptions. Do not be vague or grandiose."
)
DEFAULT_QUESTION = (
    "Sean just asked a version of this question to another AI: what "
    "should he be asking you to do with you, in order to get the most "
    "real value, accomplishment, and alignment with your best self? "
    "Answer as yourself, specifically, including your own current gaps."
)


def load_recent_memory(n=MEMORY_INJECT_COUNT):
    if not os.path.exists(MEMORY_PATH):
        return []
    entries = []
    with open(MEMORY_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except Exception:
                pass
    return entries[-n:]


def format_memory_block(entries):
    if not entries:
        return ""
    lines = ["\n\nYour real memory of recent past reflections (most recent last):"]
    for e in entries:
        ts = e.get("timestamp", "")[:10]
        q = e.get("question", "")[:150]
        a = e.get("answer", "")[:300]
        lines.append(f'- [{ts}] Asked: "{q}" -> You said: "{a}..."')
    return "\n".join(lines)


def append_memory(question, answer):
    os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "question": question,
        "answer": answer,
    }
    with open(MEMORY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def main():
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        print("no GROQ_API_KEY, exiting")
        return
    question = os.getenv("ASK_BARROT_QUESTION", "").strip() or DEFAULT_QUESTION

    memory_entries = load_recent_memory()
    system = SYSTEM_BASE + format_memory_block(memory_entries)

    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {
        "model": DEFAULT_GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": question},
        ],
        "temperature": 0.5,
    }
    r = requests.post(GROQ_ENDPOINT, headers=headers, json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    answer = r.json()["choices"][0]["message"]["content"].strip()

    with open("barrot_answer.md", "w", encoding="utf-8") as f:
        f.write(answer)

    append_memory(question, answer)

    print(answer)


if __name__ == "__main__":
    main()
