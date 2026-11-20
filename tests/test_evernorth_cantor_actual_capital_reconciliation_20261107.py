import hashlib
import json
from pathlib import Path


def test_evernorth_actual_capital_and_cantor_facility_are_separated_by_primary_evidence():
    artifact_path = (
        Path(__file__).resolve().parents[1]
        / "research"
        / "xrp_intelligence"
        / "20261107T024800Z-evernorth-cantor-facility-actual-capital-reconciliation.json"
    )
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    instruments = {item["instrument_id"]: item for item in artifact["instruments"]}
    note = instruments["evernorth_2026_10_12_convertible_senior_pik_notes"]
    facility = instruments["evernorth_2026_10_23_cantor_common_stock_purchase_agreement"]

    assert note["principal_usd"] == 30_000_000
    assert note["reported_proceeds_before_transaction_expenses_usd"] == 30_000_000
    assert note["reported_net_cash_after_advisor_fee_usd"] == 29_000_000
    assert note["capital_markets_advisor_fee_usd"] == 1_000_000
    assert note["funding_date"] == "2026-10-12"

    assert facility["maximum_new_shares"] == 5_218_935
    assert facility["purchase_price_formula"] == "97% of applicable VWAP"
    assert facility["company_purchase_obligation"] is False
    assert facility["upfront_commitment_fee_usd"] == 521_893.5
    assert facility["confirmed_eLoc_proceeds_received_usd"] is None
    assert facility["confirmed_eLoc_share_purchases_disclosed_in_reviewed_filings"] is False
    assert facility["preliminary_s1_conditional_gross_proceeds_illustration_usd"] == 80_700_000
    assert facility["final_424b3_conditional_gross_proceeds_illustration_usd"] == 76_800_000

    phrase = artifact["exact_phrase_research"]
    assert phrase["phrase"] == "actual capital"
    assert phrase["issuer_primary_document_searches"][0]["result"] == "NO_MATCH"
    assert phrase["non_primary_match"]["source_classification"].startswith("user-generated")
    assert phrase["non_primary_match"]["published_at"] == "2026-09-17T21:16:03Z"
    assert hashlib.sha256(
        phrase["non_primary_match"]["quoted_excerpt"].encode("utf-8")
    ).hexdigest() == phrase["non_primary_match"]["excerpt_sha256"]

    for source in artifact["primary_sources"]:
        assert source["original_filing_bytes_retained"] is False
        if "evidence_note" in source:
            assert hashlib.sha256(source["evidence_note"].encode("utf-8")).hexdigest() == source["evidence_note_sha256"]
        if "evidence_notes" in source:
            assert [
                hashlib.sha256(note_text.encode("utf-8")).hexdigest()
                for note_text in source["evidence_notes"]
            ] == source["evidence_note_sha256"]

    assert artifact["provenance"]["accounting_reconciliation"]["status"] == "RECONCILED"
    assert artifact["model_admission"]["eligible"] is False
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
    assert artifact["forecast"]["paper_trade_executed"] is False
    assert artifact["forecast"]["real_money_action"] is False
