"""
BARROT STRUCTURAL DISCOVERY CORE

The smallest viable capability per the V3 Geometry/MMI analysis document:
representation -> constraint evaluation -> invariant computation ->
structural signature -> classification -> relational storage -> provenance.

Deliberately excludes (see analysis doc Section 17): Grassmannian-specific
structures, amplituhedron machinery, perturbation analysis, automated
conjecture generation. Those are extensions, evaluated separately, only
after this core is proven on real cases.

Zero LLM calls -- this is deterministic math/logic, not a Groq consumer.

Hard safety rules enforced as CODE, not just comments (doc Section 29):
- UNRESOLVED is a real, distinct state -- never silently becomes VALID
  or INVALID.
- Equivalence claims are TYPED and require an explicit criterion function.
  "Looks similar" can never produce an ISOMORPHISM or ALGEBRAIC_EQUIVALENCE
  result -- only APPROXIMATE_SIMILARITY, which is a different, weaker type.
- Numerical results carry an explicit tolerance; near-zero is never
  silently treated as exact zero.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable
import uuid


class FeasibilityState(Enum):
    VALID = "valid"
    INVALID = "invalid"
    UNRESOLVED = "unresolved"
    NOT_APPLICABLE = "not_applicable"


class CorrespondenceType(Enum):
    REPRESENTATION_MATCH = "representation_match"
    ISOMORPHISM = "isomorphism"
    HOMEOMORPHISM = "homeomorphism"
    ALGEBRAIC_EQUIVALENCE = "algebraic_equivalence"
    STRUCTURAL_CORRESPONDENCE = "structural_correspondence"
    APPROXIMATE_SIMILARITY = "approximate_similarity"
    UNRESOLVED = "unresolved"


class EvidenceStatus(Enum):
    OBSERVED = "observed"
    COMPUTED = "computed"
    VERIFIED = "verified"
    DERIVED = "derived"
    INFERRED = "inferred"
    CONJECTURED = "conjectured"
    REFUTED = "refuted"
    UNRESOLVED = "unresolved"


@dataclass
class NumericResult:
    value: float
    exact: bool
    tolerance: float | None = None

    def is_effectively_zero(self) -> bool:
        if self.exact:
            return self.value == 0
        if self.tolerance is None:
            raise ValueError("Cannot judge near-zero without an explicit tolerance")
        return abs(self.value) < self.tolerance


@dataclass
class Representation:
    representation_id: str
    domain: str
    kind: str
    data: Any
    transformation_group: str | None = None


@dataclass
class Constraint:
    name: str
    predicate: Callable[[Representation], bool | None]


@dataclass
class StructuralSignature:
    signature_id: str
    representation_id: str
    invariants: dict[str, Any]
    feasibility: dict[str, FeasibilityState]
    provenance_note: str


@dataclass
class RelationalClaim:
    claim_id: str
    subject_id: str
    object_id: str
    correspondence_type: CorrespondenceType
    criterion: str
    evidence_status: EvidenceStatus
    independent_sources: int = 1


class StructuralDiscoveryCore:
    def __init__(self, mmi_adapter=None):
        self.mmi_adapter = mmi_adapter
        self.representations: dict[str, Representation] = {}
        self.signatures: dict[str, StructuralSignature] = {}
        self.claims: list[RelationalClaim] = []

    def register_representation(self, domain: str, kind: str, data: Any,
                                 transformation_group: str | None = None) -> Representation:
        rep = Representation(
            representation_id=str(uuid.uuid4()),
            domain=domain, kind=kind, data=data,
            transformation_group=transformation_group,
        )
        self.representations[rep.representation_id] = rep
        return rep

    def evaluate_constraints(self, rep: Representation,
                              constraints: list[Constraint]) -> dict[str, FeasibilityState]:
        results = {}
        for c in constraints:
            outcome = c.predicate(rep)
            if outcome is None:
                results[c.name] = FeasibilityState.UNRESOLVED
            elif outcome is True:
                results[c.name] = FeasibilityState.VALID
            elif outcome is False:
                results[c.name] = FeasibilityState.INVALID
            else:
                raise TypeError(
                    f"Constraint '{c.name}' predicate must return True/False/None, got {outcome!r}"
                )
        return results

    def compute_signature(self, rep: Representation,
                           invariant_fns: dict[str, Callable[[Representation], Any]],
                           constraints: list[Constraint]) -> StructuralSignature:
        invariants = {}
        for name, fn in invariant_fns.items():
            try:
                invariants[name] = fn(rep)
            except Exception as e:
                invariants[name] = f"UNRESOLVED: {e}"
        feasibility = self.evaluate_constraints(rep, constraints)
        sig = StructuralSignature(
            signature_id=str(uuid.uuid4()),
            representation_id=rep.representation_id,
            invariants=invariants,
            feasibility=feasibility,
            provenance_note=f"transformation_group={rep.transformation_group or 'UNSPECIFIED'}",
        )
        self.signatures[sig.signature_id] = sig
        return sig

    def claim_correspondence(self, rep_a: Representation, rep_b: Representation,
                              correspondence_type: CorrespondenceType,
                              criterion: str,
                              test_fn: Callable[[Representation, Representation], bool | None]
                              ) -> RelationalClaim:
        result = test_fn(rep_a, rep_b)
        if result is None:
            final_type = CorrespondenceType.UNRESOLVED
            evidence = EvidenceStatus.UNRESOLVED
        elif result is True:
            final_type = correspondence_type
            evidence = EvidenceStatus.COMPUTED
        else:
            final_type = CorrespondenceType.UNRESOLVED
            evidence = EvidenceStatus.REFUTED

        claim = RelationalClaim(
            claim_id=str(uuid.uuid4()),
            subject_id=rep_a.representation_id,
            object_id=rep_b.representation_id,
            correspondence_type=final_type,
            criterion=criterion,
            evidence_status=evidence,
        )
        self.claims.append(claim)

        if self.mmi_adapter is not None:
            self.mmi_adapter.evidence_record(
                claim={"claim_id": claim.claim_id, "type": final_type.value,
                       "criterion": criterion},
                status=evidence.value,
            )
        return claim
