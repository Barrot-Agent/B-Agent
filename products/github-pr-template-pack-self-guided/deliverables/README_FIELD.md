# Paid-issue field kit

The $9 tier: the forms and the rules, no Python.

Use it to decide whether a paid issue is worth attempting, to price the work
after fees, and to package a PR that answers a reviewer's questions before they
ask. Python 3.10+ is not required for this tier.

## What is inside

```
templates/issue_intake.md      one-page intake; fill it before writing code
templates/decision_rules.md    nine hard gates and the scoring formula
templates/bounty_ledger.csv    ledger header for a spreadsheet
templates/pr_body.md           the five sections a reviewer needs
templates/evidence_pack.md     claim, evidence, and limit for each statement
templates/timebox_card.md      the six phases and the stop rules, printable
```

## How to use it

1. Copy `templates/issue_intake.md` and fill every field. If the amount, the
   acceptance criteria, or the escrow status is unknown, write `UNKNOWN` and do
   not start.
2. Apply `templates/decision_rules.md`. Any failed hard gate is a NO-GO. Record
   the failing gate, not a feeling.
3. Put candidates in a spreadsheet using the header in
   `templates/bounty_ledger.csv`.
4. Run the six phases on `templates/timebox_card.md`. If the six phases cross
   120 minutes, write `CLAIM BROKEN` and keep the row.
5. Fill `templates/pr_body.md` and `templates/evidence_pack.md`. Every claim
   needs evidence and a stated limit.

## Honest limits

- A stated bounty is not escrow. The form asks; it cannot verify.
- The 120 minutes cover your six phases, not maintainer review, CI, or payment.
- The effort estimate is yours. A gate cannot detect optimism.
- No tool can see a CLA, a hidden reviewer, or a maintainer on leave.
- The pack does not find bounties, open PRs, or promise payment.
- No validator ships in this tier. You check that the issue URL exists and that
  the issue is real; the forms cannot do it for you.

## License

See `LICENSE_AND_TERMS.md` in this package root. The $9 tier covers personal use
of the templates. No resale of the files.
