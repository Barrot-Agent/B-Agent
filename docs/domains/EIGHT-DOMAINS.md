# Eight domains under TRACE-5

Date: 2026-11-17. Baseline: HEAD 37055f7a2. Data: data/domains/eight_domains.json.
Code: scripts/trace_domains.py, validator scripts/re_v2.py.

Every source below was reached by an arXiv query or a Crossref title query on this
date. No identifier was written from memory. Quotes are literal substrings of the
stored abstracts. Grades: Q quoted, E existence only, X rejected. Totals: Q 8, E 2,
X 0. Analysis fields are labelled ANALYSIS and carry no grade.

## 1. Ternary logic

- What it is really: a digit set with three states; balanced ternary uses -1, 0, +1
  and needs no separate sign bit.
- Mechanism, quoted (Q, arXiv 2512.10964): "real arithmetic in balanced ternary
  logic has received almost no attention in the literature", which "could open new
  avenues for energy-efficient computing".
- Limit: no mainstream logic family or toolchain. Every practical stack is binary,
  so the efficiency argument has nowhere to be spent.
- Transmute: use the third state as a representation for sign or unknown, not as a
  hardware bet.
- Second record: Setun and Setun 70 (doi 10.1007/978-3-642-22816-2_10), grade E, no
  abstract exposed, nothing about their performance affirmed.

## 2. Quantum mechanics

- What it is really: a probability calculus over complex amplitudes; superposition
  is linear combination, measurement is the non-linear step that returns one outcome.
- Mechanism, quoted (Q, arXiv quant-ph/0702225): entanglement entered laboratories
  "as a new resource as real as energy", and is "Being usually fragile to
  environment".
- Limit: fragility. Coupling to the environment destroys the correlations that make
  the resource useful, and copying is not free.
- Transmute: uncopyable shared state. Coordination must move or entangle a state,
  never clone it. Applies directly to handoff between agents.
- Not covered, stated rather than implied: no-cloning and decoherence numbers were
  not fetched this cycle.

## 3. Algorithms

- What it is really: procedures with an explicit cost model; the claim is about
  growth, not about any single run.
- Mechanism, quoted (Q, arXiv 2202.01446): "comparisons are both necessary and
  sufficient when the outcomes of the comparisons are observed with no noise",
  giving Theta(n log n) for comparison sorting.
- Limit: the bound is model-relative. Noise, external memory and word size move it.
- Transmute: name the model before the bound. A cost claim without its model is not
  a claim, which is also true of this repo's own task estimates.

## 4. Logarithms

- What it is really: the inverse of exponentiation; multiplication becomes addition,
  which is why information and cost are counted in log units.
- Mechanism, quoted (Q, arXiv 2303.00879): "The entropy becomes the logarithm of the
  cardinality of the set when the uniform probability is used."
- Limit: the base is a unit choice, not a fact. Comparing logs across bases without
  converting is a category error.
- Transmute: measure in log units so independent contributions add instead of
  multiplying. Use it for budgets, not just for entropy.

## 5. Transformers

- What it is really: a sequence model that routes information by learned pairwise
  attention weights instead of recurrence.
- Mechanism, quoted (Q, arXiv 1706.03762): "based solely on attention mechanisms,
  dispensing with recurrence and convolutions entirely", and "more parallelizable".
- Limit: attention compares every position with every other, so cost grows with
  sequence length. Long context is a memory problem before it is a quality problem.
- Transmute: parallel routing beats sequential depth when the dependency graph is
  dense, provided the quadratic bill is paid explicitly.

## 6. Transistors

- What it is really: a voltage-controlled switch. The gate field modulates a
  channel; fin and gate-all-around shapes exist to keep that control as it shrinks.
- Mechanism, quoted (Q, arXiv 2007.14448): negative-capacitance FinFETs can be
  scaled to almost "1.5nm node", beyond "the last FinFET node according to the
  International Roadmap for Devices and Systems".
- Limit: short-channel effects. As gate length shrinks the gate loses control, and
  leakage rises faster than density.
- Transmute: treat scaling as a control problem, not a size problem. Every density
  gain is paid for with electrostatic control.
- Not covered: this record is TCAD simulation, not fabricated silicon, and says so.
  Moore 1965 (doi 10.1109/jproc.1998.658762) is grade E: the article exists, its
  content is not verified here.

## 7. Photolithography

- What it is really: an optical transfer process. A mask is imaged onto resist, and
  resolution is set by wavelength and numerical aperture, not by intent.
- Mechanism, quoted (Q, arXiv 2310.01268): "EUV lithography is the leading
  lithography technique in semiconductor manufacturing due to its high resolution and
  throughput, but future progress in resolution can be hampered because of the
  inherent limitations of the resists."
- Limit: the resist, not the optics, is the stated bottleneck; roughness and
  resolution trade against each other.
- Transmute: the tool sets the floor. If the process window is set by materials,
  better optics will not rescue it.

## 8. 3D printing

- What it is really: additive manufacturing deposits material where it is needed, so
  cost scales with deposited volume rather than with a subtracted block.
- Mechanism, quoted (Q, arXiv 2512.24905): "they exhibit quality loss at high speeds
  due to dynamic mis-synchronization between printhead motion and material extrusion
  systems", and camera calibration recovers quality while "effectively doubling
  production speed".
- Limit: the result depends on a coupled thermal and mechanical history, so speed,
  strength and finish trade against one another.
- Transmute: calibrate the machine against its own dynamics with cheap sensing
  instead of buying precision.

## Cross-domain read

Three of the eight limits are the same shape: the process, not the intent, sets the
result (resist in lithography, extrusion dynamics in printing, electrostatic control
in transistors). Two are resource-conversion limits (entanglement fragility, ternary
without a toolchain). Three are model-relative bounds (sorting, log base, attention
cost). That grouping is analysis, not a quoted claim.

## What this does not claim

No domain is mastered. Each has one or two fetched records, not a literature review.
Domains 2 and 6 have the thinnest coverage and are marked accordingly.

## Licence and status

arXiv and Crossref metadata, fetched 2026-11-17, HTTP 200 per record. No full texts
redistributed.
