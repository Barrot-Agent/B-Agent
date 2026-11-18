"""XRP-centric paper rotation engine. No network, no keys, no orders.

The base asset is XRP. A rotation sells XRP for another asset and later buys XRP
back. Success is measured in XRP first and in USD second:

    xrp_out > xrp_in          -> the stack grew
    usd_out > usd_in          -> the USD value grew

Both can disagree. A rotation can grow XRP while the USD value falls, or the
reverse. The ledger records both so neither can hide the other.

Costs are charged on both legs. A rotation that looks profitable before costs is
the normal failure mode, so the gate requires the projected move to clear the
round-trip cost with a margin.

Nothing here can trade: no network import, no client, no key handling. Every
ratio is caller-supplied and carries a provenance tag.
"""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass, field, replace
from pathlib import Path

ASSETS = ("BTC", "ETH", "SOL", "USDT", "XLM")
DEFENSIVE_ASSET = "USDT"

STARTING_XRP = 10_000.0
MAX_RISK_PCT = 1.0
FEE_PCT_PER_SIDE = 0.10
SLIPPAGE_PCT_PER_SIDE = 0.10
ROUND_TRIP_COST_PCT = 2.0 * (FEE_PCT_PER_SIDE + SLIPPAGE_PCT_PER_SIDE)
MIN_EDGE_MULTIPLE = 1.5
MAX_HOLD_BARS = 10
MAX_TRADES_PER_DAY = 3

CONFIDENCE_MIN_CLOSED = 100
CONFIDENCE_MAX_DRAWDOWN_PCT = 10.0
CONFIDENCE_RECENT_WINDOW = 30

CSV_FIELDS = (
    "rotation_id",
    "timestamp_utc",
    "asset",
    "xrp_in",
    "entry_ratio",
    "exit_ratio",
    "stop_pct",
    "xrp_out",
    "xrp_delta",
    "xrp_delta_pct",
    "usd_in",
    "usd_out",
    "usd_delta",
    "r_multiple",
    "outcome",
    "exit_reason",
    "cost_pct",
    "bars_held",
    "mistake_tag",
    "rule_violations",
    "provenance",
)


@dataclass(frozen=True)
class RotationPlan:
    """A proposed XRP rotation. Ratios are units of asset per 1 XRP."""

    rotation_id: str
    timestamp_utc: str
    asset: str
    xrp_per_asset: float
    expected_move_pct: float
    stop_pct: float
    trend: str = "UNKNOWN"
    ratio_signal: str = "UNKNOWN"
    volume_signal: str = "UNKNOWN"
    news: str = "UNKNOWN"
    xrp_dominance: float | None = None
    bars_held: int = 0
    provenance: str = "UNKNOWN"


@dataclass(frozen=True)
class RotationVerdict:
    plan: RotationPlan
    approved: bool
    reasons: tuple[str, ...]
    xrp_allocated: float
    risk_pct: float
    xrp_at_risk: float
    round_trip_cost_pct: float
    net_edge_pct: float


@dataclass(frozen=True)
class RotationOutcome:
    plan: RotationPlan
    exit_ratio: float
    xrp_out: float
    xrp_delta: float
    xrp_delta_pct: float
    usd_in: float
    usd_out: float
    usd_delta: float
    r_multiple: float
    outcome: str
    exit_reason: str
    mistake_tag: str = ""
    rule_violations: int = 0


@dataclass(frozen=True)
class StrategyConfig:
    """Parameters the learning loop may change. Evidence required, one at a time."""

    disabled_assets: tuple[str, ...] = ()
    min_edge_multiple: float = MIN_EDGE_MULTIPLE
    max_hold_bars: int = MAX_HOLD_BARS
    notes: tuple[str, ...] = field(default_factory=tuple)


def _finite(*values: float | None) -> bool:
    return all(isinstance(v, (int, float)) and math.isfinite(v) for v in values)


