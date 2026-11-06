from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261106-clarity-act-and-risk-off-xrp-context.json"


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_clarity_act_vote_is_procedural_and_motion_to_reconsider_is_preserved():
    data = load_artifact()
    vote = data["regulatory_event"]["official_vote"]
    follow_up = data["regulatory_event"]["follow_up"]
    assert vote["record_vote_number"] == 234
    assert vote["yeas"] == 49
    assert vote["nays"] == 50
    assert vote["not_voting"] == 1
    assert vote["required_threshold"] == "3/5"
    assert vote["result"] == "Cloture on the motion to proceed rejected"
    assert follow_up["motion_to_reconsider_entered"] is True
    assert "not a final passage vote" in follow_up["interpretation"]


def test_january_3_lapse_claim_is_not_mislabeled_as_official_status():
    data = load_artifact()
    claim = data["regulatory_event"]["follow_up"]["january_3_lapse_claim"]
    assert claim["status"] == "secondary_legal_opinion_not_official_status"
    assert "do not themselves establish" in claim["description"]
    assert claim["publisher"] == "24/7 Wall St"
    assert claim["source_url"].startswith("https://247wallst.com/")
    sources = {item["id"]: item for item in load_artifact()["source_registry"]}
    assert sources["clarity_lapse_secondary_opinion"]["source_type"] == "secondary_legal_opinion"


def test_zero_etf_flow_is_not_reclassified_as_outflow():
    flows = load_artifact()["xrp_market_context"]["etf_flows"]
    assert flows["consecutive_trading_days_with_zero_net_flow"] == 3
    assert flows["net_flow_status"].startswith("zero")
    assert flows["cumulative_net_inflows_since_launch_usd"] == 1_810_000_000
    assert flows["net_assets_usd"] == 1_410_000_000
    assert "not evidence of negative cumulative flows" in flows["limitation"]


def test_okx_long_short_ratio_is_account_count_and_single_venue():
    data = load_artifact()["xrp_market_context"]["okx_derivatives"]
    assert data["venue"] == "OKX"
    assert data["open_interest_change_pct"] == -8.9
    assert data["long_short_account_ratio_midnight"] == 4.12
    assert "Account counts are not notional exposure" in data["limitation"]
    assert "Single-venue" in data["limitation"]


def test_macro_risk_off_is_context_not_xrp_causation():
    data = load_artifact()
    macro = data["macro_event"]
    assert macro["reported_closes"]["nasdaq_composite_pct"] == -5.52
    assert macro["reported_closes"]["sp500_pct"] == -4.36
    assert macro["reported_closes"]["philadelphia_semiconductor_index_pct"] == -12.0
    assert "does not prove" in macro["causal_limit"]


def test_kraken_and_coingecko_snapshots_remain_time_separated_and_model_ineligible():
    market = load_artifact()["xrp_market_context"]
    coingecko = market["coingecko_article_snapshot"]
    kraken = market["later_kraken_tool_rendered_observation"]
    assert coingecko["source_observation_utc"].startswith("2026-11-06 around 05:50")
    assert coingecko["price_usd"] == 1.20
    assert kraken["last_usd"] == 1.18647
    assert kraken["provider_event_timestamp"] is None
    assert kraken["model_eligible"] is False


def test_bls_release_is_upcoming_and_no_forecast_is_issued():
    data = load_artifact()
    assert data["event_watch"]["bls_release"]["scheduled_local"] == "2026-11-06 08:30 America/New_York"
    assert data["event_watch"]["bls_release"]["status_at_run_start"] == "upcoming"
    assert data["forecast_status"]["directional_forecast_issued"] is False
    assert data["forecast_status"]["shadow_forecast_issued"] is False


def test_sources_keep_primary_and_secondary_independence_groups_separate():
    sources = {item["id"]: item for item in load_artifact()["source_registry"]}
    assert sources["senate_roll_call_234"]["source_type"] == "primary_official"
    assert sources["senate_roll_call_234"]["independence_group"] == sources["senate_floor_0915"]["independence_group"]
    assert sources["tokenpost_xrp_etf"]["source_type"] == "secondary_republication"
    assert sources["tokenpost_xrp_etf"]["independence_group"] == "sosovalue_data_republished_by_tokenpost"
    assert sources["reuters_nasdaq_close"]["independence_group"] == sources["reuters_data_center_risk"]["independence_group"]
