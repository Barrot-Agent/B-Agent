"""OpenShell runtime wrapper — integrates policy enforcement into any agent."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from openshell.policy_manager import PolicyManager
from barrot_agent.security.policy_engine import PolicyDecision, PolicyEngine
from barrot_agent.security.audit_logger import SecurityAuditLogger

logger = logging.getLogger(__name__)


class PolicyViolationError(Exception):
    """Raised when an agent action violates the active security policy."""


class OpenShellRuntime:
    """Framework-agnostic wrapper that enforces OpenShell policies on agents.

    Usage::

        runtime = OpenShellRuntime("openshell/policies")
        runtime.initialize()

        @runtime.wrap_agent
        def my_agent(prompt: str) -> str:
            return "hello"

        result = my_agent("test")

    Or imperatively::

        result = runtime.execute_with_policy(
            action="network_request",
            context={"domain": "huggingface.co"},
            agent_id="inference_agent",
        )
    """

    def __init__(
        self,
        policy_path: str,
        config_path: Optional[str] = None,
    ) -> None:
        self._policy_path = policy_path
        self._config_path = config_path
        self._policy_manager: Optional[PolicyManager] = None
        self._policy_engine: Optional[PolicyEngine] = None
        self._audit_logger = SecurityAuditLogger(agent_id="runtime")
        self._stats: Dict[str, int] = {
            "actions_allowed": 0,
            "actions_blocked": 0,
            "agents_wrapped": 0,
        }
        self._initialized = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        """Load policies and prepare the policy engine.

        Must be called before :meth:`wrap_agent` or
        :meth:`execute_with_policy`.
        """
        self._policy_manager = PolicyManager(
            policy_directory=self._policy_path,
            hot_reload=True,
            hot_reload_interval=60,
        )
        self._policy_manager.load_all()

        # Build a merged policy view for the engine
        merged_policy = self._build_merged_policy()
        self._policy_engine = PolicyEngine(merged_policy)
        self._initialized = True
        logger.info("OpenShellRuntime initialised from '%s'", self._policy_path)

    def shutdown(self) -> None:
        """Tear down background threads."""
        if self._policy_manager:
            self._policy_manager.shutdown()
        self._initialized = False
        logger.info("OpenShellRuntime shut down")

    # ------------------------------------------------------------------
    # Agent wrapping
    # ------------------------------------------------------------------

    def wrap_agent(self, agent_callable: Callable) -> Callable:
        """Decorator that injects policy enforcement around *agent_callable*.

        The wrapper checks ``execute_code`` permission for the calling agent
        (identified by the callable's ``__name__``) before each invocation.

        Args:
            agent_callable: Any callable that represents an agent action.

        Returns:
            A wrapped callable with identical signature.
        """
        self._stats["agents_wrapped"] += 1
        runtime = self

        def _wrapped(*args: Any, **kwargs: Any) -> Any:
            agent_id = agent_callable.__name__
            decision = runtime.execute_with_policy(
                action="execute_code",
                context={"callable": agent_id},
                agent_id=agent_id,
            )
            if not decision.allowed:
                raise PolicyViolationError(
                    f"Agent '{agent_id}' blocked: {decision.reason}"
                )
            return agent_callable(*args, **kwargs)

        _wrapped.__name__ = agent_callable.__name__
        _wrapped.__doc__ = agent_callable.__doc__
        return _wrapped

    # ------------------------------------------------------------------
    # Policy execution
    # ------------------------------------------------------------------

    def execute_with_policy(
        self,
        action: str,
        context: Dict[str, Any],
        agent_id: str,
    ) -> PolicyDecision:
        """Evaluate whether *agent_id* may perform *action* given *context*.

        Args:
            action:   The action name (maps to ``api_restrictions.method``).
            context:  Contextual data passed to the policy engine.
            agent_id: Requesting agent identifier.

        Returns:
            A :class:`~barrot_agent.security.policy_engine.PolicyDecision`.

        Raises:
            RuntimeError: If :meth:`initialize` has not been called.
        """
        if not self._initialized or self._policy_engine is None:
            raise RuntimeError("OpenShellRuntime.initialize() must be called first")

        decision = self._policy_engine.evaluate_action(action, agent_id, context)

        if decision.allowed:
            self._stats["actions_allowed"] += 1
            self._audit_logger.log_execution(
                command=f"action:{action}",
                result={"returncode": 0},
                agent_id=agent_id,
            )
        else:
            self._stats["actions_blocked"] += 1
            self._audit_logger.log_policy_violation(
                violation={"action": action, "reason": decision.reason},
                agent_id=agent_id,
            )
        return decision

    def get_runtime_stats(self) -> Dict[str, Any]:
        """Return a snapshot of runtime statistics."""
        stats = dict(self._stats)
        stats["policies_loaded"] = (
            len(self._policy_manager.list_policies())
            if self._policy_manager
            else 0
        )
        return stats

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_merged_policy(self) -> Dict[str, Any]:
        """Merge all loaded policies into a single view for the engine."""
        assert self._policy_manager is not None
        merged: Dict[str, Any] = {
            "policy_name": "merged",
            "version": "1.0",
            "enforcement_mode": "strict",
            "allowed_binaries": [],
            "network_rules": {"allow_domains": [], "deny_all_other": True},
            "filesystem_permissions": [],
            "api_restrictions": [],
        }
        for name in self._policy_manager.list_policies():
            policy = self._policy_manager.get_policy(name)
            merged["allowed_binaries"].extend(
                policy.get("allowed_binaries", [])
            )
            merged["api_restrictions"].extend(
                policy.get("api_restrictions", [])
            )
            merged["filesystem_permissions"].extend(
                policy.get("filesystem_permissions", [])
            )
            net = policy.get("network_rules", {})
            merged["network_rules"]["allow_domains"].extend(
                net.get("allow_domains", [])
            )
        return merged
