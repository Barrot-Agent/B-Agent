from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261108T124058Z-xrp-live-market-etf-cross-publisher-reconciliation.json"


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_exact_exchange_response_hashes_match():
    artifact = load_artifact()
    for receipt in artifact["direct_market_receipts"]:
        digest = hashlib.sha256(receipt["raw_response_text"].encode("utf-8")).hexdigest()
        assert digest == receipt["sha256"]


def test_normalized_etf_excerpt_hashes_match():
    artifact = load_artifact()
    for receipt in artifact["source_receipts"]:
        digest = hashlib.sha256(receipt["excerpt"].encode("utf-8")).hexdigest()
        assert digest == receipt["sha256"]


def test_provider_event_times_are_not_replaced_by_retrieval_time():
    artifact = load_artifact()
    receipts = {r["publisher"]: r for r in artifact["direct_market_receipts"]}
    assert receipts["Kraken"]["provider_event_timestamp_utc"] is None
    assert receipts["OKX"]["provider_event_timestamp_utc"] == "2026-11-08T12:34:36.967Z"
    assert receipts["Binance"]["provider_event_timestamp_utc"] == "2026-11-08T12:35:59Z"
    assert artifact["retrieval_limits"]["exact_http_retrieval_time_exposed"] is False


def test_stale_and_boundary_market_observations_fail_closed():
    artifact = load_artifact()
    receipts = {r["publisher"]: r for r in artifact["direct_market_receipts"]}
    assert receipts["OKX"]["freshness_status"] == "STALE_BY_82.033_SECONDS_AT_REFERENCE"
    assert receipts["Binance"]["freshness_status"] == "AT_300_SECOND_BOUNDARY_OR_STALE_BY_RETRIEVAL_COMPLETION"
    assert all(not r["model_eligible"] for r in receipts.values())


def test_kraken_utc_day_open_is_not_renamed_as_rolling_24h_open():
    artifact = load_artifact()
    kraken = artifact["direct_market_metrics"]["kraken"]
    assert kraken["daily_open_usd"] == 1.16234
    assert "UTC-day open" in kraken["source_field_note"]
    assert "open_24h_usd" not in kraken


def test_market_metrics_reproduce_and_depth_is_not_overstated():
    artifact = load_artifact()
    metrics = artifact["direct_market_metrics"]
    assert math.isclose(metrics["kraken"]["spread_bps"], 0.0859656739, rel_tol=0, abs_tol=1e-9)
    assert math.isclose(metrics["okx"]["spread_bps"], 0.8587007857, rel_tol=0, abs_tol=1e-9)
    assert math.isclose(metrics["binance_perpetual"]["mark_index_basis_bps"], -3.112994898, rel_tol=0, abs_tol=1e-8)
    assert artifact["orderbook_depth"]["multi_level_depth_captured"] is False
    assert artifact["orderbook_depth"]["only_level_one_quotes_available"] is True


def test_etf_flow_sources_keep_different_universes_and_definitions():
    artifact = load_artifact()
    flows = artifact["etf_flow_reconciliation"]
    insights = flows["xrp_insights"]
    alpha = flows["alpha_finance"]
    assert insights["nov6_reported_holdings_delta_xrp"] == -663043
    assert insights["nov2_to_nov6_reported_holdings_delta_xrp"] == -812529
    assert insights["flow_status"] == "ISSUER_REPORTED_HOLDINGS_DELTA_PROXY_NOT_VERIFIED_CREATION_REDEMPTION"
    assert alpha["nov6_reported_daily_flow_usd"] == 0
    assert alpha["upstream_dashboard_feed"] == "CoinGlass, per Alpha Finance methodology page."
    assert set(alpha["fund_universe"]) == {"XRP/Bitwise", "XRPZ/Franklin Templeton", "XRPC/Canary Capital", "GXRP/Grayscale", "TOXR/21Shares"}
    assert "XRPR" in alpha["excluded_from_five_fund_panel"]
    assert "BITW" in alpha["excluded_from_five_fund_panel"]
    assert flows["reconciliation_status"] == "UNRESOLVED_DIFFERENT_UNIVERSES_AND_UPSTREAM_FEEDS"


def test_no_averaging_or_false_independent_confirmation():
    artifact = load_artifact()
    flows = artifact["etf_flow_reconciliation"]
    assert "not independent confirmations" in flows["source_independence"]
    assert "prevent the values from being averaged" in " ".join(flows["why_not_comparable"])


def test_no_feature_store_write_or_forecast():
    artifact = load_artifact()
    assert artifact["model_admission"]["admitted_to_feature_store"] is False
    assert artifact["forecast_status"] == "NOT_ISSUED"
    assert artifact["external_actions"]["feature_store_write"] is False
    assert artifact["external_actions"]["paper_trade"] is False
    assert artifact["external_actions"]["real_money"] is False
