import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "signal_summary.py"
SPEC = importlib.util.spec_from_file_location("signal_summary_under_test", SCRIPT_PATH)
signal_summary = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(signal_summary)


def test_legacy_score_zero_confidence_is_not_issued():
    legacy = {"score": 44, "confidence": 0.0, "news_entries": 11}
    assert not signal_summary.forecast_is_issuable(legacy)
    assert "NOT_ISSUED" in signal_summary.fallback_summary(legacy)
    line = signal_summary.fallback_line(legacy)
    assert "not issued" in line.lower()
    assert "Score 44" not in line
    assert "Confidence 0.0" not in line


def test_issued_forecast_requires_all_required_fields():
    partial = {
        "forecast_status": "ISSUED",
        "data_cutoff": "2026-10-23T16:00:00Z",
        "horizon": "24h",
        "target": "XRP/USD return positive",
        "assumptions": ["synchronized prices"],
        "probability": 0.61,
    }
    assert not signal_summary.forecast_is_issuable(partial)
    partial["alternatives"] = ["range-bound", "negative return"]
    assert signal_summary.forecast_is_issuable(partial)


def test_probability_must_be_finite_and_in_range():
    base = {
        "forecast_status": "ISSUED",
        "data_cutoff": "2026-10-23T16:00:00Z",
        "horizon": "24h",
        "target": "XRP/USD return positive",
        "assumptions": ["synchronized prices"],
        "alternatives": ["range-bound"],
        "probability": 1.1,
    }
    assert not signal_summary.forecast_is_issuable(base)
    base["probability"] = float("nan")
    assert not signal_summary.forecast_is_issuable(base)
    base["probability"] = 0.61
    assert signal_summary.forecast_is_isuable(base)


def test_main_fails_closed_without_metadata_and_skips_ai_and_tts(tmp_path, monkeypatch):
    signal_file = tmp_path / "latest_signal.json"
    summary_file = tmp_path / "latest_signal_summary.json"
    signal_file.write_text(
        json.dumps({"score": 44, "confidence": 0.0, "news_entries": 11}),
        encoding="utf-8",
    )
    monkeypatch.setattr(signal_summary, "SIGNAL_FILE", signal_file)
    monkeypatch.setattr(signal_summary, "SUMMARY_FILE", summary_file)
    monkeypatch.setattr(signal_summary, "KEY", "test-key")
    monkeypatch.setattr(signal_summary, "chat", lambda *_a, **_k: pytest.fail("AI call forbidden"))
    monkeypatch.setattr(signal_summary, "speak", lambda *_a, **_k: pytest.fail("TTS forbidden"))
    signal_summary.main()
    result = json.loads(summary_file.read_text(encoding="utf-8"))
    assert result["forecast_status"] == "NOT_ISSUED"
    assert result["summary_mode"] == "not_issued_fail_closed"
    assert "NOT_ISSUED" in result["summary"]
    assert "not issued" in result["spoken_line"].lower()
    assert "Score 44" not in result["spoken_line"]
    assert result["audio"] is None



def test_valid_forecast_has_deterministic_fallback_when_key_missing(tmp_path, monkeypatch):
    signal_file = tmp_path / "latest_signal.json"
    summary_file = tmp_path / "latest_signal_summary.json"
    signal = {
        "forecast_status": "ISSUED",
        "data_cutoff": "2026-10-23T16:00:00Z",
        "horizon": "24h",
        "target": "XRP/USD return positive",
        "assumptions": ["synchronized venue data"],
        "alternatives": ["flat", "negative return"],
        "probability": 0.61,
    }
    signal_file.write_text(json.dumps(signal), encoding="utf-8")
    monkeypatch.setattr(signal_summary, "SIGNAL_FILE", signal_file)
    monkeypatch.setattr(signal_summary, "SUMMARY_FILE", summary_file)
    monkeypatch.setattr(signal_summary, "KEY", "")
    monkeypatch.setattr(signal_summary, "speak", lambda *_a, **_k: pytest.fail("TTS forbidden"))
    signal_summary.main()
    result = json.loads(summary_file.read_text(encoding="utf-8"))
    assert result["forecast_status"] == "ISSUED"
    assert result["summary_mode"] == "deterministic_fallback"
    assert "61.0%" in result["summary"]
    assert result["audio"] is None
