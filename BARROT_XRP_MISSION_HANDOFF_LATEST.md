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

XRPL's official September 16 release introduced rippled 3.4.0 and the fixCleanup3_4_0 amendment. November 4 activation at ledger 108112129 is reported by secondary sources; this run did not independently query current validator/ledger amendment state. Do not elevate the activation claim to primary-source verified.

The BLS October CPI and Real Earnings release is scheduled for November 10 at 08:30 ET / 13:30Z. At this research cutoff it is a future event, not a published result.

Sources: [XRPL 3.4.0 release](https://xrpl.org/blog/2026/xrpld-3.4.0), [BLS November schedule](https://www.bls.gov/schedule/2026/11_sched.htm).

## Identity research

- Japan's SBIC East/Central/West remain Tokyo/Nagoya/Osaka regional Small and Medium Business Investment & Consultation companies, distinct from SBI Holdings.
- Tokyo SBIC's official course includes ChatGPT and Copilot instruction for investee companies; this is not an OpenAI partnership.
- “SBIC, ChatGPT SBIC” has no verified primary-source partnership match.
- ASK Coin remains unresolved; Permission Coin ASK is a candidate only, with no verified XRP integration.
- “Actual capital” is not a standardized XRP metric; keep cash, in-kind, debt, drawn capacity, contingent equity and secondary resales separate.
- Camilla/Kamilah Stevenson identity/guest appearances remain separate from personal-channel ownership; no unverified personal-channel upload was added.

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
