"""Coinbase Advanced Trade execution layer for Barrot."""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

try:
    from coinbase.rest import RESTClient
except ModuleNotFoundError:  # pragma: no cover - exercised indirectly in tests
    class RESTClient:  # type: ignore[override]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            del args, kwargs

        def get_product(self, product_id: str) -> dict[str, str]:
            return {"product_id": product_id, "status": "unavailable"}

        def market_order_buy(self, **kwargs: Any) -> dict[str, Any]:
            raise RuntimeError("coinbase package is not installed")

        def market_order_sell(self, **kwargs: Any) -> dict[str, Any]:
            raise RuntimeError("coinbase package is not installed")

from barrot_agent.trading.risk_manager import RiskManager


@dataclass
class TradeResult:
    executed: bool
    response: Any


class CoinbaseTrader:
    """
    Controlled Coinbase Advanced Trade interface.

    Trading defaults to dry-run mode. Buy orders must pass RiskManager
    before they can reach the exchange.
    """

    def __init__(self, risk_manager: RiskManager | None = None) -> None:
        self.dry_run = os.getenv("BARROT_TRADING_DRY_RUN", "true").lower() == "true"
        self.risk_manager = risk_manager or RiskManager()

        api_key = os.getenv("COINBASE_API_KEY")
        api_secret = os.getenv("COINBASE_API_SECRET")

        self.client = (
            RESTClient(api_key=api_key, api_secret=api_secret)
            if api_key and api_secret
            else RESTClient()
        )

    def price(self, product_id: str = "BTC-USD") -> Any:
        """Get current product information."""
        return self.client.get_product(product_id)

    @staticmethod
    def _validate_positive_amount(value: str, field_name: str) -> None:
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, ValueError) as error:
            raise ValueError(f"{field_name} must be a valid number.") from error

        if not amount.is_finite() or amount <= 0:
            raise ValueError(f"{field_name} must be greater than zero.")

    def buy(self, product_id: str, quote_size: str) -> TradeResult:
        """Buy using a specified USD amount after risk approval."""
        self._validate_positive_amount(quote_size, "quote_size")
        self.risk_manager.require_buy_approval(quote_size)

        order_id = str(uuid.uuid4())

        if self.dry_run:
            return TradeResult(
                executed=False,
                response={
                    "mode": "DRY_RUN",
                    "action": "BUY",
                    "product_id": product_id,
                    "quote_size": quote_size,
                    "client_order_id": order_id,
                },
            )

        response = self.client.market_order_buy(
            client_order_id=order_id,
            product_id=product_id,
            quote_size=quote_size,
        )
        return TradeResult(executed=True, response=response)

    def sell(self, product_id: str, base_size: str) -> TradeResult:
        """
        Sell a specified amount of the asset.

        Size validation is enforced here. Additional portfolio-level sell
        controls can be added separately without weakening buy protections.
        """
        self._validate_positive_amount(base_size, "base_size")

        order_id = str(uuid.uuid4())

        if self.dry_run:
            return TradeResult(
                executed=False,
                response={
                    "mode": "DRY_RUN",
                    "action": "SELL",
                    "product_id": product_id,
                    "base_size": base_size,
                    "client_order_id": order_id,
                },
            )

        response = self.client.market_order_sell(
            client_order_id=order_id,
            product_id=product_id,
            base_size=base_size,
        )
        return TradeResult(executed=True, response=response)
