"""Deterministic point-in-time feature validation; no network or filesystem I/O.

Schema v1 rejects late-ingested historical reconstruction rather than
backdating it. Future event times are allowed only when the exact record
version was public and available by the forecast cutoff.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping
from urllib.parse import urlsplit

from .source_independence import canonical_independence_groups


class FeatureSnapshotError(ValueError):
    """A feature record or snapshot violates the point-in-time contract."""


QUALITY_STATES = {"verified", "provisional", "unverified", "disputed", "stale", "missing"}
REVISION_STATES = {"original", "revised", "superseded"}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FeatureSnapshotError(f"{field} must be a non-empty string")
    return value.strip()


def _utc(value: Any, field: str) -> tuple[datetime, str]:
    if not isinstance(value, str) or not value.strip():
        raise FeatureSnapshotError(f"{field} must be a timezone-aware ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise FeatureSnapshotError(f"{field} is not valid ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise FeatureSnapshotError(f"{field} must include a timezone")
    normalized = parsed.astimezone(timezone.utc)
    return normalized, normalized.isoformat(timespec="microseconds").replace("+00:00", "Z")


def _strings(value: Any, field: str, *, required: bool = False) -> list[str]:
    if value is None and not required:
        return []
    if not isinstance(value, list) or (required and not value):
        raise FeatureSnapshotError(f"{field} must be a {'non-empty ' if required else ''}list of strings")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise FeatureSnapshotError(f"{field} must contain only non-empty strings")
    return sorted({item.strip() for item in value})


def _value(value: Any) -> Any:
    if isinstance(value, bool) or isinstance(value, int):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    if isinstance(value, str) and value.strip():
        return value.strip()
    raise FeatureSnapshotError("value must be a finite number, boolean or non-empty string")


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _source(value: Any, index: int) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise FeatureSnapshotError(f"sources[{index}] must be a mapping")
    source_id = _text(value.get("source_id"), f"sources[{index}].source_id")
    group = _text(value.get("independence_group"), f"sources[{index}].independence_group")
    uri = _text(value.get("source_uri"), f"sources[{index}].source_uri")
    parsed = urlsplit(uri)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise FeatureSnapshotError(f"sources[{index}].source_uri must be an HTTP(S) URL")
    digest = _text(value.get("raw_content_sha256"), f"sources[{index}].raw_content_sha256").lower()
    if not _SHA256.fullmatch(digest):
        raise FeatureSnapshotError(f"sources[{index}].raw_content_sha256 must be a SHA-256 hex digest")
    return {"source_id": source_id, "independence_group": group, "source_uri": uri, "raw_content_sha256": digest}


def validate_feature_record(
    record: Mapping[str, Any],
    cutoff_utc: str,
    *,
    captured_at_utc: str | None = None,
    max_source_age_seconds: int | None = None,
) -> dict[str, Any]:
    """Normalize one record and classify eligibility at a fixed cutoff."""
    if not isinstance(record, Mapping):
        raise FeatureSnapshotError("feature record must be a mapping")
    cutoff, cutoff_s = _utc(cutoff_utc, "cutoff_utc")
    captured, captured_s = _utc(captured_at_utc or cutoff_utc, "captured_at_utc")
    if captured < cutoff:
        raise FeatureSnapshotError("captured_at_utc cannot precede cutoff_utc")
    if max_source_age_seconds is not None and (
        isinstance(max_source_age_seconds, bool)
        or not isinstance(max_source_age_seconds, int)
        or max_source_age_seconds < 0
    ):
        raise FeatureSnapshotError("max_source_age_seconds must be a non-negative integer")

    required = (
        "record_id", "feature_id", "feature_version", "asset", "feature_name", "value", "unit",
        "event_time_utc", "known_at_utc", "source_data_as_of_utc", "ingested_at_utc",
        "revision_available_at_utc", "sources", "quality_status", "model_eligible",
        "revision_status", "adapter_version", "parser_version",
    )
    missing = [key for key in required if key not in record]
    if missing:
        raise FeatureSnapshotError("missing fields: " + ", ".join(missing))

    feature_version = record["feature_version"]
    if isinstance(feature_version, bool) or not isinstance(feature_version, int) or feature_version < 1:
        raise FeatureSnapshotError("feature_version must be a positive integer")

    times = {}
    for key in ("event_time_utc", "known_at_utc", "source_data_as_of_utc", "ingested_at_utc", "revision_available_at_utc"):
        times[key] = _utc(record[key], key)
    event_time, event_s = times["event_time_utc"]
    known_at, known_s = times["known_at_utc"]
    source_as_of, source_s = times["source_data_as_of_utc"]
    ingested_at, ingested_s = times["ingested_at_utc"]
    revision_at, revision_s = times["revision_available_at_utc"]
    if revision_at < known_at:
        raise FeatureSnapshotError("revision_available_at_utc cannot precede known_at_utc")
    if source_as_of > revision_at:
        raise FeatureSnapshotError("source_data_as_of_utc cannot follow revision_available_at_utc")
    if ingested_at < revision_at:
        raise FeatureSnapshotError("ingested_at_utc cannot precede revision_available_at_utc")

    raw_sources = record["sources"]
    if not isinstance(raw_sources, list) or not raw_sources:
        raise FeatureSnapshotError("sources must be a non-empty list")
    sources = sorted((_source(item, i) for i, item in enumerate(raw_sources)), key=lambda item: item["source_id"])
    source_ids = [item["source_id"] for item in sources]
    if len(source_ids) != len(set(source_ids)):
        raise FeatureSnapshotError("sources contains duplicate source_id values")
    groups = canonical_independence_groups(sources)

    quality = _text(record["quality_status"], "quality_status").lower()
    if quality not in QUALITY_STATES:
        raise FeatureSnapshotError(f"quality_status must be one of {sorted(QUALITY_STATES)}")
    eligible_flag = record["model_eligible"]
    if not isinstance(eligible_flag, bool):
        raise FeatureSnapshotError("model_eligible must be boolean")
    reason = record.get("eligibility_reason", "")
    if not isinstance(reason, str):
        raise FeatureSnapshotError("eligibility_reason must be a string")
    reason = reason.strip()
    if eligible_flag and quality != "verified":
        raise FeatureSnapshotError("model_eligible records must have quality_status=verified")
    if not eligible_flag and not reason:
        raise FeatureSnapshotError("ineligible records require an eligibility_reason")

    revision = _text(record["revision_status"], "revision_status").lower()
    if revision not in REVISION_STATES:
        raise FeatureSnapshotError(f"revision_status must be one of {sorted(REVISION_STATES)}")
    supersedes = record.get("supersedes_record_id")
    if supersedes is not None:
        supersedes = _text(supersedes, "supersedes_record_id")
    if revision == "original" and supersedes is not None:
        raise FeatureSnapshotError("original records cannot supersede another record")
    if revision == "revised" and (supersedes is None or supersedes == record["record_id"]):
        raise FeatureSnapshotError("revised records require a different supersedes_record_id")
    if revision == "superseded" and eligible_flag:
        raise FeatureSnapshotError("superseded records cannot be model eligible")

    normalized = {
        "record_id": _text(record["record_id"], "record_id"),
        "feature_id": _text(record["feature_id"], "feature_id"),
        "feature_version": feature_version,
        "asset": _text(record["asset"], "asset").upper(),
        "feature_name": _text(record["feature_name"], "feature_name"),
        "value": _value(record["value"]),
        "unit": _text(record["unit"], "unit"),
        "event_time_utc": event_s,
        "known_at_utc": known_s,
        "source_data_as_of_utc": source_s,
        "ingested_at_utc": ingested_s,
        "revision_available_at_utc": revision_s,
        "sources": sources,
        "source_independence_groups": groups,
        "independent_source_group_count": len(groups),
        "quality_status": quality,
        "model_eligible": eligible_flag,
        "eligibility_reason": reason,
        "revision_status": revision,
        "supersedes_record_id": supersedes,
        "adapter_version": _text(record["adapter_version"], "adapter_version"),
        "parser_version": _text(record["parser_version"], "parser_version"),
        "limitations": _strings(record.get("limitations", []), "limitations"),
        "disconfirming_evidence_ids": _strings(record.get("disconfirming_evidence_ids", []), "disconfirming_evidence_ids"),
    }
    for field in ("venue", "instrument", "currency_pair", "market_type", "aggregation_window"):
        if record.get(field) is not None:
            normalized[field] = _text(record[field], field)
    normalized["normalized_content_sha256"] = _canonical_hash(normalized)

    exclusions = []
    if known_at > cutoff:
        exclusions.append("not_public_by_cutoff")
    if source_as_of > cutoff:
        exclusions.append("source_data_after_cutoff")
    if revision_at > cutoff:
        exclusions.append("revision_not_available_by_cutoff")
    if ingested_at > cutoff:
        exclusions.append("ingested_after_cutoff")
    if not eligible_flag:
        exclusions.append("record_marked_ineligible")
    if quality != "verified":
        exclusions.append(f"quality_{quality}")
    if revision == "superseded":
        exclusions.append("record_superseded")
    if max_source_age_seconds is not None and (cutoff - source_as_of).total_seconds() > max_source_age_seconds:
        exclusions.append("source_data_stale_at_cutoff")

    return {
        "record": normalized,
        "eligible": not exclusions,
        "exclusion_reasons": sorted(set(exclusions)),
        "cutoff_utc": cutoff_s,
        "captured_at_utc": captured_s,
    }


def independent_source_groups(record: Mapping[str, Any]) -> list[str]:
    """Count distinct provenance lineages, not syndicated copies."""
    sources = record.get("sources")
    if not isinstance(sources, list) or not sources:
        raise FeatureSnapshotError("record.sources must be a non-empty list")
    try:
        return canonical_independence_groups(sources)
    except ValueError as exc:
        raise FeatureSnapshotError(str(exc)) from exc


def build_feature_snapshot(
    records: Iterable[Mapping[str, Any]],
    *,
    cutoff_utc: str,
    captured_at_utc: str,
    asset_scope: list[str] | None = None,
    max_source_age_seconds: int | None = None,
) -> dict[str, Any]:
    """Build a deterministic model-facing snapshot and explicit exclusion manifest."""
    cutoff, cutoff_s = _utc(cutoff_utc, "cutoff_utc")
    captured, captured_s = _utc(captured_at_utc, "captured_at_utc")
    if captured < cutoff:
        raise FeatureSnapshotError("captured_at_utc cannot precede cutoff_utc")
    raw = list(records)
    if not raw:
        raise FeatureSnapshotError("snapshot requires at least one input record")
    checked = [
        validate_feature_record(
            item, cutoff_s, captured_at_utc=captured_s, max_source_age_seconds=max_source_age_seconds
        )
        for item in raw
    ]
    ids = [item["record"]["record_id"] for item in checked]
    if len(ids) != len(set(ids)):
        raise FeatureSnapshotError("snapshot contains duplicate record_id values")
    records_by_id = {item["record"]["record_id"]: item for item in checked}
    superseded_by: dict[str, str] = {}
    for item in checked:
        current = item["record"]
        if not item["eligible"] or current["revision_status"] != "revised":
            continue
        predecessor_id = current["supersedes_record_id"]
        predecessor = records_by_id.get(predecessor_id)
        if predecessor is None:
            continue
        previous = predecessor["record"]
        identity_fields = (
            "feature_id",
            "asset",
            "feature_name",
            "unit",
            "event_time_utc",
            "venue",
            "instrument",
            "currency_pair",
            "market_type",
            "aggregation_window",
        )
        mismatched_identity = [
            field for field in identity_fields if previous.get(field) != current.get(field)
        ]
        if mismatched_identity:
            raise FeatureSnapshotError(
                "a revision must supersede the same feature and asset at the same event time "
                "and market dimensions: " + ", ".join(mismatched_identity)
            )
        if current["feature_version"] <= previous["feature_version"]:
            raise FeatureSnapshotError("a revision feature_version must exceed its predecessor")
        if predecessor_id in superseded_by:
            raise FeatureSnapshotError("multiple eligible revisions supersede the same predecessor")
        superseded_by[predecessor_id] = current["record_id"]

    included = sorted(
        (
            item["record"] for item in checked
            if item["eligible"] and item["record"]["record_id"] not in superseded_by
        ),
        key=lambda item: (item["feature_id"], item["asset"], item["event_time_utc"], item["record_id"]),
    )
    excluded_items = []
    for item in checked:
        record_id = item["record"]["record_id"]
        reasons = list(item["exclusion_reasons"])
        if item["eligible"] and record_id in superseded_by:
            reasons.append("superseded_by_revision")
        if reasons:
            excluded_items.append({"record_id": record_id, "reasons": sorted(set(reasons))})
    excluded = sorted(excluded_items, key=lambda item: item["record_id"])
    if not included:
        raise FeatureSnapshotError("snapshot has no point-in-time eligible records")
    derived_assets = sorted({item["asset"] for item in included})
    assets = derived_assets if asset_scope is None else [x.upper() for x in _strings(asset_scope, "asset_scope", required=True)]
    if not set(derived_assets).issubset(set(assets)):
        raise FeatureSnapshotError("eligible record asset is outside declared asset_scope")
    groups = sorted({g for item in included for g in independent_source_groups(item)})
    features: dict[str, int] = {}
    for item in included:
        features[item["feature_id"]] = features.get(item["feature_id"], 0) + 1
    manifest = {
        "schema_version": 1,
        "asset_scope": sorted(set(assets)),
        "cutoff_utc": cutoff_s,
        "captured_at_utc": captured_s,
        "input_record_count": len(raw),
        "eligible_record_count": len(included),
        "excluded_record_count": len(excluded),
        "excluded_records": excluded,
        "exclusion_reason_counts": {
            reason: sum(reason in item["reasons"] for item in excluded)
            for reason in sorted({r for item in excluded for r in item["reasons"]})
        },
        "source_ids": sorted({s["source_id"] for item in included for s in item["sources"]}),
        "source_independence_groups": groups,
        "unique_source_independence_group_count": len(groups),
        "adapter_versions": sorted({item["adapter_version"] for item in included}),
        "parser_versions": sorted({item["parser_version"] for item in included}),
        "feature_counts": dict(sorted(features.items())),
        "max_known_at_utc": max(item["known_at_utc"] for item in included),
        "max_source_data_as_of_utc": max(item["source_data_as_of_utc"] for item in included),
        "records": included,
    }
    manifest["snapshot_id"] = _canonical_hash(manifest)
    return manifest
