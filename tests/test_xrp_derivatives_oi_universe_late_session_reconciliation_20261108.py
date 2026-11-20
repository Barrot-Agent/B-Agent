from __future__ import annotations

import hashlib
import json
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research/xrp_intelligence/20261108T162835Z-xrp-derivatives-oi-universe-late-session-reconciliation.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_normalized_source_records_have_reproducible_hashes_not_raw_byte_claims():
    artifact = load_artifact()
    assert artifact["source_capture"]["raw_http_bytes_captured"] is False
    assert artifact["source_capture"]["raw_source_sha256_available"] is False
    for source in artifact["source_receipts"]:
        canonical = json.dumps(
            source["normalized_observation_record"],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        assert hashlib.sha256(canonical.encode("utf-8")).hexdigest() == source["normalized_record_sha256"]
        assert source["raw_http_bytes_captured"] is False
        assert source["model_eligible"] is False


def test_kodexius_contract_sum_reconciles_with_rounding_difference():
    artifact = load_artifact()
    source = artifact["source_receipts"][0]["normalized_observation_record"]
    listed = sum(source["contracts_by_exchange"].values())
    assert source["contracts"] == 7
    assert listed == 779_650_000
    assert source["open_interest_usd"] == 779_660_000
    assert abs(source["open_interest_usd"] - listed) == 10_000


def test_tradradar_exchange_sum_is_close_to_rounded_total():
    artifact = load_artifact()
    source = artifact["source_receipts"][1]["normalized_observation_record"]
    listed = sum(source["exchange_open_interest_usd"].values())
    assert listed == 1_897_440_000
    assert source["open_interest_usd"] == 1_900_000_000
    assert source["reported_delay_minutes"] == 15


def test_aggregator_open_interest_totals_are_not_averaged():
    comparison = load_artifact()["cross_provider_reconciliation"]["open_interest"]
    assert comparison["reported_total_usd"] == {
        "kodexius": 779_660_000,
        "tradradar": 1_900_000_000,
    }
    assert comparison["tradradar_to_kodexius_ratio"] == 2.4369597004
    assert comparison["do_not_average"] is True
    assert comparison["status"] == "UNRESOLVED_UNIVERSE_CONTRACT_SCOPE_AND_AGGREGATION_DIFFERENCE"


def test_binance_contract_specific_crosscheck_is_close_but_not_independent():
    comparison = load_artifact()["cross_provider_reconciliation"]["open_interest"]["same_contract_crosscheck"]
    assert comparison["instrument"] == "Binance XRPUSDT perpetual"
    assert comparison["difference_pct"] < 0.5
    assert comparison["source_time_gap_seconds"] == 5760
    assert "not independent confirmation" in comparison["interpretation"]


def test_funding_and_liquidation_denominators_remain_separate():
    comparison = load_artifact()["cross_provider_reconciliation"]
    assert comparison["funding"]["do_not_average"] is True
    assert comparison["liquidation_and_positioning"]["status"] == (
        "NOT_COMPARABLE_VENUE_COVERAGE_AND_METRIC_DENOMINATORS_DIFFER"
    )
    assert comparison["liquidation_and_positioning"]["tradradar"]["oi_venue_count"] == 7
    assert comparison["liquidation_and_positioning"]["tradradar"]["liquidation_venue_count"] == 5


def test_competing_positioning_hypotheses_retain_counterevidence():
    hypotheses = load_artifact()["competing_hypotheses"]
    assert len(hypotheses) == 4
    assert all(item["support"] and item["counterevidence"] for item in hypotheses)
    assert hypotheses[2]["status"] == "RISK_CONTEXT_ONLY_NOT_DIRECTIONAL"
    assert hypotheses[3]["status"] == "NOT_ESTABLISHED"


def test_stale_incomplete_sources_fail_closed_without_forecast():
    artifact = load_artifact()
    quality = artifact["data_quality"]
    assert quality["all_sources_exceed_freshness_limit"] is True
    assert quality["source_timestamps_synchronized"] is False
    assert quality["raw_exchange_payloads"] is False
    assert quality["contract_universe_reconciled"] is False
    assert artifact["admission"]["feature_store_admission"] == "PROHIBITED"
    assert artifact["forecast_status"] == "NOT_ISSUED"
