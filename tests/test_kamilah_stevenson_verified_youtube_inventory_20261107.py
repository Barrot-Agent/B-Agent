import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261107T211712Z-kamilah-stevenson-verified-youtube-inventory.json"
)


def _record():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_person_identity_is_confirmed_but_personal_channel_remains_probable():
    record = _record()
    identity = record["identity"]
    assert identity["canonical_name"] == "Dr. Kamilah Stevenson"
    assert identity["person_identity_status"] == "CONFIRMED"
    assert identity["channel_identity_status"] == "PROBABLE_MATCH_NOT_FIRST_PARTY_VERIFIED"
    assert identity["official_youtube_channel_handle"] is None
    assert identity["candidate_youtube_channel_handle"] == "@drkamilahstevenson"
    assert identity["platform_verified_badge"] == "NOT_ESTABLISHED"
    assert "remains probable" in identity["channel_ownership_caveat"]


def test_short_source_receipts_recompute_and_respect_quotation_limit():
    record = _record()
    contract = record["source_capture_contract"]
    assert contract["maximum_direct_quote_words_per_source"] == 25
    assert "bidi formatting marks" in contract["normalization_policy"]
    for source in record["sources"]:
        excerpt = source.get("excerpt")
        digest = source.get("excerpt_sha256")
        if excerpt is None:
            assert digest is None
            continue
        assert len(excerpt.split()) <= 25
        assert hashlib.sha256(excerpt.encode("utf-8")).hexdigest() == digest


def test_three_verified_public_attributions_are_separated_from_personal_channel_candidates():
    record = _record()
    verified = record["verified_videos"]
    candidates = record["candidate_videos"]
    assert len(verified) == 3
    assert {v["video_id"] for v in verified} == {"Sulo54IlQ60", "E-jdY7gy7mQ", "VSgeDgOCexs"}
    assert len(candidates) == 3
    assert {v["video_id"] for v in candidates} == {"iwhpNT73zpk", "po4bv7889ao", "12HiznN3iLQ"}
    assert record["inventory_summary"]["verified_video_attributions"] == 3
    assert record["inventory_summary"]["verified_personal_channel_uploads"] == 0
    assert record["inventory_summary"]["candidate_personal_channel_uploads"] == 3


def test_candidate_personal_uploads_are_not_attributed_to_the_confirmed_person():
    record = _record()
    for video in record["candidate_videos"]:
        assert video["attribution_status"] == "CANDIDATE_ONLY_CANONICAL_CHANNEL_UNVERIFIED"
        assert video["candidate_channel_handle"] == "@drkamilahstevenson"
        assert video["content_verified"] is False
        assert video["full_content_reviewed"] is False


def test_verified_guest_and_organization_videos_are_classified_correctly():
    record = _record()
    by_id = {v["video_id"]: v for v in record["verified_videos"]}
    assert by_id["Sulo54IlQ60"]["attribution_type"] == "GUEST_APPEARANCE"
    assert by_id["E-jdY7gy7mQ"]["attribution_type"] == "ORGANIZATION_CHANNEL_ATTRIBUTION"
    assert by_id["VSgeDgOCexs"]["attribution_type"] == "TEDX_SPEAKER_ATTRIBUTION"
    assert all(v["full_content_reviewed"] is False for v in by_id.values())


def test_interview_and_iheart_transcript_are_one_underlying_source_episode():
    record = _record()
    sources = {s["source_id"]: s for s in record["sources"]}
    assert sources["PAUL_BARRON_PODCAST_CRYPTO_PANICS"]["source_independence_group"] == "same_paul_barron_interview_episode"
    assert sources["IHEART_CRYPTO_PANICS_INTERVIEW_TRANSCRIPT"]["source_independence_group"] == "same_paul_barron_interview_episode"


def test_fake_page_warning_and_third_party_repost_remain_quarantined():
    record = _record()
    assert any("fake pages" in source.get("excerpt", "").lower() for source in record["sources"])
    assert len(record["false_positive_or_non_attributed"]) == 1
    repost = record["false_positive_or_non_attributed"][0]
    assert repost["video_id"] == "5DzBk8DfoLs"
    assert repost["classification"] == "THIRD_PARTY_COMMENTARY_NOT_KAMILAH_UPLOAD"


def test_kamilah_video_inventory_is_not_admitted_as_a_market_feature():
    record = _record()
    assert record["content_quality_and_market_use"]["model_eligible"] is False
    assert record["content_quality_and_market_use"]["forecast_status"] == "NOT_ISSUED"
    assert record["content_quality_and_market_use"]["trade_status"] == "NO_TRADE"
