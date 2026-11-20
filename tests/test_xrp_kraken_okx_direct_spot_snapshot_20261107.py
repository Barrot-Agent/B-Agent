import hashlib
import json
from pathlib import Path

ARTIFACT = Path(
    "research/xrp_intelligence/20261107T105341Z-xrp-kraken-okx-direct-spot-snapshot.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_direct_exchange_sources_and_receipt_hashes_are_preserved():
    artifact = load_artifact()
    assert artifact["sources"][0]["publisher"] == "Kraken"
    assert artifact["sources"][1]["publisher"] == "OKX"
    for source in artifact["sources"]:
        digest = hashlib.sha256(source["raw_response_text"].encode("utf-8")).hexdigest()
        assert digest == source["raw_response_sha256"]


def test_kraken_rolling_24h_fields_are_not_confused_with_today_fields():
    artifact = load_artifact()
    kraken = artifact["sources"][0]["normalized"]
    assert kraken["rolling_24h_volume_xrp"] == 27213738.58527979
    assert kraken["today_volume_xrp"] == 9158209.92249708
    assert kraken["rolling_24h_vwap_usd"] == 1.17707089
    assert kraken["today_vwap_usd"] == 1.16575418


def test_kraken_missing_provider_timestamp_is_explicit():
    artifact = load_artifact()
    kraken = artifact["sources"][0]
    assert kraken["provider_event_timestamp_utc"] is None
    assert "retrieval time, not exchange event time" in kraken["limitations"][0]


def test_okx_provider_timestamp_age_fails_live_freshness():
    artifact = load_artifact()
    okx = artifact["sources"][1]
    assert okx["provider_age_seconds_at_capture"] == 614.334
    assert okx["freshness_status"] == "STALE_OVER_300_SECONDS"
    assert okx["normalized"]["rolling_24h_volume_xrp"] == 50006650.848757


def test_native_quote_spreads_are_not_promoted_to_cross_venue_arbitrage():
    artifact = load_artifact()
    derived = artifact["derived_reconciliation"]
    assert round(derived["spread_comparison"]["kraken_level1_spread_bps"], 6) == round(
        (1.16800 - 1.16799) / ((1.16800 + 1.16799) / 2) * 10000, 6
    )
    assert round(derived["spread_comparison"]["okx_level1_spread_bps"], 6) == round(
        (1.1704 - 1.1703) / ((1.1704 + 1.1703) / 2) * 10000, 6
    )
    assert derived["executable_arbitrage_signal"] is False
    assert derived["depth_capture_status"] == "NOT_CAPTURED"


def test_stale_or_unsynchronized_quotes_are_not_model_admitted():
    artifact = load_artifact()
    admission = artifact["model_admission"]
    assert admission["eligible_as_live_price_feature"] is False
    assert admission["eligible_as_strict_historical_feature"] is False
    assert admission["eligible_as_event_timeline"] is True


def test_forecast_and_execution_remain_disabled():
    artifact = load_artifact()
    forecast = artifact["forecast"]
    assert forecast["status"] == "NOT_ISSUED"
    assert forecast["directional_forecast"] is None
    assert forecast["shadow_forecast"] is None
    assert forecast["paper_trade_executed"] is False
    assert forecast["real_money_action"] is False
