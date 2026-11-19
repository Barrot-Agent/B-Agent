from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

import pytest


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261108T210243Z-xrp-kraken-okx-current-spot-quality-recheck.json"
)


@pytest.fixture(scope="module")
def record() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_exact_exchange_response_receipts_match(record: dict) -> None:
    assert len(record["sources"]) == 2
    for source in record["sources"]:
        digest = hashlib.sha256(source["raw_response_text"].encode("utf-8")).hexdigest()
        assert digest == source["raw_response_sha256"]


def test_kraken_quote_and_rolling_vwap_are_preserved(record: dict) -> None:
    source = next(x for x in record["sources"] if x["source_id"] == "kraken_xrpusd_ticker")
    fields = source["fields"]
    assert fields["last"] == pytest.approx(1.15205)
    assert fields["bid"] == pytest.approx(1.15188)
    assert fields["ask"] == pytest.approx(1.15198)
    assert fields["volume_24h_xrp"] == pytest.approx(8119513.14254243)
    assert fields["vwap_24h_usd"] == pytest.approx(1.15692676)
    assert source["event_timestamp_utc"] is None
    assert fields["rolling_24h_open_available"] is False


def test_okx_snapshot_timestamp_age_is_reproducible(record: dict) -> None:
    source = next(x for x in record["sources"] if x["source_id"] == "okx_xrpusdt_ticker")
    provider_time = datetime.fromisoformat(source["event_timestamp_utc"].replace("Z", "+00:00"))
    reference_time = datetime.fromisoformat(record["reference_time_utc"].replace("Z", "+00:00"))
    age = (reference_time - provider_time).total_seconds()
    assert age == pytest.approx(source["provider_age_at_reference_seconds"])
    assert age < source["freshness_limit_seconds"]
    assert age > 250
    assert source["live_feature_eligible"] is False
    assert "not asserted to be the last-trade event time" in source["timestamp_semantics"]


def test_usd_and_usdt_are_not_promoted_to_arbitrage(record: dict) -> None:
    kraken = next(x for x in record["sources"] if x["source_id"] == "kraken_xrpusd_ticker")
    okx = next(x for x in record["sources"] if x["source_id"] == "okx_xrpusdt_ticker")
    assert kraken["quote_currency"] == "USD"
    assert okx["quote_currency"] == "USDT"
    assert record["model_admission"]["admitted"] is False
    assert "not synchronized arbitrage observations" in record["derived"]["comparison_warning"]


def test_top_of_book_is_not_mislabeled_as_depth(record: dict) -> None:
    assert record["market_quality"]["multi_level_orderbook_depth"] is False
    assert record["market_quality"]["executable_slippage"] is False
    assert "Top-of-book sizes are not multi-level depth" in record["derived"]["level1_warning"]


def test_derivatives_retrieval_failures_do_not_create_values(record: dict) -> None:
    assert record["market_quality"]["synchronized_derivatives_open_interest"] is False
    assert record["market_quality"]["synchronized_funding"] is False
    assert len(record["retrieval_failures"]) == 3
    assert all("no " in item["interpretation"].lower() for item in record["retrieval_failures"])


def test_no_forecast_or_external_action_is_created(record: dict) -> None:
    assert record["forecast"]["status"] == "NOT_ISSUED"
    assert record["forecast"]["directional_forecast"] is False
    assert record["forecast"]["shadow_forecast"] is False
    assert record["forecast"]["paper_trade"] is False
    assert record["forecast"]["real_money_action"] is False
    assert record["external_actions"]["repository_main_write"] is False
    assert record["external_actions"]["deployment"] is False
