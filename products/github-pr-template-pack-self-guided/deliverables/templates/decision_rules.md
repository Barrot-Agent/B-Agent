# Decision rules

These are the same gates the Python kit applies. They are configurable in
`paid_issue_kit/ledger.py` (`Policy`), but a rule that is turned off should be
turned off deliberately and written down.

## Hard gates (any failure = NO-GO)

| # | Gate | Default | Why |
|---|---|---|---|
| 1 | Amount is stated in the issue or on an issue-specific platform page | required | 94 of 100 sampled `bounty`-labelled issues stated no amount |
| 2 | Amount between $50 and $50,000 | $50 / $50,000 | Below $50 the time cost exceeds the payout; above $50,000 the scope is not a 2-hour PR |
| 3 | Acceptance criteria are written and testable | >= 20 characters | "Make it better" is not done |
| 4 | Repository is active | pushed within 120 days | A dead repo will not review or pay |
| 5 | Repository is not archived | not archived | Archived repos cannot merge |
| 6 | Repository has at least 20 stars | >= 20 | Filter for projects with real users and review |
| 7 | Title has no spam marker | deny list | Bounty-spam issues are not work |
| 8 | Effort estimate is at most 3 hours | <= 3 | The package sells a 120-minute timebox; a 10-hour task makes that claim false |
| 9 | Effective rate is at least $30/hour | >= $30 | Protects the timebox |

## Formula

```
effective_payout = amount * (1 - payout_fee_fraction) - expenses
effective_hourly = effective_payout / effort_hours
confidence       = 1.0 escrow verified
                 = 0.9 issue-specific platform link
                 = 0.8 bounty label
                 = 0.7 no signal
score            = effective_hourly * confidence
```

Worked example: $500 stated, 2 hours estimated, 0% fee, $0 expenses.

```
effective_payout = 500 * (1 - 0) - 0 = 500
effective_hourly = 500 / 2        = 250
confidence       = 1.0 (escrow verified)
score            = 250
```

The same issue with no escrow and only a label scores 225. Same work, lower
confidence. That is the point: the score is a screening order, not a promise.

## What the score is not

- It is not a probability of payment.
- It is not a measure of code quality or maintainer fit.
- It does not price the value of a merged PR to your portfolio.
- It cannot see a hidden second reviewer, a CLA, or a maintainer who is on leave.

## When to break a rule

Only with a written reason. Example: a $20 issue in a repository you already
contribute to, where the real return is a maintainer relationship. Record the
reason in the ledger row. If the reason is "I need money this week", the rule
should not be broken; the pipeline should be widened instead.
