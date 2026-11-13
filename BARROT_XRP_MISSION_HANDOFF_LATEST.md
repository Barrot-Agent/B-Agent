# Barrot XRP Intelligence Mission — Current Durable Handoff

**Run:** 91D  
**Captured:** 2026-11-13 13:45 UTC  
**Priority:** XRP intelligence and measured prediction-engine mastery  
**Protected foundation:** Barrot V3 execution, orchestration, safety and verification

This is the current-state handoff. Earlier run artifacts and the previous handoff blob remain preserved in Git history. This file is a concise operational snapshot, not a forecast.

## 1. Repository and integration state

- Repository: [Barrot-Agent/B-Agent](https://github.com/Barrot-Agent/B-Agent)
- Current main SHA at audit: `fb272b40966834754ec686f9ed3ab94123f09306`
- Code-bearing integration head audited: `c6d6dab969df061ed09fd337a869af55b69e1863`
- Branch: `integration/xrp-v3-unified-main-20261112`
- Consolidated integration: [PR #1662](https://github.com/Barrot-Agent/B-Agent/pull/1662)
- PR state at audit: open, draft, mergeable, 2,245 commits ahead and zero behind main; 1,105 changed files; 316,273 additions; 5,136 deletions; zero formal reviews, approvals or review threads.
- Recursive tree: main 1,381 entries; integration 2,351 entries; 88 integration workflow files. The recursive tree includes directory objects. The PR's 1,105-file count reconciles to 1,104 changed/added blob paths plus the mode-only `b_agent.sh` change (100755 on main to 100644 on integration, same blob SHA).
- Open PR inventory: 375 total, 361 drafts and 14 non-drafts.
- The current Run91D artifact and platform map were committed as documentation/research-only descendants after the code-bearing head. The handoff update itself is another documentation-only descendant. Their exact-head CI is pending at the moment this handoff is written; predecessor CI must not be represented as verification of those later SHAs.

## 2. Exact-head software verification

Verified on the code-bearing integration head `c6d6dab969df061ed09fd337a869af55b69e1863`:

| Check | Result |
|---|---:|
| Full repository tests | 3,557 passed |
| Failures | 0 |
| Subtests | 8 passed |
| Inclusive coverage | 61.72% |
| Full-suite duration | 66.11 seconds |
| Core tests | 729 passed |
| Core coverage | 76% |
| Wheel build | Passed |
| Packaged primary-mission verification | Passed |
| Dependency audit | Five manifest groups passed; zero known vulnerabilities reported |
| Fail-closed gate | Passed; automatic merge intentionally disabled |

Evidence:
- [Full CI run 43433988510](https://github.com/Barrot-Agent/B-Agent/actions/runs/43433988510)
- [Dependency audit 43433988513](https://github.com/Barrot-Agent/B-Agent/actions/runs/43433988513)
- [Fail-closed gate 43433988546](https://github.com/Barrot-Agent/B-Agent/actions/runs/43433988546)

These are software checks, not evidence of XRP predictive skill. Exact-head checks for the subsequent Run91D documentation-only commits must complete separately.

## 3. Current XRP market research — 13 November 2026

**Admission rule:** the web observations below are research context only. They were not inserted into the point-in-time feature store, no byte-exact publisher response was archived, and none is eligible for a live forecast.

### Spot

- OKX XRP-USDT public ticker event time: 13:06:40.668 UTC; last $1.0194, bid $1.0192, ask $1.0193; 24-hour open $1.0343, high $1.0440, low $0.9974; volume 46.397M XRP. At the 13:32 UTC audit cutoff this observation was about 25 minutes old, beyond the 300-second live-data limit.
- Kraken XRP/USD retrieval showed last $1.0188, bid $1.01860 and ask $1.01861, but the public ticker response supplied no provider event timestamp. It is excluded from strict point-in-time admission.
- These are different quote currencies and unsynchronized snapshots. No executable cross-venue spread or arbitrage conclusion is supported.
- Direct order-book depth endpoints were inaccessible in this web retrieval. No current synchronized spot L2 snapshot was admitted.

Sources: [OKX ticker API](https://www.okx.com/api/v5/market/ticker?instId=XRP-USDT), [Kraken ticker API](https://api.kraken.com/0/public/Ticker?pair=XRPUSD).

### Derivatives and liquidity

- Swiftedge's 13:11 UTC XRP perpetual snapshot: $1.0183, daily change -2.2%, range $0.9970–$1.0438; funding +0.0100% per eight hours; 91.118M XRP open interest (about $92.8M), up 2% over 24 hours. Its largest displayed bid wall was 1.0055 (3.433M XRP) and ask wall 1.0240 (2.167M XRP); it reported no clean wall event. This is vendor-derived perpetual-market positioning, not consolidated spot depth.
- Liqwall's 13:22 UTC all-exchange snapshot: approximately $1.12B XRP futures OI, down 0.9% over 24 hours; average funding +0.0084% per eight hours (Binance +0.0100%); $13.7M liquidations, $12.7M long and $1.0M short; 74.7% of Binance accounts long. This is a vendor aggregate across 14 exchanges, about 23 minutes old at the 13:45 cutoff, so it fails the 300-second live gate.
- Swiftedge's 13:11 UTC XRP perpetual snapshot: $1.0183, daily change -2.2%, range $0.9970–$1.0438; funding +0.0100% per eight hours; 91.118M XRP OI (about $92.8M), up 2% over 24 hours. Its largest displayed bid wall was 1.0055 (3.433M XRP) and ask wall 1.0240 (2.167M XRP); it reported no clean wall event. This is vendor-derived perpetual-market positioning, not consolidated spot depth.
- Kodexius's 08:44 UTC snapshot reported $614.05M across seven perpetual contracts, $1.76B 24-hour volume and +0.0003% open-interest-weighted funding. The displayed contract rows sum to about $614.03M, a $20,000 rounding difference. Funding signs differ by venue. At the audit cutoff this snapshot was about five hours old and is not live model input.
- TrackWhale's 13:20 UTC selected public transfer sample showed 52 large-transfer records: 79.73M XRP exchange inflows across four transfers, 161.61M XRP outflows across eight, net -81.88M XRP (USD estimates: -$87.36M). Internal and exchange-to-exchange transfers are excluded; unknown-wallet movements do not prove selling. The sample is about 25 minutes old and is not complete exchange-wallet accounting.
- These vendor aggregates overlap upstream exchange data. They are not independent exchange confirmations and must not be averaged with other vendor totals.

Sources: [Swiftedge XRP market](https://swiftedge.uk/xrp/today), [Kodexius XRP derivatives](https://kodexius.com/data/crypto-derivatives/XRP).

### ETF flows

XRP Insights' issuer-holdings-derived series, as of 12 November, tracks six US spot XRP ETFs plus the XRP sleeve of BITW and reports:
- 9–12 November: -9,481,905 XRP (approximately -$9.9M), across four settled trading days.
- Total reported holdings: 1,185,698,783 XRP.
- Estimated aggregate average cost basis: $1.7096 per XRP; the page values the holdings at about $1.02 on 12 November, roughly 40.3% below that estimated cost basis.

Its methodology is important: daily flows are computed from changes in issuer-reported holdings, not issuer flow reports. Flow-excluded funds count zero in the headline, BITW rebalancing or XRP-denominated fees can appear as flows, and some historical rows are reconstructed from third-party estimates. The $1.71 average cost basis is not a market support level or price target.

Alpha Finance's separate five-fund tracker, through the 12 November session, reported:
- Seven sessions (5–12 November): -$18.0M.
- Thirty sessions: -$2.8M.
- Cumulative net inflow since launch: +$1.71B.
- 12 November: $0 net flow across its five tracked funds.
- Its page says fund list, AUM, holdings and fees are not published.

These series use different universes, units and methods. Do not average them or interpret a zero as universal evidence of no creations/redemptions. Preserve each tracker cohort and missing-file policy separately.

Source: [Alpha Finance XRP ETF dashboard](https://alphafinance.io/etf/xrp/).

## 3A. Macro and cross-asset liquidity context

- Glassnode's 11 November Week 45 report says major stablecoin supply contracted by $14.2B over 30 days through 9 November, the largest contraction since June 2022. It also reports approximately $1.6B in US spot Bitcoin ETF net outflows over 20 sessions and a Coinbase spot discount. Counter-evidence in the same report: leverage had been flushed, bids outweighed asks in the Bitcoin order book, and two large BTC wallet cohorts began accumulating. These are broad crypto/BTC measures, not XRP-specific observations.
- The US BLS October PPI release on 13 November at 08:30 ET reported final demand +0.3% month over month and +6.5% year over year; final demand excluding food, energy and trade services +0.5% month over month and +4.9% year over year. Higher producer-price inflation can reinforce restrictive-rate expectations, but is not an XRP-specific causal signal.
- Reuters reported the dollar was on track for its strongest week in about two months, the US two-year yield near 4.86%, a roughly 12% market-implied chance of a 50-basis-point December Fed hike, and USD/JPY near 159.99. China also conducted large unannounced Pacific drills, with around 70 vessels still active Friday. These are macro/geopolitical risk context, not evidence of an XRP-specific catalyst.

Competing hypotheses:
1. **Risk-off:** XRP ETF holdings-derived outflows, shrinking broad stablecoin supply, hawkish-rate repricing, dollar strength and long-skewed XRP liquidations can jointly pressure risk appetite.
2. **Stabilization:** leverage flushing, BTC large-wallet accumulation and bid-side BTC depth can support a broader-market stabilization hypothesis. Those are BTC observations, not proof of XRP buying. XRP funding remains positive in the latest Liqwall aggregate and OI is down less than 1% over 24 hours, so a full XRP deleveraging conclusion is premature.
3. **Institutional adoption:** RLUSD custody and payment rails can expand XRPL stablecoin use without requiring incremental XRP demand. PNC/Coinbase uses USDC converted to USD; Standard Chartered/LMAX's planned collateral is RLUSD, not native XRP.

Sources: [Glassnode Week 45](https://research.glassnode.com/the-week-onchain-week-45-2026/), [BLS October 2026 PPI](https://www.bls.gov/news.release/ppi.nr0.htm), [Reuters dollar/yields/yen](https://www.reuters.com/world/africa/dollar-near-19-month-high-fed-hike-bets-yen-tests-160-2026-11-13/), [Reuters China drills](https://www.reuters.com/world/china/china-stages-unannounced-pacific-drills-silent-intimidation-taiwan-officials-say-2026-11-13/).

## 4. Institutional, stablecoin and regulatory evidence

- **USDC / EBA:** EBA classified USDC, issued in the EU by Circle Internet Financial Europe SAS, as the EU's first significant e-money token on 14 October 2026; dual supervision took effect 12 November. EBA directly supervises own funds, reserve assets, liquidity and recovery/redemption plans. ACPR retains governance, qualifying holdings, fit-and-proper, outsourcing and conflicts oversight. The EU issuer is distinct from US issuer Circle Internet Financial LLC. This is a significant USDC regulatory milestone and a competing dollar rail, not evidence of XRP demand. [EBA primary release](https://www.eba.europa.eu/publications-and-media/press-releases/eba-classifies-usdc-first-significant-e-money-token-european-union).
- **Standard Chartered / RLUSD:** Standard Chartered says institutional custody for RLUSD issued on XRPL is live through its DFSA-regulated DIFC branch. The LMAX collateral-mirroring arrangement is planned and remains subject to final documentation, testing, law/regulation, internal approvals and jurisdictional readiness. RLUSD custody or RLUSD collateral is not native XRP collateral or evidence of XRP purchases. [Standard Chartered primary release](https://www.sc.com/en/press-release/standard-chartered-launches-rlusd-custody-and-joins-planned-collateral-integration-with-ripple-and-lmax-group/).
- **Coinbase / RLUSD:** Coinbase added RLUSD to retail and institutional platforms on 28 October, broadening its multi-issuer stablecoin distribution. Listing RLUSD does not prove XRP spot demand, XRP collateral utilization or XRPL payment volume. [Reuters](https://www.reuters.com/legal/transactional/coinbase-adds-ripples-stablecoin-its-exchange-2026-10-28/).
- **PNC / Coinbase / USDC:** the 9 November limited pilot allows eligible PNC clients to receive Circle USDC through Coinbase, automatically converted to USD. This is a competing USDC-to-bank-USD payment path that does not require XRP or XRPL. [Reuters](https://www.reuters.com/legal/transactional/pnc-offer-stablecoin-payments-clients-coinbase-partnership-2026-11-09/).
- Existing corporate-capital conclusions remain: Evernorth cash, in-kind XRP, debt, conditional ELOC capacity and secondary resales are distinct. The $214.05M cash-funded XRP purchase is not a second capital raise; the $30M PIK notes are debt; the ELOC had zero proceeds as of the prospectus; registered resales do not generate issuer proceeds. SBI Holdings ownership is separate from Japan's regional SBIC East/Central/West entities.

## 5. Prediction-engine status

### EXECUTED on integration

- 48 public source definitions: 43 hourly and three weekly CFTC endpoints; two non-commercial XRPL node endpoints excluded; 46 scheduled endpoints.
- Read-only scheduled ingestion workflow, guarded to main.
- Per-run SHA-256 receipts, local receipt chain and cross-run receipt-index continuity prototype.
- Point-in-time SQLite feature store and snapshot validator.
- Separate CFTC Legacy Futures-Only and TFF parsers.
- Event timeline, source-independence grouping and scenario/counter-hypothesis assembler.
- Four deterministic baselines: naive class prior, momentum sign, mean-reversion sign and Gaussian volatility-normal.
- Chronological walk-forward evaluation with purge/embargo and temporal temperature calibration.
- Univariate PSI feature-drift diagnostics.
- Fail-closed forecast ledger requiring independently trusted Ed25519 evaluator attestation.

### NOT IMPLEMENTED or NOT VERIFIED

- No trained XRP-specific candidate model exists. The walk-forward engine evaluates deterministic baselines; the forecast ledger records and scores externally supplied forecasts but does not train or generate them.
- No mature synchronized historical dataset spans spot, L2, derivatives, exchange flows, collateral and macro.
- The current event registry has 73 curated events, zero byte-exact raw publisher receipts for those curated events and zero model-eligible events.
- No independent WORM store or trusted timestamp authority. Raw receipt artifacts retain 90 days; per-run feature-store checkpoints seven days; daily archives 90 days.
- No paired block-bootstrap confidence intervals or source-clustered uncertainty for candidate-versus-baseline Brier/log-loss differences.
- The overlap-adjusted sample count does not remove residual serial dependence or shared-source correlation.
- PSI is univariate; multivariate and concept-drift monitoring are incomplete.
- No independent shadow cohort, production trusted evaluator key or measured candidate superiority over all four baselines.
- The scheduled ingestion workflow is not on main and has no verified main-branch run.

**Forecast: NOT_ISSUED. Accuracy: NOT_EVALUATED.** The legacy 45.5% variable-horizon result is invalid and must not be represented as predictive accuracy.

## 6. Nine-platform coordination

Status is **DESIGNED, NOT DISPATCHED**. No external-model task dispatch or external data transfer occurred.

| Platform | Verified state |
|---|---|
| ChatGPT | Current GitHub connection verified; connector has admin/maintain/push/pull/triage permissions and is overprivileged |
| Claude | Authentication and data flow unverified |
| Grok | Unverified |
| Gemini | Unverified |
| Copilot | Review artifacts exist; no formal approval on #1662 |
| Codex | Unverified |
| Hugging Face | Prior build error; no deployment |
| Kaggle | Untested; no submission |
| Databricks | Prior HTTP 403; no write |

LunaRoute remains separate, with authentication and data flow unverified.

## 7. Security and merge decision

**NO MERGE. PR #1662 remains draft.**

Main-versus-integration review confirms:
- Main's Barrot Sync is push-triggered, reads LunaRoute/GitHub secrets, suppresses sync failures and ignores push errors. The inspected `cut -c1-30` echo prints only the fixed label; no API-key disclosure was established by that line.
- Main's issue-label Barrot Agent has contents/pull-request/issues write permissions; integration quarantines it.
- Main's A2A deployment runs on pushes to `a2a/**` and uploads Cloudflare secrets; integration requires manual dispatch, exact main SHA and separate deployment/secret-rotation confirmations.
- Main's Barrot Operations can overwrite a Databricks workspace import or download a Kaggle dataset after one broad external-change confirmation; integration adds per-action confirmation and exact-source-SHA verification.
- Main's manual Coinbase paper-trader writes paper state/logs to main and pushes; integration makes it artifact-only and exact-SHA guarded. It was not run.
- Main `opencode.json` enables remote LunaRoute MCP and allows edit/bash/webfetch; integration disables remote MCP and requires approval for mutations.
- `xrp-public-ingestion.yml` exists only on integration. It is read-only and main-ref guarded; no main ingestion run is verified.
- Main's branch reports protected=true, but the required-status-check list is empty and enforcement is non-admin-only. Direct branch-protection details return HTTP 403. The visible fallback ruleset (10863829) is disabled. Integration is unprotected.
- The GitHub connector is overprivileged.
- A prior GitHub Pages deployment ran automatically after a main push. Current publication configuration was not rechecked in this run. PR #1662 changes seven public web files, so publication authorization remains unresolved.
- Semantic review of all 1,105 PR files and 50 changed workflow files is incomplete.

Passing exact-head CI does not resolve draft status, missing independent review, branch-protection uncertainty, overprivileged access, publication authorization or semantic-review blockers.

## 8. PR backlog classification

| PR | Classification and current evidence |
|---|---|
| #1662 | **Blocked** — active consolidated draft; zero reviews/approvals/threads |
| #1661 | **Supersession candidate** — 0 ahead/113 behind; all 1,072 changed paths overlap #1662 |
| #1660 | **Supersession candidate** — 0 ahead/294 behind; all 972 paths overlap |
| #1643 | **Supersession candidate** — 0 ahead/1,356 behind; all 670 paths overlap |
| #1642 | **Supersession candidate** — 0 ahead/2,261 behind; all seven paths overlap |
| #1640 | **Preserve** — one unique commit ahead; unique commit changes `barrot-ops.yml` and two safety tests; reconcile before any closure |
| #1653 | **Unique/unreviewed** — 18 commits ahead; six source-only paths |
| #1655 | **Unique/unreviewed** — 17 commits ahead; three source-only paths |
| #1659 | **Unique/unreviewed** — eight commits ahead; four source-only paths |
| #1615 | **Unique/unreviewed security** — three commits ahead; 13 source-only paths |
| #1614 | **Unique/unreviewed prediction work** — 36 commits ahead; 27 source-only paths |
| #1644–#1650 | **Blocked dependency candidates** — reconcile versions and workflow changes against current main |
| #1254–#1255 | **Blocked older dependency candidates** — deduplicate against newer dependency updates |
| #1320, #1318, #1317, #1269 | **Unique/unreviewed** — preserve for individual safety/structural review |
| Other drafts | **Unique/unreviewed until objective/path/commit search completes** |

No source PR was closed. Do not close supersession candidates until a successor is merged and its contents are verified on main. Do not bulk-close unique work.

## 9. Durable Run91D artifacts

- [Run91D current market, exact-head CI, repository and security audit](research/xrp_intelligence/20261113T133200Z-run91d-current-market-exact-head-ci-repository-security-audit.json)
- [Run91D nine-platform capability/authentication/permission/data-flow map](research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_run91d.json)
- [Consolidated PR #1662](https://github.com/Barrot-Agent/B-Agent/pull/1662)
- [Run91D code-bearing-head full CI](https://github.com/Barrot-Agent/B-Agent/actions/runs/43433988510)
- [Run91D dependency audit](https://github.com/Barrot-Agent/B-Agent/actions/runs/43433988513)
- [Run91D fail-closed gate](https://github.com/Barrot-Agent/B-Agent/actions/runs/43433988546)

## 10. Next concrete actions

1. Finish semantic reconciliation of the 1,105-file consolidated diff and all 50 workflow changes, including the unique #1640 safety commit.
2. Resolve connector least privilege and obtain verifiable required-check/approval branch-protection enforcement.
3. Complete direct deployment/MCP review and obtain explicit authorization for any public Pages changes.
4. Keep #1662 draft. Merge only after formal review, exact-head full suite, security gates, branch protection and publication authorization all pass.
5. After any authorized merge, verify merge commit, fetch main again, inspect workflow side effects, verify merged files and run main CI.
6. Establish externally anchored raw-source receipts and synchronized historical XRP data before training an XRP-specific candidate.
7. Add paired block-bootstrap/source-clustered uncertainty, multivariate/concept drift diagnostics and independent shadow outcomes before forecast admission.

No merge, main write, deployment, secret rotation, Space restart, external-model transfer, Databricks write, Kaggle submission, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or source PR closure occurred.
