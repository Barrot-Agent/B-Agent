import json
import math
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Barrier
from types import SimpleNamespace

import pytest
import barrot_agent.research.fixed_horizon as fixed_horizon

from barrot_agent.research.fixed_horizon import ForecastLedger, _append_jsonl
from barrot_agent.sources.source_registry import (
    SourceIdentity, SourceRecord, SourceRegistry, SourceVersion, register_file_source,
)


TEST_SOURCE_REGISTRY = {
    "SRC-MARKET-001": "b" * 64,
    "SRC-PRICE-001": "c" * 64,
    "SRC-FEATURE-001": "a" * 64,
    "SRC-REPLAY-MANIFEST-001": "e" * 64,
}


class HashVerifiedRegistryFixture:
    """Test double for the byte-verifying registry interface."""

    def __init__(self, entries):
        self.entries = dict(entries)

    def require(self, source_id):
        if source_id not in self.entries:
            raise KeyError(source_id)
        return SimpleNamespace(
            version=SimpleNamespace(content_hash=self.entries[source_id]),
            lifecycle=SimpleNamespace(state="ACTIVE", inaccessible=False, revalidation_required=False),
        )

    def verify_content_hash(self, source_id, content=None):
        value = self.entries.get(source_id)
        return (
            source_id in self.entries
            and isinstance(value, str)
            and len(value) == 64
            and all(char in "0123456789abcdef" for char in value.lower())
        )


def make_file_backed_registry(root):
    registry = SourceRegistry(root / "registry.json")
    paths = {}
    hashes = {}
    for source_id in TEST_SOURCE_REGISTRY:
        path = root / "snapshots" / f"{source_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"snapshot:{source_id}", encoding="utf-8")
        record = register_file_source(
            registry,
            source_id=source_id,
            source_type="test_snapshot",
            name=source_id,
            origin="unit-test",
            path=path,
        )
        paths[source_id] = path
        hashes[source_id] = record.version.content_hash
    return registry, hashes, paths


def make_ledger(root, **kwargs):
    kwargs.setdefault("source_registry", HashVerifiedRegistryFixture(TEST_SOURCE_REGISTRY))
    return ForecastLedger(root, **kwargs)


def forecast_payload(**overrides):
    payload = {
        "forecast_id": "xrp-forecast-001",
        "asset_pair": "XRP/USD",
        "mode": "HISTORICAL_REPLAY",
        "replay_manifest_source_id": "SRC-REPLAY-MANIFEST-001",
        "issued_at_utc": "2026-10-31T00:00:00Z",
        "data_cutoff_utc": "2026-10-30T23:59:00Z",
        "horizon_seconds": 3600,
        "target": {
            "name": "xrp_usd_return_class_v1",
            "up_threshold_pct": 0.5,
            "down_threshold_pct": -0.5,
        },
        "probabilities": {"up": 0.6, "flat": 0.25, "down": 0.15},
        "assumptions": ["The point-in-time feature snapshot is complete."],
        "alternatives": ["The market remains range-bound."],
        "model": {"name": "barrot-xrp", "version": "0.1.0"},
        "feature_snapshot": {
            "snapshot_id": "features-001",
            "source_id": "SRC-FEATURE-001",
            "sha256": "a" * 64,
            "captured_at_utc": "2026-10-30T23:58:00Z",
        },
        "baseline": {
            "id": "uniform-v1",
            "trained_through_utc": "2026-10-30T23:59:00Z",
            "computed_at_utc": "2026-10-30T23:59:00Z",
            "probabilities": {"up": 1 / 3, "flat": 1 / 3, "down": 1 / 3},
        },
        "source_ids": ["SRC-MARKET-001", "SRC-FEATURE-001", "SRC-REPLAY-MANIFEST-001"],
        "price_at_issue_usd": 1.25,
        "price_at_issue_source_id": "SRC-MARKET-001",
        "price_at_issue_observed_at_utc": "2026-10-30T23:59:00Z",
    }
    payload.update(overrides)
    return payload


def test_forecast_is_appended_with_fixed_target_and_computed_confidence(tmp_path):
    ledger = make_ledger(tmp_path)
    record = ledger.append_forecast(forecast_payload())
    assert record["record_type"] == "xrp_forecast"
    assert record["horizon_seconds"] == 3600
    assert record["target_end_at_utc"] == "2026-10-31T01:00:00Z"
    assert record["confidence"] == pytest.approx(0.6)
    assert record["status"] == "OPEN"
    assert len(ledger.forecasts()) == 1
    assert ledger.outcomes() == []


def test_forecast_rejects_data_cutoff_after_issue_time(tmp_path):
    ledger = make_ledger(tmp_path)
    with pytest.raises(ValueError, match="data_cutoff_utc"):
        ledger.append_forecast(forecast_payload(data_cutoff_utc="2026-10-31T00:01:00Z"))


