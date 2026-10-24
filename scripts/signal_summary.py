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

def deterministic_summary(signal):
    """Create a factual summary from stored fields when the language model is unavailable."""
    basis = str(signal.get("score_basis", "legacy_unverified"))
    score = signal.get("score")
    confidence = signal.get("confidence")
    news_score = signal.get("news_score")
    news_entries = signal.get("news_entries")
    source = str(signal.get("source", "unknown"))

    if basis == "news_only":
        lead = (
            f"The sentiment provider was unavailable. Score {score} is a news-only sentiment "
            f"score based on {news_entries} entries; model confidence is {confidence}. "
            "This is not a price forecast."
        )
    elif basis == "unavailable_neutral_placeholder":
        lead = (
            "Sentiment generation was unavailable and no usable news score was present. "
            "Score 50 is a neutral placeholder, not a market signal or price forecast."
        )
    elif basis == "model_and_news_blend":
        lead = (
            f"Score {score} blends model sentiment with news score {news_score} across "
            f"{news_entries} entries. Confidence is {confidence}; this is not a price forecast."
        )
    elif basis == "model_only":
        lead = (
            f"The model-only sentiment score is {score}, with confidence {confidence}. "
            "No usable news score was available; this is not a price forecast."
        )
    elif source.startswith("sentiment unavailable"):
        lead = (
            "Sentiment generation is unavailable. No directional conclusion is supported "
            "by this artifact; this is not a price forecast."
        )
    else:
        lead = (
            f"The recorded sentiment score is {score} with confidence {confidence}. "
            "Its score basis is not labeled, so treat it as unverified sentiment, not a price forecast."
        )

    bullets = [
        f"Score basis: {basis}",
        f"News score: {news_score if news_score is not None else 'unavailable'}",
        f"News entries: {news_entries if news_entries is not None else 'unavailable'}",
    ]
    return lead + "\n\n" + "\n".join(f"- {item}" for item in bullets)


def fallback_line(signal):
    """Deterministic spoken line from real signal fields only."""
    score = signal.get("score")
    confidence = signal.get("confidence")
    basis = signal.get("score_basis", "legacy_unverified")
    news_entries = signal.get("news_entries")

    if basis == "news_only":
        return f"XRP news-only sentiment score {score}. Model unavailable; confidence {confidence}. Not a price forecast."
    if basis == "unavailable_neutral_placeholder":
        return "XRP signal unavailable. Neutral placeholder only. No price forecast."
    if basis == "legacy_unverified" and str(signal.get("source", "")).startswith("sentiment unavailable"):
        return "XRP sentiment provider unavailable. No directional signal. Not a price forecast."

    bits = ["XRP sentiment update."]
    if score is not None:
        bits.append(f"Score {score}.")
    if confidence is not None:
        bits.append(f"Confidence {confidence}.")
    if news_entries is not None:
        bits.append(f"Based on {news_entries} news entries.")
    bits.append("Not a price forecast.")
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

    summary = ""
    summary_source = "deterministic_fallback"
    if KEY:
        summary = chat(base)
        if summary:
            summary_source = "groq"
    if not summary:
        summary = deterministic_summary(signal)

    spoken = ""
    if summary_source == "groq":
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

    line = f"{spoken} {DISCLAIMER}"[:TTS_LIMIT]
    print(f"[tts] input ({len(line)} chars): {line}")
    if KEY:
        audio, tts_err = speak(line)
    else:
        audio, tts_err = None, "GROQ_API_KEY not set; TTS skipped"

    SUMMARY_FILE.write_text(json.dumps({
        "summary": summary,
        "summary_source": summary_source,
        "deterministic_fallback_used": summary_source != "groq",
        "spoken_line": line,
        "disclaimer": DISCLAIMER,
        "audio": audio,
        "tts_error": tts_err,
        "source_signal": signal,
    }, indent=2))
    print("Summary written")

if __name__ == "__main__":
    main()
