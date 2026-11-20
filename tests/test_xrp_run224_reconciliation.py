import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261117T202045Z-run224-market-capital-identity-reconciliation.json"


def _utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    assert parsed.tzinfo is not None
    return parsed.astimezone(timezone.utc)


def _data():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_run224_sources_and_observations_are_provenance_safe():
    data = _data()
    assert data["artifact_type"] == "xrp_run224_market_capital_identity_reconciliation"
    assert _utc(data["captured_at_utc"]) >= _utc(data["data_cutoff_utc"])
    sources = {item["id"]: item for item in data["source_registry"]}
    assert len(sources) == len(data["source_registry"])
    for source in sources.values():
        assert source["raw_content_sha256"] is None
        assert source["raw_receipt_id"] is None
        assert source["raw_capture_status"] == "web_rendered_extract_only"
        assert source["model_eligible"] is False
    for observation in data["observations"]:
        assert observation["id"] and observation["claim"]
        assert observation["evidence"]
        assert set(observation["evidence"]) <= set(sources)
        assert observation["model_eligible"] is False
    for edge in data["relationship_graph"]:
        assert edge["from"] and edge["to"] and edge["relation"] and edge["status"]
        assert set(edge["evidence"]) <= set(sources)
    for hypothesis in data["competing_hypotheses"]:
        assert hypothesis["claim"] and hypothesis["support"]
        assert hypothesis["disconfirming_or_missing"] and hypothesis["test"]
    assert data["predictions"]["issued"] is False
    assert data["predictions"]["status"] == "NOT_ISSUED"


def test_run224_keeps_spot_perpetual_and_options_observations_separate():
    data = _data()
    cutoff = _utc(data["data_cutoff_utc"])
    spot = data["market_snapshot"]["xrp_spot_order_book"]
    perp = data["market_snapshot"]["xrp_perpetual_reference"]
    oi = data["market_snapshot"]["xrp_perpetual_later"]
    comparison = data["market_snapshot"]["xrp_perpetual_comparison"]
    options = data["market_snapshot"]["xrp_options"]
    assert spot["market_type"] == "spot"
    assert perp["market_type"] == "perpetual_futures"
    assert _utc(spot["as_of_utc"]) <= cutoff
    assert _utc(perp["as_of_utc"]) <= cutoff
    assert _utc(oi["as_of_utc"]) <= cutoff
    assert _utc(comparison["as_of_utc"]) <= cutoff
    assert oi["open_interest_usd"] != comparison["open_interest_usd"]
    assert "Do not average" in data["data_quality"]["no_averaging_policy"]
    assert options["historical_tail_check"]["three_sigma_breaches"] == 20
    assert options["historical_tail_check"]["observations"] == 928
    assert options["model_eligible"] is False


def test_run224_sbi_start_bond_distinguishes_real_debt_capital_from_xrp_rewards():
    data = _data()
    bond = data["capital_and_institutional"]["sbi_start_bonds"]
    assert bond["status"] == "ISSUED_AND_SOLD_OUT"
    assert bond["total_issue_amount_jpy"] == 10_000_000_000
    assert bond["coupon_pct_annual"] == 2.15
    assert bond["blockchain_infrastructure"] == "ibet for Fin (BOOSTRY)"
    assert bond["not_xrpl"] is True
    assert bond["xrp_subscription_reward_jpy_per_100000_face"] == 200
    assert bond["potential_reward_value_if_entire_issue_eligible_jpy"] == 20_000_000
    assert bond["actual_xrp_quantity_purchased_or_distributed"] == "NOT_VERIFIED_FROM_SOURCES_INSPECTED"
    assert "NOT_A_10BN_JPY_XRP_PURCHASE" in bond["classification"]


def test_run224_doppler_sbi_partnership_is_not_mislabeled_as_deployed_capital():
    item = _data()["capital_and_institutional"]["doppler_sbi_digital_finance"]
    assert item["announcement_date"] == "2026-07-13"
    assert item["financial_terms"] == "NOT_DISCLOSED"
    assert item["production_launch_date"] == "NOT_DISCLOSED"
    assert item["live_product_confirmed"] is False
    assert item["committed_capital_confirmed"] is False
    assert item["classification"].startswith("ANNOUNCED_STRATEGIC_DEVELOPMENT_PARTNERSHIP")


def test_run224_person_identity_is_separate_from_youtube_channel_attribution():
    identity = _data()["identity_and_exact_phrase_research"]["camilla_kamilah_stevenson"]
    assert identity["person_identity_status"] == "CONFIRMED_DR_KAMILAH_STEVENSON"
    assert identity["channel_identity_status"] == "PROBABLE_CANDIDATE_NOT_FIRST_PARTY_VERIFIED"
    assert identity["first_party_crosslink_found"] is False
    assert identity["verified_personal_channel_upload_count"] == 0
    assert identity["inventory_complete"] is False


def test_run224_sbic_and_ask_exact_phrase_results_are_scope_limited():
    identity = _data()["identity_and_exact_phrase_research"]
    assert identity["sbic_chatgpt"]["status"] == "ENTITY_RESOLVED_TRAINING_ONLY"
    assert "not an OpenAI partnership" in identity["sbic_chatgpt"]["observation"]
    assert identity["ask_coin"]["identity"] == "Permission Coin (ASK), created by Permission.io for permission-based advertising/data-reward use cases."
    assert identity["ask_coin"]["xrp_relationship"] == "NOT_ESTABLISHED"
    assert identity["actual_capital"]["verified_capital_event"].startswith("SBI Holdings' JPY 10BN")
    assert identity["japanese_bank_pilot_claims"]["status"] == "UNVERIFIED_MARKETING_OR_VIDEO_CLAIM"
