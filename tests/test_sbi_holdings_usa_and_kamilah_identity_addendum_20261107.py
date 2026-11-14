import json
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261107T091652Z-sbi-holdings-usa-and-kamilah-identity-addendum.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_sbi_holdings_usa_form3_direct_evernorth_equity_is_primary_and_scoped():
    source = load_artifact()["sources"][0]
    assert source["reporting_person"] == "SBI Holdings USA, Inc."
    assert source["relationship"].find("10% Owner") >= 0
    assert source["direct_holdings"]["class_a_shares"] == 6_529_787
    assert source["direct_holdings"]["class_c_shares"] == 1_633_180
    assert "39.9%" in source["class_c_terms"]
    assert "not a report of XRP held" in source["interpretation"]


def test_s1_defines_four_sbi_controlled_stockholders_and_separates_sbic():
    artifact = load_artifact()
    s1 = artifact["sources"][1]
    assert s1["definitions"]["SBI"] == "SBI Holdings, Inc."
    assert len(s1["definitions"]["SBI_Stockholders"]) == 4
    assert "SBI Holdings USA, Inc." in s1["definitions"]["SBI_Stockholders"]
    separation = artifact["entity_separation"]
    assert "not SBI Holdings" in separation["SBIC_East_Central_West"]


def test_alta_partners_13g_is_not_misattributed_to_sbi():
    source = load_artifact()["sources"][2]
    assert source["filer"] == "Alta Partners LLC"
    assert source["accession"] == "0001094891-26-000314"
    assert "not SBI Holdings USA" in source["interpretation"]


def test_one_official_tedx_upload_is_verified_but_personal_channel_is_not():
    inventory = load_artifact()["kamilah_stevenson_identity_and_youtube_inventory"]
    assert inventory["person_identity"] == "VERIFIED_AS_DR_KAMILAH_STEVENSON"
    assert len(inventory["verified_public_youtube_videos"]) == 1
    video = inventory["verified_public_youtube_videos"][0]
    assert video["video_id"] == "VSgeDgOCexs"
    assert video["channel"] == "TEDx Talks"
    assert video["attribution_status"] == "VERIFIED_SPEAKER_ATTRIBUTION"
    assert inventory["personal_channel_candidate"]["status"] == "UNVERIFIED_CHANNEL_OWNERSHIP"


def test_other_candidate_video_and_vimeo_item_are_not_misattributed():
    inventory = load_artifact()["kamilah_stevenson_identity_and_youtube_inventory"]
    candidates = inventory["other_video_candidates_not_attributed"]
    assert candidates[0]["video_id"] == "cxeX_eu_2H0"
    assert candidates[0]["status"] == "UNVERIFIED_CHANNEL_ATTRIBUTION"
    assert candidates[1]["platform"] == "Vimeo"
    assert candidates[1]["status"] == "NOT_A_YOUTUBE_VIDEO"


def test_identity_addendum_preserves_explicit_non_inference_rules():
    artifact = load_artifact()
    rules = artifact["do_not_infer"]
    assert any("Evernorth share ownership is not proof of XRP ownership" in rule for rule in rules)
    assert any("Alta Partners Schedule 13G is not an SBI filing" in rule for rule in rules)
    assert any("does not verify the @drkamilahstevenson personal channel" in rule for rule in rules)


def test_eloc_registration_effectiveness_is_not_confused_with_a_drawdown():
    update = load_artifact()["evernorth_eloc_effectiveness_update"]
    assert update["registration_statement_file_no"] == "333-294417"
    assert update["effect_notice"]["effective_date"] == "2026-10-30"
    assert update["interpretation"].find("not that Evernorth issued a purchase notice") >= 0
    assert update["drawdown_status"].find("No post-effectiveness drawdown") >= 0
