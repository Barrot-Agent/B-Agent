"""Preimage-bound timestamp corrections for append-only XRP research artifacts."""
from __future__ import annotations

from collections.abc import Mapping
from datetime import date
from typing import Any

from .research_eligibility import (
    ResearchEligibilityError,
    _SHA1,
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


def _validate_issuer_file_timestamps(value: Any, field: str) -> None:
    if not isinstance(value, Mapping) or not value:
        raise ResearchEligibilityError(f"{field} must be a non-empty issuer timestamp mapping")
    for issuer, stamp in value.items():
        if not isinstance(issuer, str) or not issuer.strip():
            raise ResearchEligibilityError(f"{field} contains an invalid issuer key")
        if isinstance(stamp, Mapping):
            if set(stamp) != {"start", "end"}:
                raise ResearchEligibilityError(f"{field}.{issuer} must contain exactly start and end")
            start = _timestamp(stamp.get("start"), f"{field}.{issuer}.start")
            end = _timestamp(stamp.get("end"), f"{field}.{issuer}.end")
            if end < start:
                raise ResearchEligibilityError(f"{field}.{issuer} end precedes start")
        else:
            _timestamp(stamp, f"{field}.{issuer}")


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
        if target_field not in _TIMESTAMP_CORRECTION_TARGETS:
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
            if not isinstance(expected, str) or not expected.startswith(canonical_value + "T"):
                raise ResearchEligibilityError("source_event_date must match the removed timestamp's calendar date")
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
