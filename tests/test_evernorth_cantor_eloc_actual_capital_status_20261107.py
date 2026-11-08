from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261107T231833Z-evernorth-cantor-eloc-registration-fee-and-actual-capital-status.json"
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_eloc_registration_prerequisites_are_distinguished_from_commencement() -> None:
    data = _artifact()
    status = data["status_summary"]

    assert status["registration_statement_file_no"] == "333-299620"
    assert status["initial_s1_filed"] == "2026-10-23"
    assert status["effectiveness_date"] == "2026-10-30"
    assert status["final_424b3_filed"] == "2026-10-30"
    assert status["registration_prerequisites"] == "VERIFIED"
    assert status["full_commencement_under_purchase_agreement_section_7_2"] == "NOT_VERIFIED"
    assert status["actual_cantor_settlements_or_cash_received"] == "NOT_VERIFIED"


def test_eloc_capacity_is_not_reported_as_actual_cash() -> None:
    data = _artifact()
    eloc = data["capital_classification"]["cantor_eloc"]

    assert eloc["share_capacity"] == 5_218_935
    assert eloc["gross_capacity_usd_at_14_71"] == 76_800_000
    assert eloc["estimated_net_capacity_if_fully_used_usd"] == 74_400_000
    assert eloc["actual_cash_received_usd"] == "UNVERIFIED"
    assert eloc["purchase_notices"] == "UNVERIFIED"
    assert eloc["settlements"] == "UNVERIFIED"
    assert eloc["classification"] == "CONTINGENT_EQUITY_CAPACITY_NOT_ACTUAL_CAPITAL_RECEIVED"


def test_fee_deadline_and_internal_prospectus_discrepancy_are_preserved() -> None:
    data = _artifact()
    status = data["status_summary"]
    fee = data["capital_classification"]["upfront_commitment_fee"]
    prospectus = next(
        source for source in data["sources"]
        if source["source_id"] == "evernorth_eloc_final_424b3"
    )

    assert status["upfront_fee_due_date"] == "2026-11-06"
    assert fee["amount_usd"] == 521_893.50
    assert fee["payment_status"] == "NOT_VERIFIED"
    discrepancy = prospectus["internal_filing_discrepancy"]
    assert discrepancy["summary_use_of_proceeds_table_usd"] == 80_700_000
    assert discrepancy["cover_and_detailed_table_usd"] == 76_800_000
    assert discrepancy["status"] == "UNRESOLVED_INTERNAL_INCONSISTENCY"


def test_section_7_2_conditions_are_not_assumed_satisfied_from_effectiveness_alone() -> None:
    data = _artifact()
    agreement = next(
        source for source in data["sources"]
        if source["source_id"] == "evernorth_cantor_purchase_agreement_exhibit_10_1"
    )
    claims = agreement["claims"]

    assert any("all Section 7.2 conditions" in claim for claim in claims)
    assert any("FINRA no-objection" in claim for claim in claims)
    assert any("investor due diligence" in claim for claim in claims)
    assert any("transfer-agent instructions" in claim for claim in claims)
    assert any("comfort letters" in claim for claim in claims)
    assert data["status_summary"]["full_commencement_under_purchase_agreement_section_7_2"] == "NOT_VERIFIED"


def test_actual_cash_debt_capacity_warrants_and_in_kind_xrp_remain_separate() -> None:
    capital = _artifact()["capital_classification"]

    assert capital["actual_cash_received"]["advance_funding_cash_usd"] == 214_049_995
    assert capital["actual_xrp_in_kind"]["xrp"] == 388_910_554
    assert capital["debt"]["drawn_as_of_2026_10_07_usd"] == 9_700_000
    assert capital["cantor_eloc"]["actual_cash_received_usd"] == "UNVERIFIED"
    assert capital["public_warrants"]["theoretical_gross_cash_if_all_cash_exercised_usd"] == 132_249_908
    assert capital["public_warrants"]["actual_exercises_or_cash_received"] == "NOT_VERIFIED"
    assert capital["upfront_commitment_fee"]["classification"] == "CONTRACTUAL_FEE_OUTFLOW_NOT_CAPITAL_RAISED"


def test_coinbase_principal_market_edge_is_not_misrepresented_as_a_partnership() -> None:
    data = _artifact()
    edge = next(
        item for item in data["relationship_edges"]
        if item["predicate"] == "uses_as_principal_market_for_xrp_financial_reporting"
    )

    assert edge["object"] == "Coinbase"
    assert edge["status"] == "PRIMARY_ISSUER_DISCLOSURE_IN_2026-10-30_424B3"
    assert "not a custody agreement" in edge["scope"]


def test_sec_excerpt_hashes_are_not_misrepresented_as_raw_source_hashes() -> None:
    data = _artifact()

    assert data["raw_capture_policy"]["raw_source_sha256"] is None
    assert data["raw_capture_policy"]["no_raw_source_hash_claim"] is True
    for source in data["sources"]:
        assert hashlib.sha256(
            source["normalized_excerpt_text"].encode("utf-8")
        ).hexdigest() == source["normalized_excerpt_sha256"]
        assert source["raw_source_sha256"] is None
        assert source["raw_capture_status"].startswith(("SEC_", "SEC "))


def test_financing_research_does_not_issue_a_forecast_or_trade() -> None:
    data = _artifact()
    assert data["forecast_status"] == "NOT_ISSUED"
    assert data["no_paper_trade"] is True
    assert data["no_real_money_action"] is True
    assert data["feature_admission"]["model_feature_eligible"] is False
