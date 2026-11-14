import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research/xrp_intelligence/20261108T021024Z-exact-phrase-askcoin-sbic-kamilah-video-reconciliation.json"
)


def test_sbic_chatgpt_phrase_is_training_evidence_not_partnership():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    finding = data["exact_phrase_findings"]["sbic_chatgpt"]
    assert finding["exact_phrase_entity_found"] is False
    assert "ChatGPT" in finding["primary_source"]["evidence"]
    assert "does not establish an OpenAI partnership" in finding["primary_source"]["interpretation"]
    assert "SBI Holdings" in finding["entity_separation"]


def test_ask_coin_exchange_bot_and_permission_ask_are_disambiguated():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    finding = data["exact_phrase_findings"]["ask_coin"]
    assert finding["ask_coin_exchange"]["listing_status"] == "inactive"
    assert finding["ask_coin_exchange"]["volume_status"] == "untracked"
    assert finding["ask_coin_exchange"]["reserve_data"] == "unavailable"
    assert finding["ask_coin_telegram_bot"]["relationship_to_exchange"] == "not_established"
    assert finding["permission_coin_ask_token"]["name"] == "Permission Coin"
    assert finding["permission_coin_ask_token"]["relationship_to_xrp"] == "not_established"
    assert finding["result_status"] == "DISAMBIGUATED_NO_VERIFIED_XRP_LINK"


def test_actual_capital_phrase_is_not_treated_as_a_standardized_metric():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    finding = data["exact_phrase_findings"]["actual_capital"]
    assert finding["exact_phrase_use"]["source_class"] == "secondary_commentary"
    assert finding["exact_phrase_use"]["issuer_defined_metric"] is False
    assert "cash received" in finding["accounting_rule"]
    assert "XRP acquired" in finding["accounting_rule"]


def test_kamilah_person_and_video_attribution_are_scoped_without_claiming_channel_ownership():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    identity = data["kamilah_stevenson_identity"]
    assert identity["person_identity_status"] == "STRONGLY_CORROBORATED"
    assert identity["youtube_attribution_evidence"]["channel_ownership_status"] == "NOT_INDEPENDENTLY_VERIFIED_BY_FIRST_PARTY_CHANNEL_LINK"
    videos = identity["public_xrp_related_videos"]
    assert len(videos) == 7
    assert len({video["video_id"] for video in videos}) == 7
    assert any(video["publisher_byline"] == "Paul Barron Podcast" for video in videos)
    assert identity["unverified_or_unlocated"]["japan_remittance_pilot_video"].startswith("Secondary coverage")
    assert data["forecast_status"] == "NOT_ISSUED"
    assert data["model_feature_admission"] is False
