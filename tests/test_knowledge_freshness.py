from datetime import datetime, timezone, timedelta
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from knowledge_freshness import (  # noqa: E402
    as_utc_iso,
    freshness_status,
    latest_ingested_at,
    parse_ingested_at,
)


def test_latest_ingested_at_uses_maximum_valid_timestamp():
    entries = [
        {"ingested_at": "2026-10-29T13:23:00Z"},
        {"ingested_at": "2026-10-28T09:00:00+00:00"},
        {"ingested_at": "invalid"},
        {"title": "missing timestamp"},
    ]
    latest = latest_ingested_at(entries)
    assert as_utc_iso(latest) == "2026-10-29T13:23:00+00:00"


def test_stale_inputs_are_not_labeled_fresh():
    now = datetime(2026, 11, 1, 16, 51, tzinfo=timezone.utc)
    data_as_of = datetime(2026, 10, 29, 13, 23, tzinfo=timezone.utc)
    assert freshness_status(data_as_of, now) == "STALE_INPUTS"


def test_recent_inputs_are_fresh():
    now = datetime(2026, 11, 1, 16, 51, tzinfo=timezone.utc)
    data_as_of = now - timedelta(hours=12)
    assert freshness_status(data_as_of, now) == "FRESH_INPUTS"


def test_missing_and_future_timestamps_are_explicit():
    now = datetime(2026, 11, 1, 16, 51, tzinfo=timezone.utc)
    assert freshness_status(None, now) == "NO_TIMESTAMPED_INPUTS"
    assert freshness_status(now + timedelta(hours=1), now) == "FUTURE_TIMESTAMP"


def test_sentiment_shift_uses_source_cutoff_not_run_time():
    source = (ROOT / "scripts" / "sentiment_shift.py").read_text(encoding="utf-8")
    assert '"generated_at_semantics": "source_data_cutoff_not_computation_time"' in source
    assert '"generated_at": as_utc_iso(data_as_of)' in source
    assert '"input_freshness_status": freshness_status(data_as_of, now)' in source
