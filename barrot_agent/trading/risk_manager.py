"""Hard trading limits independent of Barrot's strategy."""

from __future__ import annotations

import os
from decimal import Decimal, InvalidOperation


class RiskManager:
    """Validate trade sizes against non-strategy safety limits."""

    def __init__(self) -> None:
        self.max_trade_usd = self._positive_decimal(
            os.getenv("BARROT_MAX_TRADE_USD", "25"),
            default=Decimal("25"),
        )

    @staticmethod
    def _positive_decimal(value: str | Decimal, default: Decimal | None = None) -> Decimal:
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, ValueError):
            if default is not None:
                return default
            raise ValueError("Trade amount must be a valid number.")

        if not amount.is_finite() or amount <= 0:
            if default is not None:
                return default
            raise ValueError("Trade amount must be greater than zero.")

        return amount

    def approve_buy(self, quote_size: str) -> bool:
        """Return True only for a valid amount within the hard USD limit."""
        try:
            amount = self._positive_decimal(quote_size)
        except ValueError:
            return False

        return amount <= self.max_trade_usd

    def require_buy_approval(self, quote_size: str) -> None:
        """Fail closed when a buy exceeds the configured hard limit."""
        if not self.approve_buy(quote_size):
            raise ValueError(
                f"Buy rejected by risk manager. Maximum allowed: " f"${self.max_trade_usd}"
            )
