# Barrot XRP Intelligence — Run66

- Run start: 2026-11-12 17:30:06 UTC
- Mission priority: XRP intelligence and prediction-engine mastery
- Protected foundation: Barrot V3 execution, orchestration, safety and verification
- Forecast status: NOT_ISSUED

## Repository and integration

| Item | Verified value |
|---|---|
| Main SHA | 84f28ee7755607236231545a14f3d093c1baaa85 |
| Integration branch | integration/xrp-v3-unified-main-20261111 |
| Integration head | 1d23263f5a649d404a4db7dfe88910f30003a21c |
| Ahead / behind main | 2,134 / 0 |
| Main / integration tree entries | 1,388 / 2,328 |
| Tree delta | 931 added, 139 modified, 0 deleted, 1 mode-only |
| PR #1661 | Open, draft, 1,071 changed files, +298,691 / -4,492 |
| Changed workflows | 49 |
| Other changed paths | 1,022 |
| Open PR inventory | 374 total: 360 drafts, 14 non-drafts |
| Reviews / review threads on #1661 | 0 / 0 |

## Exact-head CI

All three workflow runs below target exact head 1d23263f5a649d404a4db7dfe88910f30003a21c.

- Full CI: [43269618715](https://github.com/Barrot-Agent/B-Agent/actions/runs/43269618715) — completed successfully.
- Full repository suite: 3,512 passed, 8 subtests passed, 0 failures, 95.57 seconds.
- Inclusive coverage: 61.42% against the new 53% full-repository floor.
- Core suite: 721 passed, 8 subtests passed, 0 failures, 13.67 seconds; core coverage 76% against the retained 70% floor.
- Wheel built and installed; installed package verified Barrot V3, the primary XRP mission and canonical data assets.
- Non-blocking packaging warning: setuptools reports barrot_agent.data.missions absent from explicit package configuration; the required mission resource was nevertheless verified in the built wheel and after installation.
- Dependency audit: [43269618792](https://github.com/Barrot-Agent/B-Agent/actions/runs/43269618792) — six manifests audited, no known vulnerabilities.
- Fail-closed gate: [43269618990](https://github.com/Barrot-Agent/B-Agent/actions/runs/43269618990) — success means automatic merge remains disabled, not that the PR was approved.
- Main baseline on unchanged SHA 84f28ee: run 42944864014, 718 full-suite tests and 485 core tests passed.

## PR overlap and backlog

Blob comparisons were performed against current integration tree 1d23263.

| PR | Changed paths | Identical blobs | Different blobs | Source-only | Classification |
|---|---:|---:|---:|---:|---|
| #1660 | 972 | 939 | 33 | 0 | Superseded-source candidate; inspect 33 differences |
| #1643 | 670 | 661 | 9 | 0 | Superseded-source candidate; inspect 9 differences |
| #1640 | 280 | 234 | 46 | 0 | Superseded-source candidate; inspect 46 differences |
| #1642 | 7 | 0 | 7 | 0 | Unique prediction work; preserve |
| #1653 | 7 | 0 | 1 shared difference | 6 | Unique graph work; preserve |
| #1655 | 8 | 0 | 5 shared differences | 3 | Unique structural work; preserve |

No source PR was closed. No new branch or PR was created.

## Workflow and security audit

All 49 changed workflow patches were reviewed. Important findings:

- xrp-public-ingestion.yml exists on integration, not main. It is guarded to main, read-only, uses persist-credentials=false, requires no external API secrets, and stores GitHub Actions artifacts for 90 days.
- That collector is DESIGNED, not EXECUTED on main. The current main branch has no XRP ingestion workflow.
- GitHub Actions artifact retention is not independent WORM storage or a trusted timestamp anchor.
- Automatic merge is explicitly disabled. The fail-closed workflow does not approve, label or merge.
- Hugging Face synchronization is disabled/quarantined; self-hosted brain synchronization has a hard-false job guard.
- External workflows for model upload, Space restart, Databricks operations, Kaggle, Groq-backed research and paper-trading artifacts require manual/per-run gates. None was triggered.
- Cross Analysis runs hourly and after successful Knowledge Signal Cycle completion, has contents: read, and writes artifacts only.
- Release workflow triggers on version tags v*.*.*; a normal main push does not publish a release.
- Main's latest Cross Analysis run 43263247610 succeeded.
- Main's Pillars Consistency Check 43223351964 failed because GITHUB_APP_ID/PRIVATE_KEY/INSTALLATION_ID were missing, Databricks returned HTTP 403, and Hugging Face reported BUILD_ERROR.

Security controls remain unresolved:

- GitHub connector reports admin=true, maintain=true, push=true, pull=true and triage=true; this is overprivileged.
- Branch-protection API returned HTTP 403 Resource not accessible by integration.
- Fallback ruleset #10863829 is disabled.
- Repository setting allow_auto_merge is true, but the active Barrot gate explicitly keeps automatic merging disabled.
- GitHub Pages publication behavior/authorization remains unresolved and was not triggered.

## XRP spot and market structure

### Direct spot observations

| Source | Event / retrieval | Last | Bid | Ask | Other fields |
|---|---|---:|---:|---:|---|
| OKX XRP-USDT | Provider event 17:19:50.169 UTC | 1.0226 | 1.0228 | 1.0229 | 24h open 1.0784; high 1.0807; low 1.0164 |
| Kraken XRP/USD | Retrieved after 17:30 UTC; provider timestamp absent | 1.02601 | 1.02601 | 1.02602 | 24h open 1.05104; high 1.07248; low 1.01516; volume 26.927M XRP; VWAP 1.0396 |
| Kraken USDT/USD | Provider timestamp absent | — | 0.99896 | 0.99897 | Mid 0.998965 |

Normalized midpoint gap is approximately 0.413%. Quotes are asynchronous and not executable arbitrage. The 24-hour open fields materially disagree; they are not combined into one return.

### Order-book depth

Fuelmaps six-venue aggregate, snapshot 17:00 UTC, midpoint $1.0245. Binance and Bitget are excluded.

| Distance from midpoint | Bids USD millions | Asks USD millions | Bid share |
|---|---:|---:|---:|
| 0.5% | 7.7 | 6.1 | 55.8% |
| 1% | 12.5 | 9.5 | 56.8% |
| 2% | 18.2 | 11.2 | 61.9% |
| 5% | 29.7 | 12.1 | 71.0% |
| 10% | 33.1 | 14.8 | 69.1% |

The aggregator uses hourly snapshots and can be up to 65 minutes old. Resting orders are cancellable; this is not executable depth.

### Derivatives disagreement

| Provider | Timestamp | OI | Other observations |
|---|---|---:|---|
| Sharpe.ai | 14:00 UTC | $1.23B | 22 venues |
| Liqwall | 02:52 UTC | $1.16B | Funding +0.0057%/8h; Binance long accounts 75.3%; $4.1M liquidations |
| Kodexius | 12:34 UTC | $633.16M | 7 contracts; funding +0.0082%/8h; $1.2B volume |
| Alpha Finance | 13:40 UTC | $2.24B | $2.27B volume; $9.1M long vs $1.2M short liquidations; modeled clusters at $1.0381 and $1.0174 |

These are different provider universes and contract scopes. Do not average OI or modeled liquidation levels. Positive funding and long-account concentration coexist with long liquidations; this is positioning risk, not a directional signal.

### ETF flows

- XRP Insights, six US spot funds plus BITW: +355,000 XRP on Nov. 11; -9.213M XRP across Nov. 9–11; reported holdings approximately 1.19B XRP.
- Alpha Finance, five funds: -$7.6M Nov. 10; +$1.3M over 30 sessions; $1.71B cumulative net inflow.
- ByKaranteli, six funds: -$7.6M Nov. 10; -$18M over five sessions; $1.79B cumulative net inflow.
- TheXRPInvestor tracks 12 products: six spot, four derivatives, one index and one income product; reports 1.19B XRP trust holdings and $1.26B AUM.

Fund cohorts, denominators and settlement cutoffs differ. Missing observations are not assumed to be zero.

### Exchange flows and attributed balances

- XRP Insights: 706 attributed wallets across 24 exchanges, 22.34B XRP reported.
- Same-wallet change: +45.8M XRP over seven days and -180.9M over 30 days.
- Naive change: +61.4M and +346.7M respectively; new wallet additions explain part of the difference.
- TrackWhale large-transfer set: 166.83M XRP inflows, 221.61M outflows, net -54.78M over seven days; largest transfer 168.42M XRP, unknown wallet-to-wallet.

Attributed balances include cold storage and wrapped reserves, not just tradable float. TrackWhale is not complete exchange-reserve accounting.

### XRPL lending and collateral

At the latest reviewed validator snapshot, SingleAssetVault had 23 votes, LendingProtocol 22 and LendingProtocolV1_1 22; 29 are required. Native XRPL lending is not active and has no 14-day activation countdown. SBI customer lending of JPYSC is not XRP collateral. Coinbase cbXRP collateral is wrapped Base exposure, not proof of native XRP selling.

## Institutional rails and capital separation

- SBI VC Trade reported JPYSC handling balance above ¥30B and lending balance above ¥10B on Nov. 2. SBI Shinsei Trust Bank is issuer; SBI VC Trade distributes; Startale co-developed. Customer lending of JPYSC is not XRP collateral.
- SBI Group is a founding validator of Circle Arc. Arc uses USDC for network fees; it is a parallel institutional rail, not XRPL.
- Coinbase cbXRP proof-of-reserves snapshot: 152,087,932.36 XRP reserves versus 152,085,685.83 cbXRP supply. Morpho Nov. 6 snapshot: 119.9M cbXRP collateral and $59.2M USDC debt; a 10% oracle-decline stress model showed $8.84M near liquidation. This is wrapped collateral, not native XRP collateral.
- RLUSD chain snapshot Nov. 12 10:48 UTC: approximately $2.708B total, $885.25M on XRPL, $1.806B on Ethereum and $16.10M on Base. DefiLlama reports $2.728B, a $20.37M difference. Preserve both series.
- Evernorth's 473.276M XRP closing treasury comprised approximately 388.911M in-kind and 84.366M cash-purchased XRP. The 73.688M registered resale shares are potential shareholder supply, not issuer proceeds or proof of sales. ELOC capacity, PIK debt and treasury XRP remain separate capital categories.
- Ripple Prime's disclosed institutional collateral is RLUSD, not XRP. Coinbase's RLUSD distribution is live across stated retail/prime/exchange channels; Global Exchange collateral support was described as forthcoming, not verified live.
- Ripple National Trust Bank and Coinbase National Trust Company charter approvals expand trust/custody infrastructure; approval does not prove XRP collateral utilization or operating scale.

## Identity and exact-phrase research

### Japan SBIC

Primary company profiles identify three distinct regional sister companies under the Small and Medium Business Investment & Consultation Company Act:

- SBIC East Japan: Tokyo Small and Medium Business Investment & Consultation Co., Ltd.
- SBIC Central Japan: Nagoya Small and Medium Business Investment & Consultation Co., Ltd.
- SBIC West Japan: Osaka Small and Medium Business Investment & Consultation Co., Ltd.

They are not SBI Holdings subsidiaries. Tokyo SBIC's ChatGPT/AI training is educational activity, not an OpenAI partnership. SB OAI Japan GK is a separate SoftBank Group/OpenAI joint venture, not SBI Holdings and not a regional SBIC.

### ASK Coin and actual capital

- CoinMarketCap Askcoin token UCID 4640 is a preview listing with zero reported total/circulating supply.
- CoinMarketCap's Ask Coin exchange listing for askcoin.net is separate, inactive/untracked, with reserve data unavailable.
- Permission Coin (UCID 7105, Base/Polygon) and GoAsk (Ethereum) are separate ASK identities.
- No XRPL deployment or common issuer was verified.
- “Actual capital” is not a standardized XRP metric. Separate cash subscriptions, in-kind contributions, debt, facilities, resales, reserves and realized deployment.

### Camilla/Kamilah Stevenson

A first-party course site identifies Dr. Kamilah Stevenson / The Wealth Doctor. Third-party indexes list multiple YouTube candidates, including @drkamilahstevenson, plus numerous lookalikes. The first-party site does not cross-link a YouTube channel. No videos were attributed or inventoried. Third-party articles refer to claims about Japanese bank pilots, but no banks or primary performance records were supplied; treat these as unverified leads.

## Prediction engine

Implemented on integration:

- 47 public source definitions, 45 scheduled.
- Read-only public-data collector.
- SHA-256 raw-source receipts and hash-chain prototype.
- Point-in-time SQLite feature store.
- Event timeline and scenario/counter-hypothesis assembly.
- Naive, momentum, mean-reversion and volatility baselines.
- Chronological walk-forward with purge/embargo.
- Probability calibration and PSI drift diagnostics.
- Fail-closed forecast ledger with Ed25519 evaluator attestation.

Outstanding: independent WORM storage, trusted timestamp anchoring, replayable historical feature reconstruction, production evaluator key, independent shadow outcomes and measured out-of-sample lift over all four baselines.

Run66 web/API observations were not captured through Barrot's byte-exact RawReceiptArchive pipeline and are model-ineligible. No directional forecast, probability distribution, paper trade or real-money action was produced.

## Nine-platform coordination

- ChatGPT: GitHub authentication/data flow tested; connector permissions overprivileged.
- Claude, Grok, Gemini and Codex: authentication/data flow unverified.
- Copilot: no formal PR approval observed.
- Hugging Face: last tested BUILD_ERROR.
- Kaggle: untested; no submission.
- Databricks: last tested HTTP 403; no write.
- No external-model evidence transfer occurred.

## Merge decision and next actions

**No merge.** PR #1661 remains draft with zero approvals/reviews. Branch-protection details are inaccessible (HTTP 403); fallback ruleset is disabled; connector permissions are overprivileged; 1,022 non-workflow paths still require semantic review; main XRP ingestion has not run; Pages publication authorization remains unresolved.

Next:
1. Complete semantic review of the 1,071-file diff, prioritizing Barrot V3 runtime, XRP collector, feature store, receipt archive, forecast ledger, public interfaces and workflow side effects.
2. Resolve branch-protection visibility and least-privilege GitHub access; verify Pages publication behavior before any merge.
3. After a separately authorized merge, verify main ingestion executes and raw receipts are independently anchored.
4. Build replayable synchronized spot/L2/derivatives/ETF/exchange-flow/collateral history; complete leakage-safe walk-forward and independent shadow evaluation.
5. Keep directional forecast issuance disabled until independent-window, baseline-lift, calibration and shadow gates pass.

No merge, deployment, secret rotation, Space restart, Databricks write, Kaggle submission, external-model transfer, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or source PR closure occurred.

## Sources

- OKX ticker: https://www.okx.com/api/v5/market/ticker?instId=XRP-USDT
- Kraken XRP/USD: https://api.kraken.com/0/public/Ticker?pair=XRPUSD
- Kraken USDT/USD: https://api.kraken.com/0/public/Ticker?pair=USDTUSD
- Fuelmaps order book: https://fuelmaps.io/order-book/
- Sharpe.ai: https://sharpe.ai/markets/xrp
- Liqwall: https://liqwall.com/coins/xrp
- Kodexius: https://kodexius.com/cryptocurrencies/xrp
- Alpha Finance: https://alphafinance.io/liquidation-heatmap/xrp/
- XRP Insights: https://xrp-insights.com/data
- TrackWhale: https://trackwhale.io/xrp-whale-tracker
- TheXRPInvestor: https://thexrpinvestor.com/etf
- SBI VC Trade JPYSC: https://www.sbivc.co.jp/newsview/251102_000
- Circle Arc: https://www.circle.com/pressroom/circle-launches-arc-public-testnet
- Coinbase cbXRP proof of reserves: https://www.coinbase.com/en-gb/cbxrp/proof-of-reserves
- Ripple RLUSD: https://ripple.com/products/stablecoin/features/
- SEC Evernorth prospectus: https://www.sec.gov/Archives/edgar/data/2092592/000162828026072223/evernorth-424b3.htm
- Tokyo SBIC: https://www.sbic.co.jp/company/
- Nagoya SBIC: https://www.sbic-cj.co.jp/company/about/
- Osaka SBIC: https://www.sbic-wj.co.jp/profiles/profile/
- Tokyo SBIC seminars: https://www.sbic.co.jp/seminar/
- Askcoin token listing: https://coinmarketcap.com/currencies/askcoin/
- Ask Coin exchange listing: https://coinmarketcap.com/exchanges/ask-coin/
- Permission Coin: https://coinmarketcap.com/currencies/permission-coin/
- Kamilah Stevenson first-party course site: https://learn.kamilahstevenson.com/
- Reuters Japan wholesale inflation: https://www.reuters.com/world/asia-pacific/japan-wholesale-inflation-accelerates-keeps-alive-boj-rate-hike-view-2026-11-12/
- Reuters yen intervention warning: https://www.reuters.com/world/asia-pacific/japans-top-currency-diplomat-renews-volatility-warning-yen-nears-key-160-level-2026-11-12/


## Run66 institutional addendum — Doppler / SBI entity separation

Primary-source reconciliation completed after the initial Run66 artifact:

- SBI Holdings' official group profile identifies SBI Digital Finance Inc. as a crypto-asset lending company operating HashHub Lending. SBI Group held 51% of voting rights as of March 31, 2026. SBI Digital Finance is a distinct company, not SBI Ripple Asia, SBI Digital Markets, SBI VC Trade or SBI Shinsei Trust Bank.
- Doppler Finance's July 13, 2026 official announcement confirms a strategic development partnership with SBI Digital Finance to develop institutional XRP/digital-asset infrastructure in Japan. Its stated work areas include XRP and tokenized-asset infrastructure, compliance, liquidity, financing, collateral management and capital efficiency. The announcement gives no named institutional clients, lending rates, collateral terms, launch date or live product availability.
- A separate December 17, 2025 MOU is between SBI Ripple Asia and Doppler to explore XRP-yield infrastructure and RWA tokenization on XRPL. Doppler identifies SBI Digital Markets as institutional custodian for that initiative. Do not conflate this with the July 2026 SBI Digital Finance partnership.
- SBI Ripple Asia is the SBI Holdings/Ripple joint venture; SBI Digital Markets is a subsidiary of SBI Digital Asset Holdings; SBI Digital Finance is the HashHub Lending company; SBI VC Trade distributes/trades assets; SBI Shinsei Trust Bank issues JPYSC. These are distinct legal and operational roles.
- Doppler's September 28, 2026 company post claims more than 14,000 depositors and more than $150M cumulative deposits into XRP/RLUSD vaults since February 2025. Its analytics page displays approximately $29.48M TVL, 2.46% XRP vault APY and 5.66% RLUSD vault APY. These are company-reported figures; cumulative deposits are not current TVL and APY is not guaranteed.
- Doppler describes its current vault strategy as CeDeFi, using asset-neutral arbitrage and spot-perpetual basis strategies, institutional custody and off-exchange settlement. The company says vault shares are currently recorded on Doppler's side and cannot yet be transferred to another wallet, pledged as collateral or used in another protocol. Tokenized receipt positions are still being built.
- Doppler says dedicated institutional vaults underpin relationships with SBI Ripple Asia, SBI Digital Finance and Evernorth. This does not disclose actual funded balances, client allocations or independent evidence of deployment for those partners.
- Doppler Lending is described as planned for Q4 2026 subject to XLS-66 mainnet activation. The company says XLS-66 is designed for pooled, uncollateralized, fixed-term lending with off-chain underwriting and risk management. It is not a conventional overcollateralized XRP lending market. The amendment remains below its validator threshold; no activation countdown exists.
- The phrase "productive financial capital" appears in Doppler's announcement as strategy/marketing language. It is not a standardized, independently measured "actual capital" metric.
- A third-party article attributes claims of Japanese bank remittance pilots (approximately 60% lower costs and under four seconds) to a Kamilah Stevenson YouTube video, but names no banks and provides no primary performance records. This remains an unverified lead and is excluded from institutional-adoption evidence and model features.

Primary sources:
- SBI Digital Finance group profile: https://www.sbigroup.co.jp/english/company/group/sbidigitalfinance.html
- Doppler/SBI Digital Finance announcement, July 13, 2026: https://blog.doppler.finance/blog/doppler-finance-and-sbi-digital-finance-announce-strategic-partnership-to-expand-institutional-xrp-finance-in-japan
- SBI Ripple Asia/Doppler MOU, December 17, 2025: https://blog.doppler.finance/blog/sbi-ripple-asia-partners-with-doppler-finance-for-xrp-yield-and-rwa-tokenization
- Doppler operating-layer and vault disclosure, September 28, 2026: https://blog.doppler.finance/blog/building-the-financial-operating-layer-for-tokenized-assets
- Doppler XLS-66 lending design, July 2, 2026: https://blog.doppler.finance/blog/building-institutional-lending-on-xrp-ledger-the-role-of-xls-66
- Doppler analytics dashboard: https://doppler.finance/analytics
- EdgeX/DailyCoin article carrying the unverified Japanese pilot claim: https://pro.edgex.exchange/nl-NL/news/article/japanese-banks-xrp-remittance-pilots

Identity clarification:
- Tokyo SBIC's official seminar archive lists a February 26, 2025 event specifically titled "Generative AI (ChatGPT): Present and Future" and a June 12, 2025 two-day manufacturing course including ChatGPT usage. A March 5, 2026 Tokyo SBIC/Hamamatsu seminar also covered ChatGPT. These are training/education events, not evidence of an OpenAI partnership.
- Official Tokyo, Nagoya and Osaka SBIC profiles identify three regional sister companies under the Small and Medium Business Investment & Consultation Company Act. They are not SBI Holdings subsidiaries.
- SB OAI Japan GK is a separate SoftBank Group/OpenAI joint venture; SoftBank Group is not SBI Holdings.
- The current YouTube search identifies multiple candidate Kamilah Stevenson channels and lookalikes, but the first-party course site does not link a YouTube channel. No videos are attributed.
