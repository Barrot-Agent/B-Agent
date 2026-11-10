# Run 128 — XRP intelligence, repository integration and publication-safety reconciliation

**Captured:** 2026-11-10 11:01:17 UTC  
**Mission:** XRP intelligence and prediction-engine mastery — priority 1. Preserve Barrot V3 as execution, orchestration, safety and verification foundation.  
**Current main:** `d4d43be3427375cf79d190e768976de062e20287`  
**Current integration head before this handoff commit:** `0daeba4afd245bc17d03f118a23099dacbe5b08e`  
**Existing integration PR:** [#1640](https://github.com/Barrot-Agent/B-Agent/pull/1640)  
**Run128 evidence:** [JSON artifact](research/xrp_intelligence/20261110T110117Z-run128-live-spot-cbxrp-morpho-etf-market-structure-update.json)

## Executive state

- GitHub access, main, the complete main/integration trees, all 372 open PRs, PR ancestry, overlapping paths, current workflow runs, dependencies, security settings and the latest durable handoff were inspected.
- Main tree: 1,404 entries / 1,299 files / 86 workflows. Integration tree: 1,553 entries / 1,438 files / 87 workflows.
- PR #1640 is open, non-draft, cleanly mergeable, 934 commits ahead and zero behind main; 256 changed files, 123,180 additions and 3,554 deletions.
- Exact-head CI on `0daeba4afd245bc17d03f118a23099dacbe5b08e`: 1,368 full-suite tests passed, zero failed, eight subtests passed, 59.58% inclusive coverage against a 53% floor. Core suite: 677 passed. Wheel build/installation and Barrot V3/XRP mission package verification passed.
- Dependency audit passed all six manifests with zero known vulnerabilities. Fail-closed gate passed and explicitly leaves automatic merge disabled. CodeRabbit check was skipped.
- Exact evidence: [CI 42799439077](https://github.com/Barrot-Agent/B-Agent/actions/runs/42799439077), [dependency audit 42799439370](https://github.com/Barrot-Agent/B-Agent/actions/runs/42799439370), [fail-closed gate 42799439102](https://github.com/Barrot-Agent/B-Agent/actions/runs/42799439102).
- The current main branch still does not contain the primary XRP mission manifest, the XRP ingestion module or the scheduled ingestion workflow. The workflow remains main-only by design and has no verified scheduled main run.
- No new branch or PR was created. No PR was merged or closed.

## Public website safety correction

Main's `web/latest_signal.json` is still dated **2026-10-29 13:23:33 UTC**, with sentiment score 44, confidence 0, news score 88 and 11 headlines. Its source reports missing model credentials and a Groq HTTP 429. This is stale descriptive sentiment, not a validated forecast.

Main's `web/signal_accuracy.json` still displays 45.5% from 772/1,697 observations. The integration branch correctly classifies this legacy variable-horizon scorer as invalid and sets public accuracy to `NOT_EVALUATED`. Its `web/latest_signal.json` and summary state `NOT_ISSUED`, preserve the old sentiment only as `STALE_DESCRIPTIVE_ONLY`, and publish no directional forecast.

This is a material safety correction. However, PR #1640 changes public web assets (`web/landing.html`, `web/latest_signal.json`, `web/latest_signal_summary.json`, `web/signal_accuracy.json`, `web/signals.html`, and related files). A prior main update triggered a successful GitHub Pages build/deployment (run 41799855489 on main SHA `9100dbacb5f9f1b973b053a65ef1e91e96b64f72`). The automatic public publication is an external side effect. Specific authorization for that publication is not established; do not merge or deploy until it is.

## XRPL amendment, validator and on-ledger oracle snapshot — 2026-11-10

**Live amendment snapshot:** XRPL Dashboard reports XRP at $1.0788 and validated ledger #108237841 as of **11:00 UTC**. It reports 98 amendments enabled, nine in flight and zero in the 14-day activation countdown. The 10:59 UTC roll call heard 35/35 trusted validators; 29 affirmative votes are required.

| Amendment | Yes / 29 needed | Current status |
|---|---:|---|
| SingleAssetVault | 23 | 6 short |
| LendingProtocol | 22 | 7 short |
| LendingProtocolV1_1 | 22 | 7 short |
| ConfidentialTransfer | 21 | 8 short |
| DynamicMPT | 16 | 13 short |
| fixXChainRewardRounding | 10 | 19 short |
| Sponsor | 10 | 19 short |
| XChainBridge | 4 | 25 short |
| CryptoConditionsSuite | 0 | 29 short |

The official XRPL documentation confirms that only trusted-validator votes count and an amendment must maintain **more than 80% support for two weeks**. If support falls to 80% or below, the majority is lost and the countdown restarts. The live vote counts come from XRPL Dashboard's own-node validation recorder; the official documentation independently corroborates the rule, not the individual counts.

The native XRPL lending stack is **not active**: the dashboard states that both SingleAssetVault and LendingProtocol must be enabled, and both are below 29/35 with no activation countdown. Do not treat announced lending/vault features as live protocol capacity or current collateral rails.

Separate enabled amendments must not be confused with the in-flight lending stack:
- `fixCleanup3_4_0` activated November 4 at ledger 108112129.
- `BatchV1_1` activated October 9 at ledger 107540993.
- `PermissionDelegationV1_1` activated October 8 at ledger 107524865.
- `fixBatchV1_2` activated October 9 at ledger 107540481.
- The dashboard's `rippled 3.3.0` release summary says the other five amendments still need support, but its own per-amendment majority history records `BatchV1_1` enabled October 9 and `PermissionDelegationV1_1` enabled October 8. Treat that release-summary sentence as stale/internally inconsistent; use the per-amendment EnableAmendment ledger records and flag ledgers for activation status. `fixCleanup3_3_0` and `fixCleanup3_4_0` are distinct amendments and must not be conflated.

### XLS-47 PriceOracle: important source-scope disagreement

The XLS-47 PriceOracle amendment is already live. The current XRPL Dashboard curated-production page reports one production provider (DIA) and two DIA oracle objects. Its primary DIA object had a LastUpdateTime of **2026-11-10 08:45:43 UTC** and published XRP/USD $1.0857, RLUSD/USD $0.999938, EUROP/USD $1.1177, USDC/USD $0.999760 and USDT/USD $0.998720. The second DIA object was last updated **2025-02-24 11:44:09 UTC** and is explicitly cold; its old $2.4835 XRP quote is not current.

The full XRPLWin on-ledger oracle directory has broader scope and disagrees with the curated page's claim that Band Protocol is not currently observed publishing:
- At 07:11:10 UTC it listed Band Protocol XRP/USD $1.10166.
- RubyOracle published XRP/USD $1.0999 at 07:00:01 UTC.
- The latest DIA XRP/USD entry was dated November 9 at 19:41 UTC ($1.09717).
- XRPLWin showed three providers for XRP/USD, four active providers across the directory, 31 provider labels in its provider table, 24 accounts, 16 active pairs of 333 ever published, and 62 oracle documents.

This is a **scope/coverage disagreement**, not proof that all labels are production-grade independent providers. XRPL Dashboard curates named production accounts; XRPLWin enumerates a broader on-ledger directory including hobbyist, experimental and stale objects. Provider tags are self-declared; verify the owning account and methodology before trusting a feed. XRPLWin's page refresh time is not the same as each oracle object's LastUpdateTime. Band and RubyOracle XRP quotes were already about four hours old at the 11:01 UTC run cutoff; the DIA XRP quote was older still.

XLS-47 can put signed price pairs on-ledger, but the presence of a PriceOracle object does not establish that Morpho, an XRPL lending protocol or an institutional collateral system consumes it. No such link was verified. Do not use a stale or unverified on-ledger quote for liquidation or collateral features.

Sources: [XRPL Dashboard live amendments](https://xrpldashboard.com/amendments), [XRPL official amendment rules](https://xrpl.org/docs/concepts/networks-and-servers/amendments), [XRPL Dashboard PriceOracle objects](https://xrpldashboard.com/price-data), [XRPLWin full oracle directory](https://xrplwin.com/oracles), [XLS-47 official specification](https://github.com/XRPLF/XRPL-Standards/blob/master/XLS-0047-PriceOracles/README.md).

## Fresh market and collateral evidence

- Kraken XRP/USD at retrieval 11:01:17 UTC: last $1.07713; bid $1.07714; ask $1.07734; 24-hour volume 25.408M XRP; VWAP $1.09387149; high/low $1.11573/$1.07502. Kraken supplied no provider event timestamp.
- OKX XRP-USDT event time 10:52:39.471 UTC: last 1.0798; bid 1.0799; ask 1.0800; 24-hour volume 63.575M XRP. Kraken USDT/USD last 0.99877 gives an indicative normalized OKX reference of $1.078472, about 0.125% above Kraken. These are asynchronous quotes, not executable arbitrage.
- Latest spot-only Fuelmaps depth snapshot was 08:00 UTC, roughly three hours before the run: within 1%, $12.7M bids versus $10.1M asks. It covered six named venues but excluded Binance and Bitget. No synchronized fresh L2 snapshot was obtained at the run cutoff.
- Derivatives aggregators at 08:15 UTC report approximately $1.64B–$2.43B open interest, with contracting OI, positive but modest funding and long-heavy liquidations. Coverage overlaps and is not synchronized; do not average.
- CryptoKeyhole's 07:19 UTC November 9 ETF update is partial 3/4: −9,216,553 XRP, approximately −$10.1M, with Franklin XRPZ pending. CryptoETF and Alpha/Coinglass report slightly different totals and contradictory completeness/zero-fill behavior. Treat all tracker flows as model-ineligible; holdings changes are not automatically cash redemptions or exchange sales.
- Coinbase's latest explicitly timestamped proof-of-reserves search result reports 152,372,342.33 XRP reserves against 152,370,095.8 cbXRP supply (2,246.53 XRP displayed surplus; refresh shown as November 10, 05:09 AM, timezone unspecified). Localized/cached page variants display different refresh times and balances, including older August/September values. Preserve the cache/locale disagreement; this issuer page is not an independent attestation.
- Current Morpho REST reference confirms `GET /v0/blue/markets/{market-selector}/liquidity`; `market_liquidity` and `reallocatable_liquidity` are separate, and `borrow_amount_to_target_utilization` is not additive. The specific current `/state/history` API reference explicitly returns `total_collateral_assets`, matching the collector's history parser, while a generic Morpho "Get Market Data" tutorial says aggregate collateral totals are not available in REST. Preserve this documentation disagreement and verify live response schema before model admission; the field is documented for history, not established for the current `/state` response. Current REST provides market root/state/history/liquidity/oracle and user-specific positions, including a per-user Blue position list across markets; it does not provide a market-wide borrower-health list. Per-user position lists require known addresses, pagination and weakly consistent reads. Deriving health requires separate user-position, market-state, market-root/LLTV and oracle reads; those reads are not an atomic liquidation check. The old market-wide positions-health page returns 404. Morpho's public API is as-is with no SLA; implement fallback and freshness checks. No current Morpho market/oracle/position snapshot was retrieved.
- The November 6 historical Morpho snapshot (about $59.24M USDC debt, 119.87M cbXRP collateral, oracle 1.1843, LLTV 62.5%) is not current. Current Kraken spot is about 9.05% below that historical oracle reference, but this is only cross-date sensitivity; no current liquidation inference is justified.
- BLS October CPI and Real Earnings are scheduled for November 10 at 13:30 UTC. At this cutoff they are future events, not released results.

## Identity and institutional research

- Japan's SBIC East/Central/West remain the Tokyo, Nagoya and Osaka regional investment-consultation companies, separate from SBI Holdings. Tokyo SBIC's 2025 investee-company course included ChatGPT and Copilot instruction; no OpenAI partnership is established.
- “Ask Coin” exchange remains listed as inactive/untracked with no reserve data. Permission Coin's ASK token is a separate Polygon/Base asset; no XRP integration is verified.
- “Actual capital” is not a standardized XRP metric. Cash subscriptions, in-kind XRP, debt proceeds, drawn facilities, contingent equity capacity and secondary resales remain separate.
- Search surfaced several similarly named Kamilah Stevenson YouTube channels, but no primary cross-link establishes that they belong to the previously corroborated guest-appearance identity. No personal-channel video inventory was created.
- Coinbase/Circle USDC distribution, Circle/SBI Japan, SBI/Ripple, SBI Ripple Asia, SBI Remit XRP corridors, RLUSD, JPYSC, Coinbase/BNY/BitGo custody, and Ripple/Circle/Coinbase national trust-bank charters remain separate legal entities, products and capital/settlement flows. No stablecoin balance, custody balance or corporate revenue is counted as XRP demand without direct evidence.

## Prediction engine — actual status

Implemented on the integration branch: 46 source definitions (42 hourly, two weekly CFTC, two non-commercial XRPL nodes excluded); read-only public collector; raw-byte SHA-256 receipts and receipt-chain logic; point-in-time SQLite feature-store prototype; four deterministic baselines (naive class prior, momentum, mean reversion, volatility normal); chronological walk-forward evaluation with horizon-sized purge/embargo; temporal calibration; univariate drift diagnostics; fail-closed forecast/outcome ledger requiring trusted Ed25519 evaluator attestation.

Not production-ready: no mature synchronized historical XRP dataset; no successful scheduled main-branch run; no independent WORM/timestamp authority; no independently authenticated source-group registry; no effective-sample-size/block-bootstrap/HAC correction for overlapping multi-horizon origins; no production evaluator key or independent signing service; no demonstrated out-of-sample lift or sufficient shadow outcomes. Readiness requires at least 100 OOS samples, 100 shadow outcomes, two independent source groups, ten horizon multiples, weighted calibration error no greater than 0.05 and a trusted evaluator signature.

**Forecast status: NOT_ISSUED.** No directional forecast, paper trade or real-money action.

## Nine-platform authentication map

- ChatGPT: current-session GitHub read/write and public-web research verified.
- Copilot: comment-only PR review activity; no approval and no separate authenticated data flow.
- Claude, Grok, Gemini and Codex: unverified.
- Hugging Face: prior BUILD_ERROR; no deployment.
- Kaggle: untested; no submission.
- Databricks: prior HTTP 403; no workspace write.
- No external model received repository data; no persistent nine-platform exchange occurred.

## Current PR backlog and merge decision

- #1640: BLOCKED — sole active V3/XRP integration path; exact-head technical checks pass, but approval/protection/Pages authorization are unresolved.
- #1643: UNIQUE/UNREVIEWED — 670 changed files, 663 unique paths and seven overlaps with #1640; 19 threads, zero unresolved, three outdated; dirty/stale branch. Preserve.
- #1653: UNIQUE/UNREVIEWED — seven files, six unique and one overlap; eight unresolved review threads. Preserve and repair.
- #1614: UNIQUE/UNREVIEWED — 57 files, 49 unique, eight overlaps; draft/dirty. Preserve.
- #1611: UNIQUE/UNREVIEWED — eight files, two unique, six overlaps; draft/dirty. Preserve.
- #1612: two unique and two overlapping paths. Preserve.
- #1610: seven unique and seven overlapping paths. Preserve.
- #1608: three unique paths. Preserve.
- #1269: eight unique and one overlapping path. Preserve.
- Duplicate/superseded-content candidates, retain until #1640 is merged and verified on main: #1642 (7/7 overlapping); #1644 (8/8); #1645 (1/1); #1646 (1/1); #1647 (6/6); #1648 (1/1); #1649 (1/1); #1650 (1/1); #1317 (6/6); #1318 (2/2); #1320 (5/5); #1254 and #1255 (1/1 each).
- Open inventory: 372 PRs (356 drafts, 16 non-drafts). No PRs closed.

PR #1640 is non-draft and GitHub reports `mergeable_state=clean`, but all 62 review submissions are COMMENTED and there are zero APPROVED reviews. All 22 inline threads are resolved but outdated. CodeRabbit check is skipped. The detailed main branch-protection endpoint returns HTTP 403; the visible fallback ruleset is disabled, so effective required approvals/status contexts remain unverified.

**Do not merge.** Required independent approval is absent, effective branch protection is unverified, and the public Pages publication side effect is not specifically authorized. Never bypass protection.

## Next actions

1. Obtain independent approval and authoritative branch-protection visibility.
2. Resolve explicit authorization for automatic GitHub Pages publication before any merge.
3. Refresh the stale PR description (it still begins with Run 13) while retaining historical evidence in this canonical handoff.
4. Obtain a consistent current Morpho market-state/liquidity/oracle snapshot; do not infer live position liquidations from November 6 cohorts.
5. Reconcile Coinbase proof-of-reserves locale/cache variants and exchange-wallet attribution.
6. Capture the BLS CPI first-release vintage after 13:30 UTC.
7. Continue synchronized historical XRP data and independent raw-receipt anchoring.
8. Keep forecast issuance disabled until all independent out-of-sample, calibration, drift, shadow and evaluator-attestation gates pass.

No merge, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push or destructive worktree operation occurred.

---

# Run127A — Morpho cbXRP collateral stress and API-access reconciliation

**Research addendum captured:** 2026-11-10T10:22:50Z. This is a historical collateral-risk analysis, not a live market-state capture. It was added after Run127's 10:05:55Z run start; all underlying Morpho position observations are dated November 6 and therefore precede the cutoff.

## Historical Morpho cbXRP/USDC market snapshot

CryptoSlate's November 7 analysis of Morpho GraphQL position and market data reports a November 6 snapshot for the Base cbXRP/USDC market:

- Market ID: 0xd4a903dc6d949519060c7707f9604fdc9772c046e05c2e3a8fce0bd7196e4109.
- Chain ID 8453; cbXRP collateral; USDC loan; Chainlink XRP/USD oracle with a 1:1 USDC leg; LLTV 62.5%.
- Market state at 13:24:46 UTC: approximately $59.24M USDC debt against 119.87M cbXRP collateral, with oracle reference 1.1843 USDC per cbXRP.
- Aggregate debt/collateral-value ratio at that oracle reference: approximately 41.73%.
- Within a further 5% oracle-price decline: 462 positions, $3,229,610.99 USDC debt and 4,504,596.67 cbXRP collateral.
- Within a further 10% decline: 1,070 positions, $8,844,820.21 USDC debt and approximately 12.73M cbXRP collateral. The 5% cohort is a subset of the 10% cohort; do not add them.
- The position analysis paginated 500/500/70 rows, with page timestamps around 13:24:54–13:24:55 UTC. This was not a snapshot-isolated walk; position updates occurred around the same observation window.

Sources: [CryptoSlate analysis](https://cryptoslate.com/), [public Dune query attributed to @morpho](https://dune.com/morpho), [Morpho API](https://api.morpho.org/graphql). The Dune query and article independently identify the same market and LLTV, but both depend on Morpho's underlying data and are not independent measurements of current positions.

## Conditional comparison with the later XRP spot reference

The same-run Kraken XRP/USD ticker showed $1.08792, but supplied no provider event timestamp. This is approximately 8.14% below the November 6 Morpho oracle reference of 1.1843. The corresponding historical thresholds are:

- 5% decline threshold: 1.125085 USDC per cbXRP. The later Kraken spot reference is about 3.30% below this level.
- 10% decline threshold: 1.06587 USDC per cbXRP. The later Kraken spot reference is about 2.07% above this level.

**Conditional interpretation only:** if the current Morpho oracle moved in line with the Kraken spot reference and the November 6 positions were unchanged, the historical 5% cohort would be beyond its modeled LLTV threshold; the entire 10% cohort would not. Current Morpho oracle, current positions, repayments, collateral top-ups and executed liquidations were not retrieved. Do not call the 462 historical positions currently liquidatable. Do not infer any native XRP sale.

The November 6 market collateral of 119.87M cbXRP is about 78.67% of Coinbase's November 10 reported 152.37M cbXRP supply. This is a cross-date concentration comparison only, not a current allocation or proof that all supply remained in the market.

## Coinbase loan-protection mitigation and limits

Coinbase's official USDC-loan collateral and loan-health help pages describe opt-in liquidation protection: it must be enabled for each loan, applies once, expires after one year, requires available collateral, and may be partial or fail. Coinbase explicitly says it is not a guarantee against liquidation. The public documentation does not establish that every cbXRP Morpho position is a Coinbase-app borrower or that every cbXRP position qualifies for this feature. Treat it as a possible mitigation for some borrowers, not a market-wide offset.

Sources: [Coinbase collateral and loan protection](https://help.coinbase.com/en/coinbase/trading-and-funding/loan/collateral), [Coinbase USDC loan health](https://help.coinbase.com/en/coinbase/trading-and-funding/loan/loan-health), [Coinbase lending introduction](https://help.coinbase.com/en/coinbase/trading-and-funding/loan/lending-intro). Coinbase describes USDC deposits into Morpho vaults that route funds to lending markets; that does not make Coinbase the borrower or the owner of all market positions.

## Morpho API access conflict — do not add an unverified endpoint

A specific Morpho documentation page describes a cursor-paginated GET market positions/health endpoint with LTV filters and indexed-block/ltv-computed timestamps. The current general API documentation says the Core REST spec no longer exposes a market-wide Blue position-health list; it describes GraphQL as still served for existing integrations. These statements conflict. No direct live positions/health response was retrieved, and no endpoint was added to the scheduled source registry.

Decision: keep the existing Morpho market-parameters, market-state, liquidity, state-history and oracle endpoints as digest-only/raw-only sources. Do not add market-wide positions/health ingestion until lawful access, authentication/permission, current endpoint status, pagination consistency and terms are directly verified. If the REST endpoint is unavailable, investigate an authorized public GraphQL or on-chain event reconstruction path. Aggregate risk metrics only; do not publish borrower addresses.

Sources: [specific Morpho positions-health reference](https://docs.morpho.org/api/markets/get-market-positions-health/), [general Morpho API documentation](https://docs.morpho.org/developers/api/morpho/).

## Prediction and execution boundary

- This historical snapshot is research-only and is not model-admitted.
- No live current Morpho utilization, borrow, collateral, oracle or position-health metric was obtained.
- No actual liquidation, cbXRP redemption or native XRP sale was verified.
- Forecast status remains NOT_ISSUED. No directional forecast, paper trade or real-money action occurred.

Updated structured evidence: [Run127 market and collateral reconciliation JSON](research/xrp_intelligence/20261110T100555Z-run127-spot-cbxrp-etf-derivatives-exchange-macro-reconciliation.json).

---
# Barrot XRP Mission — Run127: spot, cbXRP reserves, ETF vintages and derivatives reconciliation

**Run start / cutoff:** 2026-11-10T10:05:55Z. Provider event/publication times are kept separate from retrieval time. A source timestamp after the cutoff is excluded; missing or unzoned timestamps are not inferred.
**Main SHA:** d4d43be3427375cf79d190e768976de062e20287.
**Integration head before Run127 artifacts:** 6a9513a227e9db8b70ad14551cef9e390476df77.
**Integration branch:** integration/core-capabilities-mmi-structural-paper-20261104.
**Active integration PR:** #1640. No new branch or PR created.
**Mission:** XRP intelligence and prediction-engine mastery, priority one. Preserve Barrot V3 as execution, orchestration, safety and verification foundation.

## 1. Repository and exact-head verification — VERIFIED

- Main tree: 1,404 entries, 1,299 files. Main SHA remains d4d43be3427375cf79d190e768976de062e20287.
- Integration tree: 1,551 entries, 1,438 files; recursive tree was not truncated.
- Main does not contain the XRP primary mission manifest, XRP ingestion workflow or XRP ingestion module. All three are on the integration branch.
- PR #1640: 929 commits ahead, zero behind, 254 changed paths; GitHub reports mergeable.
- Open PR inventory: 372 total, 356 drafts and 16 non-drafts.

Exact-head CI on 6a9513a227e9db8b70ad14551cef9e390476df77:
- Full repository suite: **1,368 passed, zero failed, eight subtests passed**.
- Inclusive coverage: **59.58%**, above the 53% floor.
- Core suite: 677 passed.
- Wheel build and installed-wheel verification passed, including Barrot V3, XRP mission and canonical data resources.
- Dependency audit: six manifests passed, zero known vulnerabilities.
- Fail-closed merge gate passed; automatic merging remains disabled.

Evidence:
- [Full CI 42794570105](https://github.com/Barrot-Agent/B-Agent/actions/runs/42794570105)
- [Dependency audit 42794570099](https://github.com/Barrot-Agent/B-Agent/actions/runs/42794570099)
- [Fail-closed gate 42794570075](https://github.com/Barrot-Agent/B-Agent/actions/runs/42794570075)

The full-suite job log confirms 1,368 passed, eight subtests and 59.58% inclusive coverage. The six-manifest audit log reports success for root runtime, development, supplemental, Hugging Face Space, legacy and pyproject manifests. The gate explicitly states that automatic merging is intentionally disabled.

## 2. Main-branch CI and security state — VERIFIED

- Main CI run 42526890841 passed on the unchanged main SHA.
- Main dependency audit 42579080840 passed.
- Main scheduled Cross Analysis run 42794199242 passed.
- Main Pillars Consistency Check 42621970927 failed on the unchanged main SHA for three separate reasons: missing GITHUB_APP_ID/PRIVATE_KEY/INSTALLATION_ID, Databricks HTTP 403, and Hugging Face Space BUILD_ERROR. No credentials were read, changed or rotated.
- GitHub reports main protected=true. Detailed branch-protection API access returns HTTP 403; the visible fallback ruleset is disabled. Effective required approvals and status contexts remain unverified.
- A previous main push triggered successful GitHub Pages publication. PR #1640 changes seven public web assets; authorization for that automatic publication remains unresolved.

## 3. XRP ingestion architecture audit — VERIFIED IN CODE, NOT YET ACTIVE ON MAIN

Correction to the older handoff count: the current integration code and tests contain **46 endpoint definitions**, not 40:
- 42 scheduled hourly endpoints.
- Two weekly CFTC endpoints.
- Two non-commercial XRPL node endpoints excluded from scheduled collection.

The XRP Public Market Ingestion workflow is configured hourly at minute 03 UTC and daily at 00:15 UTC. It has actions:read and contents:read permissions, no repository-write permission, and its capture job runs only when the ref is main. Because the workflow is not on main, scheduled XRP ingestion has not started.

Artifact retention is 90 days for raw receipts, seven days for per-run feature-store checkpoints, and 90 days for daily feature-store/walk-forward artifacts. GitHub Actions artifacts and cache are not independently controlled WORM storage. The SQLite feature-store triggers and manifest hashes deter ordinary mutation but the code explicitly states they are not an adversarial tamper-proof boundary.

Coinbase cbXRP proof-of-reserves and Morpho cbXRP collateral endpoints are digest-only/raw-only. Regression tests explicitly prevent their admission as model features. The live Morpho market state, utilization, borrow, liquidity and oracle payload were not retrieved in this run.

## 4. Fresh spot, depth and derivatives evidence

### Spot

- Kraken XRP/USD: last $1.08792; bid $1.08768; ask $1.08769; 24-hour volume 24.254M XRP; VWAP $1.09460651; high $1.11573; low $1.07502. The Kraken ticker supplied no provider event timestamp.
- OKX XRP-USDT: 1.0894; bid 1.0893; ask 1.0894; 24-hour volume 63.360M XRP; provider event time 09:51:27.078 UTC.
- Kraken USDT/USD: 0.99873, with no provider event timestamp. Mechanically normalized OKX reference: $1.088016462, approximately 0.00887% or 0.89 basis points above Kraken's last trade.
- These observations are asynchronous and are not an executable arbitrage opportunity.

Sources: [Kraken XRP/USD API](https://api.kraken.com/0/public/Ticker?pair=XRPUSD), [OKX XRP-USDT API](https://www.okx.com/api/v5/market/ticker?instId=XRP-USDT), [Kraken USDT/USD API](https://api.kraken.com/0/public/Ticker?pair=USDTUSD).

### Spot order-book depth

Fuelmaps' six-venue spot snapshot at 08:00 UTC showed XRP midpoint $1.0938 across six of six venues:
- Within 0.5%: $8.1M bids, $5.5M asks, 59.4% bid share.
- Within 1%: $12.7M bids, $10.1M asks, 55.6% bid share.
- Within 2%: $18.1M bids, $11.1M asks, 61.9% bid share.
- Within 5%: $24.3M bids, $13.5M asks, 64.3% bid share.
- Within 10%: $32.8M bids, $15.0M asks, 68.7% bid share, with five of six venues covering.

Fuelmaps includes Coinbase, OKX, Kraken, Bitstamp, Bitfinex and Gemini; excludes Binance and Bitget; spot only; one-minute snapshots are averaged into hourly columns. Resting orders can be cancelled and hidden orders are not visible. The snapshot is about two hours older than the run cutoff and is not synchronized with the later ticker observations. This is a descriptive bid-side imbalance, not a forecast.

Source: [Fuelmaps XRP spot order book](https://fuelmaps.io/order-book/).

### Derivatives

- Liqwall, 10:02 UTC: open interest $1.21B, down 2.2% in 24 hours; $4.6M liquidations, including $4.0M longs and $635K shorts; average funding +0.0079% per eight hours; Binance funding +0.0099%; 74.9% of Binance accounts with XRP positions long.
- TradRadar, 09:15 UTC with a stated 15-minute delay: open interest $1.64B across seven exchanges, down 4.13%; funding +0.0077% per eight hours; at least $4.80M liquidations, $4.07M longs and $731.56K shorts; 79.7% long account share.
- Open-interest aggregates differ by approximately 35.5%. Venue coverage overlaps and methods differ; do not average or count the providers as fully independent.
- Common descriptive finding: contracting open interest, positive funding and long-heavy liquidations. This supports deleveraging/crowding, not a directional forecast.

Sources: [Liqwall](https://liqwall.com/coins/xrp), [TradRadar](https://tradradar.io/markets/xrp).

## 5. Coinbase cbXRP reserve and exchange-wallet reconciliation

Coinbase's public proof-of-reserves page displays 152,372,342.33 XRP total reserve and 152,370,095.8 cbXRP total supply, with 152,370,095.795 cbXRP on Base. The displayed difference is 2,246.53 XRP; reserve/supply ratio is approximately 1.00001474. The page labels its refresh as November 10, 09:34 AM but does not state a timezone. This is an issuer-published page, not an independent attestation.

XRP Insights' 08:00 UTC wallet tracker includes 150.1M non-customer cbXRP on Base in its Coinbase wallet attribution. That is approximately 2.272M XRP below Coinbase's proof-of-reserves reserve total. Scope, wallet labeling or timing remains unresolved; do not treat the difference as unbacked cbXRP and do not add the two figures.

XRP Insights reports 22.33B XRP across 701 publicly attributed wallets and 24 exchanges. Same-wallet changes are -8.9M XRP over seven days and -150.9M over 30 days. Two newly tracked wallets hold 512M XRP, so the naive +361.1M total change is a coverage change, not an inflow. The wallet set includes cold, hot, deposit and omnibus balances; it is not tradable float. Same-wallet declines cannot distinguish customer withdrawals from internal transfers to untracked wallets.

Selected seven-day exchange changes: Coinbase -28.4M XRP; Kraken +26.7M; Upbit +26.3M; Bithumb -16.2M; Binance -9.0M; SBI VC Trade -3.1M; Gate.io -30.0M; Bitstamp +17.4M.

Sources: [Coinbase cbXRP proof of reserves](https://www.coinbase.com/cbxrp/proof-of-reserves), [XRP Insights exchange balances](https://xrp-insights.com/exchange-balances).

TrackWhale's current page declares a 10:07 UTC snapshot, 65 seconds after this run's 10:05:55 UTC cutoff. It is quarantined as future-at-cutoff and not used. Run126D's 09:30 UTC capture remains the latest admissible TrackWhale snapshot.

## 6. ETF flow reconciliation and disagreement

CryptoKeyhole's 09:57 UTC page reports November 9 partial data for three of four daily-tracked funds: Bitwise -8,594,551 XRP; Canary XRPC -427,341; 21Shares TOXR -194,660; Franklin XRPZ pending. The page total is -9,216,553 XRP, while the displayed components sum to -9,216,552 XRP, a one-XRP arithmetic discrepancy. The page reports approximately -$10.1M. Latest complete day November 6: -752,048 XRP; last five complete days: -765,403 XRP; cumulative through November 6: +2,622,459 XRP.

CryptoETF reports approximately -$10.3M and says three of five funds have reported, but later text on the same page claims five of five while its detailed table still marks XRPZ and GXRP pending. Alpha reports approximately -$10.4M and claims five of five, but publishes no fund list, AUM or holdings and shows zero for some funds without issuer confirmation.

These trackers share underlying issuer inputs despite separate publishers. They disagree on completeness, Canary/TOXR values and missing-versus-zero treatment. Do not average, zero-fill or interpret ETF holdings changes as proof of XRP spot sales; cash versus in-kind redemptions remain unresolved. These observations are not model-admitted.

Sources: [CryptoKeyhole](https://cryptokeyhole.com/etf-flows/xrp/), [CryptoETF.today](https://cryptoetf.today/en/xrp-etf-flows), [Alpha Finance](https://alphafinance.io/etf/xrp/).

## 7. Macro, regulation and identity research

- BLS schedules October CPI and Real Earnings for November 10 at 08:30 Eastern / 13:30 UTC. Both are future at this run cutoff; no result or reaction is inferred. [BLS calendar](https://www.bls.gov/schedule/2026/11_sched.htm).
- Reuters reports the BOJ's ETF sales pace rises to 860B yen annual book value from 330B, effective January 2027; the BOJ estimated about 1T yen / $6.33B additional annual proceeds, while the finance minister qualified that actual remittance depends on fiscal-year and budget calculations. This is macro policy, not an XRP flow. [Reuters](https://www.reuters.com/world/asia-pacific/boj-estimates-6-billion-annual-gain-faster-etf-sales-finance-minister-says-2026-11-10/).
- Japanese investors bought 493.9B yen of foreign bonds and 1.46T yen of foreign equities in October, while remaining net sellers of foreign debt by 4.16T yen year-to-date. This is cross-border capital-flow context, not direct XRP demand. [Reuters](https://www.reuters.com/business/finance/japanese-investors-become-net-buyers-foreign-bonds-first-time-three-months-2026-11-10/).
- SBIC East/Central/West remain Tokyo/Nagoya/Osaka regional Small and Medium Business Investment & Consultation companies, distinct from SBI Holdings. Tokyo SBIC's official 2025 course included ChatGPT and Copilot instruction for investee companies; this is not an OpenAI partnership.
- ASK Coin exchange listing and Permission Coin's ASK token are separate candidates; no XRP integration is verified.
- Actual capital is not a standardized XRP metric. Continue separating cash purchases, in-kind XRP, debt proceeds, drawn facilities, contingent capacity and secondary resales.
- A YouTube channel candidate named Kamilah Stevenson surfaced through a third-party directory, but its owner was not independently linked to the previously corroborated guest-appearance identity. No personal-channel video inventory or attribution was made.

## 8. Prediction engine — implemented, but forecast gate remains closed

The integration branch contains 46 endpoint definitions, a point-in-time SQLite feature store, raw-source receipt/chain logic, four deterministic baselines (naive class prior, momentum, mean reversion and volatility-normal), chronological walk-forward evaluation with purge/embargo, probability calibration and drift diagnostics, and a fail-closed forecast ledger.

Readiness thresholds verified in code: at least 100 training samples, 100 out-of-sample samples, 100 shadow outcomes, two independently receipted source groups, a time span of at least ten forecast horizons, weighted calibration error no greater than 0.05, passing calibration and shadow evaluation, and a trusted independent Ed25519 evaluator attestation. The attestation is unavailable by default, so issuance fails closed.

The public web assets remain NOT_ISSUED / NOT_EVALUATED. The legacy 45.5% signal score is explicitly labeled invalid variable-horizon history, not predictive accuracy. The scheduled ingestion workflow is not on main, so no production scheduled ingestion has been executed.

**Forecast status: NOT_ISSUED.** No directional forecast, paper trade or real-money action occurred.

## 9. Nine-platform coordination snapshot

- ChatGPT: current-session GitHub read/write on the existing integration branch and public-web research verified.
- Copilot: 62 COMMENTED review submissions, zero approvals; comment activity is not a persistent authenticated data flow.
- Claude, Grok, Gemini and Codex: unverified; independent assignments designed but not executed.
- Hugging Face: prior BUILD_ERROR; no deployment or Space restart.
- Kaggle: untested; no submission.
- Databricks: prior HTTP 403; no workspace write.
- No external model received repository data; no persistent nine-platform data exchange occurred.

## 10. PR inventory, overlap and backlog

Open inventory: 372 PRs, 356 drafts, 16 non-drafts. PR #1640 is the only active V3/XRP integration path.

- #1640: blocked integration; 929 ahead, zero behind, 254 changed files; mergeable reported. 62 review submissions are all COMMENTED, zero APPROVED. All 22 inline threads are resolved but outdated.
- #1643: 670 changed files; 663 paths unique to #1643 and seven shared with #1640. Stale/non-mergeable research archive; preserve its unique evidence.
- #1653: seven files; six unique and one shared with #1640. Eight unresolved review threads identify recursive submodule fetch risk, degraded graph state reported as synchronized, timeout handling and other correctness/stability issues. Preserve but keep blocked pending fixes.
- #1642: seven of seven paths overlap #1640; draft superseded-content candidate.
- #1644-#1650: dependency-update paths overlap #1640. The integration branch already contains checkout@v7, download-artifact@v8, upload-artifact@v7, pytest>=9.2.0, types-requests>=2.33.0.20261030, databricks-sdk>=0.158.0 and huggingface_hub>=2.4.0. Treat as superseded-content candidates only after successor merge and main verification.
- #1317: six of six paths overlap #1640; #1318: two of two; #1320: five of five. Superseded candidates, not to be closed before verified merge.
- #1254 and #1255 each change the legacy requirements path already changed by #1640; reconcile exact dependency content before any closure.
- #1269: nine files, eight unique and one shared CI workflow; preserve topology work.
- #1614: 57 files, 49 unique and eight shared with #1640; draft, preserve unique research until content reconciliation.
- #1611: eight files, six shared and two unique; draft, preserve until content reconciliation.
- #1590: 25 files, 12 shared and 13 unique; preserve unique paths.
- #1597: 17 files, 15 shared with #1643 and two unique. #1591: 14 files, 12 shared with #1643 and two unique; all 14 overlap #1597. Duplicate research candidates; do not close before verified successor merge.
- No source PR was closed. The remaining drafts are unique/unreviewed or duplicate candidates pending exact content reconciliation; no bulk closure.

## 11. Merge decision

**PR #1640 remains unmerged.** The technical checks passed on exact head 6a9513a, but zero approving reviews exist; branch-protection details are inaccessible (HTTP 403); the visible fallback ruleset is disabled; and the PR changes seven public web assets whose automatic GitHub Pages publication is not specifically authorized. The user's conditional merge authorization is therefore not satisfied. No branch-protection bypass was attempted.

## 12. Durable artifacts and next actions

- [Run127 structured evidence artifact](research/xrp_intelligence/20261110T100555Z-run127-spot-cbxrp-etf-derivatives-exchange-macro-reconciliation.json)
- [Run127 nine-platform coordination snapshot](research/xrp_intelligence/nine_platform_coordination_snapshot_20261110T100555Z.json)
- [Current mission handoff](BARROT_XRP_MISSION_HANDOFF_LATEST.md)
- [PR #1640](https://github.com/Barrot-Agent/B-Agent/pull/1640)

Next actions:
1. Obtain independent approval and authoritative branch-protection visibility; resolve Pages publication authorization before merge.
2. Capture BLS CPI/Real Earnings only after 13:30 UTC and preserve the first-release vintage.
3. Resolve the Coinbase cbXRP 2.272M XRP reserve-scope difference and obtain live Morpho market state, utilization, liquidity, history and oracle values.
4. Continue synchronized historical spot/L2/derivatives/exchange-flow/collateral data and independent WORM/timestamp anchoring.
5. Reconcile ETF issuer files, missing-versus-zero status and the one-XRP arithmetic discrepancy without averaging providers.
6. Preserve unique research and topology PRs; close only exact duplicates after successor content is merged and verified on main.
7. Continue leakage-safe out-of-sample and shadow evaluation. Keep forecast issuance disabled until every readiness gate passes.

No merge, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push or destructive worktree operation occurred.

---
# Barrot XRP Mission — Run126D: exchange-flow reconciliation and macro/geopolitical event update

**Capture time:** `2026-11-10T09:50:02.435Z`
**Main SHA:** `d4d43be3427375cf79d190e768976de062e20287`
**Previously verified code/test head:** `dd655dc5b786c72e1b16cee768976fa38be19903`
**Integration branch:** `integration/core-capabilities-mmi-structural-paper-20261104`
**Mission:** XRP intelligence and prediction-engine mastery, priority one.
**Foundation:** Preserve Barrot V3 as execution, orchestration, safety and verification.

## 1. Exact-head verification carried forward — VERIFIED

Run126C was fully verified on exact head `dd655dc5b786c72e1b16cee768976fa38be19903`:

- Full repository suite: **1,368 passed, zero failed, eight subtests passed**.
- Inclusive coverage: **59.58%**, above the 53% floor.
- Core suite: 677 passed.
- Wheel build and installed-wheel verification passed, including Barrot V3, XRP mission and canonical data assets.
- Dependency audit: six manifests passed, zero known vulnerabilities.
- Fail-closed merge gate passed; automatic merging remains disabled.

Evidence:
- [Full CI 42793432086](https://github.com/Barrot-Agent/B-Agent/actions/runs/42793432086)
- [Dependency audit 42793431999](https://github.com/Barrot-Agent/B-Agent/actions/runs/42793431999)
- [Fail-closed gate 42793432203](https://github.com/Barrot-Agent/B-Agent/actions/runs/42793432203)

The Run126D handoff update is documentation-only and must receive its own exact-head CI, dependency audit and fail-closed verification. Do not claim its checks before they complete.

## 2. New exchange-balance snapshot — November 10, 08:00 UTC

XRP Insights reports **22.33B XRP** in 701 publicly labeled XRP Ledger wallets attributed to 24 exchanges, approximately 32.4% of its circulating-supply definition and 22.3% of total supply.

Same-wallet changes:
- Seven days, Nov 3–10: **−8.9M XRP** (−0.04%).
- Thirty days, Oct 11–Nov 10: **−150.9M XRP** (−0.69%).
- Naive total change is +361.1M XRP, but includes two newly tracked wallets holding 512M XRP. That is a coverage change, not an inflow.

Largest attributed balances: Upbit 6.46B, Coinbase 5.80B, Binance 2.69B, Bithumb 1.81B, Uphold 1.69B, Kraken 982.3M, Gate 35.0M, Bitstamp 20.3M and SBI VC Trade 56.9M.

Regional distribution: South Korea 8.59B (38.4%), United States 8.48B (37.9%), Japan 1.38B (6.2%), global/offshore 2.73B and rest of world 1.16B.

The tracker reads rippled `account_info` from the latest validated ledger daily around 08:00 UTC and uses XRPSCAN public labels for attribution. It carries forward last-good values when reads fail. The total includes cold/omnibus custody, is a floor for publicly labeled wallets, and is **not tradable float**.

Approximately 481M XRP in the tracked set is identified as non-customer reserves/funds: 325.8M Binance-Peg backing, 150.1M Coinbase cbXRP backing and 5.2M insurance/charity. The Coinbase proof-of-reserves page separately displayed 152.372M XRP reserves. The approximately 2.27M difference is unresolved; wallet coverage, label scope and snapshot time may differ. Do not force a reconciliation.

Source: [XRP Insights exchange balances](https://xrp-insights.com/exchange-balances).

## 3. Independent large-transfer flow series

TrackWhale's November 10, 09:30 UTC snapshot reports, over its preceding seven days:

| Measure | XRP | USD |
|---|---:|---:|
| Inflows | 501.72M | $636.86M |
| Outflows | 608.96M | $767.62M |
| Netflow | **−107.24M** | **−$130.76M** |

The series covers 10 recorded inflow transfers and 15 outflow transfers. By venue, Binance accounts for −91.93M XRP, Kraken +14.99M, Gate −21.04M, Bitstamp +17.5M, Revolut −16.5M and OKX −10.27M.

The tracker excludes internal and exchange-to-exchange transfers, but only records large transfers; it is not every transfer or every exchange balance. It disclaims accuracy/completeness and may rely on third-party data.

A specific 40M XRP transfer from Binance to an unlabeled wallet occurred November 10 at 02:28 UTC, displayed value $43.76M. TrackWhale supplies transaction hash `C7388DFDF9DFD292E820FA8DBD3D033AFBAA0A207D16D06D7EEF8322FD78AD64` and truncated source/destination addresses. XRPSCAN direct explorer access returned HTTP 403, so independent raw transaction replay is outstanding. The transfer is an aggregator-classified exchange outflow, **not proof of a sale, customer withdrawal or intent**.

Source: [TrackWhale XRP exchange flows](https://trackwhale.io/xrp-exchange-flows).

## 4. Cross-source exchange-flow reconciliation

XRP Insights' all-attributed-wallet same-wallet balance series shows −8.9M XRP over seven days. TrackWhale's large external transfer series shows −107.24M XRP over seven days. Both indicate net outflow, but the magnitude differs by about 12x because the methods are not comparable:

- XRP Insights measures daily balance changes across a fixed set of attributed exchange wallets, including cold storage and omnibus custody.
- TrackWhale measures only recorded large external transfers, excluding internal and exchange-to-exchange movements.

Do not average them. Transfers to untracked wallets, custody reorganizations, institutional/OTC movements and customer withdrawals remain competing explanations. Neither series proves spot selling. The 40M Binance outflow is not attributed to the October 29 Binance hack; no causal evidence links the two.

## 5. Cyber/geopolitical event timeline

### Binance theft — October 29, 2026

The FBI's October 31 advisory attributes a theft of more than $6B in virtual assets from Binance on or about October 29 to North Korea-linked TraderTraitor activity. The FBI says it observed stolen assets being converted primarily into ETH and expects further laundering through DeFi and instant-swap services.

[Primary FBI advisory](https://www.fbi.gov/investigate/cyber/alerts/2026/north-korea-responsible-for-6-billion-binance-attack)

### Exchange withdrawals and stablecoin effects — November 2–3

Reuters reported $4.72B in net customer withdrawals after Binance reopened, approximately 3% of platform assets, with most withdrawals in USDT. Binance said $2.7B in inflows had followed reopening and that withdrawals were stabilizing. Binance said losses would be covered by company funds, treasury, insurance and reserves. Reuters also reported Circle had frozen more than $1.1B in USDC associated with the theft and cited Elliptic's estimate that hackers still controlled about $3.28B.

On November 3, Binance co-CEO Richard Teng said 95% of affected tokens had been replenished, hourly flows had normalized and the remaining 5% were less liquid; he said a post-mortem would follow. These are company statements reported by Reuters, not independently verified reserve attestations.

Sources:
- [Reuters, November 2](https://www.reuters.com/business/finance/binance-sees-outflows-stabilising-exchange-returns-online-after-63-billion-heist-2026-11-02/)
- [Reuters, November 3](https://www.reuters.com/world/asia-pacific/binance-co-ceo-says-company-is-very-strong-financial-health-after-63-billion-2026-11-03/)

Relevance: exchange counterparty risk, stablecoin liquidity, operational resilience and institutional risk appetite. Do not infer an XRP-specific causal effect from the Binance incident.

## 6. Macro event — November 10

Reuters reported at 09:12 UTC that Federal Reserve Governor Christopher Waller would support a 25-basis-point December rate increase even if October CPI cools, and said a 50-basis-point move should be considered if core CPI rises 0.3% or more month over month. Reuters reported approximately 85% market-implied odds of a 25bp December 8–9 hike as of Monday's close.

This is one governor's view and market pricing, not an FOMC decision or consensus. October 2026 CPI was scheduled for 13:30 UTC on November 10 and remained a future release at this capture.

[Reuters Waller report](https://www.reuters.com/business/feds-waller-plans-support-least-quarter-point-rate-hike-december-2026-11-10/)  
[BLS release schedule](https://www.bls.gov/schedule/2026/11_sched.htm)

## 7. Model admission and forecast status

The exchange series remain research-only because:
- same-wallet balances and large-transfer netflows measure different things;
- wallet labels and coverage can change;
- the 40M XRP transaction was not independently replayed from a raw XRPL response;
- raw transport bytes and independent timestamp receipts were not preserved in this capture;
- no sale, custody or customer-intent label is verified.

Forecast status: **NOT_ISSUED**. No directional forecast, paper trade or real-money action.

## 8. Repository, backlog and merge boundary

Main remains `d4d43be3427375cf79d190e768976de062e20287`. PR #1640 remains the sole V3/XRP integration path; it is open, non-draft and GitHub reports mergeable. No new branch or PR was created.

- #1643: 663 unique research paths; preserve.
- #1653: six unique knowledge-graph paths and eight unresolved review threads; preserve.
- #1642: seven changed paths overlap #1640; duplicate/superseded candidate only after verified merge.
- #1644–#1650: dependency/action overlaps; current integration already contains newer versions in active files; retain until verified on main.
- #1317/#1318/#1320: path-overlap candidates; semantic reconciliation still required.
- #1254/#1255: older dependency candidates.
- #1269: eight unique mesh/topology paths; preserve.
- #1611/#1614: preserve unique/partially overlapping prediction work.
- #1641/#1655/#1659: preserve unique material.

All 372 open PRs remain open; 356 drafts and 16 non-drafts. No source PRs were closed.

PR #1640 still has 62 COMMENTED review submissions and zero APPROVED reviews. The 22 inline threads are resolved but outdated. Main branch-protection detail access returns HTTP 403; the visible fallback ruleset is disabled. GitHub Pages is enabled and a main push previously triggered public deployment. The PR changes seven web assets and adds an hourly main-only XRP ingestion workflow; these automatic public and scheduled side effects remain part of the merge decision.

No merge, branch-protection bypass, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, force-push or destructive worktree operation occurred.

## 9. Next concrete actions

1. Complete exact-head CI, dependency audit and fail-closed verification on the Run126D documentation/research update.
2. Obtain independent approval, authoritative branch-protection visibility and explicit authorization for automatic Pages publication and scheduled ingestion activation.
3. Replay the 40M XRP transaction using an accessible public rippled endpoint or independent explorer.
4. Preserve the separate exchange-balance and large-transfer feature definitions; do not collapse them into one netflow.
5. Normalize Morpho/cbXRP and Coinbase cross-collateral data only after token decimals, block alignment, oracle timestamps and policy/version semantics are verified.
6. Expand synchronized historical spot/L2/derivatives/ETF/exchange-flow/collateral/macro-vintage data and independent receipt anchoring.
7. Continue leakage-safe out-of-sample evaluation and shadow outcomes; issue no forecast until readiness criteria pass.
8. After any authorized merge, fetch main, verify merge commit/files, run main CI, inspect automatic workflow side effects, and close only exact verified duplicates.

# Barrot XRP Mission — Run126C: exact-head verification and Coinbase collateral network

**Capture time:** `2026-11-10T09:44:51.310Z`  
**Main SHA:** `d4d43be3427375cf79d190e768976de062e20287`  
**Verified code/test head:** `483489f89c7e4a74c45c23e9b229b77565254ce1`  
**Integration branch:** `integration/core-capabilities-mmi-structural-paper-20261104`  
**Mission priority:** XRP intelligence and prediction-engine mastery.  
**Foundation:** Barrot V3 remains execution, orchestration, safety and verification.

## 1. Exact-head verification — VERIFIED

The Run126B correction fixed the final stale endpoint-count assertion. The full suite now passes on exact head `483489f89c7e4a74c45c23e9b229b77565254ce1`.

- Full repository suite: **1,368 passed, zero failed, eight subtests passed**.
- Inclusive package coverage: **59.58%**, above the 53% floor.
- Core suite: **677 passed**.
- Wheel build and installed-wheel verification passed.
- Installed package loads Barrot V3, the XRP primary mission and canonical data assets.
- Dependency audit: six manifests passed, zero known vulnerabilities.
- Fail-closed merge gate passed; automatic merging remains disabled.

Exact-head evidence:

- [Full CI — 42792815655](https://github.com/Barrot-Agent/B-Agent/actions/runs/42792815655)
- [Dependency audit — 42792815588](https://github.com/Barrot-Agent/B-Agent/actions/runs/42792815588)
- [Fail-closed gate — 42792815575](https://github.com/Barrot-Agent/B-Agent/actions/runs/42792815575)

The prior two full-suite failures were stale contract assertions: first in the Run124 market-evidence test, then in the primary-mission contract test. Both now assert the actual 46-record registry: 42 hourly scheduled sources, two weekly CFTC sources, and two excluded non-commercial XRPL nodes (44 scheduled, two excluded). The endpoint implementation itself was not failing.

Non-fatal packaging warnings remain for deprecated license metadata and package-discovery configuration. They did not prevent wheel installation or mission verification.

## 2. Repository and PR inventory

- Main SHA: `d4d43be3427375cf79d190e768976de062e20287`.
- PR #1640 head: `483489f89c7e4a74c45c23e9b229b77565254ce1`; 927 commits ahead, zero behind; 253 changed paths; open, non-draft and GitHub reports mergeable.
- Main tree: 1,404 entries / 1,299 blobs / 86 workflow files / 90 Python test files / 30 XRP research files.
- Integration tree after Run126B: 1,550 entries / 1,437 blobs / 87 workflow files / 149 Python test files / 82 XRP research files.
- Open PR inventory: 372 unique PRs, 356 drafts and 16 non-drafts.
- No new branch or PR was created. Main was not modified.

## 3. PR overlap reconciliation

Full file-list pagination confirms:

- #1643 has 670 changed paths: **663 unique to #1643 and seven shared** with #1640. Preserve its unique research archive; do not close it as duplicate.
- #1653 has seven changed paths: six unique repository-knowledge-graph paths and one shared CI path. Preserve the unique code/docs/tests and eight unresolved review threads.
- #1642 has seven changed paths, all overlapping #1640. It is a duplicate/superseded-content candidate only after the successor is merged and verified on main.
- #1644–#1650 are dependency/action update PRs whose changed paths overlap #1640. Current integration content already includes the newer checkout, upload/download artifact, pytest, types-requests, Databricks and Hugging Face versions in active files. Three workflows changed by #1644/#1647 (self-upgrade, IBM Bob audit, subagent matrix) are now quarantined with empty permissions and disabled jobs; their old checkout/artifact steps no longer execute. Keep these source PRs open until #1640 is merged and the resulting main files are verified.
- #1254/#1255 contain older dependency versions than the current integration branch; retain until verified on main.
- #1317/#1318/#1320 have path overlap with #1640, but do not close them until semantic/content reconciliation and verified successor merge.
- #1269: preserve eight unique mesh/topology paths.
- #1611/#1614: preserve unique or partially overlapping prediction work until exact contract reconciliation.
- #1641/#1655/#1659: preserve unique material.

No PRs were closed.

## 4. New Coinbase collateral network evidence

### Consumer XRP-backed USDC loans through Morpho

Coinbase's current Help Center identifies XRP as eligible collateral for its USDC crypto-backed loan product. Coinbase says borrowing is powered by Morpho on Base and the collateral is held onchain. Its product page states a maximum **$100,000 USDC loan against XRP** for eligible customers; the Help Center excludes New York for U.S. access and notes limited UK/Canada availability subject to regional eligibility.

Coinbase's backup collateral page maps native XRP to **cbXRP on Base**, contract `0xcb585250f852c6c6bf90434ab21a00f02833a4af`. This confirms the path:

`XRP held by customer → cbXRP representation on Base → Morpho collateral → USDC loan`.

The specific Morpho USDC/cbXRP market has a **62.5% LLTV**. Coinbase's generic loan page references 86% for the broader product, but that generic value must not be substituted for the XRP market's actual 62.5% immutable parameter.

Coinbase states that Morpho collateral can be liquidated automatically and Coinbase cannot prevent a protocol liquidation. Optional loan protection must be enabled per loan, requires available collateral and is not guaranteed. Morpho liquidation transfers cbXRP on Base; it does not prove a native XRP sale. A subsequent redemption or sale must be observed separately.

### Coinbase Global Derivatives cross-collateral

A separate Coinbase Global Derivatives policy lists XRP as an accepted cross-collateral currency for eligible customers in supported regions outside the United States. The policy applies from October 1, 2026 for most customers.

The published haircut table lists:
- X:PM: no XRP haircut shown.
- X:SM: **15% XRP haircut**.

The haircut is an initial-margin reserve, not a reduction in account margin balance. Coinbase also applies asset limits based on average daily quantity at the user-business-organization level; excess collateral above the limit does not contribute to portfolio value. The XRP-specific cap and actual utilization are not publicly disclosed.

This is distinct from consumer Morpho lending, Coinbase Custody, XRP spot holdings and Ripple/USDC settlement. It demonstrates collateral eligibility, not how much XRP is actually pledged.

### Historical margin offset

Coinbase's Global Exchange margin-offset table dated June 6, 2025 displayed a 0.93 offset between XRP-PERP and XRP-USDC spot. It is a historical, market-condition-dependent margin-offset weight, not a collateral haircut or current utilization figure.

The structured Run126C evidence artifact is `research/xrp_intelligence/20261110T094451Z-run126c-coinbase-collateral-channels-update.json`. These policy pages are not admitted as quantitative collateral-utilization features. The Morpho and Coinbase proof-of-reserves adapters remain raw-only until token decimals, market/block alignment, oracle timestamps, locale refresh timezone and cache semantics are normalized.

## 5. Current market and research conclusions carried forward

- Spot: Kraken $1.08144 XRP/USD and OKX 1.0812 XRP-USDT in asynchronous snapshots; no executable arbitrage inference.
- Spot depth: last multi-venue snapshot was 07:00 UTC and is stale relative to capture; displayed liquidity is cancellable.
- Derivatives: OI aggregators disagree by about 38%, both show declining OI and long-heavy liquidations with modest positive funding. Do not average.
- ETF flows: November 9 is partial. CryptoKeyhole component sum is −9,216,552 XRP while its displayed total is −9,216,553 XRP; preserve the one-XRP discrepancy. Alpha's −$10.4M and zero rows are not independently issuer-confirmed.
- Coinbase cbXRP reserves: 152,372,342.33 XRP versus 152,370,095.8 cbXRP supply on the issuer page; refresh timezone unresolved.
- Morpho Base market: $55.58M outstanding USDC, $23.54M liquidity, 88.23% utilization, 62.5% LLTV, 7.00% borrow and 6.14% lend rates; no displayed bad debt. Nov 6/8 liquidation stress estimates remain historical, not current.
- Exact phrase “SBIC, ChatGPT SBIC”: no exact match; Tokyo SBIC's official ChatGPT/Copilot course is training for investee companies, not an OpenAI partnership.
- Exact phrase “actual capital”: no standardized XRP metric or exact match in reviewed Evernorth filing. Keep cash, in-kind XRP, debt, contingent facilities, resales and warrants separate.
- ASK Coin remains ambiguous; no XRP integration verified.
- Dr. Kamilah Stevenson identity is supported, but the YouTube channel ID/handle relationship remains unverified. Ten candidate references remain candidate-only; verified personal-channel upload count remains zero.
- October 2026 CPI was scheduled for 13:30 UTC on November 10; no release result was observed at the prior capture cutoff.

## 6. Prediction-engine and platform status

The integration branch retains 46 endpoint records: 42 hourly scheduled, two weekly CFTC, two excluded non-commercial XRPL nodes. Morpho and Coinbase cbXRP proof-of-reserves endpoints are already registered, but their parsers are deliberately raw-only. The point-in-time store, four baselines, chronological purge/embargo evaluator, calibration/drift diagnostics and fail-closed forecast ledger are implemented on the integration branch.

Independent WORM/timestamp anchoring, synchronized historical market/collateral data, effective-sample-size correction, sufficient shadow outcomes and demonstrated out-of-sample lift remain incomplete.

Forecast status: **NOT_ISSUED**. No directional forecast, paper trade or real-money action.

Nine-platform status:
- ChatGPT: current-session GitHub read/write verified.
- Copilot: comment-only review activity; no approval.
- Claude, Grok, Gemini, Codex: unverified.
- Hugging Face: prior build error; no deployment.
- Kaggle: untested; no submission.
- Databricks: prior HTTP 403; no workspace write.
- No persistent authenticated cross-platform exchange or external-model data transfer.

## 7. Merge boundary

PR #1640 remains unmerged despite exact-head full-suite, dependency and fail-closed success.

- 62 review submissions remain COMMENTED; zero APPROVED.
- 22 inline review threads are resolved but outdated.
- CodeRabbit automatic review remains paused.
- Detailed main branch-protection access returns HTTP 403; the visible fallback ruleset is disabled.
- GitHub Pages has previously deployed automatically after a main push. PR #1640 changes public web assets; specific authorization for automatic publication remains unresolved.

The user's conditional merge authorization is not satisfied. No branch-protection bypass or merge was attempted.

## 8. Next actions

1. Obtain independent approval, authoritative branch-protection visibility and explicit authorization for automatic Pages publication.
2. Preserve unique research, knowledge-graph, mesh and prediction PRs; close only exact duplicates after verified successor merge.
3. Normalize Morpho and Coinbase collateral sources using token decimals, block-aligned state, oracle timestamps and issuer refresh/cache semantics.
4. Trace actual cbXRP redemptions and native XRP sales separately from Morpho liquidations.
5. Expand synchronized historical spot, L2, derivatives, exchange-flow, ETF, collateral and macro-vintage data; independently anchor raw receipts.
6. Require leakage-safe out-of-sample lift and sufficient independent shadow outcomes before any forecast issuance.
7. After any authorized merge, fetch main, verify merge commit and files, run main CI, inspect automatic workflow side effects, then close only exact verified duplicates.

No merge, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, force-push or destructive worktree operation occurred.

# Barrot XRP Mission — Run126B: second contract assertion repaired; fresh spot, ETF and cbXRP collateral evidence

**Capture time:** `2026-11-10T09:38:55.286Z`  
**Main SHA:** `d4d43be3427375cf79d190e768976de062e20287`  
**Integration branch:** `integration/core-capabilities-mmi-structural-paper-20261104`  
**Parent integration head:** `14a6d5bd0a2187cba4c0e9e71ce8aaaef2b4a880`  
**Mission:** XRP intelligence and prediction-engine mastery, priority one.  
**Foundation:** Preserve Barrot V3 as execution, orchestration, safety and verification.

## Repository and CI diagnosis

The first Run126 correction updated the feature-store contract and the Run124 market-evidence test. The next full-suite run exposed one remaining stale assertion in `tests/test_xrp_primary_mission_contract.py::test_feature_store_contract_endpoint_counts_match_registry`. It still expected “42 hourly endpoints” while the contract correctly says “42 hourly scheduled sources.” The Run124 regression test passed. This is a documentation-contract assertion, not a collector runtime failure.

On pre-correction head `14a6d5bd0a2187cba4c0e9e71ce8aaaef2b4a880`:

- Full suite: **1,367 passed, one failed, eight subtests passed**; coverage 59.58%.
- Core suite: 677 passed.
- Dependency audit: six manifests passed, zero known vulnerabilities.
- Fail-closed gate: passed; automatic merge remains disabled.

Exact evidence:
- [Full CI 42791775896](https://github.com/Barrot-Agent/B-Agent/actions/runs/42791775896) — one stale assertion described above.
- [Dependency audit 42791776039](https://github.com/Barrot-Agent/B-Agent/actions/runs/42791776039) — passed.
- [Fail-closed gate 42791775891](https://github.com/Barrot-Agent/B-Agent/actions/runs/42791775891) — passed.

The remaining assertion is corrected to require 46 total endpoint records, 42 hourly scheduled sources, two weekly CFTC sources, 44 scheduled sources total and two excluded non-commercial XRPL nodes. The correction commit must receive its own exact-head full-suite, dependency and fail-closed runs. No completion claim is made until they pass.

## Integrated repository snapshot

- PR #1640 is the sole V3/XRP integration path. It remains open and non-draft.
- The preceding head was 925 commits ahead of main, zero behind, with 252 changed paths.
- Open PR inventory: 372 unique PRs, 356 drafts and 16 non-drafts.
- Main tree: 1,404 entries / 1,299 blobs / 86 workflow files / 90 Python test files / 30 XRP research files.
- Integration tree: 1,549 entries / 1,436 blobs / 87 workflow files / 149 Python test files / 81 XRP research files before the Run126B artifact.
- No new branch or PR was created; main was not modified.

## Fresh market evidence

### Spot and depth

- Kraken XRP/USD: $1.08144; bid $1.08148; ask $1.08149; 24-hour volume 23.92M XRP; VWAP $1.09496; 24-hour high/low $1.11573/$1.07502; 24-hour open $1.09748. The displayed price is approximately 1.46% below the 24-hour open and 15.8% of the way up from the 24-hour low. Kraken supplied no provider event timestamp.
- OKX XRP-USDT: 1.0812; bid 1.0811; ask 1.0812; 24-hour volume 63.124M XRP; provider event time 09:15:26.275 UTC. Its displayed price is approximately 1.39% below the 24-hour open and 11.9% of the way up from the low.
- Kraken USDT/USD was 0.99865; mechanical normalized OKX reference approximately $1.07974. The venues and event times are not synchronized; this is not an executable arbitrage observation.
- Fuelmaps' 07:00 UTC six-venue spot-depth snapshot showed $12.4M bids/$10.0M asks within 1%, and $17.7M/$10.7M within 2%. It is over two hours old at capture and represents cancellable resting liquidity, not executed volume. No fresh synchronized raw L2 was admitted.

### Derivatives

- Liqwall 09:32 UTC: OI $1.19B, down 2.5% on its 24-hour display; $4.8M liquidations, of which $4.2M were longs; funding +0.0068% per eight hours.
- TradRadar 08:40 UTC: OI $1.64B, down 4.5%; at least $3.77M liquidations, $3.02M longs; funding +0.0060%.
- OI differs by approximately 38% across aggregators. The common observation is declining OI with long-heavy liquidations and modest positive funding. Venue coverage overlaps; do not average the figures.
- Competing hypotheses remain long-deleveraging continuation versus liquidation exhaustion/mean reversion. No directional forecast is justified.

### ETF flows — arithmetic and coverage correction

CryptoKeyhole's page updated 09:22 UTC reports a November 9 partial flow for three of four daily-collected funds:

- Bitwise: −8,594,551 XRP.
- Canary: −427,341 XRP.
- 21Shares: −194,660 XRP.
- Calculated component sum: **−9,216,552 XRP**.
- Page-displayed aggregate: **−9,216,553 XRP**, a one-XRP arithmetic discrepancy that is preserved, not silently corrected.
- Displayed USD partial: −$10.1M.

Franklin's 9 November file was published 23:47–23:52 UTC on 9 November, but its latest holdings row remained dated 6 November; it is not counted as a 9 November flow. Grayscale is quarterly-only in this tracker; REX-Osprey is excluded because its direct-only file does not represent indirect holdings.

Alpha Finance reports −$10.4M across five displayed funds but shows zeroes for Franklin and Grayscale that are not independently confirmed by current issuer daily files. The two trackers are not averaged. The latest complete day remains November 6: −752,048 XRP/−$887K across four of four daily-collected funds. The November 9 partial is excluded from the cumulative October 23–November 6 total.

### Coinbase cbXRP reserves and Morpho collateral

Coinbase's first-party proof-of-reserves page states cbXRP is backed 1:1 by XRP held by Coinbase. It displays 152,372,342.33 XRP reserves versus 152,370,095.8 cbXRP supply, a displayed surplus of 2,246.53 XRP. The page's refresh label is 8:54 AM on November 10, timezone unspecified. This is reserve/supply evidence, not customer deposits or tradable float.

The Morpho Base USDC/cbXRP market page for market `0xd4a903…4109` displays:

- 62.5% liquidation LTV.
- $55.58M outstanding USDC debt.
- $23.54M liquidity.
- 88.23% utilization.
- 7.00% borrow rate and 6.14% lend rate.
- Zero displayed realized and unrealized bad debt.
- Latest visible activity at 08:43 UTC, including repayments, withdrawals, lending and collateral supply.

The Nov 6 CryptoSlate stress snapshot estimated $8.8448M debt across 1,070 positions within a further 10% oracle decline; $3.2296M across 462 positions within 5%. The Nov 8 Catenaa snapshot estimated $8.4M debt across 920 loans within 10%, and reported 384 liquidations on Nov 6–7, $1.6M debt repaid and 1.53M cbXRP seized, with no bad debt reported. These are dated, fixed-position stress estimates and secondary analyses, not current liquidation buckets.

Morpho liquidations transfer cbXRP on Base. Native XRP sales are not automatic; they require subsequent redemption or sale evidence. The current collector already registers five Morpho endpoints and Coinbase's cbXRP proof-of-reserves endpoint, but their parsers deliberately remain raw-only. Do not promote them until token decimals, unit scaling, block/indexer alignment, oracle time semantics, page locale/timezone and cache freshness are normalized.

## Identity and exact-phrase audit

- Japan's SBIC East/Central/West remain the distinct Tokyo/Nagoya/Osaka regional investment-consultation companies, not SBI Holdings. Tokyo SBIC's official training course includes ChatGPT and Copilot instruction for investee companies; it is not an OpenAI partnership.
- Exact phrase “SBIC, ChatGPT SBIC”: no exact match found.
- Exact phrase “actual capital”: no standardized XRP metric or exact match in the reviewed Evernorth prospectus. Keep cash received, in-kind XRP, XRP purchased with cash, delayed funding, debt, contingent equity capacity, secondary resales and warrants separate.
- “ASK Coin” remains ambiguous between Permission Coin ASK and an inactive Ask Coin exchange; no XRP integration verified.
- Dr. Kamilah Stevenson person identity is supported by her branded site. A Linktree profile links to YouTube handle `@drkamilahstevenson`, but the canonical channel ID/handle relation remains unverified by first-party YouTube metadata or a reciprocal official-site link. Multiple lookalike channels exist. Keep all ten repository video references candidate-only; verified personal-channel inventory remains zero. Do not ingest or attribute candidate videos as creator uploads.
- October 2026 U.S. CPI was scheduled for 13:30 UTC on November 10 and had not been released at capture.

## Source and model admission

The structured Run126B evidence artifact is `research/xrp_intelligence/20261110T093855Z-run126b-spot-etf-cbxrp-morpho-identity-update.json`.

Web-rendered observations were not preserved as original HTTP transport bytes with independently anchored SHA-256 receipts. The artifact records provider timestamps where supplied, retrieval/capture limitations, source class and disagreements. These observations are research-only and not admitted to the feature store.

Forecast status: **NOT_ISSUED**. No directional forecast, paper trade or real-money action.

## Review, backlog and merge boundary

- PR #1640: sole active integration path; blocked.
- 62 review submissions remain COMMENTED; zero APPROVED.
- 22 inline threads are resolved but outdated.
- CodeRabbit's automatic review is paused.
- Main branch-protection detail endpoint returns HTTP 403; the visible fallback ruleset is disabled.
- GitHub Pages previously deployed automatically after a main push. The PR changes public web assets; specific authorization for automatic publication remains unresolved.
- #1643: preserve unique research archive.
- #1653: preserve unique knowledge graph and unresolved review threads.
- #1642: seven changed paths all overlap #1640; retain until successor is merged and verified on main.
- #1644–#1650: dependency/action path-overlap candidates; reconcile exact versions before closure.
- #1317/#1318/#1320: structural/schema/paper-trader overlap candidates.
- #1254/#1255: dependency candidates.
- #1269: preserve unique mesh/topology work.
- #1611/#1614: preserve unique or partially overlapping prediction contracts until exact reconciliation.
- #1641/#1655/#1659: preserve unique material.

No PRs were closed. No merge, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, force-push or destructive worktree operation occurred.

## Next concrete actions

1. Complete full-suite CI, dependency audit and fail-closed verification on the new Run126B correction head.
2. Preserve Morpho and Coinbase sources as raw-only until their timestamp/unit contracts are proven.
3. Reconcile the one-XRP CryptoKeyhole aggregate arithmetic discrepancy and the Canary/Alpha flow-method disagreement.
4. Obtain independent PR approval, effective branch-protection visibility and explicit Pages publication authorization.
5. Continue synchronized historical spot/depth/derivatives/ETF/collateral ingestion and independent receipt anchoring.
6. Require leakage-safe out-of-sample lift and sufficient independent shadow outcomes before any forecast issuance.
7. After any authorized merge, fetch main, verify merge commit and files, run main CI, inspect automatic workflow side effects, and close only exact verified duplicates.

# Barrot XRP Mission — Run126: source-registry count correction and exact-head CI repair

**Capture cutoff:** 2026-11-10T09:30:00Z.  
**Mission priority:** XRP intelligence and prediction-engine mastery.  
**Foundation:** Barrot V3 remains the execution, orchestration, safety and verification foundation.

## Repository snapshot

- Repository: `Barrot-Agent/B-Agent`
- Main SHA: `d4d43be3427375cf79d190e768976de062e20287`
- Integration branch: `integration/core-capabilities-mmi-structural-paper-20261104`
- Inspected integration head before this correction: `f7cc3791ad19adefac9de791b8274aba854a06ea`
- PR #1640: open, non-draft, GitHub reports mergeable; 925 commits ahead, zero behind; 252 changed paths.
- Full open-PR inventory: 372 unique PRs, 356 drafts and 16 non-drafts.
- Main tree: 1,404 entries / 1,299 blobs / 86 workflow files / 90 Python test files / 30 XRP research files.
- Integration tree: 1,549 entries / 1,436 blobs / 87 workflow files / 149 Python test files / 81 XRP research files.
- No new branch or PR created. Main was not modified.

## Exact-head CI diagnosis

On pre-correction head `f7cc3791ad19adefac9de791b8274aba854a06ea`:

- Core test job passed.
- Dependency audit passed.
- Fail-closed gate passed and kept automatic merging disabled.
- Full repository suite failed: **1,367 passed, 1 failed, 8 subtests passed**; coverage 59.58%.
- The sole failure was `tests/test_xrp_run124_market_evidence.py::test_run124_feature_store_contract_counts_weekly_cftc_sources`.

The failure was a stale test/documentation mismatch, not a runtime ingestion or prediction failure. The current endpoint registry contains 46 records: 42 hourly scheduled sources, two weekly CFTC sources, and two non-commercial XRPL public-node sources excluded by default. Therefore 44 sources are scheduled (42 hourly plus two weekly), and two are excluded. The test still expected the old 40-record / 36-hourly / 38-scheduled description.

## Executed correction

- Updated the feature-store contract's opening and historical endpoint-count statements to the current 46 / 42 / 2 / 2 inventory and 44 scheduled / 2 excluded split.
- Updated the Run124 regression test to assert the current count and explicitly reject the obsolete 40 / 36 wording.
- Preserved the historical Run124 artifact and all prior handoff sections.
- No market data was fabricated or admitted into the model.

## Exact-head verification boundary

The following runs belong to pre-correction head `f7cc3791ad19adefac9de791b8274aba854a06ea` and must not be represented as verification of the correction commit:

- Full CI: https://github.com/Barrot-Agent/B-Agent/actions/runs/42789782020 — failed only on the stale count assertion above.
- Dependency audit: https://github.com/Barrot-Agent/B-Agent/actions/runs/42789781625 — passed.
- Fail-closed gate: https://github.com/Barrot-Agent/B-Agent/actions/runs/42789781552 — passed.

The correction commit must receive its own full-suite CI, dependency audit and fail-closed gate. Exact-head verification is pending until those runs complete.

## Review, branch protection and publication boundary

- PR #1640 has 62 review submissions, all COMMENTED; zero APPROVED reviews.
- All 22 inline review threads are resolved, but their review state predates the latest changes.
- CodeRabbit has paused automatic review; its last reviewed commit is `ee280ed1d989f90dcc92f9ee3e8659377ef57dbc`, while `f7cc3791ad19adefac9de791b8274aba854a06ea` was unreviewed.
- Main branch-protection endpoint returned HTTP 403.
- The only visible repository ruleset is `10863829` ("Fall Back"), enforcement disabled.
- GitHub Pages has previously deployed automatically following a main push. PR #1640 changes public web assets; authorization for that automatic publication remains unresolved.
- Do not merge, bypass protection or deploy while these conditions remain unresolved.

## Integrated architecture and implemented state

On the integration branch, the XRP workstream includes the 46-record public endpoint inventory, 42 hourly scheduled sources, two conditional weekly CFTC sources, two excluded non-commercial XRPL nodes, raw-source receipt/hash logic, point-in-time SQLite feature store, four deterministic baselines, chronological walk-forward evaluation with purge/embargo, calibration and drift diagnostics, and a fail-closed forecast ledger requiring trusted evaluator attestation.

The primary mission manifests and `.github/workflows/xrp-public-ingestion.yml` remain on the integration branch, not main. No scheduled ingestion has been verified on main. SQLite mutation guards and 90-day Actions artifacts are not independent WORM storage or trusted external timestamp anchoring. Synchronized historical market, depth, exchange-flow, derivatives and collateral coverage remains incomplete.

## Backlog classification

- #1640: sole active V3/XRP integration path; blocked on exact-head CI, independent approval, effective branch-protection visibility and Pages publication authorization.
- #1643: unique XRP research archive; preserve its unique paths.
- #1653: unique repository knowledge graph; preserve its unique paths and unresolved review threads.
- #1642: forecast-snapshot work is integrated/overlapping; retain until #1640 is merged and content verified on main.
- #1644–#1650: dependency/action update candidates; reconcile exact versions and workflow diffs before classifying as superseded.
- #1317/#1318/#1320: structural, schema and paper-trader overlap candidates; do not close before verified successor merge.
- #1254/#1255: older dependency candidates; compare against current requirements before classifying.
- #1269: unique mesh/topology work; preserve.
- #1614/#1611: unique or partially overlapping prediction contracts; preserve until exact path/commit reconciliation.
- #1655/#1659/#1641: preserve unique structural, local-inference and autonomous-experimentation material.

No PRs were closed. No merge or external action occurred.

## Forecast and platform status

- Forecast status: **NOT_ISSUED**. No directional forecast, paper trade or real-money action.
- ChatGPT current-session GitHub read/write is verified.
- Copilot activity is comment-only; it is not an approval or a verified independent data flow.
- Claude, Grok, Gemini and Codex remain unverified.
- Hugging Face has prior build failure evidence; no deployment.
- Kaggle remains untested; no submission.
- Databricks previously returned HTTP 403; no workspace write.
- No persistent authenticated nine-platform exchange or external-model data transfer is verified.

## Next concrete actions

1. Complete full-suite CI, dependency audit and fail-closed gate on the correction head.
2. Reconcile the full open-PR overlap matrix and preserve unique research/graph/mesh work.
3. Obtain independent approval and authoritative branch-protection visibility.
4. Resolve automatic GitHub Pages publication authorization.
5. Expand synchronized historical XRP spot/depth/derivatives/flows/collateral data and independent raw-source anchoring.
6. Continue leakage-safe out-of-sample and shadow evaluation; issue no directional forecast until the readiness gate is genuinely met.
7. After any authorized merge, fetch main again, verify the merge commit and files, run main CI, inspect workflow side effects, then close only exact verified duplicates.

---

# Barrot XRP Mission — Run125C: Coinbase cbXRP reserves and Morpho collateral channel

**Capture cutoff: 2026-11-10T08:50:00Z.** This is a research/handoff-only update on the existing integration branch. The preceding code/test head was ab70744f0ef0073f52933ff9908e8cec4204f5b8.

## Exact-head verification

The preceding head passed exact-head CI: **1,355 passed, zero failed, eight subtests passed; 59.48% inclusive coverage; 677 core tests passed**. The installed wheel verified Barrot V3 and the XRP mission. Six dependency manifests passed strict pip-audit with no known vulnerabilities. The fail-closed gate passed and automatic merge remains disabled.

Evidence: [Full CI 42785230391](https://github.com/Barrot-Agent/B-Agent/actions/runs/42785230391), [Dependency audit 42785230472](https://github.com/Barrot-Agent/B-Agent/actions/runs/42785230472), [Fail-closed gate 42785230083](https://github.com/Barrot-Agent/B-Agent/actions/runs/42785230083).

## Coinbase primary proof-of-reserves: cbXRP

Coinbase’s official cbXRP proof-of-reserves page explicitly states that cbXRP is backed 1:1 by XRP held by Coinbase. The public locale pages show these observations:

| Locale page | Displayed refresh | XRP reserve | cbXRP supply | Excess reserve |
|---|---|---:|---:|---:|
| en-US | Nov 10, 02:04 AM | 151,921,083.53 | 151,918,836.99 | 2,246.54 |
| en-GB | Nov 10, 04:44 AM | 152,372,342.33 | 152,370,095.80 | 2,246.53 |
| en-ES | Nov 10, 06:34 AM | 152,372,342.33 | 152,370,095.80 | 2,246.53 |

The reserve surplus is approximately 2,246.5 XRP in each snapshot, consistent with 1:1 backing. The locale pages expose different cached snapshots and local refresh labels; do not infer chronological growth until timezone and cache semantics are normalized. The 152M cbXRP reserve attributed by XRP Insights is now independently corroborated by Coinbase primary pages.

Source: [Coinbase cbXRP proof of reserves](https://www.coinbase.com/cbxrp/proof-of-reserves).

## Morpho cbXRP/USDC collateral channel

Morpho’s public market page and REST market-parameter endpoint identify a Base market with USDC as the loan asset, cbXRP as collateral and a fixed **62.5% LLTV**. The immutable market configuration is:

- Market ID: 0xd4a903dc6d949519060c7707f9604fdc9772c046e05c2e3a8fce0bd7196e4109.
- Loan token: USDC, contract 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913.
- Collateral token: cbXRP, contract 0xcb585250f852C6c6bf90434AB21A00f02833a4af.
- Oracle: 0x031b2EFC8d70042Ac8d9f5c793c4149eC4b60fdE.
- Creation block: 40,855,874.

Primary sources: [Morpho market](https://app.morpho.org/base/variable/0xd4a903dc6d949519060c7707f9604fdc9772c046e05c2e3a8fce0bd7196e4109/usdc-cbxrp), [Morpho market parameters API](https://api.morpho.org/v0/blue/markets/8453:0xd4a903dc6d949519060c7707f9604fdc9772c046e05c2e3a8fce0bd7196e4109), [Morpho REST documentation](https://docs.morpho.org/developers/api/morpho/).

Morpho’s public REST API exposes immutable market parameters, total supply/borrow assets and shares, fee, oracle quote and historical market state/APY. It does not expose aggregate collateral totals or a market-wide borrower-health list through the documented REST routes. GraphQL remains served for existing integrations. This is a concrete gap in the current 40-source XRP registry: neither Morpho nor Coinbase cbXRP proof-of-reserves is currently registered.

### Liquidation-risk observations

Catenaa’s November 8 02:21 UTC scan reports $58.3M USDC debt against 120.6M cbXRP collateral, $66.3M supplied USDC, $8.1M withdrawable liquidity, 88% utilization, 6.1% supplier APY and 7.0% borrower APY. It estimates $8.4M debt at risk under a further 10% XRP price decline. It reports 384 liquidations on November 6–7, $1.6M repaid and 1.53M cbXRP seized; 3,713 liquidations since February and no reported bad debt.

CryptoSlate’s November 6 13:24:54 UTC snapshot separately reports $8.8448M debt across 1,070 positions within a further 10% oracle decline, and $3.2296M across 462 positions within 5%. The 5% set is included within the 10% set; do not add them. These are secondary analyses of public Morpho data, not independent issuer attestations.

Sources: [Catenaa](https://catenaa.com/markets/cryptocurrencies/cbxrp-loans-morpho-liquidation-risk/), [CryptoSlate](https://cryptoslate.com/morpho-loan-stress-exposes-cbxrp-but-spares-native-xrp/).

Coinbase’s published product terms match the market’s 62.5% LLTV and a 49% maximum initial LTV. That supports the inference that the market serves Coinbase’s cbXRP-backed borrowing product, but Morpho is permissionless and the market itself does not identify Coinbase as the originator. Treat the relationship as strongly supported inference, not a market-level primary label.

Using 120.6M cbXRP collateral from the November 8 secondary snapshot against the later 152.370M Coinbase supply gives an indicative 79.15% concentration. The timestamps differ, so this is not a synchronized market-share measure.

**Market interpretation:** liquidations first seize cbXRP on Base. They do not automatically create native XRP spot selling. A native XRP effect requires redemption or another transfer from wrapped collateral into native XRP markets; no such sale is inferred. This collateral channel should be tracked separately from XRP spot exchange flows.

## Integration and next action

PR #1640 remains the single V3/XRP integration path. The code/test head above passed. This Run125C commit adds only the handoff and a research artifact; its own workflow checks will be inspected before any merge consideration.

Next engineering action: add the public Morpho market-parameter, market-state, oracle-state and history endpoints, plus Coinbase cbXRP proof-of-reserves, to the existing source registry with distinct provider event/retrieval times, cache-age rules and fixture tests. Do not claim aggregate borrower-health coverage from the REST API; evaluate the documented GraphQL/position path separately. Keep wrapped-collateral liquidations separate from native XRP sales.

PR #1640 remains blocked by zero approving reviews, inaccessible effective branch-protection requirements and unresolved GitHub Pages publication authorization. No merge, deployment, external-model transfer, paper trade or real-money action occurred. **Forecast status: NOT_ISSUED.**

---

# Barrot XRP Mission — Run125B: ETF arithmetic and exchange-reserve correction

**Capture cutoff: 2026-11-10T08:46:00Z.** This correction preserves the Run125 and Run125A records and supersedes their inaccurate arithmetic/date descriptions.

## Exact-head verification

The preceding code/test head 59aa9026d99f5a5a2712022cff3114d33daec594 passed exact-head CI: **1,355 passed, zero failed, eight subtests passed; 59.48% inclusive coverage; 677 core tests passed**. Six dependency manifests passed strict pip-audit with no known vulnerabilities. The fail-closed gate passed and keeps automatic merge disabled.

Evidence: [Full CI 42784659000](https://github.com/Barrot-Agent/B-Agent/actions/runs/42784659000), [Dependency audit 42784659072](https://github.com/Barrot-Agent/B-Agent/actions/runs/42784659072), [Fail-closed gate 42784659233](https://github.com/Barrot-Agent/B-Agent/actions/runs/42784659233).

## ETF arithmetic correction

CryptoKeyhole shows three November 9 XRP holdings changes: Bitwise −8,594,551 XRP, Canary XRPC −427,341 XRP and 21Shares TOXR −194,660 XRP. Their arithmetic sum is **−9,216,552 XRP**, not −9,216,553. The page says 3 of 4 daily-reporting funds had published; Franklin XRPZ is missing for November 9.

The page states it checks NAV × shares against net assets within 0.05% plus rounding. Its rendered summary does not satisfy that rule for two funds:

| Fund | Displayed net assets | NAV × shares | Difference |
|---|---:|---:|---:|
| Bitwise | $444.7M | $478.676M | +7.64% |
| Canary XRPC | $265.2M | $285.657M | +7.71% |
| Franklin XRPZ | $339.5M | $339.654M | +0.045% |
| 21Shares TOXR | $117.1M | $117.249M | +0.127% |

The holdings divided by shares still approximately match the displayed XRP-per-share values for Bitwise and Canary. The NAV/AUM fields do not consistently reconcile. Raw issuer files were not independently fetched in this run. Treat holdings changes as provisional secondary issuer-file extractions; quarantine NAV/AUM fields and model-admit no ETF data until raw files are obtained.

Source: [CryptoKeyhole ETF flow and holdings table](https://cryptokeyhole.com/etf-flows/xrp/).

### Canary source conflicts

The official Canary XRPC page publishes its visible daily table only through November 6, with $286.859M net assets, 22.99M shares and $12.48 NAV. It does not independently confirm November 9 holdings.

CorpStacking displays 242,962,753.64 XRP as of November 9, but its own page says the last tracked event is “Awaiting first filing”; its balance-history table ends November 7 at 243,714,802.03 XRP. The difference is 752,048.39 XRP. This is an internal date/balance inconsistency, not a verified November 9 issuer balance. This corrects Run125A wording that described the last-tracked-event field as November 7.

Coin365 reports 140,376,744 XRP, $153.3M AUM, $11.57 NAV, 22.99M shares and 6.105991 XRP per share. Shares × NAV equals $265.994M, not $153.3M. NAV divided by the Kraken spot price at capture implies about 10.635 XRP per share, not 6.106. Its 100% category share is based on one tracked fund. Quarantine the dashboard.

Sources: [Canary official XRPC page](https://canaryetfs.com/xrpc/), [CorpStacking XRPC page](https://www.corpstacking.com/treasuries/canary-xrp-etf), [Coin365 XRPC dashboard](https://www.coin365.io/etf/xrp/xrpc).

Alpha Finance's −$10.4M 5/5 flow-series remains a separate observation with zero-filled Franklin and Grayscale rows; it is not reconciled to issuer-file holdings. No ETF dashboard total is model-admitted.

## Exchange-wallet reserve correction

XRP Insights' November 9 ledger snapshot attributes 22.35B XRP to 701 wallets across 24 exchanges. It includes **483.0M XRP that are not customer deposits**: 325.8M Binance-Peg XRP reserves on BNB Chain, 152.0M cbXRP reserves on Base and 5.2M insurance/charity funds.

Removing those known reserves leaves 21.867B XRP, but this is still not customer deposits or tradable float because cold, omnibus and institutional custody balances remain. The same-wallet change is −25.8M over seven days and −138.1M over 30 days, while the daily same-wallet change on November 9 was **+9.7M** and November 8 was +18.0M. A naive +373.9M total change includes two newly tracked wallets holding 512M XRP and is not a valid inflow.

The tracker identifies about 323M XRP in XRPSCAN-labeled wallets of roughly 36 exchanges outside its list from a September 29 audit. Main wallets for OKX, Coins.ph and Korbit are coverage gaps. Balances are read directly from rippled account_info; exchange attribution uses XRPSCAN public labels.

Source: [XRP Insights exchange balances and methodology](https://xrp-insights.com/exchange-balances).

## Integration and forecast status

PR #1640 remains the sole V3/XRP integration path. #1642's seven paths and all seven added tests are represented in #1640, with 19 additional readiness/receipt/embargo tests. #1644–#1650's dependency/action bumps are present in #1640. Keep these source PRs open until #1640 is merged and verified on main; then close only exact superseded changes. Preserve #1643's unique research archive, #1653's unique graph, and unique prediction/security/market/topology work.

PR #1640 has 62 COMMENTED reviews and zero approvals; 22 inline threads are resolved but outdated. Main branch-protection details return HTTP 403; fallback ruleset 10863829 is disabled. A previous main push triggered GitHub Pages publication, and #1640 changes public web assets. Automatic publication authorization remains unresolved. Do not merge or bypass protection.

The XRP mission manifest and scheduled ingestion workflow remain absent from main. The integration branch contains the 40-source registry, read-only main-only ingestion workflow, raw receipt logic, point-in-time store, four baselines, walk-forward evaluator, calibration/drift diagnostics and fail-closed forecast ledger. Independent WORM/timestamp anchoring, synchronized historical market data, effective-sample-size correction and sufficient shadow outcomes remain outstanding.

**Forecast status: NOT_ISSUED.** No paper trade, real-money action or external-model data exchange occurred.

---

# Barrot XRP Mission — Run125A: ETF source-quality and exchange-reserve correction

**Capture cutoff: 2026-11-10T08:39:00Z.** This is a documentation/research correction on the existing integration branch. The code/test head immediately before this update was 58589d163c7d9a15c0f7a9f14e2b46e93a207b0a. Its exact-head full suite, dependency audit and fail-closed gate all passed.

## Exact-head verification on the preceding code/test head

- Full repository suite: **1,355 passed, zero failed, eight subtests passed**; inclusive coverage **59.48%**; 32 fully covered files skipped.
- Core suite: **677 passed, eight subtests passed**.
- Wheel build/install and packaged Barrot V3/XRP mission verification passed.
- Six dependency manifests passed strict pip-audit; **no known vulnerabilities** were found in any manifest.
- Fail-closed merge gate passed; automatic merge remains disabled.
- [Full CI 42783870195](https://github.com/Barrot-Agent/B-Agent/actions/runs/42783870195), [Dependency audit 42783870369](https://github.com/Barrot-Agent/B-Agent/actions/runs/42783870369), [Fail-closed gate 42783869910](https://github.com/Barrot-Agent/B-Agent/actions/runs/42783869910).
- The cache budget remains read-only; this produced a non-failing cache-save warning.

## Exchange-balance correction: 483M XRP are known non-customer reserves

XRP Insights’ November 9 08:01 UTC ledger snapshot attributes **22.35B XRP** to 701 wallets across 24 exchanges. The tracker explicitly includes **483.0M XRP that are reserves or funds, not customer deposits**:

- Binance-Peg XRP reserve on BNB Chain: **325.8M XRP**.
- cbXRP reserve on Base held in Coinbase wallets: **152.0M XRP**.
- Exchange insurance and charity funds: **5.2M XRP**.
- Mechanical remainder after removing those known reserves: **21.867B XRP**. This is still not customer deposits or tradable float; other cold, omnibus and institutional custody balances remain.

Other key corrections:
- Same-wallet change is **−25.8M XRP over seven days** and **−138.1M over 30 days**, but the daily same-wallet change on November 9 was **+9.7M XRP** and November 8 was +18.0M. Do not describe every daily observation as an outflow.
- A naive total-balance comparison shows +373.9M XRP because two newly tracked wallets added 512.0M. The tracker excludes those new wallets from same-wallet change.
- The source identifies coverage gaps: an earlier September 29 audit found about 323M XRP in XRPSCAN-labeled wallets of roughly 36 exchanges outside its list; the main wallets for OKX, Coins.ph and Korbit are not in the tracked set.
- Balances are read directly from rippled account_info; exchange attribution uses XRPSCAN public labels. This is a ledger-balance tracker, not an independent third-party exchange reserve attestation.
- The 22.35B total includes cold/omnibus custody and known wrapped reserves. It is a floor for the tracked public labels, not tradable float.

Source: [XRP Insights exchange-balance methodology and snapshot](https://xrp-insights.com/exchange-balances).

## ETF source-quality correction: use file date, publication time and issuer page as-of date separately

### Canary XRPC

CryptoKeyhole’s issuer-file tracker reports **242,535,412 XRP** for November 9, with 22.88M shares, 10.6003 XRP per share, approximately $265.2M AUM and $12.485 NAV. It reports a November 9 change of **−427,341 XRP**. Its Canary file was observed on November 10 between **05:22 and 05:27 UTC**. The tracker says it checks coins against shares × XRP/share and NAV × shares against net assets, within 0.05% plus rounding. It has not yet obtained an overlapping quarter-end SEC filing for this new daily series.

Canary’s own product page is still dated **November 6**: $286.859M net assets, 22.99M shares and $12.48 NAV. Its published daily table ends November 6. It cannot independently confirm a November 9 holdings figure.

CorpStacking displays **242,962,753.64 XRP as of November 9**, but its last tracked balance event is November 7 and the sponsor page it cites is still dated November 6. Its number is 427,341 XRP above CryptoKeyhole’s newer issuer-file extraction, exactly the latter’s reported November 9 change. Classify CorpStacking’s Nov9 label as likely stale/misdated, not a competing primary observation.

Coin365’s XRPC page reports only **140,376,744 XRP**, $153.3M AUM and 100% category share. This is inconsistent with the newer issuer-file extraction and the other fund series. Quarantine this dashboard until its underlying contract/asset identity and source mapping are resolved; do not use its holdings or flows.

Alpha Finance continues to report −$10.4M across five flow-series tickers, assigning zero to Franklin and Grayscale. It is not reconciled to issuer-file holdings. Keep it as a separate dashboard observation; do not average it with CryptoKeyhole or treat zero as a missing issuer file.

Sources: [CryptoKeyhole issuer-file timestamps and reconciliation method](https://cryptokeyhole.com/etf-flows/xrp/), [Canary official XRPC page](https://canaryetfs.com/xrpc/), [CorpStacking XRPC page](https://www.corpstacking.com/treasuries/canary-xrp-etf), [Coin365 XRPC dashboard](https://www.coin365.io/etf/xrp/xrpc), [Alpha Finance ETF series](https://alphafinance.io/etf/xrp/).

## Latest spot refresh

- Kraken XRP/USD retrieval at 08:39 UTC: **$1.08787**, bid/ask **$1.08772/$1.08773**, 24-hour volume **23.638M XRP**, VWAP **$1.09530**, high/low **$1.11573/$1.07502**. Kraken supplies no provider event timestamp.
- OKX remains at 1.0920 USDT with provider event time 08:14:39.071 UTC; it was about 24 minutes old at this capture. Kraken USDT/USD was 0.99872.
- The 08:00 Fuelmaps six-venue spot book remains the latest readable snapshot: $12.7M bids and $10.1M asks within 1%, 55.6% bid share. It is now 39 minutes old. Resting orders can be cancelled; no forecast follows.
- Liqwall’s 08:22 snapshot remains $1.21B OI, down 3.3% over 24 hours; $3.6M liquidations, 82% long; average funding +0.0034% per eight hours. It is 17 minutes old at this capture.

No synchronized venue comparison or directional forecast is justified. The BLS October CPI release remains scheduled for November 10 at 13:30 UTC; it was not released at this capture.

## Integration and backlog reconciliation

PR #1640 remains the single V3/XRP integration path. Exact-head code verification passed on the preceding head. This correction changes only the durable handoff and research JSON; the resulting documentation-only commit will receive its own CI checks.

New exact-content reconciliation:
- **#1642 is fully superseded by #1640’s current branch content.** All seven paths are present. The exact verified-snapshot lookup, injected feature-store receipt clock, forecast-ledger cross-store preflight, source-lineage match and cutoff/receipt-time checks are implemented. Every one of #1642’s seven added tests is present in #1640; #1640 adds 19 additional readiness, receipt-integrity, source-independence and embargo tests. Keep #1642 open until #1640 is merged and verified on main; then close it with an explicit cross-reference.
- **#1644–#1650 dependency/action bumps are present in #1640.** The integration branch contains checkout@v7, download-artifact@v8, upload-artifact@v7, pytest>=9.2.0, types-requests>=2.33.0.20261030, databricks-sdk>=0.158.0 and huggingface_hub>=2.4.0. Several source PR files are byte-identical; others contain the same bump plus further integration changes. Keep the source PRs open until the successor is merged and verified on main; then close only the exact superseded bumps.
- #1643: preserve 663 unique research paths; stale/unmergeable.
- #1653: preserve six unique knowledge-graph paths; eight unresolved review threads.
- #1614/#1611: preserve unique prediction-validator and contract research pending integrated review.
- #1615/#1610: preserve security-containment work.
- #1605/#1597/#1269/#1655/#1659/#1641: preserve unique market, institutional, topology, structural, local-LLM and bounded-experimentation work.

No PRs were closed.

## Merge decision and prediction status

PR #1640 still has 62 COMMENTED reviews and **zero APPROVED reviews**. Its 22 inline review threads are resolved but outdated. Main branch-protection details return HTTP 403; visible fallback ruleset 10863829 is disabled. A previous main push triggered GitHub Pages publication, and #1640 changes seven public web assets. Automatic publication authorization is unresolved. **Do not merge or bypass protection.**

The XRP mission manifest and scheduled public-ingestion workflow are still absent from main; ingestion is not active on main. The integration branch has the 40-source registry, read-only main-only workflow, raw-receipt logic, point-in-time store, four baselines, walk-forward evaluator, calibration/drift diagnostics and fail-closed forecast ledger. The store is not yet populated with a synchronized historical XRP dataset. Independent WORM/timestamp anchoring, effective-sample-size correction and sufficient independent shadow outcomes remain outstanding.

**Forecast status: NOT_ISSUED.** No paper trade or real-money action occurred. No external-model data exchange occurred.

No merge, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, force-push or destructive worktree operation occurred.

---

# Barrot XRP Mission — Run125: live spot, six-venue depth, derivatives, ETF and integration reconciliation

**Capture cutoff: 2026-11-10T08:26:55Z.** XRP intelligence and prediction-engine mastery remain priority one. Barrot V3 remains the execution, orchestration, safety and verification foundation.

## Repository state and exact-head verification

- Main SHA: d4d43be3427375cf79d190e768976de062e20287.
- Existing integration PR: [#1640](https://github.com/Barrot-Agent/B-Agent/pull/1640), branch integration/core-capabilities-mmi-structural-paper-20261104.
- Current integration head: a8bf9f4a717cfb5a0407bb6c0028426aa012a106; 916 commits ahead, zero behind; 248 changed paths (+119,742/−3,554).
- Main tree: 1,404 entries / 1,299 files. Integration tree: 1,545 entries / 1,432 files.
- Complete open inventory: 372 PRs (356 drafts, 16 non-drafts), retrieved in four pages.

All three required checks passed on the exact current head:
- Full repository suite: **1,355 passed, zero failed, eight subtests passed**.
- Inclusive coverage: **59.48%**, above the 53% floor; 32 files skipped only because they had complete coverage.
- Core suite: **677 passed, eight subtests passed**.
- Wheel build/install and packaged Barrot V3 / primary XRP mission verification passed.
- Six-manifest dependency audit passed; zero known vulnerabilities reported.
- Fail-closed gate passed and explicitly keeps automatic merging disabled.

Evidence: [Full CI 42781972378](https://github.com/Barrot-Agent/B-Agent/actions/runs/42781972378), [Dependency audit 42781972163](https://github.com/Barrot-Agent/B-Agent/actions/runs/42781972163), [Fail-closed gate 42781972266](https://github.com/Barrot-Agent/B-Agent/actions/runs/42781972266).

The Actions cache budget is read-only. The warning did not fail the test, wheel or dependency jobs.

## Fresh XRP market structure

### Spot and quote normalization

- Kraken XRP/USD: last **$1.09347**, bid/ask **$1.09323/$1.09324**, 24-hour volume **23.553M XRP**, VWAP **$1.09533**, high/low **$1.11573/$1.07502**. Kraken did not supply a provider event timestamp.
- OKX XRP-USDT: last **1.0920 USDT**, bid/ask **1.0918/1.0919**, 24-hour volume **63.212M XRP**, provider event time **08:14:39.071 UTC**.
- Kraken USDT/USD: **0.99872**. Mechanical OKX normalization gives **$1.09060**, about **0.262% below** Kraken’s displayed last trade.

The observations are asynchronous. The difference is not an executable arbitrage signal and is not model-admitted.

Sources: [Kraken XRP/USD](https://api.kraken.com/0/public/Ticker?pair=XRPUSD), [OKX XRP-USDT](https://www.okx.com/api/v5/market/ticker?instId=XRP-USDT), [Kraken USDT/USD](https://api.kraken.com/0/public/Ticker?pair=USDTUSD).

### Spot order-book depth

Fuelmaps’ **08:00 UTC** snapshot shows a six-venue **spot-only** book with midpoint **$1.0938**:

| Distance | Bids | Asks | Bid share |
|---|---:|---:|---:|
| ±0.5% | $8.1M | $5.5M | 59.4% |
| ±1% | $12.7M | $10.1M | 55.6% |
| ±2% | $18.1M | $11.1M | 61.9% |
| ±5% | $24.3M | $13.5M | 64.3% |
| ±10% | $32.8M | $15.0M | 68.7% |

Venues: Coinbase, OKX, Kraken, Bitstamp, Bitfinex and Gemini. Binance and Bitget are excluded. Full-depth and near-price venue coverage differ. Resting orders can be cancelled; this is not executable depth or a price forecast.

Largest displayed bids within 10% include $2.5M at $1.050, $2.1M at $1.000, $2.0M at $1.090, $1.8M at $1.086 and $1.6M at $1.091.

Source: [Fuelmaps XRP spot order book](https://fuelmaps.io/order-book/).

A separate Binance XRPUSDT perpetual heatmap is not comparable with this spot-only snapshot. Its 06:13 UTC view showed $17.4M bids and $15.5M asks within 1%; it is retained as a separate derivatives feature, not added to spot depth.

### Derivatives

Liqwall at **08:22 UTC** reports aggregate OI **$1.21B**, down **3.3%** over 24 hours; **$3.6M** liquidations, including $3.0M longs and $631K shorts; average funding **+0.0034% per eight hours**, Binance **+0.0091%**; 74.9% of Binance XRP-position accounts long and 70.6% of top-trader accounts long.

Coinalyze data surfaced through BitcoinLeverage at 06:18 UTC covers only Binance and Bybit XRPUSDT perpetuals, two of 22 available contracts: Binance OI $344.87M, 74.55% long accounts and $2.97M 24-hour liquidations; Bybit OI $257.12M, 81.32% long accounts and $1.22M liquidations. Funding is displayed as 0.01%, but settlement intervals must remain exchange-specific.

Alpha Finance’s 01:40 UTC liquidation map showed $2.48B OI and $8.0M long versus $831.7K short liquidations. Its modeled $6.0M short cluster at $1.1192 and $3.4M long cluster at $1.0833 are stale and model-derived, not observed guaranteed liquidation levels.

The aggregators disagree materially on total OI and coverage. Do not average them. The descriptive commonality is long-heavy liquidation pressure with declining OI; no directional forecast follows.

Sources: [Liqwall](https://liqwall.com/coins/xrp), [Coinalyze coverage via BitcoinLeverage](https://bitcoinleverage.com/xrp/funding-rate), [Alpha liquidation heatmap](https://alphafinance.io/liquidation-heatmap/xrp/).

### ETF flows — zero-versus-missing correction retained

CryptoKeyhole’s issuer-file tracker reports November 9 partial coverage of **3/4 daily-reporting issuers**: Bitwise −8,594,551 XRP; Canary XRPC −427,341 XRP; 21Shares TOXR −194,660 XRP; Franklin XRPZ missing. Partial total: **−9,216,553 XRP**, approximately **−$10.1M**.

The Franklin file observed November 9 at 23:47–23:52 UTC is dated to prior-day orders and does not supply a November 9 observation. Grayscale has no accessible daily issuer file; CryptoKeyhole uses quarter-end SEC holdings. REX-Osprey direct-only holdings are not a valid proxy for its full indirect holdings.

Alpha Finance reports **−$10.4M across 5/5 flow-series tickers**, assigning zero to Franklin and Grayscale. It does not publish fund-level holdings/AUM or the fund list for that dashboard. CryptoKeyhole’s latest complete day remains November 6: −752,048 XRP. Its completed 11-session period is +2,622,459 XRP / +$3.45M and excludes the November 9 partial.

The dashboards use different coverage and zero-versus-missing treatment; publisher/source independence is not established. **Do not average, zero-fill or admit these totals as verified cash creations/redemptions.** Holdings changes are not proof of exchange sales; cash and in-kind redemption mechanics remain distinct.

Sources: [CryptoKeyhole issuer-file tracker](https://cryptokeyhole.com/etf-flows/xrp/), [Alpha Finance ETF flow series](https://alphafinance.io/etf/xrp/).

### Exchange balances

XRP Insights’ November 9 snapshot attributes **22.35B XRP** to 701 wallets across 24 exchanges. Its same-wallet-set change is −25.8M XRP over seven days and −138.1M over 30 days. Upbit is attributed 6.45B, Coinbase 5.80B and Binance 2.73B XRP.

The methodology reads public rippled account balances and uses XRPSCAN labels. The total includes cold and omnibus custody balances; it is not tradable float. Same-wallet decreases do not prove sales or customer withdrawals. Newly tracked wallets are excluded from the same-wallet comparison.

Source: [XRP Insights exchange balances](https://xrp-insights.com/exchange-balances).

## Macro and identity research

- BLS schedules October 2026 CPI and Real Earnings for **November 10 at 08:30 ET / 13:30 UTC**. They were not released at this capture cutoff. No result or market surprise was inferred. [Official BLS schedule](https://blsmon1.bls.gov/schedule/2026/11_sched_list.htm).
- No new exact-phrase match for “SBIC, ChatGPT SBIC”. Tokyo SBIC’s official June 12–13, 2025 course includes ChatGPT and Copilot instruction for investee companies; it is training, not an OpenAI partnership. [Tokyo SBIC course](https://www.sbic.co.jp/training/20250612co/).
- Permission Coin ASK remains only a candidate for “ASK Coin”. CoinMarketCap describes its ASK token on Base and Polygon using LayerZero OFT; no XRP Ledger integration was established. [Permission Coin](https://coinmarketcap.com/currencies/permission-coin/).
- “Actual capital” is not a standardized XRP metric. Keep cash subscriptions, in-kind XRP, debt proceeds, drawn facilities, contingent financing capacity and secondary resales separate.
- No additional personal-channel YouTube videos attributed to Camilla/Kamilah Stevenson were verified. Guest appearances remain distinct from channel ownership.

Previously verified Coinbase/Circle/Ripple/SBI relationships, OCC trust-charter records, Evernorth capital taxonomy and the SBIC East/Central/West legal-identity distinction remain in the prior archive. No new primary corporate change was verified in this short interval.

## Main workflows and nine-platform status

Main’s latest scheduled Cross Analysis run **42778238470** succeeded. Pillars Consistency Check **42621970927** failed because GitHub App ID/private key/installation ID are absent, Databricks returned HTTP 403, and the Hugging Face Space reported BUILD_ERROR. No external action was dispatched.

Nine-platform status: ChatGPT current-session GitHub read/write verified; Copilot comment-only review activity with no approval or persistent data flow; Claude, Grok, Gemini and Codex unverified; Hugging Face prior BUILD_ERROR; Kaggle untested; Databricks prior HTTP 403. No cross-platform data exchange executed.

The XRP mission manifest and scheduled ingestion workflow are **not on main**. The workflow exists only on the integration branch, so scheduled XRP ingestion is not active on main.

## Prediction-engine status

Integration contains 40 public-source records (36 hourly, two weekly CFTC and two excluded non-commercial XRPL nodes), raw-byte receipt capture and SHA-256 receipt-chain logic, a point-in-time SQLite feature store, four deterministic baselines, chronological walk-forward evaluation with purge/embargo, calibration and drift diagnostics, and a fail-closed forecast ledger requiring trusted evaluator attestation.

Still missing: independent WORM/timestamp anchoring, synchronized historical spot/L2/derivatives/exchange-flow/collateral data, effective-sample-size correction for overlapping horizons, sufficient independent shadow outcomes and demonstrated out-of-sample lift.

Rendered web observations in this run did **not** preserve original HTTP transport bytes/headers and have no raw-byte SHA-256 receipts. They are research cross-checks only, not model-admitted features.

**Forecast status: NOT_ISSUED.** No directional forecast, paper trade or real-money action occurred.

## PR backlog and merge decision

- #1640: **BLOCKED** sole V3/XRP integration path; exact-head CI green; 62 review submissions are all COMMENTED, zero APPROVED; 22/22 inline threads resolved but outdated.
- #1643: **UNIQUE/UNREVIEWED** research archive; 670 paths, previously measured 663 unique and seven shared with #1640; stale and not mergeable. Preserve.
- #1653: **UNIQUE/UNREVIEWED** repository knowledge graph; seven paths, 18 commits, eight unresolved review threads. Preserve.
- #1642: **DUPLICATE/SUPERSEDED CANDIDATE**; seven paths overlap #1640; draft. Retain until verified successor merge.
- #1644–#1650: dependency/action reconciliation candidates; non-draft and GitHub reports mergeable, but exact versions and overlapping workflow/manifest changes require reconciliation. Retain.
- #1614 and #1611: unique prediction-validator/ledger work; preserve unique material for integrated review.
- #1615 and #1610: security-containment work; preserve unique workflow/operations material.
- #1605: unique market-microstructure artifact; preserve.
- #1597: unique Coinbase/Circle/SBI/Ripple research; preserve.
- #1269: unique OBJ topology/triangulation; preserve.
- #1655, #1659 and #1641: unique structural, local-LLM and bounded-experimentation drafts; preserve.

No PRs were closed.

**PR #1640 remains unmerged.** Main branch-protection details return HTTP 403; visible fallback ruleset ID 10863829, “Fall Back”, is disabled. A previous main push triggered successful GitHub Pages publication; the seven public web assets in #1640 retain an unresolved automatic-publication authorization boundary. Do not bypass protection.

## Next concrete actions

1. Resolve independent approval, authoritative branch-protection visibility and Pages-publication authorization before any merge.
2. After 13:30 UTC, capture the BLS CPI release with provider event time and retrieval time separated.
3. Reconcile CryptoKeyhole’s 3/4 issuer-file holdings series against Alpha’s 5/5 flow-series dashboard without averaging or zero-filling.
4. Preserve #1643/#1653 and all unique research, security and prediction work; close only exact duplicates after a successor is merged and verified on main.
5. Expand synchronized historical market data and independent raw-byte anchoring before any forecast issuance.

No merge, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push or destructive worktree operation occurred.

---

# Barrot XRP Mission — Run124: market microstructure, ETF reporting and integrated verification

**Capture cutoff: 2026-11-10T07:58:51Z.** XRP intelligence and prediction-engine mastery remain priority one. Barrot V3 remains the execution, orchestration, safety and verification foundation.

## Repository state and exact-head evidence

- Main SHA: d4d43be3427375cf79d190e768976de062e20287.
- Existing integration PR: [#1640](https://github.com/Barrot-Agent/B-Agent/pull/1640), branch integration/core-capabilities-mmi-structural-paper-20261104.
- Integration head at start of Run124: f7dfd1747196f39051819491ee125b1d3eb3973a; 914 commits ahead, zero behind.
- PR #1640 changes 245 paths (+118,490/−3,554), including 43 workflow files and seven public web assets.
- Main tree: 1,404 entries / 1,299 files. Integration tree: 1,542 entries / 1,429 files.
- Full open-PR inventory: 372 (356 drafts, 16 non-drafts), retrieved as four pages of 100/100/100/72.

The exact integration head f7dfd1747196f39051819491ee125b1d3eb3973a passed all three required gates:

- Full suite: **1,347 passed, zero failed, eight subtests passed**, inclusive coverage **59.48%** against a 53% floor.
- Core suite: 677 passed, eight subtests passed.
- Wheel build/install and packaged Barrot V3 / primary XRP mission verification passed.
- Six dependency manifests passed; zero known vulnerabilities.
- Fail-closed merge gate passed; automatic merge remains disabled.

Evidence: [full CI 42776790058](https://github.com/Barrot-Agent/B-Agent/actions/runs/42776790058), [dependency audit 42776790394](https://github.com/Barrot-Agent/B-Agent/actions/runs/42776790394), [fail-closed gate 42776790052](https://github.com/Barrot-Agent/B-Agent/actions/runs/42776790052).

The Run124 code/test commit 4177a23050f9a17aad5467a22aba477e91fe674c passed exact-head CI: **1,355 passed, zero failed, eight subtests passed, 59.48% inclusive coverage**. All eight new Run124 evidence/contract tests passed. Core suite: 677 passed, eight subtests. Wheel build and packaged primary-mission verification passed. Six-manifest dependency audit passed with zero known vulnerabilities. Fail-closed gate passed with automatic merge disabled. Evidence: [full CI 42781477255](https://github.com/Barrot-Agent/B-Agent/actions/runs/42781477255), [dependency audit 42781477040](https://github.com/Barrot-Agent/B-Agent/actions/runs/42781477040), [fail-closed gate 42781477082](https://github.com/Barrot-Agent/B-Agent/actions/runs/42781477082). The cache-budget warning made Actions cache read-only but did not fail verification.

## Fresh XRP market evidence

### Spot and order-book depth

At the capture cutoff, Kraken's XRP/USD API response showed last **$1.09347**, bid/ask **$1.09323/$1.09324**, 24-hour volume **23.55M XRP**, VWAP **$1.09533**, high **$1.11573**, low **$1.07502**. Kraken did not provide a provider event timestamp.

OKX's XRP-USDT response showed **1.1036 USDT**, bid/ask **1.1034/1.1035**, 24-hour volume **62.67M XRP**, provider timestamp **07:41:51.664 UTC**. Kraken USDT/USD was **0.99873**. Mechanical normalization gives OKX approximately **$1.10220**, about **0.80% above** Kraken's last trade. This is not an arbitrage signal: OKX was about 17 minutes old at capture, Kraken/USDT provider event times were unavailable, and HTTP cache-age headers were not preserved.

Fuelmaps' **07:00 UTC** spot-only snapshot covered six venues (Coinbase, OKX, Kraken, Bitstamp, Bitfinex, Gemini). Within 1% of midpoint it showed **$12.4M bids vs $10.0M asks**, 55.4% bid share; within 2%, $17.7M vs $10.7M; within 5%, $24.1M vs $12.9M. Binance and Bitget were excluded. These are resting orders, not executed volume; they can be cancelled.

### Derivatives

Liqwall at 07:52 UTC reported OI **$1.23B**, down 3.0% over 24 hours, $3.7M liquidations (longs $3.0M, shorts $675K), average funding +0.0096% per eight hours and 74.6% Binance long accounts.

TradRadar at 07:10 UTC reported OI **$1.66B**, down 2.5%, funding +0.0082% per eight hours, at least $4.98M liquidations (longs $4.17M, shorts $815K), and 79.5% long accounts. Venue coverage differs; the OI readings are not averaged.

The common description is long-heavy deleveraging. Price rising while OI falls is consistent with position reduction or short-covering, but positive funding and long crowding preserve liquidation risk. No directional conclusion is established.

### ETF flows — partial reporting and a zero-versus-missing disagreement

CryptoKeyhole's issuer-file tracker updated 07:48 UTC and reports **3 of 4** daily-tracked funds for November 9: **−9,216,553 XRP (about −$10.1M)**. Bitwise −8,594,551 XRP, Canary −427,341 XRP, 21Shares TOXR −194,660 XRP; Franklin XRPZ is missing. Its latest complete day remains November 6: −752,048 XRP. The November monthly matrix value **−$903,489** is the completed-days month-to-date figure and excludes the November 9 partial; it is not the November 9 daily flow.

CryptoETF, published 05:48 UTC, reports **3 of 5** funds and −$10.3M, with XRPZ and GXRP missing. Alpha Finance reports **5 of 5** and −$10.4M but shows zero for XRPZ and GXRP, does not publish fund holdings/AUM, and derives a flow series rather than issuer holdings. Its full-coverage claim is not corroborated by the issuer-file trackers. The totals are close, but coverage, zero-versus-missing treatment and 30-session totals disagree. These publishers may share underlying issuer series; independent source groups are not established. No averaging or model admission.

### Exchange flows and custody-transfer disambiguation

TrackWhale's 07:33 UTC seven-day large-transfer subset reports 64 tracked transfers: 501.72M XRP inflows (10 transfers), 608.96M XRP outflows (15 transfers), net **−107.24M XRP** (about −$130.76M). It is not a complete XRPL exchange-flow ledger.

Its largest transfer, **368.48M XRP**, is explicitly a **Binance-to-Binance rotation** on November 4 at 19:08 UTC (transaction ED71D3EEE5A00362D5A1FDAC3EDE809FFD165EF27030A472144DC50C972A0D12). The provider excludes exchange-to-exchange/internal transfers from netflow. This transaction is not Evernorth and must not be counted as exchange outflow or attributed to the previously investigated BitGo custody reorganization. Recent Binance-to-unknown and OKX-to-unknown movements remain unlabelled; a transfer is not proof of a sale.

### Macro and sentiment

BLS reported October payrolls +165,000, unemployment 4.1%, average hourly earnings +3.1% year over year on November 6. October CPI and Real Earnings are scheduled for **November 10 at 13:30 UTC** (08:30 ET), after this cutoff; no result was recorded. October PPI is scheduled November 13 at 13:30 UTC.

Main's read-only Cross Analysis workflow run 42778238470 succeeded at 07:51 UTC. Its entity profile reports XRP net sentiment +0.46 and Ripple +0.48, but the sentiment-shift detector had zero observations in both recent and prior windows. Corpus sentiment is not a current price signal and is not model-admitted.

## Prediction-engine status and contract correction

The integration branch's registry contains **40 records: 36 hourly sources, two weekly CFTC sources and two excluded non-commercial XRPL nodes**. Therefore, 38 sources are scheduled and two are excluded. Run124 corrects a stale sentence in research/xrp_intelligence/feature-store-contract.md that incorrectly said 38 total / 36 scheduled / two excluded, omitting the weekly CFTC sources. A regression test now prevents that count from recurring.

Executed components: point-in-time validator, SQLite feature-store prototype, receipt/lineage checks, four deterministic baselines, chronological walk-forward evaluation with purge/embargo, temporal calibration diagnostics, drift reporting and fail-closed forecast ledger.

Not implemented/verified: external WORM retention, independent timestamp authority, signed external source registry, complete synchronized historical spot/L2/derivatives/exchange-flow/collateral data, sufficient independent shadow outcomes and demonstrated out-of-sample lift. GitHub raw receipts have 90-day artifact retention; feature-store checkpoints have seven-day retention and daily/manual recovery artifacts 90 days. SQLite triggers are not adversarially tamper-proof. The scheduled ingestion workflow exists only on the integration branch; it is not active on main.

**Forecast status: NOT_ISSUED.** No directional forecast, paper trade or real-money action.

## Nine-platform coordination

The Run124 snapshot records all nine platforms. Only this ChatGPT session's GitHub read/write route is verified. Copilot has comment-only activity (62 COMMENTED submissions, zero approvals), not an authenticated persistent data pipeline. Claude, Grok, Gemini and Codex remain unverified; Hugging Face has a prior BUILD_ERROR; Kaggle is untested; Databricks previously returned HTTP 403. No cross-platform data exchange occurred.

## PR backlog and merge decision

- **#1640 — blocked integration path.** 914 ahead / 0 behind, 245 changed paths, GitHub reports mergeable. 62 reviews are all COMMENTED, zero APPROVED. All 22 inline threads are resolved but outdated. Branch-protection details return HTTP 403; the visible fallback ruleset is disabled. A previous main push triggered GitHub Pages publication; the seven public web assets in this PR have no specific publication authorization.
- **#1643 — unique research archive.** 670 changed paths; seven overlap #1640 and 663 are unique. Stale/unmergeable; preserve.
- **#1653 — unique repository knowledge graph.** Seven paths; one shared CI path and six unique code/docs/tests. Eight unresolved review threads; preserve.
- **#1642 — duplicate candidate.** All seven changed paths overlap #1640; draft. Do not close before a verified successor merge.
- **#1614 — unique prediction work.** 57 paths, eight overlap #1640 and 49 unique; draft/unmergeable. Preserve unique research-artifact-clock and research material.
- **#1611 — prediction contract.** Eight paths, six overlap and two unique research/handoff paths; preserve unique material.
- **#1615 — security containment.** 14 paths, one overlap and 13 unique workflow/operations paths; preserve.
- **#1610 — security containment.** 14 paths, seven overlap and seven unique workflow/operations paths; preserve.
- **#1605 — unique market microstructure artifact; preserve.**
- **#1597 — 17 unique XRP institutional research paths; preserve.**
- #1644–#1650 dependency updates require exact version reconciliation; #1269, #1655, #1659 and #1641 retain unique work. No PRs were closed.

**No merge.** Independent approval is absent; effective branch-protection requirements remain unverified; Pages publication is not authorized. No bypass attempted.



**Post-Run124 integration head:** 4177a23050f9a17aad5467a22aba477e91fe674c; PR #1640 is now 915 commits ahead, zero behind, with 248 changed paths (+119,738/−3,554). The handoff refresh is documentation-only; the Run124 code/test commit above is the exact head on which the new 1,355-test result was produced.

## Run124 records

- Structured market artifact: research/xrp_intelligence/20261110T075851Z-run124-market-depth-derivatives-etf-macro-update.json
- Nine-platform snapshot: research/xrp_intelligence/nine_platform_coordination_snapshot_20261110T075851Z.json
- Corrected contract: research/xrp_intelligence/feature-store-contract.md
- Regression tests: tests/test_xrp_run124_market_evidence.py
- Existing integration PR: [#1640](https://github.com/Barrot-Agent/B-Agent/pull/1640)

Next actions: verify exact-head CI on the Run124 commit; resolve approval/branch-protection/Pages blockers; continue independent BitGo custody replay and ETF issuer cash-versus-in-kind reconciliation; build synchronized historical market data and external receipt anchoring; preserve unique PR work; keep forecasts NOT_ISSUED until readiness and out-of-sample requirements are met.

No merge, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push or destructive worktree operation occurred.

---

# Barrot XRP Mission — Run123B: ETF Issuer-File Refresh and Prior-Record Correction

**Capture: approximately 2026-11-10 07:37 UTC.** This addendum corrects one stale statement in the original Run123 artifact and adds the refreshed issuer-file reconciliation. Historical artifacts remain unchanged.

## Exact-head verification

The Run123A documentation/research head `ddf3a2c1ca45c41acbacb9836f2c3978e8d55d58` passed all exact-head checks:

- Full repository suite: **1,347 passed, zero failed, eight subtests passed**.
- Inclusive coverage: **59.48%**, above the 53% floor.
- Core suite: 677 passed, eight subtests passed.
- Wheel build/install and packaged verification of Barrot V3, the XRP mission and canonical data assets passed.
- Six dependency manifests passed; zero known vulnerabilities.
- Fail-closed gate passed; automatic merge disabled.
- CodeRabbit was skipped, not approved.

Evidence: [full CI 42776159334](https://github.com/Barrot-Agent/B-Agent/actions/runs/42776159334), [dependency audit 42776159082](https://github.com/Barrot-Agent/B-Agent/actions/runs/42776159082), [fail-closed gate 42776159073](https://github.com/Barrot-Agent/B-Agent/actions/runs/42776159073).

The only warning was GitHub Actions cache storage being read-only after the cache budget was reached. Tests, wheel verification and audit succeeded.

## Correction to Run123 ETF status

The original Run123 artifact `20261110T071743Z-run123-spot-depth-etf-flow-source-reconciliation.json` stated that none of CryptoKeyhole's four daily-tracked funds had published a 9 November file. That status was stale/incorrect. The CryptoKeyhole page had refreshed and now explicitly reports **3 of 4** daily-tracked funds published, updated 10 November at 07:12 UTC. The original artifact remains unchanged as a point-in-time record; this correction supersedes its `nov_9_status` field.

### CryptoKeyhole issuer-file collector — 9 November partial

- Partial total: **−9,216,553 XRP**, approximately **−$10.1M**, 3 of 4 daily-tracked funds.
- Bitwise: 406,770,578 XRP held; −8,594,551.4 XRP daily change. Its 9 Nov file was observed 10 Nov 01:37–01:42 UTC.
- Canary: 242,535,412 XRP held; −427,341.2 XRP daily change. Its 9 Nov file was observed 10 Nov 05:22–05:27 UTC.
- 21Shares TOXR: 107,100,961 XRP held; −194,660.1 XRP daily change. Its issuer file is stamped 10 Nov 06:01 UTC.
- Franklin XRPZ: latest holdings 310,430,333 XRP for 6 Nov; its 6 Nov file was published 9 Nov 23:47–23:52 UTC. Its 9 Nov holdings file was still outstanding at 07:12 UTC.
- Grayscale GXRP is not collected daily because automated reads are refused; its page shows quarterly SEC filing holdings. REX-Osprey XRPR is excluded because its 1940 Act fund structure and direct-only holdings file do not represent its full indirect exposure.

The latest complete day remains 6 November: −752,048 XRP / approximately −$887K across four of four daily-tracked funds. The 9 November partial is not included in cumulative totals. CryptoKeyhole's 23 October–6 November cumulative window is +2,622,459 XRP / approximately +$3.45M over 11 sessions; it is not comparable to a 30-session metric.

### Issuer-page cross-checks

- Bitwise's official page displays 406,770,577.61 XRP and $444.763M, with 36.44M shares; the page labels the data 8 November. CryptoKeyhole labels essentially the same balance 9 November. The amount agrees to rounding; the date label needs reconciliation. Bitwise identifies Coinbase Custody Trust Co. as digital-asset custodian and BNY Mellon as trust custodian.
- Canary's public page still displays 6 November figures ($286.86M net assets) while CryptoKeyhole reports a 9 November file observed 10 November 05:22–05:27 UTC. The newer file is not independently displayed on the issuer summary page.
- 21Shares' official page shows 9 November AUM of $117.096M and 11M shares, consistent with the 9 November TOXR file date; the public summary view does not expose the XRP holding count.
- Franklin's latest visible holdings remain 6 November.

### Three-source flow reconciliation

| Source/method | 9 Nov flow | Coverage |
|---|---:|---|
| CryptoKeyhole issuer holdings changes | −$10.1M / −9.217M XRP | 3/4 daily-tracked; Franklin pending |
| CryptoETF share-count change × NAV | −$10.3M | 3/5; XRPZ and GXRP missing |
| Alpha / Coinglass feed | −$10.4M | 5/5; Franklin and Grayscale shown as zero |

The aggregate partial outflows are close, but the Canary component is not:
- CryptoKeyhole: −427,341 XRP, approximately −$468K at its implied daily XRP/USD close.
- CryptoETF: −$700K.
- Alpha/Coinglass: −$811.4K.

CryptoETF uses `(shares(T+1)-shares(T))*NAV(T)`, with issuer-specific same-day timing exceptions. CryptoKeyhole uses issuer holdings changes in XRP and values them at its own XRP/USD close. Alpha says its data comes from the Coinglass commercial feed. The detailed CryptoETF table says 3/5 funds reported, while a lower summary line says 5/5; preserve that internal contradiction and use the detailed table.

Alpha's +$8.9M 30-session / $1.72B cumulative figures, CryptoETF's +$115M 30-session / $1.80B cumulative figures, and CryptoKeyhole's +$3.45M over 11 complete sessions are not like-for-like. Do not average or zero-fill missing funds.

**ETF flow remains NOT MODEL-ADMITTED.** The 9 November report is partial, fund coverage differs, Canary's component remains unresolved, and daily holdings reductions do not prove the XRP was sold on an exchange rather than redeemed in-kind or transferred through custody.

Sources: [CryptoKeyhole daily XRP ETF flows](https://cryptokeyhole.com/etf-flows/xrp/), [Bitwise official fund page](https://bitxrpetf.com/), [Canary official XRPC page](https://canaryetfs.com/xrpc/), [21Shares official TOXR page](https://www.21shares.com/en-us/products-us/toxr), [CryptoETF methodology](https://cryptoetf.today/en/methodology), [Alpha XRP ETF dashboard](https://alphafinance.io/etf/xrp/).

## Current integration status

- Main SHA: `d4d43be3427375cf79d190e768976de062e20287`.
- Run123A verified head: `ddf3a2c1ca45c41acbacb9836f2c3978e8d55d58`.
- PR #1640 remains the single V3/XRP integration path; 913 commits ahead, zero behind, 244 changed paths before this addendum.
- 372 open PRs: 356 drafts, 16 non-drafts. No PRs were closed.
- Main remains protected, but detailed branch-protection access returns HTTP 403. The visible `Fall Back` ruleset is disabled.
- PR #1640 has zero approving reviews; 22 inline threads are resolved but outdated.
- GitHub Pages has previously deployed automatically after a main push. Automatic publication authorization remains unresolved.
- XRP public ingestion and the primary mission manifest remain absent from main.

Merge remains blocked. No merge or branch-protection bypass occurred.

Run123B structured correction: `research/xrp_intelligence/20261110T073700Z-run123b-etf-issuer-flow-reconciliation-correction.json`.

## Next actions

1. Verify exact-head CI for the Run123B correction commit.
2. Recheck Franklin's 9 November issuer file; retain null until published and validated.
3. Reconcile Bitwise's 8 Nov issuer-page label against the 9 Nov holdings file and Canary's issuer summary lag.
4. Reconcile the Canary flow difference across XRP holdings change, share-count/NAV and Coinglass methods.
5. Keep ETF flows excluded from the feature store until fund coverage and date alignment are explicit.
6. Resolve approval, branch-protection visibility and Pages publication authorization before any merge.


---

# Barrot XRP Mission — Run123A: Latest Derivatives Refresh and Exact-Head Verification

**Capture: approximately 2026-11-10 07:32 UTC.** This addendum preserves Run123's spot, order-book and ETF source reconciliation. The earlier Run123 derivatives values remain valid historical snapshots at their stated times; the newer provider snapshots below supersede them as the latest available readings.

## Run123 exact-head verification

The Run123 research commit `266a53e4fa6e58576c25b580d346b9fc7830d692` passed all exact-head gates:

- Full repository suite: **1,347 passed, zero failed, eight subtests passed**.
- Inclusive coverage: **59.48%**, above the 53% floor.
- Core suite: **677 passed, eight subtests passed**.
- Wheel build/install and packaged verification of Barrot V3, the XRP mission and canonical data assets passed.
- Six dependency manifests passed; zero known vulnerabilities.
- Fail-closed gate passed; automatic merge remains disabled.
- CodeRabbit review check was skipped, not approved.

Evidence: [full CI 42775579721](https://github.com/Barrot-Agent/B-Agent/actions/runs/42775579721), [dependency audit 42775579719](https://github.com/Barrot-Agent/B-Agent/actions/runs/42775579719), [fail-closed gate 42775579740](https://github.com/Barrot-Agent/B-Agent/actions/runs/42775579740).

The only CI warning was the GitHub Actions cache budget being read-only. Cache saving failed after tests and wheel verification; it did not fail CI.

## Latest derivatives snapshots

- **TradRadar, 06:20 UTC:** mark $1.1006 (+0.53%/24h); OI $1.66B, down 3.99%; OI-weighted funding +0.0070%/8h; at least $6.85M liquidations, $6.07M longs and $777.81K shorts; 79.5% long accounts (ratio 3.89). OI covers seven exchanges; liquidation and long/short summaries cover five.
- **Liqwall, 07:22 UTC:** spot reference $1.10; OI $1.23B, down 3.1%; average funding +0.0092%/8h (Binance +0.0081%); $3.8M liquidations, $3.1M longs and $676K shorts; 74.6% of Binance XRP accounts long.
- **Alpha Finance, 06:08 UTC:** spot reference $1.0968; OI $2.45B; 24-hour volume $2.79B; reported long liquidations $6.0M and short liquidations $741.4K. Its modeled largest short cluster is $3.7M at $1.1193, and largest long cluster $2.8M at $1.0685. Modeled aggregate liquidity is $37.5M above and $45.3M below. Binance's heatmap is unavailable for this window.

OI ranges from $1.23B to $2.45B, almost a 2x spread. Long liquidation shares are approximately 82%–89% across the three displays. The source universes, time windows and methodologies differ; underlying venue feeds overlap. Do not average these values.

The descriptive signal is long-heavy liquidation pressure, with OI contraction in TradRadar and Liqwall and mildly positive aggregate funding. This supports a deleveraging description, not a directional forecast. A downside-continuation hypothesis competes with stabilization/mean reversion if spot bids absorb liquidation flow.

Alpha's liquidation clusters are modeled from OI and standard leverage tiers, not observed individual positions or guaranteed triggers. The earlier Run123 Fuelmaps snapshot showed $12.4M bids versus $10.0M asks within 1% across six spot venues at 07:00 UTC; resting orders can be cancelled.

Sources: [TradRadar](https://tradradar.io/markets/xrp), [Liqwall](https://liqwall.com/coins/xrp), [Alpha XRP heatmap](https://alphafinance.io/liquidation-heatmap/xrp/), [Fuelmaps spot book](https://fuelmaps.io/order-book/).

**No forecast is issued.** These cross-provider snapshots are descriptive and are not admitted as synchronized model features.

## Current repository and merge status

- Main SHA remains `d4d43be3427375cf79d190e768976de062e20287`.
- Run123 tested integration head: `266a53e4fa6e58576c25b580d346b9fc7830d692`.
- PR #1640 is the sole active V3/XRP integration path; open, non-draft, GitHub reports mergeable. Its exact current compare before this addendum is 912 commits ahead, zero behind, 243 changed paths.
- Full open PR inventory: 372 (356 drafts, 16 non-drafts); no PRs were closed.
- Main remains protected, detailed branch-protection API returns HTTP 403, and the visible `Fall Back` ruleset is disabled.
- #1640 has zero approving reviews. Its 22 inline threads are resolved but outdated.
- Main's XRP ingestion workflow and primary mission manifest remain absent; the scheduled main-only collector is not active on main.
- A previous main push triggered a successful dynamic GitHub Pages build-and-deploy. Authorization for another automatic publication remains unresolved.

Merge remains blocked. No merge or bypass occurred.

Run123A structured evidence: `research/xrp_intelligence/20261110T073200Z-run123a-latest-derivatives-refresh.json`.

## Next actions

1. Preserve the single #1640 integration path and complete the current exact-head checks after this documentation/research-only addendum.
2. Resolve independent approval, branch-protection visibility and Pages publication authorization.
3. Capture the official BLS October CPI release after 13:30 UTC; it had not yet been released at this cutoff.
4. Reconcile the partial November 9 ETF flow reports with issuer share/holdings files; keep all missing values null.
5. Expand synchronized direct derivatives collection beyond Binance/Bybit and preserve source/venue coverage.
6. Continue independent WORM/timestamp anchoring and historical point-in-time feature coverage before forecast issuance.


---

# Barrot XRP Mission — Run123: Spot Depth, Derivatives and ETF Flow Source Reconciliation

**Research cutoff: 2026-11-10 07:17:43 UTC.** This addendum preserves Run122 and its primary-source corrections.

## Run122 exact-head verification completed

The Run122 commit `8a0d5d053caf529dfd7686919069f07c76c43a7f` has now passed all exact-head checks:

- Full repository suite: **1,347 passed, zero failed, eight subtests passed**.
- Inclusive coverage: **59.48%**, above the 53% floor.
- Core suite: 677 passed, eight subtests.
- Installed wheel and Barrot V3 / XRP mission / canonical asset verification passed.
- Six dependency manifests passed; zero known vulnerabilities.
- Fail-closed gate passed; automatic merging remains disabled.

Evidence: [CI 42771625175](https://github.com/Barrot-Agent/B-Agent/actions/runs/42771625175), [dependency audit 42771625284](https://github.com/Barrot-Agent/B-Agent/actions/runs/42771625284), [fail-closed gate 42771625224](https://github.com/Barrot-Agent/B-Agent/actions/runs/42771625224).

## Current repository state

- Main: `d4d43be3427375cf79d190e768976de062e20287`.
- Integration head before Run123: `8a0d5d053caf529dfd7686919069f07c76c43a7f`.
- PR #1640: 911 commits ahead, zero behind, 242 changed paths; open, non-draft, GitHub reports mergeable.
- Main tree: 1,404 entries; integration tree: 1,539 entries. Main has 86 workflows; integration has 87.
- All 372 open PRs were enumerated through four API pages: 356 drafts, 16 non-drafts.
- Main's latest CI on the current SHA passed ([42526890841](https://github.com/Barrot-Agent/B-Agent/actions/runs/42526890841)); scheduled six-manifest dependency audit passed ([42579080840](https://github.com/Barrot-Agent/B-Agent/actions/runs/42579080840)); latest scheduled Cross Analysis on main passed ([42771367141](https://github.com/Barrot-Agent/B-Agent/actions/runs/42771367141)).
- Main still lacks `.github/workflows/xrp-public-ingestion.yml` and `data/missions/primary_mission.json`. The ingestion workflow is present only on the integration branch and its job is explicitly main-only.

## Fresh spot and order-book snapshot

**Kraken XRP/USD**, retrieved 07:17 UTC:
- Last $1.10360; bid $1.10359; ask $1.10360; displayed spread approximately 0.091 bps.
- 24-hour volume 25.166M XRP; VWAP $1.09437; 24-hour high/low $1.11573 / $1.07502.
- Kraken response does not supply an exchange event timestamp.

**OKX XRP-USDT**, provider event time 07:10:42.741 UTC:
- Last 1.1026 USDT; bid 1.1026; ask 1.1027.
- 24-hour volume 64.114M XRP; quote volume 70.232M USDT.
- Kraken USDT/USD last was 0.99868. A mechanical conversion gives approximately $1.10114 for OKX, 0.2225% below Kraken's displayed last. This is asynchronous and excludes executable fees/latency; it is not an arbitrage signal.

The surfaced JSON response-text SHA-256 values are recorded in the Run123 artifact. They hash the exact response text exposed by the retrieval, not original HTTP transport bytes or headers.

**Fuelmaps six-venue spot-only depth**, 07:00 UTC, XRP mid $1.1008:
- Within ±0.5%: $7.1M bids / $5.8M asks; 55.1% bid share.
- Within ±1%: $12.4M / $10.0M; 55.4%.
- Within ±2%: $17.7M / $10.7M; 62.4%.
- Within ±5%: $24.1M / $12.9M; 65.1%.
- Within ±10%: $31.8M / $14.7M; 68.3%, five venues.
- Six venues: Coinbase, OKX, Kraken, Bitstamp, Bitfinex and Gemini. Binance and Bitget are excluded.
- Largest displayed near-price levels: $2.0M bid at $1.094, $1.9M ask at $1.102 and $1.9M bid at $1.098.

This is resting spot liquidity, not executed volume. Orders can be cancelled. The ±10% band has only five venues. No directional inference is warranted from one hourly snapshot.

## Derivatives cross-provider disagreement

Latest accessible observations:
- TradRadar 05:05 UTC: OI $1.65B, down 3.66% in 24h; funding +0.0056%/8h; at least $8.77M liquidations, including $8.02M longs; 79.5% long accounts across its reported ratio set.
- Liqwall 02:22 UTC: OI $1.22B, down 1.8%; funding +0.0055%/8h; $8.2M liquidations, $7.5M longs; 74.5% of Binance XRP accounts long.
- Alpha's 01:40 UTC heatmap: OI $2.48B; its liquidation bands are modeled from OI and leverage tiers, not confirmed liquidation orders.

The OI range is about 2.03x. Timestamps, venue coverage and methodologies differ; do not average. The cross-source commonality is long-heavy liquidation pressure and reported OI contraction. Funding is mildly positive in aggregate, with venue-level disagreement. This describes positioning/deleveraging; it does not forecast price.

## ETF flows — methodology and coverage conflict

For 9 November:
- Alpha Finance / Coinglass reports approximately **−$10.4M**, with Bitwise −$9.4M, Canary −$0.8114M, TOXR −$0.2129M and zero for Franklin/Grayscale. It reports five funds, $1.72B cumulative flows and only +$8.9M over 30 sessions. Alpha's methodology says ETF flow is supplied by Coinglass and displayed as reported; missing feeds should be marked missing.
- CryptoETF.today reports **−$10.3M partial**, three of five funds: Bitwise −$9.4M, Canary −$0.7M and TOXR −$0.2M. XRPZ and GXRP are explicitly missing in the detailed table. It reports $1.80B cumulative and +$115M over 30 sessions. Its published method calculates flow from change in shares outstanding multiplied by NAV, generally T+1, with some issuer-specific same-day timing exceptions.
- CryptoETF.today contains an internal inconsistency: the detailed status says three of five and the table marks two funds missing, while a lower summary line says five of five. Use the detailed 3-of-5 state; preserve the contradictory line.
- CryptoKeyhole's latest complete day remains 6 November: −752,048 XRP / approximately −$887K, four of four tracked funds. Its 9 November view says none of its four daily-tracked funds had published a 9 November file. Its methodology reads issuer holdings/NAV files and does not bypass sites that refuse automated reads.

The two 9 November partial trackers agree on approximately $10.3M–$10.4M outflow for the three named funds. Alpha's Franklin/Grayscale zeros are not independently confirmed by issuer files in this run. The $80M cumulative and $106.1M 30-session differences between Alpha and CryptoETF are material methodology/coverage discrepancies. CryptoKeyhole's 9 November absence is a freshness/coverage gap, not a conflicting 9 November dollar total.

**ETF flow classification: partial / source-dependent / NOT MODEL-ADMITTED.** Do not average these trackers or substitute missing issuer reports with zero.

## Macro event

The BLS schedules October CPI and Real Earnings for **10 November at 08:30 ET / 13:30 UTC**. At the Run123 cutoff the release had not occurred. No CPI result was inferred. [Official BLS schedule](https://www.bls.gov/schedule/2026/).

## Integrated prediction-engine and platform status

The integration branch contains 40 public source records (36 hourly, two weekly CFTC, two excluded non-commercial XRPL nodes), raw-byte capture and SHA-256 receipt-chain logic, point-in-time SQLite feature storage, four baselines, chronological walk-forward with purge/embargo, calibration/drift diagnostics and a fail-closed forecast ledger requiring trusted Ed25519 attestation.

Remaining blockers: independent WORM/timestamp anchoring; synchronized historical spot/L2/derivatives/exchange-flow/collateral data; effective-sample-size correction for overlapping horizons; sufficient independent shadow outcomes; and demonstrated out-of-sample lift. The workflow stores raw artifacts for 90 days, per-run feature checkpoints for seven days and daily feature backups for 90 days. These are GitHub Actions artifacts, not independent WORM storage.

Nine-platform map remains unchanged: ChatGPT GitHub read/write verified; Copilot comment-only review activity; Claude, Grok, Gemini and Codex unverified; Hugging Face prior build error; Kaggle untested; Databricks prior HTTP 403. No cross-platform data transfer occurred.

**Forecast status: NOT_ISSUED.** No directional forecast, paper trade or real-money action occurred.

## Open PR and overlap classification

The 16 non-draft PRs are #1640, #1643, #1653, #1644–#1650, #1320, #1318, #1317, #1269, #1255 and #1254. All 372 open PRs remain open; no PR was closed.

Changed-path comparison against #1640:
- #1643: 670 paths, seven overlap, 663 unique paths; non-draft but GitHub reports not mergeable. Preserve its research archive.
- #1653: seven paths, one overlap, six unique; non-draft and mergeable, but eight unresolved review threads. Preserve the knowledge-graph work.
- #1655: eight paths, five overlap, three unique; preserve.
- #1659: six paths, two overlap, four unique; preserve.
- #1641: three unique paths; preserve.
- #1642: seven of seven exact path overlaps; duplicate candidate only after verified successor merge.
- #1614: 57 paths, eight overlap, 49 unique; preserve prediction work.
- #1611: eight paths, six overlap, two unique; reconcile prediction contracts.
- #1608, #1605, #1597, #1591, #1586, #1583, #1581, #1571, #1568, #1556 and #1554 have zero path overlap in the sampled comparison and are retained as unique-path research candidates pending semantic review.
- #1644 changes eight workflow paths all overlapping #1640; #1647 six paths all overlapping; #1645, #1646 and #1648–#1650 overlap their respective workflow/requirements paths.
- #1320 (five paths), #1318 (two) and #1317 (six) are exact path-overlap candidates.
- #1269 preserves eight unique mesh/topology paths; #1254/#1255 overlap the legacy requirements file.

Path uniqueness is not proof of semantic uniqueness. Do not close any source PR until the successor is merged and the exact content is verified on main.

## Merge decision — BLOCKED

PR #1640 has 62 review submissions, all COMMENTED, zero APPROVED; 22 inline threads are resolved but outdated. Main is marked protected, but detailed branch-protection access returns HTTP 403. The visible `Fall Back` ruleset is disabled, so effective required approvals/checks remain unverified.

A previous push to main triggered the dynamic GitHub Pages build-and-deploy run [42526890275](https://github.com/Barrot-Agent/B-Agent/actions/runs/42526890275), including successful build and deploy jobs. PR #1640 changes 43 workflows and `web/webmcp_monetization.js`. Authorization for another automatic public publication has not been established.

The user's conditional merge authorization is not satisfied. Do not merge or bypass protection. No PRs were closed.

## Next concrete actions

1. Verify exact-head CI, dependency audit and fail-closed gate for the Run123 documentation/research commit.
2. Obtain independent approval and authoritative branch-protection visibility; resolve the Pages publication side effect.
3. After the 13:30 UTC BLS release, capture the official October CPI release with its publication timestamp; do not infer the result before publication.
4. Re-fetch issuer ETF share/holdings files for 9 November and reconcile CryptoETF/Alpha/CryptoKeyhole coverage and the 30-session/cumulative differences before model admission.
5. Keep current spot/L2 and derivatives observations point-in-time; extend direct multi-venue derivatives collection beyond Binance/Bybit before treating aggregate OI as complete.
6. Preserve unique research, graph, mesh and prediction PRs. Close only exact duplicates after verified successor merges.
7. Advance independent raw-source anchoring and synchronized historical features before forecast issuance.

Run123 structured evidence: `research/xrp_intelligence/20261110T071743Z-run123-spot-depth-etf-flow-source-reconciliation.json`.

No merge, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push or destructive worktree operation occurred.


---

# Barrot XRP Mission — Run122: SBI Bond Capital, Doppler MOU, XRP Tokyo Claims and Creator Attribution

**Research cutoff: approximately 2026-11-10 06:55 UTC.** This addendum preserves Run121 and adds primary-source corrections. Run121's exact-head verification is complete; this Run122 documentation/research descendant requires its own exact-head CI.

## Run121 exact-head verification

Tested code head: `dd6abfd9fcf6196a2af0c4c10b7c186c6002423a`.

- Full repository suite: **1,347 passed, zero failed, 8 subtests passed**.
- Inclusive coverage: **59.48%**, above the 53% floor.
- Core suite: 677 passed, 8 subtests passed.
- Complete development dependencies installed; all repository tests executed.
- Wheel built and installed; installed package verified Barrot V3, the XRP mission and canonical data assets.
- Six dependency manifests passed; zero known vulnerabilities.
- Fail-closed merge gate passed; automatic merging remains disabled.

Evidence: [Full CI 42771039298](https://github.com/Barrot-Agent/B-Agent/actions/runs/42771039298), [dependency audit 42771039251](https://github.com/Barrot-Agent/B-Agent/actions/runs/42771039251), [fail-closed gate 42771039703](https://github.com/Barrot-Agent/B-Agent/actions/runs/42771039703).

Run122's new commit is a different head; verify it independently.

## SBI START Bonds — actual capital versus XRP reward

SBI Holdings' official product and issuance disclosures establish:

- **¥10 billion** issue amount; the SBI Securities product page says the bond is sold out.
- Three-year unsecured security-token bond, issued **2026-03-24**, maturity **2029-03-23**.
- Final annual coupon **2.150% pre-tax**; ordinary coupon and principal repayment remain conventional yen bond obligations.
- The security token is issued/managed on **BOOSTRY's ibet for Fin** platform and handled on Osaka Digital Exchange's **START** PTS. It is not issued on XRPL and is not XRP-denominated.
- Qualified domestic-resident individual/corporate subscribers who purchased at least ¥100,000 and completed SBI VC Trade receipt requirements were eligible for a **¥200-equivalent XRP benefit per ¥100,000 subscribed** (0.2%), scheduled by May 15, 2026.
- XRP quantity is calculated using SBI VC Trade's selling price at **2026-05-13 06:59 JST**.
- SBI Securities explicitly says the XRP benefit is separate from the regular coupon and does **not** imply XRP will be granted with each interest payment. Benefits for the 2027, 2028 and 2029 interest dates were undecided in the February 20 disclosure and may differ or not be provided.

If every yen of the ¥10B issue had qualified, the theoretical maximum for the initial 0.2% benefit would be **¥20M equivalent**. Actual eligible principal and total XRP distributed were not disclosed in the reviewed pages.

**Capital classification:** ¥10B is debt capital raised by SBI Holdings. The XRP benefit is a conditional investor incentive, not an XRP purchase, XRP-denominated coupon, XRP collateral allocation or ¥10B XRP inflow. Do not count the bond proceeds as XRP demand.

Primary sources: [SBI Holdings issuance notice, February 20, 2026](https://www.sbigroup.co.jp/english/news/pdf/2026/0220_a_en.pdf); [SBI Securities official product page](https://www.sbisec.co.jp/contents/lp/2026/bond_st_260220_sbistart.html).

## SBI Ripple Asia / Doppler — correct entity and scope

Doppler Finance's December 17, 2025 announcement says **SBI Ripple Asia** and Doppler signed an MOU to explore XRP-based yield infrastructure and RWA tokenization on XRPL. It identifies **SBI Digital Markets**, a MAS-regulated digital-asset entity, as institutional custodian for the initiative.

This corrects the previously repeated “SBI Digital Finance + Doppler” description:

- Named MOU parties: **SBI Ripple Asia and Doppler Finance**.
- Named custodian: **SBI Digital Markets**.
- These are not interchangeable with SBI Holdings, SBI VC Trade or SBI Digital Finance.
- The source is Doppler's own announcement; no separate SBI co-published release was located in this check.
- The MOU is exploratory. No launched product, committed AUM, XRP balance, client count, revenue, capital amount or production volume was disclosed.

The official XRP Tokyo 2026 agenda independently lists a Doppler Finance institutional-adoption keynote at 15:35 on April 7, 2026. [Doppler announcement](https://blog.doppler.finance/blog/sbi-ripple-asia-partners-with-doppler-finance-for-xrp-yield-and-rwa-tokenization).

## XRP Tokyo 2026 — primary agenda versus the 60% / four-second claims

The official April 7, 2026 agenda confirms the event, speakers and sessions:

- 11:05: stablecoins/tokenized-deposit panel with SBI VC Trade, HashPort, JPYC and Rakuten Wallet.
- 11:40: Evernorth COO Meg Nakamura, “When Capital Commits”.
- 11:55: institutional blockchain adoption panel with GMO Aozora Bank, HashHub and Fireblocks Japan.
- 12:30: web3 investment/global expansion panel including Evernorth, SBI Ripple Asia and a16z.
- 13:00: tokenized tourism payments with SBI Ripple Asia and Tobu Top Tours.
- 13:25: SBI VC Trade keynote on RLUSD.
- 15:35: Doppler Finance keynote on institutional XRPL adoption.

The official agenda does **not** publish a 60% SWIFT-cost reduction, sub-four-second bank-pilot result, named participating remittance banks or a list of twelve new ODL currency pairs. The 60% / under-four-second / twelve-pair narrative appears in secondary articles, including DailyCoin and 24/7 Wall St, without the underlying bank data, named corridor participants, comparison methodology or a primary Ripple/SBI announcement in the reviewed sources.

This is a **source-quality downgrade**, not proof that no private pilot occurred. The event's institutional-adoption panel is real; the specific numerical performance claims remain **UNVERIFIED** and must not be admitted as measured corridor performance or XRP demand.

Primary event source: [XRP Tokyo 2026 official agenda](https://www.xrp-tokyo.io/agenda). Secondary claims: [DailyCoin, April 14](https://dailycoin.com/japanese-banks-report-60-cost-savings-using-xrp-over-swift/), [24/7 Wall St, April 10](https://247wallst.com/investing/2026/04/10/xrp-news-ripples-japanese-bank-pilots-just-showed-60-cost-savings-using-xrp-over-swift/).

## Kamilah Stevenson — channel-level YouTube inventory

The official finance-education site identifies Dr. Kamilah Stevenson as “The Wealth Doctor” and describes a finance/investing education brand with more than 20 years of experience and 2,000+ client transformations. YouTube search results directly attribute the following videos to a channel named **Kamilah Stevenson**, with 137K–140K followers and a matching wealth-building/investing description:

| Published | Video | YouTube ID | Views / likes in indexed result |
|---|---|---|---|
| 2025-12-03 | XRP & The 2026 Setup: Something BIG Is Coming (Most People Have No Idea) | `Gy4BuGhAWE8` | 21,568 views; likes not returned |
| 2026-03-06 | Something Just Broke in Global Finance — And It's Connected to XRP | `iwhpNT73zpk` | 32,040 / 2,300 |
| 2026-08-25 | More Than 100 Million XRP Was Moved Into Flare's FXRP System — And XRP Holders Did It Voluntarily | `qtT2hLeFkM0` | 89,042 / 2,700 |
| 2026-09-13 | The CLARITY Act Is Not XRP's Biggest Event This Week | `Wa0Teymjaks` | 19,984 / 1,131 |

Direct YouTube references: [Gy4BuGhAWE8](https://www.youtube.com/watch?v=Gy4BuGhAWE8), [iwhpNT73zpk](https://www.youtube.com/watch?v=iwhpNT73zpk), [qtT2hLeFkM0](https://www.youtube.com/watch?v=qtT2hLeFkM0), [Wa0Teymjaks](https://www.youtube.com/watch?v=Wa0Teymjaks).

Attribution standard: these are direct YouTube search-result bylines, so the **channel-level uploader attribution** is verified. The official Wealth Doctor site and the channel's finance-coaching language strongly corroborate the same public creator brand. A direct official-site-to-channel cross-link was not found. Third-party directories list many near-identical Kamilah/Dr Kamilah accounts and copied bios; the `@drkamilahstevenson` handle candidate is listed at about 138K subscribers, but smaller lookalike channels are not treated as affiliated. Do not merge all similarly named accounts.

No “Camilla Stevenson” identity was independently verified as a separate creator. “Good Evening Crypto” show-host attributions are not counted as uploads on Kamilah's personal channel. BitPeaks-only titles without a direct YouTube ID remain candidates, not verified inventory.

Identity sources: [official Wealth Doctor site](https://learn.kamilahstevenson.com/), [YouTube search result for the CLARITY Act video](https://www.youtube.com/watch?v=Wa0Teymjaks), [third-party profile directory](https://www.idcrawl.com/kamilah-stevenson). The directory is a lead source, not identity proof.

## Exact-phrase research status

- **“SBIC, ChatGPT SBIC”:** no direct exact-phrase match. Tokyo SBIC's official training page includes ChatGPT and Copilot instruction for investee companies; this is training, not an OpenAI partnership. Japan's SBIC East/Central/West remain distinct from SBI Holdings.
- **“ASK Coin”:** unresolved. Permission Coin's ASK and an inactive Ask Coin exchange listing are separate candidates; neither has a verified XRP integration.
- **“actual capital”:** no standardized XRP metric. Keep cash subscriptions, in-kind XRP, debt proceeds, drawn facilities, contingent equity capacity, secondary resales and token rewards in separate categories. The SBI START Bond correction above is a concrete example.

## ETF-flow source conflict — downgrade November 9 partial

Run120/Run121 recorded a CryptoKeyhole snapshot at 06:12 UTC showing three issuer files and a partial −9,216,553 XRP estimate for November 9. A later search-index result for the same CryptoKeyhole page says **none of its four daily-tracked funds had published a November 9 file**, with November 6 still the latest complete day (−752,048 XRP / −$887K, four of four funds reported).

Other trackers still report:
- Alpha Finance: approximately −$10.4M for November 9 across five funds.
- CryptoETF.today: approximately −$10.3M, three of five funds reported.

The search-index state and earlier rendered page state conflict. The direct issuer pages accessible in this check did not independently confirm all three November 9 component files. Therefore downgrade the November 9 aggregate to **DISPUTED / NOT MODEL-ELIGIBLE** pending issuer-file re-fetch and byte-level receipt. Preserve the earlier tracker observation as a historical capture; do not silently overwrite it or average the provider values. The November 6 complete-day tracker figure is separate.

Sources: [CryptoKeyhole](https://cryptokeyhole.com/etf-flows/xrp/), [Alpha Finance](https://alphafinance.io/etf/xrp/), [CryptoETF.today](https://cryptoetf.today/en/xrp-etf-flows), [Canary issuer page](https://canaryetfs.com/xrpc/), [21Shares issuer page](https://www.21shares.com/en-us/products-us/toxr).

## Market-data freshness

Run121 remains the last validated direct exchange capture (OKX provider timestamp 06:40:33.969 UTC; Kraken response had no event timestamp) and Fuelmaps' 06:00 UTC spot-only depth snapshot. A subsequent web open of the exchange API URLs returned August 2026 cached payloads, so those responses were rejected as stale. Search results after Run121 were older or differently cached; no new synchronized spot/L2 capture is admitted. The 05:50 UTC TradRadar snapshot remains the last validated derivatives observation.

## Prediction and operational status

- The 40-source registry, raw-byte capture contracts, SHA-256 receipt chain, point-in-time SQLite feature store, four baselines, chronological walk-forward evaluation, calibration/drift diagnostics and Ed25519-gated forecast ledger remain implemented on the integration branch.
- The scheduled XRP workflow is main-only and absent from main. Production scheduled ingestion is not active.
- GitHub Actions artifact retention (90 days raw, 7 days per-run feature checkpoint, 90 days daily feature backup) is not independent WORM or trusted timestamp anchoring.
- Run122 web-rendered research did not preserve original HTTP transport bytes/headers. No raw-source hash is claimed; no observation is model-admitted.

**Forecast status: NOT_ISSUED.** No directional forecast, paper trade or real-money action occurred.

## Repository and merge status

- Main SHA: `d4d43be3427375cf79d190e768976de062e20287`.
- Parent integration head: `dd6abfd9fcf6196a2af0c4c10b7c186c6002423a`.
- PR #1640: 910 commits ahead, zero behind, 241 changed paths; GitHub reports mergeable.
- 62 review submissions: all COMMENTED, zero APPROVED.
- 22 review threads: all resolved and outdated.
- CodeRabbit check skipped.
- Branch-protection details remain HTTP 403; visible fallback ruleset disabled; Pages publication authorization unresolved.
- Open PR inventory remains 372 (356 drafts, 16 non-drafts). Run121's path-overlap classifications remain in force. Preserve unique #1643, #1653, #1614, #1269, #1655, #1659 and #1641; do not close exact-overlap candidates until successor content is merged and verified on main.

**Merge decision: BLOCKED.** No approval, no authoritative protection visibility and no Pages side-effect authorization. Do not bypass protection or merge.

## Next concrete actions

1. Verify exact-head full CI, dependency audit and fail-closed gate for the Run122 commit.
2. Obtain independent approval, authoritative branch-protection visibility and Pages-publication authorization.
3. Re-fetch November 9 issuer files directly, retain raw bytes and resolve the CryptoKeyhole/Alpha/CryptoETF.today disagreement before model admission.
4. Keep SBI START Bond as ¥10B debt issuance with a conditional XRP benefit, not XRP capital demand.
5. Treat the SBI Ripple Asia/Doppler MOU as exploratory until production product, assets, counterparties and volume are disclosed.
6. Obtain primary bank pilot data and Ripple confirmation before admitting the 60%/four-second or twelve-pair claims.
7. Replay Evernorth/BitGo transfers via direct rippled and establish destination ownership before classifying the 9.070M XRP inbound.
8. Activate XRP ingestion only after the mission manifest and workflow are on main; establish independent WORM/timestamp anchoring and complete synchronized history.
9. Preserve unique PR work; close only exact duplicates after verified successor merges.

No merge, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push or destructive worktree operation occurred.


---

# Barrot XRP Mission — Run121: Fresh Spot Depth, Derivatives and Attribution Audit

**Checked 2026-11-10 around 06:47 UTC.** This addendum supersedes only the Run120 02:00 UTC order-book snapshot and the older 05:30 UTC derivatives snapshot. It preserves Run120 and its complete exact-head CI evidence.

## Run120 exact-head verification completed

Run120 handoff/artifact commit: `43aa63532969f61ad677a443f4bdcf2dc0f46e9d`.

Its exact-head checks have now all completed successfully:

- Full repository suite: **1,347 passed, zero failed, 8 subtests passed**.
- Inclusive coverage: **59.48%**, above the 53% floor.
- Core suite: 677 passed, 8 subtests passed.
- Complete development dependencies installed; all repository tests executed.
- Wheel built and installed; installed package verified Barrot V3, the XRP mission and canonical data assets.
- Six dependency manifests passed; zero known vulnerabilities.
- Fail-closed gate passed; automatic merging remains disabled.

Evidence: [Full CI 42770438065](https://github.com/Barrot-Agent/B-Agent/actions/runs/42770438065), [dependency audit 42770437956](https://github.com/Barrot-Agent/B-Agent/actions/runs/42770437956), [fail-closed gate 42770437998](https://github.com/Barrot-Agent/B-Agent/actions/runs/42770437998).

The Run121 handoff/artifact commit is a new head and must receive its own exact-head checks. Do not transfer Run120's test result to it.

## Fresh exchange snapshot

Capture window around 2026-11-10 06:40–06:47 UTC:

- Kraken XRP/USD: last **$1.09923**, bid **$1.09909**, ask **$1.09921**, displayed spread about **1.09 bps**, 24-hour volume **26.0836M XRP**, VWAP **$1.09399877**, high **$1.10404**, low **$1.07502**. The ticker response contains no provider event timestamp.
- OKX XRP-USDT: last **1.0999 USDT**, bid **1.0997**, ask **1.0998**, 24-hour volume **65.1118M XRP**, high **1.1167**, low **1.0764**, provider timestamp **2026-11-10T06:40:33.969Z**.
- Kraken USDT/USD: bid **0.99866**, ask **0.99867**, midpoint **0.998665**. Mechanically normalized OKX last is approximately **$1.098437**, about **0.0721% below** Kraken's last. The quote conversion is sampled separately and the snapshots are asynchronous; this is not an executable arbitrage signal.

Sources: [Kraken XRP/USD](https://api.kraken.com/0/public/Ticker?pair=XRPUSD), [OKX XRP-USDT](https://www.okx.com/api/v5/market/ticker?instId=XRP-USDT), [Kraken USDT/USD](https://api.kraken.com/0/public/Ticker?pair=USDTUSD).

## Newest accessible spot-only order-book snapshot

Fuelmaps published its **06:00 UTC, November 10** hourly XRP spot-book snapshot across Coinbase, OKX, Kraken, Bitstamp, Bitfinex and Gemini:

- Mid: **$1.0977**; 6 of 6 venues cover ±5%.
- ±0.5%: **$9.1M bids / $6.5M asks**, 58.5% bid share.
- ±1%: **$13.8M bids / $10.8M asks**, 56.0% bid share.
- ±2%: **$18.3M bids / $11.6M asks**, 61.2% bid share.
- ±5%: **$24.4M bids / $14.2M asks**, 63.3% bid share.
- ±10%: **$33.2M bids / $15.6M asks**, 68.0% bid share; 5 of 6 venues cover this wider band.
- Largest displayed nearby levels: bids $2.5M at $1.050, $2.2M at $1.000, $2.1M at $1.095 and $1.8M at $1.092; ask $1.7M at $1.099.

This replaces the older Run120 02:00 UTC depth snapshot for current market context. Fuelmaps publishes one-minute-book averages in hourly columns; its 06:00 snapshot was published at 06:05 UTC and is approximately 42 minutes old at this check. Binance and Bitget are not included. Full-depth venues and near-price venues have different reach, so venue coverage must remain a feature. Resting orders can be cancelled and are not commitments.

Source and methodology: [Fuelmaps spot order-book heatmap](https://fuelmaps.io/order-book/).

## Updated perpetual derivatives

TradRadar's newest accessible snapshot is **2026-11-10 05:50 UTC**, with a 15-minute reporting delay:

- Mark price $1.1007; 24-hour price change +0.18%.
- Seven-exchange open interest **$1.66B**, down **3.97%** over 24 hours.
- OI-weighted funding **+0.0069% per 8 hours**.
- 24-hour liquidations at least **$7.58M**: $6.80M longs and $777.69K shorts.
- Account long/short ratio **3.90**, 79.6% long.

The older Run120 TradRadar 05:30 snapshot is superseded by this 05:50 observation. Liqwall's $1.22B and Alpha Finance's $2.48B are older aggregates with different venue coverage; do not average them with TradRadar's seven-exchange $1.66B. The current common description remains declining OI and long-heavy reported liquidation, not a directional price signal.

Source: [TradRadar XRP futures market data](https://tradradar.io/markets/xrp).

## ETF and CFTC status — unchanged since Run120

CryptoKeyhole still reports the November 9 partial as **−9,216,553 XRP / approximately −$10.1M**, 3 of 4 daily-tracked funds, with Franklin XRPZ missing. The displayed component integers sum to −9,216,552 XRP, a one-XRP display difference. Alpha Finance's approximately −$10.4M across five funds and CryptoETF.today's approximately −$10.3M across three of five remain separate coverage/methodology observations. Do not average.

The official CFTC TFF futures-only report remains as of November 3. It lists CME XRP, Coinbase Nano XRP and Coinbase Nano XRP Perp Style; contract-size-normalized OI is 396.2485M XRP-equivalent. Leveraged funds are net +280 CME contracts, −2,308 Nano contracts and −27,774 Nano Perp Style contracts. Keep the products and trader classifications separate.

## Evernorth/BitGo custody attribution

No new primary-source wallet ownership evidence was obtained. Retain Run120's classification: the October 23/28 multisig transfers are BitGo-originated custody movements; a custody reallocation is plausible, but beneficial owner and Evernorth attribution remain unresolved. The 9.070M XRP combined inbound is not confirmed new Evernorth capital, an exchange inflow or a sale.

## Kamilah/Camilla Stevenson channel-attribution update

A public channel-index search surfaced `@drkamilahstevenson` (channel ID candidate `UCqUPJMQdkCN6lsLVDnichPA`) with a matching investing/crypto/macro channel description; third-party counters disagree at approximately 138K versus 143K subscribers. Another directory lists `@CoachKamilahStevensonxrp` and `@KamilahStevensonDigitalNetwork` with near-identical descriptions but much smaller counts. YouTube's direct channel page could not be fully fetched in this check, and no independent cross-link established that these channels are controlled by the previously corroborated person. Treat all three as **unverified channel candidates**; add no personal-channel video to the verified inventory. Prior guest-appearance bylines remain separate.

The connected vidIQ account returned an insufficient-credit response; no credits were charged and the tool instructed not to retry. Public search results were used instead. This does not establish channel ownership.

## Prediction and operational status

- The 40-source registry, raw-byte capture contracts, SHA-256 receipt chain, point-in-time feature store, four baselines, chronological walk-forward evaluation, calibration/drift diagnostics and Ed25519-gated forecast ledger remain implemented on the integration branch.
- XRP scheduled ingestion remains main-only and is absent from main; no production ingestion run is active.
- GitHub Actions raw artifacts are retained for 90 days, per-run feature checkpoints for 7 days and daily backups for 90 days. This is not independent WORM storage or trusted timestamp anchoring.
- Run121 web-rendered observations did not retain original HTTP transport bytes/headers. No raw-source hash is claimed and no observation is model-admitted.
- Complete synchronized historical spot/L2/derivatives/exchange-flow/collateral data, independent WORM/timestamp anchoring, sufficient shadow outcomes and demonstrated out-of-sample lift remain outstanding.

**Forecast status: NOT_ISSUED.** No directional forecast, paper trade or real-money action occurred.

## Repository, workflows and merge gates

Main remains `d4d43be3427375cf79d190e768976de062e20287`. Run120's verified parent integration head was `43aa63532969f61ad677a443f4bdcf2dc0f46e9d`; this Run121 update creates a new descendant requiring exact-head CI.

PR #1640 remains the only V3/XRP integration path. It was 909 commits ahead, zero behind, 240 changed paths before this update. The full open inventory remains 372 (356 drafts, 16 non-drafts). Review state remains 62 COMMENTED submissions, zero approvals; 22 threads are resolved and outdated; CodeRabbit is skipped. Branch-protection details remain inaccessible (HTTP 403), the visible fallback ruleset is disabled, and Pages publication authorization is unresolved.

Main workflow repair status:
- Hover Bike's main workflow failed because its generation step ran inside `hover_bike_revolution` while the generator and artifact paths assumed repository-root execution. The integration branch moves both generator steps to repository-root execution. `tests/test_hover_bike_workflow.py` asserts this path contract, and the full Run120 suite passed it. End-to-end dispatch on the integration branch remains unverified.
- Riemann Harvest's main workflow failed because the shared pytest conftest imports `pydantic-settings`. The integration branch installs `pydantic-settings` before its subsystem test. A successful integration workflow dispatch remains unverified.
- Pillars Consistency Check remains blocked by missing GitHub App credentials, Databricks HTTP 403 and Hugging Face Space BUILD_ERROR. It remains read-only and fail-closed. No secret rotation or external write occurred.
- Main Cross Analysis continues to complete hourly as a read-only, artifact-only workflow. It is not the XRP ingestion workflow.

Open-PR overlap classifications from Run120 remain in force: preserve unique #1643, #1653, #1614, #1269, #1655, #1659 and #1641; retain exact-overlap/superseded candidates #1642, #1317/#1318/#1320 and dependency candidates #1644–#1650/#1254/#1255 until a successor is merged and verified on main. No PRs were closed.

**Merge decision: BLOCKED.** No independent approval, no authoritative branch-protection visibility and no Pages side-effect authorization. Do not bypass protection or merge.

## Next concrete actions

1. Verify exact-head full CI, dependency audit and fail-closed gate for the Run121 commit.
2. Obtain independent approval, authoritative branch-protection visibility and Pages-publication authorization.
3. After Franklin publishes, reconcile the final November 9 ETF issuer files without treating missing values as zero.
4. Replay Evernorth/BitGo transactions through a direct public rippled endpoint; establish destination ownership before classifying the 9.070M XRP inbound.
5. Activate the XRP workflow only after its mission manifest and workflow are safely on main; verify first scheduled capture, raw receipts and feature-store restore.
6. Establish independent WORM/timestamp anchoring and complete synchronized historical features before any forecast.
7. Preserve unique PR work; close only exact duplicates after verified successor merges.

No merge, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push or destructive worktree operation occurred.


---

# Barrot XRP Mission — Run120: Market, ETF, CFTC TFF and Integration Audit

**Updated 2026-11-10T06:35:24Z.** This update preserves Run119 and adds a new point-in-time research and repository audit. The tested code parent is `4d4a752aaa000353b4522bb8f83e7f7fe16d021b`; the combined handoff/artifact commit created by this run requires its own exact-head CI verification.

## Current repository state

- Main SHA: `d4d43be3427375cf79d190e768976de062e20287`.
- Integration branch: `integration/core-capabilities-mmi-structural-paper-20261104`; parent head before this update: `4d4a752aaa000353b4522bb8f83e7f7fe16d021b`.
- Existing integration PR: [#1640](https://github.com/Barrot-Agent/B-Agent/pull/1640), 908 commits ahead, zero behind, 239 changed paths.
- Main tree: 1,404 entries, 1,299 files, 493 Python files, 87 test modules, 86 workflow files, 30 XRP research artifacts.
- Integration tree: 1,536 entries, 1,423 files, 568 Python files, 145 test modules, 87 workflow files, 69 XRP research artifacts.
- Main does not contain `data/missions/primary_mission.json`, `barrot_agent/data/missions/primary_mission.json`, or `.github/workflows/xrp-public-ingestion.yml`. Those remain on the integration branch.

## Exact-head verification on the parent code head

On `4d4a752aaa000353b4522bb8f83e7f7fe16d021b`:

- Full repository suite: **1,347 passed, zero failed, 8 subtests passed**.
- Inclusive coverage: **59.48%**, above the 53% floor.
- Core suite: 677 passed, 8 subtests passed.
- Wheel build and installed-wheel verification passed, including Barrot V3, the XRP mission and canonical data assets.
- Six dependency manifests passed audit; zero known vulnerabilities.
- Fail-closed merge gate passed; automatic merging remains disabled.

Evidence: [Full CI 42764891140](https://github.com/Barrot-Agent/B-Agent/actions/runs/42764891140), [dependency audit 42764891132](https://github.com/Barrot-Agent/B-Agent/actions/runs/42764891132), [fail-closed gate 42764891383](https://github.com/Barrot-Agent/B-Agent/actions/runs/42764891383).

**Verification boundary:** this run adds only a research artifact and this handoff update, but that new commit is a different head. Do not transfer the parent test result to the new commit. Its exact-head CI must complete independently.

## PR #1640 review and merge gates

- GitHub reports the PR mergeable and clean.
- 62 review submissions: all COMMENTED; zero APPROVED.
- 22 review threads: all 22 resolved; all 22 marked outdated.
- CodeRabbit's latest review check was skipped.
- Main branch-protection API returns HTTP 403, “Resource not accessible by integration.”
- The visible repository ruleset “Fall Back” is disabled.
- GitHub Pages previously deployed automatically after a main push. PR #1640 changes seven public web assets; authorization for that automatic publication remains unresolved.

**Decision: BLOCKED; do not merge.** The conditional merge authorization is not satisfied. No branch-protection bypass was attempted.

## Open PR inventory and overlap classification

The complete open inventory is 372 PRs: 356 drafts and 16 non-drafts.

- **#1640:** sole active V3/XRP integration path; blocked pending independent approval, authoritative branch-protection visibility and Pages side-effect authorization.
- **#1643:** 670 changed paths; 7 overlap #1640 and 663 are unique research evidence. Preserve; do not close.
- **#1653:** 7 changed paths; one CI overlap and 6 unique repository-knowledge-graph paths. Preserve; 8 review threads remain unresolved.
- **#1642:** 7/7 changed paths overlap #1640. Superseded-content candidate; retain until successor is merged and verified on main.
- **#1614:** 57 changed paths; 8 overlap and 49 are unique prediction/clock research. Preserve the unique work.
- **#1317:** 6/6 paths overlap #1640; superseded candidate.
- **#1318:** 2/2 paths overlap #1640; superseded candidate.
- **#1320:** 5/5 paths overlap #1640; superseded candidate.
- **#1644:** 8/8 workflow paths overlap #1640.
- **#1645:** 1/1 workflow path overlaps #1640.
- **#1646 and #1648:** each changes `requirements-dev.txt`, which overlaps #1640.
- **#1647:** 6/6 workflow paths overlap #1640.
- **#1649 and #1650:** each changes `legacy/requirements_legacy.txt`, which overlaps #1640.
- **#1254 and #1255:** each changes only `legacy/requirements_legacy.txt`; older dependency candidates, fully overlapping #1640.
- **#1269:** 9 changed paths; 8 unique mesh/topology paths and one CI overlap. Preserve.
- **#1655:** 8 changed paths; 3 unique source-catalog/structural README paths and 5 overlaps. Preserve unique material.
- **#1659:** 6 changed paths; 4 unique local inference/documentation/test paths and 2 overlaps. Preserve unique material.
- **#1641:** 3/3 unique autonomous-experimentation paths. Preserve.

No PRs were closed. No unique research, mesh, knowledge-graph, prediction or experimentation work was bulk-closed. Dependency candidates require version/diff reconciliation against the single integration path before any merge.

## Main-branch scheduled workflow audit

- Main has no XRP public-ingestion workflow. The integration branch's `xrp-public-ingestion.yml` is guarded by `github.ref == refs/heads/main`; it is therefore not operational from this branch.
- Main's Cross Analysis workflow is `contents:read`, uses `persist-credentials:false`, uploads read-only analysis artifacts and does not commit or push repository files. The latest inspected run completed successfully.
- Main Pillars Consistency Check failed closed: missing GitHub App ID/private key/installation ID, Databricks HTTP 403, Hugging Face Space `BUILD_ERROR`. No secrets were rotated and no external writes were attempted.
- Main Hover Bike workflow failed artifact upload because its four expected output files were absent.
- Main Riemann Harvest workflow failed test bootstrap because `pydantic` was unavailable through the shared test conftest. The integration workflow now installs `pydantic-settings`, but a successful integration-branch dispatch has not been verified.
- The XRP workflow uploads raw-source artifacts with 90-day retention, per-run feature-store checkpoints with 7-day retention and daily feature-store backups with 90-day retention. These are GitHub Actions artifacts, not independent WORM storage or trusted timestamp anchoring. Cache is a convenience/fallback, not an immutable archive.

## XRP spot and quote-normalization snapshot

Capture cutoff: 2026-11-10T06:35:24Z.

- Kraken XRP/USD response: last **$1.09923**, bid **$1.09909**, ask **$1.09921**, displayed spread approximately **1.09 bps**, 24-hour volume **26.0836M XRP**, 24-hour VWAP **$1.09399877**, high **$1.11573**, low **$1.07502**. Kraken did not supply a provider event timestamp in the returned ticker.
- OKX XRP-USDT: last **1.0986 USDT**, bid **1.0986**, ask **1.0987**, 24-hour volume **66.69499M XRP**, provider event timestamp **2026-11-10T06:10:20.977Z**.
- Kraken USDT/USD: bid **0.99866**, ask **0.99867**, midpoint **0.998665**. Mechanical normalization gives OKX last approximately **$1.097133**, about **0.191% below** Kraken's last. The snapshots are asynchronous and quote conversion is itself sampled separately; this is not an executable arbitrage signal.

Sources: [Kraken XRP/USD ticker](https://api.kraken.com/0/public/Ticker?pair=XRPUSD), [OKX XRP-USDT ticker](https://www.okx.com/api/v5/market/ticker?instId=XRP-USDT), [Kraken USDT/USD ticker](https://api.kraken.com/0/public/Ticker?pair=USDTUSD).

## Spot order-book depth

Fuelmaps' six-venue **spot-only** snapshot at **2026-11-10 02:00 UTC** covered Coinbase, OKX, Kraken, Bitstamp, Bitfinex and Gemini:

- Within ±0.5%: $9.6M bids / $6.7M asks; 58.8% bid share.
- Within ±1%: $14.0M bids / $11.2M asks; 55.5% bid share.
- Within ±2%: $18.6M bids / $12.9M asks.
- Within ±5%: $24.7M bids / $15.1M asks.
- Six of six venues reporting at ±5%.

This snapshot is 4 hours 35 minutes old at the capture cutoff. It is not current executable depth; displayed orders can be cancelled. A fresh direct raw L2 capture was not obtained in this run.

Source: [Fuelmaps spot order-book heatmap](https://fuelmaps.io/order-book/).

## Perpetual derivatives and liquidation disagreement

- TradRadar, updated **05:30 UTC**: seven-exchange open interest **$1.65B**, 24-hour OI change **−4.12%**, OI-weighted funding **+0.0063% per 8 hours**, 24-hour liquidations **at least $8.40M** (longs $7.65M; shorts $0.749M), account long/short ratio 3.89 (79.5% long).
- Liqwall, earlier **02:22 UTC** snapshot: approximately $1.22B OI.
- Alpha Finance, earlier **01:40 UTC** snapshot: approximately $2.48B OI; modeled long/short liquidation clusters are estimates from leverage tiers, not verified executions.

These aggregates have different venue coverage and timestamps. Do not average them. The fresh TradRadar observation supports declining OI and long-heavy reported liquidation, not a directional price forecast.

Sources: [TradRadar](https://tradradar.io/markets/xrp), [Liqwall](https://liqwall.com/coins/xrp), [Alpha Finance](https://alphafinance.io/liquidation-heatmap/xrp/).

## ETF issuer-flow reconciliation — November 9 partial

CryptoKeyhole updated at **06:12 UTC** and had issuer files for 3 of its 4 daily-tracked funds:

- Bitwise XRP: **−8,594,551 XRP**, issuer file stamped 05:51 UTC.
- Canary XRPC: **−427,341 XRP**, published 05:22–05:27 UTC.
- 21Shares TOXR: **−194,660 XRP**, issuer stamp 05:01 UTC.
- Franklin XRPZ: not yet published for November 9.

CryptoKeyhole's displayed total is **−9,216,553 XRP / approximately −$10.1M**. The three displayed component integers sum to −9,216,552 XRP, a 1-XRP display/reconciliation difference that is preserved rather than silently adjusted.

Cross-provider disagreement:
- Alpha Finance reports approximately **−$10.4M** through the November 9 session across five funds.
- CryptoETF.today reports approximately **−$10.3M**, 3 of 5 funds reported.
- CryptoKeyhole reports approximately **−$10.1M**, 3 of its 4 daily-tracked funds reported.

These are different universes, file vintages and valuation methods. Do not average. CryptoKeyhole's complete-day cumulative figure through November 6 remains **+2,622,459 XRP / +$3.45M** and explicitly excludes the November 9 partial.

Sources: [CryptoKeyhole issuer-file tracker](https://cryptokeyhole.com/etf-flows/xrp/), [Alpha Finance ETF tracker](https://alphafinance.io/etf/xrp/), [CryptoETF.today](https://cryptoetf.today/en/xrp-etf-flows).

## CFTC Traders in Financial Futures — November 3 report

The official CFTC **futures-only TFF** report lists three XRP products. Contract sizes differ:

| Product | CFTC code | Open interest | Leveraged funds long / short | Net |
|---|---:|---:|---:|---:|
| CME XRP, 50,000 XRP/contract | 176740 | 7,216 | 1,976 / 1,696 | +280 |
| Coinbase Nano XRP, 500 XRP/contract | 176LM1 | 32,505 | 29,317 / 31,625 | −2,308 |
| Coinbase Nano XRP Perp Style, 500 XRP/contract | 176LM3 | 38,392 | 1,780 / 29,554 | −27,774 |

Contract-size-normalized open interest is **396.2485M XRP-equivalent** (360.8M CME + 16.2525M Nano + 19.196M Nano Perp Style). This is XRP-equivalent contract exposure, not cash capital, collateral, spot demand or net directional risk.

The CME leveraged-fund cohort is net long while both Coinbase Nano products are net short. Treat these instruments separately; leveraged funds may use basis and cross-venue hedges. Do not collapse them into a single bullish/bearish position. This TFF classification is also distinct from the Legacy COT non-commercial grouping.

Primary sources: [CFTC TFF futures-only report](https://www.cftc.gov/dea/futures/financial_lf.htm), [CFTC TFF options-and-futures combined report](https://www.cftc.gov/dea/options/financial_lof.htm).

## Evernorth / BitGo custody attribution correction

- Evernorth's SEC prospectus states that all XRP owned by the company is initially held in custody accounts at BitGo Bank & Trust, National Association. [SEC Form 424B3](https://www.sec.gov/Archives/edgar/data/2092592/000162828026072223/evernorth-424b3.htm).
- Q-Eternal reports the October 28 transfer of **3,846,153.846152 XRP** from `rUWUJ2F3aZknSd8PVutoMnxowMK792maTD` to `rBKrEjXChk7iWTx1cdr2EpBVoXRZ2Bunhj`, ledger 107963318, destination tag 2. The amount equals 5,000,000 / 1.3 to six decimal places; this arithmetic does not prove consideration or a $5M purchase. [Q-Eternal October 29 analysis](https://q-eternal.com/blog/2026-10-29/).
- Bithomp shows both addresses as multisignature accounts activated by a BitGo account. The source has no username, was activated in 2019 and currently displays about 26.6M XRP. The destination has no username, was activated by BitGo on October 20, 2026 and currently displays about 96.2M XRP. These facts establish BitGo activation/multisig, not beneficial ownership by Evernorth. [Source account](https://bithomp.com/account/rUWUJ2F3aZknSd8PVutoMnxowMK792maTD), [destination account](https://bithomp.com/account/rBKrEjXChk7iWTx1cdr2EpBVoXRZ2Bunhj).
- XRP Insights' latest read is ledger **108,233,072**, closed **2026-11-10 05:45 UTC**: 103,129,905 XRP in 13 attributed wallets, with 370,346,663 XRP moved outside that attributed set through October 22. The tracker does not attribute the destination account above. [XRP Insights Evernorth tracker](https://xrp-insights.com/xrp-radar/evernorth).

Classification: **BitGo-originated multisig-to-multisig custody transfer; probable custody reallocation is a competing hypothesis, but beneficial owner and Evernorth attribution remain unresolved.** It is not evidence of an exchange deposit, executed sale or confirmed new Evernorth purchase. Keep the 9.070M XRP combined October 23/28 inbound out of confirmed new-capital and exchange-flow features until direct ledger replay and ownership evidence resolve it.

## Macro event clock

BLS schedules October 2026 CPI and Real Earnings for **Tuesday, November 10 at 08:30 ET / 13:30 UTC**. At this capture, release is still in the future. Do not treat consensus or pre-release estimates as actual data. [BLS CPI release page](https://www.bls.gov/news.release/cpi.htm).

## Prediction-engine and ingestion status

Implemented on the integration branch:
- 40 registered public source records: 36 hourly, two weekly CFTC, two non-commercial XRPL nodes excluded from collection.
- Raw-source byte capture/receipt contracts and SHA-256 receipt-chain validation.
- Point-in-time feature validator that requires provenance hashes and rejects post-cutoff or late-ingested records.
- SQLite feature store; four deterministic baselines; chronological walk-forward evaluator with purge/embargo; calibration and drift diagnostics.
- Fixed-horizon forecast ledger; raw receipt bytes are rechecked during readiness-report registration; trusted independent Ed25519 evaluator key is required.

Operational boundary:
- Scheduled ingestion is guarded to run only on main; the workflow and mission manifests are not on main.
- Raw receipts are configured as 90-day GitHub Actions artifacts; per-run feature-store checkpoints 7 days; daily feature-store backups 90 days. This is not independent WORM retention or trusted timestamp anchoring.
- Independent external timestamp/WORM anchoring, complete synchronized history, effective-sample-size correction, sufficient independent shadow outcomes and demonstrated out-of-sample lift remain outstanding.

**Forecast status: NOT_ISSUED.** No directional forecast, paper trade or real-money action occurred. Run120 web observations are research-only: original transport bytes/headers were not retained, so no raw-byte receipt hash was fabricated and no feature was admitted to the model.

## Nine-platform authentication and data flow

- ChatGPT: current-session GitHub read/write and public-web research exercised.
- Copilot: prior one-off COMMENTED PR review activity; no approval and no separately verified persistent data flow.
- Claude, Grok, Gemini and Codex: unverified.
- Hugging Face: prior build error; no deployment.
- Kaggle: untested; no submission.
- Databricks: prior HTTP 403; no workspace write.

No persistent authenticated nine-platform exchange occurred and no external model received repository data.

## Next concrete actions

1. Verify exact-head full CI, dependency audit and fail-closed gate on the new Run120 commit; do not inherit parent results.
2. Obtain independent approving review and authoritative branch-protection visibility; resolve authorization for the automatic GitHub Pages side effect.
3. Activate XRP public ingestion only after the mission workflow is safely present on main; verify first scheduled run, raw receipts, feature-store restore, and source failures.
4. Establish independent WORM/timestamp anchoring beyond GitHub Actions' 90-day artifact retention.
5. Replay the October 22–28 Evernorth/BitGo transfers against a direct public rippled endpoint; resolve address ownership and the 9.070M XRP inbound classification.
6. Reconcile final November 9 ETF issuer files after Franklin publishes; preserve missing values as missing, not zero.
7. Capture the October CPI release only after BLS publication and maintain event-time boundaries.
8. Continue synchronized historical spot, spot L2, derivatives, exchange-flow and collateral ingestion; evaluate out-of-sample performance and shadow outcomes before any forecast.
9. Preserve unique #1643, #1653, #1614, #1269, #1655, #1659 and #1641 material. Close only exact duplicates after successor content is merged and verified on main.

No merge, intentional deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push or destructive worktree operation occurred.


---

# Barrot XRP Mission — Run119: Second BitGo Inbound and Primary Custody Disclosure

**Updated 2026-11-10T05:52:25Z · Supersedes the Run118 treatment of the rUWUJ-to-rBKr transfer as a single 5.2236M XRP event.**

## Exact-head verification before Run119 commit

Run118 head a1fca1dab45c1ba50a73fa5201e7a215bbc795c2 passed:
- Full repository suite: **1,347 passed, zero failed, 8 subtests passed**; inclusive coverage **59.48%**, above the 53% floor.
- Core suite: passed; 677 tests and 8 subtests.
- Installed wheel, Barrot V3 import and packaged XRP mission: passed.
- Six-manifest dependency audit: passed, zero known vulnerabilities.
- Fail-closed gate: passed; automatic merge disabled.
- Cache save warning was non-fatal; cache budget is read-only.

Evidence: [Full CI 42764448841](https://github.com/Barrot-Agent/B-Agent/actions/runs/42764448841), [dependency audit 42764448862](https://github.com/Barrot-Agent/B-Agent/actions/runs/42764448862), [fail-closed gate 42764448846](https://github.com/Barrot-Agent/B-Agent/actions/runs/42764448846).

## Second BitGo-to-BitGo inbound: 3.846M XRP on October 28

Q-Eternal reports a second payment from rUWUJ2F3aZknSd8PVutoMnxowMK792maTD to rBKrEjXChk7iWTx1cdr2EpBVoXRZ2Bunhj on October 28 at 18:02:02Z, ledger 107963318: **3,846,153.846152 XRP**, destination tag 2. This is the same source, destination and tag as the 5,223,608.29 XRP transfer on October 23 at ledger 107840300. The October 28 amount equals 5,000,000 / 1.3 to six decimal places; this arithmetic does not prove $5M consideration. [Q-Eternal, October 29](https://q-eternal.com/blog/2026-10-29/).

The two inbound payments total **9,069,762.136152 XRP**. Q-Eternal reports the ten-account set rose from 477,900,062.52 XRP at ledger 107956087 to 481,746,216.37 XRP at ledger 107977763, with the other nine accounts unchanged.

### Primary issuer disclosure changes the interpretation

Evernorth’s November 9 SEC prospectus states that all XRP the company owns is initially held in custody accounts at BitGo Bank & Trust, N.A.; custodial contracts generally do not restrict reallocating XRP among custodians; and the company says it does not actively trade XRP on digital-asset markets. It identifies Coinbase as its principal market for financial-reporting purposes. [SEC prospectus, lines 941 and 3055–58](https://www.sec.gov/Archives/edgar/data/2092592/000162828026072223/evernorth-424b3.htm).

This is primary evidence that BitGo is Evernorth’s initial custodian and makes internal BitGo-to-BitGo reallocation a strong hypothesis. It does not identify rUWUJ or rBKr as Evernorth-owned addresses, and it does not prove that the 9.070M XRP is a new purchase.

### Reconciliation against the disclosed closing holdings

- Company-reported closing holdings: 473,276,430.423935 XRP.
- The ten-account base before the two inbound transfers is derived at 472,676,454.233848 XRP.
- The 8-K separately discloses 600,000 XRP from Advance Funding Subscribers. Company-reported holdings less 600,000 XRP equal 472,676,430.423935 XRP, only 23.81 XRP below the derived ten-account base.
- After the two inbound transfers, the ten-account total is 481,746,216.37 XRP, **8,469,785.95 XRP above** the company-reported closing holdings.

This arithmetic suggests the 600,000 advance-subscriber tranche is outside the ten-account table and the two later payments add approximately 9.070M XRP to that wallet set. It does not establish who beneficially owns the additional XRP. The ten-account set may include existing Evernorth holdings moved from another BitGo account, an undisclosed acquisition/contribution, or third-party/shared custody funds.

### Competing hypotheses and model treatment

1. **Internal BitGo custody transfer of existing Evernorth XRP:** supported by the SEC BitGo custody disclosure, BitGo-created multisig source/destination accounts, repeated destination tag 2, and Evernorth’s statement that it does not actively trade XRP. No source-account ownership attestation is available.
2. **Additional Evernorth acquisition or contribution:** supported by the two 9.070M XRP inbound payments, the ten-account balance increase, and the second transfer’s exact 5M/1.3 arithmetic. No SEC filing or company announcement confirms it.
3. **Third-party/shared BitGo custody allocation:** supported by the source account’s many destination-tagged movements and lack of a public Evernorth label. BitGo-created multisig status alone does not identify the beneficial owner.

Current classification: **UNATTRIBUTED BITGO CUSTODY INBOUND / POSSIBLE TREASURY ALLOCATION**. No exchange destination or sale execution was identified. Do not count these transfers as actual Evernorth capital, purchases, exchange inflows or directional features until ownership and economic purpose are established.

Run118’s 370.347M wallet-set outflow remains classified as probable internal BitGo custody reorganization, not selling. Keep the 2-XRP row-sum discrepancy, tracker-versus-Q-Eternal transaction-count mismatch and ledger-index/time inconsistency unresolved.

## Run119 structured evidence

[Run119 Evernorth BitGo inbound reconciliation](research/xrp_intelligence/20261110T055225Z-run119-evernorth-bitgo-inbound-reconciliation.json)

Next: replay both inbound transactions on validated XRPL ledgers 107840300 and 107963318; verify account signer/quorum metadata; reconcile the 600K advance-subscriber tranche; check subsequent SEC disclosures; and keep all movements model-ineligible until beneficial ownership is established.

---

# Barrot XRP Mission — Run118 Evernorth Custody-Flow Reconciliation

**Updated 2026-11-10T05:46:46Z. This corrects the Run114/Run116 treatment of Evernorth's 370.35M XRP wallet-set outflow.**

## Exact-head verification before Run118 commit

Run117 head c22ee9905bfcd795a9faf0385a20e7397e4f594b passed all exact-head gates:
- Full repository suite: **1,347 passed, zero failed, 8 subtests passed**; inclusive coverage **59.48%**, above the 53% floor.
- Core suite: 677 passed, 8 subtests passed.
- Installed wheel, Barrot V3 import, packaged XRP mission and canonical data assets: passed.
- Six-manifest dependency audit: passed, zero known vulnerabilities.
- Fail-closed gate: passed; automatic merge disabled.
- Actions cache is read-only; cache save failed after test and wheel verification. Setuptools metadata/package-discovery warnings are non-fatal.

Evidence: [Full CI 42763890424](https://github.com/Barrot-Agent/B-Agent/actions/runs/42763890424), [dependency audit 42763890408](https://github.com/Barrot-Agent/B-Agent/actions/runs/42763890408), [fail-closed gate 42763890620](https://github.com/Barrot-Agent/B-Agent/actions/runs/42763890620).

## Material Evernorth finding: 370.35M XRP is probably a BitGo custody reorganization, not selling

XRP Insights reports 103.130M XRP in 13 attributed Evernorth wallets and 370.347M moved to addresses outside that 13-wallet set. Its field means outside the attributed set; it does not mean exchange deposit or sale. [Tracker JSON](https://xrp-insights.com/xrp-radar/evernorth/data.json).

Q-Eternal's independent public-ledger analysis reports an October 22 batch of 16 Payment transactions from 9 source wallets to 10 destination wallets, ledger indexes 107832376–107832379. It reports all 19 involved accounts were 2-of-3 multisig accounts created by BitGo's initialization wallet. [Q-Eternal, October 23](https://q-eternal.com/blog/2026-10-23/).

Bithomp independently shows the BitGo initializer and inspected destinations as multisig accounts activated by that initializer:
- [BitGo initializer](https://bithomp.com/account/rD4G6gtD2KwHqsRf7pcyA8r1neUzXT61ix).
- [rK1BU](https://bithomp.com/account/rK1BUXU1LD3JEkRLCqY9pKq4BEVKmDrzbf), [rJQ4](https://bithomp.com/account/rJQ4sQVyoYT2SfRNJRXXfqU4rHS915UAjW) and [rLyTy](https://bithomp.com/account/rLyTyA4nQJMy7T2wgKrd33KeZdjcEMPc2w): approximately 52.8M XRP each.
- [rwtoky](https://bithomp.com/account/rwtokyDZhkRwcC6h7b58Bv11tPFEdtJ9EW) and [rDFr](https://bithomp.com/account/rDFrBJGy2QMNphpknEWLjmrDsavmUewVrh): approximately 42.3M XRP each.
- [rMNW](https://bithomp.com/account/rMNWpkSN7iJaxmsf61uGWn1qWCeZ6STmyw) and [rHuRnn](https://bithomp.com/account/rHuRnnWDUB4UBy8Sf2XvJDMEC4rFgts1xi): approximately 200K XRP each; [rLMYD](https://bithomp.com/account/rLMYD4r2WMsReN42naTzDLc8MAmHAbjyw5): approximately 100K.
- [rPhQdy](https://bithomp.com/account/rPhQdyEaz4kcSoYKTAQhvkvdYxWKKw2vSC) and [rGy4](https://bithomp.com/account/rGy4zJtGfGtF7dtjZmBraQTcfZSQgwqpaa): approximately 50M and 52.8M XRP.
- [rBKr](https://bithomp.com/account/rBKrEjXChk7iWTx1cdr2EpBVoXRZ2Bunhj): approximately 96.2M XRP at the current explorer capture.

Q-Eternal's destination balances closely match SEC-disclosed contribution tranches: Arrington sponsor 211,319,096.061435 XRP versus about 211,319,104; Ripple 126,791,458 versus about 126,791,464; related-party entity 50M versus about 50,000,001; cash-purchased tranche 84,365,876.3625 versus about 84,365,878; delayed-funding XRP 200K versus about 200,001.

The closing 8-K separately discloses **600,000 XRP from Advance Funding Subscribers**. Q-Eternal's five-row destination table does not separately reconcile that 600K. Do not call the full 473,276,430 XRP closing amount completely mapped by that table. [Evernorth SEC 8-K](https://www.sec.gov/Archives/edgar/data/2092592/000119312526419146/d24481d8k.htm).

### Separate 5.2236M XRP inbound remains unattributed

Q-Eternal reports 5,223,608.29 XRP received by rBKr on October 23 at 02:47Z from rUWUJ2F3aZknSd8PVutoMnxowMK792maTD, destination tag 2. Both accounts are BitGo-created multisigs, but neither is publicly labeled Evernorth. The source account has many tagged movements and no verified Evernorth attribution. This could be a custody transfer or a possible purchase; it is not proof of an additional Evernorth acquisition or a BitGo omnibus account. No reviewed SEC filing confirms it. [Source account](https://bithomp.com/account/rUWUJ2F3aZknSd8PVutoMnxowMK792maTD).

### Discrepancies retained

- The tracker reports 370,346,663.22975004 XRP; its 18 displayed rows sum to approximately 370,346,661.22975, a 2-XRP difference.
- The tracker lists 18 movements across October 20–22; Q-Eternal reports 16 in the October 22 18:08:12–22 batch. The surfaced tracker rows show 13 in that exact 18:08 window plus one at 00:51:42. The counts are not reconciled.
- Run114 records ledger 108232177 at 03:45Z; the current tracker JSON says ledger 108232014 at 04:34:40Z. A lower index with a later timestamp is inconsistent. The tracker's older HTML snapshot also shows 108212382 at November 9 06:40Z. Do not treat these as one coherent point-in-time series.
- Direct rippled transaction replay was not completed. Q-Eternal is secondary ledger analysis; Bithomp is an independent explorer, not an Evernorth ownership attestation.

### Model and feature-taxonomy consequence

Classify 370.347M as **probable internal BitGo custody reorganization, high confidence**, not exchange netflow, sell pressure, tradable-float increase or confirmed distribution. Beneficial ownership of every destination is not proven.

Keep the raw wallet-set-outflow field, but do not alias it to exchange flow or sell pressure. Future classes must distinguish same-custodian reorganization, new custody wallet with owner unconfirmed, confirmed exchange deposit, confirmed exchange trade and unknown destination. Run110 already marks the exchange-balance dataset model-ineligible; preserve that fail-closed exclusion. No Run118 on-chain observation is model-admitted.

## Current integration and merge status

Before Run118 commit: main d4d43be3427375cf79d190e768976de062e20287; integration c22ee9905bfcd795a9faf0385a20e7397e4f594b; PR #1640 was 904 ahead, zero behind, 237 changed paths. It remains open and unmerged: 62 COMMENTED reviews, zero approvals; 22 inline threads resolved but outdated; branch-protection endpoint HTTP 403; visible fallback ruleset disabled; automatic Pages-publication authorization unresolved.

No PRs were closed. Preserve #1643 research, #1653 graph, #1269 topology, #1614 prediction work and unique draft material.

## Run118 structured evidence

[Run118 Evernorth–BitGo wallet reconciliation](research/xrp_intelligence/20261110T054646Z-run118-evernorth-bitgo-wallet-reconciliation.json)

Next: replay the October 22–23 transactions with an accessible public rippled endpoint or second ledger explorer; resolve the 600K advance-subscriber allocation, 2-XRP row-sum difference and ledger-index/time mismatch; determine whether rUWUJ/rBKr are custody-only or linked to a disclosed acquisition. Keep these movements excluded from directional model features until resolved.

---

# Barrot XRP Mission — Run117 Primary-Source Correction

**Updated 2026-11-10T05:42:27Z · Supersedes the Run116 institutional-charter uncertainty and supplements the Run116 ETF snapshot.**

## Verified exact-head baseline before Run117 commit

Run116's final handoff head `038af71b074ddd51421f81790da5ade84bfe3793` passed all three exact-head gates:

- Full repository suite: **1,347 passed, zero failed, 8 subtests passed**; inclusive coverage **59.48%** (53% floor).
- Core suite: 677 passed, 8 subtests passed.
- Installed wheel, Barrot V3 imports, packaged XRP mission and canonical data assets: passed.
- Six-manifest dependency audit: passed; zero known vulnerabilities.
- Fail-closed merge gate: passed; automatic merging disabled.

Evidence: [CI 42763421873](https://github.com/Barrot-Agent/B-Agent/actions/runs/42763421873), [dependency audit 42763421622](https://github.com/Barrot-Agent/B-Agent/actions/runs/42763421622), [fail-closed gate 42763421634](https://github.com/Barrot-Agent/B-Agent/actions/runs/42763421634).

The GitHub Actions cache budget is read-only; cache save failed after test and wheel verification. This was non-fatal. Setuptools emitted non-fatal metadata/package-discovery warnings.

## Major regulatory correction: three OCC trust charters are now regulator-confirmed effective

The OCC Corporate Applications Search now supplies the primary status records. The previous Run115/Run116 wording that Ripple and Circle approvals were company-reported but not regulator-index-confirmed is superseded.

| Entity | OCC charter | Approved | Consummated/effective |
|---|---:|---|---|
| Ripple National Trust Bank | 25364 | Dec 12, 2025 | **Oct 26, 2026** |
| First National Digital Currency Bank, N.A. (Circle National Trust) | 25361 | Dec 12, 2025 | **Jul 24, 2026** |
| Coinbase National Trust Company | 25390 | Apr 2, 2026 | **Nov 6, 2026** |

Primary OCC records:
- [Ripple National Trust Bank — CAS 2025-Charter-342347](https://apps.occ.gov/CAS/home/details?FilingID=RjzoD2gxmYOv&FilingSubtypeID=1093&FilingTypeID=2)
- [Circle / First National Digital Currency Bank — CAS 2025-Charter-342299](https://apps.occ.gov/CAS/home/details?FilingID=D79Z71vmerN8&FilingSubtypeID=1093&FilingTypeID=2)
- [Coinbase National Trust Company — CAS 2025-Charter-343449](https://apps.occ.gov/CAS/home/details?FilingID=3RAoRRek6o4j&FilingSubtypeID=1093&FilingTypeID=2)

These are national trust banks, not retail deposit-taking/lending banks. Effective charter status does not prove launch scale, XRP balances, collateral utilization or payment throughput.

### Their approved roles are not interchangeable

- **Ripple National Trust Bank:** Ripple says the bank is approved for segregated RLUSD reserve management, collateral-trustee functions for the benefit of RLUSD holders and fiduciary digital-asset custody. RLUSD issuance continues through Standard Custody & Trust Company, Ripple’s NYDFS-regulated limited-purpose trust company. The national trust bank itself is not the RLUSD issuer. [Ripple’s final-approval announcement](https://ripple.com/ripple-press/ripple-receives-final-occ-approval-to-establish-national-trust-bank/).
- **Circle National Trust:** Circle says the bank begins with fiduciary digital-asset custody for Circle and affiliates. Reserve management is a future capability. The OCC decision letter says the national trust bank will not issue USDC; issuance remains with Circle’s NY limited-purpose trust company. [Circle announcement](https://www.circle.com/pressroom/circle-receives-final-occ-approval-to-establish-national-trust-bank) and [OCC decision letter](https://www.occ.gov/news-issuances/news-releases/2025/nr-occ-2025-125a.pdf).
- **Coinbase National Trust Company:** its effective charter is separate from Coinbase Exchange, Coinbase Prime and Coinbase’s operating entities. Its existence is not evidence of proprietary XRP holdings or XRP collateral use.

### BNY, Coinbase and Ripple product status

- BNY’s October 27 joint release says it now supports XRP and RLUSD on Digital Asset Custody and remains primary reserve custodian for RLUSD. Direct RLUSD mint/redeem through BNY and tokenized trade-finance initiatives are intended future work subject to approvals and client requirements. [BNY primary release](https://www.bny.com/corporate/global/en/about-us/newsroom/press-release/ripple-expands-strategic-digital-assets-collaboration-with-bny-across-custody-and-tokenized-trade-finance.html).
- Coinbase’s October 28 official post confirms RLUSD live on Coinbase Prime, Coinbase Exchange and the Coinbase app, with deposits/withdrawals on XRPL, Base and Ethereum and 1:1 USD conversion. Coinbase Global Exchange collateral support was explicitly future/follow-on, not live at launch. [Coinbase primary announcement](https://www.coinbase.com/blog/rlusd-is-now-available-on-coinbase).
- BNY custody, Ripple reserve-collateral trustee, Circle affiliate custody and Coinbase trust custody are distinct roles. None independently proves XRP is being used as collateral or bridge settlement in those products.

## November 9 ETF flow: issuer-primary cross-check

CryptoETF.today displays a **partial −$10.3M** for November 9 across 3 of 5 funds: Bitwise −$9.4M, Canary/XRPC −$0.7M, 21Shares/TOXR −$0.2M; XRPZ and GXRP were not yet reported. Its flow is a secondary calculation, not an issuer cash-redemption filing. [Tracker and methodology](https://cryptoetf.today/en/xrp-etf-flows).

Issuer-page checks add useful reconciliation:

- **Canary XRPC:** sponsor page shows November 9 XRP quantity **242,962,753.64**, net assets **$285,986,592**, and **22.92M shares**. Its November 6 daily table showed 22.99M shares and $286.859M net assets. The 70,000-share reduction supports a redemption-like share change, but the exact −$0.7M tracker estimate and cash-versus-in-kind settlement are not directly confirmed. [Canary sponsor page](https://canaryetfs.com/trxs/).
- **21Shares TOXR:** official page shows November 9 AUM **$117.096M**, NAV **$10.65**, and **11.00M shares**. The earlier November 6 issuer-linked capture showed 11.02M shares; the 20,000-share change implies roughly $213K at the November 9 NAV, broadly consistent with the tracker’s −$0.2M estimate. Exact settlement form is not disclosed. [21Shares issuer page](https://www.21shares.com/en-us/products-us/toxr).
- **Bitwise XRP:** the accessible sponsor page still shows **415,365,129.04 XRP as of November 5**, so it does not verify the tracker’s November 9 −$9.4M estimate. [Bitwise sponsor page](https://bitxrpetf.com/).

Keep shares outstanding, holdings, NAV, AUM, estimated creations/redemptions and cash/in-kind settlement separate. Do not treat the partial tracker total as the final five-fund complex flow.

## Spot refresh after Run116 capture

At approximately 05:39:43Z:
- Kraken XRP/USD last $1.09548; bid $1.09542 / ask $1.09543; 24h volume 27.205M XRP; VWAP $1.09403. Kraken provided no event timestamp/cache age.
- OKX XRP-USDT last 1.0998; bid 1.0997 / ask 1.0998; event time 05:38:47.575Z (about 55 seconds old); 24h volume 68.150M XRP.
- Kraken USDT/USD last 0.99868, with no event timestamp. Mechanically normalized OKX quote is about $1.09835, 0.262% above Kraken; asynchronous, not executable arbitrage.
- No synchronized pure-spot L2 book was obtained. Do not substitute mixed spot/perpetual depth.

These rendered web responses are not original HTTP wire bytes or receipt-chain entries and remain model-ineligible.

## Prediction and identity gates

- **Forecast: NOT_ISSUED.** No Run117 web data admitted. No directional forecast, paper trade or real-money action.
- **SBIC:** East/Central/West remain Tokyo/Nagoya/Osaka regional Small and Medium Business Investment & Consultation companies, distinct from SBI Holdings. Tokyo SBIC's ChatGPT/Copilot training is not an OpenAI partnership.
- **ASK Coin:** Permission ASK remains the strongest candidate, distinct from the inactive Ask Coin exchange listing; no XRP/XRPL integration found.
- **Actual capital:** cash, in-kind XRP, debt, drawn facilities, contingent capacity and secondary resales remain separate.
- **Kamilah Stevenson:** person identity supported; exact YouTube handle/channel-ID mapping not first-party verified. Verified personal-channel inventory remains zero; candidate references are not published as a verified inventory.

## Repository, PR and merge status

Before Run117 commits: main `d4d43be3427375cf79d190e768976de062e20287`; integration `038af71b074ddd51421f81790da5ade84bfe3793`; PR #1640 is 902 commits ahead, zero behind, 236 changed paths. All 372 open PRs were paginated (100+100+100+72).

PR #1640 remains the sole active integration path. It has 62 COMMENTED reviews and zero approvals; 22 inline threads are resolved but outdated; CodeRabbit check is skipped. Branch-protection endpoint remains HTTP 403 and the visible fallback ruleset is disabled. A prior main push triggered Pages publication; authorization for this PR's automatic public Pages side effect is not established. **Do not merge.**

Backlog:
- #1643: preserve 663 unique paths; 7 overlap with #1640; 906 ahead/1 behind, not mergeable.
- #1653: preserve 6 unique paths; 1 overlap; 18 ahead/1 behind; 8 unresolved review threads.
- #1642: 7/7 paths overlap #1640.
- #1644–#1650: all changed paths overlap #1640; exact dependency/version reconciliation before any closure.
- #1317/#1318/#1320: 6/6, 2/2 and 5/5 paths overlap.
- #1254/#1255: each one path overlaps.
- #1269: preserve 8 unique paths; 1 overlap.
- #1655: preserve 3 unique paths; 5 overlap.
- #1659: preserve 4 unique paths; 2 overlap.
- #1641: preserve 3 unique paths.
- #1614: preserve 49 unique paths; 8 overlap; 36 ahead/42 behind, stale.
- No PRs closed.

## Run117 structured evidence

[Run117 OCC charter and ETF primary-source reconciliation](research/xrp_intelligence/20261110T054227Z-run117-occ-etf-primary-reconciliation.json)

Next: obtain an independent approval and authoritative branch-protection visibility; resolve Pages authorization; preserve unique research/prediction work; trace Evernorth's unclassified 370.35M XRP movement; continue synchronized market history and durable receipts; keep forecasts disabled until out-of-sample and shadow gates pass.

# Barrot XRP Mission — Canonical Current Handoff

**Run 116 · Updated 2026-11-10T05:33:23Z**

## Mission and foundation

**Priority 1:** XRP intelligence and measured prediction-engine performance.

**Preserved foundation:** Barrot V3 remains the execution, orchestration, safety, permissions, evidence-verification and fail-closed foundation. No V3 replacement, automatic merge, paper trading or real-money execution.

## Repository state — VERIFIED before Run116 evidence commit

| Item | State |
|---|---|
| Main SHA | `d4d43be3427375cf79d190e768976de062e20287` |
| Integration head before Run116 | `cae8440a0ad5710fafa187c6b50d56bce3b660a4` |
| Existing integration PR | [#1640](https://github.com/Barrot-Agent/B-Agent/pull/1640) |
| Commits ahead / behind | 900 / 0 |
| Changed paths | 235 |
| Main tree | 1,404 entries / 1,299 files |
| Integration tree | 1,532 entries / 1,419 files |
| Open PR inventory | 372: 356 drafts, 16 non-drafts |

All four open-PR API pages were read (100 + 100 + 100 + 72). No new branch or PR was created. The mission manifest, 40-source registry, seven XRP workstreams, point-in-time feature store, forecast ledger, deterministic baselines and scheduled public-ingestion workflow remain on the integration branch, not main.

## Exact-head verification — EXECUTED and VERIFIED on `cae8440a0ad5710fafa187c6b50d56bce3b660a4`

- Full repository suite: **1,347 passed, zero failed, 8 subtests passed**.
- Inclusive coverage: **59.48%**, above the 53% floor.
- Core suite: **677 passed, 8 subtests passed**.
- Installed wheel: passed; packaged mission resource verified; installed package loads Barrot V3, XRP mission and canonical data assets.
- Dependency audit: all six manifests passed; zero known vulnerabilities.
- Fail-closed gate: passed; automatic merge remains disabled.

Exact-head evidence:
- [Full CI 42762244159](https://github.com/Barrot-Agent/B-Agent/actions/runs/42762244159) — head `cae8440a0ad5710fafa187c6b50d56bce3b660a4`, success.
- [Dependency audit 42762244141](https://github.com/Barrot-Agent/B-Agent/actions/runs/42762244141) — same head, success.
- [Fail-closed gate 42762244148](https://github.com/Barrot-Agent/B-Agent/actions/runs/42762244148) — same head, success.

Non-fatal warnings: GitHub Actions cache budget is read-only; setuptools emits license-metadata and package-discovery warnings. Neither prevented full-suite tests, wheel build or installed-wheel verification.

## Run116 market update — capture cutoff 2026-11-10T05:33:23Z

### Spot

- Kraken XRP/USD: **$1.09548**; bid $1.09542 / ask $1.09543; top-of-book spread approximately 0.0913 basis points; 24-hour volume 27.205M XRP; VWAP $1.09403; high/low $1.11573 / $1.07502.
- Kraken did not provide provider event time or cache-age metadata; freshness is unknown.
- OKX XRP-USDT: **1.0953 USDT**; bid 1.0953 / ask 1.0954; 24-hour volume 69.239M XRP; event time 05:08:05.374Z, **1,517.6 seconds old** at capture, above the 300-second freshness limit.
- Kraken USDT/USD: 0.99868, with no provider event timestamp. A mechanically normalized OKX quote is about $1.09385420, approximately -0.1484% versus Kraken. This is stale/asynchronous and is not executable arbitrage evidence.

Sources: [Kraken XRP/USD](https://api.kraken.com/0/public/Ticker?pair=XRPUSD), [OKX XRP-USDT](https://www.okx.com/api/v5/market/ticker?instId=XRP-USDT), [Kraken USDT/USD](https://api.kraken.com/0/public/Ticker?pair=USDTUSD).

### Order book and derivatives

- No current synchronized pure-spot L2 snapshot was obtained.
- The prior 01:39Z mixed Binance spot / OKX perpetual book is stale and must not be presented as pure spot executable depth.
- The latest Liqwall and TradRadar OI/liquidation snapshots are from 02:22Z and 02:00Z. They show long-heavy deleveraging, but are stale at Run116 and aggregate overlapping venue universes. Do not average them or admit them as current features.

### ETF flow — provisional partial update

CryptoETF.today now displays a **partial November 9 outflow of $10.3M across 3 of 5 funds**: Bitwise −$9.4M, Canary/XRPC −$0.7M and 21Shares/TOXR −$0.2M; XRPZ and GXRP are not reported in that snapshot.

This is not a final five-fund total, not the six-spot-fund-plus-BITW universe, and not an issuer-confirmed cash-redemption series. CryptoKeyhole's earlier capture said November 9 issuer files were still pending for its four daily-readable funds; XRP Insights still displayed November 6 as its latest settled row; Alpha Finance displayed coverage through November 8. These are different retrieval cutoffs and fund universes. Preserve the partial row and each source's cutoff; do not average or treat missing reports as zero.

Sources: [CryptoETF.today](https://cryptoetf.today/en/xrp-etf-flows), [CryptoKeyhole](https://cryptokeyhole.com/etf-flows/xrp/), [XRP Insights](https://xrp-insights.com/), [Alpha Finance](https://alphafinance.io/etf/xrp/).

## Institutional network updates

- **Coinbase/Ripple:** Reuters reports Coinbase began adding RLUSD to retail and institutional platforms on October 28. This broadens Coinbase's stablecoin distribution alongside its existing Circle/USDC relationship. It is not proof of XRP purchases or XRP bridge volume.
- **PNC/Coinbase/Circle:** the November 9 pilot lets eligible corporate/institutional PNC clients receive Circle USDC converted to USD. This is an institutional dollar rail, not an XRP corridor.
- **BNY/Ripple:** the October 27 joint company announcement says BNY now supports XRP and RLUSD on Digital Asset Custody. Direct RLUSD mint/redeem and tokenized trade-finance initiatives remain intended/future work subject to approvals and client requirements. Custody availability does not prove client balances, XRP collateral use or payment throughput.
- **Standard Chartered/LMAX:** RLUSD custody in Dubai was reported live; LMAX collateral mirroring remains planned and subject to documentation, testing, regulatory and internal approvals.
- Coinbase/Circle Q3 distribution economics, Circle/SBI Japan ownership, SBI/Ripple equity and operating links, SBI Remit XRP corridors and Evernorth capital categories remain in the prior primary-source handoff. Stablecoin balances, custody assets, cash, in-kind XRP, debt, contingent capacity and secondary resales remain separate.

Sources: [Coinbase RLUSD listing](https://www.reuters.com/legal/transactional/coinbase-adds-ripples-stablecoin-its-exchange-2026-10-28/), [PNC/Coinbase USDC pilot](https://www.reuters.com/legal/transactional/pnc-offer-stablecoin-payments-clients-coinbase-partnership-2026-11-09/), [Ripple/BNY primary announcement](https://ripple.com/ripple-press/ripple-expands-collaboration-with-bny-across-custody-and-tokenized-trade-finance/), [Standard Chartered/LMAX report](https://www.coindesk.com/business/2026/10/12/standard-chartered-offers-rlusd-custody-in-dubai-and-plans-lmax-collateral-link).

## Identity corrections

- **Japan SBIC:** East/Central/West remain the Tokyo/Nagoya/Osaka regional Small and Medium Business Investment & Consultation companies, distinct from SBI Holdings. Tokyo SBIC training mentioning ChatGPT/Copilot is not an OpenAI partnership.
- **ASK Coin:** Permission's official documentation confirms ASK as its token for family rewards, consent-based AI/data exchange and agent-to-agent coordination, with 100B fixed supply and LayerZero OFT contracts on Base and Polygon. No XRP/XRPL integration was found. This remains a strong candidate for the phrase “ASK Coin,” not a confirmed intended referent; it is distinct from the inactive Ask Coin exchange listing. CMC volume observations conflict sharply ($10.60 versus an earlier $891.78 snippet), so the market is thin/scrape-sensitive.
- **“Actual capital”:** not a standardized XRP metric. Keep cash, in-kind XRP, debt, drawn facilities, contingent equity capacity and secondary resales separate.
- **Kamilah/Camilla Stevenson — correction to Run115 wording:** the person identity is supported by branded/first-person evidence, but the candidate YouTube handle `@drkamilahstevenson` is not first-party verified as channel ID `UCqUPJMQdkCN6lsLVDnichPA`. The canonical source profile explicitly records `channel_identity_status=PROBABLE_MATCH_NOT_FIRST_PARTY_VERIFIED`, `attribution_verified=false`, `identity_gate_passed=false`, and **zero verified personal-channel videos** with ten candidate references. Run115's phrase “channel-level attribution corroborated” was too strong. Direct search bylines and third-party transcript archives remain candidate evidence only. The eight titles previously listed are not a verified or exhaustive personal-channel inventory. The Alina X upload remains excluded. Do not promote candidates until first-party YouTube metadata or a reciprocal first-party link resolves the exact handle-to-channel-ID relationship.

Official ASK documentation: [Permission ASK Token](https://docs.permission.ai/ask-token), [contract addresses](https://docs.permission.ai/ask-token/contract-addresses). Candidate channel record: [Kamilah Stevenson source profile](https://github.com/Barrot-Agent/B-Agent/blob/integration/core-capabilities-mmi-structural-paper-20261104/data/xrp_intelligence/sources/kamilah_stevenson_channel.json).

## Prediction-engine status

Implemented on the integration branch, not main: 40 public source records (36 hourly, two weekly CFTC, two excluded non-commercial XRPL nodes), raw-byte receipt capture in the scheduled workflow, SHA-256 receipt-chain logic, point-in-time SQLite feature store, four deterministic baselines, chronological walk-forward with purge/embargo, calibration/drift diagnostics and fail-closed forecast ledger requiring trusted Ed25519 evaluator signature.

Still unmet: independent WORM/trusted timestamp anchoring; complete synchronized historical spot/L2/exchange-flow/derivatives/collateral coverage; effective-sample-size correction for overlapping horizons; sufficient independent out-of-sample and shadow outcomes; demonstrated lift over naive baselines.

**Forecast status: NOT_ISSUED.** Run116 web observations are research-only and model-ineligible. Rendered API text was not preserved as original HTTP wire bytes or headers; no raw-byte receipt/hash is claimed. No directional forecast, paper trade or real-money action occurred.

## Nine-platform coordination

- ChatGPT: current-session GitHub read/write and public-web research verified.
- Copilot: comment-only PR review activity; zero approvals; no separate authenticated data flow.
- Claude, Grok, Gemini and Codex: unverified; no tested authentication/data flow.
- Hugging Face: prior BUILD_ERROR; no deployment.
- Kaggle: untested; no submission.
- Databricks: prior HTTP 403; no workspace write.

No external model received repository data. Independent assignments remain designed, not executed.

## Backlog and overlap audit — 372 open PRs

| PR/workstream | Classification | Current path/ancestry evidence |
|---|---|---|
| #1640 | **Blocked integration** | Sole V3/XRP integration path; 900 ahead, 0 behind |
| #1643 | **Unique/unreviewed, blocked** | 670 PR files; paginated inventory confirms 663 unique paths and 7 overlap with #1640; 906 ahead, 1 behind current main; GitHub reports not mergeable. Preserve all unique research. |
| #1653 | **Unique/unreviewed, blocked** | 7 files; 6 unique and 1 overlap; 18 ahead, 1 behind; preserve graph work and resolve 8 open review threads. |
| #1642 | **Superseded-content candidate** | 7/7 paths overlap #1640. |
| #1644–#1650 | **Superseded/overlap candidates** | Current path comparison: every changed path overlaps #1640; reconcile exact versions/blobs after a verified main successor. |
| #1317/#1318/#1320 | **Superseded/overlap candidates** | 6/6, 2/2 and 5/5 paths respectively overlap #1640. |
| #1254/#1255 | **Dependency overlap candidates** | Each one changed path overlaps #1640. |
| #1269 | **Unique/unreviewed** | 9 files; 8 unique, 1 overlap. Preserve topology work. |
| #1655 | **Unique draft material** | 8 files; 3 unique, 5 overlap. Preserve unique content. |
| #1659 | **Unique draft material** | 6 files; 4 unique, 2 overlap. Preserve local-inference work. |
| #1641 | **Unique draft material** | 3 files; all 3 unique. Preserve. |
| #1614 | **Unique prediction work, stale** | 57 files; 49 unique, 8 overlap; 36 ahead, 42 behind current main; preserve unique work, reconcile rather than merge stale branch. |

No PRs were closed. Do not close unique research, graph, topology, local inference or prediction work before a successor is merged and verified on main.

## Merge decision — BLOCKED

PR #1640 is open, non-draft and GitHub reports mergeable. It is 900 commits ahead, zero behind, with 235 changed paths.

- Review submissions: **62 COMMENTED, zero APPROVED**.
- Inline threads: 22/22 resolved, but outdated relative to the current head.
- Current CodeRabbit check: SKIPPED.
- Main branch-protection endpoint: HTTP 403, “Resource not accessible by integration.”
- Visible “Fall Back” ruleset: enforcement disabled.
- GitHub Pages is enabled; a prior main push triggered successful public deployment [42526890275](https://github.com/Barrot-Agent/B-Agent/actions/runs/42526890275). PR #1640 changes public web assets. Authorization for that automatic publication is not established.

The user's conditional merge authorization is not satisfied. Do not bypass protections, merge or deploy.

## Main workflow status

- Latest scheduled Cross Analysis on main: [42758515738](https://github.com/Barrot-Agent/B-Agent/actions/runs/42758515738), success.
- Main full CI remains [42526890841](https://github.com/Barrot-Agent/B-Agent/actions/runs/42526890841), 718 tests and 8 subtests passed on main SHA `d4d43be3`.
- Main Pillars Consistency Check [42621970927](https://github.com/Barrot-Agent/B-Agent/actions/runs/42621970927) failed because required GitHub App credentials were absent, Databricks returned HTTP 403 and the Hugging Face Space health check reported BUILD_ERROR.
- Main Hover Bike Updates [42572261311](https://github.com/Barrot-Agent/B-Agent/actions/runs/42572261311) failed its artifact upload. The integration branch contains a root-working-directory correction and regression test, but that workflow fix has not been dispatched/verified on the integration branch.

## Run116 evidence file

- [Run116 structured market/ETF/identity/merge audit](research/xrp_intelligence/20261110T053323Z-run116-market-etf-identity-merge-audit.json)
- [Current nine-platform capability map](research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_current.json)
- [PR #1640](https://github.com/Barrot-Agent/B-Agent/pull/1640)

## Next concrete actions

1. Obtain an independent approving review and authoritative branch-protection visibility.
2. Resolve authorization for the automatic GitHub Pages publication side effect.
3. Preserve #1643's 663 unique research paths and #1653's six unique graph paths; do not bulk-close.
4. Reconcile issuer-primary November 9 ETF holdings/cash-versus-in-kind flows against the partial tracker reports.
5. Trace Evernorth's 370.3M XRP moved outside attributed wallets using direct public rippled reads or an accessible independent explorer; classify destinations before any exchange-flow inference.
6. Continue synchronized historical spot/L2/derivatives/CFTC/collateral ingestion and independent raw-source anchoring.
7. Resolve the Kamilah handle-to-channel-ID relationship with first-party metadata before publishing any personal-channel video inventory.
8. Complete leakage-safe out-of-sample evaluation and independent shadow outcomes before any forecast issuance.
9. After any authorized merge, fetch main again, verify merge commit/files, run main CI, inspect automatic workflow side effects, then close only exact verified duplicate/superseded PRs.

No merge, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push or destructive worktree operation occurred.

---

# Barrot XRP Mission — Canonical Current Handoff

**Run 115 · Updated 2026-11-10T05:20:28Z**

## Mission and foundation

**Priority 1:** XRP intelligence and measured prediction-engine performance.

**Preserved foundation:** Barrot V3 remains the execution, orchestration, safety, permissions, evidence-verification and fail-closed foundation. No replacement of V3, no automatic merge, no paper trading and no real-money execution.

## Repository state — VERIFIED before Run115 evidence commit

| Item | State |
|---|---|
| Main SHA | `d4d43be3427375cf79d190e768976de062e20287` |
| Integration parent head | `c2d07243ce417fda43c1485c09b9c25e71c43cc8` |
| Existing integration PR | [#1640](https://github.com/Barrot-Agent/B-Agent/pull/1640) |
| Commits ahead / behind | 898 / 0 |
| Changed paths | 233 |
| Main tree | 1,404 entries / 1,299 files |
| Integration tree | 1,530 entries / 1,417 files |
| Open PR inventory | 372: 356 drafts, 16 non-drafts |

All four paginated GitHub PR-list pages were read (100 + 100 + 100 + 72). No new branch or PR was created. The mission manifest, 40-source registry, seven XRP workstreams, point-in-time feature store, forecast ledger, deterministic baselines and scheduled public-ingestion workflow remain on the integration branch, not main.

## Exact-head verification — EXECUTED and VERIFIED on `c2d07243ce417fda43c1485c09b9c25e71c43cc8`

- Full repository suite: **1,347 passed, zero failed, 8 subtests passed**.
- Inclusive package coverage: **59.48%**, above the 53% floor.
- Core suite: 677 passed, 8 subtests passed.
- Installed wheel: passed; Barrot V3, XRP mission resources and canonical data assets loaded.
- Dependency audit: six manifests passed; zero known vulnerabilities.
- Fail-closed gate: passed; automatic merge disabled.

Exact-head evidence:
- [Full CI 42755448372](https://github.com/Barrot-Agent/B-Agent/actions/runs/42755448372) — head `c2d07243ce417fda43c1485c09b9c25e71c43cc8`, success.
- [Dependency audit 42755448330](https://github.com/Barrot-Agent/B-Agent/actions/runs/42755448330) — same head, success.
- [Fail-closed gate 42755448359](https://github.com/Barrot-Agent/B-Agent/actions/runs/42755448359) — same head, success.

Main's latest full CI [42526890841](https://github.com/Barrot-Agent/B-Agent/actions/runs/42526890841) passed 718 tests and 8 subtests on main SHA `d4d43be3`.

## Run115 market and data-quality findings

**Spot:** Kraken's surfaced XRP/USD response showed last $1.09379, bid $1.09413, ask $1.09414, 24-hour volume 27.50M XRP and 24-hour VWAP $1.09425. Kraken supplied no provider event timestamp or cache-age header. OKX showed 1.0953 USDT, but its event timestamp was 05:08:05.374Z, 743 seconds before this 05:20:28Z cutoff; it fails the 300-second freshness threshold. Kraken USDT/USD last was 0.99869 but had no provider event time. A normalized OKX quote of $1.093865 is only 0.0069% above Kraken, but this is asynchronous/stale and not an arbitrage signal. All three web observations are model-ineligible.

**Depth:** no fresh pure-spot L2 snapshot was obtained. The prior 01:39Z EdgeOrNot snapshot combines Binance spot and OKX perpetual liquidity and is stale for this cutoff. No current depth value is inferred.

**Derivatives:** Liqwall at 02:22Z reported $1.22B OI, −1.8% 24-hour OI change and $8.2M liquidations, $7.5M long. TradRadar at 02:00Z reported $1.66B OI, −3.9% change and at least $9.08M liquidations, $8.22M long. Both report modest positive funding and long-heavy liquidations. Aggregator venue coverage overlaps; retain both observations and do not average.

**CFTC:** the November 3 TFF futures-only report lists three XRP markets: CME #176740, 7,216 contracts × 50,000 XRP = 360.8M XRP-equivalent; Coinbase Nano #176LM1, 32,505 × 500 = 16.2525M; Coinbase Nano Perp Style #176LM3, 38,392 × 500 = 19.196M. Total reported open interest is 78,113 contracts or 396.2485M XRP-equivalent. This is contract OI, not cash, collateral or net directional exposure. The CFTC's current add/dropped-contract index explicitly lists #176LM2 XRP Coinbase Derivatives as dropped from reporting. Absence is not zero. CFTC report methodology: Tuesday positions, generally released Friday; trader classifications do not explain why positions are held.

Sources: [CFTC TFF report](https://www.cftc.gov/dea/futures/financial_lf.htm), [CFTC COT index](https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm).

## ETF flow disagreement

XRP Insights reports six US spot funds plus BITW, approximately 1.19523B XRP and $1.405B AUM. Its detailed section reports a November 6 outflow of 663,043 XRP and November 2–6 weekly outflow of approximately 812,500 XRP. The same page's top-level Week 46 card displays +0.05M XRP. This is an unresolved internal publisher conflict. The latest settled date shown is November 6; issuer holdings update after the close and no November 9 settled flow is present on this page. Other ten-fund/international ETP aggregates have different scope and are not comparable.

Source: [XRP Insights ETF tracker](https://xrp-insights.com/).

## Evernorth: actual capital, debt, contingent capacity and on-chain custody

The November 9 SEC prospectus reports approximately 473M XRP held as of October 9. It distinguishes $214.1M cash and 261.919M XRP raised through private placements; the $214.1M cash was used to buy 84.365876M XRP. At closing, gross cash proceeds were approximately $272.6M ($224.6M private-placement cash plus $48M trust cash) and in-kind XRP contributions were 388.910554M. These are different financing stages and must not be summed without tranche reconciliation.

The $30M convertible PIK note generated $29M net cash after a $1M advisor fee. It is debt, not equity proceeds or verified XRP purchases. The Cantor committed equity facility allowed up to 5,218,935 shares under a 97%-of-VWAP formula and restrictions; the prospectus reports zero proceeds received under it. A 73,688,162-share resale registration is secondary-holder liquidity, not new XRP capital; Evernorth receives no proceeds from those resales.

The prospectus attributes 9,431,914 Class A and 2,359,038 Class C shares to four SBI-controlled holders: 21.4% of common stock and 39.9% of voting power. This is the largest disclosed voting block, not majority control and not proof SBI funded 39.9% of the XRP treasury.

**On-chain tracker observation:** XRP Insights reports ledger 108,232,177, closed November 10 at 04:45Z; 103,129,905 XRP in 13 attributed wallets (21.8% of the reported closing figure), and 370,346,663 XRP moved outside the attributed set, latest October 22. Destinations remain unattributed. The tracker says it reads rippled account_info and scans signed account_tx, with attribution based on labeled wallets, payment links and tranche matches. XRPSCAN transaction pages returned HTTP 403 during this run, so individual destination transactions were not independently re-read.

The tracker also identifies a 200,000 XRP October 3 Uphold deposit as consistent with the delayed-funding tranche due at closing, but says no filing confirms that specific deposit. Its current wallet balance plus reported outflows total 473,476,568 XRP, 200,138 above the filing's 473,276,430 figure; the tracker notes the 200,000 tranche and unsolicited dust/net fees. Retain this as a reconciliation item, not evidence of unreported capital or sale.

Sources: [Evernorth SEC prospectus](https://www.sec.gov/Archives/edgar/data/2092592/000162828026072223/evernorth-424b3.htm), [Evernorth on-chain tracker](https://xrp-insights.com/xrp-radar/evernorth).

## BNY institutional custody

BNY's October 27 joint announcement with Ripple says BNY now supports XRP and RLUSD on its Digital Asset Custody platform, building on BNY's role as primary RLUSD reserve custodian and its Ripple Prime custody relationship. Planned direct RLUSD mint/redeem for BNY clients, broader XRPL tokenized-asset support and tokenized trade-finance use cases remain future plans subject to approvals/client requirements. This proves custody availability and an announced collaboration, not actual client balances, XRP collateral eligibility/utilization or payment throughput.

[BNY/Ripple primary announcement](https://www.bny.com/corporate/global/en/about-us/newsroom/press-release/ripple-expands-strategic-digital-assets-collaboration-with-bny-across-custody-and-tokenized-trade-finance.html).

## XRPL and macro timeline

XRPL's official September 16 release introduced rippled 3.4.0 and fixCleanup3_4_0 (amendment ID 98433DD0…E4FEC A76). Secondary reports claim activation November 4 at ledger 108112129. However, the official Permission Values page, last updated three days ago, still warns not to delegate PaymentBurn until the amendment is enabled; the official Known Amendments page's status is dynamically rendered as Loading in the text view. This is a real source disagreement. Current validator/validated-ledger state must be queried before asserting enabled or disabled.

The BLS October CPI and Real Earnings release is scheduled for November 10 at 08:30 ET / 13:30Z. At this research cutoff it is a future event, not a published result.

Sources: [XRPL 3.4.0 release](https://xrpl.org/blog/2026/xrpld-3.4.0), [BLS November schedule](https://www.bls.gov/schedule/2026/11_sched.htm).

## Identity research

- Japan's SBIC East/Central/West remain Tokyo/Nagoya/Osaka regional Small and Medium Business Investment & Consultation companies, distinct from SBI Holdings.
- Tokyo SBIC's official course includes ChatGPT and Copilot instruction for investee companies; this is not an OpenAI partnership.
- “SBIC, ChatGPT SBIC” has no verified primary-source partnership match.
- **ASK token:** Permission's official docs identify ASK as its native token for family rewards, consent-based AI/data exchange and agent-to-agent coordination, with 100B fixed supply and LayerZero OFT contracts on Base and Polygon. CoinMarketCap's displayed 24-hour volume was only $10.60 at one capture, while an earlier search snippet showed $891.78; treat as thin and scrape-sensitive. No XRP/XRPL integration was found. This is a strong candidate for an “ASK Coin” reference, not a confirmed intended identity.
- “Actual capital” is not a standardized XRP metric; keep cash, in-kind, debt, drawn capacity, contingent equity and secondary resales separate.
- **Kamilah/Camila Stevenson video attribution:** a channel-level identity is corroborated by direct YouTube bylines and a third-party creator profile linking channel ID `UCqUPJMQdkCN6lsLVDnichPA`. Some transcripts introduce the speaker as “Camila Stevenson”; the public byline uses “Kamilah Stevenson”. Legal identity is not independently verified. See the video inventory below.

## Run115 public video inventory — Kamilah/Camila Stevenson

Channel-level attribution is corroborated, but legal identity is not independently verified. The creator analytics page links the named Kamilah Stevenson profile to YouTube channel ID `UCqUPJMQdkCN6lsLVDnichPA`; direct YouTube search results display the Kamilah Stevenson byline. Several indexed transcripts use the spoken introduction “Camila Stevenson”. Subscriber counts conflict across sources and are not used as identity proof.

| Date | Public video | Attribution evidence |
|---|---|---|
| 2025-12-06 | [XRP collateral explainer](https://www.youtube.com/watch?v=M8TmDXO7B-0) — indexed title unavailable; description says XRP was accepted as collateral for regulated derivatives | Direct YouTube result by Kamilah Stevenson |
| 2025-12-14 | [Ripple Just Became a BANK — And XRP Holders Need to Understand This](https://www.youtube.com/watch?v=QslbjGQD0MU) | Glasp transcript archive; speaker introduces herself as Camila |
| 2025-12-24 | [XRP Is Not Bitcoin. And That's Exactly Why It Matters](https://www.youtube.com/watch?v=pmJTrXJQ8Vw) | Direct YouTube result by Kamilah Stevenson |
| 2026-01-13 | [XRP ETFs Are Here. Price Isn't Moving. Here's What Everyone's Missing.](https://www.youtube.com/watch?v=ci0FH73lbCs) | Glasp transcript archive; speaker introduces herself as Camila |
| 2026-01-15 | [Why Most People Will Lose Their Crypto Wealth (Even If They're Right)](https://www.youtube.com/watch?v=cxeX_eu_2H0) | Glasp transcript archive; speaker introduces herself as Camila |
| 2026-03-03 | [XRP Was Built for What's Coming](https://www.youtube.com/watch?v=ywQEoYPzhlQ) | Direct YouTube result by Kamilah Stevenson |
| 2026-03-06 | [Something Just Broke in Global Finance — And It's Connected to XRP](https://www.youtube.com/watch?v=iwhpNT73zpk) | Direct YouTube result by Kamilah Stevenson |
| 2026-03-19 | [How Much XRP Do You ACTUALLY Need?](https://www.youtube.com/watch?v=rv0BAV0vLgo) | Glasp transcript archive by Kamilah Stevenson |

Excluded from personal-channel inventory: [Kamilah Stevenson Breaks Down XRP's Most Important Upgrade Yet](https://www.youtube.com/watch?v=5DzBk8DfoLs), because the YouTube byline is Alina X; this is a third-party video featuring/attributing commentary to Kamilah, not an upload by her channel.

The CryptoKrios page assigns an 82/100 trust score but explicitly says there is no meaningful verified prediction-accuracy figure and lists several missed targets. That score is not used as forecast-performance evidence. Sources: [creator profile](https://cryptokrios.com/creators/kamilah-stevenson), [direct channel video](https://www.youtube.com/watch?v=pmJTrXJQ8Vw), [direct channel video](https://www.youtube.com/watch?v=ywQEoYPzhlQ), [direct channel video](https://www.youtube.com/watch?v=iwhpNT73zpk).

## Prediction-engine readiness

Implemented on the integration branch, not main: 40 public source records (36 hourly, two weekly CFTC and two excluded non-commercial XRPL nodes), raw-byte receipt capture in the scheduled workflow, SHA-256 receipt-chain logic, point-in-time SQLite feature store, four deterministic baselines, chronological walk-forward with purge/embargo, calibration/drift diagnostics and fail-closed forecast ledger requiring trusted Ed25519 evaluator signature.

Still unmet: independent WORM/timestamp anchoring; complete synchronized historical spot/L2/exchange-flow/derivatives/collateral data; effective-sample-size correction for overlapping horizons; sufficient independent out-of-sample and shadow outcomes; demonstrated lift over naive baselines.

**Forecast status: NOT_ISSUED.** Run115 web observations are not model-admitted. No directional forecast, paper trade or real-money action occurred.

## Nine-platform coordination

Run115 re-tested ChatGPT-to-GitHub read/write. No external platform authentication or data transfer was tested.

- ChatGPT: current-session GitHub read/write and public-web research verified.
- Copilot: comment-only PR activity; zero approvals; no separate authenticated pipeline.
- Claude, Grok, Gemini and Codex: unverified.
- Hugging Face: prior BUILD_ERROR, no deployment.
- Kaggle: untested, no submission.
- Databricks: HTTP 403, no workspace write.

Independent tasks remain DESIGNED, not EXECUTED. No secrets or repository content were sent to unverified platforms.

## Main workflow status and integrated regression repair

Main's recent scheduled Cross Analysis run [42758515738](https://github.com/Barrot-Agent/B-Agent/actions/runs/42758515738) succeeded. Main Pillars Consistency Check [42621970927](https://github.com/Barrot-Agent/B-Agent/actions/runs/42621970927) failed because GitHub App credentials were absent, Databricks returned HTTP 403 and the Hugging Face Space health check reported BUILD_ERROR. No credentials were rotated and no external action was attempted.

Main Hover Bike Updates [42572261311](https://github.com/Barrot-Agent/B-Agent/actions/runs/42572261311) failed artifact upload because its design generator ran from the nested project directory and generated output under a nested path. The integration branch changes that generator to run from repository root and includes a regression test. The workflow was not dispatched on the integration branch; runtime repair remains unverified.

## Open PR backlog — 372 total

| PR / workstream | Classification | Current evidence |
|---|---|---|
| #1640 | **Blocked integration** | Sole V3/XRP integration path |
| #1643 | **Unique/unreviewed** | 670 paths; 663 unique, 7 overlap; 906 ahead, 1 behind main; not mergeable; preserve |
| #1653 | **Unique but blocked** | 7 paths; 6 unique, 1 overlap; 18 ahead, 1 behind main; 8 unresolved review threads; preserve and repair |
| #1642 | **Superseded-content candidate** | Draft; 7/7 paths overlap #1640; no close before verified main successor |
| #1644–#1650 | **Overlap candidates** | All changed paths overlap #1640; reconcile exact versions/blobs after verified main integration |
| #1317/#1318/#1320 | **Overlap candidates** | All changed paths overlap #1640; retain until verified successor on main |
| #1254/#1255 | **Dependency reconciliation candidates** | Exact versions/blobs required |
| #1269 | **Unique/unreviewed** | 8 unique paths; preserve |
| #1655 | **Unique/unreviewed** | 3 unique paths; preserve |
| #1659 | **Unique/unreviewed** | 4 unique paths; preserve |

All four open-PR API pages were read. No PRs were closed.

## Merge decision — BLOCKED

PR #1640 remains open, non-draft, and GitHub reports mergeable/clean: 898 commits ahead, zero behind, 233 changed paths.

- 62 review submissions: all COMMENTED, zero APPROVED.
- 22 inline review threads: all resolved and all outdated.
- Current CodeRabbit review check: SKIPPED.
- Main branch-protection endpoint returned HTTP 403, “Resource not accessible by integration.”
- The only visible ruleset, “Fall Back,” is disabled.
- GitHub Pages is enabled; a prior main push triggered public Pages deployment [42526890275](https://github.com/Barrot-Agent/B-Agent/actions/runs/42526890275). PR #1640 changes public web assets. Specific authorization for automatic public publication is absent.

The user's conditional merge authorization is not satisfied. Do not bypass protection, merge or deploy.

## Next concrete actions

1. Obtain independent approval and authoritative branch-protection visibility.
2. Resolve the automatic GitHub Pages publication side effect before merge.
3. Trace Evernorth's 370.346M XRP outside the attributed wallet set using direct public rippled reads or an accessible independent explorer; classify destinations before any exchange-flow inference.
4. Reconcile ETF issuer holdings and the XRP Insights dashboard/detail weekly-flow conflict.
5. Preserve #1643 and #1653 unique work; do not bulk-close.
6. Once authorized and merged, fetch main, verify merge commit/files, run main CI and inspect workflow side effects.
7. Activate scheduled public ingestion only after verified main integration; establish independent receipt anchoring and synchronized historical XRP data.
8. Continue leakage-safe out-of-sample and shadow evaluation; no forecast until all gates pass.

## Run115 evidence files

- [Run115 structured market/CFTC/ETF/Evernorth/BNY artifact](research/xrp_intelligence/20261110T052028Z-run115-live-market-cftc-etf-evernorth-bny-update.json)
- [Run115 nine-platform snapshot](research/xrp_intelligence/nine_platform_coordination_snapshot_20261110T052028Z.json)
- [Current nine-platform capability map](research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_current.json)
- [PR #1640](https://github.com/Barrot-Agent/B-Agent/pull/1640)

No merge, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push or destructive worktree operation occurred.

---

## Run 114 archived handoff

## Mission and foundation

**Priority 1:** XRP intelligence and measured prediction-engine performance.

**Preserved foundation:** Barrot V3 remains the execution, orchestration, safety, permissions, evidence-verification and fail-closed foundation. No replacement of V3, no real-money execution and no automatic merge.

## Repository state — VERIFIED on Run114 evidence head

| Item | State |
|---|---|
| Main SHA | `d4d43be3427375cf79d190e768976de062e20287` |
| Latest verified integration head before this institutional addendum | `bb84e76278368aaf165628171fe36cfd4bf17fa4` |
| Existing integration PR | [#1640](https://github.com/Barrot-Agent/B-Agent/pull/1640) |
| Commits ahead / behind | 897 / 0 |
| Changed paths | 233 |
| Main tree | 1,404 entries / 1,299 files |
| Integration tree | 1,530 entries / 1,417 files |
| Main / integration workflow files | 86 / 87 |
| Open PR inventory | 372: 356 drafts, 16 non-drafts |

The branch already contains the priority-one mission manifest, 40-source registry, seven XRP workstreams, feature-store contracts, forecast ledger, prediction baselines and scheduled public-ingestion workflow. These assets are **not on main**. Main still lacks `data/missions/primary_mission.json` and `.github/workflows/xrp-public-ingestion.yml`.

No new branch or PR was created. Run114 research, the nine-platform snapshot and the canonical handoff were committed to the existing #1640 branch. The resulting evidence head `bb84e76278368aaf165628171fe36cfd4bf17fa4` subsequently passed exact-head full CI, dependency audit and fail-closed gate. This current institutional addendum is documentation/evidence-only and triggers another exact-head verification.

## Verification — EXECUTED and VERIFIED on `bb84e76278368aaf165628171fe36cfd4bf17fa4`

- Full repository suite: **1,347 passed, 0 failed, 8 subtests passed**.
- Inclusive package coverage: **59.48%**, above the 53% floor.
- Core suite: 677 passed, 8 subtests passed.
- Installed wheel: passed; Barrot V3, XRP mission assets and canonical data assets loaded.
- Dependency audit: six manifests passed; zero known vulnerabilities.
- Fail-closed merge gate: passed; automatic merge remains disabled.

Evidence:
- [Full CI 42754883526](https://github.com/Barrot-Agent/B-Agent/actions/runs/42754883526)
- [Dependency audit 42754883217](https://github.com/Barrot-Agent/B-Agent/actions/runs/42754883217)
- [Fail-closed gate 42754883215](https://github.com/Barrot-Agent/B-Agent/actions/runs/42754883215)

These are exact-head results for `bb84e76278368aaf165628171fe36cfd4bf17fa4`. The institutional addendum now being committed is documentation/evidence-only and requires its own exact-head CI. Packaging warnings remain for deprecated TOML license metadata and package-discovery warnings; they did not prevent wheel installation.

Main's latest CI [42526890841](https://github.com/Barrot-Agent/B-Agent/actions/runs/42526890841) passed 718 tests and 8 subtests on main. Main remains at `d4d43be3427375cf79d190e768976de062e20287`.

## Run114 XRP market evidence

**Capture cutoff:** 2026-11-10T04:09:55Z. These observations are descriptive and are not model-admitted.

### Spot

- Kraken XRP/USD: **$1.09053**; bid $1.09037 / ask $1.09038; 24-hour volume 27.71M XRP; 24-hour VWAP $1.09480; high/low $1.11573 / $1.07502.
- OKX XRP-USDT: **1.0924 USDT**; bid 1.0922 / ask 1.0923; 24-hour volume 69.72M XRP; provider event time 04:02:07.369 UTC.
- Kraken USDT/USD: 0.99865. Rough normalized OKX last is $1.09093, about 0.036% above Kraken. Quotes are asynchronous; this is not executable arbitrage evidence.

Exact surfaced API JSON text was SHA-256 hashed in the Run114 artifact. HTTP wire bytes and headers were not retained; receipt scope is explicitly limited to surfaced JSON text.

### Order-book depth

- Fuelmaps spot-only, 21:00 UTC Nov 9: within ±1%, bids $7.5M / asks $4.5M, 62.8% bid share, five of six venues reporting; Kraken was degraded. This is over seven hours old at capture.
- EdgeOrNot, 01:39 UTC Nov 10: within 1%, bids $8.5M / asks $8.2M, but combines Binance spot with OKX perpetual. It samples every minute and averages 15 minutes. It is not a pure spot book.
- The older XRPL DEX book-health snapshot (Oct 25) showed large quoted-versus-funded ask gaps on Bitstamp USD and GateHub USD, while the RLUSD/Ripple book was fully funded on the ask side. Historical only.

Distinguish quoted depth, funded depth, spot depth and perpetual depth. Visible orders can be cancelled; no wall is a guaranteed floor or ceiling.

### Derivatives

| Provider / cutoff | Open interest | 24h liquidations | Long side |
|---|---:|---:|---:|
| Liqwall, 02:22 UTC | $1.22B | $8.2M | $7.5M |
| TradRadar, 02:00 UTC | $1.66B | at least $9.08M | $8.22M |
| Alpha Finance, 01:40 UTC | $2.48B | $8.83M | $8.0M |

Funding is modestly positive in these snapshots. OI differs by roughly 2.03× because venue coverage and aggregation differ. The common observation is long-heavy deleveraging; it does not establish the next direction. Alpha liquidation clusters are modeled from OI and leverage tiers, not actual liquidation orders. A small Hyperliquid whale sample leaned short, but it is not market-wide exposure.

### CFTC positioning — contract distinction

The official CFTC report dated November 3 contains three XRP futures markets in the futures-only TFF report:

| Contract | Code | OI contracts | Contract size | XRP-equivalent OI |
|---|---|---:|---:|---:|
| CME XRP futures | 176740 | 7,216 | 50,000 XRP | 360.800M |
| Coinbase Nano XRP futures | 176LM1 | 32,505 | 500 XRP | 16.2525M |
| Coinbase Nano XRP Perp Style futures | 176LM3 | 38,392 | 500 XRP | 19.196M |
| **Gross contract-equivalent total** | | | | **396.2485M XRP** |

This is gross contract-equivalent open interest, not cash invested, unique unhedged exposure, spot demand or collateral.

CME 176740 TFF categories: dealers 4,228 long / 4,431 short; asset managers 868 / 802; leveraged funds 1,976 / 1,696. Coinbase Nano 176LM1 leveraged funds: 29,317 long / 31,625 short. Nano Perp Style 176LM3 leveraged funds: 1,780 long / 29,554 short; other reportables: 28,858 long / 2,853 short. These are trader-category aggregates, not identified entities.

The separate CME Legacy report shows noncommercial net +1,465 contracts; this is not equivalent to the TFF leveraged-funds category. CFTC's current contract-status index lists 176LM2 in the **futures-and-options combined** dropped section, not the futures-only dropped section. Its absence from this week's futures-only report must remain `not_reported_status_unverified`, not zero and not definitively dropped from futures-only reporting.

## ETF, custody and actual-capital reconciliation

### Issuer-primary ETF custody

- **Bitwise XRP ETP:** issuer page reports 406,770,577.61 XRP in trust as of Nov 8, market value $444.763M, 11.162749 XRP per share, 36.44M shares and AUM $444.717M. BNY Mellon is administrator and trust custodian; Coinbase Custody Trust Co. is digital-asset custodian. Expense ratio 0.34%. The product is not a 1940 Act registered investment company; ticker `XRP` is the fund share ticker, not the XRP token.
- **21Shares TOXR:** issuer page reports AUM/net assets $117.096M, 11M shares and 0.30% fee as of Nov 9. Custodians: Anchorage Digital Bank, BitGo Bank & Trust and Coinbase Custody International. Effective Aug 27, 2026, NAV benchmark changed from CME CF XRP-Dollar Reference Rate NY to FTSE XRP Index; pre-change history was not restated. The issuer page's holdings-unit table was blank in this capture.

### ETF tracker disagreement

- XRP Insights tracks six US spot funds plus BITW and reports 1.19523B XRP, $1.405B AUM, latest complete daily flow Nov 6: −663,043 XRP; Nov 2–6 week: −812.5K XRP. It says Nov 9 was not yet shown because issuer holdings settle the following morning.
- Its displayed Bitwise holding of 415.4M XRP is older than Bitwise's issuer-primary Nov 8 balance of 406.7706M by **8.595M XRP**. Its displayed TOXR AUM of $126.3M is about $9.2M above the 21Shares issuer page's $117.096M. Treat those tracker fields as stale/unreconciled.
- Corpstacking's 10-fund global ETF/ETP/trust universe reports 1.41514B XRP as of Nov 6. This is not the same universe as six US spot funds plus BITW.
- Alpha Finance reports a five-fund Nov 9 outflow of about $10.4M, while a prior CryptoKeyhole partial snapshot reported −8.789M XRP across two of four funds. These tracker universes, cutoffs and methods differ; do not average or treat them as issuer-confirmed cash flows.

A change in fund-held XRP is a holdings delta, not necessarily cash subscriptions/redemptions or an equivalent sale into spot. Cash versus in-kind AP redemptions and sponsor-fee transfers must be separated.

### Evernorth: cash, in-kind XRP, debt and contingent capacity

The Nov 9 SEC prospectus provides a company-reported closing balance; aggregator pages still labelling Evernorth as awaiting its first report are stale.

- Evernorth reports approximately **473M XRP held as of Oct 9**.
- At closing it reports approximately **$272.6M gross cash** before transaction expenses: $224.6M private-placement cash and $48M released from the SPAC trust.
- Investors contributed approximately **388.910554M XRP in kind**.
- The $214.05M advance-funding cash was used to purchase 84.365876M XRP historically, at an average $2.53657 per XRP. This was a 2025 purchase, not new Nov 2026 spot demand.
- Delayed funding included $10.5M cash and 200,000 XRP. Other in-kind tranches include 211.319M sponsor Series C XRP, 50M XRP from the contributor-related-party entity, 126.791M XRP from Ripple and 600,000 XRP from advance subscribers.

**Debt:** a $30M 4% PIK convertible note was issued Oct 12 to NH Investment & Securities as trustee of Kyobo AIM Corporate Finance General Private Investment Trust No. 3. The Nov 9 filing reports **$29M net cash after a $1M capital-markets-advisor fee**. Proceeds were intended for general corporate purposes, including XRP acquisition; the amount actually used to buy XRP is not established.

**Contingent equity facility:** Cantor may purchase up to 5,218,935 newly issued shares at 97% of VWAP, subject to a 4.99% ownership cap and 20% trading-volume cap. The $521,893.50 non-refundable commitment fee, additional fee cap, expense reimbursement and StoneX underwriter fee are costs, not proceeds. The Oct 30 prospectus's $76.8M gross / $74.4M net estimate does not reconcile cleanly with its 97%-VWAP formula: at the assumed $14.71 price, 5,218,935 shares equal $76.768M before discount, while 97% equals $74.447M before expenses. No purchase notice or settlement was identified in filings reviewed.

**Warrants and resale registration:**
- 11,499,992 public warrants at $11.50 imply up to $132.25M gross only if all are exercised for cash; no exercise receipts were verified.
- The Nov 9 resale prospectus registers 73,688,162 shares for selling securityholders. Evernorth receives no proceeds from those resales, except up to about $2.8M if the separate 239,653 sponsor warrants are exercised for cash. This is potential XRPN equity supply, not new XRP capital.

**On-chain custody gap:** XRP Insights reports 103,129,905 XRP in 13 attributed Evernorth wallets at ledger 108,231,279 (Nov 10, 03:45 UTC) and 370,346,663 XRP transferred outside that attributed set, latest Oct 22. The tracker says the wallets use 2-of-3 multisig with master keys disabled. XRPSCAN transaction-detail requests returned HTTP 403 during this run, so those transfers were not independently re-read. The 370.3M XRP is **not evidence of sale, exchange deposit, loss or encumbrance**; destination wallets remain unclassified. This is a priority investigation, not a bearish flow feature.

## Institutional relationship updates — Q3 2026 primary filings

- **Coinbase–Circle USDC economics:** Circle's Q3 2026 10-Q reports $331.3M of distribution costs to Coinbase in Q3 and $986.6M for nine months. Coinbase's Q3 10-Q reports $306.905M stablecoin revenue in Q3 and $904.487M for nine months. Coinbase says its Circle agreement was renewed on the same terms in 2026 and average USDC held in Coinbase products reached an all-time high. These are different accounting measures, not nettable profit, not direct cash-flow equivalence and not XRP demand. Higher USDC balances were partly offset by lower reserve/interest rates.
- **Circle–SBI Japan:** Circle SBI Japan K.K. is 50% Circle / 50% SBI; each contributed approximately $1.5M. Circle's Q3 filing says it had no significant operating results through September 30, 2026. This is an operating/distribution vehicle, separate from SBI's strategic equity investment in Circle.
- **SBI–Evernorth ownership:** the Nov 9 SEC prospectus attributes 9,431,914 Class A shares and 2,359,038 Class C shares to four SBI-controlled stockholders. That equals 21.4% of common stock and 39.9% of voting power. It is the largest disclosed voting block, not majority control. The filing says voting/dispositive decisions are made by the SBI board on management recommendation by majority vote; no individual board member alone controls the shares.
- **Coinbase custody capital:** Coinbase's Q3 filing reports Coinbase Custody Trust Company net capital of $618M against $222M required, a $396M regulatory capital surplus at September 30. This is a custody-subsidiary regulatory buffer, not XRP holdings or collateral.
- **XRP custody network:** Coinbase Custody Trust Co. is Bitwise's digital-asset custodian; BNY Mellon is Bitwise's trust custodian/administrator. TOXR lists Coinbase Custody International, Anchorage and BitGo. Evernorth names BitGo Trust. These are service roles, not proof of proprietary XRP purchases.
- **SBI–Ripple:** previously verified SBI's approximate 9–10% Ripple equity interest, SBI Ripple Asia's 60/40 SBI/Ripple ownership, and SBI Remit corridors in the Philippines, Vietnam and Indonesia that use XRP as a bridge currency. Current corridor volumes remain undisclosed. RLUSD distribution, JPYSC lending and tokenized-deposit POCs remain separate from XRP bridge conversion.
- **Coinbase–Ripple/USDC alternatives:** Coinbase's prior asset-disclosure snapshot reported XRP and cbXRP holdings and commercial engagement, while RLUSD was commercially engaged but not held at that snapshot. The PNC/Coinbase/Circle USDC pilot remains an alternative institutional dollar rail, not an XRP corridor.
- **Sources:** [Circle Q3 10-Q](https://www.sec.gov/Archives/edgar/data/1876042/000187604226000311/crcl-20260930.htm), [Coinbase Q3 10-Q](https://www.sec.gov/Archives/edgar/data/1679788/000167978826000122/coin-20260930.htm), [Evernorth Nov 9 prospectus](https://www.sec.gov/Archives/edgar/data/2092592/000162828026072223/evernorth-424b3.htm).

## Identity research

- Japan's SBIC East/Central/West remain Tokyo/Nagoya/Osaka regional policy-investment companies, distinct from SBI Holdings.
- Tokyo SBIC's official course includes ChatGPT and Copilot instruction; this is training for investee companies, not an OpenAI partnership.
- No new primary-source match for the exact phrase “SBIC, ChatGPT SBIC.”
- ASK Coin remains unresolved; Permission Coin ASK is a candidate, with no verified XRP integration.
- “Actual capital” is not a standardized XRP metric. Use the cash / in-kind / debt / contingent capacity / secondary resale taxonomy above.
- Camilla/Kamilah Stevenson identity and guest-appearance evidence remain separate from personal-channel ownership. No new personal-channel upload was added without independent channel verification.

## Prediction-engine readiness

**Implemented on the integration branch, not main:** 40 public source records (36 hourly, two weekly CFTC, two excluded non-commercial XRPL nodes), raw-byte SHA-256 receipt capture in the workflow, receipt-chain logic, point-in-time SQLite feature store, four deterministic baselines, chronological walk-forward with purge/embargo, calibration and drift diagnostics, and a fail-closed forecast ledger requiring a trusted Ed25519 evaluator signature.

**Still blocking forecast eligibility:** independent WORM/timestamp anchoring; synchronized historical spot/L2/exchange-flow/derivatives/collateral history; effective-sample-size correction for overlapping horizons; real-data calibration; at least 100 out-of-sample and 100 shadow outcomes; two independent source groups; calibration error at or below 0.05; at least ten horizon multiples; and demonstrated lift over naive baselines. The scheduled ingestion workflow is main-only and is not active on main.

**Forecast status: NOT_ISSUED.** Run114 observations are research-only. No directional forecast, paper trade or real-money action occurred.

## Nine-platform coordination

The current capability map remains at `research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_current.json`. The Run114 snapshot is linked below.

- ChatGPT: current-session GitHub read/write and public-web research verified.
- Copilot: comment-only GitHub review activity; zero approvals; no separate authenticated data flow.
- Claude, Grok, Gemini and Codex: no tested authentication or data flow.
- Hugging Face: prior build error, not revalidated; no deployment.
- Kaggle: untested; no submission.
- Databricks: prior HTTP 403; no workspace write.

No external model received repository data. Independent tasks remain designed, not executed. Evidence disagreements are resolved by primary-source quality and timestamp, not majority vote; minority objections remain recorded.

## Open PR backlog — 372 total

| PR / workstream | Classification | Evidence / action |
|---|---|---|
| #1640 | **Blocked integration** | Sole V3/XRP integration path; keep active |
| #1643 | **Unique/unreviewed** | 670 changed paths; 663 unique, 7 overlap; preserve |
| #1653 | **Unique but blocked** | 7 paths; 6 unique, 1 overlap; 8 unresolved review threads; preserve and repair |
| #1642 | **Superseded-content candidate** | 7/7 paths overlap; do not close before successor merge and exact blob reconciliation |
| #1644–#1650 | **Overlap candidates** | All changed paths overlap #1640; reconcile exact versions/blobs after verified main integration |
| #1317/#1318/#1320 | **Overlap candidates** | All changed paths overlap #1640; retain until verified successor on main |
| #1254/#1255 | **Dependency overlap candidates** | 1/1 path overlap each; exact version reconciliation required |
| #1269 | **Unique/unreviewed** | 9 paths; 8 unique, 1 overlap; preserve |
| #1655/#1659 | **Unique draft material** | Preserve unique content |

No PRs were closed. Do not bulk-close unique research, graph, mesh or draft work.

## Merge decision — BLOCKED

PR #1640 remains open, non-draft and GitHub reports mergeable/clean. It is 897 commits ahead, zero behind, with 233 changed paths. Current verified head before this addendum: `bb84e76278368aaf165628171fe36cfd4bf17fa4`.

- 62 review submissions: all `COMMENTED`, zero `APPROVED`.
- 22 review threads: all resolved, but outdated relative to the current head.
- CodeRabbit review check was skipped.
- Main reports `protected=true`, but the detailed branch-protection endpoint returned HTTP 403. The visible fallback ruleset is disabled; effective required approvals/checks remain unverified.
- GitHub Pages is enabled. A prior main push triggered successful public Pages deployment [42526890275](https://github.com/Barrot-Agent/B-Agent/actions/runs/42526890275). PR #1640 changes public web assets. Specific authorization for automatic public publication is absent.

The user's conditional merge authorization is not satisfied. Do not bypass branch protection, merge or deploy. No PR was closed.

## Next concrete actions

1. Run exact-head full-suite, dependency/security and fail-closed checks on the Run114 evidence/handoff commit.
2. Obtain independent approval and authoritative branch-protection visibility.
3. Resolve the GitHub Pages publication side effect before merge.
4. Preserve #1643 and #1653 unique work; do not bulk-close.
5. Reconcile ETF issuer daily holdings, share counts and cash/in-kind redemption mechanics.
6. Trace Evernorth's 370.3M XRP transfers using direct public rippled reads or an accessible independent explorer; classify destinations before any exchange-flow inference.
7. Continue synchronized historical spot/L2/derivatives/CFTC/collateral ingestion and independent raw-source anchoring.
8. Ingest the scheduled US October CPI release only after publication; do not issue a forecast without validated out-of-sample lift and shadow outcomes.

## Run114 evidence files

- [Run114 structured research artifact](research/xrp_intelligence/20261110T040955Z-run114-market-cftc-etf-custody-actual-capital.json)
- [Run114 nine-platform coordination snapshot](research/xrp_intelligence/nine_platform_coordination_snapshot_20261110T040955Z.json)
- [Current nine-platform capability map](research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_current.json)
- [PR #1640](https://github.com/Barrot-Agent/B-Agent/pull/1640)

No merge, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push or destructive worktree operation occurred.


---

## Run 129 — 2026-11-10T12:00Z

### Mission and repository state

XRP intelligence and measured prediction-engine mastery remain priority one. Barrot V3 remains the execution, orchestration, safety and verification foundation.

- Main SHA: `d4d43be3427375cf79d190e768976de062e20287`.
- Main tree: 1,404 entries / 1,299 files / 105 trees.
- Integration branch: `integration/core-capabilities-mmi-structural-paper-20261104`.
- Integration head before this handoff update: `b802664e6f0084ca6c105dc6891d7ed9886ad9ac`.
- Integration tree at the preceding head: 1,554 entries / 1,441 files / 113 trees.
- PR #1640: open, non-draft, GitHub reports mergeable; 940 commits ahead / zero behind at the preceding head; 257 changed files, 124,024 additions and 3,554 deletions. The two Run129 implementation/research commits increase the diff and ahead count; refresh PR metadata after this handoff commit.
- Open PR inventory: 372 total, 356 drafts and 16 non-drafts, enumerated across four REST pages (100/100/100/72).

### DESIGNED / EXECUTED / VERIFIED

**VERIFIED — exact prior integration head `1037d4d2e59339612c8b5d74f61751aa5f10be0a`:**

- Full repository suite: 1,368 passed, zero failed, eight subtests passed.
- Inclusive package coverage: 59.58%, above the 53% floor.
- Core suite passed.
- Wheel build and installed-wheel verification passed, including Barrot V3, XRP mission and canonical data assets.
- Six dependency manifests audited; zero known vulnerabilities.
- Fail-closed merge gate passed; automatic merging disabled.

Exact evidence:
- Full CI: [42806308425](https://github.com/Barrot-Agent/B-Agent/actions/runs/42806308425)
- Dependency audit: [42806308755](https://github.com/Barrot-Agent/B-Agent/actions/runs/42806308755)
- Fail-closed gate: [42806308349](https://github.com/Barrot-Agent/B-Agent/actions/runs/42806308349)

**EXECUTED — integrated whole-repository repair:**

Main's November 9 Hover Bike workflow failed because `hover_bike_generator.py` wrote into a nested `hover_bike_revolution/hover_bike_revolution/` directory while the workflow uploaded files from `hover_bike_revolution/`. The generator entrypoint now resolves its output directory from `Path(__file__).resolve().parents[1]`. A new regression test copies and executes the entrypoint in a temporary project, verifies all four generated artifact paths, and checks that the workflow upload paths match.

- Generator fix commit: `f2742034585911d549540aa044d61f1720f88787`.
- Regression test commit: `c6ba6d917a30ec99da3f12314e895c40cade41f8`.
- Structured Run129 evidence artifact: `research/xrp_intelligence/20261110T120000Z-run129-market-exchange-flow-etf-governance-repository-update.json`.
- Evidence artifact commit: `b802664e6f0084ca6c105dc6891d7ed9886ad9ac`.

**PENDING — descendants after the prior verified head:**

The exact-head CI was queued after the Hover Bike fix, regression test and Run129 artifact. The full suite, core job and dependency audit must be checked on the final handoff descendant; do not reuse the 1037d4d2 test result as proof for a later SHA.

### Current main workflow findings

Main has not advanced from `d4d43be3427375cf79d190e768976de062e20287`.

- Latest hourly Cross Analysis: [42810898786](https://github.com/Barrot-Agent/B-Agent/actions/runs/42810898786), success, 2026-11-10 11:51:41 UTC.
- Last main full CI: [42526890841](https://github.com/Barrot-Agent/B-Agent/actions/runs/42526890841), success, 718 tests and eight subtests, 2026-11-08 21:46:48 UTC.
- Main dependency audit: [42579080840](https://github.com/Barrot-Agent/B-Agent/actions/runs/42579080840), success, 2026-11-09 07:23:53 UTC.

Outstanding main workflow failures were inspected from job logs:

1. Pillars Consistency Check [42621970927](https://github.com/Barrot-Agent/B-Agent/actions/runs/42621970927): missing GitHub App ID/private key/installation ID, Databricks HTTP 403 and Hugging Face BUILD_ERROR. This is blocked by external authentication/provider health. No credentials were read, invented or rotated.
2. Hover Bike Updates [42572261311](https://github.com/Barrot-Agent/B-Agent/actions/runs/42572261311): missing artifact paths. The entrypoint defect is corrected on the integration branch; the workflow has not yet been re-dispatched there.
3. Riemann Research Harvest [42556313011](https://github.com/Barrot-Agent/B-Agent/actions/runs/42556313011): shared test conftest could not import pydantic. The integration workflow now installs `pytest` and `pydantic-settings` before its validation step; it has not yet been re-dispatched there.

The Pages deployment on the previous main push succeeded at [42526890275](https://github.com/Barrot-Agent/B-Agent/actions/runs/42526890275). The current GitHub integration cannot read Pages configuration.

### Run129 XRP market evidence

**Spot snapshot, cutoff approximately 2026-11-10 12:00 UTC:**

- Kraken XRP/USD: last $1.08051; bid $1.08051; ask $1.08052; 24-hour volume 24.954M XRP; 24-hour VWAP $1.09393985; high/low $1.11573/$1.07367. Kraken's ticker response did not include a provider event timestamp.
- OKX XRP-USDT: 1.0807; bid 1.0806; ask 1.0807; 24-hour volume 60.716M XRP and 66.522M USDT; provider timestamp 2026-11-10 11:53:46.923 UTC.
- Kraken USDT/USD: 0.99881. Mechanically normalized OKX reference: $1.079414, approximately 0.1014% below Kraken. These observations are asynchronous and are not an executable arbitrage spread.
- A synchronized fresh spot L2 snapshot was not captured in this run. Do not label older depth as current.

Sources: [Kraken XRP/USD](https://api.kraken.com/0/public/Ticker?pair=XRPUSD), [OKX XRP-USDT](https://www.okx.com/api/v5/market/ticker?instId=XRP-USDT), [Kraken USDT/USD](https://api.kraken.com/0/public/Ticker?pair=USDTUSD).

**Derivatives — disagreement preserved:**

- TradRadar, 08:15 UTC: approximately $1.64B OI across seven venues, −4.16% over 24h, OI-weighted funding +0.0046% per eight hours, at least $3.70M liquidations (approximately $2.90M long / $0.801M short), 79.9% long accounts.
- Liqwall, 08:32 UTC: approximately $1.21B OI, −3.2% over 24h, average funding +0.0027% per eight hours, approximately $3.7M liquidations ($3.1M long / $631K short).
- OptimistFi, 11:00 UTC: approximately $1.4B OI across 36 perpetual venues, −1.5% over 24h.

Different venue universes and methods explain why these are not interchangeable. Do not average them. The shared descriptive evidence is declining OI and long-heavy liquidations, not a directional forecast.

Sources: [TradRadar](https://tradradar.io/markets/xrp), [Liqwall](https://liqwall.com/coins/xrp), [OptimistFi](https://optimistfi.com/perps/open-interest/xrp).

**Exchange-wallet balances, November 10 08:00 UTC:**

XRP Insights reports 22.33B XRP across 701 publicly attributed wallets at 24 exchanges. Same-wallet-set balances fell 8.9M XRP over seven days and 150.9M over 30 days. A naive total change of +361.1M is distorted by two newly tracked wallets containing 512M XRP.

The tracked total includes approximately 481M XRP in wrapped-token backing and other reserves: 325.8M Binance XRP-BF2, 150.1M Coinbase cbXRP and 5.2M insurance/charity funds. It is not tradable float. The same 150.1M cbXRP reserve may overlap separate DeFi/collateral views and must not be double counted. Upbit is the largest tracked balance at 6.46B XRP, followed by Coinbase 5.80B and Binance 2.69B. OKX and Korbit wallet coverage is incomplete; 39.9% of the tracked balance lacks a hot/cold label.

Source: [XRP Insights exchange balances](https://xrp-insights.com/exchange-balances). Ledger reads are public, but wallet attribution depends on public labels and coverage; retain as an attributed-wallet measure, not a complete venue reserve series.

**ETF flows, November 9 trading day:**

CryptoKeyhole's issuer-file tracker, last checked 11:58 UTC, reports three of four daily-tracked funds:

- Bitwise: −8,594,551 XRP.
- Canary: −427,341 XRP.
- 21Shares TOXR: −194,660 XRP.
- Franklin XRPZ: missing.
- Partial total: −9,216,553 XRP, approximately −$10.1M.

Alpha Finance reports approximately −$10.4M across five displayed funds and a different Canary component (approximately −$811.4K). The trackers have different coverage, publication timing and conversion/zero-fill methods; they overlap issuer inputs and are not independent confirmations. Holdings/share changes do not prove exchange sales or establish cash versus in-kind redemption. ETF flow features remain model-ineligible.

Sources: [CryptoKeyhole issuer-file tracker](https://cryptokeyhole.com/etf-flows/xrp/), [Alpha Finance](https://alphafinance.io/etf/xrp/).

**XRPL governance, voting ledger 108,238,591 at 11:50 UTC:**

- 35/35 trusted validators heard; 29 votes required.
- 98 amendments enabled, nine in flight, zero in the 14-day activation countdown.
- SingleAssetVault 23/29; LendingProtocol 22/29; LendingProtocolV1_1 22/29; ConfidentialTransfer 21/29; DynamicMPT 16/29; fixXChainRewardRounding 10/29; Sponsor 10/29; XChainBridge 4/29; CryptoConditionsSuite 0/29.
- The activation rule is strictly more than 80% for 14 consecutive days; a drop to 80% or less resets the window.

SingleAssetVault and LendingProtocol are not active. XRPL native lending is not operational and must not be counted as live collateral or lending capacity.

Sources: [XRPL Dashboard](https://xrpldashboard.com/amendments), [XRPLWin SingleAssetVault](https://xrplwin.com/amendment/SingleAssetVault), [XRPL amendment documentation](https://xrpl.org/docs/concepts/consensus-protocol/amendments).

**Macro:** October 2026 U.S. CPI and Real Earnings were scheduled for 2026-11-10 13:30 UTC. They had not been released at the 12:00 UTC cutoff. No result was inferred. [BLS schedule](https://www.bls.gov/schedule/2026/11_sched.htm).

### Prediction engine and data integrity

The integration branch contains 46 public-source definitions: 42 hourly, two weekly CFTC and two excluded non-commercial XRPL nodes. Implemented components include a read-only collector, SHA-256 receipt-chain logic, point-in-time SQLite feature store, four deterministic baselines, chronological walk-forward evaluation with purge/embargo, calibration/drift diagnostics and a fail-closed fixed-horizon forecast ledger requiring trusted Ed25519 evaluator attestation.

Not production-ready:
- independent WORM storage and trusted timestamp anchoring;
- complete synchronized historical spot, L2, derivatives, exchange-flow and collateral datasets;
- authenticated source independence;
- effective-sample-size/block-bootstrap correction for overlapping horizons;
- sufficient independent shadow outcomes;
- demonstrated out-of-sample lift.

The scheduled collector remains on the integration branch, not main. Its workflow uses read-only repository permissions and Actions artifacts/cache; artifacts expire (raw receipts/daily backup 90 days, per-run feature checkpoint seven days), and cache is evictable. This is not WORM storage. No successful scheduled main ingestion is verified.

Raw web API transport bytes and headers were not retained in this run. The displayed response values are research cross-checks, not model-admitted feature-store rows. The Run129 JSON records provider timestamps, coverage and limitations.

**Forecast status: NOT_ISSUED.** No directional forecast, paper trade or real-money action.

### Nine-platform status

- ChatGPT: current-session GitHub read/write verified.
- Copilot: one-off COMMENTED PR review activity only; zero approvals.
- Claude, Grok, Gemini and Codex: no tested persistent authentication/data flow.
- Hugging Face: prior BUILD_ERROR; no successful deployment.
- Kaggle: not tested; no submission.
- Databricks: prior HTTP 403; no workspace write.

No external-model data transfer occurred.

### Backlog classification

All 372 open PRs remain open: 356 drafts, 16 non-drafts. The 16 non-drafts are #1653, #1650–#1643 (including #1640), #1320, #1318, #1317, #1269, #1255 and #1254.

Selected path-overlap checks against #1640:
- #1643: 670 changed paths, seven overlap, 663 unique; non-draft and non-mergeable. Preserve unique research.
- #1653: seven changed paths, one overlap, six unique; GitHub says mergeable, but eight current unresolved review threads. Preserve; blocked pending review repair.
- #1642: seven of seven overlap; draft, duplicate/superseded candidate only after verified successor merge.
- #1614: 57 changed, eight overlap, 49 unique; stale/non-mergeable; preserve unique prediction work.
- #1611: eight changed, six overlap, two unique; stale/non-mergeable.
- #1615: 14 changed, one overlap, 13 unique.
- #1610: 14 changed, seven overlap, seven unique.
- #1608: three changed, zero overlap, three unique.
- #1607: eight changed, one overlap, seven unique.
- #1606: nine changed, one overlap, eight unique.
- #1605: one unique path.
- #1604: two changed, one overlap, one unique.
- #1603: four changed, two overlap, two unique.
- #1644: eight of eight overlap; #1645, #1646, #1648, #1649 and #1650 each have all changed paths overlapping #1640; #1647 has six of six overlapping.
- #1317: six of six overlap; #1318: two of two; #1320: five of five.
- #1269: nine changed, one overlap, eight unique; stale/non-mergeable.
- #1655: eight changed, five overlap, three unique.
- #1659: six changed, two overlap, four unique.
- #1641: three changed, zero overlap, three unique.

Path overlap is not semantic equivalence. Do not close any source PR before a successor is merged and verified on main. Preserve unique research, prediction, topology and repository-graph work. Remaining unreviewed PRs stay unique/unreviewed pending semantic classification.

### Merge decision

PR #1640 remains unmerged.

- 62 review submissions, all COMMENTED; zero APPROVED.
- 22 review threads are resolved but outdated.
- GitHub reports main protected, but required status contexts are empty; detailed required-review protection endpoint returns HTTP 403.
- The visible repository ruleset “Fall Back” is disabled.
- Pages configuration is not accessible; previous main push did trigger a successful public deployment.
- Specific authorization for the automatic public Pages side effect is not established.

The user's conditional merge authorization is therefore not satisfied. Do not bypass branch protection. Do not merge, deploy or close source PRs.

### Next concrete actions

1. Verify full-suite, core, dependency and fail-closed results on the final descendant containing the Hover Bike repair and Run129 handoff.
2. Obtain independent approval and authoritative branch-protection visibility for #1640.
3. Resolve authorization for automatic GitHub Pages publication.
4. Re-dispatch only the safe Hover Bike and Riemann artifact-only workflows after their fixes are verified on the branch; do not treat the old main failures as resolved until a new successful run exists.
5. Keep Pillars blocked until valid GitHub App and Databricks/Hugging Face access is independently tested; do not invent credentials.
6. Reconcile exchange-wallet reserve overlap, ETF issuer cash/in-kind mechanics, and current Morpho collateral/oracle state before feature admission.
7. Preserve raw-source bytes/headers, provider timestamps, SHA-256 receipts and independent anchoring when scheduled ingestion is activated on main.
8. Continue leakage-safe walk-forward and shadow evaluation; issue no directional forecast until every readiness gate passes.

No merge, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push or destructive worktree operation occurred.


## Run 129B — stablecoin, RWA and payment-rail reconciliation

### RLUSD supply: two clocks and two measurement layers

At approximately 11:57 UTC on November 10, XRPL Dashboard displayed:

- Total RLUSD: $2.69B.
- Ethereum: $1.81B, 67.4%.
- XRP Ledger: $877.66M, 32.6%.
- Rolling 24-hour net supply change: +$20.04M.
- XRPL 24-hour net supply change: +$12.54M.
- Ethereum mints: $19.40M; burns: $11.91M.

The dashboard explicitly reported its live feed unavailable and warned that totals may be a few minutes stale. Ethereum-side data is not anchored in its daily signed snapshot chain. Its XRPL supply method uses `gateway_balances`; Ethereum uses `totalSupply()` and Etherscan V2 token-transfer data. It says the 24-hour net change was cross-checked against independent RPC for November 9 finalized data, not necessarily for the live November 10 snapshot.

Ripple's own transparency page separately displays $2.6329B circulating RLUSD and $2.7480B reserve funds as of November 5. The implied reserve/circulation ratio is approximately 104.37%. The visible linked monthly attestations extend through September 2026; do not describe the November 5 balance as independently attested without the matching report.

The displayed difference between the dashboard's $2.69B and Ripple's November 5 $2.6329B is $57.1M, approximately 2.17% of the issuer-page figure. It may reflect intervening growth, measurement timing or coverage. It is not a verified net mint or independent reconciliation.

Sources:
- [XRPL Dashboard RLUSD supply](https://xrpldashboard.com/rlusd)
- [Ripple RLUSD transparency](https://ripple.com/products/stablecoin/transparency/)

RLUSD on XRPL is stablecoin supply. It is not XRP demand, XRP collateral, or XRP bridge volume.

### XRPL RWA: tokenized value is not executable liquidity

XRPL Dashboard's November 10 RWA view reports:
- Eight issuer families catalogued.
- One strict two-way issuer-domain/TOML attestation.
- Two labeled AMM families and five MPT-attested families.
- Seven attributed pools.
- $438.73 directly attributed AMM liquidity.
- Attribution set last updated May 14, 2026; this is not a re-verification date.

The dashboard itself characterizes direct AMM liquidity as nominal and institutional RWA activity as early phase. Ondo's OUSG is described as a canonical issuer-attested family with no standing AMM liquidity. Other entries are curated labels or one-way MPT attestations rather than the strict two-way issuer proof.

The dashboard's May 3 third-party RWA.xyz footnote cites $3.6B represented on XRPL, divided into approximately $1.0B distributed and $2.6B represented value. This is a historical third-party estimate, not current direct liquidity and not a dashboard measurement.

It also excludes or leaves pending several recognizable names where the issuer wallet/domain proof is incomplete. A vanity wallet or pool label is not issuer attestation.

Source: [XRPL Dashboard RWA methodology and issuer list](https://xrpldashboard.com/rwa).

### Institutional payment rails: confirmed announcements versus XRP demand

1. **Ondo / Kinexys by J.P. Morgan / Mastercard / Ripple — May 6, 2026.** Ondo reported a completed cross-border, cross-bank redemption of a tokenized U.S. Treasury fund. The XRPL asset leg was reported under five seconds; Kinexys settled USD proceeds to Ripple's bank account in Singapore. This demonstrates an institutional XRPL asset leg, not an XRP bridge conversion. [Ondo announcement](https://www.prnewswire.com/news-releases/ondo-kinexys-by-jp-morgan-mastercard-and-ripple-complete-first-cross-border-cross-bank-redemption-of-tokenized-us-treasuries-302764324.html).

2. **Mastercard — June 3, 2026.** Mastercard announced plans for additional intraday, weekend and holiday settlement, including regulated stablecoins such as USDC, RLUSD, SoFiUSD and Paxos-issued tokens across eight supported chains, including XRPL. The named initial partners include ARQ, CBW Bank, Cross River, Lead Bank and Nuvei. The release describes a network-level rollout subject to regulation and partner implementation, not a live XRP corridor. [Mastercard announcement](https://www.mastercard.com/global/en/news-and-trends/press/2026/june/mastercard-expands-settlement-capabilities-to-include-stablecoin.html).

3. **Ripple / Flutterwave — June 16, 2026.** Flutterwave announced Ripple's strategic investment in its Series E and a partnership to embed RLUSD in payment rails and Send App remittance corridors, use XRPL for transaction clearing, and integrate Ripple Payments. Flutterwave stated a $3.2B Series E valuation but did not disclose Ripple's investment amount. This is an announced product/investment relationship; operational corridor volumes were not verified. [Flutterwave announcement](https://flutterwave.com/us/blog/ripple-participates-in-flutterwaves-series-e-with-strategic-investment-to-accelerate-african-stablecoin-payments).

4. **Circle Ventures / Flutterwave — July 7, 2026.** Flutterwave subsequently announced a Circle Ventures investment and USDC settlement expansion, while describing RLUSD as the default stablecoin across its stablecoin products, supported by Ripple Payments and XRPL. This indicates a multi-stablecoin, multi-rail strategy: Ripple and Circle are both investors/partners in Flutterwave, but this does not establish a direct Ripple–Circle partnership or XRP conversion volumes. [Flutterwave stablecoin infrastructure update](https://flutterwave.com/cm/blog/building-the-stablecoin-infrastructure-for-africa).

5. **SG-FORGE — February 18, 2026.** EUR CoinVertible launched on XRPL with Ripple custody support. SG-FORGE said collateral and trading-collateral use cases could be explored; the announcement does not establish current collateral utilization. [SG-FORGE announcement](https://www.sgforge.com/sgf-coinvertible-on-the-xrp-ledger/).

### Analytical conclusion

Institutional adoption on XRPL is increasingly stablecoin- and tokenized-asset-oriented. That can raise XRPL transaction activity without creating equivalent XRP bridge demand. Distinguish at least five features: stablecoin supply on XRPL, tokenized-asset represented value, distributed tokenized value, executable AMM/order-book liquidity, and XRP bridge conversion volume. Do not substitute one for another.

The new structured evidence is in [Run129 market/flow/governance artifact](research/xrp_intelligence/20261110T120000Z-run129-market-exchange-flow-etf-governance-repository-update.json), under `stablecoin_rwa_payment_network`.


## Run 129C — exact-head verification and identity resolution

### Exact-head integrated verification

The final code/test head for the Run129 implementation fixes was `04b3228ff44e5b738cd02fae7acac0f0f29638b3`.

<badge>VERIFIED</badge>

- Full repository suite: **1,371 passed, zero failed, eight subtests passed**.
- Inclusive coverage: **59.58%**, above the 53% floor.
- Core suite: **677 passed**.
- Wheel build and installed-wheel verification passed.
- Installed wheel loaded Barrot V3, the XRP mission and canonical data assets.
- Six dependency manifests passed; zero known vulnerabilities.
- Fail-closed gate passed; automatic merging remains disabled.

Exact evidence:
- [CI — 42813504144](https://github.com/Barrot-Agent/B-Agent/actions/runs/42813504144)
- [Dependency audit — 42813504079](https://github.com/Barrot-Agent/B-Agent/actions/runs/42813504079)
- [Fail-closed gate — 42813504064](https://github.com/Barrot-Agent/B-Agent/actions/runs/42813504064)

The full-suite log collected 1,371 tests and reported 59.58% coverage. The wheel step verified the packaged primary mission and imports. The only warning was the GitHub Actions cache budget becoming read-only; the tests, wheel and dependency audit succeeded.

The final identity-research JSON update and this handoff addendum are documentation/evidence-only descendants of the verified code/test head. Their PR synchronization runs must still be checked separately; do not claim they were covered by the 04b322 test run.

### Whole-repository workflow repairs

- Hover Bike Updates: the generator entrypoint now resolves the output directory relative to its own file, so its four files land in the paths the workflow uploads. Regression tests execute a copied entrypoint in a temporary project and verify the four expected outputs and absence of a double-nested directory.
- Riemann Research Harvest: a regression test verifies that `pytest` and `pydantic-settings` are installed before the test command, preventing the missing-`pydantic` conftest failure.
- Both fixes are on the integration branch. The original failed main workflows have not yet been re-dispatched on the branch; they remain unverified operationally.
- Pillars remains blocked by missing GitHub App credentials, Databricks HTTP 403 and Hugging Face BUILD_ERROR. No credential workaround or success claim was made.

### Exact-phrase and identity research update

**ASK Coin is ambiguous and at least two distinct listings must remain separate:**

1. CoinMarketCap's Ask Coin exchange listing is marked inactive/untracked, with no reserve data and no usable market table. [Listing](https://coinmarketcap.com/exchanges/ask-coin/).
2. Permission Coin's ASK token is a separate Polygon/Base asset. The retrieved CoinMarketCap snapshot displayed 100B maximum supply, approximately 16.1666B circulating, approximately $1.4M market capitalization, approximately $891.78 24-hour volume and approximately 206.18K holders. [Permission Coin](https://coinmarketcap.com/currencies/permission-coin/).

Neither listing establishes an XRP integration. Do not infer that either is the user's intended ASK Coin without additional primary evidence.

**“SBIC, ChatGPT SBIC”:** no exact-phrase evidence of a formal ChatGPT–SBIC partnership was found. Tokyo SBIC's official 2025 course lists ChatGPT and Copilot training for investee companies. This is training activity, not an OpenAI partnership. [Tokyo SBIC course](https://www.sbic.co.jp/training/20250612co/).

**“Actual capital”:** no standardized XRP project metric by that exact name was established. Continue separating settled cash subscriptions/purchases, in-kind XRP, debt actually drawn, contingent facilities/warrants and secondary resales. Market capitalization, registered resale capacity, undrawn financing and custody balances are not realized XRP capital.

**Kamilah Stevenson YouTube attribution:**

- A likely candidate surfaced: `@drkamilahstevenson`, channel ID `UCqUPJMQdkCN6lsLVDnichPA`. Third-party analytics report roughly 139K–143K subscribers and approximately 1.2K videos; its description matches stocks, crypto, macro and long-term investing.
- A first-party page, [learn.kamilahstevenson.com](https://learn.kamilahstevenson.com/), identifies Dr. Kamilah Stevenson as “The Wealth Doctor.” A separate [Buy Me a Coffee page](https://buymeacoffee.com/kamilahstevenson) uses the same name and health/wealth-coach description.
- Neither visible first-party page links to the candidate YouTube channel. A third-party Telegram directory links to the handle, which is insufficient proof of ownership.
- Several same-name channels exist, including `@CoachKamilahStevensonxrp` and Kamilah Stevenson Digital Network. A Vimeo listing titled “How $23 Turned Into $27,000” is a separate candidate, not proof of YouTube channel ownership.

**Identity status: UNVERIFIED CANDIDATE ONLY.** No personal YouTube video inventory was created or attributed. Require a first-party cross-link or equivalent primary identity proof before inventorying the candidate channel's videos.

The detailed candidate records and caveats are in [Run129 structured evidence](research/xrp_intelligence/20261110T120000Z-run129-market-exchange-flow-etf-governance-repository-update.json).

### Current merge posture

The latest verified code/test head is `04b3228`; the evidence/handoff descendants advance the integration branch but do not change application code. PR #1640 remains the sole active V3/XRP integration path.

No merge is authorized yet:
- 62 review submissions remain COMMENTED, zero APPROVED.
- Main branch protection is reported as enabled, but detailed protection and required-review settings remain inaccessible (HTTP 403).
- Required status contexts are not exposed; the fallback ruleset is disabled.
- GitHub Pages has previously deployed automatically after a main push. Specific authorization for that public deployment side effect remains absent.

Do not bypass branch protection or merge until the current PR head has current checks, required approval/protection conditions are satisfied, and Pages publication authorization is established.

No source PRs were closed. Preserve unique research, prediction, topology and knowledge-graph work. No forecast was issued.


## Run 129D — macro and geopolitical regime update

### U.S. rates

The Federal Reserve's published target range is 3.75%–4.00% (last official change shown September 17, 2026). [Federal Reserve rate history](https://www.federalreserve.gov/FOMC/fundsrate.htm).

Two market-pricing sources disagree on the December 8–9 meeting:
- Fisclear, updated November 10 at 06:31 ET, reports 99% odds of a 25bp hike from CME 30-Day Fed Funds Futures. [Fisclear](https://fisclear.com/fed-watch).
- RateProbability's cached November 10 00:00 snapshot reports 84.8% odds using Kalshi prediction-market prices. [RateProbability](https://rateprobability.com/fed).

These are different instruments and update times. Do not average them. Both are market-implied prices, not a Fed forecast.

### Japan

The October 30 BOJ decision held the policy rate at 1.25% with an 8–1 vote; one member proposed 1.50%. The BOJ also increased planned annual ETF sales from ¥330B to ¥860B book value, with implementation from January 2027. OANDA reports a market-value equivalent near ¥2.46T annually. [OANDA BOJ review](https://www.oanda.jp/lab-education/market_news/boj-oct-2026-review/).

Reuters reported on November 10 that the BOJ estimated roughly ¥1T in additional annual proceeds from the accelerated sales. The amount remitted to government is not fixed and depends on year-end calculations and budget procedures; BOJ operations remain the central bank's legal responsibility. [Reuters](https://www.reuters.com/world/asia-pacific/boj-estimates-6-billion-annual-gain-from-faster-etf-sales-finance-minister-says-2026-11-10/).

This is an indirect global-liquidity/equity-supply factor, not an XRP flow.

### Iran / energy risk

November 10 reporting indicates Brent briefly fell below $90 (FT cited approximately $89.21 before recovering near $91.25; the Guardian cited approximately $89.66) after U.S. signals of reduced likelihood of renewed strikes on Iran. Both reports caution that no formal agreement exists and Strait of Hormuz shipping has not fully normalized. The FT reported a greater than 22% November decline in Brent; the Guardian highlighted that unresolved supply and inflation risks remain.

Sources: [Financial Times](https://www.ft.com/content/07bdb58c-4557-4def-b8cb-db9be304fd72), [The Guardian](https://www.theguardian.com/business/2026/nov/10/oil-prices-fall-donald-trump-iran-war-ftse-100-markets).

Potential channel: lower energy prices may ease headline inflation and risk premia; unresolved shipping disruption preserves a geopolitical tail risk. This is a macro regime feature candidate, not a direct XRP catalyst or directional signal.

### Scheduled U.S. inflation event

BLS scheduled October CPI and Real Earnings for November 10 at 08:30 ET / 13:30 UTC. At the Run129 12:00 UTC cutoff, the release was still in the future. No result was inferred. [BLS official schedule](https://www.bls.gov/schedule/2026/11_sched.htm).

The macro readings and source disagreements are recorded in the Run129 JSON under `macro.fed`, `macro.boj` and `macro.geopolitics`. Do not convert market-implied policy probabilities or oil headlines into an XRP forecast without synchronized time-series features and out-of-sample evidence.


## Run 129E — BOJ primary-source verification

The Japan macro section is now anchored to the Bank of Japan's own October 30 statement, not only secondary reporting.

- Policy Board set the uncollateralized overnight call rate around 1.25%, with an 8–1 vote.
- The dissenting member, Takata Hajime, proposed 1.50%; the proposal was defeated.
- ETF sales were unanimously increased from approximately ¥330B to ¥860B annual book value, about 0.1% of Tokyo Stock Exchange Prime trading value.
- The BOJ estimates the market-value equivalent at approximately ¥2.46T per year.
- The new pace begins January 2027; temporary adjustments or suspension are allowed within the annual pace in response to market conditions.
- J-REIT sales remain approximately ¥5B per year book value.

Primary source: [BOJ Statement on Monetary Policy, October 30, 2026](https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2026/k261030a.pdf).

The BOJ's November 10 Summary of Opinions was released at 08:50 JST. It shows differing views: some members see underlying inflation as generally consistent with the 2% target and support further increases, while others favor holding to assess cumulative effects. This is a compilation of individual views, not a new rate decision or consensus forecast. The BOJ also notes Middle East energy/raw-material prices as a downside to fiscal-2026 activity and AI-related global demand as a support.

Primary source: [BOJ Summary of Opinions, October 29–30 meeting](https://www.boj.or.jp/en/mopo/mpmsche_minu/opinion_2026/opi261030.pdf).

Reuters' November 10 report of approximately ¥1T additional annual proceeds remains a separate estimate; the amount ultimately remitted to government depends on year-end calculations and budget procedures. [Reuters](https://www.reuters.com/world/asia-pacific/boj-estimates-6-billion-annual-gain-from-faster-etf-sales-finance-minister-says-2026-11-10/).

This reinforces the distinction between central-bank asset sales, market-value supply, book-value accounting and fiscal remittances. None is an XRP flow.


## Run 129F — final integration-head verification

The exact current integration head immediately before this handoff refresh was `f8b0be54158191c279c14947d14299c5a58a3fa7`.

<badge>VERIFIED</badge>

- Full repository suite: **1,371 passed, zero failed, eight subtests passed**.
- Inclusive coverage: **59.58%**; required floor 53%.
- Core suite: **677 passed, eight subtests passed**.
- Wheel build and installed-wheel verification passed.
- Barrot V3, primary XRP mission and canonical package assets loaded from the installed wheel.
- Six dependency manifests passed; zero known vulnerabilities.
- Fail-closed gate passed; automatic merge remains disabled.

Exact-head evidence:
- Full CI [42814368237](https://github.com/Barrot-Agent/B-Agent/actions/runs/42814368237).
- Dependency audit [42814368174](https://github.com/Barrot-Agent/B-Agent/actions/runs/42814368174).
- Fail-closed gate [42814368064](https://github.com/Barrot-Agent/B-Agent/actions/runs/42814368064).

The Run129 implementation changes are therefore verified on `f8b0be`. This handoff-only update creates a documentation descendant; its own PR synchronization checks must be inspected before any merge. The current PR description was refreshed with the exact-head evidence and Run129 findings.

Current PR #1640 state at `f8b0be`: open, non-draft, GitHub reports mergeable, 953 commits ahead / zero behind, 260 changed files, 125,245 additions and 3,555 deletions. There are 62 COMMENTED review submissions, zero approvals, and 22 resolved-but-outdated inline threads.

Main remains `d4d43be3427375cf79d190e768976de062e20287`. Main is reported protected, but detailed required-review protection returns HTTP 403, visible required status contexts are empty and the fallback ruleset is disabled. GitHub Pages previously deployed after a main push; authorization for another automatic public publication is not established.

No merge or deployment was performed. No source PRs were closed. The XRP mission manifest and scheduled read-only collector remain on the integration branch, not main. Forecast status remains `NOT_ISSUED`.

## Run 130 — exact repository verification, live XRP structure and CPI event cutoff

**Captured:** 2026-11-10 13:19:48 UTC.  
**Mission:** XRP intelligence and measured prediction-engine mastery — priority 1. Preserve Barrot V3 as execution, orchestration, safety and verification foundation.  
**Main:** `d4d43be3427375cf79d190e768976de062e20287`.  
**Integration branch/head:** `integration/core-capabilities-mmi-structural-paper-20261104` / `a2f0c70535d00729beccb8b38d0dbad044c935ed`.  
**Existing PR:** [#1640](https://github.com/Barrot-Agent/B-Agent/pull/1640).  
**Structured evidence:** [Run130 JSON](research/xrp_intelligence/20261110T131948Z-run130-xrp-market-repo-integration-cpi-cutoff.json).

### Repository and exact-head verification

- Current main remains `d4d43be3427375cf79d190e768976de062e20287`; main tree has 1,404 entries / 1,299 files. Integration tree has 1,556 entries / 1,443 files.
- PR #1640 remains the sole active V3/XRP integration path: open, non-draft, mergeable/clean, 954 commits ahead and zero behind, 260 changed files, 125,273 additions and 3,555 deletions.
- Exact PR-head checks on `a2f0c70535d00729beccb8b38d0dbad044c935ed` all passed: full repository suite **1,371 passed, zero failed, eight subtests passed**; inclusive coverage **59.58%** against a 53% floor; wheel build/installation and packaged Barrot V3/XRP mission verification; six dependency manifests with zero known vulnerabilities; fail-closed gate passed with automatic merge disabled. CodeRabbit check was skipped.
- Exact evidence: [CI 42814888613](https://github.com/Barrot-Agent/B-Agent/actions/runs/42814888613), [dependency audit 42814888645](https://github.com/Barrot-Agent/B-Agent/actions/runs/42814888645), [fail-closed gate 42814888651](https://github.com/Barrot-Agent/B-Agent/actions/runs/42814888651).
- PR review state: 62 COMMENTED submissions, zero APPROVED, zero CHANGES_REQUESTED; all 22 inline threads resolved but outdated. No reviewer is currently requested.
- Main branch-protection endpoint returns HTTP 403. The only visible repository ruleset, “Fall Back” (10863829), is disabled. Effective required approval/check settings remain unverified.
- Prior GitHub Pages run [41799855489](https://github.com/Barrot-Agent/B-Agent/actions/runs/41799855489) deployed successfully after a main push. PR #1640 changes public web assets; specific authorization for the next automatic public publication is absent. **Merge remains blocked.**

### Main workflow state and failure diagnosis

- Main scheduled Pillars run [42820781370](https://github.com/Barrot-Agent/B-Agent/actions/runs/42820781370) failed at 13:01:40 UTC. Exact diagnostics: GitHub App ID/private key/installation ID missing; Databricks HTTP 403; Hugging Face Space `BUILD_ERROR`. Deploy-sync and system-prompt checks passed. The workflow remains fail-closed; no credentials were changed or bypassed.
- Main scheduled Cross Analysis run [42819316779](https://github.com/Barrot-Agent/B-Agent/actions/runs/42819316779) succeeded. Its current workflow is read-only (`contents:read`, checkout credentials disabled, artifact upload only).
- The integration XRP collector is designed as read-only (`actions:read`, `contents:read`, checkout credentials disabled) and writes only bounded GitHub Actions artifacts/cache. It is not on main, so no scheduled production ingestion has run. Artifacts/cache are not WORM or trusted timestamp anchoring.
- Workflow audit covered 43 changed workflow files. Legacy writers/emitters and Hugging Face/Databricks bundle deployment paths are quarantined or reduced to manual approval. Self-hosted Brain and A2A deployment require explicit deployment confirmation, separate secret-rotation confirmation and exact-main-SHA checks. Barrot Ops requires external-change confirmation and exact SHA before Databricks workspace import; no dispatch occurred. Paper trader is manual artifact-only and was not dispatched.

### Public web signal correction remains pending publication

Main still exposes the stale `web/latest_signal.json` timestamp 2026-10-29 13:23:33 UTC, sentiment 44, confidence 0, news score 88 and 11 headlines. Main `web/signal_accuracy.json` still displays 45.5% (772/1,697) from a variable-horizon scorer. Integration correctly publishes `NOT_ISSUED` and `NOT_EVALUATED`, preserving the old sentiment only as stale descriptive history. This safety correction is not on main because the merge/publication gate remains blocked.

### XRP spot, liquidity and derivatives — November 10, 2026

**Spot retrieval cutoff 13:19:48 UTC:** Kraken XRP/USD last $1.07712, bid $1.07718, ask $1.07719, 24-hour volume 24.112M XRP, VWAP $1.09356134, high/low $1.11573/$1.07367. Kraken did not supply a provider event timestamp. OKX XRP-USDT last 1.0784, bid 1.0782, ask 1.0783, provider event time 13:17:53.462 UTC, 24-hour volume 58.448M XRP. Kraken USDT/USD last 0.99874. Mechanically normalized OKX last is $1.077041, approximately 0.0073% below Kraken last; normalized mid difference is approximately −0.0273%. Quotes are asynchronous; this is not executable arbitrage.

The exact visible JSON response texts were SHA-256 hashed and recorded in the Run130 artifact. These are hashes of visible response text, **not** original HTTP transport bytes or headers.

**Spot L2:** Fuelmaps' 13:00 UTC six-venue snapshot showed XRP mid $1.0786; within 1%, $13.8M bids versus $9.2M asks (60.1% bid share); within 5%, $23.2M bids versus $13.0M asks (64.1%). Venues: Coinbase, OKX, Kraken, Bitstamp, Bitfinex and Gemini; Binance and Bitget excluded. These are displayed resting orders, cancellable and up to about 65 minutes old, not executed flow or guaranteed depth. [Fuelmaps](https://fuelmaps.io/order-book/).

**Derivatives:** Liqwall at 13:02 UTC reported $1.20B OI (−0.1% 24h), +0.0089%/8h average funding and $3.7M liquidations, of which $3.3M longs. TradRadar at 12:20 UTC (15-minute delay) reported $1.65B OI (−2.7% 24h), +0.0090%/8h funding and at least $3.96M liquidations, of which $3.32M longs; its long/short account ratio was 3.89 (79.6% long). Alpha Finance's older 08:15 UTC aggregate was $2.43B. These aggregates have overlapping but different venue coverage and windows; do not average. The common descriptive evidence is positive funding and long-heavy liquidation/deleveraging, not a directional signal. [Liqwall](https://liqwall.com/coins/xrp), [TradRadar](https://tradradar.io/markets/xrp), [Alpha](https://alphafinance.io/liquidation-heatmap/xrp/).

### ETF flow quality

For the November 9 session, CryptoETF reports a partial 3/5 funds and −$10.3M, missing XRPZ and GXRP. CryptoKeyhole reports 3/4 daily-tracked funds, −9,216,553 XRP (about −$10.1M): Bitwise −8,594,551 XRP, Canary −427,341 XRP and 21Shares −194,660 XRP; Franklin XRPZ remained missing for November 9. Alpha Finance reports −$10.4M across five displayed funds. CryptoETF's detailed table says 3/5 while a summary elsewhere says 5/5; Alpha's five-fund total conflicts with issuer-file gaps visible in other trackers. These aggregators overlap the same issuer files and are not independent confirmations. Holdings reductions are not necessarily cash redemptions or exchange sales. ETF flows remain excluded from model admission; do not zero-fill or average.

### XRPL governance and macro event cutoff

XRPL Dashboard at 13:05 UTC, validated ledger 108239693: 98 amendments enabled, nine in-flight, zero in the 14-day activation countdown; 35/35 validators heard and 29 yes votes required. SingleAssetVault 23/29, LendingProtocol 22/29, LendingProtocolV1_1 22/29, ConfidentialTransfer 21/29, DynamicMPT 16/29, fixXChainRewardRounding 10/29, Sponsor 10/29, XChainBridge 4/29, CryptoConditionsSuite 0/29. Native XRPL lending remains inactive because both SingleAssetVault and LendingProtocol are below threshold. The official rule requires more than 80% trusted-validator support for 14 consecutive days. The curated dashboard identifies DIA as its production oracle provider; the broader XRPLWin directory has wider scope and lists additional oracle objects/providers. Preserve that scope disagreement and verify publisher/freshness; an oracle object does not prove collateral consumption.

BLS October CPI and Real Earnings were scheduled for **13:30 UTC / 08:30 ET**. At the Run130 cutoff of 13:19:48 UTC, the October release was still future. The BLS page still displayed September CPI (+0.6% m/m headline, +0.3% m/m core, +3.7% y/y) and states the October release time. Fed Governor Christopher Waller said he would support at least a 25bp December hike even if October CPI cooled and said core CPI at 0.3% m/m or higher should prompt consideration of 50bp. Reuters reported approximately 85% futures-implied odds of a December hike; Barron's/LSEG reported 98% after Waller's remarks. These are different market-pricing snapshots; do not average. No October CPI result was inferred and no XRP direction was issued. [BLS](https://www.bls.gov/news.release/cpi.nr0.htm), [Reuters](https://www.reuters.com/business/feds-waller-plans-support-least-quarter-point-rate-hike-december-2026-11-10/).

### Prediction and coordination status

The integration branch contains 46 source definitions (42 hourly, two weekly CFTC, two excluded non-commercial XRPL nodes), read-only collection, SHA-256 receipt-chain logic, point-in-time SQLite feature-store prototype, four deterministic baselines, chronological walk-forward evaluation with purge/embargo, calibration/drift diagnostics and a fail-closed Ed25519-attested forecast ledger. Production readiness is not established: no successful main ingestion run, no independent WORM/timestamp authority, incomplete synchronized historical spot/L2/derivatives/flow/collateral coverage, no production evaluator key, no demonstrated out-of-sample lift or sufficient shadow outcomes.

Nine-platform status is unchanged: ChatGPT current-session GitHub access verified; Copilot comment-only review; Claude, Grok, Gemini, Codex, Hugging Face, Kaggle and Databricks lack verified persistent authenticated data flows. No external model received repository data.

**Forecast status: NOT_ISSUED.** No paper trade, real-money action or external-model transfer occurred.

### Backlog path-overlap audit

The 372 open PRs were enumerated (356 drafts, 16 non-drafts). Path comparisons against #1640: #1642 7/7 overlapping; #1643 670 files with 663 unique; #1644 8/8; #1645 1/1; #1646 1/1; #1647 6/6; #1648 1/1; #1649 and #1650 each 1/1 on the same legacy dependency file; #1653 seven files with six unique; #1614 57 files with 49 unique; #1611 eight files with two unique; #1317 6/6; #1318 2/2; #1320 5/5; #1254/#1255 each one legacy dependency path; #1269 nine files with eight unique; #1655 eight files with three unique; #1659 six files with four unique; #1641 three unique paths. Path overlap is not by itself semantic equivalence. Preserve #1643, #1653, #1614, #1611, #1269, #1655, #1659 and #1641 unique work. Keep overlap candidates open until a verified successor merge; close no PRs now.

### Merge decision and next action

PR #1640 is technically green and mergeable, but remains **BLOCKED** by zero independent approvals, inaccessible effective branch-protection details and unresolved authorization for automatic GitHub Pages publication. Do not merge or bypass protection. Next actions: resolve approval/protection/publication authorization; after the BLS release, capture the official October CPI vintage with exact release time; preserve the one integration PR; keep scheduled ingestion off main until authorized; establish WORM/timestamp anchoring and synchronized historical data; do not issue forecasts until out-of-sample and shadow gates pass.

No merge, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push or destructive worktree operation occurred.

## Run 130A — cbXRP collateral, Coinbase reserves and PNC/USDC payment rail

**Captured:** 2026-11-10 13:26:11 UTC. The preceding exact integration head `e6794a2e82ced10472ffb6f1f5c115d0673d6841` passed the full suite (1,371 passed, zero failed, eight subtests), 59.58% coverage, installed-wheel verification, six-manifest dependency audit with zero known vulnerabilities and the fail-closed gate. Exact evidence: [CI 42824076149](https://github.com/Barrot-Agent/B-Agent/actions/runs/42824076149), [dependency audit 42824076046](https://github.com/Barrot-Agent/B-Agent/actions/runs/42824076046), [fail-closed gate 42824076086](https://github.com/Barrot-Agent/B-Agent/actions/runs/42824076086). This research-only descendant still requires its own exact-head checks before any merge.

### Actual XRP-linked collateral usage

Coinbase's own cbXRP proof-of-reserves page states cbXRP is backed 1:1 by XRP held by Coinbase. The US-locale search snapshot displayed **152,372,342.33 XRP reserve** against **152,370,095.8 cbXRP supply**, an apparent excess of 2,246.53 XRP. A different earlier locale snapshot displayed 151,921,083.53 XRP reserve and 151,918,836.99 cbXRP supply. The page variants expose different refresh-time labels (2:04 AM, 5:09 AM, and 9:34 AM) without an explicit timezone in the rendered result. Preserve the balances and the time-label ambiguity; do not treat this as a third-party attestation or an exact UTC-aligned reserve series. [Coinbase proof of reserves](https://www.coinbase.com/cbxrp/proof-of-reserves).

MorphoWatch's detailed public on-chain market page, using Morpho API data, reports a Base **cbXRP/USDC** market snapshot at 11:01 UTC:

- 120.41M cbXRP collateral, valued at $129.9M.
- $55.58M USDC borrowed against it; 88.2% utilization of $62.98M supplied and $7.41M immediately available.
- 11,694 borrowers.
- Fixed 62.5% liquidation LTV and 12.68% liquidation bonus.
- Borrow APY 7.00% (30-day average 7.25%); supply APY 6.15% (30-day average 6.52%).
- ChainlinkOracleV2 price approximately 1.08 USDC.
- 1,466 liquidations in the preceding 30 days, with $6.23M debt repaid.
- The page models approximately $26.01M collateral at risk under a 20% cbXRP price decline. One of its largest borrowers had health 1.04 and a displayed 3.6% price drop to liquidation; that single borrower is not representative of all positions.

MorphoWatch's later Coinbase summary at 12:31 UTC reports $55.52M borrowed, $129.9M collateral and 6.98% borrow APY. The detailed and summary snapshots differ slightly; both vintages are preserved. MorphoWatch says the Coinbase app market attribution is inferred from public on-chain matching; Coinbase does not publish the exact markets. [Detailed market](https://morphowatch.com/markets/base/cbxrp-usdc-62-5/), [Coinbase/Morpho summary](https://morphowatch.com/coinbase/).

The 120.41M cbXRP collateral amount is approximately 79.0% of the Coinbase-displayed 152.37M cbXRP supply if the snapshots are comparable. This is a cross-source approximation only: the page timezones differ, the Morpho market is one of several, and the figure is not admitted as a point-in-time feature until vintages are synchronized.

**Interpretation:** this is material XRP-linked collateral/credit use on Base, not native XRPL lending. It can support a holder-liquidity hypothesis (borrow USDC without immediate XRP sale) and a liquidation-supply counter-hypothesis (leveraged cbXRP collateral can be liquidated during a decline). It does not prove net XRP spot purchases or net XRP demand. Keep cbXRP/USDC Base lending separate from XRPL SingleAssetVault/LendingProtocol, which remain below activation thresholds (23/29 and 22/29 at the latest snapshot).

### PNC, Coinbase and Circle stablecoin rail

PNC's November 9 primary announcement and Coinbase's matching announcement establish a limited pilot for eligible PNC Corporate & Institutional Banking clients to receive **USDC on Ethereum** through Coinbase Payment APIs. Incoming USDC is automatically converted 1:1 into U.S. dollars and deposited into a designated PNC account. Reuters identifies the asset as Circle's USDC. PNC did not disclose payment volume or client count. [PNC primary release](https://pnc.mediaroom.com/2026-11-09-PNC-Bank-Launches-Incoming-Stablecoin-Payments-for-Corporate-and-Institutional-Banking-Clients), [Coinbase announcement](https://www.coinbase.com/blog/coinbase-secures-mica-license-from-luxembourg), [Reuters](https://www.reuters.com/legal/transactional/pnc-offer-stablecoin-payments-clients-coinbase-partnership-2026-11-09/).

This is a live PNC/Coinbase/Circle-issued-USDC institutional dollar rail, but it is **not** an XRP/XRPL route and no Ripple/XRP bridge leg is disclosed. It is a competing or adjacent payment path, not evidence that XRP use is displaced in other corridors.

### Model treatment

- Admit verified cbXRP collateral balances, USDC debt, utilization, oracle, LLTV, liquidation history and timestamped position-health data only as separate Base collateral features with provenance and vintage.
- Do not count cbXRP reserve balances as free float or proprietary Coinbase holdings.
- Do not count PNC USDC receipts as XRP demand.
- Preserve both the non-sale borrowing hypothesis and the liquidation-supply counter-hypothesis.
- No directional forecast issued; no paper trade or real-money action.

Structured evidence: [Run130A JSON](research/xrp_intelligence/20261110T132611Z-run130a-cbxrp-morpho-pnc-institutional-update.json).

## Run 130B — October CPI release, missing annual base and immediate market-data quality

**Captured:** 2026-11-10 13:31:08 UTC. The preceding code/evidence head `45895ec7494941cc5f09a7452a416e1e2ca7ca81` passed exact-head verification: **1,371 tests passed, zero failed, eight subtests passed in 65.23 seconds; inclusive coverage 59.58%; wheel build/install passed; six dependency manifests passed with zero known vulnerabilities; fail-closed gate passed.** Evidence: [full CI 42824636726](https://github.com/Barrot-Agent/B-Agent/actions/runs/42824636726), [dependency audit 42824636655](https://github.com/Barrot-Agent/B-Agent/actions/runs/42824636655), [fail-closed gate 42824636707](https://github.com/Barrot-Agent/B-Agent/actions/runs/42824636707). This following commit is documentation/evidence only; its own exact-head CI is pending.

### October 2026 CPI — first release

BLS published release **USDL-26-1685** at 08:30 ET / 13:30 UTC:

- Headline CPI: **+0.4% m/m seasonally adjusted**, down from +0.6% in September.
- Core CPI: **+0.3% m/m**, unchanged from September.
- Reuters pre-release consensus: +0.3% headline and +0.2% core. Both monthly prints were 0.1 percentage point hotter than consensus.
- Shelter +0.3%; food +0.5%; food at home +0.4%; food away +0.5%; energy +0.7%; gasoline +1.0%; used cars/trucks −1.2%.
- BLS explicitly states that it did not collect October 2025 survey data because of the lapse in appropriations and cannot publish 12-month changes for most October 2026 CPI series. The October headline/core YoY fields are therefore **NULL**, not zero and not an estimate. [BLS first release](https://www.bls.gov/news.release/cpi.nr0.htm), [BLS missing-data methodology](https://www.bls.gov/cpi/factsheets/approximating-missing-data.htm), [Reuters pre-release consensus](https://www.reuters.com/business/us-consumer-prices-expected-have-risen-slower-pace-october-2026-11-10/).

This matters for Barrot's point-in-time macro features: store first-release headline/core m/m with release ID and timestamp; store headline/core YoY as missing with the explicit base-period reason. Never carry September's 3.7% headline / 2.6% core YoY forward as October results, and never synthesize a 12-month comparison.

### Fed interpretation and market pricing

Waller had said core CPI of 0.3% m/m or higher should prompt consideration of a 50bp December move. The actual core print meets that stated threshold. It remains one governor's conditional view, not an FOMC decision. The latest Kalshi page showed 88% for a 25bp hike, 5% for 50bp, 9% hold and 3% cuts, but its displayed update was 06:34 ET, **before** the CPI release. Reuters' 85% futures and LSEG's 98% were also pre-release snapshots. No post-release repricing was independently verified at the capture time; preserve all instruments/timestamps and do not average them. [Reuters on Waller](https://www.reuters.com/business/feds-waller-plans-support-least-quarter-point-rate-hike-december-2026-11-10/), [Kalshi](https://kalshi.com/fed-rate-odds).

### XRP market reaction — insufficient synchronized data

Kraken's pre-release retrieval at 13:19:48 UTC showed last $1.07712, bid $1.07718 and ask $1.07719. Its post-release retrieval at 13:30:26 UTC showed last $1.07765, bid $1.07810 and ask $1.07811. The indicative last-price difference is only +0.049%, but Kraken supplies no provider event timestamp and the pre-print retrieval was over ten minutes before release. OKX still returned its 13:17:53.462 UTC ticker at the post-release check, making it stale. There is no synchronized post-release multi-venue event window. **Do not call this an XRP CPI reaction or use it as an event-study return.** [Kraken ticker](https://api.kraken.com/0/public/Ticker?pair=XRPUSD), [OKX ticker](https://www.okx.com/api/v5/market/ticker?instId=XRP-USDT).

Structured evidence: [Run130B CPI event JSON](research/xrp_intelligence/20261110T133108Z-run130b-october-cpi-release-and-market-reaction.json).

No directional forecast was issued. No paper trade or real-money action occurred.


---

## Run 130C — October 2026 Real Earnings release and repository integration audit

**Captured:** 2026-11-10 13:34:04 UTC. **Current main:** `d4d43be3427375cf79d190e768976de062e20287`. **Integration branch before this append:** `78e6eaf4a5191798fcb3010d8fe9332e3a8c5b6c`.

### BLS Real Earnings — USDL-26-1686

BLS published the October 2026 Real Earnings release at 08:30 ET / 13:30 UTC:

- All-employee real average hourly earnings were unchanged month over month, seasonally adjusted.
- Nominal average hourly earnings rose 0.4%, matching the 0.4% CPI-U increase.
- All-employee real average weekly earnings were unchanged; the average workweek was unchanged.
- Production/nonsupervisory real average hourly earnings rose 0.1% because nominal hourly earnings rose 0.4% while CPI-W rose 0.3%.
- Production/nonsupervisory real weekly earnings fell 0.3%, matching a 0.3% decline in the average workweek.
- Year-over-year real-earnings comparisons are unavailable because October 2025 CPI data were not collected during the lapse in appropriations.

Primary source: [BLS Real Earnings release USDL-26-1686](https://www.bls.gov/news.release/realer.nr0.htm). Related primary source: [BLS October CPI release USDL-26-1685](https://www.bls.gov/news.release/cpi.nr0.htm).

The CPI and Real Earnings releases are separate BLS publications but share the same publisher; they are not independent-publisher corroboration. The official page was inspected, but raw HTTP wire bytes and a raw-source digest were not captured. The artifact records a SHA-256 digest of its normalized evidence payload only; it does not misrepresent that digest as a raw BLS response hash.

### Interpretation and model treatment

The Real Earnings release shows no broad all-employee real hourly or weekly wage gain in October. It does not neutralize the CPI surprise: headline and core monthly CPI were each 0.1 percentage point above the Reuters preview consensus. October headline/core year-over-year values remain null because the comparison base is unavailable.

The artifact preserves competing interpretations: sticky core may reinforce restrictive-policy expectations; slower headline inflation may temper that interpretation; and there may be no stable XRP response without synchronized multi-asset market repricing. These are hypotheses, not causal findings.

The release is **NOT_ADMITTED** to the model feature store until a point-in-time record has a verified raw-source receipt and independent timestamp anchor. YoY values remain null. No directional forecast is issued.

Structured evidence: [Run130C JSON](research/xrp_intelligence/20261110T133404Z-run130c-real-earnings-release.json).

### Repository reality and integration gate

A fresh recursive Git tree was retrieved: main contains 1,404 entries; the current integration branch contains 1,559 entries. All **372 open PRs** were enumerated across four pages: **356 draft, 16 non-draft**. No new branch or PR was created.

- **PR #1640** remains the sole active core integration branch for MMI, XRP point-in-time ingestion, prediction safeguards and V3 foundation. Its head before this append was `78e6eaf4a5191798fcb3010d8fe9332e3a8c5b6c`, 957 commits ahead and zero behind current main, with 263 changed files. The 13:31:08 UTC Run130B commit changed only the canonical handoff and its CPI evidence JSON.
- Exact-head checks on `78e6eaf`: core CI passed; dependency audit passed across six manifests; fail-closed gate passed. The full repository suite, inclusive coverage and installed-wheel verification were still **IN_PROGRESS** at the 13:34:04 UTC observation. Runs: [CI 42825344461](https://github.com/Barrot-Agent/B-Agent/actions/runs/42825344461), [dependency audit 42825344586](https://github.com/Barrot-Agent/B-Agent/actions/runs/42825344586), [fail-closed gate 42825344668](https://github.com/Barrot-Agent/B-Agent/actions/runs/42825344668). The full-suite result from the preceding head is not substituted for this head.
- PR #1640 has 62 review submissions, all COMMENTED and zero APPROVED. The live review-thread API reports 22 threads and **zero resolved**; this corrects the stale prior handoff statement that those threads were resolved.
- **PR #1643** remains unique institutional/market/capital research, not a duplicate. Its head is `238f3ff4a69420882c77d225626a352ba19a412c`, based on old main `9100dbacb5f9f1b973b053a65ef1e91e96b64f72`; it is 906 commits ahead and one behind current main, 670 changed paths, 7 shared paths with #1640 and 663 paths unique to #1643. GitHub reports it dirty/unmergeable. It has 10 COMMENTED reviews, zero APPROVED, and 19 review threads with zero resolved. Do not merge it directly; preserve its unique research for a later current-main successor after the core integration is resolved.
- Visible repository ruleset inventory contains only the fallback ruleset “Fall Back”, with enforcement disabled. The branch-protection endpoint returns HTTP 403, so effective required reviewers/status contexts remain unverified. GitHub Pages settings are also inaccessible through the available read path; a previous main update triggered publication. Do not merge while approvals, effective protection and the public publication side effect remain unresolved.

**Backlog classification:** #1640 = active integration / blocked on current-head full-suite and governance gates; #1643 = unique research / stale-diverged / unmergeable; #1642 = unique prediction work pending path-level reconciliation; #1653, #1655 and #1659 = unique/unreviewed work to preserve; #1644–#1650 = dependency/path-overlap candidates requiring exact diff review, not bulk closure; historical safety/research PRs remain preserved until a verified successor lands. No PRs were closed.

**Next concrete action:** wait for exact-head full CI 42825344461 to complete, inspect the full-suite and installed-wheel results, then reconcile only actual failures on the existing #1640 branch. Do not create another integration PR. After #1640 is merge-ready and its governance/publication blockers are resolved, rebase the integration plan by carrying #1643's 663 unique paths into one successor on the then-current main and reconcile all seven shared paths.

**Forecast status: NOT_ISSUED.** No merge, deployment, paper-trading mutation, real-money transaction, external model transfer, secret rotation, Space restart, Kaggle submission, Databricks write, force-push or destructive worktree operation occurred.

## Run 130D — Coinbase primary collateral confirmation and live review-state correction

**Captured:** 2026-11-10 13:36:43 UTC. The preceding code/evidence head `78e6eaf4a5191798fcb3010d8fe9332e3a8c5b6c` completed exact-head verification: **1,371 passed, zero failed, eight subtests in 62.12 seconds; inclusive coverage 59.58%; installed wheel verification passed; six dependency manifests passed with zero known vulnerabilities; fail-closed gate passed.** Evidence: [CI 42825344461](https://github.com/Barrot-Agent/B-Agent/actions/runs/42825344461), [dependency audit 42825344586](https://github.com/Barrot-Agent/B-Agent/actions/runs/42825344586), [fail-closed gate 42825344668](https://github.com/Barrot-Agent/B-Agent/actions/runs/42825344668). Current branch head before this addendum is `e14c2f4dfc50259c1505efb2e69595cb294b47d6`; its full CI and dependency audit are still running ([CI 42825936890](https://github.com/Barrot-Agent/B-Agent/actions/runs/42825936890), [dependency audit 42825936511](https://github.com/Barrot-Agent/B-Agent/actions/runs/42825936511)); its fail-closed gate passed ([42825936530](https://github.com/Barrot-Agent/B-Agent/actions/runs/42825936530)).

### Coinbase confirms XRP-backed Morpho loans

Coinbase's own help pages now directly confirm that XRP is eligible collateral for USDC crypto-backed loans through Morpho on Base. Its backup collateral page maps XRP to **cbXRP** on Base at contract `0xcb585250f852c6c6bf90434ab21a00f02833a4af`. Coinbase's September 29, 2026 product update states a maximum of up to $100,000 USDC against XRP, subject to account/product limits. Coinbase states that collateral is locked on Morpho and marked locked/not tradeable while the loan is active; it remains in the displayed total balance while the debt is not netted from that balance. [Coinbase loan intro](https://help.coinbase.com/en/coinbase/trading-and-funding/loan/loan-intro), [Coinbase XRP/cbXRP Base mapping](https://help.coinbase.com/en/coinbase/trading-and-funding/loan/loan-backup), [Coinbase collateral rules](https://help.coinbase.com/en/coinbase/trading-and-funding/loan/collateral), [Coinbase product update](https://www.coinbase.com/en-pt/blog/now-get-a-usdc-loan-without-selling-your-crypto).

### Correct liquidation-threshold interpretation

Coinbase says Morpho LLTV is fixed per market and varies by collateral asset. Its help material includes example thresholds at 86%, 77% and 62.5%. The XRP/cbXRP market matched by MorphoWatch reports **62.5% LLTV and 12.68% liquidation bonus**. The generic 4.38% Coinbase help text corresponds to an 86% LLTV example; it is not the XRP market's threshold/bonus. Morpho's official docs define liquidation at LTV ≥ the market's immutable LLTV (health factor ≤1), and the liquidator receives collateral plus the market-specific bonus. Do not apply the generic 86%/4.38% example to XRP. [Coinbase loan health](https://help.coinbase.com/en/coinbase/trading-and-funding/loan/loan-health), [Morpho LTV/LLTV](https://docs.morpho.org/developers/borrow/concepts/ltv/), [Morpho liquidation](https://docs.morpho.org/developers/borrow/concepts/liquidation/), [MorphoWatch LLTV/bonus formula](https://morphowatch.com/learn/morpho-lltv-and-liquidations/).

MorphoWatch's latest captured Coinbase summary at 12:31 UTC reports $55.52M USDC borrowed against $129.9M cbXRP collateral, 6.98% borrow APY and 7.25% 30-day average. Its detailed 11:01 UTC market snapshot reports 120.41M cbXRP collateral, $55.58M debt, 88.2% utilization, $7.41M available, 1,466 liquidations in 30 days and $6.23M debt repaid. It models $26.01M collateral at risk in a 20% cbXRP decline scenario; this is not a forecast of actual liquidations. MorphoWatch explicitly says Coinbase does not publish the exact market ID; its attribution is matched from public on-chain data and Morpho API. Coinbase's primary docs corroborate the product, asset and network path, but not the exact market ID. [MorphoWatch summary](https://morphowatch.com/coinbase/), [detailed market](https://morphowatch.com/markets/base/cbxrp-usdc-62-5/).

This is actual XRP-linked collateral use on Base, not native XRPL lending. Borrowing may let some holders obtain USDC without immediately selling XRP; the counter-hypothesis is liquidation-driven collateral supply during a decline. It is not proof of new XRP purchases or net spot demand. The approximate 79% cbXRP-supply share derived from one Morpho market and Coinbase's reserve page is not synchronized and is not model-admitted.

### Corrections to the prior handoff's live PR state

The live GitHub review-thread API for PR #1640 reports **22 total, 22 resolved, zero unresolved, all 22 outdated**. Run130C's statement that zero threads were resolved was incorrect; this is corrected here. Review submissions remain 62 COMMENTED and zero APPROVED.

PR #1642 has seven changed paths and all seven overlap #1640, with zero unique paths. It is a duplicate candidate, not unique prediction work; keep it open until a successor is merged and verified on main. PR #1643 remains unique research: 670 changed paths, seven shared with #1640 and 663 unique; preserve it rather than bulk-closing. Its stale/dirty branch is not mergeable directly.

PR #1640 remains open and technically mergeable, but blocked by no independent approval, inaccessible effective branch-protection details (HTTP 403), disabled visible fallback ruleset and unresolved GitHub Pages automatic-publication authorization. No merge or source-PR closure occurred.

### Model treatment

Admit only timestamped cbXRP collateral, USDC debt, utilization, oracle, LLTV, liquidation incentive and position-health observations with their Base network, Morpho market ID, source vintage and attribution confidence. Keep reserve backing separate from free float and locked collateral separate from exchange balances. Preserve both the non-sale borrowing and liquidation-supply hypotheses. The BLS CPI/real-earnings missing YoY fields remain null for the unavailable October 2025 base.

**Forecast status: NOT_ISSUED.** No paper trade or real-money action occurred.

Structured evidence: [Run130D JSON](research/xrp_intelligence/20261110T133643Z-run130d-coinbase-xrp-collateral-and-review-state-correction.json).


---

## Run 130E — Coinbase XRP-backed credit and Morpho oracle reconciliation

**Captured:** 2026-11-10 13:39:06 UTC. **Current main:** `d4d43be3427375cf79d190e768976de062e20287`. **Integration head before this append:** `896e5a094bd3e8042e5d3f699c97e95d1ea99e0f`.

### Primary product confirmation

Coinbase's current help center explicitly lists XRP as eligible collateral for USDC loans powered by Morpho on Base. Its backup collateral mapping identifies cbXRP at `0xcb585250f852c6c6bf90434ab21a00f02833a4af`. Coinbase states collateral is locked on Morpho and marked not tradeable while the loan is active; it remains in displayed total balance while debt is not netted from that total. Coinbase's September 29, 2026 product update states up to $100,000 USDC may be borrowed against XRP, subject to account/product and regional limits. [Coinbase loan intro](https://help.coinbase.com/en/coinbase/trading-and-funding/loan/loan-intro), [cbXRP Base contract mapping](https://help.coinbase.com/en/coinbase/trading-and-funding/loan/loan-backup), [collateral treatment](https://help.coinbase.com/en/coinbase/trading-and-funding/loan/collateral), [XRP loan product update](https://www.coinbase.com/en-pt/blog/now-get-a-usdc-loan-without-selling-your-crypto).

### Exact Morpho market identity

The first-party Morpho app URL resolves the complete Base market ID:

`0xd4a903dc6d949519060c7707f9604fdc9772c046e05c2e3a8fce0bd7196e4109`

It identifies USDC/cbXRP, variable rate, 62.5% immutable LLTV, Chainlink oracle contract `0x031b2EFC8d70042Ac8d9f5c793c4149eC4b60fdE`, and Chainlink XRP/USD feed `0x9f0C1dD78C4CBdF5b9cf923a549A201EdC676D34`. The interface displays a 1-day heartbeat and 0.5% deviation threshold. [Morpho market](https://app.morpho.org/base/variable/0xd4a903dc6d949519060c7707f9604fdc9772c046e05c2e3a8fce0bd7196e4109/usdc-cbxrp).

Morpho's liquidation incentive formula is `min(1.15, 1 / (0.3 * LLTV + 0.7))`. At 62.5% LLTV it implies a 12.676% bonus, consistent with the displayed 12.67–12.68%. At 86% LLTV it implies 4.38%; Coinbase's generic 4.38% example must not be applied to the XRP 62.5% market. [Morpho LTV/LLTV](https://docs.morpho.org/developers/borrow/concepts/ltv/), [Morpho liquidation](https://docs.morpho.org/developers/borrow/concepts/liquidation/), [formula table](https://morphowatch.com/learn/morpho-lltv-and-liquidations/).

### Market observations and disagreements

MorphoWatch's 13:21 UTC snapshot reports $62.94M USDC supplied, $55.52M borrowed, 88.2% utilization, $7.42M immediately available, $7.73M including additional vault liquidity, 120.45M cbXRP collateral valued at $129.9M, 11,694 open borrowers, 7.00% borrow APY and 6.15% supply APY. It reports 1,479 liquidations and $6.27M debt repaid in 30 days. Its 20% cbXRP decline scenario models $26.81M collateral at risk; this is not an expected loss. The largest listed borrower has health factor 1.03 and a displayed 3.0% drop to liquidation. [MorphoWatch market snapshot](https://morphowatch.com/markets/base/cbxrp-usdc-62-5/).

The Morpho app separately displays $55.57M outstanding loans, $23.54M total liquidity, 88.22% utilization, 0.00 USDC realized/unrealized bad debt, and top-three supplier allocations totaling about $44.41M. These are not identical definitions or capture times. The $23.54M “total liquidity” must not be substituted for MorphoWatch's $7.42M immediately available market liquidity. The app's $219.01M “value secured” label appears in oracle attributes; its scope is unresolved and it is not treated as this market's collateral.

The Morpho app also displays a Chainlink feed latest price of $1.09782 without a feed round timestamp, while the market oracle is $1.08 and the asset page is $1.0783. The feed heartbeat/deviation metadata does not prove the feed is stale. This comparison is **QUARANTINED** until the Chainlink round ID, answer, `updatedAt`, decimals and Morpho oracle decoding are captured at the same Base block.

### XRP value-capture interpretation

This is verified XRP-linked collateral utility on Base, not native XRPL lending. Outstanding USDC borrowing is not proof of XRP purchases or net capital entering XRP. Locked cbXRP is not freely tradeable Coinbase inventory. The non-sale-liquidity hypothesis and liquidation-supply hypothesis remain in parallel; liquidator disposition after seizure is unknown. Vault allocations indicate curator concentration, not ultimate depositor concentration.

The market balances, borrower health, liquidation counts and oracle comparisons are **NOT_ADMITTED** to the point-in-time model until block-level receipts, exact oracle rounds and consistent liquidity definitions are obtained. The Morpho app and MorphoWatch share underlying Morpho/on-chain data and are not independent publisher corroboration.

Structured evidence: [Run130E JSON](research/xrp_intelligence/20261110T132100Z-run130e-cbxrp-morpho-market-and-oracle-reconciliation.json). Regression tests: `tests/test_xrp_run130_macro_and_collateral_integrity.py`.

### Exact-head verification before this append

PR #1640 head `896e5a094bd3e8042e5d3f699c97e95d1ea99e0f` passed the full repository suite: **1,371 passed, zero failed, eight subtests, 55.75 seconds; inclusive coverage 59.58%; wheel built and installed, packaged Barrot V3/XRP mission resources verified**. Six-manifest dependency audit passed with zero known vulnerabilities; fail-closed gate passed with automatic merging disabled. Runs: [CI 42826220540](https://github.com/Barrot-Agent/B-Agent/actions/runs/42826220540), [dependency audit 42826219853](https://github.com/Barrot-Agent/B-Agent/actions/runs/42826219853), [fail-closed gate 42826219887](https://github.com/Barrot-Agent/B-Agent/actions/runs/42826219887). The wheel build still emits non-failing setuptools package-discovery and deprecated-license warnings; GitHub Actions cache is read-only after budget exhaustion.

**Next concrete action:** run the new macro/collateral regression tests and the full repository suite on the resulting exact head. Then retrieve Base block-level Morpho market state and the Chainlink feed round at a common block; do not admit the provider summaries or issue a directional forecast before that reconciliation.

**Forecast status: NOT_ISSUED.** No new branch or PR, merge, deployment, paper-trading mutation, real-money transaction, force-push, secret change, external model transfer or destructive worktree operation occurred.


---

## Run 130F — Evidence-hash correction and primary SBIC identity resolution

**Captured:** 2026-11-10 13:45:56 UTC. **Main:** `d4d43be3427375cf79d190e768976de062e20287`. **Integration head before this correction:** `ff16dea174fbe07ba3fa36f57c58bb7bf43f16b0`.

### Full-suite failure isolated to two new normalized digests

Exact-head CI on `ff16dea174fbe07ba3fa36f57c58bb7bf43f16b0` completed with **1,374 passed, 2 failed, 8 subtests** in 65.01 seconds. Both failures were the normalized SHA-256 checks for Run130C and Run130E; the core suite passed. Inclusive coverage was 59.58% and the 53% threshold was met. The failure was a serialization-integrity defect: the original digests were calculated from pre-serialization Python objects, while the committed JSON normalized numeric tokens. CI exposed the exact mismatches.

The original evidence files are preserved unchanged. Run130F adds an append-only correction receipt:
- Run130C original: `b7e43b7571476ac659a4266aff7f225ed089a4990d17dd92ce119481ebc9eaf2`; recomputed over committed JSON: `cba8af99983166b3df4816d38965e1da9b1ecf0660a13f3bd2ab3558c9ca1bb6`.
- Run130E original: `fa396c143ff900a732278fa44ff99efeb21f379a73b671dce028f53fa9a081b7`; recomputed over committed JSON: `35289f68f656fce28d40538d5ef88f328aca00f90670bbcf0a35cd1a0674bfa4`.

The regression suite now recomputes both digests from the committed files and validates the correction receipt. No original file is overwritten.

### Japan SBIC identity — primary-source resolution

- **SBIC East Japan:** Tokyo Small and Medium Business Investment & Consultation Co., Ltd. Its official profile identifies the legal name, corporate number, 1963 establishment, 18-prefecture shareholder categories and the Nagoya/Osaka companies as sister companies. [Official profile](https://www.sbic.co.jp/company/profile/).
- **SBIC Central Japan:** Nagoya Small and Medium Business Investment & Consultation Co., Ltd. Its official profile identifies its separate legal name, 1963 establishment, capital and five-prefecture territory. [Official profile](https://www.sbic-cj.co.jp/company/about/).
- **SBIC West Japan:** Osaka Small and Medium Business Investment & Consultation Co., Ltd. Its official profile identifies its separate legal name, 1963 establishment, 24-prefecture territory and statutory policy-institution status. [Official profile](https://www.sbic-wj.co.jp/profiles/profile/).

These are three distinct regional Japanese Small and Medium Business Investment & Consultation companies, described by their official sites as sister companies. They are not SBI Holdings. SBIC East's public profile lists shareholder categories, not a complete register; this research does not claim to exclude every possible minority SBI Group holding.

The exact **SBIC + ChatGPT** reference is explained by an official SBIC East seminar on March 5, 2026: “Generative AI (ChatGPT): Present and Future,” organized by Tokyo SBIC, co-hosted by Hamamatsu Iwata Shinkin, and presented by Microsoft Japan executive officer/evangelist Satoshi Nishiwaki. The event description includes ChatGPT demonstrations. This is a public educational event, not evidence of an OpenAI partnership, integration or XRP relationship. [Official event page](https://www.sbic.co.jp/seminar/20260305js/).

Structured records: [Run130F hash corrections](research/xrp_intelligence/20261110T134556Z-run130f-normalized-hash-corrections.json) and [Run130F SBIC primary identity](research/xrp_intelligence/20261110T134556Z-run130f-japan-sbic-primary-identity-chatgpt-seminar.json).

### Repository and merge state

PR #1640 remains the sole active core integration branch. Its 22 review threads are resolved, but all 62 submitted reviews are COMMENTED and none is APPROVED. The exact-head full suite and dependency audit must be rerun after this correction. PR #1643 remains unique institutional/market research: 906 commits ahead, one behind main, 670 changed paths, 7 overlaps and 663 unique paths. No duplicate or unique PR was closed.

The exact-head run on `ff16dea` had core CI success, six-manifest dependency audit success and fail-closed gate success, but full-suite failure described above. Do not carry forward the earlier 1,371-test pass as evidence for this head.

**Next concrete action:** verify the Run130F commit SHA, then inspect exact-head core CI, full repository suite, dependency/security audit and fail-closed gate. If the full suite passes, continue the existing #1640 integration review. Branch-protection settings and Pages publication controls remain inaccessible; no merge until required approvals/checks and deployment side effects are resolved.

**Forecast status: NOT_ISSUED.** No new branch or PR, merge, deployment, paper-trading mutation, real-money transaction, force-push, secret change, external model transfer or destructive worktree operation occurred.


---

## Run 130G — SBIC normalized-evidence digest correction

**Captured:** 2026-11-10 13:52:38 UTC. **Main:** `d4d43be3427375cf79d190e768976de062e20287`. **Integration head before correction:** `2bfb34bd0c49b5c78172193793ba1ed843a64880`.

The exact-head full-suite run on `2bfb34bd0c49b5c78172193793ba1ed843a64880` completed with **1,379 passed, 1 failed, 8 subtests** in 51.02 seconds; inclusive coverage remained 59.58% and the 53% threshold was met. The sole failure was the Run130F SBIC artifact's normalized digest check. All other new macro, collateral, identity and correction tests passed.

The committed SBIC JSON text differed from the Python draft used to compute its stored digest: the draft contained an extra “legal entities” in the `not_sbi_holdings` sentence. The CI-computed digest over the committed artifact is `7a6bd33043ca9a3f3618051b7e496d19b29c132e658f635162e47cad9eb510db`, not the earlier recorded `997029646b9f34eccc2707d4b3eb781ca3c8c8f0b715b70ad37fb5a58631b4ee`.

Run130G adds a separate append-only correction receipt referencing the original Git blob and both digests. The original SBIC artifact is not overwritten. The regression test now validates the correction against the committed JSON content rather than falsely asserting the original digest.

Exact-head run evidence before this correction:
- Core CI passed.
- Six-manifest dependency audit passed.
- Fail-closed gate passed, with merging disabled.
- Full repository suite failed only on the SBIC digest test above.
- The wheel/package verification step did not execute because the full-suite step failed.

Runs: [CI 42827946400](https://github.com/Barrot-Agent/B-Agent/actions/runs/42827946400), [dependency audit 42827946311](https://github.com/Barrot-Agent/B-Agent/actions/runs/42827946311), [fail-closed gate 42827946255](https://github.com/Barrot-Agent/B-Agent/actions/runs/42827946255).

**Next concrete action:** verify the Run130G remote commit SHA and exact-head CI, full repository suite, six-manifest dependency audit and fail-closed gate. Do not merge until those pass and the previously recorded independent-approval, branch-protection and Pages-publication blockers are resolved.

**Forecast status: NOT_ISSUED.** No original artifact was overwritten, no new branch or PR was created, and no merge, deployment, paper-trading mutation, real-money transaction, force-push or destructive worktree operation occurred.


---

## Run 131 — CPI surprise, synchronized market snapshot, CFTC XRP positions and integration verification

**Captured:** 2026-11-10T13:55:30Z. **Main:** `d4d43be3427375cf79d190e768976de062e20287`. **Integration head before this Run131 evidence commit:** `12d9a32201199738a27030b0f6873a16fbce6597`. **Existing integration PR:** [#1640](https://github.com/Barrot-Agent/B-Agent/pull/1640).

### Repository integration and exact-head verification

The current main tree contains **1,299 files** (1,404 recursive entries); the integration tree at the verified parent head contains **1,453 files** (1,566 entries). The integration branch is **962 commits ahead and zero behind main**, with **270 changed files, 127,316 additions and 3,555 deletions**. The open PR inventory contains **372 PRs: 356 drafts and 16 non-drafts**.

PR #1640 is open, non-draft and reported mergeable, but its merge state is unstable. It remains the sole active V3/XRP integration path.

Exact-head verification on `12d9a32201199738a27030b0f6873a16fbce6597` completed:
- Full repository suite: **1,380 passed, zero failed, eight subtests passed**.
- Inclusive package coverage: **59.58%**, above the 53% floor.
- Core suite passed.
- Wheel build and installed-wheel verification passed; the installed wheel loads Barrot V3, the XRP mission and canonical data assets.
- Six-manifest dependency audit passed with zero known vulnerabilities.
- Fail-closed merge gate passed; automatic merging remains disabled.
- CodeRabbit check was skipped.

Evidence:
- [Full repository suite — 42828685337](https://github.com/Barrot-Agent/B-Agent/actions/runs/42828685337)
- [Dependency audit — 42828685291](https://github.com/Barrot-Agent/B-Agent/actions/runs/42828685291)
- [Fail-closed gate — 42828685280](https://github.com/Barrot-Agent/B-Agent/actions/runs/42828685280)

The immediately preceding head `2bfb34bd0c49b5c78172193793ba1ed843a64880` had 1,379 passes and one failure in the Run130F SBIC normalized-evidence digest test. Commit `12d9a32201199738a27030b0f6873a16fbce6597` corrected the test against the committed JSON; the complete suite then passed. This Run131 commit adds research and handoff evidence only. Its own exact-head CI must finish before any merge decision.

Non-failing warnings remain: deprecated setuptools license metadata, package-discovery warnings for `barrot_agent.data.missions` and `data.research`, and an exhausted GitHub Actions cache budget. The cache is read-only; wheel verification still passed.

### Main workflow blockers

Main's latest Cross Analysis workflow passed: [42828392035](https://github.com/Barrot-Agent/B-Agent/actions/runs/42828392035).

The main Pillars Consistency Check failed: [42820781370](https://github.com/Barrot-Agent/B-Agent/actions/runs/42820781370). The log explicitly reports missing `GITHUB_APP_ID`, `GITHUB_APP_PRIVATE_KEY` and `GITHUB_INSTALLATION_ID`; Databricks HTTP 403; and Hugging Face Space `BUILD_ERROR`. Its `deploy_sync` and `system_prompt_fiction` checks passed. No credentials were fabricated, rotated or bypassed. This remains blocked pending valid provider access.

### Latest XRP spot and liquidity observations

**Exchange ticker observations.** Kraken's public XRP/USD response showed last **$1.06706**, bid **$1.06656**, ask **$1.06657**, 24-hour volume **27.459M XRP**, VWAP **$1.08912**, high **$1.11573**, low **$1.04750** and open **$1.09748**. Kraken supplied no provider event timestamp.

OKX's XRP-USDT ticker supplied provider timestamp **2026-11-10 13:48:36.536 UTC** and showed last **1.0730 USDT**, bid **1.0729**, ask **1.0730**, 24-hour volume **67.947M XRP**, high **1.1167**, low **1.0486** and open **1.0946**. Kraken's USDT/USD last was **0.99881**. Mechanical normalization gives OKX **$1.07172**, about **0.437% above** Kraken's last. This is an asynchronous cross-venue discrepancy, not an executable arbitrage: fees, slippage, quote-currency basis, transfer latency and exact synchronized book state are not established.

Tool-returned JSON response-text SHA-256 receipts:
- Kraken XRP/USD: `3a257300f3eb72a5ddf24837febbfb193a0a3425087bbbb1b1d93ba20a165bc6`.
- OKX XRP-USDT: `a912a9e448b7b5bf3763b9294f417ad1f7d0c77ec913d596f3c1727f47f0c956`.
- Kraken USDT/USD: `637fd86c2b82a8afb50a2e3ef3702eca9d9dd7aaa18bf0b229a79e49b303fb55`.

These hashes cover the exact JSON text returned by the web retrieval tool, not original HTTP wire bytes or transport headers. Kraken's missing provider timestamp remains null.

**Spot order-book depth.** Fuelmaps' spot-only multi-venue snapshot at **13:00 UTC** reported XRP mid **$1.0786**, six of six venues:
| Distance | Bids | Asks | Bid share |
|---|---:|---:|---:|
| ±0.5% | $8.2M | $6.7M | 54.9% |
| ±1% | $13.8M | $9.2M | 60.1% |
| ±2% | $18.4M | $10.8M | 63.0% |
| ±5% | $23.2M | $13.0M | 64.1% |
| ±10% | $34.3M | $15.0M | 69.6% (five venues) |

The six covered venues are Coinbase, OKX, Kraken, Bitstamp, Bitfinex and Gemini; Binance and Bitget are excluded. These are resting orders that can be cancelled, not executed volume or guaranteed fillable depth. The snapshot precedes the 13:30 UTC CPI release and is not synchronized with the 13:48 UTC ticker observations. [Fuelmaps source](https://fuelmaps.io/order-book/).

**Derivatives.** The latest retrieved aggregator snapshots disagree on venue coverage and open interest:
- Liqwall at 08:32 UTC: **$1.21B** OI, down 3.2% over 24h; $3.7M liquidations, $3.1M longs and $631K shorts; average funding +0.0027%/8h; 74.9% of Binance XRP accounts long. [Liqwall](https://liqwall.com/coins/xrp).
- TradRadar at 11:20 UTC: **$1.64B** OI across seven exchanges, down 2.36%; funding +0.0084%/8h; at least $3.82M liquidations, $3.15M longs and $667K shorts; account long/short ratio 3.94, 79.8% long. [TradRadar](https://tradradar.io/markets/xrp).
- OptimistFi at 11:55 UTC: **$1.40B** OI across 37 venues, funding 9.2% annualized. [OptimistFi](https://optimistfi.com/perps/markets/xrp?tab=liquidations).

The common description is long-heavy positioning and long-side deleveraging. The OI values are not averaged: venue coverage and aggregation differ, and these aggregators are not independent source groups. This is not a directional forecast.

### Macro event: October U.S. CPI released

BLS released October CPI at **08:30 Eastern / 13:30 UTC on November 10**:
- Headline CPI: **+0.4% month over month**, versus Reuters consensus **+0.3%**.
- Core CPI: **+0.3%**, versus Reuters consensus **+0.2%**.
- Food: +0.5%; energy: +0.7%; shelter: +0.3%.
- BLS could not publish October 2026 12-month changes for series whose October 2025 comparison data were not collected during the lapse in appropriations.

Primary source: [BLS October 2026 CPI release](https://www.bls.gov/news.release/cpi.nr0.htm). Consensus and early policy-market context: [Reuters, November 10](https://www.reuters.com/world/us/us-consumer-prices-rise-above-expectations-october-2026-11-10/). Reuters reported that a 25bp December Fed hike was fully priced early Tuesday; no post-release probability series was captured. The CPI surprise is a macro event feature, not an XRP directional signal.

### CFTC XRP derivatives positioning — November 3 report

The CFTC Traders in Financial Futures **options-and-futures combined** report, updated November 6, identifies:
| Contract | Multiplier | Open interest | XRP-equivalent OI | Change from Oct 27 |
|---|---:|---:|---:|---:|
| CME XRP | 50,000 XRP | 7,216 | 360.800M XRP | −850 contracts / −42.500M XRP |
| Coinbase Nano XRP | 500 XRP | 32,505 | 16.2525M XRP | −32,864 / −16.432M XRP |
| Coinbase Nano XRP Perp Style | 500 XRP | 38,392 | 19.196M XRP | −465 / −0.2325M XRP |
| **Gross underlying equivalent** | — | — | **396.2485M XRP** | **−59.1645M XRP equivalent** |

The large Nano XRP contract-count decline is notable, but the report is lagged and aggregates reportable categories. Underlying-equivalent open interest is not cash invested, net directional exposure, unique unhedged risk, collateral or spot demand. Do not interpret the total as capital flowing out of XRP. [CFTC combined report](https://www.cftc.gov/dea/options/financial_lof.htm).

### ETF and exchange-flow reconciliation

The November 9 CryptoKeyhole partial issuer-file set covers three of four daily-tracked funds:
- Bitwise: −8.595M XRP.
- Canary: −0.427M XRP.
- 21Shares TOXR: −0.195M XRP.
- Partial total: **−9.217M XRP**, approximately **−$10.1M**.
- Franklin XRPZ: pending; its latest file remained dated November 6.

TradRadar separately reports approximately **−$10.42M** for November 9. These are overlapping aggregators of issuer data, not independent confirmations. Cash versus in-kind redemptions, custody transfers and actual spot executions remain unresolved. ETF flow is **NOT_ADMITTED** to the prediction feature store.

The XRP Insights labeled-wallet snapshot at 08:00 UTC tracks **22.33B XRP across 701 wallets and 24 exchanges**. Same-wallet-set changes were −8.9M XRP over seven days and −150.9M over 30 days. Two newly tracked wallets added 512M XRP, making the naive total change +361.1M. Upbit is listed at 6.46B, Coinbase 5.80B (including 150.1M non-customer cbXRP reserve) and Binance 2.69B (including 327.4M Binance-Peg reserve). These balances include cold/custody wallets and wrapped-token reserves; they are not tradable float or proof of customer deposits/withdrawals.

### Institutional and collateral relationships

**Coinbase XRP-backed borrowing.** Coinbase's official help page lists XRP as eligible collateral for USDC crypto-backed loans enabled by Morpho on Base. Coinbase supplies the interface; the underlying lending protocol is Morpho. Availability is limited by geography and product/asset terms. This verifies an XRP-linked collateral utility path on Base, not native XRPL lending or net XRP purchases. [Coinbase official help](https://help.coinbase.com/en/coinbase/trading-and-funding/loan/loan-intro).

**Circle–Coinbase.** Circle's Q3 2026 SEC 10-Q reports **$331.3M** in distribution costs to Coinbase for Q3 and **$986.6M** for the first nine months. The formula allocates amounts based on USDC held on Coinbase after issuer retention and a share of broader ecosystem growth. This is a contractual USDC distribution relationship, not XRP demand. [Circle SEC 10-Q](https://www.sec.gov/Archives/edgar/data/1876042/000187604226000311/crcl-20260930.htm).

**Circle–Binance.** The same filing states Circle issued **1.2M Class A shares to Binance at $80.84 per share**, for **$100M**, under a September 17, 2026 private placement. This establishes a direct Circle equity relationship alongside the commercial USDC distribution relationship. It does not establish Binance investment in XRP or XRP demand.

**SBI/Ripple/Circle/BNY.** Previously verified distinctions remain: Circle/SBI Japan 50/50 joint venture is separate from SBI's strategic equity investment in Circle; SBI Holdings/Ripple equity and SBI Ripple Asia are separate from SBI Remit's XRP bridge corridors; RLUSD distribution and JPYSC lending are separate products. BNY and Coinbase custody roles do not prove proprietary XRP holdings or collateral utilization. SBI Remit corridor throughput and XRP conversion volumes remain undisclosed in reviewed public records.

### SBIC, ASK Coin, actual capital and Kamilah Stevenson

Japan's SBIC East, Central and West are Tokyo, Nagoya and Osaka Small and Medium Business Investment & Consultation companies. They are separate regional sister companies under Japan's 1963 Act, not SBI Holdings. Tokyo SBIC's March 5, 2026 seminar, “Generative AI (ChatGPT): Present and Future,” was an educational event co-hosted by Hamamatsu Iwata Shinkin and presented by a Microsoft Japan executive. It is not an OpenAI partnership or XRP relationship. [Official SBIC seminar](https://www.sbic.co.jp/seminar/20260305js/).

The exact “ASK Coin” search still does not resolve one XRP-linked asset: Ask Coin exchange and Permission Coin ASK are distinct candidates; no XRP integration is verified. “Actual capital” is not a standardized XRP metric; settled cash, in-kind XRP, debt, contingent equity capacity, warrants and secondary resales remain separate categories. The Kamilah Stevenson person identity is confirmed, but canonical YouTube channel ID/handle ownership is not first-party verified. Ten candidate video references remain candidate-only; verified personal-channel inventory remains zero.

### Prediction-engine readiness

The integration branch has **46 source definitions**: 42 hourly, two weekly CFTC and two non-commercial XRPL nodes excluded by default. The collector's HTTP POST is restricted to the fixed read-only XRPL JSON-RPC `server_info` method on allowlisted public HTTPS nodes; no ledger mutation method is exposed.

Implemented: raw payload SHA-256 receipts, canonical receipt IDs, per-run hash-chain verification, point-in-time SQLite prototype, four deterministic baselines, chronological walk-forward evaluation with purge/embargo, calibration/drift diagnostics and a fail-closed forecast ledger requiring trusted Ed25519 evaluator attestation.

Limitations:
1. Raw artifacts have 90-day GitHub Actions retention; feature-store artifacts have seven-day retention.
2. No independent WORM store or trusted timestamp authority.
3. Feature-store rebuild from raw artifacts is not implemented.
4. The scheduled collector is main-only and has no verified successful main run. It uploads GitHub Actions artifacts and saves cache; it does not commit collected data to main.
5. Historical spot/L2, derivatives, exchange-flow and collateral coverage is not yet synchronized.
6. Source independence and effective sample size for overlapping horizons require stronger validation.
7. No production evaluator key, sufficient independent shadow outcomes or demonstrated out-of-sample lift.

**Forecast status: NOT_ISSUED.** No directional forecast, paper trade or real-money action occurred.

### Nine-platform coordination

- ChatGPT: current-session GitHub read/write on the existing integration branch and public web research verified; no main write, branch-protection administration, secret access, deployment or external-model data transfer.
- Copilot: 62 COMMENTED reviews, zero approvals; 22 threads resolved but outdated; no persistent external data flow verified.
- Claude, Grok, Gemini and Codex: no authenticated persistent connection or data flow verified.
- Hugging Face: prior BUILD_ERROR; no upload or Space restart.
- Kaggle: untested; no submission.
- Databricks: prior/main Pillars HTTP 403; no workspace write.

No external model received repository data. Independent assignments remain designed, not executed. Minority objections and source disagreements are retained in the evidence archive.

### Backlog, merge decision and safety

- #1640: **BLOCKED**, sole active V3/XRP integration path.
- #1642: 7/7 changed paths overlap #1640; exact duplicate/superseded candidate, but keep open until a successor is merged and verified.
- #1643: 670 changed paths, seven overlap and 663 unique; preserve unique research.
- #1653: seven paths, one overlap and six unique; preserve knowledge-graph work. Prior review record shows eight unresolved threads.
- #1614: 57 paths, eight overlap and 49 unique; preserve prediction work.
- #1611: eight paths, six overlap and two unique; preserve unique material and reconcile shared files.
- #1644–#1650: shared-path dependency/action candidates; exact content/version reconciliation remains required. Path overlap alone does not prove duplicate.
- #1269: nine paths, one overlap and eight unique; preserve topology work.
- No PRs were closed.

PR #1640 still has 62 COMMENTED reviews and zero APPROVED reviews. All 22 inline threads are resolved but outdated. Main is protected, but detailed branch-protection access returns HTTP 403; the visible “Fall Back” ruleset is disabled. GitHub Pages previously deployed automatically after a main push. PR #1640 changes public web assets, and authorization for that automatic public publication is not established. The user-authorized merge conditions are therefore not satisfied. **No merge or deployment was performed.**

No secret rotation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push, destructive worktree operation or PR closure occurred.

### Next concrete actions

1. Obtain an independent approving review and authoritative branch-protection visibility.
2. Resolve explicit authorization for automatic GitHub Pages publication before merge.
3. Complete semantic review of all 270 changed paths and the 42 changed workflow definitions; preserve #1640 as the single integration path.
4. Verify exact-head full-suite, dependency/security and fail-closed gates on the Run131 evidence commit.
5. Resolve Pillars provider blockers only with valid credentials/access; do not fabricate or rotate secrets.
6. Extend raw receipt retention beyond 90-day GitHub artifacts and implement independent WORM/timestamp anchoring and reproducible feature-store rebuilds.
7. Populate synchronized historical data, then evaluate out-of-sample lift and independent shadow outcomes before any forecast issuance.

**Forecast status: NOT_ISSUED.** Run131 records research and evidence only; no directional forecast was issued.


---

## Run131A — CFTC report-scope reconciliation, Coinbase/Circle filings and MiCA event

**Captured:** 2026-11-10T14:06:11Z. This is a supplemental research addendum to Run131; no historical artifact was overwritten.

### CFTC report-scope correction

The scheduled Barrot CFTC adapter reads the **futures-only** TFF file `financial_lf.htm`. Run131 also reviewed the separate **futures-and-options combined** file `financial_lof.htm`.

Both files show the same XRP open-interest counts as of November 3:
- CME XRP: 7,216 contracts × 50,000 XRP = 360.800M XRP-equivalent.
- Coinbase Nano XRP: 32,505 × 500 = 16.2525M.
- Coinbase Nano XRP Perp Style: 38,392 × 500 = 19.196M.
- Total gross underlying-equivalent OI: **396.2485M XRP**.

The weekly CME change differs by five contracts:
- Futures-only: −845 CME contracts; total underlying-equivalent weekly change **−58.9145M XRP**.
- Futures-and-options combined: −850 CME contracts; total underlying-equivalent weekly change **−59.1645M XRP**.

The reason for the five-contract difference is not established. Both series are preserved. The scheduled adapter must use the futures-only result; the combined report is a supplemental cross-check. Neither total represents cash invested, net directional exposure or spot demand.

### Coinbase and Circle Q3 2026 filings

Coinbase's September 30 Form 10-Q reports:
- Q3 stablecoin revenue: **$306.905M**.
- Nine-month stablecoin revenue: **$904.487M**.
- Average USDC held on Coinbase products reached a company-reported all-time high.
- The Circle arrangement was renewed on the same terms in 2026.
- Total assets on platform: $376.6B; Q3 net revenue approximately $1.2B; net income $718.7M.

The reviewed Coinbase 10-Q does not disclose XRP-specific holdings or collateral balances. This is a disclosure limitation, not proof of zero exposure. [Coinbase SEC 10-Q](https://www.sec.gov/Archives/edgar/data/1679788/000167978826000122/coin-20260930.htm).

Circle's September 30 Form 10-Q reports:
- Average USDC circulation **$73.3B**; September 30 circulation **$73.879B**.
- Q3 USDC on-chain transaction volume **$13.9T**.
- Q3 revenue and reserve income **$865M**; net income **$226M**; adjusted EBITDA **$317M**.
- Reserve income represented 76.0% of Q3 total revenue; reserve return rate was 3.5%.
- Distribution costs to Coinbase were **$331.3M in Q3** and **$986.6M for nine months**.
- Circle issued **1.2M shares to Binance at $80.84**, a **$100M** September 17 private placement. Circle also describes Binance as distributing USDC across its product suite and using USDC for corporate treasury.

Circle's USDC-on-platform measure is Circle's own platform, not Coinbase balances. Circle's distribution expense and Coinbase's stablecoin revenue are different accounting measures and must not be netted. The Binance relationship is a direct equity and USDC-distribution relationship, not evidence of XRP investment or demand. [Circle SEC 10-Q](https://www.sec.gov/Archives/edgar/data/1876042/000187604226000311/crcl-20260930.htm).

### MiCA regulatory event

The EBA announced on **October 14, 2026** that USDC issued in the EU by Circle Internet Financial Europe SAS was the first significant e-money token under MiCA. Dual supervision begins **November 12, 2026**. The EBA assumes direct responsibility for own funds, reserve assets, liquidity and recovery/redemption plans; ACPR retains governance, qualifying holdings, fit-and-proper, outsourcing and conflicts. This is a regulatory event for USDC distribution, not an XRP-specific approval. [EBA primary announcement](https://www.eba.europa.eu/publications-and-media/press-releases/eba-classifies-usdc-first-significant-e-money-token-european-union).

Legal-entity separation remains mandatory:
- Circle National Trust Bank (OCC), Circle Internet Trust Company LLC (NYDFS), Circle Internet Financial LLC (USDC issuer) and Circle Internet Financial Europe SAS (EU EMT issuer) are distinct.
- Ripple National Trust Bank (OCC) is distinct from Standard Custody & Trust Company, the RLUSD issuer identified in reviewed materials.
- Coinbase National Trust Company (OCC) is distinct from Coinbase Global, Inc.

### Ripple/Coinbase/Standard Chartered/BNY collateral and custody boundaries

- Coinbase confirms XRP as eligible collateral for USDC loans through Morpho on Base; Coinbase is the interface, Morpho the lending protocol. This is not native XRPL lending.
- Coinbase's RLUSD trading and XRPL/Base/Ethereum transfer support is live; Global Exchange collateral support was described as future.
- Standard Chartered custody support for RLUSD on XRPL is announced; LMAX collateral integration is planned, not verified live.
- BNY announced XRP and RLUSD custody support. Custody does not prove proprietary purchases, beneficial ownership or collateral utilization.
- No direct Ripple-Circle equity or operating partnership was established in the reviewed primary filings. Shared counterparties such as Coinbase and SBI do not prove a direct relationship.

### Prediction-engine architecture gap audit

The 46-source registry contains 42 hourly sources, two weekly CFTC sources and two non-commercial XRPL nodes excluded by default. It does **not** currently include scheduled BLS/PCE, Treasury yield-curve, Fed communications, oil/energy, FX/USD or geopolitical event sources. The collector does not yet generate a unified event timeline or generate scenarios/counter-hypotheses; the forecast ledger records assumptions and alternatives but does not generate them. Shadow-evaluation runner is not implemented. Feature drift is PSI-style and does not demonstrate label/concept-drift monitoring. Effective-sample-size correction for overlapping horizons, raw-artifact-to-feature-store replay, and independent WORM/timestamp anchoring remain absent.

Manual event research must remain distinct from scheduled model features. Next implementation priority is a versioned macro/event adapter with point-in-time release timestamps, raw replay, source independence and reproducible feature-store rebuild. Forecast status remains **NOT_ISSUED**.

[Structured Run131A supplemental evidence](https://github.com/Barrot-Agent/B-Agent/blob/integration/core-capabilities-mmi-structural-paper-20261104/research/xrp_intelligence/20261110T140611Z-run131a-cftc-futures-only-circle-mica-custody-update.json).


---

## Run131B — Coinbase national trust approval, PNC/USDC pilot, current cbXRP collateral and post-CPI market pricing

**Captured:** 2026-11-10T14:10:58Z. This is an append-only addendum to Run131A. No earlier evidence was overwritten.

### Repository and integration verification

- Current main: `d4d43be3427375cf79d190e768976de062e20287`; 1,404 tree entries, 1,299 files and 86 workflow files. Main has no XRP ingestion module or `.github/workflows/xrp-public-ingestion.yml`; no workflow runs or combined statuses were returned for this main SHA.
- Current #1640 integration branch parent head: `c869905562d0aeae552eca807fcbdf28c5ae0a1b`; 1,568 tree entries, 1,455 files and 87 workflow files. PR #1640 is open, non-draft, 964 commits ahead, zero behind, 273 changed files, mergeable and clean.
- Exact-head CI on the parent head passed **1,380 full-suite tests**, zero failures, eight subtests, 59.58% inclusive coverage; wheel build and installed-wheel mission verification passed. Dependency audit passed all six manifests with zero known vulnerabilities. Fail-closed gate passed and explicitly states automatic merge is disabled.
- Evidence: [CI 42830889965](https://github.com/Barrot-Agent/B-Agent/actions/runs/42830889965), [dependency audit 42830889854](https://github.com/Barrot-Agent/B-Agent/actions/runs/42830889854), [fail-closed gate 42830889942](https://github.com/Barrot-Agent/B-Agent/actions/runs/42830889942).
- PR #1640 has 62 COMMENTED reviews, zero APPROVED reviews and 22/22 inline threads resolved but outdated. The branch is clean, but required independent approval is still absent. Main is marked protected; required-status contexts exposed by the branch endpoint are empty, and detailed branch-protection settings remain inaccessible. GitHub Pages previously deployed automatically after a main push; this PR changes public web assets, and publication authorization is not established. **Do not merge.**
- The artifact/test/handoff evidence commit being added with this Run131B section is a new head; the parent-head CI above does not test that new commit. Exact-head CI must run again after the commit.
- Open PR inventory remains 372. No new PR was created.

### New Coinbase regulatory and payment-rail findings

**Coinbase National Trust Company.** Coinbase's November 9 announcement says it received final OCC approval to charter Coinbase National Trust Company. The OCC CAS filing record identifies November 6, 2026 as the consummated/effective date. This supersedes the older conditional-approval-only description in prior handoffs. The new charter expands Coinbase's federal trust/custody framework; it does not establish FDIC-insured commercial deposit banking, XRP-specific custody balances or XRP purchases. [Coinbase announcement](https://www.coinbase.com/blog/coinbase-launches-national-trust-company-with-federally-regulated-institutional-grade-custody-offering) · [OCC CAS record](https://apps.occ.gov/CAS/home/details?FilingID=3RAoRRek6o4j&FilingSubtypeID=1093&FilingTypeID=2).

**PNC/USDC pilot.** Coinbase announced on November 9 that eligible PNC Corporate and Institutional Banking clients can receive USDC through a pilot powered by Coinbase Payment APIs. Incoming USDC is automatically converted 1-to-1 into USD and deposited to a designated PNC account. No pilot volume, active-client count or independent PNC press release was located. The announced path is USDC-to-USD; no XRP, XRPL or RLUSD leg is specified. [Coinbase announcement](https://www.coinbase.com/blog/coinbase-and-pnc-expand-partnership-to-bring-stablecoin-payment-acceptance-to-corporate-clients).

**Coinbase Q3 positioning.** The October 29 issuer release reports 10.7% crypto trading-volume market share, 12.5% assets-on-platform share, $22B average USDC held in Coinbase products, subscription/services revenue at 49% of net revenue, $200M annualized prediction-markets revenue and 179% two-year CAGR in crypto derivatives volume. These are company-reported, company-level metrics; none proves XRP spot demand. Coinbase's 10-Q says its Circle arrangement was renewed on the same terms. [Coinbase Q3 release](https://investor.coinbase.com/news/news-details/2026/Coinbase-Q3-2026-Earnings-Show-All-time-high-Coinbase-One-Subscribers-and-Prediction-Markets-Surpassing-200-Million-in-Annualized-Revenue/) · [Coinbase SEC 10-Q](https://www.sec.gov/Archives/edgar/data/1679788/000167978826000122/coin-20260930.htm).

### Circle Q3 economics and Coinbase distribution dependence

Circle's November 4 Q3 results report average USDC circulation of **$73.3B**, end-period circulation of **$73.9B**, Q3 USDC onchain transaction volume of **$13.9T**, revenue and reserve income of **$865M**, reserve income of **$658M**, other revenue of **$207M** (including **$182M** ARC token presale revenue), total distribution/transaction/other costs of **$412M**, net income of **$226M** and adjusted EBITDA of **$317M**. The $182M ARC presale component is not recurring USDC reserve income. Q3 USDC minted and redeemed were each reported at $104B; gross mint/redemption volume is not net capital inflow. [Circle Q3 SEC exhibit](https://www.sec.gov/Archives/edgar/data/1876042/000187604226000309/finalq3epr-110326.htm).

Circle's Q3 10-Q reports **$331.3M** distribution costs in connection with Coinbase agreements for Q3 and **$986.6M** for the first nine months. The allocation formula depends on USDC held on Coinbase after issuer retention and broader ecosystem-growth arrangements. These are Circle-incurred distribution costs, not a direct measure of Coinbase-recognized revenue, and they must not be netted against Coinbase's stablecoin revenue. The relationship is economically material to both companies but is USDC distribution economics, not XRP demand. [Circle SEC 10-Q](https://www.sec.gov/Archives/edgar/data/1876042/000187604226000311/crcl-20260930.htm).

### Current cbXRP collateral market — 14:01 UTC

MorphoWatch, reporting Morpho API data, updated the Base cbXRP/USDC market at **14:01 UTC**:

| Metric | Snapshot |
|---|---:|
| USDC supplied | $62.93M |
| USDC borrowed | $55.37M |
| Utilization | 88.0% |
| Available USDC | $7.56M |
| cbXRP collateral | 120.40M |
| Collateral value | $128.6M |
| Open loans/borrowers displayed | 11,694 |
| Borrow / supply APY | 6.98% / 6.12% |
| LLTV / liquidation bonus | 62.5% / 12.68% |
| Oracle / displayed cbXRP price | $1.07 / $1.0680 |
| Liquidations, prior 30 days | 1,479 |
| Debt repaid in those liquidations | $6.27M |

One displayed top borrower has health factor 1.03 and a 3% price distance to liquidation. The three largest listed vaults supply $44.50M, approximately **70.71%** of total supply; the ten listed vaults supply $53.09M, approximately **84.36%**. These are vault-level concentration measures, not beneficial-lender concentration.

Coinbase's proof-of-reserves page displayed 152,372,342.33 XRP reserves against 152,370,095.8 cbXRP supply, a 2,246.53 XRP displayed surplus. The page's refresh time is 9:34 AM with timezone unspecified. Dividing the Morpho market's 120.40M cbXRP by total displayed cbXRP supply gives an indicative 79.02%, but source timestamps are not synchronized and the ratio is **not model-admitted**.

The Barrot ingestion branch already contains the exact Base market ID `0xd4a903dc6d949519060c7707f9604fdc9772c046e05c2e3a8fce0bd7196e4109`, chain ID 8453, loan/collateral token addresses and Chainlink oracle address. Its Morpho parser/tests keep these observations digest-only/raw-only. The next step is direct block-height, oracle-round, borrower-health and liquidation-transaction reconciliation before any feature admission. [Morpho market snapshot](https://morphowatch.com/markets/base/cbxrp-usdc-62-5/) · [Coinbase reserves](https://www.coinbase.com/cbxrp/proof-of-reserves).

### Post-CPI Federal Reserve pricing disagreement

The October CPI release itself is already captured in Run131: headline +0.4% m/m and core +0.3% m/m, each 0.1 percentage point above the Reuters preview consensus; BLS cannot publish most October year-over-year comparisons because October 2025 data were not collected.

This addendum locates post-release Fed-pricing reports that were unavailable in Run131:

- Investing.com, using CME 30-Day Fed Funds futures, showed a **pre-release** snapshot at 08:25 ET: 97.8% for a 25bp December hike and 2.2% hold.
- Barron's reported **post-release** CME FedWatch pricing of 86.4% for a 25bp hike, 13.6% for a 50bp hike and zero hold.
- WSJ separately reported approximately 90% for 25bp and 10% for 50bp, versus the prior day's 84%/0% split.

The common signal is that the December hike remained fully priced while a 50bp tail appeared after the CPI surprise. The 86.4/13.6 and 90/10 snapshots differ and their exact capture minutes are unavailable. Barron's and WSJ report the same CME underlying market, so they are not independent venues. Preserve both; do not average. This is a macro event feature, not an XRP directional signal. [Pre-release CME futures monitor](https://www.investing.com/central-banks/fed-rate-monitor) · [Barron's post-release report](https://www.barrons.com/livecoverage/stock-market-news-today-111026/card/odds-of-a-larger-december-rate-hike-jump-after-cpi-JCMu5hQ9u1Lqcae8Zr9k) · [WSJ post-release report](https://www.wsj.com/livecoverage/stock-market-cpi-inflation-11-10-2026/card/traders-dial-up-rate-hike-bets-UHxkB8mixxnMCsJGBcH6).

### Spot, order-book and ETF data quality

- OKX XRP-USDT ticker provider time was 13:48:36.536 UTC, **1,341.464 seconds** before the 14:10:58 UTC capture, exceeding the 300-second live-data threshold.
- Kraken ticker returned no provider event timestamp and repeated an identical cached payload.
- Binance and OKX depth requests returned HTTP 403 through this retrieval path. A 403 is access failure, not zero liquidity.
- No synchronized cross-venue post-CPI XRP spot/depth window was available.
- November 9 ETF flow observations remain partial: CryptoETF reported roughly $10.3M outflow across 3/5 funds; CryptoKeyhole reported approximately 9.217M XRP outflow across 3/4 daily funds; XRP Insights' latest settled row is November 9 but uses holdings-derived deltas and different exclusions. These sources overlap issuer files and are not independent confirmations. None proves spot execution or net cash outflow.

### Architecture, prediction boundary and backlog

The integration branch's 46-source collector, raw SHA-256 receipt archive, point-in-time SQLite prototype, chronological walk-forward baselines and fail-closed forecast ledger remain implemented on the branch, not main. The scheduled workflow is main-only and has not run successfully on main. The macro source gap remains: no scheduled BLS/PCE, Treasury yield-curve, Fed communication, energy, FX/USD or geopolitical event adapter; no unified event timeline/scenario generator; no shadow-evaluation runner; no concept-drift monitor; no reproducible raw-to-feature-store rebuild; no independent WORM/timestamp authority.

Backlog classification:
- #1640: **BLOCKED** — sole V3/XRP integration path; exact parent-head checks passed, but zero approving reviews and public Pages side-effect authorization unresolved.
- #1642: **DUPLICATE CANDIDATE** — all seven changed paths overlap #1640; keep open until successor content is merged and verified.
- #1643: **UNIQUE/UNREVIEWED, STALE/BLOCKED** — 670 paths, seven overlap #1640 and 663 unique; base is old, current head is dirty/unmergeable and has no current-head CI. Preserve unique research.
- #1653: **UNIQUE/UNREVIEWED** — six unique knowledge-graph paths and one overlap with #1640.
- #1614: **UNIQUE/STALE** — 49 paths unique to its older prediction work; preserve until reconciled.
- #1611: **UNIQUE/STALE** — two unique research artifacts; preserve.
- #1269: **UNIQUE/STALE** — eight unique topology paths; preserve.
- 372 open PRs remain. No PR was closed.

**Forecast status: NOT_ISSUED.** No synchronized post-CPI XRP market response, no new leakage-safe out-of-sample lift and no independent shadow outcomes. No paper-trading or real-money action occurred.

**Safety:** No merge, deployment, PR closure, secret change, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, force-push, reset, clean, stash or discard occurred.

### Next concrete actions

1. Verify the new Run131B artifact/test/handoff commit on exact-head full CI, dependency audit and fail-closed gate.
2. Implement a versioned BLS/PCE/Fed/Treasury/FX/energy event adapter with first-release vintages, raw-byte receipts, exact availability timestamps and leakage-safe historical replay.
3. Reconcile Morpho state directly by Base block height, oracle round, borrower health and liquidation transactions.
4. Capture synchronized multi-venue XRP/USD and XRP/USDT spot/L2 snapshots with quote-currency conversion and freshness checks.
5. Resolve #1640's independent approval and Pages publication blocker before merge.
6. Keep #1643's 663 unique research paths intact; consolidate only after a current-main integration decision.
7. Keep directional forecast issuance blocked until synchronized data and out-of-sample/shadow evaluation pass.


---

## Run131B correction — Morpho collateral-token address and Circle payment-network expansion

**Captured:** 2026-11-10T14:16:51Z. Append-only correction; the original Run131B artifact remains unchanged.

### Contract-address correction

The original Run131B JSON contains a transcription error in `market_snapshot.morpho_cbxrp_usdc.collateral_token`. Its recorded value `0xcb585250f852b6e08f4c7c32d4f71b54bda02913` is **not authoritative**. The correct cbXRP collateral token is:

`0xcb585250f852b6c6bf90434ab21a00f02833a4af`

The loan token remains:

`0x833589fcd6edb6e08f4c7c32d4f71b54bda02913`

The oracle remains:

`0x031b2efc8d70042ac8d9f5c793c4149ec4b60fde`

These values match the versioned Barrot source constants at `barrot_agent/evolution/xrp_public_ingestion.py` lines 73–75 and the abbreviated token/oracle identities displayed by MorphoWatch. The original artifact was not edited; the correction file records the original and corrected values and is authoritative for this field. The correction does **not** promote Morpho collateral data into model features; direct block-height/oracle verification is still required.

[Append-only correction artifact](research/xrp_intelligence/20261110T141651Z-run131b-cbxrp-address-circle-network-correction.json).

### Additional Circle network evidence from its November 4 Q3 release

Circle's Q3 release reports:
- Circle Payments Network annualized TPV of **$41.3B** in Q3. This is annualized gross throughput, not net capital inflow or XRP demand.
- A definitive agreement to acquire Tazapay, expected to close in 2027 subject to regulatory approvals. Circle quotes Tazapay at **$25B+** annualized payment volume, **60+** bank/fintech partners, local payout rails in **100+** markets and approximately **60%** stablecoin-related transaction volume. Tazapay has not yet been acquired; do not add its volume to Circle's current TPV.
- Visa Direct stablecoin prefunding moved from pilots to commercial deployment with Inyo Global, using **USDC** for eligible cross-border prefunding across **180+** countries.
- Arc public mainnet launched September 16 with **100+** institutional/ecosystem builders on day one and native USDC integration.
- Samsung Wallet USDC payment support to qualifying bank accounts in **60+** countries and Tereina's USDC/EURC integration into SAP-related enterprise workflows.

These are issuer-reported operating/partnership announcements. The Q3 release does not specify an XRP or XRPL settlement leg for these channels. This strengthens the competing hypothesis that Circle is building an independent stablecoin/payment network across bank, wallet, enterprise and L1 channels; it does not prove displacement of Ripple or XRP. [Circle Q3 primary release](https://www.sec.gov/Archives/edgar/data/1876042/000187604226000309/finalq3epr-110326.htm).

### Verification boundary

The Run131B parent head `cb0ad2833a2b8dd2517bca061b9b32db75c07418` had a full-suite CI run in progress when this correction was prepared. The new correction/test/handoff commit is a different head and requires its own full-suite CI, dependency audit and fail-closed gate. Do not transfer parent-head test claims to the correction head.

**Forecast status: NOT_ISSUED.** No directional forecast, paper trade, real-money action, merge or deployment occurred.
