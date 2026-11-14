import json
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261107T092400Z-sbi-evernorth-ownership-population-reconciliation.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_four_sbi_stockholder_table_totals_recompute_from_individual_entities():
    artifact = load_artifact()
    table = artifact["sources"][0]["reported_four_entity_table"]
    class_a = sum(row["class_a"] for row in table.values())
    class_c = sum(row["class_c"] for row in table.values())
    assert class_a == 9_431_914
    assert class_c == 2_359_038
    assert artifact["sources"][0]["aggregate_footnote_class_a"] == class_a


def test_closing_note_and_beneficial_ownership_table_difference_is_preserved():
    reconciliation = load_artifact()["derived_reconciliation"]
    table = reconciliation["four_sbi_stockholder_table_total"]
    closing = reconciliation["closing_note_total"]
    difference = reconciliation["difference"]
    assert table["class_a"] == 9_431_914
    assert closing["class_a"] == 11_748_249
    assert table["class_c"] == closing["class_c"] == 2_359_038
    assert difference["class_a"] == 2_316_335
    assert difference["class_c"] == 0
    assert reconciliation["status"] == "UNRESOLVED_POPULATION_SCOPE_OR_TIMING_DIFFERENCE"
    assert reconciliation["do_not_average_or_force_reconcile"] is True


def test_sbi_holdings_usa_form3_matches_its_individual_s1_table_row():
    artifact = load_artifact()
    direct = artifact["sources"][2]["direct_holdings"]
    row = artifact["sources"][0]["reported_four_entity_table"]["SBI_Holdings_USA"]
    assert direct == row
    assert artifact["sources"][2]["relationship"].find("10% owner") >= 0


def test_class_c_is_not_treated_as_current_voting_class_a():
    artifact = load_artifact()
    terms = artifact["sources"][0]["class_c_rights"]
    assert "non-voting" in terms
    assert "39.9%" in terms
    assert "not voting-equivalent" in artifact["derived_reconciliation"]["share_class_sum_warning"]


def test_sbi_parent_control_and_sbic_entity_separation_are_explicit():
    control = load_artifact()["control_and_voting"]
    assert control["SBI_definition"] == "SBI Holdings, Inc."
    assert len(control["SBI_Stockholders"]) == 4
    assert "controlled by SBI Holdings" in control["control"]
    assert "not SBI Holdings" in control["sbic_separation"]


def test_ownership_discrepancy_is_not_admitted_as_xrp_purchase_or_inventory():
    admission = load_artifact()["model_admission"]
    assert admission["eligible"] is False
    assert "not as an XRP purchase" in admission["reason"]
