"""Tests for Batch 1 entry evaluation on Sean's 2026-11-18 snapshot.

These lock three things:
  * the ratios and signals are derived from the supplied numbers, not asserted
  * one snapshot produces entries and PENDING exits, never fabricated outcomes
  * a lesson learned on a simulated scenario cannot disable an asset on real data
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from barrot_agent.trading.xrp_batch import (
    Candidate,
    MarketSnapshot,
    batch_rows,
    build_plan,
    read_batch_csv,
    summarize,
    write_batch_csv,
)
from barrot_agent.trading.xrp_rotation import (
    ROUND_TRIP_COST_PCT,
    StrategyConfig,
    evaluate,
    load_config,
)

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "market/2026-11-18-sean-feed.json"
MODULE = ROOT / "barrot_agent/trading/xrp_batch.py"
FORBIDDEN_IMPORTS = {
    "socket", "ssl", "http", "urllib", "requests", "aiohttp", "httpx",
    "websocket", "websockets", "ccxt", "web3",
}


@pytest.fixture(scope="module")
def snap() -> MarketSnapshot:
    return MarketSnapshot.from_json(SNAPSHOT)


def cand(asset: str, expected: float = 3.0, **kw) -> Candidate:
    return Candidate(
        candidate_id=kw.pop("candidate_id", f"T-{asset}"),
        asset=asset,
        thesis="test",
        expected_move_pct=expected,
        **kw,
    )


# --- snapshot ingestion -------------------------------------------------------


def test_snapshot_is_sean_supplied_and_unverified(snap):
    assert snap.provenance == "SEAN_SUPPLIED"
    payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert payload["verification"]["exchange_api_queried"] is False
    assert payload["verification"]["network_calls_made"] == 0


def test_starting_balance_is_102_27_xrp(snap):
    assert snap.balances_start["xrp"] == pytest.approx(102.27)
    assert snap.balances_start["usd_value"] == pytest.approx(100.0)


@pytest.mark.parametrize(
    "asset, expected",
    [
        ("BTC", 0.00001549),
        ("ETH", 0.0005533),
        ("SOL", 0.01327),
        ("XLM", 7.06),
    ],
)
def test_ratios_reproduce_sean_numbers(snap, asset, expected):
    # Sean's figures are rounded to 4 significant digits, so allow 0.1%.
    assert snap.ratio(asset) == pytest.approx(expected, rel=1e-3)


def test_usdt_ratio_uses_the_supplied_price_not_one_dollar(snap):
    computed = snap.ratio("USDT")
    assert computed == pytest.approx(0.9778 / 0.9989, rel=1e-9)
    assert computed != pytest.approx(0.9778, rel=1e-9)
    # The difference is a quarter of the round-trip cost, so it matters.
    gap = abs(computed - 0.9778) / 0.9778 * 100.0
    assert gap > ROUND_TRIP_COST_PCT / 4


def test_xrp_dominance_is_derived_not_assumed(snap):
    assert snap.xrp_dominance_pct() == pytest.approx(2.885, rel=1e-3)


def test_snapshot_refuses_unknown_provenance(tmp_path):
    payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    payload["provenance"] = "MADE_UP"
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError):
        MarketSnapshot.from_json(path)


def test_snapshot_refuses_missing_price(tmp_path):
    payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    del payload["prices_usd"]["SOL"]
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError):
        MarketSnapshot.from_json(path)


# --- derived signals ----------------------------------------------------------


@pytest.mark.parametrize(
    "asset, trend, ratio_signal",
    [
        ("BTC", "DOWN", "AGAINST"),
        ("ETH", "DOWN", "AGAINST"),
        ("SOL", "MIXED", "AGAINST"),
        ("XLM", "MIXED", "FAVOURS"),
    ],
)
def test_trend_and_ratio_signals_follow_the_numbers(snap, asset, trend, ratio_signal):
    assert snap.trend(asset) == trend
    assert snap.ratio_signal(asset) == ratio_signal


def test_volume_is_unknown_without_supplied_volume(snap):
    assert snap.volume_signal("BTC") == "UNKNOWN"
    assert snap.volume_signal("XLM") == "UNKNOWN"


@pytest.mark.parametrize(
    "asset, ratio_change, counterfactual",
    [
        ("BTC", 9.4118, -8.6022),
        ("ETH", 9.4118, -8.6022),
        ("SOL", 5.6818, -5.3763),
        ("XLM", -1.0638, 1.0752),
    ],
)
def test_ratio_change_and_seven_day_counterfactual(snap, asset, ratio_change, counterfactual):
    assert snap.ratio_change_pct(asset, "7d") == pytest.approx(ratio_change, abs=1e-3)
    assert snap.counterfactual_pct(asset, "7d") == pytest.approx(counterfactual, abs=1e-3)


def test_counterfactual_of_a_strengthening_xrp_is_a_loss(snap):
    """XRP outperformed, so rotating out of it lost XRP. This is the point."""
    assert snap.counterfactual_pct("BTC", "7d") < 0
    assert snap.counterfactual_pct("XLM", "7d") > 0


def test_usdt_counterfactual_needs_a_window_it_does_not_have(snap):
    assert snap.counterfactual_pct("USDT", "7d") is None


# --- the gate on this snapshot ------------------------------------------------


def test_offensive_rotation_is_rejected_in_a_downtrend(snap):
    for asset in ("BTC", "ETH", "SOL"):
        verdict = evaluate(build_plan(snap, cand(asset)), stack_xrp=102.27)
        assert not verdict.approved
        assert any("trend" in reason for reason in verdict.reasons)


def test_xlm_is_rejected_on_volume_not_on_ratio(snap):
    verdict = evaluate(build_plan(snap, cand("XLM")), stack_xrp=102.27)
    assert not verdict.approved
    assert any("volume" in reason for reason in verdict.reasons)


def test_defensive_rotation_is_approved(snap):
    verdict = evaluate(build_plan(snap, cand("USDT")), stack_xrp=102.27)
    assert verdict.approved, verdict.reasons
    assert verdict.risk_pct <= 1.0


def test_unknown_news_blocks_even_the_defensive_leg(snap):
    verdict = evaluate(
        build_plan(snap, cand("USDT", news="UNKNOWN")), stack_xrp=102.27
    )
    assert not verdict.approved
    assert any("news state unknown" in reason for reason in verdict.reasons)


# --- the batch ledger ---------------------------------------------------------


def test_batch1_writes_ten_decisions(snap):
    rows, _ = batch_rows(snap, [cand(a) for a in ("USDT", "USDT", "BTC")], 102.27)
    assert len(rows) == 3
    assert [row["decision"] for row in rows] == ["ACCEPTED", "ACCEPTED", "REJECTED"]


def test_batch1_never_records_a_realised_outcome(snap):
    rows, _ = batch_rows(snap, [cand("USDT")], 102.27)
    row = rows[0]
    assert row["exit_status"] == "PENDING"
    for field in (
        "exit_ratio", "xrp_out", "xrp_delta",
        "usd_in", "usd_out", "usd_delta", "r_multiple",
    ):
        assert row[field] == ""


def test_hold_is_no_trade_not_a_rejection(snap):
    rows, _ = batch_rows(snap, [cand("XRP", 0.0)], 102.27)
    assert rows[0]["decision"] == "NO_TRADE"
    assert "base asset held" in rows[0]["reasons"]


def test_summary_reports_undefined_metrics_not_zero(snap):
    rows, _ = batch_rows(snap, [cand("USDT"), cand("BTC")], 102.27)
    summary = summarize(rows, 102.27)
    assert summary["accepted"] == 1
    assert summary["rejected"] == 1
    assert summary["exits_pending"] == 1
    assert summary["realised_xrp_delta"] == 0.0
    assert summary["realised_r"] is None
    assert summary["win_rate"] is None


def test_batch_never_allocates_more_than_the_stack(snap):
    rows, _ = batch_rows(snap, [cand("USDT") for _ in range(12)], 102.27)
    allocated = sum(float(row["xrp_allocated"]) for row in rows if row["xrp_allocated"])
    assert allocated <= 102.27 + 1e-9


def test_capacity_guard_caps_allocation():
    """With a tight stop the risk budget allows more than is available."""
    plan = build_plan(
        MarketSnapshot.from_json(SNAPSHOT),
        Candidate("T", "USDT", "t", 3.0, stop_pct=0.5),
    )
    full = evaluate(plan, stack_xrp=102.27)
    capped = evaluate(plan, stack_xrp=102.27, available_xrp=5.0)
    assert full.xrp_allocated > 5.0
    assert capped.approved
    assert capped.xrp_allocated == pytest.approx(5.0)
    assert capped.xrp_at_risk <= 5.0


def test_risk_is_a_share_of_available_capital_not_the_raw_stack():
    """Sizing uses whatever is uncommitted, so later tranches risk less."""
    plan = build_plan(
        MarketSnapshot.from_json(SNAPSHOT),
        Candidate("T", "USDT", "t", 3.0, stop_pct=5.0),
    )
    first = evaluate(plan, stack_xrp=102.27, available_xrp=102.27)
    second = evaluate(plan, stack_xrp=102.27, available_xrp=51.135)
    assert second.xrp_allocated == pytest.approx(first.xrp_allocated / 2, rel=1e-6)
    assert second.xrp_at_risk < first.xrp_at_risk


def test_zero_capacity_is_rejected():
    plan = build_plan(
        MarketSnapshot.from_json(SNAPSHOT),
        Candidate("T", "USDT", "t", 3.0),
    )
    verdict = evaluate(plan, stack_xrp=102.27, available_xrp=0.0)
    assert not verdict.approved
    assert any("no capital" in reason for reason in verdict.reasons)


def test_ledger_round_trip(tmp_path, snap):
    rows, _ = batch_rows(snap, [cand("USDT")], 102.27)
    path = write_batch_csv(rows, tmp_path / "batch.csv")
    back = read_batch_csv(path)
    assert back[0]["asset"] == "USDT"
    assert back[0]["exit_status"] == "PENDING"
    assert back[0]["provenance"] == "SEAN_SUPPLIED"


def test_empty_ledger_is_refused(tmp_path):
    with pytest.raises(ValueError):
        write_batch_csv([], tmp_path / "empty.csv")


# --- lessons must not cross provenance ---------------------------------------


def test_simulated_lesson_cannot_disable_an_asset_on_real_data(tmp_path):
    path = tmp_path / "lessons.jsonl"
    path.write_text(
        json.dumps(
            {
                "provenance": "SIMULATED_SCENARIO",
                "proposal": {"change": "disable_asset", "asset": "XLM", "why": "fixture"},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    config, applied = load_config(path, "SEAN_SUPPLIED")
    assert applied == []
    assert config.disabled_assets == ()


def test_same_provenance_lesson_does_apply(tmp_path):
    path = tmp_path / "lessons.jsonl"
    path.write_text(
        json.dumps(
            {
                "provenance": "SEAN_SUPPLIED",
                "proposal": {"change": "disable_asset", "asset": "XLM", "why": "recorded"},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    config, applied = load_config(path, "SEAN_SUPPLIED")
    assert config.disabled_assets == ("XLM",)
    assert len(applied) == 1


def test_missing_lesson_file_is_not_an_error(tmp_path):
    config, applied = load_config(tmp_path / "absent.jsonl", "SEAN_SUPPLIED")
    assert applied == []
    assert config == StrategyConfig()


def test_module_has_no_network_imports():
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported.isdisjoint(FORBIDDEN_IMPORTS), imported & FORBIDDEN_IMPORTS
