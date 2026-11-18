# Citation Audit Checklist - DRAFT

Status: DRAFT. Not published. Not accepting clients without approval.

## Offer

A fixed-scope audit of up to 50 citation claims: every quote checked as a substring of
its source, every DOI checked for retraction, every verdict checked for a falsifier.
Delivered as a report plus a pull request that makes the checks run in CI.

## Scope and price (proposal)

| Tier | Price | Scope | Turnaround |
|---|---|---|---|
| Audit | 249 | up to 50 claims, report only | 3 business days |
| Audit and fix | 899 | up to 50 claims, report plus a CI job and tests | 7 business days |
| Retainer | 900 per month | two audits, priority queue | monthly |

Out of scope, stated up front: writing the client's research, judging scientific
truth, legal review, and any claim of correctness beyond the checks named.

## Process

1. Client sends a claims file and the source texts.
2. Every claim is validated and graded Q, E or X.
3. Report ranks findings by cost of being wrong.
4. If the fix tier is bought, a pull request adds the validator to CI.
5. Handover page explains how to keep it green.

## Sales copy

Headline: 50 citations audited, every one with a quoted line or a refusal.

Body: The audit is mechanical and repeatable. The client receives the command output,
not a summary of it, so any claim in the report can be re-run.

Call to action: Send a claims file for a free 5-claim sample.

## Evidence

The checks already exist and are tested here. No client has been served; the free
sample is the only claim that can be made until one is.

## Approval gate

Do not accept payment or publish a price until the refund policy and the sample audit
are written. An offer that cannot fail a test cannot be priced.
