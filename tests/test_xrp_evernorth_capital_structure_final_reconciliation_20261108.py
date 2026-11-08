import json
from decimal import Decimal
from pathlib import Path


ARTIFACT = Path(__file__).resolve().parents[1] / "research/xrp_intelligence/20261108T044733Z-evernorth-capital-structure-final-reconciliation.json"


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_in_kind_xrp_bridge_reconciles_exactly():
    bridge = load_artifact()["capital_bridge"]["in_kind_xrp"]
    pubco = Decimal(bridge["advance_funding_xrp"]) + Decimal(bridge["series_c_sponsor_xrp"]) + Decimal(bridge["larsen_lam_trust_xrp"])
    total = pubco + Decimal(bridge["delayed_funding_xrp"]) + Decimal(bridge["ripple_direct_contribution_to_pathfinder_xrp"])
    assert pubco == Decimal("261919096.061435")
    assert total == Decimal("388910554.061435")
    assert total == Decimal(bridge["total_in_kind_xrp"])
    assert "contained within" in bridge["reconciliation"]


def test_cash_subscription_bridge_is_rounded_without_double_counting():
    cash = load_artifact()["capital_bridge"]["cash_subscription_usd"]
    private = Decimal(cash["advance_funding_cash"]) + Decimal(cash["delayed_funding_cash"])
    gross = private + Decimal(cash["trust_account_release_after_redemptions"])
    assert private == Decimal("224550000")
    assert gross == Decimal("272550000")
    assert cash["private_placement_cash_rounded"] == 224_600_000
    assert cash["gross_closing_cash_rounded"] == 272_600_000
    assert "not additional to" in cash["reconciliation"]


def test_restricted_cash_was_used_at_close_not_left_as_post_close_restricted_cash():
    cash = load_artifact()["capital_bridge"]["cash_funded_xrp"]
    assert cash["pathfinder_restricted_cash_as_of_2026_06_30_usd"] == 49_995
    assert "used to purchase XRP at closing" in cash["close_treatment"]
    assert "not separately disclosed" in cash["close_treatment"]


def test_pathfinder_and_pubco_liquidity_and_debt_are_distinct():
    data = load_artifact()["entity_liquidity_and_debt"]
    pathfinder = data["pathfinder_as_of_2026_06_30"]
    pubco = data["evernorth_pubco_as_of_2026_06_30"]
    assert pathfinder["cash_usd"] == 800_000
    assert pathfinder["net_working_capital_deficit_usd"] == 3_700_000
    assert pathfinder["related_party_receivable_from_evernorth_usd"] == 5_900_000
    assert "related_party_payable_to_evernorth_usd" not in pathfinder
    assert pubco["cash_usd"] == 100_000
    assert pubco["net_working_capital_deficit_usd"] == 696_100_000
    facility = data["pathfinder_company_facility"]
    assert facility["borrower"] == "Pathfinder Digital Assets LLC"
    assert facility["borrowed_as_of_2026_10_07_usd"] == 9_700_000
    assert "within five business days" in facility["repayment_rule"]
    assert facility["calendar_due_date"] == "not asserted; the agreement's Business Day definition and applicable holiday calendar were not fully reconciled in this pass"
    assert facility["post_close_repayment_or_waiver_verified"] is False
    evernorth_facility = data["evernorth_facility"]
    assert evernorth_facility["borrower"] == "Evernorth Holdings Inc. (Pubco)"
    assert evernorth_facility["borrowed_as_of_2026_06_30_usd"] == 0


def test_convertible_note_gross_to_net_bridge_is_explicit():
    note = load_artifact()["entity_liquidity_and_debt"]["convertible_notes"]
    assert note["principal_usd"] == 30_000_000
    assert note["net_proceeds_before_transaction_expenses_usd_approx"] == 30_000_000
    assert note["net_cash_after_capital_markets_advisor_fee_usd"] == 29_000_000
    assert note["advisor_fee_usd"] == 1_000_000
    assert note["coupon_pct"] == 4
    assert note["maturity_year"] == 2031


