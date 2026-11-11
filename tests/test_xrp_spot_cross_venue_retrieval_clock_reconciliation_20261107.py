from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261107T170722Z-xrp-spot-cross-venue-retrieval-clock-reconciliation.json"
)


@pytest.fixture(scope="module")
def evidence() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _source(evidence: dict, source_id: str) -> dict:
    return next(item for item in evidence["sources"] if item["source_id"] == source_id)


def test_raw_response_hashes_reproduce_exact_browser_payloads(evidence: dict) -> None:
    for source in evidence["sources"]:
        digest = hashlib.sha256(source["raw_response_text"].encode("utf-8")).hexdigest()
        assert digest == source["raw_response_sha256"]


def test_provider_timestamps_fail_closed_at_reference_clock(evidence: dict) -> None:
    okx = _source(evidence, "okx_xrpusdt_ticker_170722z")
    binance = _source(evidence, "binance_xrpusdt_perpetual_premium_index_170722z")
    assert okx["provider_age_seconds_at_reference"] == pytest.approx(1524.736)
    assert binance["provider_age_seconds_at_reference"] == pytest.approx(877.998)
    assert okx["freshness"] == "stale_over_300_seconds"
    assert binance["freshness"] == "stale_over_300_seconds"
    assert okx["model_eligible"] is False
    assert binance["model_eligible"] is False


def test_kraken_missing_provider_event_time_is_not_filled_by_retrieval_clock(evidence: dict) -> None:
    source = _source(evidence, "kraken_xrpusd_ticker_170722z")
    assert source["provider_event_time_utc"] is None
    assert source["model_eligible"] is False
    assert "freshness cannot be certified" in source["limitations"][0]


def test_level_one_spreads_and_cross_venue_gap_recompute(evidence: dict) -> None:
    kraken = json.loads(_source(evidence, "kraken_xrpusd_ticker_170722z")["raw_response_text"])
    okx = json.loads(_source(evidence, "okx_xrpusdt_ticker_170722z")["raw_response_text"])
    k = kraken["result"]["XXRPZUSD"]
    o = okx["data"][0]
    kb, ka = float(k["b"][0]), float(k["a"][0])
    ob, oa = float(o["bidPx"]), float(o["askPx"])
    assert (ka - kb) / ((ka + kb) / 2) * 10_000 == pytest.approx(0.0861723533)
    assert (oa - ob) / ((oa + ob) / 2) * 10_000 == pytest.approx(0.8612151746)
    assert (float(o["last"]) / float(k["c"][0]) - 1) * 100 == pytest.approx(0.059461742)
    assert "not an arbitrage estimate" in evidence["calculations"]["note"]


def test_perpetual_premium_and_funding_are_not_mislabeled_as_spot_or_oi(evidence: dict) -> None:
    source = _source(evidence, "binance_xrpusdt_perpetual_premium_index_170722z")
    payload = json.loads(source["raw_response_text"])
    mark = float(payload["markPrice"])
    index = float(payload["indexPrice"])
    assert (mark / index - 1) * 10_000 == pytest.approx(-2.5757947624)
    assert float(payload["lastFundingRate"]) == pytest.approx(0.0001)
    assert "not spot price or open interest" in source["limitations"][1]


def test_repeated_retrieval_is_not_counted_as_independent_market_evidence(evidence: dict) -> None:
    repeat = evidence["retrieval_repeat"]
    assert repeat["identical_payloads"] is True
    assert repeat["independent_observation_count"] == 1
    assert "does not distinguish" in repeat["interpretation"]


def test_no_market_feature_or_directional_forecast_is_admitted(evidence: dict) -> None:
    assert all(source["model_eligible"] is False for source in evidence["sources"])
    assert evidence["model_admission"]["admitted_to_price_features"] is False
    assert evidence["model_admission"]["admitted_to_forecast_features"] is False
    assert evidence["forecast"]["status"] == "NOT_ISSUED"
    assert evidence["forecast"]["directional_forecast"] is False
