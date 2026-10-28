#!/usr/bin/env python3
"""Read-only audit for reconciling paper-trading state against its append-only log.

This command never writes either input file. A successful identity candidate is
evidence for a separately reviewed state repair, not authorization to perform it.
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any

STATE_PATH = Path("web/paper_trading_state.json")
LOG_PATH = Path("web/paper_trading_log.jsonl")
PORTFOLIO_TOLERANCE_USD = 0.02


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be numeric, not boolean")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{field} must be finite")
    return number


def _timestamp(value: Any, line_number: int) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"line {line_number}: missing timestamp")
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"line {line_number}: invalid timestamp: {exc}") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"line {line_number}: timestamp must include a timezone")
    return parsed


def audit_state(
    persisted_state: dict[str, Any],
    log_text: str,
    *,
    portfolio_tolerance_usd: float = PORTFOLIO_TOLERANCE_USD,
) -> dict[str, Any]:
    """Replay the logged buy/sell decisions without modifying state or log."""
    errors: list[str] = []
    rows: list[dict[str, Any]] = []
    products: set[str] = set()
    previous_timestamp: datetime | None = None
    action_counts = {"buy": 0, "sell": 0, "hold": 0}
    portfolio_mismatches: list[dict[str, Any]] = []

    for line_number, raw_line in enumerate(log_text.splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            row = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_number}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(row, dict):
            errors.append(f"line {line_number}: record must be a JSON object")
            continue

        product = row.get("product")
        if not isinstance(product, str) or not product.strip():
            errors.append(f"line {line_number}: missing product identifier")
        else:
            products.add(product)

        try:
            timestamp = _timestamp(row.get("timestamp"), line_number)
            if previous_timestamp is not None and timestamp < previous_timestamp:
                errors.append(f"line {line_number}: timestamps are not chronological")
            previous_timestamp = timestamp
        except ValueError as exc:
            errors.append(str(exc))

        decision = row.get("decision")
        if not isinstance(decision, dict):
            errors.append(f"line {line_number}: decision must be an object")
            continue
        action = decision.get("action", "hold")
        if action not in action_counts:
            errors.append(f"line {line_number}: unsupported action {action!r}")
            continue
        action_counts[action] += 1

        try:
            price = _finite_number(row.get("price"), f"line {line_number} price")
            if price <= 0:
                raise ValueError(f"line {line_number}: price must be positive")
            amount = _finite_number(decision.get("amount_usd", 0) or 0, f"line {line_number} amount_usd")
            if amount < 0:
                raise ValueError(f"line {line_number}: amount_usd cannot be negative")
        except (TypeError, ValueError) as exc:
            errors.append(str(exc))
            continue

        rows.append({
            "line": line_number,
            "timestamp": row.get("timestamp"),
            "product": product,
            "price": price,
            "action": action,
            "amount_usd": amount,
            "recorded_portfolio_value": row.get("portfolio_value_usd"),
        })

    if not rows:
        errors.append("log contains no replayable records")
    if len(products) != 1:
        errors.append(
            "position identity is ambiguous: expected exactly one product across "
            f"the log, found {sorted(products)}"
        )
    if errors:
        return {
            "status": "BLOCKED",
            "errors": errors,
            "rows_parsed": len(rows),
            "product_ids": sorted(products),
            "state_mutated": False,
        }

    first_value = rows[0]["recorded_portfolio_value"]
    try:
        initial_cash = _finite_number(first_value, "first-row portfolio_value_usd")
    except (TypeError, ValueError) as exc:
        return {
            "status": "BLOCKED",
            "errors": [str(exc)],
            "rows_parsed": len(rows),
            "product_ids": sorted(products),
            "state_mutated": False,
        }
    if initial_cash < 0:
        return {
            "status": "BLOCKED",
            "errors": ["initial portfolio value cannot be negative"],
            "rows_parsed": len(rows),
            "product_ids": sorted(products),
            "state_mutated": False,
        }

    # The first recorded portfolio value is used as initial cash. This is valid
    # only for the repository's logged lifecycle, which starts flat and has no fees.
    cash = initial_cash
    position_size = 0.0
    avg_entry_price: float | None = None
    trade_count = 0
    portfolio_mismatches = []

    for row in rows:
        action = row["action"]
        amount = row["amount_usd"]
        price = row["price"]

        if action == "buy" and amount > 0:
            buy_amount = min(amount, cash * 0.2, cash)
            if buy_amount >= 1:
                quantity = buy_amount / price
                total_quantity = position_size + quantity
                previous_cost = (avg_entry_price or 0.0) * position_size
                avg_entry_price = (
                    (previous_cost + buy_amount) / total_quantity
                    if total_quantity else None
                )
                position_size = total_quantity
                cash -= buy_amount
                trade_count += 1
        elif action == "sell" and position_size > 0:
            sell_quantity = min(
                position_size,
                amount / price if amount else position_size,
            )
            proceeds = sell_quantity * price
            cash += proceeds
            position_size -= sell_quantity
            if position_size <= 0.00000001:
                position_size = 0.0
                avg_entry_price = None
            trade_count += 1

        expected_value = cash + position_size * price
        try:
            recorded_value = _finite_number(
                row["recorded_portfolio_value"],
                f"line {row['line']} portfolio_value_usd",
            )
            if not math.isclose(
                expected_value,
                recorded_value,
                rel_tol=1e-9,
                abs_tol=portfolio_tolerance_usd,
            ):
                portfolio_mismatches.append({
                    "line": row["line"],
                    "timestamp": row["timestamp"],
                    "expected": expected_value,
                    "recorded": recorded_value,
                    "delta": expected_value - recorded_value,
                })
        except (TypeError, ValueError) as exc:
            errors.append(str(exc))

    if portfolio_mismatches:
        errors.append(
            f"{len(portfolio_mismatches)} row(s) fail portfolio-value replay"
        )

    def persisted_number(field: str) -> float | None:
        value = persisted_state.get(field)
        if value is None and field == "avg_entry_price":
            return None
        return _finite_number(value, f"state {field}")

    try:
        persisted_cash = persisted_number("cash_usd")
        persisted_size = persisted_number("position_size")
        persisted_avg = persisted_number("avg_entry_price")
        persisted_count = persisted_state.get("trade_count")
        if not isinstance(persisted_count, int) or isinstance(persisted_count, bool):
            raise ValueError("state trade_count must be an integer")
        if not math.isclose(cash, persisted_cash, rel_tol=1e-9, abs_tol=1e-6):
            errors.append(f"cash mismatch: replay={cash}, state={persisted_cash}")
        if not math.isclose(position_size, persisted_size, rel_tol=1e-9, abs_tol=1e-10):
            errors.append(
                f"position_size mismatch: replay={position_size}, state={persisted_size}"
            )
        if avg_entry_price is None:
            if persisted_avg is not None:
                errors.append(
                    f"avg_entry_price mismatch: replay=None, state={persisted_avg}"
                )
        elif persisted_avg is None or not math.isclose(
            avg_entry_price, persisted_avg, rel_tol=1e-9, abs_tol=1e-6
        ):
            errors.append(
                f"avg_entry_price mismatch: replay={avg_entry_price}, state={persisted_avg}"
            )
        if trade_count != persisted_count:
            errors.append(
                f"trade_count mismatch: replay={trade_count}, state={persisted_count}"
            )
    except (TypeError, ValueError) as exc:
        errors.append(str(exc))

    product_candidate = next(iter(products)) if len(products) == 1 else None
    open_position = position_size > 1e-8
    persisted_product = persisted_state.get("position_product")
    if open_position:
        if persisted_product not in (None, "") and persisted_product != product_candidate:
            errors.append(
                f"position_product mismatch: log={product_candidate}, state={persisted_product}"
            )
    elif persisted_product not in (None, ""):
        errors.append(
            f"flat replay has stale position_product={persisted_product!r}"
        )

    if errors:
        status = "BLOCKED"
    elif open_position and persisted_product in (None, ""):
        status = "RECONCILED_IDENTITY_CANDIDATE"
    else:
        status = "RECONCILED"

    return {
        "status": status,
        "errors": errors,
        "rows_parsed": len(rows),
        "product_ids": sorted(products),
        "first_timestamp": rows[0]["timestamp"],
        "last_timestamp": rows[-1]["timestamp"],
        "action_counts": action_counts,
        "initial_cash_usd": initial_cash,
        "initial_cash_basis": (
            "first log row portfolio_value_usd; assumes the recorded lifecycle "
            "starts flat and has no fees"
        ),
        "replayed_state": {
            "cash_usd": cash,
            "position_size": position_size,
            "avg_entry_price": avg_entry_price,
            "trade_count": trade_count,
            "position_product_candidate": product_candidate if open_position else None,
        },
        "persisted_state": {
            "cash_usd": persisted_state.get("cash_usd"),
            "position_size": persisted_state.get("position_size"),
            "position_product": persisted_product,
            "avg_entry_price": persisted_state.get("avg_entry_price"),
            "trade_count": persisted_state.get("trade_count"),
        },
        "portfolio_value_mismatch_count": len(portfolio_mismatches),
        "portfolio_value_mismatch_examples": portfolio_mismatches[:5],
        "state_mutated": False,
        "note": (
            "This report is read-only. RECONCILED_IDENTITY_CANDIDATE does not "
            "authorize changing the persisted state; a separate reviewed action is required."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, default=STATE_PATH)
    parser.add_argument("--log", type=Path, default=LOG_PATH)
    args = parser.parse_args()

    try:
        state = json.loads(args.state.read_text(encoding="utf-8"))
        if not isinstance(state, dict):
            raise ValueError("state file must contain a JSON object")
        log_text = args.log.read_text(encoding="utf-8")
        report = audit_state(state, log_text)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        report = {
            "status": "BLOCKED",
            "errors": [str(exc)],
            "state_mutated": False,
        }

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] in {"RECONCILED", "RECONCILED_IDENTITY_CANDIDATE"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
