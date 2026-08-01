#!/usr/bin/env python3
"""Generate audio summary of latest XRP/BTC signal."""
import json
import os
import sys
import urllib.request
from pathlib import Path

KB_ROOT = Path(__file__).resolve().parents[1] / "ping-pongings" / "knowledge-base"
WEB_ROOT = Path(__file__).resolve().parents[1] / "web"
SIGNAL_FILE = WEB_ROOT / "latest_signal.json"
SUMMARY_FILE = WEB_ROOT / "latest_signal_summary.json"
AUDIO_DIR = WEB_ROOT / "generated_audio"

KEY = os.environ.get("GROQ_API_KEY", "")

def ask_groq(text):
    body = json.dumps({
        "model": "openai/gpt-oss-120b",
        "messages": [{"role": "user", "content": text}],
        "max_tokens": 300,
        "temperature": 0.7,
    }).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.load(resp)["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[signal_summary] Groq error: {e}")
        return ""

def speak(text):
    """Call Groq Orpheus TTS (voice: 'autumn'), return audio_url or None."""
    if not text or not KEY:
        return None
    body = json.dumps({
        "model": "canopylabs/orpheus-v1-english",
        "inputs": {
            "text": text,
            "voice": "autumn",
            "speed": 1.0,
        }
    }).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/audio/speech",
        data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            audio_data = resp.read()
            AUDIO_DIR.mkdir(parents=True, exist_ok=True)
            audio_path = AUDIO_DIR / "latest_signal_summary.mp3"
            with audio_path.open("wb") as f:
                f.write(audio_data)
            url = f"https://raw.githubusercontent.com/Barrot-Agent/B-Agent/main/web/generated_audio/latest_signal_summary.mp3"
            return url
    except Exception as e:
        print(f"[signal_summary] TTS error: {e}")
        return None

def main():
    if not SIGNAL_FILE.is_file():
        print("latest_signal.json not found")
        sys.exit(0)

    with SIGNAL_FILE.open() as f:
        signal = json.load(f)

    direction = signal.get("direction", "?").upper()
    confidence = signal.get("confidence", 0)
    reason = signal.get("reason", "No reason provided")[:200]

    summary_prompt = f"""XRP Signal: {direction} (confidence {confidence}).
Reason: {reason}

Generate a 2-sentence summary of this signal, then 3 key points as bullets.
Format: SUMMARY: [2 sentences]
POINTS:
- [point 1]
- [point 2]
- [point 3]"""

    summary_text = ask_groq(summary_prompt).strip()
    if not summary_text:
        print("Failed to generate summary")
        sys.exit(1)

    audio_url = speak(summary_text)

    result = {
        "signal": {"direction": direction, "confidence": confidence},
        "summary_text": summary_text,
        "audio_url": audio_url,
    }

    with SUMMARY_FILE.open("w") as f:
        json.dump(result, f, indent=2)
    print(f"wrote {SUMMARY_FILE}")

if __name__ == "__main__":
    main()
