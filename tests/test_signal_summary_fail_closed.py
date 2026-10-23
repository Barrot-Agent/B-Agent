import importlib.util
import json
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "signal_summary.py"
SPEC = importlib.util.spec_from_file_location("barrot_signal_summary", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def legacy_provider_failure_signal():
    return {
        "timestamp": "2026-10-23T13:29:05Z",
        "score": 44,
        "confidence": 0.0,
        "source": "sentiment unavailable (github_failed:missing token; groq_failed:429)+news(11)",
        "news_score": 88,
        "news_entries": 11,
    }


def test_legacy_blended_score_is_not_issued_as_forecast():
    signal = legacy_provider_failure_signal()
    assert MODULE.forecast_status(signal) == "NOT_ISSUED"
    summary = MODULE.deterministic_summary(signal, "NOT_ISSUED")
    line = MODULE.fallback_line(signal, "NOT_ISSUED")
    assert "NOT_ISSUED" in summary
    assert "no calibrated XRP price forecast" in summary
    assert "provider-failure values are not forecast evidence" in summary
    assert "Score 44" not in line
    assert "News sentiment 88" in line


def test_incomplete_forecast_contract_fails_closed():
    signal = {"forecast": {"forecast_id": "xrp-1", "target": "XRP/USD"}}
    assert MODULE.forecast_status(signal) == "NOT_ISSUED"


def test_complete_forecast_contract_can_be_recognized():
    signal = {
        "forecast": {
            "forecast_id": "xrp-test-001",
            "issued_at": "2026-10-23T13:00:00Z",
            "data_cutoff": "2026-10-23T12:55:00Z",
            "target": "XRP/USD >= 1.30",
            "horizon": "4h",
            "assumptions": ["test fixture only"],
            "probability": 0.62,
            "alternatives": ["price remains below threshold"],
            "model_version": "test-model",
            "feature_snapshot_ids": ["fixture-1"],
            "calibration_version": "test-calibration",
            "baseline_comparison": "test-only",
        }
    }
    assert MODULE.forecast_status(signal) == "ISSUED"


def test_summary_is_written_without_groq_key(tmp_path, monkeypatch):
    signal_path = tmp_path / "latest_signal.json"
    summary_path = tmp_path / "latest_signal_summary.json"
    signal_path.write_text(json.dumps(legacy_provider_failure_signal()), encoding="utf-8")
    monkeypatch.setattr(MODULE, "SIGNAL_FILE", signal_path)
    monkeypatch.setattr(MODULE, "SUMMARY_FILE", summary_path)
    monkeypatch.setattr(MODULE, "KEY", "")
    monkeypatch.setattr(MODULE, "speak", lambda _line: pytest.fail("TTS must be skipped without key"))

    MODULE.main()

    result = json.loads(summary_path.read_text(encoding="utf-8"))
    assert result["forecast_status"] == "NOT_ISSUED"
    assert result["source_signal_timestamp"] == "2026-10-23T13:29:05Z"
    assert "NOT ISSUED" in result["spoken_line"]
    assert result["audio"] is None
    assert "summary still written" in result["tts_error"]
