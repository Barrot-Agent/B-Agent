from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261108T212130Z-derivatives-aggregator-vintage-reconciliation.json"
PRIOR_ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261108T211453Z-binance-hack-xrp-flow-derivatives-cross-ledger-reconciliation.json"


@pytest.fixture(scope="module")
def record() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_append_only_vintage_correction_preserves_prior_artifact(record: dict) -> None:
    assert PRIOR_ARTIFACT.is_file()
    assert record["append_only"] is True
    assert record["prior_artifact"].endswith("20261108T211453Z-binance-hack-xrp-flow-derivatives-cross-ledger-reconciliation.json")


def test_source_receipts_match_hashes_and_short_excerpt_limits(record: dict) -> None:
    receipts = record["source_receipts"]
    assert len(receipts) >= 8
    for receipt in receipts:
        assert hashlib.sha256(receipt["excerpt"].encode("utf-8")).hexdigest() == receipt["sha256"]
        assert len(receipt["excerpt"].split()) <= 25


def test_coingecko_same_publisher_search_and_page_disagreement_is_preserved(record: dict) -> None:
    facts = record["observations"]
    search = facts["coingecko_prior_search_snippet"]
    page = facts["coingecko_open_page"]
    assert search["open_interest_usd"] == 4_075_989_283
    assert page["open_interest_usd"] == 4_012_752_818
    assert search["derivative_volume_24h_usd"] == 15_232_986_467
    assert page["derivative_volume_24h_usd"] == 3_557_251_198
    assert record["source_independence"]["same_publisher"].startswith("CoinGecko search snippet")
    assert record["retrieval_vintage_disagreement"]["perps_to_spot_ratio_search_vs_page"] == [15.3, 4.0]


def test_tradradar_current_page_vintage_and_delay_are_explicit(record: dict) -> None:
    facts = record["observations"]["tradradar"]
    assert facts["open_interest_usd"] == 1_890_000_000
    assert facts["funding_rate_8h_pct"] == pytest.approx(0.0086)
    assert facts["long_short_ratio"] == pytest.approx(3.97)
    assert facts["long_account_share_pct"] == pytest.approx(79.9)
    assert facts["updated_at_utc"] == "2026-11-08T20:00:00Z"
    assert facts["stated_delay_minutes"] == 15


def test_kodexius_page_values_and_stale_update_time_are_preserved(record: dict) -> None:
    facts = record["observations"]["kodexius"]
    assert facts["open_interest_usd"] == 779_660_000
    assert facts["funding_rate_8h_pct"] == pytest.approx(0.0061)
    assert facts["volume_24h_usd"] == 666_190_000
    assert facts["contracts"] == 7
    assert facts["updated_at_utc"] == "2026-11-08T14:19:00Z"


def test_optimistfi_october_snapshot_is_excluded_as_stale(record: dict) -> None:
    facts = record["observations"]["optimistfi"]
    assert facts["open_interest_usd"] == 1_600_000_000
    assert facts["venues"] == 36
    assert facts["provider_timestamp_utc"] == "2026-10-24T02:07:00Z"
    assert facts["freshness"].startswith("STALE")
    assert "OptimistFi" in record["current_page_dispersion"]["excluded_stale_providers"]


def test_current_oi_provider_dispersion_is_not_averaged(record: dict) -> None:
    facts = record["current_page_dispersion"]
    assert facts["maximum_open_interest_usd"] == 4_012_752_818
    assert facts["minimum_open_interest_usd"] == 779_660_000
    assert facts["max_to_min_ratio"] == pytest.approx(5.146798371)
    assert "no combined OI or funding feature is defensible" in facts["conclusion"]


def test_funding_observations_remain_provider_specific(record: dict) -> None:
    facts = record["current_page_dispersion"]["funding_observations_8h_pct"]
    assert facts == {"CoinGecko": 0.0092, "TradRadar": 0.0086, "Kodexius": 0.0061}
    assert "different venue and contract universes" in record["source_independence"]["aggregators"]


def test_repeated_spot_payloads_are_not_called_live_updates(record: dict) -> None:
    facts = record["spot_retrieval_quality"]
    assert facts["kraken_payload_identical_to_21_02_capture"] is True
    assert facts["okx_payload_identical_to_21_02_capture"] is True
    assert facts["okx_age_seconds_at_21_12_retrieval"] == 892
    assert facts["kraken_provider_event_time_available"] is False
    assert "not a fresh 21:12 market update" in facts["conclusion"]


def test_no_derivatives_feature_or_directional_forecast_is_admitted(record: dict) -> None:
    assert all(value is False for value in record["market_admission"].values() if isinstance(value, bool))
    assert record["forecast"]["status"] == "NOT_ISSUED"
    assert record["forecast"]["directional_forecast"] is False
    assert record["forecast"]["paper_trade"] is False
    assert record["forecast"]["real_money_action"] is False
    assert record["external_actions"]["main_write"] is False
    assert record["external_actions"]["deployment"] is False
