"""Deterministic, point-in-time scenario and counter-hypothesis assembly.

This module organizes explicitly authored, provenance-bound research hypotheses.
It is wired to scheduled XRP event-timeline capture, but does not infer causal
relationships, generate forecast probabilities, or issue directional forecasts.
It remains research-only until independent raw-source anchoring and the separate
out-of-sample readiness gates are satisfied.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlsplit

from .source_independence import canonical_independence_groups


SCHEMA_VERSION = "1.0.0"
_ALLOWED_STANCES = {"supports", "contradicts", "context"}
_ALLOWED_SOURCE_STATUSES = {"verified", "disputed", "provisional", "unverified"}
_ALLOWED_EVENT_STATUSES = {"occurred", "scheduled", "ongoing", "unknown"}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class ScenarioHypothesisError(ValueError):
    """Raised when scenario evidence is malformed or not point-in-time safe."""


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ScenarioHypothesisError(f"{field} must be a non-empty string")
    return value.strip()


def _utc(value: Any, field: str) -> tuple[datetime, str]:
    raw = _text(value, field)
    try:
        candidate = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ScenarioHypothesisError(
            f"{field} must be an ISO-8601 timestamp"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ScenarioHypothesisError(f"{field} must include a timezone")
    normalized = parsed.astimezone(timezone.utc)
    timespec = "microseconds" if normalized.microsecond else "seconds"
    normalized_text = normalized.isoformat(timespec=timespec).replace("+00:00", "Z")
    return normalized, normalized_text


def _string_list(value: Any, field: str, *, required: bool = False) -> list[str]:
    if value is None and not required:
        return []
    if not isinstance(value, (list, tuple)):
        raise ScenarioHypothesisError(
            f"{field} must be a list or tuple of strings"
        )
    normalized = sorted(
        {_text(item, f"{field}[]") for item in value},
        key=str.casefold,
    )
    if required and not normalized:
        raise ScenarioHypothesisError(f"{field} must contain at least one item")
    return normalized


def _source_url(value: Any, field: str) -> str:
    raw = _text(value, field)
    try:
        parsed = urlsplit(raw)
        hostname = parsed.hostname
        username = parsed.username
        password = parsed.password
    except ValueError as exc:
        raise ScenarioHypothesisError(
            f"{field} must be a valid HTTP(S) URL"
        ) from exc
    if parsed.scheme.lower() not in {"http", "https"} or not hostname:
        raise ScenarioHypothesisError(f"{field} must be a valid HTTP(S) URL")
    if username or password:
        raise ScenarioHypothesisError(
            f"{field} must not contain embedded credentials"
        )
    return raw


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _normalize_evidence(
    record: Any,
    index: int,
    cutoff: datetime,
) -> tuple[dict[str, Any] | None, dict[str, str] | None]:
    prefix = f"evidence_records[{index}]"
    if not isinstance(record, Mapping):
        raise ScenarioHypothesisError(f"{prefix} must be a mapping")

    evidence_id = _text(record.get("evidence_id"), f"{prefix}.evidence_id")
    hypothesis_id = _text(record.get("hypothesis_id"), f"{prefix}.hypothesis_id")
    domain = _text(record.get("domain"), f"{prefix}.domain")
    hypothesis = _text(record.get("hypothesis"), f"{prefix}.hypothesis")
    counter_hypothesis = _text(
        record.get("counter_hypothesis"),
        f"{prefix}.counter_hypothesis",
    )
    claim = _text(record.get("claim"), f"{prefix}.claim")
    source_id = _text(record.get("source_id"), f"{prefix}.source_id")
    source_name = str(record.get("source_name") or source_id).strip()
    independence_group = _text(
        record.get("independence_group"),
        f"{prefix}.independence_group",
    )
    source_url = _source_url(record.get("source_url"), f"{prefix}.source_url")

    stance = _text(record.get("stance"), f"{prefix}.stance").lower()
    if stance not in _ALLOWED_STANCES:
        raise ScenarioHypothesisError(
            f"{prefix}.stance must be one of {sorted(_ALLOWED_STANCES)}"
        )
    source_status = _text(
        record.get("source_status"),
        f"{prefix}.source_status",
    ).lower()
    if source_status not in _ALLOWED_SOURCE_STATUSES:
        raise ScenarioHypothesisError(
            f"{prefix}.source_status must be one of "
            f"{sorted(_ALLOWED_SOURCE_STATUSES)}"
        )
    event_status = _text(
        record.get("event_status"),
        f"{prefix}.event_status",
    ).lower()
    if event_status not in _ALLOWED_EVENT_STATUSES:
        raise ScenarioHypothesisError(
            f"{prefix}.event_status must be one of "
            f"{sorted(_ALLOWED_EVENT_STATUSES)}"
        )

    event_time, event_time_text = _utc(
        record.get("event_time_utc"),
        f"{prefix}.event_time_utc",
    )
    available_at, available_at_text = _utc(
        record.get("available_at_utc"),
        f"{prefix}.available_at_utc",
    )

    if available_at > cutoff:
        return None, {
            "evidence_id": evidence_id,
            "reason": "not_available_by_data_cutoff",
        }
    if event_status == "occurred" and event_time > cutoff:
        return None, {
            "evidence_id": evidence_id,
            "reason": "occurred_event_is_after_data_cutoff",
        }
    if event_status == "scheduled" and event_time <= cutoff:
        return None, {
            "evidence_id": evidence_id,
            "reason": "scheduled_event_time_has_elapsed",
        }
    if event_status in {"ongoing", "unknown"} and event_time > cutoff:
        return None, {
            "evidence_id": evidence_id,
            "reason": "future_event_is_not_verified_as_scheduled",
        }

    raw_hash = record.get("raw_source_sha256")
    if raw_hash is not None:
        raw_hash = _text(raw_hash, f"{prefix}.raw_source_sha256").lower()
        if not _SHA256_RE.fullmatch(raw_hash):
            raise ScenarioHypothesisError(
                f"{prefix}.raw_source_sha256 must be a 64-character SHA-256 hex digest"
            )

    assumptions = _string_list(
        record.get("assumptions"),
        f"{prefix}.assumptions",
    )
    falsification = _string_list(
        record.get("falsification_conditions"),
        f"{prefix}.falsification_conditions",
        required=True,
    )

    # Provisional or unverified sources remain visible but cannot support or
    # contradict a hypothesis until their source identity and contents are checked.
    effective_stance = (
        "context" if source_status in {"provisional", "unverified"} else stance
    )

    normalized = {
        "evidence_id": evidence_id,
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
        "declared_stance": stance,
        "stance": effective_stance,
        "event_status": event_status,
        "event_time_utc": event_time_text,
        "available_at_utc": available_at_text,
        "event_is_future": event_time > cutoff,
        "raw_source_sha256": raw_hash,
        "receipt_status": "SHA256_PRESENT" if raw_hash else "MISSING_RAW_RECEIPT_HASH",
        "assumptions": assumptions,
        "falsification_conditions": falsification,
    }
    return normalized, None


def _independent_groups(records: list[dict[str, Any]]) -> list[str]:
    return canonical_independence_groups(
        [
            {
                "independence_group": record["independence_group"],
                "source_uri": record["source_url"],
            }
            for record in records
        ]
    )


def build_scenario_hypotheses(
    *,
    asset: str,
    data_cutoff_utc: str,
    horizon_seconds: int,
    evidence_records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build research-only scenarios while preserving all counter-evidence.

    Each evidence record must provide an authored hypothesis and counter-hypothesis,
    source identity and lineage, event and availability timestamps, a stance, and
    at least one falsification condition. Future scheduled events are allowed only
    when the schedule was available by the data cutoff. Evidence captured later is
    excluded to prevent look-ahead leakage.
    """
    normalized_asset = _text(asset, "asset").upper()
    cutoff, cutoff_text = _utc(data_cutoff_utc, "data_cutoff_utc")
    if isinstance(horizon_seconds, bool) or not isinstance(horizon_seconds, int):
        raise ScenarioHypothesisError("horizon_seconds must be a positive integer")
    if horizon_seconds <= 0:
        raise ScenarioHypothesisError("horizon_seconds must be a positive integer")
    if not isinstance(evidence_records, Sequence) or isinstance(
        evidence_records,
        (str, bytes),
    ):
        raise ScenarioHypothesisError(
            "evidence_records must be a sequence of mappings"
        )

    normalized: list[dict[str, Any]] = []
    excluded: list[dict[str, str]] = []
    seen_ids: set[str] = set()

    for index, record in enumerate(evidence_records):
        if isinstance(record, Mapping):
            candidate_id = record.get("evidence_id")
            if isinstance(candidate_id, str) and candidate_id.strip():
                candidate_id = candidate_id.strip()
                if candidate_id in seen_ids:
                    raise ScenarioHypothesisError(
                        f"duplicate evidence_id: {candidate_id}"
                    )
                seen_ids.add(candidate_id)
        item, exclusion = _normalize_evidence(record, index, cutoff)
        if exclusion is not None:
            excluded.append(exclusion)
        elif item is not None:
            normalized.append(item)

    normalized.sort(key=lambda item: item["evidence_id"])
    excluded.sort(key=lambda item: (item["evidence_id"], item["reason"]))

    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in normalized:
        grouped.setdefault(item["hypothesis_id"], []).append(item)

    scenarios: list[dict[str, Any]] = []
    for hypothesis_id in sorted(grouped, key=str.casefold):
        records = grouped[hypothesis_id]
        definitions = {
            (item["domain"], item["hypothesis"], item["counter_hypothesis"])
            for item in records
        }
        if len(definitions) != 1:
            raise ScenarioHypothesisError(
                f"hypothesis_id {hypothesis_id!r} has conflicting definitions"
            )
        domain, hypothesis, counter_hypothesis = next(iter(definitions))

        supporting = [item for item in records if item["stance"] == "supports"]
        contrary = [item for item in records if item["stance"] == "contradicts"]
        context = [item for item in records if item["stance"] == "context"]

        all_groups = _independent_groups(records)
        supporting_groups = _independent_groups(supporting)
        contrary_groups = _independent_groups(contrary)
        context_groups = _independent_groups(context)
        evidence_ids = [item["evidence_id"] for item in records]
        scenario_identity = {
            "asset": normalized_asset,
            "data_cutoff_utc": cutoff_text,
            "horizon_seconds": horizon_seconds,
            "hypothesis_id": hypothesis_id,
            "hypothesis": hypothesis,
            "counter_hypothesis": counter_hypothesis,
            "evidence_fingerprint": _canonical_hash(records),
        }
        scenario_id = "scenario:" + _canonical_hash(scenario_identity)[:24]

        scenarios.append(
            {
                "scenario_id": scenario_id,
                "hypothesis_id": hypothesis_id,
                "domain": domain,
                "data_cutoff_utc": cutoff_text,
                "horizon_seconds": horizon_seconds,
                "hypothesis": hypothesis,
                "counter_hypothesis": counter_hypothesis,
                "supporting_evidence": supporting,
                "contrary_evidence": contrary,
                # Never suppress objections because one side has more sources.
                "minority_objections": contrary,
                "context_evidence": context,
                "source_groups": {
                    "all": all_groups,
                    "supporting": supporting_groups,
                    "contrary": contrary_groups,
                    "context": context_groups,
                },
                "independent_source_groups_count": len(all_groups),
                "disagreement_present": bool(supporting and contrary),
                "minority_objection_count": len(contrary),
                "assumptions": sorted(
                    {
                        assumption
                        for item in records
                        for assumption in item["assumptions"]
                    },
                    key=str.casefold,
                ),
                "falsification_conditions": sorted(
                    {
                        condition
                        for item in records
                        for condition in item["falsification_conditions"]
                    },
                    key=str.casefold,
                ),
                "receipt_complete": all(
                    item["raw_source_sha256"] is not None for item in records
                ),
                "future_scheduled_event_count": sum(
                    1
                    for item in records
                    if item["event_status"] == "scheduled" and item["event_is_future"]
                ),
                "forecast_status": "NOT_ISSUED",
                "directional_forecast": False,
                "probabilities": None,
                "model_eligible": False,
                "research_only": True,
            }
        )

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "barrot.scenario_hypothesis_set",
        "asset": normalized_asset,
        "data_cutoff_utc": cutoff_text,
        "horizon_seconds": horizon_seconds,
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "excluded_evidence": excluded,
        "forecast_status": "NOT_ISSUED",
        "directional_forecast": False,
        "probabilities": None,
        "model_eligible": False,
        "research_only": True,
        "receipt_complete": all(
            item["raw_source_sha256"] is not None for item in normalized
        ),
        "evidence_fingerprint": _canonical_hash(normalized),
        "source_independence_note": (
            "Publisher and declared-lineage grouping is a conservative heuristic, "
            "not proof that underlying data or reporting are independent."
        ),
        "warnings": [
            "Hypotheses and counter-hypotheses are explicitly authored inputs; this module does not infer causality.",
            "Contrary evidence is retained as minority_objections and is never removed by a majority vote.",
            "The output is research-only and cannot be used as a directional forecast or model feature.",
        ],
    }
    payload["artifact_id"] = "scenario-set:" + _canonical_hash(payload)[:24]
    return payload
