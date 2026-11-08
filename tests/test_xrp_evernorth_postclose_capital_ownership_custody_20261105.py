from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261105-evernorth-postclose-capital-ownership-custody-goldman-13f.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_cash_and_in_kind_xrp_reconcile_to_reported_473m_treasury():
    item = load()["closing_capital_reconciliation"]
    contributions = item["in_kind_xrp_contributions"]
    contribution_components = {
        key: value for key, value in contributions.items() if key != "total_in_kind_xrp"
    }
    total_in_kind = sum(contribution_components.values())
    assert math.isclose(total_in_kind, 388_910_554.061435, rel_tol=0, abs_tol=1e-6)
    assert contributions["total_in_kind_xrp"] == total_in_kind
    derived = item["derived_treasury_reconciliation"]
    assert math.isclose(derived["cash_purchased_xrp"] + derived["in_kind_xrp"], 473_276_430.061435, rel_tol=0, abs_tol=1e-6)
    assert derived["company_reported_approximate_treasury_xrp"] == 473_000_000
    assert derived["company_reported_treasury_as_of"] == "2026-10-09"


def test_gross_closing_cash_is_not_cash_on_hand_and_advance_cash_was_deployed():
    item = load()["closing_capital_reconciliation"]
    assert item["gross_cash_proceeds_at_business_combination_usd_approx"] == 272_600_000
    assert item["components"]["private_placement_cash_usd_approx"] == 224_600_000
    assert item["components"]["remaining_spac_trust_usd_approx"] == 48_000_000
    assert item["use_of_advance_cash"]["amount_usd"] == 214_050_000
    assert item["use_of_advance_cash"]["xrp_purchased"] == 84_365_876
    assert "must not be counted again as cash on hand" in item["use_of_advance_cash"]["note"]
    assert item["gross_cash_proceeds_before_transaction_expenses"] is True


def test_spac_redemptions_and_price_adjustment_are_preserved():
    item = load()["closing_capital_reconciliation"]
    redemptions = item["spac_redemptions"]
    prices = item["signing_and_closing_price_adjustment"]
    assert redemptions["shares_redeemed"] == 18_463_753
    assert redemptions["redemption_percentage_of_shares_with_redemption_rights"] == 80.3
    assert redemptions["cash_redeemed_usd_approx"] == 195_390_000
    assert redemptions["trust_account_released_after_redemptions_usd_approx"] == 48_000_000
    assert prices["signing_xrp_price_usd"] == 2.36609
    assert prices["closing_xrp_price_usd"] == 1.43069
    assert prices["adjustment_factor"] == 0.423264965


def test_sbi_and_arrington_share_classes_are_not_confused_with_voting_control():
    item = load()["postclose_share_structure"]
    assert item["class_a_voting_shares_outstanding"] == 22_268_905
    assert item["class_c_non_voting_shares_outstanding"] == 32_211_992
    assert item["total_class_a_and_c_common_shares"] == 54_480_897
    sbi = item["sbi_holdings_group"]
    assert sbi["class_a_shares"] == 8_885_293
    assert sbi["class_a_pct"] == 39.9
    assert sbi["class_c_shares"] == 2_905_659
    assert sbi["class_c_pct"] == 9.0
    assert sbi["total_class_a_and_c_shares"] == 11_790_952
    assert math.isclose(sbi["derived_share_count_economic_pct"], 21.64, abs_tol=0.01)
    arrington = item["arrington_xrp_capital_fund"]
    assert arrington["class_a_pct"] == 19.9
    assert arrington["class_c_pct"] == 91.0
    assert math.isclose(arrington["derived_share_count_economic_pct"], 61.93, abs_tol=0.01)


def test_ripple_and_larsen_company_units_are_economic_not_pubco_voting_shares():
    item = load()["postclose_share_structure"]
    assert item["ripple"]["class_a_pct"] == 7.1
    assert item["ripple"]["company_units"] == 18_139_927
    assert "generally no voting rights" in item["ripple"]["company_unit_rights"]
    assert item["larsen_lam_childrens_remainder_trust"]["company_units"] == 6_529_941
    assert "generally no voting rights" in item["larsen_lam_childrens_remainder_trust"]["company_unit_rights"]


def test_bitgo_cold_storage_and_shared_insurance_are_not_independent_verification():
    item = load()["custody_and_treasury_operations"]
    assert item["all_xrp_in_custody_through_bitgo"] is True
    assert item["cold_storage_pct_as_of_2026_10_30"] == 100
    assert item["insurance"]["aggregate_coverage_usd_approx"] == 250_000_000
    assert item["insurance"]["dedicated_to_evernorth"] is False
    assert item["insurance"]["pct_of_evernorth_xrp_value_as_of_2026_10_09"] == 36.9
    assert item["public_wallet_addresses_disclosed"] is False
    assert item["independent_onchain_balance_verification_in_this_artifact"] is False


def test_yield_strategy_commencement_and_cold_storage_are_preserved_as_unresolved():
    item = load()["yield_and_collateral_status"]
    assert item["issuer_says_yield_strategies_commenced_following_closing"] is True
    assert item["issuer_says_all_xrp_was_in_cold_storage_as_of_2026_10_30"] is True
    assert item["deployed_xrp_amount_disclosed"] is False
    assert item["xrp_collateral_posted_disclosed"] is False
    assert "may coexist" in item["unresolved_reconciliation"]


