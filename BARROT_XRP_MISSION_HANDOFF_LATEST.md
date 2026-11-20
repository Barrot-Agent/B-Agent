# Barrot XRP Intelligence Mission — Current Durable Handoff

Updated: 2026-11-20T09:28:40Z (latest state is in the superseding section at the end)

## Mission priority

**Priority 1: XRP intelligence and measured prediction-engine mastery.** Preserve **Barrot V3** as the execution, orchestration, safety and verification foundation. The objective is an integrated, evidence-backed build with measured out-of-sample XRP predictive performance, not more fragmented PRs.

## Historical handoff preservation

This file is now the compact current-state handoff. The complete prior handoff, including all earlier run sections and Run 231 detail, is preserved verbatim in Git at commit [e52cc3c5f975f72ebcb7c25e1d418a5d438097f4](https://github.com/Barrot-Agent/B-Agent/blob/e52cc3c5f975f72ebcb7c25e1d418a5d438097f4/BARROT_XRP_MISSION_HANDOFF_LATEST.md). No Git history was rewritten, squashed or discarded. Use that immutable commit for the full historical record.

## Repository state

- **Current main SHA:** 7f8e3626c355bb3d89afdff56aeed5e056cb88f4. Main tree: 1,751 entries.
- **Latest exact-head CI-tested integration head:** 251682e1023afe3029c4fa7a87cecf09e59f8acf. Integration tree: 3,040 entries. Later map/handoff commits are documentation-only; see the superseding current-state section below.
- **Active integration PR:** [#1673](https://github.com/Barrot-Agent/B-Agent/pull/1673), base SHA 7f8e3626c355bb3d89afdff56aeed5e056cb88f4, 522 commits ahead / 0 behind, 1,494 changed files, 535,051 additions and 7,024 deletions. Changed-file inventory: 69 workflows, 422 test paths and 74 barrot_agent paths; 1,130 paths contain XRP-related identifiers.
- PR #1673 is open, draft and reported mergeable. It has no independent approving review. No merge was attempted.
- **Mainline merges:** PR #1672 and PR #1674 are already merged. PR #1674's merge commit is 33d02d3b3251350aaede9df04fcb701f2398d016. Main subsequently advanced to 7f8e362 through the existing paid-issue publisher workflow, not through this integration.
- **Branch protection:** GitHub branch metadata reports main as protected, but the direct branch-protection endpoint returns HTTP 403. The metadata exposes empty required-check contexts/checks; the only visible repository ruleset, “Fall Back,” is disabled. Effective required checks, strict status enforcement and administrator enforcement remain unverified. Do not infer them.
- **Open PR inventory:** 17 PRs remain open. No PR was created or closed in this run.
- Main's [paid-issue hunter run 44688313655](https://github.com/Barrot-Agent/B-Agent/actions/runs/44688313655) was followed by a main commit. This is an existing workflow side effect, not an integration merge.

## Integrated architecture — actual state

Barrot V3 remains the execution, orchestration, safety and verification foundation. The integration contains the XRP research and prediction stack:

- Public exchange/XRPL ingestion adapters, source registry and source-quality checks.
- SHA-256 raw-source receipts, canonical receipt metadata and a verifiable per-run receipt hash chain.
- Append-only SQLite point-in-time feature storage.
- Event timelines, competing scenarios/counter-hypotheses and a fail-closed forecast ledger.
- Naive class-prior, momentum, mean-reversion and volatility-normal baselines.
- Chronological purged/embargoed walk-forward evaluation, temporal probability calibration and feature-drift diagnostics.
- Independent evaluator-attestation requirements.

**XRP ingestion activation boundary:** The scheduled workflow [.github/workflows/xrp-public-ingestion.yml](https://github.com/Barrot-Agent/B-Agent/blob/integration/xrp-v3-mainline-successor-20261120T0135Z/.github/workflows/xrp-public-ingestion.yml) exists on the integration branch but is absent from main (main-branch content lookup returned 404). It therefore has not been running on the default branch. The successful scheduled [Cross Analysis run 44698098326](https://github.com/Barrot-Agent/B-Agent/actions/runs/44698098326) is a separate read-only workflow, not XRP market ingestion.

The XRP ingestion code declares public spot/depth sources for Binance, Coinbase, Kraken, Bitstamp, Bitbank, OKX and Bybit, plus Bybit linear derivatives and Deribit XRP perpetuals/options-related book data. It includes order-book freshness limits of 60 seconds and explicit stale/crossed-book quality checks. It handles Bybit 403 access restrictions without treating a blocked response as market data.

The workflow uses read-only actions/contents permissions and pinned actions. The raw archive is file-based and hash-chained; GitHub artifacts and cache are still mutable/expiring infrastructure, not independent WORM retention. Raw artifact retention is finite, and some sources whose redistribution rights are not established retain only hashes/receipts rather than page bytes. Independent WORM storage and timestamp anchoring remain missing.

## Historical exact-head verification — code head 6628327 (superseded by the current-state verification below)

The prior code head 6f52e50 had two full-suite failures in the legacy rendering dataset tests: the test expected at least 40 registered datasets when the catalogue contained 32, and the generated report omitted categories outside its curated tier map. Commit 6628327 fixed the underlying report behavior and corrected the test to assert the actual catalogue contract and required core entries. It also removed unsupported claims that registry metadata proved downloaded assets, licence entitlement or measured rendering performance.

On exact code head 6628327:

- Full repository suite: **4,440 passed, 1 skipped, 11 warnings, 23 subtests**.
- PR full-suite runtime: 172.55 seconds. Push full-suite runtime: 203.19 seconds.
- Inclusive coverage: 73.08%. Legacy/core coverage: 82%.
- Major-package floors: XRP telemetry 92%; MMI 92%; Barrot integration 62%; feature store 80%; forecast ledger 97%; point-in-time features 89%; source registry 95%; monetization 78%; rendering 71%; smart_agent 77%; mem_palace 100%.
- [PR CI 44700915366](https://github.com/Barrot-Agent/B-Agent/actions/runs/44700915366): full suite, tests and Pages validation-only build passed.
- [Push CI 44700905458](https://github.com/Barrot-Agent/B-Agent/actions/runs/44700905458): full suite, tests and Pages validation-only build passed.
- [Dependency audit 44700915396](https://github.com/Barrot-Agent/B-Agent/actions/runs/44700915396) and [push dependency audit 44700905372](https://github.com/Barrot-Agent/B-Agent/actions/runs/44700905372): passed all six Python manifests.
- [Money audit 44700915402](https://github.com/Barrot-Agent/B-Agent/actions/runs/44700915402): passed.
- [A2A Worker tests 44700915329](https://github.com/Barrot-Agent/B-Agent/actions/runs/44700915329): passed.
- The only full-suite warnings are existing warnings; the cache budget warning made the cache read-only and did not fail tests.

**Fail-closed merge gate:** [44700915440](https://github.com/Barrot-Agent/B-Agent/actions/runs/44700915440) and [push gate 44700905439](https://github.com/Barrot-Agent/B-Agent/actions/runs/44700905439) both blocked for exactly three reasons: PR #1673 is still draft; no independent approving review exists; branch protection could not be verified. The full suite, dependency audit, Money audit and A2A Worker tests passed. No required check was bypassed.

This handoff refresh is documentation-only. The verified code/test result above is explicitly bound to 6628327; it is not being represented as a test run on a later handoff-only commit.

## Workflow security and automatic side effects

- The 69 changed workflow files were inspected for triggers, permissions, secrets and action references. External actions in the changed workflow set are pinned to full commit SHAs.
- The active contents-write workflow found in the changed set is the release workflow, restricted to version tags. No release tag was created.
- Legacy autonomous self-upgrade, direct-main publishing, old paid-issue publishing, Hugging Face sync, Coinbase paper trading, old Databricks deployment and several A2A/creative workflows are quarantined or disabled.
- Manual Groq-backed research/analysis workflows require explicit confirmation and an expected main SHA. They were not dispatched.
- Databricks workspace creation and Kaggle dataset operations are manually gated. Kaggle submission, Databricks writes, A2A deployment, Cloudflare deployment, Space restart and secret rotation were not performed.
- The A2A deployment workflow requires explicit deployment and secret-rotation confirmations. It remains unexecuted.
- The release workflow can create a GitHub Release only on a version-tag push. No tag was pushed.
- The integration branch disables main's existing paid-issue publisher. On main, the paid-issue hunter is read-only and uploads a seven-day artifact; the separate publisher has contents:write and commits PAID-ISSUES.md plus data/money/paid_issues.json. If #1673 is later merged, that automatic main-commit side effect will stop. This must be treated as an intentional workflow behavior change.
- Main previously triggered a GitHub Pages deployment after PR #1674. PR #1673 changes public web assets. Its Pages publication boundary remains unresolved; current PR CI performs validation only and did not publish.
- Six Python dependency manifests are present: pyproject.toml, requirements.txt, requirements-dev.txt, requirements-integrations.txt, hf_space/requirements.txt and legacy/requirements_legacy.txt. No lockfile was found. Dependency audit passed, but lower-bound manifests without a lockfile do not provide fully reproducible dependency resolution.

## XRP market evidence snapshot — research-only, 2026-11-20

These public API observations are not admitted to the point-in-time feature store because this capture did not create the ingestion workflow's canonical raw-byte receipts and synchronized retrieval window.

**Spot snapshots:**

| Venue | Source time | Last | Bid / ask | Approx. top spread | 24h XRP volume |
|---|---|---:|---:|---:|---:|
| Kraken XRP/USD | Retrieval time only; ticker response has no exchange timestamp | $0.96366 | $0.96400 / $0.96408 | 0.83 bps | 40.174M |
| OKX XRP/USDT | 08:16:00.068 UTC | 0.9651 USDT | 0.9651 / 0.9652 | 1.04 bps | 46.940M |
| Bybit XRP/USDT | 08:07:10.663 UTC | 0.9665 USDT | 0.9664 / 0.9665 | 1.03 bps | 24.915M |

Sources: [Kraken public ticker](https://api.kraken.com/0/public/Ticker?pair=XRPUSD), [OKX public ticker](https://www.okx.com/api/v5/market/ticker?instId=XRP-USDT), [Bybit public ticker](https://api.bybit.com/v5/market/tickers?category=spot&symbol=XRPUSDT). Kraken's displayed top sizes were 85 XRP bid / 945 XRP ask; OKX 7,578.94 bid / 1,000 ask; Bybit 1,323.69 bid / 3,399.36 ask. These are one-level snapshots, not executable depth curves. The quote times differ; the price differences are not an arbitrage signal.

**Derivatives provider disagreement:**

- Liqwall reported XRP open interest of $919M at 07:42 UTC on Nov 20, down 0.2% over 24 hours; its displayed 30-day range was $914M on Nov 19 to $1.49B on Nov 4. [Liqwall source](https://liqwall.com/open-interest/xrp).
- TradRadar reported $1.19B across seven venues at 03:45 UTC, down 1.13% over 24 hours; OI-weighted funding was -0.0039% per eight hours, its five-venue account long/short ratio was 3.37 (77.1% long), and reported liquidations were at least $5.09M, including $4.30M longs and $792.10K shorts. [TradRadar source](https://tradradar.io/markets/xrp).
- CoinPerps' Nov 19 09:02 UTC snapshot reported $1.95B OI across 28 markets and +0.0063% OI-weighted funding per eight hours. [CoinPerps source](https://www.coinperps.com/perpetuals/xrp).

These totals have different timestamps and provider/contract universes. They must remain separate observations; do not average them or treat their difference as a real-time flow. Negative funding and long liquidations are counter-evidence to a simplistic bullish-leverage narrative, but do not independently establish a directional forecast.

**Institutional rails and counter-hypothesis:**

- BNY's Oct 27 primary announcement says its Digital Asset Custody platform now supports XRP and RLUSD for eligible institutional clients, building on BNY's RLUSD reserve-custody and Ripple Prime relationships. It discloses no XRP purchase, custody balance or incremental XRP demand. [BNY primary release](https://www.bny.com/corporate/global/en/about-us/newsroom/press-release/ripple-expands-strategic-digital-assets-collaboration-with-bny-across-custody-and-tokenized-trade-finance.html).
- Reuters reported on Nov 18 that DBS and Circle partnered to give eligible institutional clients direct USDC mint/redeem access through DBS and 24/7 USD-USDC settlement. This is a competing institutional dollar rail; it does not require XRP as a bridge asset. [Reuters](https://www.reuters.com/world/asia-pacific/dbs-partners-with-circle-expand-institutional-access-usdc-asia-2026-11-18/).

The core counter-hypothesis remains active: growth in custody, RLUSD, USDC, tokenized deposits or stablecoin settlement can benefit institutional digital-asset infrastructure without creating proportional XRP spot demand.

## Identity and exact-phrase research

- Japan's SBIC East, SBIC Central and SBIC West remain distinct regional SME investment-development companies. They are not SBI Holdings. Prior primary-source verification is preserved in the historical research records.
- “SBIC, ChatGPT SBIC” remains unresolved as an exact phrase. A Japanese SBIC West generative-AI/ChatGPT training event does not prove an OpenAI partnership. SBIC can also refer to unrelated concepts such as the Social Bias Inference Corpus; retain the context-specific distinction.
- “ASK Coin” remains ambiguous. Permission Coin's ASK is a candidate, but no direct XRP/XRPL/Ripple/Coinbase/Circle relationship has been established.
- “Actual capital” has no verified primary-source meaning as a distinct XRP metric. Cash proceeds, in-kind contributions, token transfers, market capitalization and wallet balance changes remain separate.
- Kamilah/Camilla Stevenson identity research remains quarantined by channel provenance. A first-person podcast identity clue is not sufficient to attribute the candidate XRP/Stocks channel or its uploads to the same person. No unverified channel inventory is promoted to an official creator inventory.

## Nine-platform coordination

The capability/authentication/permission/data-flow map covers ChatGPT, Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks. Only the current ChatGPT session and GitHub repository connector were tested. The GitHub connector reports repository admin/maintain/push/pull/triage capabilities, but branch-protection API access still returned 403. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks have no tested authentication/data flow in this run. No external model dispatch or cross-platform data transfer occurred. Least-privilege gates remain required.

## Open PR backlog — all 17 preserved

- **Active integration / blocked:** #1673. One coherent integration PR; no new successor.
- **Superseded-content candidates, pending final file-level verification after a successful merge:** #1663 (predecessor integration); #1677 (all 6 changed paths overlap #1673); #1670 (all 12 changed paths overlap #1673); #1541 (MMI claim-fingerprint content requires lossless reconciliation).
- **Partially superseded / preserve for review:** #1671. All 8 paths overlap #1673, but workflow content is not identical; retain any intentionally omitted security behavior until exact content review.
- **Unique or blocked work:** #1668 (3 paths overlap but provider-failover changes are not integrated); #1664 (paid-issue product/publication flow; no publication authorization); #1666 (Kaggle dependency upper-bound change); #1665 (pylint dev-dependency update).
- **Unique/unreviewed research lineage:** #1265, #1353, #1436, #1437, #1440, #1450 and #1460. Preserve; do not bulk-close.

Merged PRs #1672 and #1674 remain on main. No source PR was closed in this run. After #1673 is merged and its contents are verified on main, close only exact duplicates/superseded sources with explicit cross-references.

## Prediction readiness and next actions

**DESIGNED:** The integration includes public-source adapters, raw SHA-256 receipts, receipt-chain verification, point-in-time features, four deterministic baselines, chronological walk-forward evaluation, calibration, drift checks, event timelines, counter-hypotheses and a fail-closed forecast ledger.

**EXECUTED:** Exact full-suite verification on code head 6628327; dependency, Money and A2A Worker checks; 69-workflow security inspection; public spot API observations; cross-provider derivatives disagreement review; BNY and DBS/Circle institutional-rail review.

**VERIFIED:** Code head 6628327 passes 4,440 tests and all measured coverage floors. Exact-head merge gate remains BLOCKED. Scheduled XRP ingestion is not active on main because its workflow exists only on the integration branch.

**NOT VERIFIED / BLOCKERS:**
1. Independent WORM retention and trusted timestamp anchoring.
2. Scheduled XRP ingestion execution on main or an authorized integration-branch dispatch path.
3. Synchronized historical spot, Level-2 depth, derivatives, ETF and exchange-flow datasets with source-vintage receipts.
4. A learned candidate that outperforms naive, momentum, mean-reversion and volatility baselines in leakage-safe out-of-sample evaluation.
5. Stable probability calibration, residual dependence and concept-drift validation.
6. At least 100 out-of-sample and 100 shadow observations, five independent source groups and independent signed evaluator attestation.
7. Independent PR approval, verifiable branch-protection settings and the Pages publication decision.

**Forecast status: NOT_ISSUED.** No directional XRP forecast, paper trade or real-money action occurred.

Next actions:
1. Keep #1673 as the sole integration PR; do not create another branch or PR.
2. Obtain an independent approving review and independently verifiable branch-protection requirements. Keep fail-closed behavior.
3. Resolve the public Pages publication boundary before any merge that changes public assets.
4. Reconcile #1677, #1671, #1670 and #1541 at file-content level; retain unique work.
5. Establish independent WORM/timestamp anchoring.
6. Activate public XRP ingestion only after the integration reaches main or an authorized workflow-dispatch path is available; preserve the read-only permission boundary.
7. Expand synchronized historical data, then test learned candidates against all four baselines. Keep forecast issuance disabled until the readiness and independent-attestation gates pass.

## Safety record

This run advanced only the existing integration branch. No force-push, reset, clean, stash, history rewrite, main write, merge, PR creation, PR closure, deployment, Pages publication, secret rotation, Space/Worker restart, Databricks write, Kaggle download/submission, external model dispatch, external data transfer, paper trade, funds transfer or real-money operation occurred.

## Preserved Run174 regression anchors

The original Run174 recovery audit remains part of this integration's preserved evidence: `Run174`, historical main SHA `5b2a9c46eb878250dfec99190e294909cd5835bf`, and `research/xrp_intelligence/20261115T210147Z-run174-mainline-successor-recovery-audit.json`. This historical anchor is retained for regression traceability; it is not the current main SHA and must not be used as a present-day base.


## Current execution update — 2026-11-20T03:40:32.475Z

### Repository integration — VERIFIED

- Main SHA: `73e4dfa1ce4f21a8d419ef7e2e90d402b28d577f`
- Existing integration branch: `integration/xrp-v3-mainline-successor-20261120T0135Z`
- Branch head before this documentation/evidence update: `a96dbcd07c290e63f4f5ebbbc5351094cae0ee50`
- Last code-bearing head: `2d38b05a2a20d929cba26a685b4ad0204108f3f3`; `a96dbcd` fixed only the historical Run174 handoff regression anchor.
- Integration ancestry: **501 commits ahead, 0 behind** current main.
- Main tree: **1,744 entries**; integration tree: **3,020 entries**; no main paths are missing from integration.
- PR #1673: **1,477 changed files**, including **69 workflow definitions**; still open and draft.
- Open PR inventory: **16**. No branch or PR was created. No PR was closed.

The Run174 evidence anchor is preserved, including historical main SHA `5b2a9c46eb878250dfec99190e294909cd5835bf`. It is historical evidence, not the current main base.

### Exact-head verification — VERIFIED

Exact head `a96dbcd07c290e63f4f5ebbbc5351094cae0ee50`:

- Full repository suite: **4,390 passed, 1 skipped, 0 failed**, 11 warnings, 19 subtests.
- Runtime: **187.14 seconds**.
- Inclusive coverage: **71.34%**; legacy/core coverage: **81%**.
- XRP telemetry: 92%; MMI: 92%; feature store: 80%; forecast ledger: 97%; point-in-time features: 89%; source registry: 95%; Barrot integration: 62%; AGI orchestrator: 52%.
- Push CI: [44668095924](https://github.com/Barrot-Agent/B-Agent/actions/runs/44668095924) — passed.
- PR CI: [44668101674](https://github.com/Barrot-Agent/B-Agent/actions/runs/44668101674) — passed, including the full suite and validation-only Pages build.
- Dependency audit: [44668096070](https://github.com/Barrot-Agent/B-Agent/actions/runs/44668096070) and [44668101701](https://github.com/Barrot-Agent/B-Agent/actions/runs/44668101701) — passed, six manifests.
- Money audit: [44668101743](https://github.com/Barrot-Agent/B-Agent/actions/runs/44668101743) — passed, 14 tests.
- A2A worker tests: [44668101689](https://github.com/Barrot-Agent/B-Agent/actions/runs/44668101689) — passed.
- Fail-closed gates: [44668095922](https://github.com/Barrot-Agent/B-Agent/actions/runs/44668095922) and [44668101736](https://github.com/Barrot-Agent/B-Agent/actions/runs/44668101736) — blocked as designed.
- GitHub Actions cache budget is exhausted and cache is read-only; this produced a cache-save warning, not a test failure.

Main SHA `73e4dfa1ce4f21a8d419ef7e2e90d402b28d577f` passed main CI in [run 44653118253](https://github.com/Barrot-Agent/B-Agent/actions/runs/44653118253): 1,219 passed, 0 failed, 2 skipped, 8 subtests, 78% coverage.

### Merge decision — NO MERGE

PR #1673 is mergeable at the Git level but remains draft, has zero independent approving reviews, and branch-protection details remain inaccessible (HTTP 403). The fail-closed gate correctly refuses readiness. Required check contexts, administrator enforcement and approval requirements cannot be independently verified. GitHub Pages publication remains enabled on main and is not authorized.

No merge, force-push, branch-protection bypass or source-PR closure occurred.

### Workflow and security review — EXECUTED, transitive review INCOMPLETE

All **69/69 changed workflow YAML definitions** received a surface review of triggers, permissions, secret references, action references and potential side effects. Selected high-risk scripts were also inspected. This is not a complete audit of every invoked script or third-party action dependency.

1. Main `.github/workflows/paid-issue-publish.yml` remains an active `contents:write` workflow-run publisher that copies generated files and pushes directly to main. The integration successor disables it.
2. Main `.github/workflows/coinbase-paper-trader.yml` is manually dispatched, loads `GROQ_API_KEY`, writes simulated state and pushes to main without typed confirmation or an expected-main-SHA gate. The integration successor disables it. It was not run.
3. Main `deploy-a2a-worker.yml` attempted a Cloudflare deployment after PR #1672 was merged. [Run 44653118169](https://github.com/Barrot-Agent/B-Agent/actions/runs/44653118169) failed with Cloudflare authentication errors 10000/9109; the secret-upload step was skipped. No successful deployment or secret upload was verified. The integration workflow is manual-only and requires explicit deployment and secret-rotation confirmations plus an exact-main-SHA check. It was not dispatched.
4. The integration A2A runner is opt-in via `BARROT_A2A_AUTO_RUNNER=YES`, but its subprocess inherits the host environment. No OS sandbox, egress restriction or independent task-level authorization is verified. Keep it quarantined.
5. `scripts/push_with_token.sh` defaults `BRANCH=main` and can push directly to main. It does not force-push, but it can bypass PR review if branch protection permits. A direct-main guard is required before autonomous use.
6. Kaggle submission and Databricks write workflows were not dispatched. No Kaggle submission or Databricks write occurred.
7. GitHub Pages deployment on main is automatic and succeeded in [run 44653117146](https://github.com/Barrot-Agent/B-Agent/actions/runs/44653117146); publication authorization is not granted. Integration Pages workflow is validation-only.
8. Detailed branch-protection access remains HTTP 403; the only returned fallback ruleset is disabled. Connector token scopes have not been introspected.

The workflow surface review is complete; transitive script/action review remains **INCOMPLETE**. No secrets were read or rotated, and no external model was dispatched.

### XRP public ingestion — EXECUTED on the integration branch

Last successful ingestion: [run 44654352643](https://github.com/Barrot-Agent/B-Agent/actions/runs/44654352643), event `push`, head `4cf4039771450b13469b96ecec52ad06d124a602`, created 2026-11-20 01:32:27 UTC.

- 34 source receipts: 22 raw payloads retained, 12 digest-only.
- 21 source failures: Binance historical/derivatives provider client errors; Bybit HTTP 403; SEC EDGAR six requests blocked because a monitored contact identity was missing.
- 128 eligible features; 367 excluded features.
- Five source-independence groups; zero point-in-time timestamp violations.
- 150 events and 117 scenarios.
- Receipt chain passed within this run; no independent external timestamp/WORM anchor.
- Raw/event/receipt artifacts retain for 90 days; per-run feature-store artifact retains for 7 days. These are not WORM retention.
- Hourly/daily schedules are configured on the integration branch but are **not active on main** while PR #1673 remains unmerged.

### XRP market microstructure — RESEARCH ONLY

These public indexed snapshots have no raw HTTP bytes, SHA-256 receipt or independent timestamp anchor. None is admitted to the feature store.

- Fuelmaps, 2026-11-20 00:00 UTC: six-venue XRP mid $0.9598; within ±1%, bids $12.6M versus asks $8.1M; within ±2%, bids $17.6M versus asks $9.2M; within ±10%, coverage 5/6.
- Basis, 2026-11-20 00:23 UTC: Binance XRPUSDT perpetual mid $0.9650, spread 1.04 bps; within ±0.5%, bids $6.1M versus asks $9.2M; within ±1%, bids $11.6M versus asks $13.0M.
- Robod, 2026-11-20: reported $0.9680, 24-hour futures volume $1.41B, spot volume $589.36M, open interest $1.01B and liquidations $3.53M (longs $2.75M; shorts $784,100). Aggregator coverage/weighting is not established.
- Swiftedge, 2026-11-19 20:36 UTC: perpetual price $0.9617; bid wall $0.9560 / 6.17M XRP; ask wall $0.9650 / 5.06M XRP.

Fuelmaps' multi-venue spot aggregation shows greater bid depth near the mid; Basis' single-venue perpetual snapshot shows greater ask depth inside ±0.5% and ±1%. Robod and Swiftedge have different universes and timestamps. Preserve the disagreement; do not average or infer direction.

Sources: [Fuelmaps](https://fuelmaps.io/order-book/), [Basis](https://www.basischarts.com/liquidity-heatmap/xrp-usdt), [Robod](https://robod.com/markets/xrp?range=all), [Swiftedge](https://swiftedge.uk/xrp/levels).

### Identity and exact-phrase research

- Japan's SBIC East official training page lists a June 12–13, 2025 generative-AI/machine-learning course for investee companies that includes ChatGPT and Copilot. This is education, not an OpenAI partnership or evidence of XRP/Ripple activity: [SBIC East course](https://www.sbic.co.jp/training/20250612co/).
- Exact phrase `SBIC, ChatGPT SBIC` remains unresolved.
- `ASK Coin` remains unresolved; Permission Coin (ASK) is still the strongest exact-name candidate surfaced, with no verified XRP/XRPL relationship.
- `actual capital` remains unresolved at primary-source level. Fund cash purchases, in-kind contributions, corporate equity financing and market-cap changes remain separate categories.
- Kamilah/Camila Stevenson guest identity has interview/video-level support, but YouTube channel ownership remains unverified. Candidate channel IDs `UCqUPJMQdkCN6lsLVDnichPA` and `UCXm6KAr1WHF6UN7g5b2W7wg` are not linked by a first-party cross-reference. Only provisional video-level matches are retained; no channel-wide inventory is claimed.

Sources: [iHeart interview](https://www.iheart.com/podcast/1333-the-xrp-podcast-with-paul-284128923/episode/crypto-panics-with-dr-kamilah-stevenson-336576069/), [Glasp channel candidate](https://glasp.co/youtube/channel/UCqUPJMQdkCN6lsLVDnichPA), [YouTube channel candidate](https://www.youtube.com/channel/UCXm6KAr1WHF6UN7g5b2W7wg).

### Forecast state — NOT_ISSUED

The integration contains public-source adapters, SHA-256 receipts, a point-in-time feature store, four deterministic baselines, chronological purged/embargoed evaluation, calibration, drift diagnostics and a fail-closed forecast ledger. The dataset is not mature enough for directional forecasts. External WORM anchoring, synchronized historical depth/derivatives/flows, sufficient effective out-of-sample windows, independent evaluator keys and shadow validation remain incomplete. No directional forecast, paper trade or real-money action occurred.

### Open PR backlog — 16 preserved

- **Blocked:** #1673, #1671, #1668, #1666, #1541, #1265.
- **Superseded candidate:** #1663; keep open until #1673 is merged and its content is verified on main.
- **Duplicate candidate:** #1665; close only after successor merge and main verification.
- **Unique/unreviewed:** #1664, #1670, #1450, #1460, #1440, #1437, #1436, #1353.

No unique research branch was closed or discarded.

### Next concrete actions

1. Add a direct-main guard to `scripts/push_with_token.sh` and test it.
2. Complete the transitive script/action security audit, including A2A sandboxing, credential isolation, egress controls and task-level authorization.
3. Obtain independent review and administrator-confirmed branch-protection/required-check evidence.
4. Resolve the GitHub Pages publication boundary and the remaining automatic main writers.
5. Establish independently controlled WORM/timestamp anchoring.
6. Configure a monitored SEC contact identity; diagnose Binance and Bybit ingestion failures.
7. Expand synchronized historical spot, continuous order-book, derivatives, ETF cash/in-kind and exchange-flow datasets; then evaluate learned candidates against all four baselines.
8. Keep all eight external platform connections unverified until authentication and data flow are actually tested.

No merge, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external model dispatch, external data transfer, paper trade, funds transfer or real-money action occurred in this execution.

## Run 232 — mainline reconciliation, exact-head verification and XRP evidence refresh

Captured: 2026-11-20T04:07:18Z. This section supersedes older repository/market snapshots above where dates conflict; historical sections remain preserved.

### Repository integration — EXECUTED and VERIFIED

- Main SHA at inspection: `33d02d3b3251350aaede9df04fcb701f2398d016`.
- Existing PR #1673 branch head before this handoff update: `ab7caabaa823c24c6f0f0e4a5c02f2235979940a`.
- Main advanced through merged PR #1674. Its three new paths were `barrot_agent/reverse_engineering/__init__.py`, `barrot_agent/reverse_engineering/curriculum.py`, and `tests/test_reverse_engineering_curriculum.py`.
- The existing integration branch was updated with a normal two-parent merge commit `ab7caabaa823c24c6f0f0e4a5c02f2235979940a` (first parent previous integration head `419557bbb21f5aa22941bcd109d9a66a4b1a446b`; second parent current main `33d02d3b3251350aaede9df04fcb701f2398d016`). This was a fast-forward ref update; no force-push, branch rewrite, new branch or new PR.
- GitHub compare confirms 503 commits ahead / 0 behind. Recursive trees: main 1,748 entries; integration 3,024; 1,276 integration-only entries; zero main paths missing. PR #1673 still reports 1,477 changed files.
- The three #1674 files are now present in the integration tree. No path collision was found because they were new on main and absent from the predecessor integration tree.
- PR #1673 remains open and draft. GitHub reports `mergeable=true`; no independent approving review exists. The current branch is synchronized to main, so the former five-commit-behind condition is resolved.

### Exact-head CI — VERIFIED on `ab7caabaa823c24c6f0f0e4a5c02f2235979940a`

- PR CI [44671594675](https://github.com/Barrot-Agent/B-Agent/actions/runs/44671594675): full repository suite **4,394 passed, 1 skipped, 11 warnings, 19 subtests**, 116.54 seconds.
- Push CI [44671588537](https://github.com/Barrot-Agent/B-Agent/actions/runs/44671588537): full repository suite **4,394 passed, 1 skipped, 11 warnings, 19 subtests**, 201.52 seconds.
- Inclusive coverage 71.37%; legacy/core 81%; XRP telemetry 92%; MMI 92%; feature store 80%; forecast ledger 97%; point-in-time features 89%; source registry 95%; Barrot integration 62%; AGI orchestrator 52%. All configured mission-critical package floors passed.
- Dependency audit [44671588476](https://github.com/Barrot-Agent/B-Agent/actions/runs/44671588476): passed. Money audit [44671594638](https://github.com/Barrot-Agent/B-Agent/actions/runs/44671594638): passed. A2A Worker tests [44671594514](https://github.com/Barrot-Agent/B-Agent/actions/runs/44671594514): passed. GitHub Pages validation-only build passed.
- The 11 warnings are legacy pytest functions returning values. GitHub Actions cache reservation failed because the repository cache budget is read-only; this was non-blocking and did not fail the suite.
- Fail-closed PR gate [44671594394](https://github.com/Barrot-Agent/B-Agent/actions/runs/44671594394) and push gate [44671588502](https://github.com/Barrot-Agent/B-Agent/actions/runs/44671588502) both failed closed for exactly three blockers: PR remains draft, no independent approving review exists, and branch-protection details could not be verified. The gate did not merge or bypass anything.
- The handoff update itself is documentation-only and creates a new PR head. Its own exact-head CI must complete before any later merge decision; the 4,394-test result above belongs to the verified code head `ab7ca...`, not to a subsequent documentation commit.

### Security, workflow and authorization review

- The integration changes 69 workflow YAML files. This run inspected 17 high-risk workflows and the associated A2A/Kaggle/paper-trading entry points. The transitive script/action security audit remains **INCOMPLETE**; do not describe the entire 69-workflow surface as fully security-cleared.
- `barrot-gated-merge.yml` is read-only and fail-closed. It checks draft state, independent review, exact head, main base, required checks and branch-protection settings; it does not approve, bypass or merge.
- `xrp-public-ingestion.yml` is integration-only. Its hourly/daily schedule is not active on main. The integration-branch merge commit did not alter its path, so no ingestion run is claimed for this commit.
- `barrot-ops.yml` exposes manual Databricks write operations guarded by main ref, exact expected main SHA, explicit `YES` confirmation and host allowlisting. No Databricks write or job run occurred.
- `kaggle-competitions.yml` can submit competition entries through `scripts/kaggle_competitions_automation.py`; it is manual, requires exact main SHA, an explicit competition allowlist and `confirm_submit=YES`. No Kaggle submission occurred. The separate dataset-download workflow is not a submission.
- `deploy-a2a-worker.yml` requires explicit deployment confirmation and a separate secret-rotation confirmation. No deployment, secret rotation or Space/Worker restart occurred.
- `paid-issue-publish.yml`, `coinbase-paper-trader.yml` and `barrot-self-upgrade.yml` are disabled by an explicit false condition in the inspected integration versions. No publication, paper trade or self-upgrade was executed.
- `scripts/barrot_mcp_server.py` keeps its automatic runner opt-in through `BARROT_A2A_AUTO_RUNNER=YES`; if enabled, its subprocess inherits the host environment. OS sandboxing, task-level authorization and egress restrictions remain unverified. It was not enabled.
- `opencode.json` retains ask-before-action for edit/bash operations. `scripts/push_with_token.sh` still defaults to `main` and lacks a verified direct-main guard; do not use it for autonomous writes.
- GitHub Pages automatically deployed after the unrelated #1674 main merge. PR #1673 changes public web assets; merging it would publish those changes. Publication authorization is not recorded, so this is an additional merge blocker.
- Branch-protection API continues to return HTTP 403. The only visible fallback ruleset is disabled. Effective required contexts, strict checks, administrator enforcement and approval count remain unverified. The GitHub connector reports `admin`, `maintain`, `push`, `pull` and `triage`; token scopes were not introspected. Dependabot/code-scanning/secret-scanning alert details were not available through the tested connector endpoints.

### Nine-platform coordination map

- The structured map `research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_latest.json` remains the last saved map. It was captured at 2026-11-20 03:40:32 UTC; its platform statuses remain valid, but its repository-state fields still reference the pre-#1674 main SHA and an older integration head. Refresh the map and its tests on a later run.
- This run re-tested only the ChatGPT session -> GitHub connector -> `Barrot-Agent/B-Agent` path. Its effective permission list is visible, but token scopes are not introspected. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks remain unverified live connections.
- No external model dispatch, external data transfer, Kaggle submission, Databricks write or third-party credential use occurred. Independent red-team quorum remains unexecuted.

### XRP spot, derivatives and liquidity — RESEARCH ONLY

These web/API observations were not captured as raw HTTP bytes or SHA-256 receipts. They are not feature-store inputs and are not forecast-eligible.

**Spot snapshot around 2026-11-20 04:00–04:02 UTC:**

- Kraken XRP/USD: last `$0.96389`; bid/ask `$0.96403 / $0.96415`; indicative top-of-book spread approximately 1.24 bps; 24-hour volume approximately 47.69M XRP; high/low `$0.99680 / $0.94679`. The returned ticker had no exchange event timestamp.
- OKX XRP/USDT: last `0.9620`; bid/ask `0.9619 / 0.9620`; indicative spread approximately 1.04 bps; 24-hour volume approximately 45.69M XRP; event timestamp `2026-11-20T04:00:28.181Z`.
- OKX USDT/USD conversion event timestamp was `2026-11-20T03:44:07.073Z`, 16 minutes 21 seconds older than the XRP/USDT quote. USD normalization was rejected. The two venues' raw quote volumes are not additive and are not a synchronized global spot measure.
- No synchronized Level-2 depth curve was admitted. Top-of-book spreads do not establish executable depth, slippage or market-wide liquidity.
- Sources: [Kraken public ticker](https://api.kraken.com/0/public/Ticker?pair=XRPUSD), [OKX XRP-USDT ticker](https://www.okx.com/api/v5/market/ticker?instId=XRP-USDT), [OKX USDT-USD ticker](https://www.okx.com/api/v5/market/ticker?instId=USDT-USD).

**Derivatives and liquidity disagreement:**

- CryptoQuant's Nov 18 Binance 7-day spot-to-futures ratio was 17.9%, down from about 27.2% earlier in November (34.2% decline); the implied Binance futures volume was about 5.6x spot. This is Binance-only, not the entire market: [CryptoQuant ratio](https://cryptoquant.com/insights/quicktake/6afd2614d38bc874c06073dc-XRP-Binance-Spot-to-Futures-Ratio-Drops-34-as-Price-Falls-Below-1).
- A separate CryptoQuant/Arab Chain Binance 30-day liquidity index was approximately 0.041, a three-month low, with 30-day turnover near $2.71B: [CryptoQuant liquidity index](https://cryptoquant.com/insights/quicktake/6afd157f1dd13d48fe974b34-XRP-Binance-30D-Liquidity-Index-Hits-a-Three-Month-Low). The index is not executable order-book depth.
- CryptoPotato relays the same CryptoQuant observations and must not be counted as an independent source. Its report also notes Binance XRP open interest near $325M versus about $1.5B earlier in 2026 and estimated leverage ratio 0.13. Lower open interest/leverage may reduce liquidation fuel while weak spot liquidity may amplify price impact; net volatility effect remains unresolved.
- CME's primary Q3 2026 report records XRP futures/options suite ADV of 12.2K contracts and $10.1B notional volume. This is regulated cash-settled derivatives activity, not direct XRP spot purchases or net capital inflow: [CME Q3 2026 crypto report](https://www.cmegroup.com/newsletters/quarterly-cryptocurrencies-report/2026-q3-cryptocurrency-highlights.html).
- A secondary Nov 19 Bitcoin.com report relaying CME's X post states $81.2B cumulative XRP/Micro XRP futures notional through Nov 16. Keep this separate from the primary Q3 suite figure; notional turnover is not capital invested or open interest: [Bitcoin.com report](https://news.bitcoin.com/featured/cmes-xrp-futures-hit-81-2-billion-after-18-months-of-trading/).

### ETF holdings and exchange-wallet reconciliation — RESEARCH ONLY

- XRP Insights' ETF JSON was generated at `2026-11-20T03:49:15Z`, with settled data through Nov 18 and a provisional Nov 19 row. Its Nov 16–18 computed holdings-change flow was approximately `-5,151,723 XRP`; reported total holdings were `1,183,950,358 XRP` as of Nov 18.
- The tracker covers six spot ETF products plus BITW. GXRP flows were excluded because its holdings scrape was blocked while GXRP remained included in total holdings. Flow is inferred from holdings changes, not issuer-reported cash creation/redemption; BITW rebalancing and fee accruals can affect the change. A Nov 19 row is provisional and may be revised.
- XRP Insights' license permits citation with attribution but requires written permission for commercial redistribution. No raw payload was saved or admitted to the feature store: [ETF data JSON](https://xrp-insights.com/data/xrp-etf-flows.json).
- The exchange-wallet tracker snapshot is daily, not live: approximately 22.18B XRP across 707 attributed wallets at 24 exchanges, about 32.2% of its circulating-supply denominator. It includes approximately 484M XRP in wrapped/insurance reserves. Same-wallet changes were about -155.7M XRP over 7 days and -444.3M over 30 days.
- Attributed balances include Upbit approximately 6.46B XRP, Coinbase approximately 5.83B (including about 153.1M cbXRP reserve), Binance approximately 2.59B, and SBI VC Trade approximately 56.3M with over 99% labeled cold. These are wallet-label estimates, not beneficial ownership, tradable float or confirmed customer withdrawals. Wallet coverage and cold/wrapped reserves can change the totals: [exchange-wallet data JSON](https://xrp-insights.com/exchange-balances/data.json).
- FXEmpire's Nov 19 secondary report claimed roughly `$19M` in weekly ETF outflows. That figure is not reconciled to XRP Insights' `-5.15M XRP` computed Nov 16–18 holdings changes; different universes, dates and valuation methods may explain the difference. Preserve the disagreement; do not average the two figures.

### Macro and regulatory context

- The Bank of Japan's current-account rate is 1.25% since Sept 24, 2026; its next policy meeting is Dec 17–18. Its October Outlook was highlighted Nov 16; the latest published opinions cover the Oct 29–30 meeting. This is a global liquidity/yen-carry context variable, not an XRP-specific signal: [BOJ](https://www.boj.or.jp/en/), [2026 meeting minutes](https://www.boj.or.jp/en/mopo/mpmsche_minu/minu_2026/index.htm).
- The Federal Reserve's November 2026 regulatory service notes the Sept 16 FOMC rate increase and IORB at 3.90% from Sept 17. The Board also proposed GENIUS Act rules for Board-supervised payment stablecoin issuers and related anti-tying provisions, with comments due Nov 30. These may affect USDC/RLUSD issuer and bank rails, not prove XRP demand: [Federal Reserve Regulatory Service](https://www.federalreserve.gov/frrs/federal-reserve-regulatory-service.htm).
- The SEC/CFTC March 17, 2026 interpretive release lists XRP among digital commodities under the agencies' current taxonomy. The SEC Division of Corporation Finance FAQ updated Nov 2 explicitly says the FAQs are staff views, not a rule, regulation or Commission statement, and have no legal force. Transaction-specific investment-contract analysis remains fact-dependent: [SEC crypto FAQs](https://www.sec.gov/about/divisions-offices/division-corporation-finance/faqs-crypto-assets), [SEC/CFTC interpretive release](https://www.sec.gov/files/rules/interp/2026/33-11412.pdf).

### Identity, exact phrases and public-video attribution

- `ASK Coin`: exact searches still do not identify a unique XRP-linked entity. Results include unrelated `askr` and Permission Coin/ASK candidates; neither has a verified XRP/Ripple/Coinbase/Circle relationship.
- `actual capital`: exact phrase appears in an Aug 23 AInvest AI-assisted article saying Ripple's actual capital is flowing into RLUSD. This is secondary editorial language, not a defined accounting category or primary capital-flow disclosure: [AInvest article](https://www.ainvest.com/news/ripple-75-licenses-don-serve-token-serve-company-2608/). The intended original reference remains unresolved.
- `SBIC, ChatGPT SBIC`: exact phrase remains unresolved. SBIC East/Central/West remain separate Japanese SME investment-development entities, not SBI Holdings. SBIC East's generative-AI course and SBIC West's ChatGPT seminar are educational events, not OpenAI partnerships.
- The June 11, 2026 iHeart XRP Podcast interview verifies a guest identified as Dr. Kamilah Stevenson. In the auto-generated transcript she gives X as `@iamcamstevenson`, Instagram as `@KamillaStevenson`, and YouTube as 'doctor Kamilah Stevenson'; the host also uses the spelling Camilla. The transcript is direct guest-level evidence but contains spelling/transcription variation: [iHeart interview](https://www.iheart.com/podcast/1333-the-xrp-podcast-with-paul-284128923/episode/crypto-panics-with-dr-kamilah-stevenson-336576069/).
- The channel candidate `@KamilahStevensonXrpStocks` / ID `UCXm6KAr1WHF6UN7g5b2W7wg` is not linked by a first-party cross-reference to the guest's stated YouTube identity. The video [I Moved My XRP Off The Exchanges](https://www.youtube.com/watch?v=TfFx0g2IgGg), dated May 20, 2026, is attributed to Kamilah by YouTube search and discussed by DailyCoin, but its uploader/channel ownership remains unverified. Treat it as a video-level candidate, not an official creator-uploaded inventory. The prior channel candidate `UCqUPJMQdkCN6lsLVDnichPA` is also not cross-linked.

### Prediction readiness — NOT_ISSUED

- Implemented on integration: public source adapters, SHA-256 raw receipts and receipt-chain checks, append-only SQLite point-in-time feature store, four deterministic baselines, chronological purged/embargoed walk-forward tests, temporal calibration, drift diagnostics, event/scenario/counter-hypothesis records and fail-closed forecast ledger.
- The readiness policy requires at least 100 effective out-of-sample observations and 100 shadow observations, at least five source clusters, superiority to all four baselines on proper scoring rules with paired bootstrap checks, weighted calibration error no greater than 0.05, a minimum horizon/data multiple, and independent Ed25519 evaluator attestation.
- Independent WORM/timestamp anchoring, synchronized historical spot/depth/derivatives/ETF/exchange-flow data, stable real-data calibration, sufficient shadow outcomes and independent evaluator keys remain incomplete. No directional forecast was issued. No paper trade or real-money action occurred.

### Open PR backlog — 16 preserved

- **Blocked:** #1673 (draft, no independent approval, branch protection 403, Pages publication boundary); #1671 (write-capable self-upgrade workflow changes); #1664 (paid-issue publication and paper-trade artifacts); #1668 (Cloudflare/OpenRouter/Gemini fallback adds external data flows and secrets); #1666 (Kaggle dependency range conflicts with current compatibility cap); #1541 (unique MMI claim-identity security change pending review).
- **Superseded candidate:** #1663. Keep open until #1673 is merged and all content is verified on main.
- **Duplicate candidate:** #1665. Its Pylint `>=4.1.4` change is already present in the integration branch; close only after successor merge and main verification.
- **Unique/unreviewed:** #1670 (separate creative feature); #1450; #1460; #1440; #1436; #1437; #1353; #1265 (preserve research/repair lineage).
- `PR_BACKLOG_TRIAGE.md` remains an older historical snapshot; this canonical handoff is the current backlog source until that separate artifact is deliberately reconciled.

### Next concrete actions

1. Let the documentation-only handoff commit's exact-head CI finish; do not merge while the PR remains draft or approval/branch-protection evidence is missing.
2. Resolve the GitHub Pages publication authorization boundary before any merge that changes public web assets.
3. Refresh the structured nine-platform map and its tests with main `33d02d3`, integration `ab7ca...` and current PR/CI/backlog state.
4. Complete transitive workflow/script security review; add a direct-main guard to `scripts/push_with_token.sh`; assess A2A sandbox, inherited credentials and egress restrictions.
5. Establish independent WORM/timestamp anchoring and repair SEC contact identity / exchange provider ingestion gaps.
6. Build synchronized historical XRP spot, continuous depth, derivatives, ETF cash/in-kind and exchange-wallet datasets with point-in-time receipts; then evaluate learned candidates against all four baselines.
7. Keep all eight external platforms unverified until authentication and data flow are actually tested. No external dispatch or transfer until authorized.

No merge, main deployment initiated by this run, secret rotation, Space/Worker restart, Kaggle submission, Databricks write, external model dispatch, external data transfer, paper trade, funds transfer or real-money action occurred.


---

## Run 11 — current-main integration, exact-head verification and fresh XRP evidence
Updated: 2026-11-20T07:40:00Z

### Repository state — VERIFIED

- Repository: Barrot-Agent/B-Agent.
- Current main: 7f8e3626c355bb3d89afdff56aeed5e056cb88f4.
- Current integration branch: integration/xrp-v3-mainline-successor-20261120T0135Z.
- Current integration PR: #1673, head b091e91eb406a8e58f272f166da1472448eff42b.
- PR ancestry: 514 commits ahead, zero behind current main; merge base is the current main SHA.
- PR size: 1,491 changed files, 534,174 additions, 6,997 deletions.
- Main tree: 1,751 entries. Integration tree: 3,039 entries.
- Integration-only entries: 1,288. Modified shared paths: 263. Main paths missing from integration: zero.
- The most recent main commit, 7f8e362, is a paid-issue scan that changes only PAID-ISSUES.md and data/money/paid_issues.json. The CI workflow explicitly ignores those paths. Main's latest observed scheduled Cross Analysis and Pages runs succeeded; the last code-bearing main test baseline remains the post-#1674 run recorded above. No main write occurred in this run.
- Main's BARROT_XRP_MISSION_HANDOFF.md remains a stale November 4 snapshot. This file is the canonical current integration handoff. The 713 KB BARROT_XRP_MISSION_HANDOFF_CURRENT.md is historical append-only material and was not rewritten.

### Exact-head verification — VERIFIED on b091e91

Full repository CI run 44695508091 passed on the exact current PR head:

- Full repository suite: 4,433 passed, 1 skipped, 11 warnings, 23 subtests passed in 207.40 seconds.
- Full-suite aggregate coverage: 72% (31,341 statements; 8,829 missed).
- Mission package floors:
  - AGI orchestrator: 52% (floor 50%).
  - XRP telemetry matrix: 92% (floor 85%).
  - MMI contract/execution/ledger: 92% (floor 85%).
  - Barrot integration: 62% (floor 60%).
  - Feature store: 80% (floor 80%).
  - Forecast ledger: 97% (floor 90%).
  - Point-in-time features: 89% (floor 85%).
  - Source registry: 95% (floor 90%).
- Core Tests job: passed.
- Full repository test suite job: passed.
- GitHub Pages build, validation-only: passed.
- Dependency Audit 44695508178: passed.
- Money audit 44695508006: passed.
- A2A Worker Tests 44695508001: passed.
- Exact-head CI: https://github.com/Barrot-Agent/B-Agent/actions/runs/44695508091
- Exact-head fail-closed gate: https://github.com/Barrot-Agent/B-Agent/actions/runs/44695508040

The full-suite job discovers tracked active test modules across the repository, including the required legacy modules, rather than only the hand-selected core subset. It excludes only explicitly disabled, quarantined and fixture test paths. The global 62% floor and the mission-specific floors passed.

Coverage is improved but not complete. The legacy/core 70% report still excludes several major subpackages from that particular floor. The global 72% report includes the measured Barrot package set, but monetization, rendering, smart_agent and mem_palace do not yet have dedicated minimum floors. Next coverage task: inspect the exact-head coverage XML and add evidence-based package floors for those areas without lowering existing gates. Do not invent floors before measuring them.

### Merge decision — BLOCKED, fail-closed

PR #1673 remains draft. Its review inventory contains zero submitted reviews and zero independent approvals. GitHub reports mergeable=true, but that is not merge authorization.

The branch-protection endpoint returned HTTP 403, Resource not accessible by integration. The only repository ruleset returned is Fall Back with enforcement disabled. Effective required checks, strict-up-to-date enforcement, required approval count, force-push restrictions and administrator enforcement therefore remain unverified.

The fail-closed gate reported exactly:
- PR is still draft.
- No independent approving review exists.
- Branch protection could not be verified; the gate refuses to infer approval or bypass settings.

No merge, force-push, branch-protection bypass, source-PR closure or main-branch write occurred. Pages ran validation-only on the integration head; no publication occurred. The explicit public Pages publication boundary remains unresolved.

### Integration and overlap inventory — EXECUTED / NOT YET MERGED

PR #1673 is the sole active consolidated V3/XRP integration workstream. No branch or PR was created in this run.

Current open PR inventory: 17.

- #1673 — active consolidated integration; draft and blocked by approval/branch-protection/publication gates.
- #1677 — A2A quarantine/deployment hardening; non-draft, stale base, six changed paths all overlap #1673. #1673's body says the manual-only deployment, runner opt-in and permission hardening are represented. Keep as a duplicate/supersession candidate until content is verified on main.
- #1671 — inbound GPT Actions authority gate; draft, eight changed paths all overlap #1673. The successor says the gate module, guarded write routes and regression tests are integrated, while conflicting self-upgrade workflow changes were deliberately omitted. This is partial source-PR reconciliation, not an exact duplicate.
- #1670 — Musical DNA recursive-learning feature; non-draft, all 12 changed paths overlap #1673. The successor says the feature modules, docs, optional dependencies and tests are integrated. Duplicate candidate only after main verification.
- #1668 — provider failover; draft, all three paths overlap #1673, but the successor explicitly says its behavior is not included pending file-level compatibility review. Preserve as unique/blocked.
- #1666 — Kaggle dependency update; non-draft, two paths, one shared. Its requested Kaggle range conflicts with the integration's current compatibility cap. Blocked pending compatibility evidence.
- #1665 — Pylint dependency update; non-draft, its only path overlaps #1673 and requirements-dev.txt already contains pylint>=4.1.4. Duplicate candidate pending main verification.
- #1664 — paid-issue product work; draft, 134 paths with six overlaps. Not integrated; preserve separately and keep publication/paper-trading gates.
- #1663 — older consolidated integration predecessor; draft, all 1,470 changed paths overlap #1673. Superseded as the active integration branch, but do not close until #1673 is merged and every relevant file is verified on main.
- #1541 — MMI claim-identity fingerprint security change; draft, all five paths overlap #1673. The successor says the implementation is already present. Duplicate candidate pending exact content and main verification.
- #1460, #1450, #1440, #1437, #1436, #1353 and #1265 — preserve as unique research/repair lineage. Do not bulk-close or flatten their evidence.

Ready: none. Blocked work remains blocked. No source PR was closed. The inventory is current to the GitHub open-PR response retrieved during this run.

### Workflow, dependency and external-action security

- The integration branch's .github/workflows/ci.yml has separate core and full-repository jobs. The full-suite job passed on b091e91.
- The dependency audit checks six manifests and the PEP 621 dependency list; exact-head audit passed.
- requirements-dev.txt contains pylint>=4.1.4. pyproject.toml still caps Kaggle at >=1.5.12,<1.6; the proposed #1666 range is not accepted without compatibility testing.
- scripts/push_with_token.sh on the current integration branch rejects BRANCH=main with exit code 6. This direct-main guard is present in the inspected source; alternate push paths still require a whole-repository workflow/script audit.
- deploy-a2a-worker.yml is workflow_dispatch-only, requires explicit YES for deployment and explicit YES for secret rotation, and checks the exact current main SHA before deployment. The Cloudflare action is pinned to a full commit SHA and checkout credentials are not persisted.
- The A2A runner remains separately gated by BARROT_A2A_AUTO_RUNNER=YES. Default OpenCode configuration does not supply the A2A gateway URL or runner credentials and uses ask-before-action permissions.
- No A2A deployment, secret rotation, Space/Worker restart, Kaggle submission, Databricks write, paid-issue publication, paper trade, funds transfer or real-money action occurred.

### Public XRP ingestion — DESIGNED, not yet scheduled on main

The integration branch contains .github/workflows/xrp-public-ingestion.yml. It defines hourly and daily schedules, read-only actions:read and contents:read permissions, pinned actions, public-source capture, SEC filing ingestion, content-addressed raw receipts, a cross-run receipt-chain index, point-in-time SQLite checkpoints, event timelines, drift reports and walk-forward baseline outputs.

The workflow is not present on current main, so GitHub's default-branch schedule does not execute it yet. Integration pushes can trigger a scoped read-only capture; manual dispatch is defined, but the available GitHub connector does not expose a workflow-dispatch action. The workflow uses 90-day raw/event artifacts, a 7-day per-run feature checkpoint and a 90-day daily feature backup. These are expiring GitHub artifacts, not WORM retention or independent timestamp anchoring. No manual ingestion run was dispatched in this run.

### Fresh XRP market and institutional evidence — RESEARCH ONLY

**Exchange ticker observations, retrieved approximately 2026-11-20 07:37 UTC:**

- Kraken XRP/USD: last 0.95949; bid 0.95956; ask 0.95957; 24-hour volume 40,050,948 XRP. The returned ticker payload did not expose an exchange event timestamp.
- OKX XRP-USDT: last 0.9665; bid 0.9664; ask 0.9665; 24-hour volume 46,464,803 XRP. The server timestamp in the payload was 2026-11-20T07:12:42.461Z, about 25 minutes older than the retrieval time.
- These are not synchronized quotes. USD/USDT normalization and cross-venue price-discovery conclusions are rejected. The 24-hour volumes are not additive. No synchronized Level-2 depth payload was captured; depth remains unavailable for this observation. No market value was admitted to the feature store because exact raw HTTP bytes, headers and immutable receipt hashes were not captured.
- Kraken source: https://api.kraken.com/0/public/Ticker?pair=XRPUSD
- OKX source: https://www.okx.com/api/v5/market/ticker?instId=XRP-USDT

**Goldman Sachs Q3 2026 13F — primary SEC filing:**

Goldman Sachs Group Inc. filed Form 13F-HR on November 16, 2026, for the period ended September 30, 2026. Its information table reports five XRP spot ETP share positions:

- Franklin XRP Trust: 2,953,228 shares; reported value $47,783,229.
- Bitwise XRP ETF: 2,307,591 shares; reported value $38,375,238.
- Canary XRP ETF: 2,108,998 shares; reported value $33,258,898.
- Grayscale XRP Trust ETF: 503,523 shares; reported value $14,501,462.
- 21Shares XRP ETF: 695,767 shares; reported value $10,081,664.
- Combined reported value: $144,000,491 as of September 30.

This is a delayed 13F disclosure of ETF/ETP shares, not direct beneficial ownership of XRP, not a current November 20 position, not a report of XRP token purchases, and not evidence of post-September net capital inflow. It excludes many positions and does not reveal intra-quarter trading or short exposure.

Primary filing index: https://www.sec.gov/Archives/edgar/data/886982/000088698226000647/0000886982-26-000647-index.htm
Primary information table: https://www.sec.gov/Archives/edgar/data/886982/000088698226000647/xslForm13F_X02/Submit_this.xml

**Roundhill XRP Covered Call Strategy ETF withdrawal — primary SEC filing:**

On November 18, 2026, Roundhill requested withdrawal of Post-Effective Amendment No. 191 and associated delaying filings for its proposed XRP Covered Call Strategy ETF. The filing states that the trust no longer intends to seek effectiveness and that no securities were sold or will be sold under the registration statement. It gives no reason for the withdrawal. This was a proposed options-income product, not a spot XRP ETF; do not interpret the withdrawal as a spot-ETF redemption or infer the reason from the filing.

Primary SEC filing: https://www.sec.gov/Archives/edgar/data/1976517/000139834426020270/fp0101810-3_aw.htm

CoinDesk's November 19 report says Amplify's XRPM held about $10.36M and SOLM about $1.94M, with the two income products together at $12.3M versus approximately $3.26B in spot funds at October end. This is secondary, narrow product-universe context and not evidence of spot XRP ETF demand: https://www.coindesk.com/markets/2026/11/19/roundhill-scraps-solana-and-xrp-income-etfs-as-rival-funds-attract-just-usd12-million.

**Circle / DBS USDC rail — primary issuer announcement, November 18:**

Circle and DBS announced direct institutional USDC minting and redemption through DBS, with 24/7 USD-USDC settlement. Circle says this reduces institutions' reliance on secondary-market USDC liquidity for issuance/redemption. This is a competing regulated dollar-payment and liquidity rail. It demonstrates institutional stablecoin infrastructure expansion but does not establish XRP bridge-asset demand, XRP purchases or XRPL settlement.

Primary announcement: https://www.circle.com/pressroom/dbs-and-circle-expand-institutional-access-to-usdc-in-asia.

**Market drawdown and ETF flow report — secondary source, November 19:**

Bloomingbit reported XRP fell more than 20% in November and reached an intraday low near $0.89 on November 15. It relayed SoSoValue weekly spot XRP ETF outflows of approximately $19.13M for November 9–13 and a Binance spot/futures volume ratio of 17.9%, down from 27.2% earlier in November. This article includes an AI-generated summary and secondary analyst attributions; no raw SoSoValue or CryptoQuant source payload was captured in this run. The reported weekly dollar outflow is not directly comparable with the existing XRP Insights computed holdings-change figure of about -5.15M XRP for November 16–18. Different periods, universes, units and methods remain separate; do not average or silently reconcile them.

Source: https://en.bloomingbit.io/feed/news/124850.

**Stablecoin counter-hypothesis:** Circle's DBS mint/redeem arrangement and the previously recorded Coinbase/RLUSD distribution, BNY custody and Standard Chartered RLUSD custody/collateral initiatives show that regulated stablecoin rails can expand independently of XRP bridge usage. RLUSD activity on XRPL is not equivalent to XRP demand. XRP custody, RLUSD settlement, XRPL transactions and open-market XRP purchases remain separate features.

### SBIC, exact phrases and Kamilah/Camilla Stevenson

- Japan's Tokyo SBIC published a two-day June 12–13, 2025 training course covering generative AI, machine learning and ChatGPT usage for portfolio companies. This is primary evidence of an educational course, not an OpenAI partnership or evidence that SBIC is SBI Holdings. The regional SBIC East/Central/West entities remain distinct from SBI Holdings.
- Tokyo SBIC course: https://www.sbic.co.jp/training/20250612co/
- Exact phrase ASK Coin: no new primary-source XRP-linked entity resolution in this run. Existing ASK/ASKR and Permission Coin candidates remain distinct and unlinked.
- Exact phrase actual capital: no new primary-source use establishing a defined accounting category or XRP capital flow. Keep unresolved.
- Exact phrase SBIC, ChatGPT SBIC: no exact-phrase resolution. The SBIC training course is context only.
- The June 11, 2026 iHeart interview transcript identifies a guest as Dr. Kamilah Stevenson. In the auto-generated transcript she gives X as @iamcamstevenson, Instagram as @KamillaStevenson, and YouTube as Doctor Kamilah Stevenson; she warns about fake pages. This is direct guest-level evidence with transcription/spelling variation: https://www.iheart.com/podcast/1333-the-xrp-podcast-with-paul-284128923/episode/crypto-panics-with-dr-kamilah-stevenson-336576069/
- A YouTube channel candidate @drkamilahstevenson matches the spoken channel name, but the interview page does not provide a first-party hyperlink to that exact handle. The separate @KamilahStevensonXrpStocks channel (ID UCXm6KAr1WHF6UN7g5b2W7wg) remains unlinked. Do not merge those channel identities.
- Public videos indexed as attributed to Kamilah Stevenson include: Ripple Just Became a BANK — And XRP Holders Need to Understand This (2025-12-14, QslbjGQD0MU); XRP ETFs Are Here. Price Isn't Moving. Here's What Everyone's Missing (2026-01-13, ci0FH73lbCs); Why Most People Will Lose Their Crypto Wealth (Even If They're Right) (2026-01-15, cxeX_eu_2H0); How Much XRP Do You ACTUALLY Need? (2026-03-19, rv0BAV0vLgo); Why XRP Matters More Than Your Paycheck (2026-04-17, Us_FIT4RByY). Glasp transcripts/attribution and YouTube search metadata are secondary/indexed evidence; they do not conclusively prove uploader ownership of the candidate channel. Keep the inventory provisional pending a first-party channel cross-link.
- Example video sources: https://www.youtube.com/watch?v=QslbjGQD0MU ; https://www.youtube.com/watch?v=ci0FH73lbCs ; https://www.youtube.com/watch?v=cxeX_eu_2H0 ; https://www.youtube.com/watch?v=rv0BAV0vLgo ; https://www.youtube.com/watch?v=Us_FIT4RByY

### Nine-platform coordination map — refreshed observation, not live federation

The structured nine-platform map last had a workflow-backed observation on November 4, 2026 and is stale for current account state. This run independently tested only the GitHub repository connector, which returned admin, maintain, push, pull and triage permissions for Barrot-Agent/B-Agent. That does not establish any other platform connection.

- ChatGPT: current session only; no separate Barrot API credential or persistent adapter tested.
- Claude: no authenticated request tested.
- Grok: no xAI authentication tested. Groq is a separate provider and is not Grok.
- Gemini: no authenticated request tested.
- Copilot: prior single-use review event only; no persistent agent adapter verified.
- Codex: no separate CLI/API authentication tested.
- Hugging Face: prior public runtime probe only; no write credential or deployment authorization verified.
- Kaggle: dependency audit only; no Kaggle API authentication or submission tested.
- Databricks: prior HTTP 403 remains ambiguous among token, workspace, principal and policy; no write tested.

No external model dispatch, structured evidence transfer or agent-to-agent collaboration was performed. Least-privilege and fallback designs remain architecture, not proof of live connectivity.

### Prediction status — NOT_ISSUED

The integration branch contains public source adapters, raw-source SHA-256 receipts, receipt-chain validation, an append-only SQLite point-in-time feature store, four deterministic baselines, purged/embargoed chronological walk-forward evaluation, temporal calibration, drift diagnostics, event timelines, scenario/counter-hypothesis records and a fail-closed forecast ledger with independent Ed25519 evaluator-attestation requirements.

Still incomplete:
1. Independent WORM/timestamp anchoring.
2. Synchronized historical spot, executable Level-2 depth, derivatives, ETF cash/in-kind flows and exchange-wallet data with complete point-in-time receipts.
3. A trained XRP candidate demonstrating out-of-sample superiority to all four baselines.
4. Mature independent calibration, residual-dependence and drift validation.
5. Sufficient completed shadow observations and an independently operated evaluator key.

No directional forecast was issued. No paper trade or real-money action occurred. The fresh exchange snapshots above are research-only and not feature-store eligible.

### Next concrete actions

1. Keep #1673 as the single active integration PR; do not create another successor or feature PR.
2. Reconcile the exact content of #1677, #1671, #1670 and #1541 against the integration branch, preserving intentionally omitted workflow behavior.
3. Refresh the nine-platform structured map with current repository/run evidence and no unsupported connection claims.
4. Inspect the full-suite coverage XML and add dedicated floors for monetization, rendering, smart_agent and mem_palace based on measured coverage.
5. Complete the 69-workflow/script security review; retain the manual-only A2A deployment and explicit secret-rotation gate.
6. Establish independent WORM/timestamp anchoring and run the public XRP ingestion workflow when an authorized dispatch path is available; do not mistake expiring GitHub artifacts for WORM.
7. Build synchronized historical market data and test a learned candidate against all four baselines. Keep forecast issuance disabled until readiness policy and independent attestation pass.

DESIGNED, EXECUTED and VERIFIED remain distinct. No merge, main write, publication, deployment, secret rotation, Space/Worker restart, Kaggle submission, Databricks write, external model dispatch, external data transfer, paper trade, funds transfer or real-money action occurred.


---

## Execution checkpoint — 2026-11-20 09:10 UTC

### Mission priority and execution status

**Priority 1 remains XRP intelligence and measured prediction-engine mastery.** Barrot V3 remains the execution, orchestration, safety and verification foundation. This checkpoint preserves the prior handoff verbatim and appends the current observations; it does not rewrite prior history.

### Current repository state — VERIFIED

- Repository: `Barrot-Agent/B-Agent`; default branch: `main`.
- **Current main SHA:** `7f8e3626c355bb3d89afdff56aeed5e056cb88f4`; main tree: **1,751 entries**.
- **Active integration branch:** `integration/xrp-v3-mainline-successor-20261120T0135Z`.
- **Current integration head:** `0f4a2b98c12ee13790915d3ffd491624811c72f9`; integration tree: **3,040 entries**.
- Branch comparison against current main: **519 commits ahead, 0 behind**. The branch is based on the exact current main SHA. GitHub reports the PR mergeable, but its mergeable state is unstable because the PR remains draft.
- **PR #1673:** 1,494 changed files; 534,712 additions; 7,024 deletions. The paginated GitHub file inventory returned 1,494 unique paths. It includes 69 workflow files and 422 test files; the broad change set also contains creative/music capability work, so scope review is still required.
- **Open PR inventory:** 17. No branch, PR, issue or main ref was created, closed, rewritten or force-pushed in this checkpoint.
- The current handoff file exists on the integration branch. A lookup on `main` returns 404: this handoff is not yet on the default branch.

### Exact-head verification — VERIFIED on `0f4a2b9`

The current PR head is the documentation-only commit `0f4a2b98c12ee13790915d3ffd491624811c72f9`, whose sole changed path is `BARROT_XRP_MISSION_HANDOFF_LATEST.md`.

- [CI / full-suite run 44702604401](https://github.com/Barrot-Agent/B-Agent/actions/runs/44702604401): success.
- The **Full repository test suite** ran every tracked active repository test module, including required legacy modules. Job log: **4,440 passed, 1 skipped, 11 warnings, 23 subtests passed** in 120.27 seconds.
- Total coverage: **73.08%**. The repository-wide 62% floor, legacy/core 70% floor, and explicit mission-critical package floors all passed. The workflow now enforces coverage for monetization, rendering, smart_agent and mem_palace in addition to XRP telemetry, MMI, orchestration, feature store, forecast ledger, point-in-time features and source registry.
- [Dependency Audit 44702604415](https://github.com/Barrot-Agent/B-Agent/actions/runs/44702604415): success.
- [Money audit 44702604524](https://github.com/Barrot-Agent/B-Agent/actions/runs/44702604524): success.
- [A2A Worker Tests 44702604549](https://github.com/Barrot-Agent/B-Agent/actions/runs/44702604549): success.
- GitHub Pages validation-only build: success; it did not deploy Pages from the PR.
- The cache save emitted a read-only/budget warning. It did not fail the test job.
- [Fail-closed gate 44702604475](https://github.com/Barrot-Agent/B-Agent/actions/runs/44702604475): failed as designed. Its log records two blockers: PR is still draft; branch protection could not be verified, so the gate refuses to infer approval or bypass settings.
- PR #1673 has **zero submitted reviews**. No independent approval exists.

### Merge and branch-protection decision — BLOCKED

- PR #1673 remains draft. Do not merge.
- GitHub branch metadata reports `main` as protected and exposes `enforcement_level=non_admins`, but the returned required-check contexts and checks arrays are empty.
- The direct `/branches/main/protection` request returns HTTP 403. Effective required checks, strict-up-to-date enforcement, administrator enforcement and approval count cannot be verified.
- The only visible repository ruleset, `Fall Back`, is **disabled** and contains only deletion/non-fast-forward rules.
- Pages is enabled. A successful main-branch Pages deployment occurred at [run 44688456863](https://github.com/Barrot-Agent/B-Agent/actions/runs/44688456863). Merging #1673 would change public web assets; no separate publication approval is recorded.
- No merge, approval, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external model dispatch, paper trade, funds transfer or real-money action occurred.

### Mainline workflow side effects and unresolved security blockers — VERIFIED

Main has active workflows that the integration branch has already hardened or quarantined. Their current main versions were fetched and inspected; none was dispatched by this run.

1. `.github/workflows/paid-issue-publish.yml` on main has `contents: write`, runs after the scheduled Paid issue hunter, copies the hunter artifact into repository files and directly pushes a commit to `main`. It ran successfully at [44688383358](https://github.com/Barrot-Agent/B-Agent/actions/runs/44688383358); the resulting main commit `7f8e362` is the paid-issue hunter update. The integration version disables this publisher pending authorization and independently verified branch protection.
2. `.github/workflows/barrot-sync.yml` on main runs on every main push, receives `GH_TOKEN`, invokes `b_agent.py --sync`, stages `BARROT_SYNC.md`, and attempts `git push` without a direct-main guard. The integration version is materially safer. Do not assume its push step was harmless merely because its prior run completed.
3. `.github/workflows/barrot-self-upgrade.yml` on main has write permissions and can create candidate branches/PRs after a manual YES, but does not itself enforce the full open-PR inventory, one-active-PR rule or exact current-main-SHA check. The integration version is quarantined with no credentials or mutation.
4. `.github/workflows/coinbase-paper-trader.yml` on main can run the legacy BTC-USD simulated trader and commit simulated state without a separate per-run approval input. It was not run. The integration version is disabled; it is not the XRP shadow evaluator.
5. `.github/workflows/deploy-a2a-worker.yml` on main is push-triggered for `a2a/**` and uploads the Worker authentication secret during deployment. The integration version is manual-only, requires explicit deployment and secret-rotation confirmations plus the exact current main SHA, and pins the Cloudflare action. The earlier Cloudflare deployment attempt failed authentication; no successful deployment or secret rotation is established.
6. `.github/workflows/barrot-ops.yml` on main has a broad manual YES gate but can overwrite a Databricks workspace path and download a Kaggle dataset without an exact current-main-SHA guard. The integration version separates the Databricks-create and dataset-download confirmations, verifies exact main SHA, and refuses overwrite.
7. Main's Hugging Face sync is manual but uploads Space code and propagates multiple secrets under one confirmation. The integration version quarantines it pending private-target verification and separate secret-rotation approval.
8. Main's Databricks deploy and Kaggle submission workflows are manual and have explicit YES inputs; the integration version adds stronger exact-SHA/allowlist controls or quarantines legacy paths. No dispatch occurred.

`scripts/push_with_token.sh` on the integration branch explicitly rejects `BRANCH=main`; the current main version does not contain that guard. These mainline workflows are not safe to treat as inert. The large integration PR contains the corresponding hardening, but it cannot be merged until all exact-head, approval, branch-protection, security and publication gates are genuinely satisfied.

### Open PR backlog — all 17 preserved

| PR | Classification | Current disposition |
|---|---|---|
| #1673 | **Blocked** | Single active V3/XRP integration successor; draft, no reviews, protection unresolved, Pages publication not authorized |
| #1663 | **Superseded** | Predecessor to #1673; keep open until successor is merged and content is verified on main |
| #1677 | **Superseded candidate / blocked** | A2A quarantine and runner opt-in hardening are represented in #1673; retain source PR until main verification |
| #1671 | **Superseded candidate / blocked** | GPT Actions authority gate and route tests are represented in #1673; workflow changes intentionally excluded |
| #1541 | **Superseded candidate / blocked** | MMI claim fingerprint is represented in #1673; stacked source PR remains preserved |
| #1670 | **Unique/unreviewed** | Musical DNA capability is a distinct creative workstream, but its files were layered into #1673; #1670 is currently dirty against its base. Scope contamination must be resolved without discarding work |
| #1668 | **Blocked / unique** | Provider failover workstream; separate compatibility and secret/worker security review required |
| #1664 | **Blocked / unique** | Paid-issue product pack; staged only, no publication authorization |
| #1666 | **Blocked / unique** | Kaggle dependency update; based on stale main and needs current-main compatibility review |
| #1665 | **Blocked / unique** | Pylint dependency update; based on stale main and needs current-main compatibility review |
| #1460 | **Unique/unreviewed** | XRP institutional multirail, Binance and Kamilah research |
| #1450 | **Unique/unreviewed** | Binance phase-one, escrow and PR #1449 research audit |
| #1440 | **Unique/unreviewed** | XRP archive validation trigger repair |
| #1437 | **Unique/unreviewed** | XRP ledger source addenda and snapshot-pointer repair |
| #1436 | **Unique/unreviewed** | Binance theft, issuer-freeze and attacker-wallet graph research |
| #1353 | **Unique/unreviewed** | Lossless XRP ledger sharding and hash-verified validation |
| #1265 | **Unique/unreviewed** | Compact XRP ledger index and hash-verified snapshot pointer |

No PR is declared ready to merge. Do not close any source PR until a merged successor's exact content is verified on main. Do not bulk-close unique research or feature work.

### Fresh public XRP market observation — research-only, not feature-store eligible

**Spot:** Kraken's public XRP/USD ticker was fetched at approximately 09:10 UTC on November 20. The endpoint does not provide an exchange event timestamp in this response, so retrieval time is not represented as quote time.

- Last: **$0.95742**.
- Bid: **$0.95732**; ask: **$0.95744**.
- Top-of-book spread: approximately **1.25 bps**.
- 24-hour volume: **40.05 million XRP**.
- 24-hour high/low: **$0.99680 / $0.94679**; open: **$0.95925**.
- Direct endpoint: https://api.kraken.com/0/public/Ticker?pair=XRPUSD

This is a single venue's level-1 ticker. It does not establish cross-venue executable liquidity, slippage, or depth. Direct order-book endpoints could not be retrieved through the available web reader; no Level-2 depth value is admitted.

**Derivatives provider disagreement — do not average:**

- Liqwall, 00:12 UTC Nov 20: all-exchange open interest about **$915M**, down 0.8% over 24 hours; its displayed 30-day range was approximately $914M–$1.49B.
- TradRadar, 03:45 UTC Nov 20: **$1.19B** across seven exchanges, down 1.13% over 24 hours; OI-weighted funding -0.0039% per 8 hours; reported 24-hour liquidations at least $5.09M, including $4.30M longs and $0.792M shorts.
- OptimistFi, 06:49 UTC Nov 20: approximately **$1.7B** across 38 venues, with CME shown as 21% of the aggregate and funding reported at -2.9% annualized, paid to longs.
- Sources: https://liqwall.com/open-interest/xrp ; https://tradradar.io/markets/xrp ; https://optimistfi.com/perps/markets/xrp

The different venue universes, update times, instrument inclusion and calculation methods explain why these figures are not one interchangeable OI series. Negative funding and lower OI are descriptive positioning observations, not a directional forecast.

**ETF flow disagreement — provider coverage remains incomplete:**

- CryptoETF.today's Nov 20 page reports Nov 19 net flow of zero, the last listed move as a $4.9M XRPC outflow on Nov 17, 30-trading-day net flow of -$19.0M, cumulative net flow +$1.79B and net assets around $1.08B.
- TradersWeek reports Nov 19 net flow of zero as preliminary, with only five of six funds reported; its seven-day net is -$8.4M and holdings about 1.15B XRP.
- Sources: https://cryptoetf.today/en/xrp-etf-flows ; https://tradersweek.com/crypto/etf-flows

These are third-party trackers with different product universes and completeness. The zero Nov 19 observation does not erase earlier weekly/monthly outflows. No raw bytes, provider receipts or issuer-level reconciliation were captured in this run; these observations are not model-feature eligible.

### Institutional, custody, collateral and payment-rail research

The primary announcements establish relationships and product availability, not automatic XRP demand.

1. **BNY / Ripple — Oct 27, 2026.** BNY says it is RLUSD's primary reserve custodian, has a custody relationship with Ripple Prime, and now supports both XRP and RLUSD on its Digital Asset Custody platform. This establishes institutional custody capability. It discloses no XRP custody balance, new purchase or incremental spot flow. Source: https://www.bny.com/corporate/global/en/about-us/newsroom/press-release/ripple-expands-strategic-digital-assets-collaboration-with-bny-across-custody-and-tokenized-trade-finance.html
2. **Coinbase / Ripple — Oct 28, 2026.** Coinbase made RLUSD available on Coinbase Prime, Coinbase Exchange and its retail app, with deposits/withdrawals across XRPL, Base and Ethereum and USD conversion at 1:1. Coinbase Global Exchange collateral support was described as a future capability, not live at launch. Ripple said it would provide liquidity on Base. This is RLUSD distribution and multi-chain access; it is not proof of XRP bridge-asset demand. Source: https://www.coinbase.com/blog/rlusd-is-now-available-on-coinbase
3. **SBI / Ripple — Jun 24, 2026.** Ripple announced JFSA-approved RLUSD availability for institutional and retail customers through SBI VC Trade's VCTRADE platform. This confirms a Ripple–SBI Group distribution relationship, but does not establish that XRP is required for RLUSD payments or that SBI bought XRP in the market. Source: https://ripple.com/ripple-press/ripple-and-sbi-group-partner-to-launch-ripple-usd-in-japan/
4. **SBI / Circle — prior joint venture, operating from Mar 2025.** Circle's primary announcement says its Japan partnership with SBI Holdings began in 2023 and SBI VC Trade launched USDC in Japan on March 26, 2025. SBI is therefore a multi-rail stablecoin distributor/partner, not an exclusive Ripple channel. Source: https://www.circle.com/pressroom/circle-strengthens-commitment-to-japan-with-new-investment-and-expanded-usdc-access
5. **Circle / DBS — Nov 18, 2026.** DBS and Circle announced direct USDC mint/redeem access for eligible institutional clients through DBS, with 24/7 USD-USDC settlement. This is a competing/parallel regulated stablecoin rail and does not require XRP by the terms of the announcement. Source: https://www.dbs.com/newsroom/DBS_and_Circle_expand_institutional_access_to_USDC_in_Asia
6. **Standard Chartered / Ripple / LMAX — Oct 12, 2026.** Ripple reports Standard Chartered custody support for RLUSD on XRPL is live. The planned LMAX collateral-mirroring arrangement remains subject to final documentation, testing, law, internal approval and jurisdiction readiness; do not mark RLUSD collateral acceptance as generally live. Source: https://ripple.com/ripple-press/standard-chartered-launches-rlusd-custody-and-joins-planned-collateral-integration-with-ripple-and-lmax-group/
7. **Ripple / Jeonbuk Bank — Aug 18, 2026.** Ripple announced deployment of Ripple Payments for cross-border remittances at Jeonbuk Bank. The announcement does not specify XRP bridge-asset usage. Record this as Ripple software/payment-rail adoption, not verified XRP settlement demand. Source: https://ripple.com/ripple-press/ripple-and-jeonbuk-bank-partner-to-modernize-cross-border-payments-for-korea-s-regional-banking-sector/

**Corporate economics and counter-hypothesis:**

- Circle's Q3 2026 release (Nov 4) reports average USDC circulation **$73.3B**, Q3 onchain transaction volume **$13.9T**, revenue and reserve income **$865M**, net income **$226M**, and Adjusted EBITDA **$317M**. It reports Circle Payments Network annualized TPV of **$41.3B** and a definitive Tazapay acquisition agreement expected to close in 2027 subject to approvals. It also reports a **$100M Binance equity investment** and expanded USDC distribution partnership. The $182M ARC presale contribution to other revenue means Q3 earnings/EBITDA should not be treated as recurring reserve income. Source: https://s206.q4cdn.com/265218871/files/doc_earnings/2026/q3/earnings-result/3Q26-Earnings-Release.pdf
- Coinbase's Q3 2026 release (Oct 29) reports average USDC held in Coinbase products of **$22B**, up 49% year over year, and says Coinbase captured approximately 50% of USDC economics over the prior year. It also reports 10.7% crypto trading-volume market share and 49% of net revenue from subscription/services. This documents the Coinbase–Circle distribution/economics connection; it does not prove Coinbase or Circle has an XRP spot accumulation strategy. Source: https://investor.coinbase.com/news/news-details/2026/Coinbase-Q3-2026-Earnings-Show-All-time-high-Coinbase-One-Subscribers-and-Prediction-Markets-Surpassing-200-Million-in-Annualized-Revenue/default.aspx

**Working interpretation:** regulated custody, stablecoin issuance/redemption, Ripple Payments, RLUSD distribution, XRP custody, collateral eligibility and open-market XRP purchases are separate variables. The evidence supports growing multi-provider institutional digital-asset infrastructure. It does not support collapsing that growth into one XRP demand or actual-capital number. Counter-hypothesis: USDC and RLUSD payment/treasury growth may occur with no incremental XRP bridge usage.

### Identity and exact-phrase status

- Japan's SBIC East/Central/West remain separate regional SME investment-development companies and are not SBI Holdings. No new primary-source evidence in this checkpoint changes that resolution.
- `ASK Coin`, `actual capital`, and `SBIC, ChatGPT SBIC` remain unresolved as the intended exact-phrase references. Do not substitute similarly named tokens, corporate acronyms or market-capitalization figures.
- The Kamilah/Dr. Kamilah Stevenson interview identity and the separate XRP/Stocks YouTube channel candidate remain unlinked. Do not merge channel identities or attribute every indexed video to the verified interview guest without a first-party cross-link.

### Prediction engine — implementation versus operation

**Implemented on the integration branch:** public exchange/XRPL source adapters; SHA-256 raw-source receipts and receipt-chain validation; append-only SQLite point-in-time feature store; naive class-prior, momentum, mean-reversion and volatility-normal baselines; chronological purged/embargoed walk-forward evaluation; temporal calibration; feature-drift diagnostics; event timelines; scenario/counter-hypothesis records; and a fail-closed forecast ledger requiring an independent Ed25519 evaluator attestation.

**Not yet verified/operational:**

- `.github/workflows/xrp-public-ingestion.yml` is present on this integration branch but returns 404 on `main`. GitHub scheduled workflows execute from the default branch, so the hourly/daily schedule is **not active on main**.
- The available GitHub connector exposes reads and workflow-log/artifact retrieval but no workflow-dispatch action. No manual ingestion dispatch was possible through the available connector. No push was manufactured solely to trigger the collector.
- No fresh exchange payloads were captured into this run's feature store. The Kraken, ETF and derivatives observations above are research notes only, not raw-source receipts.
- GitHub Actions artifacts/cache have finite retention and mutable storage semantics; the current ingestion workflow's 90-day artifacts are not independent WORM storage or trusted timestamp anchoring.
- A trained candidate has not demonstrated out-of-sample superiority to all four baselines. Mature calibration, residual-dependence/drift validation, completed shadow observations and independent evaluator operation remain outstanding.

**Forecast status: NOT_ISSUED.** No probabilities or directional price forecast are published. No paper trade or real-money action occurred.

### Nine-platform coordination

Only the GitHub repository connector was tested in this checkpoint. Repository metadata reports admin, maintain, push, pull and triage access for this repository. No authenticated data-flow test was performed for Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle or Databricks. No external model dispatch or evidence transfer occurred. The nine-platform map must continue to label those connections unverified.

### Next concrete actions

1. Keep #1673 as the only active V3/XRP integration successor. Do not create another overlapping successor.
2. Resolve the main-branch direct-write and external-action workflows recorded above through the existing integration branch; do not dispatch them.
3. Obtain an independently verifiable approval and effective branch-protection/required-check evidence. Keep the PR draft until those conditions and the Pages publication boundary are resolved.
4. Reconcile the separate Musical DNA feature scope without discarding its work or misrepresenting it as XRP functionality.
5. Activate the public XRP ingestion workflow only after its reviewed code is on the default branch or an authorized read-only dispatch path exists; preserve exact data cutoffs and raw receipts.
6. Establish independent WORM/timestamp anchoring, then build synchronized historical spot, executable depth, derivatives, ETF and exchange-flow datasets.
7. Complete leakage-safe learned-model evaluation against all four baselines, probability calibration and independent shadow evaluation before forecast issuance.

DESIGNED, EXECUTED and VERIFIED remain distinct. This checkpoint updates the durable handoff only; it does not claim that main has changed, that scheduled XRP ingestion is running, or that a predictive model is ready.

---

## Current-state superseding update — 2026-11-20T09:28:40Z

This section supersedes earlier current-state head, PR-count and verification summaries in this file. Earlier research and run sections remain historical; they are not deleted.

### Repository and integration state — VERIFIED

- Repository: `Barrot-Agent/B-Agent`.
- Current main: `7f8e3626c355bb3d89afdff56aeed5e056cb88f4`; main tree: **1,751 entries**, **85 workflow files**.
- Integration branch: `integration/xrp-v3-mainline-successor-20261120T0135Z`; tree: **3,040 entries**, **94 workflow files**.
- Exact code/test head: `fc61430d301f368432d49b2ead013294d3a490cb`.
- A map-only commit refreshed the nine-platform capability/authentication map at `5b118265d5114b4238062eea42a809d73dc04076`. This handoff update is documentation-only; do not represent either documentation commit as a code change.
- Active integration PR: [#1673](https://github.com/Barrot-Agent/B-Agent/pull/1673), draft, open, mergeable, **520 commits ahead / 0 behind main**, **1,494 changed files**, 534,880 additions and 7,024 deletions. Complete changed-file inventory: 69 workflows, 422 test paths, 74 `barrot_agent/` paths and 1,130 paths whose names contain XRP-related identifiers. GitHub's compare endpoint caps its returned file list at 300; the PR changed-file API was paginated to obtain the 1,494-path count.
- No branch or PR was created. No PR was closed. No merge was attempted.
- The latest handoff file and refreshed platform map are on the integration branch; `main` still contains only the older `BARROT_XRP_MISSION_HANDOFF.md` (last updated November 4). The new `LATEST` handoff is not on main until a future authorized, fully verified merge.

Main advanced from `08ecb81e9e7501a7ff4a241c2dae6eef766ff2d3` to `7f8e3626c355bb3d89afdff56aeed5e056cb88f4` through the existing Paid Issue Publisher workflow. That commit changed only `PAID-ISSUES.md` and `data/money/paid_issues.json`. The latest scheduled Cross Analysis run [44705889254](https://github.com/Barrot-Agent/B-Agent/actions/runs/44705889254) succeeded on current main. The latest full main CI found in the inspected run inventory is [44669957726](https://github.com/Barrot-Agent/B-Agent/actions/runs/44669957726) on the earlier `33d02d3` head; do not claim full main CI for `7f8e362` has been run.

### Exact-head CI and merge gate — VERIFIED

On exact code head `fc61430d301f368432d49b2ead013294d3a490cb`:

- PR CI [44709770035](https://github.com/Barrot-Agent/B-Agent/actions/runs/44709770035): passed.
- Full repository suite: **4,440 passed, 1 skipped, 11 warnings, 23 subtests passed**, 162.55 seconds; **4,441 items collected**.
- Inclusive coverage: **73.08%**; legacy/core coverage: **82%**.
- Mission-critical package floors passed: AGI orchestrator 52%; XRP telemetry 92%; MMI 92%; Barrot integration 62%; feature store 80%; forecast ledger 97%; point-in-time features 89%; source registry 95%; monetization 78%; rendering 71%; SmartAgent 77%; memory palace 100%.
- Dependency Audit [44709769890](https://github.com/Barrot-Agent/B-Agent/actions/runs/44709769890): passed.
- Money audit [44709769908](https://github.com/Barrot-Agent/B-Agent/actions/runs/44709769908): passed.
- A2A Worker Tests [44709769947](https://github.com/Barrot-Agent/B-Agent/actions/runs/44709769947): passed.
- Push CI [44709761030](https://github.com/Barrot-Agent/B-Agent/actions/runs/44709761030) and push Dependency Audit [44709761036](https://github.com/Barrot-Agent/B-Agent/actions/runs/44709761036): passed on the same head.
- GitHub Pages job was **validation only**; no deployment was performed by PR CI.
- The configured cache budget is exhausted/read-only. The cache-save warning did not affect test outcomes.

The fail-closed gate [44709769893](https://github.com/Barrot-Agent/B-Agent/actions/runs/44709769893) correctly returned BLOCKED for three reasons:
1. PR #1673 remains draft.
2. There is no independent approving review (review inventory empty; no requested reviewers).
3. The classic branch-protection endpoint returned HTTP 403, so effective required checks, strict status enforcement and administrator enforcement cannot be verified.

GitHub branch metadata reports `main` as protected but exposes an empty required-status-check context list. The only visible repository ruleset, “Fall Back,” has enforcement disabled. This is not sufficient proof of effective merge protection. Do not bypass the gate or infer approval requirements. The PR also changes public web assets; merging to main can trigger Pages publication. That publication boundary remains unauthorized/unresolved.

### Workflow, dependency and external-action audit — VERIFIED / PARTIAL

- Six Python dependency manifests are present: `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, `requirements-integrations.txt`, `hf_space/requirements.txt`, and `legacy/requirements_legacy.txt`. No dependency lockfile was found. Six-manifest dependency audit passed, but dependency resolution is not fully reproducible without a lock.
- `.github/workflows/xrp-public-ingestion.yml` exists only on the integration branch, not main. It is read-only (`actions: read`, `contents: read`), pins actions to full SHAs, checks out with `persist-credentials: false`, and schedules hourly plus daily runs. Its job condition allows scheduled capture only on `refs/heads/main`; on integration it permits scoped push or manual dispatch. Because the workflow is absent from main, **the production schedule is not active**. No manual dispatch was available in this run.
- The ingestion adapter covers Binance, Coinbase, Kraken, Bitstamp, Bitbank, OKX and Bybit spot, plus Binance/Bybit derivatives, Deribit XRP perpetual data, ETF issuer sources, XRPL, RLUSD/USDC, CFTC/SEC and Morpho cbXRP collateral data. It applies 300-second live-ticker freshness and 60-second order-book freshness checks, quote-basis skew checks, stale/crossed-book rejection and source-specific provenance checks.
- The workflow stores raw captures and hash-chained receipt indexes as GitHub artifacts with finite 90-day retention and uses GitHub cache/artifacts for continuity. This is **not independent WORM storage or external timestamp anchoring**. Missing predecessor artifacts, expired artifacts or unverified continuity remain explicit failure states.
- The SQLite feature store uses append-oriented records, triggers and manifest checks, but its own code documents that a file owner can drop triggers and recompute unkeyed hashes. Production tamper resistance still needs independently controlled signed/checkpointed receipts.
- The forecast ledger requires all four baselines, at least 100 out-of-sample samples, at least 100 shadow samples, at least five independent source groups, calibration error no greater than 0.05, and trusted external Ed25519 evaluator keys. An empty evaluator-key trust store fails closed.
- Verified quarantine/gates in the current integration: Paid Issue Publisher disabled with empty permissions; Coinbase Paper Trader disabled; Barrot Self-Upgrade disabled; Hugging Face sync disabled; legacy Databricks deploy disabled; general Barrot Agent issue automation disabled. A2A deployment is manual-only and requires explicit deployment confirmation, separate secret-rotation confirmation and exact current-main SHA. It was not dispatched.
- Release workflow is tag-triggered with `contents: write`; no tag was created. `scripts/push_with_token.sh` explicitly rejects direct pushes to main and avoids persisting the token. No secrets were read or rotated, no Pages/Cloudflare deployment was initiated, no Space was restarted, no Kaggle submission or Databricks write occurred, and no external model was dispatched.
- Merge would disable main's existing Paid Issue Publisher. This is a real workflow behavior change, not merely documentation; preserve it in the merge review.

### Current XRP market observations — RESEARCH ONLY, NOT MODEL-ELIGIBLE

Retrieval cutoff: approximately **2026-11-20 09:28:40 UTC**. These observations were viewed from public web endpoints/pages; this run did not capture exact raw response bytes into Barrot, compute Barrot SHA-256 receipts, or store a synchronized point-in-time feature snapshot. Do not ingest these rendered observations into training or issue a forecast from them.

**Spot ticker snapshots:**

| Venue / pair | Last | Bid / size | Ask / size | Approx. spread | 24h XRP volume | Timestamp quality |
|---|---:|---:|---:|---:|---:|---|
| Kraken XRP/USD | $0.96120 | $0.96061 / 329 XRP | $0.96070 / 667 XRP | 0.94 bps | 39.981M | Retrieval time only; ticker exposes no exchange timestamp |
| OKX XRP/USDT | 0.9605 USDT | 0.9604 / 3,752.804 XRP | 0.9605 / 2,089.321 XRP | 1.04 bps | 47.055M | Exchange timestamp 09:26:11.264 UTC; retrieved about 09:28:40 UTC |

Sources: [Kraken public ticker](https://api.kraken.com/0/public/Ticker?pair=XRPUSD), [OKX public ticker](https://www.okx.com/api/v5/market/ticker?instId=XRP-USDT). OKX quote conversion to USD was not captured. Kraken's reported 24h open field ($0.95925) and OKX's 24h open field (0.9838 USDT) disagree despite similar reported highs/lows; do not compute a cross-venue 24h return from those fields. The top-level quantities are small snapshots, not depth curves. Kraken/OKX depth endpoints were inaccessible through this web retrieval path and Bybit returned 403; **no synchronized Level-2 depth curve was verified**.

**Exchange-attributed XRPL wallets, 2026-11-20 08:00 UTC:** XRP Insights reports 22.18B XRP in 707 wallets attributed to 24 exchanges, about 32.2% of its 68.89B circulating-supply denominator. Same-wallet changes: **−86.0M XRP over 7 days** and **−434.3M over 30 days**. Labeled storage: 49% cold, 12% hot, 39% unclassified. Major rows include Upbit 6.46B, Coinbase 5.82B (including 153.7M cbXRP reserve), Binance 2.60B (including 327.4M Binance-Peg XRP reserve), Bithumb 1.77B and SBI VC Trade 53.8M. Source: [XRP Insights exchange balances](https://xrp-insights.com/exchange-balances). This is a labeled-wallet coverage measure, not customer deposits, beneficial ownership or freely tradable float. OKX, Korbit and Coins.ph have known wallet-coverage gaps. Wrapped reserves and cold custody must remain separated from executable venue liquidity.

**ETF-flow disagreement, 19 November session:**

- [CryptoKeyhole](https://cryptokeyhole.com/etf-flows/xrp/) updated 08:57 UTC on November 20. It shows 19 November as partial (2/3 daily reporters) with −3,251 XRP, 18 November as complete with −3,251 XRP, five complete trading days (12–18 November) at −876,320 XRP, 659,156,742 XRP held across three daily-collected funds on November 18, and cumulative flow −7,504,058 XRP through November 18. Its prose/table coverage labels need validation: the page describes 2/3 or three funds while the table displays four daily ticker columns.
- [Alpha Finance](https://alphafinance.io/etf/xrp/) reports zero net flow on November 19 across five funds, −$8.3M over November 12–19, −$19.1M over 30 sessions, and +$1.70B cumulative since November 2025. It states that its dashboard derives flow series and does not publish fund holdings/AUM.
- These are different fund universes, aggregation methods and source lineages. They are not independent confirmations of one underlying holdings series. Preserve the disagreement; do not average, substitute or silently reconcile.

**Institutional relationship update:** [Ripple's October 27 primary release](https://ripple.com/ripple-press/ripple-expands-collaboration-with-bny-across-custody-and-tokenized-trade-finance/) and [BNY's copy](https://www.bny.com/corporate/global/en/about-us/newsroom/press-release/ripple-expands-strategic-digital-assets-collaboration-with-bny-across-custody-and-tokenized-trade-finance.html) state that BNY is RLUSD's primary reserve custodian, has a custody relationship with Ripple Prime, and now supports XRP and RLUSD on its Digital Asset Custody platform. BNY and Ripple intend to explore RLUSD mint/redeem access and tokenized trade finance on XRPL with C2FO, subject to approvals. This verifies custody/service availability and announced intentions—not BNY proprietary XRP purchases, custody balances, realized collateral utilization or mandatory XRP bridge demand. Ripple's October 28 corporate claims of near-$900M annualized product revenue, 1,700+ institutions and $16T of 2025 product transaction volume remain company-reported metrics, not audited XRP demand.

### Identity, phrase and platform status

- Japan's SBIC East/Central/West remain separate regional SME investment-development entities, not SBI Holdings. Exact phrase “SBIC, ChatGPT SBIC” remains unresolved; an SBIC West ChatGPT/AI training event is not evidence of an OpenAI partnership.
- “ASK Coin” remains ambiguous; Permission Coin's ASK is a candidate without a verified direct XRP relationship.
- “Actual capital” remains an unverified phrase, not a defined XRP metric. Equity investment, committed financing, maximum facility size, token transfer, market capitalization and cash deployed must remain distinct.
- The `@KamilahStevensonXrpStocks` channel candidate remains unlinked to Dr. Kamilah/Camilla Stevenson's self-identified accounts. Do not attribute its videos to the verified interview guest without first-party cross-link evidence.
- The nine-platform map was refreshed in `research/xrp_intelligence/20261103-nine-platform-capability-authentication-map.json` at commit `5b118265d5114b4238062eea42a809d73dc04076`. Only ChatGPT current session and GitHub repository connector are verified. GitHub connector reports admin/maintain/pull/push/triage, but effective branch-protection configuration remains unverified. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks are not authenticated live connections; no cross-platform dispatch or data transfer occurred.

### Open PR inventory and overlap classification — all 17 preserved

| PR | Paths | Overlap with #1673 | Current classification / handling |
|---|---:|---:|---|
| #1673 | 1,494 | active integration | **Blocked**: draft, no independent approval, branch protection unresolved, Pages publication boundary |
| #1677 | 6 | 6 | A2A security overlap; compare exact content after successor verification; preserve until then |
| #1671 | 8 | 8 | Partially superseded: inbound gate code overlaps, but workflow-file changes were intentionally omitted; preserve |
| #1670 | 12 | 12 | Musical DNA capability overlaps; exact content verification required before any superseded classification/closure |
| #1668 | 3 | 3 | Provider failover remains distinct; do not assume overlap means integrated; preserve |
| #1666 | 2 | 1 | Kaggle dependency update; separate review |
| #1665 | 1 | 1 | Pylint dev-dependency update; separate review |
| #1664 | 135 | 6 | Paid-issue product/publication work remains distinct and publication-gated |
| #1663 | 1,470 | 1,470 | Predecessor integration; superseded candidate, close only after #1673 merges and its content is verified on main |
| #1541 | 5 | 5 | MMI claim-fingerprint overlap; exact content reconciliation still required |
| #1460 | 8 | 0 | Unique/unreviewed XRP research |
| #1450 | 116 | 0 | Unique/unreviewed XRP research |
| #1440 | 64 | 0 | Unique/unreviewed XRP validation work |
| #1437 | 5 | 0 | Unique/unreviewed XRP repair |
| #1436 | 24 | 0 | Unique/unreviewed Binance incident research |
| #1353 | 1,084 | 0 | Unique/unreviewed XRP ledger archive lineage |
| #1265 | 144 | 1 | Unique research/index work with one CI-path overlap |

No PR is ready to merge solely on the basis of an older head's checks. No source PR is closed. After #1673 eventually merges and its content is verified on main, close only exact duplicate/superseded source PRs with cross-references; preserve unique research.

### Prediction readiness and next action

**DESIGNED:** public-source adapters, SHA-256 receipts and receipt-chain format, point-in-time feature contract, append-oriented feature store, event timeline, four deterministic baselines, purged/embargoed chronological walk-forward evaluator, calibration/drift checks and a forecast ledger with independent evaluator signature requirements.

**EXECUTED:** current repository/tree/PR/branch/overlap/CI/workflow/dependency/security inspection; exact-head full suite and audits; read-only public spot, wallet, ETF and institutional-source research; nine-platform map refresh; this handoff update.

**VERIFIED:** exact code head `fc61430` passed the full repository suite and required CI/audit jobs listed above. The fail-closed merge gate blocked for draft status, no independent approval and inaccessible branch-protection configuration. Public-market observations in this section are research-only and not feature-store eligible.

**NOT VERIFIED / BLOCKING:** production scheduled XRP ingestion on main; independent WORM/timestamp anchoring; a populated synchronized historical feature set; full Level-2 executable depth history; stable out-of-sample learned-model superiority over all four baselines; calibrated probability performance across regimes; sufficient shadow samples; independent signed evaluator attestation; and live authentication/data flow for the eight other platforms.

**Forecast status: `NOT_ISSUED`.** No directional forecast, paper trade, real-money action, deployment, publication, secret rotation, Space restart, Kaggle submission, Databricks write or external model dispatch occurred.

Next concrete action: finish file-level workflow/security review and obtain independently verifiable review plus branch-protection evidence for #1673; keep it draft and do not merge or publish while those gates remain unresolved. In parallel, preserve the read-only XRP ingestion implementation and close the WORM/historical-data gaps without fabricating depth, flows or forecasts.

---

## Post-handoff collateral and exact-head verification update — 2026-11-20T09:46:34Z

This update adds new public collateral evidence and records a newer exact-head verification. All newly viewed market/dashboard data below is research-only: no raw response bytes or Barrot receipt were captured, so none of it is feature-store or model eligible.

### Exact integration-head verification — VERIFIED

Exact integration head `251682e1023afe3029c4fa7a87cecf09e59f8acf` (523 commits ahead / 0 behind main at verification time):

- [CI / full repository suite 44712782428](https://github.com/Barrot-Agent/B-Agent/actions/runs/44712782428): passed.
- **4,440 passed, 1 skipped, 11 warnings, 23 subtests passed**; 4,441 collected; 192.72 seconds.
- Inclusive coverage 73.08%; legacy/core 82%.
- Mission-critical coverage floors: AGI orchestrator 52%; XRP telemetry 92%; MMI 92%; Barrot integration 62%; feature store 80%; forecast ledger 97%; point-in-time features 89%; source registry 95%; monetization 78%; rendering 71%; SmartAgent 77%; memory palace 100%.
- [Money audit 44712782393](https://github.com/Barrot-Agent/B-Agent/actions/runs/44712782393): passed.
- [A2A Worker Tests 44712782375](https://github.com/Barrot-Agent/B-Agent/actions/runs/44712782375): passed.
- [Dependency Audit 44712782373](https://github.com/Barrot-Agent/B-Agent/actions/runs/44712782373) and [44712772476](https://github.com/Barrot-Agent/B-Agent/actions/runs/44712772476): passed.
- Pages build was validation-only and passed; no deployment.
- [Fail-closed gate 44712782385](https://github.com/Barrot-Agent/B-Agent/actions/runs/44712782385): **BLOCKED**, with exact reasons: PR is still draft; no independent approving review exists; branch protection could not be verified, so the workflow refused to infer approval or bypass settings.

After this verified head, map and handoff commits are documentation-only. No runtime code was changed. The next handoff commit will trigger a fresh CI run; results on `251682e` are not silently transferred to that later head.

### Coinbase / Morpho cbXRP collateral channel — current public interface snapshot

Source: [Morpho Base cbXRP/USDC market](https://app.morpho.org/base/variable/0xd4a903dc6d949519060c7707f9604fdc9772c046e05c2e3a8fce0bd7196e4109/usdc-cbxrp), retrieved approximately **2026-11-20 09:44 UTC**.

The public market interface showed:

- Outstanding USDC loans: **$48.83M**.
- Total liquidity: **$20.33M**.
- Utilization: **90.37%**, versus a 90% target; the interface showed $0 borrow amount to target utilization.
- Total market size: **$69.16M**.
- Liquidation LTV: **62.5%**; liquidation penalty: **12.67%**.
- Realized and unrealized bad debt: **$0**.
- Instantaneous rate: **8.02%**; displayed 6-hour borrow rate: **9.20%**; 24-hour average: **11.53%**; 7-day average: **7.93%**.
- The market was created January 15, 2026. The interface displayed a Chainlink XRP/USD oracle with 1-day heartbeat / 0.5% deviation metadata. Its rounded market oracle field showed 0.962 USDC per cbXRP while the linked Chainlink feed row showed 0.966873; retain the field/timestamp distinction rather than forcing them into one price.
- The latest visible liquidation rows were dated November 17: 250.003 USDC repaid for 295.161 cbXRP seized, and 224.777 USDC repaid for 263.999 cbXRP seized; both showed zero bad debt. Basescan transaction links returned 403 through this research path, so the transaction pages were not independently decoded here.

[CryptoSlate's November 7 analysis](https://cryptoslate.com/morpho-loan-stress-exposes-cbxrp-but-spares-native-xrp/) used Morpho's public GraphQL API and reported that, at a November 6 13:24 UTC snapshot, **$8.8448M** of USDC debt across 1,070 positions was within a further 10% oracle decline of liquidation eligibility; **$3.2296M** across 462 positions was within a further 5% decline (a subset of the 10% bucket). The same snapshot showed about $59.24M debt against 119.87M cbXRP collateral. The article's method paginated three API result pages. This is secondary analysis of Morpho data, not independent corroboration.

[CryptoSlate's November 13 follow-up](https://cryptoslate.com/xrp-loans-trigger-883-liquidations-and-53m-remains-at-risk/) reported 883 Morpho liquidation log events from November 7–13, just over $4M USDC debt repaid, 4.18M cbXRP seized and about $53.5M debt remaining at its November 13 snapshot. One borrower can generate multiple event logs. The current Morpho interface later showed $48.83M outstanding, but that difference cannot be attributed solely to liquidations: subsequent repayments, new borrowing, collateral additions and snapshot timing are not reconciled.

[Coinbase's terms as reported by The Block](https://www.theblock.co/news/business/2026-02-18-coinbase-xrp-dogecoin-cardano-litecoin-loans-morpho-390403): eligible U.S. users (excluding New York) can borrow up to $100,000 USDC against XRP, DOGE, ADA or LTC, with a maximum 49% LTV and liquidation at 62.5%; rates float with Morpho supply/demand, and loan proceeds cannot be used to trade on Coinbase. Morpho is permissionless. Matching parameters and Coinbase's interface do not prove every position in the market belongs to a Coinbase customer.

**Interpretation:** cbXRP collateralized borrowing can lock existing XRP and create a two-sided channel: debt capacity while maintaining exposure, but potential collateral seizure and later sale if positions breach risk thresholds. Seized cbXRP is not itself proof of a native XRP sale. A native-sale claim requires a traceable cbXRP redemption/custody path and subsequent XRPL or exchange trade. No such chain was verified in this run. High utilization is a lending-market liquidity measure, not XRP spot order-book depth.

### Maple institutional XRP collateral — current product disclosures and vintage reconciliation

Primary product pages:
- [Maple syrupUSDC transparency](https://maple.finance/transparency/products/syrupusdc)
- [Maple syrupUSDT transparency](https://maple.finance/transparency/products/syrupusdt)
- [Maple / The Network Firm collateral dashboard](https://dashboard.ledgerlens.io/c/maple)
- [DefiLlama Maple adapter methodology](https://raw.githubusercontent.com/DefiLlama/DefiLlama-Adapters/main/projects/maple/index.js)

The Maple product pages displayed a collateral verification vintage of **November 17, 2026 at 01:00 UTC**:

**syrupUSDC**
- XRP collateral: **160,766,086.03 XRP**, displayed value approximately **$153.84M**.
- Two XRP-backed loan rows: 55.00M USDC principal against $89.63M collateral (163.0%); 41.61M USDC against $64.21M collateral (154.3%).
- Both rows displayed a May 8, 2027 maturity.
- The pool page showed 21 loans overall and four collateral assets; the XRP figures refer only to its XRP collateral, not total pool collateral.

**syrupUSDT**
- XRP collateral: **92,814,668.8 XRP**, displayed value approximately **$88.81M**.
- One XRP-backed loan row: 55.19M USDT principal against $88.81M collateral (160.9%), with January 15, 2027 maturity.
- The pool page showed four loans overall and three collateral assets.

Combined product-page figure: approximately **253.58M XRP**, displayed value approximately **$242.65M**, backing three XRP-collateralized positions with approximately **$151.8M nominal USDC/USDT principal**. These are public dashboard values at the stated verification vintage, not a claim that the full amount was newly purchased.

Vintage comparison: CryptoSlate's October 31 article reported 142.766M XRP in syrupUSDC and 82.315M XRP in syrupUSDT (about 225.08M XRP, displayed at $280.2M). The November 17 Maple product pages now display 160.766M and 92.815M XRP. The apparent quantity difference is about **+28.5M XRP** while the dollar value is lower. The USDC maturities shown in the current product pages (May 8, 2027) differ from the December 4 / December 12 maturities reported on October 31. A renewal, extension, additional collateral or a disclosure-universe change is possible; no loan-ID crosswalk was established, so this is **not yet a verified time-series increase or confirmed rollover**. The USDT maturity remains January 15, 2027.

Critical assurance caveat: The dashboard labels amounts “verified,” but its own disclaimer says The Network Firm Tech & Services, LLC provides a **non-attest technology service**, not an audit, review, examination or assurance engagement; it relies on Maple and third-party data and has not independently confirmed accuracy/completeness. It is point-in-time only (Nov 17 01:00 UTC). Do not describe these figures as independently audited.

The DefiLlama adapter explicitly maps Maple collateral by the chain where held (including XRP on XRPL), while loan cash/pools originate on Ethereum. It declares `timetravel: false` because Maple publishes custody addresses only for current loans. This means current collateral metadata must **not** be backfilled into historical dates or used to reconstruct past collateral balances.

**Interpretation:** Maple demonstrates a sizeable institutional stablecoin-credit use of XRP collateral, but not necessarily new XRP purchases. Existing holders may pledge XRP already owned. Repayment, renewal, authorized collateral release, margin calls or liquidation can change the amount encumbered. The three loan positions do not establish three distinct beneficial borrowers. Track token quantity, collateral value, loan principal, maturity, custody chain, pool and release status separately.

### PR overlap content check — correction

Changed-path overlap does not establish byte-identical duplicate content. A blob comparison of the changed paths found zero byte-identical changed files between the integration tree and these source PR heads: #1677 (0/6), #1671 (0/8), #1670 (0/12), #1668 (0/3) and #1541 (0/5). The paths overlap, but the blobs differ; semantic reconciliation remains necessary. #1664 has six changed-path overlaps with #1673 and 126 of its other changed paths are absent from the integration tree; preserve its distinct product work. #1265 has one changed-path overlap and substantial unique research. Do not label these PRs exact duplicates or close them based only on path overlap.

### Disposition

All Morpho and Maple page observations remain **research-only / not feature-store eligible** because raw payload bytes, retrieval receipts and synchronized historical series were not captured in Barrot. Add these sources to the next ingestion validation pass with strict source-vintage and custody semantics. No directional forecast is issued. No deployment, market action, paper trade, real-money action, PR merge or source-PR closure occurred.


---

## Run 11 — 2026-11-20 09:59 UTC research and integration checkpoint

### Executive state

- Mission priority remains **XRP intelligence and measured prediction-engine performance**.
- Barrot V3 remains the protected execution, orchestration, safety and verification foundation.
- **No new branch or PR was created. No merge, source-PR closure, deployment, secret change, external model dispatch, paper trade or real-money action was performed in this run.**
- Main is `7f8e3626c355bb3d89afdff56aeed5e056cb88f4`.
- Consolidated integration PR #1673 is based on that exact main SHA and is at code head `109625985268c1aef6f5d8731f7574cb75f2047a`.
- Main tree: 1,751 entries. Integration tree: 3,040 entries. Recursive tree comparison: **zero main paths missing from integration**.
- PR #1673: 525 commits ahead, zero behind, 1,494 changed files, draft, mergeable flag true, mergeable state unstable.
- Existing handoff blob before this append: `760a0557c4cde2f4c5b95b776a9e5a1f573c5ecc`.

### Mainline changes since the previous checkpoint

Verified merged PRs:

| PR | Merge commit | Subject |
|---|---|---|
| #1672 | `73e4dfa1ce4f21a8d419ef7e2e90d402b28d577f` | GPT Actions connected to existing OpenCode execution |
| #1674 | `33d02d3b3251350aaede9df04fcb701f2398d016` | MMI-backed capability curriculum |
| #1675 | `7e343f78b9d9e98328105988585ef4da9e0bd77f` | Evidence-gated autonomous conflict resolution |
| #1676 | `08ecb81e9e7501a7ff4a241c2dae6eef766ff2d3` | Governed V3 OpenCode documentation |

Main CI passed after the merges at:
- #1674 / #1672 ancestry: [44669957726](https://github.com/Barrot-Agent/B-Agent/actions/runs/44669957726)
- #1675: [44680354718](https://github.com/Barrot-Agent/B-Agent/actions/runs/44680354718)
- #1676: [44680928702](https://github.com/Barrot-Agent/B-Agent/actions/runs/44680928702)

The current main head `7f8e362` is a subsequent paid-issue-hunter data commit, not one of those merge commits. Its scheduled Cross Analysis passed at [44714284942](https://github.com/Barrot-Agent/B-Agent/actions/runs/44714284942), but a full CI run on the exact `7f8e362` head was not found.

### Exact-head integration verification

On code head `109625985268c1aef6f5d8731f7574cb75f2047a`:

- [CI / full repository suite 44713877185](https://github.com/Barrot-Agent/B-Agent/actions/runs/44713877185): **4,440 passed, 1 skipped, 11 warnings, 23 subtests**, 159.78 seconds, inclusive coverage **73.08%**.
- Key coverage: XRP telemetry 92%; MMI 92%; feature store 80%; forecast ledger 97%; point-in-time features 89%; source registry 95%; Barrot integration 62%; AGI orchestrator 52%.
- [Dependency audit 44713877453](https://github.com/Barrot-Agent/B-Agent/actions/runs/44713877453): passed.
- [Money audit 44713877046](https://github.com/Barrot-Agent/B-Agent/actions/runs/44713877046): passed.
- [A2A Worker tests 44713877181](https://github.com/Barrot-Agent/B-Agent/actions/runs/44713877181): passed.
- The cache budget warning is non-blocking; cache is read-only and the test suite passed.

The fail-closed gate [44713877166](https://github.com/Barrot-Agent/B-Agent/actions/runs/44713877166) failed as designed:
1. PR #1673 remains draft.
2. No review records exist on #1673.
3. The GitHub integration receives HTTP 403 when reading main branch-protection details. Main is marked protected, but the actual required checks, strict-up-to-date setting, review count and administrator enforcement cannot be verified.

No merge was attempted. PR #1673 changes public web assets; merging it would trigger the existing GitHub Pages deployment workflow. The user's no-deployment-without-specific-approval rule remains a separate blocker even if CI and branch protection are later resolved.

### Security PR #1677 — gate result is not merge authorization

PR #1677 is non-draft and changes six A2A/OpenCode files. Its head is `0d4b3484c95a46ff9f61417f94c97a391d0fefff`, based on `7e343f78`, which is **two commits behind current main** (`08ecb81` and `7f8e362)). Its branch is unprotected and it has no review records.

Its Tests, Full Repository Test Suite and audit checks passed on its own older head. Its check named “Merge disabled pending gate verification” is a no-op: the job log explicitly says automatic merge is intentionally disabled and then exits successfully. It does not verify branch protection, approvals or readiness. Do not treat that success as a merge gate.

The six paths overlap with #1673 but are not byte-identical. The integration branch already contains related manual-only deployment controls, explicit opt-in and tests, but semantic reconciliation is still required. Preserve #1677 until the security changes are reviewed against the current integration head; do not close it as a duplicate.

### Automatic mainline side effect discovered

The current main commit `7f8e362` was created by the existing scheduled Paid Issue Hunter workflow at 06:31 UTC. The follow-on publisher workflow wrote `PAID-ISSUES.md` and `data/money/paid_issues.json` directly to main. The Pages workflow then successfully deployed main commit `7f8e362` to [https://barrot-agent.github.io/B-Agent/](https://barrot-agent.github.io/B-Agent/).

This was an automatic repository workflow side effect, not an action taken by this run. No issue was claimed and no funds moved. However, the published candidate is a data-quality failure:
- The single row is marked `READY` with `amount_usd: 3`.
- Its quote contains “$3.43M”.
- `scripts/paid_issue_hunter.py` uses a numeric regex that truncates suffix amounts such as `M` and `K`; the resulting small number is still marked READY.
- The renderer documents a $50 minimum, but the current path does not enforce that minimum before assigning READY.

The scheduled hunter is read-only, but `paid-issue-publish.yml` has `contents: write` and pushes the artifact to main on `workflow_run`. The subsequent Pages deployment is real and verified. This is an existing external-write/publication path and must be included in the V3 safety review. No change or rollback was made because that would modify a separate mainline workflow outside this XRP integration.

### Current XRP market snapshot — research-only, not model-ingested

Retrieval window: approximately 09:59 UTC, November 20, 2026.

**Spot**
- Kraken XRP/USD: last $0.95628; bid $0.95603; ask $0.95604; 24-hour volume 39.97M XRP; 24-hour high $0.99680; low $0.94679. The displayed spread is approximately 0.105 bps.
- OKX XRP/USDT: quote timestamp 2026-11-20 09:59:01.764 UTC; last 0.9564; bid 0.9561; ask 0.9562; 24-hour open 0.9864; high 0.9979; low 0.9478; volume 47.14M XRP; turnover 45.57M USDT; 24-hour change approximately -3.04%. The displayed spread is approximately 1.046 bps.
- Do not directly normalize XRP/USD and XRP/USDT without a synchronized USDT/USD quote. Kraken's top-of-book and OKX's top-of-book are not a cross-venue depth curve. A synchronized Level-2 snapshot was not captured in this run; the integration code has configured depth adapters.

Sources: [Kraken public ticker](https://api.kraken.com/0/public/Ticker?pair=XRPUSD), [OKX public ticker](https://www.okx.com/api/v5/market/ticker?instId=XRP-USDT).

**Derivatives — vendor aggregate, not primary exchange receipts**
- Liqwall snapshot at 09:42 UTC: XRP $0.9602; $920M open interest, -0.1% over 24 hours; $5.2M liquidations, of which $4.5M were longs and $708K shorts; average funding -0.0046% per eight hours; Binance funding 0.0000%; 74.7% of Binance accounts with XRP positions were long.
- This is evidence of a recent long-liquidation imbalance, not a directional forecast. OI was nearly flat and the funding picture differed by venue.

Source: [Liqwall XRP dashboard](https://liqwall.com/coins/xrp), snapshot 2026-11-20 09:42 UTC.

**Exchange-wallet balances**
- XRP Insights snapshot 2026-11-20 08:00 UTC: 22.18B XRP in 707 XRPL wallets attributed to 24 exchanges, 32.2% of its 68.89B circulating-supply denominator.
- Same-wallet change: -86.0M XRP over seven days and -434.3M over 30 days.
- Largest attributed balances: Upbit 6.46B; Coinbase 5.82B; Binance 2.60B; Bithumb 1.77B.
- 484.7M XRP in the tracked set is identified as non-customer reserve/insurance/wrapped-token backing, including 153.7M attributed to Coinbase cbXRP and 327.4M Binance-Peg XRP. About 48.5% of the tracked total is labeled cold and 39.7% is unclassified.
- These are attributed-wallet balances, not exchange order-book reserves or tradable float. The source explicitly warns that untracked wallet transfers can appear as outflows.

Source and methodology: [XRP Insights exchange balances](https://xrp-insights.com/exchange-balances).

**Coinbase cbXRP and collateral**
- Coinbase's own proof-of-reserves page reported, on its 2026-11-20 02:05 AM refresh, 156,138,671.16 XRP reserve against 156,136,424.62 cbXRP supply on Base. This is direct issuer reserve evidence, not an exchange-flow estimate.
- Coinbase Help confirms that eligible users can borrow USDC against XRP through the Morpho onchain lending protocol on Base; Coinbase supplies the user interface and Morpho supplies the lending protocol. This creates a collateral/credit channel, not proof of incremental spot buying.
- XRP Insights' wallet-label estimate of 153.7M cbXRP reserve differs from Coinbase's direct 156.14M proof-of-reserves figure; retain both vintages and do not substitute the attributed-wallet number for issuer proof of reserves.

Sources: [Coinbase cbXRP proof of reserves](https://www.coinbase.com/cbxrp/proof-of-reserves), [Coinbase crypto-backed loans](https://help.coinbase.com/en/coinbase/trading-and-funding/loan/loan-intro).

**Spot ETF flows — universe reconciliation**
- XRP Insights reports week 47 (November 16–19, four trading days) at -4.96M XRP, approximately -$4.91M; the November 19 row is provisional. Its previous week (November 9–13) is -6.08M XRP, approximately -$6.64M.
- XRP Insights explicitly excludes GXRP from computed flow totals while a holdings capture gap is corrected, although GXRP holdings remain in total holdings.
- A SoSoValue-derived report carried by KuCoin reports -$19.13M for November 9–13 and includes a large GXRP redemption. The apparent discrepancy is therefore at least partly a fund-universe/capture-gap difference; it is not evidence that one series can be silently substituted for the other.
- Preserve per-fund issuer holdings, flow status, provisional/reconstructed status and excluded-fund flags. Holdings changes are not automatically cash subscriptions or redemptions.

Sources: [XRP Insights ETF tracker and daily methodology](https://xrp-insights.com/), [XRP ETF data dictionary](https://xrp-insights.com/data), [KuCoin's SoSoValue-derived weekly report](https://www.kucoin.com/blog/in-xrp-etf-outflows-8-month-high-2026).

**RLUSD and stablecoin rails**
- Ripple's transparency page reported $2.6899B circulating RLUSD and $2.8265B reserve funds as of November 12, 2026.
- XRP Insights' on-chain dashboard on November 20 reported approximately $2.81B across XRPL and Ethereum: $745.8M on XRPL (27%) and $2.06B on Ethereum (73%), excluding smaller L2/sidechain balances. The two totals have different dates and measurement definitions; retain both rather than forcing a false match.
- Most tracked RLUSD supply is on Ethereum, not XRPL. RLUSD growth is not equivalent to XRP demand or bridge-asset usage.

Sources: [Ripple RLUSD transparency](https://ripple.com/products/stablecoin/transparency/), [XRP Insights on-chain supply dashboard](https://xrp-insights.com/xrp-radar).

### Coinbase, Circle, Ripple and SBI — updated relationship graph

**Coinbase ↔ Circle**
- Coinbase's Q3 2026 Form 10-Q says average USDC held in Coinbase products reached an all-time high and that its arrangement with Circle was renewed on the same terms.
- Coinbase attributes +$84.6M in Q3 and +$201.6M over the first nine months of 2026 to higher average USDC balances, partly offset by lower interest rates (-$52.8M Q3; -$166.2M nine months).
- Coinbase's filing also records fair-value remeasurement of its investment in Circle after Circle's IPO. The filing establishes equity exposure but does not state a current ownership percentage in the cited passage.
- Circle's Q3 2026 10-Q reports distribution costs under its Coinbase agreements of $331.3M for Q3 and $986.6M for the first nine months of 2026. The filing explains that Coinbase allocations depend on USDC held on its platform after issuer retention and include half of the remaining broader-ecosystem amount after approved third-party participants.
- This is a direct equity and distribution relationship with meaningful mutual economic exposure, not merely a listing relationship.

Primary sources: [Coinbase Q3 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1679788/000167978826000122/coin-20260930.htm), [Circle Q3 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1876042/000187604226000311/crcl-20260930.htm).

**Circle ↔ SBI Holdings**
- Circle's Q3 2026 10-Q states that Circle and SBI each contributed yen equivalent to approximately $1.5M to Circle SBI Japan K.K. in November 2025.
- Circle owns 50%, consolidates the VIE because it controls the activities that most affect it, and reports no significant operating results to date as of September 30, 2026.
- SBI's March 25, 2025 announcement described the joint venture as 50:50. SBI VC Trade is a separate distribution channel and has offered USDC in Japan; do not equate the JV's reported operating results with the entire SBI VC Trade business.

Sources: [SBI Holdings JV announcement](https://www.sbigroup.co.jp/english/news/pdf/2025/0325_c_en.pdf), [Circle Q3 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1876042/000187604226000311/crcl-20260930.htm).

**Ripple ↔ SBI Holdings / SBI operating companies**
- Ripple announced official RLUSD availability in Japan with SBI Group and SBI VC Trade on June 24, 2026. This is a stablecoin distribution relationship, not proof of XRP purchases.
- Ripple's official SBI Ripple Asia page makes two distinct statements: SBI Ripple Asia sells RippleNet software and itself does not handle XRP; separately, Ripple's XRP-bridged On-Demand Liquidity service is already commercialized in Japan through SBI Remit, Coins.ph and SBI VC Trade. The company-level limitation must not be generalized to the entire SBI Group or its ODL partners.
- Thus the relationship includes both software/payment infrastructure that need not use XRP and a specific XRP-bridge ODL route. These must be separate features and event types.

Sources: [Ripple/SBI RLUSD launch, June 24, 2026](https://ripple.com/ripple-press/ripple-and-sbi-group-partner-to-launch-ripple-usd-in-japan/), [SBI Ripple Asia official description](https://ripple.com/company/sbi-ripple-asia/).

**Coinbase ↔ Ripple / XRP**
- No direct Coinbase-Ripple corporate joint venture or equity relationship was established in this run.
- The verified connections are product and market infrastructure: Coinbase lists XRP, holds XRP reserves backing cbXRP 1:1, and offers XRP-backed USDC borrowing through Morpho on Base. This can increase XRP's collateral utility while also creating liquidation/credit channels; it does not prove net spot accumulation.
- Circle USDC is also available on XRPL, but USDC settlement on XRPL does not inherently require XRP as a bridge asset.

**Circle ↔ Ripple**
- Both issue dollar stablecoins and compete/overlap in institutional settlement and multi-chain distribution. No direct corporate partnership between Circle and Ripple was established in this run.
- Circle's USDC and Ripple's RLUSD are distinct liabilities with different issuers, reserve structures, distribution contracts and chain footprints.

### SBIC, SoftBank and ChatGPT — identity correction

- Japan's SBIC regional companies remain separate from SBI Holdings and from SoftBank Group.
- Tokyo SBIC's official materials show a February 26, 2025 seminar titled “The Present and Future of Generative AI (ChatGPT)” and a June 12–13, 2025 AI/ML course that included ChatGPT use. These are educational events, not evidence of an OpenAI partnership.
- Separately, SoftBank Group/SoftBank Corp and OpenAI launched **SB OAI Japan GK** on November 5, 2025. It is a 50:50 joint venture between OpenAI and C Holdings Corporation; C Holdings is owned 51% by SoftBank Corp and 49% by SoftBank Group. This is a genuine OpenAI-SoftBank JV, but it is not SBIC East, Central or West and is not SBI Holdings' Circle JV.
- Exact phrase `SBIC, ChatGPT SBIC` remains unresolved. The SBIC training events and SB OAI Japan JV are plausible adjacent entities that must not be conflated.

Sources: [Tokyo SBIC ChatGPT seminar PDF](https://www.sbic.co.jp/wordpress/file/20250226_%E7%94%9F%E6%88%90AI%E3%81%AE%E7%8F%BE%E5%9C%A8%E3%81%A8%E6%9C%AA%E6%9D%A5%E3%80%90%E6%8A%95%E8%82%B2%E8%AA%AC%E6%98%8E%E3%81%82%E3%82%8A%E3%80%91.pdf), [SBIC Tokyo AI/ML course](https://www.sbic.co.jp/training/20250612co/), [SoftBank/OpenAI SB OAI Japan announcement](https://www.softbank.jp/en/corp/news/press/sbkk/2025/20251105_02/).

### Exact phrases and Kamilah/Camilla video identity

- `ASK Coin`: no primary source establishing an XRP-linked entity or token was found in this run.
- `actual capital`: no primary-source context was found that defines the user's exact phrase. Market capitalization, ETF holdings deltas, wallet attribution, collateral pledges and stablecoin supply must not be relabeled as actual cash capital.
- `SBIC, ChatGPT SBIC`: no exact match found; the separate SBIC education and SB OAI Japan JV findings above are retained as disambiguation candidates.
- YouTube search identifies channel `Kamilah Stevenson | XRP & Stocks`, channel ID `UCXm6KAr1WHF6UN7g5b2W7wg`, and attributes “I Moved My XRP Off The Exchanges” (May 20, 2026) to Kamilah Stevenson. A separate indexed video “Ripple Just Became a BANK” (December 14, 2025) is also attributed to Kamilah/Camila Stevenson.
- The channel's real-world identity has not been independently cross-linked to the Dr. Kamilah Stevenson interview/profile candidate. Do not admit either video to a verified creator inventory until that cross-link is established.

Candidates only: [Kamilah Stevenson channel](https://www.youtube.com/channel/UCXm6KAr1WHF6UN7g5b2W7wg), [I Moved My XRP Off The Exchanges](https://www.youtube.com/watch?v=TfFx0g2IgGg), [Ripple Just Became a BANK](https://www.youtube.com/watch?v=QslbjGQD0MU).

### Integrated prediction-engine status

**EXECUTED / VERIFIED on the integration branch**
- Seven-venue spot ticker ingestion and configured multi-venue Level-2 depth adapters.
- Binance/Bybit derivatives, Deribit XRP-USDC perpetual ticker/book, funding/open-interest/long-short data.
- ETF issuer pages and XRP Insights daily flows, attributed XRPL exchange wallets, Ripple RLUSD transparency, Circle USDC transparency, SBI lending page, Morpho cbXRP market/state/liquidity/oracle, Coinbase cbXRP proof of reserves and CFTC reports.
- SEC EDGAR adapter for Evernorth, Coinbase and Circle.
- SHA-256 raw receipts, append-only point-in-time feature store, source-independence groups, event timeline, four deterministic baselines, leakage-safe chronological walk-forward evaluation, temporal calibration, drift diagnostics, scenario/counter-hypothesis records and fail-closed forecast ledger.

**DESIGNED / NOT YET VERIFIED**
- Independent WORM/timestamp anchoring.
- Production scheduled captures on main: the workflow's hourly and daily schedules are main-only. Integration-branch push captures are scoped to ingestion/timestamp-audit code changes.
- Full historical synchronization and quality reconciliation across spot, depth, derivatives, ETF, exchange-wallet and collateral series.
- A learned candidate that beats all four baselines out of sample, stable calibration, drift validation and sufficient shadow observations.

The ingestion workflow is read-only (`actions: read`, `contents: read`) and artifacts have 90-day retention. Receipt-chain continuity checks predecessor artifacts, but GitHub Actions artifacts are not independent WORM storage. The SEC issuer registry currently contains Evernorth, Coinbase and Circle; SBI Holdings is not yet in that SEC registry and Ripple is not an SEC-reporting issuer in the configured set. Add SBI primary investor-relations and Ripple corporate-disclosure feeds with explicit availability times and conservative source lineage.

**Forecast status: NOT_ISSUED.** No directional forecast is supported by the current verified out-of-sample record. The current spot, exchange-wallet, ETF, derivatives and stablecoin observations in this addendum are research-only and were not captured as immutable Barrot raw receipts or promoted into the feature store.

### Nine-platform coordination

GitHub is the only platform whose authentication and repository access were exercised in this run. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks remain **not verified as live connections**. No credentials were requested, no external model was dispatched and no data was sent to those providers. Preserve least privilege and record actual permission/data-flow tests before changing any platform's status.

### Current open-PR inventory — 17 preserved

| PR | Classification | Current disposition |
|---|---|---|
| #1673 | blocked | Active consolidated integration; draft, no reviews, branch-protection 403, Pages deployment approval outstanding |
| #1677 | blocked / security overlap | Six-file A2A quarantine candidate; stale base by two commits; its gate is a no-op success; semantic reconciliation with #1673 required |
| #1671 | blocked / security overlap | Inbound GPT Actions authority gate; draft, stale base; review against current V3 integration |
| #1670 | unique/unreviewed | Musical DNA recursive-learning feature; separate creative workstream |
| #1668 | blocked | Provider failover; draft and requires workflow/secret review |
| #1666 | blocked | Dependabot Kaggle dependency update; stale base and current-head validation required |
| #1665 | blocked | Dependabot Pylint update; stale base and current-head validation required |
| #1664 | blocked / unique | Paid-issue PR-template product staging; distinct content, not published by this PR |
| #1663 | superseded candidate | Older V3/XRP integration successor; reconcile losslessly before any closure |
| #1541 | unique/unreviewed / security | MMI canonical-claim fingerprint work; path overlap is not proof of duplicate content |
| #1460 | unique/unreviewed | XRP institutional multirail, Binance and Kamilah research |
| #1450 | unique/unreviewed | Binance phase-one, escrow and PR #1449 audit |
| #1440 | unique/unreviewed | XRP archive validation trigger repair |
| #1437 | unique/unreviewed | XRP ledger source-addenda repair |
| #1436 | unique/unreviewed | Binance XRP theft and attacker-wallet graph |
| #1353 | unique/unreviewed | XRP ledger sharding research |
| #1265 | unique/unreviewed | XRP ledger index/snapshot-pointer research |

No unique research or creative PR was bulk-closed. #1663 is not to be closed until #1673 is merged and its content is verified on main. #1677 is not to be closed as an exact duplicate merely because paths overlap.

### Next concrete actions

1. Keep #1673 as the single active integration PR. Do not create another XRP integration PR.
2. Resolve draft/review/branch-protection verification and obtain explicit authorization for the Pages deployment that a merge would trigger.
3. Reconcile #1677 and #1671 security changes into the existing integration branch only after semantic review; do not treat their older checks or no-op gates as merge evidence.
4. Audit the automatic paid-issue publisher and correct the suffix/minimum-amount validation before trusting any READY candidate. Do not publish or deploy a new revision without authorization.
5. Add primary SBI Holdings/SBI VC Trade disclosures and Ripple corporate releases to scheduled evidence ingestion; keep the SBIC regional publisher group separate from SBI Group.
6. Capture synchronized multi-venue L2 depth and USDT/USD quotes, reconcile ETF issuer-level holdings (including GXRP gaps), and capture Coinbase/Morpho/cbXRP and RLUSD chain supply as raw receipts.
7. Establish independent immutable retention, complete historical point-in-time datasets, then run chronological baseline and learned-model comparisons. Keep forecast status NOT_ISSUED until the full evaluation standard is met.
8. Refresh the nine-platform capability/authentication/permission/data-flow map only with tested evidence.

This checkpoint is a research and documentation update on the existing integration branch. Main remains at `7f8e3626c355bb3d89afdff56aeed5e056cb88f4`; no merge or mainline code change was made by this run.


---

## Current-state addendum — 2026-11-20 11:51 UTC

This addendum supersedes earlier repository-state, exact-head CI, branch-overlap and current-market observations above. It is append-only; no prior research or branch history was rewritten.

### 1. Repository and integration state — VERIFIED

- Default branch main: 7f8e3626c355bb3d89afdff56aeed5e056cb88f4.
- Main tree: 1,751 entries / 1,578 blobs; recursive tree response was not truncated.
- Active integration PR: https://github.com/Barrot-Agent/B-Agent/pull/1673, branch integration/xrp-v3-mainline-successor-20261120T0135Z.
- Exact integration head: f690bc7aaf5a7d4a36471e378874fb2a607c35fa.
- PR #1673 is 526 commits ahead / 0 behind current main; 1,494 changed files, 535,403 additions and 7,024 deletions.
- Integration tree: 3,040 entries / 2,853 blobs; no truncation.
- PR scope: 69 workflow files, 426 test paths, 74 barrot_agent paths and 1,133 XRP/forecast/feature-store-related paths.
- Open PR inventory: 17. No new branch or PR was created.

Main's current head advanced through an automated paid-issue scan. The commit changed only PAID-ISSUES.md and data/money/paid_issues.json; it did not modify runtime or XRP code. The latest main-branch Cross Analysis run 44730978197 succeeded, but it is a read-only entity/news sentiment analysis, not the XRP spot/depth/derivatives ingestion pipeline.

### 2. Exact-head verification — VERIFIED

All results below are tied to integration head f690bc7, not an earlier branch head:

- Full repository suite 44718257764: **4,440 passed, 1 skipped, 0 failed**, 11 warnings, 23 subtests; 161.85 seconds.
- Inclusive coverage: **73.08%**; legacy/core coverage: **82%**.
- Mission package coverage: XRP telemetry 92%; MMI 92%; feature store 80%; forecast ledger 97%; point-in-time features 89%; source registry 95%; Barrot integration 62%; AGI orchestrator 52%.
- Additional package coverage: monetization 78%; rendering 71%; smart agent 77%; memory palace 100%.
- Dependency audit 44718257853: passed six manifests.
- Money audit 44718257785: passed.
- A2A Worker tests 44718258144: passed.
- Pages build: validation-only passed; no deployment.

The direct-main push guard is now present in scripts/push_with_token.sh. It refuses a default direct push to main unless a deliberate override is supplied. The branch adds tests/test_push_with_token_security.py; it passed within the exact-head full suite. This corrects the older handoff statement that the guard was still missing. No direct push to main occurred.

### 3. Merge gate — BLOCKED, fail-closed

The exact-head fail-closed gate 44718257941 failed for the following independently observed conditions:

1. PR #1673 remains draft.
2. No independent approving review exists.
3. The main branch-protection endpoint returns HTTP 403. The branch metadata says protected, but effective required checks and administrator enforcement cannot be independently read.
4. The only returned repository ruleset, Fall Back, has enforcement disabled.
5. A merge would trigger GitHub Pages publication. Pages validation is not deployment authorization.
6. A2A sandboxing, credential isolation, egress restrictions and task-level authorization remain incomplete; the 69-workflow/transitive script review is not complete.

No merge, deployment, publication, force-push, branch-protection bypass or source-PR closure occurred. The prior merge authorization applies only when every stated readiness and safety condition is actually satisfied.

### 4. Branch ancestry and overlap audit — EXECUTED

Current ancestry against main:

| PR | Ahead / behind main | Current disposition |
|---|---:|---|
| #1673 | 526 / 0 | Active consolidated integration; blocked |
| #1677 | 6 / 2 | Security overlap; blocked pending semantic review |
| #1671 | 9 / 10 | Partially superseded; workflow differences remain |
| #1670 | 47 / 13 | Mostly integrated; three changed paths remain |
| #1668 | 5 / 14 | Unique provider-failover work; not integrated |
| #1666 | 1 / 17 | Dependency change; stale and unverified on current main |
| #1665 | 1 / 17 | Dependency change; stale and unverified on current main |
| #1664 | 17 / 0 | Separate paid-issue product; draft and unpublished |
| #1663 | 486 / 9 | Superseded predecessor candidate; preserve until successor verification |
| #1541, #1460, #1450, #1440, #1437, #1436, #1353, #1265 | No common ancestor with current main | Preserve as unique/stacked research or repair work; no bulk action |

Path-level and blob-level comparison against #1673:

- #1677: all 6 changed paths overlap; 0 identical blobs. The successor and source branch both retain manual-only deployment, explicit runner opt-in and ask-before-action controls, but their files differ. The successor documentation still records sandbox/egress/task-authorization gaps. Treat as security reconciliation, not a proven byte-identical duplicate.
- #1671: all 8 changed paths overlap; 4 identical blobs and 4 different. The gate module and some API tests match; workflow and regression-test versions differ. Do not import the source workflows wholesale.
- #1670: all 12 paths overlap; 9 identical blobs and 3 different (docs/INDEX.md, pyproject.toml, tests/test_musical_adapters.py). The core Musical DNA package is present; reconcile the remaining three files before classifying the source PR as fully superseded.
- #1668: all 3 paths overlap but 0 blobs are identical. Provider failover is not verified as integrated.
- #1664: 6 paths overlap; 1 blob is identical and 5 differ. The remaining product work is separate and unpublished.
- #1666: its pyproject.toml overlap differs.
- #1665: its requirements-dev.txt overlap differs.
- #1541: 5 paths overlap; 2 blobs are identical and 3 differ, including the canonical-claim record and MMI implementation/test files. Do not call it a complete duplicate.
- #1265: 1 path overlaps and differs; 143 of its changed paths are outside the successor's changed-path set.

No source PR was closed. #1673 remains the single active XRP/V3 integration workstream. The older branches with no common ancestor remain preserved; they are not safe candidates for direct merge without a lossless, current-main successor and explicit source disposition.

### 5. Current XRP market snapshot — RESEARCH ONLY, NOT MODEL-ELIGIBLE

Kraken XRP/USD public ticker, retrieved approximately 2026-11-20 11:51 UTC:

- Last trade: $0.95329.
- Best bid: $0.95359; best ask: $0.95368.
- Indicative top-of-book spread: approximately 0.944 basis points.
- Displayed best bid/ask size: approximately 332 XRP per side.
- 24-hour volume: approximately 39.17 million XRP.
- 24-hour range: $0.94679–$0.99680.
- 24-hour VWAP: approximately $0.970307.

Quality flags: Kraken supplied no exchange event timestamp in the rendered response; last trade was below the displayed best bid at capture. Only one venue was successfully retrieved. A narrow top-of-book spread and 332 XRP at each best quote do not establish executable depth. The Level-2 depth endpoints did not return usable payloads in this research capture. No depth, cross-venue basis or slippage feature was admitted.

ETF-flow tracker, data through 2026-11-19: it displayed zero XRP-product net flow for November 19, approximately -$19 million over 30 days, approximately -$25.7 million month-to-date, $1.08 billion AUM and $1.79 billion cumulative net inflows. The provider marks November 16–19 rows provisional. Its November 17 table row shows -$6.0 million while its summary identifies a -$4.9 million XRPC move; the month-to-date summary also differs from the rounded daily-row sum. Preserve this provider-internal disagreement. These are secondary aggregated figures, not issuer-level cash receipts.

The same tracker reported broad U.S. crypto ETF outflows of approximately $718.7 million on November 19 and a CEFI fear reading of 9. Treat these as secondary broad-market context, not XRP-specific flows or a directional signal.

Sources: https://api.kraken.com/0/public/Ticker?pair=XRPUSD and https://cryptofundflows.com/xrp-etf/.

All observations in this section are research-only. Browser-rendered responses were not captured as exact raw HTTP bytes; no SHA-256 receipt or independent timestamp anchor exists. They are excluded from the point-in-time feature store and all model evaluation.

### 6. Institutional network, exact phrases and identity — NO NEW VERIFIED EDGE

The latest durable research artifacts already contain the current primary-source reconciliation for Coinbase/Circle Q3 distribution economics, Ripple/Coinbase RLUSD distribution, BNY custody, SBI/Ripple, SBI/Circle/USDC and the SBI multi-rail strategy:

- research/xrp_intelligence/20261120T025053Z-run230-circle-coinbase-usdc-distribution-economics.json
- research/xrp_intelligence/20261119T220358Z-run47-sbi-circle-market-reconciliation.json
- research/xrp_intelligence/20261120T000414Z-run48-dbs-circle-usdc-and-market-cutoff.json

No new direct Coinbase–Circle–Ripple–SBI relationship edge was established in this run. USDC distribution, RLUSD distribution, XRP custody, tokenized deposits and XRPL remittance research remain separate activities; none by itself proves incremental XRP bridge-asset demand or net XRP capital inflow.

Japan's SBIC East/Central/West identity remains resolved as three regional SME investment-development companies, distinct from SBI Holdings. The exact phrases ASK Coin, actual capital and SBIC, ChatGPT SBIC remain unresolved as a single attributable XRP-related claim. The Kamilah/Camilla Stevenson XRP channel candidate remains unlinked to a verified real-world identity; do not attribute its videos to Dr. Kamilah Stevenson without a cross-link from an authenticated channel or primary profile.

### 7. Prediction and platform status

- Forecast status: **NOT_ISSUED**.
- No synchronized receipt-backed historical market dataset, validated learned-model lift over the four baselines, stable probability calibration, completed shadow evaluation or independent attestation has been established.
- The branch contains the scheduled public-data ingestion workflow, but it is not on main. No hourly/daily XRP ingestion schedule is active on the default branch. Its GitHub artifacts/cache are not independent WORM retention.
- Only GitHub authentication and repository access were tested. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks remain unverified live connections. No external model dispatch or data transfer occurred.

### 8. Next concrete actions

1. Keep #1673 as the only active XRP/V3 integration workstream; do not create another integration PR.
2. Finish the transitive review of all 69 changed workflows and scripts, including A2A sandboxing, credential isolation, egress and task authorization.
3. Obtain verifiable branch-protection/required-check evidence and an independent approving review; keep the PR draft until then.
4. Resolve the GitHub Pages publication boundary before any merge because merge automatically publishes the site.
5. Establish independent immutable raw-source retention and activate the read-only ingestion schedule only after safe integration on main.
6. Capture synchronized venue L2 depth, historical spot, derivatives, issuer-level ETF holdings, exchange flows and institutional collateral with byte-exact receipts before model admission.
7. Continue leakage-safe walk-forward comparisons and shadow evaluation. Keep forecasts disabled until all prediction gates pass.

No mainline code change, merge, deployment, publication, secret rotation, Space restart, Kaggle submission, Databricks write, external model dispatch, paper trade, funds transfer or real-money action occurred in this run.


---

## Verification correction — 2026-11-20 12:11 UTC

This append-only correction supersedes the 11:51 UTC market snapshot and corrects one interpretation in that snapshot. No source bytes were captured; all market figures remain research-only and excluded from model features.

### Exact-head CI on 315501c — VERIFIED

The documentation-only handoff commit 315501c033c22879ea147ee3b6e0ce46bf18fd1a passed the exact-head PR CI:

- Full repository suite: **4,440 passed, 1 skipped, 0 failed**, 11 warnings, 23 subtests; 130.81 seconds.
- Inclusive coverage: **73.08%**; legacy/core floor and all mission package floors passed.
- Dependency audit: passed six manifests.
- Money audit: passed.
- A2A Worker tests: passed.
- GitHub Pages build: validation-only passed.
- Exact-head fail-closed gate: blocked, with three blockers only: PR remains draft, no independent approving review, and branch protection could not be verified (HTTP 403). It remains read-only and does not merge.

Run links:
- CI: https://github.com/Barrot-Agent/B-Agent/actions/runs/44733101893
- Dependency audit: https://github.com/Barrot-Agent/B-Agent/actions/runs/44733102107
- Money audit: https://github.com/Barrot-Agent/B-Agent/actions/runs/44733102306
- A2A Worker tests: https://github.com/Barrot-Agent/B-Agent/actions/runs/44733101992
- Fail-closed gate: https://github.com/Barrot-Agent/B-Agent/actions/runs/44733102087

This verification belongs to 315501c. The next handoff-only commit created by this correction is documentation-only; do not transfer this exact-head CI claim to a later SHA without its own run.

### Latest Kraken snapshot — 2026-11-20 12:11:13 UTC

The public Kraken XRP/USD ticker returned:

- Best bid $0.95153; best ask $0.95154; midpoint $0.951535.
- Indicative top-of-book spread approximately 0.105 bps.
- Displayed best bid size 332 XRP; best ask size 5,720 XRP.
- Last trade $0.95189, approximately 3.73 bps above the displayed midpoint.
- 24-hour volume approximately 38.63 million XRP; 24-hour VWAP $0.969575; high $0.99680; low $0.94679; open $0.95925.

The ticker still supplies no exchange event timestamp. The last trade and current quote are not synchronized by a disclosed timestamp. This is one venue and top-of-book only; it does not establish executable depth or slippage. It supersedes the 11:51 UTC Kraken observation for current-state display, but neither snapshot is model-eligible.

Source: https://api.kraken.com/0/public/Ticker?pair=XRPUSD

### ETF flow interpretation correction

The correct source is https://cryptoetf.today/en/xrp-etf-flows.

For November 17, the page's -$6.0M total is composed of -$4.9M from XRPC and -$1.1M from GXRP. The headline's -$4.9M refers specifically to XRPC, not the five-fund total. The earlier addendum incorrectly described this as a provider-internal disagreement; that claim is withdrawn.

The page still shows zero total XRP ETF net flow on November 19, -$19.0M over 30 trading days, five inflow days and ten outflow days, $1.08B net assets and +$1.79B cumulative net flow. November month-to-date headline is -$25.7M while the sum of the displayed rounded daily rows is approximately -$25.2M. The $0.5M difference may be rounding or a scope/update issue; it is not resolved from this page alone. Rows dated November 16–19 are marked provisional. This remains a secondary aggregator, not issuer-reported cash receipts.

The page also reports -$718.7M in total U.S. crypto ETF flows and CEFI 9 for November 19. This is broad-market context, not an XRP-specific flow signal.

### Current state after this correction

- Main remains 7f8e3626c355bb3d89afdff56aeed5e056cb88f4.
- PR #1673 was at head 315501c before this documentation-only correction; the correction creates a new documentation-only head and will trigger fresh CI.
- No mainline code change, merge, deployment, publication, secret rotation, paper trade, funds transfer or real-money action occurred.
- Forecast status remains NOT_ISSUED.


---

## Current-state addendum — 2026-11-20 13:26 UTC

This append-only update supersedes earlier repository-head, exact-head CI, and market observations. Prior source records and branch history are preserved.

### 1. Repository state — VERIFIED

- Current main: `c599419c284ed5c3e21c44c91d5d4229191dced8`, commit time 2026-11-20 12:28:17 UTC.
- Main commit message: `hunter: paid issue scan 2026-11-20T12:28Z from run 44735899857`.
- Main commit changed only `PAID-ISSUES.md` and `data/money/paid_issues.json`; it removed the only prior paid-issue candidate because the current scan found none. No XRP or runtime code changed.
- Main recursive tree: 1,751 entries, 93 workflow files, not truncated.
- Active integration PR: #1673, `integration/xrp-v3-mainline-successor-20261120T0135Z`.
- Current PR head: `0685526ea9c754b99032d39811f9d68d4d6db1f3`; current base: `c599419c284ed5c3e21c44c91d5d4229191dced8`.
- PR comparison: 529 commits ahead, 0 behind; 1,494 changed files; 69 changed workflow files.
- Integration recursive tree: 3,040 entries, 2,853 blobs, 94 workflow files, not truncated.
- PR remains open, draft, and GitHub reports mergeable. Review inventory is empty: zero independent approvals.
- The current main commit's two changed paths do not overlap any of the 17 open PRs, confirmed by paginated changed-filename inventories. No new branch or PR was created.

### 2. Exact-head CI — VERIFIED on 0685526

Run links:
- Full CI: https://github.com/Barrot-Agent/B-Agent/actions/runs/44741411717
- Dependency audit: https://github.com/Barrot-Agent/B-Agent/actions/runs/44741411740
- Money audit: https://github.com/Barrot-Agent/B-Agent/actions/runs/44741411762
- A2A Worker tests: https://github.com/Barrot-Agent/B-Agent/actions/runs/44741411689
- Read-only fail-closed gate: https://github.com/Barrot-Agent/B-Agent/actions/runs/44741411633

Full repository suite, exact head `0685526`:
- **4,440 passed, 1 skipped, 0 failed**, 11 warnings, 23 subtests.
- Runtime 131.58 seconds.
- Inclusive coverage 73.08%; required global and mission-critical package floors passed.
- The job explicitly ran every tracked active repository test, not only the core subset.

Other exact-head results:
- Dependency audit passed all six manifests; no known vulnerabilities reported.
- Money audit: 14 tests passed.
- A2A Worker tests: 6 tests passed; Wrangler configuration/bundle validation passed without deployment.
- GitHub Pages build in the PR CI was validation-only and passed.

The fail-closed gate remains **BLOCKED**, read-only, with three observed blockers:
1. PR #1673 is still draft.
2. No independent approving review exists.
3. Branch-protection configuration cannot be verified: the branch-protection endpoint returns HTTP 403, `Resource not accessible by integration`.

Main branch metadata reports `protected: true`, but its visible required-status-check contexts/checks arrays are empty. The only returned repository ruleset, `Fall Back`, is disabled and contains only deletion/non-fast-forward rules. Do not infer effective review requirements, strict checks, or administrator enforcement from this partial metadata.

### 3. Main automation and publication side effects — VERIFIED

Actions runs on current main:
- Pages build and deployment `44736047089`: success on the current main commit.
- Cross Analysis `44739316257`: success.
- Pillars Consistency Check `44740697804`: failure.

The Pillars check log identifies three independent integration failures:
- GitHub App check: missing `GITHUB_APP_ID`, `GITHUB_APP_PRIVATE_KEY`, and `GITHUB_APP_INSTALLATION_ID`.
- Databricks check: HTTP 403.
- Hugging Face Space check: `BUILD_ERROR`.

No secrets were read, rotated, or changed; no Databricks write or Space restart was attempted.

The successful Pages deployment on main confirms that a mainline update can automatically publish the Pages site. PR #1673 changes public web assets, so a merge can publish those changes as an automatic workflow side effect. Pages validation-only success in PR CI is not publication authorization. Do not merge until that publication boundary is explicitly authorized and all other merge gates are satisfied.

### 4. XRP ingestion and prediction architecture — IMPLEMENTATION STATE

The integration branch contains `data/missions/primary_mission.json` with mission ID `xrp_intelligence_prediction_engine`, priority 1, active status, and Barrot V3 explicitly preserved as execution/orchestration/safety/verification foundation. This mission file is not present on current main; it remains staged in #1673.

The branch adds `.github/workflows/xrp-public-ingestion.yml`:
- Hourly schedule at minute 3 and daily schedule at 00:15 UTC.
- Scheduled capture is main-only; integration-branch pushes perform read-only integration capture.
- Workflow permissions are `actions: read` and `contents: read`.
- The workflow checks predecessor receipt artifacts and records missing/expired continuity rather than silently claiming continuity.
- Raw-source and receipt-chain GitHub artifacts have 90-day retention; the hourly feature-store artifact has 7-day retention, with daily/manual feature artifacts at 90 days.
- The workflow itself explicitly labels these GitHub artifacts **not WORM**. It is not active on main because the workflow is not merged.

The branch's public ingestion adapter is version `xrp-public-market-v3.32`, parser `v3.31`, with a 10 MiB response cap and an allowlist of public source hosts. It includes raw payload SHA-256 receipts, canonical receipt IDs, write-once local raw paths, and a per-run hash chain. Some providers are configured for hash-only receipts rather than retained payload bytes because redistribution rights are not established. Do not describe every source as having retained raw bytes.

The feature store is SQLite with append-oriented triggers and manifest/row hash checks. Its own source docstring correctly states this is not adversarially tamper-proof: a file owner can remove triggers or rewrite the database and recompute unkeyed hashes. Independent signed/timestamped retention remains required.

The forecast ledger uses externally managed Ed25519 evaluator keys and fail-closed readiness thresholds, including at least 100 out-of-sample samples, 100 shadow samples, five independent source groups, and maximum weighted calibration error of 0.05. The chronological walk-forward evaluator includes naive class-prior, momentum, mean-reversion, and volatility-normal baselines.

**Not verified:** an independently anchored WORM archive; synchronized, sufficiently long historical feature coverage; a trained candidate with demonstrated out-of-sample lift over all four baselines; stable calibration and drift performance; completed shadow sample minimums; independent evaluator attestation. Forecast status remains **NOT_ISSUED**.

### 5. Fresh XRP market observations — RESEARCH ONLY, NOT MODEL-ELIGIBLE

**Kraken XRP/USD public ticker**, retrieved during this run at approximately 13:26 UTC:
- Bid $0.94042, displayed size 2,766 XRP.
- Ask $0.94043, displayed size 2,496 XRP.
- Indicative top-of-book spread approximately 0.106 bps.
- Last trade $0.94042; last-trade size approximately 2,106.918 XRP.
- 24-hour volume approximately 35.882 million XRP.
- 24-hour VWAP approximately $0.964380.
- 24-hour high $0.99680; low $0.94001.
- Ticker response did not disclose an exchange event timestamp. The open field is recorded as returned and is not relabeled as a 24-hour open.

Source: https://api.kraken.com/0/public/Ticker?pair=XRPUSD

**OKX XRP-USDT ticker**, provider timestamp 2026-11-20 13:06:51.468 UTC:
- Last $0.9454.
- Bid $0.9453, size 1,862.6 XRP; ask $0.9454, size 6,307.796609 XRP.
- Indicative spread approximately 1.058 bps.
- 24-hour open $0.9909; high $0.9979; low $0.9432.
- 24-hour volume approximately 47.446 million XRP / 45.694 million USDT.
- UTC-day open $0.9604; 08:00 UTC open $0.9695.

Source: https://www.okx.com/api/v5/market/ticker?instId=XRP-USDT

These are different quote currencies and not synchronized provider timestamps. Do not infer a cross-venue basis, aggregate volumes, or executable liquidity. No synchronized multi-level order-book capture was admitted. Both observations are research-only and excluded from the feature store and model evaluation because exact raw HTTP bytes and independently anchored retrieval receipts were not retained in this run.

### 6. Derivatives and ETF source disagreement — PRESERVED

Secondary derivatives providers returned materially different coverage totals and positioning:
- Liqwall, 2026-11-20 00:12 UTC: approximately $915M open interest, down 0.8% in 24 hours; displayed 30-day range $914M–$1.49B.
- OptimistFi, 06:49 UTC: approximately $1.7B open interest across 38 venues; OI-weighted funding negative, approximately 2.9% annualized.
- TradRadar, 09:05 UTC: approximately $1.21B open interest across seven exchanges, down 3.39% in 24 hours; OI-weighted funding -0.0036% per eight hours; at least $5.31M liquidations, including $4.54M longs.
- Coinperps, 2026-11-19 09:02 UTC: approximately $1.95B open interest across 28 markets, down 5.17% in 24 hours; funding +0.0063% per eight hours.

Sources:
- https://liqwall.com/open-interest/xrp
- https://optimistfi.com/perps/markets/xrp
- https://tradradar.io/markets/xrp
- https://www.coinperps.com/perpetuals/xrp

The providers use different venue universes, instruments, timestamps, and aggregation methods. Preserve the disagreement; do not average these values or admit them as one synchronized feature.

Crypto ETF aggregator data published 2026-11-20 05:48 UTC, through November 19:
- November 19 XRP-product net flow: zero.
- Last reported move: November 17, -$6.0M total, comprising -$4.9M XRPC and -$1.1M GXRP.
- Thirty-trading-day net flow: -$19.0M; five inflow days and ten outflow days.
- Reported AUM $1.08B; cumulative net flows +$1.79B.
- November month-to-date headline: -$25.7M; November 16–19 rows marked provisional.

Source: https://cryptoetf.today/en/xrp-etf-flows

This is secondary aggregated data, not issuer-level cash receipts or immutable holdings files. Preserve its provisional status and do not infer direct XRP bridge demand from ETF product flows alone.

### 7. Institutional relationships, identities and nine-platform map

No new verified direct relationship edge among Coinbase, Circle, Ripple, and SBI was established in this run. Existing primary-source reconciliations remain the controlling evidence. Distinguish USDC distribution, RLUSD distribution, custody, stablecoin settlement, collateral eligibility, XRP holdings, and actual XRP bridge usage; none is interchangeable with another.

- Japan's SBIC East/Central/West remain distinct regional SME investment-development entities, not SBI Holdings.
- ASK Coin, the intended exact-phrase reference for “actual capital,” and “SBIC, ChatGPT SBIC” remain unresolved as one attributable XRP-related claim.
- The candidate Kamilah/Camilla Stevenson XRP channel remains unlinked to the verified real-world identity; do not attribute its videos to Dr. Kamilah Stevenson without an authenticated cross-link.
- GitHub is the only platform connection tested. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle, and Databricks remain unverified live connections. No external model dispatch or data transfer occurred.

### 8. Open PR backlog — 17 PRs, no closures

- **Blocked active integration:** #1673.
- **Blocked security reconciliation:** #1677.
- **Partially superseded / needs exact diff reconciliation:** #1671 and #1670.
- **Unique provider-failover work, not yet integrated:** #1668.
- **Stale dependency candidates, exact-head validation pending:** #1666 and #1665.
- **Unique staged product, unpublished:** #1664.
- **Superseded predecessor; preserve until successor is merged and verified:** #1663.
- **Partially overlapping MMI claim-fingerprint work; not a complete duplicate:** #1541.
- **Unique/stacked XRP research or repair work; preserve:** #1450, #1460, #1440, #1437, #1436, #1353, #1265.

No PR was merged or closed. No source branch was rewritten or force-pushed. The current main commit did not overlap any open PR's changed paths.

### 9. Next concrete actions

1. Keep #1673 as the sole active XRP/V3 integration workstream; do not create another successor.
2. Resolve the independent approval, branch-protection verification, and Pages publication blockers before any merge.
3. Continue the transitive review of all 69 changed workflow files and scripts, especially A2A sandboxing, credential isolation, egress, task authorization, and provider write boundaries.
4. Establish independently controlled immutable raw-source retention; GitHub Actions artifacts and SQLite are not WORM.
5. Keep the XRP ingestion schedule inactive on main until the integration is approved and safely merged.
6. Build synchronized historical spot, Level-2 depth, derivatives, ETF, exchange-flow, collateral, and stablecoin datasets with byte-exact receipts.
7. Keep forecasts disabled until the learned model demonstrates leakage-safe out-of-sample superiority, calibration, drift, shadow evaluation, and independent attestation.

No mainline code change, merge, deployment, Pages publication by this run, secret operation, Space restart, Kaggle submission, Databricks write, external model dispatch, paper trade, funds transfer, or real-money action occurred.


---

## Primary-source research addendum — 2026-11-20 13:40 UTC

This section records new primary-source identity and institutional evidence found after the 13:26 checkpoint. It does not alter runtime code or authorize deployment/merge.

### 1. Japan SBIC identity — RESOLVED FROM OFFICIAL COMPANY PAGES

The three regional SBIC entities are distinct Japanese legal companies, linked as sister companies:

- **SBIC East Japan:** Tokyo Small and Medium Business Investment & Consultation Co., Ltd. (東京中小企業投資育成株式会社), official site `sbic.co.jp`. Its official company profile explicitly uses “SBIC East Japan,” gives corporate number `9011001030621`, establishment in 1963, and an operating area covering 18 prefectures east of Shizuoka, Nagano and Niigata. It lists Nagoya and Osaka as sister companies.
  Source: https://www.sbic.co.jp/company/profile/
- **SBIC Central Japan:** Nagoya Small and Medium Business Investment & Consultation Co., Ltd. (名古屋中小企業投資育成株式会社), official site `sbic-cj.co.jp`. Its company profile explicitly uses “SBIC Central Japan,” established 1963, and lists Aichi, Gifu, Mie, Toyama and Ishikawa as its operating area. It lists Tokyo and Osaka as sister companies.
  Source: https://www.sbic-cj.co.jp/company/about/
- **SBIC West Japan:** Osaka Small and Medium Business Investment & Consultation Co., Ltd. (大阪中小企業投資育成株式会社), official site `sbic-wj.co.jp`. Its profile explicitly uses “SBIC West Japan,” established 1963, and lists 24 prefectures west of Fukui, Shiga, Nara and Wakayama. It lists Tokyo and Nagoya as sister companies.
  Source: https://www.sbic-wj.co.jp/profiles/profile/

These are regional SME investment/development policy institutions established under Japan's Small and Medium Business Investment & Consultation Companies Act. They are not SBI Holdings, not SBI VC Trade, and not a single SBI Group subsidiary. Tokyo's official page describes its shareholder base as local governments, chambers of commerce, financial institutions and operating companies. The reciprocal “sister company” links establish affiliation among the three SBIC regionals, not ownership by SBI Holdings.

### 2. “SBIC, ChatGPT SBIC” — likely source identified, partnership NOT established

Tokyo SBIC's official training archive lists a completed two-day course for portfolio companies on June 12–13, 2025: “Introduction to Generative AI and Machine Learning for Manufacturing.” Its curriculum explicitly includes ChatGPT usage, Microsoft Copilot, prompt/business use, AI-generated code, information-leakage risk, RAG and API implementation. The page says general companies could not enroll; the course was restricted to portfolio companies and is marked completed.

Source: https://www.sbic.co.jp/training/20250612co/

This is a strong primary-source explanation for an “SBIC + ChatGPT” reference. It is a training course delivered by an outside instructor, not evidence of an OpenAI partnership, model deployment, ChatGPT integration contract, or SBI Holdings relationship. Exact original phrase attribution remains unresolved.

### 3. SBI banking, rewards and XRPL relationships — separate evidence classes

Primary-source findings:

- **SBI Shinsei Bank + SBI VC Trade, February 2, 2026:** an official campaign offered XRP exchange vouchers to eligible customers placing at least ¥300,000 in a six-month yen term deposit, with voucher value tiered by deposit amount up to ¥20,000. This was a time-limited campaign with entry/deposit deadlines through March 31, 2026; it was not a conversion of the full deposit principal into XRP.
  Source: https://www.sbigroup.co.jp/news/pr/2026/0202_16075.html
- **SBI VC Trade + Aplus + Visa, May 1, 2026:** an official announcement introduced SBI Visa Crypto Card products. The cardholder chooses BTC, ETH or XRP; card points are automatically exchanged into the selected asset, subject to an SBI VC Trade account. No public asset-by-asset redemption total was found, so the announcement does not establish the amount of XRP actually purchased.
  Source: https://www.sbigroup.co.jp/news/2026/0501_16304.html
- **SBI Ripple Asia, February 26, 2026:** an official conceptual proof-of-concept considered tokenized deposits and deposit-based digital money using existing infrastructure including MoneyTap and an SBI Ripple Asia token-issuance platform, with XRPL contemplated as the blockchain technology. This is a concept POC, not proof of a production bank settlement rail, transaction volume, or XRP bridge-asset use.
  Source: https://www.sbigroup.co.jp/news/pr/2026/0226_16145.html
- **SBI VC Trade, July 7, 2026:** the company reported 2 million registered service accounts as of July 6, 2026. It is an SBI Holdings consolidated subsidiary and offers crypto/stablecoin services; the account count is not an XRP-holder count or XRP balance.
  Source: https://www.sbigroup.co.jp/news/2026/0707_16468.html

A June 10, 2026 pilot allowing customers to direct approximately 20% of deposit interest into crypto vouchers (BTC/ETH/XRP) is reported by secondary outlets citing Nikkei. No matching primary SBI release was located in this search. Do not conflate that report with the independently verified February XRP-voucher campaign. Treat the June pilot's detailed terms and actual participation as secondary-reported/unverified until a primary bank notice or terms document is captured.

### 4. Circle, Coinbase and XRPL — updated official product facts

Circle's current USDC page states:
- USDC is natively supported on 38 blockchains as of September 16, 2026, including the XRPL.
- Circulation was $68.0B as of November 16, 2026.
- Circle describes USDC as fully backed by cash and cash-equivalent reserves with monthly third-party attestations.
- Circle says the Circle Reserve Fund is custodied at BNY Mellon and managed by BlackRock.
- Coinbase is displayed among Circle's institutional-grade liquidity partners.

Source: https://www.circle.com/usdc

This verifies USDC availability on XRPL and specific Circle/BNY/BlackRock and Circle/Coinbase ecosystem relationships. It does **not** establish that USDC flows use XRP as the bridge asset, quantify XRP fee/reserve demand, or demonstrate XRP price impact. The distinction between USDC settlement on XRPL and XRP bridge usage remains mandatory.

### 5. Ripple Payments Direct — current corridor and rail status

Ripple's official Payments Direct change history records:
- November 2026: Indonesia IDR corridor `ID_BIFAST` restored to the API documentation/specification after being withdrawn in September.
- October 2026: Quotes v3 returns one quote per available payment rail; the selected rail travels with the quote into the payment. For stablecoin payouts, the blockchain network is the payment rail.
- September 2026: Japan JPY corridor `JP_ZENGIN` restored.
- October 2026: Turkey TRY payouts paused pending regulatory review.

Source: https://docs.ripple.com/products/payments-direct-2/change-history

These are product/API documentation and corridor-status observations. They are not proof of completed payment volumes, XRP routing, XRP bridge usage, or the specific blockchain used for an individual corridor.

### 6. Camilla/Kamilah Stevenson identity and YouTube inventory

The June 11, 2026 iHeart interview identifies its guest as Dr. Kamilah Stevenson. In the transcript she says she uses X, Instagram, and YouTube under variants of “Cam/ Kamilah / Doctor Camilla Stevenson,” and explicitly warns that many fake pages exist. The transcript is direct evidence of the guest's claimed social presence, but it does not provide the exact YouTube channel URL or handle.

Source: https://www.iheart.com/podcast/1333-the-xrptracer-podcast-284128923/episode/crypto-panics-with-dr-kamilah-stevenson-336576069/

YouTube search attributes “I Moved My XRP Off The Exchanges” to Kamilah Stevenson, published May 20, 2026. The channel handle has not been directly cross-linked by the guest or by a verified official profile. Third-party directories list multiple similar/fake channels, consistent with the guest's warning.

Candidate video: https://www.youtube.com/watch?v=TfFx0g2IgGg

**Inventory disposition:** one candidate video recorded, but not admitted to the verified official-channel inventory. Do not attribute other lookalike channels or reposts to the guest without a direct authenticated cross-link.

### 7. Current derivatives and ETF disagreement — research-only

New provider snapshots:
- AlertaChart, November 20 11:52 UTC: OI-weighted funding -0.0019% per eight hours (-2.13% annualized) across Binance, Bybit, OKX, Coinbase and Hyperliquid; reported OI $599.44M for that five-venue set.
- TradRadar, November 20 09:05 UTC: $1.21B OI across seven exchanges, -3.39% in 24 hours; OI-weighted funding -0.0036% per eight hours; $5.31M reported liquidations, $4.54M longs.
- Liqwall, November 20 00:12 UTC: $915M OI, -0.8% in 24 hours.
- OptimistFi, November 20 06:49 UTC: $1.7B OI across 38 venues, funding approximately -2.9% annualized.
- TradersWeek reports approximately $921.97M across eight exchanges, down 2.9% in 24 hours, with approximately 77% of accounts long.

Sources:
https://www.alertachart.com/data/funding-rates/xrp
https://tradradar.io/markets/xrp
https://liqwall.com/open-interest/xrp
https://optimistfi.com/perps/markets/xrp
https://tradersweek.com/it/crypto/derivatives/xrp

These are not a single consistent OI universe. Exchange count, instrument coverage, timestamp, and aggregation methodology differ. Negative funding in several CEX aggregates is evidence of positioning/carry conditions, not a directional forecast. Do not average these totals or backfill them as synchronized point-in-time features.

ETF aggregators agree on zero reported net XRP ETF flow for November 19, but differ in holdings/AUM and preliminary coverage:
- Crypto ETF Today reports 30-day net flow -$19M, AUM $1.08B, cumulative +$1.79B, with November 19 zero and November 17 -$6M total.
- TradersWeek reports zero November 19 net flow, 7-day net flow -$8.4M and holdings around 1.15B XRP; its November 19 figures are preliminary, with five of six funds reported and two estimated from holdings changes.

Sources:
https://cryptoetf.today/en/xrp-etf-flows
https://tradersweek.com/crypto/etf-flows

The agreement on zero November 19 flow is useful but still secondary. Different fund universes, estimated holdings, timing, and preliminary status prevent treating the two dashboards as identical records.

### 8. High-risk workflow spot audit — EXECUTED, not a complete 69-file review

Read-only main-vs-integration comparison found these specific branch changes:

- `scripts/push_with_token.sh`: integration branch rejects `BRANCH=main` and directs changes through a reviewed PR; current main still permits the default direct-main push path.
- `.github/workflows/deploy-a2a-worker.yml`: current main deploys on main push or manual dispatch; integration branch removes push deployment and requires explicit `YES` deployment and separate `YES` secret-rotation inputs, exact current main SHA, and pinned actions.
- `.github/workflows/deploy-databricks.yml`: integration branch disables the legacy overwrite workflow. Its own explanation says the legacy script overwrites workspace files, resets an unpaused scheduled job and triggers a run.
- `.github/workflows/coinbase-paper-trader.yml`: integration branch disables the legacy BTC-USD paper trader because it calls an external LLM and writes simulated trades to repository state without an exact per-run approval gate.
- `.github/workflows/kaggle-competitions.yml`: explicit YES, competition allowlist, exact main SHA, and a check that main has not advanced are retained.

These are meaningful safety improvements on the integration branch, not yet on main. The complete transitive review of all 69 changed workflows and their scripts remains unfinished. No deployment, secret rotation, Databricks write, Kaggle submission, paper trade, or Space restart was run.

### 9. Verification boundary after this documentation update

The preceding code head `0685526ea9c754b99032d39811f9d68d4d6db1f3` passed the full repository suite (4,440 passed, 1 skipped, 0 failed) and exact-head dependency/money/A2A/Pages validation checks. The subsequent handoff-only commit `3b86b8cbf1777a4c61ef40242f811e805daf8d68` changes no runtime code. Its own full-suite CI was still in progress at the time this research addendum was prepared; do not describe that documentation commit's exact-head suite as complete until GitHub reports a conclusion.

The PR remains draft, no independent approval is present, branch-protection configuration remains unreadable through the current integration permission (HTTP 403), and automatic Pages publication remains an unapproved merge side effect. No merge or mainline modification was performed.
