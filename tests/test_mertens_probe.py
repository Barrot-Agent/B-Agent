"""The Mertens probe must stay bounded and must not overclaim."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.mertens_probe import mobius_sieve, probe


def test_mobius_values_are_correct_at_small_numbers():
    mu = mobius_sieve(30)
    assert mu[1] == 1
    assert mu[2] == -1
    assert mu[4] == 0
    assert mu[6] == 1
    assert mu[30] == -1


def test_probe_reports_a_bound_and_a_ratio():
    out = probe(20_000)
    assert out["bound"] == 20_000
    assert 0.0 <= out["max_abs_M_over_sqrt_x"] < 5.0
    assert "evidence for nothing beyond the bound" in out["what_this_shows"]
