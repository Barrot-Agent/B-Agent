"""SHRM 2.0 — Sapient's Hierarchical Reasoning Model, refined for Barrot.

Refinement (v2.0) of core/hrm_ternary.py (v1.0), which adapted Sapient's
Hierarchical Reasoning Model (HRM / HRM-Text, arXiv:2506.21734) into the
Barrot ternary pipeline. Like v1, this is NOT a neural network and carries
no trained weights: it adapts HRM's *dynamics* — a slow hierarchical
H-state guiding a fast L-state through nested convergence cycles.

Two execution modes, chosen explicitly:

- PARITY MODE (default, ``refined=False``): dynamics are byte-for-byte
  equivalent to v1 — same matrices, same drive, same single-H update, same
  endpoint convergence, same gate. Published signals stay comparable.
  v2.0 still adds: weighted sources (agreement only), the full decision
  trace, and H2 recorded as inert for auditability.
- REFINED MODE (``refined=True``): the full SHRM 2.0 dynamics — a genuine
  two-level H hierarchy (H1 tactical updates every cycle, H2 strategic
  every second cycle and modulates the input gain), plus the slope-based
  convergence metric with oscillation penalty.

Unchanged from canon (deliberately, in both modes):
- Direction logic: anchor-thresholded unweighted sum (1.58-bit ternary
  {-1, 0, +1}).
- Sovereign Absolution: unanimous SELL -> NULL override.
- Stability gate: low-coherence calls never trade.
- Stability Anchor: 0.707106781186548 (1/sqrt(2)).

Cycle structure defaults mirror v1 / HRM-Text: N_L=6 low-level steps,
N_H=2 high-level cycles.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Tuple

import numpy as np

ANCHOR = 0.707106781186548
N_L, N_H, DIM = 6, 2, 8
_EPS = 1e-9

# Deterministic mixing matrices, seeded from the anchor digits — identical
# to v1 so trajectories (and therefore labels) match exactly.
_rng = np.random.default_rng(707106781)
_M_L = _rng.standard_normal((DIM, DIM)) * (ANCHOR / np.sqrt(DIM))
_M_H = _rng.standard_normal((DIM, DIM)) * (ANCHOR / np.sqrt(DIM))
_W_IN = _rng.standard_normal((DIM, 16)) * (ANCHOR / np.sqrt(DIM))

GATE_THRESHOLD = 1 - ANCHOR  # 0.2928932188134524


class Ternary:
    SELL, NULL, BUY = -1, 0, 1

    @staticmethod
    def resolve(*signals: float) -> int:
        s, n = sum(signals), max(len(signals), 1)
        if s > ANCHOR * n:
            return Ternary.BUY
        if s < -ANCHOR * n:
            return Ternary.SELL
        return Ternary.NULL

    @staticmethod
    def label(t: int) -> str:
        return {1: "BUY", 0: "NULL", -1: "SELL"}[t]


@dataclass
class HRM2Resolution:
    """Decision record. Superset of v1's HRMResolution (drop-in compatible)."""

    state: int  # ternary {-1, 0, +1} AFTER gating
    label: str
    raw_state: int  # pre-gate canonical resolution
    confidence: float  # [0,1] agreement x convergence
    agreement: float  # [0,1] (weighted) source unanimity
    convergence: float  # [0,1] how cleanly the H/L dynamics settled
    iterations: int  # L-steps actually used (max N_H*N_L)
    halted_early: bool
    absolution_fired: bool  # unanimous-SELL override -> NULL
    basis: str = ""
    weighted: bool = False  # True when caller supplied source weights
    refined: bool = False  # True when refined 2.0 dynamics were used


def _validate_weights(
    signals: Mapping[str, float], weights: Optional[Mapping[str, Any]]
) -> Dict[str, float]:
    if weights is None:
        return {}
    missing = set(signals) - set(weights)
    if missing:
        raise ValueError(f"missing weights for sources: {sorted(missing)}")
    out: Dict[str, float] = {}
    for name in signals:
        w = weights[name]
        if isinstance(w, bool) or not isinstance(w, (int, float)):
            raise ValueError(f"weight for {name!r} must be numeric, got {w!r}")
        if not 0.0 <= float(w) <= 1.0:
            raise ValueError(f"weight for {name!r} must be in [0,1], got {w}")
        out[name] = float(w)
    return out


def _endpoint_convergence(residuals, r0: float) -> float:
    """v1's metric, kept verbatim for parity mode."""
    rF = residuals[-1]
    return float(np.clip(1.0 - rF / max(r0, _EPS), 0.0, 1.0))


