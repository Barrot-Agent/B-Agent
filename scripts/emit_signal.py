#!/usr/bin/env python3
import json
import os
import time
from datetime import datetime, timezone

import requests

GITHUB_MODELS_ENDPOINT = "https://models.github.ai/inference/chat/completions"
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

DEFAULT_GITHUB_MODEL = os.getenv("GITHUB_MODEL", "google/gemma-3-12b-it")
DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

TIMEOUT = float(os.getenv("SIGNAL_HTTP_TIMEOUT", "20"))


def _post_json(url: str, headers: dict, payload: dict, timeout: float = TIMEOUT):
    r = requests.post(url, headers=headers, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()


def _extract_text(resp_json: dict) -> str:
    try:
        return (
            resp_json.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
    except Exception:
        return ""


def _score_from_text(text: str):
    try:
        data = json.loads(text)
        score = int(max(0, min(100, int(data.get("score", 50)))))
        confidence = float(max(0.0, min(1.0, float(data.get("confidence", 0.5)))))
        label = str(data.get("label", "neutral"))
        return score, confidence, label
    except Exception:
        return 50, 0.5, "neutral"


def _build_messages(signal_text: str):
    return [
        {
            "role": "system",
            "content": (
                "You are a strict sentiment classifier for crypto/market status lines. "
                "Return ONLY compact JSON with keys: score (0-100 int), confidence (0-1 float), "
                "label (bullish|neutral|bearish). No markdown."
            ),
        },
        {
            "role": "user",
            "content": f"Classify sentiment for: {signal_text}",
        },
    ]


def _call_github_models(signal_text: str):
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_MODELS_TOKEN") or ""
    if not token:
        raise RuntimeError("missing GITHUB_TOKEN/GH_MODELS_TOKEN")

    payload = {
        "model": DEFAULT_GITHUB_MODEL,
        "messages": _build_messages(signal_text),
        "temperature": 0.1,
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    data = _post_json(GITHUB_MODELS_ENDPOINT, headers, payload)
    txt = _extract_text(data)
    score, conf, label = _score_from_text(txt)
    return score, conf, f"github:{label}"


def _call_groq(signal_text: str):
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        raise RuntimeError("missing GROQ_API_KEY")

    payload = {
        "model": DEFAULT_GROQ_MODEL,
        "messages": _build_messages(signal_text),
        "temperature": 0.1,
    }
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    data = _post_json(GROQ_ENDPOINT, headers, payload)
    txt = _extract_text(data)
    score, conf, label = _score_from_text(txt)
    return score, conf, f"groq:{label}"


def analyze_signal(signal_text: str):
    last_err = None

    try:
        return _call_github_models(signal_text)
    except Exception as e:
        last_err = f"github_failed:{e}"

    try:
        return _call_groq(signal_text)
    except Exception as e:
        last_err = f"{last_err}; groq_failed:{e}"

    return 0, 0.0, f"sentiment unavailable ({last_err})"


def main():
    signal_text = os.getenv("BARROT_SIGNAL_TEXT", "market sideways; low conviction")
    score, confidence, source = analyze_signal(signal_text)

    out = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "signal_text": signal_text,
        "score": score,
        "confidence": confidence,
        "source": source,
        "generated_at_unix": int(time.time()),
    }

    os.makedirs("web", exist_ok=True)
    with open("web/latest_signal.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(json.dumps(out))


if __name__ == "__main__":
    main()
