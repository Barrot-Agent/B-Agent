import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T174012Z-evernorth-cantor-fee-payment-status-correction.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_fee_is_contractual_but_payment_is_not_verified():
    fee = load()["corrected_classification"]
    assert fee["contractual_upfront_fee_usd"] == 521_893.5
    assert fee["fee_fully_earned_and_non_refundable_under_contract"] is True
    assert fee["payment_status"] == "NOT_VERIFIED"
    assert fee["actual_cash_outflow_verified"] is False
    assert fee["actual_cash_outflow_usd"] is None


def test_upfront_determination_date_and_derived_due_date_are_separate():
    timing = load()["timing"]
    assert timing["upfront_determination_date"] == "2026-10-30"
    assert timing["derived_payment_deadline"] == "2026-11-06"
    assert "derived count" in timing["calendar_assumption"]


def test_fee_is_not_misclassified_as_xrp_capital_or_verified_cash_outflow():
    data = load()
    assert data["prior_artifact_field_correction"]["corrected_value_usd"] is None
    assert data["corrected_classification"]["actual_cash_outflow_verified"] is False
    assert "not an XRP capital inflow" in data["model_rules"][0]
    assert data["source_capture_policy"]["model_eligible"] is False
