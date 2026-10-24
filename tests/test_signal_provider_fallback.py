from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load_script(relative_path: str, module_name: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "relative_path,module_name",
    [
        ("scripts/emit_signal.py", "emit_signal_fallback_test"),
        ("scripts/emit_signal_btc.py", "emit_signal_btc_fallback_test"),
    ],
)
def test_provider_failure_does_not_dilute_real_news_score(relative_path, module_name):
    module = load_script(relative_path, module_name)
    score, confidence, source, available, basis = module.combine_signal_sources(
        0, 0.0, "sentiment unavailable (HTTP 429)", 88, 11
    )
    assert score == 88
    assert confidence == 0.0
    assert available is False
    assert basis == "news_only"
    assert "news_only_fallback" in source


@pytest.mark.parametrize(
    "relative_path,module_name",
    [
        ("scripts/emit_signal.py", "emit_signal_no_news_test"),
        ("scripts/emit_signal_btc.py", "emit_signal_btc_no_news_test"),
    ],
)
def test_provider_failure_without_news_is_explicit_neutral_placeholder(relative_path, module_name):
    module = load_script(relative_path, module_name)
    score, confidence, source, available, basis = module.combine_signal_sources(
        0, 0.0, "sentiment unavailable (missing credentials)", None, 0
    )
    assert score == 50
    assert confidence == 0.0
    assert available is False
    assert basis == "unavailable_neutral_placeholder"
    assert "sentiment unavailable" in source


def test_available_model_and_news_are_blended_and_labelled():
    module = load_script("scripts/emit_signal.py", "emit_signal_blend_test")
    score, confidence, source, available, basis = module.combine_signal_sources(
        60, 0.7, "groq:bullish", 80, 4
    )
    assert score == 70
    assert confidence == 0.7
    assert available is True
    assert basis == "model_and_news_blend"
    assert source == "groq:bullish+news(4)"


def test_summary_writes_deterministic_fallback_without_provider_key(tmp_path, monkeypatch):
    module = load_script("scripts/signal_summary.py", "signal_summary_fallback_test")
    signal_path = tmp_path / "latest_signal.json"
    summary_path = tmp_path / "latest_signal_summary.json"
    signal_path.write_text(json.dumps({
        "score": 88,
        "confidence": 0.0,
        "model_available": False,
        "score_basis": "news_only",
        "news_entries": 11,
        "source": "news_only_fallback(provider unavailable)",
    }))
    monkeypatch.setattr(module, "KEY", "")
    monkeypatch.setattr(module, "SIGNAL_FILE", signal_path)
    monkeypatch.setattr(module, "SUMMARY_FILE", summary_path)
    module.main()
    result = json.loads(summary_path.read_text())
    assert result["summary_source"] == "deterministic_fallback"
    assert result["audio"] is None
    assert "GROQ_API_KEY not set" in result["tts_error"]
    assert "Score: 88" in result["summary"]
