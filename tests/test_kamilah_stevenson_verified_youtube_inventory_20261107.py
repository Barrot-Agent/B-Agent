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


def test_kamilah_identity_bridge_uses_first_party_and_interview_cross_links():
    record = _record()
    identity = record["identity"]
    assert identity["canonical_name"] == "Dr. Kamilah Stevenson"
    assert identity["identity_status"] == "HIGH_CONFIDENCE_CROSS_SOURCE_LINKAGE"
    assert identity["official_youtube_channel_handle"] == "@drkamilahstevenson"
    assert identity["platform_verified_badge"] == "NOT_ESTABLISHED"
    ids = {source["source_id"] for source in record["sources"]}
    assert "ALL_NATIONS_CHICAGO_FIRST_PARTY_LEADERSHIP" in ids
    assert "KAMILAH_STEVENSON_FIRST_PARTY_WEBSITE" in ids
    assert "IHEART_CRYPTO_PANICS_INTERVIEW_TRANSCRIPT" in ids
    assert "PAUL_BARRON_PODCAST_CRYPTO_PANICS" in ids


def test_short_source_receipts_recompute_and_respect_quotation_limit():
    record = _record()
    assert record["source_capture_contract"]["maximum_direct_quote_words_per_source"] == 25
    for source in record["sources"]:
        excerpt = source.get("excerpt")
        digest = source.get("excerpt_sha256")
        if excerpt is None:
            assert digest is None
            continue
        assert len(excerpt.split()) <= 25
        assert hashlib.sha256(excerpt.encode("utf-8")).hexdigest() == digest


def test_video_inventory_has_six_unique_verified_attributions():
    record = _record()
    videos = record["videos"]
    assert len(videos) == 6
    assert len({video["video_id"] for video in videos}) == 6
    assert record["inventory_summary"]["verified_video_attributions"] == 6
    assert record["inventory_summary"]["verified_personal_channel_uploads"] == 3
    assert record["inventory_summary"]["verified_guest_appearances"] == 1
    assert record["inventory_summary"]["verified_organization_channel_attributions"] == 1
    assert record["inventory_summary"]["verified_tedx_speaker_attributions"] == 1


def test_personal_channel_uploads_use_the_cross_linked_handle():
    record = _record()
    personal = [v for v in record["videos"] if v["attribution_type"] == "PERSONAL_CHANNEL_UPLOAD"]
    assert {v["video_id"] for v in personal} == {"iwhpNT73zpk", "po4bv7889ao", "12HiznN3iLQ"}
    assert all(v["channel_handle"] == "@drkamilahstevenson" for v in personal)
    assert all(v["attribution_status"].startswith("VERIFIED") for v in personal)


def test_unavailable_descriptions_are_not_inferred():
    record = _record()
    by_id = {v["video_id"]: v for v in record["videos"]}
    assert by_id["po4bv7889ao"]["content_verified"] is False
    assert by_id["12HiznN3iLQ"]["content_verified"] is False
    assert "description unavailable" in by_id["po4bv7889ao"]["summary"].lower()
    assert "description unavailable" in by_id["12HiznN3iLQ"]["summary"].lower()


def test_guest_and_organization_videos_are_not_mislabeled_as_personal_uploads():
    record = _record()
    by_id = {v["video_id"]: v for v in record["videos"]}
    assert by_id["Sulo54IlQ60"]["attribution_type"] == "GUEST_APPEARANCE"
    assert by_id["E-jdY7gy7mQ"]["attribution_type"] == "ORGANIZATION_CHANNEL_ATTRIBUTION"
    assert by_id["VSgeDgOCexs"]["attribution_type"] == "TEDX_SPEAKER_ATTRIBUTION"


def test_fake_page_warning_and_false_positive_channels_remain_quarantined():
    record = _record()
    assert any("fake pages" in source.get("excerpt", "").lower() for source in record["sources"])
    handles = {x["channel_handle"] for x in record["false_positive_or_non_attributed"] if "channel_handle" in x}
    assert handles == {"@CoachKamilahStevensonxrp", "@KamilahStevensonDigitalNetwork"}
    assert record["inventory_summary"]["unverified_similar_name_handles_not_counted"] == 2


def test_third_party_repost_is_not_counted_as_kamilah_authored_content():
    record = _record()
    assert record["inventory_summary"]["third_party_commentary_not_counted"] == 1
    repost = record["false_positive_or_non_attributed"][0]
    assert repost["video_id"] == "5DzBk8DfoLs"
    assert repost["classification"] == "THIRD_PARTY_COMMENTARY_NOT_KAMILAH_UPLOAD"


def test_kamilah_video_inventory_is_not_admitted_as_a_market_feature():
    record = _record()
    assert record["content_quality_and_market_use"]["model_eligible"] is False
    assert record["content_quality_and_market_use"]["forecast_status"] == "NOT_ISSUED"
    assert record["content_quality_and_market_use"]["trade_status"] == "NO_TRADE"
