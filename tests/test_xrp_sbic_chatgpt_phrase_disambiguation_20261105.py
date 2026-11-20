import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T143014Z-sbic-chatgpt-exact-phrase-disambiguation.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_primary_sbic_definition_is_social_bias_inference_corpus():
    data = load()
    assert data["entity_resolution"]["primary_academic_meaning"]["name"] == "Social Bias Inference Corpus"
    assert data["source_registry"][0]["source_id"] == "ziems_etal_computational_social_science_benchmarks"
    assert data["source_registry"][1]["source_id"] == "sap_etal_social_bias_frames_and_sbic"


def test_chatgpt_65_9_percent_is_pairwise_preference_not_accuracy():
    result = load()["reported_chatgpt_result"]
    assert result["pairwise_author_preference_over_human_gold_pct"]["GPT-3.5"] == 65.9
    assert result["pairwise_author_preference_over_human_gold_pct"]["GPT-4"] == 60.6
    assert result["pairwise_author_preference_over_human_gold_pct"]["text-davinci-003"] == 50.0
    assert "pairwise human-author preference" in result["metric_type"]
    assert "accuracy" in result["not_equivalent_to"]
    assert "market prediction skill" in result["not_equivalent_to"]


def test_primary_paper_separates_covidet_from_sbic():
    source = next(s for s in load()["source_registry"] if s["source_id"] == "ziems_etal_computational_social_science_benchmarks")
    assert any("CovidET as a separate" in claim for claim in source["claims_supported"])


def test_secondary_covid19_expansion_conflict_is_preserved():
    data = load()
    assert data["source_disagreement"]["secondary_position"].startswith("Cheng (2023)")
    assert "conflicts with the primary" in data["source_registry"][2]["limitations"][1]
    assert data["source_disagreement"]["unresolved"]


def test_japanese_sbic_and_sbi_holdings_are_not_conflated_with_dataset():
    entities = load()["entity_resolution"]
    assert entities["japanese_business_meaning"]["entities"] == ["SBIC East Japan", "SBIC Central Japan", "SBIC West Japan"]
    assert entities["sbi_holdings"]["relationship_to_academic_dataset"] == "unrelated; acronym collision only"
    assert entities["japanese_business_meaning"]["relationship_to_academic_dataset"] == "unrelated; acronym collision only"


def test_no_xrp_or_corporate_relationship_is_inferred():
    data = load()
    assert data["xrp_and_institutional_relationships"]["direct_xrp_relationship_established"] is False
    assert data["xrp_and_institutional_relationships"]["relationship_to_ripple_coinbase_circle_or_sbi_holdings"] == "none established by these sources"
    assert data["admission"]["xrp_feature_eligible"] is False
    assert data["admission"]["model_eligible"] is False


def test_source_provenance_and_model_exclusion_are_explicit():
    data = load()
    assert data["source_capture_policy"]["raw_bytes_preserved"] is False
    assert data["source_capture_policy"]["sha256_receipts"] is None
    assert all(source["model_eligible"] is False for source in data["source_registry"])
