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
    """Parse the exact classifier contract; malformed output must not become fake confidence."""
    try:
        data = json.loads(text)
    except (TypeError, ValueError) as exc:
        raise ValueError("classifier response is not valid JSON") from exc

    if not isinstance(data, dict) or set(data) != {"score", "confidence", "label"}:
        raise ValueError("classifier response must contain exactly score, confidence, and label")

    score = data["score"]
    confidence = data["confidence"]
    label = data["label"]

    if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 100:
        raise ValueError("classifier score must be an integer from 0 through 100")
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        raise ValueError("classifier confidence must be numeric")
    confidence = float(confidence)
    if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
        raise ValueError("classifier confidence must be finite and between 0 and 1")
    if label not in {"bullish", "neutral", "bearish"}:
        raise ValueError("classifier label is not in the allowed set")

    return score, confidence, label

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

    return 0, 0.0, f"sentiment unavailable ({last_err})"


def _news_score(hours=72, path="ping-pongings/knowledge-base/log.jsonl"):
    """Return a timestamp-valid, finite, XRP-relevance-weighted sentiment summary."""
    from datetime import timedelta

    if not os.path.exists(path):
        return None, 0, []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    num = den = 0.0
    used = 0
    heads = []
    with open(path, encoding="utf-8") as source_file:
        for line in source_file:
            try:
                entry = json.loads(line)
            except (TypeError, ValueError):
                continue
            if not isinstance(entry, dict) or not entry.get("distilled"):
                continue
            distill = entry.get("distill")
            if not isinstance(distill, dict):
                continue
            try:
                weight = float(distill.get("xrp_relevance", 0) or 0)
            except (TypeError, ValueError, OverflowError):
                continue
            if not math.isfinite(weight) or weight <= 0:
                continue

            raw_timestamp = entry.get("ingested_at")
            if not isinstance(raw_timestamp, str) or not raw_timestamp.strip():
                continue
            try:
                timestamp = datetime.fromisoformat(raw_timestamp.replace("Z", "+00:00"))
            except (TypeError, ValueError, OverflowError):
                continue
            if timestamp.tzinfo is None or timestamp.utcoffset() is None:
                continue
            if timestamp < cutoff:
                continue

            sentiment = distill.get("sentiment")
            if not isinstance(sentiment, str) or sentiment not in {"bullish", "neutral", "bearish"}:
                continue
            sentiment_value = {"bullish": 1.0, "neutral": 0.0, "bearish": -1.0}[sentiment]
            num += sentiment_value * weight
            den += weight
            used += 1
            if weight >= 0.5 and len(heads) < 6:
                title = entry.get("title", "")
                if not isinstance(title, str):
                    title = ""
                heads.append(f"[{sentiment}] {title[:80]}")

    if den == 0:
        return None, 0, []
    return int(round((num / den + 1) * 50)), used, heads


def _forecast_metadata(source: str, confidence, data_cutoff_utc: str):
    """This script emits descriptive sentiment only, never a calibrated price forecast."""
    source_text = source.lower() if isinstance(source, str) else ""
    unavailable_markers = ("unavailable", "failed:", "missing ", "http 429", "rate limit")
    if any(marker in source_text for marker in unavailable_markers):
        reason = "SENTIMENT_PROVIDER_UNAVAILABLE"
    else:
        try:
            value = float(confidence)
        except (TypeError, ValueError, OverflowError):
            value = float("nan")
        if not math.isfinite(value) or not 0.0 < value <= 1.0:
            reason = "INVALID_OR_ZERO_CLASSIFIER_CONFIDENCE"
        else:
            reason = "NO_CALIBRATED_FIXED_HORIZON_PRICE_MODEL"

    return {
        "status": "NOT_ISSUED",
        "reason_code": reason,
        "data_cutoff_utc": data_cutoff_utc,
        "target": None,
        "horizon": None,
        "probability": None,
        "assumptions": [],
        "alternatives": [],
        "outcome_protocol": (
            "Do not score this record as a forecast. A future forecast must pre-register "
            "its target, horizon, calibrated probability, assumptions, alternatives, and "
            "fixed outcome-scoring window before the outcome is observed."
        ),
    }


def _build_signal_output(signal_text, score, confidence, source, news_score, n_news,
                         timestamp=None, generated_at_unix=None):
    """Build a backward-compatible descriptive signal with an explicit forecast gate."""
    timestamp = timestamp or datetime.now(timezone.utc).isoformat()
    if generated_at_unix is None:
        generated_at_unix = int(time.time())
    return {
        "timestamp": timestamp,
        "signal_text": signal_text,
        "score": score,
        "confidence": confidence,
        "source": source,
        "news_score": news_score,
        "news_entries": n_news,
        "generated_at_unix": generated_at_unix,
        "signal_type": "descriptive_news_sentiment",
        "score_semantics": "descriptive_0_to_100_sentiment_blend_not_return_forecast",
        "confidence_semantics": "classifier_self_reported_confidence_not_calibrated_return_probability",
        "forecast_status": "NOT_ISSUED",
        "forecast": _forecast_metadata(source, confidence, timestamp),
    }

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

    out = _build_signal_output(
        signal_text, score, confidence, source, news_score, n_news
    )

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
    hist_entry["price_at_emission_status"] = "OBSERVED" if price_now > 0 else "UNAVAILABLE"
    hist_entry["price_reference_semantics"] = "reference_price_only_not_forecast_outcome"
    with open("web/signal_history.jsonl", "a", encoding="utf-8") as hf:
        print(json.dumps(hist_entry), file=hf)

    print(json.dumps(out))


if __name__ == "__main__":
    main()