def evaluate(
    plan: RotationPlan,
    stack_xrp: float = STARTING_XRP,
    config: StrategyConfig | None = None,
    trades_today: int = 0,
) -> RotationVerdict:
    """Size the rotation and return a fail-closed verdict."""
    config = config or StrategyConfig()
    reasons: list[str] = []
    asset = plan.asset.upper()

    if asset == "XRP":
        reasons.append("XRP is the base asset; it is not a rotation target")
    if asset not in ASSETS:
        reasons.append(f"asset {plan.asset!r} not in {ASSETS}")
    if asset in config.disabled_assets:
        reasons.append(f"asset {asset} disabled by the learning loop")

    if not _finite(stack_xrp, plan.xrp_per_asset, plan.expected_move_pct, plan.stop_pct):
        reasons.append("stack, ratio, expected move and stop must be finite")
    elif stack_xrp <= 0 or plan.xrp_per_asset <= 0:
        reasons.append("stack and ratio must be positive")

    if plan.stop_pct <= 0 or plan.stop_pct >= 100:
        reasons.append(f"stop_pct {plan.stop_pct} outside 0 < stop < 100")

    if plan.bars_held < 0 or plan.bars_held > config.max_hold_bars:
        reasons.append(f"time stop hit ({plan.bars_held} > {config.max_hold_bars} bars)")

    if trades_today < 0 or trades_today >= MAX_TRADES_PER_DAY:
        reasons.append(f"daily rotation cap reached ({trades_today}/{MAX_TRADES_PER_DAY})")

    if plan.xrp_dominance is None:
        reasons.append("XRP dominance missing: scan incomplete")
    elif not _finite(plan.xrp_dominance) or not 0 <= plan.xrp_dominance <= 100:
        reasons.append("XRP dominance outside 0..100")

    # Alignment. USDT is the defensive leg: it is allowed when the offensive
    # signals fail or when news is high impact. Offensive legs need all three.
    if asset == DEFENSIVE_ASSET:
        defensive = (
            plan.news == "HIGH_IMPACT"
            or plan.trend == "DOWN"
            or plan.ratio_signal == "AGAINST"
        )
        if not defensive:
            reasons.append(
                "USDT rotation needs a defensive trigger "
                "(high-impact news, downtrend, or ratio against)"
            )
    else:
        if plan.news == "HIGH_IMPACT":
            reasons.append("high-impact news: no offensive rotation")
        if plan.news == "UNKNOWN":
            reasons.append("news state unknown: scan incomplete")
        if plan.trend != "UP":
            reasons.append(f"trend {plan.trend!r} is not UP")
        if plan.ratio_signal != "FAVOURS":
            reasons.append(f"ratio signal {plan.ratio_signal!r} is not FAVOURS")
        if plan.volume_signal != "CONFIRMS":
            reasons.append(f"volume signal {plan.volume_signal!r} does not CONFIRM")

    cost = ROUND_TRIP_COST_PCT
    net_edge = 0.0
    xrp_allocated = 0.0
    xrp_at_risk = 0.0
    risk_pct = 0.0

    if not reasons:
        net_edge = plan.expected_move_pct - cost
        if net_edge <= 0:
            reasons.append(f"net edge {net_edge:.3f}% does not clear {cost:.3f}% round-trip cost")
        if plan.expected_move_pct < config.min_edge_multiple * cost:
            reasons.append(
                f"expected move {plan.expected_move_pct:.3f}% below "
                f"{config.min_edge_multiple:.2f}x cost ({config.min_edge_multiple * cost:.3f}%)"
            )
        # Full size up to the risk ceiling, never beyond the stack. The worst
        # case includes both legs of cost, so advertised risk equals realised
        # risk instead of understating it.
        worst_case_pct = plan.stop_pct + cost
        max_by_risk = stack_xrp * (MAX_RISK_PCT / 100.0) / (worst_case_pct / 100.0)
        xrp_allocated = round(min(stack_xrp, max_by_risk), 8)
        xrp_at_risk = round(xrp_allocated * worst_case_pct / 100.0, 8)
        risk_pct = round(xrp_at_risk / stack_xrp * 100.0, 6)
        if risk_pct > MAX_RISK_PCT:
            reasons.append(f"risk {risk_pct}% exceeds {MAX_RISK_PCT}%")

    return RotationVerdict(
        plan=plan,
        approved=not reasons,
        reasons=tuple(reasons),
        xrp_allocated=xrp_allocated,
        risk_pct=risk_pct,
        xrp_at_risk=xrp_at_risk,
        round_trip_cost_pct=cost,
        net_edge_pct=round(net_edge, 6),
    )