def test_forecast_rejects_feature_snapshot_after_data_cutoff(tmp_path):
    ledger = make_ledger(tmp_path)
    payload = forecast_payload()
    payload["feature_snapshot"]["captured_at_utc"] = "2026-10-31T00:00:01Z"
    with pytest.raises(ValueError, match="feature snapshot"):
        ledger.append_forecast(payload)


def test_forecast_rejects_baseline_trained_after_data_cutoff(tmp_path):
    ledger = make_ledger(tmp_path)
    payload = forecast_payload()
    payload["baseline"]["trained_through_utc"] = "2026-10-31T00:00:01Z"
    with pytest.raises(ValueError, match="baseline"):
        ledger.append_forecast(payload)


def test_forecast_rejects_baseline_trained_after_computation(tmp_path):
    ledger = make_ledger(tmp_path)
    payload = forecast_payload()
    payload["baseline"]["trained_through_utc"] = "2026-10-30T23:58:30Z"
    payload["baseline"]["computed_at_utc"] = "2026-10-30T23:58:00Z"
    with pytest.raises(ValueError, match="trained through a time later"):
        ledger.append_forecast(payload)


def test_forecast_rejects_baseline_computed_after_issue_time(tmp_path):
    ledger = make_ledger(tmp_path)
    payload = forecast_payload()
    payload["baseline"]["computed_at_utc"] = "2026-10-31T00:00:01Z"
    with pytest.raises(ValueError, match="baseline must be computed"):
        ledger.append_forecast(payload)


def test_forecast_rejects_issue_price_observed_after_cutoff(tmp_path):
    ledger = make_ledger(tmp_path)
    payload = forecast_payload(price_at_issue_observed_at_utc="2026-10-31T00:00:01Z")
    with pytest.raises(ValueError, match="issue price observation"):
        ledger.append_forecast(payload)


def test_forecast_requires_issue_price_source_in_source_registry(tmp_path):
    ledger = make_ledger(tmp_path)
    payload = forecast_payload(price_at_issue_source_id="SRC-UNREGISTERED")
    with pytest.raises(ValueError, match="included in source_ids"):
        ledger.append_forecast(payload)


def test_observation_lag_must_be_an_integer(tmp_path):
    with pytest.raises(ValueError, match="positive integer"):
        make_ledger(tmp_path, max_observation_lag_seconds=1.5)


def test_forecast_rejects_invalid_probability_distribution(tmp_path):
    ledger = make_ledger(tmp_path)
    payload = forecast_payload(probabilities={"up": 0.6, "flat": 0.2, "down": 0.1})
    with pytest.raises(ValueError, match="sum to one"):
        ledger.append_forecast(payload)


def test_forecast_rejects_timezone_naive_timestamps(tmp_path):
    ledger = make_ledger(tmp_path)
    with pytest.raises(ValueError, match="timezone"):
        ledger.append_forecast(forecast_payload(issued_at_utc="2026-10-31T00:00:00"))


def test_forecast_rejects_duplicate_ids(tmp_path):
    ledger = make_ledger(tmp_path)
    ledger.append_forecast(forecast_payload())
    with pytest.raises(ValueError, match="already exists"):
        ledger.append_forecast(forecast_payload())


def test_outcome_uses_latest_observation_at_or_before_fixed_horizon(tmp_path):
    ledger = make_ledger(tmp_path)
    forecast = ledger.append_forecast(forecast_payload())
    assert forecast["target_resolution_policy"] == "LATEST_OBSERVATION_AT_OR_BEFORE_HORIZON"
    assert forecast["max_pre_horizon_observation_lag_seconds"] == 120
    outcome = ledger.append_outcome(
        "xrp-forecast-001", 1.27, "2026-10-31T00:59:59Z",
        "2026-10-31T01:00:10Z", "SRC-PRICE-001"
    )
    assert outcome["target_resolution_policy"] == "LATEST_OBSERVATION_AT_OR_BEFORE_HORIZON"
    assert outcome["effective_horizon_seconds"] == pytest.approx(3599.0)
    assert outcome["observation_lag_seconds"] == pytest.approx(1.0)


def test_outcome_price_after_horizon_is_rejected(tmp_path):
    ledger = make_ledger(tmp_path)
    ledger.append_forecast(forecast_payload())
    with pytest.raises(ValueError, match="cannot be after the fixed horizon"):
        ledger.append_outcome(
            "xrp-forecast-001", 1.27, "2026-10-31T01:00:01Z",
            "2026-10-31T01:01:00Z", "SRC-PRICE-001"
        )


def test_outcome_recorded_before_horizon_is_rejected(tmp_path):
    ledger = make_ledger(tmp_path)
    ledger.append_forecast(forecast_payload())
    with pytest.raises(ValueError, match="cannot precede the fixed horizon"):
        ledger.append_outcome(
            "xrp-forecast-001", 1.27, "2026-10-31T00:59:59Z",
            "2026-10-31T00:59:59Z", "SRC-PRICE-001"
        )


