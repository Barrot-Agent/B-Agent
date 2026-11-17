#!/usr/bin/env python3
"""Bounded probe of the Mertens function, an RH-adjacent quantity.

Mertens conjectured |M(x)| < sqrt(x) for all x. That is false (Odlyzko and
te Riele, 1985), which makes it a useful falsifier case: a conjecture in the
neighbourhood of RH that died to a computation, not to rhetoric.

This script measures the ratio only up to a small bound. It cannot confirm or
refute anything beyond that bound, and says so.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path


def mobius_sieve(n: int) -> list[int]:
    mu = [1] * (n + 1)
    prime = [True] * (n + 1)
    for p in range(2, n + 1):
        if prime[p]:
            for multiple in range(p, n + 1, p):
                if multiple > p:
                    prime[multiple] = False
                mu[multiple] = -mu[multiple]
            pp = p * p
            for multiple in range(pp, n + 1, pp):
                mu[multiple] = 0
    mu[0] = 0
    return mu


def probe(n: int = 1_000_000) -> dict:
    started = time.perf_counter()
    mu = mobius_sieve(n)
    running = 0
    peak = (0.0, 1)
    for x in range(1, n + 1):
        running += mu[x]
        if x % 1000 == 0:
            ratio = abs(running) / (x ** 0.5)
            if ratio > peak[0]:
                peak = (ratio, x)
    final = running / (n ** 0.5)
    return {
        "bound": n,
        "abs_M_over_sqrt_x_at_bound": round(abs(final), 6),
        "seconds": round(time.perf_counter() - started, 3),
        "max_abs_M_over_sqrt_x": round(peak[0], 6),
        "at_x": peak[1],
        "mertens_conjecture": "FALSE (Odlyzko and te Riele, 1985); smallest known counterexample lies beyond 1e14",
        "what_this_shows": "peak below 1 up to the bound, which the false conjecture also predicts in this range; therefore evidence for nothing beyond the bound",
    }


if __name__ == "__main__":
    out = probe(int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000)
    path = Path("results/millennium/mertens.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
