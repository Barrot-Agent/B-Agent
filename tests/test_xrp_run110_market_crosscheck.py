from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261110T020036Z-run110-xrp-spot-derivatives-orderbook-etf-update.json"


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_run110_surfaced_spot_receipts_hash_exact_text_and_fail_closed_on_stale_data():
    data = load_artifact()
    spot = data["spot"]
    for key in ("kraken_xrpusd", "okx_xrpusdt"):
        item = spot[key]
        assert hashlib.sha256(item["response_text"].encode("utf-8")).hexdigest() == item["response_text_sha256"]
        assert item["model_eligible"] is False
    assert spot["kraken_xrpusd"]["provider_event_time_utc"] is None
    assert "Provider event timestamp is absent" in spot["kraken_xrpusd"]["exclusion_reason"]
    okx = spot["okx_xrpusdt"]
    assert okx["age_seconds_at_capture"] > okx["maximum_live_age_seconds"]
    assert okx["last_trade_below_displayed_bid"] is True
    assert spot["cross_venue_comparison"]["synchronized"] is False
    assert spot["cross_venue_comparison"]["contemporaneous_usdt_usd_normalization"] is False
    assert spot["cross_venue_comparison"]["arbitrage_inference"] is False


def test_run110_derivatives_disagreement_is_preserved_without_averaging():
    data = load_artifact()
    sources = {item["source"]: item for item in data["derivatives"]}
    assert set(sources) == {"Liqwall", "TradRadar"}
    assert sources["Liqwall"]["open_interest_usd"] == 1_230_000_000
    assert sources["TradRadar"]["open_interest_usd"] == 1_670_000_000
    assert data["derivatives_reconciliation"]["aggregates_averaged"] is False
    assert data["derivatives_reconciliation"]["venue_coverage_overlap"] is True
    assert data["derivatives_reconciliation"]["directional_conclusion"] is None


def test_run110_orderbook_universe_and_staleness_are_not_mixed():
    data = load_artifact()
    fuelmaps, edge = data["orderbook"]
    assert fuelmaps["market_scope"].startswith("spot-only")
    assert fuelmaps["venue_coverage"].startswith("5 of 6")
    assert fuelmaps["bands_usd"]["1pct"]["bid_share_pct"] == 62.8
    assert fuelmaps["model_eligible"] is False
    assert fuelmaps["age_seconds_at_capture"] > 18_000
    assert "perpetual" in edge["market_scope"]
    assert edge["model_eligible"] is False
    assert data["orderbook_reconciliation"]["displayed_depth_predictive_validation"] is False


def test_run110_etf_flow_methods_keep_flow_volume_and_aum_separate():
    data = load_artifact()
    byk = next(item for item in data["etf_flows"] if item["source"] == "ByKaranteli")
    alpha = next(item for item in data["etf_flows"] if item["source"] == "Alpha Finance")
    investor = next(item for item in data["etf_flows"] if item["source"] == "TheXRPInvestor")
    assert byk["latest_complete_trading_day"] == "2026-11-06"
    assert byk["five_day_net_flow_usd"] == -530_000
    assert alpha["last_seven_sessions_net_flow_usd"] == 8_400_000
    assert data["etf_reconciliation"]["averaging_performed"] is False
    assert investor["product_count_mismatch"] is True
    assert investor["flow_measurement"] is False
    assert data["etf_reconciliation"]["trading_volume_treated_as_flow"] is False


def test_run110_future_cpi_release_is_not_recorded_as_published():
    event = load_artifact()["macro_events"]["next_event"]
    scheduled = datetime.fromisoformat(event["scheduled_at_et"].replace("Z", "+00:00"))
    captured = datetime.fromisoformat(load_artifact()["captured_at_utc"].replace("Z", "+00:00"))
    assert event["status"] == "UPCOMING_AT_CAPTURE"
    assert event["result_available"] is False
    assert scheduled > captured


def test_run110_never_issues_directional_forecast_from_web_crosschecks():
    data = load_artifact()
    assert data["capture_integrity"]["model_admission"] is False
    assert data["capture_integrity"]["forecast_issued"] is False
    assert data["research_interpretation"]["no_directional_forecast"] is True
