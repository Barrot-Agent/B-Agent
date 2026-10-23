#!/usr/bin/env python3
"""Fail-closed XRP forecast summary with deterministic provider fallback."""
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


def forecast_is_issuable(signal):
    """Require explicit status and complete prediction metadata before publishing a forecast."""
    if not isinstance(signal, dict) or signal.get("forecast_status") != "ISSUED":
        return False
    for key in ("data_cutoff", "horizon", "target"):
        if not isinstance(signal.get(key), str) or not signal[key].strip():
            return False
    for key in ("assumptions", "alternatives"):
        if not isinstance(signal.get(key), list) or not signal[key]:
            return False
    probability = signal.get("probability")
    if (
        isinstance(probability, bool)
        or not isinstance(probability, (int, float))
        or not math.isfinite(probability)
        or not 0.0 <= probability <= 1.0
    ):
        return False
    return True


def fallback_summary(signal):
    """Deterministic summary that never promotes an unissued signal into a forecast."""
    if not forecast_is_issuable(signal):
        return (
            "Forecast status: NOT_ISSUED. Required forecast status, data cutoff, horizon, "
            "target, assumptions, probability, or alternatives are missing. "
            "No directional prediction is being published."
        )
    assumptions = "; ".join(str(x) for x in signal["assumptions"])
    alternatives = "; ".join(str(x) for x in signal["alternatives"])
    return (
        "Forecast status: ISSUED (metadata gate passed; this is not a guarantee). "
        f"Target: {signal['target']}. Horizon: {signal['horizon']}. "
        f"Probability: {signal['probability']:.1%}. Data cutoff: {signal['data_cutoff']}. "
        f"Assumptions: {assumptions}. Alternatives: {alternatives}."
    )


def fallback_line(signal):
    """A short deterministic line; never speak a score as a forecast when not issued."""
    if not forecast_is_issuable(signal):
        return "XRP forecast not issued; required evidence and metadata are missing."
    return (
        f"XRP forecast for {signal['target']} over {signal['horizon']}: "
        f"probability {signal['probability']:.0%}. Data cutoff {signal['data_cutoff']}."
    )


def post(url, payload, timeout):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
            "User-Agent": "Barrot-XRP-Research/1.0",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read(), None
    except urllib.error.HTTPError as exc:
        return None, f"HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')[:500]}"
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def chat(prompt, max_tokens=400):
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
    if error:
        print(f"[chat] FAILED: {error}")
        return ""
    message = json.loads(raw)["choices"][0]["message"]
    return (message.get("content") or "").strip()


def speak(text):
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
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
    if error:
        print(f"[tts] FAILED (no audio written): {error}")
        return None, error
    AUDIO_FILE.write_bytes(raw)
    return str(AUDIO_FILE.relative_to(ROOT)), None


def write_result(signal, summary, spoken, mode, audio=None, tts_error=None):
    line = f"{spoken} {DISCLAIMER}"[:TTS_LIMIT]
    SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_FILE.write_text(
        json.dumps(
            {
                "summary": summary,
                "summary_mode": mode,
                "forecast_status": "ISSUED" if forecast_is_issuable(signal) else "NOT_ISSUED",
                "spoken_line": line,
                "disclaimer": DISCLAIMER,
                "audio": audio,
                "tts_error": tts_error,
                "source_signal": signal,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print("Summary written")


def main():
    if not SIGNAL_FILE.is_file():
        sys.exit(f"{SIGNAL_FILE} not found")
    signal = json.loads(SIGNAL_FILE.read_text(encoding="utf-8"))

    # Fail closed before any model call or TTS. Legacy score/confidence fields are not forecasts.
    if not forecast_is_issuable(signal):
        summary = fallback_summary(signal)
        write_result(
            signal,
            summary,
            fallback_line(signal),
            "not_issued_fail_closed",
            audio=None,
            tts_error="TTS skipped: no issuable forecast",
        )
        return

    prompt = (
        "Summarize this already-issued XRP forecast in two sentences and three short bullets. "
        "Use only the supplied values. Do not change the probability, target, horizon, cutoff, "
        "assumptions, or alternatives. Do not claim certainty.\n\n"
        + json.dumps(signal, indent=2)
    )
    summary = chat(prompt) if KEY else ""
    mode = "groq"
    if not summary:
        summary = fallback_summary(signal)
        mode = "deterministic_fallback"

    spoken = ""
    if KEY and mode == "groq":
        spoken = chat(
            "Compress the forecast into one plain spoken sentence under 130 characters. "
            "Preserve target, horizon and probability; no markdown or raw timestamps.\n\n" + summary,
            160,
        )
        spoken = " ".join(spoken.replace("*", "").split())
    if not spoken or len(spoken) > 140:
        spoken = fallback_line(signal)

    audio, tts_error = (None, "TTS skipped: provider key unavailable")
    if KEY:
        audio, tts_error = speak(f"{spoken} {DISCLAIMER}")
    write_result(signal, summary, spoken, mode, audio=audio, tts_error=tts_error)


if __name__ == "__main__":
    main()
