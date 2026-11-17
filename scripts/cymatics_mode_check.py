#!/usr/bin/env python3
"""Cymatics mode check: does a plate mode follow the eigenproblem, or frequency magic?

Layer 1 physics, numerically tested. The 2D wave equation on a square domain with
fixed edges is

    u_tt = c^2 (u_xx + u_yy),  u = 0 on the boundary

whose modes are u_mn = sin(m*pi*x) sin(n*pi*y) with

    f_mn proportional to sqrt(m^2 + n^2).

PREDICTIONS, written before the first run (2026-11-17):
  1. f(1,2)/f(1,1) = sqrt(5/2) = 1.5811  (+/- 2%)
  2. f(2,1)/f(1,1) = 1.5811              (degenerate with (1,2))
  3. f(2,2)/f(1,1) = sqrt(4) = 2.0000
  4. f(1,3)/f(1,1) = sqrt(10/2) = 2.2361
  5. interior nodal lines counted along an off-axis cut:
     (1,1) -> 0 in x, 0 in y
     (1,2) -> 0 in x, 1 in y
     (1,3) -> 0 in x, 2 in y
     (2,2) -> 1 in x, 1 in y

If any prediction fails, the frequency-only story is wrong and the mode story is
wrong with it. That is the point of the test.

This is a finite-difference solve of the eigenproblem, not a physical plate: it
tests the mathematics that the sand pattern is claimed to follow.
"""

from __future__ import annotations

import json
import math

import numpy as np
from scipy.sparse import diags, eye, kron
from scipy.sparse.linalg import eigsh


def mode_index_pairs(max_index: int = 6) -> list[tuple[int, int]]:
    """(m, n) pairs sorted by sqrt(m^2+n^2), the predicted frequency order."""
    pairs = [(m, n) for m in range(1, max_index + 1) for n in range(1, max_index + 1)]
    return sorted(pairs, key=lambda p: (math.hypot(*p), p))


def solve_modes(n_grid: int = 60, k: int = 10) -> tuple[np.ndarray, np.ndarray]:
    """Lowest k eigenpairs of the discrete Laplacian on an n_grid x n_grid square.

    Returns (eigenvalues, eigenvectors) with eigenvectors as columns of shape
    (n_grid*n_grid, k), ordered by increasing eigenvalue.
    """
    h = 1.0 / (n_grid + 1)
    main = np.full(n_grid, 2.0 / h**2)
    off = np.full(n_grid - 1, -1.0 / h**2)
    t = diags([off, main, off], offsets=[-1, 0, 1], shape=(n_grid, n_grid))
    lap = kron(eye(n_grid), t) + kron(t, eye(n_grid))
    values, vectors = eigsh(lap.tocsc(), k=k, sigma=0.0, which="LM")
    order = np.argsort(values)
    values = np.sqrt(np.clip(values[order], 0.0, None))  # sqrt(lambda) ~ frequency
    vectors = vectors[:, order]
    return values, vectors


def nodal_counts(field: np.ndarray, cut: float = 0.37) -> tuple[int, int]:
    """Interior nodal lines crossed along an off-axis row and column.

    A sign change along a cut is a crossing of a nodal line. The cut is placed at
    0.37 so it never lands exactly on a nodal line for the modes tested.
    """
    n = field.shape[0]
    idx = max(1, min(n - 2, int(round(cut * (n - 1)))))
    row = field[idx, :]
    col = field[:, idx]
    return _sign_changes(row), _sign_changes(col)


def _sign_changes(line: np.ndarray) -> int:
    trimmed = line[1:-1]
    trimmed = trimmed[np.abs(trimmed) > 1e-9]
    return int(np.count_nonzero(np.diff(np.sign(trimmed)) != 0))


def measured_ratios(n_grid: int = 60) -> dict:
    values, vectors = solve_modes(n_grid=n_grid, k=10)
    pairs = mode_index_pairs()[: len(values)]
    base = values[0]
    rows = []
    for freq, pair, vector in zip(values, pairs, vectors.T):
        field = vector.reshape(n_grid, n_grid)
        x_nodes, y_nodes = nodal_counts(field)
        rows.append(
            {
                "mode": f"({pair[0]},{pair[1]})",
                "ratio": round(float(freq / base), 4),
                "predicted_ratio": round(math.hypot(*pair) / math.hypot(1, 1), 4),
                "nodal_x": x_nodes,
                "nodal_y": y_nodes,
                "predicted_nodal_x": pair[0] - 1,
                "predicted_nodal_y": pair[1] - 1,
            }
        )
    return {"grid": n_grid, "modes": rows}


if __name__ == "__main__":
    print(json.dumps(measured_ratios(), indent=2))
