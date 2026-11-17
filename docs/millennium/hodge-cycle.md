# Hodge under TRACE-5: four quoted claims, one excluded assertion

Date: 2026-11-17. Baseline: HEAD e3c9cf314. Code: scripts/re_v2.py. Record:
data/millennium/claims/hodge_conjecture.json.

Rule applied without exception: no identifier was written from memory. Every source
below was reached by a query, and its title had to match a fragment fixed before the
query ran.

## Targets, written before retrieval

1. The Hodge conjecture is open, not settled.
2. The integral form is false, by a torsion obstruction due to Atiyah and Hirzebruch.
3. Further counterexamples exist in codimension 2 and 3.
4. A Lefschetz (1,1) theorem characterizes divisor classes, and has a normal-variety
   analogue.
5. Some preprint claims a proof for hypersurfaces. Tested, and excluded.

## Retrieval, and what the titles forced

Query `ti:"Hodge conjecture" AND cat:math.AG` returned ten results, including a 2023
and a 2025 preprint asserting a proof. Those are not results. They are assertions,
and v2 grades what a source says, not whether it is right, so the strongest honest
record is "this paper asserts X", excluded from evidence.

Query `ti:"integral Hodge conjecture"` returned counterexample papers, which is where
the integral-form record comes from.

The Atiyah-Hirzebruch paper was reached through Crossref by bibliographic query,
because no recalled identifier was permitted. Title matched: "Analytic cycles on
complex manifolds", Topology, 1962, doi 10.1016/0040-9383(62)90094-0.

## Records

| Record | Grade | Source | Quote used |
|---|---|---|---|
| Open status | Q | arXiv 2105.04695, Known cases of the Hodge conjecture, 2021 | "The Hodge conjecture is a major open problem in complex algebraic geometry" |
| Integral form fails | E | Atiyah-Hirzebruch, Topology 1962, doi 10.1016/0040-9383(62)90094-0 | none: publisher exposes no abstract |
| Counterexamples in codim 2 and 3 | Q | arXiv 1601.06170, Further counterexamples to the integral Hodge conjecture, 2016 | "in complex codimension $2$ and $3$"; "extending his two counterexamples to a general family of groups" |
| Lefschetz (1,1) | Q | arXiv math/9904086, A Lefschetz (1,1) Theorem for normal projective complex varieties, 1999 | "We prove an analogue of the Lefschetz (1,1) Theorem characterizing cohomology classes of Cartier divisors" |
| Hypersurface proof asserted | Q, excluded | arXiv 2312.09268, 2023 | "We deduce the Hodge conjecture for smooth projective hypersurfaces" |

Grades: Q 4, E 1. Usable claims: 3. Excluded: 1.

## Why the Atiyah-Hirzebruch row is E and not Q

The title check passed, so the paper exists and is the right paper. The abstract is
not exposed, so nothing about its content can be quoted. Under v1 that row would have
carried a memory-written sentence about torsion classes next to a fetched status, and
looked exactly like the quoted rows. Under v2 it is an existence record, the claim is
not affirmed, and the ledger counts it as unusable. If a quotable source for the
torsion obstruction is wanted, it has to be a document that actually says it, such as
the counterexample paper or a survey that states the history.

## Why the 2023 preprint is quoted and still excluded

Quoting it proves the paper says what it says. It does not make the proof correct.
No refereeing, no replication, no independent check was fetched. The record therefore
carries grade Q with `excluded_from_evidence: true` and a written reason. The ledger
counts 4 quoted records and 3 usable ones, which is the whole point of keeping the
two numbers apart.

## What this cycle does not claim

No progress on Hodge. No endorsement of the 2023 or 2025 preprints. No statement
about the rational Hodge conjecture in codimension two beyond the fact that a 2021
survey calls the general problem open.

## v1 rows carried over: none

The ledger's `blocking_gap` and `transmuted_approach` strings for Hodge are still v1
analysis. They are now labelled as such in the ledger evidence block, under
`unsourced_fields`, rather than sitting beside quoted records as if they had equal
standing. Replacing them with sourced statements is the next Hodge cycle, not this
one.

## Licence and status

arXiv and Crossref API metadata, fetched 2026-11-17, HTTP 200 per record. No full
texts redistributed. The excluded preprint is stored as metadata and one quoted
sentence only.
