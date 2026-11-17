# Paid issues: READY, never claimed

Last run: 2026-11-17 21:13 UTC. Policy: manual dispatch only; no automatic schedule or repository writes.

Rules enforced by `scripts/paid_issue_hunter.py`:

- read-only: no comment, no claim, no label, no assignment
- amount must sit in the same line as a bounty word, exceed $50 and not exceed $50,000
- repository must be active: pushed within 120 days, not archived, at least 20 stars
- at least one skill keyword must appear: Go, Python, workflow, Actions, MCP, audit, CLI, test
- score = amount / difficulty, difficulty from labels (docs 1.0, bug 2.0, feature 3.0, else 2.5)

Rows: 8. Every row is READY. Nothing here is claimed or verified escrow.

## Platform-linked, amount not in the text

The body links a bounty platform but states no amount. Amount is UNKNOWN and
is not guessed. These are candidates to open by hand, not priced work.

| # | Issue | Platform | Skills | Difficulty | Repo stars |
|---|---|---|---|---|---|
| 1 | [k3d-io/k3d#1689](https://github.com/k3d-io/k3d/issues/1689) | issuehunt.io | test, workflow | 2.0 | 6627 |
| 2 | [autokey/autokey#1326](https://github.com/autokey/autokey/issues/1326) | opire.dev | cli, python | 2.5 | 3906 |
| 3 | [bk138/droidVNC-NG#372](https://github.com/bk138/droidVNC-NG/issues/372) | issuehunt.io | cli | 2.0 | 2448 |
| 4 | [LibVNC/libvncserver#729](https://github.com/LibVNC/libvncserver/issues/729) | issuehunt.io | test | 2.0 | 1377 |
| 5 | [LibVNC/libvncserver#704](https://github.com/LibVNC/libvncserver/issues/704) | issuehunt.io | cli | 2.0 | 1377 |
| 6 | [bk138/multivnc#309](https://github.com/bk138/multivnc/issues/309) | issuehunt.io | cli, go | 2.0 | 676 |
| 7 | [bk138/multivnc#293](https://github.com/bk138/multivnc/issues/293) | issuehunt.io | cli | 2.0 | 676 |
| 8 | [davidgasquez/handbook#51](https://github.com/davidgasquez/handbook/issues/51) | gitcoin.co | github action | 2.5 | 191 |

## What this file does not claim

- A stated bounty is not escrow. None of these payouts was verified.
- No issue was claimed, commented on, or started by the automation.
- Approval to start any row must come from the user.
