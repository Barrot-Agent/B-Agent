"""
data/schemas.py — Canonical data schemas for Barrot-Agent.

Defines TypedDicts for all major data domains used across the codebase.
Import these types in any module that reads or writes structured data to
ensure consistent field names and schema shapes.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    from typing import NotRequired, TypedDict
except ImportError:
    from typing_extensions import NotRequired, TypedDict  # Python < 3.11


# ---------------------------------------------------------------------------
# Merge-Conflict Domain
# ---------------------------------------------------------------------------


class MergeConflictPattern(TypedDict):
    pattern_id: str
    name: str
    description: str
    conflict_type: str
    indicators: List[str]
    file_patterns: List[str]
    frequency: str
    auto_resolvable: bool


class MergeResolutionTechnique(TypedDict):
    technique_id: str
    name: str
    description: str
    applicable_types: List[str]
    strategy: str
    commands: List[str]
    prerequisites: List[str]
    success_rate: str
    risk_level: str
    automation_level: str


class MergeConflictTool(TypedDict):
    tool_name: str
    category: str
    description: str
    use_cases: List[str]
    installation: str
    basic_usage: str
    advanced_features: List[str]
    integration_notes: str


class MergeConflictScenario(TypedDict):
    scenario_id: str
    title: str
    description: str
    conflict_type: str
    example_conflict: str
    recommended_strategy: str
    step_by_step: List[str]
    alternative_approaches: List[str]
    common_pitfalls: List[str]
    prevention_tips: List[str]


class MergeConflictBestPractice(TypedDict):
    practice_id: str
    title: str
    description: str
    category: str
    impact: str
    implementation: List[str]
    examples: List[str]
    anti_patterns: List[str]


class MergeConflictLearningOutcome(TypedDict):
    outcome_id: str
    timestamp: str
    conflict_type: str
    strategy_used: str
    success: bool


class MergeConflictKnowledgeSummary(TypedDict):
    last_updated: str
    total_patterns: int
    total_techniques: int
    total_scenarios: int
    total_tools: int
    total_best_practices: int
    total_learning_outcomes: int
    strategy_success_rates: Dict[str, Any]


class MergeConflictUnified(TypedDict):
    patterns: List[MergeConflictPattern]
    scenarios: List[MergeConflictScenario]
    tools: List[MergeConflictTool]
    best_practices: List[MergeConflictBestPractice]
    learning_outcomes: List[MergeConflictLearningOutcome]
    resolution_techniques: List[MergeResolutionTechnique]
    knowledge_summary: MergeConflictKnowledgeSummary


# ---------------------------------------------------------------------------
# Millennium Problems Domain
# ---------------------------------------------------------------------------


class MillenniumProblem(TypedDict):
    number: int
    name: str
    problem_statement: str
    official_status: str
    barrot_analysis_stage: str
    ai_ml_relevance: str
    why_matters_for_ai: str
    barrot_approach: str
    current_insights: str
    next_steps: str
    progress_status: str


class MillenniumProblemsTaxonomy(TypedDict):
    by_ai_applicability: Any
    by_status: Any
    by_mathematical_domain: Any
    by_barrot_priority: Any


class MillenniumProblemsUnified(TypedDict):
    overview: List[Dict[str, Any]]
    problems: List[MillenniumProblem]
    search_summaries: Dict[str, Any]
    taxonomy: MillenniumProblemsTaxonomy
    _meta: Dict[str, Any]


# ---------------------------------------------------------------------------
# MMI / Monetization Domain
# ---------------------------------------------------------------------------


class MMIRecommendations(TypedDict):
    timestamp: str
    analysis_version: str
    agi_gaps_identified: List[str]
    recommendations: List[Dict[str, Any]]
    total_sources_identified: int
    critical_sources_count: int
    immediate_action_sources: List[str]


class MonetizationProtocols(TypedDict):
    timestamp: str
    engine_version: str
    total_revenue_streams: int
    protocols: List[Dict[str, Any]]
    summary: Dict[str, Any]


class CouncilWeights(TypedDict):
    timestamp: str
    target_asset: str
    council_action: str
    orchestrator_weight_multiplier: float
    active_stability_anchor: str


class MMIMonetizationUnified(TypedDict):
    mmi_recommendations: MMIRecommendations
    monetization_protocols: MonetizationProtocols
    council_weights: CouncilWeights
    _meta: Dict[str, Any]


# ---------------------------------------------------------------------------
# Character / Capabilities Domain
# ---------------------------------------------------------------------------


class CharacterCapabilitiesUnified(TypedDict):
    character_database: Dict[str, Any]
    discovered_capabilities: Dict[str, Any]
    _meta: Dict[str, Any]


# ---------------------------------------------------------------------------
# Integration / Pingpong
# ---------------------------------------------------------------------------


class PingpongRequest(TypedDict):
    timestamp: str
    payload: Dict[str, Any]
    origin: str
    directive: str
    notes: Optional[str]
    topic: NotRequired[str]


# ---------------------------------------------------------------------------
# Longevity Domain
# ---------------------------------------------------------------------------


class AgingMechanism(TypedDict):
    mechanism: str
    evidence: str
    confidence: float
    tags: List[str]


class TrialOutcome(TypedDict):
    participant_id: str
    treatment_arm: str
    baseline_epigenetic_age: float
    followup_epigenetic_age: float
    nad_level_change_pct: float
    adverse_events: List[str]


class EpigeneticPatternMatrix(TypedDict):
    markers: List[str]
    matrix: List[List[float]]
    marker_averages: Dict[str, float]
    sample_count: int


class BiomarkerTimelineEntry(TypedDict):
    timestamp: str
    value: float
    source: str


class BiomarkerTimeline(TypedDict):
    participant_id: str
    biomarker: str
    timeline: List[BiomarkerTimelineEntry]
    trend: str


class ReprogrammingProtocolTemplate(TypedDict):
    protocol_id: str
    factors: List[str]
    expression_mode: str
    on_days: int
    off_days: int
    cycles: int
    target_cell_types: List[str]
    safety_notes: List[str]


class LongevityUnified(TypedDict):
    research_domain: str
    aging_mechanisms: List[AgingMechanism]
    trial_outcomes: List[TrialOutcome]
    epigenetic_pattern_matrices: List[EpigeneticPatternMatrix]
    biomarker_timelines: List[BiomarkerTimeline]
    omega_ingest: Dict[str, Any]
    mmi_breakthroughs: List[Dict[str, Any]]
    _meta: Dict[str, Any]


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------

DataFileMeta = Dict[str, Any]
"""Generic metadata dict attached to unified data files as '_meta' key."""
