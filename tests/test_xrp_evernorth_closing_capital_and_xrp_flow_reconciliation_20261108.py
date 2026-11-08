import hashlib
import json
import math
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261108T140510Z-evernorth-closing-capital-and-xrp-flow-reconciliation.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_all_normalized_sec_and_secondary_excerpt_hashes_match():
    artifact = load_artifact()
    assert len(artifact["source_receipts"]) == 12
    for receipt in artifact["source_receipts"]:
        assert hashlib.sha256(receipt["excerpt"].encode("utf-8")).hexdigest() == receipt["sha256"]
        assert receipt["retrieved_at_utc"] is None
        assert "normalized excerpt" in receipt["hash_scope"]


def test_cash_proceeds_are_reconciled_without_double_counting():
    ledger = load_artifact()["capital_ledger"]
    closing = ledger["closing"]
    components = ledger["private_placement_components"]

    private_placement_cash = (
        components["advance_funding"]["cash_usd"]
        + components["delayed_funding"]["cash_usd"]
    )
    gross_cash = private_placement_cash + closing["trust_account_cash_released_after_redemptions_usd_approx"]

    assert private_placement_cash == 224_550_000
    assert closing["private_placement_cash_usd_approx"] == 224_600_000
    assert gross_cash == 272_550_000
    assert closing["reported_gross_cash_usd_approx"] == 272_600_000
    assert closing["transaction_expenses_deducted"] is False


def test_in_kind_xrp_and_cash_purchased_xrp_remain_separate():
    ledger = load_artifact()["capital_ledger"]
    c = ledger["private_placement_components"]

    in_kind = (
        c["advance_funding"]["inkind_xrp"]
        + c["delayed_funding"]["inkind_xrp"]
        + c["series_c"]["inkind_xrp"]
        + c["ripple_contribution"]["inkind_xrp"]
        + c["contributor_related_party"]["inkind_xrp"]
    )
    assert math.isclose(in_kind, 388_910_554.061435, abs_tol=1e-6)
    assert math.isclose(ledger["reconstructed_totals"]["in_kind_xrp"], in_kind, abs_tol=1e-6)

    purchased = ledger["actual_xrp_purchase"]["xrp_purchased"]
    assert math.isclose(purchased, 84_365_876.3625, abs_tol=1e-6)
    assert ledger["actual_xrp_purchase"]["cash_used_usd"] == 214_100_000
    assert math.isclose(
        in_kind + purchased,
        ledger["reconstructed_totals"]["reconstructed_total_xrp"],
        abs_tol=1e-6,
    )
    assert ledger["actual_xrp_purchase"]["status"] == "issuer-reported actual acquisition with cash proceeds"


def test_note_proceeds_are_actual_cash_but_not_a_verified_xrp_purchase():
    note = load_artifact()["capital_ledger"]["convertible_note"]

    assert note["principal_usd"] == 30_000_000
    assert note["issue_and_payment_date"] == "2026-10-12"
    assert note["net_cash_after_fee_usd"] == 29_000_000
    assert note["advisor_fee_usd"] == 1_000_000
    assert note["specific_xrp_purchase_traced"] is False
    assert note["purchaser"] == (
        "NH Investment & Securities Co., Ltd., as trustee of "
        "Kyobo AIM Corporate Finance General Private Investment Trust No. 3"
    )


def test_ripple_related_party_facility_is_not_external_equity_capital():
    facility = load_artifact()["capital_ledger"]["ripple_related_party_facility"]

    assert facility["facility_cap_usd"] == 10_000_000
    assert facility["drawn_as_of_2026_10_07_usd"] == 9_700_000
    assert facility["annual_interest_pct"] == 3.81
    assert facility["repayment_status"] == "UNKNOWN"
    assert "five business days" in facility["repayment_term"]
    assert facility["classification"] == "related-party debt, not independent third-party capital"


def test_eloc_capacity_is_not_cash_and_97_percent_table_row_is_flagged():
    eloc = load_artifact()["capital_ledger"]["eloc"]

    calculated = eloc["maximum_new_shares"] * 14.71 * 0.97
    assert math.isclose(calculated, 74_467_417.8345, abs_tol=0.01)
    assert math.isclose(eloc["formula_recalculation_at_14_71_usd"], calculated, abs_tol=0.01)
    assert math.isclose(eloc["table_discrepancy_usd"], 2_332_582.1655, abs_tol=0.01)
    assert math.isclose(
        eloc["maximum_new_shares"] * 10.00 * 0.97,
        eloc["table_10_dollar_row_formula_result_usd"],
        abs_tol=0.01,
    )
    assert eloc["shares_being_sold_under_prospectus_as_of_date"] is False
    assert eloc["drawdown_verified"] is False
    assert eloc["classification"] == "potential equity financing capacity, not cash received"


def test_delayed_funding_share_count_is_consistent_with_cash_and_xrp_value():
    item = load_artifact()["derived_reconciliations"]["delayed_funding"]

    assert item["cash_usd"] == 10_500_000
    assert item["xrp"] == 200_000
    assert math.isclose(item["xrp_value_usd"], 286_138, abs_tol=0.01)
    assert item["aggregate_value_usd"] == 10_786_138
    assert item["shares_times_10_usd"] == 10_786_130
    assert item["difference_usd"] == -8
    delayed = load_artifact()["capital_ledger"]["private_placement_components"]["delayed_funding"]
    assert delayed["closing_shares_issued"] is True
    assert delayed["exact_subscriber_cash_xrp_split_not_itemized"] is True


def test_sbi_holdings_equity_edge_is_not_mislabeled_as_sbic_or_direct_xrp_purchase():
    artifact = load_artifact()
    edges = artifact["relationship_edges"]
    sbi = next(e for e in edges if e["from"] == "SBI Holdings-affiliated investors")

    assert sbi["to"] == "Evernorth"
    assert "equity" in sbi["relationship"]
    assert "SBIC" in artifact["competing_hypotheses"][4]["statement"]
    assert artifact["competing_hypotheses"][4]["status"] == "disconfirmed"


def test_financing_events_are_context_not_directional_price_features():
    artifact = load_artifact()

    assert artifact["model_admission"]["eligible_as_xrp_price_feature"] is False
    assert artifact["model_admission"]["eligible_as_event_or_supply_context"] is True
    assert artifact["forecast_status"] == "NOT_ISSUED"
