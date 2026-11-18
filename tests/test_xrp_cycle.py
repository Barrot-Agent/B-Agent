"""Tests for the rotating feedback loop.

The properties worth locking, in order of how easy they are to get wrong:

  * a decision made at snapshot N is only graded at snapshot N+1
  * marking a position at its own entry snapshot yields the round-trip cost and
    nothing else, so price drift cannot manufacture a win rate
  * a rejected rotation is still graded, and is recorded as a gate cost when it
    would have paid
  * the confidence score is six facts that sum to 100, not a feeling
"""
from __future__ import annotations

import csv
from dataclasses import replace
from pathlib import Path

import pytest

from barrot_agent.trading.xrp_batch import MarketSnapshot
from barrot_agent.trading.xrp_cycle import (
    FOCUS_ROTATION,
    PER_SIDE,
    WEIGHTS,
    candidates_for,
    confidence_score,
    focus_for,
    import_batch1,
    mark_row,
    next_cycle,
    open_positions,
    patterns,
    read_ledger,
    review,
    rotation_return_pct,
    rule_from,
    write_ledger,
)
from barrot_agent.trading.xrp_rotation import StrategyConfig

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "market/live-2026-11-18T193754Z.json"
SEAN = ROOT / "market/2026-11-18-sean-feed.json"
BATCH1 = ROOT / "XRP_BATCH1.csv"


def snap(prices: dict, snapshot_id: str = "S1", trend: str = "DOWN",
         changes: dict | None = None, provenance: str = "RECORDED_FEED") -> MarketSnapshot:
    """A minimal snapshot. The dataclass does not validate, which is deliberate."""
    return MarketSnapshot(
        snapshot_id=snapshot_id,
        captured_at_utc="2026-11-18T00:00:00Z",
        source="TEST",
        provenance=provenance,
        prices_usd={"XRP": 1.0, **prices},
        change_pct=changes or {},
        market_trend=trend,
        btc_dominance_pct=50.0,
        balances_start={"xrp": 100.0, "usd_value": 100.0},
        volume_24h_usd={},
        market_cap_usd={},
        disabled_assets=(),
    )


def open_row(asset: str = "BTC", entry_ratio: float = 2.0, xrp_in: float = 10.0,
             stop: float = 5.0, target: float = 3.0) -> dict:
    return {
        "cycle": 1,
        "trade_id": f"T-{asset}",
        "asset": asset,
        "entry_ratio": f"{entry_ratio:.12f}",
        "xrp_usd_entry": "1.0",
        "xrp_in": f"{xrp_in:.8f}",
        "xrp_at_risk": "1.00000000",
        "stop_pct": stop,
        "expected_move_pct": target,
        "exit_status": "OPEN",
        "decision": "ACCEPTED",
        "focus": "BTC",
        "provenance": "RECORDED_FEED",
    }


def at_ratio(ratios: dict[str, float], **kwargs) -> MarketSnapshot:
    """A snapshot whose XRP-per-asset ratios are exactly the ones given.

    `entry_ratio` in the ledger is asset-units-per-XRP, so a target ratio r for
    an asset priced against XRP=1.0 needs an asset price of 1/r.
    """
    return snap({asset: 1.0 / ratio for asset, ratio in ratios.items()}, **kwargs)


# --- focus rotation -----------------------------------------------------------


def test_focus_rotates_through_the_whole_universe():
    assert [focus_for(i) for i in range(1, 6)] == list(FOCUS_ROTATION)
    assert focus_for(6) == "BTC"


def test_focus_handles_cycle_zero_and_negatives():
    assert focus_for(0) == "BTC"
    assert focus_for(-3) == "BTC"


# --- return maths -------------------------------------------------------------


def test_flat_rotation_returns_only_the_cost():
    assert rotation_return_pct(2.0, 2.0) == pytest.approx(-0.3996, abs=1e-9)


def test_doubling_the_ratio_returns_99_2_pct():
    # entry 2.0 -> mark 1.0 means one XRP now buys twice as much asset
    assert rotation_return_pct(2.0, 1.0) == pytest.approx(99.2008, abs=1e-6)


def test_cost_is_applied_twice():
    gross = (2.0 / 1.0) * 100.0 - 100.0
    net = rotation_return_pct(2.0, 1.0)
    assert net < gross
    assert PER_SIDE == pytest.approx(0.998, abs=1e-12)


@pytest.mark.parametrize("entry, mark", [(0, 1), (1, 0), (-1, 1), (1, -1)])
def test_degenerate_ratios_return_zero(entry, mark):
    assert rotation_return_pct(entry, mark) == 0.0


# --- candidates ---------------------------------------------------------------


