#!/usr/bin/env python3
import json
import os
import time
from datetime import datetime, timezone

import requests

GITHUB_MODELS_ENDPOINT = "https://models.github.ai/inference/chat/completions"
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

DEFAULT_GITHUB_MODEL = os.getenv("GITHUB_MODEL", "openai/gpt-4.1-mini")
DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

TIMEOUT = float(os.getenv("SIGNAL_HTTP_TIMEOUT", "20"))


def _post_json(url: str, headers: dict, payload: dict, timeout: float = TIMEOUT):
    r = requests.post(url, headers=headers, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()


def _extract_text(resp_json: dict) -> str:
    try:
        return resp_json.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
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


def _news_score(hours=72, path="ping-pongings/knowledge-base/log.jsonl"):
    """Relevance-weighted sentiment from distilled news. Returns (score_0_100, n, headlines) or (None,0,[])."""
    from datetime import timedelta

    if not os.path.exists(path):
        return None, 0, []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    num = den = 0.0
    used = 0
    heads = []
    with open(path) as f:
        for line in f:
            try:
                e = json.loads(line)
            except Exception:
                continue
            if not e.get("distilled"):
                continue
            d = e.get("distill", {})
            w = float(d.get("xrp_relevance", 0) or 0)
            if w <= 0:
                continue
            try:
                ts = datetime.fromisoformat(e.get("ingested_at", "").replace("Z", "+00:00"))
                if ts < cutoff:
                    continue
            except Exception:
                pass
            s = {"bullish": 1.0, "neutral": 0.0, "bearish": -1.0}.get(d.get("sentiment"), 0.0)
            num += s * w
            den += w
            used += 1
            if w >= 0.5 and len(heads) < 6:
                heads.append(f"[{d.get('sentiment')}] {e.get('title','')[:80]}")
    if den == 0:
        return None, 0, []
    return int(round((num / den + 1) * 50)), used, heads


def main():
    news_score, n_news, headlines = _news_score()
    if headlines:
        signal_text = "Recent XRP-relevant headlines: " + " | ".join(headlines)
    else:
        signal_text = os.getenv("BARROT_SIGNAL_TEXT", "market sideways; low conviction")
    score, confidence, source = analyze_signal(signal_text)
    if news_score is not None:
        # blend: LLM read of headlines + weighted news score, equal weight
        score = int(round((score + news_score) / 2))
        source = f"{source}+news({n_news})"

    out = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "signal_text": signal_text,
        "score": score,
        "confidence": confidence,
        "source": source,
        "news_score": news_score,
        "news_entries": n_news,
        "generated_at_unix": int(time.time()),
    }

    os.makedirs("web", exist_ok=True)
    with open("web/latest_signal.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    try:
        _pr = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "ripple", "vs_currencies": "usd"},
            timeout=6,
        )
        price_now = float(_pr.json().get("ripple", {}).get("usd", 0))
    except Exception:
        price_now = 0.0
    hist_entry = dict(out)
    hist_entry["price_at_emission"] = price_now
    with open("web/signal_history.jsonl", "a", encoding="utf-8") as hf:
        print(json.dumps(hist_entry), file=hf)

    print(json.dumps(out))


if __name__ == "__main__":
    main()
