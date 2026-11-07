from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "data" / "xrp_intelligence" / "sources" / "kamilah_stevenson_channel.json"
IDENTITY_FOLLOWUP = ROOT / "research" / "xrp_intelligence" / "20261104T065909Z-identity-phrase-followup.json"


def test_candidate_channel_is_not_misrepresented_as_verified_identity():
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    creator = profile["creator"]
    policy = profile["attribution_policy"]
    assert creator["identity_status"] == "UNRESOLVED_NOT_EQUIVALENT"
    assert policy["status"] == "UNRESOLVED_NOT_EQUIVALENT"
    assert policy["allow_candidate_references"] is True
    assert policy["allow_verified_creator_inventory"] is False
    assert policy["allow_forecast_feature_admission"] is False
    assert profile["ingestion_policy"]["scope"] == "CANDIDATE_INDEX_ONLY_PENDING_FIRST_PARTY_IDENTITY_VERIFICATION"
    assert profile["video_inventory_status"]["identity_gate_passed"] is False
    assert profile["video_inventory_status"]["attribution_verified"] is False


def test_every_seed_video_remains_candidate_only_and_ineligible():
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    videos = profile["seed_videos"]
    assert videos
    assert all(video["attribution_status"] == "CANDIDATE_ONLY_IDENTITY_UNRESOLVED" for video in videos)
    assert all(video["eligible_for_forecast_feature"] is False for video in videos)


def test_profile_agrees_with_identity_followup_artifact():
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    followup = json.loads(IDENTITY_FOLLOWUP.read_text(encoding="utf-8"))
    identity = followup["identity_disambiguation"]
    assert identity["status"] == "UNRESOLVED_NOT_EQUIVALENT"
    assert identity["requested_identity"] == profile["attribution_policy"]["requested_identity"]
    assert identity["candidate_identity"].startswith("Kamilah Stevenson")
    assert profile["video_inventory_status"]["completeness_verified"] is False
    assert followup["identity_disambiguation"]["inventory_exhaustive"] is False
