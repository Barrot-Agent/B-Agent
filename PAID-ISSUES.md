# Paid issues: READY, never claimed

Last run: 2026-11-19 18:25 UTC. Schedule: every 6 hours, indefinitely, plus manual dispatch.

Rules enforced by `scripts/paid_issue_hunter.py`:

- read-only: no comment, no claim, no label, no assignment
- amount must sit in the same line as a bounty word, exceed $50 and not exceed $50,000
- repository must be active: pushed within 120 days, not archived, at least 20 stars
- at least one skill keyword must appear: Go, Python, workflow, Actions, MCP, audit, CLI, test
- a platform link counts only if it is issue-specific; repo-level sponsor links and docs links are noise
- score = amount / difficulty, difficulty from labels (docs 1.0, bug 2.0, feature 3.0, else 2.5)

Rows: 0. Every row is READY. Nothing here is claimed or verified escrow.

No issue passed the filters this run. That is a result, not a failure.

## What this file does not claim

- A stated bounty is not escrow. None of these payouts was verified.
- No issue was claimed, commented on, or started by the automation.
- Approval to start any row must come from the user.
