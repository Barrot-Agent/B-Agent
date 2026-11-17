#!/usr/bin/env python3
"""TRACE-5 across eight domains.

Same rules as the Millennium run: target sentence first, retrieve by query, quote
must be a literal substring of the fetched text, cross-check or mark single, exit
with a falsifier and what the source does not show. Q quoted, E existence only,
X rejected mismatch. Only Q may support a claim.

The four analysis fields per domain (what_it_is, limit, transmute, mechanism) are
labelled analysis. They are not quotes and carry no grade.

Usage: python3 scripts/trace_domains.py build
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.re_v2 import grade, retrieve

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "domains" / "eight_domains.json"

DOMAINS = [
    {
        "domain": "Ternary logic",
        "what_it_is": "ANALYSIS: a digit set with three states; balanced ternary uses -1, 0, +1 and needs no separate sign bit.",
        "mechanism": "QUOTED BELOW: balanced ternary real arithmetic exists and is claimed to be energy-relevant.",
        "limit": "No mainstream logic family or toolchain; every practical stack is binary, so the efficiency argument cannot be cashed in.",
        "transmute": "Treat the third state as a way to encode sign or unknown. Carry it as a data representation, not as a hardware bet.",
        "specs": [
            {
                "id": "ternary-arithmetic-neglect",
                "problem": "Ternary logic",
                "claim": "Balanced ternary real arithmetic has received almost no attention in the literature despite claimed energy-efficiency benefits.",
                "request": ["arxiv", "2512.10964"],
                "expected_title_fragment": "Tekum: Balanced Ternary Tapered Precision Real Arithmetic",
                "quotes": [
                    "real arithmetic in balanced ternary logic has received almost no attention in the literature",
                    "could open new avenues for energy-efficient computing",
                ],
                "falsifier": "a substantial body of balanced-ternary arithmetic work that this 2025 paper overlooked",
                "does_not_show": "that ternary hardware is cheaper or faster than binary; it reports a format design, not a device measurement",
            },
            {
                "id": "setun-existence",
                "problem": "Ternary logic",
                "claim": "The Setun and Setun 70 were ternary computers, described in a 2011 IFIP chapter.",
                "request": ["doi", "10.1007/978-3-642-22816-2_10"],
                "expected_title_fragment": "Ternary Computers: The Setun and the Setun 70",
                "quotes": [],
                "falsifier": "a primary document showing the machines were binary, which would contradict the title",
                "does_not_show": "content is unverified: the chapter exposes no abstract, so the existence record stands and nothing about their performance is affirmed",
            },
        ],
    },
    {
        "domain": "Quantum mechanics",
        "what_it_is": "ANALYSIS: a probability calculus over complex amplitudes; superposition is linear combination, measurement is the non-linear step that yields one outcome.",
        "mechanism": "QUOTED BELOW: entanglement behaves as a resource, comparable to energy, and is fragile to the environment.",
        "limit": "Fragility: environmental coupling destroys the correlations that make the resource useful; copying is not free, which is why error correction is expensive.",
        "transmute": "Uncopyable shared state: if a state cannot be duplicated, coordination must move or entangle it, never clone it. Applies to agent memory handoff.",
        "specs": [
            {
                "id": "entanglement-as-resource",
                "problem": "Quantum mechanics",
                "claim": "Entanglement is treated as a physical resource comparable to energy, and it is fragile to the environment.",
                "request": ["arxiv", "quant-ph/0702225"],
                "expected_title_fragment": "Quantum entanglement",
                "quotes": [
                    "as a new resource as real as energy",
                    "Being usually fragile to environment",
                ],
                "falsifier": "a demonstration that entanglement survives arbitrary environmental coupling unchanged",
                "does_not_show": "the no-cloning theorem, decoherence rates or any hardware number; those were not fetched in this cycle",
            },
        ],
    },
    {
        "domain": "Algorithms",
        "what_it_is": "ANALYSIS: procedures with a cost model; the claim is about how cost grows, not about any single run.",
        "mechanism": "QUOTED BELOW: sorting by pairwise comparisons costs Theta(n log n) in the noiseless model.",
        "limit": "The bound is model-relative. Change the model (noise, external memory, word RAM) and the bound moves, so a lower bound is only as strong as its model.",
        "transmute": "Carry the habit of naming the model before the bound. A cost claim without its model is not a claim.",
        "specs": [
            {
                "id": "comparison-sorting-bound",
                "problem": "Algorithms",
                "claim": "In the noiseless pairwise-comparison model, Theta(n log n) comparisons are necessary and sufficient for sorting.",
                "request": ["arxiv", "2202.01446"],
                "expected_title_fragment": "Noisy Sorting Capacity",
                "quotes": [
                    "comparisons are both necessary and sufficient when the outcomes of the comparisons are observed with no noise",
                ],
                "falsifier": "a comparison-based sort that is correct on all inputs with asymptotically fewer than n log n comparisons",
                "does_not_show": "anything about noisy or external-memory models, where this paper's capacity result takes over",
            },
        ],
    },
    {
        "domain": "Logarithms",
        "what_it_is": "ANALYSIS: the inverse of exponentiation; turns multiplication into addition, which is why cost and information are measured in log units.",
        "mechanism": "QUOTED BELOW: entropy reduces to the logarithm of cardinality under a uniform distribution.",
        "limit": "Base is a unit choice, not a fact. Comparing logs across bases without converting is a category error.",
        "transmute": "Measure in log units so independent contributions add. Applies to cost accounting and to information budgets.",
        "specs": [
            {
                "id": "entropy-as-log-cardinality",
                "problem": "Logarithms",
                "claim": "Shannon entropy reduces to the logarithm of the cardinality of the set when the distribution is uniform.",
                "request": ["arxiv", "2303.00879"],
                "expected_title_fragment": "Categorical magnitude and entropy",
                "quotes": ["The entropy becomes the logarithm of the cardinality of the set when the uniform probability is used."],
                "falsifier": "a uniform distribution whose entropy is not the log of its support size",
                "does_not_show": "the base convention in use, nor any complexity-theoretic application; it is a statement about a categorical generalization",
            },
        ],
    },
    {
        "domain": "Transformers",
        "what_it_is": "ANALYSIS: a sequence model that routes information by learned pairwise attention weights instead of recurrence.",
        "mechanism": "QUOTED BELOW: attention only, no recurrence and no convolution, and more parallelizable in training.",
        "limit": "Attention compares every position with every other, so cost grows with sequence length; long context is a memory problem before it is a quality problem.",
        "transmute": "Parallel routing beats sequential depth when the dependency graph is dense. Carry attention as a routing primitive, with its quadratic bill attached.",
        "specs": [
            {
                "id": "attention-only-architecture",
                "problem": "Transformers",
                "claim": "The Transformer is built solely on attention, dispensing with recurrence and convolutions, and is more parallelizable.",
                "request": ["arxiv", "1706.03762"],
                "expected_title_fragment": "Attention Is All You Need",
                "quotes": [
                    "based solely on attention mechanisms, dispensing with recurrence and convolutions entirely",
                    "more parallelizable",
                ],
                "falsifier": "a task on which the attention-only architecture is provably less parallelizable than a recurrent one",
                "does_not_show": "scaling behaviour, positional-encoding necessity, or cost per token; the paper predates all of that",
            },
        ],
    },
    {
        "domain": "Transistors",
        "what_it_is": "ANALYSIS: a voltage-controlled switch; the MOSFET's gate field modulates a channel, and the fin or gate-all-around shape is how the channel is wrapped to keep control as it shrinks.",
        "mechanism": "QUOTED BELOW: TCAD modelling projects negative-capacitance FinFETs beyond the last FinFET node.",
        "limit": "Short-channel effects: as the gate length shrinks, the gate loses control of the channel, leakage rises, and the subthreshold slope stops improving.",
        "transmute": "Carry scaling as a control problem, not a size problem. Every gain in density must be paid for with better electrostatic control.",
        "specs": [
            {
                "id": "finfet-scaling-projection",
                "problem": "Transistors",
                "claim": "TCAD simulation projects negative-capacitance FinFET scaling to about the 1.5nm node, beyond the last FinFET node in IRDS.",
                "request": ["arxiv", "2007.14448"],
                "expected_title_fragment": "Negative Capacitance Enables FinFET Scaling Beyond 3nm Node",
                "quotes": [
                    'almost "1.5nm node"',
                    "the last FinFET node according to the International Roadmap for Devices and Systems",
                ],
                "falsifier": "fabricated devices showing that NC-FinFET scaling stops at the 3nm node",
                "does_not_show": "any measured silicon; this is a simulation projection, not a fabricated result",
            },
            {
                "id": "moore-paper-existence",
                "problem": "Transistors",
                "claim": "Moore's 1965 article on component density exists in the Proceedings of the IEEE reprint.",
                "request": ["doi", "10.1109/jproc.1998.658762"],
                "expected_title_fragment": "Cramming More Components Onto Integrated Circuits",
                "quotes": [],
                "falsifier": "a bibliographic record showing the reprint is a different article",
                "does_not_show": "content is unverified: no abstract is exposed, and the 'law' as popularly stated is not in the record",
            },
        ],
    },
    {
        "domain": "Photolithography",
        "what_it_is": "ANALYSIS: an optical transfer process; a mask pattern is imaged onto resist, and resolution is set by wavelength and numerical aperture, not by intent.",
        "mechanism": "QUOTED BELOW: EUV leads on resolution and throughput, while the resist limits further progress.",
        "limit": "The resist, not the optics, is now the stated bottleneck; roughness and resolution trade against each other.",
        "transmute": "Carry the rule that the tool sets the floor. If the process window is set by materials, buying better optics does not help.",
        "specs": [
            {
                "id": "euv-resist-bottleneck",
                "problem": "Photolithography",
                "claim": "EUV is the leading lithography technique, but resist limitations can hamper further resolution progress.",
                "request": ["arxiv", "2310.01268"],
                "expected_title_fragment": "Resistless EUV lithography: photon-induced oxide patterning on silicon",
                "quotes": [
                    "EUV lithography is the leading lithography technique in semiconductor manufacturing due to its high resolution and throughput, but future progress in resolution can be hampered because of the inherent limitations of the resists.",
                ],
                "falsifier": "a resist-free or resist-improved process that removes the resolution ceiling, which this paper itself argues is possible",
                "does_not_show": "the 13.5 nm wavelength, mask architecture or scanner throughput numbers; those were not fetched",
            },
        ],
    },
    {
        "domain": "3D printing",
        "what_it_is": "ANALYSIS: additive manufacturing builds a part by depositing material, so cost scales with volume rather than with the subtraction of a block.",
        "mechanism": "QUOTED BELOW: FFF quality degrades at speed because motion and extrusion desynchronise.",
        "limit": "Process dynamics: the printed result depends on a coupled thermal and mechanical history, so speed, strength and surface finish trade against each other.",
        "transmute": "Carry the control-loop view: calibrate the machine against its own dynamics with cheap sensing, instead of buying precision.",
        "specs": [
            {
                "id": "fff-speed-quality",
                "problem": "3D printing",
                "claim": "FFF quality degrades at high speed from motion-extrusion mis-synchronisation, and camera-based calibration can double throughput at equal quality.",
                "request": ["arxiv", "2512.24905"],
                "expected_title_fragment": "One-Shot Camera-Based Extrusion Optimization for High Speed Fused Filament Fabrication",
                "quotes": [
                    "they exhibit quality loss at high speeds due to dynamic mis-synchronization between printhead motion and material extrusion systems",
                    "effectively doubling production speed while maintaining print quality",
                ],
                "falsifier": "a printer that holds quality at 3600 mm/min without any calibration or control change",
                "does_not_show": "SLA or SLS behaviour, material strength, or dimensional accuracy in absolute terms; one FFF process was measured",
            },
        ],
    },
]


def build() -> int:
    records = []
    domains = []
    for domain in DOMAINS:
        domain_records = [grade(spec, retrieve(spec["request"])) for spec in domain["specs"]]
        records.extend(domain_records)
        domains.append(
            {
                "domain": domain["domain"],
                "what_it_is": domain["what_it_is"],
                "mechanism": domain["mechanism"],
                "limit": domain["limit"],
                "transmute": domain["transmute"],
                "grades": {r["status"]: sum(1 for x in domain_records if x["status"] == r["status"]) for r in domain_records},
                "record_ids": [r["id"] for r in domain_records],
            }
        )
    payload = {
        "method": "reverse-engineering v2 (TRACE-5)",
        "built_at": "2026-11-17",
        "note": "what_it_is, limit and transmute are analysis. mechanism points at the quoted records. Only Q may support a claim.",
        "domains": domains,
        "records": records,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    counts: dict[str, int] = {}
    for record in records:
        counts[record["status"]] = counts.get(record["status"], 0) + 1
    print(json.dumps({"file": str(OUT.relative_to(ROOT)), "domains": len(domains), "records": len(records), "grades": counts}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