def test_pik_note_ripple_facility_and_eloc_are_separate_capital_types():
    item = load()["closing_capital_reconciliation"]["separate_financings"]
    note = item["convertible_senior_pik_notes"]
    assert note["principal_usd"] == 30_000_000
    assert note["net_proceeds_before_transaction_expenses_usd_approx"] == 30_000_000
    assert note["issuance_costs_expensed_usd"] == 1_000_000
    assert note["derived_proceeds_after_issuance_costs_usd_approx"] == 29_000_000
    assert note["derived_post_expense_amount_is_not_separately_reported_as_cash_received"] is True
    assert note["issuance_date"] == "2026-10-12"
    assert note["maximum_cash_settlement_usd"] == 120_000_000
    assert note["interest_rate_pct"] == 4
    facility = item["ripple_company_facility"]
    assert facility["amount_drawn_as_of_2026_10_07_usd"] == 9_700_000
    assert facility["repayment_status"] == "UNVERIFIED"
    eloc = item["cantor_committed_equity_facility"]
    assert eloc["maximum_potential_gross_capacity_usd_approx"] == 76_800_000
    assert eloc["scenario_basis"] == "cover-price estimate; not a contractual dollar cap"
    assert eloc["not_contractual_dollar_cap"] is True
    assert eloc["proceeds_received_as_of_2026_10_30_usd"] == 0


def test_goldman_13f_positions_are_etf_shares_and_premerger_spac_exposure():
    item = load()["goldman_sachs_institutional_exposure"]
    assert item["q2_2026_xrp_etf_reported_value_usd"] == 86_506_129
    assert item["q2_2026_xrp_etf_reported_shares"] == 7_390_191
    armada = item["q2_2026_armada_acquisition_corp_ii_position"]
    assert armada["value_usd"] == 3_813_470
    assert armada["shares"] == 365_976
    assert "does not establish Goldman retained XRPN after the merger." in armada["interpretation"]
    assert "may represent client assets" in item["proprietary_capital_status"]


def test_evernorth_research_remains_ineligible_and_forecast_is_not_issued():
    data = load()
    assert data["model_eligible"] is False
    assert data["forecast_issued"] is False
    assert data["predictive_admission"]["forecast_status"] == "NOT_ISSUED"
    assert data["source_capture_policy"]["raw_sec_bytes_captured"] is False
    assert all(source["raw_content_sha256"] is None for source in data["source_registry"])
    assert all(source["model_eligible"] is False for source in data["source_registry"])


def test_goldman_q2_13f_five_fund_rows_reconcile_to_sec_primary_filing():
    data = load()
    item = data["goldman_sachs_institutional_exposure"]
    positions = item["q2_2026_xrp_etf_positions"]
    assert len(positions) == 5
    assert sum(row["value_usd"] for row in positions) == 86_506_129
    assert sum(row["shares"] for row in positions) == 7_390_191
    assert {row["ticker"] for row in positions} == {"TOXR", "XRP", "XRPC", "XRPZ", "GXRP"}
    filing = item["q2_2026_filing_metadata"]
    assert filing["accession"] == "0000886982-26-000519"
    assert filing["filing_date"] == "2026-08-14"
    assert filing["position_as_of_date"] == "2026-06-30"
    universe = item["q2_2026_universe_reconciliation"]
    assert universe["cryptokeyhole_four_fund_subset_usd"] == 78_859_344
    assert universe["excluded_grayscale_value_usd"] == 7_646_785
    assert universe["cryptokeyhole_four_fund_subset_usd"] + universe["excluded_grayscale_value_usd"] == universe["sec_five_fund_total_usd"]
    assert universe["sum_verified"] is True


def test_cryptokeyhole_four_fund_scope_and_usd_thousands_are_not_confused_with_xrp():
    item = load()["etf_flow_vintage_reconciliation"]["cryptokeyhole"]
    assert item["latest_complete_trading_day"] == "2026-11-05"
    assert item["nov_5_complete_four_fund_xrp"] == -3_339
    assert item["oct_30_to_nov_5_complete_five_day_xrp"] == -1_137_098
    assert item["nov_6_partial_funds_reported"] == 3
    assert item["nov_6_partial_funds_expected"] == 4
    assert item["nov_6_partial_xrp"] == -752_048
    assert item["nov_6_partial_usd"] == -886_665
    assert item["nov_6_usd_thousands_table_value"] == -887
    assert item["nov_6_usd_table_unit"] == "USD thousands"
    assert item["nov_6_xrp_table_unit"] == "XRP"
    assert item["model_eligible"] is False


def test_etf_aggregator_universes_are_not_independent_or_direct_capital_flows():
    data = load()
    item = data["etf_flow_vintage_reconciliation"]
    assert item["xrp_insights"]["nov_6_holdings_delta_xrp"] == -663_043
    assert item["xrp_insights"]["nov_2_to_6_weekly_holdings_delta_xrp"] == -812_529
    assert item["alpha_finance"]["nov_6_daily_usd_flow"] == 0
    assert item["alpha_finance"]["fund_count"] == 5
    assert item["comparability"]["independent_confirmation"] is False
    assert item["comparability"]["directly_comparable"] is False
    assert data["model_eligible"] is False
    assert data["forecast_issued"] is False


def test_rendered_source_hashes_are_not_mislabeled_as_raw_sec_bytes():
    data = load()
    policy = data["source_capture_policy"]
    assert policy["raw_sec_bytes_captured"] is False
    assert policy["raw_content_sha256"] is None
    hashes = policy["normalized_visible_excerpt_hashes"]
    assert len(hashes) == 5
    assert all(len(value) == 64 for value in hashes.values())
    assert "not raw HTTP wire-byte hashes" in policy["hash_scope"]
    assert all(source["raw_content_sha256"] is None for source in data["source_registry"])
