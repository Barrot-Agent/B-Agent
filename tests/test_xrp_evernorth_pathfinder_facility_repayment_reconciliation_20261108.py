import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261108T142607Z-evernorth-pathfinder-facility-repayment-reconciliation.json"
PRIOR = ROOT / "research" / "xrp_intelligence" / "20261108T140510Z-evernorth-closing-capital-and-xrp-flow-reconciliation.json"


CORRECTION = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261108T143010Z-evernorth-pathfinder-facility-repayment-hash-correction.json"
)

def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def load_correction():
    return json.loads(CORRECTION.read_text(encoding="utf-8"))


def test_corrected_sec_excerpt_hashes_and_lineage_are_explicit():
    artifact = load_artifact()
    correction = load_correction()
    assert correction["supersedes_artifact_id"] == artifact["artifact_id"]
    assert correction["previous_artifact_blob_sha"] == "0f81bf15dae14b7760d3ecf10483a63276a6e0ed"
    assert correction["previous_test_blob_sha"] == "5d7099cda4544d3165121cf8ad665eac52df1ab6"
    assert correction["supersedes_fields"] == ["source_excerpts[*].sha256"]
    assert len(correction["corrected_source_excerpts"]) == 4
    for receipt in correction["corrected_source_excerpts"]:
        assert hashlib.sha256(receipt["text"].encode("utf-8")).hexdigest() == receipt["sha256"]
        assert receipt["hash_algorithm"] == "SHA-256"
        assert "not raw HTTP bytes" in receipt["hash_scope"]
        assert receipt["source_id"] == "sec_s1_20261030"
    assert correction["source_independence"]["primary_source_groups"] == 1
    assert correction["source_independence"]["independent_primary_confirmations"] == 0


def test_original_excerpt_hashes_are_preserved_and_explicitly_superseded():
    artifact = load_artifact()
    correction = load_correction()
    assert [item["sha256"] for item in artifact["source_excerpts"]] == [
        "dc75e0dc07e3c0f696b9e8bafbbd967805ac0bd1d71d89d0efe009bdb82bb875",
        "f9562531b166a4aeecdf3b3f76a44cb397b5f6b8a339cdcd5f44483209fcdfa7",
        "acb2ec0eb551825938e8251fcb6e68056b18417ab7aced9a0ae3d80df7033224",
        "31f469c5fb666929ecfdc54c9b8629da1c54011ee899fb34b93bf83ec4bf3f9d"
    ]
    assert correction["append_only"] is True
    assert correction["reconciliation_facts_unchanged"] is True


def test_hash_correction_does_not_change_facility_or_forecast_interpretation():
    artifact = load_artifact()
    correction = load_correction()
    assert correction["full_oct_7_balance_repayment_status"] == "UNKNOWN"
    assert artifact["reconciliation"]["full_oct_7_balance_repayment_status"] == "UNKNOWN"
    assert artifact["model_admission"]["eligible"] is False
    assert artifact["forecast_status"] == "NOT_ISSUED"

def test_june_30_balance_and_october_7_balance_are_not_conflated():
    facility = load_artifact()["facility"]
    reconciliation = load_artifact()["reconciliation"]
    assert facility["balance_as_of_2026_06_30_usd"] == 6_554_788
    assert facility["drawn_as_of_2026_10_07_usd"] == 9_700_000
    assert facility["amended_limit_as_of_2026_10_07_usd"] == 10_000_000
    assert reconciliation["june_30_balance_usd"] != reconciliation["oct_7_drawn_balance_usd"]


def test_pro_forma_payment_is_disclosed_and_matched_but_not_overstated():
    item = load_artifact()["reconciliation"]["pro_forma_adjustment_q"]
    assert item["amount_usd"] == 6_554_788
    assert item["cash_decrease_usd"] == 6_554_788
    assert item["related_party_note_payable_decrease_usd"] == 6_554_788
    assert item["exact_amount_match_to_june_30_balance"] is True
    assert item["facility_identity_match"] == "STRONG_INFERENCE_NOT_EXPLICITLY_NAMED_IN_ADJUSTMENT_Q"
    assert item["actual_bank_settlement_independently_verified"] is False


def test_full_october_7_balance_and_post_closing_balance_remain_unknown():
    reconciliation = load_artifact()["reconciliation"]
    assert reconciliation["full_oct_7_balance_repayment_status"] == "UNKNOWN"
    assert reconciliation["post_closing_facility_balance_status"] == "UNKNOWN"
    assert "does not reconcile" in reconciliation["repayment_status_note"]
    assert "A historical/pro forma $6,554,788 payment is disclosed" in load_artifact()["interpretation"]["correction"]


def test_competing_repayment_hypotheses_are_preserved_without_probabilities():
    hypotheses = load_artifact()["competing_hypotheses"]
    assert {item["id"] for item in hypotheses} == {"H1", "H2", "H3", "H4"}
    assert all(item["probability"] is None for item in hypotheses)


def test_related_party_debt_is_not_admitted_as_xrp_demand():
    artifact = load_artifact()
    assert artifact["model_admission"]["eligible"] is False
    assert "not a verified XRP purchase" in artifact["classification"]
    assert artifact["forecast_status"] == "NOT_ISSUED"


def test_prior_capital_artifact_is_preserved_as_historical_record():
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    facility = prior["capital_ledger"]["ripple_related_party_facility"]
    assert facility["repayment_status"] == "UNKNOWN"
    assert "does not confirm repayment" in facility["repayment_status_note"]
    assert load_artifact()["append_only"] is True
    assert load_artifact()["correction_scope"].startswith("Corrects only the repayment interpretation")
