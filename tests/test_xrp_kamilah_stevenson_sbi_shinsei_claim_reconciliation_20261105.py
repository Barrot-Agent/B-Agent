import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261105-kamilah-stevenson-sbi-shinsei-claim-reconciliation.json"
)


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_person_identity_is_confirmed_but_channel_handle_remains_probable():
    identity = load()["identity_resolution"]
    assert identity["person_identity_status"] == "CONFIRMED"
    assert identity["candidate_youtube_channel"]["handle"] == "@drkamilahstevenson"
    assert identity["candidate_youtube_channel"]["attribution_confidence"] == "PROBABLE_NOT_FULLY_FIRST_PARTY_LINKED"
    assert any("fake pages" in item.lower() for item in identity["identity_evidence"][0]["evidence"])


def test_video_inventory_is_unique_non_exhaustive_and_preserves_attribution_basis():
    data = load()
    videos = data["youtube_video_inventory"]
    ids = [video["video_id"] for video in videos]
    assert len(videos) == 11
    assert len(ids) == len(set(ids))
    assert data["video_inventory_exhaustive"] is False
    assert all(video["youtube_url"].startswith("https://www.youtube.com/watch?v=") for video in videos)
    assert sum(video["person_attribution_confidence"] == "HIGH" for video in videos) == 3
    assert any(video["title"] == "How Much XRP Do You ACTUALLY Need?" for video in videos)


def test_june_sbi_shinsei_interest_pilot_is_secondary_reported_not_primary_confirmed():
    claim = next(
        item for item in load()["claim_reconciliation"]
        if item["claim_id"] == "sbi_shinsei_20_percent_interest_crypto_pilot"
    )
    assert claim["status"] == "SECONDARY_REPORTED_PRIMARY_CONFIRMATION_NOT_LOCATED"
    assert len(claim["secondary_sources"]) == 4
    assert "not four independent primary confirmations" in claim["source_independence"]
    assert claim["capital_and_demand_interpretation"][0].startswith("Deposits remain yen-denominated")
    assert claim["capital_and_demand_interpretation"][1].startswith("A voucher is not an XRP market purchase")
    assert claim["capital_and_demand_interpretation"][2].startswith("No aggregate pilot participation")
    assert claim["model_eligible"] is False


def test_official_february_xrp_voucher_campaign_is_not_conflated_with_june_pilot():
    claim = next(
        item for item in load()["claim_reconciliation"]
        if item["claim_id"] == "sbi_shinsei_20_percent_interest_crypto_pilot"
    )
    official = claim["official_related_but_distinct_programs"][0]
    assert official["date"] == "2026-02-02"
    assert "not the reported 20%-of-interest pilot" in official["terms"]
    assert "up to ¥20,000" in official["terms"]


def test_japanese_law_is_general_framework_not_xrp_specific_approval():
    claim = next(
        item for item in load()["claim_reconciliation"]
        if item["claim_id"] == "japan_crypto_asset_reclassification"
    )
    dates = {event["date"] for event in claim["primary_timeline"]}
    assert dates == {"2026-06-11", "2026-07-15", "2026-07-23"}
    assert claim["status"] == "PARTIALLY_ACCURATE_BUT_OVERSTATED"
    assert any("does not approve XRP individually" in item for item in claim["unsupported_parts"])
    assert "within one year" in claim["statutory_detail"]


def test_sbi_xrp_swift_performance_claim_is_not_supported_by_official_poc_or_research():
    claim = next(
        item for item in load()["claim_reconciliation"]
        if item["claim_id"] == "japanese_banks_live_xrp_vs_swift_50x_60_percent"
    )
    assert claim["status"] == "UNVERIFIED_NO_PRIMARY_PERFORMANCE_EVIDENCE_FOUND"
    classifications = {item["classification"] for item in claim["primary_counterevidence"]}
    assert "CONCEPTUAL_PROOF_OF_CONCEPT" in classifications
    assert "RESEARCH_NOT_COMMERCIAL_SERVICE" in classifications
    assert "ANNOUNCED_OPERATIONAL_XRP_BRIDGE_SERVICE" in classifications
    assert "does not verify the specific live bank-versus-SWIFT performance claim" in claim["conclusion"]


def test_sbi_ripple_asia_ownership_and_operational_xrp_use_are_separated():
    data = load()["sbi_ripple_relationship_graph"]
    assert data["joint_venture"]["sbi_group_voting_rights_pct"] == 60
    assert data["joint_venture"]["ripple_share_pct"] == 40
    assert data["operational_xrp_use"]["bridge_asset"] == "XRP"
    assert data["operational_xrp_use"]["transaction_volume_disclosed"] is False
    assert data["research_and_poc"][0]["status"].startswith("research only")
    assert data["research_and_poc"][1]["status"].startswith("conceptual proof of concept")


def test_rlusd_fee_burn_and_optional_xrp_bridge_are_not_equated_with_market_demand():
    claim = next(
        item for item in load()["claim_reconciliation"]
        if item["claim_id"] == "rlusd_necessarily_increases_xrp_demand"
    )
    facts = claim["primary_protocol_facts"]
    assert any("destroys a small XRP fee" in item["fact"] for item in facts)
    assert any("can auto-bridge through XRP when cheaper" in item["fact"] for item in facts)
    assert claim["status"] == "HYPOTHESIS_NOT_ESTABLISHED"
    assert "No transaction-level bridge volume" in claim["interpretation"]


def test_exact_phrase_and_actual_capital_classifications_are_preserved():
    phrases = load()["exact_phrase_research"]
    assert phrases["ask_coin"]["status"] == "NO_NEW_VERIFIED_XRP_RELATION"
    assert phrases["actual_capital"]["status"] == "RELEVANT_EVERNORTH_USAGE_FOUND"
    assert phrases["sbic_chatgpt_sbic"]["status"] == "ACRONYM_COLLISION_RESOLVED"


def test_all_web_research_remains_model_ineligible_and_no_forecast_is_issued():
    provenance = load()["provenance"]
    assert provenance["model_eligible"] is False
    assert provenance["raw_source_sha256_receipts"] is None
    assert provenance["independent_timestamp_anchors"] is None
    assert len(load()["next_actions"]) >= 5
