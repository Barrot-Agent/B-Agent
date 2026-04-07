"""Per-agent sandbox — context manager that enforces resource limits per agent."""

from __future__ import annotations

import resource
import threading
import time
from typing import Any, Callable, Dict, Optional


class SandboxError(Exception):
    """Raised when a sandboxed execution fails due to a policy or resource error."""


class AgentSandbox:
    """Context manager that applies resource limits for a single agent session.

    Usage::

        sandbox = AgentSandbox(
            agent_id="inference_agent",
            policy={"enforcement_mode": "strict"},
            resource_limits={"max_memory_mb": 2048, "max_cpu_percent": 80},
        )
        with sandbox:
            result = sandbox.execute(my_function, arg1, kwarg=value)
    """

    def __init__(
        self,
        agent_id: str,
        policy: Optional[Dict[str, Any]] = None,
        resource_limits: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._agent_id = agent_id
        self._policy = policy or {}
        self._resource_limits = resource_limits or {}
        self._active = False
        self._stats: Dict[str, Any] = {
            "agent_id": agent_id,
            "executions": 0,
            "errors": 0,
            "total_elapsed_seconds": 0.0,
            "enter_count": 0,
        }
        self._lock = threading.Lock()
        self._saved_limits: Dict[int, tuple] = {}

    # ------------------------------------------------------------------
    # Context manager protocol
    # ------------------------------------------------------------------

    def __enter__(self) -> "AgentSandbox":
        self.enter()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        self.exit()
        return False  # Do not suppress exceptions

    def enter(self) -> None:
        """Activate the sandbox, applying resource limits to the current process."""
        with self._lock:
            self._active = True
            self._stats["enter_count"] += 1
        self._apply_resource_limits()

    def exit(self) -> None:
        """Deactivate the sandbox, restoring previous resource limits."""
        self._restore_resource_limits()
        with self._lock:
            self._active = False

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(self, callable_fn: Callable, *args: Any, **kwargs: Any) -> Any:
        """Run *callable_fn* inside the sandbox.

        Args:
            callable_fn: Function to execute.
            *args:        Positional arguments forwarded to *callable_fn*.
            **kwargs:     Keyword arguments forwarded to *callable_fn*.

        Returns:
            The return value of *callable_fn*.

        Raises:
            SandboxError: When the callable raises an exception.
        """
        if not self._active:
            raise SandboxError(
                "Sandbox is not active. Use as a context manager or call enter()."
            )
        start = time.monotonic()
        try:
            result = callable_fn(*args, **kwargs)
            with self._lock:
                self._stats["executions"] += 1
            return result
        except Exception as exc:
            with self._lock:
                self._stats["errors"] += 1
            raise SandboxError(
                f"Sandboxed execution failed in agent '{self._agent_id}': {exc}"
            ) from exc
        finally:
            elapsed = time.monotonic() - start
            with self._lock:
                self._stats["total_elapsed_seconds"] += elapsed

    def get_sandbox_stats(self) -> Dict[str, Any]:
        """Return a copy of the current sandbox statistics."""
        with self._lock:
            return dict(self._stats)

    def reset(self) -> None:
        """Reset execution statistics (does not affect active limits)."""
        with self._lock:
            self._stats["executions"] = 0
            self._stats["errors"] = 0
            self._stats["total_elapsed_seconds"] = 0.0

    # ------------------------------------------------------------------
    # Internal resource limit management
    # ------------------------------------------------------------------

    _LIMIT_MAP = {
        "max_memory_mb": (resource.RLIMIT_AS, lambda v: v * 1024 * 1024),
        "max_cpu_percent": None,  # CPU% can't be set via rlimit directly
    }

    def _apply_resource_limits(self) -> None:
        """Apply configured resource limits to the current process."""
        mem_mb = self._resource_limits.get("max_memory_mb")
        if mem_mb:
            try:
                soft, hard = resource.getrlimit(resource.RLIMIT_AS)
                self._saved_limits[resource.RLIMIT_AS] = (soft, hard)
                new_limit = int(mem_mb) * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (new_limit, hard))
            except (ValueError, resource.error):
                pass

    def _restore_resource_limits(self) -> None:
        """Restore previously saved resource limits."""
        for limit_type, saved in self._saved_limits.items():
            try:
                resource.setrlimit(limit_type, saved)
            except (ValueError, resource.error):
                pass
        self._saved_limits.clear()
