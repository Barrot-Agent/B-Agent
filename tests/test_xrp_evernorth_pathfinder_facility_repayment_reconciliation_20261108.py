import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261108T142607Z-evernorth-pathfinder-facility-repayment-reconciliation.json"
PRIOR = ROOT / "research" / "xrp_intelligence" / "20261108T140510Z-evernorth-closing-capital-and-xrp-flow-reconciliation.json"


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_sec_excerpt_hashes_and_lineage_are_explicit():
    artifact = load_artifact()
    assert len(artifact["source_excerpts"]) == 4
    for receipt in artifact["source_excerpts"]:
        assert hashlib.sha256(receipt["text"].encode("utf-8")).hexdigest() == receipt["sha256"]
        assert receipt["hash_algorithm"] == "SHA-256"
        assert "not raw HTTP bytes" in receipt["hash_scope"]
        assert receipt["source_id"] == "sec_s1_20261030"
    assert artifact["primary_sources"][0]["accession"] == "0001628280-26-068609"
    assert artifact["source_independence"]["primary_source_groups"] == 1
    assert artifact["source_independence"]["independent_primary_confirmations"] == 0


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
