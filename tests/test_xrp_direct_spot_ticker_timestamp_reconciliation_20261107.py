from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261107T143554Z-xrp-direct-spot-ticker-timestamp-reconciliation.json"
)


def _load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_direct_ticker_receipts_match_exact_returned_json_hashes():
    artifact = _load()
    for source in artifact["sources"]:
        raw = source["raw_response_text"].encode("utf-8")
        assert hashlib.sha256(raw).hexdigest() == source["raw_response_sha256"]
        assert source["hash_scope"].startswith("SHA-256 of the exact JSON text")


def test_kraken_missing_event_timestamp_is_not_backfilled_from_capture_time():
    artifact = _load()
    source = artifact["sources"][0]
    assert source["publisher"] == "Kraken"
    assert source["provider_event_timestamp_utc"] is None
    assert source["freshness"] == "UNKNOWN_PROVIDER_EVENT_TIME"
    assert source["model_eligible"] is False
    assert source["normalized"]["last_usd"] == 1.16513
    assert source["normalized"]["best_bid_usd"] == 1.16526
    assert source["normalized"]["best_ask_usd"] == 1.16527


def test_okx_timestamp_age_upper_bound_fails_300_second_gate():
    artifact = _load()
    source = artifact["sources"][1]
    captured = datetime.fromisoformat(artifact["captured_at_utc"].replace("Z", "+00:00"))
    event = datetime.fromisoformat(source["provider_event_timestamp_utc"].replace("Z", "+00:00"))
    age = (captured - event).total_seconds()
    assert age == source["age_at_reference_seconds"] == 489.937
    assert source["age_is_upper_bound"] is True
    assert age > 300
    assert source["freshness"] == "STALE_GT_300_SECONDS"
    assert source["model_eligible"] is False


def test_level_one_spreads_are_reproducible_without_claiming_depth():
    artifact = _load()
    kraken, okx = artifact["sources"]
    k = kraken["normalized"]
    o = okx["normalized"]
    k_spread = (k["best_ask_usd"] - k["best_bid_usd"]) / (
        (k["best_ask_usd"] + k["best_bid_usd"]) / 2
    ) * 10000
    o_spread = (o["best_ask_usdt"] - o["best_bid_usdt"]) / (
        (o["best_ask_usdt"] + o["best_bid_usdt"]) / 2
    ) * 10000
    assert abs(k_spread - k["level1_spread_bps"]) < 0.00001
    assert abs(o_spread - o["level1_spread_bps"]) < 0.00001
    assert artifact["reconciliation"]["depth"] == "NOT_CAPTURED"


def test_cross_venue_difference_is_not_normalized_or_admitted():
    artifact = _load()
    k, o = artifact["sources"]
    difference = abs(k["normalized"]["last_usd"] - o["normalized"]["last_usdt"]) / (
        (k["normalized"]["last_usd"] + o["normalized"]["last_usdt"]) / 2
    ) * 100
    assert abs(difference - artifact["reconciliation"]["raw_last_price_difference_pct"]) < 1e-8
    assert "not normalized" in artifact["reconciliation"]["currency_basis"].lower()
    assert artifact["model_admission"]["admitted_to_live_price_features"] is False
    assert artifact["model_admission"]["admitted_to_historical_price_features"] is False


def test_no_directional_forecast_or_external_action_is_created():
    artifact = _load()
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
    assert artifact["forecast"]["directional_forecast"] is None
    assert artifact["forecast"]["shadow_or_paper_trade"] is False
    assert artifact["forecast"]["real_money_action"] is False
