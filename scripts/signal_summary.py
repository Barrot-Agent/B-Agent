#!/usr/bin/env python3
"""Signal summary + Groq Orpheus TTS. Real keys only, real errors surfaced."""
import json, math, os, sys, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIGNAL_FILE = ROOT / "web" / "latest_signal.json"
SUMMARY_FILE = ROOT / "web" / "latest_signal_summary.json"
AUDIO_DIR = ROOT / "web" / "generated_audio"
AUDIO_FILE = AUDIO_DIR / "latest_signal_summary.wav"
KEY = os.environ.get("GROQ_API_KEY", "")
DISCLAIMER = "Not financial advice. Informational only. Do your own research."
TTS_LIMIT = 200

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
    if not KEY:
        print("[chat] unavailable: GROQ_API_KEY not set")
        return ""
    raw, err = post("https://api.groq.com/openai/v1/chat/completions",
                    {"model": "openai/gpt-oss-120b",
                     "messages": [{"role": "user", "content": prompt}],
                     "max_tokens": max_tokens, "temperature": 0.4,
                     "reasoning_effort": "low"}, 60)
    if err:
        print(f"[chat] FAILED: {err}")
        return ""
    msg = json.loads(raw)["choices"][0]["message"]
    out = (msg.get("content") or "").strip()
    if not out:
        print(f"[chat] content empty; message keys: {list(msg.keys())}")
        out = (msg.get("reasoning") or "").strip()
        if out:
            print("[chat] recovered from reasoning field")
    return out

def speak(text):
    if not KEY:
        return None, "GROQ_API_KEY not set"
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

def signal_requires_fallback(signal):
    """Reject invalid confidence and provider failures before model interpretation."""
    try:
        confidence = float(signal.get("confidence"))
    except (TypeError, ValueError):
        return True
    # NaN passes ordinary <= comparisons, and infinities/out-of-range values
    # are not valid probabilities. Fail closed before any model summary call.
    if not math.isfinite(confidence) or not 0 < confidence <= 1:
        return True
    source = str(signal.get("source", "")).lower()
    unavailable_markers = ("unavailable", "failed", "rate limit", "http 429")
    return any(marker in source for marker in unavailable_markers)


def deterministic_summary(signal, forecast_blocked=None):
    """Report observed fields only; never invent direction or imply forecast validity."""
    if forecast_blocked is None:
        forecast_blocked = signal_requires_fallback(signal)
    if forecast_blocked:
        parts = [
            "No directional forecast issued: signal confidence is zero or required model sentiment is unavailable."
        ]
    else:
        parts = [
            "Model-generated summary unavailable. This deterministic fallback reports observed fields only and adds no directional conclusion."
        ]
    for key, label in (
        ("timestamp", "Data timestamp"),
        ("score", "Reported score"),
        ("confidence", "Reported confidence"),
        ("news_score", "Reported news score"),
        ("news_entries", "News entries"),
    ):
        value = signal.get(key)
        if value is not None:
            parts.append(f"{label}: {value}.")
    parts.append("Summary generation status is not a forecast-performance validation.")
    return " ".join(parts)


def fallback_line(signal):
    """Deterministic spoken line from real signal fields only."""
    score = signal.get("score")
    conf = signal.get("confidence")
    n = signal.get("news_entries")
    bits = ["XRP signal update."]
    if signal_requires_fallback(signal):
        bits.append("No directional forecast issued.")
    if score is not None:
        bits.append(f"Score {score}.")
    if conf is not None:
        bits.append(f"Confidence {conf}.")
    if n is not None:
        bits.append(f"Based on {n} news entries.")
    return " ".join(bits)


def main():
    if not SIGNAL_FILE.is_file():
        sys.exit(f"{SIGNAL_FILE} not found")
    signal = json.loads(SIGNAL_FILE.read_text())
    print("SIGNAL KEYS:", list(signal.keys()))
    base = (
        "Summarize this XRP signal in 2 sentences, then 3 short bullets. "
        "Use ONLY the values shown. Invent nothing.\n\n"
        + json.dumps(signal, indent=2)
    )

    if signal_requires_fallback(signal):
        summary = deterministic_summary(signal, forecast_blocked=True)
        summary_mode = "DETERMINISTIC_NOT_ISSUED"
        print("[summary] invalid/unavailable signal; using deterministic no-forecast fallback")
    else:
        summary = chat(base)
        if summary:
            summary_mode = "MODEL_SUMMARY"
        else:
            summary = deterministic_summary(signal, forecast_blocked=False)
            summary_mode = "DETERMINISTIC_PROVIDER_FALLBACK"
            print("[summary] model provider unavailable; using deterministic fallback")

    if summary_mode == "MODEL_SUMMARY":
        spoken = chat(
            "Compress to ONE spoken sentence under 130 characters, "
            "Plain words only: no markdown, no asterisks, no raw timestamps. "
            "Reply with the sentence and nothing else.\n\n" + summary,
            500,
        )
        print(f"[compress] raw: {spoken!r}")
        spoken = " ".join(spoken.replace("*", "").split())
        if not spoken or len(spoken) > 140:
            spoken = fallback_line(signal)
            print(f"[compress] using deterministic fallback: {spoken}")
    else:
        spoken = fallback_line(signal)

    line = f"{spoken} {DISCLAIMER}"[:TTS_LIMIT]
    print(f"[tts] input ({len(line)} chars): {line}")
    audio, tts_err = speak(line)
    SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_FILE.write_text(
        json.dumps(
            {
                "summary": summary,
                "summary_mode": summary_mode,
                "forecast_status": (
                    "NOT_ISSUED"
                    if summary_mode == "DETERMINISTIC_NOT_ISSUED"
                    else "SUMMARY_ONLY_NOT_A_FORECAST"
                ),
                "spoken_line": line,
                "disclaimer": DISCLAIMER,
                "audio": audio,
                "tts_error": tts_err,
                "source_signal": signal,
            },
            indent=2,
        )
    )
    print(f"Summary written ({summary_mode})")


if __name__ == "__main__":
    main()
