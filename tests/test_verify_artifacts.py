"""Tests for the cross-artifact checker.

Fixtures are copies of the shapes this repo actually shipped, so these tests
are regression locks: if the checker stops detecting the real defect, the test
fails. No test reads the live repo state, so fixing the repo cannot break the
suite.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("verify_artifacts", REPO / "scripts" / "verify_artifacts.py")
va = importlib.util.module_from_spec(_spec)
sys.modules["verify_artifacts"] = va
_spec.loader.exec_module(va)

NOW = 1_800_000_000.0


def codes(findings):
    return {f["code"] for f in findings}


# ------------------------------------------------------------------ paper state

# web/paper_trading_state.json as of 2026-11-17 — a position with no product.
CORRUPT_STATE = {
    "cash_usd": 9009.936613782476,
    "position_size": 0.012445158497236623,
    "position_product": None,
    "avg_entry_price": 80436.84,
    "trade_count": 126,
    "started_at": "2026-08-25T01:42:34.501971+00:00",
}


def test_corrupt_paper_state_is_rejected():
    findings = va.check_paper_state(CORRUPT_STATE)
    assert "position_without_product" in codes(findings)
    assert all(f["level"] == "error" for f in findings)


def test_clean_paper_state_passes():
    clean = dict(CORRUPT_STATE, position_product="BTC-USD")
    assert va.check_paper_state(clean) == []


def test_flat_state_with_entry_price_is_rejected():
    flat = {
        "cash_usd": 10_000.0,
        "position_size": 0.0,
        "position_product": None,
        "avg_entry_price": 80_000.0,
        "trade_count": 3,
    }
    assert "entry_without_position" in codes(va.check_paper_state(flat))


def test_negative_cash_is_rejected():
    broken = dict(CORRUPT_STATE, cash_usd=-1.0, position_product="BTC-USD")
    assert "cash_invalid" in codes(va.check_paper_state(broken))


def test_non_numeric_size_is_rejected():
    broken = dict(CORRUPT_STATE, position_size="0.01")
    assert "position_size_invalid" in codes(va.check_paper_state(broken))


# ----------------------------------------------------------------------- signal

# web/latest_signal.json as of 2026-11-17 — confidence 0.0, score 44, 18.6 days old.
CORRUPT_SIGNAL = {
    "timestamp": "2026-10-29T13:23:33.142057+00:00",
    "signal_text": "headlines…",
    "score": 44,
    "confidence": 0.0,
    "source": "sentiment unavailable (github_failed:missing GITHUB_TOKEN; groq_failed:429)+news(11)",
    "news_score": 88,
    "news_entries": 11,
    "generated_at_unix": 1793280213,
}


def test_zero_confidence_publish_is_rejected():
    assert "confidence_not_publishable" in codes(va.check_signal(CORRUPT_SIGNAL, now=NOW))


def test_stale_signal_is_rejected():
    assert "signal_stale" in codes(va.check_signal(CORRUPT_SIGNAL, now=NOW))


def test_fresh_confident_signal_passes():
    healthy = dict(CORRUPT_SIGNAL, confidence=0.62, generated_at_unix=NOW - 60,
                   product="XRP-USD")
    assert va.check_signal(healthy, now=NOW) == []


def test_signal_without_product_is_rejected():
    """Neither live signal file names its asset; the market is only in the prose."""
    assert "product_missing" in codes(va.check_signal(CORRUPT_SIGNAL, now=NOW))


def test_future_signal_is_rejected():
    future = dict(CORRUPT_SIGNAL, confidence=0.5, generated_at_unix=NOW + 600)
    assert "generated_at_in_future" in codes(va.check_signal(future, now=NOW))


def test_missing_generated_at_is_rejected():
    broken = {k: v for k, v in CORRUPT_SIGNAL.items() if k != "generated_at_unix"}
    broken["confidence"] = 0.5
    assert "generated_at_missing" in codes(va.check_signal(broken, now=NOW))


def test_empty_signal_file_is_rejected():
    assert "signal_missing" in codes(va.check_signal({}, now=NOW))


# --------------------------------------------------------------------- accuracy

# web/signal_accuracy.json as of 2026-11-17 — 772/1697 = 45.5%.
CORRUPT_ACCURACY = {"checked_count": 1697, "correct_count": 772, "accuracy_pct": 45.5}


def test_below_chance_accuracy_is_flagged():
    assert "below_chance_floor" in codes(va.check_accuracy(CORRUPT_ACCURACY))


def test_small_sample_is_not_flagged():
    tiny = {"checked_count": 10, "correct_count": 3, "accuracy_pct": 30.0}
    assert va.check_accuracy(tiny) == []


def test_inconsistent_accuracy_is_flagged():
    lying = {"checked_count": 100, "correct_count": 60, "accuracy_pct": 45.0}
    assert "accuracy_mismatch" in codes(va.check_accuracy(lying))


def test_correct_exceeding_checked_is_flagged():
    impossible = {"checked_count": 10, "correct_count": 11, "accuracy_pct": 110.0}
    assert "correct_exceeds_checked" in codes(va.check_accuracy(impossible))


def test_good_accuracy_passes():
    good = {"checked_count": 400, "correct_count": 224, "accuracy_pct": 56.0}
    assert va.check_accuracy(good) == []


# ------------------------------------------------------------------ integration


def test_verify_reads_real_file_shapes_from_a_tmp_root(tmp_path):
    web = tmp_path / "web"
    web.mkdir()
    (web / "paper_trading_state.json").write_text(json.dumps(CORRUPT_STATE))
    (web / "latest_signal.json").write_text(json.dumps(CORRUPT_SIGNAL))
    (web / "signal_accuracy.json").write_text(json.dumps(CORRUPT_ACCURACY))

    findings = va.verify(tmp_path, now=NOW)
    assert {"position_without_product", "confidence_not_publishable",
            "signal_stale", "below_chance_floor", "product_missing"} <= codes(findings)


def test_main_exits_nonzero_on_errors(tmp_path, capsys):
    web = tmp_path / "web"
    web.mkdir()
    (web / "paper_trading_state.json").write_text(json.dumps(CORRUPT_STATE))
    rc = va.main(["--root", str(tmp_path)])
    captured = capsys.readouterr().out
    assert rc == 1
    assert "position_without_product" in captured


def test_main_exits_zero_on_clean_root(tmp_path, capsys):
    (tmp_path / "web").mkdir()
    assert va.main(["--root", str(tmp_path)]) == 0
    assert "OK" in capsys.readouterr().out


def test_main_json_output_is_valid(tmp_path, capsys):
    web = tmp_path / "web"
    web.mkdir()
    (web / "signal_accuracy.json").write_text(json.dumps(CORRUPT_ACCURACY))
    va.main(["--root", str(tmp_path), "--json"])
    assert json.loads(capsys.readouterr().out)[0]["code"] == "below_chance_floor"


def test_checker_has_no_write_side_effects(tmp_path):
    web = tmp_path / "web"
    web.mkdir()
    before = {p.name: p.read_bytes() for p in web.iterdir()}
    va.main(["--root", str(tmp_path), "--json"])
    after = {p.name: p.read_bytes() for p in web.iterdir()}
    assert before == after
