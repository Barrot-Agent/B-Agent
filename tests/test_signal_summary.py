import json

from scripts import signal_summary


def _prepare(monkeypatch, tmp_path, signal):
    signal_path = tmp_path / "latest_signal.json"
    summary_path = tmp_path / "latest_signal_summary.json"
    audio_dir = tmp_path / "audio"
    audio_dir.mkdir()
    audio_path = audio_dir / "summary.wav"
    audio_path.write_bytes(b"stale audio")
    signal_path.write_text(json.dumps(signal), encoding="utf-8")
    monkeypatch.setattr(signal_summary, "SIGNAL_FILE", signal_path)
    monkeypatch.setattr(signal_summary, "SUMMARY_FILE", summary_path)
    monkeypatch.setattr(signal_summary, "AUDIO_DIR", audio_dir)
    monkeypatch.setattr(signal_summary, "AUDIO_FILE", audio_path)
    monkeypatch.setattr(signal_summary, "KEY", "test-key")
    return summary_path, signal_path, audio_path


def _valid_signal(**updates):
    signal = {"score": 0.21, "news_entries": 4, "confidence": 0.7, "source": "local_observation"}
    signal.update(updates)
    return signal


def test_quota_429_writes_deterministic_fallback_without_more_provider_calls(monkeypatch, tmp_path):
    summary_path, _, _ = _prepare(monkeypatch, tmp_path, _valid_signal(
        confidence=0.91, sentiment="bullish", forecast="rising", catalysts=["unverified catalyst"]
    ))
    calls = []

    def fake_post(url, payload, timeout):
        calls.append(url)
        return None, "HTTP 429"

    monkeypatch.setattr(signal_summary, "post", fake_post)
    signal_summary.main()
    artifact = json.loads(summary_path.read_text(encoding="utf-8"))

    assert len(calls) == 1
    assert artifact["status"] == "SUMMARY_FALLBACK_NOT_A_FORECAST"
    assert artifact["forecast_status"] == "NOT_ISSUED"
    assert artifact["summary_only"] is True
    assert artifact["model_available"] is False
    assert artifact["fallback_used"] is True
    assert artifact["provider_error_category"] == "quota_exceeded"
    assert "score=0.21" in artifact["summary"]
    assert "news_entries=4" in artifact["summary"]
    assert "confidence" not in artifact["summary"].lower()
    assert "bullish" not in artifact["summary"].lower()
    assert "forecast=rising" not in artifact["summary"].lower()
    assert "catalyst" not in artifact["summary"].lower()
    assert artifact["audio"] is None
    assert artifact["tts_error"] == "skipped_provider_unavailable"


def test_malformed_provider_response_falls_back_and_writes_artifact(monkeypatch, tmp_path):
    summary_path, _, _ = _prepare(monkeypatch, tmp_path, _valid_signal(score=0.05))
    monkeypatch.setattr(signal_summary, "post", lambda *args, **kwargs: (b"not-json", None))

    signal_summary.main()
    artifact = json.loads(summary_path.read_text(encoding="utf-8"))

    assert artifact["status"] == "SUMMARY_FALLBACK_NOT_A_FORECAST"
    assert artifact["model_available"] is False
    assert artifact["fallback_used"] is True
    assert artifact["provider_error_category"] == "malformed_response"
    assert "score=0.05" in artifact["summary"]
    assert artifact["audio"] is None


def test_missing_api_key_still_produces_safe_artifact(monkeypatch, tmp_path):
    summary_path, _, _ = _prepare(monkeypatch, tmp_path, _valid_signal(news_entries=2))
    monkeypatch.setattr(signal_summary, "KEY", "")

    signal_summary.main()
    artifact = json.loads(summary_path.read_text(encoding="utf-8"))

    assert artifact["status"] == "SUMMARY_FALLBACK_NOT_A_FORECAST"
    assert artifact["model_available"] is False
    assert artifact["fallback_used"] is True
    assert artifact["provider_error_category"] == "missing_api_key"
    assert "news_entries=2" in artifact["summary"]


def test_tts_failure_is_nonfatal_and_does_not_reference_stale_audio(monkeypatch, tmp_path):
    summary_path, _, audio_path = _prepare(monkeypatch, tmp_path, _valid_signal(score=0.4))
    responses = iter(["A source-grounded summary.", "A short spoken line."])

    def fake_chat(prompt, max_tokens=400):
        signal_summary.LAST_PROVIDER_ERROR_CATEGORY = None
        return next(responses)

    monkeypatch.setattr(signal_summary, "chat", fake_chat)
    monkeypatch.setattr(signal_summary, "speak", lambda text: (None, "quota_exceeded"))

    signal_summary.main()
    artifact = json.loads(summary_path.read_text(encoding="utf-8"))

    assert artifact["status"] == "SUMMARY_ONLY_NOT_A_FORECAST"
    assert artifact["summary"] == "A source-grounded summary."
    assert artifact["audio"] is None
    assert artifact["tts_error"] == "quota_exceeded"
    assert artifact["speech_error_category"] == "quota_exceeded"
    assert not audio_path.exists()


def test_invalid_zero_confidence_signal_is_not_issued_without_provider(monkeypatch, tmp_path):
    summary_path, _, audio_path = _prepare(monkeypatch, tmp_path, _valid_signal(
        score=44, confidence=0.0,
        source="sentiment unavailable: missing token; provider failed: HTTP 429"
    ))
    monkeypatch.setattr(signal_summary, "chat", lambda *a, **k: (_ for _ in ()).throw(AssertionError("provider must not be called")))
    monkeypatch.setattr(signal_summary, "speak", lambda *a, **k: (_ for _ in ()).throw(AssertionError("TTS must not be called")))

    signal_summary.main()
    artifact = json.loads(summary_path.read_text(encoding="utf-8"))

    assert artifact["status"] == "NOT_ISSUED"
    assert artifact["forecast_status"] == "NOT_ISSUED"
    assert "no directional conclusion is supported" in artifact["summary"].lower()
    assert artifact["audio"] is None
    assert artifact["tts_error"] == "skipped_invalid_signal"
    assert not audio_path.exists()


def test_missing_signal_still_writes_explicit_not_issued_status(monkeypatch, tmp_path):
    summary_path, signal_path, _ = _prepare(monkeypatch, tmp_path, _valid_signal())
    signal_path.unlink()
    monkeypatch.setattr(signal_summary, "chat", lambda *a, **k: (_ for _ in ()).throw(AssertionError("provider must not be called")))

    signal_summary.main()
    artifact = json.loads(summary_path.read_text(encoding="utf-8"))

    assert artifact["status"] == "NOT_ISSUED"
    assert artifact["forecast_status"] == "NOT_ISSUED"
    assert "signal artifact is missing" in artifact["summary"].lower()
    assert artifact["input_error"].startswith("FileNotFoundError")


def test_signal_summary_workflow_is_manual_read_only_and_artifact_based():
    from pathlib import Path

    workflow = Path(".github/workflows/signal-summary.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "schedule:" not in workflow
    assert "workflow_run:" not in workflow
    assert "permissions:" in workflow
    assert "contents: read" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "retention-days: 30" in workflow
    assert "git commit" not in workflow
    assert "git push" not in workflow
    assert "contents: write" not in workflow
