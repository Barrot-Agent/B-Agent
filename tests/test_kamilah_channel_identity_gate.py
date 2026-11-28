from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "data" / "xrp_intelligence" / "sources" / "kamilah_stevenson_channel.json"
EARLIER_IDENTITY = ROOT / "research" / "xrp_intelligence" / "20261104T065909Z-identity-phrase-followup.json"
PODCAST = ROOT / "research" / "xrp_intelligence" / "20261105T2145Z-kamilah-stevenson-podcast-self-identification-addendum.json"
VIDEO_ADDENDUM = ROOT / "research" / "xrp_intelligence" / "20261105T2150Z-kamilah-stevenson-public-youtube-inventory-addendum.json"
NEW_INVENTORY = ROOT / "research" / "xrp_intelligence" / "20261127T120000Z-kamilah-youtube-channel-metadata-and-video-inventory.json"
RESEARCH_NOTE = ROOT / "research" / "xrp_intelligence" / "20261126_evernorth_actual_capital_and_sbic_identity.md"


def test_youtube_channel_page_verifies_channel_metadata_not_legal_identity():
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    artifact = json.loads(NEW_INVENTORY.read_text(encoding="utf-8"))
    creator = profile["creator"]
    status = profile["video_inventory_status"]
    assert creator["person_identity_status"] == "CONFIRMED"
    mission = profile["mission"]
    assert "first-party YouTube channel-page metadata verifies" in mission.lower()
    assert "strong but not legal-identity verified" in mission.lower()
    assert "21 earlier seed references remain candidate-only" in mission.lower()
    assert "remains probable rather than platform-verified" not in mission.lower()
    assert "not treat the inventory as complete" in mission
    assert creator["channel_identity_status"] == "PLATFORM_METADATA_VERIFIED_SELF_IDENTIFIED_CHANNEL"
    assert creator["youtube_channel_id"] == "UCqUPJMQdkCN6lsLVDnichPA"
    assert creator["youtube_handle"] == "@drkamilahstevenson"
    assert creator["handle_channel_id_relation"] == "VERIFIED_BY_YOUTUBE_CHANNEL_PAGE"
    assert creator["person_channel_association_status"] == "STRONG_NOT_LEGAL_IDENTITY_VERIFIED"
    assert creator["legal_identity_verified"] is False
    assert status["canonical_channel_verified"] is True
    assert status["identity_gate_passed"] is True
    assert status["completeness_verified"] is False
    assert status["legal_identity_verified"] is False
    assert artifact["identity_resolution"]["channel_id"] == creator["youtube_channel_id"]
    assert artifact["identity_resolution"]["channel_handle"] == creator["youtube_handle"]
    assert artifact["identity_resolution"]["legal_identity_verified"] is False
    # Earlier interview and search artifacts remain historical evidence, not rewritten.
    podcast = json.loads(PODCAST.read_text(encoding="utf-8"))
    videos = json.loads(VIDEO_ADDENDUM.read_text(encoding="utf-8"))
    assert podcast["identity_reconciliation"]["canonical_youtube_channel_verified"] is False
    assert videos["identity"]["platform_account_ownership_verified"] is False
    assert videos["identity"]["legal_identity_verified"] is False


def test_only_two_first_party_author_byline_records_enter_partial_inventory():
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    artifact = json.loads(NEW_INVENTORY.read_text(encoding="utf-8"))
    verified = profile["verified_channel_videos"]
    assert len(verified) == 2
    assert profile["video_inventory_status"]["verified_inventory_count"] == 2
    assert {item["video_id"] for item in verified} == {"vRlw4BV-cGE", "dAKrq3c9hts"}
    assert all(item["author_as_displayed"] == "Kamilah Stevenson" for item in verified)
    assert all(item["channel_id"] is None for item in verified)
    assert all(item["channel_id_exposed_on_video_result"] is False for item in verified)
    assert all(item["eligible_for_forecast_feature"] is False for item in verified)
    assert artifact["prediction_and_market_use"]["market_feature_admission"] is False
    assert artifact["channel_page_listing_snapshot"]["visible_listing_slots"] == 56
    assert artifact["channel_page_listing_snapshot"]["unique_video_count"] is None
    assert artifact["channel_page_listing_snapshot"]["members_only_included"] is False


def test_prior_seed_video_references_remain_candidate_only():
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    seeds = profile["seed_videos"]
    assert len(seeds) == 21
    assert profile["video_inventory_status"]["candidate_reference_count"] == 21
    assert all(item["attribution_status"] == "CANDIDATE_ONLY_CANONICAL_CHANNEL_UNVERIFIED" for item in seeds)
    assert all(item["eligible_for_forecast_feature"] is False for item in seeds)
    assert profile["attribution_policy"]["allow_candidate_references"] is True
    assert profile["attribution_policy"]["allow_verified_creator_inventory"] is True
    assert profile["attribution_policy"]["allow_forecast_feature_admission"] is False


def test_historical_identity_states_are_preserved_and_current_state_is_append_only():
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    earlier = json.loads(EARLIER_IDENTITY.read_text(encoding="utf-8"))
    history = profile["identity_status_history"]
    assert earlier["identity_disambiguation"]["status"] == "UNRESOLVED_NOT_EQUIVALENT"
    assert history[0]["status"] == "UNRESOLVED_NOT_EQUIVALENT"
    assert history[1]["status"] == "PERSON_CONFIRMED_CHANNEL_PROBABLE_MATCH"
    assert history[2]["status"] == "YOUTUBE_CHANNEL_METADATA_AND_TWO_AUTHOR_BYLINES_VERIFIED_PERSON_ASSOCIATION_NOT_LEGAL_IDENTITY"


def test_cached_36_title_sample_is_not_mislabeled_as_verified_video_inventory():
    note = RESEARCH_NOTE.read_text(encoding="utf-8")
    assert "36 cached titles as a verified creator-video inventory" in note
    assert "two-record partial byline-match inventory" in note
    assert "The 21 earlier seed references remain candidate-only" in note
    assert "Inventory completeness is false" in note
