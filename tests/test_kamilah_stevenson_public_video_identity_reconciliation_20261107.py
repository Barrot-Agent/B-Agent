import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261107T203431Z-kamilah-stevenson-public-video-identity-reconciliation.json"


def test_kamilah_identity_is_grounded_in_first_party_organization_evidence() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    identity = data["identity_resolution"]
    assert identity["status"] == "PERSON_IDENTITY_VERIFIED"
    assert identity["primary_identity_source"]["publisher"] == "All Nations Chicago"
    assert identity["primary_identity_source"]["url"] == "https://allnationschicago.com/leadership"
    assert "does not by itself verify ownership" in identity["identity_boundary"]


def test_only_verified_tedx_video_enters_verified_inventory() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    videos = data["verified_public_video_inventory"]
    assert len(videos) == 1
    assert videos[0]["video_id"] == "VSgeDgOCexs"
    assert videos[0]["publisher"] == "TEDx Talks"
    assert videos[0]["status"] == "VERIFIED_PUBLIC_ATTRIBUTED_APPEARANCE"


def test_all_nations_chicago_video_remains_candidate_without_channel_link() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    candidates = data["candidate_video_inventory"]
    assert len(candidates) == 1
    assert candidates[0]["video_id"] == "E-jdY7gy7mQ"
    assert candidates[0]["identity_status"] == "PERSON_MATCH_PLAUSIBLE_VIDEO_ATTRIBUTION_NOT_FULLY_VERIFIED"
    assert "could not be opened" in candidates[0]["reason"]
    assert "do not count as verified video" in candidates[0]["reason"]


def test_finance_crypto_channel_is_not_attributed_to_the_verified_person() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    channels = data["channel_identity_audit"]
    assert channels["verified_personal_youtube_channels"] == 0
    finance_channel = channels["candidates"][0]
    assert finance_channel["channel"] == "Kamilah Stevenson @drkamilahstevenson"
    assert finance_channel["status"] == "UNVERIFIED_NAMESAKE_OR_IMPERSONATION_RISK"
    assert "No first-party link" in finance_channel["reason"]


def test_camilla_and_kamilah_name_variants_are_not_merged() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert "No independently verified Camilla Stevenson identity" in data["channel_identity_audit"]["camilla_name_variant"]
    assert "Do not merge Camilla and Kamilah records" in data["channel_identity_audit"]["camilla_name_variant"]


def test_exact_phrase_research_does_not_create_unsupported_relationships() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    exact = data["exact_phrase_research"]
    assert "did not establish a new XRP relationship" in exact["ask_coin"]
    assert "no capacity figure is treated as cash raised" in exact["actual_capital"]
    assert "not an OpenAI partnership" in exact["sbic_chatgpt"]
    assert data["model_admission"]["admitted"] is False
    assert data["model_admission"]["forecast_status"] == "NOT_ISSUED"
    assert data["privacy_and_safety"]["private_or_restricted_sources_used"] is False


def test_kamilah_video_artifact_capture_time_correction_is_append_only() -> None:
    correction_path = (
        ROOT
        / "research"
        / "xrp_intelligence"
        / "20261107T204153Z-kamilah-stevenson-video-capture-window-correction.json"
    )
    correction = json.loads(correction_path.read_text(encoding="utf-8"))
    assert correction["supersedes_artifact"] == (
        "research/xrp_intelligence/20261107T203431Z-kamilah-stevenson-public-video-identity-reconciliation.json"
    )
    assert correction["superseded_artifact_git_blob_sha"] == "24bff929a7ce94c28351d9d7f3e1b695e18f2f1f"
    assert correction["supersession_scope"] == "TIMESTAMP_ONLY"
    assert correction["correction"]["previous_field_status"] == "INCORRECT_AS_EXACT_CAPTURE_TIME"
    assert correction["correction"]["corrected_exact_capture_at_utc"] is None
    assert correction["correction"]["exact_fetch_arrival_timestamp_exposed"] is False
    assert correction["evidence_content_changed"] is False
    assert correction["identity_and_video_decisions_unchanged"] is True
