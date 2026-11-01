import datetime as dt
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "sentiment_shift.py"


def load_module():
    spec = importlib.util.spec_from_file_location("sentiment_shift_quality", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_empty_sentiment_window_is_not_reported_as_a_zero_shift():
    module = load_module()
    now = dt.datetime(2026, 10, 31, 5, 0, tzinfo=dt.timezone.utc)
    score, count = module.window_score(
        [],
        "xrp_relevance",
        now - dt.timedelta(hours=24),
        now,
    )
    assert score is None
    assert count == 0


def test_shift_output_marks_missing_windows_as_insufficient_data():
    source = SCRIPT.read_text(encoding="utf-8")
    assert '"status": "EVALUATED" if shift is not None else "INSUFFICIENT_DATA"' in source
    assert '"significant_shift": flagged if shift is not None else None' in source
    assert '"data_cutoff_utc": now.isoformat()' in source
