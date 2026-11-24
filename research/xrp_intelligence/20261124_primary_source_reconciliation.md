# XRP primary-source reconciliation — 2026-11-24

**Status:** EXECUTED public-source review; RESEARCH-ONLY; not admitted to the point-in-time feature store or forecast ledger.

**Retrieval provenance:** Retrieved on 2026-11-24 through public publisher pages and official corporate/legal sources. Exact web-client retrieval timestamp and raw response bytes were not available for immutable hashing. Publisher-displayed refresh/event times are retained below with timezone marked unspecified where the page does not state one. This note is not a WORM receipt or an independently timestamped source archive.

## 1. Coinbase cbXRP reserve and supply

Coinbase's own proof-of-reserves page describes cbXRP as a wrapped token backed 1:1 by XRP held by Coinbase.

Two Coinbase page snapshots were returned on the same date:

| Snapshot | Publisher-displayed refresh | XRP price / 1D | Total XRP reserve | Total cbXRP supply |
|---|---|---:|---:|---:|
| Default page | 2026-11-24 02:06 AM (timezone not stated) | $0.95 / +3.11% | 159,914,497.35 XRP | 159,912,250.81 cbXRP |
| US mobile URL variant | 2026-11-24 12:16 AM (timezone not stated) | $0.94 / +1.32% | 159,914,497.35 XRP | 159,912,250.81 cbXRP |

At the shared token-quantity snapshot, displayed reserves exceed displayed supply by **2,246.54 XRP**. Reserve/supply is approximately **1.00001405**, or a displayed surplus of **0.001405%**. The Base network supply is shown as 159,912,250.811 cbXRP.

**Interpretation:** Coinbase's published quantities are near 1:1 at the displayed snapshot. This is a Coinbase-published dashboard, not an independent attestation. The two locale/cache variants have different displayed refresh times and prices; preserve them as separate observations rather than averaging or pretending they are synchronized. The Coinbase page links the Base token address `0xcb585250f852C6c6bf90434AB21A00f02833a4af`; the linked BaseScan address endpoint returned HTTP 403 during this review, so contract supply was not independently verified here.

## 2. Morpho Base USDC / cbXRP market

The Morpho app page identifies an isolated Base market:

- Market ID: `0xd4a903dc6d949519060c7707f9604fdc9772c046e05c2e3a8fce0bd7196e4109`
- Loan asset: USDC
- Collateral asset: cbXRP
- Creation date shown: 2026-01-15
- Liquidation loan-to-value: 62.5%
- Liquidation penalty: 12.67%
- Realized bad debt shown: 0.00 USDC
- Unrealized bad debt shown: 0.00 USDC
- Outstanding loans shown: $47.82M USDC
- Total liquidity shown: $24.96M
- Total market size shown: $72.79M
- Current utilization shown: 82.19%; target utilization: 90%
- Borrow amount to target utilization shown: $15.56M
- Instantaneous rate shown: 6.50%; 6-hour borrow rate: 6.48%; 6-hour lend rate: 5.28%
- Oracle price shown: 1 cbXRP = 0.939 USDC; DeFiLlama price shown: 0.941
- Oracle provider shown: Chainlink XRP/USD; heartbeat/deviation shown as 1 day / 0.5%
- The page shows 1,095 borrowers. Its transaction feed includes activity dated 2026-11-24 00:27–00:29; timezone is not stated.

The market page lists these vaults as suppliers, with displayed allocations: Steakhouse High Yield USDC Edition ($25.78M), Steakhouse High Yield USDC ($10.84M), Clearstar cbAssets Vault ($5.53M), Gauntlet USDC Frontier ($2.90M), and Yearn OG USDC V1 ($2.04M). These are displayed vault allocations to the market, not evidence of native XRP exchange purchases.

### Data-quality objections retained

