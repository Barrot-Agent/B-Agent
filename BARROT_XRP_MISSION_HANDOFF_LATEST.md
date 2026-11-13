# Barrot XRP Intelligence Mission — Current Durable Handoff

**Run:** 97  
**Captured:** 2026-11-13T15:22:00Z  
**Mission priority:** XRP intelligence and measured prediction-engine mastery.  
**Protected foundation:** Barrot V3 execution, orchestration, safety and verification.  
**Main SHA:** `fb272b40966834754ec686f9ed3ab94123f09306`  
**Code-bearing integration head verified before Run97 evidence/test additions:** `f04b6adf4eb0e9a4800a0bbfe0a18e37a29b10a9`  
**Merged PRs in this run:** none.

## Current operational snapshot — Run97

### Repository and exact-head verification
- Main tree: 1,381 entries; integration tree: 2,362 entries; complete, not truncated.
- Integration ancestry: 2,264 commits ahead of main, zero behind.
- PR #1662: open, draft, mergeable; 1,119 changed files, 321,839 additions, 5,230 deletions and 50 changed workflow files.
- Open PR inventory: 375.
- Exact code-bearing head `f04b6adf4eb0e9a4800a0bbfe0a18e37a29b10a9`: full repository suite **3,566 passed**, 8 subtests, zero failures, 62.08% inclusive coverage, 93.55 seconds; core suite **732 passed**, 76% coverage; wheel build and installed V3/XRP mission verification passed.
- Five dependency groups passed with zero known vulnerabilities. Fail-closed gate passed but only keeps automatic merge disabled.
- [Full CI 43450175610](https://github.com/Barrot-Agent/B-Agent/actions/runs/43450175610) · [Dependency audit 43450175954](https://github.com/Barrot-Agent/B-Agent/actions/runs/43450175954) · [Fail-closed gate 43450175627](https://github.com/Barrot-Agent/B-Agent/actions/runs/43450175627).
- Run97 adds a research artifact and regression tests for x402 SourceTag/Verifiable Intent semantics. This commit's exact-head CI must pass before merge consideration.

### Prediction-engine reality
**Implemented:** 48 XRP source definitions, 46 scheduled definitions, read-only main-only ingestion, SHA-256 receipts/local chain, cross-run receipt-index continuity, point-in-time SQLite feature store, CFTC Legacy parser separate from TFF, event/source lineage, counter-hypotheses, four deterministic baselines, chronological walk-forward purge/embargo, calibration/PSI and Ed25519-gated forecast ledger.

**Not implemented/verified:** no trained XRP-specific candidate model; no synchronized mature spot/L2/derivatives/ETF/collateral history; no independent WORM/trusted timestamp anchor; no paired block-bootstrap/source-clustered uncertainty; no independent shadow cohort; no demonstrated OOS superiority over all four baselines.

The generic `barrot_agent/models.py` is IBM Granite vision-model management, not an XRP predictor. `walk_forward.py` evaluates deterministic baselines; the forecast ledger validates readiness reports rather than training a model. The 73-event registry has zero byte-exact raw publisher receipts for new web observations and zero model-eligible events.

**Forecast:** NOT_ISSUED. **Accuracy:** NOT_EVALUATED. The historical 45.5% variable-horizon value is invalid and is not accuracy evidence.

### XRP market and supply
- OKX XRP-USDT: $1.0344 last, provider event time 14:45:50.752 UTC; already 18m15s old at the 15:04:06 UTC market cutoff. Kraken XRP/USD $1.03262 had no provider event timestamp. Normalized asynchronous midpoint difference +0.0616%; not executable arbitrage and neither quote was model-eligible.
- No synchronized spot L2 admitted. A 07:23 UTC Binance perpetual depth snapshot is historical single-venue context only.
- Derivatives vendors reported $303.6M–$613.07M OI across different contract universes; do not average. Long-account concentration and long-skewed liquidations support a crowded-long/deleveraging hypothesis, not a directional forecast.
- XRP Insights attributed 22.26B XRP to 707 wallets across 24 exchanges; same-wallet change -77.3M XRP/7d and -279.7M/30d. Wallet attribution is not tradable float; Coinbase cbXRP and Binance-Peg reserves are separate.
- ETF correction: XRP Insights metadata generated 2026-11-13 14:18:56 UTC shows data_as_of Nov12, four settled trading days, `provisional_row_date=null`, and -9,481,905 XRP for Nov9–12. This is holdings-derived, not issuer flow reports; GXRP flow is withheld and BITW rebalancing/fees can affect the metric. CryptoKeyhole's latest complete daily result remains Nov11 at -3,322 XRP with Nov12 issuer files missing; Alpha Finance reports $0 Nov12 and -$2.8M over 30 sessions. Different cohorts and source lineage; do not average.
- Latest CFTC Legacy Futures-Only XRP report remains Nov3: 7,216 contracts/360.8M XRP-equivalent; non-commercial net long 1,465, with shorts falling faster than longs. Next listed release Nov16.
- Ripple-owned escrow at ledger 108,304,969: 31.1B XRP in 99 objects across eight accounts; next 1B release becomes unlockable Dec1 2026 00:00 UTC in four objects. Ripple re-escrowed 70% over the last 12 releases; net 300M XRP/month left escrow. Unlock is not guaranteed sale or exchange inflow.
- RLUSD XRPL/Ethereum supply and AMM observations remain separate from issuer reserve attestations and XRP spot liquidity.

### Agentic payments and Mastercard — new Run97 finding
- T54's public XRPL AI Hub reports 15,694,282 all-time x402 transactions and $78,306.59 settled value, or about **$0.00499 per transaction**, with 193 merchants and 5,410 live services.
- XRP Insights reports 15,679,858 transactions, 7,031 XRP and 69,061 RLUSD settled, 191 attributed active agents, 193 merchants and 5,882 endpoints. It is a downstream T54-related aggregator, not independent confirmation. Preserve the 14,424 transaction-count difference and the different service/endpoint definitions; do not average.
- Critical attribution correction: XRPLF documentation says x402 SourceTag is merchant-chosen endpoint attribution, **not agent identity**. T54's default 804681468 therefore cannot identify the paying agent. Agent attribution requires payer-account and/or Verifiable Intent evidence.
- T54's transaction list labels the **Intent** field `Unverified`. T54 documentation makes Verifiable Intent optional; an ordinary x402 payment can still work without the L1–L3 chain. Do not interpret this label as an XRPL ledger failure or confirmation result. A sampled transaction hash/ledger index was not independently checked against XRPL in this run.
- Mastercard's June 10 Agent Pay for Machines partner list includes T54 Labs and RippleX, alongside Coinbase and others. This is program-level co-participation, not proof of a bilateral XRP settlement agreement or XRP-denominated Mastercard flows.
- x402 supports XRP and RLUSD on XRPL. RLUSD microtransactions are not native XRP demand. Keep these counters event-timeline-only, not price features, capital flows or verified agent counts.
- Regression tests were added to preserve SourceTag semantics, intent-status semantics, source dependence, micro-ticket scale and fail-closed model admission.

### Institutional, capital and regulation
- Coinbase distributes USDC and RLUSD. Coinbase's Q3 2026 filing reports large aggregate crypto/stablecoin collateral balances, but no XRP-specific collateral amount; other crypto assets are aggregated. Do not infer XRP collateral from the aggregate.
- Coinbase's RLUSD launch described Global Exchange collateral support as forthcoming, not live. PNC/Coinbase corporate-payment pilot uses USDC on Ethereum and converts to USD, not XRP.
- Circle USDC on XRPL and Circle Arc are distinct; Arc is a separate Layer 1. SBI's Circle investment/JV coexists with its Ripple stake/SBI Ripple Asia relationship: multi-rail strategy, not exclusivity.
- BNY is RLUSD's primary reserve custodian and supports XRP/RLUSD custody; direct mint/redeem and tokenized trade-finance uses remain planned/exploratory.
- Evernorth SEC filing: $272.6M gross cash, 388.91M XRP in kind, $214.05M cash used to buy 84.3659M XRP, $30M PIK debt, 5,218,935-share ELOC capacity with zero proceeds as of Nov9. The approximately $80.7M ELOC headline is conditional capacity, not received cash.
- EBA began dual supervision of USDC as the EU's first significant e-money token under MiCA on Nov12; EU issuer Circle Internet Financial Europe SAS is distinct from US issuer Circle Internet Financial LLC.

### Identity and exact phrases
- SBIC East/Central/West are Tokyo/Nagoya/Osaka regional SME investment/development companies, distinct from SBI Holdings. SBIC East's ChatGPT training is educational, not a commercial OpenAI partnership.
- ASK Coin at askcoin.net is an inactive/untracked exchange listing; Permission Coin (ASK) is a separate Polygon/Base token. No canonical XRPL ASK issuer/deployment verified.
- `actual capital`: Evernorth cash, in-kind XRP, debt, conditional ELOC and secondary resales remain separate; ELOC proceeds were zero as of Nov9.
- One verified Kamilah Stevenson public YouTube appearance: [Thinking Your Way Into Health — Kamilah Stevenson, TEDx Talks](https://www.youtube.com/watch?v=VSgeDgOCexs), published 2018-05-18. TEDx description names her and links to kamilahstevenson.com. It is a guest appearance, not own-channel upload. Candidate handles remain unverified; verified own-channel inventory remains zero.

### Nine-platform coordination
ChatGPT GitHub authentication works but connector permissions are admin/maintain/push/pull/triage and overprivileged. Copilot review artifacts exist on #1653 but no formal approval on #1662. Claude, Grok, Gemini and Codex remain unverified; Hugging Face has prior BUILD_ERROR/no deployment; Kaggle untested/no submission; Databricks previously HTTP 403/no write. LunaRoute authentication/data flow unverified. No external-model dispatch or data transfer occurred.

### Security and merge decision
- All 50 changed workflow files were screened for triggers, permissions, secrets, external calls, branch writes and deployment side effects.
- Main retains push-triggered Barrot Sync, issue-label Barrot Agent write automation, push-triggered A2A deployment/secret upload, push-triggered self-hosted Space deployment, and manual Databricks/Hugging Face mutation workflows. Integration quarantines or gates these paths.
- Main OpenCode enables remote LunaRoute MCP and write-capable permissions; integration disables remote MCP and requires approval for mutations.
- XRP ingestion is read-only and main-only; it uses GitHub Actions artifacts/cache (raw/index 90 days, per-run feature checkpoint 7 days, daily feature archive 90 days), not independent WORM storage. It has not run on main because integration is unmerged.
- GitHub Pages previously deployed automatically after a main push; seven public web files change in #1662. Publication authorization remains unresolved.
- Main branch-protection details return HTTP 403; fallback ruleset 10863829 is disabled; integration is unprotected. GitHub connector is overprivileged.
- PR #1662 remains draft with zero formal reviews, approvals and review threads.

### PR backlog
- #1661, #1660, #1643, #1642: zero commits ahead of integration and all changed paths overlap; supersession candidates, close only after #1662 is safely merged and verified.
- #1640: one stale/weaker source commit is superseded by stricter integration behavior; preserve until successor merge.
- #1653: 18 ahead/17 behind, six unique paths, six high-severity Copilot findings and eight unresolved review threads; blocked, preserve.
- #1655: 17 ahead/17 behind, three unique paths; preserve.
- #1659: 8 ahead/17 behind, four unique paths; preserve.
- #1614: 36 ahead/58 behind, 27 unique paths including `research_artifact_clock.py`; preserve.
- #1615: 3 ahead/58 behind, 13 unique paths covering scheduled-writer containment and brain-corpus export; preserve.
- Dependency candidates #1644–#1650 and #1254/#1255 remain blocked pending current-main validation. #1320, #1318, #1317 and #1269 remain unique/unreviewed.
- No source PR was closed.

### Merge decision and next action
**NO MERGE.** PR #1662 remains draft; approvals are absent; semantic review of 1,119 files is incomplete; branch-protection enforcement is not verifiable; connector permissions are overprivileged; Pages publication authorization is unresolved.

Next: verify exact-head CI for the Run97 evidence/test commit; complete semantic reconciliation and least-privilege/publication controls on the existing PR; preserve unique source PR work; establish external WORM/timestamp anchoring and synchronized historical XRP data; then build the XRP-specific candidate model and evaluate it against all four baselines with source-clustered block-bootstrap uncertainty and independent shadow outcomes. Keep forecasts disabled until the complete admission gate passes.

No merge, deployment, secret rotation, Space restart, external-model transfer, Databricks write, Kaggle submission, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or source PR closure occurred.

## Historical run archive

## Run93 14:03 UTC operational snapshot — historical

- Main SHA: `fb272b40966834754ec686f9ed3ab94123f09306`; unchanged.
- Integration head: `dd4d0ed3cec0428ebb15a6c81150d048dd112693`, 2,254 commits ahead and zero behind main. Recursive trees: main 1,381 entries; integration 2,353 entries; neither truncated.
- PR #1662: open, draft, mergeable; 1,108 changed files, 317,429 additions, 5,136 deletions; 50 workflow files changed; zero formal reviews, approvals or review threads. Open PR inventory: 375 (361 drafts, 14 non-drafts; 367 target main, eight target other branches).
- Exact current-head verification: **3,558 passed, zero failed, eight subtests; 61.72% inclusive coverage; 93.50 seconds.** Core suite: 730 passed, eight subtests, 76% coverage. Wheel and packaged mission checks passed. Five dependency manifest groups passed; zero known vulnerabilities reported. Fail-closed gate passed; automatic merge disabled.
- Exact-head evidence: [Full CI 43438388063](https://github.com/Barrot-Agent/B-Agent/actions/runs/43438388063), [dependency audit 43438387916](https://github.com/Barrot-Agent/B-Agent/actions/runs/43438387916), [fail-closed gate 43438387812](https://github.com/Barrot-Agent/B-Agent/actions/runs/43438387812).
- Main's last full repository CI on unchanged SHA passed 747 tests and eight subtests. A separate scheduled external-health check failed because GitHub App credentials were missing, Databricks returned HTTP 403, and the Hugging Face Space reported BUILD_ERROR. This is not the repository test suite. Main's scheduled Cross Analysis succeeded.
- Current spot/derivatives observations were stale or unsynchronized; ETF trackers had partial files and different cohorts. No observations were admitted to the feature store. The new Run93 market artifact preserves event times and source disagreement.
- Prediction status: no XRP-specific candidate model is implemented or trained; current walk-forward evaluation covers four deterministic baselines only. The event registry remains 73 curated events, with zero byte-exact raw publisher hashes and zero model-eligible events. Forecast **NOT_ISSUED**; accuracy **NOT_EVALUATED**.
- Security: main is marked protected but has no required status contexts/checks; direct protection detail returns HTTP 403 and fallback ruleset 10863829 is disabled. Integration is unprotected. GitHub connector permissions include admin, maintain, push, pull and triage. Pages publication authorization remains unresolved.
- **Merge decision: NO MERGE.** PR #1662 remains draft with zero approvals. Semantic review, least privilege, branch-protection visibility and Pages publication authorization remain blockers.

## Run91D historical archive — repository and integration state

- Repository: [Barrot-Agent/B-Agent](https://github.com/Barrot-Agent/B-Agent)
- Current main SHA at audit: `fb272b40966834754ec686f9ed3ab94123f09306`
- Code-bearing integration head audited: `c6d6dab969df061ed09fd337a869af55b69e1863`
- Branch: `integration/xrp-v3-unified-main-20261112`
- Consolidated integration: [PR #1662](https://github.com/Barrot-Agent/B-Agent/pull/1662)
- PR state at audit: open, draft, mergeable, 2,245 commits ahead and zero behind main; 1,105 changed files; 316,273 additions; 5,136 deletions; zero formal reviews, approvals or review threads.
- Recursive tree: main 1,381 entries; integration 2,351 entries; 88 integration workflow files. The recursive tree includes directory objects. The PR's 1,105-file count reconciles to 1,104 changed/added blob paths plus the mode-only `b_agent.sh` change (100755 on main to 100644 on integration, same blob SHA).
- Open PR inventory: 375 total, 361 drafts and 14 non-drafts.
- The current Run91D artifact and platform map were committed as documentation/research-only descendants after the code-bearing head. The handoff update itself is another documentation-only descendant. Their exact-head CI is pending at the moment this handoff is written; predecessor CI must not be represented as verification of those later SHAs.

## Run91D historical archive — exact-head software verification

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

## Run91D historical archive — XRP market research — 13 November 2026

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

## Run91D historical archive — macro and cross-asset liquidity context

- Glassnode's 11 November Week 45 report says major stablecoin supply contracted by $14.2B over 30 days through 9 November, the largest contraction since June 2022. It also reports approximately $1.6B in US spot Bitcoin ETF net outflows over 20 sessions and a Coinbase spot discount. Counter-evidence in the same report: leverage had been flushed, bids outweighed asks in the Bitcoin order book, and two large BTC wallet cohorts began accumulating. These are broad crypto/BTC measures, not XRP-specific observations.
- The US BLS October PPI release on 13 November at 08:30 ET reported final demand +0.3% month over month and +6.5% year over year; final demand excluding food, energy and trade services +0.5% month over month and +4.9% year over year. Higher producer-price inflation can reinforce restrictive-rate expectations, but is not an XRP-specific causal signal.
- Reuters reported the dollar was on track for its strongest week in about two months, the US two-year yield near 4.86%, a roughly 12% market-implied chance of a 50-basis-point December Fed hike, and USD/JPY near 159.99. China also conducted large unannounced Pacific drills, with around 70 vessels still active Friday. These are macro/geopolitical risk context, not evidence of an XRP-specific catalyst.

Competing hypotheses:
1. **Risk-off:** XRP ETF holdings-derived outflows, shrinking broad stablecoin supply, hawkish-rate repricing, dollar strength and long-skewed XRP liquidations can jointly pressure risk appetite.
2. **Stabilization:** leverage flushing, BTC large-wallet accumulation and bid-side BTC depth can support a broader-market stabilization hypothesis. Those are BTC observations, not proof of XRP buying. XRP funding remains positive in the latest Liqwall aggregate and OI is down less than 1% over 24 hours, so a full XRP deleveraging conclusion is premature.
3. **Institutional adoption:** RLUSD custody and payment rails can expand XRPL stablecoin use without requiring incremental XRP demand. PNC/Coinbase uses USDC converted to USD; Standard Chartered/LMAX's planned collateral is RLUSD, not native XRP.

Sources: [Glassnode Week 45](https://research.glassnode.com/the-week-onchain-week-45-2026/), [BLS October 2026 PPI](https://www.bls.gov/news.release/ppi.nr0.htm), [Reuters dollar/yields/yen](https://www.reuters.com/world/africa/dollar-near-19-month-high-fed-hike-bets-yen-tests-160-2026-11-13/), [Reuters China drills](https://www.reuters.com/world/china/china-stages-unannounced-pacific-drills-silent-intimidation-taiwan-officials-say-2026-11-13/).

## Run91D historical archive — institutional, stablecoin and regulatory evidence

- **USDC / EBA:** EBA classified USDC, issued in the EU by Circle Internet Financial Europe SAS, as the EU's first significant e-money token on 14 October 2026; dual supervision took effect 12 November. EBA directly supervises own funds, reserve assets, liquidity and recovery/redemption plans. ACPR retains governance, qualifying holdings, fit-and-proper, outsourcing and conflicts oversight. The EU issuer is distinct from US issuer Circle Internet Financial LLC. This is a significant USDC regulatory milestone and a competing dollar rail, not evidence of XRP demand. [EBA primary release](https://www.eba.europa.eu/publications-and-media/press-releases/eba-classifies-usdc-first-significant-e-money-token-european-union).
- **Standard Chartered / RLUSD:** Standard Chartered says institutional custody for RLUSD issued on XRPL is live through its DFSA-regulated DIFC branch. The LMAX collateral-mirroring arrangement is planned and remains subject to final documentation, testing, law/regulation, internal approvals and jurisdictional readiness. RLUSD custody or RLUSD collateral is not native XRP collateral or evidence of XRP purchases. [Standard Chartered primary release](https://www.sc.com/en/press-release/standard-chartered-launches-rlusd-custody-and-joins-planned-collateral-integration-with-ripple-and-lmax-group/).
- **Coinbase / RLUSD:** Coinbase added RLUSD to retail and institutional platforms on 28 October, broadening its multi-issuer stablecoin distribution. Listing RLUSD does not prove XRP spot demand, XRP collateral utilization or XRPL payment volume. [Reuters](https://www.reuters.com/legal/transactional/coinbase-adds-ripples-stablecoin-its-exchange-2026-10-28/).
- **PNC / Coinbase / USDC:** the 9 November limited pilot allows eligible PNC clients to receive Circle USDC through Coinbase, automatically converted to USD. This is a competing USDC-to-bank-USD payment path that does not require XRP or XRPL. [Reuters](https://www.reuters.com/legal/transactional/pnc-offer-stablecoin-payments-clients-coinbase-partnership-2026-11-09/).
- Existing corporate-capital conclusions remain: Evernorth cash, in-kind XRP, debt, conditional ELOC capacity and secondary resales are distinct. The $214.05M cash-funded XRP purchase is not a second capital raise; the $30M PIK notes are debt; the ELOC had zero proceeds as of the November 9 prospectus; registered resales do not generate issuer proceeds. Secondary $80.7M ELOC headlines describe conditional capacity, not actual cash received.

## Run91D historical archive — XRPL credit, lending and collateral

The official XRPL institutional-credit documentation describes the base Lending Protocol as **uncollateralized fixed-term loans**. Single Asset Vaults pool lender assets and can hold XRP, trust-line tokens such as RLUSD, or MPTs. Vault deposits are lender-pool funding, not borrower collateral. The documentation says collateralized loans can be built with additional logic such as on-chain custodians; that is not the base XLS-66 primitive. The use case requires both `LendingProtocol` and `LendingProtocolV1_1`.

The official Known Amendments page labels Credit/Lending as open for voting, but its dynamic mainnet status widget did not render during this retrieval. The repository's last vote snapshot is dated November 8 and is not a current November 13 RPC observation. **Current supermajority and activation status remain unverified.** Do not describe native XRPL LendingProtocol as a live XRP-collateralized market, and do not infer XRP collateral demand from Single Asset Vault deposits.

Sources: [XRPL institutional credit facilities](https://xrpl.org/docs/use-cases/defi/institutional-credit-facilities), [XRPL known amendments](https://xrpl.org/resources/known-amendments).

## Run91D historical archive — Japan SBIC identity and ChatGPT exact-phrase research

The three regional SME investment-development companies are separate from SBI Holdings:
- **East / Tokyo:** the official February 26, 2025 PDF advertises a ChatGPT/generative-AI seminar. The speaker is a Microsoft Japan executive; Tokyo Chamber of Commerce Taito branch is co-host. The November 16, 2026 Tokyo SBIC event is another generative-AI seminar led by a Microsoft Japan evangelist, including AI-agent applications. Neither page establishes an OpenAI commercial partnership.
- **Central / Nagoya:** the official June 2, 2026 notice describes a July 31 investee-only salon where executives share practical generative-AI adoption experiences. It is not ChatGPT-specific.
- **West / Osaka:** the official October 23, 2024 Investment Forum PDF advertises a ChatGPT introductory seminar taught by STORIA law-firm partner Taichi Kakinuma, with in-person and Zoom participation. It does not identify OpenAI as a partner.

These are educational and investee-support activities, not an OpenAI ownership, licensing, commercial or data-sharing relationship. They do not connect the three SBIC companies to SBI Holdings.

Primary sources: [Tokyo SBIC 2025 ChatGPT seminar](https://www.sbic.co.jp/wordpress/file/20250226_%E7%94%9F%E6%88%90AI%E3%81%AE%E7%8F%BE%E5%9C%A8%E3%81%A8%E6%9C%AA%E6%9D%A5%E3%80%90%E6%8A%95%E8%B3%87%E8%82%B2%E6%88%90%E8%AA%AC%E6%98%8E%E3%81%82%E3%82%8A%E3%80%91.pdf), [Tokyo SBIC November 16, 2026 event](https://www.sbic.co.jp/seminar/20261116/), [Nagoya SBIC generative-AI salon](https://www.sbic-cj.co.jp/news/5077/), [Osaka SBIC 2024 ChatGPT seminar](https://www.sbic-wj.co.jp/wp/wp-content/uploads/2024/07/TF128.pdf).

Exact-phrase dispositions:
- **ASK Coin:** no canonical XRPL issuer or deployment verified; unrelated ASK tokens/listings remain separate.
- **“actual capital”:** SEC filing controls over secondary headlines. The ELOC's approximately $80.7M headline value is conditional capacity; the filing reports zero ELOC proceeds as of November 9.
- **“SBIC, ChatGPT SBIC”:** primary materials show seminars and business education, not an OpenAI partnership.
- **Camilla/Kamilah Stevenson YouTube:** first-party identity material supports Dr. Kamilah Stevenson, but no first-party cross-reference proves ownership of candidate YouTube channels. Verified own-channel video inventory remains zero; guest appearances and similar names are not attributed.

## Run91D historical archive — prediction-engine status

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

## Run91D historical archive — nine-platform coordination

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

## Run91D historical archive — security and merge decision

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

## Run91D historical archive — PR backlog classification

| PR | Classification and current evidence |
|---|---|
| #1662 | **Blocked** — active consolidated draft; zero reviews/approvals/threads |
| #1661 | **Supersession candidate** — 0 ahead/113 behind; all 1,072 changed paths overlap #1662 |
| #1660 | **Supersession candidate** — 0 ahead/294 behind; all 972 paths overlap |
| #1643 | **Supersession candidate** — 0 ahead/1,356 behind; all 670 paths overlap |
| #1642 | **Supersession candidate** — 0 ahead/2,261 behind; all seven paths overlap |
| #1640 | **Supersession candidate** — its one unique commit's three-file action-specific approval objective is already present in #1662; integration has the same safety tests and stricter fail-closed credential/import behavior. Keep open until #1662 is merged and verified on main |
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

## Run91D historical archive — durable artifacts

- [Run91D current market, exact-head CI, repository and security audit](research/xrp_intelligence/20261113T133200Z-run91d-current-market-exact-head-ci-repository-security-audit.json)
- [Run91D nine-platform capability/authentication/permission/data-flow map](research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_run91d.json)
- [Consolidated PR #1662](https://github.com/Barrot-Agent/B-Agent/pull/1662)
- [Run91D code-bearing-head full CI](https://github.com/Barrot-Agent/B-Agent/actions/runs/43433988510)
- [Run91D dependency audit](https://github.com/Barrot-Agent/B-Agent/actions/runs/43433988513)
- [Run91D fail-closed gate](https://github.com/Barrot-Agent/B-Agent/actions/runs/43433988546)

## Run91D historical archive — next concrete actions

1. Finish semantic reconciliation of the 1,105-file consolidated diff and all 50 workflow changes, including the unique #1640 safety commit.
2. Resolve connector least privilege and obtain verifiable required-check/approval branch-protection enforcement.
3. Complete direct deployment/MCP review and obtain explicit authorization for any public Pages changes.
4. Keep #1662 draft. Merge only after formal review, exact-head full suite, security gates, branch protection and publication authorization all pass.
5. After any authorized merge, verify merge commit, fetch main again, inspect workflow side effects, verify merged files and run main CI.
6. Establish externally anchored raw-source receipts and synchronized historical XRP data before training an XRP-specific candidate.
7. Add paired block-bootstrap/source-clustered uncertainty, multivariate/concept drift diagnostics and independent shadow outcomes before forecast admission.

No merge, main write, deployment, secret rotation, Space restart, external-model transfer, Databricks write, Kaggle submission, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or source PR closure occurred.


## Run92 archive — 2026-11-13T13:58:22.802Z — actual capital, stablecoin rails, x402, ASK and institutional network reconciliation

### Repository and exact-head verification — VERIFIED

- Main SHA: `fb272b40966834754ec686f9ed3ab94123f09306`; main remains unchanged.
- Integration branch at capture: `integration/xrp-v3-unified-main-20261112`; head `fbb7c1fd8dd18b2763fa19dc810e3d752d7d60b8`; 2,253 commits ahead, zero behind; 1,108 changed files, 317,337 additions and 5,136 deletions.
- PR #1662 remains open, draft and mergeable. No formal approvals or review threads. It is not merge-ready.
- Open PR inventory last fully paged: 375 total; 361 drafts, 14 non-drafts; 367 target main and eight target other branches.
- Current integration tree is complete (2,353 entries); main tree is complete (1,381 entries).
- Latest commit `fbb7c1f` adds a read-only regression test for cross-analysis workflow outputs; it does not add a new runtime capability.
- [Full CI 43437656753](https://github.com/Barrot-Agent/B-Agent/actions/runs/43437656753), job 131926809011: **3,558 passed, zero failed, eight subtests**, 61.72% inclusive coverage in 61.27 seconds. Core job 131926808592: **730 passed, eight subtests**, 76% coverage. Wheel build and installed Barrot V3/XRP mission verification passed.
- [Dependency audit 43437656668](https://github.com/Barrot-Agent/B-Agent/actions/runs/43437656668): all five manifest groups passed; no known vulnerabilities reported.
- [Fail-closed gate 43437656718](https://github.com/Barrot-Agent/B-Agent/actions/runs/43437656718) and push gate 43437647463 passed. Automatic merge remains disabled.
- The Run92 handoff update itself is documentation-only and will require its own exact-head CI/audit/gate. No main change or merge occurred.

### Actual capital and XRP treasury — PRIMARY SEC EVIDENCE

Source: [Evernorth 424B3 prospectus, filed Oct 30, 2026](https://www.sec.gov/Archives/edgar/data/2092592/000162828026068590/evernorth-424b3.htm).

- Evernorth reported approximately **473 million XRP held at the Oct 9, 2026 business-combination closing**.
- Closing gross cash proceeds were approximately **$272.6 million**: $224.6 million from private-placement subscriptions plus $48.0 million remaining in the trust account after redemptions, before transaction expenses.
- The company reported **388,910,554 XRP contributed in kind**. These are real asset contributions but are not market purchases.
- The filing separately documents **84,365,876 XRP purchased with $214.05 million cash** from the advance funding, with receipts completed by Nov 6, 2025. The implied gross cash cost is approximately **$2.5366/XRP**. This is a historical purchase, not a Nov 2026 flow.
- The purchased 84.366 million XRP plus 388.911 million XRP contributed in kind reconcile to approximately 473.276 million XRP, consistent with the rounded 473 million closing holding.
- In-kind components include 211,319,096 XRP from the Arrington Sponsor Series C contribution, 126,791,458 XRP from Ripple, 50,000,000 XRP from the Larsen Lam Children's Remainder Trust, plus 600,000 XRP from advance subscribers and 200,000 XRP from delayed subscribers. Do not count these as market buys.
- The $30 million 4% PIK notes produced net proceeds received Oct 12, 2026. They are debt, with general corporate purposes including possible XRP acquisitions; the filing does not prove those proceeds were subsequently used to buy XRP.
- The Ripple-related revolving facility is debt, not equity capital. The prospectus describes a $7 million facility increased to $10 million, with $9.7 million drawn as of Oct 7, 2026.
- The Cantor equity line permits up to 5,218,935 new shares, generally at 97% of VWAP. The prospectus reference-price scenario estimates up to approximately $76.8 million gross. It is conditional financing, not cash already raised; no draw was verified in the filings reviewed through this capture.
- Up to 11,499,992 public warrants at $11.50 could produce approximately $132.25 million only if exercised for cash. No exercise of the full amount was established.
- The filing identifies four SBI-controlled Evernorth investors and reports 9,431,914 Class A shares held by SBI affiliates, plus Class C shares issued under the 39.9% ownership arrangement. It does **not** allocate the aggregate $214.05 million advance cash or XRP subscriptions to each SBI entity. Do not attribute all advance funding to SBI.
- Capital categories remain separate: cash proceeds, in-kind XRP, market XRP purchases, debt, related-party credit, conditional equity facilities, warrants and secondary resales.

### Coinbase, Circle, Ripple, SBI and the multi-rail network

**SBI ↔ Circle**
- SBI Holdings and SBI Shinsei Bank invested **$25 million each** in Circle's IPO, a $50 million combined equity investment. [SBI disclosure](https://www.sbigroup.co.jp/english/news/pdf/2025/0609_a_en.pdf).
- SBI and Circle established the SBI Circle Holdings joint venture and SBI VC Trade distributed USDC in Japan. [SBI joint-venture disclosure](https://www.sbigroup.co.jp/english/news/pdf/2025/0822_c_en.pdf).
- Circle identifies SBI Group as a founding validator of Arc. Arc uses USDC for gas and is a competing stablecoin-native payment/agentic rail; this is not an XRP deployment. [Circle Arc launch](https://www.circle.com/pressroom/circle-launches-arc-public-testnet).
- SBI therefore has a direct Circle/USDC relationship as well as its separate Ripple relationship.

**SBI ↔ Ripple**
- SBI's 2025 disclosure described SBI Group as holding approximately 9% of Ripple and as its largest external shareholder at that time; the percentage is dated, not a verified Nov 2026 cap-table figure. [SBI disclosure](https://www.sbigroup.co.jp/english/news/pdf/2025/0609_a_en.pdf).
- SBI Ripple Asia is a separate joint venture.
- SBI VC Trade launched RLUSD in Japan on June 24, 2026. [Ripple announcement](https://ripple.com/ripple-press/ripple-and-sbi-group-partner-to-launch-ripple-usd-in-japan/).
- SBI is multi-rail, not exclusively aligned to Ripple: it distributes USDC, participates in Circle's Arc and distributes RLUSD.

**Coinbase ↔ Circle**
- Circle's H1 2026 SEC 10-Q reports $655.3 million in distribution costs to Coinbase. Coinbase held $12.442 billion USDC on platform at June 30, 2026; its daily weighted-average share of USDC on platforms was 18.3% for H1 2026. This is direct distribution/revenue-sharing economics, not XRP activity. [Circle Q2 2026 10-Q](https://www.sec.gov/Archives/edgar/data/1876042/000187604226000248/crcl-20260630.htm).
- Circle's USDC has been natively available on XRPL since June 12, 2025. [Circle announcement](https://www.circle.com/blog/usdc-is-coming-to-the-xrp-ledger).

**Coinbase x402 ↔ t54 ↔ XRPL**
- Coinbase introduced x402 as an open HTTP 402 payment protocol. [Coinbase x402](https://www.coinbase.com/en-in/developer-platform/discover/launches/x402).
- XRPL's official documentation describes the XRPL x402 implementation as contributed by t54, with t54 hosting the facilitator. It can settle in XRP or supported stablecoins; this is a t54 implementation of an open Coinbase-originated protocol, not proof of a direct Coinbase-Ripple commercial agreement. [XRPL x402 documentation](https://xrpl.org/es-es/docs/agents/agentic-payments-x402).
- Ripple participated strategically in t54's $5 million seed round; the amount of Ripple's participation was not disclosed. [t54 funding announcement](https://www.t54.ai/blog/t54-labs-raises-5m-seed-round).
- Mastercard's Agent Pay for Machines initial participants include Coinbase, RippleX and t54. The program is multi-rail; the partner list does not establish XRP-specific settlement. [Mastercard announcement](https://investor.mastercard.com/investor-news/investor-news-details/2026/Mastercard-Launches-Agent-Pay-for-Machines-to-Unlock-Super-Fast-Always-On-Payments/default.aspx).
- t54's announced Evernorth collaboration is an intended integration, not proof of a production autonomous treasury deployment. [t54/Evernorth announcement](https://www.t54.ai/blog/t54-announces-strategic-collaboration-with-evernorth).

### Stablecoin and agentic-payment disconfirming evidence

- Ripple's transparency dashboard displays $2.6329 billion total circulating RLUSD and $2.748 billion reserve funds as of Nov 5, 2026. The latest linked independent CPA report is for Sep 21/Sep 30, not Nov 5, and covers multiple approved networks. [Ripple transparency](https://ripple.com/products/stablecoin/transparency/) · [September CPA report](https://cdn.sanity.io/files/ior4a5y3/production/850ed07e8f0556b3b1c1d43eb2a0fc4ef6538ce1.pdf/RLUSD%20Attestation%20Report%20(Sep)_Final%20Signed.pdf).
- Secondary XRPL dashboards disagree on XRPL-only RLUSD: XRP Insights' prior snapshot was approximately 818.6–829.3 million, while xrpl.fi's current index shows approximately $1.1 billion; Ripple's Nov 5 figure is all-chain. These have different capture times and methodologies. No common-ledger direct issuer-account reconciliation was performed; do not average them.
- xrpl.fi's current ledger index lists approximately $4.6 million USDC on XRPL. This supports native Circle USDC presence on XRPL but does not establish meaningful XRP demand.
- Circle says USDC represented 98.8% of agent-driven transaction volume since its Agent Stack launch, with most x402 activity settling in USDC. This is issuer-reported and should be tested independently, but it is material disconfirming evidence against assuming agentic-payment growth automatically accrues to XRP.
- XRP Radar reports 15.68 million x402 transactions and all-time settlement of 7,031 XRP plus 69,061 RLUSD. xrpl.fi's narrower t54 facilitator fingerprint and operator-reported cumulative count do not reconcile to that figure. The XRPL documentation states SourceTag is merchant-selected and identifies the endpoint, not the paying agent. Counts based on SourceTag are not verified agent identities or capital flows.
- XRP Radar's 22.26 billion XRP across 24 labeled exchange-wallet groups includes pooled customer deposits, cold storage and some wrapped-token backing. It is not tradable float or executable sell inventory.

### ASK Coin and exact-phrase disambiguation

- The strongest exact-phrase candidate is **Permission Coin (ASK)**. Permission's own documentation lists a LayerZero OFT token with 100 billion fixed supply and official contracts on Base and Polygon: Base `0xBB146326778227A8498b105a18f84E0987A684b4`; Polygon `0xaA3717090CDDc9B227e49d0D84a28aC0a996e6Ff`. No XRPL deployment appears in its official contract list. [Official ASK contracts](https://docs.permission.ai/ask-token/contract-addresses) · [ASK token description](https://docs.permission.ai/ask-token).
- The older 2025 Base contract is superseded by the current official Base OFT address. Do not use the old address for any integration.
- AskSurf is an x402 merchant label, not Permission Coin. Prmission is a separate USDC/x402 service, not the ASK token.
- SBIC East/Central/West identities and the distinction from SBI Holdings remain as recorded in the preceding handoff section. Official SBIC generative-AI/ChatGPT seminars do not establish an OpenAI commercial partnership.
- One TEDx Talks video is verified for Kamilah Stevenson: [Thinking Your Way Into Health — TEDxWillowCreek](https://www.youtube.com/watch?v=VSgeDgOCexs). Personal-channel ownership and other candidate videos remain unverified.

### Provenance, independence and model admission

- Primary sources: SEC prospectus/10-Q, official SBI/Ripple/Circle/Coinbase/Mastercard/t54/XRPL/Permission/SBIC documents.
- Secondary sources: XRP Insights, CryptoKeyhole, Alpha Finance, XRP Radar and xrpl.fi. ETF trackers share issuer-file inputs; on-chain dashboards share XRPL ledger and wallet-label dependencies. They are not independent confirmations merely because they are separate websites.
- This run used public web-rendered pages and SEC documents. Publisher response bytes were not persisted into Barrot RawReceiptArchive; no SHA-256 receipts were created in this run. These findings are **RESEARCH_ONLY**, not point-in-time feature-store admissions.
- The Bybit public API retrieval attempt through the web layer returned 403/inaccessible responses. This is not evidence of a Bybit outage. The Bybit adapter remains mock-tested only; live exchange execution was not verified.
- Forecast: **NOT_ISSUED**. Candidate model: not trained. Accuracy: not evaluated. No directional claim is supported by this research alone.

### V3 safety and next actions

- Keep #1662 draft. Current exact-head CI/audit/gate pass does not resolve zero approvals, incomplete semantic review, branch-protection visibility, Pages publication authorization or direct MCP approval gaps.
- Main `opencode.json` still allows remote LunaRoute MCP and edit/bash/webfetch; the integration version disables remote MCP and asks before mutations. No LunaRoute authentication/data flow has been tested.
- `MCPOrchestrator` still lacks visible MCPApprovalGate wiring for Hugging Face, Databricks and GitHub actions. The repository repair loop still lacks enforced clean-worktree preflight, unique-preimage checking and rollback. Direct deployment scripts still need internal approval gates even though the Databricks workflow has a separate manual exact-SHA/YES gate and Hugging Face sync is quarantined.
- No new external platform authentication was established. The Run91D nine-platform map remains the latest capability/authentication/permission/data-flow record.
- Next: obtain direct publisher bytes and immutable hashes; reconcile RLUSD supply at one XRPL ledger index; reconcile x402 counts using full transaction fields and merchant semantics; separate cash, debt, in-kind XRP, market purchases and contingent facilities in the capital ledger; validate Bybit live ingestion in the authorized read-only collector; complete independent review of all 1,108 changed files and 50 workflow changes; resolve approval and deployment controls before merge.
- No merge, deployment, secret rotation, Space restart, Databricks write, Kaggle submission, external-model dispatch, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or source PR closure occurred.


## Run93 — 2026-11-13T14:03:00Z — current market, exact-head CI, workflow controls and integration audit

### Repository and exact-head verification — VERIFIED

- Main SHA remains `fb272b40966834754ec686f9ed3ab94123f09306`.
- Integration head is `dd4d0ed3cec0428ebb15a6c81150d048dd112693`, parent `fbb7c1fd8dd18b2763fa19dc810e3d752d7d60b8`; 2,254 commits ahead, zero behind.
- Recursive trees are complete: main 1,381 entries; integration 2,353 entries; integration contains 88 workflow files.
- PR #1662 remains open, draft and mergeable. It changes 1,108 files (317,429 additions, 5,136 deletions), including 50 workflow files. It has zero formal reviews, approvals and review threads.
- Open-PR inventory was paged across four API pages: 375 total, 361 drafts, 14 non-drafts; 367 target main and eight target other branches.
- Exact current-head full suite: **3,558 passed, zero failed, eight subtests**, 61.72% inclusive coverage in 93.50 seconds. Core suite: 730 passed, eight subtests, 76% coverage. Wheel build and packaged primary-mission verification passed.
- Exact-head CI: [43438388063](https://github.com/Barrot-Agent/B-Agent/actions/runs/43438388063). Dependency audit: [43438387916](https://github.com/Barrot-Agent/B-Agent/actions/runs/43438387916), five manifest groups passed, no known vulnerabilities reported. Fail-closed gate: [43438387812](https://github.com/Barrot-Agent/B-Agent/actions/runs/43438387812), automatic merge disabled.
- Build warnings remain: deprecated TOML license-table configuration and setuptools package-discovery warnings for `barrot_agent.data.missions` and `data.research`. They did not fail the current build.
- Main's last full-suite CI on unchanged SHA passed 747 tests and eight subtests ([43343513172](https://github.com/Barrot-Agent/B-Agent/actions/runs/43343513172)). Main's separate scheduled Pillars health check failed ([43430139937](https://github.com/Barrot-Agent/B-Agent/actions/runs/43430139937)) because GitHub App credentials were absent, Databricks read-only SELECT returned HTTP 403, and the Hugging Face Space reported BUILD_ERROR. This is an external integration health check, not a repository CI failure. Main's scheduled Cross Analysis succeeded ([43437377285](https://github.com/Barrot-Agent/B-Agent/actions/runs/43437377285)).

### Current XRP market evidence — RESEARCH_ONLY

Capture cutoff: 2026-11-13 14:03 UTC. No publisher response bytes were persisted to Barrot's RawReceiptArchive; no raw SHA-256 receipt was created; none of these observations is a point-in-time feature-store admission.

**Spot**

- OKX XRP-USDT API event time 13:39:00.029 UTC: last $1.0397, bid $1.0396, ask $1.0397; top bid size 6,959.72 XRP, ask size 913.22 XRP; 24-hour open $1.0341, high $1.0440, low $0.9974; volume 46.968M XRP. The observation was about 24 minutes old at capture, exceeding the 300-second live-data limit.
- Kraken XRP/USD retrieval showed last $1.03723, bid $1.03710 and ask $1.03711, but no provider event timestamp. It is excluded from strict point-in-time admission.
- Binance premium-index API event time 13:44:45 UTC showed mark $1.0390, index $1.03936439 and last funding 0.0001 as a decimal (0.01% per eight-hour period). It was about 18 minutes old at capture and is excluded from the 300-second live gate.
- OKX depth and Binance open-interest endpoints were inaccessible through this retrieval. No synchronized multi-venue spot L2 snapshot or executable cross-venue spread is claimed.

Sources: [OKX ticker](https://www.okx.com/api/v5/market/ticker?instId=XRP-USDT), [Kraken ticker](https://api.kraken.com/0/public/Ticker?pair=XRPUSD), [Binance premium index](https://fapi.binance.com/fapi/v1/premiumIndex?symbol=XRPUSDT).

**Derivatives disagreement**

- Liqwall 07:02 UTC: approximately $1.12B all-exchange OI, average funding -0.0025% per eight hours, Binance +0.0026%, $19.3M liquidations ($18.4M longs, $0.906M shorts), and 75.2% Binance accounts long.
- Kodexius 07:04 UTC: $613.07M header OI across seven contracts, $1.72B 24-hour volume and -0.0005% weighted funding. Its venue/contract coverage differs from Liqwall.
- Fibonomy's Binance page displayed $305.43M OI, +0.0008% funding, mark $1.0283 and index $1.0289. This differs materially from the direct Binance premium-index response at 13:44:45 UTC. Its page capture/event time is not synchronized.
- These values must not be averaged. They represent different snapshots, contract universes and vendor aggregation methods. All are research-only at this cutoff.

Sources: [Liqwall](https://liqwall.com/coins/xrp), [Kodexius](https://kodexius.com/data/crypto-derivatives/XRP), [Fibonomy](https://fibonomy.com/en/futures/binance/xrpusdt).

**ETF flows and institutional holdings**

- CryptoETF.today published a partial November 12 reading at 05:49 UTC: +$0.1M net, with only three of five funds reported; XRPC/Canary supplied the reported inflow. Its holdings figure was 1,124,786,413 XRP for its five-fund cohort.
- XRP Insights reports -9,213,260 XRP over November 9–11 and 1,185,967,427 XRP held as of November 11; its November 12 row remains provisional.
- Alpha Finance reports $0 for November 12 in its five-fund cohort, -$2.8M over 30 sessions and $1.71B cumulative net inflow.
- CryptoKeyhole's four daily-read funds show -10.006M XRP over five complete sessions through November 11; November 12 was not fully reported at its latest capture.
- CryptoKeyhole's Q2 2026 13F analysis reports 117 institutional managers with $154.3M in XRP ETF securities across four funds. This is quarter-ended securities ownership, not a current XRP spot purchase or current holdings measure.
- These trackers use different fund cohorts, partial-file rules and issuer-holdings methods. Do not average them. A blank/partial/zero day is not proof of no activity across all funds.

Sources: [CryptoETF.today](https://cryptoetf.today/en/xrp-etf-flows), [XRP Insights](https://xrp-insights.com/data), [Alpha Finance](https://alphafinance.io/etf/xrp/), [CryptoKeyhole](https://cryptokeyhole.com/etf-flows/xrp/).

### Identity and exact-phrase updates

- Japan's SBIC East, Central and West remain distinct from SBI Holdings. Official SBIC East material advertises a 2025 generative-AI/ChatGPT training course; official SBIC West material advertises a ChatGPT introductory seminar. These are educational/investee-support events, not evidence of an OpenAI commercial partnership. Central's official company profile confirms its separate Nagoya identity.
- Exact phrase `ASK Coin`: no canonical XRPL issuer, deployment or verified Ripple/SBI relationship established by this search. Unrelated ASK token candidates remain separate.
- `actual capital`: Run92's SEC prospectus reconciliation remains controlling; cash proceeds, in-kind XRP, historical market purchases, debt, conditional equity capacity, warrants and secondary resales remain distinct.
- Dr. Kamilah/Camilla Stevenson: channel-to-person ownership remains unverified; verified own-channel video inventory remains zero. Guest appearances are not attributed as own-channel uploads.

Primary/official identity sources: [SBIC East training](https://www.sbic.co.jp/training/20250612co/), [SBIC West forum PDF](https://www.sbic-wj.co.jp/wp/wp-content/uploads/2024/07/TF128.pdf), [SBIC Central profile](https://www.sbic-cj.co.jp/company/about/).

### Prediction engine — actual implementation boundary

- Implemented on integration: 48 public endpoint definitions (43 hourly, three weekly CFTC, two noncommercial XRPL node endpoints excluded from scheduled collection); read-only main-only ingestion workflow; per-run SHA-256 receipts and hash chain; cross-run receipt-index continuity; point-in-time SQLite feature store; event timeline and counter-hypotheses; four deterministic baselines; chronological walk-forward evaluation with purge/embargo; temporal calibration; PSI drift diagnostics; fail-closed readiness ledger requiring independent Ed25519 attestation.
- Not implemented: no XRP-specific candidate model is implemented or trained. `walk_forward.py` evaluates the four deterministic baselines only; `forecast_ledger.py` validates an independently supplied readiness report and does not train a model. No model-versus-baseline paired block-bootstrap/source-clustered uncertainty is implemented. The current effective-sample-size method only counts non-overlapping target intervals and does not remove residual serial dependence or shared-source correlation.
- The scheduled ingestion workflow exists only on integration and is guarded to run on main. It has not executed on main because #1662 is unmerged. Raw receipt artifacts retain for 90 days, per-run feature-store checkpoints for seven days, and daily feature-store archives for 90 days. Independent WORM storage and trusted timestamp anchoring remain absent.
- Event registry remains 73 curated events, zero byte-exact raw publisher hashes for those curated events, and zero model-eligible events. Multivariate/concept drift and independent shadow cohort remain absent.
- Forecast **NOT_ISSUED**; accuracy **NOT_EVALUATED**. The legacy 45.5% variable-horizon score remains invalid. No directional forecast, paper trade or real-money action occurred.

### Nine-platform coordination — DESIGNED, NOT DISPATCHED

- ChatGPT GitHub connector: current-session repository read authenticated and verified; permissions remain admin, maintain, push, pull and triage, so least privilege is not met.
- Claude, Grok, Gemini and Codex: no tested authentication/data flow.
- Copilot: review artifacts exist, but no formal approval or review on #1662.
- Hugging Face: prior BUILD_ERROR; no deployment or current authenticated data flow.
- Kaggle: no authentication test and no submission.
- Databricks: prior/current read-only HTTP 403; no write.
- LunaRoute is a separate internal provider; authentication/data flow remains unverified. Integration disables remote LunaRoute MCP; main still enables it.
- No external-model dispatch, structured nine-platform evidence exchange or external-model data transfer occurred. Groq is not Grok.

### Security, workflow and merge decision

- Main is marked protected, but its required status contexts/checks are empty; enforcement is non-admins. Direct branch-protection detail returns HTTP 403. Fallback ruleset 10863829 is disabled. The integration branch is unprotected.
- GitHub connector permissions are overbroad: admin, maintain, push, pull and triage.
- Main OpenCode config enables remote LunaRoute MCP and allows edit/bash/webfetch; integration disables remote MCP and changes mutations to ask.
- Main Barrot Sync runs on main pushes, reads LunaRoute/GitHub secrets, suppresses sync failures and ignores push errors. The integration version is quarantined with no permissions and a disabled job.
- Main paper-trader workflow is manual but writes state/logs to main and pushes. Integration changes it to explicit YES + exact-main-SHA, artifact-only simulation. It was not run.
- Main A2A workflow can deploy on `a2a/**` pushes and upload Worker secrets. Integration requires manual deployment confirmation, a separate secret-rotation confirmation and exact-main-SHA verification. It was not run.
- Main Databricks bundle workflow can deploy and run after manual confirmation; integration quarantines it. No Databricks write occurred.
- Other high-risk issue, merge-queue, scheduler, brain-export, WebMCP sandbox and task-allocation workflows inspected on integration are disabled/quarantined. Hugging Face upload, Space restart, Kaggle submission and external research workflows remain manual and/or exact-SHA/allowlist gated; none was dispatched.
- `MCPApprovalGate` exists with default always-deny, but legacy `MCPOrchestrator` and direct deployment scripts lack visible approval-gate wiring.
- A previous main Pages deployment succeeded automatically; current Pages settings could not be verified through the connector. PR #1662 changes seven public web files; publication authorization remains unresolved.
- PR #1662 remains draft, mergeable and conflict-free, but has zero reviews/approvals/threads. Semantic review of 1,108 changed files and 50 workflow changes remains incomplete.
- **Merge decision: NO MERGE.** Passing exact-head tests do not resolve branch-protection visibility, least privilege, Pages publication authorization, draft status or missing approvals.

### PR backlog and source-branch reconciliation

- #1661: zero commits ahead/122 behind; 1,072 changed paths; supersession candidate.
- #1660: zero ahead/303 behind; 972 changed paths; supersession candidate.
- #1643: zero ahead/1,365 behind; 670 changed paths; supersession candidate.
- #1642: zero ahead/2,270 behind; seven changed paths; supersession candidate.
- #1640: one commit ahead/1,296 behind; its three-file safety objective is semantically covered by integration. All 26 source test names in `test_external_action_gates.py` are present among 31 integration tests; `test_external_deploys_require_confirmation.py` is byte-identical; integration's `barrot-ops.yml` fails closed where source silently skips/masks missing credentials/import errors. Keep open until #1662 is merged and verified on main.
- #1653: 18 ahead/2,271 behind; seven changed files; unique/unreviewed, preserve.
- #1655: 17 ahead/2,271 behind; eight changed files; unique/unreviewed, preserve.
- #1659: eight ahead/2,271 behind; six changed files; unique/unreviewed, preserve.
- #1615: three ahead/2,312 behind; 14 changed files; unique/unreviewed security work, preserve.
- #1614: 36 ahead/2,312 behind; 57 changed files; unique/unreviewed prediction work, preserve.
- #1644–#1650 and #1254–#1255: blocked dependency candidates pending current-main reconciliation.
- #1320, #1318, #1317 and #1269: unique/unreviewed, preserve.
- No source PR was closed.

### Durable Run93 artifacts

- [Run93 current market, exact-head CI, repository and security audit](research/xrp_intelligence/20261113T140300Z-run93-current-market-ci-repository-security-audit.json)
- [Run93 nine-platform capability/authentication/permission/data-flow map](research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_run93.json)
- [Consolidated PR #1662](https://github.com/Barrot-Agent/B-Agent/pull/1662)

### Next concrete action

Complete semantic reconciliation of the existing #1662 integration and resolve GitHub least privilege, branch-protection/required-check visibility and Pages publication authorization. Keep the PR draft until formal review and exact-head checks are satisfied. Then, after a genuinely safe merge, verify the merge commit, refetch main, inspect workflow side effects and rerun main CI. Establish externally anchored raw receipts and synchronized historical data before implementing and evaluating an XRP-specific candidate model. Add paired block-bootstrap/source-clustered uncertainty and independent shadow outcomes before forecast admission.

No merge, deployment, secret rotation, Space restart, external-model transfer, Databricks write, Kaggle submission, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or source PR closure occurred.


## Run93C — 2026-11-13T14:23:17Z — SEC/CFTC XRP classification, XRPL lending votes, ETF-flow disagreement and V3 safety integration

### Exact-head repository verification — VERIFIED

- Audited code head `b4b5fc3d8c6f8a9dc182b5a5d207c2515565b0cd`; main `fb272b40966834754ec686f9ed3ab94123f09306`.
- PR #1662: 2,258 commits ahead, zero behind; 1,113 changed files, 318,984 additions, 5,230 deletions, 50 workflow files. Open inventory 375; 361 drafts and 14 non-drafts.
- Full repository suite: 3,564 passed, zero failed, eight subtests, 62.08% inclusive coverage, 96.8 seconds. Core suite 730 passed, 76% coverage. Wheel and packaged mission checks passed.
- [Full CI 43441582146](https://github.com/Barrot-Agent/B-Agent/actions/runs/43441582146), [dependency audit 43441582247](https://github.com/Barrot-Agent/B-Agent/actions/runs/43441582247), [fail-closed gate 43441582122](https://github.com/Barrot-Agent/B-Agent/actions/runs/43441582122).
- Main's last full CI passed 747 tests and eight subtests. Main's separate Pillars external-health check failed due missing GitHub App credentials, Databricks HTTP 403 and Hugging Face BUILD_ERROR; this is not the repository suite.

### V3 safety and CI integration — EXECUTED, VERIFIED ON INTEGRATION

1. Commit `52388bdb79848a47c986da9ce3eee8378ed84e8c` wires `MCPApprovalGate` into legacy `MCPOrchestrator`. Databricks, Hugging Face downloads, GitHub commits and CI/CD triggers each require approval. External-action flags default false, approval mode defaults `always_deny`, and interactive approval defaults false. The legacy UI warns that its approval interface is unavailable and keeps external actions disabled. Full suite passed on that head in run 43440785381.
2. Commit `8b0069fd68cc74ad9a7f58196a2f415d80983662` adds a script-level paper-trader gate: `BARROT_PAPER_TRADER_APPROVED=YES` is required before state reads or provider calls. The workflow separately requires exact `confirm=YES` and expected main SHA. Full suite passed on that head in run 43441204324. No paper trade was run.
3. Commit `b4b5fc3d8c6f8a9dc182b5a5d207c2515565b0cd` makes the full suite run on pushes to `integration/**` and skips duplicate PR-event suite execution for those branches. Dependency-audit path coverage was expanded. Exact-head push CI passed in run 43441582146.

Direct deployment scripts outside the audited orchestrator/workflow paths still require semantic review. These commits did not authorize or execute any external action.

### XRP spot and derivatives — RESEARCH_ONLY

The latest fresh timestamped snapshot captured at 14:18:23 UTC:

- OKX XRP-USDT event time 14:13:42.872 UTC: last $1.0304, bid $1.0302, ask $1.0303; top bid size 1,447.8 XRP, ask size 7,783.16 XRP; spread 0.97 bps; top-level ask/bid size ratio 5.38; 24-hour open $1.0278, high $1.0440, low $0.9974, volume 47.977M XRP / 49.061M USDT.
- The OKX quote passed the 300-second freshness threshold at capture (281 seconds old), but was stale by the 14:23:17 UTC Run93C cutoff. It was not admitted to Barrot's feature store because no byte-exact raw receipt was persisted.
- Binance XRPUSDT perpetual premium-index event time 14:15 UTC: mark $1.03020818, index $1.03069049, last funding 0.0001 decimal = 0.01% per eight hours, next funding 16:00 UTC. It was 203 seconds old at capture but stale at Run93C cutoff and not admitted.
- Kraken retrieval lacked a provider event timestamp. OKX and Binance L2 retrieval remained unavailable. No synchronized depth or executable cross-venue spread is claimed.

Sources: [OKX ticker](https://www.okx.com/api/v5/market/ticker?instId=XRP-USDT), [Binance premium index](https://fapi.binance.com/fapi/v1/premiumIndex?symbol=XRPUSDT), [Kraken ticker](https://api.kraken.com/0/public/Ticker?pair=XRPUSD).

### ETF flow and institutional ownership disagreement

- CryptoETF.today's November 12 reading at 05:49 UTC was partial (three of five funds) and showed +$0.1M, all from XRPC; its 30-trading-day series showed +$106.8M and cumulative +$1.80B. The same page's lower context panel said 5/5 funds reported, contradicting its top-level 3/5 partial indicator.
- Alpha Finance's XRP-specific page showed $0 on November 12, -$2.8M over 30 sessions and +$1.71B cumulative. Its all-asset page showed -$10.8M for XRP over 30 days. This is an internal provider disagreement.
- CryptoKeyhole's XRP page was updated 00:42 UTC and showed complete data only through November 11, with -10.006M XRP over the last five complete sessions. Its all-asset page at 04:03 UTC showed only five of 15 coin categories complete for November 12, with XRPZ and XRPC still pending at that capture.
- These values are not interchangeable. Fund universe, Grayscale quarterly-only handling, REX-Osprey exclusion, issuer-file arrival, partial-day policy, staking/fee treatment and USD conversion differ. Do not average; ingest issuer files individually before constructing a standardized flow feature.
- CryptoKeyhole's Q2 2026 13F aggregate reports 117 managers and $154.3M across four funds. The primary Goldman Sachs SEC 13F for June 30, filed August 14, shows $78.859M across 21Shares, Bitwise, Canary and Franklin XRP ETF shares. CryptoKeyhole's secondary Goldman figure is $87.4M, an unresolved $8.541M difference. These are ETF securities at quarter-end, not direct XRP balances or current spot purchases.

Sources: [CryptoETF.today](https://cryptoetf.today/en/xrp-etf-flows), [Alpha Finance XRP](https://alphafinance.io/etf/xrp/), [Alpha Finance all assets](https://alphafinance.io/etf/), [CryptoKeyhole XRP](https://cryptokeyhole.com/etf-flows/xrp/), [CryptoKeyhole all assets](https://cryptokeyhole.com/etf-flows/all/), [Goldman Sachs SEC 13F](https://www.sec.gov/Archives/edgar/data/886982/000088698226000006/0000886982-26-000006-index.htm).

### XRP legal classification — primary regulatory finding

The joint SEC-CFTC interpretive release SEC 33-11412 / 34-105020, issued March 17, 2026 and effective March 23, expressly lists XRP as an example of a **digital commodity**.

This is a material agency-classification development. It is not a court judgment and is not blanket immunity for every XRP-related transaction. The release expressly states it does not supersede or replace Howey; a digital commodity may still be involved in an offer or sale that constitutes an investment contract depending on the facts and circumstances.

Primary source: [SEC-CFTC interpretive release](https://www.sec.gov/files/rules/interp/2026/33-11412.pdf).

### US stablecoin regulation — GENIUS Act implementation

The OCC's final GENIUS Act rule was issued October 21, 2026 and takes effect January 18, 2027. OCC is not yet accepting applications until OMB approves the information collection. Existing issuers may request a prior-approval waiver if a substantially complete application is pending on the effective date; no named issuer is presumed to qualify. BSA/AML/OFAC requirements are addressed in separate future rulemaking.

Do not conflate a national trust-bank charter with permitted payment-stablecoin-issuer status under the GENIUS Act or with MiCA significant-EMT supervision. These are separate legal statuses. Circle, Ripple and Coinbase trust charters do not, by themselves, establish GENIUS Act permitted issuer status.

Sources: [OCC final rule](https://www.occ.gov/news-issuances/news-releases/2026/nr-occ-2026-120.html), [OCC Bulletin 2026-51](https://www.occ.gov/news-issuances/bulletins/2026/bulletin-2026-51.html).

### XRPL lending, collateral and amendment status

Official XRPL documentation states that XLS-66 Lending Protocol creates fixed-term **uncollateralized** loans from pooled Single Asset Vault assets. Borrower underwriting is off-chain; the protocol does not include automated on-chain collateral and liquidation management in its current design. First-loss capital is optional and does not eliminate credit risk. Single Asset Vaults can hold lender assets including XRP, RLUSD trust-line tokens and MPTs; this does not make those assets borrower collateral by default. A collateralized product requires additional logic, such as on-chain custodians.

The November 13 XRPL Dashboard roll call at 11:21 UTC reported 35 validators heard, 29 required, 22 votes for LendingProtocol, 22 for LendingProtocolV1_1 and 23 for SingleAssetVault, with zero 14-day activation countdown entries. A separate tracker on November 12 showed 36 validators with the same 22/23 votes and 29 required. Preserve the denominator difference; both snapshots show the amendments below threshold and not activated.

Sources: [XRPL institutional credit facilities](https://xrpl.org/docs/use-cases/defi/institutional-credit-facilities), [XRPL Lending Protocol](https://xrpl.org/es-es/docs/concepts/tokens/lending-protocol), [XRPL amendment tracker](https://xrpldashboard.com/amendments), [independent tracker](https://xrpl.to/amendments).

### Prediction engine — no forecast

- 48 source definitions; 46 scheduled public endpoints (43 hourly, three weekly CFTC); scheduled workflow remains main-only and has not executed on main because the integration is unmerged.
- 73 curated events, zero byte-exact raw publisher hashes, zero model-eligible events. Raw artifacts retain 90 days; per-run feature-store checkpoints seven days; daily archives 90 days. External WORM and trusted timestamp anchoring are absent.
- Current walk-forward evaluator runs naive, momentum, mean-reversion and volatility baselines only. No XRP-specific candidate model is implemented or trained. Paired block-bootstrap/source-clustered uncertainty, multivariate/concept drift and an independent shadow cohort remain absent.
- Forecast **NOT_ISSUED**; accuracy **NOT_EVALUATED**. No directional forecast, paper trade or real-money action occurred.

### Nine-platform coordination and security

- ChatGPT GitHub connector read access is verified; permissions remain admin, maintain, push, pull and triage, so least privilege is not met.
- Claude, Grok, Gemini and Codex remain unverified; Copilot has no formal approval on #1662; Hugging Face has prior BUILD_ERROR; Kaggle is untested; Databricks read-only access returned HTTP 403. No external-model dispatch or data transfer occurred. Groq is not Grok.
- Main OpenCode still enables remote LunaRoute MCP and write-capable edit/bash/webfetch; integration disables remote MCP and requires approval for mutations.
- Main is marked protected but required status contexts/checks are empty; direct protection detail returns HTTP 403; fallback ruleset 10863829 is disabled. Integration is unprotected.
- GitHub connector permissions are overbroad. Pages publication authorization remains unresolved because a previous main push deployed Pages automatically and #1662 changes seven public web files.
- Direct deployment scripts outside the reviewed orchestrator/workflow paths remain under semantic review.

### PR backlog and merge decision

- #1661, #1660, #1643 and #1642 remain supersession candidates; do not close before #1662 is merged and its content verified on main.
- #1640's one-commit delta is semantically superseded by the stricter integration implementation: all source test names are present in the integration test set, the deployment-confirmation test is byte-identical, and integration fails closed where the source silently skips/masks missing credentials. Keep it open until merge verification.
- #1653, #1655, #1659, #1615 and #1614 remain unique/diverged; preserve. #1644–#1650 and #1254/#1255 remain blocked dependency candidates. #1320, #1318, #1317 and #1269 remain unique/unreviewed.
- No source PR was closed.

### Durable Run93C artifacts

- [Run93C market, regulatory, XRPL lending, ETF and safety addendum](research/xrp_intelligence/20261113T142317Z-run93c-market-regulatory-security-addendum.json)
- [Run93C nine-platform capability/authentication/permission/data-flow map](research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_run93c.json)
- [Consolidated integration PR #1662](https://github.com/Barrot-Agent/B-Agent/pull/1662)

### Next concrete action

Complete semantic reconciliation of the 1,113-file integration and direct deployment scripts. Resolve GitHub connector least privilege, branch-protection/required-check visibility and Pages publication authorization. Keep #1662 draft until formal review and approvals are satisfied. Then verify the exact merged commit, refetch main, inspect automatic workflow side effects and rerun main CI. Establish externally anchored raw receipts and synchronized historical data before implementing an XRP-specific candidate model. Add paired block-bootstrap/source-clustered uncertainty and independent shadow outcomes before forecast admission.

No merge, deployment, secret rotation, Space restart, external-model transfer, Databricks write, Kaggle submission, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or source PR closure occurred.


## Run 94 — 2026-11-13: Evernorth capital, institutional relationships and SBIC identity

**Captured:** 2026-11-13T14:31:30.954Z UTC. **Main SHA:** `fb272b40966834754ec686f9ed3ab94123f09306`. **Verified integration head before this handoff commit:** `404a34152adc8535dd3bd803d8eb1ba89e9a2269`. This head is a documentation-only descendant of code head `b4b5fc3d8c6f8a9dc182b5a5d207c2515565b0cd`; exact-head CI was rerun successfully on `404a34152adc8535dd3bd803d8eb1ba89e9a2269`.

### Exact-head verification

- [Full CI run 43442755318](https://github.com/Barrot-Agent/B-Agent/actions/runs/43442755318): **3,564 passed**, 8 subtests passed, 62.08% inclusive coverage, 76% core coverage; wheel built and installed-wheel mission verification passed.
- [Dependency audit 43442754785](https://github.com/Barrot-Agent/B-Agent/actions/runs/43442754785): five manifest groups passed; zero known vulnerabilities reported.
- [Fail-closed gate 43442755262](https://github.com/Barrot-Agent/B-Agent/actions/runs/43442755262): passed with merging disabled.
- The verified code changes include the legacy MCP approval gates, paper-trader exact per-run approval, and integration-push full-suite/dependency-audit triggers. No paper trade or external MCP action was executed.

### Evernorth actual capital reconciliation

The November 9, 2026 SEC prospectus distinguishes capital actually received from in-kind XRP and contingent financing:

- At the October 9 closing: $214.05M advance private-placement cash, $10.5M delayed private-placement cash and approximately $48M SPAC trust cash; approximately $272.6M gross cash proceeds before transaction expenses.
- The issuer reports approximately $214.1M of advance cash used to purchase 84,365,876 XRP. The implied cash-per-token amount is about $2.54, **not a verified execution price**; the filing does not identify venue, counterparty or execution timestamps.
- Approximately 388,910,554 XRP were contributed in kind: 211,319,096 by Arrington's sponsor vehicle, 50M by a Ripple-affiliated trust, 126,791,458 directly by Ripple, 600,000 by advance subscribers and 200,000 by delayed subscribers. Combined with the cash-purchased XRP, this reconciles to approximately 473.28M XRP. About 82.2% of these components were in-kind contributions, not open-market buying.
- $30M of 4% PIK convertible senior notes were issued and paid October 12, 2026. This is actual debt financing, not equity. No subsequent XRP purchase using the note proceeds was verified.
- Cantor's equity line permits up to 5,218,935 shares and approximately $76.8M potential gross proceeds, but the prospectus reports zero proceeds received as of November 9 and a $521,893.50 commitment fee. It is not capital already received.
- The issuer says it does not actively trade XRP on digital asset markets. The cash-purchase venue remains unknown.
- Four SBI Holdings-controlled entities hold 9,431,914 Class A and 2,359,038 Class C shares, representing 21.4% of common stock and 39.9% of voting power. These are SBI Holdings entities, not regional SBIC companies.
- BitGo is Evernorth's disclosed custodian, with 100% cold storage and $250M aggregate shared insurance, not dedicated coverage. Coinbase is the accounting principal market, not the custodian.

### Circle reserves and flow-measurement caveat

Circle's SEC S-1/A reports that as of March 31, 2025 approximately 90% of USDC reserves were held in the Circle Reserve Fund, managed by BlackRock and custodied by BNY; the remainder was cash distributed across banks. The fund is a Rule 2a-7 government money market fund holding short-dated U.S. Treasuries, overnight Treasury repos and cash. It is not FDIC-insured or government-guaranteed.

The same filing explicitly states that USDC minted and redeemed do **not** equal the amount acquired or redeemed by end users. This is a mandatory feature-store caveat: issuer mint/burn events cannot be treated as end-user net capital flows.

### Coinbase, Circle, Ripple and SBI relationship map

- **SBI–Ripple:** SBI stated approximately 9% Ripple ownership in 2025 materials. SBI Group held 60% of SBI Ripple Asia voting rights as of March 31, 2026. SBI Ripple Asia says it does not handle XRP; the historic ODL route uses XRP through SBI Remit, Coins.ph and SBI VC Trade. Current corridor volumes are not disclosed.
- **SBI–RLUSD:** RLUSD launched in Japan through SBI VC Trade on June 24, 2026 after JFSA approval under the Payment Services Act. This is stablecoin distribution, not proof that every RLUSD payment uses XRP as a bridge.
- **SBI–Circle:** SBI Holdings and SBI Shinsei Bank announced a combined $50M Circle IPO investment. SBI also announced ARC presale participation; its individual amount is undisclosed. Circle named SBI Group a founding validator at Arc mainnet launch. Arc uses USDC as gas and a permissioned validator set, not XRP. The exact ownership ratio of SBI Circle Holdings was not confirmed in the primary material retrieved for this run.
- **Circle–XRPL:** Circle launched native USDC on XRPL on June 12, 2025; Circle Mint and APIs support it without bridging. This adds a stablecoin rail to XRPL but does not establish material XRP buy demand.
- **Circle–Coinbase:** Circle's SEC S-1/A describes Coinbase as a minority equity investor and USDC distribution/revenue-sharing partner. Coinbase-held USDC was 21% of circulation as of June 30, 2025; this is historical, not current. Their flow measures are economically linked, not independent confirmations.
- **Coinbase–Evernorth:** Coinbase is selected as principal market for accounting valuation. BitGo is custodian. Coinbase's own help page lists New York among regions where XRP is not supported.
- **Circle–Ripple:** USDC and RLUSD coexist on XRPL. No direct commercial partnership was established in this research.

### Japan SBIC identity

- SBIC East: Tokyo Small and Medium Business Investment & Consultation Co., Ltd.
- SBIC Central: Nagoya Small and Medium Business Investment & Consultation Co., Ltd.
- SBIC West: Osaka Small and Medium Business Investment & Consultation Co., Ltd.

These are separate regional Japanese legal entities, not SBI Holdings. Tokyo SBIC's March 5, 2026 ChatGPT seminar was a genuine SBIC-hosted training event with Hamamatsu Iwata Shinkin and a Microsoft speaker; it does not establish an OpenAI partnership.

### Exact-phrase and identity status

- `ASK Coin`: unresolved; no primary XRPL issuer or XRP relationship verified. Permission Coin (ASK) and an unrelated Ask Coin exchange listing remain separate candidates.
- `actual capital`: reconciled to cash-funded XRP purchase, delayed cash, SPAC trust, in-kind XRP, debt proceeds and unused ELOC capacity.
- `SBIC, ChatGPT SBIC`: no exact authoritative partnership match. An SBIC-hosted ChatGPT seminar exists, but no OpenAI commercial/data relationship is established.
- `Camilla/Kamilah Stevenson`: one TEDxWillowCreek speaker appearance is verified for Kamilah; personal-channel ownership and broader video inventory remain unverified. Camilla remains a separate unresolved spelling.

### Research artifacts and prediction status

- [Run94 Evernorth capital and institutional-network evidence](research/xrp_intelligence/20261113T143130Z-run94-evernorth-capital-institutional-network-reconciliation.json)
- [Run94 nine-platform capability/authentication/permission/data-flow map](research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_run94.json)
- Run93C remains the source for the November 13 spot/derivatives snapshot, ETF-flow and Goldman 13F disagreements, SEC-CFTC XRP digital-commodity interpretation, OCC GENIUS Act rule, and XRPL Lending amendment/collateral status.

Prediction remains **NOT_ISSUED**. The mission has 48 source definitions, 46 scheduled public endpoints, 73 curated events, zero byte-exact raw publisher hashes, zero model-eligible events, no trained XRP candidate model and no measured out-of-sample lift. The current market and corporate web captures are research-only, not point-in-time model features.

### Merge decision and next action

PR #1662 remains draft, with zero formal reviews and approvals. Main branch-protection detail remains HTTP 403; the visible fallback ruleset is disabled; Pages publication authorization is unresolved; the GitHub connector reports admin/maintain/push/pull/triage permissions, so least privilege is not met. Semantic review of the 1,115-file integration and direct deployment scripts remains incomplete.

Keep #1662 draft. Do not merge until independent formal approval, exact-head checks, security gates, branch-protection requirements and public Pages authorization are all resolved. After a valid merge, fetch main, verify the merge commit and merged files, run main CI, and only then close exact superseded source PRs.

No merge, deployment, secret rotation, Space restart, external-model dispatch, Databricks write, Kaggle submission, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or source PR closure occurred.


## Run 95 — 2026-11-13: canonical receipt gate repair, exact-head verification and live market reconciliation

**Captured:** 2026-11-13T14:53:43.720Z UTC. **Main SHA:** `fb272b40966834754ec686f9ed3ab94123f09306`. **Integration head before this handoff commit:** `501832afe8c5a4c5fc5f5c80d28d14733dc7838f`. **PR:** [#1662](https://github.com/Barrot-Agent/B-Agent/pull/1662), still draft.

### Prediction-evidence gate correction — executed and verified

A schema mismatch was found between `RawReceiptArchive.store()` and `research_eligibility._source_registry()`. The archive emits canonical v1/v2 receipt fields including retained-byte status, retention reason and optional HTTP provenance headers, while the eligibility validator expected an incomplete field set. Synthetic tests had not exercised an actual archive receipt.

- Commit `ceafda5de59301ca3e6b574d306f8e810944f274`: validator now accepts only the exact canonical v1/v2 archive schemas, validates the allowlisted HTTP provenance headers, and rejects digest-only receipts or retention exceptions for model admission.
- Commit `501832afe8c5a4c5fc5f5c80d28d14733dc7838f`: added regression tests that construct real `RawReceiptArchive` receipts, verify retained-byte admission, and reject digest-only receipts.
- Both new regression tests passed on the exact head.

### Exact-head CI — verified on push event

- [Full CI run 43446636533](https://github.com/Barrot-Agent/B-Agent/actions/runs/43446636533): exact head `501832a`; **3,566 passed**, 8 subtests passed, 62.08% inclusive coverage, 76% core coverage. Wheel build and installed-wheel verification of Barrot V3, the XRP mission and canonical data assets passed.
- [Core suite](https://github.com/Barrot-Agent/B-Agent/actions/runs/43446636533): 732 passed, 8 subtests passed.
- [Dependency audit 43446646672](https://github.com/Barrot-Agent/B-Agent/actions/runs/43446646672): five manifest groups passed; no known vulnerabilities reported.
- [Fail-closed push gate 43446636763](https://github.com/Barrot-Agent/B-Agent/actions/runs/43446636763) and [PR gate 43446646872](https://github.com/Barrot-Agent/B-Agent/actions/runs/43446646872): passed with merging disabled.
- [PR CI event 43446646668](https://github.com/Barrot-Agent/B-Agent/actions/runs/43446646668) was skipped by the integration-branch PR condition; the push-triggered full-suite run above completed successfully. The earlier handoff's “full suite pending” state was stale because the commit-workflow helper returned only PR-triggered runs.

### Live repository and integration state

- Main remains `fb272b40966834754ec686f9ed3ab94123f09306`; no main changes.
- Integration head before this documentation commit: `501832afe8c5a4c5fc5f5c80d28d14733dc7838f`; 2,262 commits ahead, zero behind; 1,117 changed files.
- Open PR inventory: 375 total, 361 drafts and 14 non-drafts. #1662 is the only open PR currently based on the current main SHA. No PRs were closed.
- #1662 remains draft, mergeable, with zero formal reviews, zero approvals and zero inline review threads. Test success does not replace independent review.
- Main CI run 43343513172 passed, including its full repository suite (747 tests and 8 subtests). Main Pages build/deploy run 43343511839 succeeded, confirming that a main push can publish the Pages site automatically.
- Main scheduled Cross Analysis run 43446769807 completed its read-only analysis and artifact upload successfully. Pillars Check 43430139937 failed because GitHub App ID/private key/installation ID were absent, Databricks returned HTTP 403, and the Hugging Face Space reported BUILD_ERROR.
- Main branch-protection detail remains inaccessible (HTTP 403); visible fallback ruleset 10863829 is disabled. Pages configuration API was not accessible; the successful Pages deployment run is direct evidence of the side effect.

### Workflow and external-action safety screen

All 50 workflow files changed by #1662 were screened for triggers, permissions, secrets and external writes. High-risk deployment, Databricks, Hugging Face, Kaggle and paper-trading paths are manual/confirmation-gated or disabled; none were dispatched. The cross-analysis workflow is read-only and artifact-only. The XRP public-ingestion workflow is hourly plus daily but its job is explicitly restricted to `refs/heads/main`; it has not run on main because #1662 is unmerged. Direct deployment/MCP call-path semantic review is still incomplete. The MCP orchestrator requests approval before Hugging Face model downloads and Databricks job submission; the approval-gate implementation defaults to `always_deny`.

### November 13 market reconciliation — research only

- Kraken XRP/USD ticker returned bid $1.03271, ask $1.03279, last $1.03262, 24-hour volume 36.11M XRP, high $1.04269, low $0.99672 and open $1.04003. The API response did not expose a server timestamp; this is a single-venue web-rendered observation, not a model feature.
- The best-timestamped order-book snapshot retrieved was Binance XRPUSDT **perpetual**, not spot: Basis at 07:23 UTC showed a $1.0321 mid, 0.97 bp spread, 52% bid share within 1%, and $13.6M depth within 0.5%. FreeOrderBook's displayed spot cross-exchange prices materially conflicted with Kraken and its own top-20 ask summary was inconsistent. Direct synchronized spot depth remains unverified.
- Perpetual OI providers ranged from $613M (Kodexius) to $1.55B (TradRadar) to $2.26B (CoinGlass). Funding signs and magnitudes also disagreed. No cross-provider average was computed; venue/contract universes and capture times differ.
- ETF trackers disagree on Nov 12 zero versus missing and on product universes. XRP Insights and CryptoKeyhole report net XRP reductions over overlapping Nov 5-11 windows; TheXRPInvestor includes spot, derivative, index and income products. Holdings changes are not equivalent to end-user cash flows.
- All web captures are marked research-only: no byte-complete publisher payloads, no raw receipt IDs and zero eligible model observations. No forecast was issued.

Artifact: [Run95 market structure reconciliation](research/xrp_intelligence/20261113T145343Z-run95-market-structure-reconciliation.json).

### Backlog and next action

#1662 remains the single active integration candidate but is **blocked**, not ready. Obtain independent formal review; finish semantic review of direct deployment scripts and all changed paths; resolve least-privilege GitHub access, branch-protection visibility and Pages publication authorization. After any approved merge, refetch main, verify the merge commit and merged files, run main CI, account for Pages deployment and only then close exact superseded source PRs. Activate the main-only XRP ingestion workflow only after that merge; establish durable externally anchored raw receipts, synchronized spot/derivatives/ETF history and measured out-of-sample lift before forecast admission.

No merge, deployment, secret rotation, Space restart, external-model dispatch, Databricks write, Kaggle submission, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or source PR closure occurred.


## Run 96 — 2026-11-13T15:03:22.008Z: Coinbase, Circle, Ripple and SBI institutional rail reconciliation

**Main SHA:** `fb272b40966834754ec686f9ed3ab94123f09306`. **Integration head before this artifact commit:** `9dd4944c6e45e8f7cc0a60b0db159fe75edfc105`. This is a research-only update; no code or main-branch changes.

### Primary-source findings

- **Coinbase–Circle economics:** Coinbase's Q3 2026 results report $22B average USDC held in Coinbase products, 49% year-over-year growth, approximately 30% of average USDC market capitalization, and approximately 50% of USDC economics captured by Coinbase over the prior year. The 50% figure is an issuer-reported revenue/economics relationship, not equity ownership and not XRP flow. [Coinbase Q3 results](https://investor.coinbase.com/news/news-details/2026/Coinbase-Q3-2026-Earnings-Show-All-time-high-Coinbase-One-Subscribers-and-Prediction-Markets-Surpassing-200-Million-in-Annualized-Revenue/)
- **Coinbase–Ripple:** Coinbase announced RLUSD support on Prime, Exchange and its retail app in supported regions. Deposits and withdrawals are supported across XRPL, Base and Ethereum. Coinbase Global Exchange collateral support was described as forthcoming, not live at launch; Ripple said it would provide liquidity on Base. This establishes a direct RLUSD distribution relationship, not XRP as the bridge asset. [Coinbase RLUSD announcement](https://www.coinbase.com/blog/rlusd-is-now-available-on-coinbase)
- **PNC–Coinbase–Circle:** PNC's November 9 announcement says eligible corporate clients can receive Circle USDC on Ethereum through Coinbase Payment products; incoming USDC is converted 1:1 to USD and deposited into PNC accounts. The program is a limited pilot with no transaction volume disclosed. It is not an XRP or XRPL rail. [PNC announcement](https://pnc.mediaroom.com/2026-11-09-PNC-Bank-Launches-Incoming-Stablecoin-Payments-for-Corporate-and-Institutional-Banking-Clients)
- **Circle–XRPL:** Circle's USDC page reports $68.9B circulation as of November 9 and native issuance on 38 blockchains, including XRPL. Native USDC on XRPL does not prove XRP is used as a bridge asset or that transfers generate material XRP buy demand. [Circle USDC](https://www.circle.com/usdc)
- **Circle Arc and SBI:** Circle announced Arc mainnet on September 16 with USDC gas, Circle Payments Network integration, StableFX and a permissioned validator cohort that includes SBI Group, BlackRock, DTCC, ICE, Mastercard, Visa and others. Arc is a distinct institutional settlement rail and a competitive alternative for some use cases. [Arc mainnet announcement](https://investor.circle.com/news/news-details/2026/Circle-Launches-Arc-Mainnet-an-Economic-Operating-System-for-the-Internet/default.aspx)
- **Circle payment infrastructure:** ACI Worldwide/Circle announced a Colombia USDC settlement pilot alongside the Bre-B instant-payment ecosystem. Volante/Circle announced USDC workflows for existing multi-rail bank payment infrastructure. Both are pilots/evaluations; neither announcement reports XRP usage or material transaction volumes. [ACI/Circle](https://investor.circle.com/news/news-details/2026/ACI-Worldwide-and-Circle-Collaborate-to-Bring-USDC-Settlement-to-Existing-Payments-Infrastructure-in-Latin-America/default.aspx) · [Volante/Circle](https://investor.circle.com/news/news-details/2026/Volante-Technologies-and-Circle-advance-stablecoin-payment-and-settlement-capabilities-for-financial-institutions/default.aspx)
- **Circle–Binance capital:** Circle announced a $100M Binance equity investment and a five-year USDC commercial agreement on September 22. This is capital into Circle and a distribution commitment, not XRP capital. [Circle/Binance announcement](https://investor.circle.com/news/news-details/2026/Binance-Invests-100-Million-in-Circle-Expands-Strategic-Partnership-and-Renews-Commercial-Agreement-for-Five-Years/default.aspx)

### Capital-flow reconciliation and XRP implications

Circle's Arc launch announcement on September 16 cited more than $74B USDC circulation; Circle's current USDC page reports $68.9B on November 9. The two issuer snapshots show a lower later figure by at least approximately $5.1B, but they are not a reconciled daily mint/burn series. Do not call this confirmed net redemptions or end-user capital outflow without the daily supply ledger.

The new evidence shows Coinbase is a significant USDC distribution/economics channel while also listing Ripple's RLUSD. SBI Group participates in both the Circle/Arc and Ripple/RLUSD ecosystems. This is multi-rail institutional exposure, not evidence of coordinated XRP buying. PNC's pilot is Ethereum USDC; Circle's ACI/Volante pilots are USDC rails; Arc uses USDC gas. RLUSD and USDC on XRPL can increase XRPL stablecoin utility, but no direct XRP bridge volume, XRP collateral use, XRP spot purchase or disclosed XRP capital inflow was verified.

Artifact: [Run96 institutional rail reconciliation](research/xrp_intelligence/20261113T150322Z-run96-institutional-rail-reconciliation.json). See Run94 for the primary SBI/Ripple/Circle ownership, custody and Japan SBIC identity work. All new company-source extracts remain research-only with zero model-eligible observations.

### Exact-head status and next action

Before this Run96 documentation update, PR #1662 head `9dd4944c6e45e8f7cc0a60b0db159fe75edfc105` passed [full CI 43447765669](https://github.com/Barrot-Agent/B-Agent/actions/runs/43447765669): 3,566 passed, 8 subtests passed, 62.08% inclusive coverage, 76% core coverage and packaged mission verification. [Dependency audit 43447765862](https://github.com/Barrot-Agent/B-Agent/actions/runs/43447765862) and [fail-closed gate 43447765721](https://github.com/Barrot-Agent/B-Agent/actions/runs/43447765721) passed. PR #1662 remains draft with no formal approvals; no merge is authorized until independent review, branch-protection and Pages publication blockers are resolved.

No merge, deployment, secret rotation, Space restart, external-model dispatch, Databricks write, Kaggle submission, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or source PR closure occurred.
