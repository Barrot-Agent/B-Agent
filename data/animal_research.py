"""Safe, provenance-first registry utilities for animal communication research.

The module deliberately stores observations separately from interpretations.
Records are not publishable until a human reviewer approves them.
"""

from __future__ import annotations

import hashlib
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Iterable, List, Mapping, Sequence, Tuple

TRUSTED_SOURCES = {
    "peer_reviewed_literature": ("api.crossref.org", "https://api.crossref.org/works"),
    "institutional_repository": ("repository.example.edu", "https://repository.example.edu/api"),
    "experiment_registry": ("osf.io", "https://api.osf.io/v2/nodes/"),
    "open_dataset": ("dataverse.harvard.edu", "https://dataverse.harvard.edu/api/"),
}

_REQUIRED = (
    "title",
    "species",
    "study_context",
    "communication_method",
    "observations",
    "provenance",
    "ethics_approval",
    "reproducibility",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_list(value: Any) -> List[str]:
    if isinstance(value, str):
        return [value] if value.strip() else []
    return [str(item).strip() for item in value or [] if str(item).strip()]


def _text(record: Mapping[str, Any]) -> str:
    values: List[str] = []
    for key in ("title", "species", "study_context", "communication_method", "observations", "findings"):
        values.extend(_as_list(record.get(key)))
    return " ".join(values).lower()


def validate_record(record: Mapping[str, Any]) -> List[str]:
    """Return validation errors without guessing missing scientific facts."""
    errors = [f"missing {key}" for key in _REQUIRED if key not in record]
    for key in ("species", "communication_method", "observations"):
        if key in record and not _as_list(record[key]):
            errors.append(f"{key} must contain at least one item")
    provenance = record.get("provenance")
    if not isinstance(provenance, Mapping) or not provenance.get("source_url"):
        errors.append("provenance.source_url is required")
    ethics = record.get("ethics_approval")
    if not isinstance(ethics, Mapping) or not ethics.get("status"):
        errors.append("ethics_approval.status is required")
    reproducibility = record.get("reproducibility")
    if not isinstance(reproducibility, Mapping) or not reproducibility.get("status"):
        errors.append("reproducibility.status is required")
    return errors


def normalize_record(raw: Mapping[str, Any]) -> Dict[str, Any]:
    """Normalize an external record and assign a stable identity."""
    source_url = str(raw.get("provenance", {}).get("source_url", raw.get("url", ""))).strip()
    title = " ".join(str(raw.get("title", "")).split())
    species = sorted(set(_as_list(raw.get("species"))))
    identity = "|".join((title.lower(), source_url.lower(), ",".join(species)))
    record_id = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:20]
    result = dict(raw)
    result.update(
        record_id=record_id,
        title=title,
        species=species,
        communication_method=sorted(set(_as_list(raw.get("communication_method")))),
        observations=_as_list(raw.get("observations")),
        findings=_as_list(raw.get("findings")),
        uncertainty=_as_list(raw.get("uncertainty")),
        provenance=dict(raw.get("provenance") or {}, source_url=source_url),
        ethics_approval=dict(raw.get("ethics_approval") or {}),
        reproducibility=dict(raw.get("reproducibility") or {}),
        evidence_grade=grade_evidence(raw),
        status=str(raw.get("status", "draft")),
        version=int(raw.get("version", 1)),
        updated_at=str(raw.get("updated_at", _now())),
    )
    errors = validate_record(result)
    if errors:
        raise ValueError("; ".join(errors))
    return result


def grade_evidence(record: Mapping[str, Any]) -> str:
    """Conservative grade; it never upgrades a record based on interpretation."""
    design = str(record.get("study_design", "")).lower()
    reproducibility_data = record.get("reproducibility", {})
    reproducibility = (
        str(reproducibility_data.get("status", "")).lower()
        if isinstance(reproducibility_data, Mapping)
        else ""
    )
    if reproducibility in {"replicated", "independently_replicated"} and "controlled" in design:
        return "A"
    if reproducibility in {"replicated", "independently_replicated"}:
        return "B"
    if "controlled" in design or record.get("sample_size", 0) not in (0, None):
        return "C"
    return "D"


