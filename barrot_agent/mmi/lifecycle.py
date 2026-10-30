"""Pure deterministic MMI V1 execution-state evaluation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .contracts import MMIExecutionState, ParsabilityState


@dataclass(frozen=True)
class MMIEvaluationInput:
    authorized: bool
    acquired: bool
    parse_states: tuple[ParsabilityState, ...]
    protocol_requirements_met: bool
    unresolved_gaps: tuple[str, ...] = ()
    has_conflicts: bool = False
    reconciled: bool = False
    learning_accepted: bool = False
    stale: bool = False
    unavailable: bool = False
    in_scope: bool = True


@dataclass(frozen=True)
class MMIEvaluation:
    state: MMIExecutionState
    protocol_complete: bool
    knowledge_complete: bool
    reasons: tuple[str, ...]


def evaluate_mmi_state(data: MMIEvaluationInput) -> MMIEvaluation:
    """Evaluate from explicit facts only; no model-generated transition decisions."""
    if not data.in_scope:
        return MMIEvaluation(MMIExecutionState.NOT_IN_SCOPE, False, False, ("target excluded by declared scope",))
    if not data.authorized:
        return MMIEvaluation(MMIExecutionState.BLOCKED, False, False, ("acquisition not authorized",))
    if data.unavailable:
        return MMIEvaluation(MMIExecutionState.UNAVAILABLE, False, False, ("required source unavailable",))
    if data.stale:
        return MMIEvaluation(MMIExecutionState.STALE, False, False, ("evidence freshness expired",))
    if not data.acquired:
        return MMIEvaluation(MMIExecutionState.AUTHORIZED, False, False, ("acquisition not completed",))

    if not data.parse_states:
        return MMIEvaluation(MMIExecutionState.ACQUIRED, False, False, ("no parser results recorded",))
    if any(state in {ParsabilityState.MALFORMED, ParsabilityState.EMPTY, ParsabilityState.UNAVAILABLE} for state in data.parse_states):
        return MMIEvaluation(MMIExecutionState.FAILED, False, False, ("one or more required parser results are unusable",))

    parse_complete = all(state == ParsabilityState.COMPLETE for state in data.parse_states)
    protocol_complete = parse_complete and data.protocol_requirements_met
    if not protocol_complete:
        return MMIEvaluation(MMIExecutionState.PARTIAL, False, False, ("parsing or protocol requirements incomplete",))

    if data.has_conflicts and not data.reconciled:
        return MMIEvaluation(MMIExecutionState.DISPUTED, True, False, ("contradictions preserved; reconciliation pending",))
    if data.unresolved_gaps:
        state = MMIExecutionState.RECONCILED if data.reconciled else MMIExecutionState.CORROBORATED
        return MMIEvaluation(state, True, False, ("knowledge gaps remain", *data.unresolved_gaps))
    if not data.learning_accepted:
        return MMIEvaluation(MMIExecutionState.RECONCILED if data.reconciled else MMIExecutionState.CORROBORATED, True, True, ("knowledge coverage complete; learning acceptance pending",))
    return MMIEvaluation(MMIExecutionState.ACCEPTED, True, True, ())


def aggregate_protocol_completeness(states: Iterable[ParsabilityState]) -> bool:
    """Convenience predicate; empty input is never complete."""
    values = tuple(states)
    return bool(values) and all(value is ParsabilityState.COMPLETE for value in values)
