"""Paper-trading sandbox: position sizing and a fail-closed rule gate.

This module cannot trade. It has no network code, no client, no key handling and
no order path. Every price is supplied by the caller. The only thing it produces
is arithmetic plus an approve/reject verdict that can be audited later.

Rules enforced, all rejections explicit:

1. A stop is always required and must sit on the losing side of entry.
2. Risk per trade is at most 1.0% of the paper balance.
3. The reward-to-risk ratio is at least 2.0.
4. At most 3 trades per day.
5. Notional exposure does not exceed the balance (no leverage; BARROT-ADDED).
6. The contract checklist must pass, or be not applicable for a native asset.
7. Video-style "high impact news" blocks the trade. Unknown news is allowed in
   paper only and is flagged, because it cannot be verified offline.

Any input that cannot be evaluated is rejected. There is no default that
approves a trade.
"""
from __future__ import annotations

import csv
import math
import os
from dataclasses import dataclass
from pathlib import Path

MAX_RISK_PCT = 1.0
MIN_R_MULTIPLE = 2.0
MAX_TRADES_PER_DAY = 3
STARTING_BALANCE = 10_000.0

LIVE_KEY_MARKERS = (
    "BINANCE",
    "COINBASE",
    "KRAKEN",
    "BYBIT",
    "OKX",
    "KUCOIN",
    "BITTREX",
    "GEMINI",
    "ALPACA",
    "DERIBIT",
)

CSV_FIELDS = (
    "trade_id",
    "timestamp_utc",
    "pair",
    "side",
    "status",
    "balance_before",
    "risk_pct",
    "risk_amount_usd",
    "entry",
    "stop",
    "target",
    "stop_distance",
    "units",
    "notional_usd",
    "implied_leverage",
    "r_multiple_planned",
    "exit_price",
    "r_multiple_realised",
    "pnl_usd",
    "balance_after",
    "news",
    "contract_check",
    "thesis",
    "mistake_tag",
    "data_source",
    "reject_reasons",
)


@dataclass(frozen=True)
class Setup:
    """A proposed paper trade. Prices are caller-supplied, never fetched."""

    trade_id: str
    timestamp_utc: str
    pair: str
    side: str
    entry: float
    stop: float
    target: float
    thesis: str = ""
    news: str = "UNKNOWN"
    contract_check: str = "N/A_NATIVE"


@dataclass(frozen=True)
class Verdict:
    setup: Setup
    approved: bool
    reasons: tuple[str, ...]
    risk_pct: float
    risk_amount: float
    stop_distance: float
    units: float
    notional: float
    implied_leverage: float
    r_multiple: float


def _finite(*values: float) -> bool:
    return all(isinstance(v, (int, float)) and math.isfinite(v) for v in values)


def live_credentials_present(env: dict[str, str] | None = None) -> list[str]:
    """Return the names of exchange credential variables that are set.

    Presence alone is enough to stop the sandbox: a paper loop that can see a
    live key is one bug away from using it.
    """
    source = os.environ if env is None else env
    found = []
    for name in sorted(source):
        upper = name.upper()
        if upper.endswith(("_API_KEY", "_API_SECRET", "_SECRET_KEY")):
            if any(marker in upper for marker in LIVE_KEY_MARKERS):
                found.append(name)
    return found


def evaluate(
    setup: Setup,
    balance: float = STARTING_BALANCE,
    risk_pct: float = 1.0,
    trades_today: int = 0,
) -> Verdict:
    """Size the trade and return a verdict. Fail closed on anything unknown."""
    reasons: list[str] = []

    if setup.side not in ("long", "short"):
        reasons.append(f"side must be long or short, got {setup.side!r}")

    prices_ok = _finite(setup.entry, setup.stop, setup.target, balance)
    if not prices_ok:
        reasons.append("entry, stop, target and balance must be finite numbers")
    elif balance <= 0:
        reasons.append("balance must be positive")

    if prices_ok and setup.side == "long" and setup.stop >= setup.entry:
        reasons.append("long stop must be below entry")
    if prices_ok and setup.side == "short" and setup.stop <= setup.entry:
        reasons.append("short stop must be above entry")

    if risk_pct <= 0 or risk_pct > MAX_RISK_PCT:
        reasons.append(f"risk_pct {risk_pct} outside 0 < risk <= {MAX_RISK_PCT}")

    if trades_today < 0 or trades_today >= MAX_TRADES_PER_DAY:
        reasons.append(f"daily trade cap reached ({trades_today}/{MAX_TRADES_PER_DAY})")

    if setup.news.upper() == "HIGH_IMPACT":
        reasons.append("high-impact news window: trade blocked")

    if setup.contract_check.upper() not in ("PASS", "N/A_NATIVE"):
        reasons.append(f"contract checklist verdict {setup.contract_check!r} is not a pass")

    stop_distance = 0.0
    units = 0.0
    notional = 0.0
    implied_leverage = 0.0
    r_multiple = 0.0
    risk_amount = 0.0

    if not reasons:
        stop_distance = abs(setup.entry - setup.stop)
        if stop_distance <= 0:
            reasons.append("stop distance is zero")
        else:
            risk_amount = balance * risk_pct / 100.0
            units = risk_amount / stop_distance
            notional = units * setup.entry
            implied_leverage = notional / balance
            reward = abs(setup.target - setup.entry)
            r_multiple = reward / stop_distance
            if r_multiple < MIN_R_MULTIPLE:
                reasons.append(f"reward/risk {r_multiple:.2f}R below {MIN_R_MULTIPLE}R minimum")
            if implied_leverage > 1.0:
                reasons.append(
                    f"implied exposure {implied_leverage:.2f}x exceeds 1.00x (no leverage)"
                )

    return Verdict(
        setup=setup,
        approved=not reasons,
        reasons=tuple(reasons),
        risk_pct=risk_pct,
        risk_amount=round(risk_amount, 6),
        stop_distance=round(stop_distance, 8),
        units=round(units, 8),
        notional=round(notional, 6),
        implied_leverage=round(implied_leverage, 6),
        r_multiple=round(r_multiple, 6),
    )


