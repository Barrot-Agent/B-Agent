#!/usr/bin/env python3
"""Create an honest, non-directional summary artifact even when providers fail."""
import json
import math
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
UNAVAILABLE_MARKERS = ("unavailable", "failed:", "missing ", "http 429", "rate limit")


def classify_provider_error(error):
    """Return a safe category, never persist raw provider responses or credentials."""
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
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
            "User-Agent": "Barrot-Agent/1.0",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read(), None
    except urllib.error.HTTPError as exc:
        return None, f"HTTP {exc.code}"
    except Exception as exc:
        return None, type(exc).__name__


def chat(prompt, max_tokens=400):
    """Call Groq once and expose only a safe failure category."""
    global LAST_PROVIDER_ERROR_CATEGORY
    LAST_PROVIDER_ERROR_CATEGORY = None
    if not KEY:
        LAST_PROVIDER_ERROR_CATEGORY = "missing_api_key"
        return ""
    raw, error = post(
        "https://api.groq.com/openai/v1/chat/completions",
        {
            "model": "openai/gpt-oss-120b",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.2,
            "reasoning_effort": "low",
        },
        60,
    )
    if error or raw is None:
        LAST_PROVIDER_ERROR_CATEGORY = classify_provider_error(error or "empty response")
        print(f"[chat] unavailable: {LAST_PROVIDER_ERROR_CATEGORY}")
        return ""
    try:
        payload = json.loads(raw)
        choices = payload.get("choices") or []
        message = choices[0].get("message") or {}
    except (TypeError, ValueError, KeyError, IndexError, AttributeError):
        LAST_PROVIDER_ERROR_CATEGORY = "malformed_response"
        print("[chat] unavailable: malformed_response")
        return ""
    output = (message.get("content") or "").strip()
    if not output:
        output = (message.get("reasoning") or "").strip()
    if not output:
        LAST_PROVIDER_ERROR_CATEGORY = "empty_response"
        print("[chat] unavailable: empty_response")
        return ""
    return output


def speak(text):
    if not KEY:
        return None, "missing_api_key"
    raw, error = post(
        "https://api.groq.com/openai/v1/audio/speech",
        {
            "model": "canopylabs/orpheus-v1-english",
            "input": text[:TTS_LIMIT],
            "voice": "autumn",
            "response_format": "wav",
        },
        90,
    )
    if error or raw is None:
        category = classify_provider_error(error or "empty response")
        print(f"[tts] unavailable: {category}")
        return None, category
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_FILE.write_bytes(raw)
    return str(AUDIO_FILE.relative_to(ROOT)), None


def usable_signal(signal):
    """Only summarize well-formed numeric metadata from an available source."""
    if not isinstance(signal, dict):
        return False
    score = signal.get("score")
    confidence = signal.get("confidence")
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        return False
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        return False
    if not math.isfinite(float(score)) or not math.isfinite(float(confidence)):
        return False
    if not 0 < float(confidence) <= 1:
        return False
    source = signal.get("source")
    if not isinstance(source, str):
        return False
    source_lower = source.lower()
    return not any(marker in source_lower for marker in UNAVAILABLE_MARKERS)


def fallback_line(signal):
    """Neutral spoken line using only supported source values."""
    bits = ["XRP signal update."]
    for key in ("score", "news_entries"):
        if isinstance(signal, dict) and key in signal and signal[key] is not None:
            bits.append(f"{key.replace('_', ' ')} {signal[key]}.")
    if len(bits) == 1:
        bits.append("No supported signal values were present.")
    return " ".join(bits)


def fallback_summary(signal):
    """Build a neutral summary from a strict allowlist of fields actually present."""
    values = [
        f"{key}={signal[key]}"
        for key in ("score", "news_entries")
        if isinstance(signal, dict) and key in signal and signal[key] is not None
    ]
    if not values:
        return (
            "Model summary unavailable. The source signal has no supported fields "
            "for a deterministic summary. No directional forecast is issued."
        )
    return (
        "Deterministic summary using source signal values only: "
        + "; ".join(values)
        + ". No directional forecast is issued."
    )


