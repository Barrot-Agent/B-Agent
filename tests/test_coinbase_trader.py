import pytest

from barrot_agent.trading.coinbase_trader import CoinbaseTrader
from barrot_agent.trading.risk_manager import RiskManager


def test_buy_defaults_to_dry_run(monkeypatch):
    monkeypatch.delenv("BARROT_TRADING_DRY_RUN", raising=False)

    trader = CoinbaseTrader(risk_manager=RiskManager())
    result = trader.buy("BTC-USD", "1")

    assert result.executed is False
    assert result.response["mode"] == "DRY_RUN"


def test_buy_cannot_bypass_risk_limit(monkeypatch):
    monkeypatch.setenv("BARROT_MAX_TRADE_USD", "25")

    trader = CoinbaseTrader(risk_manager=RiskManager())

    with pytest.raises(ValueError, match="Buy rejected by risk manager"):
        trader.buy("BTC-USD", "26")


@pytest.mark.parametrize("amount", ["0", "-1", "abc"])
def test_invalid_buy_amount_is_rejected(amount):
    trader = CoinbaseTrader(risk_manager=RiskManager())

    with pytest.raises(ValueError):
        trader.buy("BTC-USD", amount)


@pytest.mark.parametrize("amount", ["0", "-1", "abc"])
def test_invalid_sell_amount_is_rejected(amount):
    trader = CoinbaseTrader(risk_manager=RiskManager())

    with pytest.raises(ValueError):
        trader.sell("BTC-USD", amount)
