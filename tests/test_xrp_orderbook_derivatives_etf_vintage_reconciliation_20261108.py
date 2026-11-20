from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261108T130321Z-xrp-orderbook-derivatives-etf-vintage-reconciliation.json"


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_all_preserved_source_excerpt_hashes_match():
    artifact = load_artifact()
    for receipt in artifact["source_receipts"]:
        assert hashlib.sha256(receipt["excerpt"].encode("utf-8")).hexdigest() == receipt["sha256"]


def test_fuelmaps_depth_bid_share_arithmetic_and_coverage():
    artifact = load_artifact()
    depth = artifact["orderbook_depth"]
    assert depth["snapshot_time_utc"] == "2026-11-08T12:00:00Z"
    assert depth["age_seconds_at_reference"] == 3801
    assert depth["venues_reporting"] == 6
    assert depth["excluded_venues"] == ["Binance", "Bitget"]
    for band in depth["bands"]:
        calculated = band["bids_usd_m"] / (band["bids_usd_m"] + band["asks_usd_m"]) * 100
        assert math.isclose(calculated, band["bid_share_pct"], abs_tol=0.15)
    assert depth["model_eligible"] is False


def test_binance_derivatives_timestamp_fails_freshness_gate():
    artifact = load_artifact()
    derivatives = artifact["derivatives"]
    assert derivatives["provider_event_timestamp_utc"] == "2026-11-08T12:35:59Z"
    assert derivatives["age_seconds_at_reference"] == 1642
    assert derivatives["freshness_limit_seconds"] == 300
    assert derivatives["freshness_status"] == "STALE_BY_1342_SECONDS_BEYOND_300_SECOND_LIMIT"
    assert math.isclose(derivatives["mark_index_basis_bps"], -3.112994898, abs_tol=1e-9)
    assert derivatives["last_funding_rate_pct_per_8h"] == 0.009823
    assert derivatives["open_interest"] is None
    assert derivatives["liquidations"] is None
    assert derivatives["model_eligible"] is False


def test_etf_provider_universes_and_future_dated_file_are_quarantined():
    artifact = load_artifact()
    flows = artifact["etf_flow_reconciliation"]
    assert flows["cryptokeyhole"]["reported_nov6_partial_change_xrp"] == -752048
    assert flows["cryptokeyhole"]["nov6_fund_coverage"] == "3 of 4; Franklin XRPZ missing"
    assert "future-dated" in flows["cryptokeyhole"]["date_anomaly"]
    assert flows["holdhub"]["issuer_pages_showing_daily_dollar_flow"] == 0
    assert flows["holdhub"]["franklin_xrpz_holdings_change"] == 8635002
    assert flows["alpha_finance"]["fund_universe_size"] == 5
    assert flows["reconciliation_status"] == "UNRESOLVED_DIFFERENT_UNIVERSES_AND_MEASUREMENT_DEFINITIONS"


def test_holdings_and_net_assets_are_not_conflated():
    artifact = load_artifact()
    h = artifact["etf_flow_reconciliation"]["holdhub"]
    assert h["holdings_change_pct"] > 0
    assert h["net_assets_change_pct"] < 0
    assert "not a direct flow proxy" in h["interpretation"]


def test_competing_hypotheses_and_disconfirming_evidence_are_retained():
    artifact = load_artifact()
    assert {x["id"] for x in artifact["competing_hypotheses"]} == {"H1", "H2", "H3", "H4"}
    assert len(artifact["disconfirming_evidence"]) >= 5
    assert "not independent confirmations" in artifact["etf_flow_reconciliation"]["source_independence"]


def test_no_feature_admission_or_forecast():
    artifact = load_artifact()
    assert artifact["model_admission"]["admitted_to_feature_store"] is False
    assert artifact["forecast_status"] == "NOT_ISSUED"
    assert artifact["external_actions"]["feature_store_write"] is False
    assert artifact["external_actions"]["paper_trade"] is False
    assert artifact["external_actions"]["real_money"] is False
