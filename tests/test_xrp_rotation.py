"""Tests for the XRP-centric paper rotation engine.

Locks the safety and accounting properties: XRP-denominated PnL, cost on both
legs, 1% risk including cost, fail-closed alignment, evidence-gated lessons, and
a confidence gate that simulated data can never pass.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from barrot_agent.trading.xrp_rotation import (
    MAX_TRADES_PER_DAY,
    ROUND_TRIP_COST_PCT,
    STARTING_XRP,
    RotationOutcome,
    RotationPlan,
    StrategyConfig,
    apply_lesson,
    auto_lesson,
    confidence,
    evaluate,
    max_drawdown_pct,
    read_csv,
    settle,
    to_row,
    write_csv,
)

MODULE = Path(__file__).resolve().parents[1] / "barrot_agent/trading/xrp_rotation.py"
FORBIDDEN_IMPORTS = {
    "socket",
    "ssl",
    "http",
    "urllib",
    "requests",
    "aiohttp",
    "httpx",
    "websocket",
    "websockets",
    "ccxt",
    "web3",
}


def plan(**overrides) -> RotationPlan:
    base = dict(
        rotation_id="R-001",
        timestamp_utc="2026-11-18T00:00:00Z",
        asset="BTC",
        xrp_per_asset=0.00002,
        expected_move_pct=3.0,
        stop_pct=5.0,
        trend="UP",
        ratio_signal="FAVOURS",
        volume_signal="CONFIRMS",
        news="CLEAR",
        xrp_dominance=55.0,
        bars_held=0,
        provenance="SIMULATED_SCENARIO",
    )
    base.update(overrides)
    return RotationPlan(**base)


def mk_outcome(asset="XLM", delta=-10.0, r=-0.1, violations=0, tag="") -> RotationOutcome:
    return RotationOutcome(
        plan=plan(asset=asset, rotation_id=f"{asset}-{delta}"),
        exit_ratio=1.0,
        xrp_out=1_000.0 + delta,
        xrp_delta=delta,
        xrp_delta_pct=delta / 1_000.0 * 100.0,
        usd_in=1_000.0,
        usd_out=1_000.0 + delta,
        usd_delta=delta,
        r_multiple=r,
        outcome="WIN" if delta > 0 else ("LOSS" if delta < 0 else "FLAT"),
        exit_reason="TARGET",
        mistake_tag=tag,
        rule_violations=violations,
    )


def test_starting_stack_and_cost_are_fixed():
    assert STARTING_XRP == 10_000.0
    assert ROUND_TRIP_COST_PCT == pytest.approx(0.4)


def test_valid_rotation_sizes_to_one_percent_including_cost():
    verdict = evaluate(plan())
    assert verdict.approved, verdict.reasons
    worst_case = 5.0 + ROUND_TRIP_COST_PCT
    expected_alloc = STARTING_XRP * 0.01 / (worst_case / 100.0)
    assert verdict.xrp_allocated == pytest.approx(expected_alloc, rel=1e-6)
    assert verdict.xrp_at_risk == pytest.approx(100.0, rel=1e-6)
    assert verdict.risk_pct == pytest.approx(1.0, rel=1e-6)


def test_usdt_needs_a_defensive_trigger():
    verdict = evaluate(plan(asset="USDT", trend="UP", ratio_signal="FAVOURS"))
    assert not verdict.approved
    assert any("defensive" in reason for reason in verdict.reasons)


def test_usdt_allowed_on_high_impact_news():
    verdict = evaluate(plan(asset="USDT", news="HIGH_IMPACT"))
    assert verdict.approved, verdict.reasons


def test_offensive_rotation_blocked_on_high_impact_news():
    verdict = evaluate(plan(news="HIGH_IMPACT"))
    assert not verdict.approved
    assert any("high-impact" in reason for reason in verdict.reasons)


def test_unknown_news_blocks_offensive_rotation():
    verdict = evaluate(plan(news="UNKNOWN"))
    assert not verdict.approved
    assert any("news state unknown" in reason for reason in verdict.reasons)


@pytest.mark.parametrize(
    "overrides, expected",
    [
        ({"trend": "FLAT"}, "trend"),
        ({"ratio_signal": "AGAINST"}, "ratio signal"),
        ({"volume_signal": "THIN"}, "volume signal"),
        ({"xrp_dominance": None}, "dominance"),
        ({"xrp_dominance": 140.0}, "dominance"),
    ],
)
def test_alignment_and_scan_is_fail_closed(overrides, expected):
    verdict = evaluate(plan(**overrides))
    assert not verdict.approved
    assert any(expected in reason for reason in verdict.reasons)


def test_xrp_is_not_a_rotation_target():
    verdict = evaluate(plan(asset="XRP"))
    assert not verdict.approved
    assert any("base asset" in reason for reason in verdict.reasons)


def test_unknown_asset_is_rejected():
    verdict = evaluate(plan(asset="DOGE"))
    assert not verdict.approved


def test_disabled_asset_is_rejected():
    verdict = evaluate(plan(), config=StrategyConfig(disabled_assets=("BTC",)))
    assert not verdict.approved
    assert any("disabled" in reason for reason in verdict.reasons)


def test_time_stop_blocks_stale_position():
    verdict = evaluate(plan(bars_held=11))
    assert not verdict.approved
    assert any("time stop" in reason for reason in verdict.reasons)


def test_daily_rotation_cap():
    verdict = evaluate(plan(), trades_today=MAX_TRADES_PER_DAY)
    assert not verdict.approved
    assert any("cap" in reason for reason in verdict.reasons)


def test_move_below_cost_is_rejected():
    verdict = evaluate(plan(expected_move_pct=0.3))
    assert not verdict.approved
    assert any("net edge" in reason for reason in verdict.reasons)


def test_move_must_clear_cost_multiple():
    verdict = evaluate(plan(expected_move_pct=0.5))
    assert not verdict.approved
    assert any("below" in reason for reason in verdict.reasons)


def test_settlement_grows_xrp_when_ratio_falls():
    verdict = evaluate(plan())
    exit_ratio = plan().xrp_per_asset * 0.97
    out = settle(verdict, exit_ratio, xrp_usd_entry=0.52, xrp_usd_exit=0.52)
    assert out.xrp_out > verdict.xrp_allocated
    assert out.xrp_delta > 0
    assert out.outcome == "WIN"
    assert out.r_multiple > 0


def test_settlement_loses_xrp_when_ratio_rises():
    verdict = evaluate(plan())
    exit_ratio = plan().xrp_per_asset * 1.03
    out = settle(verdict, exit_ratio, xrp_usd_entry=0.52, xrp_usd_exit=0.52)
    assert out.xrp_delta < 0
    assert out.outcome == "LOSS"
    assert out.r_multiple < 0


def test_xrp_and_usd_can_disagree_on_a_defensive_rotation():
    verdict = evaluate(plan(asset="USDT", news="HIGH_IMPACT"))
    assert verdict.approved, verdict.reasons
    out = settle(verdict, exit_ratio=plan().xrp_per_asset * 0.95, xrp_usd_entry=0.52,
                 xrp_usd_exit=0.494)
    assert out.xrp_delta > 0
    assert out.usd_delta < 0


def test_lesson_refuses_to_change_on_thin_evidence():
    outcomes = [mk_outcome(asset="XLM", delta=-5.0) for _ in range(3)]
    lesson = auto_lesson(outcomes)
    assert lesson["proposal"]["change"] == "NONE"
    assert "INSUFFICIENT_EVIDENCE" in lesson["proposal"]["why"]


def test_lesson_disables_worst_asset_with_enough_evidence():
    outcomes = [mk_outcome(asset="XLM", delta=-5.0) for _ in range(4)]
    outcomes += [mk_outcome(asset="BTC", delta=20.0)]
    lesson = auto_lesson(outcomes)
    assert lesson["proposal"]["change"] == "disable_asset"
    assert lesson["proposal"]["asset"] == "XLM"


def test_lesson_never_disables_the_defensive_asset():
    outcomes = [mk_outcome(asset="USDT", delta=-5.0) for _ in range(5)]
    lesson = auto_lesson(outcomes)
    assert lesson["proposal"]["change"] == "NONE"


def test_apply_lesson_is_one_way_and_idempotent():
    outcomes = [mk_outcome(asset="XLM", delta=-5.0) for _ in range(4)]
    lesson = auto_lesson(outcomes)
    config, applied = apply_lesson(StrategyConfig(), lesson)
    assert applied and "XLM" in config.disabled_assets
    again, applied_again = apply_lesson(config, lesson)
    assert not applied_again
    assert again == config


def test_drawdown_maths():
    assert max_drawdown_pct([10_000, 10_500, 9_450]) == pytest.approx(10.0)


def test_confidence_refuses_simulated_provenance():
    outcomes = [mk_outcome(asset="BTC", delta=5.0, r=0.5) for _ in range(120)]
    report = confidence(outcomes, provenance="SIMULATED_SCENARIO")
    assert not report["ready"]
    assert report["checks"][0][1] is False


def test_confidence_refuses_empty_record():
    report = confidence([], provenance="RECORDED_FEED")
    assert not report["ready"]
    assert all(check[1] is False for check in report["checks"] if "provenance" not in check[0])


def test_confidence_flags_rule_violations():
    outcomes = [mk_outcome(asset="BTC", delta=5.0, r=0.5) for _ in range(120)]
    outcomes[0] = mk_outcome(asset="BTC", delta=5.0, r=0.5, violations=1)
    report = confidence(outcomes, provenance="RECORDED_FEED")
    assert not report["ready"]
    assert any(name.startswith("zero rule") and not ok for name, ok, _ in report["checks"])


def test_csv_round_trip(tmp_path):
    verdict = evaluate(plan())
    out = settle(verdict, plan().xrp_per_asset * 0.97, 0.52, 0.52)
    path = write_csv([to_row(out)], tmp_path / "rotations.csv")
    back = read_csv(path)
    assert len(back) == 1
    assert back[0]["asset"] == "BTC"
    assert float(back[0]["xrp_in"]) == pytest.approx(verdict.xrp_allocated, rel=1e-6)
    assert back[0]["provenance"] == "SIMULATED_SCENARIO"


def test_empty_ledger_is_refused(tmp_path):
    with pytest.raises(ValueError):
        write_csv([], tmp_path / "empty.csv")


def test_module_has_no_network_imports():
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported.isdisjoint(FORBIDDEN_IMPORTS), imported & FORBIDDEN_IMPORTS
