import hashlib
import json
from datetime import datetime
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261107T080902Z-xrp-spot-venue-staleness-reconciliation.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_raw_exchange_receipts_match_exact_stored_json_hashes():
    artifact = load_artifact()
    for source in artifact["sources"]:
        raw = source["raw_response_exact_json"].encode("utf-8")
        assert len(raw) == source["raw_response_bytes"]
        assert hashlib.sha256(raw).hexdigest() == source["raw_response_sha256"]


def test_kraken_missing_provider_timestamp_is_not_fabricated():
    artifact = load_artifact()
    kraken = artifact["sources"][0]
    assert kraken["publisher"] == "Kraken"
    assert kraken["provider_event_timestamp_utc"] is None
    assert kraken["freshness_status"] == "UNVERIFIABLE_PROVIDER_TIMESTAMP_MISSING"


def test_okx_provider_timestamp_is_parsed_and_rejected_as_stale():
    artifact = load_artifact()
    okx = artifact["sources"][1]
    provider = datetime.fromisoformat(okx["provider_event_timestamp_utc"].replace("Z", "+00:00"))
    captured = datetime.fromisoformat(artifact["captured_at_utc"].replace("Z", "+00:00"))
    age = (captured - provider).total_seconds()
    assert abs(age - okx["provider_event_age_seconds_at_capture"]) < 0.001
    assert age > okx["freshness_limit_seconds"]
    assert okx["freshness_status"] == "STALE_EXCEEDS_300_SECOND_LIMIT"


def test_level_one_spreads_recompute_from_bid_and_ask():
    artifact = load_artifact()
    kraken, okx = artifact["sources"]
    for source, quote in (
        (kraken, "usd"),
        (okx, "usdt"),
    ):
        metrics = source["normalized_metrics"]
        bid = metrics[f"best_bid_{quote}"]
        ask = metrics[f"best_ask_{quote}"]
        expected = (ask - bid) / ((ask + bid) / 2) * 10_000
        assert abs(expected - metrics["level1_spread_bps"]) < 1e-8


def test_cross_venue_gap_is_not_called_arbitrage():
    artifact = load_artifact()
    derived = artifact["derived_reconciliation"]
    expected = (1.1756 - 1.17206) / 1.17206 * 100
    assert abs(expected - derived["raw_cross_venue_last_price_gap_pct"]) < 1e-8
    assert "not an executable arbitrage" in derived["interpretation"]


def test_okx_snapshot_change_is_timestamp_bounded_not_a_candle_return():
    artifact = load_artifact()
    derived = artifact["derived_reconciliation"]
    expected = (1.1756 - 1.169) / 1.169 * 100
    assert abs(expected - derived["okx_snapshot_to_snapshot_change_pct"]) < 1e-8
    assert derived["okx_snapshot_interval_seconds"] == 3668
    assert "not a continuous candle return" in derived["interpretation"]


def test_no_depth_or_model_feature_is_inferred_from_ticker_data():
    artifact = load_artifact()
    assert artifact["model_admission"]["eligible"] is False
    assert any("multi-level depth" in reason for reason in artifact["model_admission"]["reasons"])
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
    assert artifact["forecast"]["directional_forecast"] is None


def test_no_order_or_funds_action_occurred():
    artifact = load_artifact()
    assert artifact["external_actions"] == {
        "orders_sent": False,
        "exchange_account_accessed": False,
        "funds_transferred": False,
        "paper_trade_created": False,
        "real_money_used": False,
    }
