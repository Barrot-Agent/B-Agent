import asyncio

from xrp_liquidity_bridge import (
    OnChainSignal,
    OrderBookSignal,
    SentimentSignal,
    Ternary,
    XrpLiquidityBridge,
    extract_rss_titles,
)


def test_orderbook_signal_handles_balanced_book():
    signal = OrderBookSignal(lambda: {"bids": [["1", "10"]], "asks": [["1", "10"]]})
    assert signal.signal().value == Ternary.NULL


def test_onchain_signal_is_inert_without_fetcher():
    signal = asyncio.run(OnChainSignal().signal())
    assert signal.value == Ternary.NULL
    assert "error" in signal.metadata


def test_bridge_exposes_simulation_only_barrot_context():
    bridge = XrpLiquidityBridge(
        orderbook=OrderBookSignal(lambda: {"bids": [["1", "20"]], "asks": [["1", "1"]]}),
        onchain=OnChainSignal(lambda: {"result": {"ledger": {"transaction_count": 150}}}),
    )
    context = asyncio.run(bridge.barrot_context(["XRP adoption growth"]))
    assert context["safety"]["order_execution"] is False
    assert context["snapshot"]["label"] == "BUY"


def test_rss_titles_are_extracted():
    xml = "<rss><item><title><![CDATA[XRP adoption rises]]></title></item></rss>"
    assert extract_rss_titles(xml) == ["XRP adoption rises"]


def test_replay_does_not_change_cash_on_hold():
    bridge = XrpLiquidityBridge()
    result = bridge.replay([])
    assert result == {"starting_cash": 10000.0, "cash": 10000.0, "position": 0}

