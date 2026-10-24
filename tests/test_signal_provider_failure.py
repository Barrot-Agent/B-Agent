"""Regression tests for unavailable model-provider handling in XRP sentiment."""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


emitter = _load_module("barrot_emit_signal_under_test", "scripts/emit_signal.py")
accuracy = _load_module("barrot_check_signal_accuracy_under_test", "scripts/check_signal_accuracy.py")


def test_provider_failure_with_news_uses_news_only_not_zero_average():
    result = emitter._compose_signal(
        None, 0.0, "sentiment unavailable (providers failed)", 88, 11
    )
    assert result["score"] == 88
    assert result["confidence"] == 0.0
    assert result["model_available"] is False
    assert result["signal_status"] == "news_only"
    assert result["score_basis"] == "news_only"
    assert "news_only(11)" in result["source"]


def test_provider_and_news_failure_marks_signal_unavailable():
    result = emitter._compose_signal(
        None, 0.0, "sentiment unavailable (providers failed)", None, 0
    )
    assert result["score"] == 50
    assert result["confidence"] == 0.0
    assert result["model_available"] is False
    assert result["signal_status"] == "unavailable"
    assert result["score_basis"] == "unavailable_placeholder"


def test_available_model_can_still_blend_with_news():
    result = emitter._compose_signal(40, 0.8, "groq:bearish", 80, 4)
    assert result["score"] == 60
    assert result["confidence"] == 0.8
    assert result["model_available"] is True
    assert result["signal_status"] == "model_and_news"
    assert result["score_basis"] == "model_and_news"


def test_analyze_signal_returns_none_when_both_providers_fail(monkeypatch):
    def fail_github(_):
        raise RuntimeError("missing model token")

    def fail_groq(_):
        raise RuntimeError("HTTP 429")

    monkeypatch.setattr(emitter, "_call_github_models", fail_github)
    monkeypatch.setattr(emitter, "_call_groq", fail_groq)
    score, confidence, source = emitter.analyze_signal("test")
    assert score is None
    assert confidence == 0.0
    assert "sentiment unavailable" in source


def test_legacy_provider_failure_rows_are_excluded_from_model_accuracy():
    entry = {"source": "sentiment unavailable (github_failed; groq_failed)+news(11)"}
    assert accuracy._non_model_signal_reason(entry) == "legacy_provider_unavailable"


def test_news_only_and_unavailable_rows_are_not_model_accuracy_samples():
    assert accuracy._non_model_signal_reason({"signal_status": "news_only"}) == "news_only_not_model_evaluation"
    assert accuracy._non_model_signal_reason({"signal_status": "unavailable"}) == "signal_unavailable"


def test_model_backed_rows_remain_eligible_for_accuracy_evaluation():
    entry = {"signal_status": "model_and_news", "source": "groq:bullish+news(5)"}
    assert accuracy._non_model_signal_reason(entry) is None
