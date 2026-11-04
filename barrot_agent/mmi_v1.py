from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from hashlib import sha256
from pathlib import Path
import json
import os
import time
from datetime import datetime, timezone

try:
    import fcntl
except ImportError:  # pragma: no cover - non-POSIX fallback is single-writer only
    fcntl = None

from barrot_agent.evolution.source_independence import canonical_publisher_group


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
    # Canonical publisher/origin; shared groups are not independent.
    independence_group: str = ""


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
    claim_id: str = ""

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
    structural_signature: dict = field(default_factory=dict)
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

        stage_names = []
        for index, stage in enumerate(self.stages):
            name = getattr(stage, "name", None)
            outcome = getattr(stage, "outcome", None)
            if not isinstance(name, str) or name not in MMIStateMachine.ORDER:
                errors.append(f"unknown or invalid MMI stage at index {index}")
                continue
            stage_names.append(name)
            if not isinstance(outcome, StageOutcome):
                errors.append(f"invalid stage outcome: {name}")
        if len(stage_names) != len(set(stage_names)):
            errors.append("duplicate MMI stage names")
        positions = [MMIStateMachine.ORDER.index(name) for name in stage_names]
        if positions != sorted(positions):
            errors.append("MMI stages are not in protocol order")

        for item in self.scope:
            if not isinstance(item, ScopeItem) or not isinstance(item.state, ParseState):
                errors.append(f"invalid scope item: {getattr(item, 'path', '<unknown>')}")

        component_ids = []
        for item in self.component_map:
            component_id = getattr(item, "component_id", None)
            depth = getattr(item, "depth", None)
            if not isinstance(component_id, str) or not component_id.strip():
                errors.append("component ID must be a non-empty string")
                continue
            component_ids.append(component_id)
            if isinstance(depth, bool) or not isinstance(depth, int) or not 1 <= depth <= self.component_max_depth:
                errors.append(f"component depth out of range: {component_id}")
            if not isinstance(getattr(item, "state", None), ParseState):
                errors.append(f"invalid component parse state: {component_id}")
        if len(component_ids) != len(set(component_ids)):
            errors.append("duplicate component IDs")
        component_id_set = set(component_ids)
        for item in self.component_map:
            parent_id = getattr(item, "parent_id", None)
            if parent_id is not None:
                if not isinstance(parent_id, str) or not parent_id.strip():
                    errors.append("component parent ID must be a non-empty string or null")
                elif parent_id not in component_id_set:
                    errors.append(f"unknown component parent: {parent_id}")

        source_classes = {}
        for item in self.source_graph:
            source_id = getattr(item, "source_id", None)
            depth = getattr(item, "depth", None)
            if not isinstance(source_id, str) or not source_id.strip():
                errors.append("source ID must be a non-empty string")
                continue
            if source_id in source_classes:
                errors.append("duplicate source IDs in source graph")
            else:
                provenance_class = getattr(item, "provenance_class", None)
                source_classes[source_id] = provenance_class
                if not isinstance(provenance_class, ProvenanceClass):
                    errors.append(f"invalid source provenance class: {source_id}")
            if isinstance(depth, bool) or not isinstance(depth, int) or not 1 <= depth <= self.source_max_depth:
                errors.append(f"source depth out of range: {source_id}")
            if not isinstance(getattr(item, "uri", None), str):
                errors.append(f"source URI must be a string: {source_id}")

        evidence_ids = []
        for item in self.evidence:
            evidence_id = getattr(item, "evidence_id", None)
            if not isinstance(evidence_id, str) or not evidence_id.strip():
                errors.append("evidence ID must be a non-empty string")
                continue
            evidence_ids.append(evidence_id)
            if not isinstance(getattr(item, "state", None), ParseState):
                errors.append(f"invalid evidence parse state: {evidence_id}")
            source_ids = getattr(item, "source_ids", None)
            if not isinstance(source_ids, list):
                errors.append(f"evidence source_ids must be a list: {evidence_id}")
                continue
            for source_id in source_ids:
                if not isinstance(source_id, str) or not source_id.strip():
                    errors.append(f"invalid source reference in evidence: {evidence_id}")
                elif source_id not in source_classes:
                    errors.append(f"unknown source reference {source_id} in evidence: {evidence_id}")
        if len(evidence_ids) != len(set(evidence_ids)):
            errors.append("duplicate evidence IDs")

        external_classes = {
            ProvenanceClass.EXTERNAL_PRIMARY,
            ProvenanceClass.EXTERNAL_SECONDARY,
            ProvenanceClass.INDEPENDENT_EXTERNAL,
        }
        for item in self.evidence:
            if getattr(item, "independent", False):
                source_ids = getattr(item, "source_ids", None)
                evidence_id = getattr(item, "evidence_id", "<unknown>")
                if not isinstance(source_ids, list):
                    # The first evidence pass records the malformed container.
                    continue
                valid_source_ids = [
                    source_id for source_id in source_ids
                    if isinstance(source_id, str) and source_id.strip()
                ]
                if not valid_source_ids:
                    errors.append(f"independent evidence cannot be independent without a valid source: {evidence_id}")
                elif any(source_id not in source_classes for source_id in valid_source_ids):
                    errors.append(f"independent evidence cannot be independent with an unknown source: {evidence_id}")
                elif any(
                    not isinstance(source_classes[source_id], ProvenanceClass)
                    or source_classes[source_id] not in external_classes
                    for source_id in valid_source_ids
                ):
                    errors.append(f"independent evidence cannot be independent unless it references only external sources: {evidence_id}")

        if self.structural_signature:
            if not isinstance(self.structural_signature, dict):
                errors.append("structural signature must be an object")
            else:
                if self.structural_signature.get("valid_region") not in {"valid", "unresolved", "invalid"}:
                    errors.append("structural signature has an invalid valid_region")
                identity_hash = self.structural_signature.get("identity_hash")
                if not isinstance(identity_hash, str) or len(identity_hash) != 64 or any(ch not in "0123456789abcdef" for ch in identity_hash.lower()):
                    errors.append("structural signature identity_hash must be a 64-character SHA-256 hex digest")

        for index, result in enumerate(self.corroboration_results):
            if not isinstance(result, dict):
                errors.append(f"invalid corroboration result: {index}")
                continue
            status = str(result.get("status", "")).upper()
            if status in {"CORROBORATED", "CONTRADICTORY"}:
                if not self._claim_bound_corroboration(result):
                    errors.append(
                        f"{status} result requires claim-bound observed evidence, "
                        "source-linked publisher identities, and at least two "
                        "distinct independence groups"
                    )

        return errors

    def _independence_groups_for(self, source_ids):
        if not isinstance(source_ids, list) or len(source_ids) < 2:
            return None
        if any(not isinstance(source_id, str) or not source_id.strip() for source_id in source_ids):
            return None
        if len(set(source_ids)) != len(source_ids):
            return None

        source_by_id = {}
        for source in self.source_graph:
            source_id = getattr(source, "source_id", None)
            if not isinstance(source_id, str) or not source_id.strip() or source_id in source_by_id:
                return None
            source_by_id[source_id] = source
        if any(source_id not in source_by_id for source_id in source_ids):
            return None

        external_classes = {
            ProvenanceClass.EXTERNAL_PRIMARY,
            ProvenanceClass.EXTERNAL_SECONDARY,
            ProvenanceClass.INDEPENDENT_EXTERNAL,
        }
        groups = set()
        for source_id in source_ids:
            source = source_by_id[source_id]
            provenance_class = getattr(source, "provenance_class", None)
            if (
                not isinstance(provenance_class, ProvenanceClass)
                or provenance_class not in external_classes
            ):
                return None
            uri = getattr(source, "uri", None)
            if not isinstance(uri, str) or not uri.strip():
                return None
            resolved = canonical_publisher_group(uri)
            declared = getattr(source, "independence_group", None)
            if not resolved or not isinstance(declared, str):
                return None
            if declared.strip().casefold() != resolved.casefold():
                return None
            groups.add(resolved.casefold())
        return groups

    def _claim_bound_corroboration(self, result: dict) -> bool:
        status = str(result.get("status", "")).upper()
        claim_id = result.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id.strip():
            return False

        evidence_by_id = {}
        for evidence in self.evidence:
            evidence_id = getattr(evidence, "evidence_id", None)
            if not isinstance(evidence_id, str) or not evidence_id.strip() or evidence_id in evidence_by_id:
                return False
            evidence_by_id[evidence_id] = evidence

        if status == "CORROBORATED":
            supporting_ids = result.get("supporting_evidence_ids")
            if (
                not isinstance(supporting_ids, list)
                or len(supporting_ids) < 2
                or any(not isinstance(evidence_id, str) or not evidence_id.strip() for evidence_id in supporting_ids)
                or len(set(supporting_ids)) != len(supporting_ids)
            ):
                return False
            if any(evidence_id not in evidence_by_id for evidence_id in supporting_ids):
                return False
            evidence_records = [evidence_by_id[eid] for eid in supporting_ids]
            if any(
                evidence.claim_id != claim_id
                or evidence.supporting is not True
                or not isinstance(evidence.state, ParseState)
                or evidence.state not in {ParseState.OBSERVED, ParseState.PARSED}
                or not isinstance(evidence.source_ids, list)
                or not evidence.source_ids
                or any(not isinstance(source_id, str) or not source_id.strip() for source_id in evidence.source_ids)
                for evidence in evidence_records
            ):
                return False
            if any(
                evidence.claim_id == claim_id and evidence.supporting is False
                for evidence in self.evidence
            ):
                return False
        elif status == "CONTRADICTORY":
            supporting_ids = result.get("supporting_evidence_ids")
            contradicting_ids = result.get("contradicting_evidence_ids")
            if not isinstance(supporting_ids, list) or not supporting_ids or not isinstance(contradicting_ids, list) or not contradicting_ids:
                return False
            all_ids = supporting_ids + contradicting_ids
            if any(not isinstance(evidence_id, str) or not evidence_id.strip() for evidence_id in all_ids):
                return False
            if len(set(all_ids)) != len(all_ids):
                return False
            if any(evidence_id not in evidence_by_id for evidence_id in all_ids):
                return False
            supporting_records = [evidence_by_id[eid] for eid in supporting_ids]
            contradicting_records = [evidence_by_id[eid] for eid in contradicting_ids]
            if any(
                evidence.claim_id != claim_id
                or evidence.supporting is not True
                or not isinstance(evidence.state, ParseState)
                or evidence.state not in {ParseState.OBSERVED, ParseState.PARSED}
                or not isinstance(evidence.source_ids, list)
                or not evidence.source_ids
                or any(not isinstance(source_id, str) or not source_id.strip() for source_id in evidence.source_ids)
                for evidence in supporting_records
            ):
                return False
            if any(
                evidence.claim_id != claim_id
                or evidence.supporting is not False
                or evidence.state not in {ParseState.OBSERVED, ParseState.PARSED}
                or not isinstance(evidence.source_ids, list)
                or not evidence.source_ids
                or any(not isinstance(source_id, str) or not source_id.strip() for source_id in evidence.source_ids)
                for evidence in contradicting_records
            ):
                return False
            required_ids = set(all_ids)
            reconciled_ids = set()
            for item in self.reconciliation:
                if not isinstance(item, dict):
                    continue
                evidence_ids = item.get("evidence_ids")
                if isinstance(evidence_ids, list):
                    reconciled_ids.update(eid for eid in evidence_ids if isinstance(eid, str) and eid.strip())
            if not required_ids.issubset(reconciled_ids):
                return False
            evidence_records = supporting_records + contradicting_records
        else:
            return False

        source_ids = {
            source_id
            for evidence in evidence_records
            for source_id in evidence.source_ids
        }
        declared_source_ids = result.get("independent_source_ids")
        if (
            not isinstance(declared_source_ids, list)
            or any(not isinstance(source_id, str) or not source_id.strip() for source_id in declared_source_ids)
            or len(set(declared_source_ids)) != len(declared_source_ids)
            or set(declared_source_ids) != source_ids
        ):
            return False

        groups = self._independence_groups_for(declared_source_ids)
        if groups is None or len(groups) < 2:
            return False
        if result.get("independent_sources") != len(groups):
            return False
        return True

    def corroboration_complete(self) -> bool:
        return any(
            isinstance(result, dict)
            and str(result.get("status", "")).upper()
            in {"CORROBORATED", "CONTRADICTORY"}
            and self._claim_bound_corroboration(result)
            for result in self.corroboration_results
        )


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

        if any(outcomes.get(x) != StageOutcome.COMPLETE for x in required):
            return MMIResult.PARTIAL

        if outcomes.get("CORROBORATION") == StageOutcome.BLOCKED:
            return MMIResult.BLOCKED
        if outcomes.get("CORROBORATION") == StageOutcome.PARTIAL:
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
            if not record.corroboration_complete():
                return MMIResult.PARTIAL

        if outcomes.get("CORROBORATION") == StageOutcome.NOT_APPLICABLE:
            corroboration_stage = next(
                (
                    stage
                    for stage in record.stages
                    if stage.name == "CORROBORATION"
                ),
                None,
            )
            if (
                corroboration_stage is None
                or not corroboration_stage.details.strip()
            ):
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
        if not isinstance(event, dict):
            raise TypeError("MMI ledger event must be an object")
        if "event_hash" in event or "previous_hash" in event or "ledger_recorded_at" in event:
            raise ValueError("MMI ledger hash-chain fields are reserved")
        self.path.parent.mkdir(parents=True, exist_ok=True)

        with self.path.open("a+", encoding="utf-8") as handle:
            locked = False
            try:
                if fcntl is not None:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
                    locked = True
                if not self.verify():
                    raise ValueError("MMI execution ledger integrity check failed; refusing append")
                handle.seek(0)
                lines = handle.read().splitlines()
                last_record = next((line for line in reversed(lines) if line.strip()), None)
                previous = json.loads(last_record).get("event_hash", "") if last_record else ""

                payload = dict(event)
                payload["ledger_recorded_at"] = datetime.now(timezone.utc).isoformat()
                payload["previous_hash"] = previous
                canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
                event_hash = "sha256:" + sha256(canonical.encode()).hexdigest()
                payload["event_hash"] = event_hash

                handle.seek(0, os.SEEK_END)
                handle.write(json.dumps(payload, sort_keys=True) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
                return event_hash
            finally:
                if locked and fcntl is not None:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def verify(self) -> bool:
        if not self.path.exists():
            return True

        previous = ""
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
        except OSError:
            return False
        for line in lines:
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

        if required_stages.get("CORROBORATION") == StageOutcome.NOT_APPLICABLE.value:
            corroboration_stage = next(
                (
                    stage
                    for stage in record.stages
                    if stage.name == "CORROBORATION"
                ),
                None,
            )
            if corroboration_stage is not None and corroboration_stage.details.strip():
                artifact_presence["corroboration_results"] = True

        state_result = MMIStateMachine.evaluate(record)
        protocol_complete = (
            state_result == MMIResult.COMPLETE
            and all(artifact_presence.values())
        )

        completed_stages = sum(
            outcome in {
                StageOutcome.COMPLETE.value,
                StageOutcome.NOT_APPLICABLE.value,
            }
            for outcome in required_stages.values()
        )
        if (
            required_stages.get("CORROBORATION") == StageOutcome.COMPLETE.value
            and not record.corroboration_complete()
        ):
            completed_stages = max(0, completed_stages - 1)
        for stage_name in (
            "RECEIVED",
            "PROVENANCE_CAPTURED",
            "EVIDENCE_NORMALIZED",
            "VERIFICATION",
        ):
            if required_stages.get(stage_name) != StageOutcome.COMPLETE.value:
                if required_stages.get(stage_name) == StageOutcome.NOT_APPLICABLE.value:
                    completed_stages = max(0, completed_stages - 1)
        completed_stages = max(
            0,
            completed_stages - sum(not present for present in artifact_presence.values()),
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
            "corroboration_complete": record.corroboration_complete(),
            "validation_errors": record.validate(),
            "result": state_result.value,
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
