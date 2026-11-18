# Sales copy

Approved copy for the product page. Every number here traces to a file in this
directory. Do not add a claim that is not in `research/EVIDENCE_LOG.md`.

---

## Headline

**Ship a Paid-Issue PR in 2 Hours — GitHub Template Pack**

## Subhead

A decision ledger, a 120-minute phase gate, and a PR package that answers the
reviewer's questions before they ask. Templates for the work. Python tools for
the decisions. No account, no API key, no network call.

## Who this is for

You can read a stack trace, run a test suite, and open a pull request. You want
to turn that into paid open source work without spending a weekend guessing
which issues are real.

## Who this is not for

- Anyone looking for a list of live bounties. The pack does not contain one.
- Anyone looking for a bot that opens PRs. It does not do that.
- Anyone who needs certainty of payment. A stated bounty is not escrow, and the
  pack says so on the first page.

## The problem, measured

I sampled 100 open GitHub issues carrying the `bounty` label on 2026-11-18.
Only **6** stated a dollar amount. Three carried spam markers. A label is not an
offer.

The same day I measured 112 merged pull requests across three public
repositories. The pooled median open-to-merge time was **1.11 hours**, and
**52.7%** merged within two hours. Small, scoped PRs can clear review in one
session. Your repository will differ, and the pack does not pretend otherwise.

## What is inside

### Field Kit — $9

- `issue_intake.md`: the seven stop rules, on one page
- `decision_rules.md`: every gate and the scoring formula, with worked arithmetic
- `pr_body.md`: the five sections a reviewer needs
- `evidence_pack.md`: claim, evidence, limit, for each statement
- `bounty_ledger.csv`: the ledger header for a spreadsheet
- `timebox_card.md`: the six phases and the stop rules, printable

### Operator Kit — $19

Everything in the Field Kit plus:

- the `paid_issue_kit` Python package (standard library only)
- `score`: turn candidate issues into a scored CSV ledger
- `timebox`: six ordered phases, 120 minutes, a verdict that can say
  `CLAIM BROKEN`
- `pr`: build a PR body and evidence pack, then reject placeholder text and
  unverifiable claims
- 76 tests and a one-command self-test
- synthetic examples and the generated ledger, PR body, and evidence pack

### Team Kit — $39

Everything in the Operator Kit plus:

- internal sharing for up to 10 seats
- an invoice
- 30 days of email support, two business days response

## How the two hours work

| Phase | Minutes | Output |
|---|---|---|
| Triage | 15 | Intake completed; amount, criteria, and scope confirmed |
| Reproduce | 20 | A failing test or written reproduction |
| Patch | 40 | Smallest change that makes it pass |
| Test | 25 | Command, exit code, raw output |
| Package | 15 | PR body and evidence pack pass validation |
| Submit | 5 | PR URL recorded |

The timer does not stop when you are waiting for a maintainer. It stops when
your six phases are done. If you cross 120 minutes, the tool reports
`CLAIM BROKEN` and keeps the row. That is the point: the log stays honest.

## What the two hours do not include

- Waiting for review.
- Waiting for CI you do not control.
- Waiting for a payout.
- Learning an unfamiliar repository from zero. Triage prices that, and the
  default gate sends anything estimated over three hours to NO-GO.

## Price

$9 / $19 / $39. One-time purchase. No subscription. 14-day refund on request,
no questions.

Fees are handled by the store. At $9 the payment fee is $1.40; at $19 it is
$2.40; at $39 it is $4.40, based on the store's published 10% + $0.50 rate.

## Proof you can run

The Operator Kit ships 76 tests. The command is in the README:

```
python3 -m unittest discover -s tests
Ran 76 tests in 0.095s
OK
```

The PR package refuses to build a body that contains placeholder text, no test
command, no issue link, no rollback, or a claim that the change cannot fail. The
evidence pack refuses a non-zero exit code as proof. These are not marketing
lines; they are tested behaviour, listed by name in
`evaluation/TEST_RESULTS.md`.

## What this does not promise

- No promise that a maintainer merges your PR.
- No promise that a bounty pays.
- No income figure, typical or otherwise.
- No promise that two hours fits every issue. Some issues are a week. The gate
  is designed to tell you that before you start.

## Call to action

**Get the Field Kit — $9**

Or take the Operator Kit if you want the timer and the validator, not just the
forms.

## Footer

Digital download. Delivered as files, not a course or a call. Licence terms are
in `LICENSE_AND_TERMS.md`. The measured numbers above were taken on 2026-11-18
and will age; the method is in `research/measure_market.py` so you can re-run it.
