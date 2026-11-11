# Barrot XRP Mission Handoff — Run21

As of 2026-11-11T10:26:35Z
Mission: XRP intelligence and prediction-engine mastery, priority 1.
Foundation: preserve Barrot V3 as execution, orchestration, safety and verification.

## Repository
Main SHA 84f28ee7755607236231545a14f3d093c1baaa85.
Integration head tested: a62bad5747fc89b7e851aa9e0b2f3f58ae94106e.
PR #1661 open, draft, mergeable clean; 995 changed files, 44 workflows, 951 other paths.
2,010 commits ahead, zero behind. Complete trees: main 1,388 entries, integration 2,260 entries.
374 open PRs: 360 drafts, 14 non-drafts. Local clone still fails DNS; remote GitHub API retrieval succeeded.

## Exact-head verification
Full suite: 3,423 passed, zero failed, eight subtests, 59.98% coverage, 95.96 seconds.
Core suite: 714 passed, zero failed, eight subtests.
Wheel build, install and primary mission verification passed.
Six dependency manifests audited; zero known vulnerabilities.
Fail-closed PR and push gates passed; automatic merge remains disabled.
Full CI 43003897822; dependency audit 43003898372; gates 43003898327 and 43003891044.
Main CI 42944864014 passed 718 tests; latest Cross Analysis 42998707871 succeeded; Pages 42944862534 succeeded as automatic side effect.
The preceding head failed two exact-phrase assertions in research JSON; corrected. No runtime prediction-engine failure.

## Prediction engine
Implemented: 46 public source definitions; read-only collector; SHA-256 receipts and receipt-chain verification; SQLite point-in-time feature store; four deterministic baselines; chronological walk-forward with purge/embargo and overlap-adjusted effective sample size; calibration; univariate PSI drift diagnostics; Ed25519-attested forecast ledger.
Not production verified: independent WORM/timestamp anchor; replayable cross-run feature store; synchronized historical spot/L2/derivatives/flows/collateral; vintage-aware macro events; scenario/counter-hypothesis engine; trusted evaluator key; independent shadow outcomes; out-of-sample lift.
Issuance gates: 100 OOS samples, 100 shadow outcomes, two independent source groups, ten non-overlapping horizon multiples, calibration error no greater than 0.05, lift over four baselines on Brier score and log loss, independent Ed25519 attestation.
Forecast NOT_ISSUED. Collector is on integration only and guarded to run on main; no successful main ingestion run.

## Current market
OKX XRP-USDT at 09:58:10.975 UTC: 1.0593, bid 1.0591, ask 1.0592, 24h volume 68.10M XRP.
Kraken retrieval: $1.05705, bid $1.05729, ask $1.05730; no provider event timestamp. USDT/USD 0.99894. Normalized asynchronous midpoint difference 0.0693%, not arbitrage.
Fuelmaps spot depth at 02:00 UTC: within 1%, $14.2M bids / $10.8M asks; within 5%, $29.0M / $14.6M; stale by 8h26m.
Basis Binance XRPUSDT perpetual book at 06:28 UTC: within 1%, $16.7M bids / $14.7M asks; not spot.
TradRadar OI $1.57B (-4.96%), funding +0.0094%/8h, long-heavy liquidations. Liqwall OI $1.15B (-2.2%), funding +0.0066%/8h, long-heavy liquidations. Different universes; do not average.
Alpha ETF Nov10 -$7.6M, 30-session +$1.3M, cumulative +$1.71B. CryptoKeyhole Nov10 partial; XRP Insights Nov9 -9.54M XRP. Preserve separate universes.
October U.S. CPI beat consensus; Treasury yields and dollar rose. Broad risk-off context, not XRP-specific causation.

## Institutional and identity
Evernorth named Ripple, Kraken, Coinbase and BitGo as planned Q4 execution partners for its 473M XRP treasury. Agreements remain subject to conditions; deployment amounts and returns not verified.
Coinbase RLUSD distribution, PNC USDC-to-USD pilot, BNY XRP/RLUSD custody and Ripple Treasury AI/RLUSD capabilities do not establish XRP purchases or payment volume.
SBI's $200M Evernorth cash is included in the $214.05M advance-funding pool, not additive.
Japan SBIC East/Tokyo, Central/Nagoya and West/Osaka are distinct statutory companies, not SBI Holdings. SBIC ChatGPT activity is educational.
ASK Coin exchange and Permission Coin ASK token are separate candidates; no XRP link verified.
Actual capital must separate cash, cash deployed, in-kind XRP, debt, facilities, ELOC and resale registration.
Kamilah Stevenson person identity confirmed; candidate YouTube channel remains unverified. 21 candidate references, zero verified creator inventory.

## Nine platforms
ChatGPT GitHub API read/write on integration verified; no main write or secrets access.
Claude, Grok, Gemini and Codex unverified. Copilot no formal approval. Hugging Face prior build error; no deployment. Kaggle untested. Databricks prior HTTP 403. LunaRoute endpoint auth/data flow unverified. No external-model transfer.

## Security and backlog
Main protected, integration unprotected. Detailed branch protection endpoint 403; visible fallback ruleset disabled. Main push automatically publishes Pages; publication authorization absent.
Credential path .config/gh/hosts.yml absent main/integration but present on 17 of 17 rechecked open PR tips. Contents not read. Repo reports OAuth revoked; provider revocation unverified.
#1661 blocked. #1660 superseded candidate retained. Preserve unique #1653, #1614, #1611, #1610, #1612, #1269 and #1608. Reconcile overlap candidates #1640, #1642, #1643, #1644–#1650, #1317, #1318, #1320, #1254, #1255. No PR closed.

## Next actions
Complete semantic review of 951 non-workflow paths. Resolve branch protection, approvals, credential revocation evidence and Pages side effect. Preserve unique PRs. Only after authorized merge, verify merge commit, refetch main, verify files, run main CI and first read-only ingestion. Implement WORM anchoring and replayable store. Keep forecasts disabled.

No merge, deployment, secret action, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or PR closure.


## Run22 — 2026-11-11T11:08Z — exact-head verification, market microstructure, theft-linked flow, Ripple Prime leadership and XRPL quantum roadmap

