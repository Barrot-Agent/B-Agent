
"""Point-in-time XRP event timeline assembly.

This module converts explicitly sourced event records into a deterministic,
cutoff-safe timeline and delegates hypothesis grouping to the existing scenario
assembler. It does not fetch sources, infer causality, calculate probabilities,
create market features, or issue forecasts.

available_at_utc is when the evidence became available to Barrot.
captured_at_utc is the actual capture/ingestion time. A historical event
captured after a historical cutoff is excluded even if its publisher timestamp
is old. A raw-source hash alone does not establish receipt completeness. This module cannot
verify canonical receipt metadata, retained bytes, or an independent timestamp anchor;
a local hash chain is not an independent WORM anchor.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlsplit

from .scenario_hypotheses import (
    ScenarioHypothesisError,
    build_scenario_hypotheses,
)
from .source_independence import (
    canonical_independence_groups,
    canonical_publisher_group,
)

SCHEMA_VERSION = "1.0.0"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_ALLOWED_EVENT_TYPES = {
    "market", "derivatives", "liquidity", "exchange_flow", "collateral",
    "institutional", "custody", "stablecoin", "payments", "regulatory",
    "macro", "geopolitical", "corporate", "protocol", "identity", "other",
}

_ALLOWED_SOURCE_STATUSES = {"verified", "disputed", "provisional", "unverified"}
_ALLOWED_STANCES = {"supports", "contradicts", "context"}
_ALLOWED_EVENT_STATUSES = {"occurred", "scheduled", "ongoing", "unknown"}


class EventTimelineError(ValueError):
    """Raised when an event record is malformed or not point-in-time safe."""


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EventTimelineError(f"{field} must be a non-empty string")
    return value.strip()


def _utc(value: Any, field: str) -> tuple[datetime, str]:
    raw = _text(value, field)
    try:
        parsed = datetime.fromisoformat(raw[:-1] + "+00:00" if raw.endswith("Z") else raw)
    except ValueError as exc:
        raise EventTimelineError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise EventTimelineError(f"{field} must include a timezone")
    normalized = parsed.astimezone(timezone.utc)
    timespec = "microseconds" if normalized.microsecond else "seconds"
    return (
        normalized,
        normalized.isoformat(timespec=timespec).replace("+00:00", "Z"),
    )


def _strings(value: Any, field: str, *, required: bool = False) -> list[str]:
    if value is None and not required:
        return []
    if not isinstance(value, (list, tuple)):
        raise EventTimelineError(f"{field} must be a list or tuple of strings")
    result = sorted(
        {_text(item, f"{field}[]") for item in value},
        key=str.casefold,
    )
    if required and not result:
        raise EventTimelineError(f"{field} must contain at least one item")
    return result


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()



def _normalize_event(
    record: Any,
    index: int,
    cutoff: datetime,
    horizon_end: datetime,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None]:
    prefix = f"event_records[{index}]"
    if not isinstance(record, Mapping):
        raise EventTimelineError(f"{prefix} must be a mapping")

    event_id = _text(record.get("event_id"), f"{prefix}.event_id")
    event_type = _text(record.get("event_type"), f"{prefix}.event_type").lower()
    if event_type not in _ALLOWED_EVENT_TYPES:
        raise EventTimelineError(
            f"{prefix}.event_type must be one of {sorted(_ALLOWED_EVENT_TYPES)}"
        )
    event_name = _text(record.get("event_name"), f"{prefix}.event_name")
    hypothesis_id = _text(record.get("hypothesis_id"), f"{prefix}.hypothesis_id")
    domain = _text(record.get("domain"), f"{prefix}.domain")
    hypothesis = _text(record.get("hypothesis"), f"{prefix}.hypothesis")
    counter_hypothesis = _text(
        record.get("counter_hypothesis"),
        f"{prefix}.counter_hypothesis",
    )
    claim = _text(record.get("claim"), f"{prefix}.claim")
    source_id = _text(record.get("source_id"), f"{prefix}.source_id")
    source_name_value = record.get("source_name")
    source_name = _text(
        source_id if source_name_value is None else source_name_value,
        f"{prefix}.source_name",
    )
    source_url = _text(record.get("source_url"), f"{prefix}.source_url")
    try:
        parsed_url = urlsplit(source_url)
        hostname = parsed_url.hostname
        username = parsed_url.username
        password = parsed_url.password
    except ValueError as exc:
        raise EventTimelineError(
            f"{prefix}.source_url must be a valid HTTP(S) URL"
        ) from exc
    if parsed_url.scheme.lower() not in {"http", "https"} or not hostname:
        raise EventTimelineError(
            f"{prefix}.source_url must be a valid HTTP(S) URL"
        )
    if username or password:
        raise EventTimelineError(
            f"{prefix}.source_url must not contain embedded credentials"
        )

    independence_group = _text(
        record.get("independence_group"),
        f"{prefix}.independence_group",
    )
    source_status = _text(
        record.get("source_status"),
        f"{prefix}.source_status",
    ).lower()
    if source_status not in _ALLOWED_SOURCE_STATUSES:
        raise EventTimelineError(
            f"{prefix}.source_status must be one of {sorted(_ALLOWED_SOURCE_STATUSES)}"
        )
    stance = _text(record.get("stance"), f"{prefix}.stance").lower()
    if stance not in _ALLOWED_STANCES:
        raise EventTimelineError(
            f"{prefix}.stance must be one of {sorted(_ALLOWED_STANCES)}"
        )
    event_status = _text(
        record.get("event_status"),
        f"{prefix}.event_status",
    ).lower()
    if event_status not in _ALLOWED_EVENT_STATUSES:
        raise EventTimelineError(
            f"{prefix}.event_status must be one of {sorted(_ALLOWED_EVENT_STATUSES)}"
        )

    event_time, event_time_text = _utc(
        record.get("event_time_utc"),
        f"{prefix}.event_time_utc",
    )
    available_at, available_at_text = _utc(
        record.get("available_at_utc"),
        f"{prefix}.available_at_utc",
    )
    captured_at, captured_at_text = _utc(
        record.get("captured_at_utc"),
        f"{prefix}.captured_at_utc",
    )
    if captured_at < available_at:
        raise EventTimelineError(
            f"{prefix}.captured_at_utc cannot precede available_at_utc"
        )

    published_raw = record.get("source_published_at_utc")
    published_at_text = None
    if published_raw is not None:
        published_at, published_at_text = _utc(
            published_raw,
            f"{prefix}.source_published_at_utc",
        )
        if published_at > captured_at:
            raise EventTimelineError(
                f"{prefix}.source_published_at_utc cannot follow captured_at_utc"
            )

    raw_hash = record.get("raw_source_sha256")
    if raw_hash is not None:
        raw_hash = _text(raw_hash, f"{prefix}.raw_source_sha256").lower()
        if not _SHA256_RE.fullmatch(raw_hash):
            raise EventTimelineError(
                f"{prefix}.raw_source_sha256 must be a 64-character SHA-256 hex digest"
            )

    assumptions = _strings(record.get("assumptions"), f"{prefix}.assumptions")
    falsification = _strings(
        record.get("falsification_conditions"),
        f"{prefix}.falsification_conditions",
        required=True,
    )
    related_entities = _strings(
        record.get("related_entities"),
        f"{prefix}.related_entities",
    )
    tags = _strings(record.get("tags"), f"{prefix}.tags")

    known_at = max(available_at, captured_at)
    known_at_text = known_at.isoformat(timespec="microseconds").replace("+00:00", "Z")
    exclusion_reason = None
    if known_at > cutoff:
        exclusion_reason = "not_captured_by_data_cutoff"
    elif event_status == "occurred" and event_time > cutoff:
        exclusion_reason = "occurred_event_is_after_data_cutoff"
    elif event_status == "scheduled" and event_time <= cutoff:
        exclusion_reason = "scheduled_event_time_has_elapsed"
    elif event_status in {"ongoing", "unknown"} and event_time > cutoff:
        exclusion_reason = "future_event_not_verified_as_scheduled"
    elif event_status == "scheduled" and event_time > horizon_end:
        exclusion_reason = "scheduled_event_outside_forecast_horizon"

    publisher_group = canonical_publisher_group(source_url)
    receipt_status = (
        "RAW_SHA256_PRESENT_UNVERIFIED"
        if raw_hash is not None
        else "MISSING_RAW_RECEIPT_HASH"
    )
    if exclusion_reason is not None:
        excluded_record = {
            "event_id": event_id,
            "reason": exclusion_reason,
            "event_type": event_type,
            "event_name": event_name,
            "domain": domain,
            "hypothesis_id": hypothesis_id,
            "hypothesis": hypothesis,
            "counter_hypothesis": counter_hypothesis,
            "claim": claim,
            "event_status": event_status,
            "event_time_utc": event_time_text,
            "source_published_at_utc": published_at_text,
            "available_at_utc": available_at_text,
            "captured_at_utc": captured_at_text,
            "known_at_utc": known_at_text,
            "source_id": source_id,
            "source_name": source_name,
            "source_url": source_url,
            "independence_group": independence_group,
            "canonical_publisher_group": publisher_group,
            "source_status": source_status,
            "declared_stance": stance,
            "raw_source_sha256": raw_hash,
            "raw_hash_present": raw_hash is not None,
            "receipt_status": receipt_status,
            "assumptions": assumptions,
            "falsification_conditions": falsification,
            "related_entities": related_entities,
            "tags": tags,
            "model_eligible": False,
            "research_only": True,
        }
        return None, excluded_record, None

    timeline_record = {
        "event_id": event_id,
        "event_type": event_type,
        "event_name": event_name,
        "domain": domain,
        "event_status": event_status,
        "event_time_utc": event_time_text,
        "source_published_at_utc": published_at_text,
        "available_at_utc": available_at_text,
        "captured_at_utc": captured_at_text,
        "known_at_utc": known_at_text,
        "source_id": source_id,
        "source_name": source_name,
        "source_url": source_url,
        "independence_group": independence_group,
        "canonical_publisher_group": publisher_group,
        "source_status": source_status,
        "declared_stance": stance,
        "claim": claim,
        "hypothesis": hypothesis,
        "counter_hypothesis": counter_hypothesis,
        "related_entities": related_entities,
        "tags": tags,
        "assumptions": assumptions,
        "falsification_conditions": falsification,
        "raw_source_sha256": raw_hash,
        "raw_hash_present": raw_hash is not None,
        "receipt_status": receipt_status,
        "model_eligible": False,
        "research_only": True,
    }
    scenario_evidence = {
        "evidence_id": event_id,
        "hypothesis_id": hypothesis_id,
        "domain": domain,
        "hypothesis": hypothesis,
        "counter_hypothesis": counter_hypothesis,
        "claim": claim,
        "source_id": source_id,
        "source_name": source_name,
        "source_url": source_url,
        "independence_group": independence_group,
        "source_status": source_status,
        "stance": stance,
        "event_status": event_status,
        "event_time_utc": event_time_text,
        "available_at_utc": known_at_text,
        "raw_source_sha256": raw_hash,
        "assumptions": assumptions,
        "falsification_conditions": falsification,
    }
    return timeline_record, None, scenario_evidence

def build_event_timeline(
    *,
    asset: str = "XRP",
    data_cutoff_utc: str,
    horizon_seconds: int,
    event_records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build a deterministic event timeline and research-only scenario set.

    Future events are included only when explicitly scheduled, captured by the
    cutoff, and within the requested horizon. Historical events captured after
    the cutoff are excluded. Every scenario retains contrary evidence as
    minority objections and remains NOT_ISSUED/model-ineligible.
    """
    normalized_asset = _text(asset, "asset").upper()
    cutoff, cutoff_text = _utc(data_cutoff_utc, "data_cutoff_utc")
    if (
        isinstance(horizon_seconds, bool)
        or not isinstance(horizon_seconds, int)
        or horizon_seconds <= 0
    ):
        raise EventTimelineError("horizon_seconds must be a positive integer")
    if not isinstance(event_records, Sequence) or isinstance(
        event_records, (str, bytes)
    ):
        raise EventTimelineError("event_records must be a sequence of mappings")
    try:
        horizon_end = cutoff + timedelta(seconds=horizon_seconds)
    except OverflowError as exc:
        raise EventTimelineError("horizon_seconds exceeds the supported datetime range") from exc
    horizon_end_text = horizon_end.isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )

    timeline: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for index, record in enumerate(event_records):
        if isinstance(record, Mapping):
            candidate = record.get("event_id")
            if isinstance(candidate, str) and candidate.strip():
                candidate = candidate.strip()
                if candidate in seen_ids:
                    raise EventTimelineError(f"duplicate event_id: {candidate}")
                seen_ids.add(candidate)
        normalized, exclusion, scenario_record = _normalize_event(
            record,
            index,
            cutoff,
            horizon_end,
        )
        if exclusion is not None:
            excluded.append(exclusion)
        elif normalized is not None and scenario_record is not None:
            timeline.append(normalized)
            evidence.append(scenario_record)

    timeline.sort(
        key=lambda item: (
            item["event_time_utc"],
            item["event_type"],
            item["event_id"],
        )
    )
    excluded.sort(key=lambda item: (item["event_id"], item["reason"]))
    evidence.sort(key=lambda item: item["evidence_id"])

    try:
        scenarios = build_scenario_hypotheses(
            asset=normalized_asset,
            data_cutoff_utc=cutoff_text,
            horizon_seconds=horizon_seconds,
            evidence_records=evidence,
        )
        independence_groups = canonical_independence_groups(
            [
                {
                    "independence_group": item["independence_group"],
                    "source_uri": item["source_url"],
                }
                for item in timeline
            ]
        )
    except (ScenarioHypothesisError, ValueError) as exc:
        raise EventTimelineError(str(exc)) from exc

    raw_hash_present_count = sum(1 for item in timeline if item["raw_hash_present"])
    # Timeline inputs carry hashes but not independently verified canonical receipts.
    receipt_complete = False
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "barrot.xrp.point_in_time_event_timeline",
        "asset": normalized_asset,
        "data_cutoff_utc": cutoff_text,
        "horizon_seconds": horizon_seconds,
        "horizon_end_utc": horizon_end_text,
        "event_count": len(timeline),
        "event_timeline": timeline,
        "excluded_events": excluded,
        "source_independence_groups": independence_groups,
        "independent_source_group_count": len(independence_groups),
        "scenario_set": scenarios,
        "raw_hash_present_count": raw_hash_present_count,
        "receipt_complete": receipt_complete,
        "forecast_status": "NOT_ISSUED",
        "directional_forecast": False,
        "probabilities": None,
        "model_eligible": False,
        "research_only": True,
        "warnings": [
            "Event records are explicit inputs; this module does not discover or verify external events.",
            "A publisher SHA-256 digest is not a verified canonical receipt; raw bytes and receipt metadata are not validated here.",
            "A local SHA-256 chain is not an independent WORM or trusted timestamp anchor.",
            "Publisher independence is a conservative lineage heuristic, not proof of independent reporting.",
            "Scenario hypotheses are authored inputs; this module does not infer causality or forecast probabilities.",
            "Contrary evidence remains visible as minority objections; no majority-vote suppression occurs.",
        ],
    }
    payload["timeline_fingerprint"] = _canonical_hash(payload)
    payload["artifact_id"] = "event-timeline:" + _canonical_hash(payload)[:24]
    return payload