def test_outcome_observation_cannot_precede_forecast_issuance(tmp_path):
    ledger = make_ledger(tmp_path)
    ledger.append_forecast(forecast_payload(horizon_seconds=300))
    with pytest.raises(ValueError, match="cannot precede forecast issuance"):
        ledger.append_outcome(
            "xrp-forecast-001", 1.27, "2026-10-30T23:59:59Z",
            "2026-10-31T00:05:00Z", "SRC-PRICE-001"
        )


def test_outcome_rejects_price_observation_outside_lag_window(tmp_path):
    ledger = make_ledger(tmp_path, max_observation_lag_seconds=60)
    ledger.append_forecast(forecast_payload())
    with pytest.raises(ValueError, match="maximum pre-horizon observation lag"):
        ledger.append_outcome(
            "xrp-forecast-001", 1.27, "2026-10-31T00:58:59Z",
            "2026-10-31T01:03:00Z", "SRC-PRICE-001"
        )


def test_outcome_is_separate_and_does_not_mutate_forecast(tmp_path):
    ledger = make_ledger(tmp_path)
    ledger.append_forecast(forecast_payload())
    original_forecasts = ledger.forecasts_path.read_bytes()
    outcome = ledger.append_outcome(
        "xrp-forecast-001", 1.27, "2026-10-31T00:59:30Z",
        "2026-10-31T01:01:00Z", "SRC-PRICE-001"
    )
    assert outcome["realized_class"] == "up"
    assert outcome["realized_return_pct"] == pytest.approx(1.6)
    assert ledger.forecasts_path.read_bytes() == original_forecasts
    assert len(ledger.outcomes()) == 1


def test_duplicate_outcome_is_rejected(tmp_path):
    ledger = make_ledger(tmp_path)
    ledger.append_forecast(forecast_payload())
    ledger.append_outcome(
        "xrp-forecast-001", 1.27, "2026-10-31T00:59:30Z",
        "2026-10-31T01:01:00Z", "SRC-PRICE-001"
    )
    with pytest.raises(ValueError, match="already exists"):
        ledger.append_outcome(
            "xrp-forecast-001", 1.28, "2026-10-31T00:59:40Z",
            "2026-10-31T01:02:00Z", "SRC-PRICE-002"
        )


def test_metrics_report_brier_log_loss_baseline_and_calibration(tmp_path):
    ledger = make_ledger(tmp_path)
    ledger.append_forecast(forecast_payload())
    ledger.append_outcome(
        "xrp-forecast-001", 1.27, "2026-10-31T00:59:30Z",
        "2026-10-31T01:01:00Z", "SRC-PRICE-001"
    )
    metrics = ledger.metrics()
    assert metrics["resolved_count"] == 1
    assert metrics["pending_count"] == 0
    assert metrics["accuracy"] == 1.0
    assert metrics["mean_brier_score"] == pytest.approx(0.245)
    assert metrics["mean_log_loss"] == pytest.approx(-math.log(0.6))
    assert metrics["mean_baseline_brier_score"] == pytest.approx(2 / 3)
    assert metrics["brier_skill_score"] > 0
    assert metrics["top_label_calibration_bins"][0]["count"] == 1
    assert metrics["performance_claim_status"] == "DESCRIPTIVE_ONLY_NO_MODEL_SKILL_CLAIM"
    assert metrics["walk_forward_baseline_status"] == "NOT_IMPLEMENTED_STORED_BASELINE_CUTOFF_CHECKED"


def test_metrics_do_not_claim_skill_without_resolved_outcomes(tmp_path):
    ledger = make_ledger(tmp_path)
    ledger.append_forecast(forecast_payload())
    metrics = ledger.metrics()
    assert metrics["resolved_count"] == 0
    assert metrics["pending_count"] == 1
    assert metrics["mean_brier_score"] is None
    assert metrics["performance_claim_status"] == "NOT_AUTHORIZED"


def test_invalid_feature_snapshot_hash_is_rejected(tmp_path):
    ledger = make_ledger(tmp_path)
    payload = forecast_payload()
    payload["feature_snapshot"]["sha256"] = "not-a-hash"
    with pytest.raises(ValueError, match="SHA-256"):
        ledger.append_forecast(payload)


def test_outcome_requires_a_price_source_id(tmp_path):
    ledger = make_ledger(tmp_path)
    ledger.append_forecast(forecast_payload())
    with pytest.raises(ValueError, match="price_source_id"):
        ledger.append_outcome(
            "xrp-forecast-001", 1.27, "2026-10-31T00:59:30Z",
            "2026-10-31T01:01:00Z", ""
        )


def test_forecast_rejects_stale_issue_price_observation(tmp_path):
    ledger = make_ledger(tmp_path)
    payload = forecast_payload(price_at_issue_observed_at_utc="2026-10-30T23:57:59Z")
    with pytest.raises(ValueError, match="freshness window"):
        ledger.append_forecast(payload)


def test_forecast_accepts_issue_price_at_freshness_boundary(tmp_path):
    ledger = make_ledger(tmp_path)
    payload = forecast_payload(price_at_issue_observed_at_utc="2026-10-30T23:58:00Z")
    record = ledger.append_forecast(payload)
    assert record["price_at_issue_max_observation_lag_seconds"] == 120