def write_summary_artifact(signal, summary, *, status, model_available,
                           fallback_used, provider_error_category=None,
                           speech_error_category=None, spoken_line=None,
                           audio=None, tts_error=None, input_error=None):
    """Atomically persist honest summary status even when model/TTS calls fail."""
    payload = {
        "status": status,
        "forecast_status": "NOT_ISSUED",
        "summary_only": True,
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
        "input_error": input_error,
    }
    SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary = SUMMARY_FILE.with_suffix(SUMMARY_FILE.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(SUMMARY_FILE)
    return payload


def main():
    # Never leave a previous run's audio available to be uploaded as new output.
    try:
        AUDIO_FILE.unlink(missing_ok=True)
    except OSError as exc:
        print(f"[tts] could not remove prior runner-local audio: {type(exc).__name__}")

    signal = None
    input_error = None
    try:
        if not SIGNAL_FILE.is_file():
            raise FileNotFoundError("signal artifact missing")
        loaded = json.loads(SIGNAL_FILE.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError("signal artifact must be a JSON object")
        signal = loaded
    except (OSError, ValueError, TypeError) as exc:
        input_error = f"{type(exc).__name__}: {exc}"

    if not usable_signal(signal):
        summary = (
            "Directional forecast not issued. The signal artifact is missing, malformed, "
            "or has unavailable/invalid confidence or source data. No directional conclusion is supported."
        )
        spoken = "XRP signal unavailable; no directional forecast issued."
        write_summary_artifact(
            signal, summary,
            status="NOT_ISSUED",
            model_available=False,
            fallback_used=True,
            provider_error_category=None,
            speech_error_category="invalid_signal",
            spoken_line=f"{spoken} {DISCLAIMER}"[:TTS_LIMIT],
            audio=None,
            tts_error="skipped_invalid_signal",
            input_error=input_error,
        )
        print("Summary written: status=NOT_ISSUED; forecast_status=NOT_ISSUED")
        return

    prompt = (
        "Summarize the observed fields in this XRP signal in two short sentences and "
        "three brief bullets. Use only the supplied fields. Do not predict price, infer "
        "predictive validity, give a direction, or recommend a trade. State that this is "
        "a summary only and not a forecast.\n\n"
        + json.dumps(signal, indent=2, sort_keys=True)
    )
    summary = chat(prompt)
    provider_error_category = LAST_PROVIDER_ERROR_CATEGORY
    model_available = bool(summary)
    fallback_used = not model_available
    status = "SUMMARY_ONLY_NOT_A_FORECAST" if model_available else "SUMMARY_FALLBACK_NOT_A_FORECAST"
    if not summary:
        summary = fallback_summary(signal)

    spoken = ""
    speech_error_category = None
    tts_error = None
    audio = None
    if model_available:
        spoken = chat(
            "Write one neutral spoken sentence under 130 characters. Do not give a direction, "
            "price target, or trade recommendation. State that this is not a forecast. "
            "Reply with the sentence only.\n\n" + summary,
            160,
        )
        speech_error_category = LAST_PROVIDER_ERROR_CATEGORY
    if not spoken or len(spoken) > 140:
        spoken = fallback_line(signal)
        if model_available and not speech_error_category:
            speech_error_category = "invalid_or_empty_compression"
    line = f"{spoken} {DISCLAIMER}"[:TTS_LIMIT]

    # Do not spend extra quota on TTS after a model/provider failure.
    if model_available and provider_error_category is None and speech_error_category is None:
        audio, tts_error = speak(line)
        if tts_error:
            speech_error_category = classify_provider_error(tts_error)
    else:
        tts_error = "skipped_provider_unavailable"

    write_summary_artifact(
        signal, summary,
        status=status,
        model_available=model_available,
        fallback_used=fallback_used,
        provider_error_category=provider_error_category,
        speech_error_category=speech_error_category,
        spoken_line=line,
        audio=audio,
        tts_error=tts_error,
    )
    print(f"Summary written: status={status}; forecast_status=NOT_ISSUED")


if __name__ == "__main__":
    main()
