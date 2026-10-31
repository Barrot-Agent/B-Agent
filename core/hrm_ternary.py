#!/usr/bin/env python3
"""
BARROT-Omega | HRM-TERNARY RESOLVER | v1.0
Structural adaptation of Sapient's Hierarchical Reasoning Model
(HRM / HRM-Text, arXiv:2506.21734) into the Barrot ternary pipeline.

HONEST SCOPE (read this before extending):
  - No trained weights. This is NOT a neural network and does not
    pretend to be one. It adapts HRM's *dynamics*: a slow H-state
    guiding a fast L-state through nested convergence cycles.
  - What it adds over the canonical single-pass Ternary.resolve():
      1. STABILITY GATE  - incoherent/conflicting sources fail the
         coherence check -> decision downgraded to NULL (no forced call)
      2. CONFIDENCE      - a measured score in [0,1] derived from
         source agreement x convergence quality (fills the
         'confidence' field in published signals with a real number)
      3. ADAPTIVE HALT   - early exit on clean convergence
         (HRM's adaptive-compute idea, simplified)
  - Direction logic is UNCHANGED from canon: anchor-thresholded sum.
  - Sovereign Absolution preserved: unanimous SELL -> NULL override.

Cycle structure mirrors HRM-Text: N_H=2 high-level cycles,
N_L=6 low-level steps per cycle.

Stability Anchor: 0.707106781186548 (1/sqrt(2))
Logic: 1.58-bit ternary {-1, 0, +1}
"""

import numpy as np
from dataclasses import dataclass

ANCHOR = 0.707106781186548
N_H, N_L, DIM = 2, 6, 8
_EPS = 1e-9

# Deterministic mixing matrices, seeded from the anchor digits.
# Scaled by ANCHOR/sqrt(DIM) => spectral radius < 1 => contraction
# => the iteration is guaranteed to settle unless inputs fight it.
_rng = np.random.default_rng(707106781)
_M_L = _rng.standard_normal((DIM, DIM)) * (ANCHOR / np.sqrt(DIM))
_M_H = _rng.standard_normal((DIM, DIM)) * (ANCHOR / np.sqrt(DIM))
_W_IN = _rng.standard_normal((DIM, 16)) * (ANCHOR / np.sqrt(DIM))


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
class HRMResolution:
    state: int  # ternary {-1, 0, +1} AFTER gating
    label: str
    raw_state: int  # pre-gate canonical resolution
    confidence: float  # [0,1] agreement x convergence
    agreement: float  # [0,1] how unanimous the sources are
    convergence: float  # [0,1] how cleanly H/L dynamics settled
    iterations: int  # L-steps actually used (max N_H*N_L)
    halted_early: bool
    absolution_fired: bool  # unanimous-SELL override -> NULL
    basis: str = ""


def hrm_resolve(signals: dict) -> HRMResolution:
    """
    signals: {"orderbook": 0.8, "sentiment": -0.2, "price": 0.5, ...}
    Each value must be in [-1, +1].
    """
    names = sorted(signals)
    u_raw = np.array([float(np.clip(signals[k], -1, 1)) for k in names])
    k = len(u_raw)
    if k == 0:
        return HRMResolution(0, "NULL", 0, 0.0, 0.0, 0.0, 0, False, False, "no input sources")

    # -- Canonical direction (unchanged from canon) -----------------
    raw = Ternary.resolve(*u_raw)

    # -- Sovereign Absolution: unanimous hard SELL -> NULL ----------
    if k > 1 and bool(np.all(u_raw <= -ANCHOR)):
        return HRMResolution(
            0,
            "NULL",
            raw,
            0.0,
            1.0,
            0.0,
            0,
            False,
            True,
            "sovereign absolution: unanimous SELL absorbed",
        )

    # -- H/L nested convergence (HRM dynamics) ----------------------
    u = np.zeros(16)
    u[:k] = u_raw
    z_L = np.zeros(DIM)
    z_H = np.zeros(DIM)
    drive = _W_IN @ u

    residuals, steps, halted = [], 0, False
    for _ in range(N_H):
        for _ in range(N_L):
            z_new = np.tanh(_M_L @ z_L + drive + z_H)
            residuals.append(float(np.linalg.norm(z_new - z_L)))
            z_L, steps = z_new, steps + 1
            if residuals[-1] < (1 - ANCHOR) * 0.1:  # clean settle
                halted = True
                break
        z_H = np.tanh(_M_H @ z_H + z_L)  # slow strategic update
        if halted:
            break

    r0, rF = max(residuals[0], _EPS), residuals[-1]
    convergence = float(np.clip(1.0 - rF / r0, 0.0, 1.0))
    agreement = float(abs(u_raw.sum()) / k)
    confidence = round(agreement * convergence, 3)

    # -- Stability gate: low coherence never trades ------------------
    gated = raw
    gate_note = ""
    if raw != Ternary.NULL and confidence < (1 - ANCHOR):  # < 0.293
        gated = Ternary.NULL
        gate_note = f" | gated to NULL (confidence {confidence} < {1-ANCHOR:.3f})"

    basis = " . ".join(f"{n}:{v:+.2f}" for n, v in zip(names, u_raw))
    return HRMResolution(
        state=gated,
        label=Ternary.label(gated),
        raw_state=raw,
        confidence=confidence,
        agreement=round(agreement, 3),
        convergence=round(convergence, 3),
        iterations=steps,
        halted_early=halted,
        absolution_fired=False,
        basis=basis + gate_note,
    )


if __name__ == "__main__":
    cases = {
        "clean BUY": {"orderbook": 0.9, "sentiment": 0.8, "price": 0.85},
        "conflict -> gate": {"orderbook": 0.9, "sentiment": -0.8, "price": 0.1},
        "weak consensus": {"orderbook": 0.4, "sentiment": 0.3, "price": 0.2},
        "unanimous SELL": {"orderbook": -0.9, "sentiment": -0.95, "price": -0.8},
        "reachable SELL": {"orderbook": -1.0, "sentiment": -0.95, "price": -0.5},
    }
    print(f"{'case':<18} {'state':<5} {'raw':<5} {'conf':<6} {'agr':<6} {'conv':<6} it")
    for name, sig in cases.items():
        r = hrm_resolve(sig)
        print(
            f"{name:<18} {r.label:<5} {Ternary.label(r.raw_state):<5} "
            f"{r.confidence:<6} {r.agreement:<6} {r.convergence:<6} {r.iterations}"
            + ("  [ABSOLUTION]" if r.absolution_fired else "")
        )