def test_forecast_rejects_duplicate_source_ids(tmp_path):
    ledger = make_ledger(tmp_path)
    payload = forecast_payload(source_ids=["SRC-MARKET-001", "SRC-MARKET-001"])
    with pytest.raises(ValueError, match="source_ids must be unique"):
        ledger.append_forecast(payload)


def test_issue_price_freshness_lag_must_be_a_positive_integer(tmp_path):
    with pytest.raises(ValueError, match="max_issue_price_lag_seconds"):
        make_ledger(tmp_path, max_issue_price_lag_seconds=1.5)


def test_metrics_tie_breaks_to_flat(tmp_path):
    ledger = make_ledger(tmp_path)
    payload = forecast_payload(probabilities={"up": 1 / 3, "flat": 1 / 3, "down": 1 / 3})
    ledger.append_forecast(payload)
    ledger.append_outcome(
        "xrp-forecast-001", 1.25, "2026-10-31T00:59:30Z",
        "2026-10-31T01:01:00Z", "SRC-PRICE-001"
    )
    metrics = ledger.metrics()
    assert metrics["accuracy"] == 1.0
    assert metrics["top_label_tie_break_order"] == ["flat", "up", "down"]


def test_forecast_source_ids_are_checked_when_registry_is_supplied(tmp_path):
    ledger = ForecastLedger(
        tmp_path,
        source_registry=HashVerifiedRegistryFixture({
            "SRC-MARKET-001": "b" * 64,
            "SRC-FEATURE-001": "a" * 64,
            "SRC-REPLAY-MANIFEST-001": "e" * 64,
        }),
    )
    record = ledger.append_forecast(forecast_payload())
    assert record["source_registry_status"] == "REGISTERED"

    unregistered = ForecastLedger(tmp_path / "unregistered", source_registry={})
    with pytest.raises(ValueError, match="source_ids are not registered"):
        unregistered.append_forecast(forecast_payload())


def test_outcome_price_source_is_checked_when_registry_is_supplied(tmp_path):
    ledger = ForecastLedger(
        tmp_path,
        source_registry=HashVerifiedRegistryFixture({
            "SRC-MARKET-001": "b" * 64,
            "SRC-PRICE-001": "c" * 64,
            "SRC-FEATURE-001": "a" * 64,
            "SRC-REPLAY-MANIFEST-001": "e" * 64,
        }),
    )
    ledger.append_forecast(forecast_payload())
    outcome = ledger.append_outcome(
        "xrp-forecast-001",
        1.27,
        "2026-10-31T00:59:30Z",
        "2026-10-31T01:01:00Z",
        "SRC-PRICE-001",
    )
    assert outcome["price_source_registry_status"] == "REGISTERED"

    unregistered = ForecastLedger(
        tmp_path / "unregistered",
        source_registry=HashVerifiedRegistryFixture({
            "SRC-MARKET-001": "b" * 64,
            "SRC-FEATURE-001": "a" * 64,
            "SRC-REPLAY-MANIFEST-001": "e" * 64,
        }),
    )
    unregistered.append_forecast(forecast_payload())
    with pytest.raises(ValueError, match="price_source_id is not registered"):
        unregistered.append_outcome(
            "xrp-forecast-001",
            1.27,
            "2026-10-31T00:59:30Z",
            "2026-10-31T01:01:00Z",
            "SRC-PRICE-001",
        )


def test_forecast_and_outcome_mark_registry_unchecked_when_not_supplied(tmp_path):
    ledger = ForecastLedger(tmp_path, allow_unverified_sources=True)
    forecast = ledger.append_forecast(forecast_payload())
    assert forecast["source_registry_status"] == "NOT_CHECKED"
    outcome = ledger.append_outcome(
        "xrp-forecast-001",
        1.27,
        "2026-10-31T00:59:30Z",
        "2026-10-31T01:01:00Z",
        "SRC-PRICE-001",
    )
    assert outcome["price_source_registry_status"] == "NOT_CHECKED"
    metrics = ledger.metrics()
    assert metrics["accuracy"] is None
    assert metrics["performance_claim_status"] == "NOT_AUTHORIZED_UNVERIFIED_PROVENANCE"


def test_verified_forecast_requires_a_hash_bearing_source_registry(tmp_path):
    with pytest.raises(ValueError, match="source_registry is required"):
        ForecastLedger(tmp_path)


def test_feature_snapshot_hash_must_match_registered_source_content(tmp_path):
    registry = HashVerifiedRegistryFixture({
        "SRC-MARKET-001": "b" * 64,
        "SRC-FEATURE-001": "d" * 64,
        "SRC-REPLAY-MANIFEST-001": "e" * 64,
    })
    ledger = ForecastLedger(tmp_path, source_registry=registry)
    with pytest.raises(ValueError, match="does not match registered source content hash"):
        ledger.append_forecast(forecast_payload())