def merge_versions(records: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicate by stable identity while retaining the newest version."""
    latest: Dict[str, Dict[str, Any]] = {}
    for raw in records:
        item = normalize_record(raw)
        current = latest.get(item["record_id"])
        if current is None or (item["version"], item["updated_at"]) >= (
            current["version"],
            current["updated_at"],
        ):
            latest[item["record_id"]] = item
    return sorted(latest.values(), key=lambda item: item["record_id"])


def cross_reference(records: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """Build searchable facets and flag opposite findings for human review."""
    facets: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
    claims: Dict[Tuple[str, str], Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
    for record in records:
        rid = str(record["record_id"])
        for field in ("species", "communication_method"):
            for value in _as_list(record.get(field)):
                facets[field][value].append(rid)
        for field in ("study_context", "observations", "findings", "uncertainty"):
            for value in _as_list(record.get(field)):
                facets[field][value].append(rid)
        for finding in _as_list(record.get("findings")):
            key = (
                ",".join(sorted(_as_list(record.get("species")))),
                " ".join(
                    re.sub(
                        r"\b(?:do|does|did)\s+not\b|\b(?:not|no|avoid)\b",
                        "",
                        finding.lower(),
                    ).split()
                ),
            )
            polarity = "negative" if re.search(r"\bnot\b|\bno\b|\bavoid", finding.lower()) else "positive"
            claims[key][polarity].append(rid)
    contradictions = [
        {"claim": key[1], "records": dict(polarities)}
        for key, polarities in claims.items()
        if len(polarities) > 1
    ]
    return {"facets": {key: dict(value) for key, value in facets.items()}, "contradictions": contradictions}


class ReviewQueue:
    """Human approval gate for interpretations and publication."""

    def __init__(self, records: Iterable[Mapping[str, Any]] = ()) -> None:
        self.records = {record["record_id"]: dict(record) for record in records}

    def approve(self, record_id: str, reviewer: str) -> Dict[str, Any]:
        if record_id not in self.records:
            raise KeyError(record_id)
        if not reviewer.strip():
            raise ValueError("reviewer is required")
        record = self.records[record_id]
        record["status"] = "approved"
        record["review"] = {"reviewer": reviewer, "reviewed_at": _now()}
        return record

    def publishable(self) -> List[Dict[str, Any]]:
        return [record for record in self.records.values() if record.get("status") == "approved"]


def search_records(query: str, records: Sequence[Mapping[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
    """Dependency-free retrieval across the cross-referenceable text fields."""
    terms = set(re.findall(r"[a-z0-9]+", query.lower()))
    ranked = []
    for record in records:
        score = len(terms & set(re.findall(r"[a-z0-9]+", _text(record))))
        if score:
            ranked.append((score, record))
    return [dict(record) for _, record in sorted(ranked, key=lambda item: item[0], reverse=True)[:limit]]


def fetch_trusted_source(
    source_type: str,
    url: str,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> List[Dict[str, Any]]:
    """Fetch JSON or RSS only from the configured host for a source type."""
    if source_type not in TRUSTED_SOURCES:
        raise ValueError(f"unsupported source type: {source_type}")
    expected_host, _ = TRUSTED_SOURCES[source_type]
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != expected_host:
        raise ValueError("source URL is not on the trusted HTTPS host")
    with opener(url, timeout=20) as response:
        payload = response.read()
    try:
        data = json.loads(payload)
        items = data.get("items", data.get("records", data)) if isinstance(data, Mapping) else data
        return [dict(item) for item in items if isinstance(item, Mapping)]
    except (json.JSONDecodeError, TypeError):
        root = ET.fromstring(payload)
        return [
            {"title": item.findtext("title", ""), "url": item.findtext("link", "")}
            for item in root.iter("item")
        ]
