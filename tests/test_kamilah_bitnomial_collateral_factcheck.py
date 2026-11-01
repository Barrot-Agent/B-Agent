import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def test_user_confirmed_kamilah_profile_includes_collateral_video():
    profile = load_json("data/xrp_intelligence/sources/kamilah_stevenson_channel.json")
    assert profile["creator"]["display_name"] == "Kamilah Stevenson"
    assert "USER_CONFIRMED_CREATOR_NAME" in profile["creator"]["identity_status"]
    assert any(video["video_id"] == "M8TmDXO7B-0" for video in profile["seed_videos"])
    assert profile["video_inventory_status"]["completeness_verified"] is False


def test_bitnomial_xrp_collateral_is_venue_specific_and_haircut():
    snapshot = load_json(
        "data/xrp_intelligence/snapshots/20261101T194000Z-xrp-collateral-cftc-bitnomial-payward-kamilah-video.json"
    )
    collateral = snapshot["collateral"]
    xrp = next(asset for asset in collateral["accepted_assets"] if asset["asset"] == "XRP")
    assert xrp["haircut_pct"] == 40
    assert xrp["notional_limit_usd"] == 15_000_000
    assert collateral["rlUSD_current_schedule_status"] == "NOT_LISTED; CURRENT_ACCEPTANCE_UNCONFIRMED"
    assert snapshot["video"]["claim_verdict"] == "LIMITED_VENUE_TRUE; UNIVERSAL_CFTC_APPROVAL_AND_EQUAL_RISK_CLASS_NOT_ESTABLISHED"


def test_cftc_letter_is_conditional_and_coinbase_originated():
    snapshot = load_json(
        "data/xrp_intelligence/snapshots/20261101T194000Z-xrp-collateral-cftc-bitnomial-payward-kamilah-video.json"
    )
    regulation = snapshot["regulation"]
    assert regulation["original_requester"] == "Coinbase Financial Markets, Inc."
    assert regulation["legal_character"] == "CONDITIONAL_STAFF_NO_ACTION_POSITION_NOT_A_FORMAL_RULE"
    assert any("three months" in item.lower() for item in regulation["conditions"])
    assert "No CFTC-wide XRP approval" in regulation["xrp_specificity"]


def test_payward_acquisition_owns_bitnomial_stack_but_not_xrp_usage():
    snapshot = load_json(
        "data/xrp_intelligence/snapshots/20261101T194000Z-xrp-collateral-cftc-bitnomial-payward-kamilah-video.json"
    )
    ownership = snapshot["ownership_and_strategy"]
    assert ownership["acquisition_completed"] == "2026-05-01"
    assert set(ownership["acquired_stack"]) == {"FCM", "DCM", "DCO"}
    assert ownership["strategic_inference"].endswith("not proof of XRP volume.")


def test_cftc_no_action_path_does_not_prove_coinbase_uses_xrp():
    snapshot = load_json(
        "data/xrp_intelligence/snapshots/20261101T194000Z-xrp-collateral-cftc-bitnomial-payward-kamilah-video.json"
    )
    assert snapshot["regulation"]["coinbase_actual_use"] == "NOT_ESTABLISHED; no FCM notice, XRP customer balance or Bitnomial clearing relationship verified."


def test_kamilah_video_factcheck_preserves_transcript_and_scope_limits():
    profile = load_json("data/xrp_intelligence/sources/kamilah_stevenson_channel.json")
    fact = next(item for item in profile["video_fact_checks"] if item["video_id"] == "M8TmDXO7B-0")
    assert fact["verdict"] == "LIMITED_VENUE_TRUE; UNIVERSAL_CFTC_APPROVAL_AND_EQUAL_RISK_CLASS_NOT_ESTABLISHED"
    assert fact["transcript_status"] == "NOT_RETRIEVED"
