from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261106-institutional-xrp-network-cbxrp-sbi-circle-ripple.json"


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def relationships() -> dict:
    return {item["id"]: item for item in load_artifact()["relationship_map"]}


def test_coinbase_circle_equity_is_stock_consideration_not_new_cash():
    item = relationships()["coinbase_circle_equity"]
    assert item["consideration"].find("$209.9M") >= 0
    assert item["post_ipo_position"]["shares"] == 7901791
    assert item["post_ipo_position"]["class_a_pct"] == 3.7
    assert item["post_ipo_position"]["voting_power_pct"] == 2.6
    assert any("not $209.9M of new cash" in text for text in item["limits"])


def test_coinbase_circle_usdc_distribution_is_dated_and_not_exclusive():
    item = relationships()["coinbase_circle_distribution"]
    assert item["usdc_circulation_share_pct"] == {
        "coinbase_platform": 21, "circle_platform": 10, "other_platforms": 69
    }
    assert item["binance_participant"]["upfront_payment_usd"] == 60250000
    assert item["binance_participant"]["treasury_balance_target_usd"] == 3000000000
    assert "2025-06-30" in item["distribution_snapshot_as_of"]


def test_sbi_circle_and_ripple_equity_are_not_xrp_token_holdings():
    data = relationships()
    circle = data["sbi_circle_equity"]
    ripple = data["sbi_ripple_equity"]
    assert circle["amount_usd"] == 50000000
    assert circle["split_usd"] == {"sbi_holdings": 25000000, "sbi_shinsei_bank": 25000000}
    assert ripple["reported_ownership_pct"] == 9
    assert any("not ownership of 9% of XRP supply" in text for text in ripple["limits"])


def test_sbi_rlusd_and_xrpl_research_are_not_production_xrp_settlement():
    data = relationships()
    assert data["sbi_vc_trade_rlusd"]["launch_date"] == "2026-06-24"
    assert "not XRP" in data["sbi_vc_trade_rlusd"]["limits"][0]
    assert data["sbi_ripple_asia_xrpl_research"]["status"] == "research_initiative_not_production"
    assert "No production settlement volume" in data["sbi_ripple_asia_xrpl_research"]["limits"][0]


def test_sbi_xrp_voucher_campaign_is_separate_from_unverified_june_pilot():
    data = relationships()
    official = data["sbi_shinsei_xrp_voucher"]
    pilot = data["sbi_shinsei_june_interest_pilot"]
    assert official["date"] == "2026-02-02"
    assert "JPY 20,000" in official["relationship"]
    assert pilot["status"] == "secondary_report_only"
    assert "No matching primary" in pilot["primary_confirmation"]


def test_jpysc_is_a_separate_yen_stablecoin_not_xrp():
    item = relationships()["sbi_jpysc"]
    assert item["launch_date"] == "2026-06-24"
    assert item["reserve_and_activity_snapshot_2026_09_07"]["short_term_jgb_investment_jpy"] == 10000000000
    assert item["reserve_and_activity_snapshot_2026_09_07"]["issuance_balance_jpy"] == 20100000000
    assert item["later_snapshot_2026_11_02"]["lending_balance_jpy_greater_than"] == 10000000000
    assert "not XRP" in item["limits"][0]


def test_coinbase_ripple_rlusd_collateral_is_not_claimed_live():
    item = relationships()["coinbase_ripple_rlusd"]
    assert item["launch_date"] == "2026-10-28"
    assert item["status"] == "live_distribution_integration"
    assert "will follow" in item["collateral_status"]
    assert "not XRP" in item["limits"][0]


def test_cbxrp_reserve_supply_and_custody_are_separated_from_spot_buying():
    item = relationships()["coinbase_cbxrp"]
    snap = item["proof_of_reserves_snapshot"]
    assert snap["xrp_reserves"] == 153022397.61
    assert snap["cbxrp_supply"] == 153020151.08
    assert snap["reserve_surplus_xrp"] == 2246.53
    assert snap["independent_audit"] is False
    assert any("does not prove a new spot purchase" in text for text in item["limits"])


def test_cbxrp_morpho_collateral_is_distinguished_from_coinbase_exchange():
    item = relationships()["cbxrp_morpho_collateral"]
    assert item["collateral_factor_pct"] == 86
    assert item["market_snapshot"]["combined_displayed_deposits_usd"] == 67700000
    assert item["market_snapshot"]["combined_displayed_borrowed_usd"] == 61620000
    assert any("not proof of new XRP purchases or Coinbase Global Exchange collateral support" in text for text in item["limits"])


