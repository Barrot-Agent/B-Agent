from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261108T041850Z-kamilah-channel-identity-and-public-video-inventory.json"


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_youtube_channel_id_and_handle_are_explicitly_resolved():
    identity = load_artifact()["identity_resolution"]
    assert identity["youtube_channel_id"] == "UCqUPJMQdkCN6lsLVDnichPA"
    assert identity["youtube_handle"] == "@drkamilahstevenson"
    assert identity["channel_identity_status"] == "VERIFIED_CHANNEL_ID_AND_HANDLE_FROM_YOUTUBE_FIRST_PARTY_SEARCH_RESULT"


def test_person_to_channel_match_is_not_overstated():
    identity = load_artifact()["identity_resolution"]
    assert identity["person_to_channel_match_status"] == "STRONGLY_CORROBORATED_NOT_CONCLUSIVE"
    assert any("No reciprocal first-party website link" in item for item in identity["limitations"])
    assert load_artifact()["inventory_summary"]["direct_watch_page_upload_metadata_verified_count"] == 0


def test_channel_associated_and_external_video_inventory_is_complete_as_recorded():
    artifact = load_artifact()
    channel = artifact["channel_associated_video_candidates"]
    external = artifact["external_publisher_appearances"]
    all_ids = [v["video_id"] for v in channel + external]
    assert len(channel) == 10
    assert len(external) == 3
    assert len(all_ids) == 13
    assert len(set(all_ids)) == len(all_ids)
    assert artifact["inventory_summary"]["inventory_complete"] is False


def test_external_publisher_appearances_are_not_personal_channel_uploads():
    artifact = load_artifact()
    external = artifact["external_publisher_appearances"]
    assert {v["publisher_byline"] for v in external} == {
        "Paul Barron Podcast",
        "TEDx Talks",
        "All Nations Chicago",
    }
    assert all(v["attribution_status"].startswith("EXTERNAL_PUBLISHER_APPEARANCE") for v in external)


def test_glasp_channel_catalog_contains_four_distinct_entries():
    artifact = load_artifact()
    ids = {v["video_id"] for v in artifact["channel_associated_video_candidates"]}
    assert {"cxeX_eu_2H0", "ci0FH73lbCs", "rv0BAV0vLgo", "QslbjGQD0MU"}.issubset(ids)
    source = next(s for s in artifact["source_registry"] if s["source_id"] == "glasp_channel_catalog_20261108")
    assert source["source_type"] == "secondary_channel_catalog"


def test_transcript_spelling_variants_do_not_create_separate_person_records():
    identity = load_artifact()["identity_resolution"]
    variants = identity["transcript_name_variants"]
    assert variants["byline"] == "Kamilah Stevenson"
    assert variants["transcript_self_introduction"] == "Camila Stevenson appears in three retrieved transcript excerpts."
    assert "not as proof of a separate person" in variants["interpretation"]


def test_video_claims_are_not_admitted_as_xrp_features_or_forecasts():
    artifact = load_artifact()
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
    assert artifact["forecast"]["video_claims_admitted_as_features"] is False