def _slope_convergence(residuals, r0: float) -> float:
    """Refined convergence: log-linear decay rate + oscillation penalty.

    v1's endpoint ratio is blind to oscillation and fragile when r0 is
    tiny. The slope of log(residual) over steps measures how fast the
    dynamics contract; residual increases (sign is always positive by
    construction, so an "increase" is a bounce) indicate oscillation and
    are penalized. Result is clipped to [0, 1].
    """
    if len(residuals) < 2:
        return 0.0
    floor = max(r0, _EPS) * 1e-6
    logs = [math.log(max(r, floor)) for r in residuals]
    n = len(logs)
    xs = range(n)
    mean_x = (n - 1) / 2
    mean_y = sum(logs) / n
    var_x = sum((x - mean_x) ** 2 for x in xs) / n
    if var_x <= 0:
        return 0.0
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, logs)) / (n * var_x)
    # Map per-step log-decay to [0,1]: v1's clean-settle threshold
    # ((1-ANCHOR)*0.1 relative) corresponds to slope ~ -0.0293 per step.
    decay = max(0.0, -slope)
    quality = min(1.0, decay / 0.0293)
    bounces = sum(1 for a, b in zip(residuals, residuals[1:]) if b > a)
    oscillation_penalty = min(0.5, 0.1 * bounces)
    return float(np.clip(quality - oscillation_penalty, 0.0, 1.0))


def _run_dynamics(
    drive: "np.ndarray",
    u_raw: "np.ndarray",
    refined: bool,
) -> Tuple[float, float, int, bool, list, list]:
    """Nested HRM cycles. Returns (agreement, convergence, iterations,
    halted_early, cycle_residuals, level_activations).

    Parity mode: exactly v1 — one H level updated once per cycle, H2 inert.
    Refined mode: H1 updates every cycle; H2 updates every second cycle and
    modulates the input gain for the remainder of the run.
    """
    agreement = float(abs(u_raw.sum()) / max(len(u_raw), 1))

    u = np.zeros(16)
    u[: len(u_raw)] = u_raw
    z_L = np.zeros(DIM)
    h1 = np.zeros(DIM)
    h2 = np.zeros(DIM)
    cycle_residuals, level_activations = [], []

    residuals, steps, halted = [], 0, False
    for cycle in range(N_H):
        for _ in range(N_L):
            drive_now = drive * (1.0 + 0.1 * float(h2.mean())) if refined else drive
            z_new = np.tanh(_M_L @ z_L + drive_now + h1)
            residuals.append(float(np.linalg.norm(z_new - z_L)))
            z_L, steps = z_new, steps + 1
            if residuals[-1] < (1 - ANCHOR) * 0.1:  # clean settle (v1 rule)
                halted = True
                break
        # H1 (tactical): every cycle — this is v1's single H level.
        h1 = np.tanh(_M_H @ h1 + z_L)
        # H2 (strategic): every second cycle; in parity mode it stays inert
        # so trajectories remain byte-identical to v1.
        if refined and (cycle + 1) % 2 == 0:
            h2 = np.tanh(_M_H @ h2 + 0.5 * h1)
        level_activations.append([float(h1.mean()), float(h2.mean())])
        cycle_residuals.append(list(residuals[cycle * N_L : (cycle + 1) * N_L]))
        if halted:
            break

    r0 = max(residuals[0], _EPS)
    convergence = _slope_convergence(residuals, r0) if refined else _endpoint_convergence(residuals, r0)
    return agreement, convergence, steps, halted, cycle_residuals, level_activations


