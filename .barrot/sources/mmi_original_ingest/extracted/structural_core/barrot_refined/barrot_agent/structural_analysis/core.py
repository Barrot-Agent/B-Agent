"""Barrot V3 Structural Analysis Core v1.1.

A small deterministic kernel for evidence-aware structural analysis. It records
observations and computed descriptors without treating descriptor similarity as
mathematical equivalence or model output as proof.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from hashlib import sha256
import json
import math
from typing import Any, Callable, Iterable, Mapping, Sequence


class EvidenceStage(str, Enum):
    OBSERVED = "observed"
    COMPUTED = "computed"
    DERIVED = "derived"
    INFERRED = "inferred"
    HYPOTHESIZED = "hypothesized"


class VerificationStatus(str, Enum):
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    FAILED = "failed"
    NOT_APPLICABLE = "not_applicable"


class RelationType(str, Enum):
    EQUAL = "equal"
    ISOMORPHIC = "isomorphic"
    HOMEOMORPHIC = "homeomorphic"
    DIFFEOMORPHIC = "diffeomorphic"
    LINEARLY_EQUIVALENT = "linearly_equivalent"
    COMBINATORIALLY_EQUIVALENT = "combinatorially_equivalent"
    COORDINATE_EQUIVALENT = "coordinate_equivalent"
    APPROXIMATELY_EQUIVALENT = "approximately_equivalent"
    CONTAINED_IN = "contained_in"
    BOUNDARY_OF = "boundary_of"
    ADJACENT_TO = "adjacent_to"
    DERIVED_FROM = "derived_from"
    STRUCTURAL_CORRESPONDENCE = "structural_correspondence"


@dataclass(frozen=True)
class ConstraintResult:
    name: str
    status: str
    evidence_stage: EvidenceStage = EvidenceStage.COMPUTED
    verification: VerificationStatus = VerificationStatus.UNVERIFIED
    detail: str = ""

    def __post_init__(self) -> None:
        if self.status not in {"satisfied", "violated", "unknown"}:
            raise ValueError("constraint status must be satisfied, violated, or unknown")


@dataclass(frozen=True)
class InvariantResult:
    name: str
    value: Any
    definition: str = ""
    method: str = ""
    evidence_stage: EvidenceStage = EvidenceStage.COMPUTED
    verification: VerificationStatus = VerificationStatus.UNVERIFIED
    exact: bool = True
    tolerance: float | None = None

    def __post_init__(self) -> None:
        if self.tolerance is not None and (not math.isfinite(self.tolerance) or self.tolerance < 0):
            raise ValueError("tolerance must be finite and non-negative")


@dataclass(frozen=True)
class StructuralRelation:
    source_id: str
    target_id: str
    relation: RelationType
    criterion: str = ""
    witness: str = ""
    evidence_stage: EvidenceStage = EvidenceStage.DERIVED
    verification: VerificationStatus = VerificationStatus.UNVERIFIED


@dataclass(frozen=True)
class StructuralInput:
    representation: Any
    representation_type: str
    provenance: Mapping[str, Any] = field(default_factory=dict)
    constraints: Sequence[ConstraintResult] = field(default_factory=tuple)
    invariants: Sequence[InvariantResult] = field(default_factory=tuple)
    relations: Sequence[StructuralRelation] = field(default_factory=tuple)
    dimension: int | None = None
    codimension: int | None = None
    symmetries: Sequence[str] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.representation_type.strip():
            raise ValueError("representation_type must be non-empty")
        if self.dimension is not None and self.dimension < 0:
            raise ValueError("dimension must be non-negative")
        if self.codimension is not None and self.codimension < 0:
            raise ValueError("codimension must be non-negative")


@dataclass(frozen=True)
class StructuralSignature:
    representation_type: str
    constraints: tuple[ConstraintResult, ...]
    invariants: tuple[InvariantResult, ...]
    relations: tuple[StructuralRelation, ...]
    dimension: int | None
    codimension: int | None
    symmetries: tuple[str, ...]
    provenance: Mapping[str, Any]
    valid_region: str
    identity_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


ConstraintFn = Callable[[Any], ConstraintResult]
InvariantFn = Callable[[Any], InvariantResult]


class StructuralAnalyzer:
    """Deterministic kernel; domain-specific mathematics plugs into it."""

    def __init__(self, *, constraint_evaluators: Iterable[ConstraintFn] = (),
                 invariant_evaluators: Iterable[InvariantFn] = (),
                 max_evaluations: int = 128) -> None:
        if max_evaluations <= 0:
            raise ValueError("max_evaluations must be positive")
        self.constraint_evaluators = tuple(constraint_evaluators)
        self.invariant_evaluators = tuple(invariant_evaluators)
        self.max_evaluations = max_evaluations
        if len(self.constraint_evaluators) + len(self.invariant_evaluators) > max_evaluations:
            raise ValueError("configured evaluators exceed max_evaluations")

    def analyze(self, obj: StructuralInput) -> StructuralSignature:
        constraints = list(obj.constraints)
        invariants = list(obj.invariants)
        for fn in self.constraint_evaluators:
            result = fn(obj.representation)
            if not isinstance(result, ConstraintResult):
                raise TypeError("constraint evaluator must return ConstraintResult")
            constraints.append(result)
        for fn in self.invariant_evaluators:
            result = fn(obj.representation)
            if not isinstance(result, InvariantResult):
                raise TypeError("invariant evaluator must return InvariantResult")
            invariants.append(result)

        statuses = {c.status for c in constraints}
        region = "invalid" if "violated" in statuses else "unresolved" if "unknown" in statuses else "valid"
        # Order-independent identity: semantically unordered descriptors are normalized by name.
        constraints = sorted(constraints, key=lambda x: (x.name, x.status, x.detail))
        invariants = sorted(invariants, key=lambda x: (x.name, self._canonical(x.value)))
        relations = sorted(obj.relations, key=lambda x: (x.source_id, x.target_id, x.relation.value))
        symmetries = tuple(sorted(obj.symmetries))
        payload = {
            "representation_type": obj.representation_type,
            "constraints": [asdict(c) for c in constraints],
            "invariants": [asdict(i) for i in invariants],
            "relations": [asdict(r) for r in relations],
            "dimension": obj.dimension,
            "codimension": obj.codimension,
            "symmetries": list(symmetries),
            "provenance": dict(obj.provenance),
            "valid_region": region,
        }
        identity = sha256(self._canonical(payload).encode()).hexdigest()
        return StructuralSignature(obj.representation_type, tuple(constraints), tuple(invariants),
                                   tuple(relations), obj.dimension, obj.codimension, symmetries,
                                   dict(obj.provenance), region, identity)

    @staticmethod
    def compare_invariants(a: StructuralSignature, b: StructuralSignature) -> dict[str, Any]:
        left = {i.name: i.value for i in a.invariants}
        right = {i.name: i.value for i in b.invariants}
        common = sorted(set(left) & set(right))
        matches = [n for n in common if left[n] == right[n]]
        return {"common_invariants": common, "matching_invariants": matches,
                "same_dimension": a.dimension == b.dimension,
                "descriptor_match": bool(common) and len(matches) == len(common),
                "equivalence_claim": None,
                "evidence_stage": EvidenceStage.DERIVED.value,
                "verification": VerificationStatus.UNVERIFIED.value}

    @staticmethod
    def _canonical(value: Any) -> str:
        def normalize(x: Any) -> Any:
            if isinstance(x, Enum): return x.value
            if isinstance(x, float): return x if math.isfinite(x) else str(x)
            if isinstance(x, Mapping): return {str(k): normalize(v) for k, v in sorted(x.items(), key=lambda p: str(p[0]))}
            if isinstance(x, (list, tuple)): return [normalize(v) for v in x]
            if hasattr(x, "__dict__"): return normalize(vars(x))
            return x
        return json.dumps(normalize(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
