import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T150100Z-kamilah-stevenson-youtube-identity-and-video-inventory.json"


def test_kamilah_identity_uses_first_person_and_matching_linktree_evidence():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    identity = data["identity"]
    assert identity["canonical_display_name"] == "Dr. Kamilah Stevenson"
    assert identity["identity_status"] == "strongly_corroborated_but_canonical_youtube_channel_not_independently_verified"
    assert "not established" in identity["spelling_variant_camilla"]
    assert any("first-person official website" in item for item in identity["evidence"])
    assert any("Linktree" in item and "YouTube" in item for item in identity["evidence"])


def test_only_directly_linked_video_is_listed_and_inventory_is_not_exhaustive():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    videos = data["video_inventory"]
    assert len(videos) == 1
    assert videos[0]["video_id"] == "OvODErBT9Ug"
    assert videos[0]["title"] == "My Top 10 Digital Assets — What They Do & Why I Hold Them"
    assert videos[0]["content_reviewed"] is False
    assert data["inventory_scope"]["exhaustive"] is False
    assert data["inventory_scope"]["confirmed_linked_videos"] == 1


def test_unverified_channel_ownership_is_not_promoted_to_model_evidence():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["source_capture_policy"]["model_eligible"] is False
    assert data["admission"]["model_eligible"] is False
    assert data["admission"]["forecast_status"] == "NOT_ISSUED"
    assert data["identity"]["limitations"]
