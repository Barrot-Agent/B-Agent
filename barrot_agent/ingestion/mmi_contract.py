from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


MMI_PROTOCOL_VERSION = "1.0"
MMI_MAX_DEPTH = 4


class MMIState(str, Enum):
    RECEIVED = "RECEIVED"
    PROVENANCE_CAPTURED = "PROVENANCE_CAPTURED"
    DECOMPOSED = "DECOMPOSED"
    REPRESENTATIONS_ASSESSED = "REPRESENTATIONS_ASSESSED"
    EVIDENCE_NORMALIZED = "EVIDENCE_NORMALIZED"
    CORROBORATION = "CORROBORATION"
    GAP_ANALYSIS = "GAP_ANALYSIS"
    RECONCILIATION = "RECONCILIATION"
    LEARNING_EXTRACTED = "LEARNING_EXTRACTED"
    CAPABILITY_ANALYZED = "CAPABILITY_ANALYZED"
    ACQUISITION_TARGETS_GENERATED = "ACQUISITION_TARGETS_GENERATED"
    VERIFICATION = "VERIFICATION"
    MMI_COMPLETE = "MMI_COMPLETE"


class StageStatus(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class EvidenceState(str, Enum):
    OBSERVED = "OBSERVED"
    PARSED = "PARSED"
    DERIVED = "DERIVED"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"
    NOT_PARSABLE = "NOT_PARSABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class MMIOutcome(str, Enum):
    NEW_DATASET = "NEW_DATASET"
    DUPLICATE_RECOGNIZED = "DUPLICATE_RECOGNIZED"
    REVALIDATION_REQUESTED = "REVALIDATION_REQUESTED"
    SOURCE_UPDATED = "SOURCE_UPDATED"
    PARTIAL_REINGESTION = "PARTIAL_REINGESTION"


REQUIRED_STAGES = (
    MMIState.RECEIVED.value,
    MMIState.PROVENANCE_CAPTURED.value,
    MMIState.DECOMPOSED.value,
    MMIState.REPRESENTATIONS_ASSESSED.value,
    MMIState.EVIDENCE_NORMALIZED.value,
    MMIState.CORROBORATION.value,
    MMIState.GAP_ANALYSIS.value,
    MMIState.RECONCILIATION.value,
    MMIState.LEARNING_EXTRACTED.value,
    MMIState.CAPABILITY_ANALYZED.value,
    MMIState.ACQUISITION_TARGETS_GENERATED.value,
    MMIState.VERIFICATION.value,
)


@dataclass(frozen=True)
class MMISource:
    source_id: str
    source_type: str
    uri: str
    version: str
    content_hash: str
    acquired_at: str
    provenance: dict[str, Any] = field(default_factory=dict)

    def canonical(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MMIComponent:
    component_id: str
    parent_id: str | None
    name: str
    component_depth: int
    provenance_depth: int
    state: EvidenceState
    source_id: str
    content_hash: str | None = None
    children: list[str] = field(default_factory=list)

    def validate(self, max_depth: int = MMI_MAX_DEPTH) -> list[str]:
        errors: list[str] = []

        if self.component_depth < 0 or self.component_depth > max_depth:
            errors.append(
                f"{self.component_id}: component_depth outside 0..{max_depth}"
            )

        if self.provenance_depth < 0 or self.provenance_depth > max_depth:
            errors.append(
                f"{self.component_id}: provenance_depth outside 0..{max_depth}"
            )

        if not self.component_id:
            errors.append("component_id is required")

        if not self.source_id:
            errors.append(f"{self.component_id}: source_id is required")

        return errors


@dataclass
class MMIStage:
    name: str
    status: StageStatus
    evidence_refs: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class MMIEvidence:
    evidence_id: str
    source_id: str
    component_id: str | None
    state: EvidenceState
    statement: str
    support_refs: list[str] = field(default_factory=list)
    contradiction_refs: list[str] = field(default_factory=list)
    independent_sources: list[str] = field(default_factory=list)
    quality: float | None = None
    confidence: float | None = None
    generated_by_barrot: bool = False

    def validate(self) -> list[str]:
        errors: list[str] = []

        if self.quality is not None and not 0 <= self.quality <= 1:
            errors.append(f"{self.evidence_id}: quality must be 0..1")

        if self.confidence is not None and not 0 <= self.confidence <= 1:
            errors.append(f"{self.evidence_id}: confidence must be 0..1")

        # Barrot-generated material can be evidence, but never independent
        # corroboration.
        if self.generated_by_barrot and self.evidence_id in self.independent_sources:
            errors.append(
                f"{self.evidence_id}: self-generated evidence cannot corroborate itself"
            )

        return errors


@dataclass
class MMIResult:
    source: MMISource
    stages: list[MMIStage]
    components: list[MMIComponent] = field(default_factory=list)
    evidence: list[MMIEvidence] = field(default_factory=list)
    gaps: list[dict[str, Any]] = field(default_factory=list)
    acquisition_targets: list[dict[str, Any]] = field(default_factory=list)
    outcome: MMIOutcome = MMIOutcome.NEW_DATASET
    scope_boundary: dict[str, Any] = field(default_factory=dict)
    termination: dict[str, Any] = field(default_factory=dict)
    knowledge_complete: bool = False
    protocol_complete: bool = False

    def canonical(self) -> dict[str, Any]:
        return {
            "protocol_version": MMI_PROTOCOL_VERSION,
            "source": self.source.canonical(),
            "stages": [asdict(x) for x in self.stages],
            "components": [
                {
                    **asdict(x),
                    "state": x.state.value,
                }
                for x in self.components
            ],
            "evidence": [
                {
                    **asdict(x),
                    "state": x.state.value,
                }
                for x in self.evidence
            ],
            "gaps": self.gaps,
            "acquisition_targets": self.acquisition_targets,
            "outcome": self.outcome.value,
            "scope_boundary": self.scope_boundary,
            "termination": self.termination,
            "knowledge_complete": self.knowledge_complete,
            "protocol_complete": self.protocol_complete,
        }

    def content_hash(self) -> str:
        payload = json.dumps(
            self.canonical(),
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        return sha256(payload).hexdigest()


def clamp_depth(depth: int, maximum: int = MMI_MAX_DEPTH) -> int:
    return max(0, min(int(depth), maximum))


def assess_representation(value: Any) -> EvidenceState:
    if value is None:
        return EvidenceState.NOT_APPLICABLE

    if isinstance(value, (bytes, bytearray)):
        return EvidenceState.OBSERVED if value else EvidenceState.UNKNOWN

    if isinstance(value, (str, int, float, bool, list, tuple, dict)):
        return EvidenceState.PARSED

    return EvidenceState.NOT_PARSABLE


def build_stage_map(stages: list[MMIStage]) -> dict[str, MMIStage]:
    return {stage.name: stage for stage in stages}