1. The displayed $47.82M loans and $24.96M liquidity sum to about $72.78M, consistent with the displayed $72.79M market size. However, a simple loans/(loans + liquidity) calculation is about 65.7%, not the displayed 82.19% utilization. These fields may use different definitions or vintages; do not normalize them until the API field semantics are verified.
2. The displayed `Value secured` metric is $202M. If interpreted as the value of cbXRP collateral in this one market, it does not reconcile with Coinbase's displayed total cbXRP supply value of roughly $150M at the same broad date. Its semantics and data vintage remain unresolved; exclude it from derived collateral totals.
3. The Morpho page's Chainlink and DeFiLlama price values are reported by one Morpho interface. They are not two independently captured receipts in this review.
4. The 1-day oracle heartbeat is a configuration/risk parameter, not proof that the oracle is stale. It warrants timestamp-aware monitoring during fast XRP moves.

Morpho's documentation describes Blue markets as isolated, immutable markets with one collateral asset and one loan asset. This is a Base DeFi collateral/lending use of **Coinbase-wrapped XRP**, not direct evidence of native XRP spot demand, exchange inflows, Ripple settlement volume, or Coinbase reserve movement.

## 3. Japan SBIC identity — resolved from primary evidence

The acronym in the regional names refers to **Small and Medium Business Investment & Consultation**, not SBI Holdings.

Japan's Small and Medium Business Investment & Consultation Companies Act (Act No. 101 of 1963) Article 2 enumerates exactly three companies: Tokyo, Nagoya and Osaka. Their official corporate profiles explicitly use the East/Central/West English labels:

| Regional label | Legal company | Official English name | Established | Officially stated operating area |
|---|---|---|---|---|
| SBIC East Japan | 東京中小企業投資育成株式会社 | Tokyo Small and Medium Business Investment & Consultation Co., Ltd. | 1963-11-15 | Shizuoka, Nagano, Niigata and east; 18 prefectures |
| SBIC Central Japan | 名古屋中小企業投資育成株式会社 | Nagoya Small and Medium Business Investment & Consultation Co., Ltd. | 1963-11-18 | Aichi, Gifu, Mie, Toyama and Ishikawa |
| SBIC West Japan | 大阪中小企業投資育成株式会社 | Osaka Small and Medium Business Investment & Consultation Co., Ltd. | 1963-11-20 | Fukui, Shiga, Nara, Wakayama and west; 24 prefectures |

Tokyo's official profile lists shareholders as local governments (18 prefectures), chambers of commerce, financial institutions and operating companies, and calls Nagoya and Osaka sister companies. Nagoya and Osaka official profiles also identify the other two as sister companies.

**Conclusion:** These are three distinct regional statutory investment corporations created under the 1963 Act. They are not SBI Holdings subsidiaries or SBI Group regional offices. No primary-source evidence of ownership by SBI Holdings was found. The acronym similarity is not evidence of a corporate relationship.

## 4. SBI Holdings, Ripple and RLUSD — distinct relationship

SBI Holdings' FY2025 financial-results presentation, dated 2026-05-01, calls Ripple an SBI Group investee company and states SBI's stake is approximately 9%. The same presentation says Ripple's corporate value reached $40B after a $500M financing round in November 2025 and $50B after a $750M share buyback in March 2026. These are company-reported figures, not an independent valuation.

The presentation's XRP distribution graphic is dated 2026-04-27 and labels approximately 61.68B XRP as circulated, 5.10B as "Actual XRP", 33.20B as under escrow and 0.01B as burned. The slide's phrase **"Actual XRP"** is a holdings category; it is not evidence for the separate exact phrase "actual capital".

Ripple's 2026-06-24 press release says RLUSD officially launched in Japan after JFSA approval and is available to institutional and retail users through SBI VC Trade's VCTRADE platform. This verifies a Ripple/SBI distribution relationship for RLUSD. It does not establish that XRP is the settlement asset for RLUSD transactions.

No Coinbase/Ripple or Coinbase/SBI corporate relationship is inferred from the cbXRP reserve and Morpho market observations above.

## 5. Exact-phrase and identity queue

- `"ASK Coin"`: no primary-source XRP relationship verified in this research pass; unresolved.
- `"actual capital"`: no primary-source XRP/SBI/Ripple relationship verified in this pass. Do not conflate it with SBI's separate "Actual XRP" slide label.
- `"SBIC, ChatGPT SBIC"`: no official ChatGPT relationship found. The Japanese SBIC identity is now resolved as the three regional statutory investment companies above.
- `Camilla Stevenson / Kamilah Stevenson`: identity not verified. No YouTube inventory was performed; identity verification remains a prerequisite.

