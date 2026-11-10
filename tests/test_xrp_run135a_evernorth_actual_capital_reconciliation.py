from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261110T160534Z-run135a-evernorth-actual-capital-reconciliation.json"
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_run135a_reconciles_all_inkind_xrp_components_exactly() -> None:
    data = _artifact()
    capital = data["evernorth"]["in_kind_xrp_reconciliation"]
    components = (
        "advance_funding_xrp",
        "series_c_arrington_xrp_capital_fund_xrp",
        "ripple_affiliated_larsen_lam_childrens_remainder_trust_xrp",
        "ripple_direct_contribution_agreement_xrp",
        "delayed_funding_xrp",
    )
    total = sum((Decimal(capital[key]) for key in components), Decimal("0"))
    assert total == Decimal("388910554.061435")
    assert total == Decimal(capital["total_in_kind_xrp"])
    assert capital["exact_component_sum_matches"] is True
    assert capital["prior_200000_xrp_gap_status"] == "RESOLVED"


def test_run135a_separates_pubco_xrp_subtotal_from_total_inkind() -> None:
    capital = _artifact()["evernorth"]["in_kind_xrp_reconciliation"]
    subtotal = (
        Decimal(capital["advance_funding_xrp"])
        + Decimal(capital["series_c_arrington_xrp_capital_fund_xrp"])
        + Decimal(capital["ripple_affiliated_larsen_lam_childrens_remainder_trust_xrp"])
    )
    assert subtotal == Decimal("261919096.061435")
    assert subtotal == Decimal(capital["pubco_xrp_subtotal_xrp"])
    assert subtotal + Decimal(capital["ripple_direct_contribution_agreement_xrp"]) + Decimal(
        capital["delayed_funding_xrp"]
    ) == Decimal(capital["total_in_kind_xrp"])


def test_run135a_cash_subscription_is_not_misreported_as_exact_xrp_purchase_cash() -> None:
    cash = _artifact()["evernorth"]["cash_and_xrp_subscriptions"]
    purchased_xrp = Decimal(cash["xrp_purchased_with_cash"])
    average_price = Decimal(cash["average_purchase_price_usd"])
    arithmetic_purchase = purchased_xrp * average_price
    assert cash["advance_funding_cash_raised_usd"] == "214050000"
    assert abs(arithmetic_purchase - Decimal("214000000")) < Decimal("1")
    assert cash["cash_used_to_purchase_xrp_usd_approx"] == "214000000"
    assert cash["cash_raised_less_detailed_purchase_usd"] == "50000"


def test_run135a_distinguishes_debt_from_confirmed_xrp_purchase_capital() -> None:
    evernorth = _artifact()["evernorth"]
    notes = evernorth["convertible_notes"]
    facility = evernorth["related_party_facility"]
    assert notes["gross_principal_usd"] == "30000000"
    assert notes["net_cash_after_advisor_fee_usd"] == "29000000"
    assert notes["specific_xrp_purchase_proven"] is False
    assert notes["conversion_and_put_risk"]["possible_cash_settlement_usd_approx"] == "120000000"
    assert facility["drawn_as_of_2026_10_07_usd"] == "9700000"
    assert facility["classification"] == "DEBT"


def test_run135a_eloc_is_undrawn_capacity_not_actual_capital() -> None:
    eloc = _artifact()["evernorth"]["committed_equity_facility"]
    assert eloc["proceeds_received_as_of_prospectus_usd"] == "0"
    assert eloc["maximum_shares"] == "5218935"
    assert eloc["fee_payment_verified"] is False
    assert eloc["classification"] == "UNDRAWN CONTINGENT EQUITY CAPACITY, NOT ACTUAL CAPITAL RECEIVED"


def test_run135a_preserves_precision_and_conditional_mark_to_market_caveats() -> None:
    holdings = _artifact()["evernorth"]["derived_holdings_bridge"]
    assert holdings["arithmetic_total_xrp"] == "473276430.423935"
    assert holdings["third_party_tracker_total_xrp"] == "473276430.061435"
    assert holdings["difference_xrp"] == "0.3625"
    sensitivity = _artifact()["evernorth"]["current_price_sensitivity"]
    assert sensitivity["conditional_return_pct_approx"] == "-58.9856"
    assert "conditional" in sensitivity["caveat"].lower()


def test_run135a_is_not_a_forecast_or_model_eligible_dataset() -> None:
    data = _artifact()
    assert data["source_capture"]["raw_bytes_captured"] is False
    assert data["source_capture"]["raw_sha256_receipts_available"] is False
    assert data["model_eligible"] is False
    assert data["forecast_status"] == "NOT_ISSUED"
