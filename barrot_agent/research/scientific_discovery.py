from __future__ import annotations

import json
import subprocess
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Iterable

from barrot_agent.orchestration.repository_repair import RepairError


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
    LITERATURE = "independent_literature_corroboration"


def _timestamp() -> float:
    return time.time()


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)


def _fingerprint(*parts: Any) -> str:
    import hashlib

    body = "::".join(_canonical_json(part) for part in parts)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


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
    result: str
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
    command: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    compiled: bool = False
    independently_verified: bool = False
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""
    status: str = ClaimStatus.UNASSESSED.value

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
    timestamp: float = field(default_factory=_timestamp)


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
    questions: list[dict[str, Any]] = field(default_factory=list)
    problem: dict[str, Any] = field(default_factory=dict)
    sources: list[dict[str, Any]] = field(default_factory=list)
    claims: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    tracks: list[dict[str, Any]] = field(default_factory=list)
    cross_pollination: list[dict[str, Any]] = field(default_factory=list)
    formal_verifications: list[dict[str, Any]] = field(default_factory=list)
    adversarial_reviews: list[dict[str, Any]] = field(default_factory=list)
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
        self.root = Path(workspace).resolve() / ".git" / "barrot_research"
        self.root.mkdir(parents=True, exist_ok=True)
        self.cycles_dir = self.root / "cycles"
        self.cycles_dir.mkdir(parents=True, exist_ok=True)
        self.ledger_file = self.root / "claim_ledger.json"
        self.index_file = self.root / "cycle_index.json"

    def load_ledger(self) -> dict[str, dict[str, Any]]:
        if not self.ledger_file.exists():
            return {}
        try:
            payload = json.loads(self.ledger_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
        if isinstance(payload, dict):
            return {str(k): v for k, v in payload.items() if isinstance(v, dict)}
        return {}

    def write_ledger(self, claims: Iterable[ResearchClaim]) -> None:
        existing = self.load_ledger()
        for claim in claims:
            existing[claim.claim_id] = claim.to_dict()
        self.ledger_file.write_text(json.dumps(existing, indent=2, sort_keys=True), encoding="utf-8")

    def load_index(self) -> dict[str, str]:
        if not self.index_file.exists():
            return {}
        try:
            payload = json.loads(self.index_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
        if isinstance(payload, dict):
            return {str(k): str(v) for k, v in payload.items()}
        return {}

    def write_cycle(self, fingerprint: str, cycle: ResearchCycleRecord) -> Path:
        path = self.cycles_dir / f"{cycle.cycle_id}.json"
        path.write_text(json.dumps(cycle.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        index = self.load_index()
        index[fingerprint] = cycle.cycle_id
        self.index_file.write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")
        return path

    def load_cycle(self, cycle_id: str) -> ResearchCycleRecord | None:
        path = self.cycles_dir / f"{cycle_id}.json"
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        failure = payload.get("failure")
        if isinstance(failure, dict):
            payload["failure"] = ResearchFailure(**failure)
        return ResearchCycleRecord(**payload)

    def load_cycle_by_fingerprint(self, fingerprint: str) -> ResearchCycleRecord | None:
        cycle_id = self.load_index().get(fingerprint)
        if not cycle_id:
            return None
        return self.load_cycle(cycle_id)


class ResearchSourceIngestor:
    def __init__(self, bundle_path: str | Path):
        self.bundle_path = Path(bundle_path).resolve()

    def load_bundle(self) -> dict[str, Any]:
        payload = json.loads(self.bundle_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise RepairError("Research bundle must be a JSON object.")
        return payload

    def ingest(self) -> tuple[ResearchProblem, list[ResearchSource], list[ResearchClaim], list[ResearchEvidence], list[ResearchTrack], list[AdversarialReview], list[dict[str, Any]], list[dict[str, Any]]]:
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
            verification_id=str(spec.get("verification_id") or _fingerprint(spec)),
            system=str(spec.get("system") or "lean"),
            theorem_names=[str(item) for item in spec.get("theorem_names", [])],
            source_files=[str(item) for item in spec.get("source_files", [])],
            repository=str(spec.get("repository") or ""),
            source_commit=str(spec.get("source_commit") or ""),
            toolchain_version=str(spec.get("toolchain_version") or ""),
            command=command,
            dependencies=[str(item) for item in spec.get("dependencies", [])],
            status=ClaimStatus.FORMALIZED.value,
        )
        if runner is None:
            return record
        result = runner(command, spec.get("repository_path"))
        record.returncode = int(result.get("returncode", 1))
        record.stdout = str(result.get("stdout", ""))[-4000:]
        record.stderr = str(result.get("stderr", ""))[-4000:]
        record.compiled = record.returncode == 0
        record.independently_verified = bool(result.get("independently_verified", False))
        record.status = (
            ClaimStatus.FORMALLY_VERIFIED.value if record.compiled else ClaimStatus.UNRESOLVED.value
        )
        return record


class CrossPollinationEngine:
    def synthesize(self, tracks: list[ResearchTrack]) -> list[CrossPollinationRecord]:
        transfers: list[CrossPollinationRecord] = []
        for source in tracks:
            for recipient in tracks:
                if source.track_id == recipient.track_id:
                    continue
                overlap = sorted(set(source.focus_claims) & set(recipient.focus_claims))
                if overlap:
                    result = "duplicate_skipped"
                    synthesis = f"Shared focus already present for claims: {', '.join(overlap)}"
                else:
                    transferable = self._transferable_results(source, recipient)
                    if not transferable:
                        continue
                    result = "transferred"
                    synthesis = transferable[0]
                transfers.append(
                    CrossPollinationRecord(
                        transfer_id=_fingerprint(source.track_id, recipient.track_id, overlap, synthesis),
                        source_track_id=source.track_id,
                        discovery=(source.intermediate_results[0]["summary"] if source.intermediate_results else source.hypothesis),
                        validation_status=source.state,
                        synthesis=synthesis,
                        recipient_track_id=recipient.track_id,
                        result=result,
                        provenance=[source.track_id, recipient.track_id],
                    )
                )
        unique: dict[str, CrossPollinationRecord] = {}
        for transfer in transfers:
            unique[transfer.transfer_id] = transfer
        return list(unique.values())

    @staticmethod
    def _transferable_results(source: ResearchTrack, recipient: ResearchTrack) -> list[str]:
        discoveries: list[str] = []
        recipient_deps = set(recipient.dependencies)
        for result in source.intermediate_results:
            if not isinstance(result, dict):
                continue
            status = str(result.get("status") or "")
            claim_id = str(result.get("claim_id") or "")
            if status not in {ClaimStatus.SUPPORTED.value, ClaimStatus.REPRODUCED.value, ClaimStatus.FORMALIZED.value, ClaimStatus.FORMALLY_VERIFIED.value}:
                continue
            if claim_id and (claim_id in recipient_deps or claim_id in recipient.focus_claims):
                discoveries.append(str(result.get("summary") or claim_id))
        return discoveries


class IndependenceEvaluator:
    def assess(self, evidence: Iterable[ResearchEvidence]) -> dict[str, Any]:
        independent: list[str] = []
        ancestry_seen: set[str] = set()
        blocked: list[str] = []
        for item in evidence:
            ancestry = item.details.get("ancestry") or item.source_id
            if item.independence == VerificationIndependence.SAME_SOURCE.value:
                ancestry_seen.add(str(ancestry))
                blocked.append(item.evidence_id)
                continue
            if ancestry in ancestry_seen:
                blocked.append(item.evidence_id)
                continue
            ancestry_seen.add(str(ancestry))
            if item.independence in {
                VerificationIndependence.INDEPENDENT_IMPLEMENTATION.value,
                VerificationIndependence.INDEPENDENT_DERIVATION.value,
                VerificationIndependence.FORMAL.value,
                VerificationIndependence.LITERATURE.value,
            }:
                independent.append(item.evidence_id)
        return {
            "independent_evidence": independent,
            "blocked_evidence": blocked,
            "status": ClaimStatus.INDEPENDENTLY_VERIFIED.value if independent else ClaimStatus.UNRESOLVED.value,
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
    ):
        self.workspace = Path(workspace).resolve()
        self.ledger_store = ledger_store or ResearchLedgerStore(self.workspace)
        self.verifier = verifier or LeanVerificationGateway()
        self.cross_pollination = cross_pollination or CrossPollinationEngine()
        self.independence = independence or IndependenceEvaluator()

    def run(
        self,
        adapter: "NavierStokesProblemAdapter | StaticResearchProblemAdapter",
        *,
        formal_runner: Callable[[list[str], str | None], dict[str, Any]] | None = None,
    ) -> ResearchCycleRecord:
        fingerprint = adapter.problem_fingerprint()
        existing = self.ledger_store.load_cycle_by_fingerprint(fingerprint)
        if existing is not None:
            existing.durable_record_written = True
            return existing

        cycle = ResearchCycleRecord(
            cycle_id=_fingerprint(fingerprint, str(_timestamp()))[:24],
            problem_id=adapter.problem_id,
        )
        try:
            cycle.transition(ResearchState.AUDITING)
            problem, sources, claims, evidence, tracks, reviews, formal_specs, questions = adapter.ingest()
            cycle.problem = problem.to_dict()
            cycle.questions = questions
            cycle.transition(ResearchState.SOURCE_INGESTION)
            cycle.sources = [item.to_dict() for item in sources]
            cycle.claims = [item.to_dict() for item in claims]
            cycle.evidence = [item.to_dict() for item in evidence]
            cycle.source_ingestion_completed = True
            self.ledger_store.write_ledger(claims)

            cycle.transition(ResearchState.TRACK_PLANNING)
            cycle.tracks = [item.to_dict() for item in tracks]
            cycle.tracks_planned = True

            cycle.transition(ResearchState.TRACK_EXECUTION)
            cycle.transition(ResearchState.SYNTHESIS)
            transfers = self.cross_pollination.synthesize(tracks)
            cycle.cross_pollination = [item.to_dict() for item in transfers]
            cycle.synthesis_completed = True

            cycle.transition(ResearchState.FORMALIZATION)
            cycle.formalization_completed = bool(formal_specs)

            cycle.transition(ResearchState.FORMAL_VERIFICATION)
            formal_records = [self.verifier.verify(spec, runner=formal_runner) for spec in formal_specs]
            cycle.formal_verifications = [item.to_dict() for item in formal_records]
            cycle.formal_verification_completed = bool(formal_records)

            cycle.transition(ResearchState.ADVERSARIAL_REVIEW)
            cycle.adversarial_reviews = [item.to_dict() for item in reviews]
            cycle.adversarial_review_completed = True

            cycle.transition(ResearchState.INDEPENDENT_VERIFICATION)
            independence = self.independence.assess(ResearchEvidence.from_dict(item) for item in cycle.evidence)
            cycle.independent_verification_completed = True

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
                conflicting = [item for item in related_evidence if item.status in {ClaimStatus.CHALLENGED.value, ClaimStatus.REFUTED.value, ClaimStatus.DISPUTED.value}]
                supporting = [item for item in related_evidence if item.status in {ClaimStatus.SUPPORTED.value, ClaimStatus.REPRODUCED.value, ClaimStatus.FORMALIZED.value, ClaimStatus.FORMALLY_VERIFIED.value, ClaimStatus.INDEPENDENTLY_VERIFIED.value}]
                claim.supporting_evidence = [item.evidence_id for item in supporting]
                claim.contradicting_evidence = [item.evidence_id for item in conflicting]
                claim.derivation_status = ClaimStatus.SUPPORTED.value if supporting else ClaimStatus.UNRESOLVED.value
                formal_records_for_claim = formal_by_claim.get(claim.claim_id, [])
                if any(item.compiled for item in formal_records_for_claim):
                    claim.formalization_status = ClaimStatus.FORMALLY_VERIFIED.value
                elif formal_records_for_claim:
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
                elif claim.supporting_evidence:
                    claim.independent_verification_status = ClaimStatus.UNRESOLVED.value
                claim.confidence = round(min(0.95, 0.2 + 0.15 * len(claim.supporting_evidence)), 3)
                claim_index[claim.claim_id] = claim

            cycle.claims = [claim_index[key].to_dict() for key in claim_index]
            cycle.transition(ResearchState.ACCEPTANCE_GATE)
            acceptance = self._acceptance_decision(problem, claim_index, cycle.formal_verifications, cycle.adversarial_reviews, independence)
            cycle.problem_resolution_status = acceptance["claim_status"]
            cycle.unresolved_questions = acceptance["unresolved_questions"]
            cycle.acceptance_gate_passed = acceptance["accepted"]
            if acceptance["accepted"]:
                cycle.status = "complete"
                cycle.transition(ResearchState.COMPLETE)
            else:
                cycle.status = "no_solution_claim"
                cycle.transition(ResearchState.NO_SOLUTION_CLAIM)
            self.ledger_store.write_ledger(claim_index.values())
            self.ledger_store.write_cycle(fingerprint, cycle)
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
            )
            self.ledger_store.write_cycle(fingerprint, cycle)
            cycle.durable_record_written = True
            return cycle

    @staticmethod
    def _acceptance_decision(
        problem: ResearchProblem,
        claim_index: dict[str, ResearchClaim],
        formal_verifications: list[dict[str, Any]],
        adversarial_reviews: list[dict[str, Any]],
        independence: dict[str, Any],
    ) -> dict[str, Any]:
        unresolved: list[str] = []
        primary_claims = [claim_index[item] for item in problem.primary_claims if item in claim_index]
        if not primary_claims:
            unresolved.append("No primary claims were loaded.")
            return {"accepted": False, "claim_status": ClaimStatus.UNRESOLVED.value, "unresolved_questions": unresolved}
        if not any(item.get("compiled") for item in formal_verifications):
            unresolved.append("No compiled formal proof was recorded.")
        if any(item.get("status") in {ClaimStatus.CHALLENGED.value, ClaimStatus.DISPUTED.value, ClaimStatus.REFUTED.value} for item in adversarial_reviews):
            unresolved.append("At least one adversarial mathematical objection remains unresolved.")
        for claim in primary_claims:
            if claim.derivation_status not in {ClaimStatus.SUPPORTED.value, ClaimStatus.REPRODUCED.value}:
                unresolved.append(f"Primary claim {claim.claim_id} lacks supporting derivation evidence.")
            if claim.formalization_status not in {ClaimStatus.FORMALLY_VERIFIED.value, ClaimStatus.FORMALIZED.value}:
                unresolved.append(f"Primary claim {claim.claim_id} lacks formalization metadata.")
            if claim.independent_verification_status != ClaimStatus.INDEPENDENTLY_VERIFIED.value:
                unresolved.append(
                    f"Independent verification remains incomplete or non-independent for primary claim {claim.claim_id}."
                )
        accepted = not unresolved
        status = ClaimStatus.INDEPENDENTLY_VERIFIED.value if accepted else ClaimStatus.UNRESOLVED.value
        return {"accepted": accepted, "claim_status": status, "unresolved_questions": unresolved}


class StaticResearchProblemAdapter:
    def __init__(self, bundle_path: str | Path):
        self.ingestor = ResearchSourceIngestor(bundle_path)
        self.bundle_path = Path(bundle_path).resolve()
        self._bundle = self.ingestor.load_bundle()
        self.problem_id = str(self._bundle["problem"]["problem_id"])

    def ingest(self):
        return self.ingestor.ingest()

    def problem_fingerprint(self) -> str:
        return _fingerprint(self.problem_id, self._bundle)


class NavierStokesProblemAdapter(StaticResearchProblemAdapter):
    def __init__(self, bundle_path: str | Path | None = None):
        base = Path(bundle_path).resolve() if bundle_path is not None else Path(__file__).resolve().parents[2] / "data" / "research" / "navier_stokes_research_bundle.json"
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
        response = {
            "question_id": question_id,
            "prompt": question.get("prompt", ""),
            "answer": dict(question.get("answer", {})),
            "claims": selected_claims,
            "sources": selected_sources,
        }
        return response

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
