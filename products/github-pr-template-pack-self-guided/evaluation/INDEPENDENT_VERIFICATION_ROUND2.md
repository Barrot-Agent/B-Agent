# Independent Verification — round 2 (superseded)

Status: **SUPERSEDED**. This round missed the claim-integrity defects found in
round 1. It is kept only for the audit trail. The current report is
`evaluation/INDEPENDENT_VERIFICATION.md`.

# Independent Verification — Ship a Paid-Issue PR in 2 Hours

- **Verifier identity:** OpenCode general subagent, independent of builder
- **Date:** 2026-11-18
- **Product:** `products/github-pr-template-pack-self-guided`
- **Branch under test:** `phase1/digital-downloads-paid-issue-pr`
- **Method:** Ran the release gate, unit suite, negative control, measurement
  cross-check, capability-ledger scan, delivery-manifest existence check, and
  git history/status inspection. No source files were edited. This report is
  the only file written.

## 1. Release gate

```
$ cd products/github-pr-template-pack-self-guided && python3 evaluation/verify_release.py
release gate: github-pr-template-pack-self-guided
[PASS] required files: 38/38 present
[PASS] capability ledger: 10 PROPOSED, 0 PROVEN/ACTIVE
[PASS] test suite: Ran 74 tests, exit 0
[PASS] flake8: clean
[PASS] marketing claims: 4 files, 0 banned phrases
[PASS] secret scan: 52 files, 0 findings
[PASS] version: 1.0.0 in package, changelog match=True
[PASS] pricing arithmetic: net direct {9: 7.6, 19: 16.6, 39: 34.6}
[PASS] test count consistency: no stale '73 tests'
RESULT: PASS (9 checks, 0 failed)
exit:0
```

## 2. Unit test suite

```
$ cd products/github-pr-template-pack-self-guided/deliverables && python3 -m unittest discover -s tests 2>&1 | tail -5
..........................................................................
----------------------------------------------------------------------
Ran 74 tests in 0.242s

OK
exit:0
```

## 3. Negative control

```
$ cd products/github-pr-template-pack-self-guided/deliverables && python3 -m paid_issue_kit pr --plan ../evaluation/fixtures/bad_plan.json; echo "exit:$?"
BLOCKED: unverifiable claim present: guarantee language
exit:1
```

The gate rejects the bad plan and returns nonzero, as required.

## 4. Measurement cross-check

```
$ cd products/github-pr-template-pack-self-guided && python3 -c "import json; d=json.load(open('research/market_measurement.json')); print(d['bounties']['issues_fetched'], d['bounties']['issues_with_stated_amount'], d['bounties']['amount_usd']['median'], d['merge_latency']['pooled']['merged_sampled'], d['merge_latency']['pooled']['median_hours'], d['merge_latency']['pooled']['pct_merged_within_2h'])"
100 6 525.0 112 1.11 52.7
```

| Metric | JSON | MARKET_RESEARCH.md | SALES_COPY.md |
|---|---|---|---|
| Issues fetched | 100 | 100 | 100 |
| Issues with stated amount | 6 | 6 of 100 (6.0%) | 6 |
| Median stated amount (USD) | 525.0 | $525 | not cited |
| Merged PRs sampled | 112 | 112 | 112 |
| Pooled median hours | 1.11 | 1.11 hours | 1.11 hours |
| Share merged within 2h | 52.7 | 52.7% | 52.7% |

**Mismatches: none.** Every number cited in both documents matches the JSON.
The $525 median is absent from SALES_COPY.md, which is an omission, not a
contradiction.

## 5. Capability ledger

```
$ grep -c '| PROPOSED |' products/github-pr-template-pack-self-guided/CAPABILITY_LEDGER.md
10
$ grep -nE '\| (ACTIVE|PROVEN) \|' products/github-pr-template-pack-self-guided/CAPABILITY_LEDGER.md || echo "none active/proven"
none active/proven
```

No capability is overstated as ACTIVE or PROVEN.

## 6. DELIVERY_REQUIREMENTS.md section 2 path check

Literal package paths checked relative to the product directory:

