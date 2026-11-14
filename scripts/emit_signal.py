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


def _normalize_confidence(value) -> float:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(confidence):
        return 0.0
    return max(0.0, min(1.0, confidence))


def _normalize_score(value) -> int:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return 50
    if not math.isfinite(score):
        return 50
    return int(round(max(0.0, min(100.0, score))))


def _score_from_text(text: str):
    try:
        data = json.loads(text)
    except Exception:
        return 50, 0.0, "neutral"
    if not isinstance(data, dict):
        return 50, 0.0, "neutral"
    score = _normalize_score(data.get("score", 50))
    confidence = _normalize_confidence(data.get("confidence"))
    label = str(data.get("label", "neutral")).strip().lower()
    if label not in {"bullish", "neutral", "bearish"}:
        label = "neutral"
    return score, confidence, label


def _sentiment_feature_metadata(label: str, confidence: float):
    """Metadata that prevents sentiment output being mistaken for a forecast."""
    normalized = str(label or "neutral").strip().lower()
    if normalized not in {"bullish", "neutral", "bearish"}:
        normalized = "neutral"
    return {
        "signal_kind": "sentiment_feature_only",
        "forecast_eligible": False,
        "forecast_status": "NOT_A_FORECAST",
        "sentiment_label": normalized,
        "confidence_is_calibrated_probability": False,
        "confidence_semantics": "Uncalibrated LLM sentiment-classifier confidence; not a probability of price direction.",
        "sentiment_score_semantics": "0-100 blended LLM/news sentiment index; not a return forecast or probability.",
        "sentiment_label_source": "LLM classifier when explicitly authorized; neutral fallback otherwise.",
        "target": None,
        "horizon_seconds": None,
        "source_cutoff_utc": None,
        "source_snapshot_ids": [],
    }

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
    return score, conf, label, f"github:{label}"


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
            return result["score"], result["confidence"], str(result["label"]).strip().lower(), f"groq_sc:{result['label']}"
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
    return score, conf, label, f"groq:{label}"


def analyze_signal(signal_text: str):
    """Use an external sentiment model only after explicit per-run authorization.

    Provider selection is explicit: there is no silent GitHub Models -> Groq
    fallback and no provider credential is read before authorization.
    """
    if os.getenv("BARROT_ALLOW_EXTERNAL_SENTIMENT_CLASSIFIER") != "YES":
        return 50, 0.0, "neutral", "external_classifier_not_authorized"

    provider = os.getenv("BARROT_SENTIMENT_PROVIDER", "").strip().lower()
    if provider == "github_models":
        try:
            return _call_github_models(signal_text)
        except Exception as exc:
            return 50, 0.0, "neutral", f"github_models_failed:{type(exc).__name__}"
    if provider == "groq":
        try:
            return _call_groq(signal_text)
        except Exception as exc:
            return 50, 0.0, "neutral", f"groq_failed:{type(exc).__name__}"
    return 50, 0.0, "neutral", "sentiment_provider_not_selected"


def _news_score(hours=72, path="ping-pongings/knowledge-base/log.jsonl"):
    """Return a relevance-weighted sentiment feature using only valid recent UTC timestamps."""
    from datetime import timedelta

    if not os.path.exists(path):
        return None, 0, []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
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
            d = e.get("distill", {})
            if not isinstance(d, dict):
                continue
            try:
                w = float(d.get("xrp_relevance", 0) or 0)
            except (TypeError, ValueError, OverflowError):
                continue
            if not math.isfinite(w) or w <= 0:
                continue
            raw_timestamp = e.get("ingested_at")
            if not isinstance(raw_timestamp, str) or not raw_timestamp.strip():
                continue
            try:
                ts = datetime.fromisoformat(raw_timestamp.strip().replace("Z", "+00:00"))
                if ts.tzinfo is None or ts.utcoffset() is None:
                    continue
                ts = ts.astimezone(timezone.utc)
            except (TypeError, ValueError, OverflowError):
                continue
            if ts < cutoff:
                continue
            sentiment = str(d.get("sentiment", "")).strip().lower()
            s = {"bullish": 1.0, "neutral": 0.0, "bearish": -1.0}.get(sentiment, 0.0)
            num += s * w
            den += w
            used += 1
            if w >= 0.5 and len(heads) < 6:
                heads.append(f"[{sentiment or 'unknown'}] {str(e.get('title', ''))[:80]}")
    if den == 0:
        return None, 0, []
    return int(round((num / den + 1) * 50)), used, heads


def main():
    news_score, n_news, headlines = _news_score()
    if headlines:
        signal_text = "Recent XRP-relevant headlines: " + " | ".join(headlines)
    else:
        signal_text = os.getenv("BARROT_SIGNAL_TEXT", "market sideways; low conviction")
    score, confidence, label, source = analyze_signal(signal_text)
    score = _normalize_score(score)
    confidence = _normalize_confidence(confidence)
    if news_score is not None:
        # blend: LLM read of headlines + weighted news score, equal weight
        score = int(round((score + news_score) / 2))
        source = f"{source}+news({n_news})"

    generated_at = datetime.now(timezone.utc).isoformat()
    out = {
        "timestamp": generated_at,
        "generated_at_utc": generated_at,
        "signal_text": signal_text,
        "score": score,
        "confidence": confidence,
        "source": source,
        "news_score": news_score,
        "news_entries": n_news,
        "generated_at_unix": int(time.time()),
        **_sentiment_feature_metadata(label, confidence),
    }

    os.makedirs("web", exist_ok=True)
    with open("web/latest_signal.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    hist_entry = dict(out)
    with open("web/signal_history.jsonl", "a", encoding="utf-8") as hf:
        print(json.dumps(hist_entry), file=hf)

    print(json.dumps(out))


if __name__ == "__main__":
    main()
