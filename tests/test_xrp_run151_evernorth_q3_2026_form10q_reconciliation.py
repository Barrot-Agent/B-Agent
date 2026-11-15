from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261115T040420Z-run151-evernorth-q3-10q-market-and-integration-audit.json"
)


def _audit() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_run151_separates_cash_received_from_cash_used_to_buy_xrp() -> None:
    cash = _audit()["evernorth_q3_2026"]["cash_and_purchase"]
    assert cash["advance_funding_cash_received_usd"] == "214049995"
    assert cash["cash_used_for_identified_xrp_purchase_usd"] == "214000000"
    assert cash["xrp_purchased_with_cash"] == "84365876"
    assert (
        Decimal(cash["advance_funding_cash_received_usd"])
        - Decimal(cash["cash_used_for_identified_xrp_purchase_usd"])
        == Decimal("49995")
    )


def test_run151_does_not_claim_the_restricted_49995_was_spent_after_close() -> None:
    cash = _audit()["evernorth_q3_2026"]["cash_and_purchase"]
    assert cash["restricted_cash_dec31_usd"] == "49995"
    assert cash["restricted_cash_sep30_usd"] == "49995"
    assert cash["residual_cash_postclose_disposition"] == "NOT_DISCLOSED"
    assert "unverified/superseded" in cash["current_disposition"].lower()
    assert cash.get("residual_cash_purchase_xrp_quantity") is None


def test_run151_reconciles_in_kind_xrp_with_reported_rounding() -> None:
    capital = _audit()["evernorth_q3_2026"]["in_kind_xrp"]
    components = capital["components"]
    total = sum((Decimal(value) for value in components.values()), Decimal("0"))
    reported = Decimal(capital["reported_total_at_close"])
    assert total == reported
    private_placement_subtotal = (
        Decimal(components["advance_funding_xrp"])
        + Decimal(components["arrington_series_c_xrp_via_rippleworks"])
        + Decimal(components["ripple_affiliated_entity_xrp"])
    )
    assert private_placement_subtotal == Decimal("261919096")
    assert capital["prior_precision_status"] == "SUPERSEDED_BY_Q3_2026_10Q_WHOLE_XRP_DISCLOSURE"


def test_run151_reconciles_postclose_known_treasury_without_double_counting() -> None:
    data = _audit()["evernorth_q3_2026"]
    bridge = data["holdings_bridge"]
    assert (
        Decimal(bridge["evernorth_transfer_to_pathfinder_postclose_xrp"])
        + Decimal(bridge["ripple_contribution_already_in_pathfinder_xrp"])
        == Decimal(bridge["known_combined_postclose_treasury_xrp"])
    )
    assert (
        Decimal(data["cash_and_purchase"]["xrp_purchased_with_cash"])
        + Decimal(data["in_kind_xrp"]["reported_total_at_close"])
        == Decimal(bridge["known_combined_postclose_treasury_xrp"])
    )
    assert bridge["completeness"].startswith("KNOWN_GROSS_PATHFINDER_SUBTOTAL")
    assert bridge["classification"] == "GROSS_PATHFINDER_TREASURY_NOT_PUBCO_ATTRIBUTABLE_AMOUNT"
    assert bridge["complete_total_including_possible_restricted_cash_purchase"] == "NOT_ESTABLISHED"
    pathfinder = data["pathfinder_ownership"]
    assert pathfinder["pubco_ownership_percent"] == "71.5"
    assert pathfinder["pubco_attributable_xrp"] == "NOT_COMPUTED"


def test_run151_separates_actual_cash_debt_warrants_and_eloc_capacity() -> None:
    finance = _audit()["evernorth_q3_2026"]["debt_and_equity"]
    note = finance["convertible_note"]
    warrants = finance["warrants"]
    eloc = finance["cantor_eloc"]
    assert note["principal_usd"] == "30000000"
    assert note["net_cash_proceeds_usd"] == "29000000"
    assert note["advisor_fee_usd"] == "1000000"
    exact_warrant_cash = Decimal(warrants["exercised_shares"]) * Decimal(warrants["strike_usd"])
    assert abs(exact_warrant_cash - Decimal(warrants["gross_cash_proceeds_usd_rounded"])) < Decimal("50000")
    assert eloc["actual_draw_or_proceeds"] == "NOT_DISCLOSED"
    assert eloc["classification"] == "CONDITIONAL_EQUITY_CAPACITY_NOT_CASH_RECEIVED"


