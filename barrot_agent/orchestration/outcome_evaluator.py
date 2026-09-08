"""Evaluate autonomous action outcomes and decide whether correction is needed."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EvaluationResult:
    success: bool
    reason: str


class OutcomeEvaluator:
    """Evaluate whether an autonomous attempt achieved its goal safely."""

    def evaluate(
        self,
        *,
        results: list[dict[str, Any]],
        verification_success: bool,
    ) -> EvaluationResult:
        if not results:
            return EvaluationResult(
                success=False,
                reason="No actions were executed.",
            )

        failed = [
            result
            for result in results
            if not result.get("success", False)
        ]

        if failed:
            return EvaluationResult(
                success=False,
                reason=f"{len(failed)} action(s) failed.",
            )

        if not verification_success:
            return EvaluationResult(
                success=False,
                reason="Verification failed.",
            )

        return EvaluationResult(
            success=True,
            reason="All actions and verification checks succeeded.",
        )
