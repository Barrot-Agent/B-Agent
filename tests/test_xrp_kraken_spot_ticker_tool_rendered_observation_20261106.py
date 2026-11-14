from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T021137Z-kraken-xrpusd-spot-ticker-tool-rendered-observation.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_rendered_response_hash_and_timestamp_limits_are_explicit():
    item = load_artifact()
    source = item["source"]
    rendered = source["rendered_response_text"].encode("utf-8")
    assert hashlib.sha256(rendered).hexdigest() == source["rendered_response_sha256"]
    assert source["raw_http_wire_bytes_captured"] is False
    assert source["provider_event_timestamp_utc"] is None
    assert source["exact_retrieval_timestamp_utc"] is None
    assert item["run_context"]["exact_retrieval_timestamp_utc"] is None


def test_spot_metrics_reconcile_to_preserved_ticker_fields():
    item = load_artifact()
    observation = item["observation"]
    raw = observation["raw_ticker_fields"]
    bid = float(raw["bid"][0])
    ask = float(raw["ask"][0])
    last = float(raw["last"][0])
    assert math.isclose(
        observation["displayed_spread_bps"],
        (ask - bid) / ((ask + bid) / 2) * 10_000,
        rel_tol=0,
        abs_tol=1e-12,
    )
    assert math.isclose(observation["last_trade_usd"], last, rel_tol=0, abs_tol=1e-12)
    assert math.isclose(observation["rolling_24h_volume_xrp"], float(raw["volume"][1]))
    assert math.isclose(observation["rolling_24h_vwap_usd"], float(raw["vwap"][1]))
    assert observation["rolling_24h_trade_count"] == raw["trades"][1]
    assert observation["last_trade_usd"] < observation["best_bid_usd"]


def test_utc_day_and_rolling_24h_fields_are_not_conflated():
    observation = load_artifact()["observation"]
    assert observation["utc_day_open_usd"] == 1.20567
    assert observation["rolling_24h_vwap_usd"] == 1.25658341
    assert observation["utc_day_vwap_usd"] == 1.2156433
    assert observation["utc_day_volume_xrp"] != observation["rolling_24h_volume_xrp"]


def test_observation_remains_research_only_and_no_forecast_is_issued():
    item = load_artifact()
    assert item["model_eligible"] is False
    assert item["forecast_status"] == "NOT_ISSUED"
    assert item["data_cutoff_utc"] is None
    assert len(item["competing_hypotheses"]) == 3
    assert len(item["model_ineligibility_reasons"]) >= 5
