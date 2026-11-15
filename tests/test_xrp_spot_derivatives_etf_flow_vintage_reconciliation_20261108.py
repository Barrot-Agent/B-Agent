from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research/xrp_intelligence/20261108T195810Z-xrp-spot-derivatives-etf-flow-vintage-reconciliation.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_all_source_excerpt_and_api_body_hashes_are_reproducible():
    artifact = load_artifact()
    assert len(artifact["source_receipts"]) == 7
    for receipt in artifact["source_receipts"]:
        value = receipt.get("response_body_text", receipt.get("normalized_excerpt"))
        assert isinstance(value, str) and value
        assert hashlib.sha256(value.encode("utf-8")).hexdigest() == receipt["sha256"]
        assert "wire" in receipt["hash_scope"].lower() or "raw html" in receipt["hash_scope"].lower()


def test_spot_quotes_keep_quote_currencies_and_provider_time_distinct():
    spot = load_artifact()["spot"]
    assert spot["reference_time_utc"] == "2026-11-08T19:58:10Z"
    assert spot["kraken"]["quote_currency"] == "USD"
    assert spot["kraken"]["provider_event_time_utc"] is None
    assert spot["kraken"]["freshness_status"] == "UNKNOWN_PROVIDER_EVENT_TIME"
    assert spot["okx"]["quote_currency"] == "USDT"
    assert spot["okx"]["provider_event_time_utc"] == "2026-11-08T19:53:38.962Z"
    assert math.isclose(spot["okx"]["age_seconds_at_reference"], 271.038, abs_tol=1e-9)
    assert spot["okx"]["freshness_status"] == "WITHIN_300_SECOND_LIMIT"
    assert spot["cross_venue"]["normalized_usd_usdt_basis"] is False
    assert spot["cross_venue"]["executable_arbitrage_signal"] is False
    assert spot["level2_depth_captured"] is False
    assert spot["synchronized_trades_captured"] is False


def test_top_of_book_spreads_and_imbalances_are_reproducible_but_not_depth():
    spot = load_artifact()["spot"]
    kraken = spot["kraken"]
    okx = spot["okx"]
    kraken_spread = (kraken["ask"] - kraken["bid"]) / ((kraken["ask"] + kraken["bid"]) / 2) * 10_000
    okx_spread = (okx["ask"] - okx["bid"]) / ((okx["ask"] + okx["bid"]) / 2) * 10_000
    kraken_bid_share = kraken["bid_size_xrp"] / (kraken["bid_size_xrp"] + kraken["ask_size_xrp"]) * 100
    okx_bid_share = okx["bid_size_xrp"] / (okx["bid_size_xrp"] + okx["ask_size_xrp"]) * 100
    assert math.isclose(kraken_spread, kraken["spread_bps"], abs_tol=1e-8)
    assert math.isclose(okx_spread, okx["spread_bps"], abs_tol=1e-8)
    assert math.isclose(kraken_bid_share, kraken["top_of_book_bid_share_pct"], abs_tol=1e-4)
    assert math.isclose(okx_bid_share, okx["top_of_book_bid_share_pct"], abs_tol=1e-4)
    assert kraken_bid_share < 20
    assert okx_bid_share > 75
    assert spot["cross_venue"]["raw_last_price_gap_pct"] > 0.18
    assert spot["cross_venue"]["model_eligible"] is False


def test_derivatives_oi_components_reconcile_with_each_publishers_rounding():
    derivatives = load_artifact()["derivatives"]
    kodexius = derivatives["kodexius"]
    tradradar = derivatives["tradradar"]
    assert sum(kodexius["contract_oi_usd"].values()) == 779_650_000
    assert abs(kodexius["reported_total_oi_usd"] - sum(kodexius["contract_oi_usd"].values())) == 10_000
    assert sum(tradradar["exchange_oi_usd"].values()) == tradradar["exchange_component_sum_usd"] == 1_892_470_000
    assert tradradar["displayed_total_oi_usd"] == 1_890_000_000
    assert tradradar["liquidation_exchange_count"] == 5
    assert tradradar["exchange_count"] == 7


def test_derivatives_provider_universes_and_common_venue_differences_are_not_averaged():
    comparison = load_artifact()["derivatives"]["comparison"]
    assert comparison["displayed_total_ratio_tradradar_to_kodexius"] > 2.4
    assert comparison["do_not_average"] is True
    assert comparison["status"] == (
        "UNRESOLVED_VENUE_SCOPE_CONTRACT_SCOPE_AGGREGATION_AND_TIMESTAMP_DIFFERENCE"
    )
    assert comparison["tradradar_venues_not_in_kodexius"] == ["Gate", "MEXC", "Bitget"]
    assert comparison["kodexius_venues_not_in_tradradar"] == ["HTX"]
    assert comparison["common_venue_oi_difference_usd"] == 352_480_000
    assert comparison["overlapping_exchange_delta_pct"]["Bybit"] > 100
    assert comparison["overlapping_exchange_delta_pct"]["Hyperliquid"] > 100
    assert len(comparison["competing_hypotheses"]) == 4
    assert all(item["support"] and item["counterevidence"] for item in comparison["competing_hypotheses"])


def test_etf_provider_units_universes_and_future_date_anomaly_remain_separate():
    flows = load_artifact()["etf_flow_reconciliation"]
    assert flows["xrp_insights"]["daily_nov6_xrp"] == -663_043
    assert flows["xrp_insights"]["weekly_oct30_nov6_xrp"] == -812_529
    assert flows["cryptokeyhole"]["nov6_partial_change_xrp"] == -752_048
    assert flows["cryptokeyhole"]["coverage"] == "3 of 4 daily-readable funds"
    assert flows["cryptokeyhole"]["franklin_xrpz_missing"] is True
    assert flows["cryptokeyhole"]["date_anomaly_status"] == "QUARANTINED_FUTURE_DATE_CONFLICT"
    assert flows["alpha_finance"]["nov6_daily_flow_usd"] == 0
    assert flows["alpha_finance"]["funds_reporting"] == flows["alpha_finance"]["fund_count"] == 5
    assert flows["alpha_finance"]["holdings_or_aum_published"] is False
    assert flows["do_not_average"] is True
    assert flows["actual_capital_inference"] is False
    assert "not independent confirmations" in flows["source_independence"]


def test_no_incomplete_snapshot_enters_features_or_issues_a_forecast():
    artifact = load_artifact()
    quality = artifact["source_quality"]
    assert quality["raw_http_wire_bytes"] is False
    assert quality["synchronized_provider_timestamps"] is False
    assert quality["multi_level_orderbook_depth"] is False
    assert quality["complete_derivatives_contract_universe"] is False
    assert quality["complete_etf_issuer_universe"] is False
    assert quality["feature_store_admission"] == "PROHIBITED"
    assert artifact["forecast_status"] == "NOT_ISSUED"
    assert artifact["external_actions"]["feature_store_write"] is False
    assert artifact["external_actions"]["paper_trade"] is False
    assert artifact["external_actions"]["real_money"] is False
