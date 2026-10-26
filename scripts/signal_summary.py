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

def signal_is_unavailable(signal):
    """Recognize explicit provider failure/unavailable metadata without guessing from score alone."""
    status = str(signal.get("signal_status", "")).strip().lower()
    basis = str(signal.get("score_basis", "")).strip().lower()
    source = str(signal.get("source", "")).strip().lower()
    return (
        status in {"unavailable", "news_only"}
        or basis in {"unavailable_placeholder", "news_only"}
        or "unavailable" in source
        or "provider_failed" in source
        or "provider failure" in source
        or "failed:" in source
    )


def build_fallback_summary(signal):
    """Create a deterministic summary; never present unavailable sentiment as a forecast."""
    news_score = signal.get("news_score")
    news_entries = signal.get("news_entries")
    if signal_is_unavailable(signal):
        parts = [
            "XRP model signal unavailable because a required sentiment provider did not return a valid result.",
            "The displayed overall score must not be interpreted as a model forecast.",
        ]
        if news_score is not None and news_entries is not None:
            parts.append(
                f"Separate news-only sentiment is {news_score} across {news_entries} entries; it is not a calibrated price-direction probability."
            )
        else:
            parts.append("No valid directional forecast is available from this record.")
        return " ".join(parts)

    score = signal.get("score")
    confidence = signal.get("confidence")
    parts = ["Deterministic XRP signal summary."]
    if score is not None:
        parts.append(f"Signal score: {score}.")
    if confidence is not None:
        parts.append(f"Reported confidence: {confidence}.")
    if news_score is not None and news_entries is not None:
        parts.append(f"News sentiment: {news_score} across {news_entries} entries.")
    parts.append("This indicator is not a calibrated price forecast.")
    return " ".join(parts)


def fallback_line(signal):
    """Build a short spoken line without turning failed-provider scores into forecasts."""
    if signal_is_unavailable(signal):
        line = "XRP model signal unavailable; the displayed score is not a forecast."
        news_score = signal.get("news_score")
        news_entries = signal.get("news_entries")
        if news_score is not None and news_entries is not None:
            line += f" News-only sentiment {news_score} from {news_entries} entries."
        return line

    parts = ["XRP signal update."]
    for key, label in (("score", "Score"), ("confidence", "Confidence"), ("news_entries", "News entries")):
        if signal.get(key) is not None:
            parts.append(f"{label} {signal[key]}.")
    parts.append("This is not a calibrated price forecast.")
    return " ".join(parts)


def write_summary(payload):
    SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp_file = SUMMARY_FILE.with_suffix(SUMMARY_FILE.suffix + ".tmp")
    temp_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temp_file.replace(SUMMARY_FILE)


def main():
    if not SIGNAL_FILE.is_file():
        sys.exit(f"{SIGNAL_FILE} not found")
    try:
        signal = json.loads(SIGNAL_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        sys.exit(f"Could not read signal JSON: {type(exc).__name__}: {exc}")
    if not isinstance(signal, dict):
        sys.exit("Signal JSON must be an object")

    print("SIGNAL KEYS:", list(signal.keys()))
    summary = ""
    summary_status = "deterministic_fallback"
    if KEY and not signal_is_unavailable(signal):
        prompt = (
            "Summarize this XRP signal in 2 sentences, then 3 short bullets. "
            "Use ONLY the values shown. Invent nothing. State clearly that this is not a calibrated price forecast.\n\n"
            + json.dumps(signal, indent=2)
        )
        summary = chat(prompt)
        if summary:
            summary_status = "model_generated"

    if not summary:
        summary = build_fallback_summary(signal)
        print("[summary] using deterministic fallback")

    spoken = ""
    if summary_status == "model_generated":
        spoken = chat(
            "Compress to ONE spoken sentence under 130 characters. Plain words only; no markdown, no asterisks, no raw timestamps. Reply with the sentence and nothing else.\n\n"
            + summary,
            500,
        )
        spoken = " ".join(spoken.replace("*", "").split())
        if not spoken or len(spoken) > 140:
            spoken = ""
    if not spoken:
        spoken = fallback_line(signal)

    line = f"{spoken} {DISCLAIMER}"[:TTS_LIMIT]
    audio = None
    if KEY:
        audio, tts_error = speak(line)
    else:
        tts_error = "GROQ_API_KEY not set; TTS skipped"
        print(f"[tts] skipped: {tts_error}")

    payload = {
        "summary": summary,
        "summary_status": summary_status,
        "signal_status": signal.get("signal_status") or ("unavailable" if signal_is_unavailable(signal) else "unspecified"),
        "spoken_line": line,
        "disclaimer": DISCLAIMER,
        "audio": audio,
        "tts_error": tts_error,
        "source_signal": signal,
    }
    write_summary(payload)
    print(f"Summary written ({summary_status})")

if __name__ == "__main__":
    main()