def test_candidates_are_a_diagnostic_ladder_not_three_copies():
    s = at_ratio({"BTC": 2.0}, trend="DOWN")
    out = candidates_for(s, "BTC", 1)
    ids = [c.candidate_id for c in out]
    assert ids == [
        "C01-BTC-ASIS", "C01-BTC-TUP", "C01-BTC-TUPVOL",
        "C01-USDT-DEF", "C01-XRP-HOLD",
    ]
    only = [c for c in out if c.asset == "BTC"]
    assert only[0].trend_override is None
    assert only[1].trend_override == "UP"
    assert only[2].trend_override == "UP" and only[2].volume_override == "CONFIRMS"


def test_defensive_focus_does_not_duplicate_the_asset():
    out = candidates_for(at_ratio({"USDT": 1.0}), "USDT", 5)
    assert [c.candidate_id for c in out] == [
        "C05-USDT-ASIS", "C05-USDT-TUP", "C05-USDT-TUPVOL",
        "C05-USDT-DEF", "C05-XRP-HOLD",
    ]


def test_hold_candidate_has_no_risk():
    hold = [c for c in candidates_for(at_ratio({"BTC": 2.0}), "BTC", 1)
            if c.candidate_id == "C01-XRP-HOLD"][0]
    assert hold.asset == "XRP"
    assert hold.expected_move_pct == 0.0


# --- opening ------------------------------------------------------------------


def test_rejections_still_carry_an_entry_ratio():
    """Without a stored ratio a refusal cannot be graded next cycle."""
    s = MarketSnapshot.from_json(LIVE)
    rows, _ = open_positions(s, 1, 102.27, 76.0, StrategyConfig())
    rejected = [r for r in rows if r["decision"] == "REJECTED"]
    assert rejected
    assert all(float(r["entry_ratio"]) > 0 for r in rejected)


def test_open_positions_respects_available_capacity():
    s = MarketSnapshot.from_json(LIVE)
    rows, left = open_positions(s, 1, 102.27, 12.0, StrategyConfig())
    allocated = sum(float(r["xrp_in"]) for r in rows if r["xrp_in"])
    assert allocated <= 12.0
    assert left == pytest.approx(12.0 - allocated)


def test_disabled_asset_produces_no_accepted_rows():
    s = MarketSnapshot.from_json(LIVE)
    rows, _ = open_positions(s, 1, 102.27, 76.0, StrategyConfig(disabled_assets=("USDT",)))
    assert not [r for r in rows if r["decision"] == "ACCEPTED" and r["asset"] == "USDT"]


# --- marking ------------------------------------------------------------------


def test_marking_at_the_entry_snapshot_closes_nothing():
    """The core anti-fabrication property: entry == mark is a cost, not a win."""
    row = open_row(entry_ratio=2.0)
    marked = mark_row(row, at_ratio({"BTC": 2.0}, snapshot_id="S1"))
    assert marked["exit_status"] == "OPEN"
    assert float(marked["mark_return_pct"]) == pytest.approx(-0.3996, abs=1e-6)
    assert marked.get("realised_xrp") in ("", None)


def test_marking_records_unrealised_but_stays_open():
    row = open_row(entry_ratio=2.0, xrp_in=10.0)
    marked = mark_row(row, at_ratio({"BTC": 1.99}, snapshot_id="S2"))
    assert marked["exit_status"] == "OPEN"
    assert float(marked["mark_return_pct"]) > 0
    assert float(marked["unrealised_xrp"]) > 0


def test_stop_breach_closes_as_a_loss():
    # mark ratio 2.2 -> (2/2.2)*0.998^2*100-100 = -9.45%
    marked = mark_row(open_row(entry_ratio=2.0), at_ratio({"BTC": 2.2}, snapshot_id="S3"))
    assert marked["exit_status"] == "CLOSED"
    assert marked["outcome"] == "LOSS"
    assert marked["mistake_tag"] == "STOP_HIT"
    assert float(marked["realised_xrp"]) < 0
    assert float(marked["r_multiple"]) < 0


def test_target_reached_closes_as_a_win():
    # mark ratio 1.9 -> (2/1.9)*0.998^2*100-100 = +4.84% >= 3%
    marked = mark_row(open_row(entry_ratio=2.0), at_ratio({"BTC": 1.9}, snapshot_id="S4"))
    assert marked["exit_status"] == "CLOSED"
    assert marked["outcome"] == "WIN"
    assert marked["mistake_tag"] == ""
    assert float(marked["realised_xrp"]) > 0


def test_closed_rows_are_not_re_marked():
    closed = dict(open_row(), exit_status="CLOSED", realised_xrp="-1.0")
    again = mark_row(closed, at_ratio({"BTC": 1.0}, snapshot_id="S5"))
    assert again == closed


