import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_emit_signal():
    spec = importlib.util.spec_from_file_location(
        "emit_signal_under_test", ROOT / "scripts" / "emit_signal.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_emitted_metadata_is_sentiment_only_not_a_forecast():
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


def test_unknown_sentiment_label_is_normalized_to_neutral():
    module = _load_emit_signal()
    metadata = module._sentiment_feature_metadata("BUY", 0.99)
    assert metadata["sentiment_label"] == "neutral"


def test_subscriber_page_does_not_convert_score_to_buy_or_sell():
    page = (ROOT / "web" / "signals.html").read_text(encoding="utf-8")
    assert "_m={'1':'BUY','0':'NULL','-1':'SELL'}" not in page
    assert "signal_kind === 'sentiment_feature_only'" in page
    assert "not a price forecast" in page
    assert "not a probability" in page


def test_daily_digest_does_not_publish_legacy_accuracy_metric():
    digest = (ROOT / "scripts" / "daily_digest.py").read_text(encoding="utf-8")
    assert "signal_accuracy.json" not in digest
    assert "accuracy_pct" not in digest
    assert "NOT_ISSUED" in digest
    assert "not a price forecast" in digest


def test_public_tool_labels_sentiment_as_not_a_forecast():
    landing = (ROOT / "web" / "landing.html").read_text(encoding="utf-8")
    assert 'title: "Latest XRP Sentiment Feature"' in landing
    assert "not a price forecast" in landing
    assert "do not validate Barrot's current sentiment feature" in landing



def test_malformed_model_response_does_not_invent_confidence():
    module = _load_emit_signal()
    score, confidence, label = module._score_from_text("not valid json")
    assert score == 50
    assert confidence == 0.0
    assert label == "neutral"



def test_daily_digest_uses_real_newlines_and_validates_confidence():
    digest = (ROOT / "scripts" / "daily_digest.py").read_text(encoding="utf-8")
    assert 'body = "\\n".join(lines)' in digest
    assert "math.isfinite(confidence_value)" in digest


def test_missing_or_nonfinite_classifier_confidence_is_zero():
    module = _load_emit_signal()
    for raw in (
        '{"score": 72, "label": "bullish"}',
        '{"score": 72, "confidence": "NaN", "label": "bullish"}',
        '{"score": 72, "confidence": "Infinity", "label": "bullish"}',
    ):
        _, confidence, _ = module._score_from_text(raw)
        assert confidence == 0.0
    assert module._normalize_confidence(1.5) == 1.0
    assert module._normalize_confidence(-0.5) == 0.0
    assert module._normalize_score(float("nan")) == 50


def test_emitter_does_not_attach_a_live_price_as_a_sentiment_feature_anchor():
    source = (ROOT / "scripts" / "emit_signal.py").read_text(encoding="utf-8")
    assert "api.coingecko.com" not in source
    assert "price_at_emission" not in source
    assert "reference_price_at_feature_generation" not in source


def test_landing_page_describes_only_sentiment_not_orderbook_or_trade_signals():
    page = (ROOT / "web" / "landing.html").read_text(encoding="utf-8").lower()
    assert "order book depth" not in page
    assert "price structure" not in page
    assert "1.58-bit ternary logic" not in page
    assert "not a price forecast" in page
    assert "uncalibrated" in page
    assert "not price signals" in page


def test_ask_barrot_does_not_repeat_legacy_accuracy_as_model_performance():
    source = (ROOT / "scripts" / "ask_barrot.py").read_text(encoding="utf-8")
    assert "SIGNAL_ACCURACY" not in source
    assert "signal_accuracy.json" not in source
    assert "accuracy_pct" not in source
    assert "UNVALIDATED_VARIABLE_HORIZON" in source
    assert "NOT_ISSUED" in source
    assert "uncalibrated; not a price probability" in source


def test_subscriber_page_labels_signal_text_as_context_not_price():
    page = (ROOT / "web" / "signals.html").read_text(encoding="utf-8")
    assert 'id="signal-text"' in page
    assert 'id="price"' not in page
    assert "Sentiment context:" in page
    assert "getElementById('price')" not in page
