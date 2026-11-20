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
    / "20261107T060301Z-xrp-spot-venue-timestamp-reconciliation.json"
)


@pytest.fixture(scope="module")
def record() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_raw_response_receipts_match_exact_stored_text(record: dict) -> None:
    assert len(record["sources"]) == 2
    for source in record["sources"]:
        digest = hashlib.sha256(
            source["raw_response_text"].encode("utf-8")
        ).hexdigest()
        assert digest == source["raw_response_sha256"]


def test_kraken_spot_quote_arithmetic_is_reproducible(record: dict) -> None:
    source = next(x for x in record["sources"] if x["source_id"] == "kraken_xrpusd_ticker")
    fields = source["fields"]
    spread = (fields["ask"] - fields["bid"]) / (
        (fields["ask"] + fields["bid"]) / 2
    ) * 10_000
    assert spread == pytest.approx(record["derived"]["kraken_level1_spread_bps"])
    assert fields["last"] == pytest.approx(1.16095)
    assert fields["vwap_24h_usd"] == pytest.approx(1.18007852)
    assert source["event_timestamp_utc"] is None


def test_okx_snapshot_timestamp_is_stale_and_not_last_trade_time(record: dict) -> None:
    source = next(x for x in record["sources"] if x["source_id"] == "okx_xrpusdt_ticker")
    provider_time = datetime.fromisoformat(source["event_timestamp_utc"].replace("Z", "+00:00"))
    reference_time = datetime.fromisoformat(record["reference_at_utc"].replace("Z", "+00:00"))
    age = (reference_time - provider_time).total_seconds()
    assert age == pytest.approx(source["provider_age_at_reference_seconds"])
    assert age > source["freshness_limit_seconds"]
    assert source["live_feature_eligible"] is False
    assert "not asserted to be the last-trade event time" in source["timestamp_semantics"]


def test_usd_and_usdt_quotes_are_not_promoted_to_arbitrage(record: dict) -> None:
    kraken = next(x for x in record["sources"] if x["source_id"] == "kraken_xrpusd_ticker")
    okx = next(x for x in record["sources"] if x["source_id"] == "okx_xrpusdt_ticker")
    assert kraken["quote_currency"] == "USD"
    assert okx["quote_currency"] == "USDT"
    assert record["model_admission"]["admitted"] is False
    assert "not an arbitrage observation" in record["derived"]["comparison_warning"]


def test_no_forecast_or_external_action_is_created(record: dict) -> None:
    assert record["forecast"]["status"] == "NOT_ISSUED"
    assert record["forecast"]["directional_forecast"] is False
    assert record["forecast"]["shadow_forecast"] is False
    assert record["forecast"]["paper_trade"] is False
    assert record["forecast"]["real_money_action"] is False
