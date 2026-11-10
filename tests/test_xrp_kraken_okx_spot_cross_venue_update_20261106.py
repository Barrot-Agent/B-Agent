from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261106T165214Z-xrp-kraken-okx-spot-cross-venue-update.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_normalized_source_receipts_reproduce_and_do_not_claim_wire_capture():
    data = load_artifact()
    assert len(data["source_registry"]) == 2
    for source in data["source_registry"]:
        receipt = source["receipt"]
        assert receipt["algorithm"] == "SHA-256"
        assert hashlib.sha256(source["excerpt"].encode("utf-8")).hexdigest() == receipt["digest"]
        assert "not original HTTP wire bytes" in receipt["scope"]
    assert data["source_registry"][0]["provider_event_timestamp_utc"] is None
    assert data["source_registry"][1]["provider_event_timestamp_utc"] == "2026-11-06T16:52:14.179Z"


def test_kraken_quote_spread_and_reference_window_arithmetic():
    row = load_artifact()["spot_observations"][0]
    midpoint = (row["best_bid_usd"] + row["best_ask_usd"]) / 2
    spread = (row["best_ask_usd"] - row["best_bid_usd"]) / midpoint * 10000
    assert math.isclose(row["spread_bps"], spread, rel_tol=0, abs_tol=1e-10)
    assert math.isclose(
        row["last_vs_vwap_24h_pct"],
        (row["last_trade_usd"] / row["vwap_24h_usd"] - 1) * 100,
        rel_tol=0,
        abs_tol=1e-10,
    )
    assert math.isclose(
        row["last_vs_utc_day_open_pct"],
        (row["last_trade_usd"] / row["utc_day_open_usd"] - 1) * 100,
        rel_tol=0,
        abs_tol=1e-10,
    )
    assert row["provider_event_timestamp_utc"] is None
    assert row["quote_components_same_event_sequence_established"] is False


def test_okx_provider_timestamp_and_spot_arithmetic_are_exact():
    row = load_artifact()["spot_observations"][1]
    parsed = datetime.fromisoformat(row["provider_event_timestamp_utc"].replace("Z", "+00:00"))
    assert parsed.astimezone(timezone.utc).isoformat() == "2026-11-06T16:52:14.179000+00:00"
    assert int(parsed.timestamp() * 1000) == row["provider_timestamp_epoch_ms"] == 1793983934179
    midpoint = (row["best_bid_usdt"] + row["best_ask_usdt"]) / 2
    spread = (row["best_ask_usdt"] - row["best_bid_usdt"]) / midpoint * 10000
    assert math.isclose(row["spread_bps"], spread, rel_tol=0, abs_tol=1e-10)
    assert math.isclose(
        row["last_vs_open_24h_pct"],
        (row["last_trade_usdt"] / row["open_24h_usdt"] - 1) * 100,
        rel_tol=0,
        abs_tol=1e-10,
    )
    assert math.isclose(
        row["last_vs_utc_8h_open_pct"],
        (row["last_trade_usdt"] / row["utc_8h_open_usdt"] - 1) * 100,
        rel_tol=0,
        abs_tol=1e-10,
    )


def test_cross_venue_prices_are_not_treated_as_synchronized_spread_or_arbitrage():
    data = load_artifact()
    row = data["cross_venue_reconciliation"]
    assert row["observations_are_synchronized"] is False
    assert row["common_point_in_time_cutoff_utc"] is None
    assert row["quote_currencies_differ"] is True
    assert row["cross_venue_price_spread_or_arbitrage_claim_permitted"] is False
    assert row["order_book_depth_observed"] is False


def test_prior_derivatives_vintage_is_not_carried_forward_as_current():
    row = load_artifact()["derivatives_status"]
    assert row["status"] == "NO_NEW_SYNCHRONIZED_DERIVATIVES_OBSERVATION"
    assert "stale vintage" in row["note"]
    assert "not carried forward" in row["note"]


def test_competing_hypotheses_preserve_support_and_disconfirmation():
    rows = load_artifact()["competing_hypotheses"]
    assert len(rows) == 3
    assert all(row["supporting"] and row["disconfirming"] for row in rows)
    assert any(row["status"] == "CONFIRMED_DATA_LIMITATION" for row in rows)


def test_no_forecast_model_admission_or_market_action_is_created():
    data = load_artifact()
    assert data["forecast_status"]["status"] == "NOT_ISSUED"
    assert data["forecast_status"]["directional_forecast_issued"] is False
    assert data["model_eligibility"]["eligible"] is False
    assert data["safety"]["paper_trade_executed"] is False
    assert data["safety"]["real_money_action"] is False
    assert data["safety"]["external_submission"] is False
