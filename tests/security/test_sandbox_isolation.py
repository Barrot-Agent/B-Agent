"""Tests for sandbox isolation and execution control."""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from barrot_agent.security.sandbox_executor import (
    ExecutionTimeoutError,
    SandboxExecutor,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def executor() -> SandboxExecutor:
    return SandboxExecutor()


@pytest.fixture()
def strict_executor() -> SandboxExecutor:
    return SandboxExecutor(
        limits={
            "max_cpu_seconds": 5,
            "max_memory_bytes": 64 * 1024 * 1024,
            "max_file_descriptors": 64,
            "max_processes": 5,
        }
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_sandbox_executor_creation() -> None:
    """SandboxExecutor can be instantiated with default limits."""
    ex = SandboxExecutor()
    assert ex is not None
    stats = ex.get_execution_stats()
    assert stats["commands_executed"] == 0
    assert stats["python_snippets_executed"] == 0


def test_command_execution_allowed() -> None:
    """A whitelisted safe command executes and returns correct fields."""
    ex = SandboxExecutor()
    _completed = subprocess.CompletedProcess(
        args=["echo", "hello"],
        returncode=0,
        stdout="hello\n",
        stderr="",
    )
    with patch("subprocess.run", return_value=_completed) as mock_run:
        result = ex.execute_command(["echo", "hello"], timeout=10)

    assert result["returncode"] == 0
    assert result["stdout"] == "hello\n"
    assert "elapsed_seconds" in result
    assert ex.get_execution_stats()["commands_executed"] == 1


def test_resource_limits_applied() -> None:
    """apply_resource_limits merges new limits without losing existing keys."""
    ex = SandboxExecutor()
    original_mem = ex._limits["max_memory_bytes"]
    ex.apply_resource_limits({"max_memory_bytes": 128 * 1024 * 1024})
    assert ex._limits["max_memory_bytes"] == 128 * 1024 * 1024
    # Other limits unchanged
    assert "max_cpu_seconds" in ex._limits


def test_timeout_enforcement() -> None:
    """Commands that exceed timeout raise ExecutionTimeoutError."""
    ex = SandboxExecutor()
    with patch(
        "subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="sleep", timeout=1)
    ):
        with pytest.raises(ExecutionTimeoutError):
            ex.execute_command(["sleep", "100"], timeout=1)
    assert ex.get_execution_stats()["timeouts"] == 1


def test_policy_violation_blocked() -> None:
    """Injecting a forbidden binary name is blocked by a wrapping guard."""
    ex = SandboxExecutor()
    # Simulate a policy-blocked command by raising PermissionError in preexec
    with patch(
        "subprocess.run",
        side_effect=PermissionError("blocked by policy"),
    ):
        with pytest.raises(RuntimeError, match="Command execution failed"):
            ex.execute_command(["rm", "-rf", "/"], timeout=5)
    assert ex.get_execution_stats()["errors"] == 1


def test_execute_python_success() -> None:
    """Python execution returns captured stdout."""
    ex = SandboxExecutor()
    _completed = subprocess.CompletedProcess(
        args=["python3", "-c", "print('hi')"],
        returncode=0,
        stdout="hi\n",
        stderr="",
    )
    with patch("subprocess.run", return_value=_completed):
        result = ex.execute_python("print('hi')", timeout=10)
    assert result["returncode"] == 0
    assert ex.get_execution_stats()["python_snippets_executed"] == 1


def test_get_execution_stats_increments() -> None:
    """Execution stats accumulate across multiple calls."""
    ex = SandboxExecutor()
    _ok = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
    with patch("subprocess.run", return_value=_ok):
        ex.execute_command(["echo", "a"])
        ex.execute_command(["echo", "b"])
    assert ex.get_execution_stats()["commands_executed"] == 2