def test_missing_asset_price_leaves_the_row_untouched():
    row = open_row(asset="XLM")
    assert mark_row(row, at_ratio({"BTC": 1.0})) == row


def test_usd_realised_uses_the_xrp_price_at_each_leg():
    row = open_row(entry_ratio=2.0, xrp_in=10.0)
    exit_ = at_ratio({"BTC": 2.0}, snapshot_id="S2")
    exit_.prices_usd["XRP"] = 2.0  # XRP itself doubled in USD terms
    marked = mark_row(dict(row, xrp_usd_entry="1.0"), exit_)
    assert float(marked["unrealised_usd"]) > float(marked["unrealised_xrp"])


# --- review -------------------------------------------------------------------


def test_review_grades_refusals_and_separates_cost_from_saved():
    rows = [
        dict(open_row("BTC"), decision="REJECTED", entry_ratio="2.0"),
        dict(open_row("ETH"), decision="REJECTED", entry_ratio="2.0"),
        dict(open_row("USDT"), decision="REJECTED", entry_ratio="2.0"),
        open_row("BTC"),
    ]
    s = at_ratio({"BTC": 2.2, "ETH": 1.8, "USDT": 2.0}, snapshot_id="S2")
    report = review(rows, s, cycle=1)
    assert report["accepted"] == 1
    assert report["rejected"] == 3
    assert report["refused_return_pct"]["BTC"] < 0     # saved
    assert report["refused_return_pct"]["ETH"] > 0     # cost
    assert "ETH" in report["gate_cost"]
    assert "BTC" in report["gate_saved"]
    assert "ETH" in report["top_lesson"]


def test_win_rate_is_undefined_without_closed_rows():
    report = review([open_row()], at_ratio({"BTC": 2.0}), cycle=1)
    assert report["win_rate_pct"] is None
    assert report["closed"] == 0


def test_win_rate_counts_only_closed_rows():
    winner = dict(open_row("BTC"), exit_status="CLOSED", outcome="WIN", realised_xrp="1.0")
    loser = dict(open_row("ETH"), exit_status="CLOSED", outcome="LOSS", realised_xrp="-1.0")
    report = review([winner, loser, open_row("SOL")], at_ratio({"BTC": 2.0}), cycle=1)
    assert report["win_rate_pct"] == pytest.approx(50.0)


def test_review_skips_rows_without_a_usable_ratio():
    report = review([dict(open_row("BTC"), decision="REJECTED", entry_ratio="")],
                    at_ratio({"BTC": 2.0}), cycle=1)
    assert report["refused_return_pct"] == {}


def test_refused_returns_include_both_cost_legs():
    report = review([dict(open_row("BTC"), decision="REJECTED", entry_ratio="2.0")],
                    at_ratio({"BTC": 2.0}), cycle=1)
    # flat ratio: exactly the round-trip cost, not zero
    assert report["refused_return_pct"]["BTC"] == pytest.approx(-0.3996, abs=1e-6)


# --- rules --------------------------------------------------------------------


def test_rule_from_cost_names_the_missing_input():
    rule, evidence = rule_from({"gate_cost": ["USDT"], "refused_return_pct": {"USDT": 0.34}})
    assert "missing input" in rule.lower()
    assert "USDT" in rule and "+0.34%" in evidence


def test_rule_from_all_correct_refusals_keeps_the_threshold():
    rule, evidence = rule_from({"gate_cost": [],
                                "refused_return_pct": {"BTC": -0.34, "ETH": -0.44}})
    assert "1.5x" in rule
    assert "BTC" in evidence


def test_rule_from_untested_gate_changes_nothing():
    rule, evidence = rule_from({"gate_cost": [], "refused_return_pct": {}})
    assert "No rule change" in rule
    assert evidence == "no refusals"


def test_pattern_requires_measured_relative_strength():
    s = at_ratio({"BTC": 2.0}, changes={"XRP": {"24h": 1.03}, "BTC": {"24h": -1.58}})
    text = patterns({"unrealised_xrp": 0.088}, s)
    assert text.startswith("When XRP outperformed BTC")
    assert "+2.61%" in text or "+2.62%" in text


def test_pattern_refuses_to_invent_when_data_is_missing():
    assert patterns({}, at_ratio({"BTC": 2.0})) == "Insufficient data to state a pattern."


# --- confidence ---------------------------------------------------------------


def test_weights_sum_to_one_hundred():
    assert sum(WEIGHTS.values()) == 100


def test_provenance_only_scores_twenty():
    score = confidence_score(0, "RECORDED_FEED", 0.0, 0.0, 0.0, 0)
    assert score["score"] == 20.0
    assert score["parts"]["provenance_recorded"] == 20


