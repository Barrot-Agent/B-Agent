#!/usr/bin/env python3
"""TRACE-5 on the consciousness-bridge question.

Target: "Consciousness is the bridge between General Relativity and Quantum
Mechanics." Falsifiable form: there exists a sourced statement linking conscious
experience to a unification of GR and QM, with a test that could fail.

Nothing is written from memory. Every quote is checked by scripts/re_v2.py against
the stored abstract.

Usage: python3 scripts/consciousness_trace.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.re_v2 import grade, retrieve

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "research" / "consciousness_gr_qm.json"

TARGET = "Consciousness is the bridge between General Relativity and Quantum Mechanics."
FALSIFIABLE = (
    "At least one sourced statement links conscious experience to a unification of GR and QM, "
    "and states an observation that would refute it."
)

SPECS = [
    {
        "id": "gr-initial-value",
        "problem": "GR",
        "claim": "General Relativity is analysed as an initial-value (Cauchy) problem with hyperbolic evolution.",
        "request": ["arxiv", "1507.00476"],
        "expected_title_fragment": "The Cauchy problem in General Relativity",
        "quotes": [
            "we shall analyse the structure of the Cauchy Problem (CP briefly) for General Relativity (GR briefly)",
        ],
        "falsifier": "a formulation of GR in which no initial data determine the evolution",
        "does_not_show": "global determinism: singularities and topology can stop evolution, and nothing here concerns quantum coupling",
    },
    {
        "id": "decoherence-unsolved-measurement",
        "problem": "QM",
        "claim": "Decoherence alone does not solve the quantum measurement problem.",
        "request": ["arxiv", "quant-ph/0112095"],
        "expected_title_fragment": "Why Decoherence has not Solved the Measurement Problem",
        "quotes": ["decoherence has not solved the quantum measurement problem"],
        "falsifier": "a derivation of single outcomes from unitary evolution plus environmental coupling alone",
        "does_not_show": "which interpretation is right; it denies a claim, not establishes a replacement",
    },
    {
        "id": "orch-or-incompatible",
        "problem": "Orch-OR",
        "claim": "A 2004 paper argues that the Hameroff-Penrose Orch-OR model is incompatible with environmental decoherence.",
        "request": ["arxiv", "quant-ph/0403051"],
        "expected_title_fragment": "Quantum Models of Mind",
        "quotes": ["the Hameroff Penrose model is not compatible with decoherence"],
        "falsifier": "a demonstration that Orch-OR collapse times survive environmental decoherence in warm neural tissue",
        "does_not_show": "that Orch-OR is false; it shows one compatibility objection, from one paper",
    },
    {
        "id": "iit-defines-phi",
        "problem": "IIT",
        "claim": "Integrated Information Theory defines a quantitative measure, Phi, of integrated cause-effect structure.",
        "request": ["arxiv", "1806.01421"],
        "expected_title_fragment": "Towards Quantum Integrated Information Theory",
        "quotes": [
            "quantifies how much the integrated cause/effect structure of the global neural network fails to be accounted for by any partitioned version of it",
        ],
        "falsifier": "a system with high Phi and no reported experience, or the reverse, under a pre-registered measure",
        "does_not_show": "that Phi explains experience, or that it has anything to do with gravity",
    },
    {
        "id": "iit-missing-attention",
        "problem": "IIT",
        "claim": "A 2024 critique argues that IIT lacks an account of attention and therefore cannot explain informational differences between experiences.",
        "request": ["arxiv", "2406.06143"],
        "expected_title_fragment": "The Integrated Information Theory needs Attention",
        "quotes": ["we argue that IIT urgently needs an account of attention"],
        "falsifier": "an IIT account that predicts attentional effects on experience content",
        "does_not_show": "that IIT is wrong about consciousness; it identifies a missing component",
    },
    {
        "id": "gwt-broadcast-no-criterion",
        "problem": "Global workspace",
        "claim": "A 2026 preprint states that global workspace theory explains conscious access as broadcasting but lacks a formal criterion for the enabling mechanism.",
        "request": ["arxiv", "2608.15926"],
        "expected_title_fragment": "A Control-Theoretic Formulation of Global Workspace Theory",
        "quotes": [
            "Global workspace theory explains conscious access as the broadcasting of selected information to the rest of the network, but it lacks a formal criterion for identifying the mechanism that enables this access.",
        ],
        "falsifier": "a workspace model with a formal criterion that fails to predict access",
        "does_not_show": "any quantum or gravitational content; single unrefereed source",
    },
    {
        "id": "qbism-agent-judgment",
        "problem": "QBism",
        "claim": "QBism treats the quantum state as an agent's personal judgment rather than a description of the world.",
        "request": ["arxiv", "2303.01446"],
        "expected_title_fragment": "QBism, Where Next?",
        "quotes": ["A quantum state is an agent's personal judgment."],
        "falsifier": "a QBist prediction that constrains a state independently of any agent",
        "does_not_show": "any role for gravity or spacetime; the agent here is an interpreter, not a physical bridge",
    },
    {
        "id": "everett-relative-state",
        "problem": "Many-worlds",
        "claim": "Everett's relative-state formulation treats measurement as branching without collapse.",
        "request": ["doi", "10.1515/9781400868056-003"],
        "expected_title_fragment": "Relative State",
        "quotes": [],
        "falsifier": "a branching formulation that still requires a collapse postulate",
        "does_not_show": "content is unverified: no abstract exposed, so the branching claim is not affirmed here",
    },
    {
        "id": "causal-set-time-assertion",
        "problem": "Consciousness bridge",
        "claim": "A 2022 preprint proposes that the birth process of spacetime atoms in causal set theory is an objective correlate of the passage of time and of experience.",
        "request": ["arxiv", "2209.07653"],
        "expected_title_fragment": "Causal Set Quantum Gravity and the Hard Problem of Consciousness",
        "quotes": ["an objective physical correlate of our perception of time passing"],
        "falsifier": "a causal set prediction of a measurable timing effect in neural tissue that fails to appear",
        "does_not_show": "no experiment, no number; interpretive proposal, excluded from evidence",
        "exclude": True,
        "exclude_reason": "interpretive preprint with no testable prediction; quoted to show the claim exists, not that it holds",
    },
]


def build() -> int:
    records = [grade(spec, retrieve(spec["request"])) for spec in SPECS]
    grades: dict[str, int] = {}
    for record in records:
        grades[record["status"]] = grades.get(record["status"], 0) + 1
    payload = {
        "question": "Is consciousness the bridge between General Relativity and Quantum Mechanics?",
        "target": TARGET,
        "falsifiable_form": FALSIFIABLE,
        "method": "reverse-engineering v2 (TRACE-5)",
        "built_at": "2026-11-17",
        "grades": grades,
        "usable_claims": sum(1 for r in records if r["status"] == "Q" and not r["excluded_from_evidence"]),
        "records": records,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"file": str(OUT.relative_to(ROOT)), "grades": grades, "usable": payload["usable_claims"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