## 6. Model admission and next actions

All Coinbase/Morpho dashboard values and corporate research in this note remain **research-only and model-ineligible**. No raw response hashes, independent timestamp anchors, or complete on-chain reserve receipts were created in this review. Do not convert these snapshots directly into point-in-time features.

Next: capture Coinbase proof-of-reserves and Morpho Read API responses as raw bytes with hashes and provider timestamps; verify the cbXRP Base contract supply independently; retrieve Morpho chain indexer tip and align state/history to a block; resolve the utilization and `Value secured` discrepancies; and keep wrapped-asset collateral activity separate from native XRP spot and XRPL payment flows.

## Source register

1. Coinbase cbXRP proof of reserves: https://www.coinbase.com/cbxrp/proof-of-reserves
2. Morpho USDC/cbXRP Base market: https://app.morpho.org/base/variable/0xd4a903dc6d949519060c7707f9604fdc9772c046e05c2e3a8fce0bd7196e4109/usdc-cbxrp
3. Morpho Read API reference: https://docs.morpho.org/api/
4. Morpho Blue market structure: https://docs.morpho.org/learn/concepts/blue/
5. SBIC East Japan official profile: https://www.sbic.co.jp/company/profile/
6. SBIC Central Japan official profile: https://www.sbic-cj.co.jp/company/about/
7. SBIC West Japan official profile: https://www.sbic-wj.co.jp/profiles/profile/
8. Japanese e-Gov law record, Act No. 101 of 1963: https://laws.e-gov.go.jp/law/338AC0000000101
9. SBI Holdings FY2025 financial-results presentation (2026-05-01): https://www.sbigroup.co.jp/english/investors/disclosure/presentation/pdf/260501presentations.pdf
10. Ripple/SBI RLUSD Japan launch (2026-06-24): https://ripple.com/ripple-press/ripple-and-sbi-group-partner-to-launch-ripple-usd-in-japan/


---

## 7. 2026-11-24 08:03 UTC follow-up — institutional relationship graph and creator-attributed video inventory

This follow-up adds current primary-source evidence. It does **not** promote the observations into the point-in-time feature store: original HTTP response bytes, response headers, independently anchored capture timestamps and immutable receipt hashes were not captured.

### 7.1 Coinbase ↔ Circle: current distribution economics

- Circle's Q3 2026 Form 10-Q says Coinbase receives an allocation based on USDC held on Coinbase's platform after Circle's issuer retention, plus half of the remaining ecosystem-growth amount after payments to approved third-party participants.
- Circle reported **$986.6 million** of distribution costs in connection with its Coinbase agreements for the nine months ended 2026-09-30. This is a cost/distribution disclosure, not XRP demand.
- Coinbase's Q3 2026 Form 10-Q says it renewed its arrangement with Circle on the same terms. Coinbase also reported an all-time high average USDC balance in its products; its Q3 earnings release reported **$22 billion**.
- The 2023 Circle/Coinbase announcement says Coinbase took an equity stake in Circle and that the parties moved USDC issuance/governance from the former Centre consortium to Circle. Treat the current collaboration agreement and historical Centre governance as separate structures.

### 7.2 Circle ↔ Ripple: direct XRPL stablecoin partnership

- Circle announced USDC live natively on XRPL mainnet on 2025-06-12, with Circle Mint and Circle APIs supporting it; no third-party bridge is required.
- Ripple's same-day announcement describes a direct partnership with Circle and says Ripple intends to use USDC alongside RLUSD in its payments product.
- USDC and RLUSD are separate issuer liabilities and separate assets. Their presence on XRPL can increase ledger activity and dollar liquidity, but does not by itself establish material net XRP purchases. XRP may be used for transaction fees, DEX/auto-bridging and other liquidity functions; quantify those separately.

### 7.3 Coinbase ↔ Ripple: new direct RLUSD distribution relationship

