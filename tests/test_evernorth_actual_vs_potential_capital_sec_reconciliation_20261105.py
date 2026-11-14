import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T173711Z-evernorth-actual-vs-potential-capital-sec-reconciliation.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_cantor_registration_effective_but_no_actual_proceeds_as_of_prospectus():
    data = load()["eloc_facility"]
    assert data["registration_effective"] is True
    assert data["final_prospectus_filed"] is True
    assert data["actual_proceeds_received_as_of_2026_10_30_usd"] == 0
    assert data["full_commencement_conditions_independently_verified"] is False
    assert data["issuer_purchase_notices_or_settlements_verified"] is False


def test_cantor_gross_net_and_fee_are_separate():
    data = load()["eloc_facility"]
    assert data["share_commitment"] == 5_218_935
    assert data["cover_assumption"]["illustrative_gross_proceeds_usd"] == 76_800_000
    assert data["cover_assumption"]["illustrative_net_proceeds_usd"] == 74_400_000
    assert data["commitment_fee_cash_outflow_usd"] == 521_893.5
    assert "97% of applicable VWAP" in data["purchase_price_formula"]


def test_internal_prospectus_gross_estimate_discrepancy_is_preserved():
    data = load()["prospectus_internal_discrepancy"]
    assert data["summary_section_approx_gross_proceeds_usd"] == 80_700_000
    assert data["cover_and_use_of_proceeds_gross_proceeds_usd"] == 76_800_000
    assert data["cover_reference_price_usd"] == 14.71
    assert data["summary_figure_arithmetic_reference_price_usd"] == 15.46
    assert "stale summary text" in data["interpretation"]


def test_public_warrants_are_separate_potential_cash_and_not_xrp_purchase_receipts():
    data = load()["public_warrants"]
    assert data["shares_issuable_up_to"] == 11_499_992
    assert data["exercise_price_usd_per_share"] == 11.5
    assert data["maximum_gross_cash_if_all_exercised_usd"] == 132_249_908
    assert data["actual_exercises_or_proceeds_verified"] is False
    assert data["use_of_proceeds_earmarked_for_xrp"] is False


def test_capital_forms_are_not_double_counted_and_no_forecast_is_issued():
    data = load()
    capital = data["capital_classification"]
    assert capital["actual_cash_inflow_as_of_eloc_prospectus_date_usd"] == 0
    assert capital["actual_historical_advance_funding_cash_usd"] == 214_050_000
    assert capital["in_kind_xrp_in_advance_funding_xrp"] == 600_000
    assert capital["potential_eloc_gross_usd"] == 76_800_000
    assert capital["potential_public_warrant_gross_usd"] == 132_249_908
    assert data["model_admission"]["model_eligible"] is False
    assert data["model_admission"]["forecast_issued"] is False
