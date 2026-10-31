import datetime as dt
import json
from decimal import Decimal

import pytest

from scripts import ingest_morpho_cbxrp as ingest


def _fixtures():
    return {
        "market_list": ({"data": {"items": [{"market_id": ingest.MARKET_ID}]}}, 200),
        "market": ({"data": {
            "chain_id": 8453,
            "loan_token": {"address": ingest.USDC_ADDRESS},
            "collateral_token": {"address": ingest.CBXRP_ADDRESS},
            "oracle_address": "0x1111111111111111111111111111111111111111",
            "lltv_wad": "625000000000000000",
        }}, 200),
        "market_liquidity": ({"data": {"available_liquidity": "250"}}, 200),
        "state": ({"data": {
            "total_supply_assets": "1000",
            "total_borrow_assets": "750",
            "total_supply_shares": "900",
            "total_borrow_shares": "700",
        }}, 200),
        "apy_averages": ({"data": {"supply_apy_averages": {"24h": 0.04}, "borrow_apy_averages": {"24h": 0.06}}}, 200),
        "state_history": ({"data": [{"timestamp": "2026-10-31T03:00:00Z"}]}, 200),
        "apy_history": ({"data": [{"timestamp": "2026-10-31T03:00:00Z"}]}, 200),
        "cbxrp_price": ({"data": {"price": "1.25", "timestamp": "1793410000", "provider": "test"}}, 200),
        "usdc_price": ({"data": {"price": "1.0", "timestamp": "1793410000", "provider": "test"}}, 200),
    }


def test_build_request_urls_uses_exact_base_market_and_tokens():
    urls = ingest.build_request_urls()
    assert f"{ingest.CHAIN_ID}:{ingest.MARKET_ID}" in urls["market"]
    assert ingest.CBXRP_ADDRESS.lower() in urls["market_list"].lower()
    assert ingest.USDC_ADDRESS.lower() in urls["market_list"].lower()
    assert "lookback=thirty_days" in urls["state_history"]
    assert urls["market_liquidity"].endswith("/liquidity")
    assert "lookback=thirty_days" in urls["apy_history"]


def test_collect_snapshot_derives_utilization_from_raw_assets_and_never_admits_features():
    fixtures = _fixtures()
    calls = []

    def fake_fetch(url):
        calls.append(url)
        if "/oracles/" in url:
            return ({"data": {"price": "1250550000000000000", "last_updated_at": "2026-10-31T04:00:00Z", "last_indexed_block": 123}}, 200)
        for key, value in fixtures.items():
            if key == "market_list" and "/v1/blue/markets?" in url:
                return value
            if key != "market_list" and url == ingest.build_request_urls()[key]:
                return value
        raise AssertionError(f"unexpected URL: {url}")

    snap = ingest.collect_snapshot(fake_fetch, dt.datetime(2026, 10, 31, 4, 10, tzinfo=dt.timezone.utc))
    normalized = snap["normalized_market"]
    assert Decimal(normalized["utilization_from_raw_assets"]) == Decimal("0.75")
    assert Decimal(normalized["available_liquidity_assets_raw"]) == Decimal("250")
    assert normalized["lltv_fraction"] == "0.625"
    assert snap["status"] == "COMPLETE"
    assert snap["market_features_admitted"] is False
    assert len(calls) == 10


def test_rate_limit_is_recorded_without_retry_or_further_requests():
    fixtures = _fixtures()
    calls = []

    def fake_fetch(url):
        calls.append(url)
        if len(calls) == 2:
            raise ingest.ProviderHTTPError(429, "600", "rate limited")
        if "/v1/blue/markets?" in url:
            return fixtures["market_list"]
        raise AssertionError("request after rate limit should not occur")

    snap = ingest.collect_snapshot(fake_fetch, dt.datetime(2026, 10, 31, 4, 10, tzinfo=dt.timezone.utc))
    assert snap["status"] == "PARTIAL_RATE_LIMITED"
    assert snap["market_features_admitted"] is False
    assert len(calls) == 2
    assert snap["errors"][0]["retry_after"] == "600"


def test_inconsistent_supply_borrow_state_is_flagged():
    fixtures = _fixtures()
    fixtures["state"] = ({"data": {"total_supply_assets": "100", "total_borrow_assets": "101"}}, 200)

    def fake_fetch(url):
        if "/oracles/" in url:
            return ({"data": {"last_updated_at": "2026-10-31T04:00:00Z"}}, 200)
        for key, value in fixtures.items():
            if key == "market_list" and "/v1/blue/markets?" in url:
                return value
            if key != "market_list" and url == ingest.build_request_urls()[key]:
                return value
        raise AssertionError(f"unexpected URL: {url}")

    snap = ingest.collect_snapshot(fake_fetch, dt.datetime(2026, 10, 31, 4, 10, tzinfo=dt.timezone.utc))
    assert "BORROW_EXCEEDS_SUPPLY" in snap["data_quality_flags"]
    assert snap["market_features_admitted"] is False


def test_missing_or_stale_oracle_is_flagged():
    fixtures = _fixtures()

    def fake_fetch(url):
        if "/oracles/" in url:
            return ({"data": {"last_updated_at": "2026-10-29T00:00:00Z"}}, 200)
        for key, value in fixtures.items():
            if key == "market_list" and "/v1/blue/markets?" in url:
                return value
            if key != "market_list" and url == ingest.build_request_urls()[key]:
                return value
        raise AssertionError(f"unexpected URL: {url}")

    snap = ingest.collect_snapshot(fake_fetch, dt.datetime(2026, 10, 31, 4, 10, tzinfo=dt.timezone.utc))
    assert "ORACLE_STALE_OVER_24H" in snap["data_quality_flags"]
    assert snap["status"] == "PARTIAL"
