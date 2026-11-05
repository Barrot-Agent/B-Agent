"""Regression tests for Kamilah Stevenson channel-identity quarantine."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T013000Z-kamilah-youtube-channel-identity-quarantine.json"


def test_person_identity_does_not_promote_candidate_channel_to_canonical():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["person_identity"]["status"] == "PERSON_VERIFIED_BY_FIRST_PERSON_INTERVIEW"
    assert data["candidate_channel"]["handle"] == "@drkamilahstevenson"
    assert data["candidate_channel"]["status"] == "UNVERIFIED_CANDIDATE_ONLY"
    assert data["candidate_channel"]["canonical_channel_url"] is None
    assert any("fake pages" in item.lower() for item in data["disconfirming_evidence"])


def test_no_new_video_inventory_until_authoritative_cross_link_exists():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    inventory = data["video_inventory"]
    assert inventory["status"] == "NO_NEW_VIDEOS_ADDED_PENDING_CANONICAL_CHANNEL_VERIFICATION"
    assert inventory["prior_candidates_preserved"] == 4
    assert inventory["new_candidates_added"] == 0
    assert inventory["canonical_channel_designated"] is False


def test_identity_research_remains_outside_prediction_features():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["data_quality"]["model_eligible"] is False
    assert data["predictions"]["forecast_issued"] is False
    assert data["predictions"]["directional_xrp_forecast"] is None
    assert data["data_quality"]["raw_source_sha256"] is None
