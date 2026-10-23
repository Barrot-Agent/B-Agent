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

REQUIRED_FORECAST_FIELDS = (
    "forecast_id",
    "issued_at",
    "data_cutoff",
    "target",
    "horizon",
    "assumptions",
    "probability",
    "alternatives",
    "model_version",
    "feature_snapshot_ids",
    "calibration_version",
    "baseline_comparison",
)


def forecast_status(signal):
    """Only accept a forecast with a complete, explicit, calibratable contract."""
    forecast = signal.get("forecast")
    if not isinstance(forecast, dict):
        return "NOT_ISSUED"
    for field in REQUIRED_FORECAST_FIELDS:
        value = forecast.get(field)
        if value is None or value == "" or value == [] or value == {}:
            return "NOT_ISSUED"
    try:
        probability = float(forecast["probability"])
    except (TypeError, ValueError):
        return "NOT_ISSUED"
    if not 0.0 <= probability <= 1.0:
        return "NOT_ISSUED"
    return "ISSUED"


def deterministic_summary(signal, status):
    """Build a safe summary without external providers."""
    if status == "NOT_ISSUED":
        parts = [
            "Forecast status: NOT_ISSUED.",
            "This artifact contains sentiment/news data only; no calibrated XRP price forecast is available.",
            "Do not interpret the legacy score as a directional probability.",
        ]
        news_score = signal.get("news_score")
        news_entries = signal.get("news_entries")
        if news_score is not None:
            parts.append(f"News sentiment score: {news_score}.")
        if news_entries is not None:
            parts.append(f"News entries: {news_entries}.")
        source = str(signal.get("source", ""))
        if "sentiment unavailable" in source.lower():
            parts.append("Sentiment providers were unavailable; provider-failure values are not forecast evidence.")
        return " ".join(parts)

    forecast = signal["forecast"]
    return (
        "Forecast status: ISSUED. "
        f"Forecast ID: {forecast['forecast_id']}. "
        f"Target: {forecast['target']}. Horizon: {forecast['horizon']}. "
        f"Probability: {float(forecast['probability']):.4f}. "
        f"Data cutoff: {forecast['data_cutoff']}. "
        f"Model: {forecast['model_version']}. Calibration: {forecast['calibration_version']}. "
        f"Assumptions: {forecast['assumptions']}. Alternatives: {forecast['alternatives']}."
    )


def fallback_line(signal, status=None):
    """Deterministic spoken line; never present a sentiment score as a price forecast."""
    status = status or forecast_status(signal)
    if status == "NOT_ISSUED":
        news_score = signal.get("news_score")
        news_entries = signal.get("news_entries")
        news_text = f"News sentiment {news_score}" if news_score is not None else "News sentiment unavailable"
        count_text = f" from {news_entries} entries" if news_entries is not None else ""
        return (
            "XRP forecast status NOT ISSUED. Sentiment only; no calibrated price prediction. "
            f"{news_text}{count_text}."
        )
    forecast = signal["forecast"]
    return (
        f"XRP forecast issued. Target {forecast['target']}; horizon {forecast['horizon']}; "
        f"probability {float(forecast['probability']):.2f}."
    )


def main():
    if not SIGNAL_FILE.is_file():
        sys.exit(f"{SIGNAL_FILE} not found")
    signal = json.loads(SIGNAL_FILE.read_text(encoding="utf-8"))
    status = forecast_status(signal)
    summary = deterministic_summary(signal, status)

    # LLM summarization is optional. A provider outage must not prevent a fresh,
    # explicit NOT_ISSUED summary from being written.
    if status == "ISSUED" and KEY:
        prompt = (
            "Summarize this registered forecast. Preserve its forecast status, target, "
            "horizon, probability, data cutoff, assumptions, and alternatives. Invent nothing.\\n\\n"
            + json.dumps(signal, indent=2)
        )
        generated = chat(prompt)
        if generated:
            summary = generated

    spoken = fallback_line(signal, status)
    if status == "ISSUED" and KEY:
        compressed = chat(
            "Compress this forecast into one plain spoken sentence under 130 characters. "
            "Preserve target, horizon and probability. Reply with the sentence only.\\n\\n" + summary,
            200,
        )
        compressed = " ".join(compressed.replace("*", "").split())
        if compressed and len(compressed) <= 140:
            spoken = compressed

    line = f"{spoken} {DISCLAIMER}"[:TTS_LIMIT]
    if KEY:
        audio, tts_err = speak(line)
    else:
        audio = None
        tts_err = "GROQ_API_KEY not set; TTS skipped; deterministic summary still written"

    SUMMARY_FILE.write_text(json.dumps({
        "summary": summary,
        "spoken_line": line,
        "disclaimer": DISCLAIMER,
        "audio": audio,
        "tts_error": tts_err,
        "forecast_status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_signal_timestamp": signal.get("timestamp"),
        "source_signal": signal,
    }, indent=2), encoding="utf-8")
    print(f"Summary written; forecast_status={status}; audio={'available' if audio else 'skipped/unavailable'}")

if __name__ == "__main__":
    main()
