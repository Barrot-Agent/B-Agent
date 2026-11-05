import json
from pathlib import Path


ARTIFACT = Path(
    "research/xrp_intelligence/"
    "20261105T2150Z-kamilah-stevenson-public-youtube-inventory-addendum.json"
)


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


def test_video_inventory_count_is_corrected_from_one_to_three_not_thirteen():
    data = _load()
    scope = data["inventory_scope"]
    correction = scope["correction_to_prior_iheart_addendum"]
    assert correction["incorrect_prior_public_youtube_inventory_count"] == 13
    assert correction["supported_pre_addendum_inventory_count"] == 1
    assert correction["corrected_current_candidate_count"] == 3
    assert scope["total_candidate_videos"] == 3
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
