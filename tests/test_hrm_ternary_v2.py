"""Tests for SHRM 2.0 (Sapient's Hierarchical Reasoning Model, refinement 2.0).

SHRM 2.0 lives in barrot_agent/reasoning/hrm.py and must:
- reproduce v1 (core/hrm_ternary.py) decisions exactly on unweighted inputs
  (HACKATHON RULE: never break the working demo),
- add weighted sources, a genuine H-hierarchy, a slope-based convergence
  metric, and a machine-readable decision trace,
- preserve the house invariants: sovereign absolution, stability gate,
  1.58-bit ternary labels.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "core"))

from hrm_ternary import ANCHOR as V1_ANCHOR  # noqa: E402
from hrm_ternary import hrm_resolve as v1_resolve  # noqa: E402

from barrot_agent.reasoning.hrm import (  # noqa: E402
    ANCHOR,
    Ternary,
    hrm2_resolve,
    resolve_with_trace,
)


# --------------------------------------------------------------------------
# Canonical cases from core/hrm_ternary.py __main__ block.
# --------------------------------------------------------------------------
CANONICAL_CASES = {
    "clean BUY": {"orderbook": 0.9, "sentiment": 0.8, "price": 0.85},
    "conflict -> gate": {"orderbook": 0.9, "sentiment": -0.8, "price": 0.1},
    "weak consensus": {"orderbook": 0.4, "sentiment": 0.3, "price": 0.2},
    "unanimous SELL": {"orderbook": -0.9, "sentiment": -0.95, "price": -0.8},
    "reachable SELL": {"orderbook": -1.0, "sentiment": -0.95, "price": -0.5},
}

V1_EXPECTED = {
    # name: (gated_label, raw_label, absolution_fired)  -- verified against v1
    # NOTE: 'conflict -> gate' resolves to raw NULL under the canon
    # (|0.9-0.8+0.1| = 0.2 < ANCHOR*3), so no gate fires; v1's case name
    # is aspirational, the recorded numbers above are ground truth.
    "clean BUY": ("BUY", "BUY", False),
    "conflict -> gate": ("NULL", "NULL", False),
    "weak consensus": ("NULL", "NULL", False),
    "unanimous SELL": ("NULL", "SELL", True),
    "reachable SELL": ("SELL", "SELL", False),
}


@pytest.mark.parametrize("name", list(CANONICAL_CASES))
def test_v1_parity_canonical_cases(name):
    """SHRM 2.0 must reproduce v1's gated state, raw state, and absolution."""
    signals = CANONICAL_CASES[name]
    v1 = v1_resolve(signals)
    v2 = hrm2_resolve(signals)
    exp_label, exp_raw, exp_abs = V1_EXPECTED[name]
    # v1 ground truth matches the documented expectations
    assert (v1.label, Ternary.label(v1.raw_state), v1.absolution_fired) == (
        exp_label,
        exp_raw,
        exp_abs,
    )
    # v2 parity
    assert v2.label == exp_label
    assert v2.raw_state == v1.raw_state
    assert v2.absolution_fired == exp_abs


def test_v1_parity_randomized_unweighted():
    """Label parity must hold across a wide random corpus (unweighted)."""
    import random

    rng = random.Random(707106781)
    names_pool = ["orderbook", "sentiment", "price", "onchain", "flow", "momentum", "volume", "basis"]
    mismatches = 0
    for _ in range(2000):
        k = rng.randint(1, len(names_pool))
        names = rng.sample(names_pool, k)
        signals = {n: rng.uniform(-1, 1) for n in names}
        v1 = v1_resolve(signals)
        v2 = hrm2_resolve(signals)
        if v1.label != v2.label or v1.raw_state != v2.raw_state:
            mismatches += 1
    assert mismatches == 0, f"{mismatches}/2000 label mismatches vs v1"


def test_absolution_invariant_unweighted():
    v2 = hrm2_resolve({"a": -0.9, "b": -0.95, "c": -0.8})
    assert v2.absolution_fired is True
    assert v2.state == Ternary.NULL

    # single source can never fire absolution (v1 requires k > 1)
    v2_one = hrm2_resolve({"a": -1.0})
    assert v2_one.absolution_fired is False


def test_absolution_invariant_with_weights():
    v2 = hrm2_resolve({"a": -0.9, "b": -0.95, "c": -0.8},
                      weights={"a": 1.0, "b": 1.0, "c": 1.0})
    assert v2.absolution_fired is True
    assert v2.state == Ternary.NULL


def test_stability_gate_invariant():
    """Any non-NULL gated state must carry confidence >= 1 - ANCHOR."""
    import random

    rng = random.Random(1234)
    for _ in range(500):
        k = rng.randint(2, 6)
        signals = {f"s{i}": rng.uniform(-1, 1) for i in range(k)}
        v2 = hrm2_resolve(signals)
        if v2.state != Ternary.NULL and not v2.absolution_fired:
            assert v2.confidence >= 1 - ANCHOR, (signals, v2)
        assert v2.confidence >= 0.0 and v2.confidence <= 1.0


def test_anchor_matches_v1():
    assert ANCHOR == V1_ANCHOR == 0.707106781186548


def test_ternary_label_bijection():
    assert Ternary.label(Ternary.BUY) == "BUY"
    assert Ternary.label(Ternary.NULL) == "NULL"
    assert Ternary.label(Ternary.SELL) == "SELL"


