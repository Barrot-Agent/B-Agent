import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T181200Z-kamilah-stevenson-youtube-identity-and-xrp-video-inventory.json"


def _load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_channel_identity_is_triangulated_but_not_overstated_as_legal_identity():
    data = _load()
    identity = data["identity"]
    assert identity["youtube_handle"] == "@drkamilahstevenson"
    assert identity["youtube_channel_id"] == "UCqUPJMQdkCN6lsLVDnichPA"
    assert identity["identity_confidence"] == "HIGH_CONFIDENCE_PUBLIC_CHANNEL_MATCH"
    assert identity["legal_identity_verified"] is False
    assert identity["self_reported_social_names"]["handles_not_independently_verified"] is True
    assert any("fake pages exist" in item for item in identity["limitations"])
    assert any("auto-generated" in item for item in identity["limitations"])


def test_video_inventory_has_unique_ids_and_matches_one_channel_attribution():
    data = _load()
    videos = data["video_inventory_scope"]["videos"]
    ids = [item["video_id"] for item in videos]
    assert len(videos) == 13
    assert len(ids) == len(set(ids))
    for item in videos:
        assert item["creator_attribution"] == "Kamilah Stevenson"
        assert item["url"] == f"https://www.youtube.com/watch?v={item['video_id']}"
        assert item["model_eligible"] is False
        assert item["raw_video_bytes_preserved"] is False
        assert item["independent_timestamp_anchor"] is False
        assert item["claim_status"]
    assert next(v for v in videos if v["video_id"] == "YJdK1LvmJSo")["title"] is None


def test_guest_appearance_is_separate_from_own_channel_uploads():
    data = _load()
    guest = data["guest_appearances_not_counted_as_own_channel_uploads"]
    assert len(guest) == 1
    assert guest[0]["publisher"] == "The XRP Podcast with Paul Barron / iHeart"
    assert "no exact YouTube watch URL" in guest[0]["reason"]
    ai = guest[0]["ai_methodology_statement"]
    assert ai["provider_names_disclosed"] == []
    assert ai["authentication_or_data_flow_evidence"] is False
    assert ai["persistent_platform_coordination_verified"] is False
    assert all(v["video_id"] != "5DzBk8DfoLs" for v in data["video_inventory_scope"]["videos"])


def test_inventory_is_partial_and_creator_commentary_is_not_market_truth():
    data = _load()
    scope = data["video_inventory_scope"]
    assert scope["exhaustive"] is False
    assert scope["count"] == len(scope["videos"])
    assert data["content_use_policy"]["all_video_content_model_eligible"] is False
    assert "4.09B XRP whale accumulation and 7.03B XRP exchange outflows in the April 19 video description are unverified here." in data["content_use_policy"]["claims_requiring_special_caution"]
    assert data["model_eligible"] is False
    assert data["forecast_issued"] is False
    assert data["recorded_at_utc"] is None
    assert "approximate research-run marker" in data["file_timestamp_semantics"]
    assert all(v["metrics_snapshot_date"] is None for v in scope["videos"])
