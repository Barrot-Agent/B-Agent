# XRP research provenance correction handoff

Audit time: 2026-11-03T22:35:19Z  
Repository: Barrot-Agent/B-Agent  
Inspected main: `8007440e08a40608c119e48b7f8fa4e189175280`  
Inspected research branch before correction: `e828784d00a6b54dd0e3c2b352fc2677499aba58`  
Audit artifact: `research/xrp_intelligence/20261103T223519Z-research-artifact-clock-audit.json`

## Finding

A repository-history audit compared each research artifact's `captured_at_utc` with the GitHub server commit creation time of the commit that first introduced it.

Seven of nine examined artifacts are timestamp-inconsistent: each claims to have been captured after the commit that already contains it. Four of those timestamps were also in the future relative to this audit. This is a provenance failure, not proof that the underlying source claims are false.

The two earlier files pass only the minimum clock-order check. They are design/implementation reports, not market observations.

## Required treatment

- Preserve every original artifact unchanged.
- Quarantine the seven inconsistent artifacts from model features, training, event-time ordering and forecast justification.
- Re-fetch their cited public sources and create new contemporaneous records.
- Add a deterministic artifact-clock validator and CI regression test.
- Never backdate a corrected artifact; use a new append-only record with a `supersedes` reference.

## Engineering state

The fixed-horizon forecast ledger and point-in-time feature validator remain implemented on PR #1614. Exact-head CI and fail-closed gate were observed passing before this correction. The correction is an additional research-only commit; its own CI must complete before verification is claimed.

## Safety

No main-branch change, merge, force-push, workflow dispatch, secret access, deployment, paper trade or real-money transaction occurred.

## Next action

Implement the artifact-clock validator and CI test on the research branch, then re-verify the seven quarantined source claims from their original public URLs with real retrieval times.
