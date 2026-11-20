from __future__ import annotations

import hashlib
import json
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T154537Z-evernorth-actual-capital-eloc-warrant-reconciliation.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_eloc_is_conditional_equity_not_actual_cash_or_debt():
    eloc = load_artifact()["capital_channels"]["eloc"]
    assert eloc["instrument"].startswith("Committed equity facility")
    assert eloc["maximum_shares"] == 5_218_935
    assert eloc["company_sale_discretion"] is True
    assert eloc["oct30_final_prospectus_max_gross_proceeds_usd"] == 76_800_000
    assert eloc["actual_cash_drawn_verified"] is False
    assert eloc["actual_xrp_purchases_from_eloc_verified"] is False
    assert eloc["upfront_commitment_fee_usd"] == 521_893.5


def test_eloc_price_vintages_are_not_a_conflict():
    eloc = load_artifact()["capital_channels"]["eloc"]
    assert eloc["oct23_preliminary_max_gross_proceeds_usd"] == 80_700_000
    assert eloc["oct23_price_assumption_usd"] == 15.46
    assert eloc["oct30_final_prospectus_max_gross_proceeds_usd"] == 76_800_000
    assert eloc["oct29_reference_close_usd"] == 14.71


def test_eloc_and_warrant_registration_numbers_are_separate():
    data = load_artifact()
    reg = data["registration_statement_disambiguation"]
    assert reg["eloc_file_number"] == "333-299620"
    assert reg["public_warrant_file_number"] == "333-294417"
    assert reg["eloc_effect_notice_date_independently_located"] is False


def test_warrants_are_potential_not_actual_cash():
    row = load_artifact()["capital_channels"]["public_warrants"]
    assert row["warrants"] == 11_499_992
    assert row["exercise_price_usd"] == 11.5
    assert row["maximum_cash_exercise_gross_proceeds_usd"] == 132_249_908
    assert row["actual_cash_exercises_verified"] is False


def test_completed_xrp_purchase_and_in_kind_contribution_are_separate():
    data = load_artifact()["capital_channels"]
    assert data["private_placement_cash_used_for_xrp"]["cash_usd"] == 214_100_000
    assert data["private_placement_cash_used_for_xrp"]["xrp_purchased"] == 84_365_876
    assert data["in_kind_xrp_contribution"]["xrp"] == 388_910_554
    assert data["in_kind_xrp_contribution"]["market_purchase"] is False
    assert data["closing_gross_cash"]["gross_cash_usd"] == 272_600_000
    assert data["closing_gross_cash"]["same_as_cash_used_for_xrp_purchase"] is False


def test_note_proceeds_are_not_assumed_to_be_xrp_purchases():
    note = load_artifact()["capital_channels"]["convertible_notes"]
    assert note["principal_usd"] == 30_000_000
    assert note["reported_net_proceeds_before_expenses_usd"] == 30_000_000
    assert note["specific_xrp_purchase_from_note_proceeds_verified"] is False


def test_exact_actual_capital_phrase_search_is_not_overstated():
    row = load_artifact()["exact_phrase_search"]
    assert row["phrase"] == "actual capital"
    assert row["exact_phrase_found"] is False
    assert len(row["primary_filings_checked"]) == 3


def test_primary_source_excerpt_hashes_match():
    for source in load_artifact()["source_registry"]:
        digest = hashlib.sha256(source["normalized_excerpt"].encode("utf-8")).hexdigest()
        assert digest == source["normalized_excerpt_sha256"]
        assert source["raw_http_bytes_captured"] is False


def test_no_forecast_or_real_money_action():
    data = load_artifact()
    assert data["forecast_status"]["status"] == "NOT_ISSUED"
    assert data["forecast_status"]["directional_forecast_issued"] is False
    assert data["safety"]["no_paper_trade"] is True
    assert data["safety"]["no_real_money_action"] is True
