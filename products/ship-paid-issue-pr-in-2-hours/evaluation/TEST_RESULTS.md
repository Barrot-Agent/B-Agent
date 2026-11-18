# Test results

Run date: 2026-11-18. Machine: Linux, Python 3.13.5, standard library only.
Status: **PASS** for the automated suite and the release gate. Independent
verification is **PENDING** and is not claimed.

The raw verbose log is included at `evaluation/logs/tests-verbose.log`.

## 1. Full suite

```bash
cd deliverables
python3 -m unittest discover -s tests
```

```
Ran 76 tests in 0.095s

OK
```

Exit code 0. 76 test lines matched ` ... ok`; zero failures, zero errors, zero
skips in the verbose log. Timings vary between runs on the same machine
(0.095s-0.482s observed); the count is the invariant, the time is not.

| Module | Tests | Covers |
|---|---|---|
| `test_ledger.py` | 24 | gates, arithmetic, ordering, CSV, input validation |
| `test_pack.py` | 26 | PR builder, all validator failures, evidence claims, optional note |
| `test_timebox.py` | 16 | phase table, order, verdicts, persistence, reporting |
| `test_cli.py` | 10 | `score`, `pr`, `timebox`, `phases`, exit codes 0/1/2 |
| **Total** | **76** | |

The one-command runner was also exercised:

```bash
./run_selftest.sh
Ran 76 tests in 0.201s
OK
```

## 2. Negative controls

A test that only shows the happy path proves little. These controls show the
gates actually reject.

| Control | Command or test | Observed |
|---|---|---|
| PR body with a claim that cannot be supported | `python3 -m paid_issue_kit pr --plan ../evaluation/fixtures/bad_plan.json` | exit 1, `BLOCKED: unverifiable claim present: guarantee language` |
| Evidence pack with a non-zero exit code | `test_failing_exit_code_is_rejected` | rejected: `exit_code is not 0; a failing run cannot be presented as proof` |
| Evidence claim without a limit | `test_claim_without_limit_is_rejected` | rejected: `claim 1 missing limit` |
| Issue with no amount | `test_missing_amount_is_no_go` | `NO-GO`, reason `no stated amount` |
| Repo idle 322 days | `test_stale_repository` | `NO-GO`, reason `idle for more than 120 days` |
| $100 for 10 hours | `test_low_effective_rate_blocks` | `NO-GO`, reason `effective rate below 30 USD/hour` |
| 10-hour task under a 2-hour product | example run, `ex-105` | `NO-GO`, reason `effort above 3 hour cap` |
| Out-of-order timebox phase | `test_out_of_order_checkpoint_rejected` | `ValueError: expected 'triage'` |
| Section name only in prose | `test_section_name_inside_prose_does_not_count` | `missing section: ## Proof` |

Negative-control log: `evaluation/logs/negative-control.log`.

## 3. CLI smoke

```bash
python3 -m paid_issue_kit score --input examples/candidates.json \
  --out /tmp/ledger.csv --now 2026-11-18T12:00:00+00:00
```

```json
{
  "total": 5,
  "go": 1,
  "no_go": 4,
  "best_go_hourly_usd": 250.0,
  "go_issue_ids": ["ex-101"]
}
```

The generated ledger has one GO row and four NO-GO rows, each with a reason.
Full file: `deliverables/examples/ledger.csv`. Log:
`evaluation/logs/score-smoke.log`.

```bash
python3 -m paid_issue_kit phases
```

```
phase        minutes  purpose
triage            15  Read the issue. Confirm amount, acceptance criteria, and one-PR scope.
reproduce         20  Reproduce the failure or restate the requirement in a failing test.
patch             40  Smallest change that makes the test pass. No unrelated edits.
test              25  Run the suite. Capture command, exit code, and output.
package           15  Write the PR body and evidence pack. Check every claim.
submit             5  Open the PR, link the issue, and record the URL.
total            120
```

The timebox was exercised end to end with a real state file:

```
Mission: example issue 42
Verdict: IN PROGRESS (0.01 of 120 minutes)
Claim scope: six phases inside 120 minutes; merge and payment are excluded
Done: triage
Next: reproduce
```

## 4. Market measurement reproducibility

```bash
cd research
python3 measure_market.py --out market_measurement.json
```

Retrieved 2026-11-18T06:09:03Z. Key values:

| Measure | Value |
|---|---|
| `label:bounty is:issue is:open` | 5,319 |
| `algora in:body is:issue is:open` | 559 |
| `"paid" "pull request" in:body is:issue is:open` | 7,570 |
| 100-issue sample with a stated amount | 6 (6.0%) |
| Stated amount median / range | $525 / $450-$600 |
| 112 merged PRs, pooled median open-to-merge | 1.11 hours |
| Merged within 2 hours | 52.7% |

This is live data. A re-run will produce different counts. The JSON snapshot is
the snapshot the product cites.

## 5. Release gate

```bash
python3 evaluation/verify_release.py
```

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

## 6. What was not tested

- **No live bounty was claimed, started, or paid.** No GitHub write action of any
  kind was performed by the product. The research script is read-only.
- **No real PR was opened.** The PR body and evidence pack are generated from
  synthetic plans.
- **No payment, checkout, refund, or tax flow was tested.** No store listing
  exists.
- **Windows and macOS were not tested.** Only Linux, Python 3.13.5. Python 3.10+
  is the stated requirement; 3.10, 3.11, and 3.12 were not executed.
- **No line-coverage tool was run.** Coverage is argued by behaviour, mapped in
  `PRODUCT_SPECIFICATION.md` section 5. A coverage percentage is not claimed.
- **No load or performance test.** The suite finishes in under a second on this
  machine; that is an observation, not a benchmark.
- **No independent verification yet.** The builder ran these tests. Stage 7
  requires a separate verifier; see `PRODUCTION_WORKFLOW.md` section 5.

## 7. Verdict

Automated verification: PASS. The product is functional, the gates reject the
cases they claim to reject, and the documented numbers match the
artifacts.

Independent verification: PENDING. This is the honest state, not a formality.
