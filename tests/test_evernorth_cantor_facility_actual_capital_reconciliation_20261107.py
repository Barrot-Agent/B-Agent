import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261107T211027Z-evernorth-cantor-facility-actual-capital-reconciliation.json"
)


def _artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_evernorth_facility_artifact_is_well_formed_and_time_bounded():
    record = _artifact()
    assert record["schema_version"] == "1.0"
    assert record["record_type"] == "evernorth_cantor_facility_actual_capital_reconciliation"
    captured = datetime.fromisoformat(record["captured_at_utc"].replace("Z", "+00:00"))
    assert captured.tzinfo is not None
    assert captured.utcoffset() == timezone.utc.utcoffset(captured)


def test_sec_excerpt_receipts_are_short_and_hash_verified():
    record = _artifact()
    contract = record["source_capture_contract"]
    assert contract["raw_wire_bytes_captured"] is False
    assert contract["maximum_direct_quote_words_per_source"] == 25
    for source in record["sources"]:
        assert source["url"].startswith("https://www.sec.gov/")
        assert source["source_independence_group"] == "evernorth_issuer_primary_filing_set"
        if source.get("excerpt") is not None:
            assert len(source["excerpt"].split()) <= 25
            assert hashlib.sha256(source["excerpt"].encode("utf-8")).hexdigest() == source["excerpt_sha256"]


def test_latest_issuer_prospectus_uses_same_share_ceiling_and_newer_price_assumption():
    record = _artifact()
    sec = next(s for s in record["sources"] if s["source_id"] == "SEC_424B3_2026_10_30")
    claims = sec["claims"]
    assert claims["share_ceiling"] == 5218935
    assert claims["oct29_xrpn_close_usd"] == 14.71
    assert claims["issuer_estimated_max_gross_proceeds_usd"] == 76800000
    assert claims["exact_share_ceiling_times_oct29_close_usd"] == 76770533.85
    assert claims["upfront_commitment_fee_usd"] == 521893.5


def test_prior_and_current_gross_estimates_are_price_scenarios_not_two_facilities():
    record = _artifact()["price_assumption_reconciliation"]
    assert record["prior_illustrative_xrpn_price_usd"] == 15.46
    assert record["prior_same_share_ceiling_gross_calculation_usd"] == 80684735.1
    assert record["current_prospectus_xrpn_price_usd"] == 14.71
    assert record["current_same_share_ceiling_gross_calculation_usd"] == 76770533.85
    assert record["difference_is_new_facility"] is False


def test_purchase_capacity_is_optional_and_subject_to_conditions_and_caps():
    record = _artifact()
    claims = next(s for s in record["sources"] if s["source_id"] == "SEC_8K_EXHIBIT_10_1_2026_10_23")["claims"]
    assert claims["issuer_option_to_sell"] is True
    assert claims["investor_purchase_obligation_conditional"] is True
    assert claims["ordinary_purchase_price_percent_of_vwap"] == 97
    assert claims["beneficial_ownership_cap_percent"] == 4.99
    assert claims["purchase_volume_percentage_cap"] == 20
    assert claims["cash_settlement_deadline"] == "5 p.m. New York time on second trading day after share-delivery date"


def test_upfront_fee_is_a_nonrefundable_cost_not_proceeds():
    record = _artifact()
    ledger = record["actual_capital_ledger"]
    assert ledger["upfront_commitment_fee_usd"] == 521893.5
    assert ledger["fee_classification"] == "CASH_COST_NOT_CAPITAL_INFLOW"
    assert ledger["upfront_fee_earned_date"] == "2026-10-23"
    assert "five business days" in ledger["upfront_fee_payment_deadline"]
    assert ledger["additional_costs"]["cantor_expense_reimbursement_cap_usd"] == 500000
    assert ledger["additional_costs"]["qualified_independent_underwriter_fee_usd"] == 200000
    assert ledger["additional_costs"]["treatment"].startswith("Transaction costs")


def test_actual_cash_and_xrp_use_are_not_inferred_from_facility_capacity():
    record = _artifact()
    ledger = record["actual_capital_ledger"]
    assert ledger["realized_gross_cash_from_this_facility_verified_usd"] is None
    assert ledger["realized_net_cash_from_this_facility_verified_usd"] is None
    assert ledger["purchase_notices_publicly_verified_in_reviewed_filings"] == 0
    assert ledger["shares_issued_to_cantor_under_facility_verified"] is None
    assert ledger["xrp_purchased_from_facility_proceeds_verified"] is None
    assert "does not prove" in ledger["caveat"].lower()


def test_evernorth_facility_is_event_context_only_and_no_forecast_is_issued():
    record = _artifact()
    assert record["status"] == "PRIMARY_FILING_RECONCILIATION_MODEL_INELIGIBLE"
    assert record["model_admission"]["model_eligible"] is False
    assert record["forecast_status"] == "NOT_ISSUED"
    assert record["trade_status"] == "NO_TRADE"
