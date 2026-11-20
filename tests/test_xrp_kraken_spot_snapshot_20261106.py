"""Integrity checks for the 2026-11-06 Kraken XRP/USD rendered capture."""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime
from decimal import Decimal
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T000233Z-kraken-xrp-usd-spot-snapshot.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_rendered_capture_hash_and_wire_limitations_are_explicit() -> None:
    artifact = load_artifact()
    capture = artifact["source"]["capture"]
    rendered = capture["rendered_response_text"]
    assert hashlib.sha256(rendered.encode("utf-8")).hexdigest() == capture["rendered_text_sha256"]
    assert len(rendered.encode("utf-8")) == capture["rendered_text_utf8_bytes"]
    assert capture["kind"] == "web_rendered_json_text"
    assert capture["raw_http_wire_bytes_captured"] is False
    assert capture["response_headers_captured"] is False


def test_provider_event_time_is_not_fabricated_from_retrieval_window() -> None:
    artifact = load_artifact()
    source = artifact["source"]
    window = artifact["retrieval_window_utc"]
    start = datetime.fromisoformat(window["start"].replace("Z", "+00:00"))
    end = datetime.fromisoformat(window["end"].replace("Z", "+00:00"))
    assert start.tzinfo is not None and end.tzinfo is not None
    assert start < end
    assert source["provider_event_time_utc"] is None
    assert source["provider_http_date_utc"] is None
    assert source["data_cutoff_utc"] is None


def test_source_metrics_match_the_preserved_kraken_payload() -> None:
    artifact = load_artifact()
    payload = json.loads(artifact["source"]["capture"]["rendered_response_text"])
    row = payload["result"]["XXRPZUSD"]
    observed = artifact["observations"]
    assert observed["last_trade_usd"] == row["c"][0]
    assert observed["best_ask_usd"] == row["a"][0]
    assert observed["best_bid_usd"] == row["b"][0]
    assert observed["rolling_24h_volume_xrp"] == row["v"][1]
    assert observed["rolling_24h_vwap_usd"] == row["p"][1]
    assert observed["rolling_24h_low_usd"] == row["l"][1]
    assert observed["rolling_24h_high_usd"] == row["h"][1]
    assert observed["today_open_usd"] == row["o"]


def test_derived_spread_and_relative_prices_recompute() -> None:
    artifact = load_artifact()
    observed = artifact["observations"]
    derived = artifact["derived_observations"]
    bid = Decimal(observed["best_bid_usd"])
    ask = Decimal(observed["best_ask_usd"])
    last = Decimal(observed["last_trade_usd"])
    vwap = Decimal(observed["rolling_24h_vwap_usd"])
    day_open = Decimal(observed["today_open_usd"])
    low = Decimal(observed["rolling_24h_low_usd"])
    high = Decimal(observed["rolling_24h_high_usd"])
    midpoint = (bid + ask) / Decimal("2")
    spread = (ask - bid) / midpoint * Decimal("10000")
    assert math.isclose(derived["midpoint_usd"], float(midpoint), rel_tol=0, abs_tol=1e-12)
    assert math.isclose(derived["displayed_spread_basis_points"], float(spread), rel_tol=0, abs_tol=1e-10)
    assert math.isclose(derived["last_vs_rolling_24h_vwap_percent"], float((last / vwap - 1) * 100), rel_tol=0, abs_tol=1e-10)
    assert math.isclose(derived["last_vs_today_open_percent"], float((last / day_open - 1) * 100), rel_tol=0, abs_tol=1e-10)
    assert math.isclose(derived["last_vs_rolling_24h_low_percent"], float((last / low - 1) * 100), rel_tol=0, abs_tol=1e-10)
    assert math.isclose(derived["last_vs_rolling_24h_high_percent"], float((last / high - 1) * 100), rel_tol=0, abs_tol=1e-10)


def test_snapshot_remains_model_ineligible_and_forecast_disabled() -> None:
    artifact = load_artifact()
    assert artifact["model_eligible"] is False
    assert artifact["forecast_status"] == "NOT_ISSUED"
    assert artifact["forecast_issued"] is False
    assert artifact["model_ineligibility_reasons"]
    assert artifact["source"]["source_scope"] == "single-venue spot ticker"
