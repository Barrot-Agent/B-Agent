"""Fail-closed quality gate for synchronized XRP spot, perpetual, and FX snapshots.

This module validates market observations only. It does not generate forecasts,
recommend trades, or infer price direction from data-quality checks.
"""
from datetime import datetime, timezone
from math import isfinite
from typing import Any, Mapping


EXPECTED_PAIRS = {
    "spot": "XRP/USD",
    "perpetual": "XRP/USDT",
    "fx": "USDT/USD",
}


def _parse_timestamp(value: Any, label: str, errors: list[str]):
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}: missing timestamp")
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except (TypeError, ValueError):
        errors.append(f"{label}: invalid ISO-8601 timestamp")
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        errors.append(f"{label}: timestamp must include a timezone")
        return None
    return parsed.astimezone(timezone.utc)


def _positive_number(value: Any, label: str, errors: list[str]):
    if isinstance(value, bool):
        errors.append(f"{label}: must be a finite positive number")
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        errors.append(f"{label}: must be a finite positive number")
        return None
    if not isfinite(number) or number <= 0:
        errors.append(f"{label}: must be a finite positive number")
        return None
    return number


def validate_snapshot(
    snapshot: Mapping[str, Any],
    *,
    now: datetime | None = None,
    max_age_seconds: float = 15.0,
    max_skew_seconds: float = 5.0,
    max_future_seconds: float = 2.0,
    max_received_age_seconds: float = 30.0,
    max_basis_bps: float = 500.0,
) -> dict[str, Any]:
    """Validate a three-leg snapshot and return a JSON-serializable decision.

    Required keys:
      cutoff_time: timezone-aware ISO-8601 string
      spot: pair, bid, ask, last, event_time, received_time
      perpetual: pair, mark_price, index_price, event_time, received_time
      fx: pair, bid, ask, last, event_time, received_time

    Event timestamps must be fresh relative to cutoff_time and mutually
    synchronized. received_time records when the collector captured the data.
    A last trade outside the displayed top of book is a warning, not a hard
    failure, because trade and quote events can arrive asynchronously.
    """
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(snapshot, Mapping):
        return {
            "status": "REJECTED",
            "accepted": False,
            "errors": ["snapshot: expected a mapping"],
            "warnings": [],
        }

    cutoff = _parse_timestamp(snapshot.get("cutoff_time"), "cutoff_time", errors)
    if now is None:
        current_time = datetime.now(timezone.utc)
    elif isinstance(now, datetime) and now.tzinfo is not None and now.utcoffset() is not None:
        current_time = now.astimezone(timezone.utc)
    else:
        current_time = None
        errors.append("now: must be a timezone-aware datetime")

    if cutoff is not None and current_time is not None:
        if (cutoff - current_time).total_seconds() > max_future_seconds:
            errors.append("cutoff_time: timestamp is in the future")

    legs: dict[str, dict[str, Any]] = {}
    event_times: dict[str, datetime] = {}

    for leg_name, expected_pair in EXPECTED_PAIRS.items():
        leg = snapshot.get(leg_name)
        if not isinstance(leg, Mapping):
            errors.append(f"{leg_name}: missing market observation")
            continue
        legs[leg_name] = dict(leg)
        if leg.get("pair") != expected_pair:
            errors.append(f"{leg_name}: expected pair {expected_pair}")

        event_time = _parse_timestamp(
            leg.get("event_time"), f"{leg_name}.event_time", errors
        )
        received_time = _parse_timestamp(
            leg.get("received_time"), f"{leg_name}.received_time", errors
        )
        if event_time is not None:
            event_times[leg_name] = event_time
            if cutoff is not None:
                age = (cutoff - event_time).total_seconds()
                if age > max_age_seconds:
                    errors.append(f"{leg_name}: event timestamp is stale")
                if age < -max_future_seconds:
                    errors.append(f"{leg_name}: event timestamp is in the future")
        if received_time is not None and cutoff is not None:
            receive_age = (cutoff - received_time).total_seconds()
            if receive_age < -max_future_seconds:
                errors.append(f"{leg_name}: received timestamp is after cutoff")
            elif receive_age > max_received_age_seconds:
                errors.append(f"{leg_name}: received timestamp is stale")
        if event_time is not None and received_time is not None:
            if (event_time - received_time).total_seconds() > max_future_seconds:
                errors.append(f"{leg_name}: event time is materially after receive time")

    if cutoff is not None and len(event_times) == len(EXPECTED_PAIRS):
        event_skew = (
            max(event_times.values()) - min(event_times.values())
        ).total_seconds()
        if event_skew > max_skew_seconds:
            errors.append("snapshot: market event timestamps exceed allowed skew")
    else:
        event_skew = None

    spot = legs.get("spot", {})
    perp = legs.get("perpetual", {})
    fx = legs.get("fx", {})

    spot_bid = _positive_number(spot.get("bid"), "spot.bid", errors)
    spot_ask = _positive_number(spot.get("ask"), "spot.ask", errors)
    spot_last = _positive_number(spot.get("last"), "spot.last", errors)
    perp_mark = _positive_number(perp.get("mark_price"), "perpetual.mark_price", errors)
    perp_index = _positive_number(perp.get("index_price"), "perpetual.index_price", errors)
    fx_bid = _positive_number(fx.get("bid"), "fx.bid", errors)
    fx_ask = _positive_number(fx.get("ask"), "fx.ask", errors)
    fx_last = _positive_number(fx.get("last"), "fx.last", errors)

    if spot_bid is not None and spot_ask is not None and spot_bid > spot_ask:
        errors.append("spot: crossed book (bid exceeds ask)")
    if fx_bid is not None and fx_ask is not None and fx_bid > fx_ask:
        errors.append("fx: crossed book (bid exceeds ask)")

    if spot_bid is not None and spot_ask is not None and spot_last is not None:
        if spot_last < spot_bid or spot_last > spot_ask:
            warnings.append("spot: last trade is outside displayed top of book")
    if fx_bid is not None and fx_ask is not None and fx_last is not None:
        if fx_last < fx_bid or fx_last > fx_ask:
            warnings.append("fx: last trade is outside displayed top of book")

    normalized_mark_usd = None
    basis_bps = None
    if (
        perp_mark is not None
        and fx_bid is not None
        and fx_ask is not None
        and spot_bid is not None
        and spot_ask is not None
    ):
        fx_mid = (fx_bid + fx_ask) / 2.0
        spot_mid = (spot_bid + spot_ask) / 2.0
        normalized_mark_usd = perp_mark * fx_mid
        basis_bps = (normalized_mark_usd / spot_mid - 1.0) * 10000.0
        if abs(basis_bps) > max_basis_bps:
            warnings.append("snapshot: normalized perpetual/spot basis exceeds warning threshold")

    return {
        "status": "ACCEPTED" if not errors else "REJECTED",
        "accepted": not errors,
        "cutoff_time": cutoff.isoformat() if cutoff is not None else None,
        "errors": errors,
        "warnings": warnings,
        "event_skew_seconds": event_skew,
        "normalized_perpetual_mark_usd": normalized_mark_usd,
        "perpetual_spot_basis_bps": basis_bps,
        "forecast_status": "NOT_ISSUED",
    }
