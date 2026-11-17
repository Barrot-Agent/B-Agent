"""Truth and evidence states for Barrot geometry claims.

Truth is kept to exactly four states: VALID / INVALID / UNRESOLVED /
NOT_APPLICABLE. A contradiction is carried as a flag on ``ConstraintResult``,
not as a fifth state, so an unknown input can never be promoted to a verdict.

Evidence uses eight independent epistemic states. ``VERIFIED`` is only
reachable through a verification record; ``REFUTED`` only through evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TruthState(str, Enum):
    """The four permitted truth states. Do not add a fifth."""

    VALID = "VALID"
    INVALID = "INVALID"
    UNRESOLVED = "UNRESOLVED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


#: Higher wins when combining. A definite failure outranks missing evidence;
#: a positive claim never outranks missing evidence.
_PRECEDENCE = {
    TruthState.INVALID: 3,
    TruthState.UNRESOLVED: 2,
    TruthState.VALID: 1,
    TruthState.NOT_APPLICABLE: 0,
}


def combine(*states: TruthState) -> TruthState:
    """Combine independent checks into one state.

    INVALID dominates; UNRESOLVED dominates VALID; NOT_APPLICABLE is inert
    unless nothing else is present. ``combine()`` with no checks is
    NOT_APPLICABLE, never VALID.
    """
    if not states:
        return TruthState.NOT_APPLICABLE
    for state in states:
        if not isinstance(state, TruthState):
            raise TypeError(f"expected TruthState, got {type(state).__name__}")
    return max(states, key=lambda state: _PRECEDENCE[state])


@dataclass(frozen=True)
class ConstraintResult:
    """Outcome of one constraint evaluation.

    ``contradictory`` is true only when both satisfaction and violation have
    evidence. The state stays UNRESOLVED: conflicting evidence is not a
    verdict, and it must not be reported as INVALID.
    """

    state: TruthState
    contradictory: bool = False
    reason: str = ""


def evaluate_constraint(
    *,
    satisfied: bool | None,
    violated: bool | None,
    applicable: bool = True,
    reason: str = "",
) -> ConstraintResult:
    """Evaluate one explicit constraint from supplied evidence.

    ``None`` means "no evidence", not "false". No evidence yields
    UNRESOLVED, never INVALID.
    """
    if not applicable:
        return ConstraintResult(
            TruthState.NOT_APPLICABLE, False, reason or "constraint does not apply"
        )
    if satisfied and violated:
        return ConstraintResult(
            TruthState.UNRESOLVED,
            True,
            reason or "satisfied and violated evidence both present",
        )
    if violated:
        return ConstraintResult(TruthState.INVALID, False, reason or "constraint violated")
    if satisfied:
        return ConstraintResult(TruthState.VALID, False, reason or "constraint satisfied")
    return ConstraintResult(
        TruthState.UNRESOLVED, False, reason or "insufficient evidence"
    )


class EvidenceState(str, Enum):
    """Eight epistemic states. Not a ladder: order carries no meaning."""

    OBSERVED = "OBSERVED"
    COMPUTED = "COMPUTED"
    VERIFIED = "VERIFIED"
    DERIVED = "DERIVED"
    INFERRED = "INFERRED"
    CONJECTURED = "CONJECTURED"
    REFUTED = "REFUTED"
    UNRESOLVED = "UNRESOLVED"


#: Mapping from the existing MMI contract vocabulary. Kept explicit so a
#: change in another module cannot silently change this one.
_FROM_MMI_EVIDENCE = {
    "OBSERVED": EvidenceState.OBSERVED,
    "PARSED": EvidenceState.COMPUTED,
    "DERIVED": EvidenceState.DERIVED,
    "INFERRED": EvidenceState.INFERRED,
    "UNKNOWN": EvidenceState.UNRESOLVED,
    "NOT_PARSABLE": EvidenceState.UNRESOLVED,
    "NOT_APPLICABLE": EvidenceState.UNRESOLVED,
}

_FROM_PARSE_STATE = {
    "OBSERVED": EvidenceState.OBSERVED,
    "PARSED": EvidenceState.COMPUTED,
    "DERIVED": EvidenceState.DERIVED,
    "INFERRED": EvidenceState.INFERRED,
    "HYPOTHESIZED": EvidenceState.CONJECTURED,
    "PROPOSED": EvidenceState.CONJECTURED,
    "UNKNOWN": EvidenceState.UNRESOLVED,
    "NOT_PARSABLE": EvidenceState.UNRESOLVED,
    "NOT_PRESENT": EvidenceState.UNRESOLVED,
}

_FROM_STAGE_STATUS = {
    "COMPLETE": TruthState.VALID,
    "PARTIAL": TruthState.UNRESOLVED,
    "BLOCKED": TruthState.UNRESOLVED,
    "UNKNOWN": TruthState.UNRESOLVED,
    "NOT_APPLICABLE": TruthState.NOT_APPLICABLE,
}


def _lookup(table: dict[str, EvidenceState], value: object, label: str) -> EvidenceState:
    key = getattr(value, "value", value)
    try:
        return table[str(key)]
    except KeyError:
        raise ValueError(f"unknown {label}: {key!r}") from None


def from_mmi_evidence(value: object) -> EvidenceState:
    """Map ``mmi_contract.EvidenceState`` (or its value) into this vocabulary."""
    return _lookup(_FROM_MMI_EVIDENCE, value, "MMI evidence state")


def from_parse_state(value: object) -> EvidenceState:
    """Map ``mmi_v1.ParseState`` (or its value) into this vocabulary."""
    return _lookup(_FROM_PARSE_STATE, value, "parse state")


def from_stage_status(value: object) -> TruthState:
    """Map an MMI stage status into a truth state."""
    key = getattr(value, "value", value)
    try:
        return _FROM_STAGE_STATUS[str(key)]
    except KeyError:
        raise ValueError(f"unknown stage status: {key!r}") from None


def verified_evidence(record: str | None) -> EvidenceState:
    """VERIFIED requires a verification record; otherwise UNRESOLVED."""
    return EvidenceState.VERIFIED if record else EvidenceState.UNRESOLVED


def refuted_evidence(evidence: str | None) -> EvidenceState:
    """REFUTED requires contradicting evidence; otherwise UNRESOLVED."""
    return EvidenceState.REFUTED if evidence else EvidenceState.UNRESOLVED
