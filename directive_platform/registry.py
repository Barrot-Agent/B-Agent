"""
AgentRegistry — manages the set of AI agents available on the platform.

Agents are persisted as individual JSON files under
``.directive_platform/agents/`` so they survive application restarts.
The registry also pre-seeds a set of built-in default agents when it is
first initialised (i.e. when the agents directory is empty).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Agent, AgentStatus

_DEFAULT_AGENTS_DIR = Path(".directive_platform") / "agents"


# ---------------------------------------------------------------------------
# Built-in default agents
# ---------------------------------------------------------------------------

_DEFAULT_AGENTS: list[dict[str, Any]] = [
    {
        "agent_id": "barrot-agent",
        "name": "BarrotAgent",
        "description": (
            "The primary orchestration agent. Coordinates tasks across the "
            "platform, performs high-level reasoning, and routes work to "
            "specialist agents."
        ),
        "capabilities": ["learn", "analyze", "refine", "cooperate", "project"],
    },
    {
        "agent_id": "learner-agent",
        "name": "LearnerAgent",
        "description": (
            "Specialises in absorbing new information, synthesising knowledge "
            "from diverse sources, and building structured summaries that "
            "other agents can act on."
        ),
        "capabilities": ["learn", "knowledge_synthesis", "adaptation", "summarisation"],
    },
    {
        "agent_id": "analyst-agent",
        "name": "AnalystAgent",
        "description": (
            "Performs deep structural analysis on data and findings. "
            "Identifies patterns, anomalies, and convergence points. "
            "Partners closely with CorroborationAgent to validate conclusions."
        ),
        "capabilities": ["analyze", "pattern_detection", "convergence", "data_analysis"],
    },
    {
        "agent_id": "refinement-agent",
        "name": "RefinementAgent",
        "description": (
            "Iteratively improves capabilities, algorithms, and outputs. "
            "Applies optimisation techniques and benchmarks improvements "
            "before recommending them to the operator."
        ),
        "capabilities": ["refine", "optimisation", "benchmarking", "capability_enhancement"],
    },
    {
        "agent_id": "corroboration-agent",
        "name": "CorroborationAgent",
        "description": (
            "Cross-references data across multiple sources to validate facts, "
            "detect contradictions, and surface consensus views. "
            "Essential for directives involving uncertain or disputed information."
        ),
        "capabilities": ["cross_corroborate", "fact_checking", "data_validation", "source_analysis"],
    },
    {
        "agent_id": "project-agent",
        "name": "ProjectAgent",
        "description": (
            "Plans, coordinates, and tracks multi-agent projects. "
            "Breaks directives into sub-tasks, assigns work, monitors "
            "progress, and consolidates results into deliverables."
        ),
        "capabilities": ["project", "planning", "coordination", "task_decomposition", "cooperate"],
    },
    {
        "agent_id": "smart-agent",
        "name": "SmartAgent",
        "description": (
            "Autonomous plan-act-observe agent. Given any goal, it decomposes "
            "the work into concrete steps, invokes the appropriate built-in "
            "tool for each step (search, analyze, reason, code, summarize), "
            "reflects on intermediate results, and converges on a final answer. "
            "The core of Barrot's autonomous execution capability."
        ),
        "capabilities": [
            "autonomous_planning", "tool_use", "search", "analyze", "reason",
            "code", "summarize", "learn", "refine", "project",
        ],
    },
    # ------------------------------------------------------------------
    # Extended HRM Council (Tier 2.5) — 8 specialist agents added in
    # response to the complementary-integrity gap analysis (issue #174).
    # ------------------------------------------------------------------
    {
        "agent_id": "hrm-t",
        "name": "HRM-T (Temporal)",
        "description": (
            "Temporal Logic & Causal Chain Analysis specialist. "
            "Reasons across time, constructs causal chains, and builds "
            "predictive models from time-series data. "
            "Complements AnalystAgent and CorroborationAgent by adding the "
            "time dimension to structural analysis."
        ),
        "capabilities": [
            "temporal_reasoning", "causal_inference", "time_series_analysis",
            "predictive_modeling", "analyze",
        ],
    },
    {
        "agent_id": "hrm-x",
        "name": "HRM-X (Adversarial)",
        "description": (
            "Red Team Validation & Weakness Detection specialist. "
            "Stress-tests outputs, challenges assumptions, surfaces edge cases, "
            "and identifies blind spots in plans and conclusions. "
            "Essential for hardening any directive result before delivery."
        ),
        "capabilities": [
            "adversarial_testing", "red_teaming", "assumption_challenging",
            "edge_case_detection", "robustness_validation", "cross_corroborate",
        ],
    },
    {
        "agent_id": "hrm-e",
        "name": "HRM-E (Emotional)",
        "description": (
            "Emotional Intelligence & Empathy Modeling specialist. "
            "Models affective states, evaluates emotional resonance, and ensures "
            "outputs are calibrated for human understanding and reception. "
            "Bridges analytical output with human-centred communication."
        ),
        "capabilities": [
            "emotional_intelligence", "empathy_modeling", "affective_computing",
            "human_resonance", "communication_calibration",
        ],
    },
    {
        "agent_id": "hrm-phi",
        "name": "HRM-Phi (Ethics)",
        "description": (
            "Ethical Framework Analysis & Value Alignment specialist. "
            "Applies consequentialist, deontological, and virtue-based lenses "
            "to evaluate outputs for moral soundness and AI-safety alignment. "
            "Acts as the platform's primary ethics arbiter."
        ),
        "capabilities": [
            "ethical_reasoning", "value_alignment", "ai_safety", "moral_analysis",
            "multi_framework_ethics", "analyze",
        ],
    },
    {
        "agent_id": "hrm-sigma",
        "name": "HRM-Sigma (Systems)",
        "description": (
            "Holistic Systems Analysis & Emergence Detection specialist. "
            "Maps feedback loops, identifies emergent behaviours, and models "
            "complex adaptive systems. Prevents reductionist blind spots by "
            "maintaining a whole-system perspective throughout every directive."
        ),
        "capabilities": [
            "systems_thinking", "emergence_detection", "feedback_loop_analysis",
            "complexity_modeling", "holistic_analysis", "analyze",
        ],
    },
    {
        "agent_id": "hrm-omega",
        "name": "HRM-Omega (Embodiment)",
        "description": (
            "Physical World Integration & Embodied Reasoning specialist. "
            "Reasons about physical constraints, spatial relationships, and "
            "robotics-relevant considerations. Bridges digital plans with "
            "real-world feasibility and embodied-cognition principles."
        ),
        "capabilities": [
            "embodied_reasoning", "spatial_intelligence", "physical_constraints",
            "robotics_awareness", "sensorimotor_modeling",
        ],
    },
    {
        "agent_id": "hrm-q",
        "name": "HRM-Q (Quantum)",
        "description": (
            "Quantum Logic & Superposition Reasoning specialist. "
            "Handles non-binary decisions, probabilistic superpositions, and "
            "uncertainty quantification beyond classical Boolean logic. "
            "Augments every directive with quantum-inspired uncertainty handling."
        ),
        "capabilities": [
            "quantum_reasoning", "superposition_logic", "uncertainty_quantification",
            "non_classical_inference", "probabilistic_modeling", "reason",
        ],
    },
    {
        "agent_id": "wisdom-i",
        "name": "Wisdom-I (Indigenous)",
        "description": (
            "Indigenous Knowledge Integration & Ancient Wisdom specialist. "
            "Incorporates Ubuntu, Sankofa, Seven-Generations thinking, "
            "Dreamtime cosmology, Pachamama ecology, and other global indigenous "
            "traditions. Ensures outputs honour long-term, nature-based, and "
            "culturally diverse perspectives."
        ),
        "capabilities": [
            "indigenous_knowledge", "holistic_worldview", "intergenerational_reasoning",
            "nature_based_intelligence", "cultural_diversity", "wisdom_synthesis",
        ],
    },
]


class AgentRegistry:
    """
    Persistent registry of AI agents.

    Parameters
    ----------
    agents_dir:
        Directory in which agent JSON files are stored.
    """

    def __init__(self, agents_dir: Path | str | None = None) -> None:
        self._dir = Path(agents_dir) if agents_dir else _DEFAULT_AGENTS_DIR
        self._dir.mkdir(parents=True, exist_ok=True)
        self._seed_defaults()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register(self, agent: Agent) -> Agent:
        """Add or update an agent in the registry."""
        self._persist(agent)
        return agent

    def get(self, agent_id: str) -> Agent | None:
        """Return the agent with the given ID, or ``None`` if not found."""
        path = self._dir / f"{agent_id}.json"
        if not path.exists():
            return None
        try:
            return Agent.from_dict(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, KeyError):
            return None

    def list_all(self) -> list[Agent]:
        """Return all registered agents, sorted by name."""
        agents: list[Agent] = []
        for fp in sorted(self._dir.glob("*.json")):
            try:
                agents.append(Agent.from_dict(json.loads(fp.read_text(encoding="utf-8"))))
            except (json.JSONDecodeError, KeyError):
                pass
        return sorted(agents, key=lambda a: a.name)

    def find_by_capability(self, capability: str) -> list[Agent]:
        """Return all agents that list *capability* among their capabilities."""
        return [a for a in self.list_all() if capability in a.capabilities]

    def update_status(
        self,
        agent_id: str,
        status: str,
        current_directive_id: str | None = None,
    ) -> None:
        """Update the status (and optionally the current directive) of an agent."""
        agent = self.get(agent_id)
        if agent is None:
            return
        agent.status = status
        agent.current_directive_id = current_directive_id
        self._persist(agent)

    def deregister(self, agent_id: str) -> bool:
        """Remove an agent from the registry. Returns ``True`` if it existed."""
        path = self._dir / f"{agent_id}.json"
        if path.exists():
            path.unlink()
            return True
        return False

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _persist(self, agent: Agent) -> None:
        dest = self._dir / f"{agent.agent_id}.json"
        dest.write_text(json.dumps(agent.to_dict(), indent=2), encoding="utf-8")

    def _seed_defaults(self) -> None:
        """Register any built-in agents that are not yet in the registry.

        This is idempotent: existing agents are left untouched so that
        runtime status changes are preserved across restarts.
        """
        existing_ids = {fp.stem for fp in self._dir.glob("*.json")}
        for data in _DEFAULT_AGENTS:
            if data["agent_id"] in existing_ids:
                continue
            agent = Agent(
                agent_id=data["agent_id"],
                name=data["name"],
                description=data["description"],
                capabilities=data["capabilities"],
                status=AgentStatus.IDLE,
            )
            self._persist(agent)
