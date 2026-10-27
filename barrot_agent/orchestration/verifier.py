"""Verification layer for Barrot autonomous tasks."""

from __future__ import annotations

from dataclasses import dataclass

from .executor import BarrotExecutor


@dataclass
class VerificationResult:
    success: bool
    checks: list[dict]


class BarrotVerifier:
    """Run repository verification gates."""

    def __init__(self, executor: BarrotExecutor):
        self.executor = executor

    def verify_python(self) -> VerificationResult:
        checks = []

        result = self.executor.run(
            "python -m compileall -q barrot_agent scripts"
        )

        checks.append(
            {
                "command": result.command,
                "success": result.success,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        )

        return VerificationResult(
            success=all(check["success"] for check in checks),
            checks=checks,
        )

    def git_status(self) -> dict:
        result = self.executor.run("git status --short")

        return {
            "success": result.success,
            "output": result.stdout,
            "error": result.stderr,
        }
