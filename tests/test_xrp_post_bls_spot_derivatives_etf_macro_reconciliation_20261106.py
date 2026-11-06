from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261106T181024Z-xrp-post-bls-spot-derivatives-etf-macro-reconciliation.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_source_excerpt_receipts_reproduce_without_claiming_wire_capture():
    data = load_artifact()
    assert len(data["source_registry"]) == 9
    for source in data["source_registry"]:
        receipt = source["receipt"]
        assert receipt["algorithm"] == "SHA-256"
        assert hashlib.sha256(source["excerpt"].encode("utf-8")).hexdigest() == receipt["digest"]
    assert data["capture_contract"]["original_http_wire_bytes_captured"] is False
    assert data["capture_contract"]["common_point_in_time_cutoff_utc"] is None


def test_kraken_ticker_arithmetic_and_missing_provider_timestamp_are_preserved():
    row = load_artifact()["spot_observations"][0]
    midpoint = (row["best_bid_usd"] + row["best_ask_usd"]) / 2
    spread = (row["best_ask_usd"] - row["best_bid_usd"]) / midpoint * 10_000
    assert math.isclose(row["midpoint_usd"], midpoint, rel_tol=0, abs_tol=1e-12)
    assert math.isclose(row["spread_bps"], spread, rel_tol=0, abs_tol=1e-10)
    assert row["provider_snapshot_timestamp_utc"] is None
    assert row["quote_components_same_event_sequence_established"] is False
    assert row["last_trade_usd"] < row["best_bid_usd"] < row["best_ask_usd"]


def test_okx_provider_snapshot_timestamp_and_spot_arithmetic_are_exact():
    row = load_artifact()["spot_observations"][1]
    parsed = datetime.fromisoformat(row["provider_snapshot_timestamp_utc"].replace("Z", "+00:00"))
    assert parsed.astimezone(timezone.utc).isoformat() == "2026-11-06T17:57:25.077000+00:00"
    assert int(parsed.timestamp() * 1000) == row["provider_timestamp_epoch_ms"] == 1793987845077
    midpoint = (row["best_bid_usdt"] + row["best_ask_usdt"]) / 2
    spread = (row["best_ask_usdt"] - row["best_bid_usdt"]) / midpoint * 10_000
    assert math.isclose(row["midpoint_usdt"], midpoint, rel_tol=0, abs_tol=1e-12)
    assert math.isclose(row["spread_bps"], spread, rel_tol=0, abs_tol=1e-10)
    assert row["last_trade_event_timestamp_exposed"] is False
    assert row["quote_components_same_event_sequence_established"] is False
    assert row["last_trade_usdt"] < row["best_bid_usdt"] < row["best_ask_usdt"]


def test_same_venue_snapshot_change_is_not_mislabeled_as_realized_return():
    row = load_artifact()["same_venue_snapshot_comparison"]
    computed = (row["current_last_trade_usdt"] / row["prior_last_trade_usdt"] - 1) * 100
    assert row["venue"] == "OKX"
    assert row["elapsed_seconds"] == 3910.898
    assert math.isclose(row["snapshot_to_snapshot_last_price_change_pct"], computed, rel_tol=0, abs_tol=1e-10)
    assert row["status"] == "OBSERVED_SAME_VENUE_SNAPSHOT_CHANGE_NOT_EXECUTABLE_RETURN"
    assert "not an exact realized return" in row["limitation"]


def test_derivatives_coverage_gap_is_preserved_not_averaged():
    data = load_artifact()["derivatives"]
    trad = data["tradradar"]
    alpha = data["alpha_finance"]
    assert trad["open_interest_7_venues_headline_usd"] == 1_920_000_000
    assert trad["open_interest_venue_row_sum_usd"] == 1_922_260_000
    assert trad["open_interest_change_24h_pct"] == -1.4
    assert trad["long_liquidations_usd"] > trad["short_liquidations_usd"]
    assert alpha["all_venue_open_interest_usd"] == 2_780_000_000
    assert data["reconciliation"]["headline_oi_difference_usd"] == 860_000_000
    assert data["reconciliation"]["aggregation"] == "not_averaged"
    assert data["reconciliation"]["status"] == "COVERAGE_AND_METHODOLOGY_DIFFERENCE_UNRESOLVED"


