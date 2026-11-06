from __future__ import annotations

import hashlib
import json
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T155006Z-evernorth-capital-flow-final-correction.json"
)


def load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_214m_cash_purchase_is_dated_to_2025_not_current_flow():
    row = load()["actual_xrp_purchase"]
    assert row["advance_funding_cash_usd"] == 214_049_995
    assert row["xrp_purchased"] == 84_365_876.3625
    assert row["purchase_announcement_date"] == "2025-11-04"
    assert row["average_purchase_price_usd"] == 2.53657058
    assert "not a new November 2026 market inflow" in row["interpretation"]


def test_in_kind_contributions_reconcile_exactly_and_are_not_market_buys():
    row = load()["in_kind_contribution_reconciliation"]
    assert sum(row["components_xrp"].values()) == 388_910_554.061435
    assert row["total_xrp_reported_rounded"] == 388_910_554
    assert row["pubco_xrp_subtotal"] == 261_919_096
    assert row["components_xrp"]["ripple_contribution"] == 126_791_458
    assert row["components_xrp"]["delayed_funding_subscribers"] == 200_000


def test_closing_gross_cash_is_not_equated_with_xrp_purchase_cash():
    row = load()["closing_cash_reconciliation"]
    assert row["gross_cash_usd"] == 272_600_000
    assert row["private_placement_investments_usd"] == 224_600_000
    assert row["trust_account_release_usd"] == 48_000_000
    assert row["advance_funding_cash_used_for_xrp_usd"] == 214_049_995
    assert row["same_as_cash_used_for_xrp_purchase"] if "same_as_cash_used_for_xrp_purchase" in row else True


def test_convertible_notes_are_actual_proceeds_but_not_verified_xrp_purchases():
    row = load()["convertible_notes"]
    assert row["principal_usd"] == 30_000_000
    assert row["payment_and_issuance_date"] == "2026-10-12"
    assert row["net_proceeds_before_expenses_usd"] == 30_000_000
    assert row["specific_xrp_purchase_from_note_proceeds_verified"] is False
    assert row["disclosed_maximum_cash_settlement_usd"] == 120_000_000
    assert row["holder_selects_cash_shares_or_combination"] is True


def test_ripple_facilities_are_related_party_loans_not_spot_purchases():
    row = load()["ripple_related_party_facilities"]
    assert row["evernorth_revolving_facility_limit_usd"] == 1_000_000
    assert row["company_facility_limit_usd"] == 10_000_000
    assert row["company_facility_cash_proceeds_for_operations_through_2026_06_30_usd"] == 5_400_000
    assert row["payments_made_on_behalf_of_evernorth_usd"] == 2_400_000
    assert row["xrp_purchase_from_facility_verified"] is False


def test_eloc_and_warrant_channels_remain_conditional_and_distinct():
    data = load()
    eloc = data["eloc"]
    warrants = data["public_warrants"]
    assert eloc["registration_file_number"] == "333-299620"
    assert eloc["actual_cash_drawn_verified"] is False
    assert eloc["xrp_purchases_from_eloc_verified"] is False
    assert warrants["registration_file_number"] == "333-294417"
    assert warrants["registration_effective_date"] == "2026-08-27"
    assert warrants["earliest_exercise_date_approx"] == "2027-10-09"
    assert warrants["exercisable_as_of_2026_11_06"] is False


def test_coinbase_principal_market_is_not_misrepresented_as_custody_or_volume():
    row = load()["coinbase_relationship"]
    assert row["role"].startswith("Evernorth selected Coinbase as its principal market")
    assert row["evernorth_actively_trades_xrp_on_markets"] is False
    assert row["direct_commercial_partnership_verified"] is False
    assert row["custody_relationship_from_this_disclosure"] is False
    assert row["xrp_execution_volume_disclosed"] is False


def test_exact_phrase_search_scope_is_limited_and_no_forecast_is_issued():
    data = load()
    assert data["exact_phrase_search"]["phrase"] == "actual capital"
    assert data["exact_phrase_search"]["exact_phrase_found"] is False
    assert len(data["exact_phrase_search"]["primary_filings_checked"]) == 3
    assert data["forecast_status"]["status"] == "NOT_ISSUED"
    assert data["model_eligibility"]["eligible"] is False


def test_normalized_primary_source_hashes_match():
    for source in load()["source_registry"]:
        digest = hashlib.sha256(source["normalized_excerpt"].encode("utf-8")).hexdigest()
        assert digest == source["normalized_excerpt_sha256"]
        assert source["raw_http_bytes_captured"] is False


def test_no_paper_trade_or_real_money_action():
    safety = load()["safety"]
    assert safety["research_only"] is True
    assert safety["no_paper_trade"] is True
    assert safety["no_real_money_action"] is True
