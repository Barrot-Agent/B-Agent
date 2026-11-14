import hashlib
import json
from math import isclose
from pathlib import Path


def _artifact():
    path = (
        Path(__file__).resolve().parents[1]
        / "research"
        / "xrp_intelligence"
        / "20261107T033222Z-xrp-direct-spot-ticker-staleness-reconciliation.json"
    )
    return json.loads(path.read_text(encoding="utf-8"))


def test_direct_exchange_receipts_match_exact_retrieval_text_hashes():
    artifact = _artifact()
    records = {item["source_id"]: item for item in artifact["source_records"]}
    assert set(records) == {
        "kraken_xrpusd_ticker_20261107_033222",
        "okx_xrpusdt_ticker_20261107_033222",
    }
    for source in records.values():
        digest = hashlib.sha256(
            source["exact_response_representation"].encode("utf-8")
        ).hexdigest()
        assert digest == source["exact_response_representation_sha256"]


def test_kraken_ticker_keeps_utc_daily_open_separate_from_rolling_24h_fields():
    artifact = _artifact()
    kraken = artifact["observations"]["kraken"]
    assert kraken["last_usd"] == 1.16222
    assert kraken["utc_daily_open_usd"] == 1.17749
    assert kraken["rolling_24h_volume_xrp"] == 28_811_682.35248909
    assert kraken["rolling_24h_vwap_usd"] == 1.18478862
    assert kraken["rolling_24h_low_usd"] == 1.16124
    assert kraken["rolling_24h_high_usd"] == 1.2105


def test_okx_provider_timestamp_is_preserved_and_rejected_as_stale():
    artifact = _artifact()
    okx = next(
        item for item in artifact["source_records"]
        if item["publisher"] == "OKX"
    )
    assert okx["provider_timestamp_utc"] == "2026-11-07T03:16:30.466Z"
    assert okx["provider_timestamp_age_seconds_at_capture"] == 951.534
    assert okx["maximum_live_feature_age_seconds"] == 300
    assert okx["stale_for_live_feature"] is True


def test_level_one_spreads_and_sizes_are_arithmetically_consistent():
    artifact = _artifact()
    kraken = artifact["observations"]["kraken"]
    okx = artifact["observations"]["okx"]
    assert isclose(
        kraken["spread_bps"],
        (kraken["best_ask_usd"] - kraken["best_bid_usd"])
        / kraken["mid_usd"] * 10_000,
        rel_tol=1e-12,
    )
    assert isclose(
        okx["spread_bps"],
        (okx["best_ask_usdt"] - okx["best_bid_usdt"])
        / okx["mid_usdt"] * 10_000,
        rel_tol=1e-12,
    )
    assert kraken["best_bid_size_xrp"] == 945
    assert kraken["best_ask_size_xrp"] == 3832
    assert okx["best_bid_size_xrp"] == 1691.335
    assert okx["best_ask_size_xrp"] == 12429.818986


def test_cross_venue_price_difference_is_not_treated_as_arbitrage():
    comparison = _artifact()["comparisons"]
    assert comparison["raw_last_price_difference_pct_okx_vs_kraken"] > 0
    assert "not interpret as arbitrage" in comparison["treatment"]


def test_retrieval_vintage_change_is_not_an_event_time_return():
    vintage = _artifact()["comparisons"]["prior_kraken_retrieval_vintage"]
    assert vintage["retrieval_gap_seconds"] == 1654
    assert vintage["observed_snapshot_to_snapshot_change_pct"] < 0
    assert "not a validated event-time return" in vintage["interpretation"]


def test_market_snapshot_remains_ineligible_and_forecast_is_not_issued():
    artifact = _artifact()
    assert artifact["model_admission"]["eligible"] is False
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
    assert artifact["forecast"]["directional_forecast"] is None
    assert artifact["forecast"]["shadow_forecast"] is None
    assert artifact["forecast"]["paper_trade_executed"] is False
    assert artifact["forecast"]["real_money_action"] is False