- Coinbase and Ripple announced on 2026-10-28 that RLUSD became available through Coinbase Prime, Coinbase Exchange and the Coinbase retail app.
- The launch announcement supports RLUSD deposits/withdrawals on XRPL, Base and Ethereum. Ripple said it would provide Base liquidity. Coinbase Global Exchange collateral support was described as a later phase, not as already live at launch.
- Coinbase separately states XRP is supported on Retail, Prime and Custody, subject to jurisdictional restrictions. This is exchange/custody support, not proof of a Coinbase equity stake in Ripple.
- The new RLUSD relationship is direct commercial distribution. No evidence in the reviewed primary sources establishes Coinbase ownership of Ripple or Ripple ownership of Coinbase.

### 7.4 SBI ↔ Circle: strategic, distribution, banking and network links

- SBI Holdings and Circle signed an MOU on 2023-11-27 covering USDC circulation in Japan, banking relationships and Circle Web3 services.
- SBI's FY2024 results presentation says a 50/50 Japanese JV agreement was signed on 2025-03-18; the subsequent SBI announcement says the JV was established in 2025.
- SBI VC Trade obtained Japan's electronic-payment-instrument registration and began USDC services in March 2025. SBI Shinsei Bank was designated to provide banking services to Circle.
- SBI Holdings and SBI Shinsei Bank disclosed a combined **$50 million** strategic investment in Circle at its 2025 NYSE listing, split **$25 million each**.
- SBI Holdings disclosed participation by a consolidated subsidiary in Circle's ARC token presale on 2026-05-12. Circle separately named SBI Group in Arc's founding-validator cohort on 2026-08-05.
- SBI's 2026-05-01 strategy deck labels Circle/USDC and Ripple/RLUSD as USD-stablecoin partners while separately describing a planned JPYSC initiative. This is evidence of a multi-rail strategy; it is not proof that every planned product or partner flow is already live.

### 7.5 SBI ↔ Ripple: equity, JV, remittance and treasury links

- SBI Holdings' FY2025 results presentation describes Ripple as an SBI Group investee company and states that SBI's stake is approximately **9%**. The figure is issuer-reported, not independently valued here.
- SBI Group's company profile identifies SBI Ripple Asia as a joint venture; SBI Group's voting-rights share is 60%.
- SBI Remit's 2023-09-06 release is unusually specific about the operating flow: SBI Remit sends the customer payment request; SBI VC Trade sends XRP in response; TRANGLO processes payout to the beneficiary bank account. The release says XRP is used as a bridge between fiat currencies. This is evidence of a real XRP-enabled remittance product, but no corridor-level volume or net XRP inventory is disclosed.
- SBI Holdings' 2026-05-01 presentation says it invested **$200 million in cash** in Evernorth's PIPE and describes more than $1 billion raised through a combination of spot XRP and cash. This is a capital relationship with an XRP treasury company, not proof that the $200 million was spent on open-market XRP purchases. Keep cash, in-kind XRP, treasury holdings and exchange executions separate.

### 7.6 Relationship graph and disconfirming boundaries

| Pair | Verified relationship | What it does not prove |
|---|---|---|
| Coinbase–Circle | USDC founding/strategic relationship, Coinbase equity stake, current distribution-cost collaboration | XRP spot demand or Ripple ownership |
| Circle–Ripple | Direct USDC-on-XRPL launch partnership | Circle buying XRP or XRP being required for every USDC transfer |
| Coinbase–Ripple | Direct RLUSD listing/distribution partnership across Coinbase products | Coinbase equity ownership in Ripple or RLUSD collateral support already live at launch |
| SBI–Circle | 50/50 Japan JV, USDC distribution/banking, $50m combined Circle investment, ARC/Arc participation | XRP demand or an exclusive stablecoin arrangement |
| SBI–Ripple | Approx. 9% SBI stake in Ripple, SBI Ripple Asia JV, SBI Remit/VC Trade XRP remittance flow, Evernorth PIPE investment | All SBI/Ripple products using XRP or every financing dollar buying XRP |
| SBI–Coinbase | No direct ownership or bilateral commercial agreement established in this review | Do not draw an edge from common USDC ecosystem participation alone |

**Model treatment:** represent each legal entity, instrument, network, contract, cash flow and XRP flow separately. Circle/Coinbase reserve economics, SBI/Circle USDC distribution, Ripple RLUSD, SBI Remit ODL, Evernorth treasury funding and cbXRP/Morpho collateral are different mechanisms. None may be collapsed into a single "institutional XRP demand" feature.

