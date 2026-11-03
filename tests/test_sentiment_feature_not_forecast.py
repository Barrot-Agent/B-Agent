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
