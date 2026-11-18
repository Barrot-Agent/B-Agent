# Examples

Two kinds of file live here:

- **Input examples** (`candidates.json`, `pr_plan.json`) are synthetic. The
  repositories are `example/*` and do not exist. Amounts, stars, and dates are
  invented to exercise every branch of the scorer.
- **Generated examples** (`ledger.csv`, `PR_BODY.md`, `EVIDENCE_PACK.md`) are
  real output of the shipped code. `PR_BODY.md` carries an HTML comment saying
  it is synthetic; the test output inside it is the real output of this kit's
  suite at generation time.

Nothing here is a real bounty, a real PR, or a real payment.

## Regenerate

```bash
cd deliverables
python3 -m unittest discover -s tests
python3 -m paid_issue_kit score --input examples/candidates.json \
  --out examples/ledger.csv --now 2026-11-18T12:00:00+00:00
python3 -m paid_issue_kit pr --plan examples/pr_plan.json --out-dir examples
```

The fixed `--now` makes the repo-idle gate reproducible. Without it, a candidate
that is 119 days idle today becomes a NO-GO next week, which is the correct
behaviour but a bad example.
