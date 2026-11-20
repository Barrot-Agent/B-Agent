"""Evidence-gated decisions for GitHub-style merge conflict choices.

This module recommends a resolution; it never edits a repository or merges a PR.
The UI labels are normalized as:
- current: the target/base branch version
- incoming: the PR/source branch version
- both: a reviewed composition of both versions
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Optional


class ResolutionChoice(str, Enum):
    CURRENT = "current"
    INCOMING = "incoming"
    BOTH = "both"
    MANUAL = "manual"


@dataclass(frozen=True)
class ConflictEvidence:
    """Facts established by inspection, not assumptions.

    Defaults are deliberately false so missing evidence cannot authorize a
    destructive one-sided choice.
    """

    conflict_type: str = "content"
    incoming_is_intended_pr_change: bool = False
    incoming_preserves_current_behavior: bool = False
    incoming_is_validated: bool = False
    tests_pass: bool = False
    current_is_authoritative: bool = False
    incoming_is_superseded_or_invalid: bool = False
    both_changes_are_required: bool = False
    both_changes_are_compatible: bool = False
    composition_is_validated: bool = False
    protected_area_reviewed: bool = False
    security_or_data_loss_risk: bool = False
    evidence_summary: str = ""


@dataclass(frozen=True)
class ResolutionDecision:
    choice: ResolutionChoice
    auto_apply: bool
    confidence: float
    rationale: str
    required_checks: tuple[str, ...]
    evidence: dict


HIGH_RISK_TYPES = {
    "binary", "rename", "delete_modify", "submodule", "generated",
    "lockfile", "migration", "security", "permissions", "workflow",
    "deployment", "secret", "database",
}


def recommend_resolution(evidence: ConflictEvidence) -> ResolutionDecision:
    """Return a conservative recommendation from explicit evidence.

    Incoming is the contextual default for an intended PR improvement, but
    never wins solely because it is incoming or because Barrot authored it.
    """
    kind = evidence.conflict_type.strip().lower().replace("-", "_")
    checks = (
        "compare base, current, and incoming versions",
        "identify behavior and invariants changed on each side",
        "run relevant tests and inspect the final diff",
    )

    if kind in HIGH_RISK_TYPES or evidence.security_or_data_loss_risk:
        return ResolutionDecision(
            ResolutionChoice.MANUAL, False, 0.0,
            "High-risk conflict: require explicit semantic review; do not choose a side automatically.",
            checks + ("obtain maintainer approval for the resolved result",),
            asdict(evidence),
        )

    if evidence.current_is_authoritative and evidence.incoming_is_superseded_or_invalid:
        return ResolutionDecision(
            ResolutionChoice.CURRENT, False, 0.95,
            "Evidence identifies the current version as authoritative and the incoming change as superseded or invalid.",
            checks, asdict(evidence),
        )

    if (
        evidence.both_changes_are_required
        and evidence.both_changes_are_compatible
        and evidence.composition_is_validated
        and evidence.tests_pass
        and evidence.protected_area_reviewed
    ):
        return ResolutionDecision(
            ResolutionChoice.BOTH, False, 0.90,
            "Both changes are required and validated; this is a recommendation only. Explicit human authorization is required before applying it.",
            checks, asdict(evidence),
        )

    if (
        evidence.incoming_is_intended_pr_change
        and evidence.incoming_preserves_current_behavior
        and evidence.incoming_is_validated
        and evidence.tests_pass
        and evidence.protected_area_reviewed
    ):
        return ResolutionDecision(
            ResolutionChoice.INCOMING, False, 0.90,
            "Incoming is the intended PR improvement and passed validation; this is a recommendation only. Explicit human authorization is required before applying it.",
            checks, asdict(evidence),
        )

    if evidence.current_is_authoritative:
        return ResolutionDecision(
            ResolutionChoice.CURRENT, False, 0.75,
            "Current is marked authoritative, but the evidence is insufficient for automatic application.",
            checks, asdict(evidence),
        )

    return ResolutionDecision(
        ResolutionChoice.MANUAL, False, 0.0,
        "Insufficient evidence to discard either side or safely combine them. Stop and request semantic review.",
        checks + ("record why current, incoming, or both is correct before resolving",),
        asdict(evidence),
    )


def decision_as_dict(evidence: ConflictEvidence) -> dict:
    """JSON-friendly decision payload for Barrot orchestration and audit logs."""
    decision = recommend_resolution(evidence)
    result = asdict(decision)
    result["choice"] = decision.choice.value
    return result
