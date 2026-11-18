# Product description

Three lengths, same facts. Use the short one where space is tight, the long one
on the product page. Do not add a number that is not in
`research/EVIDENCE_LOG.md`.

## Short (30 words)

A decision ledger, a 120-minute phase gate, and a PR package that rejects
unverifiable claims. Six templates plus a standard-library Python kit. No
account, no API key, no network call.

## Medium (100 words)

Most paid open source work is lost before the first line of code: the issue says
"bounty" but no amount, the scope is vague, and the PR arrives without proof.
This pack makes those decisions cheap. A hard-gate intake, a scored CSV ledger,
a six-phase 120-minute timer, and a validator that refuses placeholder text and
claims like "this cannot fail". It ships six templates, four Python modules, 76
tests, and generated examples. It does not find bounties, verify escrow, or
promise that a maintainer merges your work.

## Long (300 words)

**GitHub PR Template Pack — Self-Guided**

Paid open source work has a filtering problem. In a sample of 100 open GitHub
issues carrying the `bounty` label, only 6 stated a dollar amount. The label is
not an offer. A stated amount is not escrow. And even a real issue can eat a
weekend if the scope is not pinned before you start.

This pack is the layer before the code.

**Decide.** A one-page intake records the amount, where it was stated, whether
escrow was actually seen, the acceptance criteria, the repo's activity, and the
honest effort estimate. Seven stop rules turn a maybe into a NO-GO before you
lose an afternoon.

**Score.** The Python ledger applies the same gates and writes a CSV sorted by
effective hourly rate after fees and expenses. A `GO` row is a candidate, not a
promise. Every `NO-GO` row carries its reason.

**Timebox.** Six phases totalling 120 minutes: triage, reproduce, patch, test,
package, submit. Order is enforced. The state file is plain JSON. The verdict is
`CLAIM HOLDS` only if all six finish inside the budget; otherwise it says
`CLAIM BROKEN` and keeps the row.

**Prove.** The PR builder writes the five sections a reviewer needs. The
validator rejects missing links, missing test commands, missing rollback,
placeholders, and unverifiable claims. The evidence pack requires a claim, its
evidence, and its limit, and it will not accept a non-zero exit code as proof.

**What you get.** Six templates (five Markdown, one CSV ledger), four Python
modules with no third-party dependencies, 76 tests, and three generated
examples. Python 3.10+.

**What it does not do.** It does not find bounties, verify escrow, open PRs, or
promise payment. Measured review-latency data is included with its limits.

## Bullets

- Nine hard gates, including a 3-hour effort cap and a $30/hour floor
- Effective rate after fees and expenses, not the headline amount
- 120-minute timer with ordered phases and a verdict that can fail
- PR validator that blocks placeholders and unverifiable claims
- Evidence pack with a stated limit for every claim
- 76 tests, standard library only, runs offline
- Field Kit $9 · Operator Kit $19 · Team Kit $39

## Keywords

paid open source, github bounty, pull request template, bounty ledger, timebox,
PR checklist, evidence pack, open source contributor, freelance developer,
GitHub issues, maintainer review

## Not this product

- Not a bounty board or a scraper subscription
- Not a course, a call, or a community
- Not a bot that writes or submits PRs
- Not financial, legal, or career advice
