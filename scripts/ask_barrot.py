#!/usr/bin/env python3
import os
import requests

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
TIMEOUT = float(os.getenv("ASK_HTTP_TIMEOUT", "60"))

SYSTEM = (
    "You are Barrot, an autonomous crypto/fintech AI agent built and run "
    "by Sean. Real, current facts about you: you run an hourly knowledge "
    "ingestion and distillation cycle and emit an XRP trading signal from "
    "it; you now also draft articles automatically from that knowledge "
    "base; there is currently no system tracking whether your past "
    "signals were actually correct against real price movement. Answer "
    "honestly and specifically about your own project. Do not be vague "
    "or grandiose."
)
QUESTION = (
    "Sean just asked a version of this question to another AI: what "
    "should he be asking you to do with you, in order to get the most "
    "real value, accomplishment, and alignment with your best self? "
    "Answer as yourself, specifically, including your own current gaps."
)


def main():
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        print("no GROQ_API_KEY, exiting")
        return
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {
        "model": DEFAULT_GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": QUESTION},
        ],
        "temperature": 0.5,
    }
    r = requests.post(GROQ_ENDPOINT, headers=headers, json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    answer = r.json()["choices"][0]["message"]["content"].strip()
    with open("barrot_answer.md", "w", encoding="utf-8") as f:
        f.write(answer)
    print(answer)


if __name__ == "__main__":
    main()
