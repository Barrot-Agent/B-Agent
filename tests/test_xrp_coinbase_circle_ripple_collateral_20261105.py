from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261105T101400Z-coinbase-circle-ripple-collateral-distribution-reconciliation.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_coinbase_circle_usdc_economics_are_direct_but_not_xrp_flows():
    item = load()["coinbase_circle_economics"]
    assert item["average_usdc_held_in_coinbase_products_usd"] == 22_000_000_000
    assert item["average_usdc_market_cap_usd"] == 73_000_000_000
    assert item["average_product_balance_share_pct"] == 30
    assert item["coinbase_q3_stablecoin_revenue_usd"] == 306_905_000
    assert item["circle_agreement_status"] == "renewed_on_same_terms_as_prior_arrangement"
    assert item["model_eligible"] is False


def test_circle_distribution_formula_preserves_issuer_retention_and_ecosystem_split():
    formula = load()["coinbase_circle_economics"]["circle_distribution_formula"]
    assert formula["issuer_retention_applied_first"] is True
    assert "USDC held on Coinbase platform" in formula["on_platform_allocation_basis"]
    assert "half of remaining payment base" in formula["ecosystem_growth_allocation"]
    assert "executory contract" in formula["accounting"]


def test_coinbase_recognized_collateral_reconciles_without_assigning_other_assets_to_xrp():
    item = load()["coinbase_collateral_and_capital"]
    lending = item["recognized_lending_collateral_usd"]
    derivatives = item["recognized_derivatives_collateral_usd"]
    assert lending["crypto_assets_total"] == 997_557_000
    assert lending["crypto_asset_components"]["bitcoin"] == 920_649_000
    assert lending["crypto_asset_components"]["ethereum"] == 67_005_000
    assert lending["crypto_asset_components"]["other_crypto_assets"] == 9_903_000
    assert derivatives["total"] == 301_943_000
    assert lending["crypto_assets_total"] + derivatives["total"] == item["balance_sheet_crypto_assets_held_as_collateral_usd"] == 1_299_500_000
    assert lending["total_recognized_lending_collateral"] == 1_009_297_000


def test_unrecognized_customer_collateral_and_company_pledges_remain_separate():
    item = load()["coinbase_collateral_and_capital"]
    customer = item["unrecognized_customer_collateral_usd"]
    pledged = item["coinbase_assets_pledged_for_short_term_borrowings_usd"]
    assert customer["crypto_assets"] == 2_804_112_000
    assert customer["fiat_and_payment_stablecoins"] == 480_450_000
    assert customer["total"] == 3_284_562_000
    assert customer["asset_level_crypto_breakdown_disclosed"] is False
    assert pledged["payment_stablecoins"] == 58_678_000
    assert pledged["crypto_assets"] == 375_485_000
    assert pledged["total"] == 434_163_000
    assert pledged["asset_level_crypto_breakdown_disclosed"] is False


def test_no_xrp_specific_collateral_claim_is_inferred_from_aggregated_other_assets():
    item = load()["coinbase_collateral_and_capital"]["xrp_specific_disclosure"]
    assert item["literal_xrp_mention_found_in_10q"] is False
    assert item["xrp_collateral_amount_disclosed"] is False
    assert item["xrp_derivatives_collateral_amount_disclosed"] is False
    assert "does not identify it" in item["conclusion"]


def test_coinbase_rlusd_network_availability_is_separate_from_future_collateral():
    item = load()["coinbase_ripple_rlusd_distribution"]
    assert item["networks_at_launch"] == ["XRPL", "Base", "Ethereum"]
    assert item["products"] == ["Coinbase Prime", "Coinbase Exchange", "Coinbase Retail app"]
    assert item["usd_conversion_ratio"] == 1
    assert item["coinbase_global_exchange_collateral_support"] == "FUTURE_NOT_LIVE_AT_LAUNCH"
    assert item["actual_rlusd_volume_disclosed"] is False
    assert item["xrp_bridge_volume_disclosed"] is False


def test_coinbase_security_statement_is_company_reported_not_independent_assurance():
    source = next(x for x in load()["source_registry"] if x["id"] == "coinbase_customer_asset_security_statement_20261104")
    assert source["source_type"] == "primary_company_security_statement"
    assert any("company representations" in x for x in source["limitations"])
    assert source["model_eligible"] is False


def test_rendered_corporate_sources_are_ineligible_and_no_forecast_is_issued():
    data = load()
    assert data["model_eligible"] is False
    assert data["forecast_issued"] is False
    assert data["predictive_admission"]["forecast_status"] == "NOT_ISSUED"
    assert data["source_capture_policy"]["raw_http_bytes_captured"] is False
    assert all(source["raw_content_sha256"] is None for source in data["source_registry"])
    assert all(source["model_eligible"] is False for source in data["source_registry"])


def test_coinbase_circle_equity_history_is_separate_from_current_ownership():
    item = load()["coinbase_circle_equity_relationship"]
    historical = item["historical_transaction"]
    current = item["continuing_relationship_as_of_2026_09_30"]
    assert historical["date"] == "2023-08"
    assert historical["consideration_usd"] == 209_900_000
    assert historical["circle_common_shares_issued_approx"] == 8_400_000
    assert historical["centre_dissolved_date"] == "2023-12"
    assert current["coinbase_q3_2026_10q_mentions_fair_value_remeasurement_of_its_investment_in_circle_after_ipo"] is True
    assert current["current_share_count_disclosed"] is False
    assert current["current_ownership_percentage_disclosed"] is False
    assert current["exact_circle_investment_fair_value_disclosed"] is False
    assert current["q3_2026_coinbase_investment_gain_loss_line_usd"] == -39_231_000
    assert "does not attribute the entire line" in current["gain_loss_attribution_rule"]
    assert item["model_eligible"] is False


def test_circle_q2_distribution_cost_change_is_year_over_year_not_quarter_over_quarter():
    item = load()["coinbase_circle_economics"]["circle_q2_2026_update"]
    assert item["year_over_year_coinbase_distribution_cost_change_usd"] == -7_700_000
    assert "versus" in item["comparison_period"]
    assert "decrease in Coinbase share" in item["stated_driver"]
    assert "quarter_over_quarter_coinbase_distribution_cost_change_usd" not in item


def test_circle_s1a_filing_date_and_coinbase_security_source_are_corrected():
    data = load()
    s1 = next(x for x in data["source_registry"] if x["id"] == "circle_centre_acquisition_sec_s1a_20250418")
    security = next(x for x in data["source_registry"] if x["id"] == "coinbase_customer_asset_security_statement_20261104")
    assert s1["publication_date"] == "2025-04-18"
    assert "000119312525084832" in s1["url"]
    assert "landing/company" in security["url"]
