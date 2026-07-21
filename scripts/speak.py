#!/usr/bin/env python3
"""BARROT-Ω SPEAK — real TTS via Groq Orpheus. Fails loudly, never fakes audio."""
import os, sys, json, subprocess
KEY = os.environ.get("GROQ_API_KEY", "")
MODEL = os.environ.get("TTS_MODEL", "canopylabs/orpheus-v1-english")
VOICE = os.environ.get("TTS_VOICE", "autumn")
def _run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr
def speak(text, out_path="barrot_voice.wav"):
    if not KEY:
        raise RuntimeError("GROQ_API_KEY not set")
    payload = json.dumps({"model": MODEL, "input": text[:2000], "voice": VOICE, "response_format": "wav"})
    _, out, _ = _run(f'curl -s -X POST https://api.groq.com/openai/v1/audio/speech -H "Authorization: Bearer {KEY}" -H "Content-Type: application/json" -d \'{payload}\' -o {out_path} -w \'%{{http_code}}\'')
    http = out.strip()[-3:]
    if http != "200":
        body = open(out_path).read()[:500] if os.path.exists(out_path) else ""
        try:
            err = json.loads(body).get("error", {})
            if err.get("code") == "model_terms_required":
                model_slug = MODEL.replace("/", "%2F")
                raise RuntimeError(
                    f"Model '{MODEL}' requires terms acceptance.\n"
                    f"ACTION REQUIRED: Have the Groq org admin accept terms at "
                    f"https://console.groq.com/playground?model={model_slug}"
                )
        except (json.JSONDecodeError, AttributeError):
            pass
        raise RuntimeError(f"TTS HTTP {http}: {body[:300]}")
    size = os.path.getsize(out_path) if os.path.exists(out_path) else 0
    if size < 100:
        raise RuntimeError(f"audio too small ({size}b)")
    return out_path, size
def main():
    text = os.environ.get("SPEAK_TEXT", "") or (sys.argv[1] if len(sys.argv) > 1 else "")
    if not text.strip():
        sys.exit("no text")
    path, size = speak(text)
    print(f"SPOKE: {path} ({size} bytes)")
if __name__ == "__main__":
    main()
