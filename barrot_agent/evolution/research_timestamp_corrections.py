"""Preimage-bound timestamp corrections for append-only XRP research artifacts."""
from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .research_eligibility import (
    ResearchEligibilityError,
    _SHA1,
    _canonical_json,
    _json_object,
    _repo_path,
    _sha256,
    _timestamp,
    git_blob_sha1,
)

_TIMESTAMP_CORRECTION_TARGETS = {
    "source_event_time_utc": "source_event_date",
    "page_checked_at_utc": "issuer_file_timestamps_utc",
}


def _utc_timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ResearchEligibilityError(f"{field} must be a timezone-aware UTC timestamp")
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ResearchEligibilityError(f"{field} must be a timezone-aware UTC timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ResearchEligibilityError(f"{field} must include a UTC timezone offset")
    return parsed.astimezone(timezone.utc)


def _validate_issuer_file_timestamps(value: Any, field: str) -> None:
    if not isinstance(value, Mapping) or not value:
        raise ResearchEligibilityError(f"{field} must be a non-empty issuer timestamp mapping")
    for issuer, stamp in value.items():
        if not isinstance(issuer, str) or not issuer.strip():
            raise ResearchEligibilityError(f"{field} contains an invalid issuer key")
        if isinstance(stamp, Mapping):
            if set(stamp) != {"start", "end"}:
                raise ResearchEligibilityError(f"{field}.{issuer} must contain exactly start and end")
            start = _utc_timestamp(stamp.get("start"), f"{field}.{issuer}.start")
            end = _utc_timestamp(stamp.get("end"), f"{field}.{issuer}.end")
            if end < start:
                raise ResearchEligibilityError(f"{field}.{issuer} end precedes start")
        else:
            _utc_timestamp(stamp, f"{field}.{issuer}")


def apply_source_timestamp_correction_overlay(
    *,
    source_artifact_path: str,
    source_artifact_bytes: bytes,
    overlay_artifact_path: str,
    overlay_artifact_bytes: bytes,
) -> dict[str, Any]:
    """Apply a timestamp overlay to an in-memory research view; never write or promote.

    Only two timestamp semantics are supported: remove a synthetic exact event
    time and replace it with the publisher's calendar date; or remove a page
    check timestamp that was actually an issuer-file timestamp and preserve
    the per-issuer timestamps separately. Market values and raw-source hashes
    are never modified.
    """
    source_path = _repo_path(source_artifact_path, "source_artifact_path")
    overlay_path = _repo_path(overlay_artifact_path, "overlay_artifact_path")
    if source_path == overlay_path:
        raise ResearchEligibilityError("source and overlay artifact paths must be different")
    source_document = _json_object(source_artifact_bytes, "source artifact")
    overlay_document = _json_object(overlay_artifact_bytes, "timestamp correction overlay")

    source_blob_sha = git_blob_sha1(source_artifact_bytes)
    overlay_blob_sha = git_blob_sha1(overlay_artifact_bytes)
    source_content_sha256 = _sha256(source_artifact_bytes)
    overlay_content_sha256 = _sha256(overlay_artifact_bytes)

    if overlay_document.get("schema_version") != "barrot.xrp.research-correction.v1":
        raise ResearchEligibilityError("unsupported timestamp correction schema_version")
    if overlay_document.get("artifact_type") != "append_only_source_timestamp_semantics_correction":
        raise ResearchEligibilityError("overlay artifact_type is not a source timestamp correction")
    artifact_id = overlay_document.get("artifact_id")
    if not isinstance(artifact_id, str) or not artifact_id.strip():
        raise ResearchEligibilityError("timestamp correction artifact_id is required")
    if overlay_document.get("target_artifact") != source_path:
        raise ResearchEligibilityError("overlay target_artifact does not match the supplied source path")
    declared_source_sha = overlay_document.get("target_artifact_blob_sha")
    if not isinstance(declared_source_sha, str) or not _SHA1.fullmatch(declared_source_sha):
        raise ResearchEligibilityError("overlay target_artifact_blob_sha must be a Git blob SHA-1")
    if declared_source_sha != source_blob_sha:
        raise ResearchEligibilityError("overlay target_artifact_blob_sha does not match exact source bytes")

    preservation = overlay_document.get("preservation")
    if not isinstance(preservation, Mapping):
        raise ResearchEligibilityError("timestamp correction preservation declaration is required")
    required_false = (
        "target_artifact_modified",
        "raw_source_text_hashes_modified",
        "forecast_issued",
        "model_eligible",
    )
    if any(preservation.get(key) is not False for key in required_false):
        raise ResearchEligibilityError(
            "timestamp overlay must preserve source, raw hashes, forecast state and ineligibility"
        )
    if preservation.get("correction_mode") != "append_only_field_overlay":
        raise ResearchEligibilityError("timestamp overlay must use append_only_field_overlay mode")
    if overlay_document.get("model_eligible") is not False or overlay_document.get("forecast_issued") is not False:
        raise ResearchEligibilityError("timestamp overlay cannot promote model eligibility or claim a forecast")

    admission = source_document.get("admission")
    admission_eligible = admission.get("model_eligible") if isinstance(admission, Mapping) else None
    source_eligible = source_document.get("model_eligible")
    if source_eligible is True or admission_eligible is True:
        raise ResearchEligibilityError("timestamp corrections cannot be applied to a model-eligible source artifact")
    if source_eligible is not False and admission_eligible is not False:
        raise ResearchEligibilityError("source artifact must explicitly remain model ineligible")
    forecast = source_document.get("forecast")
    if not isinstance(forecast, Mapping) or forecast.get("issued") is not False:
        raise ResearchEligibilityError("source artifact must explicitly record that no forecast was issued")

    registry = source_document.get("source_registry")
    if not isinstance(registry, list) or not registry:
        raise ResearchEligibilityError("source artifact needs a non-empty source_registry")
    indexed: dict[str, dict[str, Any]] = {}
    source_order: list[str] = []
    for index, item in enumerate(registry):
        if not isinstance(item, Mapping):
            raise ResearchEligibilityError(f"source_registry[{index}] must be an object")
        source_id = item.get("source_id")
        if not isinstance(source_id, str) or not source_id.strip():
            raise ResearchEligibilityError(f"source_registry[{index}] needs a source_id")
        source_id = source_id.strip()
        if source_id in indexed:
            raise ResearchEligibilityError("source_registry contains duplicate source_id values")
        indexed[source_id] = dict(item)
        source_order.append(source_id)

    prior_applications = source_document.get("correction_applications", [])
    if not isinstance(prior_applications, list):
        raise ResearchEligibilityError("correction_applications must be an array")
    if any(isinstance(item, Mapping) and item.get("artifact_id") == artifact_id for item in prior_applications):
        raise ResearchEligibilityError("timestamp correction overlay was already applied")

    entries = overlay_document.get("field_corrections")
    if not isinstance(entries, list) or not entries:
        raise ResearchEligibilityError("timestamp overlay field_corrections must be a non-empty array")

    seen: set[tuple[str, str]] = set()
    applied: list[dict[str, Any]] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            raise ResearchEligibilityError(f"field_corrections[{index}] must be an object")
        source_id = entry.get("source_id")
        target_field = entry.get("target_field")
        if not isinstance(source_id, str) or source_id.strip() not in indexed:
            raise ResearchEligibilityError(f"field_corrections[{index}] references an unknown source_id")
        source_id = source_id.strip()
        if not isinstance(target_field, str) or target_field not in _TIMESTAMP_CORRECTION_TARGETS:
            raise ResearchEligibilityError(f"field_corrections[{index}] targets a non-allowlisted timestamp field")
        key = (source_id, target_field)
        if key in seen:
            raise ResearchEligibilityError("timestamp overlay contains duplicate source/field corrections")
        seen.add(key)

        source_item = indexed[source_id]
        if target_field not in source_item:
            raise ResearchEligibilityError(f"{source_id}.{target_field} is absent from the exact source artifact")
        expected = entry.get("expected_original_value")
        if source_item[target_field] != expected:
            raise ResearchEligibilityError(f"{source_id}.{target_field} does not match the declared preimage")
        original_timestamp = _utc_timestamp(expected, f"{source_id}.{target_field}")
        if entry.get("replacement_value", object()) is not None:
            raise ResearchEligibilityError("timestamp correction may only remove unsupported exact timestamps")

        canonical_field = entry.get("canonical_field")
        expected_canonical_field = _TIMESTAMP_CORRECTION_TARGETS[target_field]
        if canonical_field != expected_canonical_field:
            raise ResearchEligibilityError(f"{source_id}.{target_field} has an unsupported canonical field")
        canonical_value = entry.get("canonical_field_value")
        if canonical_field == "source_event_date":
            if not isinstance(canonical_value, str):
                raise ResearchEligibilityError("source_event_date must be an ISO calendar date")
            try:
                parsed_date = date.fromisoformat(canonical_value)
            except ValueError as exc:
                raise ResearchEligibilityError("source_event_date must be an ISO calendar date") from exc
            if parsed_date.isoformat() != canonical_value:
                raise ResearchEligibilityError("source_event_date must use canonical YYYY-MM-DD form")
            if original_timestamp.date().isoformat() != canonical_value:
                raise ResearchEligibilityError("source_event_date must match the removed timestamp's UTC calendar date")
        else:
            _validate_issuer_file_timestamps(canonical_value, f"{source_id}.{canonical_field}")

        if canonical_field in source_item and source_item[canonical_field] != canonical_value:
            raise ResearchEligibilityError(f"{source_id}.{canonical_field} already has a conflicting value")
        reason = entry.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            raise ResearchEligibilityError(f"field_corrections[{index}] needs a non-empty reason")
        if entry.get("model_eligible") is not False:
            raise ResearchEligibilityError("timestamp corrections may not promote model eligibility")

        source_item[target_field] = None
        source_item[canonical_field] = canonical_value
        applied.append({
            "source_id": source_id,
            "target_field": target_field,
            "expected_original_value": expected,
            "replacement_value": None,
            "canonical_field": canonical_field,
            "canonical_field_value": canonical_value,
            "reason": reason.strip(),
            "model_eligible": False,
        })

    corrected_document = _json_object(source_artifact_bytes, "source artifact")
    corrected_document["source_registry"] = [indexed[source_id] for source_id in source_order]
    manifest = {
        "artifact_id": artifact_id.strip(),
        "overlay_artifact_path": overlay_path,
        "overlay_git_blob_sha1": overlay_blob_sha,
        "overlay_content_sha256": overlay_content_sha256,
        "target_artifact_path": source_path,
        "target_git_blob_sha1": source_blob_sha,
        "target_content_sha256": source_content_sha256,
        "application_status": "APPLIED_TO_IN_MEMORY_RESEARCH_VIEW_ONLY",
        "model_eligibility_effect": "NO_PROMOTION_SOURCE_REMAINS_INELIGIBLE",
        "corrections": applied,
    }
    corrected_document.setdefault("correction_applications", []).append(manifest)
    return {
        "corrected_document": corrected_document,
        "application_manifest": manifest,
        "corrected_document_sha256": _sha256(_canonical_json(corrected_document).encode("utf-8")),
        "source_artifact_preserved": True,
        "model_eligible": False,
        "forecast_issued": False,
    }


_CAPTURE_TIME_OVERLAY_TYPE = "append_only_xrp_research_timestamp_correction"
_CAPTURE_TIME_OVERLAY_SCHEMA = 1
_TIMESTAMP_OVERLAY_TYPES = {
    "append_only_source_timestamp_semantics_correction",
    _CAPTURE_TIME_OVERLAY_TYPE,
}
_MISSING = object()


def _nested_value(document: Mapping[str, Any], dotted_path: str) -> Any:
    current: Any = document
    for part in dotted_path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return _MISSING
        current = current[part]
    return current


def _set_nested_value(document: dict[str, Any], dotted_path: str, value: Any) -> None:
    parts = dotted_path.split(".")
    current: dict[str, Any] = document
    for part in parts[:-1]:
        child = current.get(part)
        if not isinstance(child, dict):
            raise ResearchEligibilityError(f"{dotted_path} does not resolve to a mutable object")
        current = child
    current[parts[-1]] = value


def apply_capture_time_interval_correction_overlay(
    *,
    source_artifact_path: str,
    source_artifact_bytes: bytes,
    overlay_artifact_path: str,
    overlay_artifact_bytes: bytes,
) -> dict[str, Any]:
    """Apply the legacy run-start correction without inventing retrieval times.

    The legacy overlay schema predates the canonical field-overlay schema. Its
    exact Git-blob preimage is still mandatory. Only the top-level run-start
    labels, the Kraken spot retrieval label, and source-registry retrieval
    labels that exactly equal the run start are removed. Provider update times
    and ETF data dates are preserved. The result is an in-memory view only.
    """
    source_path = _repo_path(source_artifact_path, "source_artifact_path")
    overlay_path = _repo_path(overlay_artifact_path, "overlay_artifact_path")
    if source_path == overlay_path:
        raise ResearchEligibilityError("source and overlay artifact paths must be different")

    source_document = _json_object(source_artifact_bytes, "source artifact")
    overlay = _json_object(overlay_artifact_bytes, "capture-time correction overlay")
    source_blob_sha = git_blob_sha1(source_artifact_bytes)
    overlay_blob_sha = git_blob_sha1(overlay_artifact_bytes)
    source_content_sha256 = _sha256(source_artifact_bytes)
    overlay_content_sha256 = _sha256(overlay_artifact_bytes)

    if type(overlay.get("schema_version")) is not int or overlay["schema_version"] != _CAPTURE_TIME_OVERLAY_SCHEMA:
        raise ResearchEligibilityError("unsupported capture-time correction schema_version")
    if overlay.get("artifact_type") != _CAPTURE_TIME_OVERLAY_TYPE:
        raise ResearchEligibilityError("artifact is not the supported capture-time correction type")
    correction_id = overlay.get("correction_id")
    if not isinstance(correction_id, str) or not correction_id.strip():
        raise ResearchEligibilityError("capture-time correction_id is required")
    if overlay.get("source_artifact_path") != source_path:
        raise ResearchEligibilityError("source_artifact_path does not match the supplied source")
    declared_blob = overlay.get("source_artifact_blob_sha")
    if not isinstance(declared_blob, str) or not _SHA1.fullmatch(declared_blob):
        raise ResearchEligibilityError("source_artifact_blob_sha must be a Git blob SHA-1")
    if declared_blob != source_blob_sha:
        raise ResearchEligibilityError("source_artifact_blob_sha does not match exact source bytes")
    source_commit = overlay.get("source_artifact_commit_sha")
    if not isinstance(source_commit, str) or not _SHA1.fullmatch(source_commit):
        raise ResearchEligibilityError("source_artifact_commit_sha must be a 40-character commit SHA")

    run_started = _utc_timestamp(overlay.get("run_started_at_utc"), "run_started_at_utc")
    lower_bound = _utc_timestamp(overlay.get("retrieval_time_lower_bound_utc"), "retrieval_time_lower_bound_utc")
    upper_bound = _utc_timestamp(overlay.get("retrieval_time_upper_bound_utc"), "retrieval_time_upper_bound_utc")
    committed = _utc_timestamp(overlay.get("artifact_committed_at_utc"), "artifact_committed_at_utc")
    conservative = _utc_timestamp(overlay.get("conservative_known_at_utc"), "conservative_known_at_utc")
    if overlay.get("exact_retrieval_time_utc") is not None:
        raise ResearchEligibilityError("exact retrieval time must remain unknown")
    if lower_bound < run_started or upper_bound < lower_bound or committed < upper_bound:
        raise ResearchEligibilityError("capture-time bounds are inconsistent")
    if conservative != upper_bound:
        raise ResearchEligibilityError("conservative known-at must equal the retrieval upper bound")
    if overlay.get("original_claimed_captured_at_utc") != overlay.get("run_started_at_utc"):
        raise ResearchEligibilityError("original claimed capture time must identify the run-start label")
    if source_document.get("captured_at_utc") != overlay.get("original_claimed_captured_at_utc"):
        raise ResearchEligibilityError("source captured_at_utc does not match the declared preimage")
    if source_document.get("data_cutoff_utc") != overlay.get("original_claimed_captured_at_utc"):
        raise ResearchEligibilityError("source data_cutoff_utc does not match the declared preimage")

    policy = overlay.get("point_in_time_policy")
    if not isinstance(policy, Mapping):
        raise ResearchEligibilityError("point_in_time_policy is required")
    if (
        policy.get("use_exact_retrieval_time") is not False
        or policy.get("may_be_used_for_earlier_cutoffs") is not False
        or policy.get("model_eligible") is not False
        or policy.get("conservative_availability_cutoff_utc") != overlay.get("conservative_known_at_utc")
    ):
        raise ResearchEligibilityError("capture-time point-in-time policy must remain conservative and ineligible")
    if overlay.get("directional_forecast_issued") is not False:
        raise ResearchEligibilityError("capture-time correction cannot claim a directional forecast")

    application = overlay.get("correction_application")
    if not isinstance(application, Mapping) or (
        application.get("original_artifact_modified") is not False
        or application.get("append_only_overlay_created") is not True
        or application.get("must_be_reconciled_with_timestamp_consumer_before_any_model_admission") is not True
    ):
        raise ResearchEligibilityError("capture-time correction must preserve the original artifact and require reconciliation")

    facts = overlay.get("preserved_facts")
    if not isinstance(facts, Mapping):
        raise ResearchEligibilityError("preserved_facts is required")
    if (
        facts.get("kraken_response_body_text_preserved") is not True
        or facts.get("numeric_market_values_changed") is not False
        or facts.get("source_urls_changed") is not False
        or facts.get("provider_event_timestamp_for_kraken_spot") is not None
        or facts.get("etf_data_as_of_dates_preserved") is not True
    ):
        raise ResearchEligibilityError("capture-time correction does not preserve source facts")

    admission = source_document.get("model_admission")
    if not isinstance(admission, Mapping) or (
        admission.get("eligible") is not False
        or admission.get("directional_forecast_issued") is not False
    ):
        raise ResearchEligibilityError("source artifact must remain explicitly model-ineligible with no forecast")
    preservation = source_document.get("preservation")
    if not isinstance(preservation, Mapping) or (
        preservation.get("original_artifacts_modified") is not False
        or preservation.get("directional_forecast_issued") is not False
        or preservation.get("paper_trade_executed") is not False
        or preservation.get("real_money_action") is not False
        or preservation.get("external_mutation") is not False
    ):
        raise ResearchEligibilityError("source artifact preservation declarations are incomplete")

    snapshot = source_document.get("market_snapshot")
    if not isinstance(snapshot, Mapping):
        raise ResearchEligibilityError("source market_snapshot is required")
    spot = snapshot.get("kraken_spot")
    if not isinstance(spot, Mapping):
        raise ResearchEligibilityError("source Kraken spot record is required")
    expected_spot_time = _nested_value(
        overlay, "superseded_fields.market_snapshot.kraken_spot.retrieved_at_utc.old_value"
    )
    if expected_spot_time != overlay.get("original_claimed_captured_at_utc"):
        raise ResearchEligibilityError("Kraken spot correction does not identify the synthetic run-start value")
    if spot.get("retrieved_at_utc") != expected_spot_time:
        raise ResearchEligibilityError("Kraken spot retrieval field does not match the declared preimage")

    raw_text = spot.get("raw_response_body_text")
    raw_hash = spot.get("raw_response_body_text_sha256")
    if not isinstance(raw_text, str) or not isinstance(raw_hash, str) or _sha256(raw_text.encode("utf-8")) != raw_hash:
        raise ResearchEligibilityError("preserved Kraken response text does not match its SHA-256 receipt")
    if facts.get("kraken_response_body_sha256") != raw_hash:
        raise ResearchEligibilityError("overlay Kraken response hash does not match the source artifact")

    source_records = source_document.get("sources")
    if not isinstance(source_records, list) or not source_records:
        raise ResearchEligibilityError("source artifact needs a non-empty sources array")
    source_ids: set[str] = set()
    for index, record in enumerate(source_records):
        if not isinstance(record, dict):
            raise ResearchEligibilityError(f"sources[{index}] must be an object")
        source_id = record.get("id")
        if not isinstance(source_id, str) or not source_id.strip() or source_id in source_ids:
            raise ResearchEligibilityError("sources must have unique non-empty id values")
        source_ids.add(source_id)
        if record.get("retrieval_time_utc") != overlay.get("original_claimed_captured_at_utc"):
            raise ResearchEligibilityError(f"sources[{index}] retrieval time does not match the synthetic run-start value")

    provider_checks = (
        (
            "kraken_perpetuals",
            "kraken_futures_provider_update_time_utc",
        ),
        (
            "tradradar_aggregate",
            "tradradar_provider_update_time_utc",
        ),
    )
    no_op_claims: list[dict[str, Any]] = []
    for section, fact_key in provider_checks:
        section_value = snapshot.get(section)
        if not isinstance(section_value, Mapping):
            raise ResearchEligibilityError(f"source market_snapshot.{section} is required")
        provider_time = facts.get(fact_key)
        if not isinstance(provider_time, str) or section_value.get("observed_at_utc") != provider_time:
            raise ResearchEligibilityError(f"{section} provider update time does not match the preserved fact")
        retrieval_field = section_value.get("retrieved_at_utc", _MISSING)
        if retrieval_field is not _MISSING:
            if retrieval_field != overlay.get("original_claimed_captured_at_utc"):
                raise ResearchEligibilityError(f"{section}.retrieved_at_utc does not match the declared preimage")
            no_op_claims.append({"path": f"market_snapshot.{section}.retrieved_at_utc", "status": "CLEARED"})
        else:
            no_op_claims.append({
                "path": f"market_snapshot.{section}.retrieved_at_utc",
                "status": "ABSENT_IN_SOURCE; provider observed_at_utc preserved",
            })

    etf = source_document.get("etf_flow_reconciliation")
    if not isinstance(etf, Mapping) or not isinstance(etf.get("observations"), list):
        raise ResearchEligibilityError("source ETF observations are required")
    etf_index = {
        item.get("source_id"): item
        for item in etf["observations"]
        if isinstance(item, Mapping) and isinstance(item.get("source_id"), str)
    }
    etf_corrections = overlay.get("superseded_fields", {}).get("etf_flow_reconciliation")
    if not isinstance(etf_corrections, Mapping):
        raise ResearchEligibilityError("ETF timestamp correction declarations are required")
    for source_id, date_field in (
        ("XRP_INSIGHTS_ETF_20261105", "data_as_of"),
        ("ALPHA_FINANCE_XRP_ETF_20261105", "data_through"),
    ):
        source_item = etf_index.get(source_id)
        correction = etf_corrections.get(source_id)
        if not isinstance(source_item, Mapping) or not isinstance(correction, Mapping):
            raise ResearchEligibilityError(f"ETF source {source_id} is missing from the declared correction")
        if source_item.get(date_field) != correction.get(date_field):
            raise ResearchEligibilityError(f"ETF source {source_id} date does not match the preserved source date")
        old = correction.get("retrieval_time_utc")
        if not isinstance(old, Mapping) or old.get("old_value") != overlay.get("original_claimed_captured_at_utc"):
            raise ResearchEligibilityError(f"ETF source {source_id} retrieval-time correction is malformed")
        if "retrieval_time_utc" in source_item:
            if source_item["retrieval_time_utc"] != old["old_value"]:
                raise ResearchEligibilityError(f"ETF source {source_id} retrieval time does not match its preimage")
            no_op_claims.append({"path": f"etf_flow_reconciliation.{source_id}.retrieval_time_utc", "status": "CLEARED"})
        else:
            no_op_claims.append({
                "path": f"etf_flow_reconciliation.{source_id}.retrieval_time_utc",
                "status": "ABSENT_IN_SOURCE; publisher data date preserved",
            })

    source_retrieval_claim = _nested_value(overlay, "superseded_fields.sources_retrieval_times.all_source_records")
    if not isinstance(source_retrieval_claim, str) or not source_retrieval_claim.strip():
        raise ResearchEligibilityError("all-source retrieval-time correction declaration is required")

    prior = source_document.get("correction_applications", [])
    if not isinstance(prior, list):
        raise ResearchEligibilityError("correction_applications must be an array")
    if any(isinstance(item, Mapping) and item.get("correction_id") == correction_id for item in prior):
        raise ResearchEligibilityError("capture-time correction overlay was already applied")

    corrected = _json_object(source_artifact_bytes, "source artifact")
    corrected["captured_at_utc"] = None
    corrected["data_cutoff_utc"] = overlay["conservative_known_at_utc"]
    _set_nested_value(corrected, "market_snapshot.kraken_spot.retrieved_at_utc", None)
    _set_nested_value(
        corrected,
        "market_snapshot.kraken_spot.known_at_upper_bound_utc",
        overlay["conservative_known_at_utc"],
    )
    for record in corrected["sources"]:
        record["retrieval_time_utc"] = None
    for section, _ in provider_checks:
        if "retrieved_at_utc" in corrected["market_snapshot"][section]:
            corrected["market_snapshot"][section]["retrieved_at_utc"] = None
    for item in corrected["etf_flow_reconciliation"]["observations"]:
        if "retrieval_time_utc" in item:
            item["retrieval_time_utc"] = None

    manifest = {
        "correction_id": correction_id,
        "overlay_artifact_path": overlay_path,
        "overlay_git_blob_sha1": overlay_blob_sha,
        "overlay_content_sha256": overlay_content_sha256,
        "target_artifact_path": source_path,
        "target_git_blob_sha1": source_blob_sha,
        "target_content_sha256": source_content_sha256,
        "source_artifact_commit_sha": source_commit,
        "application_status": "APPLIED_TO_IN_MEMORY_RESEARCH_VIEW_ONLY",
        "corrected_fields": [
            "captured_at_utc",
            "data_cutoff_utc",
            "market_snapshot.kraken_spot.retrieved_at_utc",
            "market_snapshot.kraken_spot.known_at_upper_bound_utc",
            "sources[*].retrieval_time_utc",
        ],
        "no_op_claims": no_op_claims,
        "provider_update_times_preserved": True,
        "etf_data_dates_preserved": True,
        "numeric_market_values_changed": False,
        "source_urls_changed": False,
        "model_eligibility_effect": "SOURCE_REMAINS_MODEL_INELIGIBLE",
        "forecast_issued": False,
    }
    corrected.setdefault("correction_applications", []).append(manifest)
    return {
        "corrected_document": corrected,
        "application_manifest": manifest,
        "corrected_document_sha256": _sha256(_canonical_json(corrected).encode("utf-8")),
        "source_artifact_preserved": True,
        "model_eligible": False,
        "forecast_issued": False,
    }


def apply_research_timestamp_correction_overlays(repository_root: str | Path) -> dict[str, Any]:
    """Discover and apply supported timestamp overlays to in-memory archive views.

    Only the two explicitly supported machine-readable timestamp overlay
    schemas are applied. Narrative correction addenda are reported but not
    interpreted as field patches. Unknown timestamp-correction schemas,
    missing targets, duplicate targets, duplicate IDs and symlink/path escapes
    fail closed. No repository file is modified and no source becomes eligible.
    """
    root_input = Path(repository_root)
    if root_input.is_symlink():
        raise ResearchEligibilityError("repository_root must not be a symlink")
    try:
        root = root_input.resolve(strict=True)
    except OSError as exc:
        raise ResearchEligibilityError("repository_root must be an existing directory") from exc
    if not root.is_dir():
        raise ResearchEligibilityError("repository_root must be a directory")
    archive = root / "research" / "xrp_intelligence"
    if archive.is_symlink() or not archive.is_dir():
        raise ResearchEligibilityError("research/xrp_intelligence archive directory is missing or unsafe")
    archive_resolved = archive.resolve(strict=True)

    overlays: list[tuple[str, bytes, dict[str, Any]]] = []
    narrative_only: list[str] = []
    artifact_ids: set[str] = set()
    for path in sorted(archive.rglob("*.json")):
        if path.is_symlink():
            raise ResearchEligibilityError("research archive must not contain symlinked JSON artifacts")
        try:
            resolved = path.resolve(strict=True)
            relative_to_archive = resolved.relative_to(archive_resolved)
        except (OSError, ValueError) as exc:
            raise ResearchEligibilityError("research archive artifact escapes the archive directory") from exc
        if not path.is_file():
            continue
        relative_path = (Path("research") / "xrp_intelligence" / relative_to_archive).as_posix()
        try:
            content = path.read_bytes()
        except OSError as exc:
            raise ResearchEligibilityError(f"cannot read research artifact {relative_path}") from exc
        document = _json_object(content, f"research artifact {relative_path}")
        artifact_type = document.get("artifact_type")
        if artifact_type in _TIMESTAMP_OVERLAY_TYPES:
            artifact_id = document.get("artifact_id", document.get("correction_id"))
            if not isinstance(artifact_id, str) or not artifact_id.strip():
                raise ResearchEligibilityError(f"timestamp overlay {relative_path} needs a stable ID")
            if artifact_id in artifact_ids:
                raise ResearchEligibilityError("research archive contains duplicate timestamp overlay IDs")
            artifact_ids.add(artifact_id)
            overlays.append((relative_path, content, document))
        elif isinstance(artifact_type, str) and "timestamp" in artifact_type.lower() and "correction" in artifact_type.lower():
            raise ResearchEligibilityError(f"unsupported timestamp correction schema in {relative_path}")
        elif isinstance(artifact_type, str) and "correction" in artifact_type.lower():
            narrative_only.append(relative_path)

    targets: dict[str, tuple[str, bytes, dict[str, Any]]] = {}
    for overlay_path, overlay_bytes, overlay in overlays:
        target = overlay.get("target_artifact", overlay.get("source_artifact_path"))
        target = _repo_path(target, f"{overlay_path}.target_artifact")
        if not target.startswith("research/xrp_intelligence/"):
            raise ResearchEligibilityError("timestamp overlay target must remain inside research/xrp_intelligence")
        if target in targets:
            raise ResearchEligibilityError(f"multiple timestamp overlays target {target}; composition is not defined")
        target_path = root.joinpath(*target.split("/"))
        if target_path.is_symlink():
            raise ResearchEligibilityError(f"timestamp overlay target {target} must not be a symlink")
        try:
            resolved_target = target_path.resolve(strict=True)
            resolved_target.relative_to(archive_resolved)
        except (OSError, ValueError) as exc:
            raise ResearchEligibilityError(f"timestamp overlay target {target} is missing or escapes the archive") from exc
        if not resolved_target.is_file():
            raise ResearchEligibilityError(f"timestamp overlay target {target} is not a regular file")
        try:
            source_bytes = resolved_target.read_bytes()
        except OSError as exc:
            raise ResearchEligibilityError(f"cannot read timestamp overlay target {target}") from exc
        targets[target] = (overlay_path, overlay_bytes, overlay)

    corrected_artifacts: dict[str, dict[str, Any]] = {}
    application_manifests: list[dict[str, Any]] = []
    for target in sorted(targets):
        overlay_path, overlay_bytes, overlay = targets[target]
        source_path = root.joinpath(*target.split("/"))
        source_bytes = source_path.read_bytes()
        if overlay.get("artifact_type") == _CAPTURE_TIME_OVERLAY_TYPE:
            result = apply_capture_time_interval_correction_overlay(
                source_artifact_path=target,
                source_artifact_bytes=source_bytes,
                overlay_artifact_path=overlay_path,
                overlay_artifact_bytes=overlay_bytes,
            )
        else:
            result = apply_source_timestamp_correction_overlay(
                source_artifact_path=target,
                source_artifact_bytes=source_bytes,
                overlay_artifact_path=overlay_path,
                overlay_artifact_bytes=overlay_bytes,
            )
        corrected_artifacts[target] = result["corrected_document"]
        application_manifests.append(result["application_manifest"])

    return {
        "schema_version": "barrot.xrp.timestamp-correction-archive-view.v1",
        "archive_root": "research/xrp_intelligence",
        "overlay_count": len(application_manifests),
        "corrected_artifacts": corrected_artifacts,
        "application_manifests": application_manifests,
        "narrative_only_correction_artifacts": sorted(narrative_only),
        "source_artifacts_modified": False,
        "model_eligible": False,
        "forecast_issued": False,
    }
