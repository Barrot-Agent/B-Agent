import json
from pathlib import Path


ARTIFACT = Path(__file__).resolve().parents[1] / "research/xrp_intelligence/20261108T043558Z-evernorth-actual-capital-capacity-vs-cash-reconciliation.json"


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_eloc_is_conditional_capacity_not_actual_cash():
    data = load_artifact()
    eloc = data["eloc"]
    assert eloc["share_commitment"] == 5_218_935
    assert eloc["issuer_discretion"] == "all, some or none; issuer has no obligation to sell the full commitment"
    assert eloc["proceeds_scenarios"]["prospectus_cover_gross_usd_approx"] == 76_800_000
    assert eloc["proceeds_scenarios"]["prospectus_net_usd_approx"] == 74_400_000
    assert eloc["proceeds_scenarios"]["actual_gross_proceeds_verified"] is False
    assert eloc["proceeds_scenarios"]["actual_net_proceeds_verified"] is False
    assert eloc["proceeds_scenarios"]["first_vwap_purchase_verified"] is False
    assert data["model_admission"]["eligible"] is False


def test_registration_effectiveness_does_not_prove_commencement_or_draw():
    registration = load_artifact()["eloc"]["registration"]
    assert registration["effective_date"] == "2026-10-30"
    assert registration["registration_condition"] == "verified"
    assert registration["all_section_7_2_commencement_conditions"] == "not independently verified"
    assert registration["commencement_date_verified"] is False


def test_commitment_fee_is_not_capital_raised():
    fee = load_artifact()["eloc"]["upfront_commitment_fee"]
    assert fee["amount_usd"] == 521_893.50
    assert fee["fully_earned_and_non_refundable_per_contract"] is True
    assert fee["expected_deadline_if_effective_2026_10_30"] == "2026-11-06"
    assert fee["payment_verified"] is False
    assert "not capital raised" in fee["classification"]


def test_warrant_capacity_is_not_exercised_proceeds():
    warrants = load_artifact()["warrants"]
    assert warrants["public_warrant_shares_max"] == 11_499_992
    assert warrants["cash_exercise_price_usd"] == 11.50
    assert warrants["theoretical_max_gross_cash_proceeds_if_all_exercised"] == 132_249_908
    assert warrants["exercise_verified"] is False
    assert warrants["actual_proceeds_verified"] is False


def test_cash_deployed_debt_and_in_kind_xrp_are_not_double_counted():
    capital = load_artifact()["capital_reconciliation"]
    assert capital["gross_cash_proceeds_at_closing_usd_approx"] == 272_600_000
    assert capital["gross_cash_components_usd_approx"] == {
        "private_placements": 224_600_000,
        "trust_account_release_after_redemptions": 48_000_000,
    }
    assert capital["private_placement_cash_used_to_purchase_xrp_usd_approx"] == 214_000_000
    assert capital["xrp_purchased_with_cash"] == 84_365_876
    assert capital["in_kind_xrp_contributions"] == 388_910_554
    assert capital["xrp_raised_under_private_placement_subscription_agreements"] == 261_919_096
    assert "do not add the figures" in capital["xrp_in_kind_overlap_rule"]
    assert capital["xrp_holdings_as_of_2026_10_09_approx"] == 473_000_000
    assert capital["cash_balance_as_of_2026_06_30_usd"] == 100_000
    assert capital["ripple_intercompany_facility"]["borrowed_as_of_2026_10_07_usd"] == 9_700_000
    assert "do not add it to" in capital["overlap_rule"]


def test_prospectus_internal_14_71_row_inconsistency_is_preserved():
    issue = load_artifact()["eloc"]["prospectus_internal_inconsistency"]
    assert issue["status"].startswith("unresolved")
    assert issue["filed_table_row_at_14_71_usd"] == 76_800_000
    assert issue["calculated_97pct_value_usd"] == 74_467_417.83
    assert issue["arithmetic_difference_usd"] == 2_332_582.17
    assert "Do not treat the inconsistent row" in issue["interpretation"]


def test_primary_source_provenance_and_hash_scope_are_explicit():
    data = load_artifact()
    assert len(data["source_records"]) == 5
    assert {x["source_id"] for x in data["source_records"]} >= {
        "SEC_8K_ELOC_20261023",
        "SEC_424B3_ELOC_20261030",
        "SEC_EFFECT_ELOC_20261030",
        "SEC_S1_LIQUIDITY_20261030",
        "SEC_WARRANT_POSAM_20261014",
    }
    assert data["research_limitations"]["raw_http_wire_bytes_retained"] is False
    assert data["research_limitations"]["source_text_hashes_are_excerpt_hashes"] is True
