from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106-evernorth-ripple-sbi-coinbase-bitgo-capital-reconciliation.json"
)


def _data() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_cash_purchases_in_kind_xrp_and_reported_holdings_reconcile_without_double_counting():
    data = _data()
    ledger = data["capital_ledger"]
    in_kind = ledger["in_kind_xrp_contributions"]
    component_sum = (
        in_kind["advance_funding_xrp"]
        + in_kind["delayed_funding_xrp"]
        + in_kind["series_c_arrington_xrp"]
        + in_kind["contributor_related_party_larsen_trust_xrp"]
        + in_kind["ripple_to_pathfinder_xrp"]
    )
    assert math.isclose(component_sum, in_kind["total_xrp"], abs_tol=0.000001)
    holdings = ledger["holdings_reconciliation"]
    assert math.isclose(
        holdings["cash_purchased_xrp"] + holdings["in_kind_xrp"],
        holdings["arithmetic_total_xrp"],
        abs_tol=0.000001,
    )
    assert abs(holdings["arithmetic_total_xrp"] - holdings["reported_approximate_holdings_xrp"]) < 1_000_000
    assert ledger["historical_xrp_purchase"]["cash_used_usd"] == 214_100_000
    assert ledger["historical_xrp_purchase"]["xrp_purchased"] == 84_365_876


def test_ripple_company_facility_and_evernorth_facility_are_not_conflated():
    data = _data()["capital_ledger"]
    company = data["ripple_company_facility"]
    evernorth = data["ripple_evernorth_facility"]
    assert company["amended_limit_usd"] == 10_000_000
    assert company["borrowed_usd"] == 9_700_000
    assert company["borrower"] == "Pathfinder Digital Assets LLC (the Company), not Evernorth directly."
    assert company["classification"].startswith("Related-party debt")
    assert evernorth["limit_usd"] == 1_000_000
    assert evernorth["borrowed_usd"] == 0
    assert evernorth["borrowed_as_of"] == "2026-06-30"
    assert evernorth["later_draw_disclosed_in_filing_section"] is False


def test_sbi_holdings_is_parent_of_four_entities_and_individual_subscription_is_not_inferred():
    sbi = _data()["sbi_holdings_ownership"]
    assert sbi["parent"] == "SBI Holdings, Inc."
    assert len(sbi["entities"]) == 4
    assert sbi["class_a_shares"] == 9_431_914
    assert sbi["class_c_shares"] == 2_359_038
    assert sbi["class_c_voting_status"].startswith("Non-voting")
    assert sbi["contractual_group_voting_ownership_cap_pct"] == 39.9
    assert "Not separately disclosed" in sbi["individual_cash_xrp_subscription_split"]
    assert "not SBIC" in sbi["identity_resolution"]


def test_notes_and_eloc_are_distinguished_from_xrp_purchases_and_cash_received():
    ledger = _data()["capital_ledger"]
    notes = ledger["convertible_notes"]
    eloc = ledger["cantor_committed_equity_facility"]
    assert notes["principal_usd"] == 30_000_000
    assert notes["coupon_type"] == "4.00% payment-in-kind interest"
    assert "No evidence" in notes["xrp_purchase_evidence"]
    assert eloc["proceeds_received_as_of_prospectus_date_usd"] == 0
    assert eloc["maximum_new_class_a_shares"] == 5_218_935
    assert eloc["commitment_fee_usd"] == 521_893.50
    assert "Conditional potential future" in eloc["classification"]


def test_coinbase_accounting_market_is_not_mistaken_for_custody_or_active_trading():
    custody = _data()["custody_accounting_and_collateral"]
    coinbase = custody["coinbase_principal_market"]
    assert coinbase["selected"] is True
    assert coinbase["management_says_it_does_not_actively_trade_xrp"] is True
    assert "does not prove Coinbase executed" in coinbase["inference_prohibited"]
    assert custody["custodian"] == "BitGo Bank & Trust, National Association, formerly BitGo Trust Company, Inc."


def test_bitgo_cold_storage_shared_insurance_and_collateral_limits_are_explicit():
    custody = _data()["custody_accounting_and_collateral"]
    insurance = custody["insurance"]
    assert custody["custody_status_as_of_prospectus"].startswith("All XRP held through BitGo")
    assert insurance["aggregate_shared_coverage_usd"] == 250_000_000
    assert insurance["dedicated_to_evernorth"] is False
    assert insurance["coverage_as_pct_of_evernorth_xrp_value_as_of_2026_10_09"] == 36.9
    assert "may not be available" in custody["collateral_and_liquidity_risk"]


def test_capital_reconciliation_is_not_admitted_as_a_directional_forecast():
    data = _data()
    assert data["source_receipt"]["raw_http_bytes_captured"] is False
    assert data["exact_phrase_research"]["exact_phrase_found_in_this_sec_filing"] is False
    assert data["model_eligibility"]["eligible_as_price_or_flow_feature"] is False
    assert data["model_eligibility"]["forecast_status"] == "NOT_ISSUED"


def test_sec_normalized_evidence_receipt_is_reproducible():
    data = _data()
    receipt = data["source_receipt"]
    assert hashlib.sha256(receipt["normalized_evidence"].encode("utf-8")).hexdigest() == receipt["normalized_evidence_sha256"]
    assert receipt["normalized_evidence_words"] == len(receipt["normalized_evidence"].split())
    assert receipt["quote_word_count"] == len(receipt["short_exact_quote"].split())
    assert receipt["quote_word_count"] <= 25
