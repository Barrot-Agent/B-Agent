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
    pathfinder = data["evernorth_q3_2026"]["pathfinder_ownership"]
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
    assert ripple["arrington_sponsor_xrp_via_rippleworks"] == "211319096.061435"


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
