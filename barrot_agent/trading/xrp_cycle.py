"""Rotating feedback loop: FEED -> TRADE -> REVIEW -> EVOLVE -> REQUEST NEXT FEED.

Timing matters and is easy to get wrong. A decision made at snapshot N can only
be graded at snapshot N+1. So one run of this module does two things in order:

    1. MARK the positions opened at earlier snapshots against the new prices,
       then REVIEW those decisions, including the ones the gate refused
    2. OPEN this cycle's candidates at the new prices

That means the review printed on cycle N is the review *of* cycle N-1. Nothing
is graded against the same snapshot it was decided on.

A position only becomes CLOSED when its stop or its target is actually breached
by a later price. Otherwise it stays OPEN with an unrealised result, so no cycle
can manufacture a win rate out of price drift.
"""
from __future__ import annotations

import csv
from pathlib import Path

from barrot_agent.trading.xrp_batch import Candidate, MarketSnapshot, build_plan
from barrot_agent.trading.xrp_rotation import (
    FEE_PCT_PER_SIDE,
    SLIPPAGE_PCT_PER_SIDE,
    StrategyConfig,
    evaluate,
)

FOCUS_ROTATION = ("BTC", "ETH", "SOL", "XLM", "USDT")
DEFENSIVE_ASSET = "USDT"
PER_SIDE = 1.0 - (FEE_PCT_PER_SIDE + SLIPPAGE_PCT_PER_SIDE) / 100.0

FIELDS = (
    "cycle",
    "trade_id",
    "snapshot_id",
    "snapshot_time",
    "focus",
    "asset",
    "thesis",
    "entry_ratio",
    "xrp_usd_entry",
    "stop_pct",
    "expected_move_pct",
    "xrp_in",
    "xrp_at_risk",
    "exit_status",
    "mark_ratio",
    "mark_time",
    "mark_return_pct",
    "unrealised_xrp",
    "unrealised_usd",
    "xrp_out",
    "realised_xrp",
    "realised_usd",
    "r_multiple",
    "outcome",
    "mistake_tag",
    "decision",
    "reasons",
    "provenance",
)

# Confidence weights. They sum to 100 and each one is a fact, not a feeling.
WEIGHTS = {
    "provenance_recorded": 20,
    "closed_rotations": 20,
    "stack_grew": 15,
    "drawdown_ok": 15,
    "expectancy_positive": 15,
    "no_violations": 15,
}


def focus_for(cycle: int) -> str:
    """Rotate the focus so five cycles cover the universe, then repeat."""
    return FOCUS_ROTATION[(max(cycle, 1) - 1) % len(FOCUS_ROTATION)]


def rotation_return_pct(entry_ratio: float, mark_ratio: float) -> float:
    """Return of XRP -> asset -> XRP, both cost legs included."""
    if entry_ratio <= 0 or mark_ratio <= 0:
        return 0.0
    return round((entry_ratio / mark_ratio) * PER_SIDE * PER_SIDE * 100.0 - 100.0, 6)


# --- candidates ---------------------------------------------------------------


def candidates_for(snapshot: MarketSnapshot, focus: str, cycle: int) -> list[Candidate]:
    """Five candidates: a diagnostic ladder on the focus, the defensive leg, a hold.

    The ladder forces one signal at a time so the rejects say *which* missing
    input is binding, rather than repeating the same reason three times:

        as-derived          what the gate says with the data I actually have
        trend forced UP     isolates whether volume or ratio also blocks
        trend + volume UP   isolates the ratio signal as the only remaining block

    These are diagnostics, not approvals. A forced signal means "if this were
    true", and every row records that it was forced.
    """
    tag = f"C{cycle:02d}"
    asset = DEFENSIVE_ASSET if focus == DEFENSIVE_ASSET else focus
    ladder = (
        ("ASIS", {}, f"Cycle {cycle} focus {asset}, signals exactly as derived."),
        ("TUP", {"trend_override": "UP"},
         f"Cycle {cycle} focus {asset} with the trend forced UP: isolates volume."),
        ("TUPVOL", {"trend_override": "UP", "volume_override": "CONFIRMS"},
         f"Cycle {cycle} focus {asset} with trend and volume forced: isolates ratio."),
    )
    out = []
    for suffix, overrides, thesis in ladder:
        out.append(
            Candidate(
                candidate_id=f"{tag}-{asset}-{suffix}",
                asset=asset,
                thesis=thesis,
                expected_move_pct=3.0,
                stop_pct=5.0,
                **overrides,
            )
        )
    out.append(
        Candidate(
            candidate_id=f"{tag}-USDT-DEF",
            asset=DEFENSIVE_ASSET,
            thesis=f"Cycle {cycle} defensive leg, standard 5% backstop.",
            expected_move_pct=3.0,
            stop_pct=5.0,
        )
    )
    out.append(
        Candidate(
            candidate_id=f"{tag}-XRP-HOLD",
            asset="XRP",
            thesis=f"Cycle {cycle}: hold the base asset and be scored against the rotations.",
            expected_move_pct=0.0,
        )
    )
    return out


