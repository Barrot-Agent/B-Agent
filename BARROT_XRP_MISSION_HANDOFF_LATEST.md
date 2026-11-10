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
