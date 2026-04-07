"""Privacy-first inference router — selects the best endpoint for a given model."""

from __future__ import annotations

import fnmatch
import logging
import re
from typing import Any, Dict, List, Optional

from barrot_agent.security.audit_logger import SecurityAuditLogger

logger = logging.getLogger(__name__)


_PII_PATTERNS = [
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),          # SSN
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),  # Email
    re.compile(r"\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),  # Phone
    re.compile(r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})\b"),    # Credit card
]


class PrivacyRouter:
    """Route inference requests to the most privacy-appropriate endpoint.

    The router reads endpoint and routing rules from *routing_config* (loaded
    externally) and always prefers local endpoints to avoid sending data to
    remote APIs.

    Example::

        router = PrivacyRouter(routing_config, endpoints_status)
        result = router.route_inference("llama3", {"prompt": "Hello"})
    """

    def __init__(
        self,
        routing_config: Dict[str, Any],
        endpoint_health: Optional[Dict[str, bool]] = None,
    ) -> None:
        self._config = routing_config
        self._health = endpoint_health or {}
        self._audit = SecurityAuditLogger(agent_id="privacy_router")
        self._stats: Dict[str, int] = {
            "local_routes": 0,
            "remote_routes": 0,
            "anonymized": 0,
            "fallbacks": 0,
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def route_inference(
        self,
        model_name: str,
        request_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Select an endpoint and (optionally) anonymise *request_data*.

        Args:
            model_name:   Name of the model to query.
            request_data: The inference payload (may contain PII).

        Returns:
            Dict with keys ``endpoint``, ``config``, ``request_data``,
            ``privacy_applied``, ``model_name``.
        """
        endpoint_name, endpoint_cfg = self.get_endpoint_for_model(model_name)
        is_remote = endpoint_cfg.get("type") == "remote"
        privacy_applied = False

        if is_remote:
            request_data = self.anonymize_request(request_data)
            privacy_applied = True
            self._stats["remote_routes"] += 1
            self._stats["anonymized"] += 1
        else:
            self._stats["local_routes"] += 1

        self.log_routing_decision(model_name, endpoint_name, privacy_applied)

        return {
            "endpoint": endpoint_name,
            "config": endpoint_cfg,
            "request_data": request_data,
            "privacy_applied": privacy_applied,
            "model_name": model_name,
        }

    def get_endpoint_for_model(self, model_name: str) -> "tuple[str, Dict[str, Any]]":
        """Determine the best endpoint for *model_name*.

        Priority: per-model rule → default primary → default fallback.

        Args:
            model_name: Name of the model (glob patterns are matched).

        Returns:
            Tuple of (endpoint_name, endpoint_config_dict).
        """
        endpoints: Dict[str, Any] = self._config.get("endpoints", {})
        model_routes: List[Dict[str, Any]] = self._config.get("model_routes", [])
        defaults: Dict[str, Any] = self._config.get("defaults", {})

        for route in model_routes:
            pattern = route.get("model_pattern", "")
            if fnmatch.fnmatch(model_name, pattern) or fnmatch.fnmatch(
                model_name, pattern.rstrip("*")
            ):
                preferred = route.get("preferred_endpoint")
                fallback = route.get("fallback_endpoint")
                if preferred and self._is_healthy(preferred):
                    return preferred, endpoints.get(preferred, {})
                if fallback and self._is_healthy(fallback):
                    self._stats["fallbacks"] += 1
                    return fallback, endpoints.get(fallback, {})

        # Use defaults
        primary = defaults.get("primary_endpoint", "")
        if primary and self._is_healthy(primary):
            return primary, endpoints.get(primary, {})
        fallback = defaults.get("fallback_endpoint", "")
        if fallback:
            self._stats["fallbacks"] += 1
            return fallback, endpoints.get(fallback, {})

        return "unknown", {}

    def anonymize_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Strip PII from *request_data* before sending to a remote endpoint.

        Args:
            request_data: The raw inference payload.

        Returns:
            A new dict with PII replaced by ``[REDACTED]``.
        """
        import copy
        clean = copy.deepcopy(request_data)
        _redact_pii_recursive(clean)
        return clean

    def log_routing_decision(
        self, model: str, endpoint: str, privacy_applied: bool
    ) -> None:
        """Emit an audit log entry for a routing decision.

        Args:
            model:           Model that was routed.
            endpoint:        Selected endpoint name.
            privacy_applied: Whether anonymization was applied.
        """
        self._audit.log_execution(
            command=f"route:{model}→{endpoint}",
            result={"returncode": 0, "privacy_applied": privacy_applied},
        )

    def get_routing_stats(self) -> Dict[str, int]:
        """Return a snapshot of routing statistics."""
        return dict(self._stats)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _is_healthy(self, endpoint_name: str) -> bool:
        """Return True if the endpoint is healthy or health is unknown."""
        return self._health.get(endpoint_name, True)


def _redact_pii_recursive(obj: Any) -> None:
    """Mutate *obj* in-place, replacing PII strings with ``[REDACTED]``."""
    if isinstance(obj, dict):
        for key in list(obj.keys()):
            if isinstance(obj[key], str):
                obj[key] = _redact_string(obj[key])
            else:
                _redact_pii_recursive(obj[key])
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, str):
                obj[i] = _redact_string(item)
            else:
                _redact_pii_recursive(item)


def _redact_string(text: str) -> str:
    for pattern in _PII_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text
