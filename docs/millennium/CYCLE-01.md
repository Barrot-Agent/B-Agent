# Millennium cycle 01: database audit, Poincare verified, six gaps

Date: 2026-11-17. Baseline: HEAD d28e03e7e. Machine-readable companions:
data/millennium/ledger.json and data/millennium/poincare_sources.json.

## Transmutation

ORIGINAL: "Use all up-to-date resolutions on the Millennium Problems against the
entire acquired database. For the six unsolved, map partial results, cross-analyze
the paradigms, name the blocking gap, propose a transmuted approach borrowing from
Poincare, require a measured KPI before claiming progress, then work on any
conjecture touching these six, indefinitely."

GAP 1: the acquired database is narrative. [FILLED GAP] Audited, not assumed:
7 problem files, 7 overview rows, 6 seed claims, three research bundles holding 30,
67 and 20 records. Proof artifacts, lemmas, machine-checked statements: zero. The
files contain why-it-matters prose and next-step lists. The audit says this out
loud instead of dressing it as a research corpus.

GAP 2: "all known and up-to-date" cannot be established from this repo. [FILLED
GAP] Only what is fetched counts. Five preprints were fetched from the arXiv API
today, five verification documents too, with title and first-submission date read
from the response. Everything else is listed as unfetched and may not be cited as
established.

GAP 3: "work indefinitely" has no stop rule. [FILLED GAP] A cycle ends when it
lands one verified artifact or names the data that blocks it. Both are recorded.

GAP 4: no way to separate progress from prose. [FILLED GAP] KPI gate below: a
machine-checked lemma, a reproducible computation, or a fetched citation quoted in
full. Nothing else counts as progress here.

## Poincare: the verified record

| Preprint | First submitted | What it contributes |
|---|---|---|
| math/0211159, The entropy formula for the Ricci flow | 2002-11-11 | entropy monotonicity, no local collapsing, canonical neighbourhoods |
| math/0303109, Ricci flow with surgery on three-manifolds | 2003-03-10 | the surgery procedure, extinction argument |
| math/0307245, Finite extinction time | 2003-07-17 | finite extinction, closing the remaining case |

Technique, stated as the pattern rather than the topic: Hamilton's Ricci flow made
controllable by Perelman's monotone functionals. Entropy and reduced volume forbid
collapse and localise singularities, so surgery is applied to a controlled object
rather than to a black box. Deformation, monotone quantity, controlled
singularities.

Verification: Kleiner-Lott, math/0605667, and Morgan-Tian, math/0607607, both
fetched 2026-11-17. Two later documents were also fetched: 1512.00699, a
correction to Section 19.2 of Morgan-Tian, and 1512.02046, a counterexample to
Corollary 19.10 of the same monograph. Recorded because it is the honest shape of
a verification record: a maintained body of work with published errata, not a
sealed verdict.

## The six open problems

| Problem | Blocking gap | Transmuted approach | Fetched anchor |
|---|---|---|---|
| P vs NP | relativization, natural proofs and algebrization rule out every known technique; circuit lower bounds do not reach NP | geometric complexity theory: representation-theoretic obstructions, deliberately non-relativizing; check occurrence obstructions first | none fetched |
| Hodge | integral form is false; rational form has no general cycle construction above codimension one | reframe as which cohomology classes survive monodromy of a variation of Hodge structure; test on known counterexamples before general claims | none fetched |
| Riemann | no archimedean positivity, no exact trace formula over the integers; function-field case is settled | de Bruijn-Newman flow: RH is the statement that the constant is exactly zero, and non-negativity is now a theorem, so the gap is a monotone quantity at t = 0 | Rodgers-Tao, 1801.05914, fetched |
| Yang-Mills | no nonperturbative four-dimensional construction, no control of the renormalization flow sufficient for a gap | Osterwalder-Schrader reconstruction plus a rigorous Wilsonian flow; the monotone quantity is the effective action under scale; test on the lattice first | none fetched |
| Navier-Stokes | supercritical: energy sits at the critical scaling, no monotone quantity excludes blow-up in 3D | search in the scaling-invariant norm for a non-increasing functional; energy-only arguments are already excluded by a known averaged-equation blow-up | Tao, 1402.0290, fetched |
| BSD | rank zero and one are covered; rank two and above lack Euler systems | treat Euler systems as the monotone-divisibility analogue: each level buys a divisibility that improves with rank | none fetched |

An "none fetched" anchor is not a claim that the work does not exist. It is a
statement that this cycle did not verify it, so it does not get to appear as
established.

## Cross-analysis: what the partial attempts share

1. Shape of a success: every resolved case in this family traded a hard global
   statement for a deformation plus a monotone quantity. Ricci flow and entropy;
   Euler systems as a divisibility that never decreases; the effective action under
   scale. Where the monotone object is missing, the problem is still open.
2. Shape of a barrier: a barrier theorem is a statement about a class of
   techniques, not about the problem. That is why borrowing the Poincare pattern
   works conceptually but not mechanically: the analogy supplies a template, not a
   proof.
3. Verification is part of the solution, not an afterthought. Poincare needed two
   independent expositions and still collected corrections. A claim without that
   structure is unfinished work.
4. Every failed approach recorded above failed for a nameable reason: supercritical
   scaling, missing positivity, absent Euler systems, false integral form. Failure
   with a reason is data. Failure without one is noise.

## Adjacent conjecture probed: Mertens

Mertens conjectured |M(x)| < sqrt(x). It is false, killed by computation rather
than by rhetoric, which makes it the right test case for a hypothesis-adjacent
claim.

scripts/mertens_probe.py, measured 2026-11-17: bound 10^6, runtime 0.66 s, peak
|M(x)|/sqrt(x) = 0.413118 at x = 96000, value at the bound 0.212. The peak stays
below 1, which is exactly what the false conjecture also predicts in this range.
Recorded conclusion: evidence for nothing beyond the bound. The script says this
in its own output so the number cannot be quoted as support.

## What is not claimed

No progress on any of the six. No proof, no partial proof, no "insight that might
lead to" a proof stated as a result. The database cannot support such a claim and
neither can this cycle.

## Cycle 02 stop rule

Each of the six open problems needs one fetched primary citation before its partial
results may be described as established. Until then those rows stay as named gaps
with named approaches. Cycle 02 exists only if that fetch happens, and it will be
scored by how many rows move from "none fetched" to a cited record, not by how much
prose is produced.

## Licence and status

arXiv API metadata, fetched 2026-11-17, HTTP 200 recorded per item in
data/millennium/poincare_sources.json. No full text redistributed. No other source
was touched in this cycle.
