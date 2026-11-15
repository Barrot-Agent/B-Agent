from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "data" / "xrp_intelligence" / "sources" / "kamilah_stevenson_channel.json"
EARLIER_IDENTITY = ROOT / "research" / "xrp_intelligence" / "20261104T065909Z-identity-phrase-followup.json"
PODCAST = ROOT / "research" / "xrp_intelligence" / "20261105T2145Z-kamilah-stevenson-podcast-self-identification-addendum.json"
VIDEO_ADDENDUM = ROOT / "research" / "xrp_intelligence" / "20261105T2150Z-kamilah-stevenson-public-youtube-inventory-addendum.json"


def test_person_identity_evidence_does_not_overstate_channel_ownership():
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    podcast = json.loads(PODCAST.read_text(encoding="utf-8"))
    videos = json.loads(VIDEO_ADDENDUM.read_text(encoding="utf-8"))
    assert profile["creator"]["person_identity_status"] == "CONFIRMED"
    assert profile["creator"]["channel_identity_status"] == "PROBABLE_MATCH_NOT_FIRST_PARTY_VERIFIED"
    assert profile["video_inventory_status"]["canonical_channel_verified"] is False
    assert podcast["identity_reconciliation"]["canonical_youtube_channel_verified"] is False
    assert podcast["identity_reconciliation"]["exact_social_handles_verified"] is False
    assert videos["identity"]["platform_account_ownership_verified"] is False
    assert videos["identity"]["legal_identity_verified"] is False
    assert videos["inventory_scope"]["exhaustive"] is False


def test_all_profile_video_references_remain_candidate_only():
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    videos = profile["seed_videos"]
    assert videos
    assert len(videos) == profile["video_inventory_status"]["candidate_reference_count"]
    assert profile["video_inventory_status"]["verified_inventory_count"] == 0
    assert all(v["attribution_status"] == "CANDIDATE_ONLY_CANONICAL_CHANNEL_UNVERIFIED" for v in videos)
    assert all(v["eligible_for_forecast_feature"] is False for v in videos)
    assert {"iwhpNT73zpk", "po4bv7889ao", "12HiznN3iLQ"} <= {v["video_id"] for v in videos}
    assert profile["video_inventory_status"]["candidate_reference_count"] == 21
    assert profile["attribution_policy"]["allow_verified_creator_inventory"] is False
    assert profile["ingestion_policy"]["scope"] == "CANDIDATE_REFERENCES_ONLY_PENDING_CANONICAL_CHANNEL_VERIFICATION"
    assert profile["identity_status_history"][0]["status"] == "UNRESOLVED_NOT_EQUIVALENT"
    assert profile["identity_status_history"][1]["status"] == "PERSON_CONFIRMED_CHANNEL_PROBABLE_MATCH"


def test_first_party_link_hub_and_interview_are_not_platform_account_authentication():
    podcast = json.loads(PODCAST.read_text(encoding="utf-8"))
    videos = json.loads(VIDEO_ADDENDUM.read_text(encoding="utf-8"))
    assert podcast["identity_reconciliation"]["self_reported_platform_display_names"]["youtube"] == "doctor Camilla Stevenson (display name; exact channel URL not supplied in the transcript)"
    assert videos["identity"]["attribution_assessment"].startswith("Strongly corroborated public-channel attribution")
    assert videos["identity"]["platform_account_ownership_verified"] is False
    assert videos["identity"]["exact_x_handle"] is None
    assert videos["identity"]["exact_instagram_handle"] is None

def test_person_identity_is_confirmed_but_canonical_channel_remains_unverified():
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    creator = profile["creator"]
    assert creator["identity_status"] == "PERSON_CONFIRMED_CHANNEL_PROBABLE_MATCH"
    assert creator["person_identity_status"] == "CONFIRMED"
    assert creator["channel_identity_status"] == "PROBABLE_MATCH_NOT_FIRST_PARTY_VERIFIED"
    assert creator["youtube_channel_id_status"] == "THIRD_PARTY_CANDIDATE"
    assert creator["handle_channel_id_relation"] == "UNRESOLVED_POSSIBLY_SAME_CHANNEL"
    assert profile["video_inventory_status"]["canonical_channel_verified"] is False
    assert profile["video_inventory_status"]["attribution_verified"] is False
    assert profile["video_inventory_status"]["identity_gate_passed"] is False
    assert profile["video_inventory_status"]["verified_inventory_count"] == 0

def test_all_video_references_remain_candidate_only_and_model_ineligible():
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    videos = profile["seed_videos"]
    assert len(videos) == profile["video_inventory_status"]["candidate_reference_count"]
    assert videos
    assert all(video["attribution_status"] == "CANDIDATE_ONLY_CANONICAL_CHANNEL_UNVERIFIED" for video in videos)
    assert all(video["eligible_for_forecast_feature"] is False for video in videos)
    policy = profile["attribution_policy"]
    assert policy["allow_candidate_references"] is True
    assert policy["allow_verified_creator_inventory"] is False
    assert policy["allow_forecast_feature_admission"] is False

def test_identity_status_progression_preserves_earlier_unresolved_record():
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    earlier = json.loads(EARLIER_IDENTITY.read_text(encoding="utf-8"))
    assert earlier["identity_disambiguation"]["status"] == "UNRESOLVED_NOT_EQUIVALENT"
    history = profile["identity_status_history"]
    assert history[0]["status"] == "UNRESOLVED_NOT_EQUIVALENT"
    assert history[1]["status"] == "PERSON_CONFIRMED_CHANNEL_PROBABLE_MATCH"
    assert history[1]["scope"].endswith("not platform-verified.")
