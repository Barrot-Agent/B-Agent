"""Governed capability routing, evaluation, and continual improvement.

This module deliberately keeps model providers interchangeable.  It records
what was used, evaluates outputs against explicit criteria, and only promotes
versioned updates when safety and regression gates pass.
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence


class Capability(str, Enum):
    REASONING = "reasoning"
    CODING = "coding"
    VISION = "vision"
    AUDIO = "audio"
    RESEARCH = "research"
    PLANNING = "planning"
    TOOL_USE = "tool_use"


@dataclass(frozen=True)
class BenchmarkCase:
    """A repeatable capability check with a measurable acceptance threshold."""

    case_id: str
    capability: Capability
    prompt: str
    required_terms: tuple[str, ...] = ()
    min_score: float = 0.7


DEFAULT_BENCHMARKS: tuple[BenchmarkCase, ...] = tuple(
    BenchmarkCase(f"{capability.value}-baseline", capability, f"baseline {capability.value}")
    for capability in Capability
)


@dataclass(frozen=True)
class ModelCandidate:
    """A provider endpoint; no model weights or proprietary data are copied."""

    model_id: str
    capabilities: frozenset[Capability]
    invoke: Callable[[str], str]
    license: str = "unknown"
    provenance: str = ""


@dataclass(frozen=True)
class CandidateResult:
    model_id: str
    output: str
    score: float
    license: str
    provenance: str


@dataclass(frozen=True)
class RouteDecision:
    capability: Capability
    selected: CandidateResult
    alternatives: tuple[CandidateResult, ...] = ()


class SafetyError(ValueError):
    """Raised when a proposed update fails a promotion gate."""


@dataclass(frozen=True)
class GovernancePolicy:
    """Boundaries for external data, tools, and self-improvement."""

    allowed_licenses: frozenset[str] = frozenset({"Apache-2.0", "MIT", "BSD-3-Clause"})
    require_provenance: bool = True
    require_human_approval: bool = True
    allow_personal_data: bool = False
    max_prompt_chars: int = 20_000
    max_output_chars: int = 50_000
    max_candidates: int = 5
    min_regression_score: float = 0.7
    min_safety_score: float = 0.9

    def validate_external_data(
        self, *, license: str, provenance: str, contains_personal_data: bool = False
    ) -> None:
        """Validate data before it enters routing, memory, or learning."""

        if license not in self.allowed_licenses:
            raise SafetyError(f"license is not allowed: {license}")
        if self.require_provenance and not provenance:
            raise SafetyError("external data requires provenance")
        if contains_personal_data and not self.allow_personal_data:
            raise SafetyError("personal data is disabled by policy")


@dataclass(frozen=True)
class Evaluation:
    score: float
    safety_score: float
    regression_score: float
    red_team_score: float = 1.0
    findings: tuple[str, ...] = ()

    def is_promotable(self, policy: GovernancePolicy | None = None) -> bool:
        policy = policy or GovernancePolicy()
        return (
            self.safety_score >= policy.min_safety_score
            and self.regression_score >= policy.min_regression_score
            and self.red_team_score >= policy.min_safety_score
        )


def inventory_components() -> dict[str, tuple[str, ...]]:
    """Return the current subsystem inventory used by the framework."""

    return {
        "inference": ("barrot_agent.inference.InferencePipeline",),
        "orchestration": (
            "barrot_agent.orchestration.mcp_orchestrator",
            "barrot_agent.upgrade_flywheel.UpgradeFlywheel",
        ),
        "ingestion": ("barrot_agent.ingestion",),
        "memory": ("barrot_agent.mem_palace", "data.registry"),
        "mcp": ("barrot_agent.mcp_discovery", "barrot_agent.mcp_approval"),
        "benchmarking": ("tests", "scripts/self_benchmark.py"),
        "upgrade": ("barrot_agent.upgrade_flywheel", "barrot_agent.reconfiguration"),
    }


class CapabilityRouter:
    """Route requests and select outputs using an injected evaluator."""

    def __init__(
        self,
        candidates: Iterable[ModelCandidate],
        *,
        evaluator: Callable[[str, str], float] | None = None,
        policy: GovernancePolicy | None = None,
    ) -> None:
        self.policy = policy or GovernancePolicy()
        self.candidates = tuple(candidates)
        self._evaluator = evaluator or self._default_evaluator

    def route(self, capability: Capability, prompt: str) -> RouteDecision:
        if not prompt:
            raise ValueError("prompt must not be empty")
        if len(prompt) > self.policy.max_prompt_chars:
            raise ValueError(
                f"prompt length {len(prompt)} exceeds the configured resource limit "
                f"of {self.policy.max_prompt_chars}"
            )
        eligible = [c for c in self.candidates if capability in c.capabilities]
        if len(eligible) > self.policy.max_candidates:
            eligible = eligible[: self.policy.max_candidates]
        if not eligible:
            raise LookupError(f"no candidate supports {capability.value}")
        results = tuple(self._evaluate(capability, prompt, candidate) for candidate in eligible)
        ordered = tuple(sorted(results, key=lambda result: result.score, reverse=True))
        return RouteDecision(capability, ordered[0], ordered[1:])

    def _evaluate(
        self, capability: Capability, prompt: str, candidate: ModelCandidate
    ) -> CandidateResult:
        if self.policy.require_provenance and not candidate.provenance:
            raise SafetyError(f"candidate {candidate.model_id} has no provenance")
        if candidate.license not in self.policy.allowed_licenses:
            raise SafetyError(f"license for {candidate.model_id} is not allowed")
        output = candidate.invoke(prompt)
        if len(output) > self.policy.max_output_chars:
            raise SafetyError("candidate output exceeds the configured resource limit")
        return CandidateResult(
            candidate.model_id,
            output,
            max(0.0, min(1.0, self._evaluator(prompt, output))),
            candidate.license,
            candidate.provenance,
        )

    @staticmethod
    def _default_evaluator(prompt: str, output: str) -> float:
        """Conservative baseline: non-empty, bounded outputs receive partial credit."""

        if not output.strip():
            return 0.0
        return min(1.0, len(output.strip()) / max(1, len(prompt.strip())))


def evaluate_benchmark(
    case: BenchmarkCase, output: str, *, safety_score: float = 1.0
) -> Evaluation:
    """Score a benchmark output without treating fluency as correctness."""

    normalized = output.casefold()
    matched = sum(term.casefold() in normalized for term in case.required_terms)
    term_score = matched / len(case.required_terms) if case.required_terms else 1.0
    score = min(1.0, term_score if case.required_terms else (1.0 if output.strip() else 0.0))
    return Evaluation(
        score=score,
        safety_score=max(0.0, min(1.0, safety_score)),
        regression_score=score,
        findings=() if score >= case.min_score else (f"below threshold for {case.case_id}",),
    )


@dataclass(frozen=True)
class LearningProposal:
    proposal_id: str
    parent_version: str
    changes: Mapping[str, str]
    evaluation: Evaluation
    approved: bool = False
    created_at: float = field(default_factory=time.time)


class ContinualLearningStore:
    """Append-only feedback store with explicit promotion and rollback."""

    def __init__(self, path: Path | str, policy: GovernancePolicy | None = None) -> None:
        self.path = Path(path)
        self.policy = policy or GovernancePolicy()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record_feedback(self, *, task: str, reward: float, notes: str = "") -> None:
        self._append({"type": "feedback", "task": task, "reward": reward, "notes": notes})

    def propose(
        self,
        *,
        parent_version: str,
        changes: Mapping[str, str],
        evaluation: Evaluation,
        human_approved: bool = False,
    ) -> LearningProposal:
        proposal = LearningProposal(
            str(uuid.uuid4()),
            parent_version,
            dict(changes),
            evaluation,
            approved=human_approved,
        )
        if not evaluation.is_promotable(self.policy):
            raise SafetyError("proposal failed safety or regression gates")
        if not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in changes.items()
        ):
            raise TypeError("learning changes must be a string-to-string mapping")
        if not human_approved:
            raise SafetyError("human approval is required before promotion")
        self._append({"type": "proposal", **asdict(proposal)})
        return proposal

    def rollback(self, version: str, reason: str) -> None:
        if not version or not reason:
            raise ValueError("rollback requires a version and reason")
        self._append({"type": "rollback", "version": version, "reason": reason})

    def _append(self, record: Mapping[str, object]) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(dict(record), default=str) + "\n")
