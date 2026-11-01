"""Timestamp provenance helpers for knowledge-base analytics."""

from datetime import datetime, timedelta, timezone


def parse_ingested_at(value):
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def latest_ingested_at(entries):
    timestamps = [
        ts
        for entry in entries
        if (ts := parse_ingested_at(entry.get("ingested_at"))) is not None
    ]
    return max(timestamps) if timestamps else None


def freshness_status(data_as_of, now=None, stale_after_hours=48):
    if data_as_of is None:
        return "NO_TIMESTAMPED_INPUTS"
    now = now or datetime.now(timezone.utc)
    if data_as_of.tzinfo is None:
        data_as_of = data_as_of.replace(tzinfo=timezone.utc)
    data_as_of = data_as_of.astimezone(timezone.utc)
    now = now.astimezone(timezone.utc)
    if data_as_of > now + timedelta(minutes=5):
        return "FUTURE_TIMESTAMP"
    if now - data_as_of > timedelta(hours=stale_after_hours):
        return "STALE_INPUTS"
    return "FRESH_INPUTS"


def as_utc_iso(value):
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()
