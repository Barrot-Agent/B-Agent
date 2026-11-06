"""Evidence-aware structural analysis primitives for Barrot V3.

This module produces deterministic descriptors. Descriptor agreement is not a
proof of mathematical equivalence; verification must come from an independent,
explicitly recorded method and witness.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
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


def _normalize(value: Any) -> Any:
    """Convert supported values to strict, deterministic JSON primitives."""
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return _normalize(asdict(value))
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite floats are not valid structural evidence")
        return value
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, Mapping):
        if not all(isinstance(key, str) for key in value):
            raise TypeError("canonical mapping keys must be strings")
        return {key: _normalize(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_normalize(item) for item in value]
    raise TypeError(f"unsupported canonical value type: {type(value).__name__}")


def _canonical(value: Any) -> str:
    return json.dumps(_normalize(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True)
class ConstraintResult:
    name: str
    status: str
    evidence_stage: EvidenceStage = EvidenceStage.COMPUTED
    verification: VerificationStatus = VerificationStatus.UNVERIFIED
    detail: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("constraint name must be non-empty")
        if self.status not in {"satisfied", "violated", "unknown"}:
            raise ValueError("constraint status must be satisfied, violated, or unknown")
        if not isinstance(self.evidence_stage, EvidenceStage):
            raise TypeError("evidence_stage must be EvidenceStage")
        if not isinstance(self.verification, VerificationStatus):
            raise TypeError("verification must be VerificationStatus")


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
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("invariant name must be non-empty")
        _normalize(self.value)
        if self.tolerance is not None and (
            not isinstance(self.tolerance, (int, float))
            or isinstance(self.tolerance, bool)
            or not math.isfinite(self.tolerance)
            or self.tolerance < 0
        ):
            raise ValueError("tolerance must be finite and non-negative")
        if not isinstance(self.evidence_stage, EvidenceStage):
            raise TypeError("evidence_stage must be EvidenceStage")
        if not isinstance(self.verification, VerificationStatus):
            raise TypeError("verification must be VerificationStatus")


@dataclass(frozen=True)
class StructuralRelation:
    source_id: str
    target_id: str
    relation: RelationType
    criterion: str = ""
    witness: str = ""
    evidence_stage: EvidenceStage = EvidenceStage.DERIVED
    verification: VerificationStatus = VerificationStatus.UNVERIFIED

    def __post_init__(self) -> None:
        if not isinstance(self.source_id, str) or not self.source_id.strip():
            raise ValueError("relation source_id must be non-empty")
        if not isinstance(self.target_id, str) or not self.target_id.strip():
            raise ValueError("relation target_id must be non-empty")
        if not isinstance(self.relation, RelationType):
            raise TypeError("relation must be RelationType")
        if not isinstance(self.evidence_stage, EvidenceStage):
            raise TypeError("evidence_stage must be EvidenceStage")
        if not isinstance(self.verification, VerificationStatus):
            raise TypeError("verification must be VerificationStatus")


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
        if not isinstance(self.representation_type, str) or not self.representation_type.strip():
            raise ValueError("representation_type must be non-empty")
        for name, value in (("dimension", self.dimension), ("codimension", self.codimension)):
            if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value < 0):
                raise ValueError(f"{name} must be a non-negative integer or None")
        _normalize(self.provenance)
        if not all(isinstance(item, ConstraintResult) for item in self.constraints):
            raise TypeError("constraints must contain ConstraintResult values")
        if not all(isinstance(item, InvariantResult) for item in self.invariants):
            raise TypeError("invariants must contain InvariantResult values")
        if not all(isinstance(item, StructuralRelation) for item in self.relations):
            raise TypeError("relations must contain StructuralRelation values")
        if not all(isinstance(item, str) and item.strip() for item in self.symmetries):
            raise ValueError("symmetries must contain non-empty strings")


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
        """Return a JSON-safe representation, including enum values."""
        return _normalize(asdict(self))

    def to_json(self) -> str:
        return _canonical(self.to_dict())


ConstraintFn = Callable[[Any], ConstraintResult]
InvariantFn = Callable[[Any], InvariantResult]


class StructuralAnalyzer:
    """Deterministic descriptor kernel; domain-specific mathematics plugs into it."""

    def __init__(self, *, constraint_evaluators: Iterable[ConstraintFn] = (),
                 invariant_evaluators: Iterable[InvariantFn] = (),
                 max_evaluations: int = 128) -> None:
        if not isinstance(max_evaluations, int) or isinstance(max_evaluations, bool) or max_evaluations <= 0:
            raise ValueError("max_evaluations must be a positive integer")
        self.constraint_evaluators = tuple(constraint_evaluators)
        self.invariant_evaluators = tuple(invariant_evaluators)
        self.max_evaluations = max_evaluations
        if len(self.constraint_evaluators) + len(self.invariant_evaluators) > max_evaluations:
            raise ValueError("configured evaluators exceed max_evaluations")
        if not all(callable(fn) for fn in self.constraint_evaluators + self.invariant_evaluators):
            raise TypeError("all evaluators must be callable")

    def analyze(self, obj: StructuralInput) -> StructuralSignature:
        if not isinstance(obj, StructuralInput):
            raise TypeError("analyze requires StructuralInput")
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

        constraints.sort(key=_canonical)
        invariants.sort(key=_canonical)
        relations = sorted(obj.relations, key=_canonical)
        symmetries = tuple(sorted(obj.symmetries))
        statuses = {c.status for c in constraints}
        region = "invalid" if "violated" in statuses else "unresolved" if "unknown" in statuses else "valid"
        payload = {
            "representation_type": obj.representation_type,
            "constraints": constraints,
            "invariants": invariants,
            "relations": relations,
            "dimension": obj.dimension,
            "codimension": obj.codimension,
            "symmetries": symmetries,
            "provenance": obj.provenance,
            "valid_region": region,
        }
        identity = sha256(_canonical(payload).encode("utf-8")).hexdigest()
        return StructuralSignature(obj.representation_type, tuple(constraints), tuple(invariants),
                                   tuple(relations), obj.dimension, obj.codimension, symmetries,
                                   _normalize(obj.provenance), region, identity)

    @staticmethod
    def compare_invariants(a: StructuralSignature, b: StructuralSignature) -> dict[str, Any]:
        left: dict[str, list[Any]] = {}
        right: dict[str, list[Any]] = {}
        for item in a.invariants:
            left.setdefault(item.name, []).append(_normalize(item.value))
        for item in b.invariants:
            right.setdefault(item.name, []).append(_normalize(item.value))
        common = sorted(set(left) & set(right))
        matches = [name for name in common if _canonical(left[name]) == _canonical(right[name])]
        return {
            "common_invariants": common,
            "matching_invariants": matches,
            "same_dimension": a.dimension == b.dimension,
            "descriptor_match": bool(common) and len(matches) == len(common),
            "equivalence_claim": None,
            "evidence_stage": EvidenceStage.DERIVED.value,
            "verification": VerificationStatus.UNVERIFIED.value,
        }
