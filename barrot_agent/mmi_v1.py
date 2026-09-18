from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from hashlib import sha256
from pathlib import Path
import json
import time


class ParseState(str, Enum):
    OBSERVED = "OBSERVED"
    PARSED = "PARSED"
    DERIVED = "DERIVED"
    INFERRED = "INFERRED"
    HYPOTHESIZED = "HYPOTHESIZED"
    PROPOSED = "PROPOSED"
    UNKNOWN = "UNKNOWN"
    NOT_PARSABLE = "NOT_PARSABLE"
    NOT_PRESENT = "NOT_PRESENT"


class ProvenanceClass(str, Enum):
    EXTERNAL_PRIMARY = "EXTERNAL_PRIMARY"
    EXTERNAL_SECONDARY = "EXTERNAL_SECONDARY"
    INDEPENDENT_EXTERNAL = "INDEPENDENT_EXTERNAL"
    INTERNAL_OBSERVATION = "INTERNAL_OBSERVATION"
    MODEL_DERIVED = "MODEL_DERIVED"
    BARROT_GENERATED = "BARROT_GENERATED"


class Freshness(str, Enum):
    STATIC = "STATIC"
    SLOW_CHANGE = "SLOW_CHANGE"
    TIME_SENSITIVE = "TIME_SENSITIVE"
    VOLATILE = "VOLATILE"