def test_etf_holdings_delta_is_not_treated_as_ap_cash_flow_or_nov6_flow():
    row = load_artifact()["etf_holdings_flow"]
    assert row["settled_data_through"] == "2026-11-05"
    assert row["nov5_holdings_delta_xrp"] == 110_214
    assert row["nov2_to_nov5_net_holdings_delta_xrp"] == -149_487
    assert row["settled_trading_days"] == 4
    assert "not direct AP cash creations or redemptions" in row["limitation"]
    assert "issuer-reported XRP holdings" in row["method"]


def test_bls_macro_context_has_no_false_xrp_event_causal_join():
    data = load_artifact()["macro_event"]
    assert data["bls_release_time_utc"] == "2026-11-06T13:30:00Z"
    assert data["payroll_change_october"] == 165_000
    assert data["unemployment_rate_pct"] == 4.1
    assert data["august_september_revisions_combined"] == 84_000
    assert data["market_implied_december_fed_hike_probability_pct"] == 78
    assert "no causal XRP event-study result" in data["interpretation_limit"]


def test_no_directional_forecast_or_external_action_is_authorized():
    data = load_artifact()
    assert data["forecast_status"]["status"] == "NOT_ISSUED"
    assert data["forecast_status"]["directional_forecast_issued"] is False
    assert data["model_eligibility"]["eligible"] is False
    assert data["safety"]["paper_trade_executed"] is False
    assert data["safety"]["real_money_action"] is False
    assert data["safety"]["external_submission"] is False
    assert data["safety"]["external_ai_data_transfer"] is False


def test_fuelmaps_spot_depth_preserves_snapshot_coverage_and_cancel_risk():
    data = load_artifact()
    row = data["spot_depth_snapshot"]
    assert row["snapshot_time_utc"] == "2026-11-06T17:00:00Z"
    assert row["mid_usd"] == 1.1947
    assert row["venue_count"] == 6
    assert "fuelmaps_multi_venue_spot_depth_aggregator" in data["source_independence_groups"]
    assert row["bands"] == [
        {"within_pct": 0.5, "bids_usd": 8_600_000, "asks_usd": 6_200_000, "bid_share_pct": 58.0, "venues_covering": 6},
        {"within_pct": 1, "bids_usd": 13_200_000, "asks_usd": 9_600_000, "bid_share_pct": 57.8, "venues_covering": 6},
        {"within_pct": 2, "bids_usd": 18_300_000, "asks_usd": 10_000_000, "bid_share_pct": 64.5, "venues_covering": 6},
        {"within_pct": 5, "bids_usd": 25_900_000, "asks_usd": 13_000_000, "bid_share_pct": 66.5, "venues_covering": 6},
        {"within_pct": 10, "bids_usd": 32_000_000, "asks_usd": 15_900_000, "bid_share_pct": 66.8, "venues_covering": 5},
    ]
    method = row["method"]
    assert method["market_type"] == "spot_only"
    assert method["excluded_venues"] == ["Binance", "Bitget"]
    assert method["hidden_and_iceberg_orders_included"] is False
    assert method["resting_orders_can_be_cancelled"] is True
    assert method["hourly_column"] == "average_of_one_minute_book_snapshots"
    assert "not fillable depth" in row["interpretation_limit"]
    source = next(x for x in data["source_registry"] if x["source_id"] == "FUELMAPS_XRP_SPOT_BOOK_20261106T1700Z")
    assert hashlib.sha256(source["excerpt"].encode("utf-8")).hexdigest() == source["receipt"]["digest"]
