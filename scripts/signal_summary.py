#!/usr/bin/env python3
"""Resilient signal summary with deterministic fallback when Groq is unavailable."""
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

def fallback_summary(signal):
    """Build a factual summary using only fields already present in the signal."""
    lines = ["Deterministic XRP signal summary (AI summary unavailable)."]
    signal_text = signal.get("signal_text")
    if isinstance(signal_text, str) and signal_text.strip():
        lines.append(f"Signal text: {signal_text.strip()}")
    fields = (
        ("score", "Score"),
        ("confidence", "Confidence"),
        ("news_entries", "News entries"),
        ("news_score", "News score"),
        ("source", "Source"),
        ("timestamp", "Timestamp"),
    )
    for key, label in fields:
        value = signal.get(key)
        if value is not None and value != "":
            lines.append(f"- {label}: {value}")
    return "\n".join(lines)

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

def main():
    if not SIGNAL_FILE.is_file():
        sys.exit(f"{SIGNAL_FILE} not found")
    signal = json.loads(SIGNAL_FILE.read_text())
    print("SIGNAL KEYS:", list(signal.keys()))
    base = ("Summarize this XRP signal in 2 sentences, then 3 short bullets. "
            "Use ONLY the values shown. Invent nothing.\n\n"
            + json.dumps(signal, indent=2))

    summary = chat(base) if KEY else ""
    used_fallback = not bool(summary)
    if used_fallback:
        summary = fallback_summary(signal)
        print("[summary] using deterministic fallback; AI summary unavailable")

    if KEY and not used_fallback:
        spoken = chat("Compress to ONE spoken sentence under 130 characters, "
                      "Plain words only: no markdown, no asterisks, no raw timestamps. Reply with the sentence and nothing else.\n\n" + summary, 500)
        print(f"[compress] raw: {spoken!r}")
        spoken = " ".join(spoken.replace("*", "").split())
    else:
        spoken = ""

    if not spoken or len(spoken) > 140:
        spoken = fallback_line(signal)
        print(f"[compress] using deterministic fallback: {spoken}")

    line = f"{spoken} {DISCLAIMER}"[:TTS_LIMIT]
    print(f"[tts] input ({len(line)} chars): {line}")
    if KEY:
        audio, tts_err = speak(line)
    else:
        audio = None
        tts_err = "GROQ_API_KEY not set; TTS skipped"
        print(f"[tts] skipped: {tts_err}")

    SUMMARY_FILE.write_text(json.dumps({
        "summary": summary, "summary_mode": "deterministic_fallback" if used_fallback else "groq",
        "spoken_line": line, "disclaimer": DISCLAIMER,
        "audio": audio, "tts_error": tts_err,
        "source_signal": signal}, indent=2))
    print("Summary written")

if __name__ == "__main__":
    main()
