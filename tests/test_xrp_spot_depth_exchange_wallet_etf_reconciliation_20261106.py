from __future__ import annotations

import json
import math
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T030136Z-xrp-spot-depth-exchange-wallet-etf-reconciliation.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_kraken_spot_snapshot_preserves_utc_open_vwap_and_spread_semantics():
    item = load_artifact()["market_snapshot"]["kraken_spot"]
    midpoint = (item["best_bid_usd"] + item["best_ask_usd"]) / 2
    assert math.isclose(
        item["spread_bps"],
        (item["best_ask_usd"] - item["best_bid_usd"]) / midpoint * 10_000,
        abs_tol=1e-9,
    )
    assert item["provider_event_timestamp_utc"] is None
    assert math.isclose(item["last_vs_utc_day_open_percent"], 0.794578947804947, abs_tol=1e-9)
    assert item["last_vs_24h_vwap_percent"] < 0
    assert "not a trend reversal" in item["interpretation"]


def test_tradradar_derivatives_preserve_venue_sum_and_lower_bound_semantics():
    item = load_artifact()["market_snapshot"]["tradradar_perpetuals"]
    assert sum(item["exchange_open_interest_usd"].values()) == 1_924_480_000
    assert item["open_interest_usd"] == 1_920_000_000
    assert item["liquidations_24h_lower_bound_usd"] == 14_900_000
    assert item["long_liquidations_usd"] > item["short_liquidations_usd"]
    assert item["displayed_delay_minutes"] == 15


def test_coinfuty_futures_depth_is_not_mislabeled_as_live_spot_depth():
    item = load_artifact()["market_snapshot"]["coinfuty_perpetual_orderbook"]
    bands = {row["within_percent"]: row for row in item["depth_bands_usd_millions"]}
    assert bands[2]["bids"] == 80.45
    assert bands[2]["asks"] == 72.51
    assert item["live_book_exchange_count"] == "0/5 at rendered page capture"
    assert item["snapshot_timestamp_utc"] is None
    assert "futures" in item["interpretation"]
    assert item["model_eligible"] if "model_eligible" in item else True


def test_exchange_wallet_balances_are_not_treated_as_tradable_float():
    item = load_artifact()["market_snapshot"]["xrp_insights_exchange_wallets"]
    assert item["attributed_xrpl_wallet_balance_xrp"] == 22_280_000_000
    assert item["wallets"] == 701 and item["exchanges"] == 24
    assert item["same_wallet_7d_change_xrp"] == -301_500_000
    assert item["same_wallet_30d_change_xrp"] == -226_900_000
    assert item["non_customer_or_wrapped_reserves_xrp"] == 486_900_000
    assert item["reserve_components_xrp"]["coinbase_cbxrp_base"] == 150_000_000
    assert "not proof of customer withdrawals" in item["interpretation"]


def test_etf_provider_universes_and_vintages_remain_separate():
    item = load_artifact()["market_snapshot"]["etf_flows"]
    insights = item["xrp_insights"]
    alpha = item["alpha_finance"]
    keyhole = item["cryptokeyhole"]
    assert insights["settled_net_flow_xrp"] == -259_701
    assert insights["latest_row_status"] == "provisional_until_next_morning_resettle"
    assert alpha["last_30_sessions_net_flow_usd"] == 78_900_000
    assert alpha["nov4_net_flow_usd"] == 0
    assert keyhole["nov3_net_flow_xrp"] == -3_339
    assert keyhole["nov4_status"] == "partial_3_of_4_funds"
    assert "Do not average" in load_artifact()["source_independence"]["rule"]


def test_etf_aggregator_internal_inconsistencies_are_quarantined():
    item = load_artifact()["market_snapshot"]["etf_flows"]
    corp = item["corpstacking"]
    investor = item["thexrpinvestor"]
    assert corp["headline_fund_count"] == 10
    assert corp["included_nciq_index_etf"] is True
    assert corp["methodology_says_index_funds_excluded"] is True
    assert corp["status"] == "QUARANTINED_INTERNAL_COUNT_AND_PRODUCT_SCOPE_INCONSISTENCY"
    assert investor["tracker_product_count"] == 12
    assert investor["category_sum"] == 11
    assert investor["tracker_aum_usd"] != investor["companion_flows_page_aum_usd"]
    assert investor["status"] == "QUARANTINED_INTERNAL_PAGE_DISAGREEMENT"


def test_all_sources_and_observations_remain_model_ineligible():
    item = load_artifact()
    ids = [source["source_id"] for source in item["source_registry"]]
    assert len(ids) == len(set(ids))
    assert item["model_eligibility"]["eligible"] is False
    assert item["model_eligibility"]["forecast_issued"] is False
    assert item["source_capture_policy"]["raw_source_bytes_preserved"] is False
    assert len(item["competing_hypotheses"]) >= 6
    assert len(item["model_eligibility"]["reasons"]) >= 8
