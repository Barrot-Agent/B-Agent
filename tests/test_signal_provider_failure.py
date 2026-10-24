from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def load_script(relative_path: str, module_name: str):
    path = REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EMITTER = load_script("scripts/emit_signal.py", "emit_signal_provider_failure_test")
ACCURACY = load_script(
    "scripts/check_signal_accuracy.py", "check_signal_accuracy_provider_failure_test"
)
SUMMARY = load_script("scripts/signal_summary.py", "signal_summary_provider_failure_test")
SCORE_UTIL = load_script("utils/score_to_signal.py", "score_to_signal_status_test")


def test_two_provider_failures_return_unavailable_not_zero(monkeypatch):
    def fail(_signal_text):
        raise RuntimeError("provider unavailable")

    monkeypatch.setattr(EMITTER, "_call_github_models", fail)
    monkeypatch.setattr(EMITTER, "_call_groq", fail)

    score, confidence, source = EMITTER.analyze_signal("test market context")

    assert score is None
    assert confidence == 0.0
    assert "sentiment unavailable" in source


def test_news_only_signal_does_not_blend_in_missing_model_zero():
    result = EMITTER._compose_signal(
        (None, 0.0, "sentiment unavailable (providers failed)"), 88, 11
    )

    assert result["score"] == 88
    assert result["confidence"] == 0.0
    assert result["signal_status"] == "news_only"
    assert result["score_basis"] == "news_only"
    assert result["model_score"] is None
    assert result["model_available"] is False


def test_all_inputs_unavailable_uses_explicit_placeholder():
    result = EMITTER._compose_signal(
        (None, 0.0, "sentiment unavailable (providers failed)"), None, 0
    )

    assert result["score"] == 50
    assert result["signal_status"] == "unavailable"
    assert result["score_basis"] == "unavailable_placeholder"
    assert result["confidence"] == 0.0
    assert result["model_available"] is False


def test_model_and_news_are_blended_only_when_model_is_available():
    result = EMITTER._compose_signal((60, 0.8, "github:neutral"), 80, 4)

    assert result["score"] == 70
    assert result["confidence"] == 0.8
    assert result["signal_status"] == "model_and_news"
    assert result["score_basis"] == "equal_weight_model_and_news"
    assert result["model_available"] is True


def test_model_only_signal_keeps_model_score_and_confidence():
    result = EMITTER._compose_signal((63, 0.7, "groq:bullish"), None, 0)

    assert result["score"] == 63
    assert result["confidence"] == 0.7
    assert result["signal_status"] == "model_only"
    assert result["score_basis"] == "model_only"


def test_accuracy_filter_excludes_unavailable_and_news_only_records():
    assert ACCURACY._non_model_signal_reason(
        {"signal_status": "unavailable", "source": "provider failed"}
    ) == "signal_unavailable"
    assert ACCURACY._non_model_signal_reason(
        {"signal_status": "news_only", "source": "news only"}
    ) == "news_only_not_model_evaluation"


def test_accuracy_filter_excludes_legacy_provider_failure_rows():
    assert ACCURACY._non_model_signal_reason(
        {"source": "sentiment unavailable (github_failed; groq_failed)"}
    ) == "legacy_provider_unavailable"


def test_accuracy_filter_keeps_model_backed_records():
    assert ACCURACY._non_model_signal_reason(
        {"signal_status": "model_and_news", "source": "github:bullish+news(3)"}
    ) is None



def test_summary_skips_model_and_tts_for_news_only_signal():
    signal = {
        "signal_status": "news_only",
        "score": 88,
        "news_score": 88,
        "news_entries": 11,
        "confidence": 0.0,
        "source": "news_only; sentiment unavailable",
    }

    assert SUMMARY._needs_source_fallback(signal) is True
    payload = SUMMARY._source_unavailable_payload(signal)
    assert payload["summary_method"] == "deterministic_source_unavailable"
    assert "not a calibrated XRP price forecast" in payload["summary"]
    assert payload["audio"] is None
    assert payload["tts_error"] == "skipped_source_signal_unavailable"


def test_summary_skips_model_for_legacy_provider_failure():
    assert SUMMARY._needs_source_fallback(
        {"score": 44, "source": "sentiment unavailable (github_failed; groq_failed)"}
    ) is True


def test_shared_status_guard_rejects_unavailable_and_news_only_states():
    assert SCORE_UTIL.is_model_backed_signal(
        {"signal_status": "unavailable", "score": 50}
    ) is False
    assert SCORE_UTIL.is_model_backed_signal(
        {"signal_status": "news_only", "score": 88}
    ) is False
    assert SCORE_UTIL.is_model_backed_signal(
        {"signal_status": "model_and_news", "score": 66}
    ) is True


def test_shared_status_guard_rejects_legacy_provider_failure():
    assert SCORE_UTIL.is_model_backed_signal(
        {"score": 44, "source": "sentiment unavailable (provider failed)"}
    ) is False


def test_shared_status_guard_preserves_legacy_model_backed_records():
    assert SCORE_UTIL.is_model_backed_signal(
        {"score": 61, "source": "github:bullish"}
    ) is True


DIGEST = load_script("scripts/daily_digest.py", "daily_digest_signal_status_test")


def test_digest_does_not_present_provider_failure_as_directional_signal():
    text = DIGEST._format_latest_signal({
        "score": 44,
        "confidence": 0.0,
        "news_score": 88,
        "source": "sentiment unavailable (github_failed; groq_failed)+news(11)",
    })
    assert "model signal unavailable" in text
    assert "no directional forecast issued" in text
    assert "score 44/100" not in text


def test_digest_labels_news_only_record_as_not_forecast():
    text = DIGEST._format_latest_signal({
        "score": 88,
        "signal_status": "news_only",
        "source": "news_only; sentiment unavailable",
    })
    assert "news-only score 88/100" in text
    assert "no model-backed directional forecast" in text


def test_digest_labels_model_backed_score_as_not_calibrated_forecast():
    text = DIGEST._format_latest_signal({
        "score": 62,
        "confidence": 0.7,
        "model_confidence": 0.7,
        "signal_status": "model_and_news",
        "source": "github:bullish+news(3)",
    })
    assert "Latest XRP sentiment" in text
    assert "not a calibrated price forecast" in text