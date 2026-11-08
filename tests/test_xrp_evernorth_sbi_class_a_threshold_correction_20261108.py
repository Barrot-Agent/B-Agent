import json
from pathlib import Path


ARTIFACT = Path(__file__).resolve().parents[1] / "research/xrp_intelligence/20261108T050336Z-evernorth-sbi-class-a-threshold-correction.json"


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_sbi_39_9_percent_is_class_a_threshold_not_voting_power_cap():
    threshold = load_artifact()["corrected_facts"]["sbi_affiliated_class_a_threshold"]
    assert threshold["percentage"] == 39.9
    assert threshold["denominator"] == "Outstanding Pubco Class A Common Stock"
    assert threshold["excess_share_treatment"] == "Pubco Class C Common Stock"
    assert threshold["class_c_convertible_to_class_a_under_governing_documents"] is True
    assert threshold["not_a_voting_power_cap"] is True
    assert threshold["not_proof_of_sbi_holdings_direct_registered_ownership"] is True
    assert threshold["not_proof_of_total_39_9_percent_beneficial_ownership"] is True


def test_sbi_specific_class_c_count_is_attributed_to_424b3_not_october_9_8k():
    shares = load_artifact()["corrected_facts"]["closing_share_disclosures"]
    assert shares["sec_424b3_advance_and_delayed_class_a_shares"] == 11_748_249
    assert shares["sec_424b3_advance_and_delayed_class_c_shares"] == 2_359_038
    assert shares["sec_8k_advance_funding_class_a_shares"] == 10_123_015
    assert shares["sec_8k_advance_funding_class_c_shares"] == 2_905_659
    assert shares["sec_8k_delayed_funding_class_a_shares"] == 663_510
    assert shares["sec_8k_sbi_specific_class_c_count"] is None
    assert shares["reconciliation_status"] == "UNRESOLVED_DIFFERENT_ISSUER_DISCLOSURES"


def test_sbi_is_not_over_attributed_and_thresholds_remain_distinct():
    facts = load_artifact()["corrected_facts"]
    assert "certain investors affiliated with SBI Holdings" in facts["sbi_affiliated_class_a_threshold"]["issuer_named_party"].lower()
    assert "Do not attribute" in facts["attribution_limit"]
    thresholds = facts["distinct_thresholds"]
    assert thresholds["sbi_affiliated_investors"]["denominator"] == "Outstanding Pubco Class A Common Stock"
    assert "voting ownership threshold" in thresholds["arrington_sponsor"]["meaning"]
    assert "voting-power restriction" in thresholds["ripple_and_contributor_related_party_entity"]["meaning"]


def test_correction_is_append_only_and_not_model_eligible():
    data = load_artifact()
    assert data["status"]["prior_artifacts"] == "PRESERVED_UNCHANGED"
    assert data["model_admission"]["eligible"] is False
    assert data["model_admission"]["forecast_status"] == "NOT_ISSUED"
    assert data["source_independence"]["independent_confirmation_count"] == 0
    assert all(source["raw_source_sha256"] is None for source in data["source_records"])
