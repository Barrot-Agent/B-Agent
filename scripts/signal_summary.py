#!/usr/bin/env python3
"""Signal summary + Groq Orpheus TTS. Real keys only, real errors surfaced."""
import json, os, sys, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIGNAL_FILE = ROOT / "web" / "latest_signal.json"
SUMMARY_FILE = ROOT / "web" / "latest_signal_summary.json"
AUDIO_DIR = ROOT / "web" / "generated_audio"
AUDIO_FILE = AUDIO_DIR / "latest_signal_summary.wav"
KEY = os.environ.get("GROQ_API_KEY", "")
DISCLAIMER = "Not financial advice. Informational only. Do your own research."
TTS_LIMIT = 200
LAST_CHAT_ERROR = None

def post(url, payload, timeout):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {KEY}",
                 "Content-Type": "application/json",
                 "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                               "AppleWebKit/537.36 (KHTML, like Gecko) "
                               "Chrome/126.0.0.0 Safari/537.36",
                 "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read(), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read().decode('utf-8','replace')[:500]}"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"

def chat(prompt, max_tokens=400):
    global LAST_CHAT_ERROR
    raw, err = post("https://api.groq.com/openai/v1/chat/completions",
                    {"model": "openai/gpt-oss-120b",
                     "messages": [{"role": "user", "content": prompt}],
                     "max_tokens": max_tokens, "temperature": 0.4,
                     "reasoning_effort": "low"}, 60)
    if err:
        LAST_CHAT_ERROR = err
        print(f"[chat] FAILED: {err}")
        return ""
    LAST_CHAT_ERROR = None
    msg = json.loads(raw)["choices"][0]["message"]
    out = (msg.get("content") or "").strip()
    if not out:
        print(f"[chat] content empty; message keys: {list(msg.keys())}")
        out = (msg.get("reasoning") or "").strip()
        if out:
            print("[chat] recovered from reasoning field")
    return out

def speak(text):
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    raw, err = post("https://api.groq.com/openai/v1/audio/speech",
                    {"model": "canopylabs/orpheus-v1-english",
                     "input": text[:TTS_LIMIT], "voice": "autumn",
                     "response_format": "wav"}, 90)
    if err:
        print(f"[tts] FAILED (no audio written): {err}")
        return None, err
    AUDIO_FILE.write_bytes(raw)
    print(f"[tts] OK: {len(raw)} bytes -> {AUDIO_FILE}")
    return str(AUDIO_FILE.relative_to(ROOT)), None

def fallback_line(signal):
    """Deterministic spoken line from real signal fields only."""
    score = signal.get("score")
    conf = signal.get("confidence")
    n = signal.get("news_entries")
    bits = ["XRP signal update."]
    if score is not None:
        bits.append(f"Score {score}.")
    if conf is not None:
        bits.append(f"Confidence {conf}.")
    if n is not None:
        bits.append(f"Based on {n} news entries.")
    return " ".join(bits)

def model_unavailable(signal):
    status = str(signal.get("signal_status", "")).lower()
    source = str(signal.get("source", "")).lower()
    return (
        signal.get("model_available") is False
        or status in {"unavailable", "news_only"}
        or "sentiment unavailable" in source
        or "github_failed:" in source
        or "groq_failed:" in source
    )


def fallback_summary(signal):
    """Describe valid fields only; never repeat a contaminated combined score."""
    status = str(signal.get("signal_status", "")).lower()
    news_score = signal.get("news_score")
    news_entries = signal.get("news_entries")
    if status == "unavailable" or (model_unavailable(signal) and news_score is None):
        return (
            "Signal unavailable because model-provider analysis or usable news data is missing. "
            "No directional forecast is issued. This is not a calibrated price prediction."
        )
    if model_unavailable(signal):
        score_text = f"news-only sentiment score {news_score}" if news_score is not None else "no usable news score"
        count_text = f" from {news_entries} news entries" if news_entries is not None else ""
        return (
            f"Model-provider analysis is unavailable. The {score_text}{count_text} is reported separately; "
            "do not interpret a combined compatibility score as a directional signal. "
            "This is not a calibrated price prediction."
        )
    score = signal.get("score")
    confidence = signal.get("confidence")
    if score is None:
        return "No model score is available. No directional forecast is issued. This is not a calibrated price prediction."
    confidence_text = f" Confidence field: {confidence}." if confidence is not None else ""
    return f"Observed signal score: {score}.{confidence_text} This is sentiment analysis, not a calibrated price prediction."


