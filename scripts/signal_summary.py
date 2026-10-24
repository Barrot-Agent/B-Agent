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

def _needs_source_fallback(signal):
    """Avoid model/TTS calls when the upstream signal is not model-backed."""
    status = str(signal.get("signal_status", "")).lower()
    source = str(signal.get("source", "")).lower()
    if status in {"unavailable", "news_only"}:
        return True
    return not status and "sentiment unavailable" in source


def _source_unavailable_payload(signal):
    """Build a deterministic summary that cannot turn missing sentiment into a market call."""
    status = str(signal.get("signal_status") or "legacy_provider_unavailable").lower()
    if status == "news_only":
        news_score = signal.get("news_score")
        news_entries = signal.get("news_entries", 0)
        summary = (
            f"Model sentiment is unavailable. News-only sentiment score {news_score} "
            f"from {news_entries} entries is not a calibrated XRP price forecast."
        )
    elif status == "unavailable":
        summary = (
            "XRP signal unavailable because model sentiment and news inputs are unavailable. "
            "The compatibility score is not a market signal."
        )
    else:
        summary = (
            "XRP model sentiment is unavailable because the configured providers failed. "
            "The legacy score must not be interpreted as a bearish signal."
        )
    return {
        "summary": summary,
        "spoken_line": "XRP model signal unavailable; no directional forecast issued.",
        "disclaimer": DISCLAIMER,
        "audio": None,
        "tts_error": "skipped_source_signal_unavailable",
        "summary_method": "deterministic_source_unavailable",
        "source_signal_status": status,
        "source_signal": signal,
    }


def main():
    if not SIGNAL_FILE.is_file():
        sys.exit(f"{SIGNAL_FILE} not found")
    signal = json.loads(SIGNAL_FILE.read_text())
    if _needs_source_fallback(signal):
        SUMMARY_FILE.write_text(json.dumps(_source_unavailable_payload(signal), indent=2))
        print("Source signal is not model-backed; deterministic summary written, model/TTS skipped.")
        return
    if not KEY:
        sys.exit("GROQ_API_KEY not set")
    print("SIGNAL KEYS:", list(signal.keys()))
    base = ("Summarize this XRP signal in 2 sentences, then 3 short bullets. "
            "Use ONLY the values shown. Invent nothing.\n\n"
            + json.dumps(signal, indent=2))
    summary = chat(base)
    if not summary:
        sys.exit("Summary generation failed; nothing written.")
    spoken = chat("Compress to ONE spoken sentence under 130 characters, "
                  "Plain words only: no markdown, no asterisks, no raw timestamps. Reply with the sentence and nothing else.\n\n" + summary, 500)
    print(f"[compress] raw: {spoken!r}")
    spoken = " ".join(spoken.replace("*", "").split())
    if not spoken or len(spoken) > 140:
        spoken = fallback_line(signal)
        print(f"[compress] using deterministic fallback: {spoken}")
    line = f"{spoken} {DISCLAIMER}"[:TTS_LIMIT]
    print(f"[tts] input ({len(line)} chars): {line}")
    audio, tts_err = speak(line)
    SUMMARY_FILE.write_text(json.dumps({
        "summary": summary, "spoken_line": line, "disclaimer": DISCLAIMER,
        "audio": audio, "tts_error": tts_err,
        "source_signal": signal}, indent=2))
    print("Summary written")

if __name__ == "__main__":
    main()
