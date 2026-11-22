# Barrot XRP Intelligence — Canonical Durable Handoff

**Updated:** 2026-11-22 06:00 UTC  
**Mission priority:** XRP intelligence and measured prediction-engine capability. Preserve Barrot V3 as execution, orchestration, safety and verification foundation.  
**Record policy:** The Current State — Run 12 section immediately below is authoritative for this update. Run 11 and earlier run-specific sections are preserved historical evidence; prior run detail remains in Git revisions and linked GitHub Actions artifacts. No branch history is rewritten.


## Current State — Run 12 — 2026-11-22 06:00 UTC

This section is authoritative for the current snapshot. Run 11 and all earlier sections remain preserved historical evidence. The repository was inspected as one integrated product before any write. The audited code head was `c8917c4f5fcf6743334143b0cf34080dddc95018`; this atomic handoff/map/test refresh is parented to that exact head and must receive its own exact-head CI. No application runtime or workflow code is changed by this refresh.

### Repository and integration

- Main remains `550a647ee7269a704d4600ff337b2145acc90473`; its complete recursive tree has 3,115 entries.
- Existing XRP integration branch `integration/xrp-post-merge-verification-20261121T0002Z` is at `c8917c4f5fcf6743334143b0cf34080dddc95018`: 145 commits ahead, 0 behind main; 27 changed files; 3 changed workflow files; 3,127 complete tree entries; zero main paths missing.
- No new branch or PR was created. Main was not modified.
- Current integration objective remains consolidated in [PR #1684](https://github.com/Barrot-Agent/B-Agent/pull/1684).

### Exact-head CI on `c8917c4`

- [PR CI 44987836051](https://github.com/Barrot-Agent/B-Agent/actions/runs/44987836051): full repository suite **4,564 passed, 0 failed, 1 skipped**, 11 warnings and 32 subtests; 180.15 seconds.
- [Push CI 44987832154](https://github.com/Barrot-Agent/B-Agent/actions/runs/44987832154): successful; its duplicate full-suite job was skipped by the integration-push guard. The PR-event full-suite job above is the controlling full-suite evidence.
- [Dependency audit 44987836044](https://github.com/Barrot-Agent/B-Agent/actions/runs/44987836044): passed.
- [Money audit 44987836128](https://github.com/Barrot-Agent/B-Agent/actions/runs/44987836128): passed.
- [Conflict integrity 44987836078](https://github.com/Barrot-Agent/B-Agent/actions/runs/44987836078): passed.
- GitHub Pages validation passed in validation-only mode; no deployment.
- [Historical backfill replay](https://github.com/Barrot-Agent/B-Agent/actions/runs/44987836051): 118 records recovered across 11 source lineages; isolated store grew from 18,483 to 18,601 records and 30 to 31 snapshots. SQLite integrity passed; 33 historical artifact ZIP digests matched, zero mismatches. Point-in-time visibility was false immediately before and true immediately after the availability bound. Reconciliation SHA-256: `dd1be5b3c55afa3f3ba13715b50f6804fe07c976a40939be813b13b84a8afa24`. This was an isolated CI copy, not a main database write. The GitHub API run-date clock is a post-append availability bound, not verified physical commit time or an external trusted timestamp.
- [Fail-closed gate 44987836136](https://github.com/Barrot-Agent/B-Agent/actions/runs/44987836136) correctly refused readiness because the PR is draft, there is no independent approval and branch protection cannot be inspected. No merge was attempted.

### Latest successful main ingestion — Run 59

[Ingestion run 44988443368](https://github.com/Barrot-Agent/B-Agent/actions/runs/44988443368) completed successfully on main SHA `550a647ee7269a704d4600ff337b2145acc90473`; data cutoff `2026-11-22T05:13:39.556002Z`.

- Feature store: 18,606 historical records across 31 snapshots; 490 delta candidates; 123 eligible and 367 excluded; SQLite integrity `ok`.
- Receipts: 34 total; 22 retained payloads and 12 digest-only; 18 source failures; 23 raw-only sources. Cross-run sequence 31 continued from run 44984161724 and verified. The cache reservation failed because the GitHub Actions cache budget is exhausted/read-only; the workflow restored the Run58 per-run feature-store checkpoint. Feature-store checkpoint retention is 7 days; raw, event and receipt-index artifacts retain 90 days. Reconstruction from retained raw artifacts is not implemented.
- Receipt-chain head SHA-256: `fb2fa68d25fbd075660011f6e4870ee71dadfdf5cf64a5bfc158dad5fbd54f58`. Chain-log SHA-256: `9687a745436e316d71614299361c110b5069a4313cd195f4eb59c1f2866e92f3`. Receipt-log SHA-256: `b971a60a172a5c0f083e1170d64904299af1acfd97e754ca91e9687dd9c8b16a`. External trusted/WORM anchor remains absent.
- Event timeline: 150 events, 112 declared independence groups, 59 exact publisher timestamps and 91 missing publisher timestamps. Zero raw-source hashes and zero event-to-receipt links; receipt completeness and model eligibility remain false. Scenario registry: 117 hypotheses, probabilities null.
- Drift: 0 of 204 features evaluated; status `INSUFFICIENT_DATA`. Walk-forward: zero forecasts; one-hour label only; status `PARTIAL_OR_BLOCKED`. Forecast issuance remains `NOT_ISSUED`.
- SEC capture remains `BLOCKED_CONFIGURATION`: no approved contact identity, zero raw receipts and three source failures. No SEC data is promoted to XRP market features.
- OKX same-venue XRP-USDT / USDT-USD top-of-book normalization at 05:13:29 UTC: bid $0.9152658, ask $0.915374772, mid $0.915320286, spread 1.1905 bps, component skew 0.096 seconds. Both receipts share one OKX publisher group. This is top-of-book only, not consolidated depth or independent confirmation.
- Artifacts: feature-store checkpoint 14740881478 (7-day retention); raw payloads 14740811755, events 14740404906, receipt index 14740782043 and correction audit 14741125026 (90-day retention for the latter four).

[Cross Analysis run 44991201670](https://github.com/Barrot-Agent/B-Agent/actions/runs/44991201670) succeeded at 05:51:42 UTC. XRP sentiment input remains stale: newest entry 2026-10-29 12:39:22 UTC, age 569.208 hours; forecast eligibility false.

### Current open-PR inventory and overlap audit

| PR | Classification | Current evidence | Disposition |
|---|---|---|---|
| [#1684 XRP integration](https://github.com/Barrot-Agent/B-Agent/pull/1684) | Blocked | Draft; 145 ahead/0 behind; 27 files; zero formal reviews. Exact-head full suite and isolated backfill replay passed on `c8917c4`. | Keep draft. Gate blocks for draft/no independent approval/protection visibility. |
| [#1685 A2A credential separation](https://github.com/Barrot-Agent/B-Agent/pull/1685) | Blocked | Non-draft; 5 commits ahead/0 behind; 9 files; zero formal reviews. Its current head `e512f4e` has prior exact-head suite 4,536 passed, 0 failed, 1 skipped. | Keep runner quarantined until independent review, OS sandbox, provider-credential isolation, egress controls and task-level authorization are verified. No deployment or secret action. |
| [#1686 LunaRoute runtime decommission](https://github.com/Barrot-Agent/B-Agent/pull/1686) | Unique/unreviewed; CI-blocked | Draft; 18 commits; 16 files; zero formal reviews. Exact head `ded2546`; full suite run 44988220240: 4,508 passed, **11 failed**, 1 skipped, 11 warnings, 21 subtests. | Do not merge or run its local cleanup script. It removes provider/refinement code and changes OpenCode configuration; Barrot V3 compatibility requires review. |

PR #1686's 11 failures are concrete: nine tests hit `NameError: os is not defined` in `barrot_agent/refinement/pipeline.py`; one configuration test fails because the string `lunaroute` remains in the agent prompt; one state test fails because the prompt no longer contains required authentication wording. Dependency audit 44988220200, Money audit 44988220204, conflict integrity 44988235542 and Pages validation passed; the fail-closed gate 44988235544 failed.

PR #1685 and #1686 both modify `tests/test_mcp_server.py`. The inspected patches touch different hunks, but the shared path must be reconciled before either PR can be merged. PR #1686 has no path overlap with XRP PR #1684. Its added `scripts/decommission_lunaroute_local.sh` edits shell profiles and deletes `~/.lunaroute_key` if present. The script was not executed. No source PR was closed; #1686 is unique, not a duplicate.

### Governance, dependencies and platform map

- Repository metadata reports admin/maintain/push/pull/triage permissions; connector token scopes were not introspected.
- Main branch-protection metadata says protected, but the protection endpoint returns HTTP 403. The visible `Fall Back` ruleset is disabled. CODEOWNERS is `* @Barrot-Agent`, not an independent reviewer. All three open PRs have zero formal reviews. Repository metadata also reports `web_commit_signoff_required=true`; its effect on the applicable merge path remains unverified.
- Automatic Pages publication on main was previously observed enabled; authorization remains NOT_GRANTED. No deployment occurred.
- Main dependency configuration was inspected: core project dependencies and optional integrations are declared in `pyproject.toml`; development/test tooling is in `requirements-dev.txt`; Dependabot weekly checks pip and GitHub Actions. The exact-head dependency audit on #1684 passed.
- Nine-platform map is refreshed append-only. ChatGPT-to-GitHub authentication/data flow is verified for this session; repository permissions are broad and token scopes are unknown. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks remain unverified. No dispatch, evidence transfer or red-team quorum occurred.

### Prediction readiness and next actions

No directional forecast was issued. No paper trade or real-money action occurred. The 150-event receipt gap, absent external timestamp anchor, 0/204 drift evaluations, zero walk-forward origins, stale sentiment and incomplete SEC configuration prevent model admission.

1. Run exact-head CI on this documentation/test refresh commit; do not transfer `c8917c4` results to the new commit.
2. Capture lawful raw event-source bytes and bind each event to publisher URL, publication/event/capture times, SHA-256 receipt and independence lineage.
3. Implement deterministic feature-store reconstruction from retained raw artifacts before relying on seven-day checkpoints; cache is read-only and the rebuild path is absent.
4. Configure SEC capture only with an approved monitored project identity.
5. Accumulate genuine sequential point-in-time origins; backfilled rows sharing one recovery availability bound are not independent forecast origins. Evaluate naive, momentum, mean-reversion and volatility baselines before calibration.
6. Reconcile the shared `tests/test_mcp_server.py` path before considering PR #1685 or #1686.
7. Keep PR #1686 draft until its full-suite failures and provider-removal impact are reviewed. Do not run its local cleanup script.

**Run 12 disposition:** no merge; no new PR or branch; no main write; no deployment, secret rotation, Space restart, external model dispatch, Kaggle submission, Databricks write, paper trade, funds transfer or real-money action.


## Current State — Run 11 — 2026-11-22 04:54 UTC

This section supersedes earlier repository, CI, ingestion, and backlog snapshots below. It records the state actually fetched and inspected in this run. The audited code head is `d58b5f5b7cfcf2f0551c181814ac1f1342b60667`; this handoff refresh is documentation-only and must receive its own exact-head CI after the update commit.

### Repository and integration

- Repository: `Barrot-Agent/B-Agent`; default branch `main`.
- Current main SHA: `550a647ee7269a704d4600ff337b2145acc90473`; recursive tree: 3,115 entries, complete and not truncated.
- Existing XRP integration branch: `integration/xrp-post-merge-verification-20261121T0002Z`; audited code head: `d58b5f5b7cfcf2f0551c181814ac1f1342b60667`.
- Integration comparison: 144 commits ahead, 0 behind; 27 changed files; 3,127 tree entries; no main paths missing. Main was not modified.
- No new branch or PR was created. The existing XRP work remains consolidated in PR #1684.

### Open PR inventory and backlog

| PR | Workstream | Classification | Evidence and disposition |
|---|---|---|---|
| [#1684](https://github.com/Barrot-Agent/B-Agent/pull/1684) | XRP ingestion, historical recovery, event provenance and prediction readiness | Blocked | Draft; 144 ahead/0 behind; 27 files; no formal reviews. Exact-head full suite and preserved-artifact replay passed on `d58b5f5`, but independent approval and branch-protection verification are absent. |
| [#1685](https://github.com/Barrot-Agent/B-Agent/pull/1685) | A2A gateway/runner credential separation | Blocked | Non-draft; 5 commits ahead/0 behind; 9 files; no formal reviews. Exact-head full suite passed (4,536 passed, 0 failed, 1 skipped); worker, dependency, Money and conflict checks passed. OS sandbox, provider-credential isolation, egress restrictions and task-level authorization remain incomplete. Runner stays quarantined. |
| [#1686](https://github.com/Barrot-Agent/B-Agent/pull/1686) | LunaRoute runtime decommission | Unique/unreviewed; CI-blocked | Draft; 4 files; no reviews. Full suite: 4,528 passed, 6 failed, 1 skipped, 11 warnings. Failures are stale assertions expecting the LunaRoute provider/configuration to remain present. The PR replaces the gateway adapter with OpenCode CLI and adds a local script that edits shell profiles and deletes `~/.lunaroute_key`; that script was not executed. Provider-side egress is not proven local-only. No overlap with #1684 or #1685. |

Backlog count: 3 open workstreams; 0 ready, 2 blocked, 1 unique/unreviewed, 0 duplicate, 0 superseded. No PR was closed. PR #1686 is not an XRP duplicate and must not be bulk-closed.

### Governance and merge decision

- PR #1684 remains draft and has zero independent approving reviews. PR #1685 and #1686 also have zero formal reviews.
- The main branch-protection endpoint returns HTTP 403. The only visible repository ruleset, “Fall Back”, is disabled. CODEOWNERS is `* @Barrot-Agent`, not an independent reviewer. Effective required checks, strict up-to-date enforcement and admin enforcement remain unverified.
- Repository metadata reports `web_commit_signoff_required=true`. The audited integration commit `d58b5f5` is unsigned (`verification.reason=unsigned`). This is not treated as proof of a GPG-signature requirement; the applicable sign-off policy must be resolved before merge.
- Main’s `.github/workflows/barrot-gated-merge.yml` still reads draft status using `.draft // true`, which misclassifies Boolean `false` as absent in jq. PR #1684 contains the corrected presence-aware expression and regression tests. The correction is not on main.
- Exact-head fail-closed gate [44986596674](https://github.com/Barrot-Agent/B-Agent/actions/runs/44986596674) correctly returned BLOCKED: PR #1684 is draft, no independent approval exists, and branch protection could not be verified. The gate is read-only.
- **Decision: NO MERGE.** Do not mark #1684 ready or merge it until its workstream is complete, independent approval exists, protection and sign-off policy are verifiable, and exact-head checks pass. No merge, main write or source-PR closure occurred.

### Exact-head verification on audited code head `d58b5f5`

- [CI 44986596629](https://github.com/Barrot-Agent/B-Agent/actions/runs/44986596629): full repository suite **4,564 passed, 0 failed, 1 skipped**, 11 warnings, 32 subtests, 73.20% coverage, 133.19 seconds.
- [Dependency audit 44986596638](https://github.com/Barrot-Agent/B-Agent/actions/runs/44986596638): passed.
- [Money audit 44986596617](https://github.com/Barrot-Agent/B-Agent/actions/runs/44986596617): passed.
- [Conflict integrity 44986596745](https://github.com/Barrot-Agent/B-Agent/actions/runs/44986596745): passed.
- GitHub Pages build passed in validation-only mode; no publication/deployment occurred.
- [Fail-closed gate 44986596674](https://github.com/Barrot-Agent/B-Agent/actions/runs/44986596674): BLOCKED by governance conditions above, not a test failure.

The full-suite job discovers every tracked active test module, including legacy and mission-critical packages, while excluding only disabled/quarantined tests and fixtures. The hand-selected core job is not being treated as the full suite.

### Preserved-artifact historical feature-store recovery

- Exact-head replay ran inside CI run [44986596629](https://github.com/Barrot-Agent/B-Agent/actions/runs/44986596629), artifact [14739946860](https://github.com/Barrot-Agent/B-Agent/actions/runs/44986596629/artifacts/14739946860).
- 118 records recovered across 11 source lineages; isolated feature store grew from 18,483 to 18,601 records and 30 to 31 snapshots.
- SQLite integrity `ok`; all 33 downloaded historical artifact ZIPs matched GitHub’s recorded digests; 0 digest mismatches.
- Point-in-time visibility: 18,483 records immediately before the availability bound and 18,601 one microsecond after it.
- Reconciliation SHA-256: `dd1be5b3c55afa3f3ba13715b50f6804fe07c976a40939be813b13b84a8afa24`.
- This replay used preserved artifacts in an isolated CI copy. Main’s feature store was not modified. The stored receipt is a post-append availability bound, not the physical SQLite commit time or an external trusted timestamp.

### Latest successful main ingestion — Run58

- [XRP Public Market Ingestion 44984161724](https://github.com/Barrot-Agent/B-Agent/actions/runs/44984161724), run 58, created 2026-11-22 04:14:26 UTC; success on main SHA `550a647`. [Cross Analysis 44986878817](https://github.com/Barrot-Agent/B-Agent/actions/runs/44986878817) completed successfully at 04:51:35 UTC.
- 34 receipts: 22 retained raw payloads and 12 digest-only. 22/22 retained payload SHA-256 values matched their receipt hashes. 18 provider/source failures; 23 raw-only sources.
- Receipt chain: 34 sequential entries; current cross-run sequence 30; previous successful ingestion run `44979814130`; cross-run continuity `CONTINUED` and verified. External WORM/trusted timestamp anchor remains `NOT_ANCHORED`.
- Raw artifact ZIP SHA-256 from GitHub artifact metadata: `438f60a3d5e05ff8192551c2c9e7caefeb627519519e37f913b7889054cb1b02`. Raw artifact tree SHA-256: `0e18f2b14be89e3129d082187bc921ad35c5778113246c6f34767cf23ab5ea89`.
- Feature store: 18,483 historical records across 30 snapshots; latest snapshot has 490 input candidates, 124 eligible records and 366 excluded records; 12 source IDs across 5 independent publisher groups; SQLite integrity `ok`.
- Cache budget is exhausted/read-only. Run58 successfully restored the trusted per-run feature-store checkpoint from run `44979814130`; the cache write then failed non-fatally. Per-run feature-store artifacts retain 7 days; daily archive and raw/event/index artifacts retain 90 days. Rebuild directly from raw receipts is still not implemented. No cache deletion or billing/retention change was attempted.

### Run58 spot microstructure — research snapshot, not a forecast

Capture window: 2026-11-22 04:14:43–04:14:45 UTC; feature cutoff 04:14:55.217676 UTC. Five publisher groups were observed. These are separate single-venue snapshots, not consolidated executable liquidity.

| Venue / pair | Mid | Spread | Bid depth within 10 bps | Ask depth within 10 bps | 10-bps imbalance |
|---|---:|---:|---:|---:|---:|
| Bitstamp XRP/USD | $0.919305 | 0.1088 bps | $374,222 | $321,267 | +7.61% |
| Coinbase XRP/USD | $0.919400 | 2.1753 bps | $470,061 | $326,323 | +18.05% |
| Kraken XRP/USD | $0.919305 | 0.5439 bps | $327,839 | $355,032 | -3.98% |
| OKX XRP/USDT | $0.919612 normalized | 1.1854 bps | 168,914 USDT | 160,071 USDT | +2.69% |
| Bitbank XRP/JPY | 146.0525 JPY | 0.0685 bps | 16,396,574 JPY | 9,347,563 JPY | +27.38% |

OKX normalization used the observed same-venue USDT/USD mid of `0.998005`; no 1:1 peg was assumed. The quote-basis components had 0.899 seconds of timestamp skew and a maximum age of 11.052 seconds. Only OKX top-of-book was USD-normalized; its depth remains USDT-denominated. Bitbank remains JPY-denominated. No venue aggregation or directional inference is permitted from this snapshot.

### Event provenance, SEC capture and prediction readiness

- Event timeline: 150 curated events; 112 declared independence groups, 56 canonical publisher labels, 59 source publication timestamps and 91 missing publisher timestamps. Zero event raw-source hashes and zero event-to-receipt links; receipt completeness false; model eligibility false.
- Scenario registry: 117 hypotheses; 19 with supporting evidence, 6 with contrary evidence and 6 with minority objections. Probabilities remain null. These are authored hypotheses, not causal inference or a forecast.
- SEC capture remains `BLOCKED_CONFIGURATION`: no approved monitored contact identity; 3 source failures; zero submissions/companyfacts sources, filing events, capital facts or primary-document captures. Do not infer actual capital from missing SEC data.
- Walk-forward forecasts: 0. Drift features considered: 204; evaluated: 0. Directional forecast issuance remains disabled.
- The branch includes the delayed-bar target-anchor correction and venue-label normalization fix with regression tests; the exact-head suite passed. This is implementation verification, not predictive-performance validation. The 100-training-sample and 100 genuine out-of-sample-origin gates remain unmet; historical bulk backfill with shared availability timestamps does not create independent forecast origins.

### Research-only observations

- Bitbank latest-60-trade sample: 60 trades over 675.435 seconds, 04:02:23.224–04:13:38.659 UTC; buy taker 8,601.6061 XRP, sell taker 41,044.968 XRP, net taker flow -32,443.3619 XRP. This variable-duration sample is not a fixed-window or 24-hour flow metric and remains model-ineligible.
- XRP Insights ETF holdings delta as of 2026-11-20: four direct-spot funds showed -$7,452,638 / -8,242,683.02 XRP; one direct-spot fund was excluded; two mixed-indirect funds showed +$200,465 / +221,715.84 XRP. This is holdings delta, not issuer/AP cash flow, cash creations/redemptions or exchange execution. Full CSV bytes were not retained under the publisher’s terms; hash-only and model-ineligible.
- Derivatives open-interest dashboards remain methodologically inconsistent; Binance endpoints return HTTP 451 and Bybit endpoints HTTP 403. Do not average external OI aggregates or treat exchange-wallet attribution as tradable reserves.

### Nine-platform coordination and entity research

- The capability map remains `research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_latest.json`. ChatGPT-to-GitHub connector flow was re-tested in this run; repository-level permission reports admin/maintain/push/pull/triage, but token scopes were not introspected. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks remain unverified. No external model dispatch, evidence transfer or red-team review occurred.
- Japan’s SBIC East/Tokyo, Central/Nagoya and West/Osaka are distinct statutory regional companies, not SBI Holdings divisions; no XRP relationship is established. Existing primary-source SBIC resolution remains in the research records.
- Existing Coinbase/Circle/Ripple/SBI/BNY analysis supports a multi-rail stablecoin, custody and distribution network, not an exclusive XRP settlement thesis. RLUSD/USDC distribution, custody and collateral availability are not proof of XRP purchases or XRP-denominated settlement volume.
- ASK Coin remains unresolved beyond Permission Coin (ASK) as a candidate; no XRP relationship is verified. “Actual capital” continues to distinguish cash received, cash-funded XRP purchases, in-kind contributions, debt, warrant proceeds and undrawn facility capacity. Kamilah/Camila Stevenson channel ownership remains unverified; no attributed YouTube inventory is promoted without identity linkage.

### Next concrete actions

1. Preserve PR #1684 and finish event-to-receipt capture: exact publisher URL, publication/event/availability/capture times, raw bytes, SHA-256 and source-independence lineage for each admitted event.
2. Resolve SEC contact configuration only with an approved monitored project identity; capture submissions, companyfacts and primary filing documents without inferring XRP purchases from financing facts.
3. Keep the verified artifact-checkpoint fallback; implement deterministic reconstruction from retained raw artifacts before relying on cache continuity beyond artifact retention.
4. Accumulate genuine sequential point-in-time origins, then run naive, momentum, mean-reversion and volatility baselines, chronological walk-forward tests, calibration and drift evaluation without relaxing sample gates.
5. Reconcile derivatives venue coverage, contract units and timestamps; reconcile ETF issuer creations/redemptions separately from holdings deltas and in-kind flows.
6. Keep #1685 quarantined pending OS sandbox, provider-credential isolation, egress restrictions and task-level authorization. Keep #1686 unreviewed until its six test failures, OpenCode provider egress and local cleanup side effects are reviewed; do not execute its local cleanup script.
7. Revisit merge only after independent approval, verifiable branch protection/sign-off policy, conflict-free exact-head CI, full suite, dependency/security gates and all required checks.

No merge, main write, deployment, cache deletion, local cleanup, secret rotation, Space restart, external model dispatch, Kaggle submission, Databricks write, paper trade, funds transfer or real-money action occurred.

## Historical compatibility anchor

The preserved **Run174** mainline-successor audit remains at [research/xrp_intelligence/20261115T210147Z-run174-mainline-successor-recovery-audit.json](https://github.com/Barrot-Agent/B-Agent/blob/integration/xrp-post-merge-verification-20261121T0002Z/research/xrp_intelligence/20261115T210147Z-run174-mainline-successor-recovery-audit.json). Its contemporaneous main SHA was `5b2a9c46eb878250dfec99190e294909cd5835bf`; this is a historical audit anchor, not the current main SHA. The full earlier handoff history remains available in Git revisions.


## 1. Repository and integration state

- **Main:** `550a647ee7269a704d4600ff337b2145acc90473`; recursive tree: 3,115 entries, not truncated.
- **XRP integration branch:** `integration/xrp-post-merge-verification-20261121T0002Z`; code/test change commit: `b85d5ee5f7703cb88ddad1764cecd487103bc9cc`. This handoff refresh is a fast-forward documentation update on that commit.
- The integration tree has 3,127 entries, is not truncated, and contains every main path. No main path is missing. The branch-only files are the backfill module, its regression tests and the existing XRP research artifacts.
- **No new branch or PR was created.** The only open workstreams remain:
  - [PR #1684 — XRP integration](https://github.com/Barrot-Agent/B-Agent/pull/1684): draft; blocked.
  - [PR #1685 — A2A credential separation](https://github.com/Barrot-Agent/B-Agent/pull/1685): non-draft; blocked.
- The PRs have no overlapping changed paths. No merge occurred in this run. Last mainline integration merge remains #1673.

## 2. Integrated architecture and implementation status

Barrot V3 remains the preserved execution, orchestration, safety and verification foundation. The XRP work is integrated into the existing repository architecture rather than split into another project.

| Capability | State |
|---|---|
| Scheduled public XRP ingestion (hourly and daily) | EXECUTED on main |
| Content-addressed raw receipts and cross-run receipt index | EXECUTED; GitHub artifact retention is not WORM |
| Point-in-time feature store and quality gates | EXECUTED; cache is derived/evictable |
| Historical artifact-backed feature-store recovery | EXECUTED and VERIFIED in isolated CI |
| Event timeline and counter-hypotheses | EXECUTED; event-to-raw-receipt linkage remains incomplete |
| Naive, momentum, mean-reversion and volatility baselines | IMPLEMENTED; evaluation is currently blocked by history/target alignment |
| Temporal calibration and paired block-bootstrap diagnostics | IMPLEMENTED; not validated on a mature independent XRP cohort |
| PSI feature-distribution drift report | EXECUTED; provisional univariate monitor only |
| Independent shadow cohort and shadow evaluation | NOT IMPLEMENTED |
| Directional forecast authorization | DISABLED |

The current feature-store cache does not automatically rebuild from raw receipts. Raw artifacts are retained for 90 days; routine feature-store checkpoints are 7 days and the daily archive is configured for 90 days. External WORM anchoring and an independent trusted timestamp authority are not configured.

## 3. Latest verification evidence

### Last fully verified code head: `10f039068e06e25c8f465cd035f04e9e3f02285c`

[Exact-head CI run 44973528255](https://github.com/Barrot-Agent/B-Agent/actions/runs/44973528255):
- Full repository suite: **4,563 passed, 1 skipped, 0 failed**; 11 warnings; 32 subtests; 73.20% inclusive coverage; 148.44 seconds.
- Pages build was validation-only.
- [Dependency audit 44973528223](https://github.com/Barrot-Agent/B-Agent/actions/runs/44973528223), [Money audit 44973528229](https://github.com/Barrot-Agent/B-Agent/actions/runs/44973528229) and [conflict integrity 44973528306](https://github.com/Barrot-Agent/B-Agent/actions/runs/44973528306) passed.

### Preserved real-artifact recovery

[Backfill replay and artifact 14734098606](https://github.com/Barrot-Agent/B-Agent/actions/runs/44973528255/artifacts/14734098606) used main ingestion run [44970457568](https://github.com/Barrot-Agent/B-Agent/actions/runs/44970457568):
- 118 records recovered across 11 source lineages.
- 18,113 to 18,231 records; 27 to 28 snapshots.
- 31 downloaded ZIP digests matched GitHub's recorded digests; zero mismatches.
- 34 source receipts (22 retained payloads, 12 digest-only).
- SQLite integrity and point-in-time visibility boundary passed.

Reconciliation SHA-256: `c172130198549293ac39b4886f9026599e992587a38724d1d9476d3217a3313b`.

This is isolated CI evidence, not a production database change. The receipt is a post-append availability bound, not a physical SQLite commit timestamp or independent trusted timestamp.

### New code change awaiting verification

Commit `b85d5ee5f7703cb88ddad1764cecd487103bc9cc` changes the walk-forward target anchor from `data_cutoff + horizon` to `latest_completed_bar_event_time + horizon`. It records the origin bar age, realized event-time horizon and actual availability-to-target lead time. A regression test uses a 13-minute delayed capture. The 100-sample training/OOS gates, embargo and target tolerance were not relaxed.

- [Exact-head PR CI 44975332794](https://github.com/Barrot-Agent/B-Agent/actions/runs/44975332794): in progress at handoff capture.
- [Dependency audit 44975332865](https://github.com/Barrot-Agent/B-Agent/actions/runs/44975332865): in progress.
- Money audit, conflict integrity and fail-closed checks were also triggered for this head.
- The prior head's in-progress full suite is not evidence for this newer code commit.

The new target-anchor behavior is **EXECUTED as a branch change, not yet VERIFIED by exact-head CI**.

## 4. Current main ingestion and prediction readiness

Latest visible successful main ingestion at audit time: [44970457568](https://github.com/Barrot-Agent/B-Agent/actions/runs/44970457568), created 2026-11-22 01:13:48 UTC. Latest visible Cross Analysis: [44973386575](https://github.com/Barrot-Agent/B-Agent/actions/runs/44973386575), created 01:51:24 UTC. No newer main ingestion was visible at 02:20 UTC; the expected 02:03 hourly run had not appeared in the inventory.

Run449704:
- 34 receipts: 22 retained payloads, 12 digest-only.
- 18 source failures; 23 raw-only sources.
- 18,113 feature records across 27 snapshots; latest snapshot 106 eligible and 384 excluded features.
- 150 event records; 117 scenarios.
- SEC capture: 3 failures, zero raw SEC receipts and zero filing events.
- Drift report generated: SHA-256 `57e7e2b1c5aad1007a35011edec5d80492901deeddaed05d361832e30463cd91`.
- Walk-forward forecast count: **zero**; status `PARTIAL_OR_BLOCKED`.
- OKX same-venue USD-normalized top-of-book mid: `$0.9308639755` at 01:14:05.070 UTC; 1.1724 bps spread, 11.324-second maximum component age and 1.399-second component skew. Four top-of-book features only, one publisher-independence group; not consolidated depth.

The 1h evaluator requires 100 training samples and 100 genuine out-of-sample origins. The current historical Binance bars share one availability timestamp; most of the Coinbase historical batch also shares one capture timestamp. Only about 25 sequential capture origins are available. The target-anchor fix addresses the delayed-bar mismatch, but the 100-origin minimum remains unmet. Continue accumulating real sequential captures; do not manufacture origins or loosen point-in-time gates.

## 5. Current market observations — research only, model-ineligible

Dynamic public pages observed on 2026-11-22; publisher bytes were not retained and no raw SHA-256 receipt was created:
- [CoinGlass XRP spot page](https://www.coinglass.com/currencies/XRP/spot): page displayed about $0.9310, 24h range $0.8591–$0.9386, spot volume $678.38M, futures volume $2.72B, open interest $1.78B, funding 0.0059%, liquidations $17.22M (80% longs), and November 20 ETF flow of -$5.0M. Its live page did not expose an exact capture timestamp.
- [Liqwall XRP OI](https://liqwall.com/open-interest/xrp): explicitly timestamped 01:42 UTC, November 22, at $863M OI, -3.1% over 24h; 30-day range $863M–$1.49B. This is about half CoinGlass's $1.78B. Do not average: exchange coverage, contract multipliers, quote units and aggregation methodology must be reconciled first.
- [CryptoKeyhole ETF page](https://cryptokeyhole.com/etf-flows/xrp/) reported a partial November 20 outflow of 2,659,361 XRP (about $2.4M), from 2 of 3 funds, while awaiting Franklin. The same page showed a “latest issuer file” date of November 23 despite a November 21 update timestamp; this forward-dated field is a temporal-integrity warning.
- [Alpha Finance](https://alphafinance.io/etf/xrp/), [ByKaranteli](https://bykaranteli.com/etf/xrp) and CoinGlass displayed about $5.0M outflow across broader five-fund coverage. These dashboards may reuse the same issuer files and are not independent confirmations. Obtain issuer files and reconcile dates, holdings, shares and in-kind activity before admission.

## 6. Institutional and entity identity research

### Japan SBIC — primary identity resolved

These are three separate Japanese companies, not SBI Holdings divisions or subsidiaries:
- **SBIC East Japan:** Tokyo Small and Medium Business Investment & Consultation Co., Ltd. — https://www.sbic.co.jp/company/profile/
- **SBIC Central Japan:** Nagoya Small and Medium Business Investment & Consultation Co., Ltd. — https://www.sbic-cj.co.jp/company/about/
- **SBIC West Japan:** Osaka Small and Medium Business Investment & Consultation Co., Ltd. — https://www.sbic-wj.co.jp/profiles/profile/

Each was established in 1963 under Japan's Small and Medium Business Investment & Consultation Co. Act. Tokyo's official FAQ says it originally received partial national-government capital but is now a private corporation conducting independent investment; it is a statutory policy-implementation institution, not a government financial institution. Tokyo's profile lists 18 prefectures and shareholders including local governments, chambers of commerce, financial institutions and companies. The companies identify one another as sister companies. Primary source: https://www.sbic.co.jp/.

### Ripple, SBI, Coinbase, Circle and BNY

- **SBI VC Trade / Ripple:** SBI Holdings' official June 24, 2026 release says SBI VC Trade began handling RLUSD under its Japanese-law Type IV electronic payment instrument classification. The issuer is Standard Custody & Trust Company, a Ripple subsidiary. SBI VC Trade already handled USDC from March 2025. https://www.sbigroup.co.jp/news/pr/2026/0624_16424.html.
- **Coinbase / Ripple:** Ripple's October 28, 2026 release says RLUSD became available on Coinbase Prime, Coinbase Exchange and Coinbase Retail across XRPL, Base and Ethereum. The release said Coinbase Global Exchange collateral availability would follow; do not record it as live collateral at launch. https://ripple.com/ripple-press/ripple-and-coinbase-partner-to-expand-access-to-rlusd/.
- **BNY / Ripple:** BNY's October 27, 2026 release says it is RLUSD's primary reserve custodian, has a custody relationship with Ripple Prime, and now supports XRP and RLUSD on its Digital Asset Custody platform. Direct mint/redeem and broader tokenized assets are intended future capabilities; tokenized trade finance with C2FO is exploratory and subject to approvals. https://www.bny.com/corporate/global/en/about-us/newsroom/press-release/ripple-expands-strategic-digital-assets-collaboration-with-bny-across-custody-and-tokenized-trade-finance.html.
- **Coinbase / Circle:** USDC remains a separate Coinbase distribution/economic relationship; Reuters described USDC as Coinbase's flagship stablecoin before the RLUSD listing. No direct Ripple-Circle partnership was verified in this review. https://www.reuters.com/legal/transactional/coinbase-adds-ripples-stablecoin-its-exchange-2026-10-28/.
- Counter-hypothesis: institutional stablecoin distribution and custody can grow without proportional XRP-token demand. RLUSD is multi-chain; Coinbase collateral was future at announcement; BNY's trade-finance work is exploratory. Partnership announcements are not XRP purchase volume or XRP settlement volume.

## 7. Exact-phrase and creator-identity status

- **“ASK Coin”:** Permission Coin (ticker ASK) is the best-supported candidate, but no XRP relationship is verified. CoinGecko and DeFiLlama display differing shortened contract representations; preserve the discrepancy. https://www.coingecko.com/en/coins/permission-coin ; https://defillama.com/token/ASK.
- **“actual capital”:** distinguish cash received, cash-funded XRP purchases, in-kind XRP, debt, exercised warrants and undrawn facilities. A registration statement, authorization or facility capacity is not cash received.
- **“SBIC, ChatGPT SBIC”:** SBIC/VOST training evidence does not establish an OpenAI partnership.
- **Camilla/Kamilah Stevenson:** search surfaces multiple same-name YouTube channels and third-party channel aggregators, but no first-party identity-to-channel ownership evidence is verified. Do not attribute videos or merge namesakes; the video inventory remains blocked.

## 8. Nine-platform coordination and security

- **Verified:** ChatGPT-to-GitHub authentication and data flow.
- **Unverified:** Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks. No external model dispatch or data transfer occurred.
- Main is marked protected, but detailed branch-protection inspection returns HTTP 403. The visible fallback ruleset is disabled. CODEOWNERS is `* @Barrot-Agent`, not independent review.
- Space restart, A2A deployment/secret upload and Kaggle submission workflows are manual-only and require explicit YES plus exact-main-SHA/allowlist inputs. Databricks deploy/token-rotation and self-deployment workflows are disabled or quarantined. Release is tag-only. Pages CI is validation-only; repository Pages settings were not readable.
- No merge, deployment, secret rotation, Space restart, external model dispatch, Kaggle submission, Databricks write, paper trade, funds transfer or real-money action occurred.

## 9. Backlog, blockers and next action

- **PR #1684 XRP integration — BLOCKED:** one existing integration PR; draft; no independent approval; branch-protection requirements cannot be verified. Continue this branch; do not create a successor or duplicate.
- **PR #1685 A2A credential security — BLOCKED:** no independent approval; OS sandbox, provider-credential isolation, egress controls and task-level authorization remain outstanding; runner remains quarantined.
- No PR is ready to merge. Do not merge based on a prior head's CI. Recheck exact current-head CI, full suite, dependency/security gates, approvals and automatic side effects before any merge.

**Next concrete actions**
1. Complete exact-head full-suite CI, dependency audit, fail-closed gate and backfill replay on the new walk-forward target-anchor commit and the final handoff commit.
2. Inspect the delayed 02:03 UTC main ingestion when it appears; preserve its receipt and feature-store lineage.
3. Accumulate at least 100 genuine chronological OOS origins; retain the new event-time horizon and actual availability lead fields.
4. Preserve hourly `walk_forward.json` and drift reports for audit; fix event-to-raw-receipt linkage for the 150-event registry.
5. Resolve SEC capture only with an approved monitored identity; reconcile OI contracts and ETF issuer files.
6. Keep forecast issuance disabled until chronological evaluation, all four baseline comparisons, calibration, independent source clusters and drift checks support it.

**Forecasts:** none issued. No outcome exists to score.

## Superseding current-state verification — Run56 / 2026-11-22 02:26 UTC

This section supersedes older repository, CI and ingestion snapshots elsewhere in this rolling handoff. Historical details remain in prior Git revisions. No branch history is rewritten.

### Repository and PR inventory

- Current main: `550a647ee7269a704d4600ff337b2145acc90473`; recursive tree: 3,115 entries, not truncated.
- Existing XRP integration branch: `integration/xrp-post-merge-verification-20261121T0002Z`; immediately preceding handoff head: `14429a848cdc98b1c6378b1b5ecd384285b14b74`; 136 commits ahead, zero behind main; 27 changed files; integration tree: 3,127 entries, not truncated. Compare confirms no main paths are missing.
- PR #1684 remains the one XRP integration workstream, draft, mergeable, no independent reviews. PR #1685 remains the separate A2A credential-security workstream, non-draft, no independent reviews. Their changed-path sets do not overlap. No new PR or branch was created.
- Main is marked protected in repository metadata, but branch-protection details return HTTP 403. The only visible repository ruleset, “Fall Back,” is disabled. Effective required checks and administrator enforcement remain unverified.

### Main ingestion Run56 — EXECUTED and VERIFIED

Main workflow run [44975469065](https://github.com/Barrot-Agent/B-Agent/actions/runs/44975469065) completed successfully on main SHA `550a647`, created 2026-11-22 02:18:26 UTC. Adapter version `xrp-public-market-v3.32`; parser `xrp-public-market-v3.31`.

- 34 source receipts: 22 retained raw payloads, 12 digest-only.
- 18 source failures and 23 raw-only sources.
- Feature-store checkpoint: 18,236 records across 28 snapshots; latest snapshot 123 eligible feature records and 367 excluded records.
- Event timeline: 150 events; scenario set: 117.
- Drift: 0 of 204 candidate features evaluated; status `INSUFFICIENT_DATA`.
- Walk-forward forecasts: 0; status `PARTIAL_OR_BLOCKED`; `forecast_model_eligible=false` and forecast issuance remains disabled.
- SEC capture: three configuration/provider failures, zero raw SEC receipts and zero filing events.
- Same-venue OKX USD-normalized top-of-book mid: `$0.9276701035`; bid `$0.927615552`; ask `$0.927724655`; spread `1.1761 bps`; component skew `0.195 s`; maximum component age `9.615 s`. This is one OKX publisher-independence group and top-of-book only, not consolidated depth or independent cross-venue corroboration.

Run56 artifacts and publisher hashes:
- Raw archive artifact [14735970629](https://github.com/Barrot-Agent/B-Agent/actions/runs/44975469065/artifacts/14735970629), GitHub artifact digest `sha256:3e0d078ea7cc32524bab55f40ae1af40b314b3d2774dca6b9f7da0a041d5a738`; raw artifact tree SHA-256 `73ef1f853deb07fd0f07eeb07ce623bc17c9d1f78654e697ef4ceae4eba63c74`.
- Event artifact [14735357388](https://github.com/Barrot-Agent/B-Agent/actions/runs/44975469065/artifacts/14735357388), digest `sha256:5a9944c4978ff9b15cc5db6d577b212a9d65e87561e8ee2a63313e2232b1579c`.
- Feature-store artifact [14735163274](https://github.com/Barrot-Agent/B-Agent/actions/runs/44975469065/artifacts/14735163274), digest `sha256:013add7ebd73132e6b21aa9802b84df7049be1a04d6abe91ade27e16c18aee87`; seven-day retention.
- Receipt-index artifact [14736100197](https://github.com/Barrot-Agent/B-Agent/actions/runs/44975469065/artifacts/14736100197), digest `sha256:6a9d1a6b2ba0cf67ed9e0cc44f08820baf9ca4b9a9e7a1357b63c35c47a43066`.
- GitHub Actions artifacts are retention-limited, not WORM or independently timestamp-anchored.

### Historical backfill — EXECUTED and VERIFIED in isolated CI

The exact-head PR CI run [44975408837](https://github.com/Barrot-Agent/B-Agent/actions/runs/44975408837) included a successful preserved-real-artifact replay (job 137064077498) using main Run56:
- 118 records recovered across 11 source lineages.
- Isolated database: 18,236 to 18,354 records; 28 to 29 snapshots.
- SQLite integrity passed; one-microsecond point-in-time boundary passed (invisible at 2026-11-22 02:20:57.999999 UTC; visible at 02:20:58.000001 UTC).
- All downloaded historical artifact ZIP digests checked in this replay matched GitHub's recorded digests; zero mismatches.
- Reconciliation SHA-256: `0a8a9858ce6733d183c5031b31574c9f92850dd5a2e458176c7cc9ed5eed24a4`.
- Replay artifact [14735710929](https://github.com/Barrot-Agent/B-Agent/actions/runs/44975408837/artifacts/14735710929), ZIP digest `sha256:ec3c50af84db04f94a3569e9f59be69efce614c180a4c3f9a3d1cb201c6b7e65`.

This is isolated CI evidence; main's database was not modified. The recovery receipt clock is the GitHub API run Date header and represents a post-append availability bound, not a measured physical SQLite commit timestamp or an independent trusted timestamp.

### Exact-head CI on 14429a848 — BLOCKED by one stale handoff assertion

- Full repository suite [44975408837](https://github.com/Barrot-Agent/B-Agent/actions/runs/44975408837): **4,563 passed, 1 failed, 1 skipped**; 11 warnings; 32 subtests; 73.20% coverage; 212.83 seconds.
- The sole failure is `tests/test_run174_mainline_successor_preservation.py::test_run174_mainline_successor_preserves_mainline_and_xrp_mission`. The test's historical audit JSON assertions pass, but its final handoff assertion expects the rolling current-state file to retain the literal `Run174` and the historical main SHA. The prior compaction removed that anchor while preserving earlier detail in Git history. This handoff update restores an explicit, accurate historical anchor; it does not change the historical SHA or claim it is current.
- Pages build passed in validation-only mode.
- Dependency audit [44975408903](https://github.com/Barrot-Agent/B-Agent/actions/runs/44975408903), Money audit [44975408897](https://github.com/Barrot-Agent/B-Agent/actions/runs/44975408897), and conflict integrity [44975408945](https://github.com/Barrot-Agent/B-Agent/actions/runs/44975408945) passed.
- Fail-closed gate [44975408881](https://github.com/Barrot-Agent/B-Agent/actions/runs/44975408881) correctly blocked: PR #1684 is draft; no independent approving review exists; branch protection could not be verified; the exact-head full suite had one failure. No merge was attempted.

The current handoff-only update must receive a new exact-head full-suite run. No prior-head test result is transferable to it.

### Backlog and next action

- **PR #1684 — BLOCKED:** unique, single XRP integration workstream; draft; no independent approval; current exact-head suite has one stale handoff-compatibility failure. Continue the existing branch; do not create a successor or duplicate.
- **PR #1685 — BLOCKED:** unique A2A credential-security workstream; no independent approval; OS sandbox, provider-credential isolation, egress controls and task-level authorization remain outstanding; runner remains quarantined.
- **No PR is ready to merge.** Never bypass required checks or infer branch protection. Re-evaluate exact-head CI, full-suite tests, dependency/security checks, independent approval and workflow side effects before any merge.

**Next concrete action:** verify this handoff update landed on the existing branch, then rerun the full repository suite and fail-closed gate on the resulting exact head. If the historical anchor resolves the sole test failure, proceed to the next evidence blocker: event-to-raw-receipt linkage, followed by genuine chronological out-of-sample accumulation. Keep directional forecast issuance disabled.

**Forecasts:** none issued; no outcome exists to score. No merge, deployment, secret rotation, Space restart, external model dispatch, Kaggle submission, Databricks write, paper trade, funds transfer or real-money action occurred.


## Run11 exact-head verification and research update — 2026-11-22 02:44 UTC

This section supersedes earlier current-state CI and research snapshots. It records the verified state at the time of this update. Web research below was viewed through public pages/search results only; publisher bytes were not downloaded and no SHA-256 raw receipts were created. These observations remain **research-only and model-ineligible** until captured through the scheduled ingestion and linked to canonical receipts.

### Exact-head verification — 0a33e6e7d44e17c8af7536602af74013f199b1da

[PR CI run 44976987720](https://github.com/Barrot-Agent/B-Agent/actions/runs/44976987720) completed successfully on the exact PR head:
- Full repository suite: **4,564 passed, 1 skipped, 0 failed**; 11 warnings; 32 subtests; 73.20% inclusive coverage; 118.59 seconds.
- Core test job: passed.
- Pages build: passed in validation-only mode; no deployment.
- Historical backfill replay job 137068981075: passed against the preserved Run56 main artifacts.
- Dependency audit [44976987847](https://github.com/Barrot-Agent/B-Agent/actions/runs/44976987847): passed all six dependency sources (root runtime, development, integrations, Hugging Face Space, legacy, and PEP 621 pyproject); no known vulnerabilities found.
- Money audit [44976988697](https://github.com/Barrot-Agent/B-Agent/actions/runs/44976988697): passed.
- Conflict-integrity check [44976987676](https://github.com/Barrot-Agent/B-Agent/actions/runs/44976987676): passed.
- Push CI [44976983907](https://github.com/Barrot-Agent/B-Agent/actions/runs/44976983907): core tests and Pages validation passed; the full suite was intentionally skipped on integration-branch push because the PR event is authoritative. The PR run above is the full-suite evidence.
- Fail-closed gate [44976987678](https://github.com/Barrot-Agent/B-Agent/actions/runs/44976987678): correctly blocked; PR #1684 is draft, no independent approving review exists, and branch protection could not be verified. It is read-only and did not merge.

The Run56 replay recovered 118 records across 11 source lineages, from 18,236 to 18,354 records and 28 to 29 snapshots in the isolated CI database. SQLite integrity and the point-in-time visibility boundary passed. Reconciliation SHA-256: `0a8a9858ce6733d183c5031b31574c9f92850dd5a2e458176c7cc9ed5eed24a4`. Main's database was not modified.

### New market-structure cross-check — 2026-11-21 to 2026-11-22

- [CoinGlass XRP futures dashboard](https://www.coinglass.com/currencies/XRP/futures) displayed XRP at approximately $0.9301, +2.28% over 24h; $0.8591–$0.9386 range; $685.95M spot volume; $2.74B futures volume (4.0x spot); $1.78B open interest; 0.0053% funding; $17.26M 24h liquidations with 80% longs; and -$5.0M ETF net flow for November 20. The same page describes OI down 56.4% from $4.1B on September 23 to about $1.8B. Its spot/futures net-flow summary and timeframe table are not internally aligned; do not ingest those flow fields without raw endpoint and metric-definition reconciliation.
- [CoinDesk, November 21](https://www.coindesk.com/markets/2026/11/21/xrp-falls-10-as-long-bets-unwind-and-etf-assets-slip-below-usd1-billion) reported an approximately 9% decline to $0.87, about $18M in liquidations with roughly 94% longs, $4.97M November 20 ETF outflows, about $990M ETF net assets and $1.78B cumulative net inflows. Net assets are market value; cumulative net inflows are a different measure. The 94% long-liquidation share and CoinGlass's 80% are different captures/windows and are not averaged.
- [Liqwall](https://liqwall.com/open-interest/xrp) reported $865M all-exchange OI at 00:32 UTC November 22, down 2.9% over 24h, versus CoinGlass's $1.78B. This roughly 2.06x discrepancy remains unresolved; exchange coverage, contract units, multipliers, inclusion of inverse contracts and aggregation methodology must be reconciled before combining.
- [XRP Insights exchange-wallet page](https://xrp-insights.com/exchange-balances) reported 21.96B XRP across 707 XRPL wallets attributed to 24 exchanges at 08:01 UTC November 21, with same-wallet balances down 299.8M XRP over seven days and 650.7M over 30 days. The provider explicitly includes cold-labeled wallets and says its total is not tradable float. Treat as attributed custody/exchange-wallet inventory, not executable exchange reserves; raw bytes and address-level attribution are not yet captured by Barrot.
- Main Run56's separate OKX USD-normalized top-of-book snapshot at 02:18:51 UTC November 22 was $0.9276701035 with a 1.1761 bps spread, 0.195-second component skew and 9.615-second maximum component age. It is one publisher group and top-of-book only, not consolidated depth.

### Capital, stablecoin, custody and institutional relationships

#### Evernorth — separate actual cash, XRP in kind, debt, warrant proceeds and equity-line capacity

Primary sources: [SEC 424B3 prospectus supplement](https://www.sec.gov/Archives/edgar/data/2092592/000162828026073931/evernorth-424stickerresalea.htm) and [SEC S-1](https://www.sec.gov/Archives/edgar/data/2092592/000162828026068609/xrpn-20261030.htm).

- Closing proceeds: approximately **$272.6M gross cash**, comprising $224.6M private-placement cash and $48.0M trust-account release, before transaction expenses. Investors also contributed approximately **388,910,554 XRP in kind**. Do not treat the XRP contribution as cash or open-market buying.
- Historical cash-funded XRP purchase: $214,049,995 of advance-funding cash was used to acquire **84,365,876.3625 XRP** at a reported average of **$2.53657058** per XRP in October–November 2025. This is the clearest disclosed cash-funded XRP acquisition; it is not a November 2026 purchase.
- Convertible note: $30.0M principal, 4.00% senior unsecured PIK notes due 2031; the later 424B3 reports **$29.0M net cash proceeds after a $1.0M advisor fee**. The stated use includes general corporate purposes and possible XRP acquisition, not proof all proceeds bought XRP.
- Warrant exercises: 3,073,366 warrants exercised for cash from October 12 through November 9, 2026, producing **$35.3M gross proceeds**; 8,666,279 warrants remained. These are corporate cash proceeds, not evidence of XRP purchases.
- ELOC: right, not obligation, to sell up to 5,218,935 Class A shares to Cantor at generally 97% of applicable VWAP, subject to volume, price and ownership limits. The $0.5M commitment fee is fully earned/non-refundable. Facility capacity is not cash received; actual proceeds depend on notices and completed purchases.
- Ripple-related credit: the Company Facility was increased to $10M and $9.7M was borrowed as of October 7, 2026. Evernorth's separate $1M Ripple facility had no borrowing as of September 30. These are related-party debt/liquidity support, not external equity capital or XRP spot demand.
- At September 30, Evernorth reported about $0.1M unrestricted cash, a $10M net working-capital deficit and $185.6M accumulated deficit. Those are dated historical balances, not a current cash balance.
- XRP contributed by Ripple and other investors, internal transfers to Pathfinder, the cash-funded purchase, note proceeds, warrant proceeds and ELOC capacity must remain separate ledger categories. No total should be labeled “actual capital deployed into XRP” without transaction-level use-of-proceeds evidence.

#### Coinbase, Circle, Ripple and SBI — multi-rail alignment, not an exclusive XRP thesis

- [Ripple's October 28 announcement](https://ripple.com/ripple-press/ripple-and-coinbase-partner-to-expand-access-to-rlusd/) and [Coinbase's announcement](https://www.coinbase.com/blog/rlusd-is-now-available-on-coinbase) confirm RLUSD availability on Coinbase Prime, Coinbase Exchange and the retail app, with deposits/withdrawals on XRPL, Ethereum and Base. One-to-one USD conversion is supported. RLUSD collateral for Coinbase Global Exchange customers was described as a later phase, not a feature confirmed live at launch. Ripple said it would provide liquidity on Base. RLUSD support on XRPL does not itself prove XRP is used as a bridge asset.
- [Circle's October 16 economics disclosure](https://www.circle.com/blog/the-economics-of-usdc-and-why-our-partners-win) says that in H1 2026 it generated about $1.4B revenue, paid about $819M (59 cents per revenue dollar) in distribution/transaction costs, reinvested about $473M (34 cents) and retained about 7 cents net profit per dollar. Circle identified Coinbase as its largest and longest-standing partner and said Coinbase's average USDC balances in its products reached $20B in Q2, up 44% year over year. These are Circle's own reported figures.
- [SBI's June 9, 2025 announcement](https://www.sbigroup.co.jp/news/2025/0609_15491.html) says SBI Holdings and SBI Shinsei Bank each purchased $25M of Circle shares at its IPO, $50M combined. [Circle's March 2025 announcement](https://www.circle.com/pressroom/circle-strengthens-commitment-to-japan-with-new-investment-and-expanded-usdc-access) confirms the SBI joint venture and SBI VC Trade's full USDC launch in Japan. SBI later established SBI Circle Holdings as the JV entity.
- [Circle's September 16, 2026 Arc mainnet announcement](https://investor.circle.com/news/news-details/2026/Circle-Launches-Arc-Mainnet-an-Economic-Operating-System-for-the-Internet/default.aspx) names SBI Group in the founding validator cohort and Coinbase among exchanges providing Arc access. SBI says it will participate in Arc operation/governance and expects to use USDC and JPYSC, a trust-type yen stablecoin issued by SBI Shinsei Trust. Arc is a separate USDC-centric L1; it is not XRPL.
- [SBI VC Trade's June 24, 2026 RLUSD notice](https://www.sbigroup.co.jp/news/pr/2026/0624_16424.html) confirms RLUSD listing in Japan through the SBI/Ripple relationship. [SBI Ripple Asia's February 26, 2026 PoC](https://www.sbigroup.co.jp/news/pr/2026/0226_16145.html) describes tokenized deposits/deposit-based digital money using MoneyTap and a token issuance platform with XRPL as the contemplated ledger. That is not proof XRP is the bridge asset or that the PoC is production payment volume.
- [BNY's October 27, 2026 announcement](https://www.bny.com/corporate/global/en/about-us/newsroom/press-release/ripple-expands-strategic-digital-assets-collaboration-with-bny-across-custody-and-tokenized-trade-finance.html) says BNY is RLUSD's primary reserve custodian, has a custody relationship with Ripple Prime, and now supports XRP and RLUSD on its Digital Asset Custody platform while exploring tokenized trade finance. Custody support is not evidence of BNY market purchases.
- [Ripple's October 28 corporate update](https://ripple.com/ripple-press/ripple-reports-banner-year-approaching-900m-product-revenue-run-rate-signs-multi-solution-partnerships/) claims a $900M annualized product-revenue run rate, over $16T transactions enabled in 2025, more than 85 licenses and 1,700+ institutions/corporates/enterprises. These are Ripple corporate claims and do not equal XRP-denominated settlement volume or token demand.

The combined evidence supports a **multi-rail SBI strategy**: SBI has strategic/equity relationships with both Ripple and Circle, distributes both RLUSD and USDC, operates in XRPL-related initiatives, and participates in Circle's Arc validator set. Do not collapse these into an exclusive XRP adoption thesis. Coinbase similarly distributes USDC and RLUSD and participates in Arc's ecosystem; its RLUSD listing is a direct commercial relationship, not proof that Coinbase routes all stablecoin or payment flows through XRP.

#### SBIC identity, ASK token and YouTube attribution

- Japan's three SBIC entities remain distinct: Tokyo/SBIC East, Nagoya/SBIC Central and Osaka/SBIC West. Primary company profiles: [East](https://www.sbic.co.jp/company/profile/), [Central](https://www.sbic-cj.co.jp/company/about/) and [West](https://www.sbic-wj.co.jp/profiles/profile/). SBIC East's [March 5, 2026 ChatGPT seminar](https://www.sbic.co.jp/seminar/20260305js/) identifies a Microsoft speaker and ChatGPT demonstration; it does not establish an OpenAI contract or partnership. Do not conflate any of these companies with SBI Holdings.
- The identifiable ASK candidate is **Permission Coin (ASK)**, not an established XRP token. [Permission's current contract docs](https://docs.permission.ai/ask-token/contract-addresses) list Base `0xBB146326778227A8498b105a18f84E0987A684b4` and Polygon `0xaA3717090CDDc9B227e49d0D84A28aC0a996e6Ff`; its [January 2025 launch post](https://www.permission.ai/blog/ask-is-now-live-on-base-eeaba) lists a different Base address `0x79322cee6c90735b967d2396b9adc392915aebb6`. Treat this as an unresolved contract-version/migration discrepancy. No verified Ripple/XRP relationship was found.
- A candidate [Kamilah Stevenson YouTube channel](https://www.youtube.com/@KamilahStevensonXrpStocks) and attributed videos surfaced, but a channel-name/video-intro spelling difference (Kamilah vs Camila) remains unresolved by primary identity evidence. **No creator identity merge and no video inventory were made.**
- Exact-phrase searches for “ASK Coin”, “actual capital” and “SBIC, ChatGPT SBIC” remain query-specific research tasks. The SEC accounting analysis above is the current primary-source “actual capital” reconciliation; no evidence supports relabeling in-kind XRP or undrawn facilities as cash capital.

### Prediction readiness and platform coordination

- Historical backfill is verified in isolated CI; main's feature store is unchanged.
- Scheduled market ingestion is executed, but Run56 still reports 18 source failures, 23 raw-only sources, 0 of 204 drift candidates evaluated, 150 events with no raw-source hashes, and zero walk-forward forecasts.
- The current 1h evaluator anchors the target at the latest completed bar event time and records the variable availability-to-target lead. This is **not** the same as a fixed one-hour horizon from the data cutoff. Keep the semantics explicit; do not calibrate or compare these as fixed-cutoff 1h forecasts. Minimum training/OOS origin gates remain unmet.
- Forecast issuance remains disabled. No directional forecast or scored outcome exists.
- ChatGPT-to-GitHub is the only verified platform data flow. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks remain unverified; no external model dispatch occurred.

### Governance and next action

- Main remains `550a647ee7269a704d4600ff337b2145acc90473`, protected=true. The visible protection metadata exposes no required status-check contexts; direct branch-protection details return HTTP 403. CODEOWNERS is `* @Barrot-Agent`, which is not independent review. The fail-closed gate correctly refuses merge.
- PR #1684: **BLOCKED** — draft, no independent approval; exact-head full suite and backfill pass, but branch-protection verification and independent review remain absent.
- PR #1685: **BLOCKED** — separate A2A credential-security workstream, non-draft, exact-head CI and A2A Worker Tests passed on its current head, but no independent approval. OS sandboxing, provider-credential isolation, egress controls and task-level action restrictions remain outstanding; runner remains disabled.
- No new branch/PR was created. No merge, deployment, secret rotation, Space restart, external model dispatch, Kaggle submission, Databricks write, paper trade, funds transfer or real-money action occurred.

**Next concrete action:** keep the existing XRP branch; prioritize event-source capture and exact raw-receipt linkage, legitimate SEC capture configuration, and accumulation of sequential point-in-time market origins. Reconcile the CoinGlass/Liqwall OI coverage and exchange-wallet attribution before model admission. Do not loosen the 100-origin gates or issue a directional forecast.


## Run11 follow-up — exact-head verification on 2e32d875 / 2026-11-22 02:50 UTC

The prior section's pending exact-head statement is now resolved for commit `2e32d8756645199bfecbb790def7750e2ce6faaa`:

- [PR CI run 44977413192](https://github.com/Barrot-Agent/B-Agent/actions/runs/44977413192): **4,564 passed, 0 failed, 1 skipped**, 11 warnings, 32 subtests, 73.20% inclusive coverage, 119.30 seconds. Exact head `2e32d875`.
- [Dependency audit 44977413249](https://github.com/Barrot-Agent/B-Agent/actions/runs/44977413249): passed all six dependency sources; no known vulnerabilities reported.
- [Money audit 44977413185](https://github.com/Barrot-Agent/B-Agent/actions/runs/44977413185): passed.
- [Conflict-integrity check 44977413236](https://github.com/Barrot-Agent/B-Agent/actions/runs/44977413236): passed.
- Pages build validation passed; deployment was not run.
- Preserved Run56 artifact replay passed (job 137070292411): 118 records/11 lineages recovered in an isolated copy; 18,236 to 18,354 records; 28 to 29 snapshots; SQLite and point-in-time visibility passed. Main database unchanged.
- [Fail-closed gate 44977413191](https://github.com/Barrot-Agent/B-Agent/actions/runs/44977413191) correctly returned BLOCKED: PR #1684 is draft, no independent approving review exists, and branch-protection details could not be verified. It did not approve or merge.

The current exact-head state is now recorded in the latest nine-platform map at [research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_latest.json](https://github.com/Barrot-Agent/B-Agent/blob/integration/xrp-post-merge-verification-20261121T0002Z/research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_latest.json). Its `run11_current_state` entry supersedes older current-state snapshots without rewriting historical run records or the historical `merge_decision` sentinel.

### Creator identity red-team update

The June 11, 2026 [XRPTracer/iHeart episode with Dr. Kamilah Stevenson](https://www.iheart.com/podcast/1333-the-xrptracer-podcast-284128923/episode/crypto-panics-with-dr-kamilah-stevenson-336576069/) is a first-party guest appearance. In the transcript, the guest introduces herself as Camila/Camilla and verbally identifies her YouTube presence as “doctor Camilla Stevenson”; she also explicitly warns that fake pages exist. The candidate channel `@KamilahStevensonXrpStocks` has not been cross-linked to that stated handle through primary evidence. Similar names and video introductions are insufficient to establish channel ownership. **Keep the guest identity separate from the candidate channel; do not inventory or attribute that channel's videos.**

### Current disposition

PR #1684 remains draft and blocked despite the exact-head full-suite pass. PR #1685 remains a separate, non-draft A2A security workstream; its exact-head full suite and A2A Worker Tests passed on `e512f4e6`, but it has no independent approval and the runner-isolation controls remain incomplete. No PR is ready to merge.

This handoff/map refresh is documentation/evidence-only. Its new commit must receive its own exact-head CI and artifact replay; results from parent `2e32d875` are not transferable to the new commit. No main write, merge, deployment, secret change, external model dispatch, Kaggle submission, Databricks write, paper trade or real-money action occurred.


## Run11 continuation — 2026-11-22 03:06 UTC

This current-state section supersedes earlier repository, exact-head, ingestion-cache and merge-gate snapshots in this handoff. It does not rewrite prior run history.

### Repository recheck

- Main remains `550a647ee7269a704d4600ff337b2145acc90473`.
- Main recursive tree: **3,115 entries**, not truncated. Integration tree at `c61c43c95c768dd60632a0e5cd201902f2a973d4`: **3,127 entries**, not truncated; zero main paths are missing.
- Existing XRP branch: **139 commits ahead, zero behind**, 27 changed files. PR #1684 is the sole XRP integration PR. No new branch or PR was created.
- Open PR inventory remains exactly #1684 and #1685. Their changed-path sets do not overlap.
- Main is unchanged. The existing V3 architecture and branch history are preserved.

### Exact-head verification — c61c43c95c768dd60632a0e5cd201902f2a973d4

- [PR CI 44977982045](https://github.com/Barrot-Agent/B-Agent/actions/runs/44977982045): **4,564 passed, 0 failed, 1 skipped**, 11 warnings, 32 subtests, 73.20% coverage, 119.28 seconds. Full-suite job completed successfully on this exact head.
- The exact-head historical replay job **137072032833** passed using preserved Run56 artifacts: 118 records across 11 source lineages; 18,236 to 18,354 records; 28 to 29 snapshots; SQLite integrity and the point-in-time visibility boundary passed. Artifact ZIP digests matched GitHub's recorded digests. Reconciliation SHA-256: `95de7453fea5d55bd54564210738beedc7729171203ab82f778cc93c7b4f0eb4`. The main feature store was not modified.
- [Dependency audit 44977982030](https://github.com/Barrot-Agent/B-Agent/actions/runs/44977982030): all six sources passed (runtime, development, integrations, Hugging Face Space, legacy and PEP 621); no known vulnerabilities found.
- [Money audit 44977982061](https://github.com/Barrot-Agent/B-Agent/actions/runs/44977982061): passed.
- [Conflict integrity 44977982078](https://github.com/Barrot-Agent/B-Agent/actions/runs/44977982078): passed.
- [Pages validation](https://github.com/Barrot-Agent/B-Agent/actions/runs/44977982045): passed in validation-only mode; no deployment.
- [Fail-closed gate 44978466149](https://github.com/Barrot-Agent/B-Agent/actions/runs/44978466149): failed as designed. PR #1684 is draft and the branch-protection endpoint returned HTTP 403. No merge was attempted. GitHub's PR review endpoint returned no formal review records at inspection.

These results apply to `c61c43c`, not to any subsequent documentation commit created by this handoff refresh. The new handoff commit must receive its own exact-head checks.

### Latest verified main ingestion — Run56

[Scheduled ingestion run 44975469065](https://github.com/Barrot-Agent/B-Agent/actions/runs/44975469065) completed successfully at 2026-11-22 02:18:26 UTC on main. The workflow's hourly cron is minute 03; the 03:03 UTC scheduled run was not yet visible in the workflow inventory at this 03:06 UTC inspection.

- 34 source receipts: 22 retained raw payloads and 12 digest-only receipts.
- 18 source failures; 23 raw-only sources.
- Feature-store history: 18,236 records, 28 snapshots; 490 delta records. Latest snapshot: `6f96f891d0d295045ec27063d65457003d3b56b92ebedafe4939d4925c4e0455`, status verified, 123 eligible records and 367 excluded.
- Event timeline: 150 events and 117 scenarios, but `event_timeline_receipt_complete=false`; no event-to-raw-source hash linkage is verified. External receipt anchoring remains `NOT_ANCHORED`.
- Drift: 204 candidate features, zero evaluated; status `INSUFFICIENT_DATA`.
- Walk-forward forecast count: zero. Forecast status: `NOT_ISSUED`. No directional forecast was issued.
- SEC capture: zero raw receipts, three source failures; no filing events were promoted.
- OKX USD-normalized top-of-book snapshot at 02:18:51.066 UTC: mid **$0.9276701035**, spread **1.1761 bps**, component skew **0.195 s**, maximum component age **9.615 s**. One publisher group; depth levels were not normalized. This is a timestamped historical snapshot, not a live quote or consolidated depth.
- The run summary reports `raw_only_source_count=23` while its inline `raw_only_source_ids` array is empty. Inspect the separately retained raw-only artifact before treating source identities as resolved.
- The feature-store restore used trusted prior per-run checkpoint `44970457568`. The new per-run checkpoint artifact was uploaded with seven-day retention; the daily/manual archive path is configured for 90 days.

**New storage blocker:** the GitHub Actions cache-save step reported that the configured cache budget was exhausted and the cache had become read-only. The step is `continue-on-error`, so Run56 still completed and its per-run feature-store artifact was uploaded (artifact ZIP SHA-256 `013add7ebd73132e6b21aa9802b84df7049be1a04d6abe91ade27e16c18aee87`). No cache deletion, retention increase, billing change or other storage mutation was attempted. The fallback checkpoint path currently prevents immediate data loss, but raw-artifact-to-feature-store rebuild remains unimplemented and the seven-day per-run retention is a continuity risk if cache writes remain unavailable.

Artifact receipts:
- Raw-source bundle: [artifact 14735970629](https://github.com/Barrot-Agent/B-Agent/actions/runs/44975469065/artifacts/14735970629), SHA-256 `3e0d078ea7cc32524bab55f40ae1af40b314b3d2774dca6b9f7da0a041d5a738`.
- Cross-run receipt index: [artifact 14736100197](https://github.com/Barrot-Agent/B-Agent/actions/runs/44975469065/artifacts/14736100197), SHA-256 `6a9d1a6b2ba0cf67ed9e0cc44f08820baf9ca4b9a9e7a1357b63c35c47a43066`.
- Event bundle: [artifact 14735357388](https://github.com/Barrot-Agent/B-Agent/actions/runs/44975469065/artifacts/14735357388), SHA-256 `5a9944c4978ff9b15cc5db6d577b212a9d65e87561e8ee2a63313e2232b1579c`.
- Feature-store checkpoint: [artifact 14735163274](https://github.com/Barrot-Agent/B-Agent/actions/runs/44975469065/artifacts/14735163274), SHA-256 `013add7ebd73132e6b21aa9802b84df7049be1a04d6abe91ade27e16c18aee87`.

### Merge-gate defect and PR backlog

- **PR #1684 — XRP integration: BLOCKED.** Draft; 139 ahead/0 behind; 27 changed files; zero formal review records; exact-head full suite, dependency audit, Money audit, conflict integrity and preserved-artifact replay passed on `c61c43c`. It remains unmergeable under the user's stated governance because it is draft, independent approval is absent, and effective branch-protection settings cannot be verified.
- **PR #1685 — A2A credential separation: BLOCKED.** Non-draft according to the current PR API; head `e512f4e6d66c1575186d00b60852c93caba687e0`; five commits ahead/zero behind; nine changed files; no overlap with #1684; zero formal review records. Its prior exact-head full suite and worker tests passed, but the runner remains quarantined pending independent security review, OS sandboxing, provider-credential isolation, egress controls and task-level action restrictions.
- **Confirmed fail-closed false-positive on #1685:** current GitHub PR metadata says `draft=false`, but its latest gate rerun [44955747971, attempt 5](https://github.com/Barrot-Agent/B-Agent/actions/runs/44955747971) reports “PR is still draft.” The main-branch `.github/workflows/barrot-gated-merge.yml` still uses `jq -r '.draft // true'`; jq's `//` operator treats explicit Boolean `false` as absent and substitutes `true`. The existing #1684 integration branch contains the explicit-presence fix (`if has("draft") then (.draft|tostring) else "unknown" end`) and regression tests. This is a confirmed false positive in main's current gate implementation, not evidence that #1685 is actually draft. The gate also independently reports **no independent approving review** and **branch protection could not be verified**; those remain genuine blockers. Do not alter #1685 or create a duplicate PR to carry this fix.
- Main branch protection is marked protected, but the protection endpoint returns HTTP 403. The visible fallback ruleset remains disabled. Main CODEOWNERS is `* @Barrot-Agent`, not independent review. Do not infer required checks or bypass protection.
- No PR is ready to merge. No source PR is superseded or duplicate; neither should be closed.

### Next concrete actions

1. Keep the existing XRP integration PR; obtain independent review and verifiable branch-protection settings before any merge consideration.
2. Verify the next scheduled main ingestion and confirm the checkpoint restore still works with cache writes unavailable.
3. Inspect the raw-only artifact and reconcile the 23-source count versus empty inline ID array.
4. Implement/verify a reproducible raw-artifact-to-feature-store rebuild or another retention-safe checkpoint path without increasing storage spend or deleting user data.
5. Link each curated event to exact raw source URL, capture timestamp and SHA-256; resolve approved SEC contact configuration.
6. Reconcile CoinGlass/Liqwall OI methodology and exchange-wallet attribution before feature admission.
7. Accumulate true point-in-time origins, then run leakage-safe naive/momentum/mean-reversion/volatility baselines, calibration and drift evaluation. Keep the minimum-origin gates unchanged.

**Forecasts:** none issued; no outcome exists to score. No merge, deployment, secret rotation, Space restart, external model dispatch, Kaggle submission, Databricks write, paper trade, funds transfer or real-money action occurred.


---

## Run 11 continuation — 2026-11-22 03:59 UTC

### Repository audit and integration state

- Main remains `550a647ee7269a704d4600ff337b2145acc90473`; its complete recursive tree contains 3,115 entries.
- Existing XRP integration branch `integration/xrp-post-merge-verification-20261121T0002Z` was at `7b9973611ee149b8dcf06ac7d9972dc671b39ec0` before this handoff-only update. It is 140 commits ahead and zero behind main. Its recursive tree contains 3,127 entries; no main-tree path is missing.
- PR #1684 has 27 changed files and remains draft. PR #1685 has 9 changed files and is non-draft. Their changed-path sets do not overlap. No new branch or PR was created.
- Main's post-merge CI for `550a647` is verified: run [44839159044](https://github.com/Barrot-Agent/B-Agent/actions/runs/44839159044), 4,534 passed, 1 skipped, 11 warnings, 32 subtests. The main-branch dependency and Money audits passed. The Pages deployment run [44839139424](https://github.com/Barrot-Agent/B-Agent/actions/runs/44839139424) was an automatic workflow side effect of the preceding merge, not a deployment initiated in this run.
- On exact PR #1684 head `7b99736`, full-suite run [44979537921](https://github.com/Barrot-Agent/B-Agent/actions/runs/44979537921) passed 4,564 tests, 1 skipped, 11 warnings, 32 subtests; inclusive coverage was 73.20%, and the required 62% floor passed. The additional per-package coverage gates for monetization, rendering, smart-agent, memory-palace, orchestration and XRP feature-store components passed.
- Exact-head dependency audit [44979537982](https://github.com/Barrot-Agent/B-Agent/actions/runs/44979537982) passed all six configured audit sources without reported vulnerabilities. Money audit [44979537910](https://github.com/Barrot-Agent/B-Agent/actions/runs/44979537910), conflict-integrity [44979537936](https://github.com/Barrot-Agent/B-Agent/actions/runs/44979537936), and Pages validation passed.
- Exact-head preserved-artifact replay restored 118 historical records across 11 source lineages. It reconciled 27 main-ingestion run IDs and verified 31 downloaded ZIP digests. Feature-store history advanced from 18,236 to 18,354 records and from 28 to 29 snapshots in the isolated replay. Reconciliation SHA-256: `896068c10f7f669178a22b87355799784d9ddda4364bb8ccd143e82c0e1bcad8`. Main's database was not modified.
- PR #1684's fail-closed gate [44979538019](https://github.com/Barrot-Agent/B-Agent/actions/runs/44979538019) remains blocked: the PR is draft and branch protection could not be verified. Its review list is empty. Main still contains the jq `.draft // true` false-value bug; the integration branch contains the explicit-presence correction, but it has not reached main. The visible fallback ruleset is disabled, the protection endpoint remains inaccessible (403), and CODEOWNERS does not provide an independent reviewer. No bypass or merge was attempted.
- PR #1685 remains blocked despite its prior exact-head test and worker-test successes: no independent approving review, and the main-branch draft-detection defect causes a false-positive gate result for its non-draft metadata. Its nine paths do not overlap #1684. Keep it quarantined pending security review and an independently verifiable merge gate.

### Main XRP ingestion Run57 — executed and artifact-checked

Latest completed main ingestion: [44979814130](https://github.com/Barrot-Agent/B-Agent/actions/runs/44979814130), captured 2026-11-22 around 03:16 UTC.

- 34 source receipts; 22 retained raw payloads; 12 digest-only receipts; 18 source failures; 23 entries in the global raw-only source artifact.
- The downloaded raw archive SHA-256 is `aa8078fab4857c3130d467138d550a05af553fe551c36ca3bfc06be2aa8953e0`. All 22 payload filenames matched the SHA-256 of their actual payload bytes. The receipt manifest and receipt chain each contain 34 records; cross-run sequence is 29 and continuity checks passed. There is no independent WORM/external timestamp anchor.
- Feature-store artifact SHA-256: `8d46f3fd01ed2e43f4641f2d08477c18f5941698877130a824ce0f4363fb23af`. SQLite `integrity_check` returned `ok`. It contains 18,359 feature records across 29 snapshots. The newest snapshot contains 123 eligible records from 12 source IDs and five independent spot publisher groups.
- Drift: zero of 204 candidate features evaluated. Walk-forward forecast origins: zero. Forecasts issued: zero.
- Event timeline artifact SHA-256: `62eb3789a6e7805224f2d0f5eea00c22c7e0fc87b1f95e602ea9d02713d9c586`. It contains 150 events and 117 scenarios, but zero event rows have a raw-source SHA-256 or receipt ID. All 150 have a source URL and capture timestamp. The registry's newest capture is 2026-11-19 15:16:42 UTC; it is stale and receipt-incomplete. None of these events is model-eligible.
- The earlier apparent `raw_only_source_ids: []` discrepancy is resolved: that field is scoped to the weekly-source-policy summary, not the global raw-only registry. The actual `raw_only_sources.json` artifact contains 23 entries. Do not treat this as a missing-ID defect.
- Cache quota remains exhausted: the run restored the prior trusted checkpoint from main run `44975469065`, but cache save failed. The hourly raw artifact is retained for 90 days; the feature-store artifact is retained for 7 days; the daily archive step did not run in this hourly execution. No cache deletion, billing change or retention mutation was attempted. Rebuilding the feature store from retained raw artifacts is still an unimplemented continuity fallback.

#### Spot and order-book snapshot

The latest eligible spot snapshot is timestamped approximately 2026-11-22 03:16:01 UTC:

- Bitstamp mid: `0.916725 USD`
- Coinbase mid: `0.916750 USD`
- Kraken mid: `0.916805 USD`
- OKX USD-normalized mid: `0.916817 USD`
- Bitbank mid: `145.6015 JPY`

Across the four USD-convertible venues, observed 24-hour lows were approximately `0.8591–0.8597 USD` and highs `0.9368–0.9389 USD`; venue windows are not perfectly synchronized. This is a descriptive rebound from the low, not a forecast.

Displayed 10-basis-point depth was materially different by venue: Coinbase about `174k bid / 529k ask USD`; Bitstamp `175k / 239k USD`; Kraken `294k / 390k USD`; OKX `131k / 121k USDT`; Bitbank `14.67m / 4.55m JPY`. These figures are not aggregated: quote currencies, endpoint semantics, venue windows and depth construction differ.

Derivatives and flow coverage remain incomplete. Binance returned HTTP 451, Bybit HTTP 403, Deribit data remained raw-only, Grayscale returned HTTP 429, Franklin parsing failed, and three SEC submission captures failed. No current derivatives, ETF-flow or SEC event feature was promoted to the eligible feature store. External open-interest estimates around `1.77bn USD` and `865m USD` have incompatible/unresolved venue coverage and must not be averaged.

### Cross-analysis and sentiment quality

Cross-analysis run [44982502055](https://github.com/Barrot-Agent/B-Agent/actions/runs/44982502055) completed, but its newest XRP sentiment observation is 2026-10-29 13:23:01 UTC, approximately 566.478 hours old at this run. The recent and prior comparison windows are empty. Historical aggregates (XRP: 286 mentions, score +0.455; Ripple: 219 mentions, score +0.484) are not current sentiment and are not model-eligible. Cross-analysis artifact SHA-256: `f740a08a5a92566bddb8bdcfa5749752c09498cf3275c5dec159b5969bc31ba9`.

### New primary-source institutional and capital-flow research

The following sources were reviewed in this run. They are **web-research-only**: the ingestion pipeline did not capture their raw bytes or receipt hashes, so they are not model-eligible. Source publication/data dates are preserved separately from this retrieval time.

1. **Evernorth Q3 2026 Form 10-Q**, filed 2026-11-13, period ended 2026-09-30:  
   https://www.sec.gov/Archives/edgar/data/2092592/000162828026073871/xrpn-20260930.htm  
   Before the October business-combination close, the filing reports only `$91,397` unrestricted cash, a roughly `$10m` working-capital deficit, and a nine-month operating loss of about `$273.2m`, largely driven by approximately `$271.0m` of digital-asset impairment. Nine-month operating cash use was about `$1.722m`. A `$1m` Ripple-related revolving facility was undrawn as of September 30; Pathfinder had paid approximately `$3.6m` of operating costs. These are pre-close figures and must not be described as the post-close company's current cash balance.

2. **Evernorth pro forma transaction filing**, filed 2026-11-13, illustrative balance sheet as if the combination occurred on September 30:  
   https://www.sec.gov/Archives/edgar/data/2092592/000162828026074319/evernorth-proforma20260930.htm  
   It reports pro forma cash of approximately `$76.027m`, digital assets net of approximately `$342.223m`, total assets of `$418.593m`, total liabilities of `$46.276m`, redeemable non-controlling interest of `$229.531m`, and stockholders' equity of `$142.785m`. These are pro forma values, not a live November balance sheet.

3. **Evernorth XRP capital reconciliation — avoid double counting**:
   - `$214.05m` of advance cash subscriptions funded the purchase of `84.365876m XRP`.
   - `261.919096m XRP` of in-kind private-placement contributions comprised `0.6m` from investors, `211.319096m` routed from RippleWorks through Arrington XRP Capital Fund, and `50m` from a Ripple-affiliated entity.
   - Ripple separately contributed `126.791458m XRP`; delayed funding added `$10.5m` cash and `0.2m XRP`.
   - Total in-kind XRP was `388.910554m`; adding the `84.365876m` cash-purchased XRP yields `473.276430m XRP` at the close.
   - The `346.284972m XRP` reported as held at September 30 already includes the `84.365876m` cash-purchased amount plus the `261.919096m` in-kind private-placement amount. Do **not** add that September 30 balance to the full `388.910554m` in-kind total; that would double-count `261.919096m XRP`.
   - The `$272.6m` gross cash proceeds at closing comprise approximately `$224.6m` of private-placement cash plus `$48m` released from the SPAC trust, before transaction expenses. The `$214.05m` already used to buy XRP is not retained cash.
   - A later `$30m` principal convertible PIK note produced about `$29m` net proceeds after a `$1m` fee; it bears 4% PIK interest and matures in 2031. This is debt financing, not an XRP purchase.
   - The filing identifies SBI Holdings-affiliated subscribers as subject to a 39.9% ownership cap and Class C share arrangements. This is evidence of an SBI Holdings-linked Evernorth investment, not evidence that SBIC East/Central/West are SBI Holdings subsidiaries.

4. **Circle Q2 2026 Form 10-Q**, period ended 2026-06-30:  
   https://www.sec.gov/Archives/edgar/data/1876042/000187604226000248/crcl-20260630.htm  
   It states that Circle SBI Japan K.K. (also presented by SBI as SBI Circle Holdings K.K.) is a 50/50 Circle–SBI Holdings venture. In November 2025, each party contributed approximately `$1.5m` equivalent in yen. Circle consolidates the entity as a VIE; SBI's interest is shown as non-controlling interest. The filing says there had been no significant operating results to date as of June 30, 2026. SBI's own investor deck explicitly maps “Circle SBI Japan KK” as the English name and “SBI Circle Holdings K.K.” as the Japanese name. This JV is separate from the regional SBIC entities.

5. **SBI–Circle capital and infrastructure links**:
   - SBI Holdings and SBI Shinsei Bank invested `$25m` each (total `$50m`) in Circle shares around Circle's June 2025 IPO: https://www.sbigroup.co.jp/news/2025/0609_15491.html
   - SBI Holdings said a consolidated subsidiary participated in Circle's ARC token presale in May 2026; SBI's amount was not disclosed: https://www.sbigroup.co.jp/news/2026/0512_16310.html
   - Circle named SBI Group among Arc's founding validators on 2026-08-05: https://www.circle.com/pressroom/circle-announces-founding-validator-cohort-and-major-integrations-for-arc-ahead-of-september-16-mainnet-launch
   - Circle's 10-Q confirms the 50/50 Circle SBI Japan K.K. ownership and the absence of significant operating results as of June 30, 2026. Do not convert the JV or validator relationship into an unsupported claim of large Japanese USDC flows.

6. **SBI–Ripple and the XRPL stablecoin rail**:
   - SBI VC Trade, a subsidiary of SBI Holdings, launched RLUSD in Japan on 2026-06-24 after JFSA approval: https://www.sbigroup.co.jp/news/pr/2026/0624_16424.html
   - Circle's USDC has been natively available on XRPL since 2025-06-12, with Circle Mint and API support and no bridge required: https://www.circle.com/blog/now-available-usdc-on-the-xrpl
   - Circle's current USDC page reports `$67.3bn` in global circulation as of 2026-11-19; Circle's Q2 10-Q reported `$73.269bn` at 2026-06-30. The roughly 8.1% difference is a global supply comparison, not XRPL-specific supply and not evidence of XRP demand.
   - These facts show SBI's multi-rail position across Ripple/RLUSD and Circle/USDC. They do not establish a direct Circle–Ripple corporate partnership. USDC and RLUSD coexist on XRPL; shared network presence and a common SBI partner are not proof of a three-way agreement.

7. **Coinbase–Circle economics and Coinbase's XRP exposure**:
   - Circle's Q2 2026 SEC filing reports `$655.3m` of distribution costs in the first half of 2026 in connection with its agreements with Coinbase. Coinbase allocations depend on USDC held on its platform and a share of remaining ecosystem-growth economics after approved third-party payments. Circle did not disclose a current Coinbase-held percentage in this filing. The same filing reports Circle's own on-platform share separately; do not confuse it with Coinbase's share.
   - Circle's SEC filing: https://www.sec.gov/Archives/edgar/data/1876042/000187604226000248/crcl-20260630.htm
   - Coinbase's disclosure page lists XRP as “Coinbase Holding: Yes” and “Commercial Engagement: Yes” for U.S. trading assets, and also lists XRP under Coinbase Custody Trust Company. Holdings are dated 2026-03-31; no quantity is disclosed. Its broad “commercial engagement” definition includes financial or business relationships and does not identify a specific XRP contract: https://www.coinbase.com/legal/digital-asset-disclosures
   - Coinbase and Ripple announced RLUSD on Coinbase Prime, Exchange and retail on 2026-10-28. The launch announcement said Global Exchange collateral eligibility would follow; this run found no primary evidence that XRP or RLUSD collateral eligibility had since become active: https://www.coinbase.com/blog/rlusd-is-now-available-on-coinbase
   - The Evernorth 10-Q uses Coinbase as the principal market for XRP valuation. This is a valuation input, not proof of Evernorth execution volume or a custody balance.

8. **Ripple regulatory and custody structure**:
   - OCC Corporate Applications Search lists Ripple National Trust Bank, charter `25364`, as approved on 2025-12-12 and consummated/effective on 2026-10-26: https://apps.occ.gov/CAS/home/details?FilingID=RjzoD2gxmYOv&FilingSubtypeID=1093&FilingTypeID=2
   - The OCC conditional approval describes Ripple Labs as the direct holding company and the proposed bank's activities as managing segregated RLUSD reserves, acting as collateral trustee for RLUSD holders, and providing fiduciary digital-asset custody. The charter is a regulatory/custody development; it does not itself prove XRP market purchases, settlement volume or XRP collateral demand: https://www.occ.gov/topics/charters-and-licensing/interpretations-and-decisions/2026/ca1359.pdf

### Entity-relationship conclusions and counter-hypotheses

- SBI Holdings is a common institutional node across Circle equity/JV/Arc, Ripple RLUSD distribution, and SBI-affiliated Evernorth subscriptions. This supports a multi-rail strategic relationship, not exclusivity to Ripple or Circle.
- Circle–Coinbase has a direct and material revenue-sharing/distribution relationship. Ripple–Coinbase has a direct RLUSD listing relationship and Coinbase's disclosed XRP holding/commercial engagement, but these do not prove Coinbase's XRP trading volume or XRP collateral use.
- Circle USDC is native on XRPL; Ripple's RLUSD also operates on XRPL. Their coexistence does not establish a direct corporate partnership.
- Ripple's OCC trust-bank status strengthens the regulated custody/reserve framework for RLUSD; it does not create an automatic causal link to XRP token demand.
- Evernorth's cash, debt, XRP purchases and in-kind contributions must remain separate. The in-kind XRP is not open-market buying; the convertible note is debt; gross transaction proceeds are not retained cash.

### Remaining research identity gates

- Japan's SBIC East/Central/West remain distinct from SBI Holdings and the Circle/SBI JV. Keep separate legal-entity records.
- Exact-phrase work for “ASK Coin” and “SBIC, ChatGPT SBIC” remains unresolved. The “actual capital” question now has a primary-source Evernorth capital reconciliation, but no unverified phrase or allegation is treated as fact.
- No YouTube inventory was attributed to Camilla/Kamilah Stevenson because a channel-to-person identity match has not met the verification threshold. Do not publish or merge video attributions until identity is verified.
- Nine-platform map is unchanged: ChatGPT-to-GitHub is the only verified authenticated data path. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks remain unverified. No external model dispatch occurred.

### Execution state and next concrete actions

**VERIFIED:** main and integration trees; branch ancestry; PR inventory and non-overlapping path sets; main post-merge full suite; PR #1684 exact-head full suite and security checks; isolated historical backfill; raw payload hashes; receipt-chain continuity; feature-store SQLite integrity; SEC/Circle/SBI/Coinbase/OCC source facts listed above.

**EXECUTED:** downloaded and inspected Run57 raw, feature-store, event and receipt-chain artifacts; downloaded and inspected Run279 cross-analysis artifact; performed the Evernorth capital reconciliation; updated this canonical handoff. Web-retrieved institutional sources remain outside Barrot's raw-receipt store.

**DESIGNED / NOT YET EXECUTED:** reconstruct the feature store from retained raw artifacts when Actions cache writes are unavailable; capture every event source with URL, capture timestamp and raw SHA-256; add trusted external timestamp anchoring; ingest the SEC/Circle/SBI/Coinbase primary filings as raw receipts before feature promotion; restore derivatives/ETF/SEC coverage through lawful public endpoints; build sufficient chronological target origins and evaluate naive, momentum, mean-reversion and volatility baselines with calibration and drift gates.

**Next action:** verify the CI and fail-closed gate triggered by this handoff commit; then inspect the next main hourly ingestion, address the cache reconstruction fallback and event-to-receipt completeness, and only then advance walk-forward evaluation. Directional forecasts remain disabled. No merge, deployment, cache deletion, secret rotation, Space restart, external model dispatch, Kaggle submission, Databricks write, paper trade, funds transfer or real-money action occurred.


---

## Run11 continuation — 2026-11-22 04:25 UTC

### Repository, branch and PR audit

- Main remains `550a647ee7269a704d4600ff337b2145acc90473`.
- Main recursive tree: 3,115 entries, `truncated=false`.
- Existing XRP integration branch: `integration/xrp-post-merge-verification-20261121T0002Z`.
- Integration head at this audit: `5b0ae38470f334b3e08e231a8daf87b3dca95992`.
- Integration recursive tree: 3,127 entries, `truncated=false`.
- Ancestry: 142 commits ahead of main, zero behind; 27 changed files. The integration tree contains all current main paths.
- Open PR inventory remains exactly #1684 (XRP integration) and #1685 (A2A credential security). Their changed-file sets have zero overlap. No branch or PR was created.
- #1684 remains draft. No independent review is visible. #1685 remains a separate non-draft security workstream, five commits ahead with nine changed files; no independent review is visible.
- Main reports `protected=true`, but the branch-protection detail endpoint returns HTTP 403. The visible fallback ruleset is disabled. CODEOWNERS assigns all paths to `@Barrot-Agent`, not an independent reviewer. Repository `security_and_analysis` settings were not exposed by the available metadata response.
- The combined-status endpoint returned no status records for main SHA. The latest scheduled main ingestion completed successfully; no merge occurred, so no post-merge main CI was required.

### Exact-head CI — verified on the existing integration head

On `5b0ae38470f334b3e08e231a8daf87b3dca95992`:

- Full repository suite: **4,564 passed, 0 failed, 1 skipped**, 11 warnings, 32 subtests; 73.20% coverage; 167.41 seconds.
- Core tests and the expanded full-suite job both passed.
- Preserved-artifact historical backfill replay passed.
- Dependency audit [44984089336](https://github.com/Barrot-Agent/B-Agent/actions/runs/44984089336) passed all six dependency manifests: root runtime, development, supplemental integrations, Hugging Face Space, legacy requirements and PEP 621 project dependencies.
- Money audit [44984089303](https://github.com/Barrot-Agent/B-Agent/actions/runs/44984089303) passed.
- Conflict-integrity check [44984089307](https://github.com/Barrot-Agent/B-Agent/actions/runs/44984089307) passed.
- Pages validation passed.
- Fail-closed gate [44984089286](https://github.com/Barrot-Agent/B-Agent/actions/runs/44984089286) remained blocked: draft status is true and branch-protection details could not be verified. No bypass was attempted.

### Main ingestion Run58 — 2026-11-22 04:14 UTC

[Run58](https://github.com/Barrot-Agent/B-Agent/actions/runs/44984161724) completed successfully on main SHA `550a647`.

- 34 source receipts; 22 retained raw payloads; 12 digest-only receipts.
- 23 sources classified raw-only: 11 with retained payload bytes and 12 digest-only.
- Every raw-only source ID is present in the receipt manifest. The earlier apparent empty `raw_only_source_ids` field was a scope misunderstanding: it belongs to the CFTC weekly-source policy subset, not the global raw-only inventory. The global `raw_only_source_count` is 23.
- 18 source failures: eight HTTP 451 responses (Binance), five HTTP 403 responses (Bybit), three SEC contact-identity/configuration failures, one HTTP 429 (Grayscale), and one Franklin issuer-page parse failure. No proxy, alternate identity or access-control workaround was used.
- 2,230 input feature records; 485 delta records; 124 eligible feature records; 367 excluded feature records.
- Main feature-store checkpoint before isolated recovery: 18,483 records across 30 snapshots.
- Drift: zero of 204 candidate features evaluated. Walk-forward forecast count: zero. SEC capture remains configuration-blocked with zero raw receipts.
- The cross-run receipt chain reached sequence 30.

Raw artifact ZIP SHA-256: `438f60a3d5e05ff8192551c2c9e7caefeb627519519e37f913b7889054cb1b02`. Feature-store artifact ZIP SHA-256: `22afecaffb3ff9d42b1fb3596c36a3e4178dccf07e91a49cf936100130824c8a`. Both were downloaded and hashed locally against the published artifact digests.

### Run58 spot and order-book structure

The synchronized OKX XRP-USDT / USDT-USD top-of-book calculation produced a USD-normalized mid of `0.9196117075`, spread `1.18545 bps`, component maximum age `11.000429 seconds`, and snapshot skew `0.797 seconds`. This is one OKX publisher group; only top-of-book prices were normalized. OKX depth remains in USDT.

The near-synchronous USD-quoted books (approximately 04:14:42–04:14:46 UTC) were:

| Venue | Mid USD | Spread | 10 bps bid / ask depth | 50 bps bid / ask depth | 100 bps bid / ask depth |
|---|---:|---:|---:|---:|---:|
| Coinbase | 0.919450 | 1.0876 bps | $470.1k / $326.3k | $1.960m / $1.495m | $4.488m / $2.838m |
| Bitstamp | 0.919305 | 0.1088 bps | $374.2k / $321.3k | $748.0k / $730.2k | $861.9k / $840.9k |
| Kraken | 0.919320 | 0.6527 bps | $327.8k / $355.0k | bid $2.819m; ask unavailable | 100 bps pair unavailable |

OKX showed 10 bps bid/ask depth of 168.9k / 160.1k USDT, 50 bps 862.4k / 885.4k USDT, and 100 bps 1.159m / 1.195m USDT. Bitbank showed 10 bps 16.397m / 9.348m JPY, 50 bps 58.118m / 24.464m JPY, and 100 bps 63.804m / 37.548m JPY. Neither quote currency is converted into USD depth in this snapshot.

Coinbase and Bitstamp showed positive displayed bid-side imbalance; Kraken showed slight ask-side imbalance at 10 bps; OKX was near balanced with slight ask-side imbalance beyond 10 bps. This is mixed venue-specific book state, not a consolidated directional signal. Do not sum the venues or call the displayed amounts executable global liquidity. Coinbase sequence is retained but there is no WebSocket sequence bridge; Kraken and Bitstamp are point-in-time snapshots without a continuity bridge; OKX sequence is retained without a sequence bridge.

### Historical backfill — Run58 artifact reconciliation

The isolated replay [from the exact-head CI artifact](https://github.com/Barrot-Agent/B-Agent/actions/runs/44984089338/artifacts/14738942253) restored 118 records from 11 source lineages:

- Before: 18,483 records, 30 snapshots.
- After: 18,601 records, 31 verified snapshots.
- SQLite integrity: `ok`.
- 33 downloaded historical artifact ZIP digests matched their GitHub artifact digests.
- Point-in-time boundary: 18,483 records visible one microsecond before the recovery receipt bound; 18,601 visible one microsecond after.
- Reconciliation SHA-256: `d81f7a76f0b29f740dfb76cb438d91beb230ac57dd345cc2c322ad9a976c7d0c`.
- External trusted timestamp/WORM anchor: **not anchored**.
- Recovery receipt time is a post-append availability bound, not a claim about the historical database commit time.

### Walk-forward blocker corrected at code level; data sufficiency still fails

Main's daily Run54 [walk-forward report](https://github.com/Barrot-Agent/B-Agent/actions/runs/44967713690) evaluated ten venue/horizon combinations (1h, 4h, 24h, 7d and 30d) but produced zero forecasts. All ten were marked blocked with `no records remain after venue filtering`.

Inspection of the Run54 feature-store database found:
- Binance: 999 eligible hourly close records but only one distinct `known_at_utc` capture origin.
- Coinbase: 373 eligible hourly close records but only 25 distinct `known_at_utc` capture origins.

The existing integration branch contains the case-insensitive `_venue_key` normalization and regression test in `walk_forward.py`; that test passed on the exact head. This corrects the venue-label mismatch. It does **not** manufacture chronological origins. The evaluator still requires at least 100 training examples and 100 out-of-sample origins per evaluation, with an embargo equal to the target horizon. After the venue filter correction, the observed one/25 availability origins remain insufficient. The next daily evaluation must confirm the new blocker; do not relax the 100-origin gate or treat a bulk historical backfill's shared capture timestamp as historical availability.

### New Coinbase / cbXRP / Morpho collateral intelligence

**Primary Coinbase evidence**

1. Coinbase's [cbXRP proof-of-reserves page](https://www.coinbase.com/cbxrp/proof-of-reserves) reported a displayed refresh time of 2026-11-22 02:03 AM (page timezone not specified), total reserves of **158,565,196.07 XRP** and total supply of **158,562,949.53 cbXRP**, all shown on Base. The issuer-reported reserve excess is **2,246.54 XRP**, about **0.00142%** of supply. This is Coinbase-published proof-of-reserves data, not an independent audit.
2. Coinbase Help's [loan introduction](https://help.coinbase.com/en/coinbase/trading-and-funding/loan/loan-intro) says eligible customers can borrow USDC against XRP using the Morpho protocol on Base, with regional/asset restrictions. New York's eligible list is narrower and does not include XRP.
3. Coinbase Help's [backup collateral instructions](https://help.coinbase.com/en/coinbase/trading-and-funding/loan/loan-backup) explicitly maps loan asset XRP to collateral asset **cbXRP**, network **Base**, contract `0xcb585250f852c6c6bf90434ab21a00f02833a4af`.
4. Coinbase's [loan-health guide](https://help.coinbase.com/en/coinbase/trading-and-funding/loan/loan-health) says each Morpho market has a predetermined, market-specific LLTV; the public guide does not assign one universal threshold to XRP. Do not apply the generic 86% figure on the [borrow landing page](https://www.coinbase.com/borrow) to every collateral asset.
5. Coinbase's [November 6, 2026 blog update](https://www.coinbase.com/blog/protecting-our-customers-standing-up-extortionists%29) says eligible customers can borrow up to $100,000 USDC against XRP, LTC, DOGE, ZEC, HYPE or PAXG; the product is powered by Morpho. The interface provides access; collateral moves onchain.

**Morpho market identity**

- Run58 captured the public Morpho market-parameter endpoint for Base market ID `0xd4a903dc6d949519060c7707f9604fdc9772c046e05c2e3a8fce0bd7196e4109`, its state, liquidity and 30-day state history, plus oracle state `0x031b2efc8d70042ac8d9f5c793c4149ec4b60fde`.
- These six Morpho/cbXRP receipts and Coinbase's proof-of-reserves receipt are digest-only and model-ineligible pending raw-response retention terms, token-decimal normalization and lineage validation. Their hashes are preserved:
  - Market parameters: `675a6d3711533831266991a632135ceb70e3c7ec33dbb7292b40919e9a351b52`
  - Market state: `ca240338e012af2f0c15b4a01e3a885cc0ae85e55dc4e9ed465fc086d0a76fd7`
  - Market liquidity: `3c54540e8576d8ad624a81792a8f7f8189c1c2fc8778eafa58369e5db6372d47`
  - 30-day market state history: `fcab52b15d8eaf4f6cb8a5c66871e55fc9e41ab88ec224ef636d1a52e998ca7e`
  - Oracle state: `8e4fd2b72d7fcb3a07892adef830f57cb9d14aabd6c0a8e9fcbf0cf4a75e794b`
  - Coinbase cbXRP proof-of-reserves: `6fb8eda3ca291dec280b7eea444ed8ea76920ab04507ce28dd75fc2916072aab`
- Morpho's own [Dune query, “Coinbase Borrow Markets”](https://dune.com/queries/7437221), lists this exact market ID as Base cbXRP/USDC with **62.5% LLTV**. This identifies the market as part of the Coinbase Borrow market set. Morpho's [API documentation](https://docs.morpho.org/api/) describes the market parameters as immutable and provides public read endpoints for market state, history and liquidity.

**Independent analysis and limitations**

- CleanSky's 2026-08-26 analysis, using an 2026-08-24 snapshot, reported 117.288m cbXRP supply, 91.619m cbXRP in Morpho (78.1%), 90.78m cbXRP in the 62.5% market and $41.0m live USDC debt. The article itself labels the Coinbase-product attribution as an inference from market parameters and timing. Morpho's Dune market list now independently supports the market identity, but the August balances remain dated: https://cleansky.io/blog/coinbase-wrappers-manufactured-demand-2026/
- Comparing that August supply with Coinbase's 2026-11-22 proof-of-reserves display gives a cross-source increase of about **41.275m cbXRP / 35.19%**. This indicates more XRP represented by the Coinbase wrapper/custody rail; it does **not** prove those units were bought on the open market. Existing holders can wrap/pledge XRP without selling it.
- CryptoSlate's 2026-11-13 analysis of Morpho-indexed events reported 883 liquidation logs from Nov 7 to Nov 13, about 4.182m cbXRP seized and 4.016m USDC repaid, with about $53.53m USDC debt at its Nov 13 state snapshot: https://cryptoslate.com/xrp-loans-trigger-883-liquidations-and-53m-remains-at-risk/
- A separate ODEI dashboard read on 2026-11-21 19:29 UTC reported 880 liquidations over seven days, about $2.969m liquidated in seven days, $891k in 24 hours and zero bad debt. The dashboard labels the source as public Base RPC data but says it has not been independently checked. Treat it as an unverified monitoring lead, not a model feature: https://network.odei.ai/research/wallet-activity/mr_3tyeasjgos4644q3
- The liquidation counts and amounts above use different windows and indexers and are not directly comparable. A liquidation log is not a unique borrower. USDC debt repaid is not borrower economic loss. cbXRP seized on Base is not proof of native XRP sold on a centralized exchange.

**Causal hypotheses to test**

1. Existing XRP holders wrap/pledge native XRP as cbXRP, borrow USDC and retain XRP price exposure. This can increase custody/wrapper supply without creating a spot buy.
2. Falling XRP prices increase LTV and can trigger cbXRP collateral liquidations. Liquidators may retain, swap or redeem cbXRP; only a traced redemption/custody transfer followed by native XRP sale establishes direct spot-supply pressure.
3. Arbitrageurs may buy discounted cbXRP and redeem it, absorbing onchain liquidation supply without an immediate broad native-XRP sell. This counter-hypothesis remains open.
4. The wrapper/collateral rail may deepen institutional utility while simultaneously adding leverage and liquidation feedback. Measure these separately; do not collapse custody growth, loan originations, current debt, collateral seizures and native exchange flows into one “capital inflow” metric.

Required follow-on features: cbXRP total supply and reserve ratio; Morpho market total supply, borrow, collateral and liquidity; oracle price/time; LLTV; liquidation events; cbXRP/USDC pool depth and swaps; cbXRP redemption/unwrap flows; Coinbase custody movements; native XRP exchange deposits/withdrawals and executed trades. Keep these model-ineligible until payload terms, token decimals, market identity and event-to-receipt linkage are verified.

### Exact-phrase and identity research

- Exact phrase `"ASK Coin"` returned Permission Coin (ticker ASK) on CoinGecko/CoinMarketCap, but no verified XRP relationship. Treat this as a likely false-positive candidate, not the user's intended entity: https://www.coingecko.com/en/coins/permission-coin
- Exact phrase `"actual capital"` produced no new attributable primary-source match in this run. The earlier Evernorth cash/in-kind/debt reconciliation remains the relevant primary-source capital analysis.
- Exact phrase `"SBIC, ChatGPT SBIC"` produced no corroborating result in this run. Keep SBIC East/Central/West distinct from SBI Holdings and the Circle–SBI Japan JV.
- Search surfaced two public YouTube channel candidates named Kamilah Stevenson: `UCqUPJMQdkCN6lsLVDnichPA` (`@drkamilahstevenson`) and `UCGZz6xGqdQDk9wNul__VQbg` (`@drkamilahstevenson-j9r`). Their descriptions are similar, but no reliable person-to-channel identity match was established. One candidate page showed a video attributed to Honeybeardtraining; it is not attributed to the named person without verification. No video inventory was produced. No Camilla Stevenson identity match was established.
- Nine-platform status unchanged: only ChatGPT-to-GitHub authentication and data flow are verified. The other eight platforms remain unverified; no external dispatch occurred.

### Durable status and next action

**VERIFIED:** complete main/integration trees; branch ancestry and PR inventory; no PR path overlap; exact-head full suite and dependency/security checks listed above; Run58 raw artifact digests; 33-artifact historical replay; SQLite and point-in-time recovery boundary; USD venue depth snapshot; Coinbase cbXRP reserve/supply display; Coinbase collateral eligibility and cbXRP Base contract; Morpho market ID/62.5% LLTV identification.

**EXECUTED:** inspected Run58 raw and feature-store artifacts; queried the feature-store SQLite database; reconciled the daily Run54 walk-forward block to venue-label casing and actual availability-origin counts; searched exact phrases and YouTube identity candidates; reviewed Coinbase, Morpho, CleanSky, CryptoSlate and ODEI collateral evidence; appended this canonical handoff.

**NOT YET VERIFIED / BLOCKED:** exact-head CI triggered by this new handoff commit; direct payload inspection for digest-only Morpho/cbXRP receipts; current Morpho market debt/collateral/liquidity from retained raw bytes; current native XRP redemption/sale linkage; 100 chronological OOS origins; SEC monitored contact identity; external WORM timestamp anchor; branch-protection details and independent review.

**Next concrete action:** verify CI on this new handoff commit; then add lawful, receipt-backed Morpho liquidation and cbXRP redemption/market-flow capture to the existing XRP integration workstream, preserving digest-only receipts until raw-response terms are reviewed. Accumulate genuine point-in-time origins before re-running multi-horizon evaluation. Keep directional forecasts disabled. Do not relax sample gates, create another PR, bypass protection, or infer native XRP selling from cbXRP liquidation alone.

No merge, deployment, cache deletion, secret rotation, Space restart, external model dispatch, Kaggle submission, Databricks write, paper trade, funds transfer or real-money action occurred.


---

## Post-update verification and Run58 supplemental audit — 2026-11-22 04:45 UTC

### Exact-head result for handoff commit 7f4b051

[CI 44985891309](https://github.com/Barrot-Agent/B-Agent/actions/runs/44985891309) completed successfully on exact head `7f4b051a25288997ba4d618c2252b81cb90a23c0`:

- Full repository suite: **4,564 passed, 0 failed, 1 skipped**, 11 warnings, 32 subtests; 73.20% coverage; 214.49 seconds.
- Core test job: passed.
- Full repository test job: passed.
- GitHub Pages validation-only build: passed.
- Preserved-artifact historical backfill replay: passed.
- Exact-head dependency audit [44985891262](https://github.com/Barrot-Agent/B-Agent/actions/runs/44985891262): passed.
- Exact-head Money audit [44985891273](https://github.com/Barrot-Agent/B-Agent/actions/runs/44985891273): passed.
- Exact-head conflict-integrity check [44985891248](https://github.com/Barrot-Agent/B-Agent/actions/runs/44985891248): passed.

The exact-head backfill artifact [14739926702](https://github.com/Barrot-Agent/B-Agent/actions/runs/44985891309/artifacts/14739926702) was downloaded and inspected:

- 118 records recovered from 11 source lineages.
- 18,483 to 18,601 records; 30 to 31 snapshots.
- SQLite integrity `ok`.
- All 33 historical artifact ZIP digests matched their GitHub artifact digests.
- One-microsecond point-in-time visibility boundary verified.
- Reconciliation SHA-256: `6316dcb3606351056c2d26e9806f18011c696468e4fa057f70792c0bc9973f33`.
- Reconciliation ZIP SHA-256: `a25c335f7f1387ac93d9790026b42d0b89fb243356cf08e98708d6341639551b`.
- External trusted timestamp/WORM anchor remains `NOT_ANCHORED`.

The fail-closed gate [44985891288](https://github.com/Barrot-Agent/B-Agent/actions/runs/44985891288) completed with **READINESS=BLOCKED** for three explicit reasons: PR is still draft; no independent approving review exists; branch protection could not be verified because the detail endpoint returned HTTP 403. No merge was attempted.

### Current open PR inventory — three distinct workstreams

The latest open-PR search returned exactly three PRs:

| PR | Workstream | Classification | Current disposition |
|---|---|---|---|
| [#1684](https://github.com/Barrot-Agent/B-Agent/pull/1684) | XRP ingestion, research and prediction readiness | Blocked | Draft; exact-head suite passed; no independent approval; protection details unavailable |
| [#1685](https://github.com/Barrot-Agent/B-Agent/pull/1685) | A2A gateway/runner credential separation | Blocked | Non-draft; separate security workstream; runner quarantined; no independent approval or completed OS sandbox/egress controls |
| [#1686](https://github.com/Barrot-Agent/B-Agent/pull/1686) | LunaRoute runtime decommission | Unique/unreviewed; blocked | Draft; four commits, four files; no exact-head CI or reviews; not an XRP objective |

PR #1686 changes `.env.example`, `b_agent.py`, `opencode.json` and adds `scripts/decommission_lunaroute_local.sh`. Its path set has zero overlap with #1684 and #1685. It is not a duplicate or superseded XRP PR. The script would remove local shell startup lines and `~/.lunaroute_key`; **it was not executed**. No local device cleanup or runtime-provider removal was performed. This change remains unreviewed and must not be merged or run as a side effect of the XRP mission.

The XRP branch at the time of this audit was 143 commits ahead of main and zero behind, with 27 changed paths. No new branch or PR was created by this run.

### Repository governance note

The repository metadata reports `web_commit_signoff_required=true`. GitHub reports the handoff commit `7f4b051` as unsigned (`verification.reason=unsigned`). No sign-off was fabricated. Verify the applicable sign-off policy and obtain any required authorized sign-off before merge. This is separate from the already-failing fail-closed gate; it does not justify bypassing review or branch protection.

### Run58 event timeline and research-only observations

The Run58 event artifact reports:

- 150 curated events across 50 declared independence groups.
- Zero event raw-source hashes; receipt completeness false; model eligibility false.
- 117 structured scenario hypotheses; probabilities are null; forecast status `NOT_ISSUED`.
- Only 19 scenarios contain supporting evidence, six contain contrary evidence, and six contain minority objections. The registry is useful hypothesis scaffolding, not an evidence-complete causal model.
- SEC capital-event capture: zero filing events, zero primary-document captures, zero capital facts; the three SEC failures are configuration/contact-identity failures. No issuer cash-flow claim is derived from SEC data in this run.

Two separate research-only observations were recorded:

1. **Bitbank XRP/JPY latest-60-trade sample**, captured 2026-11-22 04:14:44.617 UTC: 60 trades from 04:02:23.224 to 04:13:38.659 UTC (675.435 seconds); buy taker 8,601.6061 XRP; sell taker 41,044.968 XRP; net taker flow **-32,443.3619 XRP**. Sell/buy taker ratio is 4.77. Raw bytes were retained with SHA-256 `075c32f488f5893bf33bfe7ec652f9073d67edeede7b3654a41c53cd7fe1f3fb`. This variable-duration latest-60-trade sample is not a fixed-duration or 24-hour flow metric and remains model-ineligible.

2. **XRP Insights ETF holdings-delta CSV**, data as of 2026-11-20, captured 2026-11-22 04:14:47.269 UTC. Seven fund rows: four direct-spot flow funds, one excluded direct-spot flow fund, and two mixed-indirect funds. The four direct-spot funds showed a holdings delta of **-$7,452,638 / -8,242,683.02 XRP**; the two mixed-indirect funds showed **+$200,465 / +221,715.84 XRP**; the index sleeve showed zero flow. Direct-spot holdings were 1,122,521,062.26 XRP; index-sleeve holdings 20,872,764 XRP; mixed-indirect holdings 32,728,671.98 XRP. The CSV contains 1,667 rows (1,478 settled, 189 reconstructed, seven initial). Receipt SHA-256: `a200eab17109c4a878af34e051c6d072f2c197672dc46530a1682a1034c66a97`. Source: https://xrp-insights.com/data/xrp-etf-flows.csv . Its terms permit attributed citation but require written permission for commercial redistribution: https://xrp-insights.com/terms . The full CSV was not retained. The source explicitly classifies this as **holdings delta, not issuer AP cash flow**; it is research-eligible but model-ineligible pending primary issuer reconciliation.

Other public ETF dashboards disagree on the same Nov. 20 date: one five-fund dashboard reports about -$5.0m; another partial dashboard reports -$2.4m from two of three reported funds; a broader six-spot-plus-BITW dashboard reports about -$8.02m. These differ in fund coverage, inclusion of index/indirect products, missing issuer rows and flow methodology. Do not average them. Issuer creations/redemptions and AP cash activity remain the required primary evidence for “actual capital.”

### Cache continuity remains degraded

The Run58 ingestion and the exact-head full-suite job both reported GitHub Actions cache reservation failures because the configured cache budget is exhausted and cache writes are read-only. This was nonfatal: the previous trusted checkpoint restored, Run58 per-run artifacts and receipt indexes uploaded, and the 118-record isolated backfill replay succeeded. No cache was deleted and no billing/retention setting was changed. Rebuilding the feature store from retained raw artifacts is still not implemented; seven-day checkpoint expiry remains a continuity risk.

### Corrections and interpretation boundaries

- Correction to the preceding cbXRP section: there are **five Morpho receipts plus one Coinbase proof-of-reserves receipt (six total)**, not six Morpho receipts plus Coinbase.
- Coinbase's cbXRP supply growth, Morpho collateral, liquidation logs, USDC repayments and native XRP exchange sales remain distinct measures. No direct native-XRP sale was traced from the liquidation data.
- The Nov. 20 ETF holdings delta is not AP cash flow and is not proof of spot purchases/redemptions.
- The Bitbank latest-60-trade sample is not a 24-hour flow measure.
- The event/scenario registry has no event raw hashes or probabilities; it cannot support directional forecasts.

### Current execution state

**VERIFIED:** exact-head full suite on `7f4b051`; dependency, Money, conflict-integrity and Pages checks; exact-head historical replay; 33 artifact digest matches; current three-PR inventory and non-overlapping paths; Run58 raw receipt inventory; event/scenario quality status; Bitbank sample; ETF holdings-delta observation; Coinbase cbXRP/ Morphо collateral evidence.

**EXECUTED:** updated the existing canonical handoff in PR #1684; re-read current repository and PR state; downloaded and hashed Run58 raw, feature-store, event and exact-head backfill artifacts; inspected SQLite feature-store origins; reconciled order-book depth, ETF holdings-delta definitions and cbXRP/Morpho source relationships.

**BLOCKED / NOT VERIFIED:** independent review and branch-protection configuration; PR #1684 draft status; PR #1685 sandbox/egress/security review; PR #1686 provider-removal scope and local cleanup authorization; SEC contact identity; cache reconstruction fallback; direct retained Morpho payloads and current collateral/debt/liquidity; native XRP redemption-to-sale linkage; 100 genuine chronological out-of-sample origins; event raw-source hashes; external WORM anchor; nine-platform external authentication.

**Next concrete action:** preserve the existing XRP integration branch; obtain independent review and verifiable protection before any merge; implement authorized, receipt-backed Morpho liquidation/redemption and Coinbase custody-flow capture; accumulate at least 100 true point-in-time OOS origins without treating historical bulk capture as availability; build raw-artifact cache reconstruction; configure SEC capture only with an approved monitored identity. Keep directional forecasts disabled.

No merge, deployment, local cleanup, secret rotation, cache deletion, Space restart, external model dispatch, Kaggle submission, Databricks write, paper trade, funds transfer or real-money action occurred.
