"""Regression tests for Evernorth actual-capital and Cantor ELOC reconciliation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261110T144953Z-run132b-evernorth-eloc-effectiveness-and-actual-capital-reconciliation.json"
)


def _load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_run132b_eloc_effective_but_no_proceeds_as_of_november_9():
    data = _load()
    eloc = data["eloc"]
    assert eloc["registration_effective_at"] == "2026-10-30T20:00:00Z"
    assert eloc["registration_statement_no"] == "333-299620"
    assert eloc["maximum_new_class_a_shares"] == 5_218_935
    assert eloc["issuer_option_not_obligation"] is True
    assert eloc["status_as_of_2026_11_09"]["proceeds_received_usd"] == 0
    assert eloc["status_as_of_2026_11_09"]["status"] == "ISSUER_DISCLOSED_NO_PROCEEDS"


def test_run132b_separate_selling_holder_resale_is_not_eloc_funding():
    data = _load()
    resale = data["eloc"]["resale_registration_distinction"]
    assert resale["registration_statement_no"] == "333-299739"
    assert resale["securities_registered_for_selling_securityholders"]["class_a_shares"] == 73_688_162
    assert resale["company_proceeds_from_selling_securityholder_resales_usd"] == 0


def test_run132b_actual_xrp_reconciliation_separates_contributions_and_purchases():
    actual = _load()["actual_capital_and_xrp"]
    assert actual["in_kind_xrp_contributions"] == 388_910_554.061435
    assert actual["xrp_reported_purchased_with_cash"] == 84_365_876
    assert actual["derived_xrp_total"] == 473_276_430.061435
    assert actual["derived_xrp_reconciliation"]["agrees_with_issuer_approximation"] is True
    assert actual["derived_xrp_reconciliation"]["verification_level"] == "issuer_filing_arithmetic_only"
    assert actual["reported_gross_cash_proceeds_at_closing_usd"] == 272_600_000


def test_run132b_ripple_credit_and_convertible_notes_are_not_assumed_xrp_purchases():
    actual = _load()["actual_capital_and_xrp"]
    facilities = actual["other_actual_financing"]
    ripple_company = next(x for x in facilities if x["source"] == "Ripple / Pathfinder Company Facility")
    assert ripple_company["facility_limit_usd"] == 10_000_000
    assert ripple_company["borrowed_usd"] == 9_700_000
    assert ripple_company["xrp_purchase_proven"] is False
    notes = next(x for x in facilities if x.get("principal_usd") == 30_000_000)
    assert notes["interest"] == "4.00% paid in kind"
    assert notes["xrp_purchase_proven"] is False


def test_run132b_prospectus_proceeds_estimates_remain_unreconciled_and_not_actual():
    eloc = _load()["eloc"]
    calc = eloc["proceeds_estimate_reconciliation"]
    assert calc["cover_illustration_usd"] == 76_800_000
    assert calc["offering_summary_illustration_usd"] == 80_700_000
    assert calc["calculated_at_97pct_of_same_reference_price_usd"] == 74_467_417.8345
    assert calc["status"] == "UNRECONCILED_PROSPECTUS_PRESENTATION"
    assert eloc["fees"]["payment_status"] == "NOT_VERIFIED"


def test_run132b_source_excerpt_hashes_reproduce_without_claiming_raw_bytes():
    for receipt in _load()["source_receipts"]:
        assert receipt["raw_bytes_captured"] is False
        assert receipt["raw_byte_sha256"] is None
        digest = hashlib.sha256(receipt["normalized_excerpt"].encode("utf-8")).hexdigest()
        assert digest == receipt["normalized_excerpt_sha256"]


def test_run132b_actual_capital_is_not_admitted_as_directional_market_flow():
    admission = _load()["forecast_admission"]
    assert admission["status"] == "EXCLUDED_FROM_DIRECTIONAL_XRP_FEATURES"
