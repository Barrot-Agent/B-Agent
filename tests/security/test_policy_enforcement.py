"""Tests for the policy evaluation engine."""

from __future__ import annotations

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from barrot_agent.security.policy_engine import PolicyEngine, PolicyDecision


# ---------------------------------------------------------------------------
# Test policy fixture
# ---------------------------------------------------------------------------

_SAMPLE_POLICY: Dict[str, Any] = {
    "version": "1.0",
    "policy_name": "test_policy",
    "enforcement_mode": "strict",
    "allowed_binaries": ["git", "python3", "pip"],
    "network_rules": {
        "allow_domains": ["huggingface.co", "pypi.org"],
        "deny_all_other": True,
    },
    "filesystem_permissions": [
        {"path": "/app", "access": "read_write"},
        {"path": "/data", "access": "read_only"},
        {"path": "/var/log", "access": "append"},
    ],
    "api_restrictions": [
        {
            "method": "execute_code",
            "allow_from": ["inference_agent", "research_agent"],
            "log_level": "info",
        },
        {
            "method": "access_credentials",
            "allow_from": ["deployment_agent"],
            "log_level": "critical",
        },
    ],
}


@pytest.fixture()
def engine() -> PolicyEngine:
    return PolicyEngine(_SAMPLE_POLICY)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_policy_engine_creation() -> None:
    """PolicyEngine can be instantiated and accepts a policy dict."""
    pe = PolicyEngine()
    assert pe is not None
    pe.load_policy(_SAMPLE_POLICY)
    assert pe._policy["policy_name"] == "test_policy"


def test_allowed_action_passes(engine: PolicyEngine) -> None:
    """An agent listed in allow_from receives an allowed=True decision."""
    decision = engine.evaluate_action("execute_code", "inference_agent", {})
    assert decision.allowed is True
    assert "inference_agent" in decision.reason


def test_denied_action_blocked(engine: PolicyEngine) -> None:
    """An agent not in allow_from is denied."""
    decision = engine.evaluate_action("execute_code", "audit_agent", {})
    assert decision.allowed is False
    assert "audit_agent" in decision.reason


def test_network_permission_check(engine: PolicyEngine) -> None:
    """Allowed domains pass; unlisted domains are blocked."""
    allowed = engine.check_network_permission("huggingface.co", "inference_agent")
    assert allowed.allowed is True

    blocked = engine.check_network_permission("evil.com", "inference_agent")
    assert blocked.allowed is False


def test_filesystem_permission_check(engine: PolicyEngine) -> None:
    """Filesystem access is controlled by path prefix + access mode."""
    rw = engine.check_filesystem_permission("/app/models", "write", "agent")
    assert rw.allowed is True

    ro_write = engine.check_filesystem_permission("/data/file.txt", "write", "agent")
    assert ro_write.allowed is False

    ro_read = engine.check_filesystem_permission("/data/file.txt", "read", "agent")
    assert ro_read.allowed is True

    no_rule = engine.check_filesystem_permission("/etc/passwd", "read", "agent")
    assert no_rule.allowed is False


def test_api_permission_check(engine: PolicyEngine) -> None:
    """check_api_permission delegates to evaluate_action."""
    assert engine.check_api_permission("access_credentials", "deployment_agent").allowed
    assert not engine.check_api_permission("access_credentials", "inference_agent").allowed


def test_binary_permission_check(engine: PolicyEngine) -> None:
    """Whitelisted binaries are allowed; others are blocked."""
    assert engine.check_binary_permission("git", "any_agent").allowed
    assert not engine.check_binary_permission("curl", "any_agent").allowed


def test_strict_mode_denies_unknown_action(engine: PolicyEngine) -> None:
    """Unknown actions are denied in strict enforcement mode."""
    decision = engine.evaluate_action("unknown_action", "inference_agent", {})
    assert decision.allowed is False


def test_permissive_mode_allows_unknown_action() -> None:
    """Unknown actions are allowed in permissive enforcement mode."""
    permissive_policy = {**_SAMPLE_POLICY, "enforcement_mode": "permissive"}
    engine = PolicyEngine(permissive_policy)
    decision = engine.evaluate_action("new_action", "some_agent", {})
    assert decision.allowed is True


def test_get_policy_decision_network(engine: PolicyEngine) -> None:
    """get_policy_decision dispatches network requests correctly."""
    decision = engine.get_policy_decision(
        {"request_type": "network", "domain": "pypi.org", "agent_id": "agent"}
    )
    assert decision.allowed is True


def test_get_policy_decision_filesystem(engine: PolicyEngine) -> None:
    """get_policy_decision dispatches filesystem requests correctly."""
    decision = engine.get_policy_decision(
        {
            "request_type": "filesystem",
            "path": "/app/data",
            "access_type": "read",
            "agent_id": "agent",
        }
    )
    assert decision.allowed is True
