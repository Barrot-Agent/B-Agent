<!-- SYNTHETIC EXAMPLE: the issue URL is a placeholder. Replace it and rerun your own tests before using this as a PR body. -->

## What changed

Adds the paid-issue kit: ledger scoring, PR packaging, and the 120-minute timebox.

- Added ledger.py with hard gates, effective-rate scoring, and a CSV ledger.
- Added pack.py with a PR body builder and an evidence-pack validator.
- Added timebox.py with six ordered phases totalling 120 minutes.

## Why

Issue: https://github.com/example/project/issues/42

The kit needs a tested way to decide which paid issues are worth attempting and to package proof without unverifiable claims.

## Proof

Command: `python3 -m unittest discover -s tests`
Result: Ran 76 tests in 0.095s, OK

## Risk and rollback

Risk: The default thresholds are opinionated and may reject legitimate work; they are configurable in Policy.
Rollback: Delete the paid_issue_kit package and the tests; no other module imports it.

## Checklist

- [x] Full suite run after the last edit
- [x] No unrelated files changed
- [x] Every new module has tests
