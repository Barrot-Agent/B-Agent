# Bounty platform APIs: what answers without an account

Date: 2026-11-17. Method: `scripts/bounty_api_probe.py`, one GET per endpoint, 25 second
timeout, user agent `Barrot/1.0`. Record: `data/money/bounty_apis.json`.

Purpose: the hunter can only price an issue if a number is obtainable. Stated bounties
in issue text are the only source found so far. This page records whether any platform
returns an amount anonymously.

## Measured

| Endpoint | Status | Body begins with | Amount obtainable |
|---|---|---|---|
| issuehunt.io/r/k3d-io/k3d | 502 | `502 Bad Gateway` | no |
| issuehunt.io/api/v1/repos/k3d-io/k3d | 200 | `<!DOCTYPE html>` (app shell, not JSON) | no |
| api.issuehunt.io/v1/repos/k3d-io/k3d | 404 | `Something went wrong with the request.` | no |
| api.opire.dev/health | 200 | `{"message":"I am healthy!"}` | no, health only |
| api.opire.dev/bounties | 404 | HTML error page | no |
| api.algora.io/v1/bounties | 404 | HTML error page | no |
| algora.io/v1/bounties | 404 | HTML error page | no |
| api.polar.sh/v1/products?limit=1 | 401 | `{"error":"Unauthorized"}` | no, login required |
| api.polar.sh/v1/issues/search | 404 | `{"detail":"Not Found"}` | no |

Amount sources found: 0 of 9.

## What this proves and what it does not

Proves: none of these nine endpoints returned a bounty amount to an anonymous GET on
this date. The Polar endpoints require a token. IssueHunt's web front end was serving
502 and its API path returns the application HTML shell, so its former JSON API is not
reachable at the guessed path.

Does not prove: that these platforms have no bounties. A 401 or 404 says the request
was refused or the route is wrong. Reading a real amount needs either a documented API
route or an account token.

## Consequence for the hunter

No change to `scripts/paid_issue_hunter.py` follows from this. The rule stays: an
amount is only reported when a bounty word and a number sit on the same line of the
issue itself. Platform rows are only listed when the link is issue-specific, and that
list is currently empty because the earlier eight matches were repo-level sponsor
templates.

The honest path to a priced row is one of:

1. a documented platform API route, supplied or discovered with a key;
2. a platform account with payout details, so a token can read the amount;
3. an issue whose own text states a bounty amount on the same line.

Option 3 is already implemented and currently yields zero of 137 scanned issues.
