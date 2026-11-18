# The 120-minute card

Print this. Write the clock time in the margin when you start each phase.
The timer is the product. If a phase runs over, stop and write why.

| Phase | Budget | Clock time | Done when |
|---|---|---|---|
| Triage | 15 min | | Amount, criteria, scope, and repo activity are recorded in the intake |
| Reproduce | 20 min | | A failing test or a written reproduction exists |
| Patch | 40 min | | The test passes and the diff is limited to the issue |
| Test | 25 min | | Full command, exit code, and output are captured |
| Package | 15 min | | PR body and evidence pack pass the validator |
| Submit | 5 min | | PR URL is recorded in the ledger |

Total: 120 minutes.

## Stop rules

- 20 minutes into Reproduce with no reproduction -> comment on the issue with
  what you tried, close the session, mark NO-GO.
- 40 minutes into Patch with the test still failing -> revert to the last
  checkpoint, write the blocker, stop.
- Test phase shows a failure you cannot explain in one sentence -> stop. Do not
  open the PR.
- Any phase over budget by more than 10 minutes -> the claim "in 2 hours" is
  already false for this run. Record it as broken and keep the row.

## What the two hours do not include

- Waiting for a maintainer to reply.
- Waiting for CI you do not control.
- Waiting for a bounty to be paid.
- Learning the repository from zero. Triage should surface that cost; if the
  repo is unfamiliar, the honest estimate is above 3 hours and the gate says
  NO-GO.

## After submit

Record: PR URL, review comments count, merge date, payout received (YES / NO /
UNKNOWN), and actual hours. The next run's estimate gets better only if this
row exists.
