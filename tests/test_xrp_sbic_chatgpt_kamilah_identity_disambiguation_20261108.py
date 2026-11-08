from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261108T071910Z-sbic-chatgpt-benchmark-kamilah-identity-disambiguation.json"
REGISTRY = ROOT / "data/xrp_intelligence/sources/kamilah_stevenson_channel.json"


def test_sbic_chatgpt_academic_benchmark_is_separated_from_japan_sbic() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    sbic = data["academic_sbic"]

    assert sbic["primary_dataset_name"] == "Social Bias Inference Corpus (SBIC)"
    assert sbic["dataset_origin"]["inferences"] == 34_000
    assert sbic["dataset_origin"]["structured_annotations"] == 150_000
    assert sbic["chatgpt_65_9_metric"]["model"] == "GPT-3.5 (the review calls it ChatGPT)"
    assert sbic["chatgpt_65_9_metric"]["value_pct"] == 65.9
    assert "pairwise expert rankings" in sbic["chatgpt_65_9_metric"]["metric"]
    assert "Not classification accuracy" in sbic["chatgpt_65_9_metric"]["not"]
    assert "COVID-19" in sbic["secondary_review"]["mislabel"]
    assert "conflict" in sbic["conflict_resolution"]["secondary_error"].lower()
    assert sbic["relation_to_japan_sbic"].startswith("NONE_ESTABLISHED")
    assert sbic["relation_to_sbi_holdings"] == "NONE_ESTABLISHED"
    assert sbic["relation_to_openai_partnership"].startswith("NONE")

    for receipt in data["source_receipts"]:
        actual = hashlib.sha256(receipt["excerpt"].encode("utf-8")).hexdigest()
        assert actual == receipt["excerpt_sha256"]

    identity = data["kamilah_identity"]
    assert identity["person_identity"]["status"].startswith("CONFIRMED")
    assert identity["candidate_youtube_channel"]["identity_status"] == "UNVERIFIED_CHANNEL_PERSON_RELATION"
    assert identity["conflict_and_risk"]["decision"].startswith("The person is verified; the YouTube channel is not")
    assert len(identity["unverified_video_discovery_candidates"]) == 2
    assert all(v["inventory_action"] == "NOT_ADDED" for v in identity["unverified_video_discovery_candidates"])
    assert identity["existing_registry_state"]["verified_personal_channel_uploads"] == 0
    assert identity["existing_registry_state"]["canonical_channel_verified"] is False

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    assert len(registry["seed_videos"]) == 21
    assert registry["video_inventory_status"]["verified_inventory_count"] == 0
    assert registry["identity_status"]["canonical_channel_verified"] is False
