#!/usr/bin/env python3
"""Emit an XRP sentiment artifact without converting missing evidence into a score.

This module emits sentiment metadata only. It does not issue a calibrated price
forecast; forecast_status therefore remains NOT_ISSUED.
"""
import json
import math
import os
import time
from datetime import datetime, timedelta, timezone

import requests

GITHUB_MODELS_ENDPOINT = "https://models.github.ai/inference/chat/completions"
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

DEFAULT_GITHUB_MODEL = os.getenv("GITHUB_MODEL", "openai/gpt-4.1-mini")
DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
TIMEOUT = float(os.getenv("SIGNAL_HTTP_TIMEOUT", "20"))
VALID_LABELS = {"bullish", "neutral", "bearish"}
ACADEMIC_SOURCE_MARKERS = (
    "academic", "arxiv", "scholarly", "research paper", "research_paper",
    "peer-reviewed", "peer reviewed", "preprint", "journal article",
    "conference paper", "conference proceedings", "working paper",
)
ACADEMIC_DOMAIN_MARKERS = (
    "arxiv.org", "doi.org", "semanticscholar.org", "researchgate.net",
    "openreview.net", "dl.acm.org", "acm.org", "ieeexplore.ieee.org",
    "ieee.org", "link.springer.com", "springer.com", "sciencedirect.com",
    "ssrn.com",
)
# Narrow title signatures observed in contaminated XRP sentiment inputs. These
# are supplemental to provenance/domain checks, not a general news classifier.
ACADEMIC_TITLE_MARKERS = (
    "analysis of the xrp ledger consensus protocol",
    "to squelch or not to squelch",
    "probabilistic edge multicast routing",
    "pub/sub dissemination on the xrp ledger",
    "consensus crash testing",
    "causal ai for xrpl/gossipsub",
    "dissemination on the xrp ledger",
    "gossipsub network configuration",
)


