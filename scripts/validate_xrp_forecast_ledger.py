#!/usr/bin/env python3
"""Read-only validation for immutable XRP forecast issuance/outcome JSONL ledgers.

No market data is fetched and no source record is edited. Issuance rows are
immutable; realized outcomes are separate records.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

HASH_RE = re.compile(r"^[a-f0-9]{64}$")
PROBABILITY_CLASSES = {"UP", "DOWN", "FLAT"}
ISSUANCE_FIELDS = {
    "schema_version", "record_type", "forecast_id", "issued_at_utc",
    "data_cutoff_utc", "asset", "target", "horizon_seconds",
    "target_definition", "probabilities", "probability_status",
    "feature_snapshot_sha256", "source_manifest_sha256", "model_version",
    "assumptions", "alternatives", "baseline_model_ids", "resolution_protocol",
    "calibration_artifact_sha256",
}
OUTCOME_FIELDS = {
    "schema_version", "record_type", "outcome_id", "forecast_id",
    "resolved_at_utc", "resolution_data_cutoff_utc", "outcome_status",
    "outcome", "start_price_usd", "end_price_usd", "observed_return_bps",
    "reference_source_id", "reference_snapshot_sha256", "resolution_method",
    "data_quality_flags",
}


def _utc(value: Any, field: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str):
        errors.append(f"{field}: expected ISO-8601 timestamp string")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{field}: invalid ISO-8601 timestamp")
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        errors.append(f"{field}: timezone offset is required")
        return None
    return parsed.astimezone(timezone.utc)


def _hash(value: Any, field: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not HASH_RE.fullmatch(value):
        errors.append(f"{field}: expected 64-character lowercase SHA-256 hex")


def _nonempty(value: Any, field: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field}: expected non-empty string")


def validate_issuance(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ISSUANCE_FIELDS - {"calibration_artifact_sha256"}
    missing = sorted(required - record.keys())
    if missing:
        return ["missing required fields: " + ", ".join(missing)]
    extras = sorted(record.keys() - ISSUANCE_FIELDS)
    if extras:
        errors.append("unknown fields: " + ", ".join(extras))
    if record["schema_version"] != "1.0" or record["record_type"] != "forecast_issuance":
        errors.append("schema_version/record_type mismatch")
    if record["asset"] != "XRP" or record["target"] != "XRP_USD_DIRECTION":
        errors.append("unsupported asset/target")
    for field in ("forecast_id", "target_definition", "model_version"):
        _nonempty(record[field], field, errors)
    issued = _utc(record["issued_at_utc"], "issued_at_utc", errors)
    cutoff = _utc(record["data_cutoff_utc"], "data_cutoff_utc", errors)
    if issued and cutoff and cutoff > issued:
        errors.append("data_cutoff_utc must not be later than issued_at_utc")
    horizon = record["horizon_seconds"]
    if isinstance(horizon, bool) or not isinstance(horizon, int) or horizon <= 0:
        errors.append("horizon_seconds must be a positive integer")
    probs = record["probabilities"]
    if not isinstance(probs, dict) or set(probs) != PROBABILITY_CLASSES:
        errors.append("probabilities must contain exactly UP, DOWN and FLAT")
    else:
        values = list(probs.values())
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or not 0 <= v <= 1 for v in values):
            errors.append("each probability must be finite and within [0, 1]")
        elif abs(sum(values) - 1.0) > 1e-6:
            errors.append("UP/DOWN/FLAT probabilities must sum to 1 within 1e-6")
    status = record["probability_status"]
    if status not in ("CALIBRATED", "UNCALIBRATED"):
        errors.append("probability_status must be CALIBRATED or UNCALIBRATED")
    if status == "CALIBRATED":
        _hash(record.get("calibration_artifact_sha256"), "calibration_artifact_sha256", errors)
    elif "calibration_artifact_sha256" in record:
        errors.append("uncalibrated records must not claim a calibration artifact")
    _hash(record["feature_snapshot_sha256"], "feature_snapshot_sha256", errors)
    _hash(record["source_manifest_sha256"], "source_manifest_sha256", errors)
    for field in ("assumptions", "alternatives", "baseline_model_ids"):
        values = record[field]
        if not isinstance(values, list) or not values or any(not isinstance(v, str) or not v.strip() for v in values):
            errors.append(f"{field} must be a non-empty list of non-empty strings")
    protocol = record["resolution_protocol"]
    protocol_fields = {"reference_source_id", "start_price_definition", "end_price_definition", "neutral_band_bps", "horizon_tolerance_seconds"}
    if not isinstance(protocol, dict) or not protocol_fields.issubset(protocol):
        errors.append("resolution_protocol is missing required fields")
    else:
        extras = sorted(protocol.keys() - protocol_fields)
        if extras:
            errors.append("unknown resolution_protocol fields: " + ", ".join(extras))
        for field in ("reference_source_id", "start_price_definition", "end_price_definition"):
            _nonempty(protocol[field], f"resolution_protocol.{field}", errors)
        band = protocol["neutral_band_bps"]
        tolerance = protocol["horizon_tolerance_seconds"]
        if isinstance(band, bool) or not isinstance(band, (int, float)) or not math.isfinite(band) or band < 0:
            errors.append("resolution_protocol.neutral_band_bps must be finite and non-negative")
        if isinstance(tolerance, bool) or not isinstance(tolerance, int) or tolerance < 0:
            errors.append("resolution_protocol.horizon_tolerance_seconds must be a non-negative integer")
        elif isinstance(horizon, int) and not isinstance(horizon, bool) and tolerance >= horizon:
            errors.append("horizon_tolerance_seconds must be smaller than horizon_seconds")
    return errors


def validate_outcomes(issuances: list[dict[str, Any]], outcomes: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    issuance_by_id: dict[str, dict[str, Any]] = {}
    for index, issuance in enumerate(issuances):
        fid = issuance.get("forecast_id")
        if not isinstance(fid, str) or not fid:
            errors.append(f"issuance[{index}]: missing forecast_id")
        elif fid in issuance_by_id:
            errors.append(f"duplicate forecast_id: {fid}")
        else:
            issuance_by_id[fid] = issuance
    seen_outcome_ids: set[str] = set()
    seen_forecasts: set[str] = set()
    for index, outcome in enumerate(outcomes):
        prefix = f"outcome[{index}]"
        missing = sorted((OUTCOME_FIELDS - {"start_price_usd", "end_price_usd", "observed_return_bps", "data_quality_flags"}) - outcome.keys())
        if missing:
            errors.append(f"{prefix}: missing required fields: " + ", ".join(missing))
            continue
        extras = sorted(outcome.keys() - OUTCOME_FIELDS)
        if extras:
            errors.append(f"{prefix}: unknown fields: " + ", ".join(extras))
        oid = outcome["outcome_id"]
        fid = outcome["forecast_id"]
        if not isinstance(oid, str) or not oid:
            errors.append(f"{prefix}: outcome_id must be non-empty")
        elif oid in seen_outcome_ids:
            errors.append(f"duplicate outcome_id: {oid}")
        else:
            seen_outcome_ids.add(oid)
        if not isinstance(fid, str) or not fid:
            errors.append(f"{prefix}: forecast_id must be non-empty")
            continue
        if fid in seen_forecasts:
            errors.append(f"multiple final outcomes for forecast_id: {fid}")
        else:
            seen_forecasts.add(fid)
        if outcome["schema_version"] != "1.0" or outcome["record_type"] != "forecast_outcome":
            errors.append(f"{prefix}: schema_version/record_type mismatch")
        for field in ("reference_source_id", "resolution_method"):
            _nonempty(outcome[field], f"{prefix}.{field}", errors)
        _hash(outcome["reference_snapshot_sha256"], f"{prefix}.reference_snapshot_sha256", errors)
        resolved = _utc(outcome["resolved_at_utc"], f"{prefix}.resolved_at_utc", errors)
        cutoff = _utc(outcome["resolution_data_cutoff_utc"], f"{prefix}.resolution_data_cutoff_utc", errors)
        if resolved and cutoff and cutoff > resolved:
            errors.append(f"{prefix}: resolution_data_cutoff_utc must not be later than resolved_at_utc")
        issuance = issuance_by_id.get(fid)
        if issuance is None:
            errors.append(f"{prefix}: no matching issuance record for {fid}")
            continue
        issue_errors = validate_issuance(issuance)
        if issue_errors:
            errors.append(f"{prefix}: linked issuance is invalid")
            continue
        issued = _utc(issuance["issued_at_utc"], "issued_at_utc", [])
        horizon = issuance["horizon_seconds"]
        tolerance = issuance["resolution_protocol"]["horizon_tolerance_seconds"]
        earliest_valid_cutoff = (
            issued + timedelta(seconds=horizon - tolerance) if issued else None
        )
        if resolved and earliest_valid_cutoff and resolved < earliest_valid_cutoff:
            errors.append(f"{prefix}: outcome resolved before forecast horizon tolerance")
        if cutoff and earliest_valid_cutoff and cutoff < earliest_valid_cutoff:
            errors.append(f"{prefix}: resolution_data_cutoff_utc is before forecast horizon tolerance")
        expected_source = issuance["resolution_protocol"]["reference_source_id"]
        if outcome["reference_source_id"] != expected_source:
            errors.append(f"{prefix}: reference_source_id differs from predeclared resolution protocol")
        flags = outcome.get("data_quality_flags", [])
        if not isinstance(flags, list) or any(not isinstance(flag, str) or not flag.strip() for flag in flags):
            errors.append(f"{prefix}: data_quality_flags must be a list of non-empty strings")
        status = outcome["outcome_status"]
        label = outcome["outcome"]
        if status not in ("RESOLVED", "UNRESOLVED", "CENSORED"):
            errors.append(f"{prefix}: invalid outcome_status")
        if status == "RESOLVED":
            if label not in ("UP", "DOWN", "FLAT"):
                errors.append(f"{prefix}: RESOLVED outcome must be UP, DOWN or FLAT")
                continue
            start, end, ret = (outcome.get("start_price_usd"), outcome.get("end_price_usd"), outcome.get("observed_return_bps"))
            numeric = (start, end, ret)
            if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in numeric):
                errors.append(f"{prefix}: resolved outcome requires finite start/end prices and observed_return_bps")
                continue
            if start <= 0 or end <= 0:
                errors.append(f"{prefix}: reference prices must be positive")
                continue
            calculated = (end / start - 1.0) * 10000.0
            if abs(calculated - ret) > 0.5:
                errors.append(f"{prefix}: observed_return_bps does not match reference prices")
            band = issuance["resolution_protocol"]["neutral_band_bps"]
            expected = "UP" if calculated > band else "DOWN" if calculated < -band else "FLAT"
            if label != expected:
                errors.append(f"{prefix}: outcome label {label} conflicts with return-derived label {expected}")
        elif label != "UNRESOLVED":
            errors.append(f"{prefix}: UNRESOLVED/CENSORED status requires outcome=UNRESOLVED")
    return errors


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: each JSONL row must be an object")
            records.append(value)
    return records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issuance", required=True, type=Path, help="JSONL forecast issuance ledger")
    parser.add_argument("--outcomes", required=True, type=Path, help="JSONL append-only forecast outcomes ledger")
    args = parser.parse_args(argv)
    try:
        issuances = read_jsonl(args.issuance)
        outcomes = read_jsonl(args.outcomes)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "INVALID", "errors": [str(exc)]}, sort_keys=True))
        return 1
    errors: list[str] = []
    for index, issuance in enumerate(issuances):
        errors.extend(f"issuance[{index}]: {error}" for error in validate_issuance(issuance))
    errors.extend(validate_outcomes(issuances, outcomes))
    print(json.dumps({
        "status": "VALID" if not errors else "INVALID",
        "issuance_records": len(issuances),
        "outcome_records": len(outcomes),
        "errors": errors,
        "source_files_modified": False
    }, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
