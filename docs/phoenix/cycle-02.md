# Phoenix cycle 02: KPI proof, gap, upgrade

Date: 2026-11-17. Baseline: HEAD d28e03e7e, docs/phoenix/PROGRAM.md.
Rule: a KPI that was never measured is not a KPI. Three of six were measurable in
this cycle; three were not, and say so.

## Measured this cycle

1. Recovery. scripts/restore_drill.py: 200 files written, tarred, deleted, restored.
   Restore 1.865 s, files lost or changed 0, lossless true. Test:
   tests/test_restore_drill.py, 1 passed.
2. Redundancy, N-1. Broke the config mirror on purpose (one byte appended to
   data/mcp_config.json): audit exited 1 and named config_mirror. Restored the file:
   audit exited 0. The check fails when a link is removed, which is the point of an
   N-1 test.
3. Governance. Commits today: 28. Flight Recorder records: 10 in 7 files. Commits
   without a matching record: 18, coverage 36 percent. Approximate match, not
   line-for-line, but the size of the hole is real.

## Not measured, with the reason

- Thermal and energy. /sys/class/thermal is present but exposes no zones, there is
  no power sensor and no load generator. Any watts-per-volume number would be
  invented. No number claimed.
- Parallel agents. Two subagent runs cost 3 to 5 minutes of the 15-minute cap and
  were not spent here. Convergence time is therefore unknown.
- Learning loop. Needs a retracted-paper fixture and a claim set. Not assembled in
  this cycle, so catch rate is unknown.

## Gap to what Phoenix implies, and the upgrade

| Cluster | Phoenix implies | Measured now | Gap | Upgrade |
|---|---|---|---|---|
| Recovery | rebirth with nothing lost | files restored in 1.9 s, zero loss | files only, no running service, no offsite copy | service-level drill: stop, restore, start, verify; needs live-state approval |
| Thermal | survive cosmic fire | nothing measured | no sensor, no number | datasheet budget plus one measured load test on the device |
| Redundancy | survive any single death | static link fails and is caught | no live replica quorum | kill-one-server drill behind approval |
| Parallel | many minds, one action | nothing measured | no convergence number | two agents, same task, measure wall clock and agreement |
| Learning | assimilate knowledge instantly | nothing measured | no retraction test | 10 retracted papers, 10 live claims, measure catch rate |
| Governance | transformation is automatic | 36 percent coverage | 18 of 28 commits have no record | add a coverage link to cross_domain_audit |

## Implemented in this cycle

- scripts/restore_drill.py plus its test. Recovery now has a number that a re-run
  can contradict.
- Tar extraction switched to filter="data": the previous call carried the path
  traversal warning, and a backup restore is exactly where that matters.

## Not implemented, on purpose

The governance coverage link was not added to the audit in this cycle: it will fail
red immediately on 18 historical commits, and a check that is born red gets
ignored. The honest sequence is to record the number first (done above), then set
the threshold with your approval.

## Licence and status

No new external source was fetched this cycle. All previous source entries keep
their licence and 2026-11-17 probe status; nothing was re-crawled.