class StageOutcome(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class MMIResult(str, Enum):
    COMPLETE = "MMI_COMPLETE"
    PARTIAL = "MMI_PARTIAL"
    BLOCKED = "MMI_BLOCKED"
    ESCALATED = "MMI_ESCALATED"


class TerminationReason(str, Enum):
    MAX_DEPTH = "MAX_DEPTH"
    MAX_ACQUISITION_BUDGET = "MAX_ACQUISITION_BUDGET"
    MAX_UNRESOLVED_ITERATIONS = "MAX_UNRESOLVED_ITERATIONS"
    RESOURCE_LIMIT = "RESOURCE_LIMIT"
    DUPLICATE_THRESHOLD = "DUPLICATE_THRESHOLD"
    DIMINISHING_INFORMATION_GAIN = "DIMINISHING_INFORMATION_GAIN"
    HUMAN_ESCALATION = "HUMAN_ESCALATION"


class Idempotency(str, Enum):
    IDENTICAL_REVALIDATION = "IDENTICAL_REVALIDATION"
    SOURCE_UPDATED = "SOURCE_UPDATED"
    PARTIAL_REINGESTION = "PARTIAL_REINGESTION"
    NEW_DATASET = "NEW_DATASET"


class Reconciliation(str, Enum):
    CONFIRMS_EXISTING = "CONFIRMS_EXISTING"
    EXTENDS_EXISTING = "EXTENDS_EXISTING"
    REFINES_EXISTING = "REFINES_EXISTING"
    SUPERSEDES_EXISTING = "SUPERSEDES_EXISTING"
    CONTRADICTS_EXISTING = "CONTRADICTS_EXISTING"
    DUPLICATES_EXISTING = "DUPLICATES_EXISTING"
    UNRELATED = "UNRELATED"


@dataclass
class ScopeItem:
    path: str
    state: ParseState
    scale: str
    reason: str = ""


@dataclass
class SourceRecord:
    source_id: str
    uri: str
    provenance_class: ProvenanceClass
    depth: int = 1
    content_hash: str = ""
    observed_at: str = ""


@dataclass
class ComponentRecord:
    component_id: str
    parent_id: str | None
    depth: int
    state: ParseState
    relationship: str = ""
    source_ids: list[str] = field(default_factory=list)


@dataclass
class EvidenceRecord:
    evidence_id: str
    claim: str
    state: ParseState
    source_ids: list[str] = field(default_factory=list)
    supporting: bool = True
    independent: bool = False
    content_hash: str = ""
    observed_at: str = ""

    def lineage_key(self) -> str:
        source = self.source_ids[0] if self.source_ids else "none"
        return "|".join(
            [
                self.evidence_id,
                source,
                self.observed_at,
                self.content_hash,
            ]
        )


@dataclass
class StageRecord:
    name: str
    outcome: StageOutcome
    details: str = ""


@dataclass
class MMIRecord:
    ingestion_id: str
    dataset: dict
    provenance: dict
    component_map: list[ComponentRecord] = field(default_factory=list)
    source_graph: list[SourceRecord] = field(default_factory=list)
    scope: list[ScopeItem] = field(default_factory=list)
    exclusions: list[str] = field(default_factory=list)
    evidence: list[EvidenceRecord] = field(default_factory=list)
    corroboration_results: list[dict] = field(default_factory=list)
    knowledge_gaps: list[str] = field(default_factory=list)
    related_knowledge: list[str] = field(default_factory=list)
    learning: list[str] = field(default_factory=list)
    capability_implications: list[str] = field(default_factory=list)
    discovery_targets: list[str] = field(default_factory=list)
    acquisition_requests: list[str] = field(default_factory=list)
    self_upgrade_candidates: list[str] = field(default_factory=list)
    reconciliation: list[dict] = field(default_factory=list)
    negative_knowledge: list[dict] = field(default_factory=list)
    stages: list[StageRecord] = field(default_factory=list)
    protocol_completeness: float = 0.0
    knowledge_completeness: float = 0.0
    result: MMIResult = MMIResult.PARTIAL
    termination_reason: TerminationReason | None = None
    idempotency: Idempotency | None = None

    component_max_depth: int = 4
    source_max_depth: int = 4
    mmi_version: str = "1.0"

    def validate(self) -> list[str]:
        errors = []

        if self.component_max_depth != 4:
            errors.append("component depth must be 4")

        if self.source_max_depth != 4:
            errors.append("source depth must be 4")

        for item in self.scope:
            if not isinstance(item.state, ParseState):
                errors.append(f"invalid scope state: {item.path}")

        for item in self.component_map:
            if not 1 <= item.depth <= self.component_max_depth:
                errors.append(f"component depth out of range: {item.component_id}")

        for item in self.source_graph:
            if not 1 <= item.depth <= self.source_max_depth:
                errors.append(f"source depth out of range: {item.source_id}")

        source_classes = {
            s.source_id: s.provenance_class for s in self.source_graph
        }

        for evidence in self.evidence:
            if evidence.independent:
                if not evidence.source_ids:
                    errors.append(
                        f"independent evidence has no source: {evidence.evidence_id}"
                    )
                if all(
                    source_classes.get(s) in {
                        ProvenanceClass.MODEL_DERIVED,
                        ProvenanceClass.BARROT_GENERATED,
                    }
                    for s in evidence.source_ids
                ):
                    errors.append(
                        f"Barrot-derived evidence cannot be independent: "
                        f"{evidence.evidence_id}"
                    )

        return errors


class MMIStateMachine:
    ORDER = [
        "RECEIVED",
        "PROVENANCE_CAPTURED",
        "DECOMPOSED",
        "REPRESENTATIONS_ASSESSED",
        "EVIDENCE_NORMALIZED",
        "CORROBORATION",
        "GAP_ANALYSIS",
        "RECONCILIATION",
        "LEARNING_EXTRACTED",
        "CAPABILITY_ANALYZED",
        "ACQUISITION_TARGETS_GENERATED",
        "VERIFICATION",
    ]

    @classmethod
    def evaluate(cls, record: MMIRecord) -> MMIResult:
        errors = record.validate()
        if errors:
            return MMIResult.BLOCKED

        outcomes = {s.name: s.outcome for s in record.stages}

        required = [
            "RECEIVED",
            "PROVENANCE_CAPTURED",
            "EVIDENCE_NORMALIZED",
            "VERIFICATION",
        ]

        if any(outcomes.get(x) == StageOutcome.BLOCKED for x in required):
            return MMIResult.BLOCKED

        if any(outcomes.get(x) == StageOutcome.PARTIAL for x in required):
            return MMIResult.PARTIAL

        # A COMPLETE label is not sufficient proof by itself.
        # Required artifacts must actually exist.
        if outcomes.get("PROVENANCE_CAPTURED") == StageOutcome.COMPLETE:
            if not record.provenance or not record.source_graph:
                return MMIResult.PARTIAL

        if outcomes.get("EVIDENCE_NORMALIZED") == StageOutcome.COMPLETE:
            if not record.evidence:
                return MMIResult.PARTIAL

        if outcomes.get("CORROBORATION") == StageOutcome.COMPLETE:
            if not record.corroboration_results:
                return MMIResult.PARTIAL

        if all(
            outcomes.get(x) in {
                StageOutcome.COMPLETE,
                StageOutcome.NOT_APPLICABLE,
            }
            for x in cls.ORDER
        ):
            return MMIResult.COMPLETE

        return MMIResult.PARTIAL


class BoundedTraversal:
    def __init__(self, max_depth: int = 4):
        if max_depth < 1:
            raise ValueError("max_depth must be positive")
        self.max_depth = max_depth

    def walk(self, roots, children):
        result = []

        def visit(node, depth, ancestry):
            if depth > self.max_depth:
                return
            key = str(node)
            if key in ancestry:
                return

            result.append((node, depth))
            for child in children(node):
                visit(child, depth + 1, ancestry | {key})

        for root in roots:
            visit(root, 1, set())

        return result


class FreshnessPolicy:
    def __init__(
        self,
        volatile_hours: int = 24,
        time_sensitive_days: int = 30,
        slow_change_days: int = 365,
    ):
        self.volatile_hours = volatile_hours
        self.time_sensitive_days = time_sensitive_days
        self.slow_change_days = slow_change_days

    def classify(self, observed_at: float | None, now: float | None = None) -> Freshness:
        if observed_at is None:
            return Freshness.STATIC

        now = time.time() if now is None else now
        age = max(0.0, now - observed_at)

        if age <= self.volatile_hours * 3600:
            return Freshness.VOLATILE
        if age <= self.time_sensitive_days * 86400:
            return Freshness.TIME_SENSITIVE
        if age <= self.slow_change_days * 86400:
            return Freshness.SLOW_CHANGE
        return Freshness.STATIC


def classify_idempotency(
    previous_hash: str | None,
    current_hash: str,
    *,
    previous_complete: bool = True,
) -> Idempotency:
    if previous_hash is None:
        return Idempotency.NEW_DATASET
    if previous_hash == current_hash and previous_complete:
        return Idempotency.IDENTICAL_REVALIDATION
    if previous_hash == current_hash:
        return Idempotency.PARTIAL_REINGESTION
    return Idempotency.SOURCE_UPDATED


class MMIExecutionLedger:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: dict) -> str:
        previous = ""
        if self.path.exists():
            lines = self.path.read_text().splitlines()
            if lines:
                previous = json.loads(lines[-1]).get("event_hash", "")

        payload = dict(event)
        payload["previous_hash"] = previous
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        event_hash = "sha256:" + sha256(canonical.encode()).hexdigest()
        payload["event_hash"] = event_hash

        with self.path.open("a") as f:
            f.write(json.dumps(payload, sort_keys=True) + "\n")

        return event_hash

    def verify(self) -> bool:
        if not self.path.exists():
            return True

        previous = ""
        for line in self.path.read_text().splitlines():
            if not line.strip():
                continue

            try:
                event = json.loads(line)
            except (json.JSONDecodeError, TypeError):
                return False

            if not isinstance(event, dict):
                return False

            recorded = event.pop("event_hash", None)

            if event.get("previous_hash", "") != previous:
                return False

            canonical = json.dumps(
                event, sort_keys=True, separators=(",", ":")
            )
            expected = "sha256:" + sha256(canonical.encode()).hexdigest()

            if recorded != expected:
                return False

            previous = recorded

        return True


