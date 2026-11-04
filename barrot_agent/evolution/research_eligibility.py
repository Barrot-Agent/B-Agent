"""Apply append-only research eligibility overlays before feature admission."""
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable, Mapping
from datetime import datetime, timezone
from pathlib import PurePosixPath
from typing import Any
from urllib.parse import urlsplit

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


def _timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ResearchEligibilityError(f"{field} must be a timezone-aware ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ResearchEligibilityError(f"{field} is not valid ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ResearchEligibilityError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _source_registry(source_document: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    raw_sources = source_document.get("source_registry")
    if not isinstance(raw_sources, list) or not raw_sources:
        raise ResearchEligibilityError("eligible source artifact needs a non-empty source_registry")
    registry: dict[str, dict[str, Any]] = {}
    for index, source in enumerate(raw_sources):
        if not isinstance(source, Mapping):
            raise ResearchEligibilityError(f"source_registry[{index}] must be an object")
        source_id = source.get("source_id", source.get("id"))
        if not isinstance(source_id, str) or not source_id.strip():
            raise ResearchEligibilityError(f"source_registry[{index}] needs a source_id")
        source_id = source_id.strip()
        if source_id in registry:
            raise ResearchEligibilityError("source_registry contains duplicate source_id values")

        digest = source.get("raw_content_sha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ResearchEligibilityError(
                f"source_registry[{index}].raw_content_sha256 must be a SHA-256 hex digest"
            )
        receipt_id = source.get("raw_receipt_id")
        if not isinstance(receipt_id, str) or not receipt_id.strip():
            raise ResearchEligibilityError(f"source_registry[{index}] needs a raw_receipt_id")
        capture_status = source.get("raw_capture_status")
        if capture_status != "byte_complete":
            raise ResearchEligibilityError(
                f"source_registry[{index}] raw_capture_status must be byte_complete"
            )
        independence_group = source.get("independence_group")
        if not isinstance(independence_group, str) or not independence_group.strip():
            raise ResearchEligibilityError(f"source_registry[{index}] needs an independence_group")
        source_uri = source.get("source_uri", source.get("url"))
        if not isinstance(source_uri, str) or not source_uri.strip():
            raise ResearchEligibilityError(f"source_registry[{index}] needs a source_uri")
        parsed_uri = urlsplit(source_uri.strip())
        if parsed_uri.scheme not in {"http", "https"} or not parsed_uri.netloc:
            raise ResearchEligibilityError(f"source_registry[{index}].source_uri must be HTTP(S)")

        source_as_of = _timestamp(
            source.get("source_data_as_of_utc"), f"source_registry[{index}].source_data_as_of_utc"
        )
        captured_at = _timestamp(
            source.get("captured_at_utc"), f"source_registry[{index}].captured_at_utc"
        )
        if captured_at < source_as_of:
            raise ResearchEligibilityError(
                f"source_registry[{index}] capture time precedes source data as-of time"
            )
        registry[source_id] = {
            "source_id": source_id,
            "raw_receipt_id": receipt_id.strip(),
            "raw_content_sha256": digest,
            "raw_capture_status": capture_status,
            "independence_group": independence_group.strip(),
            "source_uri": source_uri.strip(),
            "source_data_as_of_utc": source_as_of,
            "captured_at_utc": captured_at,
        }
    return registry


def _observation_index(
    source_document: Mapping[str, Any],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    if source_document.get("model_eligible") is not True:
        raise ResearchEligibilityError("source artifact is not explicitly model eligible")
    if source_document.get("quality_status") != "verified":
        raise ResearchEligibilityError("source artifact quality_status must be verified")

    registry = _source_registry(source_document)
    observations = source_document.get("observations")
    if not isinstance(observations, list) or not observations:
        raise ResearchEligibilityError("source artifact must contain a non-empty observations array")

    indexed: dict[str, dict[str, Any]] = {}
    for index, observation in enumerate(observations):
        if not isinstance(observation, Mapping):
            raise ResearchEligibilityError(f"source observations[{index}] must be an object")
        identifier = observation.get("observation_id")
        if not isinstance(identifier, str) or not identifier.strip():
            raise ResearchEligibilityError(f"source observations[{index}] needs an observation_id")
        identifier = identifier.strip()
        if identifier in indexed:
            raise ResearchEligibilityError("source artifact contains duplicate observation_id values")
        if observation.get("model_eligible") is not True:
            raise ResearchEligibilityError(
                f"source observation {identifier!r} is not explicitly model eligible"
            )
        if observation.get("quality_status") != "verified":
            raise ResearchEligibilityError(
                f"source observation {identifier!r} quality_status must be verified"
            )

        source_ids = observation.get("source_ids")
        if (
            not isinstance(source_ids, list)
            or not source_ids
            or any(not isinstance(item, str) or not item.strip() for item in source_ids)
        ):
            raise ResearchEligibilityError(
                f"source observation {identifier!r} needs a non-empty source_ids list"
            )
        normalized_source_ids = sorted({item.strip() for item in source_ids})
        if len(normalized_source_ids) != len(source_ids):
            raise ResearchEligibilityError(
                f"source observation {identifier!r} contains duplicate source_ids"
            )
        missing_sources = sorted(set(normalized_source_ids) - set(registry))
        if missing_sources:
            raise ResearchEligibilityError(
                f"source observation {identifier!r} references unreceipted sources: "
                + ", ".join(missing_sources)
            )

        event_time = _timestamp(
            observation.get("event_time_utc"), f"source observations[{index}].event_time_utc"
        )
        known_at = _timestamp(
            observation.get("known_at_utc"), f"source observations[{index}].known_at_utc"
        )
        source_as_of = _timestamp(
            observation.get("source_data_as_of_utc"),
            f"source observations[{index}].source_data_as_of_utc",
        )
        if known_at < source_as_of:
            raise ResearchEligibilityError(
                f"source observation {identifier!r} known_at_utc precedes source data as-of"
            )
        latest_source_as_of = max(registry[item]["source_data_as_of_utc"] for item in normalized_source_ids)
        if source_as_of < latest_source_as_of:
            raise ResearchEligibilityError(
                f"source observation {identifier!r} source_data_as_of_utc predates one of its sources"
            )

        groups = sorted({registry[item]["independence_group"] for item in normalized_source_ids})
        declared_groups = observation.get("source_independence_groups")
        if declared_groups is not None:
            if (
                not isinstance(declared_groups, list)
                or any(not isinstance(item, str) or not item.strip() for item in declared_groups)
                or sorted(set(item.strip() for item in declared_groups)) != groups
            ):
                raise ResearchEligibilityError(
                    f"source observation {identifier!r} source_independence_groups do not match its receipts"
                )

        indexed[identifier] = {
            "source_ids": normalized_source_ids,
            "source_independence_groups": groups,
            "event_time_utc": event_time,
            "known_at_utc": known_at,
            "source_data_as_of_utc": source_as_of,
        }
    return indexed, registry


def _validate_feature_binding(
    record: Mapping[str, Any],
    observation: Mapping[str, Any],
    registry: Mapping[str, Mapping[str, Any]],
    identifier: str,
) -> None:
    if _timestamp(record.get("event_time_utc"), f"{identifier}.event_time_utc") != observation["event_time_utc"]:
        raise ResearchEligibilityError(f"feature record {identifier!r} event time does not match its source observation")
    if _timestamp(
        record.get("source_data_as_of_utc"), f"{identifier}.source_data_as_of_utc"
    ) != observation["source_data_as_of_utc"]:
        raise ResearchEligibilityError(
            f"feature record {identifier!r} source data as-of does not match its source observation"
        )
    if _timestamp(record.get("known_at_utc"), f"{identifier}.known_at_utc") < observation["known_at_utc"]:
        raise ResearchEligibilityError(
            f"feature record {identifier!r} claims availability before its source observation"
        )

    sources = record.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ResearchEligibilityError(f"feature record {identifier!r} needs source lineage")
    normalized_ids: list[str] = []
    latest_capture: datetime | None = None
    for index, source in enumerate(sources):
        if not isinstance(source, Mapping):
            raise ResearchEligibilityError(f"feature record {identifier!r} sources[{index}] must be an object")
        source_id = source.get("source_id")
        if not isinstance(source_id, str) or source_id.strip() not in registry:
            raise ResearchEligibilityError(
                f"feature record {identifier!r} references a source without a raw receipt"
            )
        source_id = source_id.strip()
        expected = registry[source_id]
        if source.get("independence_group") != expected["independence_group"]:
            raise ResearchEligibilityError(f"feature record {identifier!r} source group does not match receipt")
        if source.get("source_uri") != expected["source_uri"]:
            raise ResearchEligibilityError(f"feature record {identifier!r} source URI does not match receipt")
        if source.get("raw_content_sha256") != expected["raw_content_sha256"]:
            raise ResearchEligibilityError(f"feature record {identifier!r} raw hash does not match receipt")
        normalized_ids.append(source_id)
        latest_capture = max(latest_capture or expected["captured_at_utc"], expected["captured_at_utc"])

    if sorted(normalized_ids) != observation["source_ids"]:
        raise ResearchEligibilityError(
            f"feature record {identifier!r} source IDs do not exactly match the source observation"
        )
    ingested_at = _timestamp(record.get("ingested_at_utc"), f"{identifier}.ingested_at_utc")
    if latest_capture is not None and ingested_at < latest_capture:
        raise ResearchEligibilityError(
            f"feature record {identifier!r} was ingested before its raw-source receipt"
        )


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

    observation_index, source_registry = _observation_index(source_document)
    source_ids = set(observation_index)
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
        observation = observation_index[identifier]
        _validate_feature_binding(record, observation, source_registry, identifier)

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
    used_source_ids = sorted({
        source_id
        for record in raw_records
        for source_id in observation_index[record["research_observation_id"].strip()]["source_ids"]
    })
    snapshot["research_source_receipts"] = [
        {
            "source_id": source_id,
            "raw_receipt_id": source_registry[source_id]["raw_receipt_id"],
            "raw_content_sha256": source_registry[source_id]["raw_content_sha256"],
            "raw_capture_status": source_registry[source_id]["raw_capture_status"],
            "independence_group": source_registry[source_id]["independence_group"],
            "source_uri": source_registry[source_id]["source_uri"],
            "source_data_as_of_utc": source_registry[source_id]["source_data_as_of_utc"].isoformat().replace("+00:00", "Z"),
            "captured_at_utc": source_registry[source_id]["captured_at_utc"].isoformat().replace("+00:00", "Z"),
        }
        for source_id in used_source_ids
    ]
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
