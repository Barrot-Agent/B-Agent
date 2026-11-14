import json
from pathlib import Path


ARTIFACT_PATH = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261105T123059Z-xrp-market-derivatives-circle-sbi-binance-network-update.json"
)


def _artifact():
    return json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))


def test_spot_snapshot_reconciles_spread_and_keeps_single_level_scope():
    data = _artifact()["market_snapshot"]
    assert data["best_bid_usd"] < data["best_ask_usd"]
    midpoint = (data["best_bid_usd"] + data["best_ask_usd"]) / 2
    expected = (data["best_ask_usd"] - data["best_bid_usd"]) / midpoint * 10_000
    assert abs(data["displayed_spread_bps"] - expected) < 1e-12
    assert data["best_ask_displayed_size_xrp"] > data["best_bid_displayed_size_xrp"]
    assert "One top-of-book level only" in data["interpretation_limits"][1]
    assert data["daily_open_semantics"].endswith("not a 24-hour open.")


def test_derivatives_disagreement_is_preserved_without_averaging():
    data = _artifact()["derivatives"]
    disagreement = data["unresolved_same_venue_disagreement"]
    expected = (
        disagreement["tradradar_open_interest_usd"]
        - disagreement["seandra_open_interest_usd"]
    ) / disagreement["seandra_open_interest_usd"] * 100
    assert abs(disagreement["tradradar_above_seandra_pct"] - expected) < 1e-10
    assert disagreement["absolute_difference_usd"] == 89_000_000
    assert "Do not average" in disagreement["resolution"]
    assert "account-count ratio, not notional exposure" in data["observations"][0]["long_short_ratio_scope"]


def test_etf_flow_scope_and_product_exclusions_are_explicit():
    data = _artifact()["etf_flows"]
    assert data["data_as_of"] == "2026-11-04"
    assert data["net_flow_nov_2_to_4_xrp"] == -259_701
    assert data["net_flow_as_pct_of_total_holdings"] < 0
    warnings = " ".join(data["scope_warnings"])
    assert "BITW" in warnings
    assert "GXRP" in warnings
    assert "not an issuer-reported AP cash" in data["row_semantics"]["flow_status_computed"]


def test_circle_reserve_and_arc_revenue_are_not_conflated():
    data = _artifact()["institutional_and_network"]["circle_q3_2026"]
    assert data["average_usdc_circulation_usd"] == 73_300_000_000
    assert data["reserve_income_yoy_pct"] == -8
    assert data["other_revenue_usd"] == 207_000_000
    assert data["arc_token_presale_revenue_usd"] == 182_000_000
    assert data["circle_payments_network_annualized_tpv_usd"] == 41_300_000_000
    assert data["tazapay_acquisition_status"].startswith("Definitive agreement signed")
    assert data["model_eligible"] is False


def test_coinbase_usdc_and_rlusd_collateral_status_are_separated():
    network = _artifact()["institutional_and_network"]
    coinbase = network["coinbase_q3_2026"]
    rlusd = network["coinbase_rlusd_distribution"]
    assert coinbase["average_usdc_held_in_coinbase_products_usd"] == 22_000_000_000
    assert coinbase["average_usdc_held_yoy_pct"] == 49
    assert "Future availability" in rlusd["global_exchange_rlusd_collateral"]
    assert "not live at launch" in rlusd["global_exchange_rlusd_collateral"]


def test_sbi_distribution_channels_are_not_misclassified_as_xrp_spot_buys():
    network = _artifact()["institutional_and_network"]
    card = network["sbi_visa_crypto_rewards"]
    rlusd = network["sbi_vctrade_rlusd"]
    assert "XRP" in card["supported_reward_assets"]
    assert "not evidence of direct card-funded XRP purchases" in card["interpretation_limits"][0]
    assert rlusd["network_scope"]["official_release"].endswith("does not name the supported chain.")
    assert "Ethereum-only support at launch" in rlusd["network_scope"]["secondary_launch_reporting"]


def test_binance_network_notice_does_not_claim_native_xrp_withdrawals_resumed():
    data = _artifact()["institutional_and_network"]["binance_post_incident_withdrawal_networks"]
    assert data["bsc_network_asset_list_includes"] == "XRP"
    assert data["xrp_ledger_network_asset_string"] == "RLUSDFD"
    assert any("does not establish native XRPL XRP withdrawal status" in item for item in data["interpretation_limits"])


def test_research_snapshot_remains_ineligible_and_issues_no_forecast():
    data = _artifact()
    assert data["raw_capture"]["raw_source_bytes_preserved"] is False
    assert data["raw_capture"]["sha256"] is None
    assert data["raw_capture"]["independent_timestamp_anchor"] is False
    assert data["model_eligibility"]["eligible_sources"] == 0
    assert data["model_eligibility"]["directional_forecast_issued"] is False
    assert data["institutional_and_network"]["coinbase_q3_2026"]["model_eligible"] is False
