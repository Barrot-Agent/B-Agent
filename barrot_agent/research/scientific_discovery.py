from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Iterable

from barrot_agent.evolution.claim_integrity import ClaimIntegrityEngine
from barrot_agent.orchestration.repository_repair import RepairError
from barrot_agent.orchestration.shared_runtime import (
    Artifact,
    Checkpoint,
    CompletionGate,
    DurableStateStore,
    ExecutionRecord,
    Failure,
    FailureCode,
    Fingerprint,
    RetryPolicy,
    TaskState,
    ValidationResult,
    bounded_subprocess,
)


class ResearchState(str, Enum):
    IDLE = "IDLE"
    AUDITING = "AUDITING"
    SOURCE_INGESTION = "SOURCE_INGESTION"
    TRACK_PLANNING = "TRACK_PLANNING"
    TRACK_EXECUTION = "TRACK_EXECUTION"
    SYNTHESIS = "SYNTHESIS"
    FORMALIZATION = "FORMALIZATION"
    FORMAL_VERIFICATION = "FORMAL_VERIFICATION"
    ADVERSARIAL_REVIEW = "ADVERSARIAL_REVIEW"
    INDEPENDENT_VERIFICATION = "INDEPENDENT_VERIFICATION"
    ACCEPTANCE_GATE = "ACCEPTANCE_GATE"
    COMPLETE = "COMPLETE"
    NO_SOLUTION_CLAIM = "NO_SOLUTION_CLAIM"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    RETRY_EXHAUSTED = "RETRY_EXHAUSTED"


class ClaimStatus(str, Enum):
    UNASSESSED = "UNASSESSED"
    HYPOTHESIS = "HYPOTHESIS"
    SUPPORTED = "SUPPORTED"
    REPRODUCED = "REPRODUCED"
    FORMALIZED = "FORMALIZED"
    FORMALLY_VERIFIED = "FORMALLY_VERIFIED"
    INDEPENDENTLY_VERIFIED = "INDEPENDENTLY_VERIFIED"
    CHALLENGED = "CHALLENGED"
    REFUTED = "REFUTED"
    DISPUTED = "DISPUTED"
    UNRESOLVED = "UNRESOLVED"


class EvidenceKind(str, Enum):
    ASSUMPTION = "assumption"
    DEFINITION = "definition"
    LEMMA = "lemma"
    PROPOSITION = "proposition"
    ESTIMATE = "estimate"
    THEOREM = "theorem"
    CONSEQUENCE = "consequence"
    FORMALIZATION = "formalization"
    COMPUTATIONAL = "computational_evidence"
    ADVERSARIAL = "adversarial_objection"
    INDEPENDENT = "independent_verification"
    UNRESOLVED = "unresolved_question"


class VerificationIndependence(str, Enum):
    SAME_SOURCE = "same_source_confirmation"
    SAME_MODEL = "same_model_confirmation"
    CROSS_MODEL = "cross_model_confirmation"
    INDEPENDENT_IMPLEMENTATION = "independent_implementation"
    INDEPENDENT_DERIVATION = "independent_mathematical_derivation"
    FORMAL = "formal_verification"
    SOURCE_TEAM_FORMAL = "formally_verified_by_source_team"
    LITERATURE = "independent_literature_corroboration"


class ConvergenceIndependence(str, Enum):
    INDEPENDENT = "INDEPENDENT"
    DEPENDENT = "DEPENDENT"
    PARTIALLY_INDEPENDENT = "PARTIALLY_INDEPENDENT"
    UNKNOWN = "UNKNOWN"
    INVALID = "INVALID"


class ConvergenceStatus(str, Enum):
    AGREEMENT = "AGREEMENT"
    CONVERGENCE = "CONVERGENCE"
    PARTIAL_CONVERGENCE = "PARTIAL_CONVERGENCE"
    CONTRADICTION = "CONTRADICTION"
    DIVERGENCE = "DIVERGENCE"
    DUPLICATION = "DUPLICATION"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class ScenarioMaturity(str, Enum):
    OBSERVED = "OBSERVED"
    REPORTED = "REPORTED"
    CORROBORATED = "CORROBORATED"
    EMERGING = "EMERGING"
    PLAUSIBLE = "PLAUSIBLE"
    SPECULATIVE = "SPECULATIVE"
    UNRESOLVED = "UNRESOLVED"
    REFUTED = "REFUTED"


class ScenarioRelationshipType(str, Enum):
    DEPENDS_ON = "DEPENDS_ON"
    ENABLES = "ENABLES"
    CONSTRAINS = "CONSTRAINS"
    CORRELATES_WITH = "CORRELATES_WITH"
    CAUSES = "CAUSES"
    MAY_CAUSE = "MAY_CAUSE"
    REQUIRES = "REQUIRES"
    CONFLICTS_WITH = "CONFLICTS_WITH"
    SPECULATED_TO_ENABLE = "SPECULATED_TO_ENABLE"


TERMINAL_RESEARCH_STATUSES = {"complete", "no_solution_claim", "failed", "blocked"}
TRANSFERABLE_STATUSES = {
    ClaimStatus.SUPPORTED.value,
    ClaimStatus.REPRODUCED.value,
    ClaimStatus.FORMALIZED.value,
    ClaimStatus.FORMALLY_VERIFIED.value,
}


def _timestamp() -> float:
    return time.time()


