"""Batch entry evaluation from a dated market snapshot. Paper only.

A single snapshot can answer one question: *would this rotation be approved at
this price, and at what size?* It cannot answer the next one, because the exit
price does not exist yet. So this module records entries and marks every exit
`PENDING`. It never invents an exit ratio, a realised PnL, or an R-multiple.

Signal derivation is mechanical, never discretionary:

    trend            the asset's own USD trend, from the disclosed % changes
    ratio_signal     the direction of the XRP-per-asset ratio over 7d
    volume_signal    CONFIRMS only when volume for that asset is supplied

`ratio_signal == "FAVOURS"` means the asset has been losing value against XRP,
which is the regime `xrp_rotation.settle` profits from: XRP is sold high, the
asset falls, XRP is bought back cheaper. The gate additionally requires the
asset's own USD trend to be UP, so a candidate must be rising in USD while
losing ground to XRP. That is a narrow condition on purpose.

There is a known tension worth stating instead of hiding: those two conditions
pull in opposite directions, and on 2026-11-18 no offensive candidate satisfies
both. The gate therefore refuses every offensive rotation and only the defensive
USDT leg survives. That is the correct result for a bearish tape.

No network import, no client, no keys. Every number here is caller-supplied.
"""
from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path

from barrot_agent.trading.xrp_rotation import (
    ROUND_TRIP_COST_PCT,
    RotationPlan,
    StrategyConfig,
    evaluate,
)

ASSETS = ("BTC", "ETH", "SOL", "USDT", "XLM")
PRICE_ASSETS = ("BTC", "ETH", "XRP", "SOL", "XLM", "USDT")
DEFENSIVE_ASSET = "USDT"

EXIT_PENDING = "PENDING"

BATCH_FIELDS = (
    "candidate_id",
    "snapshot_id",
    "captured_at_utc",
    "asset",
    "decision",
    "thesis",
    "entry_ratio",
    "expected_move_pct",
    "stop_pct",
    "xrp_allocated",
    "xrp_at_risk",
    "risk_pct",
    "round_trip_cost_pct",
    "net_edge_pct",
    "counterfactual_7d_pct",
    "exit_status",
    "exit_ratio",
    "xrp_out",
    "xrp_delta",
    "usd_in",
    "usd_out",
    "usd_delta",
    "r_multiple",
    "reasons",
    "provenance",
)


def _finite(value) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value)