def settle(
    verdict: RotationVerdict,
    exit_ratio: float,
    xrp_usd_entry: float,
    xrp_usd_exit: float,
    exit_reason: str = "TARGET",
    mistake_tag: str = "",
    rule_violations: int = 0,
) -> RotationOutcome:
    """Close an approved rotation and book the XRP and USD results."""
    plan = verdict.plan
    per_side = 1.0 - (FEE_PCT_PER_SIDE + SLIPPAGE_PCT_PER_SIDE) / 100.0
    asset_units = verdict.xrp_allocated * plan.xrp_per_asset * per_side
    xrp_out = asset_units / exit_ratio * per_side
    xrp_delta = xrp_out - verdict.xrp_allocated
    xrp_delta_pct = (
        xrp_delta / verdict.xrp_allocated * 100.0 if verdict.xrp_allocated else 0.0
    )
    risk_xrp = verdict.xrp_at_risk if verdict.xrp_at_risk else 1.0
    r_multiple = xrp_delta / risk_xrp
    outcome = "WIN" if xrp_delta > 0 else ("LOSS" if xrp_delta < 0 else "FLAT")
    return RotationOutcome(
        plan=plan,
        exit_ratio=exit_ratio,
        xrp_out=round(xrp_out, 8),
        xrp_delta=round(xrp_delta, 8),
        xrp_delta_pct=round(xrp_delta_pct, 6),
        usd_in=round(verdict.xrp_allocated * xrp_usd_entry, 4),
        usd_out=round(xrp_out * xrp_usd_exit, 4),
        usd_delta=round(xrp_out * xrp_usd_exit - verdict.xrp_allocated * xrp_usd_entry, 4),
        r_multiple=round(r_multiple, 6),
        outcome=outcome,
        exit_reason=exit_reason,
        mistake_tag=mistake_tag,
        rule_violations=rule_violations,
    )


def auto_lesson(outcomes: list[RotationOutcome], window: int = 10) -> dict:
    """Review the last `window` closed rotations and propose exactly one change."""
    recent = outcomes[-window:]
    if not recent:
        return {"window": 0, "proposal": {"change": "NONE", "why": "NO_TRADES"}, "per_asset": {}}

    per_asset: dict[str, dict] = {}
    for item in recent:
        bucket = per_asset.setdefault(
            item.plan.asset, {"trades": 0, "wins": 0, "xrp_delta": 0.0, "r_sum": 0.0}
        )
        bucket["trades"] += 1
        bucket["wins"] += 1 if item.outcome == "WIN" else 0
        bucket["xrp_delta"] += item.xrp_delta
        bucket["r_sum"] += item.r_multiple

    for bucket in per_asset.values():
        bucket["win_rate"] = round(bucket["wins"] / bucket["trades"], 4)
        bucket["avg_r"] = round(bucket["r_sum"] / bucket["trades"], 4)
        bucket["xrp_delta"] = round(bucket["xrp_delta"], 6)

    ranked = sorted(per_asset.items(), key=lambda kv: kv[1]["xrp_delta"])
    worst_asset, worst = ranked[0]
    best_asset, best = ranked[-1]

    mistakes: dict[str, int] = {}
    for item in recent:
        if item.mistake_tag:
            mistakes[item.mistake_tag] = mistakes.get(item.mistake_tag, 0) + 1
    top_mistakes = sorted(mistakes.items(), key=lambda kv: (-kv[1], kv[0]))[:3]

    proposal: dict
    if worst["trades"] >= 4 and worst["xrp_delta"] < 0 and worst_asset != DEFENSIVE_ASSET:
        proposal = {
            "change": "disable_asset",
            "asset": worst_asset,
            "why": f"{worst_asset}: {worst['trades']} trades, {worst['xrp_delta']:.4f} XRP net",
        }
    elif worst["trades"] < 4:
        proposal = {
            "change": "NONE",
            "why": f"INSUFFICIENT_EVIDENCE: worst bucket has {worst['trades']} trades, need 4",
        }
    else:
        proposal = {"change": "NONE", "why": "NO_NEGATIVE_BUCKET_WITH_ENOUGH_EVIDENCE"}

    return {
        "window": len(recent),
        "per_asset": per_asset,
        "best_asset": best_asset,
        "best_xrp_delta": best["xrp_delta"],
        "worst_asset": worst_asset,
        "worst_xrp_delta": worst["xrp_delta"],
        "top_mistakes": top_mistakes,
        "proposal": proposal,
    }


def apply_lesson(config: StrategyConfig, lesson: dict) -> tuple[StrategyConfig, bool]:
    """Apply one evidence-backed change. No evidence, no change."""
    proposal = lesson.get("proposal", {})
    if proposal.get("change") != "disable_asset":
        return config, False
    asset = proposal["asset"]
    if asset in config.disabled_assets:
        return config, False
    updated = replace(
        config,
        disabled_assets=tuple(sorted(config.disabled_assets + (asset,))),
        notes=config.notes + (proposal["why"],),
    )
    return updated, True


