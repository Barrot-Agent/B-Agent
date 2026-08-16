"""
SmartAgent — an autonomous plan-act-observe AI agent.

The SmartAgent accepts a natural-language *goal*, autonomously decomposes it
into a sequence of concrete :class:`PlanStep` objects, executes each step
using a built-in tool library, reflects on intermediate results, and produces
a final consolidated answer.

All responses are generated without an external LLM so the agent works
out-of-the-box. The architecture is designed to be subclassed: override
``_plan``, ``_act``, or ``_reflect`` to plug in a real language model.

Usage
-----
    from barrot_agent import SmartAgent, AgentEventType

    agent = SmartAgent()
    for event in agent.run("Research the latest advances in AI agents"):
        print(event.type, event.content)
"""

from __future__ import annotations

import hashlib
import logging
import re
import textwrap
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterator

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Event types
# ---------------------------------------------------------------------------


class AgentEventType(str, Enum):
    GOAL = "goal"  # Agent received the goal
    THINKING = "thinking"  # Agent is reasoning / planning
    PLAN = "plan"  # Full plan produced
    ACTION = "action"  # Starting a step / tool call
    TOOL_RESULT = "tool_result"  # Result of a tool call
    OBSERVATION = "observation"  # Agent reflects on the result
    ANSWER = "answer"  # Final consolidated answer
    ERROR = "error"  # Unrecoverable error


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class PlanStep:
    """A single step in the agent's execution plan."""

    step_number: int
    title: str
    description: str
    tool: str
    tool_args: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_number": self.step_number,
            "title": self.title,
            "description": self.description,
            "tool": self.tool,
            "tool_args": self.tool_args,
        }


@dataclass
class ToolCall:
    """A single invocation of a built-in tool."""

    tool_name: str
    args: dict[str, Any]
    call_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])


@dataclass
class ToolResult:
    """Output of a :class:`ToolCall`."""

    call_id: str
    tool_name: str
    success: bool
    output: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentEvent:
    """A single event emitted by the agent loop."""

    type: AgentEventType
    content: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    @property
    def is_final(self) -> bool:
        return self.type in (AgentEventType.ANSWER, AgentEventType.ERROR)


# ---------------------------------------------------------------------------
# Built-in tool library
# ---------------------------------------------------------------------------


