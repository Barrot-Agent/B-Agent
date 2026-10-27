import pytest

import barrot_agent.trading.coinbase_trader as coinbase_trader
from barrot_agent.trading.risk_manager import RiskManager


@pytest.fixture(autouse=True)
def fake_rest_client(monkeypatch):
    class DummyRESTClient:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def get_product(self, product_id):
            return {"product_id": product_id, "status": "ok"}

        def market_order_buy(self, **kwargs):
            return kwargs

        def market_order_sell(self, **kwargs):
            return kwargs

    monkeypatch.setattr(coinbase_trader, "RESTClient", DummyRESTClient)


def test_buy_defaults_to_dry_run(monkeypatch):
    monkeypatch.delenv("BARROT_TRADING_DRY_RUN", raising=False)

    trader = coinbase_trader.CoinbaseTrader(risk_manager=RiskManager())
    result = trader.buy("BTC-USD", "1")

    assert result.executed is False
    assert result.response["mode"] == "DRY_RUN"


def test_buy_cannot_bypass_risk_limit(monkeypatch):
    monkeypatch.setenv("BARROT_MAX_TRADE_USD", "25")

    trader = coinbase_trader.CoinbaseTrader(risk_manager=RiskManager())

    with pytest.raises(ValueError, match="Buy rejected by risk manager"):
        trader.buy("BTC-USD", "26")


@pytest.mark.parametrize("amount", ["0", "-1", "abc"])
def test_invalid_buy_amount_is_rejected(amount):
    trader = coinbase_trader.CoinbaseTrader(risk_manager=RiskManager())

    with pytest.raises(ValueError):
        trader.buy("BTC-USD", amount)


@pytest.mark.parametrize("amount", ["0", "-1", "abc"])
def test_invalid_sell_amount_is_rejected(amount):
    trader = coinbase_trader.CoinbaseTrader(risk_manager=RiskManager())

    with pytest.raises(ValueError):
        trader.sell("BTC-USD", amount)
