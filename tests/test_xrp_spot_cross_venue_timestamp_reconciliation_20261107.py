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
    / "20261107T070318Z-xrp-spot-cross-venue-timestamp-reconciliation.json"
)


@pytest.fixture(scope="module")
def record() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_direct_exchange_receipts_match_exact_stored_text(record: dict) -> None:
    assert len(record["sources"]) == 2
    for source in record["sources"]:
        digest = hashlib.sha256(source["raw_response_text"].encode("utf-8")).hexdigest()
        assert digest == source["raw_response_sha256"]


def test_spot_spreads_and_cross_venue_gap_are_reproducible(record: dict) -> None:
    kraken = next(x for x in record["sources"] if x["source_id"] == "kraken_xrpusd_ticker")
    okx = next(x for x in record["sources"] if x["source_id"] == "okx_xrpusdt_ticker")
    k, o = kraken["fields"], okx["fields"]
    k_spread = (k["ask"] - k["bid"]) / ((k["ask"] + k["bid"]) / 2) * 10_000
    o_spread = (o["ask"] - o["bid"]) / ((o["ask"] + o["bid"]) / 2) * 10_000
    gap = (o["last"] / k["last"] - 1) * 100
    assert k_spread == pytest.approx(record["derived"]["kraken_level1_spread_bps"])
    assert o_spread == pytest.approx(record["derived"]["okx_level1_spread_bps"])
    assert gap == pytest.approx(record["derived"]["raw_last_price_difference_percent_kraken_vs_okx"])
    assert k["vwap_24h_usd"] == pytest.approx(1.17916231)
    assert o["open_24h_usdt"] == pytest.approx(1.1923)


def test_okx_timestamp_age_fails_live_feature_freshness(record: dict) -> None:
    source = next(x for x in record["sources"] if x["source_id"] == "okx_xrpusdt_ticker")
    provider_time = datetime.fromisoformat(source["event_timestamp_utc"].replace("Z", "+00:00"))
    reference_time = datetime.fromisoformat(record["reference_at_utc"].replace("Z", "+00:00"))
    age = (reference_time - provider_time).total_seconds()
    assert age == pytest.approx(source["provider_age_at_reference_seconds"])
    assert age > source["freshness_limit_seconds"]
    assert source["live_feature_eligible"] is False


def test_kraken_without_provider_timestamp_is_not_live_eligible(record: dict) -> None:
    source = next(x for x in record["sources"] if x["source_id"] == "kraken_xrpusd_ticker")
    assert source["event_timestamp_utc"] is None
    assert source["live_feature_eligible"] is False


def test_okx_snapshot_delta_is_descriptive_not_a_continuous_return(record: dict) -> None:
    derived = record["derived"]
    change = (1.169 / 1.1607 - 1) * 100
    assert change == pytest.approx(derived["okx_snapshot_to_snapshot_last_price_change_percent"])
    assert derived["okx_snapshot_interval_seconds"] == pytest.approx(3759.533)
    assert "not a continuous trade return" in derived["same_venue_change_warning"]


def test_etf_zero_flow_retains_feed_lineage_and_limits(record: dict) -> None:
    source = next(x for x in record["secondary_sources"] if x["source_id"] == "alpha_finance_xrp_etf_flows")
    assert source["reported"]["funds_covered"] == 5
    assert source["reported"]["latest_session_net_flow_usd"] == 0
    assert source["source_group"] == "aggregator_coinglass_feed"
    assert any("not a direct issuer" in x for x in source["methodology_and_limits"])
    assert source["model_eligible"] is False


def test_binance_outflow_keeps_internal_transfer_counterhypothesis(record: dict) -> None:
    source = next(x for x in record["secondary_sources"] if x["source_id"] == "cryptoquant_binance_xrp_outflow_darkfost")
    assert source["reported"]["xrp_outflow"] == 418_500_000
    assert any("internal transfers" in x for x in source["limitations"])
    assert any("not proof of net accumulation" in x for x in source["limitations"])
    assert source["model_eligible"] is False


def test_liquidation_clusters_are_modelled_not_actual_resting_orders(record: dict) -> None:
    source = next(x for x in record["secondary_sources"] if x["source_id"] == "alpha_finance_xrp_liquidation_heatmap")
    assert source["reported"]["modelled_short_liquidity_above_usd"] == 90_600_000
    assert source["reported"]["modelled_long_liquidity_below_usd"] == 29_900_000
    assert any("not actual resting liquidation orders" in x for x in source["methodology_and_limits"])
    assert source["model_eligible"] is False


def test_all_sources_remain_model_ineligible_and_no_forecast_is_issued(record: dict) -> None:
    assert record["model_admission"]["admitted"] is False
    assert all(source["live_feature_eligible"] is False for source in record["sources"])
    assert all(source["model_eligible"] is False for source in record["secondary_sources"])
    assert record["forecast"]["status"] == "NOT_ISSUED"
    assert record["forecast"]["directional_forecast"] is False
    assert record["forecast"]["shadow_forecast"] is False
    assert record["forecast"]["paper_trade"] is False
    assert record["forecast"]["real_money_action"] is False
