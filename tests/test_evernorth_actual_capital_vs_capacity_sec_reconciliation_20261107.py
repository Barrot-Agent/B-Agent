import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261107T222415Z-evernorth-actual-capital-vs-capacity-sec-reconciliation.json"
)


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_sec_excerpt_hashes_are_exact_and_within_quote_limit():
    data = load()
    limit = data["source_capture_contract"]["maximum_direct_quote_words_per_source"]
    for source in data["sources"]:
        excerpt = source.get("excerpt")
        if excerpt is not None:
            assert len(excerpt.split()) <= limit
            assert hashlib.sha256(excerpt.encode("utf-8")).hexdigest() == source["excerpt_sha256"]
        for item in source.get("excerpts", []):
            assert len(item["text"].split()) <= limit
            assert hashlib.sha256(item["text"].encode("utf-8")).hexdigest() == item["sha256"]


def test_actual_cash_purchase_and_restricted_cash_are_not_conflated():
    capital = load()["capital_ledger"]["actual_cash_and_assets"]
    assert capital["advance_funding_cash_received_exact_usd"] == 214049995
    assert capital["advance_funding_cash_used_for_xrp_purchase_usd"] == 214000000
    assert capital["restricted_cash_remaining_usd"] == 49995
    assert capital["xrp_purchased_exact"] == 84365876.3625
    assert capital["xrp_purchase_average_cost_usd_per_xrp"] == 2.53657058
    assert "20261107T113335Z-evernorth-c07-average-cost-correction-supersession.json" in capital["xrp_purchase_cost_source"]


def test_private_placement_cash_trust_cash_and_in_kind_xrp_are_separate():
    capital = load()["capital_ledger"]["actual_cash_and_assets"]
    assert capital["private_placement_cash_total_usd"] == 224549995
    assert capital["trust_account_release_after_redemptions_usd"] == 47600000
    assert capital["reported_aggregate_gross_cash_proceeds_usd"] == 272600000
    assert capital["reported_transaction_costs_usd"] == 14413386
    components = capital["in_kind_xrp_components"]
    assert sum(components.values()) == capital["in_kind_xrp_total"]
    assert capital["in_kind_xrp_total"] == 388910554.061435
    assert capital["approximate_xrp_holdings_as_of_2026_10_09"] == 473000000
    assert "not cash purchases" in capital["classification"]


def test_cantor_eloc_effective_registration_is_not_a_verified_draw():
    eloc = load()["capital_ledger"]["contingent_equity_capacity"]["cantor_eloc"]
    assert eloc["registration_statement_effective"] is True
    assert eloc["effective_at_utc"] == "2026-10-30T20:00:00Z"
    assert eloc["commencement_status"] == "NOT_VERIFIED_ALL_CONDITIONS"
    assert eloc["maximum_shares"] == 5218935
    assert eloc["illustrative_gross_proceeds_at_cover_price_usd"] == 76800000
    assert eloc["illustrative_net_proceeds_at_cover_price_usd"] == 74400000
    assert eloc["purchase_price"] == "97% of VWAP"
    assert eloc["daily_volume_limit_pct"] == 20
    assert eloc["beneficial_ownership_cap_pct"] == 4.99
    assert eloc["upfront_commitment_fee_usd"] == 521893.5
    assert eloc["fee_due_date"] == "2026-11-06"
    assert eloc["fee_payment_confirmed"] is False
    assert eloc["post_effective_draw_status"].endswith("NOT_PROOF_OF_NONE")


def test_public_warrants_are_contingent_and_not_earmarked_cash():
    warrants = load()["capital_ledger"]["contingent_equity_capacity"]["public_warrants"]
    assert warrants["count"] == 11499992
    assert warrants["exercise_price_usd"] == 11.5
    assert warrants["maximum_gross_cash_exercise_proceeds_usd"] == 132249908
    assert warrants["no_assurance"] is True
    assert warrants["exercise_status"] == "NO_EXERCISE_PROCEEDS_VERIFIED"
    assert "not specifically earmarked for XRP" in warrants["proceeds_use"]


def test_debt_is_separate_from_equity_and_potential_cash_settlement():
    debt = load()["capital_ledger"]["actual_debt_and_related_party_funding"]
    note = debt["convertible_notes"]
    facility = debt["ripple_company_facility"]
    assert note["principal_usd"] == 30000000
    assert note["net_proceeds_before_transaction_expenses_usd"] == 30000000
    assert note["maximum_cash_settlement_on_conversion_usd"] == 120000000
    assert note["purchaser"].startswith("NH Investment & Securities")
    assert facility["borrower"] == "Pathfinder Digital Assets LLC"
    assert facility["lender"] == "Ripple"
    assert facility["drawn_as_of_2026_10_07_usd"] == 9700000
    assert facility["repayment_terms"].startswith("Five business days")
    assert facility["post_closing_repayment_status"] == "UNRESOLVED_NO_REPAYMENT_CONFIRMATION_LOCATED"
    assert debt["ripple_evernorth_facility"]["borrowed_as_of_2026_06_30_usd"] == 0


def test_sbi_holdings_identity_and_evernorth_ownership_are_primary_source_resolved():
    sbi = load()["ownership_and_relationships"]["sbi_holdings"]
    assert sbi["parent_name"] == "SBI Holdings, Inc."
    assert sbi["sbi_stockholder_entities"] == [
        "SBI Venture Fund 2023A Investment LPS",
        "SBI Venture Fund 2023B Investment LPS",
        "SBI PE Holdings Co., Ltd.",
        "SBI Holdings USA, Inc.",
    ]
    assert sbi["class_a_shares"] == 9431914
    assert sbi["class_c_shares"] == 2359038
    assert sbi["total_common_ownership_pct"] == 21.4
    assert sbi["voting_power_pct"] == 39.9
    assert sbi["exact_cash_contribution_usd"] == "NOT_ISOLATED_IN_REVIEWED_FILING"
    assert "distinct from SBI Holdings" in load()["ownership_and_relationships"]["sbic_distinction"]["distinction"]


def test_ripple_and_sponsor_xrp_contributions_are_in_kind_not_cash():
    ripple = load()["ownership_and_relationships"]["ripple_ecosystem"]
    assert ripple["ripple_direct_in_kind_xrp"] == 126791458
    assert ripple["arrington_sponsor_in_kind_xrp"] == 211319096.061435
    assert ripple["larsen_lam_trust_in_kind_xrp"] == 50000000
    assert "not cash purchases" in ripple["classification"]


def test_effectiveness_is_not_sec_approval_and_absence_of_draw_filing_is_not_proof():
    data = load()
    assert "not SEC approval" in data["accounting_reconciliation"]["sec_effectiveness"]
    assert "not proof that no transaction occurred" in data["sources"][-1]["summary"]
    assert data["model_eligibility"]["model_eligible"] is False
    assert data["forecast_status"] == "NOT_ISSUED"
