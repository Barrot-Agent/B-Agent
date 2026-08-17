#!/usr/bin/env python3
"""Simulation-safe XRP signal collection for Barrot.

This module deliberately has no order-placement code.  It normalizes optional
market inputs into a provenance-preserving context that Barrot can inspect or
backtest.  Network access is opt-in through injected fetchers.
"""

from __future__ import annotations

import asyncio
import json
import re
import urllib.request
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Iterable

ANCHOR = 0.707106781186548


class Ternary:
    SELL, NULL, BUY = -1, 0, 1

    @staticmethod
    def resolve(*signals: int) -> int:
        if not signals:
            return Ternary.NULL
        average = sum(signals) / len(signals)
        if average > ANCHOR:
            return Ternary.BUY
        if average < -ANCHOR:
            return Ternary.SELL
        return Ternary.NULL

    @staticmethod
    def label(signal: int) -> str:
        return {Ternary.SELL: "SELL", Ternary.NULL: "NULL", Ternary.BUY: "BUY"}[
            signal
        ]


@dataclass
class Signal:
    source: str
    value: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BridgeSnapshot:
    signal: int
    label: str
    signals: list[Signal]
    mode: str = "simulation"

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal": self.signal,
            "label": self.label,
            "signals": [item.to_dict() for item in self.signals],
            "mode": self.mode,
        }


class OrderBookSignal:
    """Convert a Binance-compatible depth payload into a ternary signal."""

    def __init__(self, fetcher: Callable[[], dict[str, Any]] | None = None) -> None:
        self.fetcher = fetcher

    def fetch(self) -> dict[str, Any]:
        if self.fetcher is not None:
            return self.fetcher()
        request = urllib.request.Request(
            "https://api.binance.com/api/v3/depth?symbol=XRPUSDT&limit=20",
            headers={"User-Agent": "Barrot-XRP-Bridge/1.0"},
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            return json.load(response)

    def signal(self) -> Signal:
        try:
            book = self.fetch()
            bids = book.get("bids", [])
            asks = book.get("asks", [])
            bid_volume = sum(float(row[1]) for row in bids)
            ask_volume = sum(float(row[1]) for row in asks)
            total = bid_volume + ask_volume
            imbalance = (bid_volume - ask_volume) / total if total else 0.0
            value = 1 if imbalance > ANCHOR * 0.1 else -1 if imbalance < -ANCHOR * 0.1 else 0
            return Signal("orderbook", value, {
                "bid_volume": bid_volume,
                "ask_volume": ask_volume,
                "imbalance": imbalance,
            })
        except (KeyError, IndexError, TypeError, ValueError, OSError) as exc:
            return Signal("orderbook", Ternary.NULL, {"error": str(exc)})


class OnChainSignal:
    """Interpret an already-fetched XRPL ledger response.

    WebSocket transport is intentionally supplied by the caller so importing
    Barrot does not require an optional websocket dependency.
    """

    def __init__(self, fetcher: Callable[[], dict[str, Any]] | None = None) -> None:
        self.fetcher = fetcher

    async def signal(self) -> Signal:
        if self.fetcher is None:
            return Signal("onchain", Ternary.NULL, {"error": "no fetcher configured"})
        try:
            result = self.fetcher()
            if asyncio.iscoroutine(result):
                result = await result
            ledger = result.get("result", {}).get("ledger", {})
            tx_count = ledger.get("transaction_count", 0)
            value = 1 if int(tx_count) > 100 else -1 if int(tx_count) < 20 else 0
            return Signal("onchain", value, {
                "ledger_index": ledger.get("ledger_index"),
                "transaction_count": int(tx_count),
            })
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            return Signal("onchain", Ternary.NULL, {"error": str(exc)})


class SentimentSignal:
    """Provide deterministic headline scoring without sending secrets to an LLM."""

    POSITIVE = ("adoption", "growth", "surge", "approval", "bull", "rise")
    NEGATIVE = ("fraud", "lawsuit", "hack", "decline", "bear", "fall")

    def classify(self, headlines: Iterable[str]) -> Signal:
        values = [str(headline) for headline in headlines]
        score = sum(
            (1 if any(word in text.casefold() for word in self.POSITIVE) else 0)
            - (1 if any(word in text.casefold() for word in self.NEGATIVE) else 0)
            for text in values
        )
        value = 1 if score > 0 else -1 if score < 0 else 0
        return Signal("sentiment", value, {"headlines": values, "score": score})


class XrpLiquidityBridge:
    """Collect signals and produce Barrot-compatible, simulation-only context."""

    def __init__(
        self,
        orderbook: OrderBookSignal | None = None,
        onchain: OnChainSignal | None = None,
        sentiment: SentimentSignal | None = None,
    ) -> None:
        self.orderbook = orderbook or OrderBookSignal()
        self.onchain = onchain or OnChainSignal()
        self.sentiment = sentiment or SentimentSignal()

    async def snapshot(self, headlines: Iterable[str] = ()) -> BridgeSnapshot:
        signals = [
            self.orderbook.signal(),
            await self.onchain.signal(),
            self.sentiment.classify(headlines),
        ]
        value = Ternary.resolve(*(item.value for item in signals))
        return BridgeSnapshot(value, Ternary.label(value), signals)

    async def barrot_context(self, headlines: Iterable[str] = ()) -> dict[str, Any]:
        snapshot = await self.snapshot(headlines)
        return {
            "domain": "xrp_liquidity",
            "capability": "market_analysis",
            "safety": {"mode": "simulation", "order_execution": False},
            "snapshot": snapshot.to_dict(),
        }

    @staticmethod
    def replay(
        snapshots: Iterable[BridgeSnapshot],
        starting_cash: float = 10_000.0,
    ) -> dict[str, Any]:
        """Replay signals as a no-fee position model; never places orders."""
        cash = float(starting_cash)
        position = 0
        for snapshot in snapshots:
            if snapshot.signal == Ternary.BUY and cash > 0:
                position, cash = 1, 0.0
            elif snapshot.signal == Ternary.SELL and position:
                position, cash = 0, starting_cash
        return {"starting_cash": starting_cash, "cash": cash, "position": position}


def extract_rss_titles(xml_text: str, limit: int = 5) -> list[str]:
    """Extract RSS titles while safely ignoring malformed or empty entries."""
    titles = re.findall(r"<title[^>]*>\s*<!\[CDATA\[(.*?)\]\]>\s*</title>", xml_text, re.I | re.S)
    if not titles:
        titles = re.findall(r"<title[^>]*>(.*?)</title>", xml_text, re.I | re.S)
    return [re.sub(r"<[^>]+>", "", title).strip() for title in titles[:limit] if title.strip()]
