from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261106T1102Z-xrp-cross-source-market-window.json"


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_kraken_snapshot_hash_and_timestamp_limits_are_explicit():
    spot = load_artifact()["spot"]
    assert spot["last_usd"] == 1.19626
    assert spot["best_bid_usd"] == 1.19624
    assert spot["best_ask_usd"] == 1.19625
    assert spot["volume_24h_xrp"] == 48615402.71473088
    assert spot["vwap_24h_usd"] == 1.23952667
    assert spot["utc_day_open_usd"] == 1.20567
    assert spot["provider_event_timestamp"] is None
    assert spot["retrieval_timestamp_utc"] is None
    assert spot["raw_http_wire_bytes_attached"] is False
    assert len(spot["rendered_response_sha256"]) == 64
    assert spot["model_eligible"] is False
    assert "not byte-complete" in spot["hash_scope"]


def test_utc_day_open_is_not_mislabeled_as_rolling_24_hour_open():
    spot = load_artifact()["spot"]
    assert spot["utc_day_open_usd"] == 1.20567
    assert spot["last_vs_utc_day_open_pct"] < 0
    assert "UTC day" in spot["depth_status"] or "UTC day" in load_artifact()["source_registry"][0]["url"] or "daily" in spot["depth_status"].lower()


def test_derivatives_preserve_venue_coverage_and_lower_bound_liquidations():
    data = load_artifact()["derivatives"]
    assert len(data["venue_coverage"]) == 7
    assert data["open_interest_usd"] == 1870000000
    assert data["open_interest_change_24h_pct"] == -8.85
    assert data["oi_weighted_funding_pct_per_8h"] == 0.0071
    assert data["long_liquidations_lower_bound_usd"] == 19320000
    assert data["short_liquidations_lower_bound_usd"] == 486910
    assert data["long_short_account_ratio"] == 3.99
    assert "not notional exposure" in data["account_ratio_caveat"]


def test_etf_latest_day_is_not_promoted_to_a_complete_zero():
    etf = load_artifact()["etf_flows"]
    assert etf["xrp_insights"]["net_flow_xrp"] == -259701
    assert etf["xrp_insights"]["nov_5_status"].startswith("Provisional")
    assert etf["cryptokeyhole"]["nov_5_status"].startswith("Partial")
    assert etf["cryptoetf_today"]["reporting_funds"] == 2
    assert etf["cryptoetf_today"]["total_funds"] == 5
    assert etf["cryptoetf_today"]["reported_flow_usd"] == 0
    assert etf["cryptoetf_today"]["status"] == "partial"
    assert etf["the_xrp_investor"]["headline_product_count"] != etf["the_xrp_investor"]["listed_category_count"]


def test_market_hypotheses_retain_counterevidence_and_no_forecast():
    data = load_artifact()
    ids = {item["id"] for item in data["competing_hypotheses"]}
    assert {"leveraged_long_unwind", "cross_asset_risk_off", "spot_stabilization_or_short_covering", "etf_flow_absorption_gap", "provider_vintage_disagreement"} <= ids
    assert all("counterevidence" in item for item in data["competing_hypotheses"])
    assert data["forecast_status"]["directional_forecast_issued"] is False
    assert data["forecast_status"]["shadow_forecast_issued"] is False
    assert data["data_quality"]["point_in_time_model_eligible"] is False
    assert data["no_action"]["real_money_actions"] is False
    assert data["no_action"]["paper_trade_executed"] is False
