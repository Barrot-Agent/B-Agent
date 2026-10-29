#!/usr/bin/env python3
"""Quota-safe signal summary and optional Groq Orpheus TTS."""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIGNAL_FILE = ROOT / "web" / "latest_signal.json"
SUMMARY_FILE = ROOT / "web" / "latest_signal_summary.json"
AUDIO_DIR = ROOT / "web" / "generated_audio"
AUDIO_FILE = AUDIO_DIR / "latest_signal_summary.wav"
KEY = os.environ.get("GROQ_API_KEY", "")
DISCLAIMER = "Not financial advice. Informational only. Do your own research."
TTS_LIMIT = 200
LAST_PROVIDER_ERROR_CATEGORY = None


def classify_provider_error(error):
    """Return a safe category, never the raw provider body or credentials."""
    value = str(error).lower()
    if "429" in value or "rate limit" in value or "quota" in value:
        return "quota_exceeded"
    if "timeout" in value or "timed out" in value:
        return "timeout"
    if "401" in value or "403" in value or "api key" in value or "unauthorized" in value:
        return "authentication_or_permission"
    if "json" in value or "decode" in value or "malformed" in value:
        return "malformed_response"
    if "empty" in value:
        return "empty_response"
    if "5" in value and "http" in value:
        return "provider_unavailable"
    return "provider_error"


def post(url, payload, timeout):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {KEY}",
                 "Content-Type": "application/json",
                 "User-Agent": "Barrot-Signal-Summary/1.0",
                 "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read(), None
    except urllib.error.HTTPError as exc:
        return None, f"HTTP {exc.code}"
    except Exception as exc:
        return None, type(exc).__name__


def chat(prompt, max_tokens=400):
    """Call Groq once; record a safe error category instead of leaking raw errors."""
    global LAST_PROVIDER_ERROR_CATEGORY
    LAST_PROVIDER_ERROR_CATEGORY = None
    if not KEY:
        LAST_PROVIDER_ERROR_CATEGORY = "missing_api_key"
        return ""
    raw, error = post(
        "https://api.groq.com/openai/v1/chat/completions",
        {"model": "openai/gpt-oss-120b",
         "messages": [{"role": "user", "content": prompt}],
         "max_tokens": max_tokens, "temperature": 0.4,
         "reasoning_effort": "low"},
        60,
    )
    if error:
        LAST_PROVIDER_ERROR_CATEGORY = classify_provider_error(error)
        print(f"[chat] unavailable: {LAST_PROVIDER_ERROR_CATEGORY}")
        return ""
    try:
        payload = json.loads(raw)
        choices = payload.get("choices") or []
        msg = choices[0].get("message") or {}
    except (TypeError, ValueError, KeyError, IndexError, AttributeError):
        LAST_PROVIDER_ERROR_CATEGORY = "malformed_response"
        print("[chat] unavailable: malformed_response")
        return ""
    output = (msg.get("content") or "").strip()
    if not output:
        output = (msg.get("reasoning") or "").strip()
    if not output:
        LAST_PROVIDER_ERROR_CATEGORY = "empty_response"
        print("[chat] unavailable: empty_response")
        return ""
    return output


def speak(text):
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    raw, error = post(
        "https://api.groq.com/openai/v1/audio/speech",
        {"model": "canopylabs/orpheus-v1-english",
         "input": text[:TTS_LIMIT], "voice": "autumn",
         "response_format": "wav"},
        90,
    )
    if error:
        category = classify_provider_error(error)
        print(f"[tts] unavailable: {category}")
        return None, category
    AUDIO_FILE.write_bytes(raw)
    print(f"[tts] OK: {len(raw)} bytes")
    return str(AUDIO_FILE.relative_to(ROOT)), None


def fallback_line(signal):
    """Deterministic spoken line using only supported source values."""
    bits = ["XRP signal update."]
    for key in ("score", "news_entries"):
        if key in signal and signal[key] is not None:
            bits.append(f"{key.replace('_', ' ')} {signal[key]}.")
    if len(bits) == 1:
        bits.append("No supported signal values were present.")
    return " ".join(bits)


def fallback_summary(signal):
    """Build a neutral summary only from fields actually present in the signal."""
    values = [
        f"{key}={signal[key]}"
        for key in ("score", "news_entries")
        if key in signal and signal[key] is not None
    ]
    if not values:
        return (
            "Model summary unavailable. The source signal has no supported fields "
            "for a deterministic summary."
        )
    return "Deterministic fallback using source signal values only: " + "; ".join(values) + "."


def write_summary_artifact(signal, summary, *, model_available, fallback_used,
                           provider_error_category=None, spoken_line=None,
                           audio=None, tts_error=None, speech_error_category=None):
    """Persist a valid artifact even when model summarization or TTS is unavailable."""
    payload = {
        "summary": summary,
        "spoken_line": spoken_line,
        "disclaimer": DISCLAIMER,
        "audio": audio,
        "tts_error": tts_error,
        "source_signal": signal,
        "model_available": bool(model_available),
        "fallback_used": bool(fallback_used),
        "provider_error_category": provider_error_category,
        "speech_error_category": speech_error_category,
    }
    SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_FILE.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main():
    if not SIGNAL_FILE.is_file():
        sys.exit(f"{SIGNAL_FILE} not found")
    try:
        signal = json.loads(SIGNAL_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        sys.exit(f"Source signal could not be read: {type(exc).__name__}")
    if not isinstance(signal, dict):
        sys.exit("Source signal must be a JSON object")
    print("SIGNAL KEYS:", list(signal.keys()))

    prompt = (
        "Summarize this XRP signal in 2 sentences, then 3 short bullets. "
        "Use ONLY the values shown. Invent nothing.\n\n"
        + json.dumps(signal, indent=2)
    )
    summary = chat(prompt)
    provider_error_category = LAST_PROVIDER_ERROR_CATEGORY
    model_available = bool(summary)
    fallback_used = not model_available
    if not summary:
        summary = fallback_summary(signal)

    speech_error_category = None
    tts_error = None
    audio = None
    spoken = None
    if model_available:
        spoken = chat(
            "Compress to ONE spoken sentence under 130 characters, plain words only: "
            "no markdown, no asterisks, no raw timestamps. Reply with the sentence only.\n\n"
            + summary,
            180,
        )
        speech_error_category = LAST_PROVIDER_ERROR_CATEGORY
    if not spoken or len(spoken) > 140:
        spoken = fallback_line(signal)
        if model_available and not speech_error_category:
            speech_error_category = "invalid_or_empty_compression"
    line = f"{spoken} {DISCLAIMER}"[:TTS_LIMIT]

    # Do not spend additional provider quota on TTS after a model/quota failure.
    if model_available and provider_error_category is None and speech_error_category is None:
        audio, tts_error = speak(line)
        if tts_error:
            speech_error_category = classify_provider_error(tts_error)
    else:
        tts_error = "skipped_provider_unavailable"

    artifact = write_summary_artifact(
        signal, summary,
        model_available=model_available,
        fallback_used=fallback_used,
        provider_error_category=provider_error_category,
        spoken_line=line,
        audio=audio,
        tts_error=tts_error,
        speech_error_category=speech_error_category,
    )
    print(
        "Summary written:",
        f"model_available={artifact['model_available']}",
        f"fallback_used={artifact['fallback_used']}",
        f"provider_error_category={artifact['provider_error_category']}",
    )


if __name__ == "__main__":
    main()
