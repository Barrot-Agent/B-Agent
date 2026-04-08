"""
DirectivePlatform — top-level orchestrator for the AI Directive Platform.

The platform ties together the AgentRegistry, DirectiveManager, and
SessionManager into a single façade.  When ``run_directive`` is called the
platform:

1. Transitions the directive to *active*.
2. Opens a :class:`~directive_platform.models.CollaborationSession`.
3. Posts an opening message from the human author.
4. Asks each assigned agent to respond in sequence, simulating a real
   multi-agent collaboration (responses are generated from deterministic
   templates parameterised by directive type and agent capabilities).
5. Closes the session and marks the directive *completed*.

The response generation is intentionally lightweight so the platform works
without any external model inference — real inference can be layered on top
by subclassing and overriding ``_agent_response``.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Iterator

from .models import (
    Agent,
    Directive,
    CollaborationSession,
    Message,
    DirectiveStatus,
    AgentStatus,
    MessageType,
    DirectiveType,
)
from .registry import AgentRegistry
from .directives import DirectiveManager
from .session import SessionManager

_PLATFORM_DIR = Path(".directive_platform")


# ---------------------------------------------------------------------------
# Response templates keyed on directive type
# ---------------------------------------------------------------------------

_OPENING: dict[str, str] = {
    DirectiveType.LEARN: (
        "I am commencing a structured learning pass on the topic. I will "
        "systematically absorb available sources, synthesise key concepts, "
        "and surface open questions for further investigation."
    ),
    DirectiveType.REFINE: (
        "Beginning capability refinement analysis. I will audit the current "
        "implementation, identify bottlenecks and gaps, and propose targeted "
        "improvements with measurable benchmarks."
    ),
    DirectiveType.ANALYZE: (
        "Initiating deep structural analysis. I will decompose the subject "
        "into its constituent components, map dependencies, and converge on "
        "a consolidated view of the findings."
    ),
    DirectiveType.COOPERATE: (
        "Standing by to cooperate. I will align my working context with the "
        "other assigned agents, share intermediate findings, and integrate "
        "results into a coherent joint output."
    ),
    DirectiveType.CROSS_CORROBORATE: (
        "Starting cross-corroboration sweep. I will compare data across "
        "independent sources, flag inconsistencies, and produce a confidence-"
        "weighted consensus summary."
    ),
    DirectiveType.PROJECT: (
        "Engaging project mode. I will decompose the directive into "
        "sub-tasks, assign work to the most capable agents, and track "
        "progress toward the stated project goal."
    ),
}

_INSIGHTS: dict[str, list[str]] = {
    DirectiveType.LEARN: [
        "Identified {n} primary knowledge clusters relevant to the topic.",
        "Surfaced {n} open sub-problems that warrant further investigation.",
        "Cross-linked findings with {n} related concepts already in the knowledge base.",
        "Flagged {n} conflicting or outdated claims requiring corroboration.",
    ],
    DirectiveType.REFINE: [
        "Detected {n} performance hot-paths eligible for optimisation.",
        "Catalogued {n} capability gaps against the target specification.",
        "Proposed {n} incremental improvements ordered by expected impact.",
        "Identified {n} regression risks that must be benchmarked before deployment.",
    ],
    DirectiveType.ANALYZE: [
        "Discovered {n} structural patterns across the dataset.",
        "Converged on {n} high-confidence conclusions from the evidence.",
        "Raised {n} anomalies that deviate from expected baselines.",
        "Generated {n} hypotheses for further experimental validation.",
    ],
    DirectiveType.COOPERATE: [
        "Established shared context with {n} co-assigned agents.",
        "Delegated {n} sub-tasks based on declared capabilities.",
        "Resolved {n} conflicting approaches through peer negotiation.",
        "Produced {n} jointly-authored interim deliverables.",
    ],
    DirectiveType.CROSS_CORROBORATE: [
        "Compared {n} independent data sources on the subject.",
        "Confirmed {n} facts with high inter-source agreement.",
        "Flagged {n} discrepancies requiring human adjudication.",
        "Constructed {n} weighted-consensus statements for operator review.",
    ],
    DirectiveType.PROJECT: [
        "Decomposed the directive into {n} concrete sub-tasks.",
        "Assigned sub-tasks to {n} specialist agents.",
        "Completed {n} milestone deliverables ahead of schedule.",
        "Escalated {n} blockers requiring human decision-making.",
    ],
}

_HANDOFF: dict[str, str] = {
    DirectiveType.LEARN: (
        "Knowledge acquisition phase complete. Synthesised summary and "
        "open questions handed off to downstream agents for action."
    ),
    DirectiveType.REFINE: (
        "Refinement proposal package ready. Passing to the next agent for "
        "independent review and prioritisation."
    ),
    DirectiveType.ANALYZE: (
        "Analysis artefacts committed to shared workspace. Handing over to "
        "CorroborationAgent for cross-validation."
    ),
    DirectiveType.COOPERATE: (
        "My contribution to this cooperative task is finalised. "
        "Merging outputs with peer agents."
    ),
    DirectiveType.CROSS_CORROBORATE: (
        "Corroboration pass complete. Consensus report committed. "
        "Escalating flagged discrepancies to the human operator."
    ),
    DirectiveType.PROJECT: (
        "Project milestone reached. Status report and next-steps plan "
        "delivered to the requesting operator."
    ),
}

_CLOSING: dict[str, str] = {
    DirectiveType.LEARN: (
        "All agents have completed their learning passes. A consolidated "
        "knowledge summary is now available. Key open questions have been "
        "logged for follow-up directives."
    ),
    DirectiveType.REFINE: (
        "Capability refinement cycle complete. Improvement proposals from "
        "all agents have been merged and ranked by priority."
    ),
    DirectiveType.ANALYZE: (
        "Analysis convergence achieved. All agents' findings have been "
        "integrated into a unified report."
    ),
    DirectiveType.COOPERATE: (
        "Cooperative session concluded. Joint deliverables have been "
        "finalised and are ready for operator review."
    ),
    DirectiveType.CROSS_CORROBORATE: (
        "Cross-corroboration complete. Consensus statements confirmed. "
        "Discrepancy report forwarded to the human operator."
    ),
    DirectiveType.PROJECT: (
        "Project directive fulfilled. All assigned sub-tasks are complete "
        "and the full deliverable package has been assembled."
    ),
}


class DirectivePlatform:
    """
    Top-level façade for the AI Directive Platform.

    Parameters
    ----------
    platform_dir:
        Root directory for all platform data (agents, directives, sessions).
        Defaults to ``.directive_platform/`` in the current working directory.
    """

    def __init__(self, platform_dir: Path | str | None = None) -> None:
        self._root = Path(platform_dir) if platform_dir else _PLATFORM_DIR
        self._root.mkdir(parents=True, exist_ok=True)

        self.registry = AgentRegistry(self._root / "agents")
        self.directives = DirectiveManager(self._root / "directives")
        self.sessions = SessionManager(self._root / "sessions")

    @property
    def platform_dir(self) -> Path:
        return self._root

    # ------------------------------------------------------------------
    # Primary operations
    # ------------------------------------------------------------------

    def issue_directive(
        self,
        *,
        title: str,
        description: str,
        directive_type: str,
        agent_ids: list[str],
        human_author: str,
    ) -> Directive:
        """
        Create a new directive and return it in *pending* state.

        The directive is not started until :meth:`run_directive` is called.
        """
        directive = self.directives.create(
            title=title,
            description=description,
            directive_type=directive_type,
            assigned_agent_ids=agent_ids,
            human_author=human_author,
        )
        return directive

    def run_directive(self, directive_id: str) -> CollaborationSession:
        """
        Execute a directive synchronously and return the completed session.

        All agent responses are generated via :meth:`_agent_response` and
        appended to the session before it is closed.  The directive is
        transitioned from *pending* → *active* → *completed* (or *failed*
        on error).
        """
        directive = self.directives.get(directive_id)
        if directive is None:
            raise ValueError(f"Directive {directive_id!r} not found.")

        self.directives.update_status(directive_id, DirectiveStatus.ACTIVE)
        agents = [
            a for aid in directive.assigned_agent_ids
            if (a := self.registry.get(aid)) is not None
        ]
        participant_ids = ["human"] + [a.agent_id for a in agents]
        session = self.sessions.create_session(directive_id, participant_ids)

        try:
            # Mark agents as active
            for agent in agents:
                self.registry.update_status(
                    agent.agent_id, AgentStatus.ACTIVE, directive_id
                )

            # Human opening message
            self._post(session, Message(
                session_id=session.session_id,
                sender_id="human",
                sender_name=directive.human_author,
                content=(
                    f"**Directive issued:** {directive.title}\n\n"
                    f"{directive.description}"
                ),
                message_type=MessageType.DIRECTIVE,
            ))

            # Each agent contributes
            for i, agent in enumerate(agents):
                for msg in self._agent_turn(session, agent, directive, i, len(agents)):
                    self._post(session, msg)
                    time.sleep(0)  # yield to event loop if called from async context

            # Closing summary (posted as the platform / system)
            self._post(session, Message(
                session_id=session.session_id,
                sender_id="platform",
                sender_name="Platform",
                content=_CLOSING.get(
                    directive.directive_type,
                    "All assigned agents have completed their contributions.",
                ),
                message_type=MessageType.RESULT,
            ))

            # Record result on the directive
            self.directives.add_result(directive_id, {
                "session_id": session.session_id,
                "agents": [a.agent_id for a in agents],
                "messages": len(session.messages),
            })
            self.directives.update_status(directive_id, DirectiveStatus.COMPLETED)
            self.sessions.close_session(session.session_id, "completed")

        except Exception as exc:  # noqa: BLE001
            self.directives.update_status(directive_id, DirectiveStatus.FAILED)
            self.sessions.close_session(session.session_id, "failed")
            raise

        finally:
            # Release agents
            for agent in agents:
                self.registry.update_status(agent.agent_id, AgentStatus.IDLE, None)

        return self.sessions.get_session(session.session_id) or session

    def run_directive_streaming(
        self, directive_id: str
    ) -> Iterator[tuple[Message, CollaborationSession]]:
        """
        Execute a directive and *yield* ``(message, session)`` tuples as each
        message is produced.  Useful for driving a streaming UI.

        The directive lifecycle (status transitions, agent status updates,
        persistence) is identical to :meth:`run_directive`.
        """
        directive = self.directives.get(directive_id)
        if directive is None:
            raise ValueError(f"Directive {directive_id!r} not found.")

        self.directives.update_status(directive_id, DirectiveStatus.ACTIVE)
        agents = [
            a for aid in directive.assigned_agent_ids
            if (a := self.registry.get(aid)) is not None
        ]
        participant_ids = ["human"] + [a.agent_id for a in agents]
        session = self.sessions.create_session(directive_id, participant_ids)

        try:
            for agent in agents:
                self.registry.update_status(
                    agent.agent_id, AgentStatus.ACTIVE, directive_id
                )

            opening = Message(
                session_id=session.session_id,
                sender_id="human",
                sender_name=directive.human_author,
                content=(
                    f"**Directive issued:** {directive.title}\n\n"
                    f"{directive.description}"
                ),
                message_type=MessageType.DIRECTIVE,
            )
            self._post(session, opening)
            yield opening, session

            for i, agent in enumerate(agents):
                for msg in self._agent_turn(session, agent, directive, i, len(agents)):
                    self._post(session, msg)
                    yield msg, session

            closing = Message(
                session_id=session.session_id,
                sender_id="platform",
                sender_name="Platform",
                content=_CLOSING.get(
                    directive.directive_type,
                    "All assigned agents have completed their contributions.",
                ),
                message_type=MessageType.RESULT,
            )
            self._post(session, closing)
            yield closing, session

            self.directives.add_result(directive_id, {
                "session_id": session.session_id,
                "agents": [a.agent_id for a in agents],
                "messages": len(session.messages),
            })
            self.directives.update_status(directive_id, DirectiveStatus.COMPLETED)
            self.sessions.close_session(session.session_id, "completed")

        except Exception:
            self.directives.update_status(directive_id, DirectiveStatus.FAILED)
            self.sessions.close_session(session.session_id, "failed")
            raise

        finally:
            for agent in agents:
                self.registry.update_status(agent.agent_id, AgentStatus.IDLE, None)

    # ------------------------------------------------------------------
    # Agent response generation
    # ------------------------------------------------------------------

    def _agent_turn(
        self,
        session: CollaborationSession,
        agent: Agent,
        directive: Directive,
        agent_index: int,
        total_agents: int,
    ) -> list[Message]:
        """
        Generate the sequence of messages for a single agent's contribution.

        Override this method in a subclass to plug in real model inference.
        """
        messages: list[Message] = []
        dtype = directive.directive_type

        # Opening acknowledgement
        opening_text = _OPENING.get(dtype, "Acknowledged. Beginning work on directive.")
        messages.append(Message(
            session_id=session.session_id,
            sender_id=agent.agent_id,
            sender_name=agent.name,
            content=opening_text,
            message_type=MessageType.RESPONSE,
        ))

        # Insights (one per applicable template)
        templates = _INSIGHTS.get(dtype, [
            "Processed {n} data points relevant to the directive.",
        ])
        for idx, template in enumerate(templates):
            n = 3 + (idx * 2) + agent_index
            messages.append(Message(
                session_id=session.session_id,
                sender_id=agent.agent_id,
                sender_name=agent.name,
                content=template.format(n=n),
                message_type=MessageType.INSIGHT,
            ))

        # Handoff (if not the last agent)
        if agent_index < total_agents - 1:
            handoff_text = _HANDOFF.get(
                dtype,
                "Contribution complete. Handing off to the next agent.",
            )
            messages.append(Message(
                session_id=session.session_id,
                sender_id=agent.agent_id,
                sender_name=agent.name,
                content=handoff_text,
                message_type=MessageType.HANDOFF,
            ))
        else:
            messages.append(Message(
                session_id=session.session_id,
                sender_id=agent.agent_id,
                sender_name=agent.name,
                content=(
                    "My contribution to this directive is complete. "
                    "Results are committed to the session log."
                ),
                message_type=MessageType.RESULT,
            ))

        return messages

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _post(self, session: CollaborationSession, message: Message) -> None:
        """Append *message* to *session* both in memory and on disk."""
        session.messages.append(message)
        self.sessions.update_session(session)
