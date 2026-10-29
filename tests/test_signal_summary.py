import json

from scripts import signal_summary


def _prepare(monkeypatch, tmp_path, signal):
    signal_path = tmp_path / "latest_signal.json"
    summary_path = tmp_path / "latest_signal_summary.json"
    signal_path.write_text(json.dumps(signal), encoding="utf-8")
    monkeypatch.setattr(signal_summary, "SIGNAL_FILE", signal_path)
    monkeypatch.setattr(signal_summary, "SUMMARY_FILE", summary_path)
    monkeypatch.setattr(signal_summary, "AUDIO_DIR", tmp_path / "audio")
    monkeypatch.setattr(signal_summary, "AUDIO_FILE", tmp_path / "audio" / "summary.wav")
    monkeypatch.setattr(signal_summary, "KEY", "test-key")
    return summary_path


def test_quota_429_writes_deterministic_fallback_without_more_provider_calls(monkeypatch, tmp_path):
    summary_path = _prepare(monkeypatch, tmp_path, {
        "score": 0.21, "news_entries": 4, "confidence": 0.91,
        "sentiment": "bullish", "forecast": "rising",
        "catalysts": ["unverified catalyst"],
    })
    calls = []

    def fake_post(url, payload, timeout):
        calls.append(url)
        return None, "HTTP 429"

    monkeypatch.setattr(signal_summary, "post", fake_post)
    signal_summary.main()
    artifact = json.loads(summary_path.read_text(encoding="utf-8"))

    assert len(calls) == 1
    assert artifact["model_available"] is False
    assert artifact["fallback_used"] is True
    assert artifact["provider_error_category"] == "quota_exceeded"
    assert "score=0.21" in artifact["summary"]
    assert "news_entries=4" in artifact["summary"]
    assert "confidence" not in artifact["summary"].lower()
    assert "bullish" not in artifact["summary"].lower()
    assert "forecast" not in artifact["summary"].lower()
    assert "catalyst" not in artifact["summary"].lower()
    assert artifact["audio"] is None
    assert artifact["tts_error"] == "skipped_provider_unavailable"


def test_malformed_provider_response_falls_back_and_writes_artifact(monkeypatch, tmp_path):
    summary_path = _prepare(monkeypatch, tmp_path, {"score": 0.05})
    monkeypatch.setattr(signal_summary, "post", lambda *args, **kwargs: (b"not-json", None))

    signal_summary.main()
    artifact = json.loads(summary_path.read_text(encoding="utf-8"))

    assert artifact["model_available"] is False
    assert artifact["fallback_used"] is True
    assert artifact["provider_error_category"] == "malformed_response"
    assert "score=0.05" in artifact["summary"]
    assert artifact["audio"] is None


def test_missing_api_key_still_produces_safe_artifact(monkeypatch, tmp_path):
    summary_path = _prepare(monkeypatch, tmp_path, {"news_entries": 2})
    monkeypatch.setattr(signal_summary, "KEY", "")

    signal_summary.main()
    artifact = json.loads(summary_path.read_text(encoding="utf-8"))

    assert artifact["model_available"] is False
    assert artifact["fallback_used"] is True
    assert artifact["provider_error_category"] == "missing_api_key"
    assert "news_entries=2" in artifact["summary"]


def test_tts_failure_is_nonfatal_and_does_not_reference_stale_audio(monkeypatch, tmp_path):
    summary_path = _prepare(monkeypatch, tmp_path, {"score": 0.4})
    responses = iter(["A source-grounded summary.", "A short spoken line."])

    def fake_chat(prompt, max_tokens=400):
        signal_summary.LAST_PROVIDER_ERROR_CATEGORY = None
        return next(responses)

    monkeypatch.setattr(signal_summary, "chat", fake_chat)
    monkeypatch.setattr(signal_summary, "speak", lambda text: (None, "quota_exceeded"))

    signal_summary.main()
    artifact = json.loads(summary_path.read_text(encoding="utf-8"))

    assert artifact["summary"] == "A source-grounded summary."
    assert artifact["audio"] is None
    assert artifact["tts_error"] == "quota_exceeded"
    assert artifact["speech_error_category"] == "quota_exceeded"