def test_feature_snapshot_source_must_be_in_forecast_source_ids(tmp_path):
    ledger = make_ledger(tmp_path)
    payload = forecast_payload(source_ids=["SRC-MARKET-001"])
    with pytest.raises(ValueError, match="feature_snapshot.source_id must be included"):
        ledger.append_forecast(payload)


def test_source_registry_rejects_invalid_entries(tmp_path):
    with pytest.raises(ValueError, match="source_registry keys must be non-empty"):
        ForecastLedger(tmp_path, source_registry={"": "a" * 64})
    with pytest.raises(ValueError, match="hash-bearing mapping or SourceRegistry"):
        ForecastLedger(tmp_path, source_registry="SRC-STRING")


def test_plain_hash_mapping_cannot_authorize_verified_forecast_metrics(tmp_path):
    with pytest.raises(ValueError, match="plain source_registry mappings cannot verify snapshot bytes"):
        ForecastLedger(tmp_path / "strict", source_registry=TEST_SOURCE_REGISTRY)
    ledger = ForecastLedger(
        tmp_path / "id-only",
        source_registry=TEST_SOURCE_REGISTRY,
        allow_unverified_sources=True,
    )
    forecast = ledger.append_forecast(forecast_payload())
    assert forecast["source_registry_status"] == "ID_ONLY_NOT_HASH_VERIFIED"
    outcome = ledger.append_outcome(
        "xrp-forecast-001", 1.27, "2026-10-31T00:59:30Z",
        "2026-10-31T01:01:00Z", "SRC-PRICE-001"
    )
    assert outcome["price_source_registry_status"] == "ID_ONLY_NOT_HASH_VERIFIED"
    metrics = ledger.metrics()
    assert metrics["accuracy"] is None
    assert metrics["performance_claim_status"] == "NOT_AUTHORIZED_UNVERIFIED_PROVENANCE"



def test_concurrent_jsonl_appends_serialize_duplicate_forecast_ids(tmp_path):
    path = tmp_path / "forecasts.jsonl"
    barrier = Barrier(8)
    record = {"forecast_id": "xrp-concurrent-duplicate"}

    def append(_):
        barrier.wait(timeout=5)
        try:
            _append_jsonl(path, record, "duplicate forecast_id")
            return "written"
        except ValueError:
            return "duplicate"

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(append, range(8)))

    assert results.count("written") == 1
    assert results.count("duplicate") == 7
    assert [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] == [record]



def _ledger_with_valid_outcome(tmp_path):
    ledger = make_ledger(tmp_path)
    ledger.append_forecast(forecast_payload())
    ledger.append_outcome(
        "xrp-forecast-001", 1.27, "2026-10-31T00:59:59Z",
        "2026-10-31T01:00:10Z", "SRC-PRICE-001"
    )
    return ledger


def _rewrite_single_outcome(ledger, **changes):
    rows = [json.loads(line) for line in ledger.outcomes_path.read_text(encoding="utf-8").splitlines()]
    rows[0].update(changes)
    ledger.outcomes_path.write_text(
        "".join(json.dumps(row) + "\n" for row in rows),
        encoding="utf-8",
    )


def test_metrics_reject_persisted_post_horizon_observation(tmp_path):
    ledger = _ledger_with_valid_outcome(tmp_path)
    _rewrite_single_outcome(ledger, price_observed_at_utc="2026-10-31T01:00:01Z")
    with pytest.raises(ValueError, match="outside the forecast horizon"):
        ledger.metrics()


def test_metrics_reject_persisted_observation_lag_tampering(tmp_path):
    ledger = _ledger_with_valid_outcome(tmp_path)
    _rewrite_single_outcome(ledger, observation_lag_seconds=0.0)
    with pytest.raises(ValueError, match="observation_lag_seconds is inconsistent"):
        ledger.metrics()


def test_metrics_reject_persisted_realized_class_tampering(tmp_path):
    ledger = _ledger_with_valid_outcome(tmp_path)
    _rewrite_single_outcome(ledger, realized_class="down")
    with pytest.raises(ValueError, match="realized_class is inconsistent"):
        ledger.metrics()


def test_metrics_reject_persisted_realized_return_tampering(tmp_path):
    ledger = _ledger_with_valid_outcome(tmp_path)
    _rewrite_single_outcome(ledger, realized_return_pct=-99.0)
    with pytest.raises(ValueError, match="realized_return_pct is inconsistent"):
        ledger.metrics()


def test_metrics_exposes_effective_horizon_and_observation_lag(tmp_path):
    ledger = _ledger_with_valid_outcome(tmp_path)
    metrics = ledger.metrics()
    assert metrics["mean_observation_lag_seconds"] == pytest.approx(1.0)
    assert metrics["max_observation_lag_seconds"] == pytest.approx(1.0)
    assert metrics["min_effective_horizon_seconds"] == pytest.approx(3599.0)
    assert metrics["max_effective_horizon_seconds"] == pytest.approx(3599.0)

