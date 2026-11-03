# Barrot V3 Scheduled Writer Containment — 2026-11-03 12:16:07 UTC

## Main
Current base: `0acd6407dcd5bdc2ce31f4519d83716fc08da322`. Main was not changed.

## Five current-main scheduled writer risks
1. `subscriber_sync.yml`: hourly Gumroad API query; unsalted SHA-256 email hashes written to public `web/subscribers.json`; commit/push to main. File contents were not inspected. No plaintext email disclosure established.
2. `daily-digest.yml`: daily public issue writer with issues:write. Public issue #1538 contains the legacy unvalidated 45.5% accuracy claim despite confidence 0.0, missing provider credentials and a Groq 429.
3. `auto-resolve-issues.yml`: daily `scripts/resolve_issue.py --all` with issues:write. Prior observed run closed #1545, #1514 and #1492 without per-issue approval.
4. `barrot-autonomous-resolver.yml`: hourly issues/PR writer. Its claimed 24-hour failure scan omitted a createdAt cutoff and branch/event filter; it created #1574–#1579 from failed PR-branch validations with zero jobs.
5. `self-schedule.yml`: six-hour source-gap issue writer with issues:write. Prior observed run was a no-op, but the capability remains.

## Proposal
Five workflows are now manual-only, permissions-empty and job-disabled on a fresh-main branch. The existing `tests/test_v3_scripts.py` file has a regression test for manual-only triggers, empty permissions, inert jobs, no secrets and no mutation commands. It is already in core CI, so this proposal does not modify CI configuration.

## Privacy limitation
Unsalted SHA-256 email hashes can be dictionary-matched. The current public file was not inspected, and no plaintext email disclosure is claimed. Do not copy subscriber identifiers into research artifacts. Review the data before any re-enable decision.

## Execution status
Changes exist only on branch `security/fresh-main-scheduled-writer-containment-0acd6407-20261103T1215Z`. No main commit, secret access, Gumroad request, issue mutation, assignment or deployment occurred. Core CI and fail-closed verification are pending.

## Next
1. Verify exact-head CI.
2. Open/update the fresh-main PR and retain draft status.
3. Obtain approval before any merge.
4. Separately review subscriber data and the public digest issue.