```
OK   deliverables/README_FIELD.md
OK   LICENSE_AND_TERMS.md
OK   deliverables/CHANGELOG.md
MISS templates/issue_intake.md
MISS templates/decision_rules.md
MISS templates/pr_body.md
MISS templates/evidence_pack.md
MISS templates/bounty_ledger.csv
MISS templates/timebox_card.md
OK   deliverables/README.md
OK   deliverables/run_selftest.sh
MISS TEAM_LICENSE.txt
kit py: 6
tests py: 4
templates: 0
MISS examples/
```

Interpretation: section 2 describes the **packaged** layout, not the repo
tree, and it explicitly marks README sources. All six forms exist at
`deliverables/templates/`, and examples exist at `deliverables/examples/`.
`TEAM_LICENSE.txt` is generated at packaging time and is therefore not expected
in the repo. **No source artifact is missing**, but the literal section-2 paths
(`templates/*`, `examples/*`, package-root `README.md`) do not exist at the
product root. Packaging output was not produced or verified here.

## 7. Git history and status

```
$ git -C /root/barrot/Barrot-Agent log --oneline main..HEAD
(no output)
$ git -C /root/barrot/Barrot-Agent status --short | head -5
AM products/github-pr-template-pack-self-guided/evaluation/logs/negative-control.log
A  products/github-pr-template-pack-self-guided/evaluation/logs/phases.log
A  products/github-pr-template-pack-self-guided/evaluation/logs/release-gate.log
A  products/github-pr-template-pack-self-guided/evaluation/logs/score-smoke.log
AM products/github-pr-template-pack-self-guided/evaluation/logs/tests-verbose.log
```

Additional diagnostic (same step, to explain the empty log):

```
$ git rev-parse --abbrev-ref HEAD
phase1/digital-downloads-paid-issue-pr
$ git rev-list --left-right --count main...HEAD
0	0
$ git log --oneline -3
c54447c32 money: probe bounty platforms for anonymous amounts, 0 of 9 answer
b41914a61 recorder: hunter cycle, 8 false-positive rows and the scheduled-write split
d04caaa5c loop: 7c, scheduled hunter cannot write, workflow_run publishes
$ git status --short | wc -l
24
```

The branch has **zero commits not already on main**, while 24 working-tree
changes remain uncommitted. The staged content under test exists only in the
dirty working tree, not as a reviewable branch delta.

## FAILURES FOUND

1. **Branch state contradicts the staged-release premise.** `main...HEAD` is
   `0 0` and `git log main..HEAD` is empty: the named branch contains no commits
   absent from main. The 24 uncommitted files are the actual staged content.
   This does not break the product, but a reviewer cannot see a branch diff, and
   "merge to main" would be a no-op for committed history.
2. **Section 2 manifest paths are not materialized.** Literal paths
   `templates/*` and `examples/*` do not exist at the product root; the package
   layout has not been built. Sources exist under `deliverables/`. This is a
   packaging gap, not a missing source file.

No gate failure, test failure, arithmetic error, ledger overstatement, secret
finding, or measurement mismatch was found.

## UNVERIFIED CLAIMS

- **Packaging output:** no $9/$19/$39 archive was built, so the packaged
  README placement, absence of Python from the Field Kit, and generated
  `TEAM_LICENSE.txt` were not observed.
- **Measurement provenance:** the six numbers are internally consistent across
  JSON, research, and sales copy, but raw GitHub issue/PR records were not
  re-fetched or independently recomputed.
- **Demand and sales:** no sales, revenue, or demand claim was tested. The
  product itself is marked STAGED / not for sale.
- **Runtime behavior beyond the fixture:** only the single bad-plan negative
  control was run; other documented failure modes were not independently
  exercised.

## VERDICT

**PASS WITH CAVEATS**

The release gate, 74-test suite, negative control, capability honesty, pricing
arithmetic, and all cited measurements check out. The caveats are the empty
branch delta (work is uncommitted) and the unbuilt package layout; neither
indicates a false claim or a broken deliverable, but both must be resolved
before this can be called a reviewable, shippable branch.

Gate line: `RESULT: PASS (9 checks, 0 failed)`

I did not modify source files, merge to main, publish, change prices, or run a transaction.