### 7.7 Kamilah Stevenson public-channel attribution and curated public inventory

**Attribution status:** the main public channel `@drkamilahstevenson` is now linked to the creator's public brand at the channel/brand level. The YouTube channel index identifies the channel as "Kamilah Stevenson", lists the creator-controlled link `go.prescribewealth.com/yt-bio`, and describes a stocks/crypto/macro investing channel. The linked brand domain `prescribewealth.com` identifies MKS Health LLC / The Inner Circle as founded by Dr. Kamilah Stevenson. This is a creator-controlled cross-link, not independent legal-identity or credential verification.

**Do not merge** the channel with the separate London-based Camilla Stevenson LinkedIn profile, or with other low-subscriber YouTube channels using similar names/descriptions. A transcript result for one video renders the spoken name as "Camila"; the channel and brand spell it "Kamilah". The main channel also posted that it created a second channel, `@PrescribeWealth`; that second channel's content was not separately inventoried here.

**Curated public inventory from the main channel index** (displayed view counts and relative ages are a search-index snapshot, not independently audited analytics; individual video IDs were not exposed for most entries):

Recent public uploads:
1. "This NEW Bank Deal Shows Exactly Where XRP Is Headed" — 29K views, 1 day
2. "This New SEC Proposal Could Unlock Trillions for XRP (and nobody realizes)" — 28K, 2 days
3. "Exactly How to Retire With Your XRP Portfolio (Even If You're Cash Poor)" — 41K, 4 days
4. "XRP vs Banks: Why Your Money Needs Autonomy NOW" — 9.8K, 5 days
5. "Did SWIFT Just Change XRP Forever? (The Truth)" — 77K, 5 days
6. "BlackRock Is Moving Wall Street Onchain. XRP Holders, Pay Attention." — 21K, 8 days
7. "A $119 Billion African Bank Just Put Its License Behind XRP" — 27K, 9 days
8. "A New XRP Tool Can Buy and Sell for You" — 13K, 11 days
9. "Invest NOW or Get Left Behind. Institutions Are Already Moving." — 16K, 12 days
10. "The CFTC Just Said What XRP Holders Waited Years to Hear" — 44K, 12 days
11. "Wall Street Just Got a Company Built to Keep BUYING XRP" — 16K, 2 weeks
12. "XRP Ledger Technology Just Reached Europe's Central Bank" — 11K, 2 weeks

Popular public uploads surfaced by the same channel index:
- "Japan Just Ended 30 Years of ZERO Interest Rates—Why XRP Could Explode" — 253K, 10 months
- "How the Wealthy Will Use XRP (Most People Won't Understand)" — 151K, 8 months
- "Flare Is Putting 100 Million XRP to Work. Holders Can Earn From It" — 148K, 1 month
- "Why XRP Could Be Repriced (Banks Aren't Trading It)" — 143K, 10 months
- "Banks Just Got the GREEN LIGHT on Crypto—Are You Positioned" — 139K, 7 months
- "SEC Silent, CFTC Approved: XRP Just Got Treated Like Gold" — 135K, 10 months
- "The CLARITY Act Just Failed in the Senate. What This Means for XRP" — 129K, 1 month
- "SWIFT Just Connected 11,000 Banks—and XRP Is at the Center" — 86K, 6 months
- "Why Banks Need XRP to Be Expensive (Retail Is Thinking About It Wrong)" — 84K, 10 months
- "Most XRP Holders Don't Understand What They're Actually Holding" — 83K, 7 months
- "Japan's Top Financial CEO Just Publicly DEMANDED The US Senate Act On XRP" — 82K, 4 months