@dataclass(frozen=True)
class MarketSnapshot:
    snapshot_id: str
    captured_at_utc: str
    source: str
    provenance: str
    prices_usd: dict
    change_pct: dict
    market_trend: str
    btc_dominance_pct: float
    balances_start: dict
    volume_24h_usd: dict
    market_cap_usd: dict
    disabled_assets: tuple

    @classmethod
    def from_json(cls, path: Path | str) -> "MarketSnapshot":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if payload.get("record_type") != "market_snapshot":
            raise ValueError(f"not a market_snapshot: {payload.get('record_type')!r}")
        provenance = payload.get("provenance", "")
        if provenance not in ("SEAN_SUPPLIED", "RECORDED_FEED"):
            raise ValueError(f"refusing provenance {provenance!r}")
        prices = payload["prices_usd"]
        missing = [asset for asset in PRICE_ASSETS if not _finite(prices.get(asset))]
        if missing:
            raise ValueError(f"snapshot missing usable prices: {missing}")
        if not _finite(prices["XRP"]) or prices["XRP"] <= 0:
            raise ValueError("XRP price must be positive")
        for asset in PRICE_ASSETS:
            if prices[asset] <= 0:
                raise ValueError(f"{asset} price must be positive")
        return cls(
            snapshot_id=payload["snapshot_id"],
            captured_at_utc=payload["captured_at_utc"],
            source=payload.get("source", "UNKNOWN"),
            provenance=provenance,
            prices_usd=dict(prices),
            change_pct=dict(payload.get("change_pct", {})),
            market_trend=payload.get("regime", {}).get("market_trend", "UNKNOWN"),
            btc_dominance_pct=float(payload.get("regime", {}).get("btc_dominance_pct", 0.0)),
            balances_start=dict(payload["balances_start"]),
            volume_24h_usd=dict(payload.get("volume_24h_usd", {})),
            market_cap_usd=dict(payload.get("market_cap_usd", {})),
            disabled_assets=tuple(payload.get("disabled_assets", ())),
        )

    # --- derived market facts -------------------------------------------------

    def ratio(self, asset: str) -> float:
        """Units of `asset` per 1 XRP, computed from the supplied prices."""
        return self.prices_usd["XRP"] / self.prices_usd[asset]

    def relative_pct(self, asset: str) -> dict:
        """Asset performance minus XRP performance, per window."""
        if asset == "XRP":
            return {window: 0.0 for window in ("24h", "7d", "30d")}
        own = self.change_pct.get(asset, {})
        base = self.change_pct.get("XRP", {})
        out = {}
        for window in ("24h", "7d", "30d"):
            a, x = own.get(window), base.get(window)
            if _finite(a) and _finite(x):
                out[window] = round(a - x, 4)
        return out

    def ratio_change_pct(self, asset: str, window: str = "7d") -> float | None:
        """Change in XRP-per-asset over `window`, in percent."""
        relative = self.relative_pct(asset).get(window)
        base = self.change_pct.get("XRP", {}).get(window)
        own = self.change_pct.get(asset, {}).get(window)
        if not (_finite(base) and _finite(own)):
            return None
        del relative
        # ratio = p_xrp / p_asset, so ratio_new/ratio_old = (1+x)/(1+a).
        if own <= -100 or base <= -100:
            return None
        return round(((1 + base / 100.0) / (1 + own / 100.0) - 1.0) * 100.0, 4)

    def counterfactual_pct(self, asset: str, window: str = "7d") -> float | None:
        """XRP result of a round trip started `window` ago, before costs.

        Holding the asset then converting back to XRP returns
        (1+a)/(1+x) - 1, i.e. the inverse of the ratio change. This is an
        approximation from two disclosed endpoints: no path, no fees.
        """
        change = self.ratio_change_pct(asset, window)
        if change is None:
            return None
        return round(1.0 / (1.0 + change / 100.0) - 1.0, 6) * 100.0

    def trend(self, asset: str) -> str:
        """The asset's own USD trend from the disclosed changes."""
        if asset == DEFENSIVE_ASSET:
            return self.market_trend
        own = self.change_pct.get(asset, {})
        day, week = own.get("24h"), own.get("7d")
        if not (_finite(day) and _finite(week)):
            return "UNKNOWN"
        if day > 0 and week > 0:
            return "UP"
        if day < 0 and week < 0:
            return "DOWN"
        return "MIXED"

    def ratio_signal(self, asset: str) -> str:
        """FAVOURS when the asset is losing ground to XRP over 7d."""
        change = self.ratio_change_pct(asset, "7d")
        if change is None:
            return "UNKNOWN"
        if change <= -1.0:
            return "FAVOURS"  # asset cheaper in XRP terms: the engine's win case
        if change >= 1.0:
            return "AGAINST"
        return "NEUTRAL"

    def volume_signal(self, asset: str) -> str:
        """CONFIRMS only with supplied volume. Absence is not confirmation."""
        volume = self.volume_24h_usd.get(asset)
        if not _finite(volume) or volume <= 0:
            return "UNKNOWN"
        return "CONFIRMS"

    def defensive_trigger(self) -> bool:
        return self.market_trend == "DOWN"

    def xrp_dominance_pct(self) -> float | None:
        """Derive XRP dominance from BTC dominance and both market caps.

        total = btc_mcap / btc_dominance, xrp_dominance = xrp_mcap / total.
        Returns None when any input is missing, so the gate fails closed rather
        than receiving a fabricated number.
        """
        btc_cap = self.market_cap_usd.get("BTC")
        xrp_cap = self.market_cap_usd.get("XRP")
        if not _finite(btc_cap) or btc_cap <= 0:
            return None
        if not _finite(xrp_cap) or xrp_cap <= 0:
            return None
        if not _finite(self.btc_dominance_pct) or not 0 < self.btc_dominance_pct <= 100:
            return None
        total = btc_cap / (self.btc_dominance_pct / 100.0)
        return round(xrp_cap / total * 100.0, 4)


