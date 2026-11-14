import json
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261107-evernorth-capital-capacity-vs-realized-cash.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_public_warrant_capacity_is_contingent_not_realized_cash():
    a = load_artifact()
    s = next(x for x in a["primary_sources"] if x["id"] == "sec_424b3_public_warrants_oct19")
    f = s["key_facts"]
    assert f["public_warrant_shares_registered"] * f["exercise_price_usd_per_share"] == 132249908
    assert "only to the extent" in f["proceeds_condition"]
    assert "General corporate purposes" in f["stated_use_of_proceeds"]


def test_eloc_is_discretionary_and_registration_effective_does_not_prove_a_draw():
    a = load_artifact()
    s = next(x for x in a["primary_sources"] if x["id"] == "sec_424b3_cantor_facility_oct30")
    f = s["key_facts"]
    assert f["eloc_shares_available"] == 5218935
    assert f["purchase_price_formula"] == "97% of applicable VWAP"
    assert "all, some or none" in f["company_discretion"]
    assert "No purchase notice" in f["actual_draw_status"]
    effect = next(x for x in a["primary_sources"] if x["id"] == "sec_effect_cantor_resale_registration_oct30")
    assert effect["effectiveness_date"] == "2026-10-30"


def test_eloc_illustrative_proceeds_math_is_flagged_not_silently_reconciled():
    a = load_artifact()
    m = next(x for x in a["primary_sources"] if x["id"] == "sec_424b3_cantor_facility_oct30")["material_disclosure_reconciliation"]
    expected = 5218935 * 14.71 * 0.97
    assert abs(expected - m["calculated_gross_at_14_71_with_97pct_vwap_usd"]) < 0.01
    assert abs(m["difference_between_reported_76_8m_and_97pct_calculation_usd"] - (76800000 - expected)) < 0.01
    assert m["conclusion"].startswith("The cover and table row")
    assert m["stated_net_proceeds_usd_approx"] == 74400000


def test_warrant_count_delta_remains_unresolved_and_is_not_booked_as_proceeds():
    a = load_artifact()
    r = a["warrant_count_reconciliation"]
    assert r["closing_pubco_warrants_oct09"] - r["pubco_warrant_shares_issuable_oct22"] == 2455798
    assert r["illustrative_cash_if_difference_all_exercised_for_cash_usd"] == 28241677
    assert r["status"] == "UNRECONCILED"
    assert "not actual proceeds" in r["interpretation"]


def test_pik_notes_are_separate_actual_debt_proceeds():
    a = load_artifact()
    s = next(x for x in a["primary_sources"] if x["id"] == "sec_424b3_pik_note_proceeds_oct30")
    f = s["key_facts"]
    assert f["principal_usd"] == 30000000
    assert f["issuance_and_payment_date"] == "2026-10-12"
    assert f["classification"].startswith("Actual debt proceeds")
    assert f["transaction_level_xrp_allocation"] == "Not verified."


def test_actual_capital_phrase_is_secondary_not_issuer_language():
    a = load_artifact()
    hit = a["exact_phrase_research"][0]
    assert hit["phrase"] == "actual capital raised"
    assert hit["source_class"] == "Secondary media"
    assert hit["exact_excerpt"].startswith("Actual capital raised")
    assert "No exact phrase match" in a["exact_phrase_research"][1]["primary_source_search"]


def test_effectiveness_is_not_sec_merits_approval():
    a = load_artifact()
    effect = next(x for x in a["primary_sources"] if x["id"] == "sec_effect_public_warrant_registration_oct19")
    assert effect["effectiveness_date"] == "2026-10-19"
    assert "not SEC endorsement" in effect["interpretation"]
    assert a["model_eligibility"]["status"] == "NOT_ADMITTED"


def test_no_directional_forecast_or_external_execution():
    a = load_artifact()
    assert a["forecast"]["status"] == "NOT_ISSUED"
    assert a["external_actions"] == {
        "orders_sent": False,
        "paper_trade_created": False,
        "real_money_used": False,
    }