class _BuiltinTools:
    """
    A collection of lightweight built-in tools available to the SmartAgent.

    Each tool method accepts keyword arguments and returns a :class:`ToolResult`.
    Tools are intentionally deterministic so they work without external APIs.
    Real implementations can be substituted by subclassing :class:`SmartAgent`
    and overriding ``_call_tool``.
    """

    # ------------------------------------------------------------------
    # Tool: analyze
    # ------------------------------------------------------------------

    @staticmethod
    def analyze(*, topic: str, depth: str = "standard") -> ToolResult:
        """
        Analyse a topic and return structured observations.

        Parameters
        ----------
        topic:
            Subject to analyse.
        depth:
            ``"quick"`` | ``"standard"`` | ``"deep"``
        """
        call_id = str(uuid.uuid4())[:8]
        depth_map = {
            "quick": (2, 2, 1),
            "standard": (3, 3, 2),
            "deep": (5, 5, 3),
        }
        n_concepts, n_patterns, n_gaps = depth_map.get(depth, (3, 3, 2))

        # Derive deterministic but plausible content from the topic hash
        h = int(hashlib.md5(topic.encode()).hexdigest(), 16)

        concept_adjectives = [
            "foundational",
            "emergent",
            "cross-domain",
            "high-leverage",
            "underexplored",
            "well-established",
            "contested",
            "pivotal",
        ]
        pattern_types = [
            "recursive self-improvement loops",
            "multi-agent cooperation dynamics",
            "goal-gradient alignment issues",
            "capability generalisation gaps",
            "feedback latency effects",
            "adversarial brittleness",
            "data scarcity bottlenecks",
            "emergent tool-use behaviours",
            "reasoning chain fragmentation",
        ]
        gap_types = [
            "standardised evaluation benchmarks",
            "long-horizon memory architectures",
            "efficient grounding mechanisms",
            "robust uncertainty quantification",
            "cross-modal reasoning pipelines",
            "explainable intermediate representations",
        ]

        concepts = [
            concept_adjectives[(h >> (i * 3)) % len(concept_adjectives)] for i in range(n_concepts)
        ]
        patterns = [pattern_types[(h >> (i * 5)) % len(pattern_types)] for i in range(n_patterns)]
        gaps = [gap_types[(h >> (i * 7)) % len(gap_types)] for i in range(n_gaps)]

        lines = [
            f"**Analysis of:** {topic}  (depth: {depth})",
            "",
            f"**Key concepts identified ({n_concepts}):**",
        ]
        for i, c in enumerate(concepts, 1):
            lines.append(f"  {i}. A {c} concept central to understanding the topic.")
        lines += [
            "",
            f"**Patterns observed ({n_patterns}):**",
        ]
        for i, p in enumerate(patterns, 1):
            lines.append(f"  {i}. The data reveals {p}.")
        lines += [
            "",
            f"**Knowledge gaps ({n_gaps}):**",
        ]
        for i, g in enumerate(gaps, 1):
            lines.append(f"  {i}. Insufficient coverage of {g}.")

        return ToolResult(
            call_id=call_id,
            tool_name="analyze",
            success=True,
            output="\n".join(lines),
            metadata={
                "topic": topic,
                "depth": depth,
                "concepts": n_concepts,
                "patterns": n_patterns,
                "gaps": n_gaps,
            },
        )

    # ------------------------------------------------------------------
    # Tool: search
    # ------------------------------------------------------------------

    @staticmethod
    def search(*, query: str, max_results: int = 3) -> ToolResult:
        """
        Simulate a knowledge-base search and return relevant findings.

        Parameters
        ----------
        query:
            Search query.
        max_results:
            Maximum number of results to return.
        """
        call_id = str(uuid.uuid4())[:8]
        h = int(hashlib.md5(query.encode()).hexdigest(), 16)

        source_names = [
            "ArXiv preprint server",
            "GitHub trending repositories",
            "Semantic Scholar research index",
            "HuggingFace model hub",
            "Google Scholar citation graph",
            "OpenReview peer-review platform",
            "Papers With Code benchmark leaderboards",
            "DeepMind technical blog",
        ]
        finding_templates = [
            "Recent work demonstrates significant improvements in {query_summary} "
            "through the application of reinforcement learning from human feedback.",
            "A survey of 47 papers on {query_summary} identifies three dominant "
            "architectural patterns and two open research challenges.",
            "State-of-the-art results on {query_summary} benchmarks show a 23% "
            "improvement over the previous best published method.",
            "Community consensus suggests {query_summary} is entering a phase of "
            "rapid capability expansion driven by scale and novel training objectives.",
            "Practitioners report that {query_summary} techniques are increasingly "
            "deployed in production systems, with reliability remaining the top concern.",
        ]

        query_summary = " ".join(query.split()[:5])
        lines = [f'**Search results for:** "{query}"', ""]
        for i in range(min(max_results, 5)):
            src = source_names[(h >> (i * 4)) % len(source_names)]
            finding = finding_templates[(h >> (i * 6)) % len(finding_templates)].format(
                query_summary=query_summary
            )
            lines.append(f"**Result {i + 1}** — *{src}*")
            lines.append(f"  {finding}")
            lines.append("")

        return ToolResult(
            call_id=call_id,
            tool_name="search",
            success=True,
            output="\n".join(lines),
            metadata={"query": query, "results_returned": min(max_results, 5)},
        )

    # ------------------------------------------------------------------
    # Tool: reason
    # ------------------------------------------------------------------

    @staticmethod
    def reason(*, premise: str, objective: str) -> ToolResult:
        """
        Apply structured reasoning to derive conclusions from a premise.

        Parameters
        ----------
        premise:
            Background context or facts.
        objective:
            What the agent is trying to conclude or decide.
        """
        call_id = str(uuid.uuid4())[:8]
        h = int(hashlib.md5((premise + objective).encode()).hexdigest(), 16)

        reasoning_steps = [
            "Identify the core entities and their relationships.",
            "Map the dependencies between facts stated in the premise.",
            "Apply first-principles logic to each dependency chain.",
            "Evaluate alternative interpretations and assign confidence weights.",
            "Converge on the most-supported conclusion given the available evidence.",
        ]
        conclusions = [
            "The available evidence strongly supports proceeding with the proposed approach.",
            "Multiple lines of reasoning converge on a consistent conclusion.",
            "The primary objective is achievable with moderate effort and available resources.",
            "Key uncertainties have been identified and mitigation strategies are viable.",
        ]
        step_subset = reasoning_steps[: (3 + h % 3)]
        conclusion = conclusions[h % len(conclusions)]

        lines = [
            f"**Reasoning chain for:** {objective}",
            "",
            "**Steps:**",
        ]
        for i, s in enumerate(step_subset, 1):
            lines.append(f"  {i}. {s}")
        lines += [
            "",
            f"**Conclusion:** {conclusion}",
        ]

        return ToolResult(
            call_id=call_id,
            tool_name="reason",
            success=True,
            output="\n".join(lines),
            metadata={"objective": objective, "steps": len(step_subset)},
        )

    # ------------------------------------------------------------------
    # Tool: code
    # ------------------------------------------------------------------

    @staticmethod
    def code(*, task: str, language: str = "python") -> ToolResult:
        """
        Generate a code snippet to accomplish a programming task.

        Parameters
        ----------
        task:
            Description of what the code should do.
        language:
            Target programming language.
        """
        call_id = str(uuid.uuid4())[:8]
        h = int(hashlib.md5(task.encode()).hexdigest(), 16)

        # Generate a plausible skeleton based on the task keywords
        keywords = re.findall(r"\b[a-zA-Z]{4,}\b", task.lower())
        func_name = "_".join(keywords[:2]) if keywords else "process_data"
        func_name = re.sub(r"[^a-z_]", "", func_name)[:40] or "run_task"

        param_options = ["data", "config", "input_path", "context", "query"]
        param = param_options[h % len(param_options)]

        snippet = textwrap.dedent(f"""\
            def {func_name}({param}):
                \"\"\"
                {task}

                Parameters
                ----------
                {param}:
                    Input data or configuration for the task.

                Returns
                -------
                dict
                    A result dictionary with status and output fields.
                \"\"\"
                # Step 1: Validate input
                if not {param}:
                    raise ValueError("Input '{param}' must not be empty.")

                # Step 2: Core processing
                result = {{}}
                # TODO: implement domain logic here

                # Step 3: Return structured output
                return {{"status": "success", "output": result}}
        """)

        output = (
            f"**Generated {language} code for:** {task}\n\n"
            f"```{language}\n{snippet}\n```\n\n"
            "The function skeleton is ready. Add domain-specific logic in Step 2."
        )

        return ToolResult(
            call_id=call_id,
            tool_name="code",
            success=True,
            output=output,
            metadata={"task": task, "language": language, "function": func_name},
        )

    # ------------------------------------------------------------------
    # Tool: repo_hunt
    # ------------------------------------------------------------------

    @staticmethod
    def repo_hunt(*, topic: str, mode: str = "both") -> ToolResult:
        """
        Evaluate GitHub repositories for contribution or integration opportunities.

        Parameters
        ----------
        topic:
            Subject area or project context to guide the repository search.
        mode:
            ``"contribute"`` – repos where resolving open issues adds value.
            ``"integrate"``  – repos whose capabilities Barrot should adopt.
            ``"both"``       – return recommendations for both categories.
        """
        call_id = str(uuid.uuid4())[:8]
        h = int(hashlib.md5(topic.encode()).hexdigest(), 16)

        contribute_repos = [
            ("langchain-ai/langchain", "LLM orchestration", "memory management, tool reliability"),
            ("microsoft/autogen", "Multi-agent framework", "agent coordination, error recovery"),
            (
                "huggingface/transformers",
                "Model hub",
                "inference optimisation, tokeniser edge cases",
            ),
            ("openai/openai-python", "OpenAI SDK", "retry logic, streaming robustness"),
            ("BerriAI/litellm", "LLM proxy", "provider fallback, cost tracking"),
            ("stanford-crfm/helm", "Evaluation harness", "new benchmark coverage, reproducibility"),
            ("guidance-ai/guidance", "Structured generation", "grammar support, latency reduction"),
            ("run-llama/llama_index", "RAG framework", "retrieval accuracy, chunking strategies"),
        ]

        integrate_repos = [
            ("langchain-ai/langchain", "Composable tool chains and memory primitives"),
            ("microsoft/semantic-kernel", "Planner and skill plug-in architecture"),
            ("huggingface/smolagents", "Lightweight agent loop compatible with HF models"),
            ("run-llama/llama_index", "Vector-store RAG pipeline and data connectors"),
            ("openai/swarm", "Lightweight multi-agent handoff primitives"),
            ("BerriAI/litellm", "Unified LLM gateway for cost and latency control"),
            ("pydantic/pydantic-ai", "Type-safe agent scaffolding built on Pydantic"),
            ("anthropics/anthropic-sdk-python", "Direct Claude API integration"),
        ]

        n_contribute = 4 if mode in ("both", "contribute") else 0
        n_integrate = 4 if mode in ("both", "integrate") else 0

        lines: list[str] = [f"**Repo Hunt results for:** {topic}  (mode: {mode})", ""]

        if n_contribute:
            lines += ["### 🔧 Repositories to contribute to (open-issue resolution)", ""]
            for i in range(n_contribute):
                repo, domain, issues = contribute_repos[(h >> (i * 4)) % len(contribute_repos)]
                lines.append(
                    f"  {i + 1}. **{repo}** [{domain}] — "
                    f"open issues worth addressing: *{issues}*."
                )
            lines.append("")

        if n_integrate:
            lines += ["### 🔌 Repositories to integrate with", ""]
            for i in range(n_integrate):
                repo, rationale = integrate_repos[(h >> (i * 5)) % len(integrate_repos)]
                lines.append(f"  {i + 1}. **{repo}** — {rationale}.")
            lines.append("")

        metadata: dict[str, Any] = {
            "topic": topic,
            "mode": mode,
            "contribute_count": n_contribute,
            "integrate_count": n_integrate,
        }

        return ToolResult(
            call_id=call_id,
            tool_name="repo_hunt",
            success=True,
            output="\n".join(lines),
            metadata=metadata,
        )

    # ------------------------------------------------------------------
    # Tool: summarize
    # ------------------------------------------------------------------

    @staticmethod
    def summarize(*, content: str, style: str = "bullet") -> ToolResult:
        """
        Condense accumulated findings into a structured summary.

        Parameters
        ----------
        content:
            Raw text to summarise.
        style:
            ``"bullet"`` | ``"paragraph"`` | ``"executive"``
        """
        call_id = str(uuid.uuid4())[:8]

        # Extract the most information-dense sentences as a proxy for summarisation
        sentences = [s.strip() for s in re.split(r"[.!?]", content) if len(s.strip()) > 30]
        # Keep up to 5 meaningful sentences
        top = sentences[:5] if len(sentences) >= 5 else sentences

        if style == "paragraph":
            body = "  ".join(top) + "."
            output = f"**Summary (paragraph):**\n\n{body}"
        elif style == "executive":
            output = (
                "**Executive Summary:**\n\n"
                + f"This analysis covered {len(sentences)} key statements. "
                + "The most critical finding is: "
                + (top[0] if top else "no significant findings.")
                + "."
            )
        else:  # bullet
            bullets = "\n".join(f"- {s}." for s in top) if top else "- No significant findings."
            output = f"**Summary (bullet points):**\n\n{bullets}"

        return ToolResult(
            call_id=call_id,
            tool_name="summarize",
            success=True,
            output=output,
            metadata={"style": style, "sentences_extracted": len(top)},
        )

    # ------------------------------------------------------------------
    # Tool: reconfigure_infra
    # ------------------------------------------------------------------

    @staticmethod
    def reconfigure_infra(*, target: str = "barrot", mode: str = "audit") -> ToolResult:
        """
        Inspect and reconfigure Barrot's infrastructure using live state.

        Parameters
        ----------
        target:
            Label describing what is being reconfigured (informational).
        mode:
            ``"audit"``  – Read-only gap analysis against declared capability
                           targets and the live MCP registry.
            ``"plan"``   – Produce a structured :class:`ReconfigurationReport`
                           with server promotion proposals.
            ``"apply"``  – Invoke the MCP integration pipeline in dry-run mode
                           and return its stats.  Writes are still blocked by
                           the default ``MCPApprovalGate(mode="always_deny")``.
        """
        call_id = str(uuid.uuid4())[:8]

        try:
            from barrot_agent.reconfiguration import build_reconfiguration_report
        except ImportError as exc:
            return ToolResult(
                call_id=call_id,
                tool_name="reconfigure_infra",
                success=False,
                output=f"Failed to import reconfiguration module: {exc}",
            )

        mode = mode.lower().strip()
        if mode not in ("audit", "plan", "apply"):
            return ToolResult(
                call_id=call_id,
                tool_name="reconfigure_infra",
                success=False,
                output=(
                    f"Unknown mode {mode!r}. "
                    "Choose one of: 'audit', 'plan', 'apply'."
                ),
            )

        logger.debug("reconfigure_infra: target=%s mode=%s", target, mode)

        # ---- audit / plan: build report from live registry ----
        if mode in ("audit", "plan"):
            try:
                report = build_reconfiguration_report(dry_run=True)
            except Exception as exc:  # noqa: BLE001
                logger.warning("reconfigure_infra audit error: %s", exc)
                return ToolResult(
                    call_id=call_id,
                    tool_name="reconfigure_infra",
                    success=False,
                    output=f"Error during infrastructure audit: {exc}",
                )

            summary = "\n".join(report.summary_lines())

            if mode == "audit":
                output = (
                    f"## 🔍 Infrastructure Audit — `{target}`\n\n"
                    + summary
                )
                metadata: dict[str, Any] = {
                    "mode": "audit",
                    "target": target,
                    "gaps": len(report.gaps),
                    "proposals": len(report.proposals),
                    "dry_run": report.dry_run,
                }
            else:  # plan
                output = (
                    f"## 🗺️ Reconfiguration Plan — `{target}`\n\n"
                    + summary
                    + "\n\n"
                    + "**Next steps:**\n"
                    + "  1. Review each proposed server in the list above.\n"
                    + "  2. Set `MCPApprovalGate(mode='interactive')` and "
                    + "`IntegrationConfig(dry_run=False)` to apply.\n"
                    + "  3. Re-run with `mode='apply'` to invoke the pipeline.\n"
                )
                metadata = {
                    "mode": "plan",
                    "target": target,
                    "gaps": len(report.gaps),
                    "proposals": len(report.proposals),
                    "estimated_coverage_gain": report.estimated_coverage_gain,
                    "required_human_approvals": report.required_human_approvals,
                    "dry_run": report.dry_run,
                    "report": report.to_dict(),
                }

            return ToolResult(
                call_id=call_id,
                tool_name="reconfigure_infra",
                success=True,
                output=output,
                metadata=metadata,
            )

        # ---- apply: invoke the MCP integration pipeline (dry_run=True) ----
        try:
            from barrot_agent.mcp_integration import MCPIntegration, IntegrationConfig

            cfg = IntegrationConfig(dry_run=True)
            integration = MCPIntegration(cfg)
            stats = integration.run_pipeline()

            output = (
                f"## ⚙️ Infrastructure Pipeline Run — `{target}` (dry_run=True)\n\n"
                "The MCP integration pipeline completed in dry-run mode.\n"
                "No production state was modified — human approval is required "
                "before any server can be promoted.\n\n"
                "**Pipeline stats:**\n"
                + "\n".join(f"  • {k}: {v}" for k, v in stats.items())
            )

            report = build_reconfiguration_report(dry_run=True)
            output += (
                "\n\n**Post-run infrastructure state:**\n"
                + "\n".join(report.summary_lines())
            )

            return ToolResult(
                call_id=call_id,
                tool_name="reconfigure_infra",
                success=True,
                output=output,
                metadata={
                    "mode": "apply",
                    "target": target,
                    "dry_run": True,
                    "pipeline_stats": stats,
                },
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("reconfigure_infra apply error: %s", exc)
            return ToolResult(
                call_id=call_id,
                tool_name="reconfigure_infra",
                success=False,
                output=f"Pipeline error during apply: {exc}",
            )

_PLAN_TEMPLATES: dict[str, list[dict[str, Any]]] = {
    # ---- research / learn ----
    "research": [
        {"title": "Search for existing work", "tool": "search", "tool_args": {"max_results": 3}},
        {"title": "Analyse core concepts", "tool": "analyze", "tool_args": {"depth": "standard"}},
        {"title": "Reason about implications", "tool": "reason", "tool_args": {}},
        {"title": "Summarise findings", "tool": "summarize", "tool_args": {"style": "bullet"}},
    ],
    "learn": [
        {
            "title": "Search for learning resources",
            "tool": "search",
            "tool_args": {"max_results": 3},
        },
        {"title": "Deep-analyse the subject", "tool": "analyze", "tool_args": {"depth": "deep"}},
        {"title": "Reason about key takeaways", "tool": "reason", "tool_args": {}},
        {
            "title": "Produce learning summary",
            "tool": "summarize",
            "tool_args": {"style": "paragraph"},
        },
    ],
    # ---- build / code ----
    "build": [
        {"title": "Analyse requirements", "tool": "analyze", "tool_args": {"depth": "standard"}},
        {"title": "Reason about architecture", "tool": "reason", "tool_args": {}},
        {"title": "Generate code scaffold", "tool": "code", "tool_args": {"language": "python"}},
        {
            "title": "Summarise implementation",
            "tool": "summarize",
            "tool_args": {"style": "bullet"},
        },
    ],
    "code": [
        {"title": "Analyse coding task", "tool": "analyze", "tool_args": {"depth": "quick"}},
        {"title": "Generate implementation", "tool": "code", "tool_args": {"language": "python"}},
        {
            "title": "Summarise code produced",
            "tool": "summarize",
            "tool_args": {"style": "executive"},
        },
    ],
    # ---- analyse / investigate ----
    "analyse": [
        {"title": "Search for background data", "tool": "search", "tool_args": {"max_results": 3}},
        {"title": "Deep-analyse subject", "tool": "analyze", "tool_args": {"depth": "deep"}},
        {"title": "Cross-validate findings", "tool": "reason", "tool_args": {}},
        {
            "title": "Synthesise conclusions",
            "tool": "summarize",
            "tool_args": {"style": "executive"},
        },
    ],
    # ---- explain ----
    "explain": [
        {
            "title": "Search for reference material",
            "tool": "search",
            "tool_args": {"max_results": 3},
        },
        {"title": "Analyse key concepts", "tool": "analyze", "tool_args": {"depth": "standard"}},
        {"title": "Reason about best explanation", "tool": "reason", "tool_args": {}},
        {
            "title": "Produce clear summary",
            "tool": "summarize",
            "tool_args": {"style": "paragraph"},
        },
    ],
    # ---- repo hunt ----
    "repo_hunt": [
        {
            "title": "Hunt for contribution and integration repos",
            "tool": "repo_hunt",
            "tool_args": {"mode": "both"},
        },
        {
            "title": "Reason about top candidates",
            "tool": "reason",
            "tool_args": {},
        },
        {
            "title": "Summarise repo hunt findings",
            "tool": "summarize",
            "tool_args": {"style": "bullet"},
        },
    ],
    # ---- reconfigure / infrastructure ----
    "reconfigure": [
        {
            "title": "Deep-audit current infrastructure state",
            "tool": "analyze",
            "tool_args": {"depth": "deep"},
        },
        {
            "title": "Identify capability gaps and coverage",
            "tool": "reconfigure_infra",
            "tool_args": {"mode": "audit"},
        },
        {
            "title": "Reason about optimal reconfiguration changes",
            "tool": "reason",
            "tool_args": {},
        },
        {
            "title": "Produce structured reconfiguration plan",
            "tool": "reconfigure_infra",
            "tool_args": {"mode": "plan"},
        },
        {
            "title": "Produce executive reconfiguration report",
            "tool": "summarize",
            "tool_args": {"style": "executive"},
        },
    ],
}

_KEYWORD_INTENT_MAP: list[tuple[list[str], str]] = [
    (["research", "find", "discover", "explore", "investigate", "look up"], "research"),
    (["learn", "understand", "study", "read about", "teach me"], "learn"),
    (["build", "create", "make", "implement", "develop", "write a"], "build"),
    (["code", "program", "script", "function", "class", "algorithm"], "code"),
    (["analyse", "analyze", "examine", "evaluate", "assess", "review"], "analyse"),
    (["explain", "describe", "what is", "how does", "define", "tell me"], "explain"),
    (
        [
            "repo hunt",
            "hunt repos",
            "find repos",
            "github repos",
            "integrate with",
            "contribute to",
        ],
        "repo_hunt",
    ),
    (
        [
            "reconfigure",
            "infrastructure",
            "self-modify",
            "upgrade",
            "restructure",
            "reconfig",
            "rebuild infra",
            "optimize infrastructure",
        ],
        "reconfigure",
    ),
]

_DEFAULT_PLAN_KEY = "research"


def _infer_intent(goal: str) -> str:
    """Map a natural-language goal to one of the known plan template keys."""
    goal_lower = goal.lower()
    for keywords, intent in _KEYWORD_INTENT_MAP:
        if any(kw in goal_lower for kw in keywords):
            return intent
    return _DEFAULT_PLAN_KEY


def _build_plan(goal: str) -> list[PlanStep]:
    """Construct a :class:`PlanStep` list for the given goal."""
    intent = _infer_intent(goal)
    template = _PLAN_TEMPLATES[intent]

    steps: list[PlanStep] = []
    for i, tpl in enumerate(template, 1):
        # Fill in tool-specific positional argument from the goal
        args = dict(tpl["tool_args"])
        if tpl["tool"] == "search":
            args.setdefault("query", goal)
        elif tpl["tool"] == "analyze":
            args.setdefault("topic", goal)
        elif tpl["tool"] == "reason":
            args.setdefault("premise", f"Goal: {goal}")
            args.setdefault("objective", tpl["title"])
        elif tpl["tool"] == "code":
            args.setdefault("task", goal)
        elif tpl["tool"] == "repo_hunt":
            args.setdefault("topic", goal)
        elif tpl["tool"] == "reconfigure_infra":
            args.setdefault("target", goal)
        elif tpl["tool"] == "summarize":
            args.setdefault("content", goal)  # will be replaced at runtime with accumulated output

        steps.append(
            PlanStep(
                step_number=i,
                title=tpl["title"],
                description=f"Use the '{tpl['tool']}' tool to {tpl['title'].lower()} for: {goal}",
                tool=tpl["tool"],
                tool_args=args,
            )
        )

    return steps


# ---------------------------------------------------------------------------
# SmartAgent
# ---------------------------------------------------------------------------

_THINKING_TEMPLATES = [
    "Breaking down the goal into manageable sub-tasks…",
    "Identifying the most effective sequence of actions…",
    "Selecting the best tools for each step in the plan…",
    "Validating plan feasibility before execution begins…",
]

_OBSERVATION_TEMPLATES = [
    "Step completed successfully. Integrating result into working context.",
    "Findings recorded. Adjusting remaining steps if necessary.",
    "Tool output assessed — confidence in approach remains high.",
    "Intermediate result aligns with expectations. Continuing execution.",
]


class SmartAgent:
    """
    An autonomous AI agent that decomposes a goal into steps and executes them.

    The agent follows a **plan → act → observe** loop:

    1. **Plan**: Infer intent from the goal and build a step-by-step plan.
    2. **Act**: Execute each step by calling the appropriate built-in tool.
    3. **Observe**: Reflect on each result and adapt if needed.
    4. **Answer**: Consolidate all observations into a final response.

    Parameters
    ----------
    name:
        Display name for this agent instance.
    """

    def __init__(self, name: str = "BarrotSmartAgent") -> None:
        self.name = name
        self._tools = _BuiltinTools()
        self._tool_dispatch: dict[str, Any] = {
            "analyze": self._tools.analyze,
            "search": self._tools.search,
            "reason": self._tools.reason,
            "code": self._tools.code,
            "summarize": self._tools.summarize,
            "repo_hunt": self._tools.repo_hunt,
            "reconfigure_infra": self._tools.reconfigure_infra,
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, goal: str) -> Iterator[AgentEvent]:
        """
        Execute the full plan-act-observe loop for *goal*.

        Yields :class:`AgentEvent` objects as work progresses.  The final
        event has ``type == AgentEventType.ANSWER``.
        """
        goal = goal.strip()
        if not goal:
            yield AgentEvent(
                type=AgentEventType.ERROR,
                content="No goal provided. Please supply a non-empty goal.",
            )
            return

        # 1 — Emit goal event
        yield AgentEvent(
            type=AgentEventType.GOAL,
            content=f"**Goal received:** {goal}",
            data={"goal": goal},
        )

        # 2 — Think / plan
        for i, thinking in enumerate(_THINKING_TEMPLATES, 1):
            yield AgentEvent(
                type=AgentEventType.THINKING,
                content=thinking,
                data={"step": i},
            )

        plan = _build_plan(goal)
        yield AgentEvent(
            type=AgentEventType.PLAN,
            content=self._format_plan(plan),
            data={"steps": [s.to_dict() for s in plan]},
        )

        # 3 — Execute plan
        accumulated_output: list[str] = []
        obs_idx = 0

        for step in plan:
            # Emit action event
            yield AgentEvent(
                type=AgentEventType.ACTION,
                content=(
                    f"**Step {step.step_number}/{len(plan)}: {step.title}**  \n"
                    f"*Tool:* `{step.tool}`  \n"
                    f"{step.description}"
                ),
                data=step.to_dict(),
            )

            # Execute tool
            result = self._call_tool(step, accumulated_output)

            # Emit tool result
            yield AgentEvent(
                type=AgentEventType.TOOL_RESULT,
                content=result.output,
                data={
                    "call_id": result.call_id,
                    "tool": result.tool_name,
                    "success": result.success,
                    "metadata": result.metadata,
                },
            )

            if not result.success:
                yield AgentEvent(
                    type=AgentEventType.ERROR,
                    content=f"Tool `{step.tool}` failed: {result.output}",
                )
                return

            accumulated_output.append(result.output)

            # Emit observation
            obs_text = _OBSERVATION_TEMPLATES[obs_idx % len(_OBSERVATION_TEMPLATES)]
            obs_idx += 1
            yield AgentEvent(
                type=AgentEventType.OBSERVATION,
                content=obs_text,
                data={"step": step.step_number},
            )

        # 4 — Produce final answer
        answer = self._consolidate(goal, plan, accumulated_output)
        yield AgentEvent(
            type=AgentEventType.ANSWER,
            content=answer,
            data={"goal": goal, "steps_executed": len(plan)},
        )

    # ------------------------------------------------------------------
    # Protected hooks — override in subclasses to inject real LLM calls
    # ------------------------------------------------------------------

    def _call_tool(self, step: PlanStep, accumulated: list[str]) -> ToolResult:
        """Execute the tool specified by *step* and return a :class:`ToolResult`."""
        tool_fn = self._tool_dispatch.get(step.tool)
        if tool_fn is None:
            return ToolResult(
                call_id=str(uuid.uuid4())[:8],
                tool_name=step.tool,
                success=False,
                output=f"Unknown tool: {step.tool!r}",
            )

        # For summarize, replace placeholder 'content' with accumulated output
        args = dict(step.tool_args)
        if step.tool == "summarize" and accumulated:
            args["content"] = "\n\n".join(accumulated)

        try:
            return tool_fn(**args)
        except Exception as exc:  # noqa: BLE001
            return ToolResult(
                call_id=str(uuid.uuid4())[:8],
                tool_name=step.tool,
                success=False,
                output=str(exc),
            )

    def _consolidate(self, goal: str, plan: list[PlanStep], outputs: list[str]) -> str:
        """Build the final answer from accumulated tool outputs."""
        lines = [
            f"## ✅ Task Complete",
            f"",
            f"**Goal:** {goal}",
            f"",
            f"**Execution summary:** {len(plan)} steps completed using "
            f"{len({s.tool for s in plan})} distinct tools.",
            f"",
            "---",
            f"",
        ]
        if outputs:
            # Include the last tool output (typically a summarize result) as the body
            lines.append(outputs[-1])
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _format_plan(plan: list[PlanStep]) -> str:
        lines = ["**Execution plan:**", ""]
        for step in plan:
            lines.append(f"{step.step_number}. **{step.title}** — tool: `{step.tool}`")
        return "\n".join(lines)
