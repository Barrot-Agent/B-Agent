# Barrot XRP Intelligence — Canonical Durable Handoff

**Updated:** 2026-11-22 02:26 UTC  
**Mission priority:** XRP intelligence and measured prediction-engine capability. Preserve Barrot V3 as execution, orchestration, safety and verification foundation.  
**Record policy:** This is the rolling current-state handoff, not an append-only run diary. Prior run-by-run detail remains in the previous Git revisions of this file and the linked GitHub Actions artifacts. No branch history is rewritten.

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