def test_eloc_proceeds_and_table_inconsistencies_are_preserved():
    eloc = load_artifact()["eloc"]
    assert eloc["share_commitment"] == 5_218_935
    assert eloc["registration"]["effective_date"] == "2026-10-30"
    assert eloc["registration"]["registration_condition_verified"] is True
    assert eloc["registration"]["all_section_7_2_conditions_verified"] is False
    assert eloc["registration"]["commencement_date_verified"] is False
    proceeds = eloc["proceeds_disclosures"]
    assert proceeds["summary_gross_usd_approx"] == 80_700_000
    assert proceeds["cover_gross_usd_approx"] == 76_800_000
    assert proceeds["net_usd_approx"] == 74_400_000
    table = eloc["table_formula_discrepancy"]
    assert table["filed_table_amount_usd_approx"] == 76_800_000
    assert table["shares_times_price_times_97pct_usd"] == 74_467_417.8345
    assert table["status"].startswith("unresolved")
    fees = eloc["fees_and_expenses"]
    assert fees["upfront_commitment_fee_usd"] == 521_893.50
    assert fees["payment_verified"] is False
    assert fees["expected_deadline_if_effective_2026_10_30"] == "2026-11-06"


def test_warrant_registration_and_later_prospectus_counts_remain_distinct():
    warrants = load_artifact()["warrants"]
    assert warrants["pos_am_registered_public_warrant_shares_2026_10_13"] == 11_499_992
    assert warrants["final_424b3_disclosed_pubco_warrant_shares_issuable_2026_10_30"] == 9_283_847
    assert warrants["difference_shares"] == 2_216_145
    assert warrants["reconciliation_status"].startswith("unresolved")
    assert warrants["actual_exercise_count_verified"] is False
    assert warrants["actual_cash_proceeds_verified"] is False


def test_sbi_subscription_amounts_are_not_over_attributed():
    edge = next(x for x in load_artifact()["relationships_and_governance"] if x["from"] == "SBI Stockholders and affiliates")
    assert "39.9%" in edge["relationship"]
    assert "not attributed entirely to SBI" in edge["relationship"]
    assert "not evidence of SBI Holdings majority voting control" not in edge["relationship"]


def test_rippleworks_ripple_trust_and_sponsor_edges_are_distinct():
    edges = load_artifact()["relationships_and_governance"]
    rw = next(x for x in edges if x["from"] == "RippleWorks, Inc.")
    ripple = next(x for x in edges if x["from"] == "Ripple Labs Inc.")
    trust = next(x for x in edges if x["from"] == "Larsen Lam Children's Remainder Trust")
    assert "211,319,096.061435 XRP" in rw["relationship"]
    assert "separate nonprofit foundation" in load_artifact()["entity_definitions"]["rippleworks"]
    assert "126,791,458 XRP" in ripple["relationship"]
    assert "50,000,000 XRP" in trust["relationship"]


def test_strategy_is_not_mistaken_for_realized_yield_or_revenue():
    strategy = load_artifact()["custody_and_strategy"]
    assert strategy["primary_kpi"] == "XRP per share"
    assert "no revenue generated" in strategy["revenue_status"]
    assert "no deployment or realized yield" in strategy["execution_status"]


def test_manual_sec_research_does_not_claim_raw_source_receipts_or_forecasts():
    data = load_artifact()
    assert all(x["raw_source_sha256"] is None for x in data["source_records"])
    assert data["provenance_quality"]["raw_http_wire_bytes_retained"] is False
    assert data["provenance_quality"]["raw_source_sha256_captured"] is False
    assert data["forecast_and_model_admission"]["eligible"] is False
    assert data["forecast_and_model_admission"]["forecast_status"] == "NOT_ISSUED"
