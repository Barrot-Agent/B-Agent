"""Policy evaluation engine — decides whether agent actions are permitted."""

from __future__ import annotations

import fnmatch
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class PolicyDecision:
    """Container for a single policy evaluation outcome."""

    __slots__ = ("allowed", "policy_name", "reason", "log_level")

    def __init__(
        self,
        allowed: bool,
        policy_name: str = "default",
        reason: str = "",
        log_level: str = "info",
    ) -> None:
        self.allowed = allowed
        self.policy_name = policy_name
        self.reason = reason
        self.log_level = log_level

    def as_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "policy_name": self.policy_name,
            "reason": self.reason,
            "log_level": self.log_level,
        }


class PolicyEngine:
    """Evaluate security policies for agent actions.

    The engine works against a policy dict loaded externally (e.g. via
    ``PolicyManager``).  It exposes granular check methods for network, file-
    system, binary, and API access, as well as a general ``evaluate_action``
    entry point.

    Example::

        engine = PolicyEngine(policy)
        decision = engine.evaluate_action("network_request", "inference_agent", {})
        if not decision.allowed:
            raise PermissionError(decision.reason)
    """

    _DEFAULT_DENY = PolicyDecision(
        allowed=False,
        policy_name="default",
        reason="No matching rule; deny-by-default",
    )

    def __init__(self, policy: Optional[Dict[str, Any]] = None) -> None:
        self._policy: Dict[str, Any] = policy or {}

    def load_policy(self, policy: Dict[str, Any]) -> None:
        """Replace the active policy dict."""
        self._policy = policy

    # ------------------------------------------------------------------
    # High-level evaluation
    # ------------------------------------------------------------------

    def evaluate_action(
        self,
        action_type: str,
        agent_id: str,
        context: Dict[str, Any],
    ) -> PolicyDecision:
        """Determine whether *agent_id* may perform *action_type*.

        Checks ``api_restrictions`` entries in the loaded policy.

        Args:
            action_type: The method / action name (e.g. ``"network_request"``).
            agent_id:    Identifier of the requesting agent.
            context:     Additional contextual data (currently advisory).

        Returns:
            A :class:`PolicyDecision` instance.
        """
        restrictions: List[Dict[str, Any]] = self._policy.get("api_restrictions", [])
        policy_name: str = self._policy.get("policy_name", "unknown")

        for restriction in restrictions:
            if restriction.get("method") != action_type:
                continue
            allowed_agents: List[str] = restriction.get("allow_from", [])
            log_level: str = restriction.get("log_level", "info")
            if agent_id in allowed_agents:
                return PolicyDecision(
                    allowed=True,
                    policy_name=policy_name,
                    reason=f"Agent '{agent_id}' explicitly allowed for '{action_type}'",
                    log_level=log_level,
                )
            return PolicyDecision(
                allowed=False,
                policy_name=policy_name,
                reason=(
                    f"Agent '{agent_id}' not authorised for '{action_type}'; "
                    f"allowed agents: {allowed_agents}"
                ),
                log_level=log_level,
            )

        # No restriction rule matched
        mode = self._policy.get("enforcement_mode", "strict")
        if mode == "strict":
            return PolicyDecision(
                allowed=False,
                policy_name=policy_name,
                reason=f"No rule for '{action_type}'; strict mode denies by default",
            )
        return PolicyDecision(
            allowed=True,
            policy_name=policy_name,
            reason=f"No rule for '{action_type}'; permissive mode allows by default",
        )

    def check_network_permission(
        self, domain: str, agent_id: str
    ) -> PolicyDecision:
        """Check whether *agent_id* may reach *domain*.

        Evaluates ``network_rules.allow_domains`` with glob matching.
        """
        policy_name = self._policy.get("policy_name", "unknown")
        network_rules: Dict[str, Any] = self._policy.get("network_rules", {})
        allowed_domains: List[str] = network_rules.get("allow_domains", [])
        deny_all: bool = network_rules.get("deny_all_other", True)

        for pattern in allowed_domains:
            if fnmatch.fnmatch(domain, pattern) or domain.endswith(f".{pattern}"):
                return PolicyDecision(
                    allowed=True,
                    policy_name=policy_name,
                    reason=f"Domain '{domain}' matches allow pattern '{pattern}'",
                )

        if deny_all:
            return PolicyDecision(
                allowed=False,
                policy_name=policy_name,
                reason=f"Domain '{domain}' not in allow list; deny_all_other=true",
            )
        return PolicyDecision(
            allowed=True,
            policy_name=policy_name,
            reason=f"Domain '{domain}' not in allow list; deny_all_other=false",
        )

    def check_filesystem_permission(
        self, path: str, access_type: str, agent_id: str
    ) -> PolicyDecision:
        """Check whether *access_type* is permitted on *path* for *agent_id*.

        Evaluates ``filesystem_permissions`` entries; longest prefix wins.

        Args:
            path:        File-system path being accessed.
            access_type: One of ``"read"``, ``"write"``, ``"append"``.
            agent_id:    Requesting agent.
        """
        policy_name = self._policy.get("policy_name", "unknown")
        fs_perms: List[Dict[str, Any]] = self._policy.get(
            "filesystem_permissions", []
        )

        best_match: Optional[Dict[str, Any]] = None
        for entry in fs_perms:
            entry_path: str = entry.get("path", "")
            if path.startswith(entry_path):
                if best_match is None or len(entry_path) > len(
                    best_match.get("path", "")
                ):
                    best_match = entry

        if best_match is None:
            return PolicyDecision(
                allowed=False,
                policy_name=policy_name,
                reason=f"No filesystem rule covers path '{path}'",
            )

        access_mode: str = best_match.get("access", "none")
        allowed = _access_mode_allows(access_mode, access_type)
        return PolicyDecision(
            allowed=allowed,
            policy_name=policy_name,
            reason=(
                f"Path '{path}' matched rule '{best_match['path']}' "
                f"with access={access_mode}; request={access_type}"
            ),
        )

    def check_binary_permission(
        self, binary: str, agent_id: str
    ) -> PolicyDecision:
        """Check whether *binary* is in the allowed binaries whitelist."""
        policy_name = self._policy.get("policy_name", "unknown")
        allowed: List[str] = self._policy.get("allowed_binaries", [])
        if binary in allowed:
            return PolicyDecision(
                allowed=True,
                policy_name=policy_name,
                reason=f"Binary '{binary}' is whitelisted",
            )
        return PolicyDecision(
            allowed=False,
            policy_name=policy_name,
            reason=f"Binary '{binary}' not in allowed_binaries whitelist",
        )

    def check_api_permission(self, method: str, agent_id: str) -> PolicyDecision:
        """Alias for :meth:`evaluate_action` for clarity at call sites."""
        return self.evaluate_action(method, agent_id, {})

    def get_policy_decision(self, request: Dict[str, Any]) -> PolicyDecision:
        """Unified entry point — dispatch to the appropriate check method.

        ``request`` must contain ``"request_type"`` and ``"agent_id"``.  Valid
        ``request_type`` values: ``"network"``, ``"filesystem"``, ``"binary"``,
        ``"api"``, ``"action"``.

        Additional keys depend on ``request_type``:

        * ``network`` → ``domain``
        * ``filesystem`` → ``path``, ``access_type``
        * ``binary`` → ``binary``
        * ``api`` / ``action`` → ``method`` or ``action_type``
        """
        rtype = request.get("request_type", "action")
        agent_id = request.get("agent_id", "")

        if rtype == "network":
            return self.check_network_permission(
                request.get("domain", ""), agent_id
            )
        if rtype == "filesystem":
            return self.check_filesystem_permission(
                request.get("path", ""),
                request.get("access_type", "read"),
                agent_id,
            )
        if rtype == "binary":
            return self.check_binary_permission(
                request.get("binary", ""), agent_id
            )
        # Default: API / action check
        action = request.get("method") or request.get("action_type", "")
        return self.evaluate_action(action, agent_id, request)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _access_mode_allows(mode: str, request: str) -> bool:
    """Return True when *mode* grants the *request* access level."""
    if mode == "none":
        return False
    if mode == "read_only":
        return request in ("read",)
    if mode == "read_write":
        return request in ("read", "write", "append")
    if mode == "append":
        return request in ("read", "append")
    return False
