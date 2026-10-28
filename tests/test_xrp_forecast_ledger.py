import json
import subprocess
import sys
from pathlib import Path

from scripts.validate_xrp_forecast_ledger import validate_issuance, validate_outcomes

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "data" / "xrp_intelligence" / "schemas"
HASH = "a" * 64


def issuance():
    return {
        "schema_version": "1.0",
        "record_type": "forecast_issuance",
        "forecast_id": "xrp-direction-24h-20261028T100000Z",
        "issued_at_utc": "2026-10-28T10:00:00Z",
        "data_cutoff_utc": "2026-10-28T09:59:00Z",
        "asset": "XRP",
        "target": "XRP_USD_DIRECTION",
        "horizon_seconds": 86400,
        "target_definition": "USD reference price return over the next 24 hours with a +/- 10 bps neutral band.",
        "probabilities": {"UP": 0.45, "DOWN": 0.35, "FLAT": 0.20},
        "probability_status": "UNCALIBRATED",
        "feature_snapshot_sha256": HASH,
        "source_manifest_sha256": "b" * 64,
        "model_version": "synthetic-test-model-1",
        "assumptions": ["All features are available at or before the data cutoff."],
        "alternatives": ["Risk-off macro shock", "USDC route substitution", "No measurable event effect"],
        "baseline_model_ids": ["always_flat_v1", "expanding_majority_v1"],
        "resolution_protocol": {
            "reference_source_id": "SYNTHETIC-TEST-PRICE-SOURCE",
            "start_price_definition": "First eligible reference close at or after issued_at_utc.",
            "end_price_definition": "First eligible reference close at or after issued_at_utc plus horizon_seconds.",
            "neutral_band_bps": 10.0,
            "horizon_tolerance_seconds": 300
        }
    }


def outcome(label="UP"):
    return {
        "schema_version": "1.0",
        "record_type": "forecast_outcome",
        "outcome_id": "outcome-001",
        "forecast_id": "xrp-direction-24h-20261028T100000Z",
        "resolved_at_utc": "2026-10-29T10:00:00Z",
        "resolution_data_cutoff_utc": "2026-10-29T09:59:00Z",
        "outcome_status": "RESOLVED",
        "outcome": label,
        "start_price_usd": 1.0,
        "end_price_usd": 1.02,
        "observed_return_bps": 200.0,
        "reference_source_id": "SYNTHETIC-TEST-PRICE-SOURCE",
        "reference_snapshot_sha256": "c" * 64,
        "resolution_method": "Synthetic fixture; not market data.",
        "data_quality_flags": []
    }


def test_schema_files_are_valid_json_and_capture_point_in_time_provenance():
    issuance_schema = json.loads((SCHEMA_DIR / "forecast_issuance.schema.json").read_text())
    outcome_schema = json.loads((SCHEMA_DIR / "forecast_outcome.schema.json").read_text())
    assert issuance_schema["$schema"].endswith("/2020-12/schema")
    assert outcome_schema["$schema"].endswith("/2020-12/schema")
    assert "data_cutoff_utc" in issuance_schema["required"]
    assert "feature_snapshot_sha256" in issuance_schema["required"]
    assert "source_manifest_sha256" in issuance_schema["required"]
    assert "resolution_data_cutoff_utc" in outcome_schema["required"]
    assert "reference_snapshot_sha256" in outcome_schema["required"]


def test_valid_synthetic_issuance_passes():
    assert validate_issuance(issuance()) == []


def test_future_data_cutoff_is_rejected():
    record = issuance()
    record["data_cutoff_utc"] = "2026-10-28T10:00:01Z"
    assert any("must not be later" in error for error in validate_issuance(record))


def test_probabilities_must_sum_to_one():
    record = issuance()
    record["probabilities"] = {"UP": 0.45, "DOWN": 0.35, "FLAT": 0.25}
    assert any("sum to 1" in error for error in validate_issuance(record))


def test_calibrated_probability_requires_calibration_artifact():
    record = issuance()
    record["probability_status"] = "CALIBRATED"
    assert any("calibration_artifact_sha256" in error for error in validate_issuance(record))


def test_valid_outcome_passes_without_mutating_issuance():
    issued = issuance()
    before = json.dumps(issued, sort_keys=True)
    assert validate_outcomes([issued], [outcome()]) == []
    assert json.dumps(issued, sort_keys=True) == before


def test_outcome_before_horizon_is_rejected():
    early = outcome()
    early["resolved_at_utc"] = "2026-10-29T09:00:00Z"
    early["resolution_data_cutoff_utc"] = "2026-10-29T08:59:00Z"
    assert any("before forecast horizon" in error for error in validate_outcomes([issuance()], [early]))


def test_outcome_label_must_match_reference_price_return():
    assert any("conflicts with return-derived label" in error for error in validate_outcomes([issuance()], [outcome("DOWN")]))


def test_outcome_resolution_source_must_match_predeclared_source():
    mismatched = outcome()
    mismatched["reference_source_id"] = "different-source"
    assert any(
        "differs from predeclared resolution protocol" in error
        for error in validate_outcomes([issuance()], [mismatched])
    )


def test_resolution_cutoff_must_cover_horizon_within_tolerance():
    early_cutoff = outcome()
    early_cutoff["resolution_data_cutoff_utc"] = "2026-10-29T09:54:59Z"
    assert any(
        "resolution_data_cutoff_utc is before forecast horizon tolerance" in error
        for error in validate_outcomes([issuance()], [early_cutoff])
    )


def test_data_quality_flags_must_be_nonempty_strings():
    malformed = outcome()
    malformed["data_quality_flags"] = ["", 7]
    assert any(
        "data_quality_flags must be a list of non-empty strings" in error
        for error in validate_outcomes([issuance()], [malformed])
    )


def test_unknown_forecast_and_duplicate_final_outcomes_are_rejected():
    missing = outcome()
    missing["forecast_id"] = "unknown-forecast"
    assert any("no matching issuance" in error for error in validate_outcomes([issuance()], [missing]))
    first = outcome()
    second = outcome()
    second["outcome_id"] = "outcome-002"
    assert any("multiple final outcomes" in error for error in validate_outcomes([issuance()], [first, second]))


def test_cli_is_read_only_and_reports_valid_synthetic_ledgers(tmp_path):
    issuance_path = tmp_path / "issuance.jsonl"
    outcome_path = tmp_path / "outcomes.jsonl"
    issuance_path.write_text(json.dumps(issuance()) + "\n", encoding="utf-8")
    outcome_path.write_text(json.dumps(outcome()) + "\n", encoding="utf-8")
    before = (issuance_path.read_bytes(), outcome_path.read_bytes())
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_xrp_forecast_ledger.py"),
         "--issuance", str(issuance_path), "--outcomes", str(outcome_path)],
        check=False, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["status"] == "VALID"
    assert report["source_files_modified"] is False
    assert before == (issuance_path.read_bytes(), outcome_path.read_bytes())
