import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "signal_summary.py"
SPEC = importlib.util.spec_from_file_location("signal_summary", SCRIPT)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def test_provider_failure_does_not_repeat_contaminated_combined_score():
    signal = {
        "score": 44,
        "confidence": 0.0,
        "source": "sentiment unavailable (github_failed:missing token; groq_failed:429)+news(11)",
        "news_score": 88,
        "news_entries": 11,
    }
    summary = module.fallback_summary(signal)
    line = module.fallback_line(signal)
    assert "news-only sentiment score 88" in summary
    assert "combined compatibility score" in summary
    assert "44" not in summary
    assert "news-only score 88" in line
    assert "Score 44" not in line


def test_unavailable_without_news_never_invents_a_score():
    signal = {"signal_status": "unavailable", "score": 50, "confidence": 0.0}
    assert "No directional forecast" in module.fallback_summary(signal)
    assert "50" not in module.fallback_summary(signal)
    assert "unavailable" in module.fallback_line(signal).lower()


def test_healthy_signal_fallback_uses_available_fields():
    signal = {"score": 63, "confidence": 0.72, "source": "github_model+groq_model"}
    summary = module.fallback_summary(signal)
    assert "score: 63" in summary
    assert "0.72" in summary
    assert "not a calibrated price prediction" in summary.lower()


def test_main_writes_deterministic_summary_without_provider_key(tmp_path, monkeypatch):
    signal_path = tmp_path / "web" / "latest_signal.json"
    summary_path = tmp_path / "web" / "latest_signal_summary.json"
    signal_path.parent.mkdir(parents=True)
    signal_path.write_text(json.dumps({
        "score": 44,
        "confidence": 0.0,
        "source": "sentiment unavailable (github_failed:missing token; groq_failed:429)+news(11)",
        "news_score": 88,
        "news_entries": 11,
    }))
    monkeypatch.setattr(module, "SIGNAL_FILE", signal_path)
    monkeypatch.setattr(module, "SUMMARY_FILE", summary_path)
    monkeypatch.setattr(module, "AUDIO_DIR", tmp_path / "web" / "generated_audio")
    monkeypatch.setattr(module, "KEY", "")
    monkeypatch.setattr(module, "chat", lambda *a, **k: (_ for _ in ()).throw(AssertionError("chat must not be called")))
    monkeypatch.setattr(module, "speak", lambda *a, **k: (_ for _ in ()).throw(AssertionError("TTS must not be called")))

    module.main()
    result = json.loads(summary_path.read_text())
    assert result["summary_method"] == "deterministic_fallback"
    assert result["model_available"] is False
    assert "news-only sentiment score 88" in result["summary"]
    assert result["audio"] is None


def test_main_writes_fallback_after_rate_limit(tmp_path, monkeypatch):
    signal_path = tmp_path / "web" / "latest_signal.json"
    summary_path = tmp_path / "web" / "latest_signal_summary.json"
    signal_path.parent.mkdir(parents=True)
    signal_path.write_text(json.dumps({
        "score": 44, "confidence": 0.0,
        "source": "sentiment unavailable (groq_failed:429)+news(11)",
        "news_score": 88, "news_entries": 11,
    }))
    monkeypatch.setattr(module, "SIGNAL_FILE", signal_path)
    monkeypatch.setattr(module, "SUMMARY_FILE", summary_path)
    monkeypatch.setattr(module, "AUDIO_DIR", tmp_path / "web" / "generated_audio")
    monkeypatch.setattr(module, "KEY", "test-key")
    monkeypatch.setattr(module, "LAST_CHAT_ERROR", "HTTP 429: rate limit")
    monkeypatch.setattr(module, "chat", lambda *a, **k: "")
    monkeypatch.setattr(module, "speak", lambda *a, **k: (_ for _ in ()).throw(AssertionError("TTS must be skipped")))

    module.main()
    result = json.loads(summary_path.read_text())
    assert result["summary_method"] == "deterministic_fallback"
    assert result["provider_error"] == "HTTP 429 rate limited"
    assert "news-only sentiment score 88" in result["summary"]
    assert result["audio"] is None

def test_main_bypasses_summary_model_when_signal_model_is_unavailable(tmp_path, monkeypatch):
    signal_path = tmp_path / "web" / "latest_signal.json"
    summary_path = tmp_path / "web" / "latest_signal_summary.json"
    signal_path.parent.mkdir(parents=True)
    signal_path.write_text(json.dumps({
        "score": 44,
        "confidence": 0.0,
        "source": "sentiment unavailable (github_failed:missing token; groq_failed:429)+news(11)",
        "news_score": 88,
        "news_entries": 11,
    }))
    monkeypatch.setattr(module, "SIGNAL_FILE", signal_path)
    monkeypatch.setattr(module, "SUMMARY_FILE", summary_path)
    monkeypatch.setattr(module, "AUDIO_DIR", tmp_path / "web" / "generated_audio")
    monkeypatch.setattr(module, "KEY", "test-key")
    monkeypatch.setattr(module, "LAST_CHAT_ERROR", None)
    monkeypatch.setattr(module, "chat", lambda *a, **k: (_ for _ in ()).throw(AssertionError("summarizer must not see contaminated score")))
    monkeypatch.setattr(module, "speak", lambda *a, **k: (_ for _ in ()).throw(AssertionError("TTS must be skipped")))

    module.main()
    result = json.loads(summary_path.read_text())
    assert result["summary_method"] == "deterministic_fallback"
    assert result["signal_model_available"] is False
    assert result["summary_model_available"] is False
    assert "news-only sentiment score 88" in result["summary"]
    assert "44" not in result["summary"]
    assert result["audio"] is None
