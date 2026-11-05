from __future__ import annotations

import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261105T031000Z-evernorth-actual-capital-facility-reconciliation.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_eloc_capacity_is_not_mislabeled_as_actual_cash():
    document = load_artifact()
    facility = document["eloc_facility"]

    assert document["model_eligible"] is False
    assert document["forecast_issued"] is False
    assert facility["registration_effective_date"] == "2026-10-30"
    assert facility["maximum_new_class_a_shares"] == 5_218_935
    assert facility["actual_draw_amount_usd"] is None
    assert facility["actual_draw_status"] == "NOT_ESTABLISHED_BY_REVIEWED_FILINGS"
    assert facility["do_not_assume_zero_draw"] is True
    assert "all, some or none" in facility["issuer_control"]


def test_eloc_limits_fees_and_dilution_are_preserved():
    facility = load_artifact()["eloc_facility"]

    assert facility["purchase_price_rule"].startswith("97%")
    assert facility["cantors_beneficial_ownership_cap_percent"] == 4.99
    assert "20%" in facility["volume_limit"]
    assert facility["stated_cap_as_percent_of_pre_facility_shares"] == 19.99
    assert facility["estimated_post_issue_share_dilution_if_all_shares_issued_percent"] == 16.7
    assert facility["upfront_commitment_fee_usd"] == 521_893.50
    assert facility["aggregate_commitment_fee_cap_usd"] == 1_000_000
    assert facility["separate_expense_reimbursement_cap_usd"] == 500_000
    assert "regardless of whether purchases are made" in facility["fee_character"]


def test_published_proceeds_discrepancies_are_not_silently_reconciled():
    facility = load_artifact()["eloc_facility"]
    estimates = facility["gross_proceeds_published_estimates_usd"]
    math = facility["arithmetic_reconciliation"]

    assert estimates["prospectus_cover_and_use_of_proceeds"] == 76_800_000
    assert estimates["offering_summary_use_of_proceeds"] == 80_700_000
    assert estimates["prospectus_estimated_net_proceeds"] == 74_400_000
    assert math["shares_times_oct29_close_usd"] == 76_770_533.85
    assert math["shares_times_oct29_close_times_97_percent_usd"] == 74_467_417.8345
    assert "Do not silently reconcile" in math["discrepancy"]


def test_historical_cash_and_convertible_note_are_separate_actual_capital_events():
    events = {x["event_id"]: x for x in load_artifact()["actual_capital_events"]}

    advance = events["advance_funding_2025"]
    assert advance["cash_received_usd"] == 214_049_995
    assert advance["in_kind_xrp_received"] == 600_000
    assert advance["not_current_eloc_draw"] is True

    note = events["convertible_notes_2026_close"]
    assert note["principal_usd"] == 30_000_000
    assert note["net_cash_proceeds_usd"] == 29_000_000
    assert note["transaction_fee_usd"] == 1_000_000
    assert note["classification"] == "actual_debt_financing_cash"

    delayed = events["delayed_funding_commitment"]
    assert delayed["status"] == "committed_delivery_not_independently_verified_in_this_capture"


def test_issuer_intended_use_is_not_treated_as_an_executed_xrp_purchase():
    document = load_artifact()

    assert any(
        "not evidence of an executed XRP purchase" in item
        for item in document["key_distinctions"]
    )
    assert any(
        "No ELOC draw amount" in item
        for item in document["disconfirming_evidence"]
    )
    assert document["prediction_status"] == "NOT_ISSUED"


def test_sec_excerpt_hashes_are_labeled_as_rendered_not_raw_receipts():
    document = load_artifact()

    assert document["source_capture_policy"]["raw_http_bytes_captured"] is False
    assert document["source_capture_policy"]["rendered_excerpt_hashes_are_not_raw_source_hashes"] is True
    for source in document["source_registry"]:
        assert source["raw_capture_status"] == "web_rendered_excerpt_only"
        assert source["raw_http_bytes_sha256"] is None
        assert len(source["rendered_excerpt_sha256"]) == 64