@dataclass
class ResearchSource:
    source_id: str
    title: str
    author_or_organization: str
    source_type: str
    url: str
    publication_date: str = ""
    version: str = ""
    source_commit: str = ""
    sections: list[str] = field(default_factory=list)
    equations: list[str] = field(default_factory=list)
    theorem_names: list[str] = field(default_factory=list)
    definitions: list[str] = field(default_factory=list)
    citations: list[str] = field(default_factory=list)
    relationships: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResearchSource":
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ResearchEvidence:
    evidence_id: str
    claim_id: str
    kind: str
    summary: str
    source_id: str
    source_location: str = ""
    status: str = ClaimStatus.UNASSESSED.value
    independence: str = VerificationIndependence.SAME_SOURCE.value
    provenance: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResearchEvidence":
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ResearchClaim:
    claim_id: str
    statement: str
    domain: str
    claim_type: str
    source: str
    source_location: str = ""
    source_commit: str = ""
    assumptions: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    supporting_evidence: list[str] = field(default_factory=list)
    contradicting_evidence: list[str] = field(default_factory=list)
    derivation_status: str = ClaimStatus.UNASSESSED.value
    formalization_status: str = ClaimStatus.UNASSESSED.value
    independent_verification_status: str = ClaimStatus.UNASSESSED.value
    adversarial_status: str = ClaimStatus.UNASSESSED.value
    acceptance_status: str = ClaimStatus.UNASSESSED.value
    confidence: float = 0.0
    provenance: list[str] = field(default_factory=list)
    timestamp: float = field(default_factory=_timestamp)
    parent_claims: list[str] = field(default_factory=list)
    child_claims: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResearchClaim":
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ResearchTrack:
    track_id: str
    role: str
    strategy: str
    hypothesis: str
    assumptions: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    focus_claims: list[str] = field(default_factory=list)
    intermediate_results: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    failed_approaches: list[str] = field(default_factory=list)
    unresolved_objections: list[str] = field(default_factory=list)
    confidence: float = 0.0
    provenance: list[str] = field(default_factory=list)
    state: str = ResearchState.TRACK_EXECUTION.value
    checkpoints: list[dict[str, Any]] = field(default_factory=list)
    execution_records: list[dict[str, Any]] = field(default_factory=list)
    validation: dict[str, Any] = field(default_factory=dict)
    artifacts: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResearchTrack":
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CrossPollinationRecord:
    transfer_id: str
    source_track_id: str
    discovery: str
    validation_status: str
    synthesis: str
    recipient_track_id: str
    new_hypothesis: str
    result: str
    transferred_claim_ids: list[str] = field(default_factory=list)
    failed_approaches: list[str] = field(default_factory=list)
    contradiction_with_recipient: bool = False
    independent_confirmation: bool = False
    provenance: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CrossPollinationRecord":
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FormalVerificationRecord:
    verification_id: str
    system: str
    theorem_names: list[str]
    source_files: list[str]
    repository: str
    source_commit: str = ""
    toolchain_version: str = ""
    formal_statement: str = ""
    source_location: str = ""
    command: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    compiled: bool = False
    independently_verified: bool = False
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""
    status: str = ClaimStatus.UNASSESSED.value
    provenance: list[str] = field(default_factory=list)
    timestamp: float = field(default_factory=_timestamp)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FormalVerificationRecord":
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ConvergenceObservation:
    observation_id: str
    track_id: str
    research_problem_id: str
    statement: str
    features: list[str] = field(default_factory=list)
    source: str = ""
    evidence_ids: list[str] = field(default_factory=list)
    provenance_id: str = ""
    independence_status: str = ConvergenceIndependence.UNKNOWN.value
    confidence: float = 0.0
    timestamp: float = field(default_factory=_timestamp)
    dependencies: list[str] = field(default_factory=list)
    parent_observations: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConvergenceObservation":
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ConvergencePattern:
    pattern_id: str
    observations: list[str]
    common_features: list[str] = field(default_factory=list)
    supporting_evidence: list[str] = field(default_factory=list)
    contradicting_evidence: list[str] = field(default_factory=list)
    independence_analysis: dict[str, Any] = field(default_factory=dict)
    ancestry_graph: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    status: str = ConvergenceStatus.INSUFFICIENT_DATA.value
    timestamp: float = field(default_factory=_timestamp)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConvergencePattern":
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ContradictionAnalysis:
    contradiction_id: str
    claim_a: str
    claim_b: str
    evidence_comparison: dict[str, Any] = field(default_factory=dict)
    assumption_comparison: dict[str, Any] = field(default_factory=dict)
    domain_comparison: dict[str, Any] = field(default_factory=dict)
    resolution_status: str = ClaimStatus.UNRESOLVED.value
    provenance: list[str] = field(default_factory=list)
    timestamp: float = field(default_factory=_timestamp)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ContradictionAnalysis":
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ScenarioHypothesis:
    hypothesis_id: str
    statement: str
    derived_from_patterns: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    supporting_evidence: list[str] = field(default_factory=list)
    contradicting_evidence: list[str] = field(default_factory=list)
    required_tests: list[str] = field(default_factory=list)
    falsification_conditions: list[str] = field(default_factory=list)
    confidence: float = 0.0
    status: str = ScenarioMaturity.UNRESOLVED.value
    provenance: list[str] = field(default_factory=list)
    timestamp: float = field(default_factory=_timestamp)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScenarioHypothesis":
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ScenarioRelationship:
    relationship_id: str
    source_node: str
    target_node: str
    relationship_type: str
    evidence: list[str] = field(default_factory=list)
    source: str = ""
    confidence: float = 0.0
    assumptions: list[str] = field(default_factory=list)
    provenance: list[str] = field(default_factory=list)
    status: str = ScenarioMaturity.UNRESOLVED.value

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScenarioRelationship":
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ScenarioEvidence:
    evidence_id: str
    statement: str
    source: str
    classification: list[str] = field(default_factory=list)
    verification_status: str = ScenarioMaturity.UNRESOLVED.value
    provenance: list[str] = field(default_factory=list)
    timestamp: float = field(default_factory=_timestamp)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScenarioEvidence":
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ConvergenceAnalysis:
    analysis_id: str
    research_problem_id: str
    observations: list[dict[str, Any]] = field(default_factory=list)
    patterns: list[dict[str, Any]] = field(default_factory=list)
    contradictions: list[dict[str, Any]] = field(default_factory=list)
    hypotheses: list[dict[str, Any]] = field(default_factory=list)
    scenario_graph: list[dict[str, Any]] = field(default_factory=list)
    temporal_analysis: list[dict[str, Any]] = field(default_factory=list)
    scenario_materials: list[dict[str, Any]] = field(default_factory=list)
    current_state: dict[str, Any] = field(default_factory=dict)
    emerging_signals: list[str] = field(default_factory=list)
    converging_features: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    possible_transitions: list[str] = field(default_factory=list)
    consequences: list[str] = field(default_factory=list)
    falsification_tests: list[str] = field(default_factory=list)
    evidence_status: str = ScenarioMaturity.UNRESOLVED.value
    blind_mode: bool = False
    controlled_release_ready: bool = False
    external_verification_required: bool = False
    completion_gate: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=_timestamp)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConvergenceAnalysis":
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AdversarialReview:
    review_id: str
    claim_id: str
    objections: list[str]
    evidence: list[str] = field(default_factory=list)
    responses: list[str] = field(default_factory=list)
    status: str = ClaimStatus.UNRESOLVED.value
    reviewer_role: str = "adversarial_mathematician"
    provenance: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AdversarialReview":
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ResearchProblem:
    problem_id: str
    title: str
    domain: str
    primary_question: str
    primary_claims: list[str]
    related_problems: list[str] = field(default_factory=list)
    acceptance_requirements: dict[str, Any] = field(default_factory=dict)
    research_questions: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResearchProblem":
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ResearchFailure:
    state: str
    code: str
    message: str
    failed_operation: str = ""
    raw_error: str = ""
    timestamp: float = field(default_factory=_timestamp)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ResearchCycleRecord:
    cycle_id: str
    problem_id: str
    status: str = "failed"
    current_state: str = ResearchState.IDLE.value
    state_history: list[str] = field(default_factory=lambda: [ResearchState.IDLE.value])
    source_ingestion_completed: bool = False
    tracks_planned: bool = False
    synthesis_completed: bool = False
    formalization_completed: bool = False
    formal_verification_completed: bool = False
    adversarial_review_completed: bool = False
    independent_verification_completed: bool = False
    acceptance_gate_passed: bool = False
    durable_record_written: bool = False
    problem_resolution_status: str = ClaimStatus.UNASSESSED.value
    resumed_from_cycle_id: str = ""
    questions: list[dict[str, Any]] = field(default_factory=list)
    problem: dict[str, Any] = field(default_factory=dict)
    sources: list[dict[str, Any]] = field(default_factory=list)
    claims: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    tracks: list[dict[str, Any]] = field(default_factory=list)
    cross_pollination: list[dict[str, Any]] = field(default_factory=list)
    convergence_analysis: dict[str, Any] = field(default_factory=dict)
    formal_verifications: list[dict[str, Any]] = field(default_factory=list)
    adversarial_reviews: list[dict[str, Any]] = field(default_factory=list)
    checkpoints: list[dict[str, Any]] = field(default_factory=list)
    execution_records: list[dict[str, Any]] = field(default_factory=list)
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    completion_gate: dict[str, Any] = field(default_factory=dict)
    retry_policy: dict[str, Any] = field(default_factory=dict)
    unresolved_questions: list[str] = field(default_factory=list)
    failure: ResearchFailure | None = None

    def transition(self, state: ResearchState) -> None:
        if self.current_state == state.value:
            return
        self.current_state = state.value
        self.state_history.append(state.value)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.failure is None:
            payload["failure"] = None
        return payload


