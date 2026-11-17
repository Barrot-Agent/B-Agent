# Consciousness as a bridge between GR and QM: TRACE-5 verdict

Date: 2026-11-17. Baseline HEAD: 4a4bfcbcc. Claims file:
data/research/consciousness_gr_qm.json (9 records, grades Q 8 / E 1 / X 0,
usable 7, 1 Q excluded). Offline re-validation: `python3 scripts/re_v2.py check`
-> `"valid": true`.

## Target

Question: is consciousness the bridge between General Relativity and Quantum
Mechanics?

Falsifiable form: at least one sourced statement links conscious experience to a
unification of GR and QM, and states an observation that would refute it.

## 1. Data pulled, not narrated

`scripts/research_inventory.py` scans every string leaf of the 62 JSON files under
data/ for the fourteen requested terms. Result, copied from
data/research/inventory.json:

| Term | Records mentioning |
|---|---|
| general relativity | 6 |
| quantum mechanics | 7 |
| consciousness | 14 |
| measurement | 16 |
| observer | 0 |
| decoherence | 11 |
| entanglement | 10 |
| information theory | 7 |
| ternary | 19 |
| transformer | 6 |
| transistor | 3 |
| algorithm | 38 |
| logarithm | 12 |

The word "observer" appears in zero stored records. That is a real gap: the
consciousness literature is observer-centric, and this repository has never stored
the term.

A keyword hit is not a claim. Only records that already carry a TRACE-5 grade count
as evidence, and those are the nine in the claims file.

## 2. The gap, quoted

GR side, Q. arXiv 1507.00476, "The Cauchy problem in General Relativity: An
algebraic characterization":

> we shall analyse the structure of the Cauchy Problem (CP briefly) for General Relativity (GR briefly)

Falsifier: a formulation of GR in which no initial data determine the evolution.
What it does not show: global determinism. Singularities and topology can stop
evolution, and nothing in that paper couples gravity to quantum matter.

QM side, Q. arXiv quant-ph/0112095, "Why Decoherence has not Solved the Measurement
Problem":

> decoherence has not solved the quantum measurement problem

Falsifier: a derivation of single outcomes from unitary evolution plus environmental
coupling alone. What it does not show: which interpretation is right. It denies a
claim; it does not establish a replacement.

The exact contradiction in this dataset is not "GR and QM disagree on a measurement".
It is narrower and it lands directly on the bridge hypothesis: the only candidate
mechanism that puts gravity and consciousness in one place is Orch-OR, and the
retrieved critique argues it does not survive environmental decoherence, which is
the same decoherence theory that the QM side says is already insufficient for
measurement.

## 3. Theories tested

| Theory | Claim tested | Grade | Falsifier | Does not show |
|---|---|---|---|---|
| Orch-OR | 2004 critique: the Hameroff-Penrose model is incompatible with decoherence (quant-ph/0403051) | Q | collapse times survive decoherence in warm tissue | that Orch-OR is false; one objection from one paper |
| IIT | defines Phi over integrated cause-effect structure (1806.01421) | Q | high Phi with no reported experience, or reverse, pre-registered | that Phi explains experience, or touches gravity |
| IIT critique | IIT urgently needs an account of attention (2406.06143) | Q | an IIT account predicting attentional effects on content | that IIT is wrong about consciousness |
| Global workspace | access is broadcast, but no formal criterion for the enabling mechanism (2608.15926, 2026 preprint) | Q, unrefereed | a workspace model with a formal criterion that fails to predict access | any quantum or gravitational content |
| QBism | a quantum state is an agent's personal judgment (2303.01446) | Q | a QBist prediction constraining a state independently of an agent | any role for gravity or spacetime |
| Many-worlds | relative-state formulation of measurement (DOI 10.1515/9781400868056-003) | E | a branching formulation that still needs collapse | content unverified: no abstract exposed, claim not affirmed |
| Decoherence without observer | decoherence does not solve measurement (quant-ph/0112095) | Q | single outcomes derived without collapse | an observer substitute |
| Causal-set time | spacetime-atom birth as correlate of time passage (2209.07653) | Q, excluded | a causal-set timing prediction in neural tissue that fails | no experiment, no number; excluded from evidence |

## 4. Emergent capabilities from the cross-analysis

| Capability | Support | Falsifier | Grade |
|---|---|---|---|
| Computation has hard limits independent of physics | algebrization barrier, data/millennium/claims/p_vs_np.json: "we present such a barrier, which we call algebraic relativization or algebrization" | a non-algebrizing separation that still relativizes | Q |
| Observer-dependent reality | QBism quote only | a state constrained with no agent | E: an interpretation says it, no result shows it |
| Information as fundamental | none retrieved this cycle | a physical quantity that is not informational but is conserved identically | X: not fetched, not false |
| Time as emergent | causal-set preprint, excluded | a measured timing effect that fails | E, unrefereed and excluded |
| Consciousness couples to gravity | Orch-OR only, and under a decoherence objection | a measured collapse-time anomaly in neural tissue | X: contradicted on the compatibility question |

Only one capability earns Q, and it is a statement about computation, not about
consciousness, gravity, or their relation. That is the honest yield.

## 5. Verdict

**C: Unsupported / contradicted.**

The falsifier that decides it: no record in this dataset links conscious experience
to a unification of GR and QM with an observation that could refute the link, and the
one mechanism that tries (Orch-OR) carries a quoted decoherence objection against it.

Why not A: A requires a Q quote asserting the bridge. Zero such quotes exist in the
nine records; the only bridge-adjacent quote (causal set) is an interpretive preprint
with no test, and it is excluded.

Why not B: B requires a gap that a specified experiment could close. The retrieved
literature does not even agree on what the bridge would predict, so there is no gap
with a shape.

Why not D: D is "untestable with current data". That is close, but the stronger
statement is available: what does exist is contradicted.

**This verdict would become A if** a peer-reviewed source reports a pre-registered
measurement in which a neural or behavioural variable tracks a specific
quantum-gravity prediction (for example a collapse-rate anomaly scaling with mass or
geometry) and an independent group replicates it. No such source was retrieved.

## 6. What this document does not claim

- It does not claim consciousness is not the bridge. It claims no retrieved Q record
  supports it and one candidate is contradicted on compatibility.
- It does not grade the excluded causal-set preprint as false, only as unusable.
- It does not treat the 2026 global-workspace preprint as refereed.
- It does not claim the inventory is exhaustive over the web, only over data/ in this
  repository at this commit.

## Overrun

Overrun logged, not used as a stop reason: inventory script, claims regeneration,
verdict, loop file, tests, push.