def test_run151_sbi_affiliation_is_not_misreported_as_direct_parent_ownership() -> None:
    sbi = _audit()["evernorth_q3_2026"]["sbi_affiliated_investors"]
    assert sbi["filing_language"] == "Certain investors affiliated with SBI Holdings, Inc."
    assert sbi["class_a_ownership_threshold"] == "39.9%"
    assert sbi["class_c_shares_issued_to_sbi_affiliated_investors"] == "2359038"
    assert sbi["direct_sbi_holdings_ownership"] == "NOT_ESTABLISHED"


def test_run151_does_not_treat_noncash_fair_value_gain_as_revenue() -> None:
    results = _audit()["evernorth_q3_2026"]["liquidity_and_results"]
    assert results["net_income_q3_usd"] == "155264700"
    assert results["net_loss_9m_usd"] == "32870033"
    assert results["q3_fair_value_gain_on_refundable_advances_usd"] == "162834432"
    assert results["digital_asset_impairment_usd"] == "271037170"
    assert results["revenue_generated"] == "NONE_REPORTED"


def test_run151_preserves_ripple_related_entity_and_pathfinder_distinctions() -> None:
    ripple = _audit()["evernorth_q3_2026"]["ripple_and_related_entities"]
    assert ripple["ripple_direct_contribution_to_pathfinder_xrp"] == "126791458"
    assert ripple["ripple_class_a_shares"] == "1678382"
    assert ripple["ripple_pathfinder_units"] == "16461545"
    assert ripple["ripple_affiliated_entity_xrp"] == "50000000"
    assert ripple["combined_ripple_and_affiliate_pubco_ownership_limit"] == "9.9%"
    assert ripple["arrington_sponsor_xrp_via_rippleworks"] == "211319096"


def test_run151_source_and_forecast_gates_remain_fail_closed() -> None:
    data = _audit()
    assert data["source_capture"]["raw_source_bytes_captured"] is False
    assert data["source_capture"]["raw_sha256_receipts_available"] is False
    assert data["source_capture"]["model_eligible"] is False
    assert data["prediction_engine"]["forecast_status"] == "NOT_ISSUED"
    assert data["prediction_engine"]["accuracy"] == "NOT_EVALUATED"


def test_run151_cost_basis_lots_reconcile_without_false_source_attribution() -> None:
    data = _audit()["evernorth_q3_2026"]
    lots = data["cost_basis_lot_table"]
    assert sum(Decimal(lot["units"]) for lot in lots["lots"]) == Decimal("346284972")
    assert lots["category_mapping"] == "NOT_EXPLICITLY_DISCLOSED"
    assert lots["lots"][2]["units"] == "211619196"
    assert data["in_kind_xrp"]["components"]["arrington_series_c_xrp_via_rippleworks"] == "211319096"


def test_run151_coinbase_principal_market_is_not_misreported_as_custodian() -> None:
    data = _audit()["evernorth_q3_2026"]
    assert data["liquidity_and_results"]["principal_market_for_financial_reporting"] == "Coinbase"
    assert data["custody"]["postclose_initial_custodian"] == "BitGo Trust"
    assert data["custody"]["coinbase_custody_relationship"] == "NOT_ESTABLISHED_BY_THIS_FILING"


def test_run151_does_not_compute_xrp_per_share_from_gross_pathfinder_treasury() -> None:
    data = _audit()["evernorth_q3_2026"]["xrp_per_share"]
    assert data["pubco_ownership_of_pathfinder_percent"] == "71.5"
    assert data["calculated_xrp_per_share"] == "NOT_COMPUTED"


def test_run151_sec_commission_interpretation_classifies_xrp_but_preserves_howey() -> None:
    rule = _audit()["regulatory_status"]["sec_commission_interpretation"]
    assert rule["release_number"] == "33-11412"
    assert rule["xrp_classification"] == "DIGITAL_COMMODITY"
    assert rule["xrp_itself_is_security"] is False
    assert rule["nonsecurity_asset_sale_caveat"]
    assert rule["howey_test_preserved"] is True
    assert rule["blanket_exemption"] is False