def test_unknown_provenance_scores_zero():
    assert confidence_score(0, "GUESSED", 0.0, 0.0, 0.0, 0)["score"] == 0.0


def test_full_house_scores_one_hundred():
    score = confidence_score(200, "RECORDED_FEED", 5.0, 2.0, 0.5, 0)
    assert score["score"] == 100.0


def test_expectancy_and_violations_cannot_score_without_closed_trades():
    score = confidence_score(0, "RECORDED_FEED", 5.0, 0.0, 0.9, 0)
    assert score["parts"]["expectancy_positive"] == 0
    assert score["parts"]["no_violations"] == 0


def test_drawdown_above_ten_percent_loses_its_points():
    score = confidence_score(50, "RECORDED_FEED", 1.0, 12.0, 0.5, 0)
    assert score["parts"]["drawdown_ok"] == 0


# --- ledger -------------------------------------------------------------------


def test_ledger_round_trip(tmp_path):
    rows = [open_row(), dict(open_row("ETH"), decision="REJECTED", xrp_in="")]
    path = write_ledger(rows, tmp_path / "L.csv")
    back = read_ledger(path)
    assert len(back) == 2
    assert back[0]["trade_id"] == "T-BTC"
    assert back[1]["decision"] == "REJECTED"
    assert back[1]["xrp_in"] == ""


def test_ledger_writes_every_field_even_when_missing(tmp_path):
    path = write_ledger([{"trade_id": "only-one"}], tmp_path / "L.csv")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        row = next(reader)
        assert set(row) == set(reader.fieldnames)
        assert row["asset"] == ""


def test_missing_ledger_reads_as_empty(tmp_path):
    assert read_ledger(tmp_path / "nope.csv") == []


def test_next_cycle_counts_from_the_highest():
    assert next_cycle([]) == 1
    assert next_cycle([{"cycle": "0"}, {"cycle": "4"}]) == 5
    assert next_cycle([{"cycle": ""}, {"cycle": "x"}]) == 1


def test_import_batch1_brings_refusals_forward():
    rows = import_batch1(BATCH1, [])
    decisions = {r["decision"] for r in rows}
    assert {"ACCEPTED", "REJECTED", "NO_TRADE"} <= decisions
    accepted = [r for r in rows if r["decision"] == "ACCEPTED"]
    assert accepted and all(float(r["xrp_in"]) > 0 for r in accepted)
    rejected = [r for r in rows if r["decision"] == "REJECTED"]
    assert rejected and all(r["xrp_in"] == "" for r in rejected)
    assert all(r["exit_status"] == "OPEN" for r in accepted)


def test_import_batch1_is_idempotent():
    once = import_batch1(BATCH1, [])
    twice = import_batch1(BATCH1, once)
    assert len(twice) == len(once)


def test_import_batch1_marks_refusals_as_not_open():
    rows = import_batch1(BATCH1, [])
    for row in rows:
        if row["decision"] != "ACCEPTED":
            assert row["exit_status"] == "NONE"


def test_imported_entry_price_comes_from_the_caller():
    rows = import_batch1(BATCH1, [], xrp_usd_entry=0.5)
    assert all(r["xrp_usd_entry"] == "0.50000000" for r in rows)


# --- timing invariant, end to end ---------------------------------------------


def test_two_snapshot_loop_grades_at_the_next_snapshot_not_its_own():
    """Use a real snapshot, because the gate needs real signals to approve."""
    first = MarketSnapshot.from_json(LIVE)
    rows, _ = open_positions(first, 1, 102.27, 76.0, StrategyConfig())
    accepted = [r for r in rows if r["decision"] == "ACCEPTED"]
    assert accepted, "the defensive leg should have been accepted on live data"

    # Mark at the entry snapshot. Every position pays the round-trip cost, and
    # nothing is allowed to close on a price that has not moved.
    at_entry = [mark_row(r, first) for r in accepted]
    assert all(r["exit_status"] == "OPEN" for r in at_entry)
    assert all(float(r["mark_return_pct"]) < 0 for r in at_entry)

    # A later snapshot: USDT loses 6% against XRP, past the 5% stop, so a closed
    # result becomes possible and only then.
    later = replace(
        first,
        snapshot_id="S2",
        prices_usd={**first.prices_usd,
                    "USDT": first.prices_usd["USDT"] * 0.94},
    )
    graded = [mark_row(r, later) for r in at_entry]
    assert any(r["exit_status"] == "CLOSED" for r in graded)

    report = review(graded, later, cycle=1)
    assert report["closed"] >= 1
    assert report["snapshot_read_at"] == "S2"
