from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261106T160035Z-xrp-market-exchange-flow-stablecoin-reconciliation.json"


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_source_excerpt_receipts_are_reproducible_and_scoped():
    data = load_artifact()
    assert len(data["source_registry"]) == 13
    for source in data["source_registry"]:
        receipt = source["receipt"]
        assert receipt["algorithm"] == "SHA-256"
        assert hashlib.sha256(source["excerpt"].encode("utf-8")).hexdigest() == receipt["digest"]
        assert "not byte-complete" in receipt["scope"]
    groups = data["source_independence_groups"]
    assert "xrp_insights_public_data_aggregator" in groups
    assert data["source_registry"][4]["independence_group"] == data["source_registry"][6]["independence_group"]


def test_kraken_spot_quote_arithmetic_and_timestamp_limit_are_explicit():
    row = load_artifact()["spot_market"]
    expected = (row["best_ask_usd"] - row["best_bid_usd"]) / ((row["best_ask_usd"] + row["best_bid_usd"]) / 2) * 10000
    assert math.isclose(row["spread_bps"], expected, rel_tol=0, abs_tol=1e-8)
    assert row["last_trade_usd"] >= row["best_bid_usd"]
    assert row["last_trade_usd"] <= row["best_ask_usd"]
    assert row["provider_event_timestamp_utc"] is None
    assert row["quote_consistency"]["same_event_time_established"] is False


def test_tradradar_venue_oi_reconciles_without_merging_universes():
    row = load_artifact()["derivatives"]
    assert sum(row["venue_open_interest_usd"].values()) == row["venue_open_interest_row_sum_usd"]
    assert row["venue_open_interest_row_sum_usd"] == 1_904_610_000
    assert row["liquidations_24h_lower_bound_usd"] == 19_190_000
    assert row["long_liquidations_usd"] > row["short_liquidations_usd"]
    assert row["long_account_share_pct"] == 80
    assert "notional exposure" in row["limitations"][2]


def test_fuelmaps_depth_arithmetic_and_missing_venue_coverage_are_preserved():
    row = load_artifact()["order_book_depth"]["fuelmaps"]
    assert row["snapshot_time_utc"] == "2026-11-06T09:00:00Z"
    assert {"Binance", "Bitget"}.issubset(set(row["excluded_venues"]))
    for level in row["levels"]:
        share = level["bid_depth_usd"] / (level["bid_depth_usd"] + level["ask_depth_usd"]) * 100
        assert abs(share - level["bid_share_pct"]) < 0.15
    assert next(x for x in row["levels"] if x["band"] == "10%")["venues_reporting"] == 5


def test_edgeornot_mixed_spot_perp_depth_is_not_comparable_to_fuelmaps():
    data = load_artifact()["order_book_depth"]
    assert data["edgeornot"]["market_scope"] == "Binance spot and OKX perpetual combined"
    assert data["comparability"]["fuelmaps_and_edgeornot_directly_comparable"] is False
    assert "Different venue coverage" in data["comparability"]["reason"]


def test_exchange_balance_same_wallet_method_and_reserve_discrepancy_are_retained():
    row = load_artifact()["exchange_balances"]
    assert row["attributed_xrp_ledger_wallet_balance_xrp"] == 22_340_000_000
    assert row["same_wallet_change_7d_xrp"] == -34_700_000
    assert row["same_wallet_change_30d_xrp"] == -152_600_000
    assert row["naive_total_change_including_new_wallets_xrp"] == 359_400_000
    assert row["newly_tracked_wallet_balance_xrp"] == 512_000_000
    conflict = row["wrapped_and_noncustomer_reserve_reconciliation"]
    assert conflict["binance_peg_reserve_table_value_xrp"] - conflict["binance_peg_reserve_methodology_value_xrp"] == 1_600_000
    assert conflict["status"] == "SOURCE_INTERNAL_DISCREPANCY_UNRESOLVED"
    assert "not tradable float" in row["methodology"]


def test_trackwhale_large_transfer_flow_is_not_mislabeled_as_all_exchange_flow():
    row = load_artifact()["exchange_flows"]
    rounded_net = row["exchange_inflows_xrp"] - row["exchange_outflows_xrp"]
    assert abs(rounded_net - row["reported_net_exchange_flow_xrp"]) <= 15_000
    assert row["reported_net_exchange_flow_xrp"] < 0
    assert row["tracked_large_transfers"] == 77
    assert any("not a complete ledger flow census" in item for item in row["limitations"])
    assert any("not proof of sales" in item for item in row["limitations"])


def test_etf_provider_universes_and_partial_vintages_are_not_averaged():
    row = load_artifact()["etf_flows"]
    assert row["xrp_insights"]["nov5_net_holdings_change_xrp"] == 110_214
    assert row["cryptoetf_today"]["nov5_net_flow_usd"] == 0
    assert row["cryptoetf_today"]["funds_reported"] == 5
    assert row["cryptokeyhole"]["funds_reported"] == 3
    assert row["cryptokeyhole"]["funds_in_universe"] == 4
    assert row["reconciliation"]["values_comparable"] is False
    assert row["reconciliation"]["direct_cash_creation_redemption_observed"] is False


def test_xrpl_stablecoin_supply_is_not_treated_as_payment_volume():
    row = load_artifact()["stablecoins"]
    assert row["total_market_cap_usd"] == 987_230_000
    assert row["rlusd"]["market_cap_usd"] == 897_010_000
    assert math.isclose(row["rlusd"]["market_cap_usd"] / row["total_market_cap_usd"] * 100, row["rlusd"]["dominance_pct"], abs_tol=0.02)
    assert row["change_30d_pct"] == -26.22
    assert any("not transaction volume" in item for item in row["limitations"])


def test_bls_release_is_observed_macro_data_not_an_xrp_causal_claim():
    row = load_artifact()["macro"]
    assert row["release_time_utc"] == "2026-11-06T13:30:00Z"
    assert row["nonfarm_payroll_change"] == 165_000
    assert row["unemployment_rate_pct"] == 4.1
    assert row["average_hourly_earnings_change_mom_pct"] == 0.4
    assert row["combined_revisions"] == 84_000
    assert "not an XRP-specific causal feature" in row["interpretation"]


def test_xrpl_lending_amendments_remain_below_activation_and_collateral_is_not_claimed():
    row = load_artifact()["xrpl_governance"]
    assert row["validators_heard"] == 35
    assert row["required_yes_votes"] == 29
    assert row["votes_yes"]["SingleAssetVault"] == 23
    assert row["votes_yes"]["LendingProtocol"] == 21
    assert row["active_14_day_countdowns"] == 0
    assert row["fixCleanup3_4_0"]["status"] == "ENABLED"
    assert "not evidence of borrower collateral" in row["lending_design_boundary"]["vault_deposits"]
    assert "No live" in row["lending_design_boundary"]["live_use_evidence"]


def test_competing_hypotheses_keep_disconfirming_evidence_and_no_causality():
    data = load_artifact()
    assert len(data["competing_hypotheses"]) == 7
    assert all(row["supporting"] and row["disconfirming"] for row in data["competing_hypotheses"])
    assert data["model_eligibility"]["eligible"] is False


def test_no_directional_forecast_or_trade_is_created():
    data = load_artifact()
    assert data["forecast_status"]["status"] == "NOT_ISSUED"
    assert data["forecast_status"]["target"] is None
    assert data["forecast_status"]["horizon"] is None
    assert data["forecast_status"]["probabilities"] is None
    assert data["safety"]["paper_trade_executed"] is False
    assert data["safety"]["real_money_action"] is False
    assert data["safety"]["external_submission"] is False