@dataclass(frozen=True)
class Candidate:
    """One proposed rotation. `thesis` is the reason, recorded and auditable."""

    candidate_id: str
    asset: str
    thesis: str
    expected_move_pct: float
    stop_pct: float = 5.0
    news: str = "CLEAR"
    bars_held: int = 0
    note: str = ""


def build_plan(
    snapshot: MarketSnapshot,
    candidate: Candidate,
    trend: str | None = None,
    ratio_signal: str | None = None,
    volume_signal: str | None = None,
) -> RotationPlan:
    """Turn a candidate plus snapshot into a plan, deriving signals by default."""
    asset = candidate.asset.upper()
    defensive = asset == DEFENSIVE_ASSET
    if defensive:
        default_trend = snapshot.market_trend if snapshot.defensive_trigger() else "FLAT"
        default_ratio = "AGAINST"
        default_volume = "THIN"
    else:
        default_trend = snapshot.trend(asset)
        default_ratio = snapshot.ratio_signal(asset)
        default_volume = snapshot.volume_signal(asset)
    return RotationPlan(
        rotation_id=candidate.candidate_id,
        timestamp_utc=snapshot.captured_at_utc,
        asset=asset,
        xrp_per_asset=snapshot.ratio(asset),
        expected_move_pct=candidate.expected_move_pct,
        stop_pct=candidate.stop_pct,
        trend=trend or default_trend,
        ratio_signal=ratio_signal or default_ratio,
        volume_signal=volume_signal or default_volume,
        news=candidate.news,
        xrp_dominance=snapshot.xrp_dominance_pct(),
        bars_held=candidate.bars_held,
        provenance=snapshot.provenance,
    )


