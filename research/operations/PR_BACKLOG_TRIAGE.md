# Barrot-Agent/B-Agent pull-request backlog triage

**Snapshot:** 2026-11-04, after merge of PR #1639.

- Open pull requests: 362
- Draft: 356
- Non-draft: 6

## Current-main integration work

The following source proposals are being reconciled into one fresh-main core-capability integration branch, not independently merged from stale bases:

- #1540 — MMI claim-bound corroboration and source-independence grouping (draft; CI/gate passed on source head).
- #1317 — deterministic structural-analysis core and source manifest.
- #1318 — strict scientific-discovery response-schema validation.
- #1320 — paper-trader position-product identity validation and workflow safety.
- #1255 — Databricks SDK dependency floor update.
- #1254 — Hugging Face Hub dependency floor update.

Integration branch: `integration/core-capabilities-mmi-structural-paper-20261104`, based on main `9100dbacb5f9f1b973b053a65ef1e91e96b64f72`.

The shared `scripts/barrot_agent.py`, `tests/test_scientific_discovery.py`, and `.github/workflows/ci.yml` are manually reconciled against current main. The paper-trader workflow is strengthened beyond its source PR with explicit YES confirmation, exact-main-SHA checks, model-secret isolation and a separate write-only persistence job. The current state has a nonzero position size but `position_product=null`; no paper-trading workflow is to be run until identity is verified.

## Separate workstreams

- #1269 — OBJ mesh topology/triangulation; stale geometry workstream, requires fresh-main refresh and full-suite CI. Its duplicate predecessors #1252 and #1137 are closed.
- #1614 — unique XRP research archive; preserve until all unique research artifacts are reconciled into the canonical append-only archive.
- #1611 — predecessor to #1614; preserve until archive reconciliation.
- #1314 — predecessor to #1317; close only after the successor is merged and verified.
- #758 — closed as stale/unreviewed because it combined self-upgrade with trading recommendations and was over 500 commits behind.
- #1181 — closed because its temporary-payload-lifetime fix and regression test were already present on current main.

## Closed duplicate/superseded proposals

Fifteen were closed with cross-references while preserving their branches/history: #1637, #1636, #1634, #1627, #1626, #1622, #1621, #1628, #1625, #1624, #1537, #1181, #1252, #1137 and #758.

PR #1639 was merged; source PRs #1623, #1618 and #1616 were closed only after all changed paths were verified on main.

## Operating rules

1. Inspect current main and the entire open-PR inventory before work.
2. One active integration PR per coherent workstream; no fragmented successors.
3. Reconcile source branches against current main; never merge stale bases blindly.
4. Run exact-head core CI, full repository suite, fail-closed gate and relevant dependency/security audits.
5. Merge only after verification and explicit user authorization.
6. After merge, verify main, then close source PRs only when their changes are demonstrably present.
7. Never bulk-close drafts or discard unique work; preserve branches/history and classify each as ready, blocked, superseded, duplicate or unique/unreviewed.
