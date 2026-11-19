import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research/xrp_intelligence/20261119T2049Z-run46-sbi-evernorth-circle-market-reconciliation.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_sbi_actual_xrp_label_is_not_sbi_holdings():
    data = load_artifact()
    slide = data["capital_and_ownership"]["sbi_ripple_supply_slide"]
    assert slide["ripple_actual_xrp_outside_escrow_approx"] == 5_100_000_000
    assert slide["ripple_xrp_under_escrow_approx"] == 33_200_000_000
    assert "not an SBI Holdings balance" in slide["semantic_guard"]
    assert data["capital_and_ownership"]["sbi_holdings"]["ripple_equity_stake_pct"] == 9


def test_evernorth_sec_starting_treasury_reconciles():
    data = load_artifact()["capital_and_ownership"]["evernorth_sec_reconciliation"]
    post = data["post_close"]
    assert post["xrp_transferred_to_pathfinder_xrp"] == 346_484_972
    assert post["ripple_contribution_to_pathfinder_xrp"] == 126_791_458
    assert post["reported_starting_combined_treasury_xrp"] == 473_276_430
    assert (
        post["xrp_transferred_to_pathfinder_xrp"]
        + post["ripple_contribution_to_pathfinder_xrp"]
        == post["reported_starting_combined_treasury_xrp"]
    )
    assert data["cash_purchased_xrp"] == 84_365_876
    assert data["cash_purchase_recorded_cost_usd"] == 214_000_000
    assert round(data["cash_purchase_average_usd_per_xrp"], 5) == 2.53657
    assert data["sbi_specific_share_of_cash_purchase_xrp"] is None


def test_evernorth_accounting_value_is_not_market_value():
    data = load_artifact()["capital_and_ownership"]["evernorth_sec_reconciliation"]
    assert data["pre_close_historical_cost_usd"] == 846_575_043
    assert data["pre_close_carrying_value_after_impairment_usd"] == 341_887_231
    assert data["cumulative_impairment_usd"] == 504_687_812
    assert data["impairment_2025_usd"] == 233_650_642
    assert data["impairment_2026_ytd_usd"] == 271_037_170
    assert data["impairment_q3_2026_usd"] == 6_891_073
    assert (
        data["pre_close_historical_cost_usd"]
        - data["cumulative_impairment_usd"]
        == data["pre_close_carrying_value_after_impairment_usd"]
    )
    assert data["pre_close_carrying_value_after_impairment_usd"] < data["pre_close_historical_cost_usd"]


def test_onchain_tracker_discrepancy_is_quarantined():
    tracker = load_artifact()["capital_and_ownership"]["evernorth_onchain_counter_evidence"]
    assert tracker["attributed_wallets_xrp"] == 103_129_905
    assert tracker["moved_outside_attributed_set_xrp"] == 370_346_663
    assert tracker["arithmetic_overage_xrp"] == 200_138
    assert tracker["status"] == "PROVISIONAL_STALE_SECONDARY"
    assert tracker["model_eligible"] is False


def test_circle_usdc_supply_change_is_not_xrp_flow():
    data = load_artifact()["circle_and_stablecoin_rails"]["usdc_circulation"]
    assert data["sec_end_period_2026_09_30_usd"] == 73_879_000_000
    assert data["circle_page_2026_11_16_usd"] == 68_000_000_000
    assert data["change_usd"] == -5_879_000_000
    assert round(data["change_pct"], 2) == -7.96
    assert "not a direct XRP flow" in data["interpretation"]


def test_exchange_wallet_and_etf_definitions_are_preserved():
    market = load_artifact()["market_observations"]
    exchange = market["exchange_wallets"]
    etfs = market["etfs"]
    assert exchange["total_xrp"] == 22_180_000_000
    assert exchange["tradable_float"] is False
    assert exchange["sbi_vc_trade_xrp"] == 56_300_000
    assert exchange["sbi_vc_trade_cold_share_pct"] == 99
    assert etfs["reported_total_xrp_six_spot_plus_BITW"] == 1_184_150_000
    assert etfs["reported_net_holdings_change_xrp"] == -5_310_000
    assert etfs["gxrp_excluded_from_flow_total_due_data_gap"] is True
    assert etfs["flow_semantics"].startswith("Issuer-reported XRP holdings delta")


def test_no_raw_receipts_or_directional_forecast_are_fabricated():
    data = load_artifact()
    assert data["model_eligible"] is False
    assert data["raw_capture"]["raw_http_bytes_captured"] is False
    assert data["raw_capture"]["raw_response_sha256"] is None
    assert data["raw_capture"]["immutable_receipt_id"] is None
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["source_quality"]["sha256_receipts_created"] == 0
    assert data["source_quality"]["point_in_time_features_written"] == 0
    assert all(
        source["raw_response_sha256"] is None and source["receipt_id"] is None
        for source in data["source_registry"]
    )