def to_row(
    verdict: Verdict,
    balance_before: float = STARTING_BALANCE,
    exit_price: float | None = None,
    realised_r: float | None = None,
    mistake_tag: str = "",
) -> dict[str, object]:
    """Flatten a verdict into one CSV row. Open trades carry no PnL."""
    setup = verdict.setup
    pnl = 0.0
    balance_after = balance_before
    status = "REJECTED" if not verdict.approved else "OPEN"
    if verdict.approved and realised_r is not None:
        pnl = verdict.risk_amount * realised_r
        balance_after = balance_before + pnl
        status = "CLOSED"
    return {
        "trade_id": setup.trade_id,
        "timestamp_utc": setup.timestamp_utc,
        "pair": setup.pair,
        "side": setup.side,
        "status": status,
        "balance_before": round(balance_before, 2),
        "risk_pct": verdict.risk_pct,
        "risk_amount_usd": verdict.risk_amount,
        "entry": setup.entry,
        "stop": setup.stop,
        "target": setup.target,
        "stop_distance": verdict.stop_distance,
        "units": verdict.units,
        "notional_usd": verdict.notional,
        "implied_leverage": verdict.implied_leverage,
        "r_multiple_planned": verdict.r_multiple,
        "exit_price": "" if exit_price is None else exit_price,
        "r_multiple_realised": "" if realised_r is None else realised_r,
        "pnl_usd": round(pnl, 2),
        "balance_after": round(balance_after, 2),
        "news": setup.news,
        "contract_check": setup.contract_check,
        "thesis": setup.thesis,
        "mistake_tag": mistake_tag,
        "data_source": "SIMULATED_NO_FEED",
        "reject_reasons": " | ".join(verdict.reasons),
    }


def write_csv(rows: list[dict[str, object]], path: Path | str) -> Path:
    """Write rows with a fixed header. Refuses to write an empty ledger."""
    if not rows:
        raise ValueError("refusing to write an empty paper ledger")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return target


def read_csv(path: Path | str) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def summarise(
    rows: list[dict[str, str | object]],
    starting_balance: float = STARTING_BALANCE,
) -> dict:
    """Win rate, average R, max drawdown and mistake counts over closed rows."""
    closed = [row for row in rows if str(row.get("status")) == "CLOSED"]
    wins = 0
    r_values = []
    equity = starting_balance
    peak = starting_balance
    max_drawdown = 0.0
    mistakes: dict[str, int] = {}

    for row in closed:
        try:
            realised = float(row.get("r_multiple_realised") or 0.0)
        except (TypeError, ValueError):
            realised = 0.0
        r_values.append(realised)
        if realised > 0:
            wins += 1
        equity += float(row.get("pnl_usd") or 0.0)
        peak = max(peak, equity)
        if peak > 0:
            max_drawdown = max(max_drawdown, (peak - equity) / peak)
        tag = str(row.get("mistake_tag") or "").strip()
        if tag:
            mistakes[tag] = mistakes.get(tag, 0) + 1

    top = sorted(mistakes.items(), key=lambda item: (-item[1], item[0]))[:3]
    return {
        "closed_trades": len(closed),
        "wins": wins,
        "win_rate": round(wins / len(closed), 4) if closed else 0.0,
        "avg_r": round(sum(r_values) / len(r_values), 4) if r_values else 0.0,
        "max_drawdown_pct": round(max_drawdown * 100.0, 4),
        "ending_balance": round(equity, 2),
        "top_mistakes": top,
    }
