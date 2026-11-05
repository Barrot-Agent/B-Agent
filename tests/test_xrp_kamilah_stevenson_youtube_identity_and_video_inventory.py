import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261105T084500Z-kamilah-stevenson-youtube-identity-and-video-inventory.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_identity_and_fake_page_warning_are_preserved():
    data = load()
    identity = data["identity_assessment"]
    assert identity["person_identity"] == "HIGH_CONFIDENCE_VERIFIED"
    assert identity["canonical_channel_id"] == "NOT_FULLY_VERIFIED"
    assert identity["unverified_candidate_channel"]["status"] == "NOT_ATTRIBUTED"
    assert data["source_quality"]["fake_page_warning_preserved"] is True


def test_only_direct_youtube_creator_metadata_counts_as_own_channel_upload():
    inventory = data = load()["video_inventory"]
    own = [item for item in inventory if item["attribution_status"] == "VERIFIED_CREATOR_UPLOAD"]
    assert {item["video_id"] for item in own} == {"Gy4BuGhAWE8", "QslbjGQD0MU", "8xiy8w2YlfY"}
    assert all(item["creator_label"] == "Kamilah Stevenson" for item in own)


def test_guest_appearance_is_not_misclassified_as_creator_upload():
    data = load()
    guest = next(item for item in data["video_inventory"] if item["video_id"] == "Sulo54IlQ60")
    assert guest["attribution_status"] == "VERIFIED_GUEST_APPEARANCE_NOT_OWN_CHANNEL_UPLOAD"
    assert guest["creator_label"] == "Paul Barron Podcast"


def test_secondary_transcript_candidates_remain_unverified():
    data = load()
    candidates = [item for item in data["video_inventory"] if item["attribution_status"] == "CANDIDATE_PENDING_DIRECT_CHANNEL_METADATA"]
    assert {item["video_id"] for item in candidates} == {"ci0FH73lbCs", "cxeX_eu_2H0"}


def test_third_party_clip_is_excluded_from_creator_inventory():
    data = load()
    clip = next(item for item in data["video_inventory"] if item["video_id"] == "5DzBk8DfoLs")
    assert clip["attribution_status"] == "THIRD_PARTY_CLIP_EXCLUDED_FROM_OWN_CHANNEL_INVENTORY"
    assert clip["creator_label"] == "Alina X"


def test_research_artifact_is_not_a_model_feature_or_forecast():
    data = load()
    assert data["model_eligible"] is False
    assert data["forecast_issued"] is False
    assert data["source_quality"]["raw_source_bytes_captured"] is False
