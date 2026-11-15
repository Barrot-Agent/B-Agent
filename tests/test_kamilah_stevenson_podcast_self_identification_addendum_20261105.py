import json
from pathlib import Path


ARTIFACT = Path(
    "research/xrp_intelligence/"
    "20261105T2145Z-kamilah-stevenson-podcast-self-identification-addendum.json"
)


def _load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_iheart_episode_supports_name_variant_reconciliation_without_legal_identity_claim():
    data = _load()
    assert data["episode"]["title"] == "Crypto Panics! with Dr. Kamilah Stevenson"
    assert data["episode"]["publication_date"] == "2026-06-11"
    assert data["episode"]["duration_minutes"] == 42
    assert data["episode"]["transcript_status"].startswith("auto-generated")
    assert data["transcript_observations"][-2]["time"] == "40:07-40:26"
    identity = data["identity_reconciliation"]
    assert identity["spoken_name_variants"] == ["Camila", "Camilla"]
    assert identity["self_reported_platform_display_names"]["instagram"].startswith("Kamilla")
    assert identity["self_reported_platform_display_names"]["youtube"].startswith("doctor Camilla")
    assert identity["legal_identity_verified"] is False
    assert identity["exact_social_handles_verified"] is False
    assert identity["canonical_youtube_channel_verified"] is False


def test_iheart_episode_is_not_added_to_youtube_video_inventory_without_a_youtube_url():
    data = _load()
    inventory = data["video_inventory_treatment"]
    assert inventory["classify_this_iheart_episode_as_youtube_video"] is False
    assert inventory["prior_public_youtube_inventory_count"] == 13
    assert inventory["new_youtube_video_added"] == 0
    assert inventory["prior_inventory_exhaustive"] is False


def test_interview_claims_are_not_promoted_to_xrp_market_features():
    data = _load()
    assert data["xrp_claim_handling"]["episode_topic_includes_xrp"] is True
    assert data["xrp_claim_handling"]["guest_market_or_adoption_statements_are_primary_market_data"] is False
    assert data["xrp_claim_handling"]["claims_eligible_as_event_features"] is False
    assert data["model_admission"]["eligible"] is False
    assert data["model_admission"]["directional_forecast_issued"] is False
    assert data["sources"][0]["raw_bytes_captured"] is False
