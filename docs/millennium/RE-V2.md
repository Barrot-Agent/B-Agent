# Reverse-engineering v2: what v1 actually did, and what replaced it

Date: 2026-11-17. Baseline: HEAD 5b47ac5c5. Companion code: scripts/re_v2.py,
tests/test_re_v2.py, data/millennium/claims/p_vs_np.json.

## 1. Audit of the last two cycles

Cycle 01, the Millennium database pass, ran these steps in this order:

1. Listed data/millennium*, read one problem file in full, skimmed the overview.
2. Grepped for millennium references, counted records in the three research bundles.
3. Wrote scripts/millennium_audit.py with two dictionaries hardcoded: BLOCKING_GAP
   and TRANSMUTED_APPROACH. Both were written from memory, not from a source.
4. Fetched five preprints and four verification documents by identifier, and stored
   title and first-submission date for each.
5. Wrote CYCLE-01.md, including a "what it contributes" column for each preprint.
   That column came from memory and sat next to a fetched status, sharing its
   apparent authority.
6. Gated the whole thing with four tests. All four checked shape: fields present,
   statuses spelled right, forbidden words absent. None checked content.

Cycle 02, the Phoenix pass, was different in kind: it measured a restore, deliberately
broke a file and watched the audit fail, and counted commits against recorder entries.
No citation was involved, and nothing in it was invented. That contrast matters: the
work that lied was the work that paraphrased sources from memory.

## 2. The pattern, extracted

v1 was not reverse engineering. It was recall, with the network used as a notary.

    recall identifier -> fetch metadata -> narrate content -> gate on schema

Every step except the fetch is a memory operation, and the fetch only proved the
identifier existed. Reversing v1 therefore reverses four assumptions: that a recalled
identifier is correct, that existence implies content, that a schema gate is an
evidence gate, and that a sampled row set is a representative one.

## 3. Where v1 fails, with today's evidence

| Failure | Evidence from this session |
|---|---|
| Recalled identifiers are wrong | arXiv 0801.4877 was recalled as the algebrization paper; it is "Transseries for beginners". DOI 10.1145/1462153.1462156 was recalled as algebrization; it is Valiant, "Evolvability". Two of three memory identifiers were wrong. |
| Existence is not content | Cycle 01 stored no abstracts at all. Every "contributes" sentence was unverifiable from the record it sat beside. |
| Schema gate passes anything | Four tests were green while every content claim was unsourced. Shape was checked; truth was not. |
| Convenience sampling | Four of six open problems were left "none fetched" because those were the rows I could not recall quickly, not because they were less important. |
| No falsifier | No row stated what would kill it, so no row could ever go red. A claim that cannot fail is not a claim. |
| The metric rewarded the flaw | Cycle 02's stop rule measured how many rows gained a citation. A wrong DOI raises that count. |

Where it hallucinates: at the seam between a fetched identifier and a paraphrased
sentence. That seam is invisible in the artifact, which is why it survived a test
suite. Where it stops: at the first document that agrees with what it already
believed. It never looks for the correction, and never checks that the document says
the specific thing being attributed to it.

## 4. Reverse-engineering v2: TRACE-5

    T  Target      write the claim as a falsifiable sentence, plus the title fragment
                   the source must resolve to. Written before searching.
    R  Retrieve    by query or DOI. Never by an identifier recalled from memory.
    A  Assert-quote  the quote must be a literal substring of the retrieved text.
                   No quote, no claim. This is the whole method.
    C  Cross-check   a second, independent document, or the record says "single".
    E  Exit        falsifier, what the source does not show, and an evidence grade.

Grades: Q quoted primary, E existence only (content not verified), X rejected
mismatch. Only Q may support a claim.

Enforcement is code, not discipline. scripts/re_v2.py will not emit Q unless the
quote matches the retrieved abstract, and it refuses to emit Q if the title does not
contain the expected fragment. `python3 scripts/re_v2.py check` re-validates the
written file offline, so a record cannot drift away from its source after the fact.
The two wrong identifiers are kept in the file as permanent negative controls, with
grade X, so the check is demonstrated firing rather than asserted to work.

## 5. Applied to the Millennium ledger: the P vs NP row

| Record | Grade | Source |
|---|---|---|
| Relativization: oracles exist with P^A = NP^A and with P^B != NP^B | Q | Baker-Gill-Solovay, SIAM J. Comput. 1975, doi 10.1137/0204037 |
| Algebrization: a third barrier beyond relativization and natural proofs; P vs NP needs non-algebrizing techniques | Q | Aaronson-Wigderson, ACM Trans. Comput. Theory 2009, doi 10.1145/1490270.1490272 |
| Attribution of the barrier to Aaronson and Wigderson | Q | arXiv 2511.14038, secondary document |
| Natural proofs | E | Razborov-Rudich, JCSS 1997, doi 10.1006/jcss.1997.1494 |
| Recalled arXiv id | X | resolved to Transseries for beginners |
| Recalled DOI | X | resolved to Evolvability |

Two sentences are quoted from the primary texts and are now usable. The natural
proofs row is existence only: the publisher exposes no abstract, so the claim about
what Razborov and Rudich prove stays unaffirmed in this repo. That is the honest
outcome, and v1 would have hidden it.

Consequence for the ledger: data/millennium/ledger.json now carries an `evidence`
block for P vs NP, with grade counts and the rule that only Q records may support a
claim. At the time of writing the other rows had no evidence block, which is a
visible statement rather than an omission; Hodge has since gained one under the same
method.

## What v2 still cannot do

- It cannot tell whether a quoted sentence is true, only that the source said it.
- It cannot choose which row deserves fetching. Sampling bias survives.
- It fails closed on paywalled abstracts, which turns real results into E records.
  That is the right failure, but it means v2 under-reports.
- A secondary cross-check establishes attribution, not correctness.

## Licence and status

Crossref and arXiv API metadata, fetched 2026-11-17, HTTP 200 per record, stored in
data/millennium/claims/p_vs_np.json. No full texts redistributed.
