#!/usr/bin/env python3
"""
BARROT-Ω · TERNARY LOGIC MODULE
1.58-bit ternary {-1, 0, +1} for the SmartAgent loop.
Import: from barrot_agent.ternary import Ternary, ANCHOR
"""

ANCHOR = 0.707106781186548  # 1/√2 — canonical stability constant


class Ternary:
    """
    Ternary logic engine. Absorbs contradiction via NULL state.
    Never crashes — contradiction → NULL, not exception.
    """

    REJECT = DRIFT = SELL = -1
    NULL = HOLD = WAIT = 0
    ACCEPT = VALID = BUY = 1

    @staticmethod
    def resolve(*signals: float) -> int:
        """Collapse signal vector to ternary output."""
        s = sum(signals)
        n = len(signals) or 1
        if s > ANCHOR * n:
            return Ternary.VALID
        elif s < -ANCHOR * n:
            return Ternary.DRIFT
        else:
            return Ternary.NULL

    @staticmethod
    def label(t: int) -> str:
        return {1: "VALID", 0: "NULL", -1: "DRIFT"}[t]

    @staticmethod
    def color(t: int) -> str:
        return {1: "🟢", 0: "🟡", -1: "🔴"}[t]

    @staticmethod
    def gate(value: float, threshold: float = ANCHOR) -> int:
        """Single-value ternary gate against threshold."""
        if value > threshold:
            return Ternary.VALID
        elif value < -threshold:
            return Ternary.DRIFT
        else:
            return Ternary.NULL

    @staticmethod
    def confidence(*signals: int) -> float:
        """
        How many signals agree with the majority?
        Returns float 0.0–1.0. Must exceed ANCHOR to execute.
        """
        if not signals:
            return 0.0
        majority = max(set(signals), key=signals.count)
        return sum(1 for s in signals if s == majority) / len(signals)