### Repository and CI
- Main remains `84f28ee7755607236231545a14f3d093c1baaa85`; integration branch remains `integration/xrp-v3-unified-main-20261111`, parent/current head before this documentation update `64b8738710f4823af1641a9704dd3948ccc640a1`; 2,011 ahead, zero behind.
- PR #1661 remains open/draft, reported mergeable; zero formal reviews, approvals and review threads. Open PR inventory: 374 (360 drafts, 14 non-drafts). Complete trees: main 1,388, integration 2,260. Local Git clone still fails DNS; remote GitHub API works.
- Exact head `64b8738`: 3,423 full-suite tests passed, zero failures, eight subtests, 59.98% coverage in 94.07s; 714 core tests passed; wheel build/install and primary mission verification passed; six dependency manifests audited, zero known vulnerabilities reported; fail-closed PR/push gates passed. Full CI [43005232066](https://github.com/Barrot-Agent/B-Agent/actions/runs/43005232066), audit [43005232071](https://github.com/Barrot-Agent/B-Agent/actions/runs/43005232071), PR gate [43005232185](https://github.com/Barrot-Agent/B-Agent/actions/runs/43005232185), push gate [43005224271](https://github.com/Barrot-Agent/B-Agent/actions/runs/43005224271).
- Coverage floor remains 53%, below the previous 70% target; measured coverage is 59.98% for barrot_agent, not all repository packages.
- Main scheduled Cross Analysis [43007129290](https://github.com/Barrot-Agent/B-Agent/actions/runs/43007129290) succeeded. Its workflow has contents:read, persist-credentials:false, performs read-only entity/sentiment analysis and uploads artifacts; it does not commit or push. Main's legacy signal-accuracy workflow is disabled with permissions:{} and if:false. Main push still triggers Pages deployment; publication authorization remains unresolved.

### Current XRP market and microstructure — descriptive only
- OKX XRP-USDT at provider timestamp 2026-11-11T10:21:28.166Z: last 1.0625, bid 1.0622, ask 1.0623, 24h volume 68.13M XRP. Kraken XRP/USD retrieval: last $1.06507, bid $1.06483, ask $1.06484, 24h volume 33.45M XRP, no provider timestamp. Kraken USDT/USD midpoint about 0.999025. Normalized OKX/Kraken midpoint difference about 0.34%, asynchronous; Kraken last is above displayed ask. Do not use as an executable spread signal.
- Fuelmaps spot order-book snapshot 11:00 UTC, mid $1.0605, six venues: within ±1%, $9.5M bids/$8.6M asks (52.6% bid share); ±5%, $19.6M/$13.2M (59.8%); ±10%, $28.3M/$14.5M (66.2%, five of six venues). Largest displayed bid $3.4M at $1.000. Binance and Bitget are excluded; orders can cancel; hourly book is an average of one-minute observations. This is resting spot liquidity, not guaranteed support.
- Binance 30-day cumulative funding reached +0.18%, highest since October 2025, per CryptoQuant's original Nov 10 Quicktake. CryptoTicker reports its direct OKX query found 76 positive settlements out of the last 100 since Oct 9, cumulative +0.39%, current period +0.01%; raw response was not independently captured here. These are distinct venue/window measures.
- Binance XRPUSDT via cached public-market page: OI about $323.31M, -5.37% 24h, funding +0.0100%/8h. Coinalyze partial 2/22 coverage at 07:31 UTC: Binance long accounts 74.65%, Bybit 81.42%; taker buy share about 48.5% and 50.5%, respectively. Account ratios are not notional exposure.
- Liqwall all-exchange OI $1.15B at 10:22 UTC, -1.9%/24h; Kodexius seven contracts $639.27M at 06:09 UTC, weighted funding +0.0094%/8h. These universes differ; do not average.
- TokenPost reports Binance spot CVD about -4.33M XRP on Nov 9: sell-initiated trading dominated the measured window, not equivalent cash outflow.
- ETF correction: SoSoValue's $10.42M XRP ETF outflow belongs to **November 9**, not November 10; about $9.40M was Bitwise, $0.811M Canary, $0.213M 21Shares. Nov 3–6 were flat. Oct 12–Nov 9 cumulative net outflow was about $4.2M, roughly 0.3% of $1.24B net assets. Multiple outlets repeat the same SoSoValue dataset; this is one underlying source group, not independent confirmations.
- Binance theft-linked XRP: CryptoTicker reports a direct query at validated ledger 108,255,241 (Nov 11 06:44 UTC): 33,455,915 XRP moved from the last dormant wallet at 00:01 UTC into collection wallet `ryB7NESZcttqzRioiD5L6Kf5tFL87ktmx`; collection wallet held 29,466,416 XRP and had sent 32.34M XRP in 193 payments since the prior measurement. Elliptic is cited for mostly THORChain swaps into BTC. Explorer is JS-rendered and the ledger query was not independently replayed here. Payments are not proof of executed sales or final cash-out; buyer identity is unknown.

### Institutional and protocol developments
- CoinDesk reports Marc Asch will leave Ripple Prime at year-end 2026; Noel Kimmel, SVP, will take over leadership. Ripple Prime offers institutional prime brokerage, clearing and financing; Ripple says RLUSD is collateral for some products. This is not evidence of XRP collateral eligibility or XRP purchases.
- XRPL Foundation's 2027 protocol roadmap lists Quantum as a proposed, unapproved amendment using ML-DSA-44. Migration study is scheduled for H1 2027; development/review/audit in late 2027 or 2028; 640 build hours, 400 Ripple review hours, $215k–$255k estimated cost. Quantum-signed payment size estimated 5,331 bytes versus 1,704 baseline (3.13x). Activation requires validator approval; roadmap items are not promised. Draft spec #295 still records cross-implementation seed derivation mismatch, incomplete admin RPC support, and testing/audit gaps. Long-horizon security milestone, not near-term XRP demand.
- Exact phrase ASK Coin / “actual capital” / “SBIC, ChatGPT SBIC” remains unresolved at primary-source level. Regional SBIC entities remain distinct from SBI Holdings. Kamilah/Camilla YouTube inventory remains candidate-only pending platform-side channel verification.

### Prediction and safety
Forecast remains `NOT_ISSUED`. These web observations are not model-eligible: no Barrot collector raw receipts, trusted timestamps or replayable point-in-time feature-store admission were created in this run. Preserve competing hypotheses: crowded-long fragility; spot absorption/short-squeeze potential; macro-driven risk repricing; and positive funding caused by hedged basis/relative-value demand. Do not issue direction from this snapshot.

### Next actions
1. Finish 951-path semantic review, prioritizing V3 runtime, ingestion, point-in-time store, forecast ledger and public surfaces.
2. Add source-receipted direct funding histories and hourly Fuelmaps depth with explicit venue coverage and stale-age controls.
3. Reconcile derivatives by contract and XRP-denominated OI; never average incompatible vendor universes.
4. Correct ETF event date to Nov 9 and preserve SoSoValue source-group dependence.
5. Add XRPL Quantum proposal milestones and Ripple Prime leadership transition to the event timeline as non-price-causal context.
6. Resolve authoritative branch-protection/approval requirements, OAuth revocation evidence, 17 affected PR branch-tip copies and automatic Pages publication authorization.
7. Keep forecast issuance disabled until WORM anchoring, replayable point-in-time data, independent shadow outcomes and out-of-sample lift pass.

No merge, deployment, secret rotation/revocation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or PR closure occurred.


## Run22b — exact-head CI completion and additional options/macro/SBIC evidence

### Exact-head CI completion

The Run22 research/documentation commit `bd7daf29642bc79249ee32816d248cd357639b26` completed exact-head verification:

- Full repository suite: **3,423 passed, zero failures, eight subtests**, 79.78 seconds.
- Inclusive coverage: 59.98% for `barrot_agent`; total coverage report 60% across 23,403 statements. Coverage floor 53% passed.
- Core suite: 714 passed, zero failures, eight subtests.
- XRP public ingestion module coverage: 78% (2,156 statements).
- Wheel built and installed; packaged primary mission and canonical data assets loaded successfully.
- Six dependency manifests audited; zero known vulnerabilities reported.
- Fail-closed PR and push gates passed.
- Exact evidence: [CI 43010469954](https://github.com/Barrot-Agent/B-Agent/actions/runs/43010469954), full-suite job 130488490574; [dependency audit 43010469955](https://github.com/Barrot-Agent/B-Agent/actions/runs/43010469955), push audit 43010461200; [PR gate 43010470014](https://github.com/Barrot-Agent/B-Agent/actions/runs/43010470014), push gate 43010461199.
- Packaging warnings remain: deprecated license-table metadata and setuptools package-discovery warnings for `barrot_agent.data.missions` and `data.research`. The mission resource was nevertheless verified in the wheel. Coverage floor 53% remains below the previous 70% target.

### Options and tail-risk observation

Fuelmaps' Deribit daily capture at 2026-11-11 00:01 UTC, reference XRP $1.0564, reports 30-day/tenor IV in the high-50s to mid-60s: 65.5% for Nov 12 expiry, 66.0% Nov 13, 61.6% Nov 20, 59.4% Nov 27 and 59.0% Dec 25. Its historical daily 08:00 UTC settlement test reports 20 of 928 days beyond the options-implied 3-sigma band (2.2%) versus 0.27% under a normal curve. This is roughly 8.1 times the Gaussian reference, but it is a source-reported, model-specific historical statistic, not a forecast or calibrated future probability. Reproduce from raw options/settlement vintages before use.

The Nov 12 08:00 UTC 32-hour band is 1.0146–1.0982 at 1 sigma and 0.9373–1.1886 at 3 sigma; Nov 13 2d8h 1 sigma 1.0007–1.1120 and 3 sigma 0.9005–1.2357. The bands are options-implied, not forecasts. Fuelmaps notes XRP USDC-settled options have fewer strikes/expiries than BTC/ETH and one contract represents 1,000 XRP. OptimistFi's Nov 10 skew description and Fuelmaps' sign convention differ; preserve raw call/put IV and methodology rather than treating skew signs as directly comparable.

### Macro primary-source correction

BLS's November 10 primary October 2026 CPI release: headline +0.4% m/m, core +0.3%, food +0.5%, energy +0.7%, shelter +0.3%. Due the 2025 lapse in appropriations, October 2025 data were not collected and BLS cannot publish 12-month percentage changes for most October 2026 series. Consensus-surprise estimates come from market sources, not BLS. Source: https://www.bls.gov/news.release/archives/cpi_11102026.htm

### SBIC identity and ChatGPT activity — primary evidence

- Tokyo SBIC is Tokyo Small and Medium Business Investment & Consultation Co., Ltd., explicitly labelled SBIC East Japan; its official profile names Nagoya and Osaka as sister companies: https://www.sbic.co.jp/company/profile/ .
- Nagoya SBIC is SBIC Central Japan: https://www.sbic-cj.co.jp/company/about/ .
- Osaka SBIC is SBIC West Japan: https://www.sbic-wj.co.jp/profiles/profile/ .
- Tokyo SBIC's official June 12–13, 2025 training for investee companies covered generative AI/ML, ChatGPT use, Copilot, APIs, RAG and information-leak risk: https://www.sbic.co.jp/training/20250612co/ . This proves educational activity by SBIC East, not an OpenAI partnership.
- West Japan's October 23, 2024 ChatGPT seminar likewise remains educational activity, not partnership.
- Exact phrase “SBIC, ChatGPT SBIC” still has no primary-source match as a combined entity/partnership. Exact “actual capital” appears in secondary Evernorth coverage referring to proceeds contingent on warrant exercises; primary filings remain the authority for cash actually received/deployed. “ASK Coin” remains ambiguous; Permission Coin ASK is Base/Polygon LayerZero OFT, with no XRP/XRPL relationship verified. No Camilla/Kamilah Stevenson YouTube videos attributed without first-party channel verification.

The artifact now contains these options, macro and SBIC observations with provenance, limitations and non-model-eligibility flags. The addendum itself is a documentation-only successor commit and requires its own exact-head CI.


## Run22c — Evernorth actual-capital bridge and SBI/Ripple/Circle entity graph (primary filings)

The November 9, 2026 SEC Form 424B3 resolves the “actual capital” question. Do not collapse cash, token contributions, debt, contingent equity or resale registrations into one number.

- SBI announced a **$200M cash contribution** on October 21, 2025. The SEC filing identifies four SBI-controlled stockholders in the Advance Funding Subscription Agreements and records a 39.9% SBI Group voting-ownership limitation. The Advance Funding pool is **$214.05M aggregate cash** plus 600,000 XRP. The filing does not disclose each subscriber's exact cash allocation. Cross-document reconciliation: SBI's $200M is within the aggregate pool; do not add $200M to $214.05M.
- Advance Funding cash $214.05M was used to purchase **84,365,876.3625 XRP**, average **$2.53657/XRP**. Advance subscribers also contributed 600,000 XRP in kind. Delayed Funding added **$10.5M cash** and 200,000 XRP.
- In-kind XRP totals **388,910,554.061435 XRP**: 211,319,096.061435 from RippleWorks via Arrington XRP Capital Fund Series C; 126,791,458 under Ripple's Contribution Agreement; 50M from Larsen Lam Children's Remainder Trust; 600,000 Advance; 200,000 Delayed.
- Closing gross cash proceeds were **$272.6M before transaction expenses**: $224.6M private placements (Advance + Delayed) plus $48.0M SPAC trust after redemptions. This is not all XRP purchase cash.
- As of **October 9, 2026**, Evernorth reported approximately **473M XRP**. The token blocks reconcile to 84.365876M cash-purchased + 388.910554M in-kind = 473.276430M. Approximately **82.2% was contributed in kind** and **17.8% bought with cash**.
- At the Nov 11 10:21 UTC OKX quote of $1.0625, the cash-purchased tranche mechanically marks at about $89.64M versus $214.05M historical cost (-$124.41M / -58.1%). This is not a realized loss, accounting treatment or the value of all holdings.

### Separate financing and dilution

- Convertible notes: $30M principal, 4% PIK, due 2031, issued Oct 12. SEC 424B3 says approximately $30M net proceeds before transaction expenses; earlier secondary coverage described $29M after a $1M fee. Preserve discrepancy. Debt, not equity or proof of XRP purchase.
- Ripple Company Facility: $10M cap after Oct 7 amendment; $9.7M drawn as of Oct 7, 3.81%. Repayment due within five business days after Closing or earlier upon Ripple demand with five business days' notice; post-close repayment status not established.
- Evernorth Facility: separate $1M revolving facility, undrawn as of June 30, 2026.
- Cantor ELOC: up to 5,218,935 new shares, generally 97% of VWAP, subject to registration, 4.99% ownership and 20% volume caps. **Zero proceeds as of Nov 9.** $521,893.50 fee fully earned/non-refundable regardless of purchases; aggregate fee cap $1M. Contingent dilution capacity, not capital raised.
- Resale registration: up to 73,688,162 shares and 239,653 sponsor warrants. Evernorth receives no proceeds from selling-holder resales. Warrants could generate up to about $2.8M only if all are exercised for cash; no assurance.
- As of June 30, 2026, Evernorth reported no revenue, $265.6M loss, $0.1M unrestricted cash and $696.1M working-capital deficit. Pre-close historical figures, not current post-close liquidity.
- Disconfirming adoption evidence: the SEC prospectus says retail/commercial/payment use of XRP is limited and speculators make up a significant portion of users. It warns that adoption need not translate into XRP price appreciation and that permissioned DLTs, SWIFT, ACH and card networks compete with XRP.

### Ownership and SBI ecosystem

- SBI stockholders: SBI Venture Fund 2023A, SBI Venture Fund 2023B, SBI PE Holdings and SBI Holdings USA. Filing lists 9,431,914 Class A shares (36.1% of Class A) and 2,359,038 Class C shares (7.5% of Class C); separately, defined SBI Group voting cap was 39.9% as of Oct 9. Class C is ordinarily non-voting but convertible to Class A. Do not call 39.9% total economic ownership.
- Ripple held 1,678,382 Class A shares (6.4%); Chris Larsen 2,340,249 Class A shares (9.0%), subject to beneficial-ownership qualifications. Contributor Group voting power capped at 9.9%. Arrington Sponsor held 4,704,137 Class A (18.0%) and 29,033,708 Class C (92.5%); 4,215,479 Class A side-pocket shares tied to RippleWorks' XRP contribution carry RippleWorks voting instructions and specified consent rights.
- SBI's official June 2025 notice and May 2026 presentation report approximately **9% of Ripple equity** as largest external shareholder. SBI Ripple Asia is 60% SBI / 40% Ripple; SBI Remit uses XRP as bridge currency in Asian remittance corridors. This is equity in Ripple, not direct SBI XRP ownership.
- SBI Holdings and SBI Shinsei Bank invested **$50M total** in Circle at its June 5, 2025 NYSE listing ($25M each). SBI/Circle alliance dates to Nov 2023; SBI VC Trade offered USDC in Japan in Mar 2025; Circle SBI Japan KK was planned. This is USDC, not XRP.
- SBI separately announced **$200M cash** for Evernorth. SBI announced a $50M Startale investment in Mar 2026. JPYSC technology by Startale, issuer SBI Shinsei Trust Bank, distribution SBI VC Trade. SBI's strategy lists USDC, RLUSD and JPYSC as separate rails.
- SBI's May 2026 presentation reports Ripple balances of 5.10B XRP outside escrow and 33.20B in escrow as of Apr 27, 2026. These are Ripple balances presented by SBI, not SBI holdings and not an independent on-chain audit. SBI's presentation lists Ripple acquisitions: Metaco ($250M), Standard Custody (undisclosed), Rail ($200M), Hidden Road ($1.25B), GTreasury ($1B).

Primary sources: [Evernorth SEC 424B3](https://www.sec.gov/Archives/edgar/data/2092592/000162828026072223/evernorth-424b3.htm), [SBI $200M Evernorth announcement](https://www.sbigroup.co.jp/english/news/pdf/2025/1021_a_en.pdf), [SBI $50M Circle investment / Ripple stake](https://www.sbigroup.co.jp/english/news/pdf/2025/0609_a_en.pdf), [SBI FY2025 presentation](https://www.sbigroup.co.jp/english/investors/disclosure/presentation/pdf/260501presentations.pdf), [SBI/Startale investment](https://www.sbigroup.co.jp/news/2026/0326_16202.html), [SBI/RLUSD agreement](https://www.sbigroup.co.jp/news/2025/0822_15680.html), [SBI XRP remittance corridors](https://www.sbigroup.co.jp/news/2023/0906_14052.html).

These capital/corporate observations remain research-only until raw filings and presentations are hashed, timestamped and admitted into Barrot's point-in-time store. Forecast remains `NOT_ISSUED`.


## Run23 — 2026-11-11T11:35:50Z — repository, exchange reserves, Evernorth custody, stablecoin and model-risk reconciliation

### Repository and exact-head verification

- Main SHA: `84f28ee7755607236231545a14f3d093c1baaa85`. Integration parent inspected: `7a55848cab17f7cb2fd6549b0c463cc45efd47ae`.
- PR #1661: open, draft, mergeable-clean, 2,014 commits ahead/zero behind, 997 changed files (44 workflows, 953 other paths), 236,814 additions and 4,363 deletions. Complete trees: main 1,388 entries/1,288 files/86 workflows; integration 2,262 entries/2,153 files/87 workflows.
- Open PR inventory: 374 total, 360 draft and 14 non-draft. #1661 remains the sole consolidated integration workstream. No new PR was created.
- Exact parent-head CI on `7a55848` passed **3,423 tests, zero failures, eight subtests, 59.98% coverage, 93.67 seconds**. Wheel and installed Barrot V3/XRP mission verification passed. Six dependency manifests audited; zero known vulnerabilities reported. Dependency audit #43012397124 and fail-closed PR gate #43012397190 passed; push gate #43012390401 passed. [Full CI](https://github.com/Barrot-Agent/B-Agent/actions/runs/43012397193) · [full-suite job](https://github.com/Barrot-Agent/B-Agent/actions/runs/43012397193/job/130495019833).
- Main exact-head CI on `84f28ee` passed 718 tests/eight subtests. Main scheduled Cross Analysis #43007129290 succeeded. Main Pages build #42944862534 succeeded as an automatic push-triggered publication side effect.
- Local Git transport still fails DNS resolution for `github.com`; complete remote inspection succeeded through the GitHub API.

### Integration review corrections

- The current PR file list includes `hf_space/app.py`. The prior map claim that it was unchanged was incorrect. The PR changes it from v7.0 to v7.1 for safety: external inference disabled by default; explicit operator opt-in plus session consent; one configured provider and no silent fallback; public forecast endpoint returns `NOT_ISSUED`; legacy directional ledger rows are quarantined. Orbitron and Share Tech Mono CSS declarations are unchanged. The archival `.barrot/orbit/command_schema.json` and `ORBIT_REMOVED.md` remain in both main and integration, but no Orbit path changed in #1661 and no active Orbit runtime was reintroduced.
- Current blob-hash overlap: #1660 972/972 paths represented (959 identical, 13 different); #1643 670/670 (661 identical, nine different); #1642 seven/seven (zero identical, seven different); #1640 280/280 (253 identical, 27 different). These are overlap/supersession candidates, not confirmed duplicates. #1660 remains open/draft and three commits behind main.
- The current-map test contract was stale: it asserted `hf_space/app.py` was unchanged and recorded older CI evidence. Run23 corrects those assertions, records the font-preservation invariant and exact parent-head CI, and adds tests for connector over-permission, research-only provenance and non-WORM retention. One new research artifact path is added; post-commit PR count must be verified.

### Security and permissions

- GitHub repository metadata reports connector permissions `admin=true`, `maintain=true`, `push=true`, `pull=true`, `triage=true`. This exceeds least privilege. No main write, secret-value read or branch-protection bypass was performed.
- Main branch summary reports protected=true but `required_status_checks.contexts=[]` and `enforcement_level=non_admins`. Detailed branch-protection access returns HTTP 403. The visible fallback ruleset “Fall Back” is disabled. With connector metadata reporting admin=true, non-admin-only enforcement is not a sufficient merge gate.
- `.config/gh/hosts.yml` remains absent from main and active integration but present in all 17 rechecked current open-PR tips: #1653, #1650–#1644, #1643, #1642, #1640, #1320, #1318, #1317, #1269, #1255 and #1254. No file contents were read. Repository sync reports OAuth revoked, but provider-side revocation is unverified. No secret was rotated/revoked and no history was rewritten.
- Automatic GitHub Pages publication remains an unresolved side effect; explicit publication authorization is absent.

### XRP market and capital findings

**Spot and liquidity**
- OKX XRP-USDT: 1.0583, event time 11:33:13.571 UTC; bid 1.0581/ask 1.0582. Kraken XRP/USD: $1.06031 without provider event timestamp. Kraken USDT/USD: 0.99902. Normalized OKX reference is $1.0572629, about 0.2874% below Kraken's last. Asynchronous; not executable arbitrage.
- Fuelmaps' 09:00 UTC six-venue resting-book snapshot: $11.9M bids/$9.2M asks within 1%, $23.1M/$12.2M within 5%. Binance and Bitget excluded. More than two hours old at retrieval; resting orders can be cancelled.

**Exchange balances versus external transfers**
- XRP Insights reports 22.33B XRP in 701 attributed wallets across 24 exchanges at 08:00 UTC Nov 11; same-wallet change +1.3M XRP over seven days and -155.7M over 30 days. It includes cold storage and wrapped-token reserves: 48% labelled cold, 12% hot, 40% unclassified. Not tradable float, exchange liabilities or beneficial ownership.
- Regional attributed balances: South Korea 8.59B, United States 8.46B, Japan 1.38B. SBI VC Trade is listed at 56.9M XRP in two wallets, over 99% labelled cold; exchange custody, not SBI Holdings corporate XRP.
- Coinbase's 5.80B tracker balance includes a 149.6M cbXRP reserve annotation; Binance's 2.69B includes a 327.4M Binance-Peg reserve annotation. Wrapped backing may overlap DeFi categories; do not double count.
- TrackWhale's prior seven-day tracked external-transfer snapshot showed 501.72M inflows and 602.93M outflows, net -101.21M XRP. Different, older large-transfer universe; it disagrees in sign with same-wallet exchange-balance change. Preserve both; do not average or infer customer withdrawals from wallet-label changes.

**Evernorth actual capital and custody**
- SEC Form 424B3 dated Nov 9 reports approximately 473.276430M XRP at closing/as of Oct 9: 84.365876M cash-purchased using $214.05M advance-funding cash at about $2.53657/XRP, plus 388.910554M in-kind. SBI's announced $200M is included within the $214.05M pool; exact subscriber-level allocation is not disclosed. Gross closing cash was $272.6M before expenses, including $10.5M delayed cash and $48M SPAC trust; this is not all XRP purchase cash.
- XRP Insights' Nov 11 10:57 UTC ledger read attributes 103.129905M XRP to 13 Evernorth-linked wallets. It reports 370.346663M moved outside the attributed set, latest Oct 22. About 78.25% of the reported closing amount is outside that set. Destination ownership/custody is unknown; not proof of sale, disposal or loss of beneficial ownership.
- At normalized OKX reference, the cash-purchased tranche mechanically marks near $89.20M versus $214.05M historical cost (-58.33%). This is an unrealized mark on the cash-purchased tranche only, not realized loss or valuation of all Evernorth holdings.

**Wrapped XRP and stablecoins**
- Coinbase cbXRP page displayed 151,866,756.78 XRP reserve against 151,864,510.253 cbXRP supply (2,246.527 XRP excess), refreshed Nov 11 at 10:40 AM with timezone unspecified. Issuer-published proof-of-reserves, not independent custody audit. XRP Insights' 149.6M reserve annotation differs by about 2.26M; reconcile wallet coverage/vintage before adding.
- Ripple transparency reports $2.6329B RLUSD circulating and $2.748B reserves as of Nov 5 (104.37% coverage), with monthly independent CPA reserve reports. RLUSD issuance/custody is not automatically XRP demand or XRP collateral. Circle transparency page is dated Nov 9; static extraction did not expose numerical balances, so none are inferred.

**Derivatives, options and protocol risk**
- TradRadar 11:10 UTC snapshot: $1.57B OI, down 4.2%; funding +0.0092% per eight hours; $15.17M liquidations, $14.05M long and $1.13M short; 79.6% long accounts. Aggregator coverage is not interchangeable with other vendors.
- Fuelmaps' Nov 11 00:01 UTC options snapshot reports 20 of 928 daily 08:00 UTC outcomes beyond its options-implied 3-sigma band (2.16%) versus 0.27% Gaussian reference, about eight times. Source-reported, not independently reproduced. It motivates a Student-t/empirical-quantile baseline experiment; not a future probability or forecast.
- XRPL Foundation's 2027 roadmap lists ML-DSA-44 quantum signatures as proposed, not approved; validator vote required. Study target H1 2027 and development/review/audit late 2027 or 2028. Long-horizon security milestone, not near-term demand.
- Ripple Prime leadership transition (Marc Asch to Noel Kimmel at year-end 2026) is secondary-source reporting attributed to a company spokesperson. RLUSD collateral use for some prime products is distinct from XRP collateral eligibility.

### Prediction-engine audit

- 46 source definitions: 42 hourly, two weekly CFTC and two optional non-commercial XRPL nodes; 44 scheduled. `xrp_exchange_balances_json` is scheduled but digest-only because raw redistribution permission is not explicit.
- Raw receipts use SHA-256 content addressing and a per-run hash chain; not independent WORM. Workflow retains raw artifacts 90 days, per-run feature-store checkpoints seven days and daily backups 90 days. SQLite row guards are not adversarially tamper-proof.
- Scheduled walk-forward evaluation sets embargo equal to forecast horizon; overlap-adjusted effective sample size uses greedy non-overlapping target intervals. Residual serial dependence/shared-source correlation remain uncorrected.
- Four baselines: naive class prior, momentum sign, mean-reversion sign and Gaussian volatility normal. The options tail statistic requires reproducing raw vintages and testing heavy-tailed/empirical alternatives. A scenario/counter-hypothesis generator is not implemented; the ledger alternatives field is only a contract.
- Readiness requires at least 100 OOS and 100 shadow raw samples, at least ten non-overlapping target windows in each, two source groups, stable drift, weighted calibration error <=0.05, lower Brier and log loss than all four baselines, and trusted Ed25519 evaluator attestation. No successful main-branch collector run, WORM archive, production evaluator key or OOS lift is verified.

### Identity, platforms and forecast

- SBIC East/Tokyo, Central/Nagoya and West/Osaka remain resolved as distinct regional SME investment companies, not SBI Holdings. Exact “ASK Coin”, “actual capital” and “SBIC, ChatGPT SBIC” combined phrase remain unresolved at primary-source level. Kamilah/Camilla YouTube attribution remains gated on first-party identity verification.
- ChatGPT GitHub connector is verified in this session but repository metadata reports admin=true. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks have no new authenticated data flow. Copilot has no formal approval on #1661. LunaRoute remains repository-declared but endpoint authentication/data flow unverified. No external-model data transfer occurred.
- Forecast remains `NOT_ISSUED`. All Run23 web observations lack Barrot raw receipts and are excluded from model features. No directional forecast, paper trade or real-money action occurred.

### Backlog and decision

- #1661: blocked, sole consolidated integration draft. Parent head passed exact CI; Run23 documentation/test-contract commit requires its own exact-head CI. Draft, zero approvals/reviews, admin-exempt branch protection, empty required-check contexts, disabled fallback ruleset, overprivileged connector, 953-path semantic review incomplete, Pages authorization absent.
- #1660: superseded-source candidate; retain until successor merge and main verification. #1640/#1642/#1643: overlap candidates with differing blobs; reconcile before closure. #1644–#1650 and #1254/#1255: dependency candidates; preserve until compatibility/security reconciliation.
- Preserve unique/unreviewed #1608, #1610, #1611, #1612, #1614, #1317, #1318, #1320, #1269, #1653, #1655 and #1659. No source PR was closed; no confirmed duplicate closure occurred.
- Next: complete exact-head CI on the Run23 update; reduce GitHub connector permissions to least privilege and resolve branch-protection admin exemption; finish semantic review; verify OAuth revocation and additively remediate the 17 branch tips; obtain Pages authorization; build WORM/timestamp anchoring, heavy-tailed baselines and scenario generation. Keep forecasts disabled.

No merge, deployment, secret rotation/revocation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or PR closure occurred.

## Run24 reconciliation — 2026-11-11T12:05Z–12:29Z

The canonical map records Runs24 through 24e; this handoff file had not yet been synchronized with those updates. Key additions:

- Evernorth reported 473.276430M XRP at closing/as of October 9: 84.365876M cash-purchased using $214.05M advance cash and 388.910554M in kind. SBI's announced $200M is included in the $214.05M pool, not additive; subscriber-level allocation is undisclosed.
- XRP Insights' November 11 ledger read attributed 103.129905M XRP to 13 Evernorth-linked wallets. Another 370.346663M was outside that attributed wallet set, with destinations unresolved. This is not proof of sale, loss or disposal.
- SBI's $50M Circle investment is split $25M SBI Holdings and $25M SBI Shinsei Bank. This is equity into Circle, not XRP purchase capital.
- Run24e exact-head CI on a41fa failed two current-map assertions after 3,425 passes. These were evidence-map contract assertions, not runtime XRP-engine failures; the fields were corrected before the Run25 code-head verification.

## Run25 — 2026-11-11T13:02:17Z

### Repository and CI

- Main SHA: 84f28ee7755607236231545a14f3d093c1baaa85.
- Existing integration branch: integration/xrp-v3-unified-main-20261111; verified code parent 7155eede2a852355e5626c4f00c9c79a5ed1d1c7, 2,020 commits ahead and zero behind.
- PR #1661: open, draft, mergeable; 1,000 changed files (44 workflows, 956 other paths), 238,998 additions and 4,363 deletions. Complete trees: main 1,388 entries/1,288 files; integration 2,265 entries/2,153 files. Paginated PR file page 11 returned zero, confirming the 1,000-file listing is complete.
- Open PR inventory: 374 total, 360 drafts and 14 non-drafts. PR #1661 remains the sole consolidated integration workstream. No branch or PR was created.
- Exact code parent 7155eede: 3,427 passed, zero failures, eight subtests, 59.98% coverage, 96.83 seconds. Full-suite job 130523332780; core job 130523332437; wheel and installed Barrot V3/XRP mission verified.
- Six-manifest dependency audit passed with zero known vulnerabilities: run 43020832903/job 130523332180. Fail-closed PR gate passed: run 43020833177; automatic merge remains disabled.
- The atomic Run25 handoff/map/research commit is documentation/evidence only and requires its own exact-head CI. Do not substitute parent-head results for that run.
- Main scheduled Cross Analysis succeeded (43023990234). Main read-only Pillars Consistency Check failed (43025487840): GITHUB_APP_ID, PRIVATE_KEY and INSTALLATION_ID missing; Databricks HTTP 403; Hugging Face BUILD_ERROR. This is a platform-health failure, not the main Python test suite.

### Current XRP market snapshot

- OKX XRP-USDT at 12:34:10.894 UTC: 1.0527; rolling 24h open 1.0796, high 1.0854, low 1.0311, volume 68.19M XRP. Kraken last $1.05602 with no provider event timestamp; USDT/USD $0.99903. Normalized OKX reference is about $1.05168, approximately 0.41% below Kraken. Asynchronous and freshness-sensitive; not executable arbitrage.
- Fuelmaps 12:00 UTC six-venue spot book: $10.3M bids/$9.4M asks within 1%; $19.3M/$12.6M within 5%. Binance and Bitget excluded; resting orders can be cancelled.
- TradRadar 12:10 UTC: OI $1.57B (-4.41%), funding +0.0087%/8h, at least $15.0M liquidations ($13.87M long), 79.7% long accounts. Liqwall 12:52 UTC: OI $1.15B (-2.1%), funding +0.0086%, $16.9M liquidations ($15.8M long), 75.2% Binance accounts long. Different universes; do not average.
- OptimistFi/Deribit 12:00 UTC: 30-day ATM IV 58.3%, 25-delta skew -0.6 points (puts richer), put/call 0.55, Dec25 OI $47.2M. Near expiries remain more put-rich; same-provider 30-day skew changed sign versus the earlier +0.3 snapshot.
- Alpha Finance through Nov10: daily -$7.6M, Nov9 -$10.4M, 30-session +$1.3M, cumulative net inflow $1.71B. XRP Insights' wider tracker reports -9.568M XRP across Nov9–10 and 1.1856B XRP held. Different universes/windows; do not average.
- XRPL.to Token Market reports 7.26M XRP/197,168 trades, 25.55M XRP AMM liquidity and 6.41M XRP order-book activity. Its separate DEX Volume & Stats page reports 7.74M XRP/189,675 trades, with 6.91M order-book and 0.836M AMM volume. Preserve the discrepancy. Both are issued-token trading on XRPL, not native XRP/USD turnover or institutional XRP inflow.

### Evernorth capital and liquidity — material counter-evidence

The latest SEC Form 424B3 (accession 000162828026072223) materially qualifies the institutional-accumulation thesis:

- Evernorth had not generated revenue as described in the filing. Historical June 30, 2026 figures include $0.1M unrestricted cash, $696.1M net working-capital deficit, $340.9M accumulated deficit and $265.6M reported operating loss.
- Six-month net loss was $188.1M, but operating cash used was about $1.33M; the filing identifies $264.1M digital-asset impairment and a $77.5M non-cash gain on refundable investor advances. Do not equate accounting loss with cash burn.
- Ripple's company facility was increased to $10M; $9.7M had been borrowed as of October 7. This is related-party debt, not equity.
- A $30M 4% PIK convertible senior note was funded October 12. The holder chooses cash or share settlement on conversion. The filing discloses conditional cash-settlement exposure up to $120M (4x principal) and an 8% yield-to-put on specified default/fundamental-transaction events. These are conditional risks, not currently due cash payments.
- The company states note proceeds are for general corporate purposes, including possible XRP acquisition; this filing does not prove the $30M was used to buy XRP.
- Cantor ELOC permits up to 5,218,935 shares at 97% of VWAP subject to registration, price, volume and ownership conditions. No ELOC proceeds had been received as of the prospectus. It is contingent capacity, not current cash.
- The filing warns XRP is less liquid than cash and the company may need to sell XRP to meet cash obligations in adverse conditions.

This creates a genuine counter-hypothesis: the treasury represents institutional XRP exposure, but its funding structure and cash obligations can create future selling pressure. Keep the $200M SBI announcement, $214.05M advance cash, in-kind XRP, Ripple debt, $30M notes and undrawn ELOC as separate ledger categories.

### Stablecoins, custody and network relationships

- Standard Chartered's RLUSD custody on XRPL is live through its DIFC branch; the Ripple/LMAX collateral integration remains planned, not proven live.
- SBI VC Trade handles RLUSD in Japan; SBI Shinsei Trust Bank issues JPYSC and SBI VC Trade distributes it. JPYSC reserve investment into Japanese government bonds is separate reserve management, not XRP collateral.
- SBI Ripple Asia's tokenized-deposit concept proof assumes XRPL/MoneyTap infrastructure; it is not verified production XRP settlement volume.
- Stablecoin distribution, custody, tokenized deposits and treasury balances do not automatically establish XRP bridge demand, XRP collateral usage or new spot purchases.

### Nine-platform and security state

- ChatGPT GitHub API access is verified, but repository metadata reports admin=true, maintain=true, push=true, pull=true and triage=true. This exceeds least privilege.
- Claude, Grok, Gemini and Codex remain unauthenticated/unverified; Copilot has no formal approval; Kaggle is untested; Databricks returned HTTP 403; Hugging Face reports BUILD_ERROR. LunaRoute is repository-declared but endpoint authentication/data flow is unverified. No external-model data transfer occurred.
- Main branch-protection details return HTTP 403. The visible fallback ruleset is disabled. Required approval/check policy is not verified. With admin=true, non-admin-only enforcement is not an adequate safety boundary.
- .config/gh/hosts.yml remains absent from main and #1661 but present in all 17 previously rechecked affected open-PR tips. Contents were not read. Repository notes report OAuth revoked, but provider-side revocation is unverified.
- Automatic GitHub Pages publication remains a merge side effect without explicit authorization.

### Prediction-engine status

- Implemented: 46 source definitions, 44 scheduled public sources, read-only collector, SHA-256 receipts/hash chain, point-in-time SQLite store, four deterministic baselines, chronological purge/embargo walk-forward evaluation, calibration/PSI drift diagnostics and fail-closed Ed25519 evaluator-attestation contract.
- Not production verified: independent WORM/timestamp anchor, replayable historical feature store, synchronized multi-venue spot/L2/derivatives/flow/collateral history, vintage-aware macro timeline, scenario/counter-hypothesis generator, production evaluator key, sufficient shadow outcomes and out-of-sample lift over all four baselines.
- Run25 web observations were not captured by Barrot's raw collector and are excluded from model features.
- Forecast remains NOT_ISSUED. No directional forecast, paper trade or real-money action occurred.

### Backlog and decision

- #1661: blocked, sole consolidated integration PR; draft, zero formal approvals/reviews, incomplete semantic review of 956 pre-existing non-workflow paths, branch-protection requirements not visible, overprivileged connector, credential-path remediation and Pages authorization unresolved.
- #1660: superseded-source candidate; retain until successor merge and main verification.
- Preserve unique/unreviewed work including #1653, #1614, #1611, #1610, #1612, #1269 and #1608; reconcile overlap candidates #1640, #1642, #1643, #1644–#1650, #1317, #1318, #1320, #1254 and #1255 only after verified successor merge. No source PR was closed.
- Next: verify exact-head CI on the atomic Run25 commit; reduce connector permissions; resolve GitHub App, Databricks and Hugging Face health; obtain branch-protection/approval visibility; verify OAuth revocation and additively remediate the 17 affected tips; complete semantic review; resolve Pages authorization; then consider merge only if every gate passes.

No merge, deployment, secret rotation/revocation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or PR closure occurred.

## Run25b — SEC entity-level scope correction — 2026-11-11T13:15:41Z

A closer read of SEC Form 424B3 separates Pubco (Evernorth Holdings Inc., the parent Company) from the Evernorth operating subsidiary. The previous Run25 summary quoted the subsidiary figures correctly but did not clearly attribute the parent-level financing instruments.

- Pubco parent, June 30, 2026: $0.8M unrestricted cash, $3.7M net working-capital deficit, $3.1M accumulated deficit, $2.2M operating loss and $2.138M operating cash used.
- Evernorth operating subsidiary, June 30, 2026: no revenue generated; $0.1M unrestricted cash, $696.1M net working-capital deficit, $340.9M accumulated deficit, $265.6M operating loss and $188.1M six-month net loss. Its six-month operating cash use was $1.330M, not $188.1M. The latter includes $264.1M non-cash digital-asset impairment partly offset by a $77.5M non-cash fair-value gain.
- Pubco Company Facility: $10M limit, $9.7M drawn as of October 7 at 3.81%. The filing says amounts were subject to repayment within five business days after the Closing Date or earlier on five business days' notice from Ripple; the later repayment/current balance is not established by this excerpt.
- Separate Evernorth Facility: $1M limit, undrawn as of June 30.
- Pubco convertible note: $30M 4% PIK note funded October 12. The holder chooses cash or share settlement; conversion value is capped at 4x principal, and specified default/fundamental-transaction events carry an 8% yield-to-put. These are conditional terms, not currently due cash payments.
- Pubco Cantor ELOC: up to 5,218,935 shares at 97% VWAP, subject to registration, price, volume and ownership conditions; zero proceeds as of the prospectus.
- The filing says the $30M note proceeds may fund general corporate purposes including XRP acquisition; it does not prove that those proceeds were used to buy XRP.

This correction avoids mixing subsidiary financials with parent-level obligations. Primary source: https://www.sec.gov/Archives/edgar/data/2092592/000162828026072223/evernorth-424b3.htm