def fallback_line(signal):
    status = str(signal.get("signal_status", "")).lower()
    news_score = signal.get("news_score")
    news_entries = signal.get("news_entries")
    if status == "unavailable" or (model_unavailable(signal) and news_score is None):
        return "XRP signal unavailable; no directional forecast."
    if model_unavailable(signal):
        score_text = f"news-only score {news_score}" if news_score is not None else "no usable news score"
        count_text = f" from {news_entries} headlines" if news_entries is not None else ""
        return f"XRP model unavailable; {score_text}{count_text}; no directional forecast."
    score = signal.get("score")
    confidence = signal.get("confidence")
    parts = ["XRP signal update."]
    if score is not None:
        parts.append(f"Score {score}.")
    if confidence is not None:
        parts.append(f"Confidence {confidence}.")
    return " ".join(parts)


def safe_error_label(error):
    if not error:
        return None
    text = str(error)
    for code, label in ((429, "HTTP 429 rate limited"), (401, "HTTP 401 unauthorized"), (403, "HTTP 403 forbidden")):
        if f"HTTP {code}" in text:
            return label
    return text.split(":", 1)[0][:100]


def main():
    global LAST_CHAT_ERROR
    if not SIGNAL_FILE.is_file():
        sys.exit(f"{SIGNAL_FILE} not found")
    signal = json.loads(SIGNAL_FILE.read_text(encoding="utf-8"))
    print("SIGNAL KEYS:", list(signal.keys()))

    base = (
        "Summarize this XRP signal in 2 sentences, then 3 short bullets. "
        "Use ONLY the values shown. Invent nothing.\\n\\n"
        + json.dumps(signal, indent=2)
    )
    summary = ""
    provider_error = None
    summary_method = "model_generated"
    signal_model_available = not model_unavailable(signal)

    # Do not send a contaminated compatibility score to another model.
    if not signal_model_available:
        summary = fallback_summary(signal)
        summary_method = "deterministic_fallback"
        provider_error = "signal model unavailable; summary model bypassed"
        LAST_CHAT_ERROR = provider_error
        print("[chat] skipped: signal model unavailable; using deterministic fallback")
    elif KEY:
        summary = chat(base)
        provider_error = safe_error_label(LAST_CHAT_ERROR)
    else:
        provider_error = "GROQ_API_KEY missing"
        LAST_CHAT_ERROR = provider_error
        print("[chat] skipped: GROQ_API_KEY missing; using deterministic fallback")

    if not summary:
        summary = fallback_summary(signal)
        summary_method = "deterministic_fallback"

    spoken = ""
    if KEY and summary_method == "model_generated":
        spoken = chat(
            "Compress to ONE spoken sentence under 130 characters, plain words only: "
            "no markdown, no asterisks, no raw timestamps. Reply with the sentence and nothing else.\\n\\n"
            + summary,
            500,
        )
        provider_error = safe_error_label(LAST_CHAT_ERROR) or provider_error

    spoken = " ".join((spoken or "").replace("*", "").split())
    if not spoken or len(spoken) > 140:
        spoken = fallback_line(signal)

    line = f"{spoken} {DISCLAIMER}"[:TTS_LIMIT]
    audio = None
    tts_error = None
    if KEY and summary_method == "model_generated" and not LAST_CHAT_ERROR:
        audio, tts_error = speak(line)
    else:
        tts_error = "skipped because model provider was unavailable or key was missing"

    SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_FILE.write_text(
        json.dumps(
            {
                "summary": summary,
                "summary_method": summary_method,
                "summary_status": "available" if summary else "unavailable",
                "spoken_line": line,
                "disclaimer": DISCLAIMER,
                "audio": audio,
                "tts_error": tts_error,
                "provider_error": provider_error,
                "model_available": signal_model_available,
                "signal_model_available": signal_model_available,
                "summary_model_available": summary_method == "model_generated",
                "source_signal": signal,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Summary written ({summary_method})")


if __name__ == "__main__":
    main()
