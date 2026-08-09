"""Tests for the provider-neutral capability parity layer."""

from __future__ import annotations

import pytest

from barrot_agent.capability_parity import (
    CapabilityStatus,
    DEFAULT_BENCHMARKS,
    DEFAULT_CAPABILITY_MATRIX,
    StrategyRouter,
    evaluate_benchmark,
)


def test_default_matrix_covers_requested_capability_groups() -> None:
    expected = {
        "coding", "planning", "reasoning", "web_search", "file_terminal",
        "vision", "documents", "tools_mcp", "multi_agent", "memory",
        "safety", "socratic_learning",
    }
    assert {item.key for item in DEFAULT_CAPABILITY_MATRIX.capabilities} == expected


def test_matrix_exposes_auditable_gaps() -> None:
    gaps = DEFAULT_CAPABILITY_MATRIX.gaps()
    assert gaps
    assert all(item.barrot != CapabilityStatus.IMPLEMENTED for item in gaps)
    assert any(item.key == "coding" for item in gaps)


def test_matrix_serialization_is_json_friendly() -> None:
    serialized = DEFAULT_CAPABILITY_MATRIX.to_dict()
    assert serialized[0]["barrot"] in {status.value for status in CapabilityStatus}
    assert isinstance(serialized[0]["evidence"], list)


def test_benchmark_evaluation_reports_missing_criteria() -> None:
    task = DEFAULT_BENCHMARKS[0]
    result = evaluate_benchmark(task, "plan with risks")
    assert result.passed is False
    assert result.missing_criteria == ("validation",)


class _FakeStrategy:
    provider_name = "fake"

    def complete(self, prompt: str, *, context=None) -> str:
        return f"{prompt}:{context['mode']}"


def test_strategy_router_selects_provider() -> None:
    router = StrategyRouter([_FakeStrategy()])
    assert router.providers() == ("fake",)
    assert router.complete("fake", "hello", context={"mode": "test"}) == "hello:test"


def test_strategy_router_rejects_unknown_provider() -> None:
    with pytest.raises(KeyError, match="No strategy"):
        StrategyRouter().complete("missing", "hello")
