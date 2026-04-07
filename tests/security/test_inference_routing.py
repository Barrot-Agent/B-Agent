"""Tests for privacy-first inference routing."""

from __future__ import annotations

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from barrot_agent.inference.privacy_router import PrivacyRouter, _redact_string


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_ROUTING_CONFIG: Dict[str, Any] = {
    "defaults": {
        "primary_endpoint": "local_nvidia_gpu",
        "fallback_endpoint": "huggingface_api",
        "privacy_mode": "strict",
        "anonymize_on_fallback": True,
    },
    "endpoints": {
        "local_nvidia_gpu": {
            "type": "local",
            "url": "http://localhost:8000",
            "supported_models": ["granite-vision", "llama3", "mistral"],
            "priority": 1,
        },
        "huggingface_api": {
            "type": "remote",
            "url": "https://api-inference.huggingface.co",
            "requires_token": True,
            "token_env_var": "HF_TOKEN",
            "data_anonymization": True,
            "priority": 2,
        },
    },
    "model_routes": [
        {
            "model_pattern": "granite*",
            "preferred_endpoint": "local_nvidia_gpu",
            "fallback_endpoint": "huggingface_api",
        },
        {
            "model_pattern": "llama*",
            "preferred_endpoint": "local_nvidia_gpu",
            "fallback_endpoint": "huggingface_api",
        },
    ],
}


@pytest.fixture()
def router() -> PrivacyRouter:
    return PrivacyRouter(_ROUTING_CONFIG, endpoint_health={"local_nvidia_gpu": True})


@pytest.fixture()
def router_no_local() -> PrivacyRouter:
    """Router where local GPU is unhealthy, forcing remote fallback."""
    return PrivacyRouter(
        _ROUTING_CONFIG,
        endpoint_health={"local_nvidia_gpu": False, "huggingface_api": True},
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_privacy_router_creation() -> None:
    """PrivacyRouter can be instantiated."""
    r = PrivacyRouter(_ROUTING_CONFIG)
    assert r is not None
    assert r.get_routing_stats()["local_routes"] == 0


def test_local_gpu_preferred(router: PrivacyRouter) -> None:
    """Local endpoint is selected when healthy."""
    result = router.route_inference("llama3", {"prompt": "hello"})
    assert result["endpoint"] == "local_nvidia_gpu"
    assert result["privacy_applied"] is False  # local → no anonymization


def test_fallback_to_remote(router_no_local: PrivacyRouter) -> None:
    """Falls back to remote endpoint when local is unhealthy."""
    result = router_no_local.route_inference("llama3", {"prompt": "hello"})
    assert result["endpoint"] == "huggingface_api"
    assert result["privacy_applied"] is True  # remote → anonymization applied


def test_request_anonymization(router: PrivacyRouter) -> None:
    """PII fields are stripped from anonymized request data."""
    raw = {
        "prompt": "My SSN is 123-45-6789 and email is user@example.com",
        "temperature": 0.7,
    }
    clean = router.anonymize_request(raw)
    assert "123-45-6789" not in clean["prompt"]
    assert "user@example.com" not in clean["prompt"]
    assert "[REDACTED]" in clean["prompt"]
    # Non-PII fields are untouched
    assert clean["temperature"] == 0.7


def test_model_route_selection(router: PrivacyRouter) -> None:
    """Per-model routing rules override defaults."""
    ep, cfg = router.get_endpoint_for_model("granite-vision")
    assert ep == "local_nvidia_gpu"

    ep2, cfg2 = router.get_endpoint_for_model("llama3")
    assert ep2 == "local_nvidia_gpu"


def test_routing_stats_increment(router: PrivacyRouter) -> None:
    """Routing statistics are updated after each call."""
    router.route_inference("llama3", {"prompt": "test"})
    stats = router.get_routing_stats()
    assert stats["local_routes"] == 1


def test_pii_redaction_email() -> None:
    """_redact_string removes email addresses."""
    result = _redact_string("Contact us at admin@corp.io for help")
    assert "admin@corp.io" not in result
    assert "[REDACTED]" in result


def test_routing_unknown_model_uses_defaults() -> None:
    """An unrecognised model name falls through to the default endpoint."""
    r = PrivacyRouter(_ROUTING_CONFIG, endpoint_health={"local_nvidia_gpu": True})
    ep, _ = r.get_endpoint_for_model("some-unknown-model")
    assert ep == "local_nvidia_gpu"
