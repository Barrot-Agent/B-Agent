import json
from decimal import Decimal
from pathlib import Path


ARTIFACT = Path(__file__).resolve().parents[1] / "research/xrp_intelligence/20261108T044555Z-evernorth-primary-capital-structure-xrp-bridge-correction.json"


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_in_kind_xrp_contribution_bridge_reconciles_exactly():
    data = load_artifact()
    bridge = data["capital_bridge"]["in_kind_xrp_components"]
    advance = Decimal(bridge["advance_funding_xrp"])
    delayed = Decimal(bridge["delayed_funding_xrp"])
    series_c = Decimal(bridge["series_c_sponsor_xrp"])
    trust = Decimal(bridge["larsen_lam_childrens_remainder_trust_xrp"])
    ripple = Decimal(bridge["ripple_direct_contribution_to_pathfinder_xrp"])
    pubco_subtotal = advance + series_c + trust
    total = pubco_subtotal + delayed + ripple
    assert pubco_subtotal == Decimal("261919096.061435")
    assert total == Decimal("388910554.061435")
    assert total == Decimal(bridge["total_in_kind_xrp"])
    assert "contained within" in bridge["overlap_rule"]


def test_cash_bridge_does_not_double_count_private_placement_components():
    cash = load_artifact()["capital_bridge"]["cash_subscription_components_usd"]
    private = Decimal(cash["advance_funding_cash"]) + Decimal(cash["delayed_funding_cash"])
    gross = private + Decimal(cash["trust_account_release_after_redemptions"])
    assert private == Decimal("224550000")
    assert gross == Decimal("272550000")
    assert cash["private_placement_cash_rounded_in_filing"] == 224_600_000
    assert cash["gross_closing_cash_rounded_in_filing"] == 272_600_000
    assert "Do not add $214.05M again" in cash["arithmetic_rule"]


def test_xrp_purchase_and_restricted_cash_are_separately_described():
    bridge = load_artifact()["capital_bridge"]
    assert bridge["cash_funded_xrp"]["xrp_purchased_with_advance_funding_cash"] == "84365876.3625"
    assert bridge["cash_funded_xrp"]["restricted_cash_at_pathfinder_as_of_2026_06_30_usd"] == 49_995
    assert "quantity is not separately disclosed" in bridge["cash_funded_xrp"]["restricted_cash_close_treatment"]
    assert bridge["cash_funded_xrp"]["reported_consolidated_xrp_holdings_as_of_2026_10_09_approx"] == "473000000"


def test_pathfinder_and_pubco_liquidity_and_facilities_are_not_conflated():
    data = load_artifact()
    entities = data["entity_liquidity_and_debt"]
    assert entities["pathfinder_as_of_2026_06_30"]["unrestricted_cash_usd"] == 800_000
    assert entities["pathfinder_as_of_2026_06_30"]["net_working_capital_deficit_usd"] == 3_700_000
    assert entities["evernorth_pubco_as_of_2026_06_30"]["unrestricted_cash_usd"] == 100_000
    assert entities["evernorth_pubco_as_of_2026_06_30"]["net_working_capital_deficit_usd"] == 696_100_000
    facility = entities["pathfinder_company_facility"]
    assert facility["borrower"] == "Pathfinder Digital Assets LLC"
    assert facility["borrowed_as_of_2026_10_07_usd"] == 9_700_000
    assert facility["post_close_repayment_or_waiver_verified"] is False
    assert facility["expected_contractual_repayment_date_if_unextended"] == "2026-10-16"
    evernorth_facility = entities["evernorth_facility"]
    assert evernorth_facility["borrower"] == "Evernorth Holdings Inc. (Pubco)"
    assert evernorth_facility["borrowed_as_of_2026_06_30_usd"] == 0


