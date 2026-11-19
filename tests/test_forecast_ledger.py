import base64
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from barrot_agent.evolution.feature_store import HistoricalFeatureStore
from barrot_agent.evolution.forecast_ledger import (
    ForecastAlreadyResolvedError,
    ForecastLedger,
    ForecastLedgerError,
    _validate_canonical_raw_receipt,
    _validate_readiness_report,
)
from barrot_agent.evolution.point_in_time_features import build_feature_snapshot
from barrot_agent.evolution.xrp_public_ingestion import RawReceiptArchive
from barrot_agent.evolution.source_independence import canonical_independence_groups

REPO_ROOT = Path(__file__).resolve().parents[1]

_TEST_EVALUATOR_PRIVATE_KEY = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
_TEST_EVALUATOR_PUBLIC_KEY = _TEST_EVALUATOR_PRIVATE_KEY.public_key().public_bytes(
    Encoding.Raw, PublicFormat.Raw
)
_EVALUATOR_ATTESTATION_DOMAIN = b"BARROT_XRP_MODEL_READINESS_V6\0"


def _trusted_test_evaluator_keys():
    return {"test-independent-evaluator": _TEST_EVALUATOR_PUBLIC_KEY}


def _sign_readiness_report(report, *, key_id="test-independent-evaluator", attested_at_utc="2026-11-03T16:00:40Z"):
    unsigned = dict(report)
    unsigned.pop("evaluator_attestation", None)
    attestation_metadata = {
        "scheme": "Ed25519",
        "key_id": key_id,
        "attested_at_utc": attested_at_utc,
    }
    signed_document = {"report": unsigned, "attestation": attestation_metadata}
    payload = json.dumps(
        signed_document, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")
    payload_sha256 = hashlib.sha256(payload).hexdigest()
    signature = _TEST_EVALUATOR_PRIVATE_KEY.sign(
        _EVALUATOR_ATTESTATION_DOMAIN + bytes.fromhex(payload_sha256)
    )
    report["evaluator_attestation"] = {
        **attestation_metadata,
        "signed_payload_sha256": payload_sha256,
        "signature_base64": base64.b64encode(signature).decode("ascii"),
    }
    return report



def _declared_cadence_diagnostics():
    return {
        "cadence_seconds": 3600.0,
        "cadence_source": "declared",
        "max_gap_multiple": 1.5,
        "contiguous_segment_count": 1,
        "contiguous_segment_lengths": [200],
        "largest_contiguous_segment": 200,
        "valid_block_window_count": 196,
    }


def _paired_comparisons_fixture(sample_count=200):
    comparisons = {}
    for baseline in (
        "naive_class_prior", "momentum_sign", "mean_reversion_sign", "volatility_normal"
    ):
        comparisons[baseline] = {
            "paired_origin_count": sample_count,
            "mean_brier_difference_vs_benchmark": -0.05,
            "mean_log_loss_difference_vs_benchmark": -0.10,
            "temporal_moving_block_bootstrap": {
                "status": "ESTIMATED",
                "confidence_level": 0.99375,
                "brier_difference_ci": [-0.08, -0.02],
                "log_loss_difference_ci": [-0.15, -0.04],
                "sampling_diagnostics": _declared_cadence_diagnostics(),
                "log_loss_sampling_diagnostics": _declared_cadence_diagnostics(),
            },
            "source_clustered_moving_block_bootstrap": {
                "status": "ESTIMATED",
                "confidence_level": 0.99375,
                "source_cluster_count": 5,
                "source_group_ids": sorted(FEATURE_SOURCE_GROUPS),
                "minimum_origins_per_source_cluster": 5,
                "observed_minimum_origins_per_source_cluster": 40,
                "equal_cluster_weighted_mean_brier_difference": -0.05,
                "equal_cluster_weighted_mean_log_loss_difference": -0.10,
                "brier_difference_ci": [-0.08, -0.02],
                "log_loss_difference_ci": [-0.15, -0.04],
                "brier_sampling_diagnostics": {
                    "status": "ESTIMATED",
                    "source_cluster_count": 5,
                    "source_group_ids": sorted(FEATURE_SOURCE_GROUPS),
                    "per_cluster": {group_id: _declared_cadence_diagnostics() for group_id in FEATURE_SOURCE_GROUPS},
                },
                "log_loss_sampling_diagnostics": {
                    "status": "ESTIMATED",
                    "source_cluster_count": 5,
                    "source_group_ids": sorted(FEATURE_SOURCE_GROUPS),
                    "per_cluster": {group_id: _declared_cadence_diagnostics() for group_id in FEATURE_SOURCE_GROUPS},
                },
            },
        }
    return comparisons


def _paired_uncertainty_fixture():
    return {
        "method": "paired_temporal_and_source_clustered_moving_block_bootstrap_v1",
        "sampling_policy": "non_circular_contiguous_time_blocks_v1",
        "candidate_model_id": "xrp-test-v1",
        "familywise_confidence_level": 0.95,
        "familywise_comparison_count": 8,
        "multiplicity_method": "bonferroni",
        "individual_confidence_level": 0.99375,
        "bootstrap_replicates": 10000,
        "block_length_origins": 5,
        "minimum_paired_origins": 100,
        "minimum_source_clusters": 5,
        "minimum_origins_per_source_cluster": 5,
        "out_of_sample": {"status": "PASS", "comparisons": _paired_comparisons_fixture(200)},
        "shadow_evaluation": {"status": "PASS", "comparisons": _paired_comparisons_fixture(200)},
    }


CUTOFF = "2026-11-03T16:00:00Z"
ISSUED = "2026-11-03T16:01:00Z"
TARGET = "2026-11-03T17:00:00Z"
OUTCOME_TIME = "2026-11-03T17:00:30Z"
RESOLVED = "2026-11-03T17:01:00Z"
TEST_NOW = datetime(2026, 11, 3, 16, 1, 30, tzinfo=timezone.utc)


FEATURE_CUTOFF = "2026-11-03T15:59:30Z"
FEATURE_CAPTURED = "2026-11-03T15:59:35Z"
STORE_RECEIPT = datetime(2026, 11, 3, 15, 59, 40, tzinfo=timezone.utc)
FEATURE_RECORD = {
    "record_id": "xrp:spot:mid:2026-11-03T15:59:30Z:v1",
    "feature_id": "xrp.spot.mid_price",
    "feature_version": 1,
    "asset": "XRP",
    "feature_name": "spot_mid_price",
    "value": 1.27,
    "unit": "USD/XRP",
    "event_time_utc": FEATURE_CUTOFF,
    "known_at_utc": FEATURE_CUTOFF,
    "source_data_as_of_utc": FEATURE_CUTOFF,
    "ingested_at_utc": FEATURE_CUTOFF,
    "revision_available_at_utc": FEATURE_CUTOFF,
    "sources": [
        {
            "source_id": "kraken-001",
            "independence_group": "kraken.com",
            "source_uri": "https://api.kraken.com/0/public/Ticker?pair=XRPUSD",
            "raw_content_sha256": "a" * 64,
        },
        {
            "source_id": "macro-001",
            "independence_group": "fred.stlouisfed.org",
            "source_uri": "https://api.stlouisfed.org/fred/series/observations",
            "raw_content_sha256": "b" * 64,
        },
        {
            "source_id": "coinbase-001",
            "independence_group": "coinbase.com",
            "source_uri": "https://api.exchange.coinbase.com/products/XRP-USD/ticker",
            "raw_content_sha256": "c" * 64,
        },
        {
            "source_id": "binance-001",
            "independence_group": "binance.com",
            "source_uri": "https://api.binance.com/api/v3/ticker/price?symbol=XRPUSDT",
            "raw_content_sha256": "d" * 64,
        },
        {
            "source_id": "okx-001",
            "independence_group": "okx.com",
            "source_uri": "https://www.okx.com/api/v5/market/ticker?instId=XRP-USDT",
            "raw_content_sha256": "e" * 64,
        },
    ],
    "quality_status": "verified",
    "model_eligible": True,
    "eligibility_reason": "",
    "revision_status": "original",
    "supersedes_record_id": None,
    "adapter_version": "test-adapter-v1",
    "parser_version": "test-parser-v1",
    "limitations": [],
    "disconfirming_evidence_ids": [],
}
FEATURE_SOURCE_GROUPS = canonical_independence_groups(FEATURE_RECORD["sources"])
FEATURE_SNAPSHOT = build_feature_snapshot(
    [FEATURE_RECORD],
    cutoff_utc=FEATURE_CUTOFF,
    captured_at_utc=FEATURE_CAPTURED,
)


def _readiness_fixture(asset, horizon_seconds, source_ids=None):
    """Synthetic test-only evidence; never represents real XRP model readiness."""
    source_ids = source_ids or ["kraken-001", "macro-001", "coinbase-001", "binance-001", "okx-001"]
    source_details = {
        "kraken-001": (
            "kraken.com",
            "https://api.kraken.com/0/public/Ticker?pair=XRPUSD",
            b'{"pair":"XRP/USD","mid":1.27}',
        ),
        "macro-001": (
            "fred.stlouisfed.org",
            "https://api.stlouisfed.org/fred/series/observations",
            b'{"series":"DFF","value":"4.00"}',
        ),
        "coinbase-001": (
            "coinbase.com",
            "https://api.exchange.coinbase.com/products/XRP-USD/ticker",
            b'{"product_id":"XRP-USD","price":"1.27"}',
        ),
        "binance-001": (
            "binance.com",
            "https://api.binance.com/api/v3/ticker/price?symbol=XRPUSDT",
            b'{"symbol":"XRPUSDT","price":"1.27"}',
        ),
        "okx-001": (
            "okx.com",
            "https://www.okx.com/api/v5/market/ticker?instId=XRP-USDT",
            b'{"instId":"XRP-USDT","last":"1.27"}',
        ),
        "unregistered": (
            "unregistered.example",
            "https://example.com/receipt",
            b'{"source":"unregistered-test-only"}',
        ),
    }
    raw_receipt_bytes = {}
    receipts = []
    for source_id in source_ids:
        group, source_uri, raw_bytes = source_details[source_id]
        raw_digest = hashlib.sha256(raw_bytes).hexdigest()
        canonical_payload = {
            "source_id": source_id,
            "source_uri": source_uri,
            "captured_at_utc": FEATURE_CAPTURED,
            "source_data_as_of_utc": FEATURE_CUTOFF,
            "source_http_date": None,
            "raw_content_sha256": raw_digest,
            "payload_size_bytes": len(raw_bytes),
            "raw_payload_path": f"raw/sha256/{raw_digest}.json",
            "raw_bytes_retained": True,
            "raw_retention_reason": "",
            "model_eligible_source": True,
            "raw_only_reason": "",
        }
        canonical_receipt_id = hashlib.sha256(
            json.dumps(
                canonical_payload,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            ).encode("utf-8")
        ).hexdigest()
        canonical_receipt = {**canonical_payload, "receipt_id": canonical_receipt_id}
        raw_receipt_bytes[canonical_receipt_id] = raw_bytes
        receipts.append(
            {
                "source_id": source_id,
                "receipt_id": canonical_receipt_id,
                "raw_content_sha256": raw_digest,
                "raw_capture_status": "byte_complete",
                "raw_receipt_sha256_verified": True,
                "independence_group": group,
                "source_uri": source_uri,
                "source_data_as_of_utc": FEATURE_CUTOFF,
                "captured_at_utc": FEATURE_CAPTURED,
                "raw_receipt": canonical_receipt,
            }
        )
    independence_groups = canonical_independence_groups(receipts)
    dataset_manifest = {
        "model_eligible": True,
        "quality_status": "verified",
        "asset": asset,
        "venue": "kraken:XRP/USD",
        "feature_ids": ["xrp.spot.mid_price"],
        "feature_snapshot_ids": [FEATURE_SNAPSHOT["snapshot_id"]],
        "source_ids": source_ids,
        "source_independence_groups": independence_groups,
        "raw_source_receipts": receipts,
        "data_cutoff_utc": FEATURE_CUTOFF,
    }
    canonical_dataset = json.dumps(
        dataset_manifest,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    report = {
        "schema_version": "barrot.xrp.model-readiness.v6",
        "evaluation_type": "chronological_walk_forward_model_evaluation",
        "status": "PASS",
        "policy_id": "xrp_forecast_readiness_v6",
        "evaluation_id": f"test-evaluation-{asset.lower()}-{horizon_seconds}-{'-'.join(source_ids)}",
        "model_version": "xrp-test-v1",
        "baseline_model_version": "naive-frequency-v1",
        "asset": asset,
        "venue": "kraken:XRP/USD",
        "horizon_seconds": horizon_seconds,
        "embargo_seconds": horizon_seconds,
        "purge_policy": "training_start_and_outcome_available_by_cutoff_minus_embargo",
        "dataset_receipt_id": f"test-dataset-receipt-{asset.lower()}-{horizon_seconds}",
        "dataset_sha256": hashlib.sha256(canonical_dataset).hexdigest(),
        "dataset_manifest": dataset_manifest,
        "source_independence_group_count": len(independence_groups),
        "training_sample_count": 1000,
        "out_of_sample_sample_count": 200,
        "shadow_evaluation_sample_count": 200,
        "effective_sample_size_method": "greedy_non_overlapping_target_intervals_v1",
        "out_of_sample_effective_sample_size": min(
            200,
            int((datetime.fromisoformat("2026-10-20T00:00:00+00:00") - datetime.fromisoformat("2026-10-01T00:00:00+00:00")).total_seconds() // horizon_seconds),
        ),
        "shadow_evaluation_effective_sample_size": min(
            200,
            int((datetime.fromisoformat("2026-11-03T15:00:00+00:00") - datetime.fromisoformat("2026-10-20T00:00:00+00:00")).total_seconds() // horizon_seconds),
        ),
        "out_of_sample_start_utc": "2026-10-01T00:00:00Z",
        "out_of_sample_end_utc": "2026-10-20T00:00:00Z",
        "shadow_evaluation_start_utc": "2026-10-20T00:00:00Z",
        "shadow_evaluation_end_utc": "2026-11-03T15:00:00Z",
        "leakage_check_status": "PASS",
        "calibration_status": "PASS",
        "drift_status": "STABLE",
        "shadow_evaluation_status": "PASS",
        "weighted_calibration_error": 0.02,
        "model_metrics": {"mean_brier_score": 0.15, "mean_log_loss": 0.42},
        "baseline_metrics": {
            "naive_class_prior": {"mean_brier_score": 0.24, "mean_log_loss": 0.65},
            "momentum_sign": {"mean_brier_score": 0.22, "mean_log_loss": 0.61},
            "mean_reversion_sign": {"mean_brier_score": 0.23, "mean_log_loss": 0.63},
            "volatility_normal": {"mean_brier_score": 0.21, "mean_log_loss": 0.59},
        },
        "paired_uncertainty": _paired_uncertainty_fixture(),
        "evaluation_data_cutoff_utc": "2026-11-03T15:59:40Z",
        "evaluation_completed_at_utc": "2026-11-03T16:00:30Z",
        "evaluator_id": "test-independent-evaluator",
        "evaluator_version": "fixture-evaluator-v1",
        "evaluation_code_sha256": "c" * 64,
        "evaluation_artifact_sha256": "d" * 64,
    }
    _sign_readiness_report(report)
    report_bytes = json.dumps(
        report,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    receipt_id = f"test-readiness-receipt-{asset.lower()}-{horizon_seconds}-{'-'.join(source_ids)}"
    report_sha256 = hashlib.sha256(report_bytes).hexdigest()
    return {
        "report_bytes": report_bytes,
        "receipt_id": receipt_id,
        "raw_receipt_bytes": raw_receipt_bytes,
        "certificate": {
            "report_sha256": report_sha256,
            "receipt_id": receipt_id,
            "policy_id": "xrp_forecast_readiness_v6",
            "status": "PASS",
        },
    }


READINESS_FIXTURES = {
    ("XRP", 3600): _readiness_fixture("XRP", 3600),
    ("XRP", 14400): _readiness_fixture("XRP", 14400),
    ("BTC", 3600): _readiness_fixture("BTC", 3600),
    ("XRP", 3600, "source_mismatch"): _readiness_fixture(
        "XRP", 3600, [
            "kraken-001", "macro-001", "coinbase-001", "binance-001", "okx-001", "unregistered"
        ]
    ),
}
def _register_readiness_fixtures(ledger):
    for fixture in READINESS_FIXTURES.values():
        ledger.register_readiness_report(
            fixture["report_bytes"],
            receipt_id=fixture["receipt_id"],
            raw_receipt_bytes=fixture["raw_receipt_bytes"],
        )


class MutableClock:
    def __init__(self, current):
        self.current = current

    def __call__(self):
        return self.current

    def set(self, current):
        self.current = current


def make_ledger(path, *, now=TEST_NOW, store_clock=STORE_RECEIPT, snapshot=FEATURE_SNAPSHOT):
    # Readiness evidence must be registered before the forecast issue timestamp.
    clock = MutableClock(datetime(2026, 11, 3, 16, 0, 45, tzinfo=timezone.utc))
    store = HistoricalFeatureStore(
        Path(path).parent / "feature_store.sqlite3",
        clock=lambda: store_clock,
    )
    store.append_snapshot(snapshot)
    ledger = ForecastLedger(
        path,
        clock=clock,
        feature_store=store,
        trusted_evaluator_public_keys=_trusted_test_evaluator_keys(),
    )
    _register_readiness_fixtures(ledger)
    clock.set(now)
    ledger._test_clock = clock
    ledger._test_feature_store = store
    ledger._test_snapshot_id = snapshot["snapshot_id"]
    return ledger


def set_ledger_time(ledger, value):
    ledger._test_clock.set(datetime.fromisoformat(value.replace("Z", "+00:00")))


def forecast(**overrides):
    value = {
        "asset": "XRP",
        "venue": "kraken:XRP/USD",
        "target_definition": "XRP/USD mid-price return at exact target timestamp; three-class thresholded outcome",
        "reference_price_usd": 1.27,
        "reference_price_timestamp_utc": FEATURE_CUTOFF,
        "reference_price_source_id": "kraken-001",
        "reference_price_max_age_seconds": 60,
        "data_cutoff_utc": CUTOFF,
        "issued_at_utc": ISSUED,
        "target_time_utc": TARGET,
        "horizon_seconds": 3600,
        "model_version": "xrp-test-v1",
        "baseline_model_version": "naive-frequency-v1",
        "probabilities": {"down": 0.2, "flat": 0.3, "up": 0.5},
        "baseline_probabilities": {"down": 0.3, "flat": 0.4, "up": 0.3},
        "flat_band_bps": 25.0,
        "outcome_tolerance_seconds": 60,
        "feature_max_timestamp_utc": FEATURE_CUTOFF,
        "feature_snapshot_ids": [FEATURE_SNAPSHOT["snapshot_id"]],
        "source_ids": ["kraken-001", "macro-001", "coinbase-001", "binance-001", "okx-001"],
        "assumptions": ["No venue outage during horizon"],
        "alternatives": ["Derivatives deleveraging overwhelms spot demand"],
        "fee_bps": 10.0,
        "slippage_bps": 5.0,
    }
    value.update(overrides)
    if "readiness_certificate" not in value:
        fixture_key = (str(value["asset"]).strip().upper(), value["horizon_seconds"])
        if "unregistered" in value["source_ids"]:
            fixture_key = (*fixture_key, "source_mismatch")
        fixture = READINESS_FIXTURES.get(fixture_key, READINESS_FIXTURES[("XRP", 3600)])
        value["readiness_certificate"] = fixture["certificate"]
    return value


def test_readiness_rejects_missing_paired_uncertainty():
    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    report.pop("paired_uncertainty")
    with pytest.raises(ForecastLedgerError, match="paired_uncertainty"):
        _validate_readiness_report(report)


def test_readiness_rejects_insufficient_source_clusters_in_shadow_window():
    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    source = report["paired_uncertainty"]["shadow_evaluation"]["comparisons"]["momentum_sign"]["source_clustered_moving_block_bootstrap"]
    source["source_cluster_count"] = 4
    source["source_group_ids"] = source["source_group_ids"][:4]
    with pytest.raises(ForecastLedgerError, match="source_cluster_count must be at least 5"):
        _validate_readiness_report(report)


def test_readiness_rejects_source_cluster_minimum_shorter_than_bootstrap_block():
    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    report["paired_uncertainty"]["minimum_origins_per_source_cluster"] = 4
    with pytest.raises(
        ForecastLedgerError,
        match="minimum_origins_per_source_cluster must be at least 5",
    ):
        _validate_readiness_report(report)


def test_readiness_rejects_source_cluster_ids_not_backed_by_raw_receipts():
    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    source = report["paired_uncertainty"]["out_of_sample"]["comparisons"]["naive_class_prior"]["source_clustered_moving_block_bootstrap"]
    source["source_group_ids"][0] = "fabricated-publisher.example"
    with pytest.raises(ForecastLedgerError, match="not backed by dataset source receipts"):
        _validate_readiness_report(report)


def test_readiness_rejects_source_cluster_count_group_id_mismatch():
    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    source = report["paired_uncertainty"]["out_of_sample"]["comparisons"]["naive_class_prior"]["source_clustered_moving_block_bootstrap"]
    source["source_cluster_count"] = 6
    with pytest.raises(ForecastLedgerError, match="source_cluster_count must match source_group_ids"):
        _validate_readiness_report(report)


def test_readiness_rejects_non_superior_familywise_interval():
    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    temporal = report["paired_uncertainty"]["out_of_sample"]["comparisons"]["volatility_normal"]["temporal_moving_block_bootstrap"]
    temporal["brier_difference_ci"] = [-0.08, 0.001]
    with pytest.raises(ForecastLedgerError, match="upper bound must be below zero"):
        _validate_readiness_report(report)


def test_readiness_rejects_inferred_temporal_bootstrap_cadence():
    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    temporal = report["paired_uncertainty"]["out_of_sample"]["comparisons"]["naive_class_prior"]["temporal_moving_block_bootstrap"]
    temporal["sampling_diagnostics"]["cadence_source"] = "median_observed_interval"
    with pytest.raises(ForecastLedgerError, match="must use a declared expected cadence"):
        _validate_readiness_report(report)


def test_readiness_rejects_inferred_source_cluster_bootstrap_cadence():
    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    source = report["paired_uncertainty"]["out_of_sample"]["comparisons"]["naive_class_prior"]["source_clustered_moving_block_bootstrap"]
    first_group = source["source_group_ids"][0]
    source["brier_sampling_diagnostics"]["per_cluster"][first_group]["cadence_source"] = "median_observed_interval"
    with pytest.raises(ForecastLedgerError, match="must use a declared expected cadence"):
        _validate_readiness_report(report)


def test_readiness_rejects_unadjusted_confidence_intervals():
    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    temporal = report["paired_uncertainty"]["out_of_sample"]["comparisons"]["naive_class_prior"]["temporal_moving_block_bootstrap"]
    temporal["confidence_level"] = 0.95
    with pytest.raises(ForecastLedgerError, match="not familywise-adjusted"):
        _validate_readiness_report(report)


def test_record_is_idempotent_and_append_only(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    first = ledger.record_forecast(forecast())
    second = ledger.record_forecast(forecast())
    assert first == second
    assert len(ledger.events(first)) == 1
    assert ledger.get_forecast(first)["forecast_id"] == first


def test_live_shadow_issue_event_records_actual_ledger_receipt_time(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    event = ledger.events(forecast_id)[0]
    assert event["recorded_at_utc"] == "2026-11-03T16:01:30.000000Z"
    assert event["recording_mode"] == "live_shadow"


def test_live_shadow_ledger_rejects_backdated_forecast_after_target(tmp_path):
    now = datetime(2026, 11, 4, 3, 30, tzinfo=timezone.utc)
    ledger = make_ledger(tmp_path / "forecasts.sqlite3", now=now)
    with pytest.raises(ForecastLedgerError, match="target_time_utc must be after actual ledger recording time"):
        ledger.record_forecast(forecast())


def test_live_shadow_ledger_rejects_backdated_issue_before_future_target(tmp_path):
    now = datetime(2026, 11, 3, 16, 10, tzinfo=timezone.utc)
    ledger = make_ledger(tmp_path / "forecasts.sqlite3", now=now)
    with pytest.raises(ForecastLedgerError, match="older than the five-minute live recording window"):
        ledger.record_forecast(forecast())


def test_live_shadow_ledger_rejects_future_issue_timestamp(tmp_path):
    now = datetime(2026, 11, 3, 16, 0, 30, tzinfo=timezone.utc)
    ledger = make_ledger(tmp_path / "forecasts.sqlite3", now=now)
    with pytest.raises(ForecastLedgerError, match="cannot be later than actual ledger recording time"):
        ledger.record_forecast(forecast())


def test_rejects_unsupported_horizon(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="horizon_seconds"):
        ledger.record_forecast(forecast(horizon_seconds=7200))


def test_rejects_naive_timestamp(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="UTC timezone"):
        ledger.record_forecast(forecast(data_cutoff_utc="2026-11-03T16:00:00"))


def test_rejects_feature_lookahead(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="look-ahead"):
        ledger.record_forecast(forecast(feature_max_timestamp_utc="2026-11-03T16:00:01Z"))


def test_rejects_reference_price_after_cutoff(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="reference_price_timestamp_utc exceeds data cutoff"):
        ledger.record_forecast(forecast(reference_price_timestamp_utc="2026-11-03T16:00:01Z"))


def test_rejects_stale_reference_price(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="older than the declared maximum age"):
        ledger.record_forecast(forecast(reference_price_timestamp_utc="2026-11-03T15:58:59Z"))


def test_reference_price_source_must_be_in_source_manifest(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="included in source_ids"):
        ledger.record_forecast(forecast(reference_price_source_id="unregistered-reference-source"))


def test_rejects_target_time_mismatch(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="target_time_utc"):
        ledger.record_forecast(forecast(target_time_utc="2026-11-03T17:01:00Z"))


def test_rejects_probabilities_that_do_not_sum_to_one(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="sum to 1"):
        ledger.record_forecast(forecast(probabilities={"down": 0.2, "flat": 0.2, "up": 0.2}))


def test_rejects_missing_alternative(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="alternatives"):
        ledger.record_forecast(forecast(alternatives=[]))


def test_rejects_resolution_before_target(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    with pytest.raises(ForecastLedgerError, match="precedes target"):
        set_ledger_time(ledger, "2026-11-03T17:00:00Z")
        ledger.resolve_forecast(
            forecast_id,
            resolved_at_utc="2026-11-03T16:59:59Z",
            outcome_price_usd=1.28,
            outcome_price_timestamp_utc="2026-11-03T17:00:00Z",
            outcome_venue="kraken:XRP/USD",
            outcome_source_ids=["kraken-outcome-001"],
        )


def test_scored_outcome_records_brier_and_baseline(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    set_ledger_time(ledger, "2026-11-03T17:01:00Z")
    outcome = ledger.resolve_forecast(
        forecast_id,
        resolved_at_utc=RESOLVED,
        outcome_price_usd=1.28,
        outcome_price_timestamp_utc=OUTCOME_TIME,
        outcome_venue="kraken:XRP/USD",
        outcome_source_ids=["kraken-outcome-001"],
    )
    assert outcome["status"] == "scored"
    assert outcome["actual_class"] == "up"
    assert outcome["directional_correct"] is True
    assert outcome["brier_score"] < outcome["baseline_brier_score"]
    assert len(ledger.events(forecast_id)) == 2
    summary = ledger.summary()
    assert summary["scored"] == 1
    assert summary["unresolved"] == 0
    assert summary["mean_brier_score"] == outcome["brier_score"]
    assert summary["brier_improvement_vs_baseline"] > 0


def test_rejects_cross_venue_without_normalization(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    with pytest.raises(ForecastLedgerError, match="cross-venue"):
        set_ledger_time(ledger, "2026-11-03T17:01:00Z")
        ledger.resolve_forecast(
            forecast_id,
            resolved_at_utc=RESOLVED,
            outcome_price_usd=1.28,
            outcome_price_timestamp_utc=OUTCOME_TIME,
            outcome_venue="coinbase:XRP-USD",
            outcome_source_ids=["coinbase-outcome-001"],
        )


def test_cross_venue_requires_explicit_normalization(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    set_ledger_time(ledger, "2026-11-03T17:01:00Z")
    outcome = ledger.resolve_forecast(
        forecast_id,
        resolved_at_utc=RESOLVED,
        outcome_price_usd=1.28,
        outcome_price_timestamp_utc=OUTCOME_TIME,
        outcome_venue="coinbase:XRP-USD",
        outcome_source_ids=["coinbase-outcome-001"],
        cross_venue_normalization="USD spot mid-price; same UTC target timestamp; no FX conversion",
    )
    assert outcome["status"] == "scored"
    assert outcome["cross_venue_normalization"]


def test_missing_outcome_is_unscorable_not_a_miss(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    set_ledger_time(ledger, "2026-11-03T17:05:00Z")
    outcome = ledger.resolve_forecast(
        forecast_id,
        resolved_at_utc="2026-11-03T17:05:00Z",
        outcome_price_usd=None,
        unscorable_reason="No venue price available within the predeclared target tolerance",
    )
    assert outcome["status"] == "unscorable"
    assert outcome["actual_class"] is None
    assert outcome["directional_correct"] is None
    summary = ledger.summary()
    assert summary["unscorable"] == 1
    assert summary["scored"] == 0
    assert summary["directional_accuracy"] is None


def test_outcome_is_immutable(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    set_ledger_time(ledger, "2026-11-03T17:01:00Z")
    ledger.resolve_forecast(
        forecast_id,
        resolved_at_utc=RESOLVED,
        outcome_price_usd=1.28,
        outcome_price_timestamp_utc=OUTCOME_TIME,
        outcome_venue="kraken:XRP/USD",
        outcome_source_ids=["kraken-outcome-001"],
    )
    with pytest.raises(ForecastAlreadyResolvedError):
        set_ledger_time(ledger, "2026-11-03T17:01:00Z")
        ledger.resolve_forecast(
            forecast_id,
            resolved_at_utc=RESOLVED,
            outcome_price_usd=1.25,
            outcome_price_timestamp_utc=OUTCOME_TIME,
            outcome_venue="kraken:XRP/USD",
            outcome_source_ids=["kraken-outcome-002"],
        )
    assert len(ledger.events(forecast_id)) == 2


def test_rejects_outcome_timestamp_outside_tolerance(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    with pytest.raises(ForecastLedgerError, match="tolerance"):
        set_ledger_time(ledger, "2026-11-03T17:05:00Z")
        ledger.resolve_forecast(
            forecast_id,
            resolved_at_utc=RESOLVED,
            outcome_price_usd=1.28,
            outcome_price_timestamp_utc="2026-11-03T17:05:00Z",
            outcome_venue="kraken:XRP/USD",
            outcome_source_ids=["kraken-outcome-001"],
        )


def test_calibration_bins_are_reported(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    set_ledger_time(ledger, "2026-11-03T17:01:00Z")
    ledger.resolve_forecast(
        forecast_id,
        resolved_at_utc=RESOLVED,
        outcome_price_usd=1.28,
        outcome_price_timestamp_utc=OUTCOME_TIME,
        outcome_venue="kraken:XRP/USD",
        outcome_source_ids=["kraken-outcome-001"],
    )
    summary = ledger.summary()
    assert summary["calibration_bins"][0]["count"] == 1
    assert summary["weighted_calibration_error"] is not None


def test_summary_does_not_pool_different_horizons(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    one_hour_id = ledger.record_forecast(forecast())
    four_hour_id = ledger.record_forecast(
        forecast(
            target_time_utc="2026-11-03T20:00:00Z",
            horizon_seconds=14400,
        )
    )
    set_ledger_time(ledger, "2026-11-03T17:01:00Z")
    ledger.resolve_forecast(
        one_hour_id,
        resolved_at_utc=RESOLVED,
        outcome_price_usd=1.28,
        outcome_price_timestamp_utc=OUTCOME_TIME,
        outcome_venue="kraken:XRP/USD",
        outcome_source_ids=["kraken-outcome-001"],
    )
    set_ledger_time(ledger, "2026-11-03T20:01:00Z")
    ledger.resolve_forecast(
        four_hour_id,
        resolved_at_utc="2026-11-03T20:01:00Z",
        outcome_price_usd=1.28,
        outcome_price_timestamp_utc="2026-11-03T20:00:30Z",
        outcome_venue="kraken:XRP/USD",
        outcome_source_ids=["kraken-outcome-004h"],
    )

    summary = ledger.summary()
    assert summary["scored"] == 2
    assert summary["directional_accuracy"] is None
    assert summary["top_class_accuracy"] is None
    assert summary["mean_brier_score"] is None
    assert len(summary["cohort_summaries"]) == 2
    assert {item["horizon_seconds"] for item in summary["cohort_summaries"]} == {3600, 14400}
    assert all(item["scored"] == 1 for item in summary["cohort_summaries"])


def test_database_rejects_mutation_of_ledger_records(tmp_path):
    import sqlite3

    db_path = tmp_path / "forecasts.sqlite3"
    ledger = make_ledger(db_path)
    forecast_id = ledger.record_forecast(forecast())
    connection = sqlite3.connect(db_path)
    try:
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            connection.execute(
                "UPDATE forecasts SET venue = 'other' WHERE forecast_id = ?",
                (forecast_id,),
            )
        connection.rollback()
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "DELETE FROM events WHERE forecast_id = ?",
                (forecast_id,),
            )
        connection.rollback()
    finally:
        connection.close()


def test_rejects_boolean_probability(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="not boolean"):
        ledger.record_forecast(
            forecast(probabilities={"down": True, "flat": 0.0, "up": 0.0})
        )



def test_default_forecast_ledger_database_and_sidecars_are_gitignored() -> None:
    ignored = set((REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines())
    assert {
        "data/xrp_intelligence/forecast_ledger.sqlite3",
        "data/xrp_intelligence/forecast_ledger.sqlite3-wal",
        "data/xrp_intelligence/forecast_ledger.sqlite3-shm",
        "data/xrp_intelligence/forecast_ledger.sqlite3-journal",
    }.issubset(ignored)


def test_resolve_rejects_future_resolution_timestamp(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    set_ledger_time(ledger, "2026-11-03T16:30:00Z")
    with pytest.raises(ForecastLedgerError, match="cannot be later than actual ledger recording time"):
        ledger.resolve_forecast(
            forecast_id,
            resolved_at_utc=RESOLVED,
            outcome_price_usd=1.28,
            outcome_price_timestamp_utc=OUTCOME_TIME,
            outcome_venue="kraken:XRP/USD",
            outcome_source_ids=["kraken-outcome-001"],
        )


def test_resolve_rejects_future_outcome_price_timestamp(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    set_ledger_time(ledger, "2026-11-03T17:00:15Z")
    with pytest.raises(ForecastLedgerError, match="outcome_price_timestamp_utc cannot be later than actual ledger recording time"):
        ledger.resolve_forecast(
            forecast_id,
            resolved_at_utc="2026-11-03T17:00:15Z",
            outcome_price_usd=1.28,
            outcome_price_timestamp_utc="2026-11-03T17:00:30Z",
            outcome_venue="kraken:XRP/USD",
            outcome_source_ids=["kraken-outcome-001"],
        )


def test_unscorable_outcome_waits_until_tolerance_window_closes(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    forecast_id = ledger.record_forecast(forecast())
    set_ledger_time(ledger, "2026-11-03T17:00:30Z")
    with pytest.raises(ForecastLedgerError, match="tolerance_seconds window closes"):
        ledger.resolve_forecast(
            forecast_id,
            resolved_at_utc="2026-11-03T17:00:30Z",
            outcome_price_usd=None,
            unscorable_reason="No price within the predeclared target tolerance",
        )
    set_ledger_time(ledger, "2026-11-03T17:01:00Z")
    outcome = ledger.resolve_forecast(
        forecast_id,
        resolved_at_utc="2026-11-03T17:01:00Z",
        outcome_price_usd=None,
        unscorable_reason="No price within the predeclared target tolerance",
    )
    assert outcome["status"] == "unscorable"
    assert outcome["recorded_at_utc"] == "2026-11-03T17:01:00.000000Z"
    assert ledger.events(forecast_id)[-1]["recorded_at_utc"] == "2026-11-03T17:01:00.000000Z"


def test_forecast_recording_requires_a_verified_feature_store(tmp_path):
    clock = MutableClock(datetime(2026, 11, 3, 16, 0, 45, tzinfo=timezone.utc))
    ledger = ForecastLedger(
        tmp_path / "forecasts.sqlite3",
        clock=clock,
        trusted_evaluator_public_keys=_trusted_test_evaluator_keys(),
    )
    _register_readiness_fixtures(ledger)
    clock.set(TEST_NOW)
    with pytest.raises(ForecastLedgerError, match="verified HistoricalFeatureStore"):
        ledger.record_forecast(forecast())


def test_readiness_registration_fails_closed_without_an_external_trust_root(tmp_path):
    fixture = READINESS_FIXTURES[("XRP", 3600)]
    ledger = ForecastLedger(tmp_path / "forecasts.sqlite3", clock=lambda: TEST_NOW)
    with pytest.raises(ForecastLedgerError, match="no trusted independent evaluator public keys"):
        ledger.register_readiness_report(
            fixture["report_bytes"],
            receipt_id=fixture["receipt_id"],
            raw_receipt_bytes=fixture["raw_receipt_bytes"],
        )


def test_production_environment_rejects_test_only_evaluator_key(monkeypatch, tmp_path):
    encoded_key = base64.b64encode(_TEST_EVALUATOR_PUBLIC_KEY).decode("ascii")
    monkeypatch.setenv(
        "BARROT_XRP_EVALUATOR_PUBLIC_KEYS_JSON",
        json.dumps({"test-independent-evaluator": encoded_key}),
    )
    with pytest.raises(ForecastLedgerError, match="test-only evaluator key IDs"):
        ForecastLedger(tmp_path / "forecasts.sqlite3", clock=lambda: TEST_NOW)


def test_readiness_signature_binds_metrics_and_dataset_manifest(tmp_path):
    fixture = READINESS_FIXTURES[("XRP", 3600)]
    report = json.loads(fixture["report_bytes"])
    report["model_metrics"]["mean_brier_score"] = 0.001
    tampered_bytes = json.dumps(
        report, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")
    ledger = ForecastLedger(
        tmp_path / "forecasts.sqlite3",
        clock=lambda: datetime(2026, 11, 3, 16, 0, 45, tzinfo=timezone.utc),
        trusted_evaluator_public_keys=_trusted_test_evaluator_keys(),
    )
    with pytest.raises(ForecastLedgerError, match="signature payload hash"):
        ledger.register_readiness_report(
            tampered_bytes,
            receipt_id="tampered-readiness-report",
            raw_receipt_bytes=fixture["raw_receipt_bytes"],
        )


def test_readiness_attestation_timestamp_is_cryptographically_bound(tmp_path):
    fixture = READINESS_FIXTURES[("XRP", 3600)]
    report = json.loads(fixture["report_bytes"])
    report["evaluator_attestation"]["attested_at_utc"] = "2026-11-03T16:00:41Z"
    report_bytes = json.dumps(
        report, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")
    ledger = ForecastLedger(
        tmp_path / "forecasts.sqlite3",
        clock=lambda: datetime(2026, 11, 3, 16, 0, 45, tzinfo=timezone.utc),
        trusted_evaluator_public_keys=_trusted_test_evaluator_keys(),
    )
    with pytest.raises(ForecastLedgerError, match="signature payload hash"):
        ledger.register_readiness_report(
            report_bytes,
            receipt_id="timestamp-tampered-readiness-report",
            raw_receipt_bytes=fixture["raw_receipt_bytes"],
        )


def test_readiness_rejects_untrusted_evaluator_key(tmp_path):
    fixture = READINESS_FIXTURES[("XRP", 3600)]
    report = json.loads(fixture["report_bytes"])
    report["evaluator_id"] = "untrusted-evaluator"
    _sign_readiness_report(report, key_id="untrusted-evaluator")
    report_bytes = json.dumps(
        report, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")
    ledger = ForecastLedger(
        tmp_path / "forecasts.sqlite3",
        clock=lambda: datetime(2026, 11, 3, 16, 0, 45, tzinfo=timezone.utc),
        trusted_evaluator_public_keys=_trusted_test_evaluator_keys(),
    )
    with pytest.raises(ForecastLedgerError, match="is not trusted"):
        ledger.register_readiness_report(
            report_bytes,
            receipt_id="untrusted-readiness-report",
            raw_receipt_bytes=fixture["raw_receipt_bytes"],
        )


def test_readiness_attestation_must_follow_evaluation_and_precede_registration(tmp_path):
    fixture = READINESS_FIXTURES[("XRP", 3600)]
    for index, (attested_at, expected) in enumerate((
        ("2026-11-03T16:00:20Z", "predates evaluation completion"),
        ("2026-11-03T16:01:00Z", "postdates actual readiness-report registration"),
    )):
        report = json.loads(fixture["report_bytes"])
        _sign_readiness_report(report, attested_at_utc=attested_at)
        report_bytes = json.dumps(
            report, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
        ).encode("utf-8")
        ledger = ForecastLedger(
            tmp_path / f"attestation-time-{index}.sqlite3",
            clock=lambda: datetime(2026, 11, 3, 16, 0, 45, tzinfo=timezone.utc),
            trusted_evaluator_public_keys=_trusted_test_evaluator_keys(),
        )
        with pytest.raises(ForecastLedgerError, match=expected):
            ledger.register_readiness_report(
                report_bytes,
                receipt_id=f"attestation-time-{attested_at}",
                raw_receipt_bytes=fixture["raw_receipt_bytes"],
            )


def test_readiness_requires_candidate_to_beat_every_baseline():
    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    report["baseline_metrics"]["momentum_sign"]["mean_brier_score"] = 0.14
    report["baseline_metrics"]["momentum_sign"]["mean_log_loss"] = 0.40
    with pytest.raises(ForecastLedgerError, match="momentum_sign"):
        _validate_readiness_report(report)


def test_rejects_unknown_or_non_sha256_feature_snapshot(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="SHA-256 snapshot IDs"):
        ledger.record_forecast(forecast(feature_snapshot_ids=["snapshot-001"]))
    with pytest.raises(ForecastLedgerError, match="unavailable or failed integrity"):
        ledger.record_forecast(forecast(feature_snapshot_ids=["f" * 64]))


def test_rejects_feature_snapshot_for_another_asset(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="does not cover asset BTC"):
        ledger.record_forecast(forecast(asset="BTC"))


def test_rejects_forecast_source_manifest_that_differs_from_snapshot_lineage(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="do not exactly match referenced feature lineage"):
        ledger.record_forecast(forecast(source_ids=["kraken-001", "macro-001", "coinbase-001", "binance-001", "okx-001", "unregistered"]))


def test_rejects_underreported_feature_information_timestamp(tmp_path):
    ledger = make_ledger(tmp_path / "forecasts.sqlite3")
    with pytest.raises(ForecastLedgerError, match="must equal the maximum feature information"):
        ledger.record_forecast(forecast(feature_max_timestamp_utc="2026-11-03T15:59:29Z"))


def test_rejects_feature_snapshot_received_after_forecast_cutoff(tmp_path):
    late_store_receipt = datetime(2026, 11, 3, 16, 0, 1, tzinfo=timezone.utc)
    ledger = make_ledger(
        tmp_path / "forecasts.sqlite3",
        store_clock=late_store_receipt,
    )
    with pytest.raises(ForecastLedgerError, match="not captured and stored by the forecast cutoff"):
        ledger.record_forecast(forecast())


def test_rejects_feature_snapshot_data_cutoff_after_forecast_cutoff(tmp_path):
    later_snapshot = build_feature_snapshot(
        [FEATURE_RECORD],
        cutoff_utc="2026-11-03T16:00:01Z",
        captured_at_utc="2026-11-03T16:00:02Z",
    )
    ledger = make_ledger(
        tmp_path / "forecasts.sqlite3",
        store_clock=datetime(2026, 11, 3, 16, 0, 3, tzinfo=timezone.utc),
        snapshot=later_snapshot,
    )
    with pytest.raises(ForecastLedgerError, match="data cutoff exceeds forecast cutoff"):
        ledger.record_forecast(
            forecast(feature_snapshot_ids=[later_snapshot["snapshot_id"]])
        )

def _mutated_readiness_report(mutate):
    fixture = READINESS_FIXTURES[("XRP", 3600)]
    report = json.loads(fixture["report_bytes"])
    mutate(report)
    dataset_bytes = json.dumps(
        report["dataset_manifest"],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    report["dataset_sha256"] = hashlib.sha256(dataset_bytes).hexdigest()
    return report


def test_readiness_rejects_two_differently_labeled_receipts_from_same_publisher():
    def mutate(report):
        manifest = report["dataset_manifest"]
        receipt = manifest["raw_source_receipts"][1]
        uri = "https://www.kraken.com/0/public/Ticker?pair=XRPUSD"
        receipt["source_uri"] = uri
        receipt["independence_group"] = "renamed-kraken-feed"
        canonical = dict(receipt["raw_receipt"])
        canonical.pop("receipt_id")
        canonical["source_uri"] = uri
        receipt_id = hashlib.sha256(
            json.dumps(
                canonical,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            ).encode("utf-8")
        ).hexdigest()
        receipt["raw_receipt"] = {**canonical, "receipt_id": receipt_id}
        receipt["receipt_id"] = receipt_id
        manifest["source_independence_groups"] = ["publisher:kraken.com"]
        report["source_independence_group_count"] = 1

    report = _mutated_readiness_report(mutate)
    with pytest.raises(ForecastLedgerError, match="independently receipted source groups"):
        _validate_readiness_report(report)


def test_readiness_report_rejects_source_data_after_dataset_cutoff():
    report = _mutated_readiness_report(
        lambda value: value["dataset_manifest"]["raw_source_receipts"][0].update(
            source_data_as_of_utc="2026-11-03T15:59:31Z"
        )
    )
    with pytest.raises(ForecastLedgerError, match="source data as-of exceeds dataset cutoff"):
        _validate_readiness_report(report)


def test_readiness_report_rejects_raw_capture_after_evaluation_cutoff():
    report = _mutated_readiness_report(
        lambda value: value["dataset_manifest"]["raw_source_receipts"][0].update(
            captured_at_utc="2026-11-03T15:59:41Z"
        )
    )
    with pytest.raises(ForecastLedgerError, match="capture exceeds evaluation data cutoff"):
        _validate_readiness_report(report)


def test_readiness_report_accepts_capture_after_source_asof_when_available_by_cutoff():
    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    assert report["dataset_manifest"]["raw_source_receipts"][0]["source_data_as_of_utc"] == FEATURE_CUTOFF
    assert report["dataset_manifest"]["raw_source_receipts"][0]["captured_at_utc"] == FEATURE_CAPTURED
    assert _validate_readiness_report(report)["status"] == "PASS"


def test_readiness_report_rejects_noncanonical_raw_receipt_metadata():
    report = _mutated_readiness_report(
        lambda value: value["dataset_manifest"]["raw_source_receipts"][0]["raw_receipt"].update(
            source_uri="https://attacker.example/relabelled-source"
        )
    )
    with pytest.raises(ForecastLedgerError, match="receipt_id does not match canonical receipt metadata"):
        _validate_readiness_report(report)


def test_readiness_report_rejects_raw_receipt_path_traversal():
    def mutate(report):
        receipt = report["dataset_manifest"]["raw_source_receipts"][0]
        canonical = dict(receipt["raw_receipt"])
        canonical.pop("receipt_id")
        canonical["raw_payload_path"] = "../../outside/sha256/" + canonical["raw_content_sha256"] + ".json"
        receipt_id = hashlib.sha256(
            json.dumps(
                canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
            ).encode("utf-8")
        ).hexdigest()
        receipt["raw_receipt"] = {**canonical, "receipt_id": receipt_id}
        receipt["receipt_id"] = receipt_id

    report = _mutated_readiness_report(mutate)
    with pytest.raises(ForecastLedgerError, match="canonical raw path is not bound"):
        _validate_readiness_report(report)


def test_readiness_registration_rechecks_canonical_receipt_payload_size(tmp_path):
    fixture = READINESS_FIXTURES[("XRP", 3600)]
    report = json.loads(fixture["report_bytes"])
    receipt = report["dataset_manifest"]["raw_source_receipts"][0]
    old_receipt_id = receipt["receipt_id"]
    receipt["raw_receipt"]["payload_size_bytes"] += 1
    canonical = dict(receipt["raw_receipt"])
    canonical.pop("receipt_id")
    receipt_id = hashlib.sha256(
        json.dumps(
            canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
        ).encode("utf-8")
    ).hexdigest()
    receipt["raw_receipt"]["receipt_id"] = receipt_id
    receipt["receipt_id"] = receipt_id
    raw_receipt_bytes = dict(fixture["raw_receipt_bytes"])
    raw_receipt_bytes[receipt_id] = raw_receipt_bytes.pop(old_receipt_id)
    dataset_bytes = json.dumps(
        report["dataset_manifest"], sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False
    ).encode("utf-8")
    report["dataset_sha256"] = hashlib.sha256(dataset_bytes).hexdigest()
    _sign_readiness_report(report)
    report_bytes = json.dumps(
        report, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")
    ledger = ForecastLedger(
        tmp_path / "receipt-size.sqlite3",
        clock=lambda: datetime(2026, 11, 3, 16, 0, 45, tzinfo=timezone.utc),
        trusted_evaluator_public_keys=_trusted_test_evaluator_keys(),
    )
    with pytest.raises(ForecastLedgerError, match="payload size does not match canonical receipt bytes"):
        ledger.register_readiness_report(
            report_bytes,
            receipt_id="receipt-size-test",
            raw_receipt_bytes=raw_receipt_bytes,
        )



def test_forecast_ledger_accepts_exact_raw_receipt_archive_schema(tmp_path):
    raw_bytes = b'{"symbol":"XRPUSDT","price":"1.31"}'
    archive = RawReceiptArchive(tmp_path / "raw")
    canonical = archive.store(
        source_id="binance_spot_ticker",
        source_uri="https://api.binance.com/api/v3/ticker/24hr?symbol=XRPUSDT",
        captured_at_utc="2026-11-05T13:00:00.000000Z",
        source_data_as_of_utc="2026-11-05T12:59:59.000000Z",
        raw_bytes=raw_bytes,
        model_eligible=True,
    )
    outer = {
        "source_id": canonical["source_id"],
        "source_uri": canonical["source_uri"],
        "captured_at_utc": canonical["captured_at_utc"],
        "source_data_as_of_utc": canonical["source_data_as_of_utc"],
        "raw_content_sha256": canonical["raw_content_sha256"],
        "receipt_id": canonical["receipt_id"],
        "raw_receipt": canonical,
    }

    verified = _validate_canonical_raw_receipt(outer, 0, raw_bytes)

    assert verified["raw_bytes_retained"] is True
    assert verified["raw_retention_reason"] == ""
    assert verified["raw_content_sha256"] == canonical["raw_content_sha256"]


def test_forecast_ledger_rejects_digest_only_raw_receipt_for_readiness(tmp_path):
    raw_bytes = b'{"symbol":"XRPUSDT","price":"1.31"}'
    archive = RawReceiptArchive(tmp_path / "raw")
    canonical = archive.store(
        source_id="binance_spot_ticker",
        source_uri="https://api.binance.com/api/v3/ticker/24hr?symbol=XRPUSDT",
        captured_at_utc="2026-11-05T13:00:00.000000Z",
        source_data_as_of_utc="2026-11-05T12:59:59.000000Z",
        raw_bytes=raw_bytes,
        model_eligible=True,
        retain_raw_bytes=False,
        raw_retention_reason="publisher redistribution restriction",
    )
    outer = {
        "source_id": canonical["source_id"],
        "source_uri": canonical["source_uri"],
        "captured_at_utc": canonical["captured_at_utc"],
        "source_data_as_of_utc": canonical["source_data_as_of_utc"],
        "raw_content_sha256": canonical["raw_content_sha256"],
        "receipt_id": canonical["receipt_id"],
        "raw_receipt": canonical,
    }

    with pytest.raises(ForecastLedgerError, match="retained raw bytes"):
        _validate_canonical_raw_receipt(outer, 0, raw_bytes)


def test_readiness_report_rejects_embargo_shorter_than_forecast_horizon():
    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    report["embargo_seconds"] = 3599
    with pytest.raises(ForecastLedgerError, match="embargo_seconds must be an integer at least as large as horizon_seconds"):
        _validate_readiness_report(report)


def test_readiness_report_rejects_missing_or_invalid_embargo_policy():
    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    report.pop("purge_policy")
    with pytest.raises(ForecastLedgerError, match="purge_policy must declare"):
        _validate_readiness_report(report)
    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    report["embargo_seconds"] = True
    with pytest.raises(ForecastLedgerError, match="embargo_seconds must be an integer"):
        _validate_readiness_report(report)


def test_readiness_policy_v4_requires_overlap_adjusted_effective_sample_size_and_horizon_sized_embargo():
    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    assert report["schema_version"] == "barrot.xrp.model-readiness.v6"
    assert report["policy_id"] == "xrp_forecast_readiness_v6"
    assert report["effective_sample_size_method"] == "greedy_non_overlapping_target_intervals_v1"
    assert report["out_of_sample_effective_sample_size"] >= 10
    assert report["shadow_evaluation_effective_sample_size"] >= 10
    assert report["embargo_seconds"] >= report["horizon_seconds"]
    assert report["purge_policy"] == "training_start_and_outcome_available_by_cutoff_minus_embargo"
    assert _EVALUATOR_ATTESTATION_DOMAIN == b"BARROT_XRP_MODEL_READINESS_V6\0"


def test_readiness_rejects_missing_or_unsupported_effective_sample_size_method():
    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    report.pop("effective_sample_size_method")
    with pytest.raises(ForecastLedgerError, match="effective_sample_size_method is unsupported"):
        _validate_readiness_report(report)
    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    report["effective_sample_size_method"] = "raw_sample_count_only"
    with pytest.raises(ForecastLedgerError, match="effective_sample_size_method is unsupported"):
        _validate_readiness_report(report)


def test_readiness_rejects_effective_sample_size_below_independent_window_minimum():
    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    report["out_of_sample_effective_sample_size"] = 9
    with pytest.raises(ForecastLedgerError, match="out_of_sample_effective_sample_size must be at least 10"):
        _validate_readiness_report(report)


def test_readiness_rejects_effective_sample_size_above_raw_count_or_horizon_capacity():
    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    report["out_of_sample_effective_sample_size"] = 201
    with pytest.raises(ForecastLedgerError, match="cannot exceed raw sample count"):
        _validate_readiness_report(report)

    report = json.loads(READINESS_FIXTURES[("XRP", 14400)]["report_bytes"])
    report["out_of_sample_effective_sample_size"] += 1
    with pytest.raises(ForecastLedgerError, match="exceeds horizon-span capacity"):
        _validate_readiness_report(report)


def test_readiness_rejects_unspecified_or_circular_bootstrap_sampling_policy():
    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    report["paired_uncertainty"].pop("sampling_policy")
    with pytest.raises(ForecastLedgerError, match="sampling_policy"):
        _validate_readiness_report(report)

    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    report["paired_uncertainty"]["sampling_policy"] = "circular_moving_blocks_v1"
    with pytest.raises(ForecastLedgerError, match="sampling_policy"):
        _validate_readiness_report(report)


def test_forecast_ledger_scalar_validation_helpers_cover_strict_rejections():
    from barrot_agent.evolution.forecast_ledger import _number, _probs, _utc

    with pytest.raises(ForecastLedgerError, match="not valid ISO-8601"):
        _utc("not-a-time", "timestamp")
    with pytest.raises(ForecastLedgerError, match="must include UTC timezone"):
        _utc("2026-11-03T12:00:00-05:00", "timestamp")
    with pytest.raises(ForecastLedgerError, match="must be numeric"):
        _number("not-a-number", "price")
    with pytest.raises(ForecastLedgerError, match="must be finite"):
        _number(float("nan"), "price")
    with pytest.raises(ForecastLedgerError, match="must contain down, flat and up"):
        _probs({"up": 1.0}, "probabilities")


def test_trusted_evaluator_key_loader_rejects_malformed_environment(monkeypatch):
    from barrot_agent.evolution.forecast_ledger import _load_trusted_evaluator_keys

    monkeypatch.setenv("BARROT_XRP_EVALUATOR_PUBLIC_KEYS_JSON", "{")
    with pytest.raises(ForecastLedgerError, match="must contain a JSON object"):
        _load_trusted_evaluator_keys(None)
    monkeypatch.setenv("BARROT_XRP_EVALUATOR_PUBLIC_KEYS_JSON", "[]")
    with pytest.raises(ForecastLedgerError, match="must be a mapping"):
        _load_trusted_evaluator_keys(None)


@pytest.mark.parametrize(
    ("configured", "message"),
    [
        ({" ": _TEST_EVALUATOR_PUBLIC_KEY}, "non-empty strings"),
        ({"external": "not-base64!"}, "not valid base64"),
        ({"external": object()}, "raw bytes or base64"),
        ({"external": b"short"}, "32 Ed25519 public-key bytes"),
        (
            {"external": _TEST_EVALUATOR_PUBLIC_KEY, " external ": _TEST_EVALUATOR_PUBLIC_KEY},
            "must be unique",
        ),
    ],
)
def test_trusted_evaluator_key_loader_rejects_invalid_key_entries(configured, message):
    from barrot_agent.evolution.forecast_ledger import _load_trusted_evaluator_keys

    with pytest.raises(ForecastLedgerError, match=message):
        _load_trusted_evaluator_keys(configured)


def test_trusted_evaluator_key_loader_accepts_raw_and_base64_public_keys(monkeypatch):
    from barrot_agent.evolution.forecast_ledger import _load_trusted_evaluator_keys

    encoded = base64.b64encode(_TEST_EVALUATOR_PUBLIC_KEY).decode("ascii")
    keys = _load_trusted_evaluator_keys(
        {"raw-key": _TEST_EVALUATOR_PUBLIC_KEY, "encoded-key": encoded}
    )
    assert set(keys) == {"raw-key", "encoded-key"}
    monkeypatch.setenv(
        "BARROT_XRP_EVALUATOR_PUBLIC_KEYS_JSON",
        json.dumps({"external-evaluator": encoded}),
    )
    assert set(_load_trusted_evaluator_keys(None)) == {"external-evaluator"}


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("missing_field", "complete evaluator_attestation"),
        ("wrong_scheme", "scheme must be Ed25519"),
        ("blank_key", "key_id is required"),
        ("evaluator_mismatch", "must match the trusted attestation key_id"),
        ("unknown_key", "is not trusted"),
        ("bad_digest", "must be a SHA-256 digest"),
        ("digest_mismatch", "payload hash does not match"),
        ("missing_signature", "signature_base64 is required"),
        ("bad_signature_base64", "not valid base64"),
        ("short_signature", "must contain 64 bytes"),
        ("invalid_signature", "signature verification failed"),
    ],
)
def test_evaluator_attestation_rejects_invalid_signature_contracts(mutation, message):
    from barrot_agent.evolution.forecast_ledger import _verify_evaluator_attestation

    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    attestation = report["evaluator_attestation"]
    if mutation == "missing_field":
        attestation.pop("scheme")
    elif mutation == "wrong_scheme":
        attestation["scheme"] = "RSA"
    elif mutation == "blank_key":
        attestation["key_id"] = " "
    elif mutation == "evaluator_mismatch":
        report["evaluator_id"] = "different-evaluator"
    elif mutation == "unknown_key":
        attestation["key_id"] = "unknown-evaluator"
        report["evaluator_id"] = "unknown-evaluator"
    elif mutation == "bad_digest":
        attestation["signed_payload_sha256"] = "not-a-digest"
    elif mutation == "digest_mismatch":
        attestation["signed_payload_sha256"] = "a" * 64
    elif mutation == "missing_signature":
        attestation["signature_base64"] = ""
    elif mutation == "bad_signature_base64":
        attestation["signature_base64"] = "!"
    elif mutation == "short_signature":
        attestation["signature_base64"] = base64.b64encode(b"short").decode("ascii")
    elif mutation == "invalid_signature":
        attestation["signature_base64"] = base64.b64encode(b"x" * 64).decode("ascii")

    trusted = {"test-independent-evaluator": _TEST_EVALUATOR_PRIVATE_KEY.public_key()}
    with pytest.raises(ForecastLedgerError, match=message):
        _verify_evaluator_attestation(report, trusted, "2026-11-03T16:00:45Z")


def test_evaluator_attestation_requires_a_nonempty_external_trust_root():
    from barrot_agent.evolution.forecast_ledger import _verify_evaluator_attestation

    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    with pytest.raises(ForecastLedgerError, match="no trusted independent evaluator public keys"):
        _verify_evaluator_attestation(report, {}, "2026-11-03T16:00:45Z")


def _raw_receipt_edge_fixture(tmp_path):
    raw_bytes = b'{"symbol":"XRPUSDT","price":"1.31"}'
    archive = RawReceiptArchive(tmp_path / "raw-edge")
    canonical = archive.store(
        source_id="binance_spot_ticker",
        source_uri="https://api.binance.com/api/v3/ticker/24hr?symbol=XRPUSDT",
        captured_at_utc="2026-11-05T13:00:00.000000Z",
        source_data_as_of_utc="2026-11-05T12:59:59.000000Z",
        raw_bytes=raw_bytes,
        model_eligible=True,
    )
    outer = {
        "source_id": canonical["source_id"],
        "source_uri": canonical["source_uri"],
        "captured_at_utc": canonical["captured_at_utc"],
        "source_data_as_of_utc": canonical["source_data_as_of_utc"],
        "raw_content_sha256": canonical["raw_content_sha256"],
        "receipt_id": canonical["receipt_id"],
        "raw_receipt": canonical,
    }
    return outer, raw_bytes


def _rebind_raw_receipt(outer, **updates):
    canonical = dict(outer["raw_receipt"])
    canonical.pop("receipt_id", None)
    canonical.update(updates)
    encoded = json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    receipt_id = hashlib.sha256(encoded).hexdigest()
    outer["raw_receipt"] = {**canonical, "receipt_id": receipt_id}
    outer["receipt_id"] = receipt_id
    return outer


def test_canonical_raw_receipt_requires_a_complete_document_and_exact_fields(tmp_path):
    outer, raw_bytes = _raw_receipt_edge_fixture(tmp_path)
    missing = dict(outer)
    missing.pop("raw_receipt")
    with pytest.raises(ForecastLedgerError, match="complete canonical raw_receipt"):
        _validate_canonical_raw_receipt(missing, 0, raw_bytes)

    unexpected = dict(outer)
    unexpected["raw_receipt"] = {**outer["raw_receipt"], "unreviewed_field": "value"}
    with pytest.raises(ForecastLedgerError, match="exact RawReceiptArchive fields"):
        _validate_canonical_raw_receipt(unexpected, 0, raw_bytes)


@pytest.mark.parametrize(
    ("headers", "message"),
    [
        ("not-an-object", "source_http_headers must be an object"),
        ({"authorization": "Bearer private"}, "invalid HTTP provenance headers"),
        ({"etag": ""}, "invalid HTTP provenance headers"),
        ({"etag": "x" * 513}, "invalid HTTP provenance headers"),
        ({"etag": "bad\nvalue"}, "invalid HTTP provenance headers"),
    ],
)
def test_canonical_raw_receipt_rejects_unapproved_http_provenance_headers(tmp_path, headers, message):
    outer, raw_bytes = _raw_receipt_edge_fixture(tmp_path)
    _rebind_raw_receipt(outer, source_http_headers=headers)
    with pytest.raises(ForecastLedgerError, match=message):
        _validate_canonical_raw_receipt(outer, 0, raw_bytes)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("source_id", "different-source", "source identity"),
        ("captured_at_utc", "2026-11-05T13:00:01.000000Z", "capture time"),
        ("source_data_as_of_utc", "2026-11-05T12:59:58.000000Z", "source data as-of"),
        ("raw_content_sha256", "f" * 64, "raw hash"),
    ],
)
def test_canonical_raw_receipt_binds_outer_identity_and_timestamps(tmp_path, field, value, message):
    outer, raw_bytes = _raw_receipt_edge_fixture(tmp_path)
    outer[field] = value
    with pytest.raises(ForecastLedgerError, match=message):
        _validate_canonical_raw_receipt(outer, 0, raw_bytes)


@pytest.mark.parametrize(
    ("updates", "message"),
    [
        ({"payload_size_bytes": 0}, "payload_size_bytes must be a positive integer"),
        ({"raw_bytes_retained": False, "raw_retention_reason": "retention restriction"}, "requires retained raw bytes"),
        ({"raw_payload_path": "bad\\path"}, "raw payload path is invalid"),
        ({"model_eligible_source": False}, "does not attest an eligible source capture"),
        ({"source_http_date": "bad\nvalue"}, "source HTTP Date is invalid"),
    ],
)
def test_canonical_raw_receipt_rejects_invalid_retention_and_payload_metadata(tmp_path, updates, message):
    outer, raw_bytes = _raw_receipt_edge_fixture(tmp_path)
    _rebind_raw_receipt(outer, **updates)
    with pytest.raises(ForecastLedgerError, match=message):
        _validate_canonical_raw_receipt(outer, 0, raw_bytes)


@pytest.mark.parametrize(
    ("provided_bytes", "message"),
    [
        ("not-bytes", "exact raw payload bytes are required"),
        (b"", "exact raw payload bytes are required"),
        (b"x", "payload size does not match"),
        (b"z" * len(b'{"symbol":"XRPUSDT","price":"1.31"}'), "do not match canonical receipt SHA-256"),
    ],
)
def test_canonical_raw_receipt_verifies_exact_raw_payload_bytes(tmp_path, provided_bytes, message):
    outer, _ = _raw_receipt_edge_fixture(tmp_path)
    with pytest.raises(ForecastLedgerError, match=message):
        _validate_canonical_raw_receipt(outer, 0, provided_bytes)


def test_readiness_report_rejects_non_object_and_invalid_top_level_contract():
    with pytest.raises(ForecastLedgerError, match="must be a JSON object"):
        _validate_readiness_report(None)

    cases = [
        (lambda r: r.update(schema_version="barrot.xrp.model-readiness.v5"), "schema is unsupported"),
        (lambda r: r.update(evaluation_type="baseline_only"), "non-chronological evaluation"),
        (lambda r: r.update(status="BLOCKED"), "has not passed the active forecast policy"),
        (lambda r: r.update(evaluation_id=" "), "evaluation_id must be a non-empty string"),
        (lambda r: r.update(model_version=r["baseline_model_version"]), "distinct from its baseline model"),
        (lambda r: r.update(evaluation_code_sha256="bad"), "evaluation_code_sha256 must be a SHA-256 digest"),
        (lambda r: r.update(horizon_seconds=7200), "horizon_seconds is unsupported"),
        (lambda r: r.update(dataset_manifest=None), "immutable dataset_manifest"),
        (lambda r: r["dataset_manifest"].update(model_eligible=False), "not verified and model eligible"),
        (lambda r: r["dataset_manifest"].update(asset="BTC"), "asset/venue does not match"),
        (lambda r: r["dataset_manifest"].update(feature_ids=["x", "x"]), "feature_ids contains duplicates"),
        (lambda r: r["dataset_manifest"].update(feature_snapshot_ids=["not-a-sha"]), "feature_snapshot_ids must be SHA-256"),
        (lambda r: r["dataset_manifest"].update(data_cutoff_utc=None), "data_cutoff_utc is required"),
        (lambda r: r["dataset_manifest"].update(raw_source_receipts=[]), "needs byte-addressed raw_source_receipts"),
        (lambda r: r["dataset_manifest"]["raw_source_receipts"].__setitem__(0, None), "must be an object"),
        (lambda r: r["dataset_manifest"]["raw_source_receipts"][0].update(source_id=" "), "needs source_id"),
        (lambda r: r["dataset_manifest"]["raw_source_receipts"][0].update(receipt_id=" "), "needs receipt_id"),
        (lambda r: r["dataset_manifest"]["raw_source_receipts"][0].update(raw_content_sha256="bad"), "needs a SHA-256 digest"),
        (lambda r: r["dataset_manifest"]["raw_source_receipts"][0].update(raw_capture_status="digest_only"), "must be byte_complete"),
        (lambda r: r["dataset_manifest"]["raw_source_receipts"][0].update(raw_receipt_sha256_verified=False), "has not verified its raw bytes"),
        (lambda r: r["dataset_manifest"]["raw_source_receipts"][0].update(independence_group=" "), "needs independence_group"),
        (lambda r: r["dataset_manifest"]["raw_source_receipts"][0].update(source_uri="ftp://example.com/data"), "source_uri must be HTTP"),
        (lambda r: r["dataset_manifest"]["raw_source_receipts"][0].update(captured_at_utc="2026-11-03T15:59:20Z"), "capture precedes source data as-of"),
        (lambda r: r["dataset_manifest"].update(source_ids=["kraken-001"]), "source_ids do not exactly match raw receipt sources"),
        (lambda r: r["dataset_manifest"].update(source_independence_groups=["wrong-group"]), "needs at least"),
        (lambda r: r.update(source_independence_group_count=99), "source_independence_group_count does not match"),
        (lambda r: r.update(training_sample_count=99), "training_sample_count must be at least"),
        (lambda r: r.update(shadow_evaluation_effective_sample_size=201), "shadow effective sample size cannot exceed raw sample count"),
        (lambda r: r.update(out_of_sample_end_utc="2026-10-01T01:00:00Z"), "span must cover at least"),
        (lambda r: r.update(
            shadow_evaluation_start_utc="2026-11-03T00:00:00Z",
            shadow_evaluation_end_utc="2026-11-03T10:00:00Z",
            shadow_evaluation_effective_sample_size=11,
        ), "shadow effective sample size exceeds horizon-span capacity"),
        (lambda r: r.update(
            shadow_evaluation_start_utc="2026-10-19T00:00:00Z",
            shadow_evaluation_end_utc="2026-10-20T10:00:00Z",
            shadow_evaluation_effective_sample_size=10,
        ), "shadow evaluation must follow"),
        (lambda r: r.update(leakage_check_status="FAIL"), "leakage check did not pass"),
        (lambda r: r.update(calibration_status="FAIL"), "calibration did not pass"),
        (lambda r: r.update(drift_status="DRIFT"), "drift status is not stable"),
        (lambda r: r.update(shadow_evaluation_status="FAIL"), "shadow evaluation did not pass"),
        (lambda r: r.update(weighted_calibration_error=0.10), "weighted calibration error exceeds"),
        (lambda r: r.update(model_metrics=None), "must include model and baseline metrics"),
        (lambda r: r["baseline_metrics"].pop("volatility_normal"), "missing one or more required baselines"),
        (lambda r: r["baseline_metrics"].update(momentum_sign=None), "baseline metrics for momentum_sign must be an object"),
        (lambda r: r.update(paired_uncertainty=None), "needs paired_uncertainty"),
        (lambda r: r["paired_uncertainty"].update(method="unsupported"), "method is unsupported"),
        (lambda r: r["paired_uncertainty"].update(sampling_policy="circular"), "sampling_policy must use non-circular"),
        (lambda r: r["paired_uncertainty"].update(candidate_model_id="other"), "candidate_model_id must match"),
        (lambda r: r["paired_uncertainty"].update(multiplicity_method="none"), "must use Bonferroni"),
        (lambda r: r["paired_uncertainty"].update(familywise_confidence_level=0.90), "familywise_confidence_level must be in"),
        (lambda r: r["paired_uncertainty"].update(familywise_comparison_count=7), "comparison_count must cover"),
        (lambda r: r["paired_uncertainty"].update(individual_confidence_level=0.90), "confidence intervals do not meet"),
        (lambda r: r["paired_uncertainty"].update(bootstrap_replicates=9999), "bootstrap_replicates must be at least"),
        (lambda r: r["paired_uncertainty"]["out_of_sample"]["comparisons"]["naive_class_prior"]["temporal_moving_block_bootstrap"].update(confidence_level=True), "confidence_level must be a finite number"),
        (lambda r: r["paired_uncertainty"]["out_of_sample"]["comparisons"]["naive_class_prior"]["temporal_moving_block_bootstrap"].update(sampling_diagnostics=None), "missing cadence diagnostics"),
        (lambda r: r["paired_uncertainty"]["out_of_sample"]["comparisons"]["naive_class_prior"]["temporal_moving_block_bootstrap"]["sampling_diagnostics"].update(cadence_source="inferred"), "must use a declared expected cadence"),
        (lambda r: r["paired_uncertainty"]["out_of_sample"]["comparisons"]["naive_class_prior"]["temporal_moving_block_bootstrap"]["sampling_diagnostics"].update(cadence_seconds=0), "cadence_seconds must be positive"),
        (lambda r: r["paired_uncertainty"]["out_of_sample"]["comparisons"]["naive_class_prior"]["source_clustered_moving_block_bootstrap"].update(brier_sampling_diagnostics=None), "missing source-cluster cadence diagnostics"),
        (lambda r: r["paired_uncertainty"]["out_of_sample"]["comparisons"]["naive_class_prior"]["source_clustered_moving_block_bootstrap"]["brier_sampling_diagnostics"].update(per_cluster={}), "per_cluster must cover exactly"),
        (lambda r: r["paired_uncertainty"]["out_of_sample"]["comparisons"]["naive_class_prior"]["temporal_moving_block_bootstrap"].update(brier_difference_ci=[0.1, -0.1]), "lower bound exceeds upper bound"),
        (lambda r: r["paired_uncertainty"]["out_of_sample"].update(status="FAIL"), "out_of_sample window did not pass"),
        (lambda r: r["paired_uncertainty"]["out_of_sample"]["comparisons"].pop("volatility_normal"), "missing a required baseline comparison"),
        (lambda r: r["paired_uncertainty"]["out_of_sample"]["comparisons"].update(naive_class_prior=None), "comparison for naive_class_prior must be an object"),
        (lambda r: r["paired_uncertainty"]["out_of_sample"]["comparisons"]["naive_class_prior"].update(mean_brier_difference_vs_benchmark=0.0), "mean brier difference must favor"),
        (lambda r: r["paired_uncertainty"]["out_of_sample"]["comparisons"]["naive_class_prior"]["temporal_moving_block_bootstrap"].update(status="MISSING"), "temporal interval is not estimated"),
        (lambda r: r["paired_uncertainty"]["out_of_sample"]["comparisons"]["naive_class_prior"]["source_clustered_moving_block_bootstrap"].update(status="MISSING"), "source-clustered interval is not estimated"),
        (lambda r: r["paired_uncertainty"]["out_of_sample"]["comparisons"]["naive_class_prior"]["source_clustered_moving_block_bootstrap"].update(confidence_level=0.5), "source-clustered interval is not familywise-adjusted"),
        (lambda r: r["paired_uncertainty"]["out_of_sample"]["comparisons"]["naive_class_prior"]["source_clustered_moving_block_bootstrap"].update(source_group_ids=["same"] * 5), "source_group_ids must be unique non-empty strings"),
        (lambda r: r["paired_uncertainty"]["out_of_sample"]["comparisons"]["naive_class_prior"]["source_clustered_moving_block_bootstrap"].update(equal_cluster_weighted_mean_brier_difference=0.0), "source-clustered mean brier difference must favor"),
        (lambda r: r.update(evaluation_completed_at_utc="2026-10-21T00:00:00Z"), "evaluation completion precedes"),
    ]

    for mutate, message in cases:
        report = _mutated_readiness_report(mutate)
        with pytest.raises(ForecastLedgerError, match=message):
            _validate_readiness_report(report)


def test_readiness_report_rejects_a_dataset_hash_that_does_not_match_its_manifest():
    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    report["dataset_sha256"] = "f" * 64
    with pytest.raises(ForecastLedgerError, match="dataset manifest SHA-256"):
        _validate_readiness_report(report)


def test_readiness_report_rejects_invalid_raw_receipt_capture_after_evaluation_cutoff():
    report = _mutated_readiness_report(
        lambda value: value["dataset_manifest"]["raw_source_receipts"][0].update(
            captured_at_utc="2026-11-03T16:00:00Z"
        )
    )
    with pytest.raises(ForecastLedgerError, match="capture exceeds evaluation data cutoff"):
        _validate_readiness_report(report)


def test_readiness_certificate_rejects_invalid_and_unregistered_certificates(tmp_path):
    ledger = make_ledger(tmp_path / "certificate-validation.sqlite3")
    valid = forecast()
    assert ledger._verify_readiness_certificate(valid)["status"] == "PASS"

    cases = [
        (lambda p: p.pop("readiness_certificate"), "certificate is required"),
        (lambda p: p["readiness_certificate"].update(report_sha256="bad"), "report_sha256 must be a SHA-256"),
        (lambda p: p["readiness_certificate"].update(receipt_id=" "), "receipt_id is required"),
        (lambda p: p["readiness_certificate"].update(policy_id="other"), "does not match the active forecast policy"),
        (lambda p: p["readiness_certificate"].update(status="BLOCKED"), "does not match the active forecast policy"),
        (lambda p: p["readiness_certificate"].update(report_sha256="f" * 64), "not registered"),
        (lambda p: p["readiness_certificate"].update(receipt_id="different"), "does not match the registered report"),
        (lambda p: p.update(model_version="different"), "model_version does not match"),
        (lambda p: p.update(asset="BTC"), "asset does not match"),
        (lambda p: p.update(venue="different-venue"), "venue does not match"),
        (lambda p: p.update(horizon_seconds=14400), "horizon does not match"),
        (lambda p: p.update(data_cutoff_utc="2026-11-03T15:59:00Z"), "cutoff exceeds forecast cutoff"),
        (lambda p: p.update(issued_at_utc="2026-11-03T16:00:20Z"), "completed after forecast issue time"),
        (lambda p: p.update(issued_at_utc="2026-11-03T16:00:40Z"), "registered after forecast issue time"),
        (lambda p: p.update(source_ids=["kraken-001"]), "source_ids do not match forecast"),
    ]
    for mutate, message in cases:
        payload = json.loads(json.dumps(valid))
        mutate(payload)
        with pytest.raises(ForecastLedgerError, match=message):
            ledger._verify_readiness_certificate(payload)


def test_forecast_normalizer_rejects_remaining_required_and_policy_fields(tmp_path):
    ledger = make_ledger(tmp_path / "normalize-validation.sqlite3")
    with pytest.raises(ForecastLedgerError, match="forecast must be a mapping"):
        ledger._normalize(None)

    cases = [
        (lambda p: p.pop("fee_bps"), "missing fields"),
        (lambda p: p.update(reference_price_max_age_seconds=True), "reference_price_max_age_seconds must be 0..3600"),
        (lambda p: p.update(issued_at_utc="2026-11-03T15:59:00Z"), "issued_at_utc must be >= cutoff"),
        (lambda p: p.update(outcome_tolerance_seconds=True), "outcome_tolerance_seconds must be 0..3600"),
        (lambda p: p.update(asset=" "), "must be non-empty strings"),
        (lambda p: p.update(reference_price_source_id=" "), "reference_price_source_id must be a non-empty string"),
        (lambda p: p.update(readiness_certificate="not-an-object"), "readiness_certificate must be an object"),
        (lambda p: p["readiness_certificate"].update(report_sha256="bad"), "report_sha256 must be a SHA-256"),
        (lambda p: p["readiness_certificate"].update(receipt_id=" "), "receipt_id is required"),
        (lambda p: p["readiness_certificate"].update(policy_id="other"), "does not match the active policy"),
        (lambda p: p.update(source_ids=["macro-001"]), "must be included in source_ids"),
    ]
    for mutate, message in cases:
        payload = json.loads(json.dumps(forecast()))
        mutate(payload)
        with pytest.raises(ForecastLedgerError, match=message):
            ledger._normalize(payload)


def test_feature_snapshot_verifier_rejects_malformed_verified_snapshot_payloads(tmp_path):
    ledger = make_ledger(tmp_path / "snapshot-validation.sqlite3")
    payload = ledger._normalize(forecast())
    report = json.loads(READINESS_FIXTURES[("XRP", 3600)]["report_bytes"])
    snapshot_id = payload["feature_snapshot_ids"][0]
    base = ledger._test_feature_store.verified_snapshot(snapshot_id)

    class SnapshotStub:
        def __init__(self, value):
            self.value = value

        def verified_snapshot(self, requested_id):
            return self.value

    payload_with_duplicate = json.loads(json.dumps(payload))
    payload_with_duplicate["feature_snapshot_ids"] = [snapshot_id, snapshot_id]
    with pytest.raises(ForecastLedgerError, match="feature_snapshot_ids must be unique"):
        ledger._verify_feature_snapshots(payload_with_duplicate, report)

    cases = [
        (lambda s: s.update(snapshot_id="f" * 64), "different snapshot ID"),
        (lambda s: s["verification"].update(valid=False), "integrity is not verified"),
        (lambda s: s.update(manifest={}), "malformed manifest"),
        (lambda s: s["manifest"].update(records=[]), "contains no model-facing records"),
        (lambda s: s["manifest"]["records"][0].update(feature_id=" "), "invalid feature_id"),
        (lambda s: s["manifest"]["records"][0].update(sources="not-a-list"), "source lineage is malformed"),
        (lambda s: s["manifest"]["records"][0]["sources"][0].update(source_id=" "), "invalid source ID"),
        (lambda s: s["manifest"]["records"][0].update(known_at_utc="2026-11-03T16:00:01Z"), "exceeds forecast cutoff"),
        (lambda s: s["manifest"]["records"][0].update(feature_id="xrp.unseen_feature"), "feature IDs absent"),
    ]
    for mutate, message in cases:
        snapshot = json.loads(json.dumps(base))
        mutate(snapshot)
        ledger.feature_store = SnapshotStub(snapshot)
        with pytest.raises(ForecastLedgerError, match=message):
            ledger._verify_feature_snapshots(payload, report)


def test_forecast_ledger_resolve_edges_and_unfiltered_event_query(tmp_path):
    ledger = make_ledger(tmp_path / "resolve-edges.sqlite3")
    with pytest.raises(ForecastLedgerError, match="unknown forecast_id"):
        ledger.resolve_forecast(
            "missing-forecast",
            resolved_at_utc=ISSUED,
            outcome_price_usd=None,
        )

    forecast_id = ledger.record_forecast(forecast())
    assert ledger.get_forecast("missing-forecast") is None
    assert len(ledger.events()) == 1

    set_ledger_time(ledger, "2026-11-03T17:01:00Z")
    with pytest.raises(ForecastLedgerError, match="resolved_at_utc precedes outcome timestamp"):
        ledger.resolve_forecast(
            forecast_id,
            resolved_at_utc="2026-11-03T17:00:45Z",
            outcome_price_usd=1.28,
            outcome_price_timestamp_utc="2026-11-03T17:00:50Z",
            outcome_venue="kraken:XRP/USD",
            outcome_source_ids=["kraken-001"],
        )
    with pytest.raises(ForecastLedgerError, match="outcome_venue required"):
        ledger.resolve_forecast(
            forecast_id,
            resolved_at_utc="2026-11-03T17:00:55Z",
            outcome_price_usd=1.28,
            outcome_price_timestamp_utc="2026-11-03T17:00:50Z",
            outcome_venue=None,
            outcome_source_ids=["kraken-001"],
        )

    set_ledger_time(ledger, "2026-11-03T17:02:00Z")
    with pytest.raises(ForecastLedgerError, match="unscorable_reason required"):
        ledger.resolve_forecast(
            forecast_id,
            resolved_at_utc="2026-11-03T17:02:00Z",
            outcome_price_usd=None,
        )


def test_forecast_ledger_rejects_a_forecast_id_collision(monkeypatch, tmp_path):
    from barrot_agent.evolution import forecast_ledger as ledger_module

    ledger = make_ledger(tmp_path / "forecast-collision.sqlite3")
    monkeypatch.setattr(ledger_module, "_hash", lambda value: "f" * 64)
    ledger.record_forecast(forecast())
    with pytest.raises(ForecastLedgerError, match="forecast ID collision"):
        ledger.record_forecast(forecast(assumptions=["A materially different assumption"]))
