from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261107T083302Z-xrp-direct-spot-freshness-reconciliation.json"


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_raw_exchange_receipts_match_exact_stored_json_text() -> None:
    data = load_artifact()
    assert data["source_receipt_contract"]["hash_algorithm"] == "SHA-256"
    for source in data["sources"]:
        raw = source["raw_response_exact_json"].encode("utf-8")
        assert len(raw) == source["raw_response_bytes"]
        assert hashlib.sha256(raw).hexdigest() == source["raw_response_sha256"]


def test_kraken_missing_provider_timestamp_is_not_fabricated() -> None:
    data = load_artifact()
    kraken = next(item for item in data["sources"] if item["publisher"] == "Kraken")
    assert kraken["provider_event_timestamp_utc"] is None
    assert kraken["freshness_status"] == "UNVERIFIABLE_PROVIDER_TIMESTAMP_MISSING"
    assert "retrieval time cannot prove source freshness" in " ".join(kraken["limitations"])


def test_okx_provider_timestamp_is_parsed_and_fresh_at_capture() -> None:
    data = load_artifact()
    okx = next(item for item in data["sources"] if item["publisher"] == "OKX")
    capture = datetime.fromisoformat(data["captured_at_utc"].replace("Z", "+00:00"))
    provider = datetime.fromisoformat(okx["provider_event_timestamp_utc"].replace("Z", "+00:00"))
    assert (capture - provider).total_seconds() == okx["provider_event_age_seconds_at_capture"]
    assert okx["provider_event_age_seconds_at_capture"] <= okx["freshness_limit_seconds"]
    assert okx["freshness_status"] == "FRESH_WITHIN_300_SECOND_LIMIT"


def test_level_one_spreads_recompute_from_bid_and_ask() -> None:
    data = load_artifact()
    kraken, okx = data["sources"]
    for source, currency in ((kraken, "usd"), (okx, "usdt")):
        metrics = source["normalized_metrics"]
        bid = metrics[f"best_bid_{currency}"]
        ask = metrics[f"best_ask_{currency}"]
        expected = (ask - bid) / ((ask + bid) / 2.0) * 10_000
        assert abs(expected - metrics["level1_spread_bps"]) < 1e-8


def test_cross_venue_gap_is_not_promoted_to_arbitrage() -> None:
    data = load_artifact()
    derived = data["derived_reconciliation"]
    kraken, okx = data["sources"]
    expected = (
        okx["normalized_metrics"]["last_usdt"]
        / kraken["normalized_metrics"]["last_usd"]
        - 1.0
    ) * 100
    assert abs(expected - derived["raw_cross_venue_last_price_gap_pct"]) < 1e-8
    assert "not an executable arbitrage observation" in derived["interpretation"]
    assert "USDT is not silently treated as USD" in " ".join(okx["limitations"])


def test_okx_snapshot_change_is_timestamp_bounded_not_a_candle_return() -> None:
    data = load_artifact()
    prior = data["derived_reconciliation"]["prior_okx_snapshot"]
    current = data["derived_reconciliation"]["current_okx_snapshot"]
    prior_time = datetime.fromisoformat(prior["provider_event_timestamp_utc"].replace("Z", "+00:00"))
    current_time = datetime.fromisoformat(current["provider_event_timestamp_utc"].replace("Z", "+00:00"))
    expected_interval = (current_time - prior_time).total_seconds()
    expected_change = (current["last_usdt"] / prior["last_usdt"] - 1.0) * 100
    derived = data["derived_reconciliation"]
    assert expected_interval == derived["okx_snapshot_interval_seconds"]
    assert abs(expected_change - derived["okx_snapshot_to_snapshot_change_pct"]) < 1e-8
    assert "not a continuous candle return" in derived["interpretation"]


def test_ticker_data_does_not_claim_multi_level_depth() -> None:
    data = load_artifact()
    assert all(
        "not a multi-level order-book depth ladder" in " ".join(source["limitations"])
        for source in data["sources"]
    )
    assert data["model_admission"]["admitted_feature_count"] == 0


def test_observations_remain_model_ineligible_and_forecast_is_not_issued() -> None:
    data = load_artifact()
    assert data["model_admission"]["eligible"] is False
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["forecast"]["directional_forecast"] is None
    assert data["forecast"]["shadow_forecast"] is None


def test_no_order_or_external_financial_action_occurred() -> None:
    data = load_artifact()
    assert all(value is False for value in data["external_actions"].values())
    assert data["forecast"]["paper_trade_executed"] is False
    assert data["forecast"]["real_money_action"] is False