# --- opening a position -------------------------------------------------------


def open_positions(snapshot: MarketSnapshot, cycle: int, stack: float,
                   available: float, config: StrategyConfig) -> tuple[list[dict], float]:
    focus = focus_for(cycle)
    rows: list[dict] = []
    for candidate in candidates_for(snapshot, focus, cycle):
        if candidate.asset == "XRP":
            rows.append(
                _row(snapshot, cycle, focus, candidate, "NO_TRADE",
                     entry_ratio=1.0, reasons="base asset held; no rotation proposed")
            )
            continue
        plan = build_plan(snapshot, candidate)
        verdict = evaluate(plan, stack_xrp=stack, config=config, available_xrp=available)
        if not verdict.approved:
            rows.append(
                _row(snapshot, cycle, focus, candidate, "REJECTED",
                     entry_ratio=plan.xrp_per_asset, reasons="; ".join(verdict.reasons))
            )
            continue
        available -= verdict.xrp_allocated
        row = _row(snapshot, cycle, focus, candidate, "ACCEPTED",
                   entry_ratio=plan.xrp_per_asset, reasons="")
        row["xrp_in"] = f"{verdict.xrp_allocated:.8f}"
        row["xrp_at_risk"] = f"{verdict.xrp_at_risk:.8f}"
        row["exit_status"] = "OPEN"
        rows.append(row)
    return rows, available


def _row(snapshot: MarketSnapshot, cycle: int, focus: str, candidate: Candidate,
         decision: str, entry_ratio: float, reasons: str) -> dict:
    return {
        "cycle": cycle,
        "trade_id": candidate.candidate_id,
        "snapshot_id": snapshot.snapshot_id,
        "snapshot_time": snapshot.captured_at_utc,
        "focus": focus,
        "asset": candidate.asset,
        "thesis": candidate.thesis,
        "entry_ratio": f"{entry_ratio:.12f}",
        "xrp_usd_entry": f"{snapshot.prices_usd.get('XRP', 0.0):.8f}",
        "stop_pct": candidate.stop_pct,
        "expected_move_pct": candidate.expected_move_pct,
        "xrp_in": "",
        "xrp_at_risk": "",
        "exit_status": "NONE",
        "mark_ratio": "",
        "mark_time": "",
        "mark_return_pct": "",
        "unrealised_xrp": "",
        "unrealised_usd": "",
        "xrp_out": "",
        "realised_xrp": "",
        "realised_usd": "",
        "r_multiple": "",
        "outcome": "",
        "mistake_tag": "",
        "decision": decision,
        "reasons": reasons,
        "provenance": snapshot.provenance,
    }


# --- marking and closing ------------------------------------------------------


def mark_row(row: dict, snapshot: MarketSnapshot) -> dict:
    """Reprice one open position. Closes it only if stop or target is breached."""
    if row.get("exit_status") != "OPEN" or not row.get("entry_ratio"):
        return row
    asset = row["asset"]
    if asset not in snapshot.prices_usd:
        return row

    entry_ratio = float(row["entry_ratio"])
    mark_ratio = snapshot.ratio(asset)
    xrp_in = float(row["xrp_in"])
    xrp_usd_entry = float(row.get("xrp_usd_entry") or snapshot.prices_usd["XRP"])
    xrp_usd_mark = snapshot.prices_usd["XRP"]

    pct = rotation_return_pct(entry_ratio, mark_ratio)
    xrp_out = xrp_in * (entry_ratio / mark_ratio) * PER_SIDE * PER_SIDE

    updated = dict(row)
    updated["mark_ratio"] = f"{mark_ratio:.12f}"
    updated["mark_time"] = snapshot.captured_at_utc
    updated["mark_return_pct"] = f"{pct:.6f}"
    updated["unrealised_xrp"] = f"{xrp_out - xrp_in:.8f}"
    updated["unrealised_usd"] = f"{xrp_out * xrp_usd_mark - xrp_in * xrp_usd_entry:.4f}"

    stop = float(row["stop_pct"])
    target = float(row["expected_move_pct"])
    risk = max(float(row["xrp_at_risk"]), 1e-9)
    if pct <= -stop:
        updated.update(
            exit_status="CLOSED",
            xrp_out=f"{xrp_out:.8f}",
            realised_xrp=f"{xrp_out - xrp_in:.8f}",
            realised_usd=f"{xrp_out * xrp_usd_mark - xrp_in * xrp_usd_entry:.4f}",
            r_multiple=f"{(xrp_out - xrp_in) / risk:.6f}",
            outcome="LOSS",
            mistake_tag="STOP_HIT",
        )
    elif pct >= target:
        updated.update(
            exit_status="CLOSED",
            xrp_out=f"{xrp_out:.8f}",
            realised_xrp=f"{xrp_out - xrp_in:.8f}",
            realised_usd=f"{xrp_out * xrp_usd_mark - xrp_in * xrp_usd_entry:.4f}",
            r_multiple=f"{(xrp_out - xrp_in) / risk:.6f}",
            outcome="WIN",
            mistake_tag="",
        )
    return updated