Public live streams surfaced by the channel index:
- "XRP Got Everything We Waited For. So Why Isn't It Soaring?" — 19K, 1 day
- "XRP's Next Big Move Could Come Down to These 4 Days" — 26K, 3 days
- "Bank Of America's CEO Just ADMITTED What XRP Holders Already Knew" — 20K, 6 days
- "I Was WRONG About XRP. The Timeline Just Changed." — 35K, 8 days
- "191,000 Traders Got Wiped Out While XRP Became Wall Street Collateral" — 22K, 2 weeks
- "Bad Jobs. Higher Rates. Something Just Broke. Watch Your XRP." — 23K, 2 weeks
- "Your XRP Can Now Trade Without You" — 21K, 2 weeks
- "America's Biggest Banks Just Picked Quant. XRP Was Never the Competition." — 42K, 3 weeks
- "The White House Is Done Waiting on Congress. XRP Moves Forward Anyway" — 19K, 3 weeks
- "The CLARITY Act Exposed the Banks. XRP Just Became More Important" — 23K, 4 weeks
- "The SEC Just Approved Stocks Onchain. XRP Was Built for What Comes Next" — 11K, 1 month
- "The CLARITY Act Vote Failed. XRP Ran 580% Without It" — 22K, 1 month

Members-only videos were excluded. The inventory is a curated XRP/Japan/institutional subset, not all 1.2K channel uploads. A separately indexed public video, "Japan's Yen Crisis Put $1 Trillion of U.S. Debt at Risk" (2026-08-07), is directly linked at https://www.youtube.com/watch?v=Qvz-NilZTgo.

### 7.8 Exact-phrase status after follow-up

- `"ASK Coin"`: still no primary-source XRP/XRPL identity. Permission Coin (ASK) remains a separate ticker-collision candidate; no XRPL relationship established.
- `"actual capital"`: no exact primary-source XRP/SBI/Ripple match established. SBI's slide label "Actual XRP" is a different phrase and category; do not conflate them.
- `"SBIC, ChatGPT SBIC"`: no official ChatGPT relationship established. The regional SBIC legal identity remains separate from SBI Holdings.

### 7.9 Added source register

11. SBI Holdings FY2024 results / Circle-SBI 50:50 JV slide: https://www.sbigroup.co.jp/english/investors/disclosure/presentation/pdf/250509presentations.pdf
12. SBI Holdings/Circle MOU (2023-11-27): https://www.sbigroup.co.jp/english/news/pdf/2023/1127_a_en.pdf
13. SBI Holdings/Circle JV announcement (2025-08-22): https://www.sbigroup.co.jp/news/2025/0822_15679.html
14. SBI Holdings/SBI Shinsei $50m Circle investment (2025-06-09): https://www.sbigroup.co.jp/english/news/pdf/2025/0609_a_en.pdf
15. SBI VC Trade USDC registration (2025-03-04): https://www.sbigroup.co.jp/news/2025/0304_15290.html
16. SBI Holdings ARC presale announcement (2026-05-12): https://www.sbigroup.co.jp/news/2026/0512_16310.html
17. Circle Arc founding validator cohort (2026-08-05): https://www.circle.com/pressroom/circle-announces-founding-validator-cohort-and-major-integrations-for-arc-ahead-of-september-16-mainnet-launch
18. Circle USDC on XRPL (2025-06-12): https://www.circle.com/blog/now-available-usdc-on-the-xrpl
19. Ripple/Circle USDC-on-XRPL partnership (2025-06-12): https://ripple.com/ripple-press/ripple-and-circle-launch-usdc-on-the-xrp-ledger/
20. Coinbase/Ripple RLUSD distribution partnership (2026-10-28): https://www.coinbase.com/blog/rlusd-is-now-available-on-coinbase
21. Ripple/Coinbase RLUSD announcement (2026-10-28): https://ripple.com/ripple-press/ripple-and-coinbase-partner-to-expand-access-to-rlusd/
22. Circle Q3 2026 Form 10-Q (2026-09-30): https://www.sec.gov/Archives/edgar/data/1876042/000187604226000311/crcl-20260930.htm
23. Coinbase Q3 2026 Form 10-Q (2026-09-30): https://www.sec.gov/Archives/edgar/data/1679788/000167978826000122/coin-20260930.htm
24. Coinbase Q3 2026 results (2026-10-29): https://investor.coinbase.com/news/news-details/2026/Coinbase-Q3-2026-Earnings-Show-All-time-high-Coinbase-One-Subscribers-and-Prediction-Markets-Surpassing-200-Million-in-Annualized-Revenue/default.aspx
25. Prescribewealth official brand site: https://prescribewealth.com/
26. Main YouTube channel: https://www.youtube.com/channel/UCqUPJMQdkCN6lsLVDnichPA
