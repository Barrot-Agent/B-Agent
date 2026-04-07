"""Endpoint lifecycle manager — register, select, and track inference endpoints."""

from __future__ import annotations

import logging
import threading
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class EndpointNotFoundError(KeyError):
    """Raised when an endpoint name is not registered."""


class EndpointManager:
    """Manage the lifecycle of inference endpoints.

    Example::

        em = EndpointManager()
        em.register_endpoint("local_gpu", {"type": "local", "url": "http://localhost:8000"})
        cfg = em.get_endpoint("local_gpu")
    """

    _VALID_STATUSES = frozenset({"healthy", "degraded", "unhealthy", "unknown"})

    def __init__(self) -> None:
        self._endpoints: Dict[str, Dict[str, Any]] = {}
        self._statuses: Dict[str, str] = {}
        self._lock = threading.RLock()

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_endpoint(self, name: str, config: Dict[str, Any]) -> None:
        """Register an endpoint under *name*.

        Args:
            name:   Unique identifier for the endpoint.
            config: Endpoint configuration dict (``type``, ``url``, etc.).
        """
        with self._lock:
            self._endpoints[name] = dict(config)
            self._statuses[name] = "unknown"
        logger.info("Registered endpoint '%s' (type=%s)", name, config.get("type"))

    def get_endpoint(self, name: str) -> Dict[str, Any]:
        """Retrieve the configuration for *name*.

        Raises:
            EndpointNotFoundError: When the endpoint is not registered.
        """
        with self._lock:
            if name not in self._endpoints:
                raise EndpointNotFoundError(f"Endpoint '{name}' not found")
            return dict(self._endpoints[name])

    def list_endpoints(self) -> List[str]:
        """Return a sorted list of all registered endpoint names."""
        with self._lock:
            return sorted(self._endpoints.keys())

    # ------------------------------------------------------------------
    # Health & selection
    # ------------------------------------------------------------------

    def check_endpoint_health(self, name: str) -> str:
        """Perform a synchronous health check for *name*.

        Currently returns the stored status; integrators should override this
        method or call :meth:`update_endpoint_status` after an actual probe.

        Args:
            name: Endpoint identifier.

        Returns:
            Status string (e.g. ``"healthy"``, ``"unhealthy"``).
        """
        with self._lock:
            return self._statuses.get(name, "unknown")

    def select_best_endpoint(
        self,
        model_name: str,
        requirements: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Choose the highest-priority healthy endpoint that supports *model_name*.

        Priority is determined by the ``priority`` field in each endpoint config
        (lower number = higher priority).  If ``requirements`` contains
        ``"type": "local"`` only local endpoints are considered.

        Args:
            model_name:   Model to serve.
            requirements: Optional filter dict (e.g. ``{"type": "local"}``).

        Returns:
            The name of the selected endpoint, or ``None`` if none qualify.
        """
        requirements = requirements or {}
        req_type = requirements.get("type")

        with self._lock:
            candidates = []
            for name, cfg in self._endpoints.items():
                status = self._statuses.get(name, "unknown")
                if status == "unhealthy":
                    continue
                if req_type and cfg.get("type") != req_type:
                    continue
                supported = cfg.get("supported_models", [])
                if supported and model_name not in supported:
                    # Also check prefix matching
                    if not any(model_name.startswith(m.rstrip("*")) for m in supported):
                        continue
                candidates.append((name, cfg.get("priority", 99)))

        if not candidates:
            return None
        candidates.sort(key=lambda x: x[1])
        return candidates[0][0]

    def update_endpoint_status(self, name: str, status: str) -> None:
        """Update the health status for *name*.

        Args:
            name:   Endpoint identifier.
            status: One of ``"healthy"``, ``"degraded"``, ``"unhealthy"``,
                    ``"unknown"``.

        Raises:
            ValueError: For invalid status values.
            EndpointNotFoundError: When the endpoint is not registered.
        """
        if status not in self._VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{status}'; must be one of {sorted(self._VALID_STATUSES)}"
            )
        with self._lock:
            if name not in self._endpoints:
                raise EndpointNotFoundError(f"Endpoint '{name}' not found")
            self._statuses[name] = status
        logger.debug("Endpoint '%s' status → %s", name, status)