class ResearchLedgerStore:
    def __init__(self, workspace: str | Path):
        self.workspace = Path(workspace).resolve()
        self.state_store = DurableStateStore(self.workspace, "barrot_research")
        self.ledger_file = self.state_store.root / "claim_ledger.json"

    def load_ledger(self) -> dict[str, dict[str, Any]]:
        if not self.ledger_file.exists():
            return {}
        try:
            payload = json.loads(self.ledger_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
        return {str(k): v for k, v in payload.items() if isinstance(v, dict)} if isinstance(payload, dict) else {}

    def write_ledger(self, claims: Iterable[ResearchClaim]) -> None:
        current = self.load_ledger()
        for claim in claims:
            current[claim.claim_id] = claim.to_dict()
        self.ledger_file.write_text(json.dumps(current, indent=2, sort_keys=True), encoding="utf-8")

    def write_cycle(self, fingerprint: str, cycle: ResearchCycleRecord) -> Path:
        return self.state_store.write_state(cycle.cycle_id, cycle.to_dict(), fingerprint=fingerprint)

    def load_cycle(self, cycle_id: str) -> ResearchCycleRecord | None:
        payload = self.state_store.load_state(cycle_id)
        if not payload:
            return None
        failure = payload.get("failure")
        if isinstance(failure, dict):
            payload["failure"] = ResearchFailure(**failure)
        return ResearchCycleRecord(**payload)

    def load_cycle_by_fingerprint(self, fingerprint: str) -> ResearchCycleRecord | None:
        payload = self.state_store.load_state_by_fingerprint(fingerprint)
        if not payload:
            return None
        failure = payload.get("failure")
        if isinstance(failure, dict):
            payload["failure"] = ResearchFailure(**failure)
        return ResearchCycleRecord(**payload)

    def write_checkpoint(self, checkpoint: Checkpoint) -> Path:
        return self.state_store.write_checkpoint(checkpoint)


class ResearchSourceIngestor:
    def __init__(self, bundle_path: str | Path):
        self.bundle_path = Path(bundle_path).resolve()

    def load_bundle(self) -> dict[str, Any]:
        payload = json.loads(self.bundle_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise RepairError("Research bundle must be a JSON object.")
        return payload

    def ingest(
        self,
    ) -> tuple[
        ResearchProblem,
        list[ResearchSource],
        list[ResearchClaim],
        list[ResearchEvidence],
        list[ResearchTrack],
        list[AdversarialReview],
        list[dict[str, Any]],
        list[dict[str, Any]],
    ]:
        bundle = self.load_bundle()
        problem = ResearchProblem.from_dict(bundle["problem"])
        sources = [ResearchSource.from_dict(item) for item in bundle.get("sources", [])]
        claims = [ResearchClaim.from_dict(item) for item in bundle.get("claims", [])]
        evidence = [ResearchEvidence.from_dict(item) for item in bundle.get("evidence", [])]
        tracks = [ResearchTrack.from_dict(item) for item in bundle.get("tracks", [])]
        reviews = [AdversarialReview.from_dict(item) for item in bundle.get("adversarial_reviews", [])]
        formal_specs = [dict(item) for item in bundle.get("formal_verification", []) if isinstance(item, dict)]
        question_map = [dict(item) for item in bundle.get("question_map", []) if isinstance(item, dict)]
        return problem, sources, claims, evidence, tracks, reviews, formal_specs, question_map


class LeanVerificationGateway:
    ALLOWED_PROGRAMS = {"lake", "lean", "elan"}

    def verify(
        self,
        spec: dict[str, Any],
        *,
        runner: Callable[[list[str], str | None], dict[str, Any]] | None = None,
    ) -> FormalVerificationRecord:
        command = [str(item) for item in spec.get("command", []) if str(item).strip()]
        if command and command[0] not in self.ALLOWED_PROGRAMS:
            raise RepairError(f"Unsupported formal verification command: {command[0]}")
        record = FormalVerificationRecord(
            verification_id=str(spec.get("verification_id") or Fingerprint.create(spec).value),
            system=str(spec.get("system") or "lean"),
            theorem_names=[str(item) for item in spec.get("theorem_names", [])],
            source_files=[str(item) for item in spec.get("source_files", [])],
            repository=str(spec.get("repository") or ""),
            source_commit=str(spec.get("source_commit") or ""),
            toolchain_version=str(spec.get("toolchain_version") or ""),
            formal_statement=str(spec.get("formal_statement") or ""),
            source_location=str(spec.get("source_location") or ""),
            command=command,
            dependencies=[str(item) for item in spec.get("dependencies", [])],
            status=ClaimStatus.FORMALIZED.value,
            provenance=[str(item) for item in spec.get("provenance", [])],
        )
        if runner is not None:
            result = runner(command, spec.get("repository_path"))
            record.returncode = int(result.get("returncode", 1))
            record.stdout = str(result.get("stdout", ""))[-4000:]
            record.stderr = str(result.get("stderr", ""))[-4000:]
            record.compiled = record.returncode == 0
            record.independently_verified = bool(result.get("independently_verified", False))
        elif spec.get("repository_path"):
            validation = bounded_subprocess(command, cwd=str(spec.get("repository_path")), timeout=int(spec.get("timeout", 120)))
            check = validation.checks[0] if validation.checks else {}
            record.returncode = check.get("returncode")
            record.stdout = check.get("stdout", "")
            record.stderr = check.get("stderr", "")
            record.compiled = validation.passed
        record.status = ClaimStatus.FORMALLY_VERIFIED.value if record.compiled else ClaimStatus.FORMALIZED.value
        return record


class CrossPollinationEngine:
    def __init__(self) -> None:
        self.claim_integrity = ClaimIntegrityEngine()

    def synthesize(self, tracks: list[ResearchTrack]) -> list[CrossPollinationRecord]:
        transfers: list[CrossPollinationRecord] = []
        for source in tracks:
            for recipient in tracks:
                if source.track_id == recipient.track_id:
                    continue
                validation = self._validate_transfer(source, recipient)
                transfers.append(validation)
        unique: dict[str, CrossPollinationRecord] = {}
        for transfer in transfers:
            unique[transfer.transfer_id] = transfer
        return list(unique.values())

    def _validate_transfer(self, source: ResearchTrack, recipient: ResearchTrack) -> CrossPollinationRecord:
        discovery = (
            str(source.intermediate_results[0].get("summary"))
            if source.intermediate_results and isinstance(source.intermediate_results[0], dict)
            else source.hypothesis
        )
        transferred_claim_ids = [
            str(item.get("claim_id"))
            for item in source.intermediate_results
            if isinstance(item, dict)
            and str(item.get("status") or "") in TRANSFERABLE_STATUSES
            and str(item.get("claim_id") or "")
        ]
        contradiction = self.claim_integrity.compare(source.hypothesis, recipient.hypothesis)["status"] == "contradiction"
        overlap = sorted(set(source.focus_claims) & set(recipient.focus_claims))
        missing_provenance = not source.provenance
        circular = source.track_id in recipient.dependencies or recipient.track_id in source.dependencies
        duplicate = bool(overlap)
        matched_dependencies = sorted(set(transferred_claim_ids) & set(recipient.dependencies + recipient.focus_claims))
        independent_confirmation = False
        result = "transferred"
        synthesis = discovery
        new_hypothesis = f"Test whether {discovery} strengthens {recipient.role}."
        if missing_provenance:
            result = "invalid_transfer"
            synthesis = "Source discovery lacks provenance and cannot be transferred."
            new_hypothesis = ""
        elif circular:
            result = "circular_blocked"
            synthesis = "Transfer would create circular ancestry between source and recipient tracks."
            new_hypothesis = ""
        elif duplicate:
            result = "duplicate_skipped"
            synthesis = f"Shared focus already present for claims: {', '.join(overlap)}"
            new_hypothesis = ""
        elif contradiction:
            result = "contradictory_transfer"
            synthesis = "Source discovery contradicts the recipient hypothesis and is recorded as a challenge."
            new_hypothesis = f"Explain or resolve contradiction between {source.track_id} and {recipient.track_id}."
        elif not matched_dependencies and not transferred_claim_ids:
            result = "invalid_transfer"
            synthesis = "No validated reusable claim or dependency match was found for transfer."
            new_hypothesis = ""
        else:
            lemma = matched_dependencies[0] if matched_dependencies else transferred_claim_ids[0]
            synthesis = f"Reusable lemma candidate: {lemma} from {source.track_id}."
            new_hypothesis = f"Use {lemma} to strengthen {recipient.role}."
        transfer_id = Fingerprint.create(source.track_id, recipient.track_id, result, synthesis, transferred_claim_ids).value
        return CrossPollinationRecord(
            transfer_id=transfer_id,
            source_track_id=source.track_id,
            discovery=discovery,
            validation_status=source.state,
            synthesis=synthesis,
            recipient_track_id=recipient.track_id,
            new_hypothesis=new_hypothesis,
            result=result,
            transferred_claim_ids=matched_dependencies or transferred_claim_ids,
            failed_approaches=list(source.failed_approaches),
            contradiction_with_recipient=contradiction,
            independent_confirmation=independent_confirmation,
            provenance=list(dict.fromkeys([*source.provenance, *recipient.provenance, source.track_id, recipient.track_id])),
        )


class IndependenceEvaluator:
    def assess(self, evidence: Iterable[ResearchEvidence], formal_records: Iterable[FormalVerificationRecord] | None = None) -> dict[str, Any]:
        independent: list[str] = []
        blocked: list[str] = []
        ancestry_seen: set[str] = set()
        for item in evidence:
            ancestry = str(item.details.get("ancestry") or item.source_id)
            if item.independence in {
                VerificationIndependence.SAME_SOURCE.value,
                VerificationIndependence.SAME_MODEL.value,
                VerificationIndependence.CROSS_MODEL.value,
                VerificationIndependence.SOURCE_TEAM_FORMAL.value,
            }:
                ancestry_seen.add(ancestry)
                blocked.append(item.evidence_id)
                continue
            if ancestry in ancestry_seen:
                blocked.append(item.evidence_id)
                continue
            ancestry_seen.add(ancestry)
            if item.independence in {
                VerificationIndependence.INDEPENDENT_IMPLEMENTATION.value,
                VerificationIndependence.INDEPENDENT_DERIVATION.value,
                VerificationIndependence.FORMAL.value,
                VerificationIndependence.LITERATURE.value,
            }:
                independent.append(item.evidence_id)
        if formal_records is not None:
            for record in formal_records:
                if record.independently_verified:
                    independent.append(record.verification_id)
                elif record.compiled:
                    blocked.append(record.verification_id)
        unique_independent = list(dict.fromkeys(independent))
        unique_blocked = [item for item in dict.fromkeys(blocked) if item not in unique_independent]
        return {
            "independent_evidence": unique_independent,
            "blocked_evidence": unique_blocked,
            "status": ClaimStatus.INDEPENDENTLY_VERIFIED.value if unique_independent else ClaimStatus.UNRESOLVED.value,
        }


class ConvergenceScenarioEngine:
    def __init__(self) -> None:
        self.claim_integrity = ClaimIntegrityEngine()

    def analyze(
        self,
        *,
        research_problem_id: str,
        domain: str,
        tracks: list[ResearchTrack],
        evidence: list[ResearchEvidence],
        cross_pollination: list[CrossPollinationRecord] | None = None,
        formal_records: list[FormalVerificationRecord] | None = None,
        blind_mode: bool = False,
    ) -> ConvergenceAnalysis:
        observations = self.build_observations(
            research_problem_id=research_problem_id,
            tracks=tracks,
            evidence=evidence,
            cross_pollination=cross_pollination or [],
            formal_records=formal_records or [],
            blind_mode=blind_mode,
        )
        scenario_materials = [
            self.classify_source_material(source=item.source, statement=item.statement)
            for item in observations
            if "remote_viewing" in item.source.lower() or "scenario_material" in item.source.lower()
        ]
        return self.analyze_observations(
            research_problem_id=research_problem_id,
            domain=domain,
            observations=observations,
            blind_mode=blind_mode,
            scenario_materials=scenario_materials,
        )

    def build_observations(
        self,
        *,
        research_problem_id: str,
        tracks: list[ResearchTrack],
        evidence: list[ResearchEvidence],
        cross_pollination: list[CrossPollinationRecord],
        formal_records: list[FormalVerificationRecord],
        blind_mode: bool,
    ) -> list[ConvergenceObservation]:
        evidence_index = {item.evidence_id: item for item in evidence}
        parents_by_track: dict[str, list[str]] = {}
        if not blind_mode:
            for transfer in cross_pollination:
                if transfer.result in {
                    "transferred",
                    "contradictory_transfer",
                    "duplicate_skipped",
                }:
                    parents_by_track.setdefault(transfer.recipient_track_id, []).append(transfer.source_track_id)
        observations: list[ConvergenceObservation] = []
        for track in tracks:
            if track.intermediate_results:
                results = track.intermediate_results
            else:
                results = [{"claim_id": "", "summary": track.hypothesis, "status": ClaimStatus.HYPOTHESIS.value}]
            for index, result in enumerate(results):
                if not isinstance(result, dict):
                    continue
                statement = str(result.get("summary") or track.hypothesis).strip()
                observation = ConvergenceObservation(
                    observation_id=Fingerprint.create(research_problem_id, track.track_id, index, statement).value,
                    track_id=track.track_id,
                    research_problem_id=research_problem_id,
                    statement=statement,
                    features=self._track_features(track, result, evidence_index),
                    source=track.provenance[0] if track.provenance else track.role,
                    evidence_ids=list(track.evidence),
                    provenance_id=Fingerprint.create(track.provenance, track.evidence, result.get("claim_id", "")).value if track.provenance or track.evidence else "",
                    confidence=track.confidence,
                    dependencies=list(track.dependencies),
                    parent_observations=[] if blind_mode else list(dict.fromkeys(parents_by_track.get(track.track_id, []))),
                )
                observations.append(observation)
        for record in formal_records:
            observations.append(
                ConvergenceObservation(
                    observation_id=Fingerprint.create(research_problem_id, record.verification_id, "formal").value,
                    track_id=record.verification_id,
                    research_problem_id=research_problem_id,
                    statement=(
                        f"Formal verification record for {', '.join(record.theorem_names) or 'unnamed theorem'}: "
                        f"{'compiled' if record.compiled else 'formalized only'}"
                    ),
                    features=sorted(
                        {
                            *(f"formal:{item}" for item in record.theorem_names),
                            *(f"dependency:{item}" for item in record.dependencies),
                            f"repository:{record.repository}",
                            f"source_commit:{record.source_commit}",
                        }
                    ),
                    source=record.repository or "formal_verification",
                    evidence_ids=[record.verification_id],
                    provenance_id=Fingerprint.create(record.repository, record.source_commit, record.theorem_names).value,
                    independence_status=(
                        ConvergenceIndependence.INDEPENDENT.value
                        if record.independently_verified
                        else ConvergenceIndependence.DEPENDENT.value
                    ),
                    confidence=1.0 if record.compiled else 0.5,
                    dependencies=list(record.dependencies),
                    parent_observations=[],
                )
            )
        return observations

    def analyze_observations(
        self,
        *,
        research_problem_id: str,
        domain: str,
        observations: list[ConvergenceObservation],
        blind_mode: bool = False,
        scenario_materials: list[ScenarioEvidence] | None = None,
    ) -> ConvergenceAnalysis:
        enriched = self._assign_observation_independence(observations)
        patterns: list[ConvergencePattern] = []
        contradictions: list[ContradictionAnalysis] = []
        graph: list[ScenarioRelationship] = []
        converging_features: set[str] = set()
        for index, left in enumerate(enriched):
            for right in enriched[index + 1 :]:
                pattern = self._analyze_pair(left, right)
                patterns.append(pattern)
                if pattern.status in {ConvergenceStatus.CONVERGENCE.value, ConvergenceStatus.PARTIAL_CONVERGENCE.value}:
                    converging_features.update(pattern.common_features)
                    provenance = sorted(
                        {
                            value
                            for node in pattern.ancestry_graph.values()
                            for value in node.get("provenance", [])
                            if value
                        }
                    )
                    graph.append(
                        self.build_relationship(
                            source_node=left.track_id,
                            target_node=right.track_id,
                            relationship_type=ScenarioRelationshipType.CORRELATES_WITH.value,
                            evidence=pattern.supporting_evidence,
                            source="convergence_analysis",
                            confidence=pattern.confidence,
                            assumptions=[],
                            provenance=provenance,
                        )
                    )
                if pattern.status == ConvergenceStatus.CONTRADICTION.value:
                    contradictions.append(self._build_contradiction(left, right, pattern))
                    graph.append(
                        self.build_relationship(
                            source_node=left.track_id,
                            target_node=right.track_id,
                            relationship_type=ScenarioRelationshipType.CONFLICTS_WITH.value,
                            evidence=pattern.supporting_evidence,
                            source="convergence_analysis",
                            confidence=pattern.confidence,
                            assumptions=[],
                            provenance=sorted(set(pattern.ancestry_graph.get(left.observation_id, {}).get("provenance", []) + pattern.ancestry_graph.get(right.observation_id, {}).get("provenance", []))),
                        )
                    )
        hypotheses = self._generate_hypotheses(domain, patterns, contradictions)
        temporal = self._temporal_analysis(enriched)
        gate = CompletionGate(
            gate_id=Fingerprint.create(research_problem_id, hypotheses, contradictions).value,
            requirements={
                "observations_recorded": bool(enriched),
                "independent_convergence_requires_external_verification": all(
                    hypothesis.required_tests for hypothesis in hypotheses
                )
                if hypotheses
                else True,
                "no_hypothesis_marked_verified_without_evidence": not any(
                    hypothesis.status in {ClaimStatus.SUPPORTED.value, ClaimStatus.INDEPENDENTLY_VERIFIED.value}
                    for hypothesis in hypotheses
                ),
            },
            satisfied=not hypotheses or all(hypothesis.status not in {ClaimStatus.SUPPORTED.value, ClaimStatus.INDEPENDENTLY_VERIFIED.value} for hypothesis in hypotheses),
            unresolved=[
                "External verification is required for convergence-derived hypotheses."
                for hypothesis in hypotheses
                if hypothesis.required_tests
            ],
        )
        analysis_fingerprint = Fingerprint.create(
            research_problem_id,
            [item.observation_id for item in enriched],
            [item.pattern_id for item in patterns],
            [item.hypothesis_id for item in hypotheses],
            blind_mode,
        ).value
        return ConvergenceAnalysis(
            analysis_id=analysis_fingerprint,
            research_problem_id=research_problem_id,
            observations=[item.to_dict() for item in enriched],
            patterns=[item.to_dict() for item in patterns],
            contradictions=[item.to_dict() for item in contradictions],
            hypotheses=[item.to_dict() for item in hypotheses],
            scenario_graph=[item.to_dict() for item in graph],
            temporal_analysis=temporal,
            scenario_materials=[item.to_dict() for item in scenario_materials or []],
            current_state={"observation_count": len(enriched), "pattern_count": len(patterns)},
            emerging_signals=sorted(converging_features),
            converging_features=sorted(converging_features),
            dependencies=sorted({dep for item in enriched for dep in item.dependencies}),
            assumptions=sorted({feature.removeprefix("assumption:") for item in enriched for feature in item.features if feature.startswith("assumption:")}),
            possible_transitions=[hypothesis.statement for hypothesis in hypotheses],
            consequences=[item.claim_b for item in contradictions],
            falsification_tests=sorted({test for hypothesis in hypotheses for test in hypothesis.falsification_conditions}),
            evidence_status=(
                ScenarioMaturity.CORROBORATED.value
                if any(pattern.status == ConvergenceStatus.CONVERGENCE.value for pattern in patterns)
                else ScenarioMaturity.UNRESOLVED.value
            ),
            blind_mode=blind_mode,
            controlled_release_ready=blind_mode and bool(enriched),
            external_verification_required=bool(hypotheses),
            completion_gate=gate.to_dict(),
        )

    def build_relationship(
        self,
        *,
        source_node: str,
        target_node: str,
        relationship_type: str,
        evidence: list[str],
        source: str,
        confidence: float,
        assumptions: list[str],
        provenance: list[str],
    ) -> ScenarioRelationship:
        requested = relationship_type
        effective = requested
        status = ScenarioMaturity.UNRESOLVED.value
        if requested == ScenarioRelationshipType.CAUSES.value and len(evidence) < 2:
            effective = ScenarioRelationshipType.MAY_CAUSE.value
            status = ScenarioMaturity.SPECULATIVE.value
        elif requested == ScenarioRelationshipType.CORRELATES_WITH.value:
            status = ScenarioMaturity.REPORTED.value
        elif requested == ScenarioRelationshipType.MAY_CAUSE.value:
            status = ScenarioMaturity.SPECULATIVE.value
        else:
            status = ScenarioMaturity.CORROBORATED.value if len(evidence) >= 2 else ScenarioMaturity.EMERGING.value
        return ScenarioRelationship(
            relationship_id=Fingerprint.create(source_node, target_node, effective, evidence, provenance).value,
            source_node=source_node,
            target_node=target_node,
            relationship_type=effective,
            evidence=list(evidence),
            source=source,
            confidence=round(confidence, 3),
            assumptions=list(assumptions),
            provenance=list(provenance),
            status=status,
        )

    def classify_source_material(self, *, source: str, statement: str) -> ScenarioEvidence:
        return ScenarioEvidence(
            evidence_id=Fingerprint.create(source, statement, "scenario_material").value,
            statement=statement,
            source=source,
            classification=["SOURCE_REPORTED", "UNVERIFIED", "HYPOTHESIS_MATERIAL"],
            verification_status=ScenarioMaturity.UNRESOLVED.value,
            provenance=[source],
        )

    def _track_features(
        self,
        track: ResearchTrack,
        result: dict[str, Any],
        evidence_index: dict[str, ResearchEvidence],
    ) -> list[str]:
        features = {
            f"role:{track.role}",
            *(f"claim:{item}" for item in track.focus_claims),
            *(f"dependency:{item}" for item in track.dependencies),
            *(f"assumption:{item}" for item in track.assumptions),
            *(f"evidence:{item}" for item in track.evidence),
            *(f"provenance:{item}" for item in track.provenance),
        }
        if result.get("claim_id"):
            features.add(f"claim:{result['claim_id']}")
        if result.get("status"):
            features.add(f"status:{result['status']}")
        for evidence_id in track.evidence:
            if evidence_id in evidence_index:
                evidence = evidence_index[evidence_id]
                features.add(f"source:{evidence.source_id}")
                ancestry = str(evidence.details.get("ancestry") or evidence.source_id)
                features.add(f"ancestry:{ancestry}")
        return sorted(item for item in features if item)

    def _assign_observation_independence(self, observations: list[ConvergenceObservation]) -> list[ConvergenceObservation]:
        enriched: list[ConvergenceObservation] = []
        for observation in observations:
            if observation.independence_status != ConvergenceIndependence.UNKNOWN.value:
                enriched.append(observation)
                continue
            if not observation.provenance_id or not observation.source:
                observation.independence_status = ConvergenceIndependence.INVALID.value
            elif observation.parent_observations:
                observation.independence_status = ConvergenceIndependence.DEPENDENT.value
            elif any(feature.startswith("source:") for feature in observation.features):
                observation.independence_status = ConvergenceIndependence.PARTIALLY_INDEPENDENT.value
            else:
                observation.independence_status = ConvergenceIndependence.UNKNOWN.value
            enriched.append(observation)
        return enriched

    def _analyze_pair(self, left: ConvergenceObservation, right: ConvergenceObservation) -> ConvergencePattern:
        left_features = set(left.features)
        right_features = set(right.features)
        common = sorted(left_features & right_features)
        shared_evidence = sorted(set(left.evidence_ids) & set(right.evidence_ids))
        shared_provenance = []
        if left.provenance_id and left.provenance_id == right.provenance_id:
            shared_provenance.append(left.provenance_id)
        independent_status = self._pair_independence(left, right, shared_evidence, common)
        contradiction = self.claim_integrity.compare(left.statement, right.statement)
        status = ConvergenceStatus.INSUFFICIENT_DATA.value
        if independent_status == ConvergenceIndependence.INVALID.value:
            status = ConvergenceStatus.INSUFFICIENT_DATA.value
        elif left.observation_id == right.observation_id or (
            shared_provenance and left.statement == right.statement and set(left.evidence_ids) == set(right.evidence_ids)
        ):
            status = ConvergenceStatus.DUPLICATION.value
        elif contradiction["status"] == "contradiction":
            status = ConvergenceStatus.CONTRADICTION.value
        elif common and independent_status == ConvergenceIndependence.INDEPENDENT.value:
            status = ConvergenceStatus.CONVERGENCE.value if len(common) >= 2 else ConvergenceStatus.AGREEMENT.value
        elif common and independent_status == ConvergenceIndependence.PARTIALLY_INDEPENDENT.value:
            status = ConvergenceStatus.PARTIAL_CONVERGENCE.value
        elif common:
            status = ConvergenceStatus.DUPLICATION.value if independent_status == ConvergenceIndependence.DEPENDENT.value else ConvergenceStatus.AGREEMENT.value
        else:
            status = ConvergenceStatus.DIVERGENCE.value if independent_status == ConvergenceIndependence.INDEPENDENT.value else ConvergenceStatus.INSUFFICIENT_DATA.value
        confidence = round(min(0.99, 0.2 + (0.15 * len(common)) + (0.1 if independent_status == ConvergenceIndependence.INDEPENDENT.value else 0.0)), 3)
        ancestry_graph = {
            left.observation_id: {"parents": left.parent_observations, "provenance": [left.source, left.provenance_id]},
            right.observation_id: {"parents": right.parent_observations, "provenance": [right.source, right.provenance_id]},
        }
        return ConvergencePattern(
            pattern_id=Fingerprint.create(left.observation_id, right.observation_id, status, common).value,
            observations=[left.observation_id, right.observation_id],
            common_features=common,
            supporting_evidence=sorted(set(left.evidence_ids + right.evidence_ids)),
            contradicting_evidence=sorted(set(shared_evidence if status == ConvergenceStatus.CONTRADICTION.value else [])),
            independence_analysis={
                "status": independent_status,
                "shared_evidence": shared_evidence,
                "shared_provenance": shared_provenance,
                "shared_sources": sorted({left.source, right.source} if left.source == right.source else set()),
            },
            ancestry_graph=ancestry_graph,
            confidence=confidence,
            status=status,
        )

    def _pair_independence(
        self,
        left: ConvergenceObservation,
        right: ConvergenceObservation,
        shared_evidence: list[str],
        common_features: list[str],
    ) -> str:
        if not left.provenance_id or not right.provenance_id:
            return ConvergenceIndependence.INVALID.value
        if left.track_id == right.track_id:
            return ConvergenceIndependence.DEPENDENT.value
        if set(left.parent_observations) & {right.track_id, right.observation_id}:
            return ConvergenceIndependence.DEPENDENT.value
        if set(right.parent_observations) & {left.track_id, left.observation_id}:
            return ConvergenceIndependence.DEPENDENT.value
        if left.provenance_id == right.provenance_id or shared_evidence:
            return ConvergenceIndependence.DEPENDENT.value
        left_sources = {item.removeprefix("source:") for item in left.features if item.startswith("source:")}
        right_sources = {item.removeprefix("source:") for item in right.features if item.startswith("source:")}
        left_ancestry = {item.removeprefix("ancestry:") for item in left.features if item.startswith("ancestry:")}
        right_ancestry = {item.removeprefix("ancestry:") for item in right.features if item.startswith("ancestry:")}
        if left_ancestry & right_ancestry:
            return ConvergenceIndependence.DEPENDENT.value
        if left_sources & right_sources:
            return ConvergenceIndependence.PARTIALLY_INDEPENDENT.value
        if any(feature.startswith("claim:") for feature in common_features):
            return ConvergenceIndependence.INDEPENDENT.value
        return ConvergenceIndependence.UNKNOWN.value

    def _build_contradiction(
        self,
        left: ConvergenceObservation,
        right: ConvergenceObservation,
        pattern: ConvergencePattern,
    ) -> ContradictionAnalysis:
        left_assumptions = sorted(item.removeprefix("assumption:") for item in left.features if item.startswith("assumption:"))
        right_assumptions = sorted(item.removeprefix("assumption:") for item in right.features if item.startswith("assumption:"))
        left_domains = sorted(item.removeprefix("role:") for item in left.features if item.startswith("role:"))
        right_domains = sorted(item.removeprefix("role:") for item in right.features if item.startswith("role:"))
        status = ClaimStatus.DISPUTED.value
        if left_assumptions != right_assumptions:
            status = "BOTH_SUPPORTED_UNDER_DIFFERENT_ASSUMPTIONS"
        elif pattern.independence_analysis.get("status") == ConvergenceIndependence.DEPENDENT.value:
            status = ClaimStatus.UNRESOLVED.value
        return ContradictionAnalysis(
            contradiction_id=Fingerprint.create(left.observation_id, right.observation_id, "contradiction").value,
            claim_a=left.statement,
            claim_b=right.statement,
            evidence_comparison={
                "left": left.evidence_ids,
                "right": right.evidence_ids,
                "shared": pattern.independence_analysis.get("shared_evidence", []),
            },
            assumption_comparison={"left": left_assumptions, "right": right_assumptions},
            domain_comparison={"left": left_domains, "right": right_domains},
            resolution_status=status,
            provenance=[left.source, right.source],
        )

    def _generate_hypotheses(
        self,
        domain: str,
        patterns: list[ConvergencePattern],
        contradictions: list[ContradictionAnalysis],
    ) -> list[ScenarioHypothesis]:
        hypotheses: list[ScenarioHypothesis] = []
        contradiction_map = {item.contradiction_id: item for item in contradictions}
        for pattern in patterns:
            if pattern.status not in {
                ConvergenceStatus.CONVERGENCE.value,
                ConvergenceStatus.PARTIAL_CONVERGENCE.value,
                ConvergenceStatus.AGREEMENT.value,
            }:
                continue
            common_claims = [item.removeprefix("claim:") for item in pattern.common_features if item.startswith("claim:")]
            if not common_claims and not pattern.common_features:
                continue
            status = self._hypothesis_status(pattern, contradiction_map)
            required = self._required_tests_for_domain(domain)
            hypotheses.append(
                ScenarioHypothesis(
                    hypothesis_id=Fingerprint.create(pattern.pattern_id, "hypothesis").value,
                    statement=(
                        f"Pattern suggests {' and '.join(common_claims) if common_claims else ', '.join(pattern.common_features[:3])} "
                        "may represent a reusable scenario rather than proof."
                    ),
                    derived_from_patterns=[pattern.pattern_id],
                    assumptions=sorted(item.removeprefix("assumption:") for item in pattern.common_features if item.startswith("assumption:")),
                    supporting_evidence=list(pattern.supporting_evidence),
                    contradicting_evidence=list(pattern.contradicting_evidence),
                    required_tests=required,
                    falsification_conditions=[
                        "Independent evidence disproves the shared feature set.",
                        "Adversarial review finds an unsupported assumption.",
                        "Formal or computational validation fails to reproduce the pattern.",
                    ],
                    confidence=round(min(0.85, pattern.confidence), 3),
                    status=status,
                    provenance=sorted({value for node in pattern.ancestry_graph.values() for value in node.get("provenance", []) if value}),
                )
            )
        return hypotheses

    def _hypothesis_status(
        self,
        pattern: ConvergencePattern,
        contradictions: dict[str, ContradictionAnalysis],
    ) -> str:
        if pattern.contradicting_evidence:
            return ScenarioMaturity.UNRESOLVED.value
        if pattern.independence_analysis.get("status") == ConvergenceIndependence.INDEPENDENT.value:
            return ScenarioMaturity.CORROBORATED.value if pattern.status == ConvergenceStatus.CONVERGENCE.value else ScenarioMaturity.EMERGING.value
        if pattern.independence_analysis.get("status") == ConvergenceIndependence.PARTIALLY_INDEPENDENT.value:
            return ScenarioMaturity.EMERGING.value
        return ScenarioMaturity.REPORTED.value if pattern.status == ConvergenceStatus.AGREEMENT.value else ScenarioMaturity.SPECULATIVE.value

    def _required_tests_for_domain(self, domain: str) -> list[str]:
        lowered = domain.lower()
        if lowered in {"math", "mathematics"}:
            return [
                "FORMAL_VERIFICATION",
                "INDEPENDENT_DERIVATION",
                "ADVERSARIAL_REVIEW",
                "LITERATURE_CHECK",
            ]
        if lowered in {"science", "physics", "chemistry", "biology"}:
            return [
                "COMPUTATIONAL_TEST",
                "EXPERIMENTAL_TEST",
                "SOURCE_CORROBORATION",
                "ADVERSARIAL_REVIEW",
            ]
        if lowered in {"technology", "engineering", "cybersecurity", "economics", "product_research", "future_scenarios", "creative_research"}:
            return [
                "LITERATURE_CHECK",
                "COMPUTATIONAL_TEST",
                "SOURCE_CORROBORATION",
                "ADVERSARIAL_REVIEW",
            ]
        return ["SOURCE_CORROBORATION", "ADVERSARIAL_REVIEW"]

    def _temporal_analysis(self, observations: list[ConvergenceObservation]) -> list[dict[str, Any]]:
        if len(observations) < 2:
            return []
        ordered = sorted(observations, key=lambda item: item.timestamp)
        recurring = sorted(set(ordered[0].features).intersection(*(set(item.features) for item in ordered[1:])))
        new_features = sorted(set(ordered[-1].features) - set(ordered[0].features))
        disappearing = sorted(set(ordered[0].features) - set(ordered[-1].features))
        return [
            {
                "observation_ids": [item.observation_id for item in ordered],
                "recurring_features": recurring,
                "new_features": new_features,
                "disappearing_features": disappearing,
                "trend_hypothesis": (
                    "Recurring structured features persist across observations."
                    if recurring
                    else "No recurring structured feature set was established."
                ),
                "provenance": [item.source for item in ordered],
            }
        ]


class ScientificDiscoveryController:
    def __init__(
        self,
        *,
        workspace: str | Path,
        ledger_store: ResearchLedgerStore | None = None,
        verifier: LeanVerificationGateway | None = None,
        cross_pollination: CrossPollinationEngine | None = None,
        independence: IndependenceEvaluator | None = None,
        convergence_engine: ConvergenceScenarioEngine | None = None,
        retry_policy: RetryPolicy | None = None,
    ):
        self.workspace = Path(workspace).resolve()
        self.ledger_store = ledger_store or ResearchLedgerStore(self.workspace)
        self.verifier = verifier or LeanVerificationGateway()
        self.cross_pollination = cross_pollination or CrossPollinationEngine()
        self.independence = independence or IndependenceEvaluator()
        self.convergence_engine = convergence_engine or ConvergenceScenarioEngine()
        self.retry_policy = retry_policy or RetryPolicy(max_attempts=3, base_delay_seconds=1.0, max_delay_seconds=8.0)

    def run(
        self,
        adapter: "NavierStokesProblemAdapter | StaticResearchProblemAdapter",
        *,
        formal_runner: Callable[[list[str], str | None], dict[str, Any]] | None = None,
        stop_after_state: ResearchState | None = None,
        blind_mode: bool = False,
    ) -> ResearchCycleRecord:
        fingerprint = adapter.problem_fingerprint()
        existing = self.ledger_store.load_cycle_by_fingerprint(fingerprint)
        cycle = self._resume_or_create(existing, adapter)
        if cycle.status in TERMINAL_RESEARCH_STATUSES:
            cycle.durable_record_written = True
            return cycle
        try:
            cycle.retry_policy = asdict(self.retry_policy)
            self._transition(cycle, ResearchState.AUDITING, "Starting research cycle audit.", fingerprint)
            if self._maybe_stop(cycle, fingerprint, stop_after_state):
                return cycle

            problem, sources, claims, evidence, tracks, reviews, formal_specs, questions = adapter.ingest()
            cycle.problem = problem.to_dict()
            cycle.questions = questions
            cycle.artifacts = [
                Artifact(
                    artifact_id=Fingerprint.create("research_bundle", getattr(adapter, "bundle_path", adapter.problem_id)).value,
                    kind="research_bundle",
                    path=str(getattr(adapter, "bundle_path", "")),
                    fingerprint=Fingerprint.create(problem.to_dict(), questions).value,
                    metadata={"problem_id": problem.problem_id},
                ).to_dict()
            ]
            cycle.sources = [item.to_dict() for item in sources]
            cycle.claims = [item.to_dict() for item in claims]
            cycle.evidence = [item.to_dict() for item in evidence]
            cycle.source_ingestion_completed = True
            self.ledger_store.write_ledger(claims)
            self._transition(cycle, ResearchState.SOURCE_INGESTION, "Loaded sources, claims, and evidence.", fingerprint)
            if self._maybe_stop(cycle, fingerprint, stop_after_state):
                return cycle

            prepared_tracks = self._prepare_tracks(tracks)
            cycle.tracks = [item.to_dict() for item in prepared_tracks]
            cycle.tracks_planned = True
            self._transition(cycle, ResearchState.TRACK_PLANNING, "Prepared differentiated research tracks.", fingerprint)
            if self._maybe_stop(cycle, fingerprint, stop_after_state):
                return cycle

            executed_tracks = self._execute_tracks(prepared_tracks)
            cycle.tracks = [item.to_dict() for item in executed_tracks]
            self._transition(cycle, ResearchState.TRACK_EXECUTION, "Recorded per-track execution state.", fingerprint)
            if self._maybe_stop(cycle, fingerprint, stop_after_state):
                return cycle

            transfers = self.cross_pollination.synthesize(executed_tracks)
            cycle.cross_pollination = [item.to_dict() for item in transfers]
            cycle.synthesis_completed = True
            self._transition(cycle, ResearchState.SYNTHESIS, "Completed validated cross-pollination.", fingerprint)
            if self._maybe_stop(cycle, fingerprint, stop_after_state):
                return cycle

            cycle.formalization_completed = bool(formal_specs)
            self._transition(cycle, ResearchState.FORMALIZATION, "Recorded formalization targets.", fingerprint)
            if self._maybe_stop(cycle, fingerprint, stop_after_state):
                return cycle

            formal_records = [self.verifier.verify(spec, runner=formal_runner) for spec in formal_specs]
            cycle.formal_verifications = [item.to_dict() for item in formal_records]
            cycle.formal_verification_completed = bool(formal_records)
            self._transition(cycle, ResearchState.FORMAL_VERIFICATION, "Captured formal verification outcomes.", fingerprint)
            if self._maybe_stop(cycle, fingerprint, stop_after_state):
                return cycle

            cycle.adversarial_reviews = [item.to_dict() for item in reviews]
            cycle.adversarial_review_completed = True
            self._transition(cycle, ResearchState.ADVERSARIAL_REVIEW, "Recorded adversarial reviews.", fingerprint)
            if self._maybe_stop(cycle, fingerprint, stop_after_state):
                return cycle

            independence = self.independence.assess(evidence, formal_records)
            cycle.independent_verification_completed = True
            self._transition(cycle, ResearchState.INDEPENDENT_VERIFICATION, "Computed independence status.", fingerprint)
            if self._maybe_stop(cycle, fingerprint, stop_after_state):
                return cycle

            claim_index = self._materialize_claims(claims, evidence, formal_specs, formal_records, reviews, independence)
            cycle.claims = [claim.to_dict() for claim in claim_index.values()]
            self.ledger_store.write_ledger(claim_index.values())
            convergence = self.convergence_engine.analyze(
                research_problem_id=problem.problem_id,
                domain=problem.domain,
                tracks=executed_tracks,
                evidence=evidence,
                cross_pollination=transfers,
                formal_records=formal_records,
                blind_mode=blind_mode,
            )
            cycle.convergence_analysis = convergence.to_dict()
            cycle.artifacts.append(
                Artifact(
                    artifact_id=Fingerprint.create(cycle.cycle_id, "convergence_analysis").value,
                    kind="convergence_analysis",
                    path="",
                    fingerprint=Fingerprint.create(cycle.convergence_analysis).value,
                    metadata={"analysis_id": convergence.analysis_id, "blind_mode": blind_mode},
                ).to_dict()
            )

            gate = self._acceptance_decision(problem, claim_index, cycle.formal_verifications, cycle.adversarial_reviews)
            cycle.completion_gate = gate.to_dict()
            cycle.problem_resolution_status = (
                ClaimStatus.INDEPENDENTLY_VERIFIED.value if gate.satisfied else ClaimStatus.UNRESOLVED.value
            )
            cycle.unresolved_questions = list(gate.unresolved)
            cycle.acceptance_gate_passed = gate.satisfied
            self._transition(cycle, ResearchState.ACCEPTANCE_GATE, "Evaluated research completion gate.", fingerprint)
            if gate.satisfied:
                for claim in claim_index.values():
                    if claim.claim_id in problem.primary_claims:
                        claim.acceptance_status = ClaimStatus.INDEPENDENTLY_VERIFIED.value
                cycle.claims = [claim.to_dict() for claim in claim_index.values()]
                cycle.status = "complete"
                self._transition(cycle, ResearchState.COMPLETE, "Research acceptance gate satisfied.", fingerprint)
            else:
                for claim in claim_index.values():
                    if claim.claim_id in problem.primary_claims:
                        claim.acceptance_status = ClaimStatus.UNRESOLVED.value
                cycle.claims = [claim.to_dict() for claim in claim_index.values()]
                cycle.status = "no_solution_claim"
                self._transition(cycle, ResearchState.NO_SOLUTION_CLAIM, "Research remains unresolved.", fingerprint)
            cycle.durable_record_written = True
            self.ledger_store.write_cycle(fingerprint, cycle)
            return cycle
        except Exception as exc:  # noqa: BLE001
            cycle.status = "failed"
            cycle.transition(ResearchState.FAILED)
            cycle.failure = ResearchFailure(
                state=cycle.current_state,
                code=type(exc).__name__,
                message=str(exc),
                failed_operation="scientific_discovery.run",
                raw_error=str(exc),
            )
            self._persist_cycle(cycle, fingerprint)
            cycle.durable_record_written = True
            return cycle

    def _resume_or_create(
        self,
        existing: ResearchCycleRecord | None,
        adapter: "NavierStokesProblemAdapter | StaticResearchProblemAdapter",
    ) -> ResearchCycleRecord:
        if existing is not None:
            if existing.status not in TERMINAL_RESEARCH_STATUSES:
                existing.resumed_from_cycle_id = existing.cycle_id
            return existing
        return ResearchCycleRecord(
            cycle_id=Fingerprint.create(adapter.problem_id, _timestamp()).value[:24],
            problem_id=adapter.problem_id,
            status="running",
        )

    def _prepare_tracks(self, tracks: list[ResearchTrack]) -> list[ResearchTrack]:
        prepared: list[ResearchTrack] = []
        for track in tracks:
            track.checkpoints.append(
                Checkpoint(
                    checkpoint_id=Fingerprint.create(track.track_id, "planned").value,
                    task_id=track.track_id,
                    state=TaskState.PLANNING.value,
                    summary=f"Prepared track {track.role}.",
                    fingerprint=Fingerprint.create(track.to_dict()).value,
                ).to_dict()
            )
            prepared.append(track)
        return prepared

    def _execute_tracks(self, tracks: list[ResearchTrack]) -> list[ResearchTrack]:
        executed: list[ResearchTrack] = []
        for track in tracks:
            validation = ValidationResult(
                passed=bool(track.hypothesis and track.strategy),
                summary="track metadata complete" if track.hypothesis and track.strategy else "track metadata incomplete",
                checks=[
                    {
                        "track_id": track.track_id,
                        "has_hypothesis": bool(track.hypothesis),
                        "has_strategy": bool(track.strategy),
                        "evidence_count": len(track.evidence),
                    }
                ],
                failure=(
                    None
                    if track.hypothesis and track.strategy
                    else Failure(
                        code=FailureCode.VALIDATION_FAILED.value,
                        message="Track must define hypothesis and strategy.",
                        failed_operation=track.track_id,
                    )
                ),
            )
            record = ExecutionRecord(
                record_id=Fingerprint.create(track.track_id, track.hypothesis, track.strategy, track.intermediate_results).value,
                operation="research_track_execution",
                state=TaskState.COMPLETE.value if validation.passed else TaskState.FAILED.value,
                input_fingerprint=Fingerprint.create(track.track_id, track.focus_claims, track.dependencies).value,
                output_fingerprint=Fingerprint.create(track.intermediate_results, track.failed_approaches).value,
                response={
                    "role": track.role,
                    "intermediate_results": track.intermediate_results,
                    "failed_approaches": track.failed_approaches,
                    "unresolved_objections": track.unresolved_objections,
                },
            )
            track.execution_records.append(record.to_dict())
            track.validation = validation.to_dict()
            track.checkpoints.append(
                Checkpoint(
                    checkpoint_id=Fingerprint.create(track.track_id, "executed").value,
                    task_id=track.track_id,
                    state=TaskState.EXECUTING.value,
                    summary=f"Executed track {track.role}.",
                    fingerprint=record.output_fingerprint,
                ).to_dict()
            )
            executed.append(track)
        return executed

    def _materialize_claims(
        self,
        claims: list[ResearchClaim],
        evidence: list[ResearchEvidence],
        formal_specs: list[dict[str, Any]],
        formal_records: list[FormalVerificationRecord],
        reviews: list[AdversarialReview],
        independence: dict[str, Any],
    ) -> dict[str, ResearchClaim]:
        claim_index = {item.claim_id: item for item in claims}
        evidence_by_claim: dict[str, list[ResearchEvidence]] = {}
        for item in evidence:
            evidence_by_claim.setdefault(item.claim_id, []).append(item)
        formal_by_claim: dict[str, list[FormalVerificationRecord]] = {}
        for spec, record in zip(formal_specs, formal_records):
            for claim_id in spec.get("claim_ids", []):
                formal_by_claim.setdefault(str(claim_id), []).append(record)
        reviews_by_claim: dict[str, list[AdversarialReview]] = {}
        for review in reviews:
            reviews_by_claim.setdefault(review.claim_id, []).append(review)

        for claim in claims:
            related_evidence = evidence_by_claim.get(claim.claim_id, [])
            supporting = [item for item in related_evidence if item.status in TRANSFERABLE_STATUSES | {ClaimStatus.INDEPENDENTLY_VERIFIED.value}]
            conflicting = [item for item in related_evidence if item.status in {ClaimStatus.CHALLENGED.value, ClaimStatus.REFUTED.value, ClaimStatus.DISPUTED.value}]
            claim.supporting_evidence = [item.evidence_id for item in supporting]
            claim.contradicting_evidence = [item.evidence_id for item in conflicting]
            claim.derivation_status = ClaimStatus.SUPPORTED.value if supporting else ClaimStatus.UNRESOLVED.value
            formal_for_claim = formal_by_claim.get(claim.claim_id, [])
            if any(item.compiled for item in formal_for_claim):
                claim.formalization_status = ClaimStatus.FORMALLY_VERIFIED.value
            elif formal_for_claim:
                claim.formalization_status = ClaimStatus.FORMALIZED.value
            reviews_for_claim = reviews_by_claim.get(claim.claim_id, [])
            if any(item.status in {ClaimStatus.REFUTED.value, ClaimStatus.DISPUTED.value} for item in reviews_for_claim):
                claim.adversarial_status = ClaimStatus.DISPUTED.value
            elif any(item.status == ClaimStatus.CHALLENGED.value for item in reviews_for_claim):
                claim.adversarial_status = ClaimStatus.CHALLENGED.value
            elif reviews_for_claim:
                claim.adversarial_status = ClaimStatus.SUPPORTED.value
            if any(item.evidence_id in independence["independent_evidence"] for item in related_evidence):
                claim.independent_verification_status = ClaimStatus.INDEPENDENTLY_VERIFIED.value
            elif any(item.verification_id in independence["independent_evidence"] for item in formal_for_claim):
                claim.independent_verification_status = ClaimStatus.INDEPENDENTLY_VERIFIED.value
            elif claim.supporting_evidence or formal_for_claim:
                claim.independent_verification_status = ClaimStatus.UNRESOLVED.value
            claim.acceptance_status = ClaimStatus.UNRESOLVED.value
            claim.confidence = round(min(0.95, 0.2 + 0.15 * len(claim.supporting_evidence) + 0.1 * len(formal_for_claim)), 3)
        return claim_index

    def _transition(self, cycle: ResearchCycleRecord, state: ResearchState, summary: str, fingerprint: str) -> None:
        cycle.transition(state)
        record = ExecutionRecord(
            record_id=Fingerprint.create(cycle.cycle_id, state.value, summary, len(cycle.checkpoints)).value,
            operation="research_cycle_transition",
            state=state.value,
            input_fingerprint=fingerprint,
            output_fingerprint=Fingerprint.create(cycle.problem_id, state.value, summary).value,
            response={"summary": summary},
        )
        cycle.execution_records.append(record.to_dict())
        checkpoint = Checkpoint(
            checkpoint_id=Fingerprint.create(cycle.cycle_id, state.value, len(cycle.checkpoints)).value,
            task_id=cycle.cycle_id,
            state=state.value,
            summary=summary,
            fingerprint=record.output_fingerprint,
            payload={
                "status": cycle.status,
                "current_state": cycle.current_state,
                "problem_id": cycle.problem_id,
            },
        )
        cycle.checkpoints.append(checkpoint.to_dict())
        self.ledger_store.write_checkpoint(checkpoint)
        self._persist_cycle(cycle, fingerprint)

    def _persist_cycle(self, cycle: ResearchCycleRecord, fingerprint: str) -> None:
        self.ledger_store.write_cycle(fingerprint, cycle)

    def _maybe_stop(self, cycle: ResearchCycleRecord, fingerprint: str, stop_after_state: ResearchState | None) -> bool:
        if stop_after_state is None or cycle.current_state != stop_after_state.value:
            return False
        cycle.status = "checkpointed"
        self._persist_cycle(cycle, fingerprint)
        return True

    @staticmethod
    def _acceptance_decision(
        problem: ResearchProblem,
        claim_index: dict[str, ResearchClaim],
        formal_verifications: list[dict[str, Any]],
        adversarial_reviews: list[dict[str, Any]],
    ) -> CompletionGate:
        requirements = {
            "primary_claims_present": False,
            "compiled_formal_verification": any(item.get("compiled") for item in formal_verifications),
            "adversarial_reviews_resolved": not any(
                item.get("status") in {ClaimStatus.CHALLENGED.value, ClaimStatus.DISPUTED.value, ClaimStatus.REFUTED.value}
                for item in adversarial_reviews
            ),
            "independent_verification": False,
            "derivation_supported": False,
        }
        unresolved: list[str] = []
        primary_claims = [claim_index[item] for item in problem.primary_claims if item in claim_index]
        requirements["primary_claims_present"] = bool(primary_claims)
        if not primary_claims:
            unresolved.append("No primary claims were loaded.")
        requirements["independent_verification"] = bool(
            primary_claims
            and all(
                claim.independent_verification_status == ClaimStatus.INDEPENDENTLY_VERIFIED.value
                for claim in primary_claims
            )
        )
        requirements["derivation_supported"] = bool(
            primary_claims
            and all(claim.derivation_status in {ClaimStatus.SUPPORTED.value, ClaimStatus.REPRODUCED.value} for claim in primary_claims)
        )
        if not requirements["compiled_formal_verification"]:
            unresolved.append("No compiled formal proof was recorded.")
        if not requirements["adversarial_reviews_resolved"]:
            unresolved.append("At least one adversarial mathematical objection remains unresolved.")
        if not requirements["derivation_supported"]:
            unresolved.append("Primary claim derivation evidence remains incomplete.")
        if not requirements["independent_verification"]:
            for claim in primary_claims:
                if claim.independent_verification_status != ClaimStatus.INDEPENDENTLY_VERIFIED.value:
                    unresolved.append(
                        f"Independent verification remains incomplete or non-independent for primary claim {claim.claim_id}."
                    )
        return CompletionGate(
            gate_id=Fingerprint.create(problem.problem_id, requirements, unresolved).value,
            requirements=requirements,
            satisfied=all(requirements.values()),
            unresolved=unresolved,
        )


class StaticResearchProblemAdapter:
    def __init__(self, bundle_path: str | Path):
        self.ingestor = ResearchSourceIngestor(bundle_path)
        self.bundle_path = Path(bundle_path).resolve()
        self._bundle = self.ingestor.load_bundle()
        self.problem_id = str(self._bundle["problem"]["problem_id"])

    def ingest(self):
        return self.ingestor.ingest()

    def problem_fingerprint(self) -> str:
        return Fingerprint.create(self.problem_id, self._bundle).value


class NavierStokesProblemAdapter(StaticResearchProblemAdapter):
    def __init__(self, bundle_path: str | Path | None = None):
        base = (
            Path(bundle_path).resolve()
            if bundle_path is not None
            else Path(__file__).resolve().parents[2] / "data" / "research" / "navier_stokes_research_bundle.json"
        )
        super().__init__(base)

    def answer_question(self, question_id: str) -> dict[str, Any]:
        question_map = self._bundle.get("question_map", [])
        questions = {str(item.get("question_id")): item for item in question_map if isinstance(item, dict)}
        if question_id not in questions:
            raise KeyError(f"Unknown question_id: {question_id}")
        question = questions[question_id]
        claims = {item["claim_id"]: item for item in self._bundle.get("claims", []) if isinstance(item, dict)}
        sources = {item["source_id"]: item for item in self._bundle.get("sources", []) if isinstance(item, dict)}
        selected_claims = [claims[item] for item in question.get("claim_ids", []) if item in claims]
        selected_sources = [sources[item] for item in question.get("source_ids", []) if item in sources]
        return {
            "question_id": question_id,
            "prompt": question.get("prompt", ""),
            "answer": dict(question.get("answer", {})),
            "claims": selected_claims,
            "sources": selected_sources,
        }

    def source_summary(self) -> dict[str, Any]:
        problem, sources, claims, evidence, tracks, reviews, formal_specs, questions = self.ingest()
        return {
            "problem": problem.to_dict(),
            "source_count": len(sources),
            "claim_count": len(claims),
            "evidence_count": len(evidence),
            "track_count": len(tracks),
            "formal_verification_count": len(formal_specs),
            "question_count": len(questions),
            "primary_claims": problem.primary_claims,
        }


class CreativeEngineStatus(str, Enum):
    PENDING = "PENDING"
    READY = "READY"
    COMPLETE = "COMPLETE"


def is_scientific_discovery_task(title: str, body: str) -> bool:
    text = f"{title}\n{body}".lower()
    triggers = (
        "navier",
        "stokes",
        "scientific discovery",
        "formal verification",
        "lean",
        "millennium prize",
        "research question",
    )
    return any(token in text for token in triggers)
