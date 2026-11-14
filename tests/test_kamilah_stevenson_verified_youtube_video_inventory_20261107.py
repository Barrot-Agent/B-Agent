import json
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261107T081221Z-kamilah-stevenson-verified-youtube-video-inventory.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_exactly_one_public_video_is_verified():
    artifact = load_artifact()
    assert artifact["inventory_totals"]["verified_public_videos"] == 1
    assert len(artifact["verified_youtube_videos"]) == 1


def test_verified_video_is_published_by_verified_tedx_channel():
    video = load_artifact()["verified_youtube_videos"][0]
    assert video["video_id"] == "VSgeDgOCexs"
    assert video["publisher_channel"] == "TEDx Talks"
    assert video["publisher_channel_verified"] is True
    assert video["channel_is_personal_channel"] is False
    assert video["attribution_evidence"]["youtube_description_names_dr_kamilah_stevenson"] is True
    assert video["attribution_evidence"]["youtube_description_links_first_party_domain"] is True


def test_personal_channel_ownership_is_not_inferred():
    artifact = load_artifact()
    assert artifact["inventory_totals"]["verified_personal_youtube_channels"] == 0
    assert artifact["candidate_handling"]["candidate_channels_attributed_to_person"] is False


def test_all_existing_candidate_references_remain_unverified_and_preserved():
    artifact = load_artifact()
    assert artifact["inventory_totals"]["unverified_seed_video_references_preserved"] == 18
    assert artifact["inventory_totals"]["related_public_video_references_preserved"] == 2
    assert artifact["candidate_handling"]["seed_video_references_preserved"] == 18
    assert artifact["candidate_handling"]["related_public_video_references_preserved"] == 2
    assert artifact["candidate_handling"]["candidate_channel_status"] == "PROBABLE_MATCH_NOT_FIRST_PARTY_VERIFIED"
    assert artifact["candidate_handling"]["existing_candidate_registry"] == (
        "data/xrp_intelligence/sources/kamilah_stevenson_channel.json"
    )


def test_spelling_variant_does_not_create_a_second_person():
    spelling = load_artifact()["identity_resolution"]["spelling_policy"]
    assert spelling["canonical"] == "Kamilah"
    assert "not treated as proof of a separate person" in spelling["treatment"]


def test_identity_research_is_excluded_from_xrp_market_features():
    usage = load_artifact()["forecast_or_market_use"]
    assert usage["model_feature"] is False
    assert usage["xrp_market_signal"] is False