def test_metrics_refuse_to_pool_resolved_forecasts_with_different_horizons(tmp_path):
    ledger = make_ledger(tmp_path)
    ledger.append_forecast(forecast_payload())
    ledger.append_forecast(forecast_payload(
        forecast_id="xrp-forecast-002",
        horizon_seconds=7200,
    ))
    ledger.append_outcome(
        "xrp-forecast-001", 1.27, "2026-10-31T00:59:59Z",
        "2026-10-31T01:00:10Z", "SRC-PRICE-001"
    )
    ledger.append_outcome(
        "xrp-forecast-002", 1.28, "2026-10-31T01:59:59Z",
        "2026-10-31T02:00:10Z", "SRC-PRICE-001"
    )

    metrics = ledger.metrics()

    assert metrics["forecast_count"] == 2
    assert metrics["resolved_count"] == 2
    assert metrics["accuracy"] is None
    assert metrics["mean_brier_score"] is None
    assert metrics["performance_claim_status"] == "NOT_COMPARABLE_MIXED_PROTOCOLS"
    assert metrics["evaluation_protocol_status"] == "MIXED_PROTOCOLS_NOT_AGGREGATED"
    assert {
        item["protocol"]["horizon_seconds"]
        for item in metrics["evaluation_protocols"]
    } == {3600, 7200}


def test_metrics_refuse_to_pool_different_target_thresholds(tmp_path):
    ledger = make_ledger(tmp_path)
    ledger.append_forecast(forecast_payload())
    ledger.append_forecast(forecast_payload(
        forecast_id="xrp-forecast-002",
        target={
            "name": "xrp_usd_return_class_v1",
            "up_threshold_pct": 1.0,
            "down_threshold_pct": -1.0,
        },
    ))

    metrics = ledger.metrics()

    assert metrics["accuracy"] is None
    assert metrics["performance_claim_status"] == "NOT_COMPARABLE_MIXED_PROTOCOLS"
    assert len(metrics["evaluation_protocols"]) == 2


def test_metrics_refuse_to_pool_different_model_versions(tmp_path):
    ledger = make_ledger(tmp_path)
    ledger.append_forecast(forecast_payload())
    ledger.append_forecast(forecast_payload(
        forecast_id="xrp-forecast-002",
        model={"name": "barrot-xrp", "version": "0.2.0"},
    ))

    metrics = ledger.metrics()

    assert metrics["accuracy"] is None
    assert metrics["performance_claim_status"] == "NOT_COMPARABLE_MIXED_PROTOCOLS"
    assert len(metrics["evaluation_protocols"]) == 2

def test_metrics_refuse_to_pool_different_baseline_versions(tmp_path):
    ledger = make_ledger(tmp_path)
    ledger.append_forecast(forecast_payload())
    ledger.append_forecast(forecast_payload(
        forecast_id="xrp-forecast-002",
        baseline={
            "id": "uniform-v2",
            "trained_through_utc": "2026-10-30T23:59:00Z",
            "computed_at_utc": "2026-10-30T23:59:00Z",
            "probabilities": {"up": 1 / 3, "flat": 1 / 3, "down": 1 / 3},
        },
    ))

    metrics = ledger.metrics()

    assert metrics["accuracy"] is None
    assert metrics["performance_claim_status"] == "NOT_COMPARABLE_MIXED_PROTOCOLS"
    assert len(metrics["evaluation_protocols"]) == 2


def test_source_registry_object_verifies_feature_snapshot_content_hash(tmp_path):
    registry, hashes, paths = make_file_backed_registry(tmp_path)
    payload = forecast_payload()
    payload["feature_snapshot"]["sha256"] = hashes["SRC-FEATURE-001"]
    ledger = ForecastLedger(tmp_path / "ledger", source_registry=registry)
    record = ledger.append_forecast(payload)
    assert record["source_registry_status"] == "REGISTERED"
    assert record["feature_snapshot_hash_verified"] is True
    assert record["source_content_hashes"]["SRC-FEATURE-001"] == hashes["SRC-FEATURE-001"]
    assert all(registry.verify_content_hash(source_id) for source_id in TEST_SOURCE_REGISTRY)
    assert all(path.is_file() for path in paths.values())


def test_metrics_refuse_tampered_registered_feature_snapshot_hash(tmp_path):
    ledger = make_ledger(tmp_path)
    ledger.append_forecast(forecast_payload())
    ledger.append_outcome(
        "xrp-forecast-001", 1.27, "2026-10-31T00:59:30Z",
        "2026-10-31T01:01:00Z", "SRC-PRICE-001"
    )
    rows = [
        json.loads(line)
        for line in ledger.forecasts_path.read_text(encoding="utf-8").splitlines()
    ]
    rows[0]["source_content_hashes"]["SRC-FEATURE-001"] = "d" * 64
    ledger.forecasts_path.write_text(
        "".join(json.dumps(row) + "\n" for row in rows),
        encoding="utf-8",
    )
    metrics = ledger.metrics()
    assert metrics["accuracy"] is None
    assert metrics["performance_claim_status"] == "NOT_AUTHORIZED_UNVERIFIED_PROVENANCE"


