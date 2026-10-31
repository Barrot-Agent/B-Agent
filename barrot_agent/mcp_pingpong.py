"""
MCP Ping-Pong – Step 5
=======================
Implements proposal exchange, critique, testing, and refinement between
specialised agents using the existing Ping-Pongings protocol
(``ping-pongings/protocols/ping-pongings-protocol.md``).

A *proposal* is a candidate MCP integration.  The Proposer agent drafts
it; the Critic agent evaluates it; the Refiner iterates.  Each round is
recorded as an immutable exchange object.
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Domain types
# ---------------------------------------------------------------------------


class Phase(str, Enum):
    PROPOSAL = "proposal"
    CRITIQUE = "critique"
    REFINEMENT = "refinement"
    ACCEPTANCE = "acceptance"
    REJECTION = "rejection"


@dataclass
class MCPProposal:
    """A candidate integration package proposed for adoption."""

    server_id: str
    description: str
    score: float
    adapter_class: str
    rationale: str
    risks: List[str] = field(default_factory=list)
    mitigations: List[str] = field(default_factory=list)
    proposal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class PingPongMessage:
    """A single message in a ping-pong exchange."""

    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    phase: Phase = Phase.PROPOSAL
    sender: str = "proposer"
    receiver: str = "critic"
    payload: Dict[str, Any] = field(default_factory=dict)
    round_number: int = 1


@dataclass
class ExchangeRecord:
    """Full record of a ping-pong exchange for one proposal."""

    proposal: MCPProposal
    messages: List[PingPongMessage] = field(default_factory=list)
    final_phase: Phase = Phase.PROPOSAL
    cycles: int = 0
    exchange_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "exchange_id": self.exchange_id,
            "proposal_id": self.proposal.proposal_id,
            "server_id": self.proposal.server_id,
            "final_phase": self.final_phase.value,
            "cycles": self.cycles,
            "messages": [
                {
                    "message_id": m.message_id,
                    "phase": m.phase.value,
                    "sender": m.sender,
                    "receiver": m.receiver,
                    "round": m.round_number,
                    "payload": m.payload,
                }
                for m in self.messages
            ],
        }


# ---------------------------------------------------------------------------
# Agent roles (pluggable callables)
# ---------------------------------------------------------------------------

ProposerFn = Callable[[MCPProposal], Dict[str, Any]]
CriticFn = Callable[[MCPProposal, Dict[str, Any]], Dict[str, Any]]
RefinerFn = Callable[[MCPProposal, Dict[str, Any]], MCPProposal]


def _default_proposer(proposal: MCPProposal) -> Dict[str, Any]:
    """Default proposer: serialise the proposal as the initial payload."""
    return {
        "server_id": proposal.server_id,
        "score": proposal.score,
        "adapter_class": proposal.adapter_class,
        "rationale": proposal.rationale,
        "risks": proposal.risks,
        "mitigations": proposal.mitigations,
    }


def _default_critic(proposal: MCPProposal, proposer_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Default critic: apply simple heuristic rules.

    - Score < 40 → reject.
    - Unmitigated risks → request refinement.
    - Otherwise → accept.
    """
    score = proposer_payload.get("score", 0.0)
    risks = proposer_payload.get("risks", [])
    mitigations = proposer_payload.get("mitigations", [])

    issues: List[str] = []
    if score < 40:
        issues.append(f"Score {score:.1f} is below the acceptance threshold of 40.")
    unmitigated = [r for r in risks if r not in " ".join(mitigations)]
    if unmitigated:
        issues.append(f"Unmitigated risks: {unmitigated}")

    if issues:
        verdict = "needs_refinement" if score >= 40 else "reject"
    else:
        verdict = "accept"

    return {"verdict": verdict, "issues": issues}


def _default_refiner(proposal: MCPProposal, critique: Dict[str, Any]) -> MCPProposal:
    """Default refiner: add generic mitigations for each reported issue."""
    issues = critique.get("issues", [])
    extra_mitigations = [f"Addressed: {issue}" for issue in issues]
    from dataclasses import replace

    return replace(
        proposal,
        mitigations=proposal.mitigations + extra_mitigations,
    )


# ---------------------------------------------------------------------------
# Ping-Pong engine
# ---------------------------------------------------------------------------


class MCPPingPong:
    """
    Coordinates proposal→critique→refinement→acceptance cycles.

    Usage::

        engine = MCPPingPong(max_cycles=3)
        record = engine.run(proposal)
        if record.final_phase == Phase.ACCEPTANCE:
            ...  # proceed to sandbox
    """

    def __init__(
        self,
        max_cycles: int = 3,
        proposer: Optional[ProposerFn] = None,
        critic: Optional[CriticFn] = None,
        refiner: Optional[RefinerFn] = None,
    ) -> None:
        self._max_cycles = max_cycles
        self._proposer: ProposerFn = proposer or _default_proposer
        self._critic: CriticFn = critic or _default_critic
        self._refiner: RefinerFn = refiner or _default_refiner

    def run(self, proposal: MCPProposal) -> ExchangeRecord:
        """
        Execute the full ping-pong cycle for *proposal*.

        Returns an :class:`ExchangeRecord` with ``final_phase`` set to
        :attr:`Phase.ACCEPTANCE` or :attr:`Phase.REJECTION`.
        """
        record = ExchangeRecord(proposal=proposal)
        current_proposal = proposal

        for cycle in range(1, self._max_cycles + 1):
            record.cycles = cycle
            logger.info(
                "Ping-pong cycle %d/%d for server=%s",
                cycle,
                self._max_cycles,
                proposal.server_id,
            )

            # ---- PING: Proposer ----
            proposer_payload = self._proposer(current_proposal)
            record.messages.append(
                PingPongMessage(
                    phase=Phase.PROPOSAL,
                    sender="proposer",
                    receiver="critic",
                    payload=proposer_payload,
                    round_number=cycle,
                )
            )

            # ---- PONG: Critic ----
            critique = self._critic(current_proposal, proposer_payload)
            record.messages.append(
                PingPongMessage(
                    phase=Phase.CRITIQUE,
                    sender="critic",
                    receiver="proposer",
                    payload=critique,
                    round_number=cycle,
                )
            )

            verdict = critique.get("verdict", "reject")

            if verdict == "accept":
                record.final_phase = Phase.ACCEPTANCE
                logger.info(
                    "Proposal accepted for server=%s after %d cycle(s)",
                    proposal.server_id,
                    cycle,
                )
                break

            if verdict == "reject":
                record.final_phase = Phase.REJECTION
                logger.info(
                    "Proposal rejected for server=%s after %d cycle(s)",
                    proposal.server_id,
                    cycle,
                )
                break

            # needs_refinement → refine and loop
            current_proposal = self._refiner(current_proposal, critique)
            record.messages.append(
                PingPongMessage(
                    phase=Phase.REFINEMENT,
                    sender="proposer",
                    receiver="critic",
                    payload={
                        "updated_mitigations": current_proposal.mitigations,
                    },
                    round_number=cycle,
                )
            )
        else:
            # Exhausted max cycles without acceptance
            record.final_phase = Phase.REJECTION
            logger.warning(
                "Proposal for server=%s exhausted %d cycles without acceptance.",
                proposal.server_id,
                self._max_cycles,
            )

        return record

    def run_batch(self, proposals: List[MCPProposal]) -> List[ExchangeRecord]:
        """Run ping-pong for every proposal in *proposals*."""
        return [self.run(p) for p in proposals]
