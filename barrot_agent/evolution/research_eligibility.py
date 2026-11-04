"""Apply append-only research eligibility overlays before feature admission."""
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable, Mapping
from pathlib import PurePosixPath
from typing import Any

from .point_in_time_features import FeatureSnapshotError, build_feature_snapshot

_SHA1 = re.compile(r"^[0-9a-f]{40}$")
_MAX_ARTIFACT_BYTES = 10 * 1024 * 1024


class ResearchEligibilityError(ValueError):
    """A research eligibility overlay cannot be safely applied."""


def _canonical_json(value: Any) -> str:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ResearchEligibilityError("document is not canonical-JSON compatible") from exc


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git_blob_sha1(content: bytes) -> str:
    """Return the Git object SHA-1 for exact file bytes, not a plain SHA-1."""
    if not isinstance(content, bytes) or len(content) > _MAX_ARTIFACT_BYTES:
        raise ResearchEligibilityError("artifact content must be bytes within the size limit")
    header = b"blob " + str(len(content)).encode("ascii") + b"\0"
    return hashlib.sha1(header + content).hexdigest()


def _repo_path(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ResearchEligibilityError(f"{field} must be a non-empty repository-relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value:
        raise ResearchEligibilityError(f"{field} must be a normalized repository-relative path")
    return value


def _json_object(content: bytes, field: str) -> dict[str, Any]:
    if not isinstance(content, bytes) or not content or len(content) > _MAX_ARTIFACT_BYTES:
        raise ResearchEligibilityError(f"{field} bytes are missing or exceed the size limit")
    try:
        value = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise ResearchEligibilityError(f"{field} is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise ResearchEligibilityError(f"{field} must contain a JSON object")
    return value


def _observation_ids(source_document: Mapping[str, Any]) -> set[str]:
    observations = source_document.get("observations")
    if not isinstance(observations, list) or not observations:
        raise ResearchEligibilityError("source artifact must contain a non-empty observations array")
    identifiers: list[str] = []
    for index, observation in enumerate(observations):
        if not isinstance(observation, Mapping):
            raise ResearchEligibilityError(f"source observations[{index}] must be an object")
        identifier = observation.get("observation_id")
        if not isinstance(identifier, str) or not identifier.strip():
            raise ResearchEligibilityError(f"source observations[{index}] needs an observation_id")
        identifiers.append(identifier.strip())
    if len(identifiers) != len(set(identifiers)):
        raise ResearchEligibilityError("source artifact contains duplicate observation_id values")
    return set(identifiers)


def build_feature_snapshot_with_research_overlay(
    records: Iterable[Mapping[str, Any]],
    *,
    overlay: Mapping[str, Any],
    source_artifact_path: str,
    source_artifact_bytes: bytes,
    overlay_artifact_path: str,
    overlay_artifact_bytes: bytes,
    cutoff_utc: str,
    captured_at_utc: str,
    asset_scope: list[str] | None = None,
    max_source_age_seconds: int | None = None,
) -> dict[str, Any]:
    """Apply verified downgrade-only corrections, then build a point-in-time snapshot.

    Each input feature record must carry research_observation_id,
    source_artifact_path and source_artifact_blob_sha metadata. These binding
    fields are checked here and removed before the canonical feature validator
    runs. Overlay provenance and correction reasons are included in the
    resulting snapshot manifest and therefore in its snapshot_id.
    """
    source_path = _repo_path(source_artifact_path, "source_artifact_path")
    overlay_path = _repo_path(overlay_artifact_path, "overlay_artifact_path")
    source_document = _json_object(source_artifact_bytes, "source artifact")
    overlay_document = _json_object(overlay_artifact_bytes, "overlay artifact")

    if _canonical_json(dict(overlay)) != _canonical_json(overlay_document):
        raise ResearchEligibilityError("overlay mapping does not match the exact overlay artifact bytes")

    source_blob_sha = git_blob_sha1(source_artifact_bytes)
    overlay_blob_sha = git_blob_sha1(overlay_artifact_bytes)
    source_content_sha256 = _sha256(source_artifact_bytes)
    overlay_content_sha256 = _sha256(overlay_artifact_bytes)

    if overlay_document.get("schema_version") != "barrot.xrp.research-correction.v1":
        raise ResearchEligibilityError("unsupported research correction schema_version")
    if overlay_document.get("artifact_type") != "append_only_observation_eligibility_correction":
        raise ResearchEligibilityError("overlay artifact_type is not an eligibility correction")
    artifact_id = overlay_document.get("artifact_id")
    if not isinstance(artifact_id, str) or not artifact_id.strip():
        raise ResearchEligibilityError("overlay artifact_id is required")
    if overlay_document.get("source_artifact") != source_path:
        raise ResearchEligibilityError("overlay source_artifact does not match the supplied artifact path")
    declared_source_sha = overlay_document.get("source_artifact_blob_sha")
    if not isinstance(declared_source_sha, str) or not _SHA1.fullmatch(declared_source_sha):
        raise ResearchEligibilityError("overlay source_artifact_blob_sha must be a Git blob SHA-1")
    if declared_source_sha != source_blob_sha:
        raise ResearchEligibilityError("overlay source_artifact_blob_sha does not match exact source bytes")

    preservation = overlay_document.get("preservation")
    if not isinstance(preservation, Mapping):
        raise ResearchEligibilityError("overlay preservation declaration is required")
    if preservation.get("source_artifact_modified") is not False:
        raise ResearchEligibilityError("overlay must preserve the original source artifact")
    if preservation.get("raw_source_receipts_modified") is not False:
        raise ResearchEligibilityError("overlay must preserve original raw-source receipts")
    if preservation.get("correction_mode") != "append_only_observation_overlay":
        raise ResearchEligibilityError("overlay must use append-only correction mode")
    if preservation.get("forecast_issued") is not False:
        raise ResearchEligibilityError("eligibility correction cannot attest that a forecast was issued")
    if preservation.get("consumer_application_status") != "NOT_EXECUTED":
        raise ResearchEligibilityError("overlay must disclose that consumer application was not previously executed")

    source_ids = _observation_ids(source_document)
    correction = overlay_document.get("correction")
    if not isinstance(correction, Mapping):
        raise ResearchEligibilityError("overlay correction object is required")
    entries = correction.get("observations")
    if not isinstance(entries, list) or not entries:
        raise ResearchEligibilityError("overlay correction observations must be a non-empty array")

    corrections: dict[str, str] = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            raise ResearchEligibilityError(f"correction observations[{index}] must be an object")
        identifier = entry.get("observation_id")
        if not isinstance(identifier, str) or not identifier.strip():
            raise ResearchEligibilityError(f"correction observations[{index}] needs an observation_id")
        identifier = identifier.strip()
        if identifier in corrections:
            raise ResearchEligibilityError("overlay contains duplicate observation_id corrections")
        if identifier not in source_ids:
            raise ResearchEligibilityError(f"overlay references unknown source observation {identifier!r}")
        if entry.get("model_eligible") is not False:
            raise ResearchEligibilityError("research overlays may downgrade eligibility only; promotion is forbidden")
        reason = entry.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            raise ResearchEligibilityError(f"correction for {identifier!r} needs a non-empty reason")
        corrections[identifier] = reason.strip()

    raw_records = list(records)
    if not raw_records:
        raise ResearchEligibilityError("at least one normalized feature record is required")
    seen: set[str] = set()
    prepared: list[dict[str, Any]] = []
    for index, record in enumerate(raw_records):
        if not isinstance(record, Mapping):
            raise ResearchEligibilityError(f"feature records[{index}] must be an object")
        identifier = record.get("research_observation_id")
        if not isinstance(identifier, str) or not identifier.strip():
            raise ResearchEligibilityError(f"feature records[{index}] needs research_observation_id")
        identifier = identifier.strip()
        if identifier not in source_ids:
            raise ResearchEligibilityError(f"feature record references unknown source observation {identifier!r}")
        if identifier in seen:
            raise ResearchEligibilityError(f"duplicate feature mapping for research observation {identifier!r}")
        if record.get("source_artifact_path") != source_path:
            raise ResearchEligibilityError(f"feature record {identifier!r} is not bound to the supplied source path")
        if record.get("source_artifact_blob_sha") != source_blob_sha:
            raise ResearchEligibilityError(f"feature record {identifier!r} is not bound to the exact source blob")
        seen.add(identifier)

        item = dict(record)
        if identifier in corrections:
            prior_reason = item.get("eligibility_reason", "")
            if not isinstance(prior_reason, str):
                raise ResearchEligibilityError(f"feature record {identifier!r} has an invalid eligibility_reason")
            reasons = list(dict.fromkeys(
                value for value in (prior_reason.strip(), corrections[identifier]) if value
            ))
            item["model_eligible"] = False
            item["eligibility_reason"] = "; ".join(reasons)
        item.pop("research_observation_id", None)
        item.pop("source_artifact_path", None)
        item.pop("source_artifact_blob_sha", None)
        prepared.append(item)

    missing_records = sorted(set(corrections) - seen)
    if missing_records:
        raise ResearchEligibilityError(
            "overlay corrections lack exactly mapped feature records: " + ", ".join(missing_records)
        )

    snapshot = build_feature_snapshot(
        prepared,
        cutoff_utc=cutoff_utc,
        captured_at_utc=captured_at_utc,
        asset_scope=asset_scope,
        max_source_age_seconds=max_source_age_seconds,
    )
    snapshot["research_eligibility_overlays"] = [
        {
            "artifact_id": artifact_id,
            "overlay_artifact_path": overlay_path,
            "overlay_git_blob_sha1": overlay_blob_sha,
            "overlay_content_sha256": overlay_content_sha256,
            "source_artifact_path": source_path,
            "source_git_blob_sha1": source_blob_sha,
            "source_content_sha256": source_content_sha256,
            "application_status": "APPLIED_BEFORE_POINT_IN_TIME_VALIDATION",
            "corrections": [
                {
                    "observation_id": identifier,
                    "model_eligible": False,
                    "reason": corrections[identifier],
                }
                for identifier in sorted(corrections)
            ],
        }
    ]
    manifest_without_id = {key: value for key, value in snapshot.items() if key != "snapshot_id"}
    snapshot["snapshot_id"] = hashlib.sha256(
        _canonical_json(manifest_without_id).encode("utf-8")
    ).hexdigest()
    return snapshot