def test_id_only_registry_cannot_authorize_forecast_metrics(tmp_path):
    ledger = ForecastLedger(
        tmp_path,
        source_registry=set(TEST_SOURCE_REGISTRY),
        allow_unverified_sources=True,
    )
    forecast = ledger.append_forecast(forecast_payload())
    assert forecast["source_registry_status"] == "ID_ONLY_NOT_HASH_VERIFIED"
    assert forecast["feature_snapshot_hash_verified"] is False
    ledger.append_outcome(
        "xrp-forecast-001", 1.27, "2026-10-31T00:59:30Z",
        "2026-10-31T01:01:00Z", "SRC-PRICE-001"
    )
    metrics = ledger.metrics()
    assert metrics["accuracy"] is None
    assert metrics["performance_claim_status"] == "NOT_AUTHORIZED_UNVERIFIED_PROVENANCE"


def test_historical_replay_records_system_append_time_and_manifest(tmp_path, monkeypatch):
    monkeypatch.setattr(
        fixed_horizon,
        "_utc_now",
        lambda: datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc),
    )
    ledger = make_ledger(tmp_path)
    record = ledger.append_forecast(forecast_payload())
    assert record["mode"] == "HISTORICAL_REPLAY"
    assert record["recorded_at_utc"] == "2026-11-01T00:00:00Z"
    assert record["replay_manifest_source_id"] == "SRC-REPLAY-MANIFEST-001"
    assert record["source_content_hashes"]["SRC-REPLAY-MANIFEST-001"] == "e" * 64


def test_historical_replay_requires_manifest_source(tmp_path):
    ledger = make_ledger(tmp_path)
    payload = forecast_payload(replay_manifest_source_id=None)
    with pytest.raises(ValueError, match="requires replay_manifest_source_id"):
        ledger.append_forecast(payload)


def test_forecast_rejects_caller_supplied_recorded_at(tmp_path):
    ledger = make_ledger(tmp_path)
    payload = forecast_payload(recorded_at_utc="2026-10-31T00:00:01Z")
    with pytest.raises(ValueError, match="system-generated"):
        ledger.append_forecast(payload)


def test_live_forecast_records_system_time_and_rejects_backfill(tmp_path, monkeypatch):
    monkeypatch.setattr(
        fixed_horizon,
        "_utc_now",
        lambda: datetime(2026, 10, 31, 0, 0, 10, tzinfo=timezone.utc),
    )
    ledger = make_ledger(tmp_path)
    payload = forecast_payload(
        mode="LIVE",
        replay_manifest_source_id=None,
        issued_at_utc="2026-10-31T00:00:00Z",
    )
    record = ledger.append_forecast(payload)
    assert record["mode"] == "LIVE"
    assert record["recorded_at_utc"] == "2026-10-31T00:00:10Z"
    assert record["replay_manifest_source_id"] is None

    monkeypatch.setattr(
        fixed_horizon,
        "_utc_now",
        lambda: datetime(2026, 10, 31, 2, 0, 0, tzinfo=timezone.utc),
    )
    with pytest.raises(ValueError, match="too old"):
        make_ledger(tmp_path / "backfill").append_forecast(
            forecast_payload(
                mode="LIVE",
                replay_manifest_source_id=None,
                issued_at_utc="2026-10-31T00:00:00Z",
            )
        )


def test_live_forecast_rejects_already_elapsed_target_horizon(tmp_path, monkeypatch):
    monkeypatch.setattr(
        fixed_horizon,
        "_utc_now",
        lambda: datetime(2026, 10, 31, 0, 0, 2, tzinfo=timezone.utc),
    )
    ledger = make_ledger(tmp_path)
    payload = forecast_payload(
        mode="LIVE",
        replay_manifest_source_id=None,
        horizon_seconds=1,
    )
    with pytest.raises(ValueError, match="already elapsed"):
        ledger.append_forecast(payload)


def test_metrics_never_pool_live_and_historical_replay(tmp_path, monkeypatch):
    monkeypatch.setattr(
        fixed_horizon,
        "_utc_now",
        lambda: datetime(2026, 11, 1, 0, 0, 10, tzinfo=timezone.utc),
    )
    ledger = make_ledger(tmp_path)
    ledger.append_forecast(forecast_payload())
    live = forecast_payload(
        forecast_id="xrp-live-forecast-001",
        mode="LIVE",
        replay_manifest_source_id=None,
        issued_at_utc="2026-11-01T00:00:00Z",
        data_cutoff_utc="2026-10-31T23:59:00Z",
        feature_snapshot={
            "snapshot_id": "features-live-001",
            "source_id": "SRC-FEATURE-001",
            "sha256": "a" * 64,
            "captured_at_utc": "2026-10-31T23:58:00Z",
        },
        baseline={
            "id": "uniform-v1",
            "trained_through_utc": "2026-10-31T23:59:00Z",
            "computed_at_utc": "2026-10-31T23:59:00Z",
            "probabilities": {"up": 1 / 3, "flat": 1 / 3, "down": 1 / 3},
        },
        price_at_issue_observed_at_utc="2026-10-31T23:59:00Z",
    )
    ledger.append_forecast(live)
    metrics = ledger.metrics()
    assert metrics["accuracy"] is None
    assert metrics["evaluation_protocol_status"] == "MIXED_PROTOCOLS_NOT_AGGREGATED"
    assert {item["protocol"]["mode"] for item in metrics["evaluation_protocols"]} == {
        "LIVE",
        "HISTORICAL_REPLAY",
    }


