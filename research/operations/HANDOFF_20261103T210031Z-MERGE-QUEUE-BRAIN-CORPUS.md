# Barrot V3 durable handoff — Merge Queue and public brain-corpus export

- Capture: 2026-11-03T21:00:31.525Z
- Repository: Barrot-Agent/B-Agent
- Fresh base: fada1c0712894e92f301e2cb5e6aa098280bfbe8
- Status: EXECUTED, pending exact-head CI and independent review
- Mission: XRP intelligence and prediction-engine mastery remain highest priority; Barrot V3 remains the execution and verification foundation.

## Confirmed main-branch findings

1. Merge Queue is manually dispatched, but can select every open PR with `mode=all`, `max_prs=0` (unlimited), and `dry_run=false`. It has contents and pull-request write permissions, can update branches, comment, merge PRs, and delete merged branches. This conflicts with the explicit no-merge/no-branch-deletion boundary.
2. Dump Brain Corpus is manually dispatched with contents:write and a Databricks token. Its exporter queries the full non-error `workspace.barrot.brain` table and writes timestamp/topic/insight/session records into public JSON and Markdown files.
3. The current public files are 353,950 bytes and 296,527 bytes. Their contents were not opened; record-level sensitivity remains unclassified.

## Proposed containment

- Disable `.github/workflows/merge-queue.yml` with workflow_dispatch-only, `permissions: {}`, and `if: false`.
- Disable `.github/workflows/dump-brain-corpus.yml` with the same fail-closed pattern.
- Replace `scripts/dump_brain_corpus.py` with an inert status-only entry point.
- Remove `brain_corpus/dump.json` and `brain_corpus/dump.md` from the proposed current tree; do not rewrite history.
- Add regression tests to the CI-included `tests/test_v3_scripts.py`.

## Verification

- DESIGNED: least-privilege containment and explicit re-enablement criteria.
- EXECUTED: fresh-main branch and proposed file changes.
- VERIFIED: not yet. Exact-head CI and the fail-closed gate must pass.

## Preservation and limits

No main modification, merge, force-push, workflow dispatch, branch update, branch deletion, Databricks query, secret access, deployment, paper trade or real-money transaction occurred. Historical Git objects, forks and caches remain untouched. No administrative branch-protection changes are proposed.

## Next action

Run exact-head CI and fail-closed verification. Then audit the remaining Cross Analysis and legacy signal-accuracy writers, while building the historical XRP feature/outcome store.
