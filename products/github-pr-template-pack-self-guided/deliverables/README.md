# Paid-issue kit

A small, dependency-free toolkit for the paid-issue workflow:

1. Decide which issues are worth attempting (`score`).
2. Keep a 120-minute phase gate (`timebox`).
3. Package a PR body and an evidence pack that reject unverifiable claims (`pr`).

Python 3.10 or newer. Standard library only. No account, no API key, no network
call. The tools work offline. The market measurement script mentioned in the product
page is not part of this package; it is an internal research tool.

## Quickstart

Run these from this folder (the package root). In the source tree, that is
`deliverables/`.

```bash
python3 -m unittest discover -s tests          # 76 tests, OK
python3 -m paid_issue_kit score --input examples/candidates.json
python3 -m paid_issue_kit pr --plan examples/pr_plan.json --out-dir /tmp/pr
python3 -m paid_issue_kit timebox start --state /tmp/run.json --mission "issue 42"
python3 -m paid_issue_kit timebox checkpoint --state /tmp/run.json --phase triage
python3 -m paid_issue_kit timebox status --state /tmp/run.json
```

## Commands

### `score`

Reads a JSON list of candidates and writes a CSV ledger, best score first.

```bash
python3 -m paid_issue_kit score --input examples/candidates.json --out ledger.csv
```

Output summary for the shipped example:

```json
{
  "total": 5,
  "go": 1,
  "no_go": 4,
  "best_go_hourly_usd": 250.0,
  "go_issue_ids": ["ex-101"]
}
```

Candidate fields:

| Field | Required | Meaning |
|---|---|---|
| `issue_id` | yes | Your short id |
| `url` | yes | Issue-specific URL |
| `repo` | yes | `owner/name` |
| `title` | yes | Issue title |
| `amount_usd` | no | Stated amount; `null` means none stated |
| `acceptance_criteria` | yes | Quoted definition of done |
| `repo_stars` | yes | Integer |
| `repo_pushed_at` | yes | ISO date |
| `archived` | no | Boolean |
| `escrow_verified` | no | Boolean; only true if you saw escrow |
| `platform` | no | `opire`, `algora`, or empty |
| `labels` | no | List |
| `comments` | no | Integer |
| `effort_hours` | no | Default 4; the default policy rejects over 3 |
| `payout_fee_fraction` | no | 0.0-1.0 |
| `expenses_usd` | no | Number |

Gates and formula: `templates/decision_rules.md`.

### `timebox`

Six phases, 120 minutes, order enforced. State is a JSON file you can inspect.

```bash
python3 -m paid_issue_kit phases
```

`status` reports `CLAIM HOLDS` only when all six phases are complete inside 120
minutes. It also reports `CLAIM BROKEN`. The claim excludes maintainer review,
merge, and payment; the tool says so in every status block.

### `pr`

Builds `PR_BODY.md` and `EVIDENCE_PACK.md` from a plan, then validates both.
It exits 1 and prints `BLOCKED:` lines when anything fails.

What it rejects:

- a missing required section, issue link, test command, result, or rollback
- fewer than two checked checklist items
- placeholder text (`TODO`, `TBD`, `FIXME`, `<insert`)
- unverifiable claims (`guaranteed`, `100%`, `zero risk`, `production-ready`,
  `bulletproof`, `never fails`, `fixes everything`)
- an evidence pack claim without evidence or without a stated limit
- a non-zero exit code presented as proof

## Files

```
paid_issue_kit/     the package (ledger, pack, timebox, cli)
tests/              76 unittest cases, no third-party runner
templates/          intake, PR body, evidence pack, decision rules, timebox card, ledger CSV
examples/           synthetic candidate set and generated outputs
run_selftest.sh     one-command test run
```

## Honest limits

- The score is a screening order, not a probability of payment.
- A stated bounty is not escrow. `escrow_verified` is only true if a human saw
  escrow; the tool cannot verify it.
- The timebox measures your phases, not a maintainer's review speed.
- No tool can see a CLA, a hidden second reviewer, or a maintainer on leave.
- The tests use synthetic fixtures. No live bounty was submitted, claimed, or
  paid as part of this build.
- Link shape is checked, not existence. The kit makes no network call, so a
  well-formed but nonexistent issue URL can still pass.
- Placeholder detection covers `TODO`, `TBD`, `FIXME`, and `<insert`; it does not
  reject every square-bracket text.

## Test result

```
$ python3 -m unittest discover -s tests
Ran 76 tests in 0.095s

OK
```

Environment: Python 3.13.5 on Linux, standard library only. Recorded
2026-11-18. Re-run it on your machine; the count is the check, the timing is not.

## License

See `LICENSE_AND_TERMS.md` in the package root. The $9 tier covers personal use of the templates;
the $19 tier adds this toolkit; the $39 tier adds internal team sharing. No
resale of the files.