# --- review -------------------------------------------------------------------


def review(rows: list[dict], snapshot: MarketSnapshot, cycle: int) -> dict:
    """Grade one cycle's decisions against the snapshot that followed it."""
    accepted = [r for r in rows if r["decision"] == "ACCEPTED"]
    rejected = [r for r in rows if r["decision"] == "REJECTED"]
    closed = [r for r in rows if r["exit_status"] == "CLOSED"]

    # .get() everywhere: a ledger written before a column existed must still grade.
    unrealised = sum(float(r.get("unrealised_xrp") or 0) for r in accepted)
    realised = sum(float(r.get("realised_xrp") or 0) for r in closed)
    realised_usd = sum(float(r.get("realised_usd") or 0) for r in closed)
    open_count = sum(1 for r in accepted if r["exit_status"] == "OPEN")

    # Score the refusals. A refusal that would have paid is a cost of the gate.
    refused: dict[str, float] = {}
    for row in rejected:
        ratio = float(row.get("entry_ratio") or 0)
        if ratio <= 0:
            continue
        pct = rotation_return_pct(ratio, snapshot.ratio(row["asset"]))
        refused[row["asset"]] = pct

    wins = [r for r in closed if r.get("outcome") == "WIN"]
    win_rate = round(len(wins) / len(closed) * 100.0, 2) if closed else None
    focus = rows[0].get("focus", "UNKNOWN") if rows else "UNKNOWN"

    return {
        "cycle": cycle,
        "snapshot_read_at": snapshot.snapshot_id,
        "focus": focus,
        "accepted": len(accepted),
        "rejected": len(rejected),
        "closed": len(closed),
        "open": open_count,
        "win_rate_pct": win_rate,
        "realised_xrp": round(realised, 8),
        "realised_usd": round(realised_usd, 4),
        "unrealised_xrp": round(unrealised, 8),
        "refused_return_pct": refused,
        "gate_saved": sorted(a for a, p in refused.items() if p < 0),
        "gate_cost": sorted((a for a, p in refused.items() if p > 0),
                            key=lambda a: -refused[a]),
        "top_lesson": _lesson(refused, closed),
        "rule": rule_from({"gate_cost": sorted(
            (a for a, p in refused.items() if p > 0), key=lambda a: -refused[a]),
            "refused_return_pct": refused}),
    }


def _lesson(refused: dict[str, float], closed: list[dict]) -> str:
    if not refused:
        return "No rotation was refused, so the gate went untested this cycle."
    missed = {a: p for a, p in refused.items() if p > 0}
    if missed:
        worst = max(missed, key=missed.get)
        return (
            f"Refused {worst}; it would have returned {missed[worst]:+.2f}% after costs. "
            "A refusal is a decision and it is scored like one."
        )
    best = max(refused.items(), key=lambda kv: kv[1])
    return (
        f"Every refusal was correct. The closest call was {best[0]} at {best[1]:+.2f}%, "
        "so the gate earned its cost this cycle."
    )


def rule_from(report: dict) -> tuple[str, str]:
    """Turn one cycle's measured result into one imperative rule plus its evidence.

    A finding is not a rule. This converts "refused X, it would have paid" into
    something the next cycle must actually do differently.
    """
    cost = report.get("gate_cost") or []
    refused = report.get("refused_return_pct", {})
    if cost:
        worst = cost[0]
        pct = refused.get(worst, 0.0)
        return (
            f"A missing input is not neutral. An UNKNOWN field forced a refusal on "
            f"{worst} that cost {pct:+.2f}% at the next snapshot. Treat a missing "
            f"field as a request for data, not as a decision.",
            f"{worst} refused, would have returned {pct:+.2f}% after costs",
        )
    if refused:
        best = max(refused.items(), key=lambda kv: kv[1])
        return (
            "Keep the 1.5x cost threshold. Every refusal this cycle was correct.",
            f"closest call {best[0]} at {best[1]:+.2f}%",
        )
    return ("No rule change: the gate went untested this cycle.", "no refusals")


