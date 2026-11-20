from __future__ import annotations

import json
import math
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261109T133222Z-evernorth-actual-capital-and-cantor-facility-status.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_historical_cash_and_xrp_acquisition_are_separated_and_reconciled() -> None:
    data = load_artifact()
    capital = data["verified_historical_capital"]

    assert capital["cash_raised_since_inception_usd"] == 214_100_000
    assert capital["xrp_purchased_with_cash_proceeds"] == 84_365_876
    assert capital["total_xrp_contributed_in_kind_at_closing"] == 388_910_554
    assert capital["reported_xrp_held_as_of_2026_10_09_approx"] == 473_000_000
    assert capital["reconciliation"]["implied_total_xrp"] == 473_276_430
    assert capital["reconciliation"]["reported_total_rounds_to_approx_473m"] is True
    assert "not additive" in capital["note"]


def test_closing_cash_and_convertible_notes_are_not_double_counted_as_xrp_buys() -> None:
    data = load_artifact()
    capital = data["verified_historical_capital"]
    note = data["additional_financing"]["convertible_notes"]

    assert capital["closing_gross_cash_proceeds_usd"] == 272_600_000
    assert capital["closing_cash_components_usd"]["private_placement_investments"] == 224_600_000
    assert capital["closing_cash_components_usd"]["trust_account_release_after_redemptions"] == 48_000_000
    assert note["principal_usd"] == 30_000_000
    assert note["net_proceeds_before_transaction_expenses_usd"] == 30_000_000
    assert note["xrp_purchase_from_these_proceeds_verified"] is False


def test_ripple_company_and_evernorth_facilities_are_distinct() -> None:
    data = load_artifact()
    facilities = data["additional_financing"]["ripple_facilities"]

    assert facilities["company_facility"]["borrower"] == "The Company (not Evernorth)"
    assert facilities["company_facility"]["limit_usd"] == 10_000_000
    assert facilities["company_facility"]["amount_borrowed_usd"] == 9_700_000
    assert facilities["evernorth_facility"]["limit_usd"] == 1_000_000
    assert facilities["evernorth_facility"]["amount_borrowed_usd"] == 0


def test_cantor_registration_effective_does_not_equal_commencement_or_drawdown() -> None:
    data = load_artifact()
    facility = data["cantor_committed_equity_facility"]

    assert facility["registration"]["effective_date"] == "2026-10-30"
    assert facility["commencement"]["effective_registration_is_one_condition_not_the_only_condition"] is True
    assert facility["commencement"]["commencement_date_publicly_confirmed"] is False
    assert facility["drawdown"]["purchase_notices_publicly_verified"] is False
    assert facility["drawdown"]["cash_settlement_publicly_verified"] is False
    assert facility["drawdown"]["incremental_xrp_purchase_from_facility_publicly_verified"] is False
    assert facility["fees_and_expenses"]["payment_confirmed"] is False


def test_prospectus_97_percent_math_discrepancy_is_detected() -> None:
    data = load_artifact()
    check = data["prospectus_arithmetic_reconciliation"]
    expected = check["shares"] * check["assumed_xrpn_closing_price_usd_on_2026_10_29"] * 0.97

    assert math.isclose(expected, check["contract_97_percent_price_calculation_usd"], rel_tol=0, abs_tol=0.01)
    assert math.isclose(check["undiscounted_multiplication_usd"], 76_770_533.85, rel_tol=0, abs_tol=0.01)
    assert math.isclose(check["contract_97_percent_price_calculation_usd"], 74_467_417.8345, rel_tol=0, abs_tol=0.01)
    assert check["discrepancy"]["table_row_exceeds_97_percent_calculation_by_usd"] > 2_300_000
    assert check["discrepancy"]["classification"] == "PROSPECTUS_ARITHMETIC_DISCLOSURE_INCONSISTENCY_REQUIRING_ISSUER_RECONCILIATION"


def test_cantor_capacity_is_not_counted_as_xrp_capital_flow() -> None:
    data = load_artifact()
    model = data["model_admission"]

    assert model["cantor_facility_capacity"].startswith("NOT_A_CAPITAL_FLOW_FEATURE")
    assert model["xrp_purchase_from_cantor_proceeds"] == "NOT_ESTABLISHED"
    assert model["directional_forecast_eligible"] is False
    assert model["forecast_status"] == "NOT_ISSUED"