def test_run151_genius_act_occ_rule_is_not_yet_effective() -> None:
    rule = _audit()["regulatory_status"]["genius_act_occ_final_rule"]
    assert rule["announced_date"] == "2026-10-21"
    assert rule["effective_date"] == "2027-01-18"
    assert rule["status_as_of_2026_11_15"] == "NOT_YET_EFFECTIVE"


def test_run151_circle_binance_equity_and_coinbase_distribution_are_separate() -> None:
    data = _audit()["institutional_network"]
    binance = data["circle_binance"]
    distribution = data["circle_coinbase_distribution"]
    assert binance["equity_investment_usd"] == "100000000"
    assert binance["shares_purchased"] == "1200000"
    assert distribution["q3_2026_distribution_costs_usd"] == "331300000"
    assert distribution["nine_month_2026_distribution_costs_usd"] == "986600000"
    assert "not a flat 50%" in distribution["arrangement"]


def test_run151_coinbase_rewards_table_narrative_mismatch_is_preserved() -> None:
    item = _audit()["institutional_network"]["coinbase_usdc_rewards_discrepancy"]
    assert item["table_q3_change_usd"] == "17675000"
    assert item["narrative_q3_increase_usd"] == "71600000"
    assert item["table_nine_month_change_usd"] == "47655000"
    assert item["narrative_nine_month_increase_usd"] == "175700000"
    assert item["reconciliation"] == "UNRESOLVED_INTERNAL_TABLE_NARRATIVE_DISAGREEMENT"


def test_run151_fresh_spot_observations_remain_model_ineligible() -> None:
    market = _audit()["market_snapshot_followup"]
    assert market["okx_xrp_usdt"]["age_at_cutoff_seconds"] > 300
    assert market["okx_xrp_usdt"]["model_eligible"] is False
    assert market["kraken_xrp_usd"]["provider_event_time"] == "ABSENT"
    assert market["kraken_xrp_usd"]["model_eligible"] is False
    assert market["depth"] == "No synchronized multi-venue L2 captured. Single-level ticker sizes are not full depth."


def test_run151_coinbase_sec_filing_link_uses_correct_accession() -> None:
    data = _audit()["institutional_network"]
    correct = "https://www.sec.gov/Archives/edgar/data/1679788/000167978826000122/coin-20260930.htm"
    assert data["coinbase_q3_2026"]["sec_filing_url"] == correct
    assert data["coinbase_usdc_rewards_discrepancy"]["source_url"] == correct


def test_run151_circle_custody_entities_are_distinguished() -> None:
    data = _audit()["institutional_network"]["circle_custody"]
    assert data["circle_national_trust"]["opened_date"] == "2026-07-24"
    assert data["circle_national_trust"]["initial_services"] == "Fiduciary digital-asset custody services to Circle and its affiliates"
    assert data["circle_internet_trust_company"]["date"] == "2026-07-31"
    assert "do not assume all third-party customer assets" in data["scope_caveat"]


def test_run151_circle_reserve_sensitivity_is_not_a_forecast() -> None:
    data = _audit()["institutional_network"]["circle_reserve_economics"]
    assert data["reserve_income_share_of_revenue_q3"] == "76.0%"
    assert data["reserve_income_share_of_revenue_nine_months"] == "87.5%"
    assert data["sensitivity_from_september_average_yield"] == "3.62%"
    assert data["twelve_month_sensitivity_usd_millions"]["rate_change_minus_100_bps"]["reserve_income"] == "-739"
    assert "not a forecast" in data["caveat"].lower()
    assert "highly uncertain and unproven" in data["caveat"]


def test_run151_occ_trust_charters_keep_entity_and_scope_distinct() -> None:
    charters = _audit()["regulatory_status"]["occ_trust_charters"]
    by_name = {x["entity"]:x for x in charters}
    assert by_name["Circle National Trust / First National Digital Currency Bank, N.A."]["opened_date"] == "2026-07-24"
    assert by_name["Ripple National Trust Bank"]["effective_date"] == "2026-10-26"
    assert by_name["Coinbase National Trust Company"]["effective_date"] == "2026-11-06"