def _post_json(url: str, headers: dict, payload: dict, timeout: float = TIMEOUT):
    response = requests.post(url, headers=headers, json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()


def _extract_text(resp_json: dict) -> str:
    try:
        value = resp_json.get("choices", [{}])[0].get("message", {}).get("content", "")
        return value.strip() if isinstance(value, str) else ""
    except (AttributeError, IndexError, TypeError):
        return ""


def _score_from_text(text: str):
    """Return a validated (score, confidence, label) tuple, or None.

    Missing keys, malformed JSON, coercions, non-finite confidence, and
    out-of-range values are unavailable evidence—not neutral sentiment.
    """
    if not isinstance(text, str) or not text.strip():
        return None
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(data, dict):
        return None

    score = data.get("score")
    confidence = data.get("confidence")
    label = data.get("label")
    if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 100:
        return None
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        return None
    confidence = float(confidence)
    if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
        return None
    if not isinstance(label, str) or label.strip().lower() not in VALID_LABELS:
        return None
    return score, confidence, label.strip().lower()


def _build_messages(signal_text: str):
    return [
        {
            "role": "system",
            "content": (
                "Classify only the sentiment of the supplied crypto/market text. "
                "Return ONLY JSON with score (integer 0-100), confidence (number 0-1), "
                "and label (bullish|neutral|bearish). Do not claim to predict price."
            ),
        },
        {"role": "user", "content": f"Classify sentiment for: {signal_text}"},
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
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    parsed = _score_from_text(_extract_text(_post_json(GITHUB_MODELS_ENDPOINT, headers, payload)))
    if parsed is None:
        raise ValueError("invalid GitHub Models sentiment JSON contract")
    score, confidence, label = parsed
    return score, confidence, f"github:{label}"


def _call_groq(signal_text: str):
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        raise RuntimeError("missing GROQ_API_KEY")
    if os.getenv("USE_SELF_CONSISTENCY", "") == "1":
        try:
            from groq_chain import classify_with_self_consistency
            result = classify_with_self_consistency(signal_text)
            parsed = _score_from_text(json.dumps(result))
            if parsed is not None:
                score, confidence, label = parsed
                return score, confidence, f"groq_sc:{label}"
        except Exception:
            pass

    payload = {
        "model": DEFAULT_GROQ_MODEL,
        "messages": _build_messages(signal_text),
        "temperature": 0.1,
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    parsed = _score_from_text(_extract_text(_post_json(GROQ_ENDPOINT, headers, payload)))
    if parsed is None:
        raise ValueError("invalid Groq sentiment JSON contract")
    score, confidence, label = parsed
    return score, confidence, f"groq:{label}"


def analyze_signal(signal_text: str):
    errors = []
    for provider_name, provider in (
        ("github", _call_github_models),
        ("groq", _call_groq),
    ):
        try:
            return provider(signal_text)
        except Exception as exc:
            errors.append(f"{provider_name}_failed:{exc}")
    return None, None, "sentiment unavailable (" + "; ".join(errors) + ")"


def _news_score(hours=72, path="ping-pongings/knowledge-base/log.jsonl"):
    """Return a freshness-gated sentiment score or (None, 0, []).

    Records with missing/invalid/naive timestamps, materially future timestamps,
    academic provenance, invalid weights, or unknown sentiment are excluded.
    """
    if not os.path.exists(path):
        return None, 0, []
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=hours)
    num = den = 0.0
    used = 0
    headlines = []
    with open(path, encoding="utf-8") as source_file:
        for line in source_file:
            try:
                entry = json.loads(line)
            except (json.JSONDecodeError, TypeError):
                continue
            if not isinstance(entry, dict) or not entry.get("distilled"):
                continue
            distill = entry.get("distill")
            if not isinstance(distill, dict):
                continue

            provenance = " ".join(
                str(entry.get(key, ""))
                for key in (
                    "source", "source_type", "category", "publisher", "domain",
                    "url", "feed", "doi", "authors",
                )
            ).lower()
            title_text = str(entry.get("title", "")).lower()
            if any(marker in provenance for marker in ACADEMIC_SOURCE_MARKERS):
                continue
            if any(marker in provenance for marker in ACADEMIC_DOMAIN_MARKERS):
                continue
            if any(marker in title_text for marker in ACADEMIC_TITLE_MARKERS):
                continue

            raw_timestamp = entry.get("ingested_at")
            if not isinstance(raw_timestamp, str) or not raw_timestamp.strip():
                continue
            try:
                timestamp = datetime.fromisoformat(raw_timestamp.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                continue
            if timestamp.tzinfo is None or timestamp.utcoffset() is None:
                continue
            if timestamp < cutoff or timestamp > now + timedelta(minutes=5):
                continue

            try:
                weight = float(distill.get("xrp_relevance", 0) or 0)
            except (TypeError, ValueError):
                continue
            if not math.isfinite(weight) or weight <= 0:
                continue
            sentiment = distill.get("sentiment")
            if not isinstance(sentiment, str) or sentiment.lower() not in VALID_LABELS:
                continue
            sentiment = sentiment.lower()
            sentiment_value = {"bullish": 1.0, "neutral": 0.0, "bearish": -1.0}[sentiment]
            num += sentiment_value * weight
            den += weight
            used += 1
            if weight >= 0.5 and len(headlines) < 6:
                title = str(entry.get("title", ""))[:80]
                headlines.append(f"[{sentiment}] {title}")

    if den == 0:
        return None, 0, []
    return int(round((num / den + 1.0) * 50.0)), used, headlines


def main():
    news_score, news_count, headlines = _news_score()
    if headlines:
        signal_text = "Recent XRP-relevant headlines: " + " | ".join(headlines)
    else:
        signal_text = os.getenv("BARROT_SIGNAL_TEXT", "market sideways; low conviction")

    model_score, confidence, source = analyze_signal(signal_text)
    if model_score is None:
        score = None
        confidence = None
        signal_status = "news_only" if news_score is not None else "unavailable"
    else:
        score = int(round((model_score + news_score) / 2)) if news_score is not None else model_score
        signal_status = "model_plus_news" if news_score is not None else "model_only"

    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "generated_at_unix": int(time.time()),
        "signal_text": signal_text,
        "model_score": model_score,
        "score": score,
        "confidence": confidence,
        "source": source,
        "signal_status": signal_status,
        "forecast_status": "NOT_ISSUED",
        "news_score": news_score,
        "news_entries": news_count,
    }

    os.makedirs("web", exist_ok=True)
    with open("web/latest_signal.json", "w", encoding="utf-8") as output_file:
        json.dump(output, output_file, indent=2)
    print(json.dumps(output))


if __name__ == "__main__":
    main()