def test_convertible_note_proceeds_are_reconciled_gross_to_net():
    note = load_artifact()["entity_liquidity_and_debt"]["convertible_notes"]
    assert note["principal_usd"] == 30_000_000
    assert note["net_proceeds_before_transaction_expenses_usd_approx"] == 30_000_000
    assert note["net_cash_after_capital_markets_advisor_fee_usd"] == 29_000_000
    assert note["advisor_fee_usd"] == 1_000_000
    assert note["coupon_pct"] == 4
    assert note["maturity_year"] == 2031


def test_eloc_prospectus_inconsistencies_and_non_commencement_are_preserved():
    eloc = load_artifact()["eloc"]
    assert eloc["share_commitment"] == 5_218_935
    assert eloc["registration"]["effective_date"] == "2026-10-30"
    assert eloc["registration"]["registration_condition_verified"] is True
    assert eloc["registration"]["all_section_7_2_commencement_conditions_verified"] is False
    assert eloc["registration"]["commencement_date_verified"] is False
    proceeds = eloc["proceeds_disclosures"]
    assert proceeds["summary_gross_usd_approx"] == 80_700_000
    assert proceeds["cover_gross_usd_approx"] == 76_800_000
    assert proceeds["net_usd_approx"] == 74_400_000
    discrepancy = eloc["table_formula_discrepancy"]
    assert discrepancy["filed_table_amount_usd_approx"] == 76_800_000
    assert discrepancy["exact_shares_times_reference_price_times_97pct_usd"] == 74_467_417.8345
    assert discrepancy["status"].startswith("unresolved")
    assert eloc["fees_and_expenses"]["payment_verified"] is False
    assert eloc["fees_and_expenses"]["expected_deadline_if_effective_2026_10_30"] == "2026-11-06"
    assert eloc["proceeds_disclosures"]["actual_gross_proceeds_verified"] is False


def test_warrant_registration_and_later_prospectus_counts_are_not_conflated():
    warrants = load_artifact()["warrants"]
    assert warrants["pos_am_2026_10_13_registered_public_warrant_shares"] == 11_499_992
    assert warrants["final_424b3_2026_10_30_disclosed_pubco_warrant_shares_issuable"] == 9_283_847
    assert warrants["difference_shares"] == 2_216_145
    assert warrants["count_reconciliation_status"].startswith("unresolved")
    assert warrants["actual_exercise_count_verified"] is False
    assert warrants["actual_cash_proceeds_verified"] is False


def test_ripple_sbi_sponsor_relationship_edges_preserve_legal_entity_distinctions():
    data = load_artifact()
    edges = data["relationships_and_governance"]
    rippleworks = next(x for x in edges if x["from"] == "RippleWorks, Inc.")
    sbi = next(x for x in edges if x["from"] == "SBI-affiliated subscribers")
    ripple = next(x for x in edges if x["from"] == "Ripple Labs Inc.")
    assert "211,319,096 XRP" in rippleworks["relationship"]
    assert "separate nonprofit foundation" in rippleworks["classification"]
    assert "39.9%" in sbi["relationship"]
    assert "not evidence of SBI Holdings majority voting control" in sbi["classification"]
    assert "126,791,458 XRP" in ripple["relationship"]


def test_potential_share_overhang_is_not_reported_as_current_outstanding():
    data = load_artifact()
    overhang = data["potential_equity_overhang_as_disclosed_in_2026_10_30_prospectus"]
    assert overhang["pubco_warrant_shares_issuable"] == 9_283_847
    assert overhang["company_units_exchangeable_or_redeemable_for_class_a"] == 22_953_128
    assert "not current outstanding shares" in overhang["treatment"]


def test_evidence_provenance_and_forecast_gates_remain_fail_closed():
    data = load_artifact()
    assert all(x.get("raw_source_sha256") is None for x in data["source_records"])
    assert data["provenance_quality"]["raw_http_wire_bytes_retained"] is False
    assert data["model_admission"]["eligible"] is False
    assert data["model_admission"]["forecast_status"] == "NOT_ISSUED"
