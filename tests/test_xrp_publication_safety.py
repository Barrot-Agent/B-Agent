import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def _load_emit_signal():
    spec = importlib.util.spec_from_file_location(
        "emit_signal_publication_safety", ROOT / "scripts" / "emit_signal.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_external_sentiment_classifier_is_denied_without_explicit_confirmation(monkeypatch):
    module = _load_emit_signal()
    monkeypatch.delenv("BARROT_ALLOW_EXTERNAL_SENTIMENT_CLASSIFIER", raising=False)
    monkeypatch.delenv("BARROT_SENTIMENT_PROVIDER", raising=False)
    monkeypatch.setattr(module, "_call_github_models", lambda _: pytest.fail("GitHub Models called without consent"))
    monkeypatch.setattr(module, "_call_groq", lambda _: pytest.fail("Groq called without consent"))
    assert module.analyze_signal("public headline") == (
        50, 0.0, "neutral", "external_classifier_not_authorized"
    )


def test_external_sentiment_provider_must_be_selected_explicitly(monkeypatch):
    module = _load_emit_signal()
    monkeypatch.setenv("BARROT_ALLOW_EXTERNAL_SENTIMENT_CLASSIFIER", "YES")
    monkeypatch.delenv("BARROT_SENTIMENT_PROVIDER", raising=False)
    assert module.analyze_signal("public headline") == (
        50, 0.0, "neutral", "sentiment_provider_not_selected"
    )


def test_explicit_provider_selection_does_not_silently_fallback(monkeypatch):
    module = _load_emit_signal()
    monkeypatch.setenv("BARROT_ALLOW_EXTERNAL_SENTIMENT_CLASSIFIER", "YES")
    monkeypatch.setenv("BARROT_SENTIMENT_PROVIDER", "github_models")
    monkeypatch.setattr(module, "_call_github_models", lambda _: (72, 0.7, "bullish", "github:bullish"))
    monkeypatch.setattr(module, "_call_groq", lambda _: pytest.fail("Silent Groq fallback is forbidden"))
    assert module.analyze_signal("public headline") == (72, 0.7, "bullish", "github:bullish")


def test_emitted_metadata_is_sentiment_only_and_never_forecast_eligible():
    module = _load_emit_signal()
    metadata = module._sentiment_feature_metadata("BULLISH", 0.91)
    assert metadata["signal_kind"] == "sentiment_feature_only"
    assert metadata["forecast_eligible"] is False
    assert metadata["forecast_status"] == "NOT_A_FORECAST"
    assert metadata["sentiment_label"] == "bullish"
    assert metadata["confidence_is_calibrated_probability"] is False
    assert metadata["target"] is None
    assert metadata["horizon_seconds"] is None
    assert metadata["source_cutoff_utc"] is None
    assert metadata["source_snapshot_ids"] == []


def test_malformed_or_nonfinite_classifier_response_does_not_invent_confidence():
    module = _load_emit_signal()
    assert module._score_from_text("not json") == (50, 0.0, "neutral")
    assert module._score_from_text("[]") == (50, 0.0, "neutral")
    _, confidence, _ = module._score_from_text(
        '{"score":72,"confidence":"NaN","label":"bullish"}'
    )
    assert confidence == 0.0


def test_emitter_writes_sentiment_metadata_without_price_anchor_or_network_by_default(tmp_path, monkeypatch, capsys):
    module = _load_emit_signal()
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("BARROT_ALLOW_EXTERNAL_SENTIMENT_CLASSIFIER", raising=False)
    monkeypatch.delenv("BARROT_SENTIMENT_PROVIDER", raising=False)
    monkeypatch.setattr(module, "_news_score", lambda: (None, 0, []))
    monkeypatch.setattr(module, "_call_github_models", lambda _: pytest.fail("GitHub Models called"))
    monkeypatch.setattr(module, "_call_groq", lambda _: pytest.fail("Groq called"))
    module.main()
    output = json.loads(capsys.readouterr().out)
    saved = json.loads((tmp_path / "web" / "latest_signal.json").read_text(encoding="utf-8"))
    history = json.loads((tmp_path / "web" / "signal_history.jsonl").read_text(encoding="utf-8"))
    assert output == saved == history
    assert saved["signal_kind"] == "sentiment_feature_only"
    assert saved["forecast_eligible"] is False
    assert saved["forecast_status"] == "NOT_A_FORECAST"
    assert saved["confidence"] == 0.0
    assert "price_at_emission" not in saved
    assert "reference_price_at_feature_generation" not in saved


def test_ask_barrot_does_not_publish_legacy_accuracy_or_misclassify_scores():
    source = (ROOT / "scripts" / "ask_barrot.py").read_text(encoding="utf-8")
    assert "SIGNAL_ACCURACY" not in source
    assert "accuracy_pct" not in source
    assert "signal accuracy tracker" not in source.lower()
    assert "UNVALIDATED_VARIABLE_HORIZON" in source
    assert "NOT_ISSUED" in source
    assert "sentiment_feature_only" in source
    assert "uncalibrated; not a price probability" in source
    assert 'return "\\n\\nYour real, current sentiment-feature and evaluation-status data:\\n"' in source


def test_webmcp_forecast_and_accuracy_tools_return_status_only():
    page = (ROOT / "web" / "landing.html").read_text(encoding="utf-8")
    latest = page.split('name: "getLatestXRPSignal"', 1)[1].split('mcp.registerTool({', 1)[0]
    accuracy = page.split('name: "getSignalAccuracy"', 1)[1].split('mcp.registerTool({', 1)[0]
    assert 'fetch("latest_signal.json")' not in latest
    assert "forecast_issued: false" in latest
    assert "VALIDATED_FIXED_HORIZON_FORECAST_NOT_AVAILABLE" in latest
    assert "return await res.json()" not in accuracy
    assert "reported_percentage" not in accuracy
    assert "accuracy_pct: null" in accuracy


def test_legacy_accuracy_is_preserved_separately_and_not_in_current_status():
    current = json.loads((ROOT / "web" / "signal_accuracy.json").read_text(encoding="utf-8"))
    legacy = json.loads((ROOT / "web" / "legacy" / "signal_accuracy_unvalidated.json").read_text(encoding="utf-8"))
    assert current["status"] == "NOT_EVALUATED"
    assert current["forecast_eligible"] is False
    assert current["accuracy_pct"] is None
    assert "reported_percentage" not in current
    assert legacy["status"] == "UNVALIDATED_LEGACY"
    assert legacy["reported_percentage"] == 45.5
    assert legacy["valid_predictive_accuracy"] is False


def test_subscriber_page_is_forecast_status_only():
    page = (ROOT / "web" / "signals.html").read_text(encoding="utf-8").lower()
    assert "forecast status: not_issued" in page
    assert "buy" not in page
    assert "sell" not in page