class MMICompletenessReport:
    """Deterministic audit of MMI protocol completeness."""

    REQUIRED_ARTIFACTS = (
        "provenance",
        "source_graph",
        "evidence",
        "corroboration_results",
    )

    @classmethod
    def build(cls, record: MMIRecord) -> dict:
        artifact_presence = {
            name: bool(getattr(record, name))
            for name in cls.REQUIRED_ARTIFACTS
        }

        required_stages = {}
        for stage in MMIStateMachine.ORDER:
            matching = next(
                (item for item in record.stages if item.name == stage),
                None,
            )
            required_stages[stage] = (
                matching.outcome.value
                if matching is not None
                else None
            )

        protocol_complete = (
            all(
                outcome in {
                    StageOutcome.COMPLETE.value,
                    StageOutcome.NOT_APPLICABLE.value,
                }
                for outcome in required_stages.values()
            )
            and all(artifact_presence.values())
        )

        completed_stages = sum(
            outcome in {
                StageOutcome.COMPLETE.value,
                StageOutcome.NOT_APPLICABLE.value,
            }
            for outcome in required_stages.values()
        )
        protocol_completeness = (
            completed_stages / len(required_stages)
            if required_stages
            else 0.0
        )

        return {
            "mmi_version": record.mmi_version,
            "ingestion_id": record.ingestion_id,
            "protocol_complete": protocol_complete,
            "protocol_completeness": protocol_completeness,
            "knowledge_completeness": record.knowledge_completeness,
            "required_artifacts": artifact_presence,
            "stage_outcomes": required_stages,
            "result": (
                MMIResult.COMPLETE.value
                if protocol_complete
                else MMIResult.PARTIAL.value
            ),
        }


class MMIEngine:
    def __init__(self, *, components=None, ledger=None):
        self.components = components or {}
        self.ledger = ledger

    def create_record(self, ingestion_id: str, dataset: dict, provenance: dict):
        record = MMIRecord(
            ingestion_id=ingestion_id,
            dataset=dataset,
            provenance=provenance,
        )

        if self.ledger is not None:
            self.ledger.append({
                "event": "MMI_RECEIVED",
                "ingestion_id": ingestion_id,
            })

        return record

    def record_corroboration(
        self,
        record: MMIRecord,
        result: dict,
    ) -> MMIRecord:
        record.corroboration_results.append(result)

        if self.ledger is not None:
            self.ledger.append({
                "event": "MMI_CORROBORATION_RECORDED",
                "ingestion_id": record.ingestion_id,
                "corroboration": result,
            })

        return record

    def complete(self, record: MMIRecord) -> MMIRecord:
        record.result = MMIStateMachine.evaluate(record)

        if self.ledger is not None:
            self.ledger.append({
                "event": "MMI_COMPLETED",
                "ingestion_id": record.ingestion_id,
                "result": record.result.value,
            })

        return record

    def completeness_report(self, record: MMIRecord) -> dict:
        report = MMICompletenessReport.build(record)

        if self.ledger is not None:
            self.ledger.append({
                "event": "MMI_COMPLETENESS_REPORTED",
                "ingestion_id": record.ingestion_id,
                "protocol_complete": report["protocol_complete"],
                "result": report["result"],
            })

        return report

    def serialize(self, record: MMIRecord) -> dict:
        return asdict(record)
