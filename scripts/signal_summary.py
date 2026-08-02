#!/usr/bin/env python3
"""Signal summary + Groq TTS probe. Prints real errors, never fakes output."""
import os, json, urllib.request, urllib.error

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
SIG_PATH = "web/latest_signal.json"
OUT_JSON = "web/latest_signal_summary.json"
OUT_WAV  = "web/latest_signal_summary.wav"
DISCLAIMER = ("Not financial advice. Automated output for informational "
              "purposes only. Do your own research.")

def groq_chat(prompt):
    body = json.dumps({
        "model": "openai/gpt-oss-120b",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 400, "temperature": 0.4,
    }).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {GROQ_KEY}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["choices"][0]["message"]["content"]

def groq_tts(text, model, voice):
    body = json.dumps({"model": model, "input": text,
                       "voice": voice, "response_format": "wav"}).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/audio/speech", data=body,
        headers={"Authorization": f"Bearer {GROQ_KEY}",
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.read(), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read().decode('utf-8','replace')[:400]}"
    except Exception as e:
        return None, str(e)

def main():
    if not GROQ_KEY:
        raise SystemExit("GROQ_API_KEY not set")
    with open(SIG_PATH) as f:
        signal = json.load(f)
    print("REAL SIGNAL KEYS:", list(signal.keys()))
    summary = groq_chat(
        "Write a 2-sentence plain-English summary of this trading signal, "
        "then 3 short bullets. Use ONLY the values shown. Invent nothing.\n\n"
        + json.dumps(signal, indent=2))
    audio, err = groq_tts(
        summary + " " + DISCLAIMER,
        os.environ.get("TTS_MODEL", "canopylabs/orpheus-v1-english"),
        os.environ.get("TTS_VOICE", "autumn"))
    if audio:
        with open(OUT_WAV, "wb") as f: f.write(audio)
        print(f"TTS OK: {len(audio)} bytes -> {OUT_WAV}")
    else:
        print(f"TTS FAILED (no audio written): {err}")
    with open(OUT_JSON, "w") as f:
        json.dump({"summary": summary, "disclaimer": DISCLAIMER,
                   "audio": OUT_WAV if audio else None,
                   "tts_error": err, "signal": signal}, f, indent=2)
    print("Summary written")

if __name__ == "__main__":
    main()