def _core(
    signals: Mapping[str, float],
    weights: Optional[Mapping[str, float]],
    refined: bool,
    want_trace: bool = False,
) -> Tuple[HRM2Resolution, Dict[str, Any]]:
    names = sorted(signals)
    k = len(names)
    if k == 0:
        empty = HRM2Resolution(0, "NULL", 0, 0.0, 0.0, 0.0, 0, False, False, "no input sources")
        trace: Dict[str, Any] = {}
        if want_trace:
            trace = {
                "version": "2.0",
                "names": [],
                "levels": (N_L, N_H),
                "inputs": {"signals": {}, "weights": None},
                "iterations_used": 0,
                "cycle_residuals": [],
                "level_activations": [],
                "gate": {"threshold": GATE_THRESHOLD, "decision": "no input"},
                "basis": "no input sources",
            }
        return empty, trace

    w_map = _validate_weights(signals, weights)
    u_raw = np.array([float(np.clip(signals[n], -1, 1)) for n in names])

    # -- Canonical direction (unchanged from canon: unweighted sum) --------
    raw = Ternary.resolve(*u_raw)

    # -- Sovereign Absolution: unanimous hard SELL -> NULL -----------------
    if k > 1 and bool(np.all(u_raw <= -ANCHOR)):
        res = HRM2Resolution(
            0, "NULL", raw, 0.0, 1.0, 0.0, 0, False, True,
            "sovereign absolution: unanimous SELL absorbed",
            bool(w_map), refined,
        )
        trace = (
            {
                "version": "2.0",
                "names": names,
                "levels": (N_L, N_H),
                "inputs": {"signals": dict(signals), "weights": w_map or None},
                "iterations_used": 0,
                "cycle_residuals": [],
                "level_activations": [],
                "gate": {"threshold": GATE_THRESHOLD, "decision": "absolution override"},
                "basis": res.basis,
            }
            if want_trace
            else {}
        )
        return res, trace

    # Weighted agreement: reliability-weighted unanimity. Direction stays
    # unweighted (canon); weights express how much to TRUST the vote, not
    # how to rig it.
    if w_map:
        weights_vec = np.array([w_map[n] for n in names])
        agreement = float(abs(float(weights_vec @ u_raw)) / max(float(weights_vec.sum()), _EPS))
    else:
        agreement = float(abs(u_raw.sum()) / k)

    drive = _W_IN @ _as_input(u_raw)
    agreement_dyn, convergence, steps, halted, cycle_residuals, level_activations = _run_dynamics(
        drive, u_raw, refined
    )
    # _run_dynamics recomputes unweighted agreement for the trace; the
    # weighted one above is authoritative when weights are present.
    agreement = agreement if w_map else agreement_dyn

    confidence = round(agreement * convergence, 3)

    # -- Stability gate: low coherence never trades -------------------------
    gated = raw
    gate_note = ""
    gate_decision = "kept"
    if raw != Ternary.NULL and confidence < GATE_THRESHOLD:
        gated = Ternary.NULL
        gate_note = f" | gated to NULL (confidence {confidence} < {GATE_THRESHOLD:.3f})"
        gate_decision = f"gated (confidence {confidence} < {GATE_THRESHOLD:.3f})"

    basis = " . ".join(
        f"{n}:{v:+.2f}" + (f"(w{w_map[n]:.2f})" if w_map else "")
        for n, v in zip(names, u_raw)
    ) + gate_note

    res = HRM2Resolution(
        state=gated,
        label=Ternary.label(gated),
        raw_state=raw,
        confidence=confidence,
        agreement=round(agreement, 3),
        convergence=round(convergence, 3),
        iterations=steps,
        halted_early=halted,
        absolution_fired=False,
        basis=basis,
        weighted=bool(w_map),
        refined=refined,
    )
    if not want_trace:
        return res, {}
    trace = {
        "version": "2.0",
        "names": names,
        "levels": (N_L, N_H),
        "inputs": {"signals": dict(signals), "weights": w_map or None},
        "iterations_used": steps,
        "cycle_residuals": cycle_residuals,
        "level_activations": level_activations,
        "gate": {"threshold": GATE_THRESHOLD, "decision": gate_decision},
        "basis": basis,
    }
    return res, trace


def _as_input(u_raw: "np.ndarray") -> "np.ndarray":
    """Pad the signal vector into the 16-wide input channel (v1 layout)."""
    u = np.zeros(16)
    u[: len(u_raw)] = u_raw
    return u


def hrm2_resolve(
    signals: Mapping[str, float],
    weights: Optional[Mapping[str, float]] = None,
    *,
    refined: bool = False,
) -> HRM2Resolution:
    """Resolve signals into a gated 1.58-bit ternary decision.

    signals: {"orderbook": 0.8, "sentiment": -0.2, ...}; each in [-1,+1].
    weights: optional per-source reliability in [0,1]; keys must cover all
             signals. Affects agreement/confidence, not the canonical sum.
    refined: run the full SHRM 2.0 dynamics (H-hierarchy + slope
             convergence). Default False preserves exact v1 behavior.
    """
    res, _ = _core(signals, weights, refined, want_trace=False)
    return res


def resolve_with_trace(
    signals: Mapping[str, float],
    weights: Optional[Mapping[str, float]] = None,
    *,
    refined: bool = False,
) -> Tuple[HRM2Resolution, Dict[str, Any]]:
    """Resolve and return the full machine-readable decision trace."""
    res, trace = _core(signals, weights, refined, want_trace=True)
    return res, trace


__all__ = [
    "ANCHOR",
    "GATE_THRESHOLD",
    "HRM2Resolution",
    "Ternary",
    "hrm2_resolve",
    "resolve_with_trace",
]