def test_outcome_recorded_at_uses_system_time_not_caller_claim(tmp_path, monkeypatch):
    monkeypatch.setattr(
        fixed_horizon,
        "_utc_now",
        lambda: datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc),
    )
    ledger = make_ledger(tmp_path)
    ledger.append_forecast(forecast_payload())
    outcome = ledger.append_outcome(
        "xrp-forecast-001",
        1.27,
        "2026-10-31T00:59:30Z",
        "2026-10-31T01:01:00Z",
        "SRC-PRICE-001",
    )
    assert outcome["outcome_recorded_at_utc"] == "2026-11-01T00:00:00Z"
    assert outcome["caller_claimed_recorded_at_utc"] == "2026-10-31T01:01:00Z"





def test_forecast_rejects_source_snapshot_bytes_changed_after_registration(tmp_path):
    registry, hashes, paths = make_file_backed_registry(tmp_path)
    payload = forecast_payload()
    payload["feature_snapshot"]["sha256"] = hashes["SRC-FEATURE-001"]
    ledger = ForecastLedger(tmp_path / "ledger", source_registry=registry)
    ledger.append_forecast(payload)
    paths["SRC-PRICE-001"].write_text("tampered after registration", encoding="utf-8")
    with pytest.raises(ValueError, match="source snapshot bytes"):
        ledger.append_outcome(
            "xrp-forecast-001", 1.27, "2026-10-31T00:59:30Z",
            "2026-10-31T01:01:00Z", "SRC-PRICE-001"
        )


def test_metrics_fail_closed_when_source_snapshot_bytes_change_after_outcome(tmp_path):
    registry, hashes, paths = make_file_backed_registry(tmp_path)
    payload = forecast_payload()
    payload["feature_snapshot"]["sha256"] = hashes["SRC-FEATURE-001"]
    ledger = ForecastLedger(tmp_path / "ledger", source_registry=registry)
    ledger.append_forecast(payload)
    ledger.append_outcome(
        "xrp-forecast-001", 1.27, "2026-10-31T00:59:30Z",
        "2026-10-31T01:01:00Z", "SRC-PRICE-001"
    )
    paths["SRC-PRICE-001"].write_text("tampered after outcome", encoding="utf-8")
    metrics = ledger.metrics()
    assert metrics["accuracy"] is None
    assert metrics["performance_claim_status"] == "NOT_AUTHORIZED_UNVERIFIED_PROVENANCE"

def test_metrics_refuse_tampered_registered_replay_manifest_hash(tmp_path):
    ledger = make_ledger(tmp_path)
    ledger.append_forecast(forecast_payload())
    ledger.append_outcome(
        "xrp-forecast-001",
        1.27,
        "2026-10-31T00:59:30Z",
        "2026-10-31T01:01:00Z",
        "SRC-PRICE-001",
    )
    rows = [
        json.loads(line)
        for line in ledger.forecasts_path.read_text(encoding="utf-8").splitlines()
    ]
    rows[0]["source_content_hashes"]["SRC-REPLAY-MANIFEST-001"] = "f" * 64
    ledger.forecasts_path.write_text(
        "".join(json.dumps(row) + "\n" for row in rows),
        encoding="utf-8",
    )
    metrics = ledger.metrics()
    assert metrics["accuracy"] is None
    assert metrics["performance_claim_status"] == "NOT_AUTHORIZED_UNVERIFIED_PROVENANCE"

def test_metrics_refuse_tampered_registered_outcome_price_source_hash(tmp_path):
    ledger = _ledger_with_valid_outcome(tmp_path)
    _rewrite_single_outcome(ledger, price_source_content_hash="f" * 64)
    metrics = ledger.metrics()
    assert metrics["accuracy"] is None
    assert metrics["performance_claim_status"] == "NOT_AUTHORIZED_UNVERIFIED_PROVENANCE"


def test_metrics_refuse_outcome_when_registered_price_source_hash_changes(tmp_path):
    ledger = _ledger_with_valid_outcome(tmp_path)
    ledger.source_registry.entries["SRC-PRICE-001"] = "f" * 64
    metrics = ledger.metrics()
    assert metrics["accuracy"] is None
    assert metrics["performance_claim_status"] == "NOT_AUTHORIZED_UNVERIFIED_PROVENANCE"

