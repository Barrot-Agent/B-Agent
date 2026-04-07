"""OpenShell Policy Manager — loads, validates, and hot-reloads YAML policies."""

from __future__ import annotations

import logging
import os
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


class PolicyLoadError(Exception):
    """Raised when a policy file cannot be loaded or parsed."""


class PolicyNotFoundError(KeyError):
    """Raised when a requested policy name does not exist."""


class PolicyManager:
    """Manages OpenShell security policies with optional hot-reload support.

    Policies are loaded from YAML files located in *policy_directory*.  The
    manager keeps an in-memory registry keyed by ``policy_name`` field found
    inside each YAML document.  When hot-reload is enabled a background thread
    periodically re-reads files that have changed on disk.

    Example::

        pm = PolicyManager("openshell/policies")
        pm.load_all()
        decision = pm.enforce_policy("network_request", {"agent_id": "inference_agent"})
    """

    def __init__(
        self,
        policy_directory: str,
        hot_reload: bool = False,
        hot_reload_interval: int = 60,
    ) -> None:
        self._policy_dir = Path(policy_directory)
        self._policies: Dict[str, Dict[str, Any]] = {}
        self._file_mtimes: Dict[str, float] = {}
        self._hot_reload = hot_reload
        self._hot_reload_interval = hot_reload_interval
        self._reload_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.RLock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_all(self) -> None:
        """Load every ``*.yaml`` file found in *policy_directory*."""
        if not self._policy_dir.is_dir():
            raise PolicyLoadError(
                f"Policy directory not found: {self._policy_dir}"
            )
        for path in self._policy_dir.glob("*.yaml"):
            try:
                self._load_file(path)
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to load policy %s: %s", path, exc)

        if self._hot_reload:
            self._start_hot_reload()

    def reload_policy(self, policy_path: str) -> None:
        """Force-reload a single policy file from disk.

        Args:
            policy_path: Absolute or relative path to the ``.yaml`` file.
        """
        path = Path(policy_path)
        if not path.is_absolute():
            path = self._policy_dir / path
        self._load_file(path)

    def get_policy(self, name: str) -> Dict[str, Any]:
        """Return the policy dict for *name*.

        Raises:
            PolicyNotFoundError: When *name* is not registered.
        """
        with self._lock:
            if name not in self._policies:
                raise PolicyNotFoundError(f"Policy '{name}' not found")
            return dict(self._policies[name])

    def list_policies(self) -> List[str]:
        """Return a sorted list of all loaded policy names."""
        with self._lock:
            return sorted(self._policies.keys())

    def validate_policy(self, policy_dict: Dict[str, Any]) -> bool:
        """Validate a policy dictionary against the minimum required schema.

        Args:
            policy_dict: A parsed YAML policy document.

        Returns:
            ``True`` if valid.

        Raises:
            ValueError: Describing which required fields are missing.
        """
        required_fields = {"version", "policy_name"}
        missing = required_fields - set(policy_dict.keys())
        if missing:
            raise ValueError(f"Policy missing required fields: {missing}")
        if not isinstance(policy_dict.get("version"), str):
            raise ValueError("'version' must be a string")
        return True

    def enforce_policy(
        self, action: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate whether *action* is permitted given *context*.

        The method walks all loaded policies in load order, checking
        ``api_restrictions`` entries.  The first explicit *deny* wins; if no
        restriction matches and ``enforcement_mode`` is ``strict`` the default
        answer is *deny*.

        Args:
            action:  The API method / action name being requested.
            context: A dict that must contain at least ``agent_id``.

        Returns:
            A decision dict with keys ``allowed`` (bool), ``policy`` (str),
            ``reason`` (str).
        """
        agent_id: str = context.get("agent_id", "")

        with self._lock:
            policies_snapshot = dict(self._policies)

        for policy_name, policy in policies_snapshot.items():
            restrictions: List[Dict[str, Any]] = policy.get(
                "api_restrictions", []
            )
            for restriction in restrictions:
                if restriction.get("method") != action:
                    continue
                allowed_agents: List[str] = restriction.get("allow_from", [])
                if agent_id in allowed_agents:
                    return {
                        "allowed": True,
                        "policy": policy_name,
                        "reason": f"Agent '{agent_id}' is explicitly allowed",
                    }
                return {
                    "allowed": False,
                    "policy": policy_name,
                    "reason": (
                        f"Agent '{agent_id}' not in allow_from list for "
                        f"action '{action}'"
                    ),
                }

        # No explicit rule found — default depends on enforcement_mode
        for policy in policies_snapshot.values():
            if policy.get("enforcement_mode") == "strict":
                return {
                    "allowed": False,
                    "policy": "default",
                    "reason": "No matching rule; strict mode denies by default",
                }

        return {
            "allowed": True,
            "policy": "default",
            "reason": "No matching rule; permissive mode allows by default",
        }

    def shutdown(self) -> None:
        """Stop the hot-reload background thread if running."""
        self._stop_event.set()
        if self._reload_thread and self._reload_thread.is_alive():
            self._reload_thread.join(timeout=5)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_file(self, path: Path) -> None:
        """Parse *path* and register the policy under its ``policy_name``."""
        with open(path, encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)

        if not isinstance(raw, dict):
            raise PolicyLoadError(f"Expected a YAML mapping in {path}")

        self.validate_policy(raw)
        policy_name: str = raw["policy_name"]

        with self._lock:
            self._policies[policy_name] = raw
            self._file_mtimes[str(path)] = path.stat().st_mtime

        logger.info("Loaded policy '%s' from %s", policy_name, path)

    def _start_hot_reload(self) -> None:
        """Spawn a daemon thread that watches policy files for changes."""
        self._stop_event.clear()
        self._reload_thread = threading.Thread(
            target=self._hot_reload_loop,
            name="policy-hot-reload",
            daemon=True,
        )
        self._reload_thread.start()
        logger.info(
            "Hot-reload enabled (interval=%ds)", self._hot_reload_interval
        )

    def _hot_reload_loop(self) -> None:
        while not self._stop_event.wait(timeout=self._hot_reload_interval):
            for path in self._policy_dir.glob("*.yaml"):
                try:
                    mtime = path.stat().st_mtime
                    if mtime != self._file_mtimes.get(str(path)):
                        logger.info("Policy file changed, reloading: %s", path)
                        self._load_file(path)
                except Exception as exc:  # noqa: BLE001
                    logger.error(
                        "Hot-reload error for %s: %s", path, exc
                    )
