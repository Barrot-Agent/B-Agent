from barrot_agent.trading.risk_manager import RiskManager


def test_approves_amount_within_limit(monkeypatch):
    monkeypatch.setenv("BARROT_MAX_TRADE_USD", "25")
    assert RiskManager().approve_buy("25") is True


def test_rejects_amount_over_limit(monkeypatch):
    monkeypatch.setenv("BARROT_MAX_TRADE_USD", "25")
    assert RiskManager().approve_buy("25.01") is False


def test_rejects_invalid_or_non_positive_amounts():
    manager = RiskManager()

    for value in ("0", "-1", "abc", "NaN", "Infinity"):
        assert manager.approve_buy(value) is False
