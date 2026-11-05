"""Regression checks for the Fuelmaps XRP spot order-book depth observation."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T130000Z-xrp-spot-orderbook-depth-fuelmaps.json"


def test_xrp_orderbook_depth_snapshot_preserves_published_bands_and_scope():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    market = data["market_snapshot"]
    assert market["displayed_mid_usd"] == 1.3059
    assert market["venues_reporting"] == 6
    assert market["venue_universe"] == ["Coinbase", "OKX", "Kraken", "Bitstamp", "Bitfinex", "Gemini"]
    bands = {item["within_pct"]: item for item in market["depth_bands_usd_millions"]}
    assert bands[0.5] == {"within_pct": 0.5, "bids": 7.6, "asks": 5.1, "bid_share_pct": 59.7, "venues_reporting": 6}
    assert bands[1]["bids"] == 10.2 and bands[1]["asks"] == 8.4
    assert bands[5]["bids"] == 18.8 and bands[5]["asks"] == 15.5
    assert bands[10]["venues_reporting"] == 5
    assert market["excluded_venues"] == ["Binance", "Bitget"]


def test_xrp_orderbook_snapshot_does_not_claim_durable_or_executable_liquidity():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    limits = data["source_registry"][0]["source_limits"]
    assert any("cancelled" in item for item in limits)
    assert any("hidden or iceberg" in item for item in limits)
    assert any("hourly columns average one-minute snapshots" in item for item in limits)
    assert data["source_independence"]["publisher_groups"] == 1
    assert data["source_independence"]["not_six_independent_publishers"] is True


def test_xrp_orderbook_snapshot_remains_research_only_without_raw_receipts():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    raw = data["raw_capture"]
    assert raw["raw_source_bytes_preserved"] is False
    assert raw["sha256"] is None
    assert raw["independent_timestamp_anchor"] is False
    assert data["model_eligibility"]["eligible"] is False
    assert data["model_eligibility"]["forecast_issued"] is False
    assert data["model_eligibility"]["feature_admission"] == "RESEARCH_ONLY_NOT_ADMITTED"
    assert {item["id"] for item in data["competing_hypotheses"]} == {
        "H1_DISPLAYED_BID_SIDE_SKEW",
        "H2_CANCELLATION_AND_HIDDEN_LIQUIDITY",
        "H3_INCOMPLETE_VENUE_UNIVERSE",
    }
