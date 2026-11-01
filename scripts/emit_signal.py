#!/usr/bin/env python3
import json
import math
import os
import time
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

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
    try:
        data = json.loads(text)
    except Exception as exc:
        raise ValueError("invalid sentiment response JSON") from exc

    if not isinstance(data, dict):
        raise ValueError("sentiment response must be a JSON object")
    if not {"score", "confidence", "label"}.issubset(data):
        raise ValueError("sentiment response is missing required fields")

    raw_score = data["score"]
    raw_confidence = data["confidence"]
    if isinstance(raw_score, bool) or isinstance(raw_confidence, bool):
        raise ValueError("boolean score/confidence is invalid")
    try:
        score = int(raw_score)
        confidence = float(raw_confidence)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("score/confidence must be numeric") from exc
    if float(raw_score) != score or not 0 <= score <= 100:
        raise ValueError("score must be an integer from 0 to 100")
    if not 0.0 <= confidence <= 1.0:
        raise ValueError("confidence must be between 0 and 1")
    label = str(data["label"]).strip().lower()
    if label not in {"bullish", "neutral", "bearish"}:
        raise ValueError("label must be bullish, neutral or bearish")
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

    return None, None, f"sentiment unavailable ({last_err})"


def _parse_aware_timestamp(value):
    if value is None:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (TypeError, ValueError, OverflowError):
        try:
            parsed = parsedate_to_datetime(raw)
        except (TypeError, ValueError, OverflowError):
            return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def _news_score(hours=72, path="ping-pongings/knowledge-base/log.jsonl"):
    """Return a publication-time-bounded, relevance-weighted sentiment observation."""
    cutoff_now = datetime.now(timezone.utc)
    cutoff = cutoff_now - timedelta(hours=hours)
    allowed_clock_skew = timedelta(minutes=5)
    num = den = 0.0
    used = 0
    heads = []
    seen_urls = set()
    if not os.path.exists(path):
        return None, 0, []

    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
            except Exception:
                continue
            if not isinstance(entry, dict) or not entry.get("distilled"):
                continue
            distill = entry.get("distill")
            if not isinstance(distill, dict):
                continue

            ingested_at = _parse_aware_timestamp(entry.get("ingested_at"))
            published_at = _parse_aware_timestamp(entry.get("published_at"))
            if published_at is None:
                published_at = _parse_aware_timestamp(entry.get("published"))
            if ingested_at is None or published_at is None:
                continue
            if ingested_at > cutoff_now + allowed_clock_skew:
                continue
            if published_at > cutoff_now + allowed_clock_skew:
                continue
            if published_at > ingested_at + allowed_clock_skew:
                continue
            if published_at < cutoff:
                continue

            url = str(entry.get("url", "")).strip()
            if url and url in seen_urls:
                continue

            try:
                weight = float(distill.get("xrp_relevance", 0) or 0)
            except (TypeError, ValueError, OverflowError):
                continue
            if not math.isfinite(weight) or not 0.0 < weight <= 1.0:
                continue

            sentiment = str(distill.get("sentiment", "")).strip().lower()
            sentiment_value = {"bullish": 1.0, "neutral": 0.0, "bearish": -1.0}.get(sentiment)
            if sentiment_value is None:
                continue

            num += sentiment_value * weight
            den += weight
            used += 1
            if url:
                seen_urls.add(url)
            title = str(entry.get("title", ""))
            if weight >= 0.5 and len(heads) < 6:
                heads.append(f"[{sentiment}] {title[:80]}")

    if not math.isfinite(den) or den <= 0.0:
        return None, 0, []
    score = int(round((num / den + 1.0) * 50.0))
    return score, used, heads


def main():
    news_score, n_news, headlines = _news_score()
    explicit_text = os.getenv("BARROT_SIGNAL_TEXT", "").strip()
    if headlines:
        signal_text = "Recent XRP-relevant headlines: " + " | ".join(headlines)
    elif explicit_text:
        signal_text = explicit_text
    else:
        signal_text = None

    if signal_text is None:
        score, confidence, source = None, None, "unavailable:no_qualifying_headlines_or_explicit_signal_text"
    else:
        score, confidence, source = analyze_signal(signal_text)

    valid_output = False
    if score is not None and confidence is not None and not isinstance(score, bool) and not isinstance(confidence, bool):
        try:
            score_value = int(score)
            confidence_value = float(confidence)
            valid_output = (
                float(score) == score_value
                and 0 <= score_value <= 100
                and math.isfinite(confidence_value)
                and 0.0 < confidence_value <= 1.0
            )
        except (TypeError, ValueError, OverflowError):
            valid_output = False
    if valid_output:
        score = score_value
        confidence = confidence_value
    if valid_output and news_score is not None:
        # Blend only after a valid provider response; a failed provider must
        # never turn a missing score into a numeric signal.
        score = int(round((score + news_score) / 2))
        source = f"{source}+news({n_news})"

    out = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "SENTIMENT_OBSERVATION" if valid_output else "UNAVAILABLE",
        "forecast_status": "NOT_ISSUED",
        "signal_text": signal_text,
        "score": int(score) if valid_output else None,
        "confidence": float(confidence) if valid_output else None,
        "confidence_kind": "MODEL_REPORTED_NOT_CALIBRATED" if valid_output else None,
        "source": source,
        "news_score": news_score,
        "news_entries": n_news,
        "generated_at_unix": int(time.time()),
        "history_appended": False,
    }

    if valid_output:
        price_now = None
        try:
            response = requests.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": "ripple", "vs_currencies": "usd"},
                timeout=6,
            )
            response.raise_for_status()
            candidate = float(response.json().get("ripple", {}).get("usd"))
            if candidate > 0:
                price_now = candidate
        except Exception:
            price_now = None

        hist_entry = dict(out)
        hist_entry["price_at_emission"] = price_now
        hist_entry["history_appended"] = True
        os.makedirs("web", exist_ok=True)
        with open("web/signal_history.jsonl", "a", encoding="utf-8") as hf:
            print(json.dumps(hist_entry), file=hf)
        out["history_appended"] = True
    else:
        out["reason"] = "No qualifying input or no valid provider response; no numeric sentiment score emitted."

    os.makedirs("web", exist_ok=True)
    with open("web/latest_signal.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(json.dumps(out))


if __name__ == "__main__":
    main()
