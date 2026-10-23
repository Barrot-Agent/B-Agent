"""Tests for deterministic signal-summary fallback behavior."""

import importlib.util
import json
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "signal_summary.py"
SPEC = importlib.util.spec_from_file_location("signal_summary_under_test", SCRIPT_PATH)
signal_summary = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(signal_summary)


@pytest.fixture
def signal_payload():
    return {
        "timestamp": "2026-10-23T00:00:00Z",
        "signal_text": "XRP signal remains mixed.",
        "score": 0.25,
        "confidence": 0.6,
        "source": "test-fixture",
        "news_score": 2,
        "news_entries": 4,
        "generated_at_unix": 1792713600,
    }


def test_fallback_summary_uses_existing_signal_values(signal_payload):
    summary = signal_summary.fallback_summary(signal_payload)

    assert "XRP signal remains mixed." in summary
    assert "Score: 0.25" in summary
    assert "Confidence: 0.6" in summary
    assert "News entries: 4" in summary
    assert "Source: test-fixture" in summary
    assert "AI summary unavailable" in summary


def test_main_writes_summary_without_groq_key(tmp_path, monkeypatch, signal_payload):
    signal_file = tmp_path / "latest_signal.json"
    summary_file = tmp_path / "latest_signal_summary.json"
    signal_file.write_text(json.dumps(signal_payload), encoding="utf-8")
    monkeypatch.setattr(signal_summary, "SIGNAL_FILE", signal_file)
    monkeypatch.setattr(signal_summary, "SUMMARY_FILE", summary_file)
    monkeypatch.setattr(signal_summary, "KEY", "")
    monkeypatch.setattr(
        signal_summary, "speak",
        lambda _text: pytest.fail("TTS must not run without a key"),
    )

    signal_summary.main()

    result = json.loads(summary_file.read_text(encoding="utf-8"))
    assert result["summary_mode"] == "deterministic_fallback"
    assert "XRP signal remains mixed." in result["summary"]
    assert result["audio"] is None
    assert "GROQ_API_KEY not set" in result["tts_error"]


def test_main_writes_summary_when_groq_summary_fails(
    tmp_path, monkeypatch, signal_payload
):
    signal_file = tmp_path / "latest_signal.json"
    summary_file = tmp_path / "latest_signal_summary.json"
    signal_file.write_text(json.dumps(signal_payload), encoding="utf-8")
    monkeypatch.setattr(signal_summary, "SIGNAL_FILE", signal_file)
    monkeypatch.setattr(signal_summary, "SUMMARY_FILE", summary_file)
    monkeypatch.setattr(signal_summary, "KEY", "test-key")
    monkeypatch.setattr(signal_summary, "chat", lambda *_args, **_kwargs: "")
    monkeypatch.setattr(
        signal_summary, "speak", lambda _text: (None, "HTTP 429: rate limited")
    )

    signal_summary.main()

    result = json.loads(summary_file.read_text(encoding="utf-8"))
    assert result["summary_mode"] == "deterministic_fallback"
    assert result["source_signal"] == signal_payload
    assert "XRP signal remains mixed." in result["summary"]
    assert result["tts_error"] == "HTTP 429: rate limited"