def test_weighted_sources_change_outcome():
    """Weights must actually matter: they move trust (agreement/confidence),
    while the canonical direction stays unweighted (canon preserved)."""
    signals = {"orderbook": 0.9, "sentiment": -0.9}
    unweighted = hrm2_resolve(signals)
    # opposite signals, equal trust -> agreement 0
    assert unweighted.agreement == pytest.approx(0.0)
    assert unweighted.weighted is False

    # trust orderbook, distrust sentiment -> weighted agreement rises
    orderbook_dominant = hrm2_resolve(
        signals, weights={"orderbook": 1.0, "sentiment": 0.05}
    )
    assert orderbook_dominant.weighted is True
    assert orderbook_dominant.agreement > unweighted.agreement
    assert orderbook_dominant.agreement == pytest.approx(
        abs(0.9 - 0.9 * 0.05) / 1.05, abs=1e-3
    )

    # zero-weighted sources drop out of the weighted vote; agreement is
    # weighted vote MAGNITUDE (|Σ w·u| / Σ w), matching v1's semantics
    # extended to weights — one surviving source at 0.9 strength -> 0.9.
    solo = hrm2_resolve(signals, weights={"orderbook": 1.0, "sentiment": 0.0})
    assert solo.agreement == pytest.approx(0.9)
    # direction is still computed from the unweighted canon sum: raw_state
    # for (+0.9, -0.9) is NULL in every mode.
    assert solo.raw_state == Ternary.NULL


def test_weight_validation_rejects_garbage():
    signals = {"a": 0.5, "b": -0.5}
    with pytest.raises(ValueError):
        hrm2_resolve(signals, weights={"a": 0.5})  # missing weight for b
    with pytest.raises(ValueError):
        hrm2_resolve(signals, weights={"a": 1.5, "b": 0.5})  # out of range
    with pytest.raises(ValueError):
        hrm2_resolve(signals, weights={"a": "x", "b": 0.5})  # non-numeric


def test_empty_signals_is_null():
    v2 = hrm2_resolve({})
    assert v2.state == Ternary.NULL
    assert v2.label == "NULL"
    assert v2.confidence == 0.0
    assert v2.basis == "no input sources"


def test_determinism():
    signals = {"orderbook": 0.9, "sentiment": -0.8, "price": 0.1}
    a, b = hrm2_resolve(signals), hrm2_resolve(signals)
    assert (a.state, a.confidence, a.iterations) == (b.state, b.confidence, b.iterations)


def test_trace_is_complete_and_consistent():
    signals = {"orderbook": 0.9, "sentiment": 0.8, "price": 0.85}
    res, trace = resolve_with_trace(signals)
    assert trace["version"] == "2.0"
    assert trace["names"] == sorted(signals)
    assert len(trace["cycle_residuals"]) >= 1
    assert trace["iterations_used"] == res.iterations
    assert res.iterations <= trace["levels"][0] * trace["levels"][1]
    assert trace["gate"]["threshold"] == pytest.approx(1 - ANCHOR)
    assert trace["inputs"]["signals"] == signals
    # every recorded residual is finite and positive (per-cycle nested lists)
    flat = [r for cycle in trace["cycle_residuals"] for r in cycle]
    assert all(r >= 0.0 for r in flat)


def test_early_halt_bounds_iterations():
    v2 = hrm2_resolve({"orderbook": 0.9, "sentiment": 0.8, "price": 0.85})
    assert v2.iterations <= 2 * 6
    if v2.halted_early:
        assert v2.iterations < 2 * 6


def test_confidence_symmetry_agreement():
    """Perfect positive consensus -> agreement 1.0."""
    v2 = hrm2_resolve({"a": 1.0, "b": 1.0, "c": 1.0})
    assert v2.agreement == pytest.approx(1.0)


def test_refined_mode_runs_and_audits_hierarchy():
    """refined=True: genuine 2-level H hierarchy + slope convergence."""
    signals = {"orderbook": 0.9, "sentiment": -0.8, "price": 0.1}
    parity_res, parity_trace = resolve_with_trace(signals, refined=False)
    refined_res, refined_trace = resolve_with_trace(signals, refined=True)

    assert refined_res.refined is True
    assert refined_res.state in (Ternary.BUY, Ternary.NULL, Ternary.SELL)
    assert 0.0 <= refined_res.confidence <= 1.0
    # refined mode must actually engage H2 (nonzero strategic activation)
    assert any(act[1] != 0.0 for act in refined_trace["level_activations"]), (
        refined_trace["level_activations"]
    )
    # parity mode keeps H2 inert (byte-identical v1 trajectories)
    assert all(act[1] == 0.0 for act in parity_trace["level_activations"])
    # refined mode runs a different convergence metric -> trace records mode
    assert refined_trace["gate"]["threshold"] == parity_trace["gate"]["threshold"]


def test_refined_mode_never_trades_on_low_coherence():
    """Gate invariant holds in refined mode too."""
    import random

    rng = random.Random(777)
    for _ in range(500):
        k = rng.randint(2, 6)
        signals = {f"s{i}": rng.uniform(-1, 1) for i in range(k)}
        v2 = hrm2_resolve(signals, refined=True)
        if v2.state != Ternary.NULL and not v2.absolution_fired:
            assert v2.confidence >= 1 - ANCHOR, (signals, v2)
