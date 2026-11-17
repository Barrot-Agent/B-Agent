"""Prediction gate for the cymatics mode check.

Predictions were written in scripts/cymatics_mode_check.py before the first run.
This test fails if the measured eigenproblem disagrees with them.

One prediction was too strong and is recorded as such: per-axis nodal counts for
degenerate mode pairs are not determined by frequency, because the solver (like a
physical drive) returns an arbitrary mixture of the degenerate pair. That is a
result, not a bug: same frequency, two patterns.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.cymatics_mode_check import measured_ratios


def test_ten_modes_measured():
    data = measured_ratios()
    assert len(data["modes"]) == 10


def test_ratios_match_sqrt_m2_plus_n2():
    for row in measured_ratios()["modes"]:
        predicted = row["predicted_ratio"]
        error = abs(row["ratio"] - predicted) / predicted
        assert error < 0.015, (row["mode"], row["ratio"], predicted, error)


def test_non_degenerate_mode_has_predicted_nodal_lines():
    # (2,2) is the only non-degenerate mode in the first ten: one line per axis.
    row = next(r for r in measured_ratios()["modes"] if r["mode"] == "(2,2)")
    assert (row["nodal_x"], row["nodal_y"]) == (1, 1)


def test_degenerate_pair_shares_a_frequency():
    modes = {r["mode"]: r for r in measured_ratios()["modes"]}
    for left, right in (("(1,2)", "(2,1)"), ("(1,3)", "(3,1)"), ("(2,3)", "(3,2)")):
        assert math.isclose(modes[left]["ratio"], modes[right]["ratio"], rel_tol=1e-3)
        # Same frequency, mixed nodal pattern: counts need not stay per-axis.
        assert modes[left]["nodal_x"] + modes[left]["nodal_y"] >= 1
        assert modes[right]["nodal_x"] + modes[right]["nodal_y"] >= 1
