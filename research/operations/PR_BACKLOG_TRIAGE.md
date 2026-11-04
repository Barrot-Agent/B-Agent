# Barrot-Agent/B-Agent pull-request backlog triage

**Snapshot:** 2026-11-04T11:42:54Z, after creation of PR #1643.

- Open pull requests: 366
- Draft: 359
- Non-draft: 7

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
- #1597, #1605, #1608 and #1614 — unique XRP research source branches; PR #1643 is the consolidated current-main archive successor. Keep the source PRs open until all included paths are verified on main; excluded candidate video inventories remain preserved in their source branches.
- #1611 — predecessor to #1614; preserve until its remaining code and research content is separately reconciled.
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


## Run 12 — current classification (2026-11-04T11:42:54Z)

### Current-main integration PRs

- **#1640 — blocked / nearly ready:** non-draft, 20 commits ahead of main, zero behind, 26 files. Exact code head `b654e6c7884f0ba002f0b285ace57098b422916d` passed 553 core tests + 8 subtests, 788 full-suite tests + 8 subtests, four-manifest pip-audit with no known vulnerabilities, and fail-closed gate. Zero unresolved review threads, but zero approving reviews. Main is protected and the detailed protection endpoint returned 403; required approval policy is not confirmed. A documentation-only child now records Run 12; its own exact-head checks must finish. Do not merge until required approval conditions are verified and satisfied.
- **#1642 — unique/unreviewed; blocked on integration order:** point-in-time snapshot/forecast issuance integrity. Exact head `86d9f12f7e8133ea40c5b6742fd26c2ef79a17b1` passed 492 core tests + 8 subtests, 725 full-suite tests + 8 subtests and fail-closed gate. Draft. Its handoff edit overlaps #1640's shared durable handoff; reconcile before merging.
- **#1641 — unique/unreviewed:** bounded autonomous experimentation foundation. Exact head `5e064a12409230762d35360430ececb90f7a97c3` passed 485 core tests + 8 subtests, 728 full-suite tests + 8 subtests and fail-closed gate. Draft.
- **#1643 — unique/unreviewed:** consolidated XRP research archive on current main, 40 files (39 historical JSON artifacts plus one live market snapshot with two exact API-body SHA-256 receipts). Head `9d40454d6882d0ea32c5682f593a16a1f9806586`; core tests passed 485 + 8 subtests; fail-closed gate passed; full suite was still running at the cutoff. No dependency manifests changed, so dependency audit did not trigger. Draft; do not merge until full suite and review finish.

### Research source PRs

- **#1597, #1605, #1608, #1614 — unique/unreviewed; included portions pending supersession by #1643.** Their stale branches remain untouched. Do not close until #1643 is merged, every included path is verified on main, and cross-references are posted. Candidate Kamilah/Camilla video lists were excluded because first-party identity/canonical channel ownership remains unverified.
- **#1611 — unique/unreviewed predecessor.** Preserve until its remaining code and research are compared against current main and #1642; no closure.
- **#1317, #1318, #1320, #1269, #1255, #1254 — non-draft, unreviewed/unique workstreams.** No bulk closure or changes in this run.

### Counts and safety

- Open PRs: 366; drafts: 359; non-drafts: 7. The seven non-drafts are #1640, #1318, #1320, #1317, #1269, #1255 and #1254.
- No branches were force-pushed or rewritten. No user work was reset, stashed or discarded. No merge, deployment, secret rotation, Space restart, Kaggle submission, paper trade or real-money action occurred.
