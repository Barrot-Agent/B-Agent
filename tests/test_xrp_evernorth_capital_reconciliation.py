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

    delayed = events["delayed_funding_2026_close"]
    assert delayed["cash_received_usd"] == 10_500_000
    assert delayed["in_kind_xrp_received"] == 200_000
    assert delayed["status"] == "issuer_disclosed_paid_prior_to_close_and_shares_issued_at_close"


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


def test_evernorth_custody_and_coinbase_valuation_roles_are_distinguished():
    document = load_artifact()
    relationships = document["custody_and_relationships"]

    custody = relationships["evernorth_xrp_custody"]
    assert custody["custodian"] == "BitGo Bank & Trust, National Association"
    assert "100% of its XRP" in custody["status_as_of_prospectus"]
    assert custody["insurance"]["dedicated_to_evernorth"] is False
    assert custody["insurance"]["shared_among_bitgo_clients"] is True
    assert custody["insurance"]["stated_coverage_as_percent_of_evernorth_xrp_value_as_of_2026_10_09"] == 36.9

    coinbase = relationships["coinbase_relationship"]
    assert coinbase["role"].startswith("principal market")
    assert coinbase["custodian"] is False
    assert coinbase["prime_broker"] is False
    assert coinbase["direct_execution_or_custody_contract_disclosed_in_this_prospectus"] is False


def test_sbi_holdings_entities_are_not_regional_sbic_companies():
    sbi = load_artifact()["custody_and_relationships"]["sbi_relationship"]

    assert sbi["parent_identity"] == "SBI Holdings, Inc."
    assert len(sbi["issuer_defined_controlled_stockholders"]) == 4
    assert sbi["class_a_shares_disclosed_as_held_by_sbi_stockholders"] == 9_431_914
    assert sbi["class_c_shares_issued_at_2026_10_09_close_to_certain_sbi_affiliates"] == 2_359_038
    assert sbi["ownership_limit_percent"] == 39.9
    assert sbi["limit_is_not_verified_exact_current_ownership"] is True
    assert sbi["regional_sbic_east_central_west_are_distinct_from_sbi_holdings"] is True


def test_ripple_equity_in_kind_contributions_and_related_party_debt_are_separate():
    ripple = load_artifact()["custody_and_relationships"]["ripple_relationship"]

    assert ripple["ripple_xrp_contribution_to_pathfinder"] == 126_791_458
    assert ripple["contributor_related_party_entity_xrp_subscription"] == 50_000_000
    assert ripple["contributor_related_party_entity_name"] == "Larsen Lam Children's Remainder Trust"
    assert "investor affiliated with Ripple" in ripple["contributor_related_party_entity_issuer_description"]
    assert ripple["ripple_class_a_shares_issued_at_close"] == 1_678_382
    assert ripple["ripple_pathfinder_units_issued_at_close"] == 16_461_545
    assert ripple["combined_ripple_group_ownership_limit_percent"] == 9.9

    credit = ripple["related_party_credit_facility"]
    assert credit["lender"] == "Ripple Labs Inc."
    assert credit["borrower"] == "Pathfinder Digital Assets LLC"
    assert credit["limit_usd"] == 10_000_000
    assert credit["drawn_usd_as_of_2026_10_07"] == 9_700_000
    assert credit["classification"] == "related_party_debt_not_equity_and_not_eloc_proceeds"
    assert credit["repayment_status"] == "not_verified_in_this_capture"
    assert ripple["governance_and_conflicts"]["issuer_disclosed_potential_conflicts"] is True


def test_sponsor_and_rippleworks_in_kind_xrp_are_not_direct_ripple_cash():
    document = load_artifact()
    sponsor = document["sponsor_relationship"]
    events = {x["event_id"]: x for x in document["actual_capital_events"]}

    assert sponsor["sponsor"] == "Arrington XRP Capital Fund, LP"
    assert sponsor["general_partner"] == "Arrington Capital Management, LLC"
    assert sponsor["rippleworks_is_limited_partner"] is True

    series_c = events["series_c_sponsor_xrp"]
    assert series_c["contributor"] == "RippleWorks, Inc."
    assert series_c["in_kind_xrp"] == 211_319_096.061435
    assert series_c["classification"] == "in_kind_xrp_contribution_not_cash_and_not_a_direct_ripple_corporate_contribution"

    trust = events["contributor_related_party_entity_subscription"]
    assert trust["contributor"] == "Larsen Lam Children's Remainder Trust"
    assert trust["in_kind_xrp"] == 50_000_000

    direct_ripple = events["ripple_contribution"]
    assert direct_ripple["contributor"] == "Ripple Labs Inc."
    assert direct_ripple["in_kind_xrp"] == 126_791_458


def test_convertible_note_purchaser_and_issuer_date_disagreement_are_recorded():
    note = next(
        item for item in load_artifact()["actual_capital_events"]
        if item["event_id"] == "convertible_notes_2026_close"
    )
    assert note["purchaser"] == (
        "NH Investment & Securities Co., Ltd., as trustee of Kyobo AIM "
        "Corporate Finance General Private Investment Trust No. 3"
    )
    assert note["date_disagreement"]["financial_notes_date"] == "2026-10-09 (Closing Date)"
    assert note["date_disagreement"]["prospectus_summary_completion_date"] == "2026-10-12"
    assert "Preserve both" in note["date_disagreement"]["resolution"]


def test_ripple_related_party_credit_is_not_the_cantor_eloc():
    events = {x["event_id"]: x for x in load_artifact()["actual_capital_events"]}
    credit = events["ripple_related_party_credit_facility"]
    eloc = load_artifact()["eloc_facility"]

    assert credit["lender"] == "Ripple Labs Inc."
    assert credit["drawn_amount_usd"] == 9_700_000
    assert credit["classification"] == "related_party_debt_not_equity_and_not_eloc_proceeds"
    assert credit["repayment_status"] == "not_verified_in_this_capture"
    assert eloc["actual_draw_amount_usd"] is None
