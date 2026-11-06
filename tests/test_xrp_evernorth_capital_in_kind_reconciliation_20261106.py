"""Primary-source capital and in-kind XRP reconciliation checks for Evernorth."""
from __future__ import annotations

import json
import math
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T000715Z-evernorth-capital-in-kind-xrp-reconciliation.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_in_kind_xrp_components_reconcile_to_sec_total() -> None:
    artifact = load_artifact()
    capital = artifact["capital_reconciliation"]
    components = capital["in_kind_xrp_contributions"]
    component_sum = (
        components["series_c_sponsor"]
        + components["ripple_group_affiliates"]
        + components["advance_funding_subscribers"]
        + components["delayed_funding_subscribers"]
        + components["ripple_contribution_agreement"]
    )
    assert math.isclose(component_sum, components["total"], rel_tol=0, abs_tol=1e-6)
    assert round(components["total"]) == components["total_rounded_in_filing"]


def test_cash_purchase_plus_in_kind_is_consistent_with_approximate_holdings() -> None:
    artifact = load_artifact()
    capital = artifact["capital_reconciliation"]
    holdings = capital["holdings_reconciliation"]
    total = holdings["cash_purchased_xrp"] + holdings["in_kind_xrp"]
    assert math.isclose(total, holdings["arithmetic_total_xrp"], rel_tol=0, abs_tol=1e-6)
    assert round(total / 1_000_000) == 473
    assert holdings["filing_reported_holdings_approx_xrp"] == 473_000_000
    assert holdings["filing_holdings_as_of"] == "2026-10-09"


def test_gross_cash_proceeds_are_not_double_counted() -> None:
    artifact = load_artifact()
    capital = artifact["capital_reconciliation"]
    cash = capital["cash_subscriptions"]
    closing = capital["closing_cash_proceeds"]
    component_cash = cash["advance_funding"]["cash_usd"] + cash["delayed_funding"]["cash_usd"]
    assert component_cash == cash["private_placement_cash_components_usd"]
    assert round(component_cash / 100_000) * 100_000 == cash["private_placement_cash_gross_usd_rounded"]
    gross = closing["private_placement_investments_usd_rounded"] + closing["trust_account_after_redemptions_usd_rounded"]
    assert gross == closing["gross_cash_proceeds_before_transaction_expenses_usd_rounded"]
    assert cash["cash_from_advance_funding_used_to_purchase_xrp_usd_rounded"] < gross


def test_advance_funding_cash_purchase_ratio_is_derived_not_execution_vwap() -> None:
    artifact = load_artifact()
    cash = artifact["capital_reconciliation"]["cash_subscriptions"]
    ratio = cash["advance_funding"]["cash_usd"] / cash["xrp_purchased_with_that_cash"]
    assert math.isclose(ratio, cash["implied_cash_deployed_per_xrp_usd"], rel_tol=0, abs_tol=1e-12)
    assert "not an exchange execution vwap" in cash["implied_cash_deployed_per_xrp_note"].lower()


def test_sbi_is_defined_as_holdings_parent_and_cash_allocation_is_not_inferred() -> None:
    artifact = load_artifact()
    relationships = artifact["institutional_relationships"]
    assert relationships["sbi_definition"] == "The filing explicitly defines 'SBI' as SBI Holdings, Inc."
    assert len(relationships["sbi_stockholders_controlled_by_sbi"]) == 4
    assert relationships["sbi_aggregate_pubco_class_a_shares"] == 9_431_914
    assert relationships["sbi_group_ownership_percentage_as_of_2026_10_09"] == 39.9
    assert relationships["sbi_ownership_limitation"]["voting_ownership_cap_percent"] == 39.9
    assert artifact["capital_reconciliation"]["cash_subscriptions"]["advance_funding"]["sbi_specific_cash_allocation_usd"] is None
    assert "not a 39.9% cash contribution" in relationships["sbi_ownership_limitation"]["interpretation"]
    assert "SBIC East" in relationships["sbic_disambiguation"]
    assert "SBIC Central" in relationships["sbic_disambiguation"]
    assert "SBIC West" in relationships["sbic_disambiguation"]


def test_notes_and_related_party_borrowing_are_separate_from_xrp_purchases() -> None:
    artifact = load_artifact()
    separate = artifact["capital_reconciliation"]["separate_financing"]
    assert separate["convertible_senior_pik_notes"]["principal_usd"] == 30_000_000
    assert separate["convertible_senior_pik_notes"]["deployment_to_xrp_verified"] is False
    assert separate["ripple_related_party_credit_facility"]["drawn_as_of_2026_10_07_usd"] == 9_700_000
    assert "borrowing" in separate["ripple_related_party_credit_facility"]["classification"]


def test_primary_source_receipt_limits_and_forecast_gate_are_explicit() -> None:
    artifact = load_artifact()
    capture = artifact["primary_source"]["capture"]
    assert capture["raw_html_wire_bytes_captured"] is False
    assert capture["raw_source_sha256"] is None
    assert capture["line_references"]
    assert artifact["model_eligible"] is False
    assert artifact["forecast_status"] == "NOT_ISSUED"
    assert artifact["exact_phrase_research"]["camilla_kamilah_stevenson"]["inventory_status"].startswith("candidate leads only")



def test_pubco_warrant_capital_is_contingent_stock_financing_not_xrp_purchase_cash() -> None:
    artifact = load_artifact()
    warrants = artifact["capital_reconciliation"]["contingent_warrant_capital"]
    assert warrants["security_underlying"] == "Pubco Class A common stock, not XRP"
    assert warrants["public_warrants_outstanding_as_of_2026_06_30"] == 11_500_000
    assert warrants["private_placement_warrants_outstanding_as_of_2026_06_30"] == 355_000
    assert warrants["private_placement_warrants_forfeited_at_closing"] == 115_347
    assert warrants["private_placement_warrants_remaining_after_forfeiture"] == 239_653
    assert warrants["public_warrant_max_gross_cash_proceeds_if_all_exercised_for_cash_usd"] == 132_250_000
    assert warrants["remaining_private_warrant_max_gross_cash_proceeds_if_all_exercised_for_cash_usd"] == 2_756_009.50
    assert warrants["total_max_gross_cash_proceeds_if_all_exercised_for_cash_usd"] == 135_006_009.50
    assert warrants["actual_cash_proceeds_from_warrant_exercises_usd"] is None
    assert warrants["status"] == "CONTINGENT_NOT_RECEIVED"
    assert "registration statement" in warrants["cash_exercise_conditions"].lower()
    assert "cashless" in warrants["cash_exercise_conditions"].lower()
    assert "not XRP purchase capital" in warrants["classification"]
    assert artifact["exact_phrase_research"]["actual_capital"]["warrant_context"]["underlying_security"] == "Pubco Class A common stock, not XRP"
