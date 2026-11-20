"""Evidence-gated decisions for GitHub-style merge conflict choices.

This module recommends a resolution only. It never applies a choice, edits a
repository, approves a pull request, merges, pushes, or deploys.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum


class ResolutionChoice(str, Enum):
    CURRENT = "current"
    INCOMING = "incoming"
    BOTH = "both"
    MANUAL = "manual"


@dataclass(frozen=True)
class ConflictEvidence:
    """Facts established by inspection. Missing evidence always fails closed."""

    conflict_type: str = "content"
    file_path: str = ""
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
    # Compatibility field; this policy never authorizes automatic application.
    auto_apply: bool
    confidence: float
    rationale: str
    required_checks: tuple[str, ...]
    evidence: dict


HIGH_RISK_TYPES = {
    "binary", "rename", "delete_modify", "submodule", "generated",
    "lockfile", "migration", "security", "permissions", "workflow",
    "deployment", "secret", "database", "authentication", "authorization",
}
HIGH_RISK_PATH_PARTS = {
    "secrets", "credentials", "migrations", "terraform", "infrastructure",
    "deploy", "deployment", "auth", "security", "permissions",
}
HIGH_RISK_FILENAMES = {
    "codeowners", ".gitmodules", "dockerfile", "docker-compose.yml",
    "docker-compose.yaml", "poetry.lock", "pipfile.lock", "cargo.lock",
    "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
}


def _is_high_risk_path(file_path: str) -> bool:
    normalized = file_path.replace("\\", "/").strip("/").lower()
    if not normalized:
        return False
    parts = normalized.split("/")
    filename = parts[-1]
    if filename in HIGH_RISK_FILENAMES:
        return True
    if filename.startswith(("auth", "security", "permission", "secret", "credential")):
        return True
    if normalized.startswith((".github/workflows/", ".github/actions/")):
        return True
    if normalized == ".github/codeowners" or filename == "codeowners":
        return True
    if any(part in HIGH_RISK_PATH_PARTS for part in parts[:-1]):
        return True
    if filename == ".env" or filename.startswith(".env."):
        return True
    return filename.endswith((".lock", ".sql"))


def recommend_resolution(evidence: ConflictEvidence) -> ResolutionDecision:
    """Recommend a choice from explicit evidence; never authorize applying it."""
    kind = (
        evidence.conflict_type.strip().lower()
        .replace("-", "_").replace("/", "_").replace(" ", "_")
    )
    checks = (
        "compare merge base, current, and incoming versions",
        "identify behavior and invariants changed on each side",
        "inspect the complete proposed result and its diff",
        "run relevant tests against the exact candidate result",
    )
    if (
        kind in HIGH_RISK_TYPES
        or evidence.security_or_data_loss_risk
        or _is_high_risk_path(evidence.file_path)
    ):
        return ResolutionDecision(
            ResolutionChoice.MANUAL, False, 0.0,
            "High-risk conflict or protected path: require explicit semantic review; no side may be selected automatically.",
            checks + ("obtain explicit maintainer authorization for the resolved result",),
            asdict(evidence),
        )
    if evidence.current_is_authoritative and evidence.incoming_is_superseded_or_invalid:
        return ResolutionDecision(
            ResolutionChoice.CURRENT, False, 0.95,
            "Evidence identifies current as authoritative and incoming as superseded or invalid; human authorization is still required.",
            checks + ("obtain explicit human authorization before retaining current",),
            asdict(evidence),
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
            "Both changes are required, compatibility was reviewed, and the composed result passed validation. Human authorization is still required.",
            checks + ("obtain explicit human authorization before applying the composition",),
            asdict(evidence),
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
            "Incoming is the intended improvement; existing behavior was preserved and the result was reviewed and tested. Human authorization is still required.",
            checks + ("obtain explicit human authorization before applying incoming",),
            asdict(evidence),
        )
    if evidence.current_is_authoritative:
        return ResolutionDecision(
            ResolutionChoice.CURRENT, False, 0.75,
            "Current is marked authoritative, but evidence is insufficient for automatic application. Human authorization is required.",
            checks + ("obtain explicit human authorization before retaining current",),
            asdict(evidence),
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
