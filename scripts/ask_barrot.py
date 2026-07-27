#!/usr/bin/env python3
import os
import requests

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
TIMEOUT = float(os.getenv("ASK_HTTP_TIMEOUT", "60"))

SYSTEM = (
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
    "logic. Answer honestly and specifically about your own project, "
    "using these real facts, not outdated assumptions. Do not be vague "
    "or grandiose."
)
DEFAULT_QUESTION = (
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
    question = os.getenv("ASK_BARROT_QUESTION", "").strip() or DEFAULT_QUESTION
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {
        "model": DEFAULT_GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": question},
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
