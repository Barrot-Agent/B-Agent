"""Canonical Massive Micro Ingestion (MMI) V1 contracts.

These types define evidence and execution boundaries. They deliberately do not
infer truth: parsers, models, and acquisition adapters must report what they
actually observed. The evaluator consumes these immutable declarations.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from urllib.parse import urlparse


_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class ContractError(ValueError):
    """Raised when an MMI declaration is incomplete or internally invalid."""


class ParsabilityState(str, Enum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    UNSUPPORTED = "unsupported"
    MALFORMED = "malformed"
    EMPTY = "empty"
    UNAVAILABLE = "unavailable"


class EvidenceOrigin(str, Enum):
    EXTERNAL = "external"
    BARROT_GENERATED = "barrot_generated"
    USER_SUPPLIED = "user_supplied"
    DERIVED = "derived"


class FreshnessState(str, Enum):
    CURRENT = "current"
    AGING = "aging"
    STALE = "stale"
    UNKNOWN = "unknown"


class MMIExecutionState(str, Enum):
    DECLARED = "declared"
    AUTHORIZED = "authorized"
    ACQUIRED = "acquired"
    PARSED = "parsed"
    PARTIAL = "partial"
    CORROBORATED = "corroborated"
    DISPUTED = "disputed"
    RECONCILED = "reconciled"
    LEARNED = "learned"
    ACCEPTED = "accepted"
    FAILED = "failed"
    BLOCKED = "blocked"
    STALE = "stale"
    UNAVAILABLE = "unavailable"
    NOT_IN_SCOPE = "not_in_scope"


@dataclass(frozen=True)
class ScopeDeclaration:
    """Finite, explicit scope and resource contract for one target."""

    included: tuple[str, ...]
    excluded: tuple[str, ...] = ()
    component_depth: int = 4
    source_depth: int = 4
    max_nodes: int = 10_000
    max_bytes: int = 50_000_000
    max_records: int = 100_000
    max_elapsed_seconds: int = 900

    def __post_init__(self) -> None:
        if not self.included or any(not item.strip() for item in self.included):
            raise ContractError("scope.included must contain non-empty declarations")
        if self.component_depth != 4 or self.source_depth != 4:
            raise ContractError("MMI V1 requires exactly four component and source depths")
        for name in ("max_nodes", "max_bytes", "max_records", "max_elapsed_seconds"):
            if getattr(self, name) <= 0:
                raise ContractError(f"{name} must be positive")
        if set(self.included) & set(self.excluded):
            raise ContractError("a scope item cannot be both included and excluded")


@dataclass(frozen=True)
class DatasetTarget:
    """Stable target identity plus the declared acquisition and parsing scope."""

    target_id: str
    source_uri: str
    scope: ScopeDeclaration
    expected_license: str = "unknown"
    expected_version: Optional[str] = None
    origin: EvidenceOrigin = EvidenceOrigin.EXTERNAL

    def __post_init__(self) -> None:
        if not self.target_id.strip():
            raise ContractError("target_id is required")
        parsed = urlparse(self.source_uri)
        if parsed.scheme not in {"https", "http", "file"}:
            raise ContractError("source_uri must use https, http, or file")
        if self.origin == EvidenceOrigin.BARROT_GENERATED and parsed.scheme in {"http", "https"}:
            # Generated artifacts may be stored remotely; origin remains explicit.
            return


@dataclass(frozen=True)
class AcquisitionManifest:
    """Immutable identity for bytes actually retrieved, not a configured source."""

    execution_id: str
    target_id: str
    source_uri: str
    retrieved_at: str
    content_sha256: str
    byte_count: int
    license: str
    version: Optional[str] = None
    content_range: Optional[str] = None
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    origin: EvidenceOrigin = EvidenceOrigin.EXTERNAL
    parent_artifact_sha256: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.execution_id or not self.target_id or not self.retrieved_at:
            raise ContractError("execution_id, target_id, and retrieved_at are required")
        if not _SHA256.fullmatch(self.content_sha256):
            raise ContractError("content_sha256 must be 64 lowercase hexadecimal characters")
        if self.byte_count < 0:
            raise ContractError("byte_count cannot be negative")
        if self.parent_artifact_sha256 and not _SHA256.fullmatch(self.parent_artifact_sha256):
            raise ContractError("parent_artifact_sha256 must be a SHA-256 digest")


@dataclass(frozen=True)
class ParseCoverage:
    """Parser result with explicit loss/unsupported accounting."""

    parser_id: str
    state: ParsabilityState
    parsed_units: int
    total_units: Optional[int] = None
    unsupported_ranges: tuple[str, ...] = ()
    dropped_ranges: tuple[str, ...] = ()
    error_code: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.parser_id:
            raise ContractError("parser_id is required")
        if self.parsed_units < 0 or (self.total_units is not None and self.total_units < 0):
            raise ContractError("parse counts cannot be negative")
        if self.total_units is not None and self.parsed_units > self.total_units:
            raise ContractError("parsed_units cannot exceed total_units")
        if self.state == ParsabilityState.COMPLETE and (
            self.unsupported_ranges or self.dropped_ranges
            or (self.total_units is not None and self.parsed_units != self.total_units)
        ):
            raise ContractError("complete parsing cannot contain omitted or unsupported units")


@dataclass(frozen=True)
class SourceLocation:
    """Exact location within the acquired representation."""

    locator: str
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None
    page: Optional[int] = None
    section: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.locator:
            raise ContractError("source locator is required")
        if self.start_offset is not None and self.start_offset < 0:
            raise ContractError("start_offset cannot be negative")
        if self.end_offset is not None and (
            self.start_offset is None or self.end_offset < self.start_offset
        ):
            raise ContractError("end_offset requires a valid start_offset")


@dataclass(frozen=True)
class Observation:
    """Verbatim or losslessly represented source observation; never a model summary."""

    observation_id: str
    acquisition_sha256: str
    raw_value: str
    location: SourceLocation
    origin: EvidenceOrigin = EvidenceOrigin.EXTERNAL

    def __post_init__(self) -> None:
        if not self.observation_id or not self.raw_value:
            raise ContractError("observation_id and raw_value are required")
        if not _SHA256.fullmatch(self.acquisition_sha256):
            raise ContractError("observation must reference a valid acquisition digest")


@dataclass(frozen=True)
class Interpretation:
    """A derived interpretation, explicitly linked to observations and method."""

    interpretation_id: str
    observation_ids: tuple[str, ...]
    method: str
    method_version: str
    output: str

    def __post_init__(self) -> None:
        if not self.interpretation_id or not self.observation_ids or not self.method:
            raise ContractError("interpretation requires id, observations, and method")
        if not self.method_version or not self.output:
            raise ContractError("interpretation requires method_version and output")


@dataclass(frozen=True)
class SourceLineage:
    """Lineage metadata used to avoid counting copied/syndicated sources independently."""

    source_id: str
    publisher_id: Optional[str] = None
    owner_id: Optional[str] = None
    parent_source_id: Optional[str] = None
    content_sha256: Optional[str] = None
    syndicated_from: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.source_id:
            raise ContractError("source_id is required")
        if self.content_sha256 and not _SHA256.fullmatch(self.content_sha256):
            raise ContractError("content_sha256 must be a SHA-256 digest")


@dataclass(frozen=True)
class FreshnessPolicy:
    """Deterministic age thresholds in seconds."""

    aging_after_seconds: int
    stale_after_seconds: int

    def __post_init__(self) -> None:
        if self.aging_after_seconds < 0 or self.stale_after_seconds <= self.aging_after_seconds:
            raise ContractError("freshness thresholds must satisfy 0 <= aging < stale")


@dataclass(frozen=True)
class CompletenessReport:
    """Independent protocol and knowledge completeness dimensions."""

    protocol_complete: bool
    knowledge_complete: bool
    required_scope_units: int
    parsed_scope_units: int
    unresolved_gaps: tuple[str, ...] = ()
    exclusions_applied: tuple[str, ...] = ()
    failure_reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.required_scope_units < 0 or self.parsed_scope_units < 0:
            raise ContractError("completeness counts cannot be negative")
        if self.parsed_scope_units > self.required_scope_units:
            raise ContractError("parsed scope cannot exceed required scope")
        if self.knowledge_complete and self.unresolved_gaps:
            raise ContractError("knowledge cannot be complete while gaps remain")
