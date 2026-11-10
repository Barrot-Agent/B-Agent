"""Regression tests for the Binance bank-supervisory outreach and XRP market addendum."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T110654Z-binance-bank-supervisory-outreach-and-xrp-market-update.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_supervisory_outreach_is_reported_not_officially_confirmed():
    data = load()
    sources = {item["source_id"]: item for item in data["source_registry"]}
    claims = {item["claim_id"]: item for item in data["claims"]}
    outreach = claims["US_REGULATOR_BANK_OUTREACH_REPORTED"]
    assert outreach["status"] == "single_independent_news_report_not_officially_confirmed"
    assert sources["REUTERS_US_BANK_SUPERVISORY_OUTREACH_20261105"]["source_independence_group"] == "reuters_independent_reporting"
    assert data["data_quality"]["official_regulator_confirmation"] is False
    assert data["data_quality"]["xrp_specific_regulatory_action_established"] is False
    assert claims["BANK_SOURCE_REPORTED_NO_DISRUPTION"]["status"] == "limited_single_bank_source_observation"
    assert claims["BINANCE_UNAWARE_OF_BANK_REGULATOR_DISCUSSIONS"]["status"] == "issuer_response"


def test_binance_gross_affected_value_is_not_net_loss_or_recovery():
    claims = {item["claim_id"]: item for item in load()["claims"]}
    affected = claims["BINANCE_GROSS_AFFECTED_ASSET_VALUE"]
    frozen = claims["BINANCE_FROZEN_INTERCEPTED_VALUE"]
    replenishment = claims["BINANCE_REPLENISHMENT_CLAIM"]
    assert affected["amount_usd"] == 6_340_000_000
    assert affected["net_unrecovered_loss_usd"] is None
    assert frozen["amount_usd"] == 2_850_000_000
    assert replenishment["replenished_pct"] == 98
    assert "not the same as recovery" in " ".join(replenishment["limitations"])


def test_kraken_spot_quote_arithmetic_and_capture_gaps_are_explicit():
    data = load()
    spot = data["market_snapshot"]["spot"]
    mid = (spot["best_bid_usd"] + spot["best_ask_usd"]) / 2
    spread = (spot["best_ask_usd"] - spot["best_bid_usd"]) / mid * 10_000
    assert math.isclose(spot["mid_usd"], mid, rel_tol=0, abs_tol=1e-12)
    assert math.isclose(spot["displayed_spread_bps"], spread, rel_tol=0, abs_tol=1e-12)
    assert spot["volume_24h_xrp"] > 0
    assert spot["low_24h_usd"] <= spot["last_usd"] <= spot["high_24h_usd"]
    assert spot["quote_event_timestamp_utc"] is None
    assert spot["model_eligible"] is False


def test_market_and_event_data_remain_model_ineligible_without_raw_receipts():
    data = load()
    assert data["source_capture_policy"]["raw_http_bytes_captured"] is False
    assert data["source_capture_policy"]["raw_content_sha256"] is None
    assert data["source_capture_policy"]["independent_timestamp_anchor"] is False
    assert data["model_eligible"] is False
    assert data["forecast_issued"] is False
    assert data["predictions"]["status"] == "NOT_ISSUED"
    assert all(source["model_eligible"] is False for source in data["source_registry"])
