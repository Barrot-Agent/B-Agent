"""barrot_agent.reasoning — hierarchical reasoning engines.

SHRM 2.0 (Sapient's Hierarchical Reasoning Model, refinement 2.0) is the
entry point; it refines core/hrm_ternary.py (v1) with weighted sources,
a genuine two-level H hierarchy (opt-in), a slope-based convergence
metric (opt-in), and a full machine-readable decision trace.

Parity guarantee: ``hrm2_resolve(signals)`` (unweighted, default mode)
reproduces ``core.hrm_ternary.hrm_resolve`` labels exactly — property-
tested against randomized corpora in tests/test_hrm_ternary_v2.py.
"""

from .hrm import (
    ANCHOR,
    GATE_THRESHOLD,
    HRM2Resolution,
    Ternary,
    hrm2_resolve,
    resolve_with_trace,
)

__all__ = [
    "ANCHOR",
    "GATE_THRESHOLD",
    "HRM2Resolution",
    "Ternary",
    "hrm2_resolve",
    "resolve_with_trace",
]
