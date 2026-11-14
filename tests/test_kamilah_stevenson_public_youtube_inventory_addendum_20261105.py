import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T2150Z-kamilah-stevenson-public-youtube-inventory-addendum.json"


def _load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_public_youtube_results_match_the_corroborated_channel_display_name():
    data = _load()
    assert data["identity"]["channel_handle"] == "@drkamilahstevenson"
    assert data["identity"]["channel_page_title"] == "Kamilah Stevenson"
    videos = {item["video_id"]: item for item in data["video_inventory"]}
    assert videos["iwhpNT73zpk"]["author_as_displayed"] == "Kamilah Stevenson"
    assert videos["pmJTrXJQ8Vw"]["author_as_displayed"] == "Kamilah Stevenson"
    assert videos["iwhpNT73zpk"]["published_at"] == "2026-03-06"
    assert videos["pmJTrXJQ8Vw"]["published_at"] == "2025-12-24"
    assert videos["iwhpNT73zpk"]["content_reviewed"] is False
    assert videos["pmJTrXJQ8Vw"]["content_reviewed"] is False


def test_video_inventory_counts_remain_scoped_to_their_source_artifacts():
    data = _load()
    scope = data["inventory_scope"]
    reconciliation = scope["correction_to_prior_iheart_addendum"]
    assert reconciliation["prior_inventory_counts_by_artifact"]["20261105T150100Z-kamilah-stevenson-youtube-identity-and-video-inventory.json"] == 1
    assert reconciliation["prior_inventory_counts_by_artifact"]["20261105T181200Z-kamilah-stevenson-youtube-identity-and-xrp-video-inventory.json"] == 13
    assert reconciliation["current_addendum_record_count"] == 3
    assert reconciliation["existing_in_prior_13_video_ids"] == ["iwhpNT73zpk", "pmJTrXJQ8Vw"]
    assert reconciliation["new_unique_video_ids"] == ["OvODErBT9Ug"]
    assert scope["total_candidate_videos"] == 14
    assert scope["new_unique_video_candidates"] == 1
    assert scope["exhaustive"] is False


def test_iheart_podcast_is_not_counted_as_a_youtube_video():
    data = _load()
    assert data["inventory_scope"]["direct_link_hub_video_links"] == 1
    assert all(item["publisher"] == "YouTube" for item in data["video_inventory"])
    assert data["sources"] if "sources" in data else data["source_registry"]


def test_channel_attribution_does_not_claim_legal_identity_or_exact_social_handles():
    data = _load()
    identity = data["identity"]
    assert identity["attribution_assessment"].startswith("Strongly corroborated public-channel attribution")
    assert identity["legal_identity_verified"] is False
    assert identity["platform_account_ownership_verified"] is False
    assert identity["exact_x_handle"] is None
    assert identity["exact_instagram_handle"] is None


def test_creator_opinions_and_search_metadata_are_not_market_features():
    data = _load()
    assert data["admission"]["model_eligible"] is False
    assert data["admission"]["directional_forecast_issued"] is False
    assert all(item["market_claims_admissible_as_facts"] is False for item in data["video_inventory"] if "market_claims_admissible_as_facts" in item)
    assert all(source["raw_bytes_captured"] is False for source in data["source_registry"])


def test_video_without_a_retrieved_publication_date_is_not_marked_source_reported():
    channel_path = ROOT / "data" / "xrp_intelligence" / "sources" / "kamilah_stevenson_channel.json"
    channel = json.loads(channel_path.read_text(encoding="utf-8"))
    video = next(x for x in channel["seed_videos"] if x["video_id"] == "OvODErBT9Ug")
    assert video["published_date_reported"] is None
    assert video["published_date_status"] == "NOT_REPORTED"
