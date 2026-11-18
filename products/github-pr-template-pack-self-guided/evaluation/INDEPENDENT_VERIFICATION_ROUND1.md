# Independent verification — round 1 (superseded)

Status: **SUPERSEDED**. Kept as an audit trail. The current report is
`evaluation/INDEPENDENT_VERIFICATION.md`.

- Verifier: independent OpenCode subagent, not the builder.
- Date: 2026-11-18, ~06:40–07:05 UTC.
- Target: branch `phase1/digital-downloads-paid-issue-pr`, working tree.
- Verdict: **FAIL** on claim integrity; code and gate passed.

Findings that blocked the verdict:

1. `research/EVIDENCE_LOG.md` E-13 said the 30% marketplace rate on $9 leaves
   $5.80. Correct: $6.30, matching `PRICING.md`.
2. Fee range in `MARKET_RESEARCH.md` and `PRODUCT_SPECIFICATION.md` said
   11.3%–15.6% while also citing 30% marketplace; the range omitted the 30% case.
3. `PRODUCT_SPECIFICATION.md` and `marketing/PROMOTIONAL_COPY.md` said the other
   94 of 100 issues were "noise, stale, or unpaid". The evidence log explicitly
   does not support that.
4. Three documents called the test log "committed" when no commit existed.
5. The captured `evaluation/logs/release-gate.log` said 50 files while the live
   gate said 52.
6. `PRICING.md` used a 45-minute support break-even; at $34.60 net and $50/hour
   the figure is 41.5 minutes.
7. The ledger accepted a well-formed fake URL as GO; the evidence validator
   accepted a non-URL. The kit is offline and cannot check existence.
8. The PR validator accepted square-bracket placeholders although the template
   said a leftover bracket is rejected.
9. `verify_release.py` did not require `deliverables/README_FIELD.md`.
10. Two minor overbroad sentences in `QUALITY_CHECKLIST.md` (all URLs fetched;
    eight files) and an unexplained platform-count overlap.

What passed: 74 tests, release gate 9/9, all six market numbers matched the JSON
and a live re-query, all ten capabilities PROPOSED, no merge/publish/transaction,
Field manifest resolved.

Disposition: every finding was repaired or documented as a limit; see
`evaluation/IMPROVEMENT_LOG.md` and the current verification report.
