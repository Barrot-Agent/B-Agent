#!/usr/bin/env python3
import json
import math
import os
import time
from datetime import datetime, timezone

import requests

GITHUB_MODELS_ENDPOINT = "https://models.github.ai/inference/chat/completions"
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

DEFAULT_GITHUB_MODEL = os.getenv("GITHUB_MODEL", "openai/gpt-4.1-mini")
DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

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
    """Parse provider JSON strictly; malformed or incomplete output is unavailable evidence."""
    if not isinstance(text, str):
        raise ValueError("invalid_model_json")
    try:
        data = json.loads(text)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid_model_json") from exc
    if not isinstance(data, dict):
        raise ValueError("model_json_must_be_object")

    score = data.get("score")
    confidence = data.get("confidence")
    label = data.get("label")
    if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 100:
        raise ValueError("invalid_model_score")
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        raise ValueError("invalid_model_confidence")
    confidence = float(confidence)
    if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
        raise ValueError("invalid_model_confidence")
    if not isinstance(label, str) or label.lower() not in {"bullish", "neutral", "bearish"}:
        raise ValueError("invalid_model_label")
    return score, confidence, label.lower()

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

    # Opt-in real chain-of-thought + self-consistency classifier
    # (Wei et al. 2022, Wang et al. 2023) - uses 3x Groq calls per
    # classification instead of 1x, so this is gated behind an env var
    # rather than silently tripling token usage on the live pipeline.
    # Set USE_SELF_CONSISTENCY=1 to enable.
    if os.getenv("USE_SELF_CONSISTENCY", "") == "1":
        try:
            from groq_chain import classify_with_self_consistency
            result = classify_with_self_consistency(signal_text)
            return result["score"], result["confidence"], f"groq_sc:{result['label']}"
        except Exception:
            pass  # fall through to the original single-shot call below

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

    return None, 0.0, f"sentiment unavailable ({last_err})"


ACADEMIC_SOURCE_NAMES = {
    "research", "research_paper", "research_article", "paper", "working_paper",
    "whitepaper", "journal_article", "preprint", "conference_paper",
    "scholarly_paper", "thesis", "dissertation", "academic", "academic_paper",
    "scholarly_article",
}
ACADEMIC_PREFIXES = ("academic", "scholarly", "crossref", "semantic_scholar", "openalex", "arxiv")


def _is_market_news_entry(entry):
    """Require a source label and exclude records explicitly identified as scholarly research."""
    def normalize(value):
        return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")

    source = normalize(entry.get("source") or entry.get("source_type"))
    content_type = normalize(entry.get("content_type") or entry.get("document_type"))
    if not source:
        return False
    if source in ACADEMIC_SOURCE_NAMES or content_type in ACADEMIC_SOURCE_NAMES:
        return False
    if source.startswith(ACADEMIC_PREFIXES) or content_type.startswith(ACADEMIC_PREFIXES):
        return False
    return True


def _news_score(hours=72, path="ping-pongings/knowledge-base/log.jsonl"):
    """Return a freshness- and provenance-gated market-news score, or (None, 0, [])."""
    from datetime import timedelta

    if not os.path.exists(path):
        return None, 0, []
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=hours)
    num = den = 0.0
    used = 0
    heads = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line)
            except Exception:
                continue
            if not isinstance(e, dict) or not e.get("distilled"):
                continue
            if not _is_market_news_entry(e):
                continue
            d = e.get("distill", {})
            if not isinstance(d, dict):
                continue
            raw_weight = d.get("xrp_relevance", 0)
            try:
                weight = float(raw_weight or 0)
            except (TypeError, ValueError, OverflowError):
                continue
            if not math.isfinite(weight) or weight <= 0:
                continue

            raw_timestamp = e.get("ingested_at")
            if not isinstance(raw_timestamp, str) or not raw_timestamp.strip():
                continue
            try:
                stamp = datetime.fromisoformat(raw_timestamp.strip().replace("Z", "+00:00"))
            except (TypeError, ValueError, OverflowError):
                continue
            # A naive timestamp has no reliable timezone; do not assume UTC.
            if stamp.tzinfo is None or stamp.utcoffset() is None:
                continue
            stamp = stamp.astimezone(timezone.utc)
            if stamp < cutoff or stamp > now + timedelta(minutes=5):
                continue

            sentiment = str(d.get("sentiment") or "").strip().lower()
            if sentiment not in {"bullish", "neutral", "bearish"}:
                continue
            value = {"bullish": 1.0, "neutral": 0.0, "bearish": -1.0}[sentiment]
            num += value * weight
            den += weight
            used += 1
            if weight >= 0.5 and len(heads) < 6:
                heads.append(f"[{sentiment}] {str(e.get('title') or '')[:80]}")
    if den == 0:
        return None, 0, []
    return int(round((num / den + 1) * 50)), used, heads

def main():
    news_score, n_news, headlines = _news_score()
    if headlines:
        signal_text = "Recent XRP-relevant headlines: " + " | ".join(headlines)
    else:
        signal_text = os.getenv("BARROT_SIGNAL_TEXT", "market sideways; low conviction")

    model_score, confidence, source = analyze_signal(signal_text)
    if model_score is None:
        # Never manufacture a numeric combined score from a provider failure.
        score = None
        signal_status = "news_only" if news_score is not None else "unavailable"
        score_basis = "news" if news_score is not None else "unavailable"
    elif news_score is not None:
        score = int(round((model_score + news_score) / 2))
        source = f"{source}+news({n_news})"
        signal_status = "model_and_news"
        score_basis = "model_and_news"
    else:
        score = model_score
        signal_status = "model_only"
        score_basis = "model"

    out = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "signal_text": signal_text,
        "score": score,
        "confidence": confidence,
        "source": source,
        "model_score": model_score,
        "model_confidence": confidence,
        "model_available": model_score is not None,
        "signal_status": signal_status,
        "score_basis": score_basis,
        "forecast_status": "NOT_ISSUED",
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
