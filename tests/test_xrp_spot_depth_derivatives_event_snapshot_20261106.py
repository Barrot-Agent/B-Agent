from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261106T081536Z-xrp-live-spot-depth-derivatives-event-snapshot.json"


def load_snapshot():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_live_kraken_spot_quote_preserves_top_of_book_and_timestamp_limits():
    data = load_snapshot()
    spot = data["spot_market"]["kraken_xrpusd"]
    assert spot["last_trade_usd"] == 1.18042
    assert spot["best_bid_usd"] == 1.18005
    assert spot["best_ask_usd"] == 1.18023
    expected = (spot["best_ask_usd"] - spot["best_bid_usd"]) / ((spot["best_ask_usd"] + spot["best_bid_usd"]) / 2) * 10000
    assert math.isclose(spot["spread_bps"], expected, rel_tol=0, abs_tol=1e-12)
    assert spot["provider_event_time_utc"] is None
    assert spot["model_eligible"] is False


def test_spot_depth_keeps_venue_scope_and_older_snapshot_time():
    data = load_snapshot()
    depth = data["order_book_depth"]
    assert depth["snapshot_time_utc"] == "2026-11-06T03:00:00Z"
    assert depth["venue_coverage_count"] == 6
    assert "Binance" in data["source_registry"][1]["excluded_venues"]
    two = next(x for x in depth["levels"] if x["band"] == "±2%")
    assert two["bid_depth_usd"] == 19600000
    assert two["ask_depth_usd"] == 11300000
    assert two["venues_reporting"] == 6


def test_derivatives_provider_totals_are_not_averaged_across_unmatched_universes():
    data = load_snapshot()["derivatives"]
    assert data["tradradar"]["open_interest_7_exchanges_usd"] == 1910000000
    assert data["kodexius"]["open_interest_7_contracts_usd"] == 799210000
    assert data["comparability"]["headline_open_interest_values_comparable"] is False
    assert data["comparability"]["difference_usd"] == 1110790000


def test_macro_event_is_scheduled_and_prediction_remains_fail_closed():
    data = load_snapshot()
    event = data["macro_event_timeline"][0]
    assert event["scheduled_utc"] == "2026-11-06T13:30:00Z"
    assert event["status_at_cutoff"] == "SCHEDULED_NOT_YET_RELEASED"
    assert data["model_eligibility"]["eligible"] is False
    assert data["forecast_status"] == "NOT_ISSUED"
    assert data["directional_forecast_issued"] is False
    assert data["paper_trade_executed"] is False
    assert data["real_money_action"] is False