def patterns(review_row: dict, snapshot: MarketSnapshot) -> str:
    """One intuition-library entry, written from measured values only."""
    xrp = snapshot.change_pct.get("XRP", {})
    btc = snapshot.change_pct.get("BTC", {})
    relative = None
    if xrp.get("24h") is not None and btc.get("24h") is not None:
        relative = round(xrp["24h"] - btc["24h"], 2)
    if relative is None:
        return "Insufficient data to state a pattern."
    if relative > 0 and (btc.get("24h") or 0) < 0:
        setup = f"XRP outperformed BTC by {relative:+.2f}% while BTC was down"
        consequence = (
            "offensive rotations marked negative and the defensive leg marked "
            f"{review_row['unrealised_xrp']:+.4f} XRP unrealised"
        )
    elif relative < 0:
        setup = f"XRP underperformed BTC by {relative:+.2f}%"
        consequence = "the rotation out of XRP had the wind behind it"
    else:
        setup = "XRP tracked BTC"
        consequence = "no relative-strength edge to rotate on"
    return f"When {setup}, then {consequence}."


# --- confidence ---------------------------------------------------------------


def confidence_score(closed_count: int, provenance: str, stack_delta: float,
                     drawdown_pct: float, recent_expectancy: float,
                     violations: int) -> dict:
    provenance_recorded = provenance in ("RECORDED_FEED", "SEAN_SUPPLIED")
    parts = {
        "provenance_recorded": WEIGHTS["provenance_recorded"] if provenance_recorded else 0,
        "closed_rotations": round(
            min(closed_count, 100) / 100 * WEIGHTS["closed_rotations"], 2
        ),
        "stack_grew": WEIGHTS["stack_grew"] if stack_delta > 0 else 0,
        "drawdown_ok": WEIGHTS["drawdown_ok"] if closed_count and drawdown_pct <= 10 else 0,
        "expectancy_positive": WEIGHTS["expectancy_positive"]
        if closed_count and recent_expectancy > 0 else 0,
        "no_violations": WEIGHTS["no_violations"] if closed_count and violations == 0 else 0,
    }
    return {"score": round(sum(parts.values()), 2), "parts": parts,
            "max": sum(WEIGHTS.values()), "closed": closed_count}


# --- ledger -------------------------------------------------------------------


def read_ledger(path: Path | str) -> list[dict]:
    target = Path(path)
    if not target.exists():
        return []
    with target.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_ledger(rows: list[dict], path: Path | str) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in FIELDS})
    return target


def next_cycle(rows: list[dict]) -> int:
    cycles = [int(row["cycle"]) for row in rows if str(row.get("cycle", "")).isdigit()]
    return (max(cycles) + 1) if cycles else 1


def import_batch1(path: Path | str, rows: list[dict],
                  xrp_usd_entry: float = 0.9778) -> list[dict]:
    """Bring Batch 1 forward as cycle 0, refusals included.

    The refusals are imported on purpose: they are decisions, and cycle 0 can
    only be graded if the ones the gate turned down are in the ledger.
    """
    target = Path(path)
    if not target.exists():
        return rows
    imported = []
    with target.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if any(existing["trade_id"] == row["candidate_id"] for existing in rows):
                continue
            decision = row.get("decision", "")
            if decision not in ("ACCEPTED", "REJECTED", "NO_TRADE"):
                continue
            imported.append(
                {
                    "cycle": 0,
                    "trade_id": row["candidate_id"],
                    "snapshot_id": row["snapshot_id"],
                    "snapshot_time": row["captured_at_utc"],
                    "focus": "USDT",
                    "asset": row["asset"],
                    "thesis": row["thesis"],
                    "entry_ratio": row["entry_ratio"],
                    "xrp_usd_entry": f"{xrp_usd_entry:.8f}",
                    "stop_pct": row["stop_pct"],
                    "expected_move_pct": row["expected_move_pct"],
                    "xrp_in": row["xrp_allocated"] if decision == "ACCEPTED" else "",
                    "xrp_at_risk": row["xrp_at_risk"] if decision == "ACCEPTED" else "",
                    "exit_status": "OPEN" if decision == "ACCEPTED" else "NONE",
                    "decision": decision,
                    "reasons": row["reasons"],
                    "provenance": row["provenance"],
                }
            )
    return imported + rows
