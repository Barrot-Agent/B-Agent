import json

from scripts import signal_summary


def test_zero_confidence_signal_is_blocked_from_model_interpretation():
    signal = {"score": 44, "confidence": 0, "source": "provider unavailable"}
    assert signal_summary.signal_requires_fallback(signal) is True
    summary = signal_summary.deterministic_summary(signal)
    assert "No directional forecast issued" in summary
    assert "Reported score: 44." in summary


def test_missing_confidence_fails_closed():
    assert signal_summary.signal_requires_fallback({"score": 50}) is True


def test_provider_failure_forces_deterministic_fallback():
    signal = {"score": 55, "confidence": 0.7, "source": "sentiment unavailable: HTTP 429"}
    assert signal_summary.signal_requires_fallback(signal) is True


def test_valid_signal_is_not_marked_invalid_only_by_positive_score():
    signal = {"score": 55, "confidence": 0.7, "source": "model"}
    assert signal_summary.signal_requires_fallback(signal) is False


def test_main_persists_summary_when_provider_key_is_missing(monkeypatch, tmp_path):
    signal_file = tmp_path / "latest_signal.json"
    summary_file = tmp_path / "latest_signal_summary.json"
    audio_dir = tmp_path / "generated_audio"
    audio_file = audio_dir / "latest_signal_summary.wav"
    signal_file.write_text(
        json.dumps(
            {
                "timestamp": "2026-10-27T08:38:05Z",
                "score": 44,
                "confidence": 0,
                "news_score": 88,
                "news_entries": 11,
                "source": "sentiment unavailable; Groq HTTP 429",
            }
        )
    )
    monkeypatch.setattr(signal_summary, "SIGNAL_FILE", signal_file)
    monkeypatch.setattr(signal_summary, "SUMMARY_FILE", summary_file)
    monkeypatch.setattr(signal_summary, "AUDIO_DIR", audio_dir)
    monkeypatch.setattr(signal_summary, "AUDIO_FILE", audio_file)
    monkeypatch.setattr(signal_summary, "KEY", "")

    signal_summary.main()

    result = json.loads(summary_file.read_text())
    assert result["summary_mode"] == "DETERMINISTIC_NOT_ISSUED"
    assert result["forecast_status"] == "NOT_ISSUED"
    assert "No directional forecast issued" in result["summary"]
    assert result["audio"] is None
    assert result["tts_error"] == "GROQ_API_KEY not set"
    assert not audio_file.exists()