def max_drawdown_pct(equity: list[float]) -> float:
    peak = 0.0
    worst = 0.0
    for value in equity:
        peak = max(peak, value)
        if peak > 0:
            worst = max(worst, (peak - value) / peak * 100.0)
    return round(worst, 4)


def confidence(outcomes: list[RotationOutcome], provenance: str) -> dict:
    """Decide whether this record justifies asking Sean for real money.

    The provenance gate is absolute: simulated scenarios can never justify real
    capital, no matter how good the numbers look.
    """
    closed = [item for item in outcomes if item.exit_ratio > 0]
    equity: list[float] = []
    stack = STARTING_XRP
    for item in closed:
        stack += item.xrp_delta
        equity.append(stack)
    total_delta = sum(item.xrp_delta for item in closed)
    recent = closed[-CONFIDENCE_RECENT_WINDOW:]
    recent_avg_r = sum(item.r_multiple for item in recent) / len(recent) if recent else 0.0
    violations = sum(item.rule_violations for item in closed)
    drawdown = max_drawdown_pct(equity) if equity else 0.0

    checks = [
        ("provenance is recorded market data", provenance != "SIMULATED_SCENARIO", provenance),
        (
            f"closed rotations >= {CONFIDENCE_MIN_CLOSED}",
            len(closed) >= CONFIDENCE_MIN_CLOSED,
            f"{len(closed)}",
        ),
        ("XRP stack grew after costs", total_delta > 0, f"{total_delta:.4f} XRP"),
        (
            f"XRP drawdown <= {CONFIDENCE_MAX_DRAWDOWN_PCT}%",
            bool(closed) and drawdown <= CONFIDENCE_MAX_DRAWDOWN_PCT,
            f"{drawdown}%",
        ),
        ("recent expectancy > 0", recent_avg_r > 0, f"{recent_avg_r:.4f}R over last {len(recent)}"),
        ("zero rule violations", bool(closed) and violations == 0, f"{violations}"),
    ]
    ready = all(ok for _, ok, _ in checks)
    return {"ready": ready, "checks": checks, "closed": len(closed)}


def to_row(outcome: RotationOutcome) -> dict[str, object]:
    return {
        "rotation_id": outcome.plan.rotation_id,
        "timestamp_utc": outcome.plan.timestamp_utc,
        "asset": outcome.plan.asset,
        "xrp_in": round(outcome.xrp_out - outcome.xrp_delta, 8),
        "entry_ratio": outcome.plan.xrp_per_asset,
        "exit_ratio": outcome.exit_ratio,
        "stop_pct": outcome.plan.stop_pct,
        "xrp_out": outcome.xrp_out,
        "xrp_delta": outcome.xrp_delta,
        "xrp_delta_pct": outcome.xrp_delta_pct,
        "usd_in": outcome.usd_in,
        "usd_out": outcome.usd_out,
        "usd_delta": outcome.usd_delta,
        "r_multiple": outcome.r_multiple,
        "outcome": outcome.outcome,
        "exit_reason": outcome.exit_reason,
        "cost_pct": ROUND_TRIP_COST_PCT,
        "bars_held": outcome.plan.bars_held,
        "mistake_tag": outcome.mistake_tag,
        "rule_violations": outcome.rule_violations,
        "provenance": outcome.plan.provenance,
    }


def from_row(row: dict[str, str]) -> RotationOutcome:
    """Rebuild an outcome from a ledger row, without trusting hidden state."""
    plan = RotationPlan(
        rotation_id=row["rotation_id"],
        timestamp_utc=row["timestamp_utc"],
        asset=row["asset"],
        xrp_per_asset=float(row["entry_ratio"]),
        expected_move_pct=0.0,
        stop_pct=float(row["stop_pct"]),
        provenance=row["provenance"],
    )
    return RotationOutcome(
        plan=plan,
        exit_ratio=float(row["exit_ratio"]),
        xrp_out=float(row["xrp_out"]),
        xrp_delta=float(row["xrp_delta"]),
        xrp_delta_pct=float(row["xrp_delta_pct"]),
        usd_in=float(row["usd_in"]),
        usd_out=float(row["usd_out"]),
        usd_delta=float(row["usd_delta"]),
        r_multiple=float(row["r_multiple"]),
        outcome=row["outcome"],
        exit_reason=row["exit_reason"],
        mistake_tag=row["mistake_tag"],
        rule_violations=int(row["rule_violations"]),
    )


def write_csv(rows: list[dict[str, object]], path: Path | str) -> Path:
    if not rows:
        raise ValueError("refusing to write an empty rotation ledger")
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
