"""
MCP Approval Gate – Step 7
===========================
Requires explicit human approval before installation, repository writes,
workflow execution, or production deployment.

The gate is *blocking*: nothing proceeds until a human (or an authorised
automated proxy with a signed token) explicitly approves the action.

In CI / headless mode the gate can read approval from an environment
variable ``MCP_APPROVAL_TOKEN`` that must match a pre-registered value.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Domain types
# ---------------------------------------------------------------------------


class ActionType(str, Enum):
    INSTALL = "install"
    REPO_WRITE = "repo_write"
    WORKFLOW_EXECUTION = "workflow_execution"
    PRODUCTION_DEPLOY = "production_deploy"
    REGISTRY_PROMOTE = "registry_promote"


@dataclass
class ApprovalRequest:
    """A pending action that requires human approval."""

    action_type: ActionType
    server_id: str
    description: str
    requested_by: str = "barrot-agent"
    request_id: str = field(default_factory=lambda: hashlib.sha256(os.urandom(16)).hexdigest()[:16])
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ApprovalDecision:
    """The outcome of a human review of an :class:`ApprovalRequest`."""

    request_id: str
    approved: bool
    decided_by: str
    reason: str = ""
    decided_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ---------------------------------------------------------------------------
# Approval gate
# ---------------------------------------------------------------------------


class MCPApprovalGate:
    """
    Human-in-the-loop gate for sensitive MCP operations.

    Modes
    -----
    interactive
        Prompts the user on stdin/stdout.  Suitable for local development.
    env_token
        Reads ``MCP_APPROVAL_TOKEN`` from the environment and compares it
        against a pre-registered HMAC.  Suitable for CI pipelines.
    always_deny
        Blocks all operations.  Safe default when no auth is configured.
    """

    ENV_TOKEN_VAR = "MCP_APPROVAL_TOKEN"
    ENV_TOKEN_SECRET = "MCP_APPROVAL_SECRET"

    def __init__(
        self,
        mode: str = "always_deny",
        interactive: bool = False,
    ) -> None:
        self._mode = mode
        self._interactive = interactive
        self._decisions: List[ApprovalDecision] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def request_approval(self, req: ApprovalRequest) -> ApprovalDecision:
        """
        Submit *req* and block until a decision is reached.

        Returns an :class:`ApprovalDecision`.  The caller MUST check
        ``decision.approved`` before proceeding.
        """
        logger.info(
            "Approval requested: action=%s server=%s id=%s",
            req.action_type.value,
            req.server_id,
            req.request_id,
        )

        if self._mode == "interactive" and self._interactive:
            decision = self._interactive_prompt(req)
        elif self._mode == "env_token":
            decision = self._env_token_check(req)
        else:
            # always_deny (safe default)
            decision = ApprovalDecision(
                request_id=req.request_id,
                approved=False,
                decided_by="system",
                reason=(
                    "Approval gate is in 'always_deny' mode. "
                    "Configure MCP_APPROVAL_TOKEN and MCP_APPROVAL_SECRET "
                    "or enable interactive mode."
                ),
            )

        self._decisions.append(decision)
        if decision.approved:
            logger.info(
                "APPROVED: action=%s server=%s by=%s",
                req.action_type.value,
                req.server_id,
                decision.decided_by,
            )
        else:
            logger.warning(
                "DENIED: action=%s server=%s reason=%s",
                req.action_type.value,
                req.server_id,
                decision.reason,
            )
        return decision

    def get_decisions(self) -> List[ApprovalDecision]:
        """Return all decisions recorded so far (read-only copy)."""
        return list(self._decisions)

    # ------------------------------------------------------------------
    # Gate implementations
    # ------------------------------------------------------------------

    def _interactive_prompt(self, req: ApprovalRequest) -> ApprovalDecision:
        print(
            f"\n{'='*60}\n"
            f"APPROVAL REQUIRED\n"
            f"{'='*60}\n"
            f"Action   : {req.action_type.value}\n"
            f"Server   : {req.server_id}\n"
            f"Details  : {req.description}\n"
            f"Request  : {req.request_id}\n"
            f"{'='*60}"
        )
        try:
            answer = input("Approve? [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            answer = "n"
        approved = answer in ("y", "yes")
        return ApprovalDecision(
            request_id=req.request_id,
            approved=approved,
            decided_by="human-interactive",
            reason="Interactive approval." if approved else "Interactive denial.",
        )

    def _env_token_check(self, req: ApprovalRequest) -> ApprovalDecision:
        """
        Validate ``MCP_APPROVAL_TOKEN`` against an HMAC of the request_id.

        Expected token = HMAC-SHA256(secret, request_id).
        The secret must be set in ``MCP_APPROVAL_SECRET``.
        """
        secret = os.environ.get(self.ENV_TOKEN_SECRET, "")
        provided_token = os.environ.get(self.ENV_TOKEN_VAR, "")

        if not secret:
            return ApprovalDecision(
                request_id=req.request_id,
                approved=False,
                decided_by="system",
                reason=f"Environment variable {self.ENV_TOKEN_SECRET} is not set.",
            )

        expected = hmac.new(
            secret.encode(),
            req.request_id.encode(),
            "sha256",
        ).hexdigest()

        if hmac.compare_digest(provided_token, expected):
            return ApprovalDecision(
                request_id=req.request_id,
                approved=True,
                decided_by="env-token",
                reason="Valid MCP_APPROVAL_TOKEN presented.",
            )

        return ApprovalDecision(
            request_id=req.request_id,
            approved=False,
            decided_by="system",
            reason="Invalid or missing MCP_APPROVAL_TOKEN.",
        )