def test_coinbase_xrp_etf_custody_and_ripple_prime_derivatives_are_separate():
    data = relationships()
    assert data["coinbase_xrp_etf_custody"]["status"] == "documented_institutional_custody"
    assert data["ripple_prime_coinbase_derivatives"]["status"] == "documented_institutional_derivatives_access"
    assert "not a Ripple–Coinbase equity partnership" in data["ripple_prime_coinbase_derivatives"]["limits"][0]


def test_circle_ripple_shared_bny_does_not_imply_direct_partnership():
    data = load_artifact()["network_conclusions"]["indirect_relationships"]
    assert "No direct Circle–Ripple partnership" in data["circle_ripple"]
    assert "not evidence of a direct Circle–Ripple partnership" in relationships()["circle_ripple_shared_bny"]["limits"][0]


def test_sbi_entities_and_regional_sbic_companies_are_not_conflated():
    entities = load_artifact()["entity_identity"]
    assert entities["sbi_holdings"]["type"] != entities["sbic_east_central_west"]["type"]
    assert "Not aliases" in entities["sbic_east_central_west"]["role"]
    assert "separate legal entity" in entities["sbi_shinsei_bank"]["role"]


def test_actual_capital_classification_excludes_vouchers_and_wrapping_from_spot_purchases():
    capital = load_artifact()["actual_capital_classification"]
    assert any("equity capital" in item for item in capital["direct_equity_capital"])
    assert any("promotional distributions" in item for item in capital["not_proven_spot_xrp_purchases"])
    assert any("not XRP purchases" in item for item in capital["not_proven_spot_xrp_purchases"])


def test_circle_and_sbi_source_independence_is_not_overstated():
    data = load_artifact()
    registry = {item["id"]: item for item in data["source_registry"]}
    assert registry["circle_s1_coinbase_equity_and_distribution"]["source_type"] == "primary_sec_filing"
    assert registry["sbi_ripple_and_circle_equity"]["source_type"] == "primary_company_announcement"
    assert registry["sbi_shinsei_june_pilot"]["source_type"] == "secondary_reporting_and_podcast"
    assert registry["sbi_rlusd_japan_listing"]["independence_group"] == "sbi_group_primary"
    assert data["quality_and_limits"]["june_10_sbi_shinsei_pilot_primary_confirmation"] is False
    assert data["forecast_status"]["directional_forecast_issued"] is False


def test_binance_circle_2026_equity_and_five_year_agreement_is_separate_from_2024_terms():
    data = relationships()
    item = data["circle_binance_2026"]
    assert item["equity_investment_usd"] == 100000000
    assert item["commercial_term_years"] == 5
    assert item["date"] == "2026-09-22"
    old = data["coinbase_circle_distribution"]["binance_participant"]
    assert old["status"].startswith("historical_2024_terms")
    assert "as the current 2026 Binance agreement" in old["limitation"]


def test_circle_q3_gross_mints_and_redemptions_are_not_net_capital():
    item = relationships()["circle_q3_2026_operating_metrics"]["metrics"]
    assert item["average_usdc_circulation_usd"] == 73300000000
    assert item["end_period_usdc_circulation_usd"] == 73900000000
    assert item["usdc_minted_gross_usd"] == 104000000000
    assert item["usdc_redeemed_gross_usd"] == 104000000000
    assert item["end_period_usdc_on_platform_usd"] == 13900000000
    assert item["circle_payments_network_annualized_tpv_usd"] == 41300000000


def test_coinbase_q3_circle_renewal_and_stablecoin_revenue_are_primary_filing_data():
    item = relationships()["coinbase_circle_distribution"]
    assert item["renewal_status"].find("renewed on the same terms") >= 0
    assert item["coinbase_q3_2026"]["stablecoin_revenue_usd"] == 306905000
    assert item["coinbase_q3_2026"]["arrangement_renewed"] == "same terms"


def test_coinbase_institutional_collateral_is_not_xrp_specific():
    item = relationships()["coinbase_institutional_collateral"]
    assert item["collateral_requirements_pct_range"] == [100, 250]
    assert item["recognized_crypto_collateral_fair_value_usd"] == 997557000
    assert item["customer_collateral_not_recognized_fair_value_usd"] == 3284600000
    assert item["counterparties_above_10pct_of_loan_receivables"] == 3
    assert item["xrp_specific_amount_disclosed"] is False
    assert item["measurement_period"] == "2026-09-30"
    assert "XRP-specific collateral balance" in item["limits"][0] or "XRP-specific" in item["asset_specificity"]
    assert "does not disclose an XRP-specific collateral balance" in item["asset_specificity"]


def test_circle_payment_metrics_preserve_annualized_and_pending_status():
    item = relationships()["circle_payment_rails_and_strategy"]
    assert "annualized" in item["limits"][0].casefold().lower()
    assert "pending regulatory approval" in item["limits"][1]
    assert "not XRPL" in item["limits"][2]
