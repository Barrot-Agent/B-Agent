import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "signal_summary.py"
WORKFLOW = ROOT / ".github" / "workflows" / "signal-summary.yml"
SPEC = importlib.util.spec_from_file_location("signal_summary_fallback", SCRIPT)
module = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(module)


def unavailable_signal():
    return {
        "timestamp": "2026-10-26T19:27:51Z",
        "score": 44,
        "confidence": 0.0,
        "source": "sentiment unavailable (github_failed:missing token; groq_failed:429)+news(11)",
        "news_score": 88,
        "news_entries": 11,
    }


def test_provider_failure_summary_does_not_present_overall_score_as_forecast():
    summary = module.build_fallback_summary(unavailable_signal())
    assert "model signal unavailable" in summary.lower()
    assert "displayed overall score must not be interpreted as a model forecast" in summary.lower()
    assert "news-only sentiment is 88 across 11 entries" in summary.lower()
    assert "Signal score: 44" not in summary


def test_provider_failure_spoken_line_omits_invalid_score():
    line = module.fallback_line(unavailable_signal())
    assert "unavailable" in line.lower()
    assert "not a forecast" in line.lower()
    assert "44" not in line
    assert "88" in line and "11" in line


def test_healthy_signal_fallback_explicitly_disclaims_forecast():
    signal = {"score": 63, "confidence": 0.7, "news_score": 61, "news_entries": 4, "source": "model_and_news"}
    summary = module.build_fallback_summary(signal)
    assert "Signal score: 63" in summary
    assert "not a calibrated price forecast" in summary


def test_main_writes_fallback_when_chat_is_rate_limited(tmp_path, monkeypatch):
    signal_path = tmp_path / "latest_signal.json"
    summary_path = tmp_path / "latest_signal_summary.json"
    signal_path.write_text(json.dumps(unavailable_signal()), encoding="utf-8")
    monkeypatch.setattr(module, "SIGNAL_FILE", signal_path)
    monkeypatch.setattr(module, "SUMMARY_FILE", summary_path)
    monkeypatch.setattr(module, "KEY", "test-key")
    monkeypatch.setattr(module, "chat", lambda *args, **kwargs: "")
    monkeypatch.setattr(module, "speak", lambda text: (None, "HTTP 429 rate limit"))
    module.main()
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["summary_status"] == "deterministic_fallback"
    assert payload["signal_status"] == "unavailable"
    assert "not be interpreted as a model forecast" in payload["summary"]
    assert payload["audio"] is None
    assert payload["tts_error"] == "HTTP 429 rate limit"
    assert payload["source_signal"]["score"] == 44


def test_missing_key_still_writes_summary_and_skips_provider_calls(tmp_path, monkeypatch):
    signal_path = tmp_path / "latest_signal.json"
    summary_path = tmp_path / "latest_signal_summary.json"
    signal_path.write_text(json.dumps(unavailable_signal()), encoding="utf-8")
    monkeypatch.setattr(module, "SIGNAL_FILE", signal_path)
    monkeypatch.setattr(module, "SUMMARY_FILE", summary_path)
    monkeypatch.setattr(module, "KEY", "")
    monkeypatch.setattr(module, "chat", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("chat should be skipped")))
    monkeypatch.setattr(module, "speak", lambda text: (_ for _ in ()).throw(AssertionError("TTS should be skipped")))
    module.main()
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["summary_status"] == "deterministic_fallback"
    assert payload["audio"] is None
    assert "GROQ_API_KEY not set" in payload["tts_error"]


def test_workflow_is_read_only_and_artifact_only():
    workflow = WORKFLOW.read_text(encoding="utf-8").lower()
    assert "contents: read" in workflow
    assert "upload-artifact@v4" in workflow
    assert "git push" not in workflow
    assert "git commit" not in workflow
    assert "contents: write" not in workflow
