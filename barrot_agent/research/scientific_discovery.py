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


class ScientificDiscoveryController:
    def __init__(
        self,
        *,
        workspace: str | Path,
        ledger_store: ResearchLedgerStore | None = None,
        verifier: LeanVerificationGateway | None = None,
        cross_pollination: CrossPollinationEngine | None = None,
        independence: IndependenceEvaluator | None = None,
        retry_policy: RetryPolicy | None = None,
    ):
        self.workspace = Path(workspace).resolve()
        self.ledger_store = ledger_store or ResearchLedgerStore(self.workspace)
        self.verifier = verifier or LeanVerificationGateway()
        self.cross_pollination = cross_pollination or CrossPollinationEngine()
        self.independence = independence or IndependenceEvaluator()
        self.retry_policy = retry_policy or RetryPolicy(max_attempts=3, base_delay_seconds=1.0, max_delay_seconds=8.0)

    def run(
        self,
        adapter: "NavierStokesProblemAdapter | StaticResearchProblemAdapter",
        *,
        formal_runner: Callable[[list[str], str | None], dict[str, Any]] | None = None,
        stop_after_state: ResearchState | None = None,
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
