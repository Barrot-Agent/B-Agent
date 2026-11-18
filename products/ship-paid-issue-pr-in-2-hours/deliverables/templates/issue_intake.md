# Paid-issue intake

Fill this before writing any code. If a field is unknown, write `UNKNOWN` and
stop. An unknown amount or an unknown scope is a reason not to start.

| Field | Value | Rule |
|---|---|---|
| Issue URL | | Must be issue-specific, not a repo or profile link |
| Repository | | |
| Issue title | | |
| Amount stated | | Exact text and where it appears |
| Amount source | | Issue body / comment / platform page |
| Escrow verified | YES / NO / UNKNOWN | A stated bounty is not escrow |
| Platform | | Algora / Opire / direct / none |
| Repo stars | | |
| Last push | | Must be inside 120 days |
| Archived | YES / NO | YES is a stop |
| Acceptance criteria | | Quote the text that defines done |
| Criteria testable | YES / NO | If NO, ask in the issue before coding |
| Estimated hours | | > 3 hours is a stop for this timebox |
| One-PR scope | YES / NO | If NO, split or stop |
| Unrelated edits needed | | Any is a stop |
| Effective rate | | (amount net of fees - expenses) / hours |
| Decision | GO / NO-GO | |
| Reason | | Copy the failing gate text |

## Stop rules

1. No stated amount -> stop.
2. Amount below $50 or above $50,000 -> stop.
3. No acceptance criteria -> ask, then stop until answered.
4. Acceptance criteria need more than one PR -> stop.
5. Repo archived, under 20 stars, or idle over 120 days -> stop.
6. Estimated effort over 3 hours -> stop. This pack sells 120 minutes.
7. Effective rate below $30/hour -> stop unless the PR buys something else you
   can name (portfolio piece, maintainer relationship, learning a specific API).

## After the work

Record the PR URL, the review outcome, the actual hours, and whether the payout
arrived. A row with `payout received = NO` is the most valuable row in the
ledger, because it shows which platform or maintainer does not pay.
