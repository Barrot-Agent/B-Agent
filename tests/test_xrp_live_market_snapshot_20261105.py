from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261105T100426Z-live-market-etf-derivatives-macro-snapshot.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_kraken_spot_quote_arithmetic_preserves_last_trade_separately():
    spot = load()["market_snapshot"]["spot"]
    midpoint = (spot["best_bid_usd"] + spot["best_ask_usd"]) / 2
    spread_bps = (spot["best_ask_usd"] - spot["best_bid_usd"]) / midpoint * 10000
    assert spot["best_bid_usd"] <= spot["best_ask_usd"]
    assert math.isclose(spot["midpoint_usd"], midpoint, rel_tol=0, abs_tol=1e-12)
    assert math.isclose(spot["displayed_spread_bps"], spread_bps, rel_tol=0, abs_tol=1e-12)
    assert spot["last_trade_usd"] == 1.318
    assert spot["last_trade_usd"] > spot["best_ask_usd"]
    assert spot["volume_24h_xrp"] > 0
    assert spot["low_24h_usd"] <= spot["high_24h_usd"]
    assert spot["model_eligible"] is False


def test_binance_premium_index_keeps_raw_funding_period_unconfirmed():
    item = load()["market_snapshot"]["derivatives"]["binance_premium_index"]
    expected_basis = (item["mark_price_usdt"] / item["index_price_usdt"] - 1) * 10000
    assert math.isclose(item["mark_index_basis_bps"], expected_basis, rel_tol=0, abs_tol=1e-12)
    assert item["last_funding_rate_raw"] == 0.0001
    assert item["funding_interval_hours_confirmed"] is False
    assert item["source_event_time_utc"] == "2026-11-05T09:53:31Z"
    assert item["next_funding_time_utc"] == "2026-11-05T16:00:00Z"
    assert item["model_eligible"] is False


def test_tradradar_exchange_open_interest_reconciles_without_rounding_liquidations():
    item = load()["market_snapshot"]["derivatives"]["tradradar_seven_exchange"]
    assert sum(item["exchange_open_interest_usd"].values()) == item["exchange_sum_open_interest_usd"] == 2067130000
    assert item["open_interest_usd_displayed"] == 2070000000
    assert item["funding_oi_weighted_pct_per_8h"] == 0.01
    assert item["long_short_account_ratio"] == 3.22
    assert item["long_account_share_pct"] == 76.3
    assert item["short_liquidations_usd_displayed"] > item["long_liquidations_usd_displayed"]
    assert item["short_liquidations_usd_displayed"] + item["long_liquidations_usd_displayed"] != item["liquidations_24h_minimum_usd"]
    assert item["model_eligible"] is False


def test_etf_holdings_delta_is_not_promoted_to_cash_creation_redemption():
    item = load()["market_snapshot"]["etf_flows"]
    assert item["data_as_of_date"] == "2026-11-03"
    assert item["latest_row_date"] == "2026-11-04"
    assert item["latest_row_status"] == "provisional"
    assert item["net_flow_xrp_nov2_nov3"] == -194875
    assert item["total_holdings_xrp_nov3"] == 1196405311
    assert "BITW" in item["fund_universe"]
    assert item["methodology"].startswith("Flows are day-over-day changes")
    assert any("reconstructed" in text.lower() for text in item["exclusions_and_reconstruction"])
    assert item["model_eligible"] is False


def test_stablecoin_custody_and_distribution_are_not_xrp_demand():
    data = load()["institutional_and_stablecoin"]
    circle = data["circle_usdc"]
    rlusd = data["rlusd"]
    bny = data["bny_ripple"]
    sbi = data["sbi_ripple"]
    assert circle["circulation_usd_as_of_2026_11_02"] == 69800000000
    assert circle["native_network_count"] == 38
    assert circle["xrpl_listed_as_supported_network"] is True
    assert rlusd["issuer"] == "Standard Custody & Trust Company, LLC"
    assert rlusd["circulation_usd_as_of_2026_10_29"] == 2627000000
    assert rlusd["reserve_funds_usd_as_of_2026_10_29"] == 2758600000
    assert bny["current_custody_support"] == ["XRP", "RLUSD"]
    assert bny["direct_rlusd_mint_redeem_through_bny"].startswith("INTENDED_FUTURE")
    assert bny["xrp_specific_assets_under_custody_disclosed"] is False
    assert bny["xrp_collateral_balance_disclosed"] is False
    assert sbi["japanese_rlusd_distribution_announced"] is True
    assert sbi["xrp_payment_volume_disclosed"] is False


def test_xrpl_validator_denominator_disagreement_is_preserved():
    item = load()["xrpl_protocol"]["lending_protocol_vote_snapshot"]
    assert item["xrplwin_denominator"] == 35
    assert item["xrpl_to_denominator"] == 36
    assert item["xrplwin_votes_for"] == 19
    assert item["xrplwin_votes_required"] == item["xrpl_to_votes_required"] == 29
    assert item["status"] == "VOTING_NOT_ACTIVATED"
    assert "not combined" in item["interpretation"]


def test_macro_relief_and_escalation_scenarios_remain_competing():
    macro = load()["macro_context"]
    assert macro["observations"]["brent_usd_per_barrel"] == 95.4
    assert macro["observations"]["us_10y_treasury_yield_pct"] == 4.87
    scenarios = {item["id"] for item in macro["competing_scenarios"]}
    assert scenarios == {"geopolitical_deescalation_risk_relief", "persistent_conflict_or_escalation"}
    assert all("No direct XRP causal relationship" in " ".join(item["limitations"]) for item in macro["competing_scenarios"] if item["id"] == "geopolitical_deescalation_risk_relief")


def test_rendered_source_vintages_remain_ineligible_and_no_forecast_is_issued():
    data = load()
    assert data["model_eligible"] is False
    assert data["forecast_issued"] is False
    assert data["predictive_admission"]["forecast_status"] == "NOT_ISSUED"
    assert data["source_capture_policy"]["raw_http_bytes_captured"] is False
    assert data["source_capture_policy"]["raw_content_sha256"] is None
    assert all(source["raw_content_sha256"] is None for source in data["source_registry"])
    assert all(source["model_eligible"] is False for source in data["source_registry"])


def test_run_start_identifier_is_not_misrepresented_as_source_retrieval_time():
    data = load()
    assert data["recorded_at_utc"] is None
    assert data["research_cutoff_utc"] is None
    assert data["recorded_on_date"] == "2026-11-05"
    assert "not an independently verified retrieval timestamp" in data["artifact_timestamp_semantics"]
    assert all(source["retrieved_at_utc"] is None for source in data["source_registry"])
    assert all("not exposed" in source["retrieval_time_note"] for source in data["source_registry"])
