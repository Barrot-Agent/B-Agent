#!/usr/bin/env python3
"""Create an honest, non-directional summary artifact even when providers fail."""
import json
import math
import os
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIGNAL_FILE = ROOT / "web" / "latest_signal.json"
SUMMARY_FILE = ROOT / "web" / "latest_signal_summary.json"
AUDIO_DIR = ROOT / "web" / "generated_audio"
AUDIO_FILE = AUDIO_DIR / "latest_signal_summary.wav"
KEY = os.environ.get("GROQ_API_KEY", "")
DISCLAIMER = "Not financial advice. Informational only. Do your own research."
TTS_LIMIT = 200
UNAVAILABLE_MARKERS = ("unavailable", "failed:", "missing ", "http 429", "rate limit")


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
        return None, f"HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')[:300]}"
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def chat(prompt, max_tokens=400):
    if not KEY:
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
        print(f"[chat] unavailable: {error or 'empty response'}")
        return ""
    try:
        message = json.loads(raw)["choices"][0]["message"]
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        print(f"[chat] invalid response: {type(exc).__name__}")
        return ""
    return (message.get("content") or "").strip()


def speak(text):
    if not KEY:
        return None, "skipped: GROQ_API_KEY unavailable"
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
        print(f"[tts] unavailable: {error or 'empty response'}")
        return None, error or "empty response"
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_FILE.write_bytes(raw)
    return str(AUDIO_FILE.relative_to(ROOT)), None


def usable_signal(signal):
    """Only accept well-formed numeric metadata with a nonzero confidence."""
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


def write_summary(payload):
    SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary = SUMMARY_FILE.with_suffix(SUMMARY_FILE.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    temporary.replace(SUMMARY_FILE)


def main():
    # Avoid uploading a stale tracked audio file when this run cannot create new audio.
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

    valid = usable_signal(signal)
    audio = None
    tts_error = "skipped: summary-only output"
    if not valid:
        summary = (
            "Directional forecast not issued. The signal artifact is missing, malformed, "
            "or has unavailable/invalid confidence or source data. No directional conclusion is supported."
        )
        spoken = "XRP signal unavailable; no directional forecast issued."
        status = "NOT_ISSUED"
    else:
        summary = ""
        if KEY:
            prompt = (
                "Summarize the observed fields in this XRP signal in two short sentences and "
                "three brief bullets. Use only the supplied fields. Do not predict price, "
                "infer predictive validity, give a direction, or recommend a trade. State "
                "that this is a summary only and not a forecast.\n\n"
                + json.dumps(signal, indent=2, sort_keys=True)
            )
            summary = chat(prompt)
        if summary:
            status = "SUMMARY_ONLY_NOT_A_FORECAST"
            spoken = chat(
                "Write one neutral spoken sentence under 130 characters. Do not give a "
                "direction, price target, or trade recommendation. State that this is not "
                "a forecast. Reply with the sentence only.\n\n" + summary,
                160,
            )
            spoken = " ".join(spoken.replace("*", "").split())
            if not spoken or len(spoken) > 140:
                spoken = "XRP signal summary only; no forecast issued."
            line = f"{spoken} {DISCLAIMER}"[:TTS_LIMIT]
            audio, tts_error = speak(line)
        else:
            status = "SUMMARY_FALLBACK_NOT_A_FORECAST"
            summary = (
                "The signal artifact was loaded, but model-generated summarization is unavailable. "
                "No directional forecast is issued by this workflow."
            )
            spoken = "XRP summary unavailable; no forecast issued."
            tts_error = "skipped: model summary unavailable"
    if not valid:
        line = f"{spoken} {DISCLAIMER}"[:TTS_LIMIT]

    write_summary({
        "status": status,
        "forecast_status": "NOT_ISSUED",
        "summary_only": True,
        "summary": summary,
        "spoken_line": line,
        "disclaimer": DISCLAIMER,
        "audio": audio,
        "tts_error": tts_error,
        "input_error": input_error,
        "source_signal": signal,
    })
    print(f"Summary written: status={status}; forecast_status=NOT_ISSUED")


if __name__ == "__main__":
    main()