def batch_rows(
    snapshot: MarketSnapshot,
    candidates: list[Candidate],
    stack_xrp: float,
    config: StrategyConfig | None = None,
) -> tuple[list[dict], list[str]]:
    """Evaluate candidates in order, spending capacity as entries are approved.

    Nothing is ever exited: every row is `exit_status=PENDING` and every
    realised field is left empty rather than filled with a placeholder number.
    """
    config = config or StrategyConfig(disabled_assets=snapshot.disabled_assets)
    rows: list[dict] = []
    log: list[str] = []
    available = float(stack_xrp)

    for candidate in candidates:
        if candidate.asset.upper() == "XRP":
            # Holding the base asset is a decision, not a rotation. Scoring it
            # through the rotation gate would report a false rejection.
            rows.append(
                {
                    "candidate_id": candidate.candidate_id,
                    "snapshot_id": snapshot.snapshot_id,
                    "captured_at_utc": snapshot.captured_at_utc,
                    "asset": "XRP",
                    "decision": "NO_TRADE",
                    "thesis": candidate.thesis,
                    "entry_ratio": "1.0000000000",
                    "expected_move_pct": candidate.expected_move_pct,
                    "stop_pct": candidate.stop_pct,
                    "xrp_allocated": "",
                    "xrp_at_risk": "",
                    "risk_pct": "",
                    "round_trip_cost_pct": 0.0,
                    "net_edge_pct": "",
                    "counterfactual_7d_pct": "0.0000",
                    "exit_status": EXIT_PENDING,
                    "exit_ratio": "",
                    "xrp_out": "",
                    "xrp_delta": "",
                    "usd_in": "",
                    "usd_out": "",
                    "usd_delta": "",
                    "r_multiple": "",
                    "reasons": "base asset held; no rotation proposed",
                    "provenance": snapshot.provenance,
                }
            )
            log.append(f"{candidate.candidate_id} XRP   NO_TRADE hold base asset")
            continue

        plan = build_plan(snapshot, candidate)
        verdict = evaluate(
            plan,
            stack_xrp=stack_xrp,
            config=config,
            available_xrp=available,
        )
        counterfactual = snapshot.counterfactual_pct(candidate.asset, "7d")
        row = {
            "candidate_id": candidate.candidate_id,
            "snapshot_id": snapshot.snapshot_id,
            "captured_at_utc": snapshot.captured_at_utc,
            "asset": candidate.asset,
            "decision": "ACCEPTED" if verdict.approved else "REJECTED",
            "thesis": candidate.thesis,
            "entry_ratio": f"{plan.xrp_per_asset:.10f}",
            "expected_move_pct": candidate.expected_move_pct,
            "stop_pct": candidate.stop_pct,
            "xrp_allocated": f"{verdict.xrp_allocated:.8f}" if verdict.approved else "",
            "xrp_at_risk": f"{verdict.xrp_at_risk:.8f}" if verdict.approved else "",
            "risk_pct": f"{verdict.risk_pct:.6f}" if verdict.approved else "",
            "round_trip_cost_pct": ROUND_TRIP_COST_PCT,
            "net_edge_pct": f"{verdict.net_edge_pct:.6f}" if verdict.approved else "",
            "counterfactual_7d_pct": "" if counterfactual is None else f"{counterfactual:.4f}",
            "exit_status": EXIT_PENDING,
            "exit_ratio": "",
            "xrp_out": "",
            "xrp_delta": "",
            "usd_in": "",
            "usd_out": "",
            "usd_delta": "",
            "r_multiple": "",
            "reasons": "; ".join(verdict.reasons),
            "provenance": snapshot.provenance,
        }
        if verdict.approved:
            available -= verdict.xrp_allocated
            log.append(
                f"{candidate.candidate_id} {candidate.asset:<5} ACCEPT "
                f"alloc={verdict.xrp_allocated:.4f} risk={verdict.risk_pct:.3f}% "
                f"available={available:.4f}"
            )
        else:
            log.append(f"{candidate.candidate_id} {candidate.asset:<5} REJECT {verdict.reasons[0]}")
        rows.append(row)
    return rows, log


def write_batch_csv(rows: list[dict], path: Path | str) -> Path:
    if not rows:
        raise ValueError("refusing to write an empty batch ledger")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=BATCH_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return target


def read_batch_csv(path: Path | str) -> list[dict]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def summarize(rows: list[dict], stack_xrp: float) -> dict:
    """Totals that cannot flatter the record: nothing has exited, so PnL is 0."""
    accepted = [row for row in rows if row["decision"] == "ACCEPTED"]
    rejected = [row for row in rows if row["decision"] == "REJECTED"]
    held = [row for row in rows if row["decision"] == "NO_TRADE"]
    allocated = sum(float(row["xrp_allocated"]) for row in accepted)
    at_risk = sum(float(row["xrp_at_risk"]) for row in accepted)
    by_reason: dict[str, int] = {}
    for row in rejected:
        reason = row["reasons"].split(";")[0].strip()
        by_reason[reason] = by_reason.get(reason, 0) + 1
    return {
        "candidates": len(rows),
        "accepted": len(accepted),
        "rejected": len(rejected),
        "no_trade": len(held),
        "stack_xrp": stack_xrp,
        "xrp_allocated": round(allocated, 8),
        "xrp_idle": round(stack_xrp - allocated, 8),
        "xrp_at_risk": round(at_risk, 8),
        "risk_pct_of_stack": round(at_risk / stack_xrp * 100.0, 4) if stack_xrp else 0.0,
        "exits_pending": len(accepted),
        "realised_xrp_delta": 0.0,
        "realised_usd_delta": 0.0,
        "realised_r": None,
        "win_rate": None,
        "reject_reasons": by_reason,
    }
