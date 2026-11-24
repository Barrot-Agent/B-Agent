"""Recursive Query Transmutation Protocol: bounded, deterministic, read-only.

This module extends the existing inbound authority gate; it does not replace or
duplicate it. ``barrot_agent.inbound.gate`` remains the primitive that extracts a
requirement, six gap categories, conflicts, a bounded refinement, and a policy
verdict. This module adds the stages the gate deliberately omits:

    domain expansion          which connected investigations this request implies
    capability discovery      what already exists, with file-level evidence
    hypothesis ranking        competing explanations and their falsifiers
    budget                    depth, iterations, parallelism, questions, clock
    stop states               the nine explicit terminal states
    durable records           immutable original + append-only hash-linked journal
    recovery                  reload the record and its next checkpoint

The protocol never executes an action. ``execution_mode`` is always
``READ_ONLY_PLAN``; ``decision`` only authorises a bounded investigation.

Record schema: the seventeen charter fields plus three justified extensions,
``protocol_version``, ``received_at``, and ``subquestions``, which are required to
version a record, recover it after process restart, and expose the derived
investigation without parsing prose.

No network imports. No subprocess. No writes outside the record directory.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .gate import Command, Severity, Source, gate as inbound_gate, scan

PROTOCOL_VERSION = "1.0"
DEFAULT_RECORD_DIR = Path("results") / "transmutation"
EXECUTION_MODE = "READ_ONLY_PLAN"

# A request that trips these rules is denied and its raw text is never written to
# disk. The hash is still recorded, so the rejection is auditable without copying
# the credential material into a record.
SENSITIVE_CODES = frozenset({"SECRET_READ", "SEED_PHRASE"})

# Hard maxima. A caller may ask for more; the request is clamped and the clamp is
# recorded, mirroring the gate's refusal to hide a silent cap.
HARD_MAX_DEPTH = 4
HARD_MAX_ITERATIONS = 12
HARD_MAX_PARALLEL = 4
HARD_MAX_QUESTIONS = 32
HARD_MAX_HYPOTHESES = 16
HARD_MAX_WALL_CLOCK = 300.0
HARD_MAX_RETRIES = 3

JOURNAL_TAIL_BYTES = 65536


class StopState(str, Enum):
    """Explicit terminal states. ``None`` means an authorised continuation point."""

    SUCCESS_VALIDATED = "SUCCESS_VALIDATED"
    SUCCESS_WITH_LIMITATIONS = "SUCCESS_WITH_LIMITATIONS"
    NO_MEANINGFUL_IMPROVEMENT = "NO_MEANINGFUL_IMPROVEMENT"
    INCONCLUSIVE = "INCONCLUSIVE"
    BLOCKED_DEPENDENCY = "BLOCKED_DEPENDENCY"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    AUTHORIZATION_REQUIRED = "AUTHORIZATION_REQUIRED"
    SAFETY_ABORT = "SAFETY_ABORT"
    FAILED_REPRODUCIBLY = "FAILED_REPRODUCIBLY"


class CapabilityStatus(str, Enum):
    IMPLEMENTED_AND_VERIFIED = "IMPLEMENTED AND VERIFIED"
    IMPLEMENTED_NOT_VERIFIED = "IMPLEMENTED BUT NOT VERIFIED"
    PARTIALLY_IMPLEMENTED = "PARTIALLY IMPLEMENTED"
    DOCUMENTED_ONLY = "DOCUMENTED ONLY"
    DESIGNED_ONLY = "DESIGNED ONLY"
    MISSING = "MISSING"
    SUPERSEDED = "SUPERSEDED"


class TransmutationError(ValueError):
    """Raised when a request cannot be preserved or a record is inconsistent."""


class TransmutationConflict(TransmutationError):
    """Raised when a request id already exists with a different request hash."""


@dataclass(frozen=True)
class Budget:
    """Resource ceiling for one transmutation and any bounded continuation."""

    max_depth: int = 2
    max_iterations: int = 6
    max_parallel: int = 1
    max_questions: int = 16
    max_hypotheses: int = 8
    wall_clock_seconds: float = 30.0
    max_retries: int = 1

    def validated(self) -> tuple["Budget", tuple[str, ...]]:
        """Return a hard-capped budget and the names of every clamped field."""
        values = {
            "max_depth": (self.max_depth, HARD_MAX_DEPTH, int),
            "max_iterations": (self.max_iterations, HARD_MAX_ITERATIONS, int),
            "max_parallel": (self.max_parallel, HARD_MAX_PARALLEL, int),
            "max_questions": (self.max_questions, HARD_MAX_QUESTIONS, int),
            "max_hypotheses": (self.max_hypotheses, HARD_MAX_HYPOTHESES, int),
            "wall_clock_seconds": (
                self.wall_clock_seconds,
                HARD_MAX_WALL_CLOCK,
                float,
            ),
            "max_retries": (self.max_retries, HARD_MAX_RETRIES, int),
        }
        clamped: list[str] = []
        resolved: dict[str, Any] = {}
        for name, (requested, ceiling, kind) in values.items():
            if requested < 0:
                raise TransmutationError(f"{name} cannot be negative")
            value = min(requested, ceiling)
            if value != requested:
                clamped.append(name)
            resolved[name] = kind(value)
        return Budget(**resolved), tuple(clamped)

    def as_dict(self) -> dict[str, Any]:
        return {
            "max_depth": self.max_depth,
            "max_iterations": self.max_iterations,
            "max_parallel": self.max_parallel,
            "max_questions": self.max_questions,
            "max_hypotheses": self.max_hypotheses,
            "wall_clock_seconds": self.wall_clock_seconds,
            "max_retries": self.max_retries,
        }


@dataclass(frozen=True)
class Domain:
    key: str
    title: str
    triggers: tuple[str, ...]
    why: str
    subquestions: tuple[str, ...]
    capabilities: tuple[str, ...]
    baseline: bool = False

    def score(self, text: str) -> tuple[int, tuple[str, ...]]:
        matched: list[str] = []
        for pattern in self.triggers:
            if re.search(pattern, text, re.IGNORECASE):
                matched.append(pattern)
        return len(matched), tuple(matched)


# Capability references are declared as (name, path, test path or None, kind).
CAPABILITIES: tuple[tuple[str, str, str | None, str], ...] = (
    ("inbound_gate", "barrot_agent/inbound/gate.py", "tests/test_gpt_api.py", "code"),
    (
        "query_transmutation_protocol",
        "barrot_agent/inbound/transmutation.py",
        "tests/test_inbound_transmutation.py",
        "code",
    ),
    ("agent_prompt_contract", ".opencode/agent/barrot.md", None, "doc"),
    ("capability_audit", "barrot_capability_audit.json", None, "data"),
    ("mmi_ledger", "barrot_agent/mmi_v1.py", "tests/test_mmi_v1.py", "code"),
    ("evidence_store", "barrot_agent/evolution/evidence_store.py", None, "code"),
    (
        "raw_receipt_archive",
        "barrot_agent/evolution/xrp_public_ingestion.py",
        None,
        "code",
    ),
    (
        "mission_registry",
        "barrot_agent/orchestration/mission_registry.py",
        None,
        "code",
    ),
    ("skill_index", "barrot_agent/skills/SKILL-INDEX.md", None, "doc"),
    (
        "durable_state",
        "barrot_agent/orchestration/shared_runtime.py",
        None,
        "code",
    ),
    (
        "autonomous_state",
        "barrot_agent/orchestration/autonomous_state.py",
        None,
        "code",
    ),
    (
        "verified_learning",
        "barrot_agent/orchestration/verified_learning_store.py",
        None,
        "code",
    ),
    ("mem_palace", "barrot_agent/mem_palace.py", None, "code"),
    ("sandbox_runner", "barrot_agent/sandbox/runner.py", "tests/test_sandbox.py", "code"),
    ("flight_recorder", "barrot_agent/flight_recorder.py", None, "code"),
    ("context_budget", "barrot_agent/context_budget.py", None, "code"),
    ("gist_memory", "barrot_agent/gist_memory.py", "tests/test_gist_memory.py", "code"),
    (
        "scientific_discovery",
        "barrot_agent/research/scientific_discovery.py",
        "tests/test_scientific_discovery.py",
        "code",
    ),
    ("apex_lattice_cycle", "apex_lattice/cycle.py", None, "code"),
    (
        "repository_repair",
        "barrot_agent/orchestration/repository_repair.py",
        "tests/test_repository_repair.py",
        "code",
    ),
    (
        "refinement_engine",
        "barrot_agent/refinement/engine.py",
        "tests/test_pingpong_refinement.py",
        "code",
    ),
    (
        "infinite_ingest_budget",
        "barrot_agent/infinite_ingest/continuous.py",
        "tests/test_infinite_ingest.py",
        "code",
    ),
    (
        "acceptance_matrix",
        ".barrot/collaboration_records/barrot_v3_acceptance_matrix.json",
        None,
        "data",
    ),
    (
        "point_in_time_features",
        "barrot_agent/evolution/point_in_time_features.py",
        "tests/test_point_in_time_features.py",
        "code",
    ),
    (
        "walk_forward",
        "barrot_agent/evolution/walk_forward.py",
        "tests/test_walk_forward.py",
        "code",
    ),
    (
        "forecast_ledger",
        "barrot_agent/evolution/forecast_ledger.py",
        "tests/test_forecast_ledger.py",
        "code",
    ),
    (
        "audio_render",
        "barrot_agent/creative/audio_render.py",
        "tests/test_musical_adapters.py",
        "code",
    ),
    (
        "musical_dna",
        "barrot_agent/creative/musical_dna.py",
        "tests/test_musical_dna.py",
        "code",
    ),
    ("midi_export", "barrot_agent/creative/midi_export.py", None, "code"),
)

DOMAINS: tuple[Domain, ...] = (
    Domain(
        key="query_transformation",
        title="Recursive reasoning and query transformation",
        triggers=(r"\btransmut", r"\brewrite\b", r"\brephrase\b", r"\brefine\b"),
        why=(
            "The request is about how an incoming request becomes an investigation; "
            "every later stage depends on this transformation."
        ),
        subquestions=(
            "Which entry point receives an ordinary request, and does it call a "
            "transmutation stage?",
            "What does the transformation add beyond restating the request?",
            "Which transformation stages exist in code, in prose only, or not at all?",
        ),
        capabilities=("inbound_gate", "query_transmutation_protocol", "agent_prompt_contract"),
        baseline=True,
    ),
    Domain(
        key="mmi_ingestion",
        title="MMI ingestion and evidence provenance",
        triggers=(r"\bevidence\b", r"\bprovenance\b", r"\bhash\b", r"\bledger\b", r"\bsource\b"),
        why=(
            "A transmuted record is only usable if the original request and every "
            "supporting artifact are hash-linked and append-only."
        ),
        subquestions=(
            "Is the exact original request stored immutably with a full SHA-256?",
            "Is every record linked to its predecessor, and is the chain verifiable?",
            "Which evidence is OBSERVED, DERIVED, or merely asserted?",
        ),
        capabilities=("mmi_ledger", "evidence_store", "raw_receipt_archive"),
        baseline=True,
    ),
    Domain(
        key="hypothesis_generation",
        title="Hypothesis generation and competing explanations",
        triggers=(r"\bwhy\b", r"\bcause\b", r"\bexplanation\b", r"\bhypothes", r"\bdiagnos"),
        why=(
            "A stop in behavior is not explained by the first plausible story; "
            "competing causes need falsifiers and a discriminating experiment."
        ),
        subquestions=(
            "What are the mutually exclusive explanations for the observed behavior?",
            "What observation would falsify each explanation?",
            "Which single read-only experiment separates the leading explanations?",
        ),
        capabilities=("scientific_discovery", "inbound_gate"),
        baseline=True,
    ),
    Domain(
        key="resource_optimization",
        title="Resource optimization and bounded expansion",
        triggers=(r"\bbudget\b", r"\bresource\b", r"\bcost\b", r"\blimit\b", r"\bconsumption\b"),
        why=(
            "Recursive expansion is only safe when depth, iterations, parallelism, "
            "and wall-clock cost have hard ceilings and visible clamping."
        ),
        subquestions=(
            "What is the hard ceiling for depth, iterations, and parallel work?",
            "How is a clamp recorded so it cannot look like success?",
            "When does expected value fall below the cost of another investigation?",
        ),
        capabilities=("context_budget", "infinite_ingest_budget"),
        baseline=True,
    ),
    Domain(
        key="failure_analysis",
        title="Failure analysis and correction learning",
        triggers=(
            r"\bstopp?ed\b",
            r"\bbroken\b",
            r"\bregress",
            r"\bfail",
            r"\bunsuccess",
            r"\brestore\b",
            r"\bmissing\b",
        ),
        why=(
            "The request asserts a capability stopped; the cause must be established "
            "from history and call paths, not from recollection."
        ),
        subquestions=(
            "What was the last change to the capability, and what exactly did it remove?",
            "Is the capability absent, uninvoked, or merely unobserved?",
            "Which negative result must be preserved so the same repair is not repeated?",
        ),
        capabilities=("flight_recorder", "repository_repair", "acceptance_matrix"),
    ),
    Domain(
        key="persistent_memory",
        title="Persistent memory and continuity",
        triggers=(
            r"\bmemory\b",
            r"\bremember\b",
            r"\bpersist",
            r"\bcheckpoint\b",
            r"\bdurable\b",
        ),
        why=(
            "A prompt rule can disappear between sessions; durable memory that still "
            "asserts it creates a false belief that the behavior is active."
        ),
        subquestions=(
            "Which durable notes assert the behavior, and do they match the live prompt?",
            "What state must survive a process restart for the record to be resumable?",
            "How is stale memory corrected without rewriting history?",
        ),
        capabilities=("durable_state", "autonomous_state", "verified_learning", "mem_palace"),
    ),
    Domain(
        key="multi_agent_orchestration",
        title="Multi-agent orchestration and invocation paths",
        triggers=(
            r"\bagent\b",
            r"\borchestrat",
            r"\bdelegate\b",
            r"\bruntime\b",
            r"\bincoming request",
            r"\bopencode\b",
        ),
        why=(
            "A capability that no authoritative entry point calls is dead code, "
            "however complete its tests are."
        ),
        subquestions=(
            "Which runtime path is authoritative for an ordinary request?",
            "Which components are reachable from that path, and which are orphaned?",
            "What is the smallest wiring change that restores reachability?",
        ),
        capabilities=("durable_state", "sandbox_runner", "flight_recorder"),
    ),
    Domain(
        key="b_aces_skills",
        title="B-ACES capability discovery and skill engineering",
        triggers=(r"\bcapabilit", r"\bskill\b", r"\breuse\b", r"\bdiscover"),
        why=(
            "Reuse must precede construction; a missing capability is only real after "
            "the existing modules, tests, and skill index have been searched."
        ),
        subquestions=(
            "Which existing module already performs this stage?",
            "Does a direct test exist, and does it prove behavior or only imports?",
            "What is the smallest extension rather than a new subsystem?",
        ),
        capabilities=("capability_audit", "mission_registry", "skill_index"),
    ),
    Domain(
        key="context_compression",
        title="Context compression and retrieval",
        triggers=(r"\bcontext\b", r"\bcompress", r"\bsummar", r"\bretriev", r"\bgist\b"),
        why=(
            "A transmuted investigation must remain retrievable after the original "
            "context is gone; compression must link back to raw evidence."
        ),
        subquestions=(
            "What compact representation links to the full raw record?",
            "Which details are lossy, and is the loss stated?",
            "Can a fresh process reconstruct the plan from the record alone?",
        ),
        capabilities=("context_budget", "gist_memory"),
    ),
    Domain(
        key="constrained_exploration",
        title="Constrained possibility exploration",
        triggers=(r"\bexplor", r"\bpossibilit", r"\bsearch space\b", r"\bbranch"),
        why=(
            "Unconstrained branching multiplies work without increasing evidence; "
            "expansion needs an explicit frontier and duplicate detection."
        ),
        subquestions=(
            "Which branches are mutually exclusive?",
            "How is a repeated branch detected before it is re-run?",
            "What frontier remains after the budget is applied?",
        ),
        capabilities=("apex_lattice_cycle", "inbound_gate"),
    ),
    Domain(
        key="adaptive_experimentation",
        title="Adaptive experimentation",
        triggers=(r"\blearn\b", r"\bexperiment\b", r"\bimprov", r"\battempt"),
        why=(
            "A failed attempt must change the next decision, not merely add a log "
            "entry; the protocol must compare outcomes against a baseline."
        ),
        subquestions=(
            "What baseline does the experiment improve on?",
            "What outcome classification is used: improvement, regression, equivalent, "
            "or inconclusive?",
            "What new hypothesis is justified by the observed outcome?",
        ),
        capabilities=("repository_repair", "refinement_engine"),
    ),
    Domain(
        key="sandbox_validation",
        title="Sandbox execution and validation",
        triggers=(r"\bsandbox\b", r"\bvalidat", r"\btest\b", r"\bverif"),
        why=(
            "The cheapest discriminating experiment should run isolated and read-only "
            "before any repository mutation."
        ),
        subquestions=(
            "What is the smallest isolated experiment that can fail?",
            "Which preconditions must hold before the experiment is meaningful?",
            "What evidence proves the experiment actually ran?",
        ),
        capabilities=("sandbox_runner", "inbound_gate"),
    ),
    Domain(
        key="xrp_intelligence",
        title="XRP intelligence and prediction evaluation",
        triggers=(
            r"\bxrp\b",
            r"\bxrpl\b",
            r"\border books?\b",
            r"\bledger\b",
            r"\betf\b",
            r"\bfunding\b",
            r"\bforecast\b",
        ),
        why=(
            "XRP requests require market, ledger, flow, and evaluation evidence with "
            "point-in-time discipline; a forecast is not authorised by a plan."
        ),
        subquestions=(
            "Which timestamped raw feeds support the claim, and what is their cutoff?",
            "Is the evaluation leakage-safe and compared against naive baselines?",
            "Are calibration, sample counts, and shadow outcomes sufficient to issue "
            "a directional forecast?",
            "What is OBSERVED market data versus DERIVED feature versus INFERRED regime?",
        ),
        capabilities=("point_in_time_features", "walk_forward", "forecast_ledger"),
    ),
    Domain(
        key="professional_audio",
        title="Professional audio production",
        triggers=(
            r"\baudio\b",
            r"\bmix(?:ing|ed)?\b",
            r"\bmaster(?:ing|ed)?\b",
            r"\bwav\b",
            r"\bbeat\b",
            r"\bcompos",
            r"\brender\b",
            r"\blicens",
        ),
        why=(
            "A successful render is a technical artifact, not an accepted production; "
            "mixing, mastering, rights, and listening acceptance are separate gates."
        ),
        subquestions=(
            "Which stages exist: composition, arrangement, render, mix, master?",
            "What technical QC proves level, peak, stereo, and format correctness?",
            "Are sample and model rights resolved, and who accepts the result?",
            "Is this a test render or a deliverable, and which gate distinguishes them?",
        ),
        capabilities=("audio_render", "musical_dna", "midi_export"),
    ),
    Domain(
        key="long_horizon_continuity",
        title="Long-horizon continuity across sessions and processes",
        triggers=(
            r"\bcontinuity\b",
            r"\bcontinue\b",
            r"\bsession\b",
            r"\brestart\b",
            r"\bresume\b",
            r"\bcheckpoint\b",
        ),
        why=(
            "Cross-session work needs immutable task identity, durable state, and "
            "duplicate suppression before another process can safely resume it."
        ),
        subquestions=(
            "What immutable identity prevents a second process from duplicating the task?",
            "Which state is durable, and which exists only in the current context?",
            "Can the next checkpoint be resumed without replaying completed work?",
        ),
        capabilities=("durable_state", "mission_registry", "autonomous_state"),
    ),
)


@dataclass(frozen=True)
class HypothesisTemplate:
    key: str
    statement: str
    falsifier: str
    experiment: str
    when_domains: tuple[str, ...]
    prior: float
    benefit: int
    testability: int
    complexity: int
    risk: int
    cost: int
    time: int

    def score(self) -> float:
        raw = 2.0 * self.prior + self.benefit + self.testability
        penalty = 1 + self.complexity + self.risk + self.cost + self.time
        return round(raw / penalty, 3)


HYPOTHESES: tuple[HypothesisTemplate, ...] = (
    HypothesisTemplate(
        key="INVOCATION_PATH_MISSING",
        statement="The capability exists but no authoritative entry point calls it.",
        falsifier="Trace the authoritative entry point and show a live call to the capability.",
        experiment="Enumerate every import and call site of the capability module.",
        when_domains=("failure_analysis", "query_transformation"),
        prior=0.30,
        benefit=5,
        testability=5,
        complexity=1,
        risk=1,
        cost=1,
        time=1,
    ),
    HypothesisTemplate(
        key="PROMPT_CONTRACT_WEAKENED",
        statement=(
            "The instruction that required the behavior was removed or reduced to a "
            "weaker line."
        ),
        falsifier="Diff the governing prompt across the change window and show the rule intact.",
        experiment="Read the prompt history for the behavior's name and diff the change window.",
        when_domains=("failure_analysis", "query_transformation"),
        prior=0.30,
        benefit=5,
        testability=5,
        complexity=1,
        risk=1,
        cost=1,
        time=1,
    ),
    HypothesisTemplate(
        key="QUARANTINE_OVERREACH",
        statement="A quarantine written for one utility suppresses a different capability by name.",
        falsifier=(
            "Show that the quarantine text is scoped to the retired utility and not "
            "the capability."
        ),
        experiment="Compare the quarantine section's stated scope with the capability it names.",
        when_domains=("failure_analysis", "query_transformation"),
        prior=0.20,
        benefit=4,
        testability=5,
        complexity=1,
        risk=1,
        cost=1,
        time=1,
    ),
    HypothesisTemplate(
        key="STALE_DURABLE_MEMORY",
        statement=(
            "Durable notes assert the behavior is active while the live prompt no "
            "longer requires it."
        ),
        falsifier="Show the durable note and the live prompt agree on the requirement.",
        experiment="Compare the memory entry against the current prompt section by section.",
        when_domains=("failure_analysis", "persistent_memory"),
        prior=0.20,
        benefit=3,
        testability=5,
        complexity=1,
        risk=1,
        cost=1,
        time=1,
    ),
    HypothesisTemplate(
        key="DISCONNECTED_STAGE",
        statement=(
            "A refinement or orchestration stage exists but is not connected to "
            "request intake."
        ),
        falsifier="Show a call path from intake through the stage to a recorded outcome.",
        experiment="Build the call graph from intake and list unreachable refinement modules.",
        when_domains=("failure_analysis", "multi_agent_orchestration"),
        prior=0.25,
        benefit=4,
        testability=4,
        complexity=2,
        risk=2,
        cost=2,
        time=2,
    ),
    HypothesisTemplate(
        key="REFINEMENT_PROVIDER_BOUND",
        statement=(
            "The refinement engine depends on a retired provider and cannot run as "
            "configured."
        ),
        falsifier="Run the engine offline with no retired provider configured.",
        experiment="Inspect provider selection and run the offline path.",
        when_domains=("failure_analysis", "adaptive_experimentation"),
        prior=0.15,
        benefit=2,
        testability=4,
        complexity=3,
        risk=3,
        cost=3,
        time=3,
    ),
    HypothesisTemplate(
        key="RECURSION_CAP_TOO_EARLY",
        statement="A recursion guard terminates the useful expansion before a fixed point.",
        falsifier="Show the guard bounds only repeated identical work and not useful expansion.",
        experiment="Read the guard and count distinct expansions it permits.",
        when_domains=("failure_analysis", "resource_optimization"),
        prior=0.15,
        benefit=1,
        testability=4,
        complexity=2,
        risk=2,
        cost=2,
        time=2,
    ),
    HypothesisTemplate(
        key="BUDGET_OR_CONTEXT_LIMIT",
        statement="A token, context, or wall-clock budget truncates the investigation.",
        falsifier="Show an untruncated record and a completed investigation under the same budget.",
        experiment="Inspect records and logs for truncation markers and budget stops.",
        when_domains=("failure_analysis", "resource_optimization"),
        prior=0.15,
        benefit=1,
        testability=3,
        complexity=2,
        risk=2,
        cost=2,
        time=2,
    ),
    HypothesisTemplate(
        key="TOOL_DISCOVERY_FAILURE",
        statement="The agent cannot discover or delegate to the tool that performs the stage.",
        falsifier="Show the tool registered and invoked successfully from the same session.",
        experiment="Inspect the tool registry and a successful invocation record.",
        when_domains=("failure_analysis", "multi_agent_orchestration"),
        prior=0.10,
        benefit=1,
        testability=3,
        complexity=3,
        risk=2,
        cost=2,
        time=2,
    ),
    HypothesisTemplate(
        key="DOCUMENTATION_ONLY",
        statement=(
            "The behavior is described in documentation but was never implemented as "
            "runtime behavior."
        ),
        falsifier="Show a runtime entry point that produces the documented artifact.",
        experiment="Search for the documented artifact's producer and its tests.",
        when_domains=("failure_analysis", "query_transformation"),
        prior=0.25,
        benefit=4,
        testability=5,
        complexity=1,
        risk=1,
        cost=1,
        time=1,
    ),
    HypothesisTemplate(
        key="XRP_LOOKAHEAD_LEAKAGE",
        statement="A feature uses information unavailable at the forecast cutoff.",
        falsifier="Rebuild features using only data timestamped before each cutoff.",
        experiment="Audit feature joins for post-cutoff timestamps.",
        when_domains=("xrp_intelligence",),
        prior=0.20,
        benefit=5,
        testability=4,
        complexity=3,
        risk=3,
        cost=3,
        time=3,
    ),
    HypothesisTemplate(
        key="XRP_INSUFFICIENT_OOS",
        statement="Out-of-sample and shadow sample counts are too small to support a forecast.",
        falsifier="Show the required sample counts with chronological separation.",
        experiment="Count eligible out-of-sample and shadow outcomes.",
        when_domains=("xrp_intelligence",),
        prior=0.25,
        benefit=5,
        testability=5,
        complexity=1,
        risk=1,
        cost=1,
        time=1,
    ),
    HypothesisTemplate(
        key="XRP_SOURCE_DEPENDENCE",
        statement="Multiple feeds are not independent, so corroboration overstates confidence.",
        falsifier="Show distinct publishers and collection paths for each corroborating source.",
        experiment="Trace each feed to its publisher and ingestion path.",
        when_domains=("xrp_intelligence",),
        prior=0.20,
        benefit=4,
        testability=4,
        complexity=2,
        risk=2,
        cost=2,
        time=2,
    ),
    HypothesisTemplate(
        key="AUDIO_RENDER_IS_NOT_ACCEPTANCE",
        statement="A successful render is being treated as a finished, accepted production.",
        falsifier="Show a listening acceptance record and a rights clearance record.",
        experiment="Compare render metrics with an acceptance checklist.",
        when_domains=("professional_audio",),
        prior=0.30,
        benefit=4,
        testability=5,
        complexity=1,
        risk=1,
        cost=1,
        time=1,
    ),
    HypothesisTemplate(
        key="AUDIO_MISSING_DSP_CHAIN",
        statement="Mixing, mastering, or technical QC stages do not exist in the pipeline.",
        falsifier="Show the DSP and QC stages invoked on a real deliverable.",
        experiment="Enumerate the audio pipeline stages and their tests.",
        when_domains=("professional_audio",),
        prior=0.30,
        benefit=4,
        testability=5,
        complexity=2,
        risk=2,
        cost=2,
        time=2,
    ),
    HypothesisTemplate(
        key="CONTINUITY_DUPLICATE_WORK",
        statement="A second process repeats work because task identity is not durable.",
        falsifier="Show two processes sharing an immutable task id and refusing the duplicate.",
        experiment="Run the same task identity from two processes and inspect the ledger.",
        when_domains=("long_horizon_continuity",),
        prior=0.25,
        benefit=5,
        testability=5,
        complexity=2,
        risk=2,
        cost=2,
        time=2,
    ),
    HypothesisTemplate(
        key="CONTINUITY_STATE_LOSS",
        statement="Checkpoint state exists only in the current context and is lost on restart.",
        falsifier="Restart the process and resume from the persisted checkpoint.",
        experiment="Kill and restart, then reload the checkpoint.",
        when_domains=("long_horizon_continuity",),
        prior=0.30,
        benefit=5,
        testability=5,
        complexity=2,
        risk=2,
        cost=2,
        time=2,
    ),
)


@dataclass
class TransmutationResult:
    record: dict[str, Any]
    record_path: Path
    duplicate: bool = False


def _canonical(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _hash(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def request_id_for(text: str) -> str:
    """Stable id derived from the exact request bytes, so duplicates are detectable."""
    return "QR-" + _sha256_text(text)[:12]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def classify_domains(text: str) -> list[dict[str, Any]]:
    """Rank connected domains by trigger evidence, with four protocol baselines."""
    ranked: list[dict[str, Any]] = []
    for domain in DOMAINS:
        score, matched = domain.score(text)
        if domain.baseline:
            ranked.append(
                {
                    "key": domain.key,
                    "title": domain.title,
                    "why": domain.why,
                    "relevance": "baseline",
                    "score": max(score, 1),
                    "matched_triggers": list(matched),
                }
            )
        elif score:
            ranked.append(
                {
                    "key": domain.key,
                    "title": domain.title,
                    "why": domain.why,
                    "relevance": "matched",
                    "score": score,
                    "matched_triggers": list(matched),
                }
            )
    ranked.sort(key=lambda item: (item["relevance"] == "baseline", -item["score"], item["key"]))
    return ranked


def _domain_by_key(key: str) -> Domain:
    for domain in DOMAINS:
        if domain.key == key:
            return domain
    raise TransmutationError(f"unknown domain: {key}")


def discover_capabilities(
    domains: Sequence[Mapping[str, Any]],
    *,
    repo_root: Path,
    verified: Iterable[str] = (),
) -> list[dict[str, Any]]:
    """Discover declared capabilities and classify them from file evidence only.

    File existence is not verification. ``verified`` is caller-supplied evidence
    naming capabilities whose behavior was actually executed and observed.
    """
    verified_names = set(verified)
    by_name: dict[str, dict[str, Any]] = {}
    domain_keys = [str(item["key"]) for item in domains]
    for key in domain_keys:
        for name in _domain_by_key(key).capabilities:
            by_name.setdefault(name, {"domains": []})
            if key not in by_name[name]["domains"]:
                by_name[name]["domains"].append(key)

    table = {name: (path, test, kind) for name, path, test, kind in CAPABILITIES}
    discovered: list[dict[str, Any]] = []
    for name, extra in sorted(by_name.items()):
        if name not in table:
            raise TransmutationError(f"capability is declared but not catalogued: {name}")
        path, test, kind = table[name]
        module_exists = (repo_root / path).is_file()
        test_exists = bool(test) and (repo_root / test).is_file()
        if name in verified_names and module_exists:
            status = CapabilityStatus.IMPLEMENTED_AND_VERIFIED
            note = "caller-supplied verification evidence"
        elif kind != "code":
            status = (
                CapabilityStatus.DOCUMENTED_ONLY if module_exists else CapabilityStatus.MISSING
            )
            note = "documentation or data artifact; not executable behavior"
        elif module_exists and test_exists:
            status = CapabilityStatus.IMPLEMENTED_NOT_VERIFIED
            note = "module and test present; not executed in this scan"
        elif module_exists:
            status = CapabilityStatus.IMPLEMENTED_NOT_VERIFIED
            note = "module present; no direct test"
        else:
            status = CapabilityStatus.MISSING
            note = "declared path not found"
        discovered.append(
            {
                "name": name,
                "status": status.value,
                "module": path,
                "test": test,
                "note": note,
                "domains": extra["domains"],
            }
        )
    return discovered


def rank_hypotheses(
    domains: Sequence[Mapping[str, Any]],
    *,
    budget: Budget,
    evidence: Mapping[str, Mapping[str, str]] | None = None,
) -> list[dict[str, Any]]:
    """Filter the hypothesis catalogue to matched domains and rank by cost/benefit."""
    domain_keys = {str(item["key"]) for item in domains}
    supplied = evidence or {}
    ranked: list[dict[str, Any]] = []
    for template in HYPOTHESES:
        if not domain_keys.intersection(template.when_domains):
            continue
        supplied_entry = supplied.get(template.key, {})
        status = supplied_entry.get("status", "UNTESTED")
        if status not in {"UNTESTED", "SUPPORTED", "REFUTED", "INCONCLUSIVE"}:
            raise TransmutationError(f"invalid hypothesis status: {status}")
        ranked.append(
            {
                "id": template.key,
                "statement": template.statement,
                "falsifier": template.falsifier,
                "experiment": template.experiment,
                "status": status,
                "evidence": supplied_entry.get("evidence", ""),
                "prior": template.prior,
                "score": template.score(),
                "scores": {
                    "benefit": template.benefit,
                    "testability": template.testability,
                    "complexity": template.complexity,
                    "risk": template.risk,
                    "cost": template.cost,
                    "time": template.time,
                },
            }
        )
    ranked.sort(key=lambda item: (-item["score"], item["id"]))
    return ranked[: budget.max_hypotheses]


def _subquestions(
    domains: Sequence[Mapping[str, Any]], budget: Budget
) -> tuple[list[str], int]:
    questions: list[str] = []
    seen: set[str] = set()
    for item in domains:
        for question in _domain_by_key(str(item["key"])).subquestions:
            if question in seen:
                continue
            if len(questions) >= budget.max_questions:
                return questions, 1
            seen.add(question)
            questions.append(question)
    return questions, 0


def _capability_gaps(capabilities: Sequence[Mapping[str, Any]]) -> list[str]:
    gaps: list[str] = []
    for capability in capabilities:
        if capability["status"] == CapabilityStatus.MISSING.value:
            gaps.append(f"capability_missing:{capability['name']}")
    return gaps


def _ranked_plan(
    *,
    request_id: str,
    original_hash: str,
    gate_gaps: Sequence[str],
    domains: Sequence[Mapping[str, Any]],
    hypotheses: Sequence[Mapping[str, Any]],
    capabilities: Sequence[Mapping[str, Any]],
) -> list[str]:
    steps = [
        f"1. preserve original {request_id} (sha256 {original_hash[:12]}...) before any action",
    ]
    for gap in gate_gaps:
        if len(steps) >= 9:
            break
        steps.append(f"{len(steps) + 1}. resolve {gap} before acting")
    if domains:
        top = _domain_by_key(str(domains[0]["key"]))
        steps.append(f"{len(steps) + 1}. investigate {top.title}: {top.subquestions[0]}")
    if hypotheses:
        steps.append(
            f"{len(steps) + 1}. run the cheapest discriminating experiment for "
            f"{hypotheses[0]['id']}: {hypotheses[0]['experiment']}"
        )
    reusable = [
        capability["name"]
        for capability in capabilities
        if capability["status"]
        in {
            CapabilityStatus.IMPLEMENTED_AND_VERIFIED.value,
            CapabilityStatus.IMPLEMENTED_NOT_VERIFIED.value,
            CapabilityStatus.PARTIALLY_IMPLEMENTED.value,
        }
    ]
    if reusable:
        steps.append(
            f"{len(steps) + 1}. reuse {len(reusable)} existing modules before building: "
            + ", ".join(reusable[:3])
        )
    steps.append(
        f"{len(steps) + 1}. stop at an explicit stop state when acceptance criteria are met "
        "or expected value falls below cost"
    )
    return steps


def _original_path(record_dir: Path, request_id: str) -> Path:
    return record_dir / "original" / f"{request_id}.json"


def _record_path(record_dir: Path, request_id: str) -> Path:
    return record_dir / "records" / f"{request_id}.json"


def _write_new(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, indent=2, sort_keys=True, default=str).encode("utf-8")
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
    except Exception:
        # O_EXCL created the file; remove only this incomplete artifact.
        try:
            path.unlink()
        except OSError:
            pass
        raise


def _last_entry_hash(journal: Path) -> str:
    if not journal.is_file():
        return "GENESIS"
    with journal.open("rb") as handle:
        handle.seek(0, os.SEEK_END)
        size = handle.tell()
        handle.seek(max(0, size - JOURNAL_TAIL_BYTES))
        tail = handle.read().decode("utf-8", errors="replace")
    for line in reversed(tail.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            return str(json.loads(line)["entry_hash"])
        except (ValueError, KeyError) as exc:
            raise TransmutationError("journal tail is corrupt; refusing to chain") from exc
    return "GENESIS"


def _append_journal(journal: Path, event: Mapping[str, Any]) -> dict[str, Any]:
    journal.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(event)
    payload["prev_entry_hash"] = _last_entry_hash(journal)
    payload["entry_hash"] = _hash(payload)
    with journal.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True, default=str) + "\n")
    return payload


def _preserve_original(
    *,
    text: str,
    source: Source,
    received_from: str,
    record_dir: Path,
    received_at: str,
    withhold: bool = False,
    withheld_reason: str = "",
) -> tuple[str, str, Path]:
    request_id = request_id_for(text)
    digest = _sha256_text(text)
    path = _original_path(record_dir, request_id)
    payload = {
        "protocol_version": PROTOCOL_VERSION,
        "request_id": request_id,
        "text": None if withhold else text,
        "text_withheld": withhold,
        "withheld_reason": withheld_reason if withhold else "",
        "sha256": digest,
        "source": source.value,
        "received_from": received_from,
        "received_at": received_at,
    }
    try:
        _write_new(path, payload)
    except FileExistsError:
        existing = json.loads(path.read_text(encoding="utf-8"))
        if existing.get("sha256") != digest:
            raise TransmutationConflict(
                f"request id {request_id} already exists with different content"
            ) from None
        if not existing.get("text_withheld") and existing.get("text") != text:
            raise TransmutationConflict(
                f"request id {request_id} already exists with different content"
            ) from None
    return request_id, digest, path


def load_record(request_id: str, record_dir: str | Path = DEFAULT_RECORD_DIR) -> dict[str, Any]:
    """Reload a persisted record and verify it against the immutable original."""
    directory = Path(record_dir)
    record = json.loads(_record_path(directory, request_id).read_text(encoding="utf-8"))
    original = json.loads(_original_path(directory, request_id).read_text(encoding="utf-8"))
    if record.get("original_request_hash") != original.get("sha256"):
        raise TransmutationConflict(f"record {request_id} does not match its original")
    if not original.get("text_withheld"):
        if _sha256_text(str(original.get("text"))) != original.get("sha256"):
            raise TransmutationConflict(f"original {request_id} fails its own hash")
    return record


def resume(request_id: str, record_dir: str | Path = DEFAULT_RECORD_DIR) -> dict[str, Any]:
    """Return the next checkpoint for a persisted record, or fail closed."""
    record = load_record(request_id, record_dir)
    checkpoint = record.get("next_checkpoint")
    if not isinstance(checkpoint, dict) or not checkpoint:
        raise TransmutationError(f"record {request_id} has no resumable checkpoint")
    return checkpoint


def transmute_request(
    text: str,
    *,
    source: Source = Source.OPERATOR,
    received_from: str = "",
    record_dir: str | Path = DEFAULT_RECORD_DIR,
    repo_root: str | Path | None = None,
    budget: Budget | None = None,
    depth: int = 0,
    evidence_refs: Iterable[str] = (),
    hypothesis_evidence: Mapping[str, Mapping[str, str]] | None = None,
    verified_capabilities: Iterable[str] = (),
    now: str | None = None,
) -> TransmutationResult:
    """Transmute one request into a bounded, persisted, read-only investigation.

    The original text is preserved before any analysis, except when the request
    trips a credential-handling rule; in that case only its hash is stored and the
    raw text is withheld. A repeated request id is suppressed and journalled,
    never re-planned. Depth above the budget is refused after preservation, so the
    original is never lost to a resource stop.
    """
    if not isinstance(text, str) or not text.strip():
        raise TransmutationError("request text must be a non-empty string")
    if depth < 0:
        raise TransmutationError("depth cannot be negative")

    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[2]
    directory = Path(record_dir)
    started = time.monotonic()
    resolved_budget, clamped = (budget or Budget()).validated()
    received_at = now or _now()
    sensitive_hits = [
        hit
        for hit in scan(text)
        if hit.code in SENSITIVE_CODES and hit.severity is Severity.DENY
    ]
    withhold = bool(sensitive_hits)
    withheld_reason = sensitive_hits[0].code if sensitive_hits else ""

    request_id, digest, original_path = _preserve_original(
        text=text,
        source=source,
        received_from=received_from,
        record_dir=directory,
        received_at=received_at,
        withhold=withhold,
        withheld_reason=withheld_reason,
    )
    record_path = _record_path(directory, request_id)
    journal = directory / "journal.jsonl"

    if record_path.is_file():
        existing = load_record(request_id, directory)
        _append_journal(
            journal,
            {
                "event": "duplicate_suppressed",
                "request_id": request_id,
                "original_request_hash": digest,
                "record_hash": _hash(existing),
                "at": received_at,
            },
        )
        return TransmutationResult(existing, record_path, duplicate=True)

    verdict = inbound_gate(Command(text=text, source=source, received_from=received_from))
    decision = "PROCEED_BOUNDED"
    stop_reason: str | None = None
    reasons: list[str] = []

    if withhold:
        requirement = f"[withheld by policy: {withheld_reason}]"
        gate_gaps: list[str] = []
        domains: list[dict[str, Any]] = []
        capabilities: list[dict[str, Any]] = []
        hypotheses: list[dict[str, Any]] = []
        questions: list[str] = []
        questions_truncated = 0
        gaps: list[str] = []
        plan: list[str] = []
        decision = "STOP"
        stop_reason = StopState.SAFETY_ABORT.value
        reasons = list(verdict.reasons)
    else:
        final_pass = verdict.passes[-1] if verdict.passes else None
        requirement = final_pass.requirement if final_pass else "no actionable requirement"
        gate_gaps = list(final_pass.gaps) if final_pass else []
        domains = classify_domains(text)
        capabilities = discover_capabilities(
            domains, repo_root=root, verified=verified_capabilities
        )
        hypotheses = rank_hypotheses(
            domains, budget=resolved_budget, evidence=hypothesis_evidence
        )
        questions, questions_truncated = _subquestions(domains, resolved_budget)
        gaps = gate_gaps + _capability_gaps(capabilities)
        plan = _ranked_plan(
            request_id=request_id,
            original_hash=digest,
            gate_gaps=gate_gaps,
            domains=domains,
            hypotheses=hypotheses,
            capabilities=capabilities,
        )
        if verdict.severity is Severity.DENY:
            decision = "STOP"
            stop_reason = StopState.SAFETY_ABORT.value
            reasons = list(verdict.reasons)
        elif verdict.severity is Severity.APPROVE and source is not Source.OPERATOR:
            decision = "REQUEST_AUTHORIZATION"
            stop_reason = StopState.AUTHORIZATION_REQUIRED.value
            reasons = list(verdict.reasons)
        elif depth > resolved_budget.max_depth:
            decision = "STOP"
            stop_reason = StopState.BUDGET_EXHAUSTED.value
            reasons = [
                f"depth {depth} exceeds max_depth {resolved_budget.max_depth}; "
                "preserve the checkpoint and require a new discriminating hypothesis"
            ]

    elapsed = time.monotonic() - started
    if elapsed > resolved_budget.wall_clock_seconds and stop_reason is None:
        decision = "STOP"
        stop_reason = StopState.BUDGET_EXHAUSTED.value
        reasons.append(
            f"wall clock {elapsed:.3f}s exceeded {resolved_budget.wall_clock_seconds}s"
        )

    secondary = [
        f"investigate {item['title']}" for item in domains if item["relevance"] == "matched"
    ]
    budget_record = resolved_budget.as_dict()
    budget_record["clamped"] = list(clamped)
    budget_record["depth"] = depth
    budget_record["questions_emitted"] = len(questions)
    budget_record["questions_truncated"] = questions_truncated
    budget_record["elapsed_seconds"] = round(elapsed, 6)

    record: dict[str, Any] = {
        "protocol_version": PROTOCOL_VERSION,
        "received_at": received_at,
        "request_id": request_id,
        "original_request_ref": str(original_path),
        "original_request_hash": digest,
        "intent": {
            "requirement": requirement,
            "primary": requirement,
            "secondary": secondary,
            "source": source.value,
        },
        "invariants": [
            "the original request text and hash are immutable",
            "transmuted scope never overrides the original intent; conflicts are recorded",
            "policy is evaluated on the original and on every refinement pass",
            "this protocol produces a plan and never executes an action",
            "recursion is bounded by the budget and every clamp is recorded",
            "no secret is read, printed, or transmitted",
            "records are append-only; existing records are never rewritten",
        ],
        "constraints": {
            "severity": verdict.severity.value,
            "allowed": verdict.allowed,
            "executed": verdict.executed,
            "approval_needed": list(verdict.approval_needed),
            "reasons": list(verdict.reasons),
            "converged": verdict.converged,
            "capped": verdict.capped,
            "clamped": verdict.clamped,
            "refinement_passes": len(verdict.passes),
        },
        "domains": domains,
        "subquestions": questions,
        "existing_capabilities": capabilities,
        "gaps": gaps,
        "hypotheses": hypotheses,
        "ranked_plan": plan,
        "budget": budget_record,
        "execution_mode": EXECUTION_MODE,
        "evidence_refs": sorted(
            {
                *evidence_refs,
                "barrot_agent/inbound/gate.py",
                "barrot_agent/inbound/transmutation.py",
            }
        ),
        "decision": decision,
        "stop_reason": stop_reason,
        "next_checkpoint": {
            "request_id": request_id,
            "record_path": str(record_path),
            "resume_at": plan[0] if plan else None,
            "depth": depth,
            "max_depth": resolved_budget.max_depth,
            "protocol_version": PROTOCOL_VERSION,
            "requires": (
                "reload with load_record(); re-enter only with a new discriminating "
                "hypothesis, at depth + 1"
            ),
        },
    }
    if reasons:
        record["constraints"]["stop_reasons"] = reasons

    _write_new(record_path, record)
    _append_journal(
        journal,
        {
            "event": "recorded",
            "request_id": request_id,
            "original_request_hash": digest,
            "record_hash": _hash(record),
            "decision": decision,
            "stop_reason": stop_reason,
            "at": received_at,
        },
    )
    return TransmutationResult(record, record_path, duplicate=False)


def main(argv: Sequence[str] | None = None) -> int:
    """Read-only CLI entry point. Prints the record and never executes the plan."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", nargs="?", help="request text; reads stdin when omitted")
    parser.add_argument("--record-dir", default=str(DEFAULT_RECORD_DIR))
    parser.add_argument(
        "--source",
        default=Source.OPERATOR.value,
        choices=[s.value for s in Source],
    )
    parser.add_argument("--received-from", default="")
    parser.add_argument("--depth", type=int, default=0)
    parser.add_argument("--max-depth", type=int, default=Budget().max_depth)
    parser.add_argument("--evidence", action="append", default=[])
    args = parser.parse_args(argv)

    text = args.request if args.request is not None else sys.stdin.read()
    result = transmute_request(
        text,
        source=Source(args.source),
        received_from=args.received_from,
        record_dir=args.record_dir,
        budget=Budget(max_depth=args.max_depth),
        depth=args.depth,
        evidence_refs=args.evidence,
    )
    print(json.dumps(result.record, indent=2, sort_keys=True))
    if result.record["stop_reason"] == StopState.SAFETY_ABORT.value:
        return 3
    if result.record["stop_reason"] == StopState.AUTHORIZATION_REQUIRED.value:
        return 4
    if result.record["stop_reason"] == StopState.BUDGET_EXHAUSTED.value:
        return 5
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised through subprocess tests
    raise SystemExit(main())
