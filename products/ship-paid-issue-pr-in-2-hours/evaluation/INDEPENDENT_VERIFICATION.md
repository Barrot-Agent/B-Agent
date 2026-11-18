# Independent verification (round 2) — ship-paid-issue-pr-in-2-hours

**Verifier:** Independent OpenCode subagent (DeepSeek V4.1 Flash Free). Not the builder.
**Date:** 2026-11-18 UTC.
**HEAD:** `b4515d42e2a03809722e883537579dc98722cbdc` (`b4515d42e`), branch `phase1/digital-downloads-paid-issue-pr`, 1 commit ahead of `main` (`c54447c32`).
**Working tree:** clean (0 modified/staged/untracked entries).
**Method:** read-only inspection and execution. No source file edited. The only file written is this report. No commit, push, merge, publish, price change, or transaction.

## Exact outputs

### 1. Release gate (`python3 evaluation/verify_release.py`, exit 0)

```
release gate: ship-paid-issue-pr-in-2-hours
[PASS] required files: 39/39 present
[PASS] capability ledger: 10 PROPOSED, 0 PROVEN/ACTIVE
[PASS] test suite: Ran 76 tests, exit 0
[PASS] flake8: clean
[PASS] marketing claims: 4 files, 0 banned phrases
[PASS] secret scan: 54 files, 0 findings
[PASS] version: 1.0.0 in package, changelog match=True
[PASS] pricing arithmetic: net direct {9: 7.6, 19: 16.6, 39: 34.6}
[PASS] test count consistency: no stale '73 tests'
RESULT: PASS (9 checks, 0 failed)
```

### 2. Test suite

`python3 -m unittest discover -s tests -v` → `Ran 76 tests in 0.636s` / `OK`. Per module: ledger 24, pack 26, timebox 16, cli 10 = 76. `./run_selftest.sh` exits 0.

### 3. Bad-plan fixture (`evaluation/fixtures/bad_plan.json`)

```
BLOCKED: unverifiable claim present: guarantee language
EXIT=1
```

### 4. Adversarial probes

```
non-http issue_url  -> ['issue_url is not an http(s) URL']
bracket placeholder -> ['placeholder bracket present: [One paragraph. What does the diff do, in plain language?]']
valid-shape fake URL-> EVIDENCE_FAKE_SHAPE: []   LEDGER_FAKE_SHAPE: GO []
```

The fake-URL pass is expected: the kit makes no network call and checks link shape, not existence. That limit is now stated in `deliverables/README.md` (lines 118–119), `marketing/FAQ.md` (lines 19, 64–65), and in `templates/pr_body.md`.

### 5. Capabilities and repo state

```
capability rows: 10, statuses {'PROPOSED': 10}, non_proposed: NONE
commits ahead of main: 1; merge commits: 0; HEAD parents: 1
remote branch: 0; HEAD checkout/product URL: none (only https://gumroad.com/pricing)
git-tracked product files: 54; on-disk files (no __pycache__): 54
```

## Round-1 findings

| # | Finding | Status | Evidence |
|---|---|---|---|
| 1 | E-13 marketplace net $5.80 instead of $6.30 | **FIXED** | `EVIDENCE_LOG.md:232` now `$6.30`, matching `PRICING.md:52` |
| 2 | Fee range omitted 30% marketplace | **FIXED** | `MARKET_RESEARCH.md:131` and `PRODUCT_SPECIFICATION.md` say 11.3–15.6% direct, 30% marketplace |
| 3 | Unsupported "rest were noise, stale, or unpaid" | **FIXED** | Removed from spec and marketing; only 94-of-100 measurement remains |
| 4 | Logs called "committed" while uncommitted | **FIXED** | `b4515d42e` contains all five `evaluation/logs/*.log`; "committed" wording is now true. Spec says "captured log"; TEST_RESULTS:7 still says "committed", which is now accurate |
| 5 | Captured `release-gate.log` stale | **NOT FIXED** | `git show HEAD:./evaluation/logs/release-gate.log` still reads `38/38`, `Ran 74 tests`, `secret scan: 50 files` vs fresh `39/39`, `76`, `54` |
| 6 | Support break-even 45 min arithmetically wrong | **FIXED** | `PRICING.md:65` now states a formula, not a fixed 45-minute claim |
| 7 | URL existence not checked / not documented | **DOCUMENTED** (partial) | `pack.py` rejects non-http; README and FAQ state "link shape, not existence". `README_FIELD.md` has no such note (it ships no validator, so the risk is lower) |
| 8 | Bracket placeholders accepted while template says reject | **FIXED** | Regex rejects `[...]` with space or `...`; new regression test in `test_pack.py`; template wording says "Replace every placeholder" and "not a general square-bracket linter" |
| 9 | `README_FIELD.md` absent from gate | **FIXED** | `REQUIRED_FILES` has 39 entries including `deliverables/README_FIELD.md`; gate reports 39/39 |
| 10 | QUALITY_CHECKLIST wording and platform overlap | **FIXED** | Checklist says "eight required + CAPABILITY_LEDGER.md" and flags S15 local; `MARKET_RESEARCH.md:40-41` explains 9 distinct issues / 15 platform matches |

## Remaining caveats

1. **Stale gate log (finding 5).** The file is committed but was not regenerated after the count changes. A reader of the log sees `74 tests` and `50 files` where the live tree has `76` and `54`. Fix: regenerate and amend, or drop the log from the release evidence.
2. **`README_FIELD.md` lacks the URL-existence note.** The Field tier ships no validator, so it is a documentation gap at most.
3. **Fake but well-formed URLs pass.** Confirmed and documented; not a defect under the stated offline design.
4. **This report itself changes the scan count.** It adds one file, so the next gate run will say 55 scanned files.
5. **Demand, payouts, and the 2-hour buyer outcome remain unmeasured.** No sales, accepted bounty, or end-to-end buyer run exists. The docs state this limit.

## Verdict

**PASS WITH CAVEATS**

9 of 10 round-1 findings are fixed and the 10th (URL existence) is documented as a limit. Code, tests, gate, capability ledger, and repo state are consistent. The one unfixed item is the committed `release-gate.log`, which contradicts the live gate on test count and scan count; that log must be regenerated before it is used as release evidence.

## Signed statement

I did not modify any source file. I did not commit, push, merge, publish, change a price, or run a transaction. The only file I wrote is `evaluation/INDEPENDENT_VERIFICATION.md`. All outputs above are from commands run against the working tree at HEAD `b4515d42e`.

Signed: Independent Verifier (OpenCode subagent, DeepSeek V4.1 Flash Free) — 2026-11-18
