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

### 7.7 Camilla/Kamilah Stevenson identity and YouTube attribution — unresolved

**Person identity:** Dr. Kamilah Stevenson is identifiable through the official PrescribeWealth brand site and an independent interview. This does not establish ownership of a particular YouTube channel.

**Channel identity:** the candidate channel `UCqUPJMQdkCN6lsLVDnichPA` links to a PrescribeWealth bio URL, but the official PrescribeWealth site does not reciprocally link to that channel. Multiple similarly named channels exist, and the independent interview transcript varies between Kamilah/Camilla/Kamilla while giving an imprecise channel name. A one-way channel description link is insufficient to bind the exact channel ID to the person.

**Attribution decision:** the earlier tentative channel-level attribution and curated title list are superseded and withdrawn. The titles and livestreams previously surfaced from that candidate channel are not attributed to Dr. Stevenson, are not a verified creator inventory, and must not be used as evidence about her statements or positions. **No public-video inventory was performed.**

Resume only after a reciprocal official link or equivalent primary identity confirmation binds the exact YouTube channel ID to Dr. Stevenson. Then inventory public uploads, Shorts and livestreams by canonical video ID with publication timestamps and transcript provenance. Exclude member-only material and respect platform access controls.

Correction record: [PR #1702 identity-audit note](https://github.com/Barrot-Agent/B-Agent/pull/1702#issuecomment-7151626175). The JSON addendum's existing `data_quality` and `search_log` already record the no-identity/no-inventory result; this Markdown section now aligns with that evidence.

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
26. Candidate YouTube channel (ownership by Dr. Kamilah Stevenson not verified; not attributed): https://www.youtube.com/channel/UCqUPJMQdkCN6lsLVDnichPA


### 7.10 2026-11-25 public-source follow-up — SBIC East AI education and unverified video candidates

- Tokyo SBIC East's official 2025-06-12/13 manufacturing course on generative AI and machine learning explicitly includes ChatGPT use and Copilot. The page says it was limited to investee companies; this proves AI education activity by the Tokyo SBIC company, not an OpenAI partnership, investment, sponsorship or XRP program. Source: https://www.sbic.co.jp/training/20250612co/
- Tokyo SBIC East's official 2026-10-06 seminar, "The Present and Future of Generative AI," names a Microsoft Japan executive evangelist as speaker and was free to both investee and general-company participants. This is further evidence of SBIC East's AI education activity, not a ChatGPT corporate relationship. Source: https://www.sbic.co.jp/seminar/20261006js/
- Public search indexing surfaced another channel titled "Kamilah Stevenson | Xrp & Stocks" (channel ID `UCXm6KAr1WHF6UN7g5b2W7wg`, indexed as 2 subscribers / 14 videos) and a video titled "I Moved My XRP Off The Exchanges" attributed by the index to Kamilah Stevenson. This channel ID differs from the previously stored candidate `UCqUPJMQdkCN6lsLVDnichPA`. The channel page was throttled and the video page could not be independently opened; no reciprocal official PrescribeWealth link was verified. Treat both as unverified search candidates only. No video inventory or creator attribution is authorized by this evidence.
- Exact-phrase search surfaced an AInvest opinion article dated 2026-08-23 using "Ripple's actual capital" as generic editorial wording about RLUSD. It is secondary commentary, not a primary-source disclosure, named entity or independently verified capital-flow record. Source: https://www.ainvest.com/news/ripple-75-licenses-don-serve-token-serve-company-2608/
- No new primary-source XRP relation for "ASK Coin" or official ChatGPT/SBIC affiliation was found. Keep both unresolved; do not convert these search hits into relationship-graph edges or model features.

Additional source register:
27. Tokyo SBIC East generative-AI / machine-learning course (2025-06-12/13): https://www.sbic.co.jp/training/20250612co/
28. Tokyo SBIC East "The Present and Future of Generative AI" seminar (2026-10-06): https://www.sbic.co.jp/seminar/20261006js/
29. Unverified YouTube channel search candidate `UCXm6KAr1WHF6UN7g5b2W7wg` (not attributed): https://www.youtube.com/channel/UCXm6KAr1WHF6UN7g5b2W7wg
30. Unverified YouTube video search result (not attributed): https://www.youtube.com/watch?v=TfFx0g2IgGg
31. AInvest secondary commentary containing the phrase "actual capital" (not primary evidence): https://www.ainvest.com/news/ripple-75-licenses-don-serve-token-serve-company-2608/


### 7.11 2026-11-25 primary-source resolution — Japanese SBIC legal identities

**Resolution:** In the Japanese corporate context covered by this research, “SBIC East Japan,” “SBIC Central Japan,” and “SBIC West Japan” are the English regional labels of three separate statutory small-and-medium-business investment companies. They are not alternative names for SBI Holdings, Inc.

- The Japanese **Small and Medium Business Investment & Consultation Companies Act** (Act No. 101 of 1963), Article 1 defines the purpose as investing in SMEs to strengthen their equity and support healthy growth. Article 2 names exactly three companies: Tokyo Small and Medium Business Investment & Consultation Co., Ltd., Nagoya Small and Medium Business Investment & Consultation Co., Ltd., and Osaka Small and Medium Business Investment & Consultation Co., Ltd.
- **SBIC East Japan:** Tokyo Small and Medium Business Investment & Consultation Co., Ltd. (東京中小企業投資育成株式会社), corporate number 9011001030621; established 1963-11-15; capital ¥6.6734 billion. Its official profile describes shareholders as local public bodies (18 prefectures), chambers of commerce, financial institutions and business companies, and its operating area as 18 prefectures east of Shizuoka, Nagano and Niigata.
- **SBIC Central Japan:** Nagoya Small and Medium Business Investment & Consultation Co., Ltd. (名古屋中小企業投資育成株式会社); established 1963-11-18; capital ¥4.3808 billion; operating area Aichi, Gifu, Mie, Toyama and Ishikawa. Its official profile explicitly uses “SBIC Central Japan” and lists Tokyo and Osaka as sister companies. Its shareholder-composition chart shows local public bodies, the Nagoya Chamber of Commerce, financial institutions, insurers and business companies.
- **SBIC West Japan:** Osaka Small and Medium Business Investment & Consultation Co., Ltd. (大阪中小企業投資育成株式会社); established 1963-11-20; capital ¥6.822 billion; operating area 24 prefectures west of Fukui, Shiga, Nara and Wakayama. Its official profile explicitly uses “SBIC West Japan” and lists Tokyo and Nagoya as sister companies.
- **SBI Holdings is a different legal entity:** its official corporate profile identifies the company as SBI Holdings, Inc., established 1999-07-08, with the principal business of controlling and managing the SBI Group through share ownership. The 1963 statute and the three companies' own profiles identify the regional SBIC companies separately.

**Relationship conclusion:** The three regional SBIC companies are statutory sister companies, not the SBI Holdings corporate group. The initials “SBI” are not sufficient evidence of a corporate relationship. The primary sources reviewed do not establish that any of the three SBIC companies is a subsidiary of SBI Holdings, an OpenAI/ChatGPT partner, or an XRP issuer, custodian, exchange or payment-rail operator. The published shareholder descriptions are category-level on the pages reviewed; this does not prove that no minority cross-shareholding or indirect commercial relationship exists. Do not claim a total absence of every possible link without current named shareholder registers and contractual disclosures.

**Research interpretation:** SBIC's investment and growth-support mandate is relevant to Japanese SME finance and regional business development. Its generative-AI training/seminars demonstrate education activity only; they do not establish a ChatGPT partnership, sponsorship, investment or access arrangement. No XRP relationship follows from the identity resolution.

Additional primary-source register:
32. Small and Medium Business Investment & Consultation Companies Act (Act No. 101 of 1963), e-Gov: https://laws.e-gov.go.jp/law/338AC0000000101/20220617_504AC0000000068
33. Tokyo SBIC East official company profile: https://www.sbic.co.jp/company/profile/
34. Nagoya SBIC Central official company profile: https://www.sbic-cj.co.jp/company/about/
35. Osaka SBIC West official company profile: https://www.sbic-wj.co.jp/profiles/profile/
36. SBI Holdings official corporate profile: https://www.sbigroup.co.jp/english/company/information/profile.html
37. Nagoya SBIC Central official shareholder-composition chart: https://www.sbic-cj.co.jp/assets/images/company/shareholder.jpg



### 7.12 2026-11-25 primary-source update — OCC, BNY custody, C2FO/RLUSD and SBI operating boundaries

**Retrieval basis:** Public official pages and a SEC filing were opened on 2026-11-25. Publisher dates are retained below. The browser retrieval did not provide original response bytes or independent timestamp anchoring; this section is research-only and is not a content-addressed ingestion receipt.

#### 7.12.1 Ripple National Trust Bank — final approval, separate issuer

- The OCC Corporate Applications Search record for control **2025-Charter-342347**, proposed charter **25364**, lists the Ripple National Trust Bank application as approved **2025-12-12** and **Consummated/Effective 2026-10-26**.
- Ripple's 2026-10-26 announcement says the OCC granted final approval. The approved bank activities include management of the segregated RLUSD reserve, collateral-trustee services for RLUSD holders, and fiduciary digital-asset custody.
- **RLUSD's legal issuer remains Standard Custody & Trust Company, LLC (SCTC)**, a Ripple subsidiary and New York DFS-regulated limited-purpose trust company. Ripple National Trust Bank adds a federal trust-bank layer; it does not replace SCTC as issuer.
- Ripple says the national trust bank will provide fiduciary custody services upon opening. The OCC CAS effective date is verified, but this review did not independently verify customer onboarding, live custody balances or completed custody transactions at the new bank.
- BNY remains identified by Ripple as RLUSD's primary reserve custodian. Do not collapse the issuer, reserve custodian, collateral trustee and trading venue into one role. No deposit-insurance or retail-bank-deposit claim is supported.

#### 7.12.2 BNY — XRP and RLUSD custody support

- In the 2026-10-27 joint announcement, Ripple and BNY state that BNY's Digital Asset Custody platform now supports **XRP and RLUSD** for eligible institutional clients, including safekeeping, holding and transfer.
- BNY's pre-existing role as primary reserve custodian for RLUSD and its custody relationship with Ripple Prime are distinct from its newly announced client-asset custody support for XRP and RLUSD.
- BNY says it intends to broaden support for tokenized assets and investment products issued on XRPL and to work with Ripple to enable BNY clients to mint and redeem RLUSD directly through BNY. Those are **future intentions subject to final BNY and regulatory approvals**, not verified live services in this review.
- Ripple and BNY also say they are exploring tokenized trade finance on XRPL, beginning with a supply-chain-finance initiative with C2FO. This is an exploration/initiative announcement, not proof of completed receivables tokenization, financing volume or XRP purchases.

#### 7.12.3 C2FO Instant Pay — announced RLUSD settlement, not XRP settlement

- C2FO's 2026-10-27 primary announcement says the financing and settlement activity supporting C2FO Instant Pay is intended to move onto XRPL, using **RLUSD for settlement**. Participating capital providers fund early payment; suppliers are intended to receive funds in seconds while invoice terms and due dates remain unchanged.
- C2FO says its existing Early Pay programs have helped businesses access more than **$525 billion** in working capital. That is a company-reported cumulative figure for its broader existing programs; it is **not** Instant Pay volume, XRPL volume, RLUSD settlement volume or XRP demand.
- C2FO's current Instant Pay product page displays a **Join Waitlist** action and says the service will be available in the U.S. at launch. This is a material readiness caveat: the partnership and product are announced, but this review did not verify general availability, a completed customer transaction, settlement volume or production adoption on XRPL.
- The announced settlement asset is RLUSD, not XRP. XRP may be required for XRPL network fees, but no evidence in these announcements establishes XRP as the settlement principal, a bridge asset in this product, or a material source of net XRP spot demand.

#### 7.12.4 SBI / Ripple — distinguish the software JV, ODL operators and RLUSD distributor

- Ripple's current SBI Ripple Asia company page says SBI Ripple Asia sells RippleNet software services to financial institutions and remittance companies. It explicitly states that SBI Ripple Asia **does not handle XRP**.
- The same page separately says XRP-based On-Demand Liquidity is commercialized in Japan through **SBI Remit, Coins.ph and SBI VC Trade** for Philippines remittances. This is a product/operator relationship, not evidence that SBI Ripple Asia itself holds, trades or custodies XRP.
- SBI VC Trade's 2026-06-24 official release says it began handling RLUSD through VCTRADE after maintenance on that date. The release classifies RLUSD for Japanese distribution as a **Type 4 electronic payment instrument** under its interpretation of Japanese law, identifies SBI VC Trade as an SBI Holdings consolidated subsidiary and identifies Ripple Labs as the stablecoin partner. It also says RLUSD deposits and withdrawals are free on that service. This is RLUSD distribution, not evidence that RLUSD transfers use XRP as settlement.
- These are separate relationship edges: (1) SBI Ripple Asia—RippleNet software sales; (2) SBI Remit / Coins.ph / SBI VC Trade—XRP-based ODL corridor; and (3) SBI VC Trade—RLUSD distribution. None changes the legal identity of SBIC East/Central/West or establishes a relationship between those statutory SBIC companies and SBI Holdings.

#### 7.12.5 Coinbase / Ripple / Circle — distribution and collateral remain separate

- Ripple's 2026-10-28 release says RLUSD became available through Coinbase Prime, Coinbase Exchange and Coinbase Retail, with 1:1 conversion from U.S. dollars and other supported USD-denominated stablecoins. The launch supports RLUSD across XRPL, Base and Ethereum.
- The same release describes Coinbase Global Exchange access, including RLUSD collateral use, as a later phase. The reviewed primary sources did not provide a subsequent dated activation notice or collateral terms by 2026-11-25. Therefore **trading/listing support is announced as live; Global Exchange collateral support remains unverified**.
- Circle's SEC-filed 2026-06-30 Form 10-Q describes the Coinbase Collaboration Agreement: Coinbase receives allocations tied to USDC held on its platform after Circle's issuer retention, plus a share of remaining ecosystem-growth economics after approved third-party participant payments. Circle reported distribution costs in connection with its Coinbase agreements of **$324.6 million for Q2 2026** and **$655.3 million for H1 2026**. The separate Q3 2026 filing already cited above reports **$986.6 million for the nine months ended 2026-09-30**. These are Circle-reported distribution costs under the agreement, not XRP flows or proof of a Ripple/Coinbase equity relationship.
- Circle's issuer page reported **$67.8 billion USDC in circulation as of 2026-11-23** and says USDC was natively issued on **38 networks**, including XRPL (network list as of 2026-09-16). These are issuer-displayed figures, not independent exchange-flow or XRP-demand observations.
- Coinbase therefore has two distinct direct stablecoin commercial relationships in the reviewed record: the long-running Circle/USDC distribution-economics agreement and the October 2026 Ripple/RLUSD distribution agreement. Do not infer that one replaces the other, or that either implies a cross-equity relationship with Ripple.

#### 7.12.6 Relationship graph, source independence and model treatment

| Entity / relationship | Verified primary-source statement | Boundary |
|---|---|---|
| OCC → Ripple National Trust Bank | Final approval and OCC CAS consummated/effective date 2026-10-26 | Does not make the bank RLUSD's issuer |
| SCTC → RLUSD | SCTC remains the legal issuer | Separate from reserve custody, trustee and exchange functions |
| BNY → XRP / RLUSD custody | BNY says its Digital Asset Custody platform supports both assets for eligible institutional clients | Custody availability is not evidence of BNY buying XRP |
| BNY ↔ Ripple ↔ C2FO | Tokenized trade-finance exploration on XRPL | No completed financing volume verified |
| C2FO Instant Pay → RLUSD | Announced XRPL settlement using RLUSD | Product page waitlist; no verified production volume; not XRP settlement |
| SBI Ripple Asia → RippleNet | Software-services sales to FIs/remitters; SBI Ripple Asia says it does not handle XRP | Do not attribute ODL asset custody or trading to this JV |
| SBI Remit / Coins.ph / SBI VC Trade → ODL | XRP bridge used for the Japan–Philippines remittance service | No corridor-level net XRP inventory or volume quantified here |
| SBI VC Trade → RLUSD | VCTRADE distribution began 2026-06-24 under Japanese electronic-payment-instrument framework | RLUSD is not XRP |
| Coinbase ↔ Ripple | RLUSD listing/distribution on Coinbase products | Global Exchange collateral phase not confirmed live |
| Coinbase ↔ Circle | USDC distribution economics disclosed in SEC filings | Not an XRP-demand feature |
| Circle → XRPL | USDC native issuance on XRPL | Stablecoin circulation does not establish net XRP purchases |

**Source independence:** OCC CAS is a regulator's application record. Circle's Form 10-Q is a regulatory filing made by Circle. BNY, Ripple, C2FO and SBI releases are primary counterparty/company statements; jointly authored releases are one coordinated announcement, not multiple independent confirmations. C2FO's own product page provides a separate availability caveat. No raw HTTP response bytes, independent timestamp anchors or chain-state receipts were captured in this browser research pass.

**Disconfirming evidence and unresolved measurements retained:**
1. BNY custody support is not XRP inventory acquisition, and the BNY mint/redeem, tokenized-asset and C2FO trade-finance initiatives include future/conditional language.
2. C2FO's existing $525B working-capital figure predates and is broader than Instant Pay; it must not be treated as XRPL or RLUSD volume.
3. RLUSD settlement on XRPL is not XRP settlement. Do not infer XRP bridge demand from RLUSD transfers without transaction-level route evidence.
4. Coinbase RLUSD listing does not establish that Global Exchange collateral use is live; no activation notice or collateral schedule was verified in this pass.
5. USDC and RLUSD supply/circulation figures are issuer-reported; they do not establish the amount held on Coinbase, SBI VC Trade or any specific chain without chain-level/account-level evidence.

**Model treatment:** all observations in this section remain research-only and model-ineligible. Keep issuer, reserve custodian, collateral trustee, custodian platform, distributor, settlement asset, network fee asset and financing capital provider as separate typed entities/roles. No XRP feature, directional forecast, or market-demand conclusion is admitted from these announcements alone.

Additional primary-source register:
38. OCC Corporate Applications Search — Ripple National Trust Bank, control 2025-Charter-342347: https://apps.occ.gov/CAS/home/details?FilingID=RjzoD2gxmYOv&FilingSubtypeID=1093&FilingTypeID=2
39. Ripple final OCC approval announcement (2026-10-26): https://ripple.com/ripple-press/ripple-receives-final-occ-approval-to-establish-national-trust-bank/
40. BNY/Ripple custody and tokenized trade-finance announcement (2026-10-27): https://prodcs.bny.com/corporate/global/en/about-us/newsroom/press-release/ripple-expands-strategic-digital-assets-collaboration-with-bny-across-custody-and-tokenized-trade-finance.html
41. C2FO/Ripple Instant Pay announcement (2026-10-27): https://c2fo.com/newsroom/c2fo-and-ripple-partner-to-modernize-trade-finance-using-the-xrp-ledger/
42. C2FO Instant Pay product page (accessed 2026-11-25): https://c2fo.com/instant-pay/
43. Ripple SBI Ripple Asia official company page (accessed 2026-11-25): https://ripple.com/company/sbi-ripple-asia/
44. SBI VC Trade RLUSD launch notice (2026-06-24): https://www.sbigroup.co.jp/news/pr/2026/0624_16424.html
45. Ripple/SBI RLUSD Japan launch (2026-06-24): https://ripple.com/ripple-press/ripple-and-sbi-group-partner-to-launch-ripple-usd-in-japan/
46. Ripple/Coinbase RLUSD distribution announcement (2026-10-28): https://ripple.com/ripple-press/ripple-and-coinbase-partner-to-expand-access-to-rlusd/
47. Coinbase RLUSD availability announcement (2026-10-28): https://www.coinbase.com/blog/rlusd-is-now-available-on-coinbase
48. Circle Form 10-Q for quarter ended 2026-06-30: https://www.sec.gov/Archives/edgar/data/1876042/000187604226000248/crcl-20260630.htm
49. Circle USDC issuer page (accessed 2026-11-25): https://www.circle.com/usdc


#### 7.12.7 Circle–SBI Japan K.K. — a separate 50/50 USDC distribution joint venture

- Circle's SEC-filed Form 10-Q for the quarter ended **2026-03-31** identifies **Circle SBI Japan K.K.** In November 2025, Circle and SBI Holdings each contributed Japanese yen worth approximately **US$1.5 million**. Circle owns **50%** and consolidates the entity as a variable-interest entity because it directs the activities that most significantly affect the entity and has potentially significant exposure to benefits/losses. SBI's 50% interest is shown as noncontrolling interest. Circle reported no significant operating results for the entity through March 31, 2026.
- This is a direct Circle–SBI corporate joint venture to support USDC distribution in Japan. It is **not** SBI Ripple Asia and is not a subsidiary of Ripple. Keep the two JVs separate: **SBI Ripple Asia (SBI Holdings + Ripple, established 2016)** and **Circle SBI Japan K.K. (Circle + SBI Holdings, established November 2025)**.
- Circle's March 25, 2025 announcement says SBI VC Trade began full-scale USDC distribution on March 26, following JFSA approval. This is a distribution channel, not proof of USDC being used for XRP settlement.

#### 7.12.8 Circle on XRPL and Arc — distinguish network access from corporate affiliation

- Circle announced **native USDC on XRPL mainnet on 2025-06-12**, with Circle Mint and Circle APIs supporting the asset; no third-party bridge is required for the native XRPL issuance. This creates a dollar-liquidity rail on XRPL, but it does not establish a Circle–Ripple equity relationship, a joint venture, or net XRP purchases.
- Circle announced the **Arc public mainnet launch on 2026-09-16**. Circle's current USDC page lists native support on 38 networks, including XRPL, as of that date. Circle's launch materials identify SBI Group as a **founding validator** on Arc; SBI's stated role includes network operation/governance and its broader on-chain initiatives. Arc is a separate Circle L1, not the XRP Ledger, and its activity is not automatically XRP demand.
- Ripple's RLUSD and Circle's USDC are separate issuer liabilities. Both can be available on XRPL, but issuer, reserve, redemption, distribution and on-ledger liquidity must remain separate in the model.

#### 7.12.9 Coinbase–Circle economics and Coinbase's XRP access

- Circle's Q1 2026 Form 10-Q reports **US$330.6 million** of distribution costs in connection with its Coinbase agreements for the three months ended March 31, 2026 (versus US$303.2 million in Q1 2025). It describes Coinbase allocations tied to USDC held on Coinbase after Circle's issuer retention, plus a share of remaining ecosystem-growth economics after approved third-party participant payments. Circle's Q1 2026 operating indicators show USDC circulation of **US$77.049 billion** at quarter-end, **US$75.2 billion** average circulation and a **17.2%** daily weighted-average share on Circle's own platform. These figures are Circle-reported and do not identify the share held on XRPL or SBI VC Trade.
- Coinbase's current XRP support article says XRP is supported on Coinbase Retail, Prime and Custody, but not in Japan, New York or Singapore and not on Coinbase Wallet. This current support matrix supersedes assumptions based on Coinbase's 2021 suspension notice, which described a different Wallet status.
- Coinbase's 2023 perpetual-futures announcement lists XRP contracts settled in USDC, with up to 3x leverage at launch. This is a Coinbase derivatives product using USDC collateral/settlement; it is not a Ripple–Coinbase corporate equity relationship and does not measure spot XRP demand.
- Coinbase's October 2026 RLUSD distribution/listing arrangement with Ripple (already documented in §7.12.5) is a separate commercial relationship from Coinbase's USDC distribution economics with Circle. No primary source reviewed here establishes a Coinbase equity interest in Ripple or a Circle–Ripple joint venture.

#### 7.12.10 SBI Ripple Asia — tokenized-deposit proof of concept, not commercial XRP demand

- SBI Holdings' 2026-02-26 release says SBI Ripple Asia conducted a proof of concept for low-cost tokenized deposits and deposit-based digital money using existing SBI domestic transfer infrastructure (MoneyTap) and an XRPL-based token issuance platform. The announcement is a concept demonstration; it does not establish a live deposit product, customer balances, payment volume, or XRP as the principal settlement asset.
- SBI Ripple Asia's 2026-02-24 announcement with DSRV Labs describes joint research into Japan–Korea remittance/payment services using XRPL. This is research/implementation exploration, not evidence of a launched corridor or quantified XRP demand.

#### 7.12.11 Relationship graph and evidence boundaries

| Edge | Primary evidence | Correct interpretation |
|---|---|---|
| Coinbase ↔ Circle | 2023 collaboration/equity announcement; Circle SEC filings | Coinbase owns a minority equity stake in Circle and receives USDC distribution economics; Q1 2026 distribution costs were $330.6M |
| Circle ↔ SBI Holdings | Circle SBI Japan K.K. 50/50 JV; Circle's 2025 USDC Japan launch | Direct USDC distribution JV; Circle consolidates the VIE, SBI is noncontrolling |
| SBI Holdings ↔ Ripple | SBI Ripple Asia JV; SBI VC Trade/Ripple RLUSD launch; SBI Remit ODL corridor | Separate software, distribution and payment-operator roles |
| Ripple ↔ Coinbase | Coinbase RLUSD listing/distribution | Direct commercial distribution relationship; no equity tie established |
| Circle ↔ XRPL | Native USDC issuance on XRPL | Network integration, not a corporate partnership with Ripple |
| SBI Group ↔ Circle Arc | Founding validator announcement | Validator/governance participation on Arc, a separate L1 |
| Coinbase ↔ XRP | Retail/Prime/Custody support; XRP perpetuals settled in USDC | Exchange and derivatives access; no corporate control or XRP purchase inference |

**Source independence:** Circle's SEC Form 10-Q is a regulatory filing by Circle and is the strongest evidence for the Circle SBI Japan K.K. ownership/consolidation and Coinbase distribution-cost facts. Circle, Coinbase, Ripple and SBI releases are primary company statements; jointly issued releases count as one coordinated announcement, not independent corroboration. No raw HTTP bytes or independent timestamp anchor were captured in this browser research pass.

**Disconfirming evidence retained:** (1) Circle's JV had no significant operating results as of 2026-03-31; formation is not proof of material USDC distribution volume. (2) Native USDC on XRPL does not prove XRP purchases or XRP bridge use. (3) Arc is not XRPL. (4) RLUSD settlement is not XRP settlement. (5) Coinbase XRP listing/derivatives support does not establish Ripple equity ownership. (6) SBI Ripple Asia's tokenized-deposit work is a POC, not a live banking product. All these observations remain research-only and model-ineligible.

Additional primary-source register:
50. Circle Q1 2026 Form 10-Q, including Circle SBI Japan K.K. and Coinbase distribution economics: https://www.sec.gov/Archives/edgar/data/1876042/000187604226000150/crcl-20260331.htm
51. Circle — USDC native on XRPL (2025-06-12): https://www.circle.com/blog/now-available-usdc-on-the-xrpl
52. Circle — Arc public mainnet launch and founding validators (2026-09-16): https://www.circle.com/pressroom/circle-launches-arc-mainnet-an-economic-operating-system-for-the-internet
53. Circle — USDC distribution in Japan with SBI (2025-03-25): https://www.circle.com/pressroom/circle-strengthens-commitment-to-japan-with-new-investment-and-expanded-usdc-access
54. Coinbase Help — current XRP support by product/jurisdiction (accessed 2026-11-25): https://help.coinbase.com/en/coinbase/trading-and-funding/cryptocurrency-trading-pairs/ripple-sec
55. Coinbase — XRP perpetual futures settled in USDC (2023-10-18): https://www.coinbase.com/blog/coinbase-customers-in-eligible-non-us-jurisdictions-can-now-trade
56. SBI Holdings/SBI Ripple Asia — tokenized-deposit and deposit-based digital-money POC (2026-02-26): https://www.sbigroup.co.jp/news/pr/2026/0226_16145.html
57. SBI Holdings/SBI Ripple Asia — Japan–Korea remittance/payment research with DSRV (2026-02-24): https://www.sbigroup.co.jp/news/pr/2026/0224_16132.html


---

## 7.12.12 2026-11-25 — SBI/Evernorth capital deployment: actual cash-funded XRP purchase verified

**Evidence standard:** SBI's announcement is a company statement of intended use; the later SEC prospectus and Form 10-Q are the stronger evidence for the financing structure, acquisition and custody. This section remains research-only and is not an immutable ingestion receipt.

- **SBI commitment (2025-10-21):** SBI Holdings said SBI Group would contribute **US$200 million in cash** to Evernorth's PIPE and that proceeds would be used primarily to purchase XRP on the open market. This is the announced commitment and use-of-proceeds intent, not by itself proof of execution.
- **SEC Form 424B3 (filed 2026-10-19):** The filing identifies four “SBI Stockholders” — SBI Venture Fund 2023A Investment LPS, SBI Venture Fund 2023B Investment LPS, SBI PE Holdings Co., Ltd. and SBI Holdings USA, Inc. — as entities controlled by SBI Holdings. Their subscription amendments were subject to a 39.9% ownership cap. The filing describes **US$214.05 million** of aggregate Advance Funding cash proceeds (plus 600,000 XRP in kind) and says Evernorth used the **US$214.05 million cash proceeds to purchase 84,365,876.3625 XRP**. This verifies an actual aggregate cash-funded XRP acquisition, not merely an intention.
- **Attribution boundary:** SBI publicly announced a US$200 million contribution, and SBI-controlled entities are identified among the Advance Funding subscribers. The SEC filing does not allocate the 84,365,876.3625 XRP purchase among individual subscribers. Do not claim that all 84.365 million XRP, or a mathematically prorated amount, was purchased with SBI's specific dollars.
- **In-kind capital is separate:** The same closing disclosure reports approximately **388,910,554 XRP contributed in kind** by multiple parties, including Ripple-related and other investors. These contributions are not cash purchases and are not all attributable to SBI. Keep cash subscriptions, open-market acquisitions, XRP contributions, trust-account proceeds, debt and optional equity facilities as separate ledger events.
- **Post-close financing:** A **US$30 million 4.00% PIK convertible note** was issued after the October 9, 2026 business-combination closing; its stated possible uses include XRP acquisitions and other ecosystem activity, but the filing does not prove those proceeds had been used to buy XRP. The October 23 equity-line facility permits, but does not require, sales of up to 5,218,935 shares; potential proceeds are not actual cash until notices and purchases occur.
- **Corporate transition:** Evernorth was a wholly owned Ripple subsidiary at September 30, 2026; the business combination closed October 9, after which the public parent structure changed. The prospectus describes the public company as a holding company whose principal asset is a 71.5% interest in Pathfinder, with no independent means of generating revenue.
- **Custody and Coinbase boundary:** The SEC prospectus says all XRP is held through BitGo Trust, initially in cold storage; the stated US$250 million cold-storage insurance is shared across BitGo clients, not dedicated to Evernorth. Evernorth selected **Coinbase as its principal market for financial-reporting valuation**, while also stating it does not actively trade XRP on digital-asset markets for that accounting determination. This is not evidence that Coinbase is the custodian or execution venue for the treasury. BNY's announced XRP custody support is not evidence that Evernorth moved its XRP to BNY.
- **Liquidity/risk context:** The Form 10-Q reports US$1.722 million net cash used in operating activities for the period ended September 30. It explains that the reported US$32.9 million net loss included large non-cash fair-value and digital-asset impairment items; do not equate reported loss with cash burn.

**Reconciliation:** The earlier statement that SBI's US$200 million was “not proof of open-market XRP purchases” remains correct only as a subscriber-specific attribution caveat. It is now incomplete if read as saying no actual cash-funded purchase is verified. The SEC filing confirms that the aggregate Advance Funding cash pool — in which SBI-controlled entities participated — funded 84,365,876.3625 XRP purchases. Exact SBI-dollar-to-XRP allocation remains undisclosed.

## 7.12.13 2026-11-25 — Kamilah Stevenson channel-level identity and public-video index

**Attribution standard:** The main public channel self-identifies as Kamilah Stevenson, links to the Prescribe Wealth bio domain, and publishes posts signed “Kamilah.” The linked official site identifies Dr. Kamilah Stevenson and MKS Health LLC as the founder/company. This provides high-confidence channel-to-brand attribution, but the official site does not reciprocally link to the channel in the page reviewed. Therefore this is a **channel-level inventory**, not independent proof of the person's legal identity or a blanket endorsement of every statement.

- Primary channel: https://www.youtube.com/@drkamilahstevenson — page index reported approximately 142K subscribers and 1.2K public videos on 2026-11-25; link target: https://go.prescribewealth.com/yt-bio. Official brand page: https://prescribewealth.com/.
- The main channel's own public post announces a second channel, https://www.youtube.com/@PrescribeWealth. The link is attributable to the main channel; a separate inventory of that channel was not available in this capture.
- Similar-name channels, including https://www.youtube.com/@KamilahStevensonXrpStocks, were not cross-linked by the main channel or official brand page and remain **unverified/excluded**. “Camilla” is not independently verified as the same person; the verified channel spelling is “Kamilah.”
- Public XRP-related channel-index sample (relative ages/views are publisher-index snapshots, not independently verified performance metrics):
  1. “This NEW Bank Deal Shows Exactly Where XRP Is Headed” — 29K views, index says 1 day ago.
  2. “This New SEC Proposal Could Unlock Trillions for XRP (and nobody realizes)” — 28K, 2 days ago.
  3. “Exactly How to Retire With Your XRP Portfolio (Even If You're Cash Poor)” — 41K, 4 days ago.
  4. “XRP vs Banks: Why Your Money Needs Autonomy NOW” — 9.8K, 5 days ago.
  5. “Did SWIFT Just Change XRP Forever? (The Truth)” — 77K, 5 days ago.
  6. “BlackRock Is Moving Wall Street Onchain. XRP Holders, Pay Attention.” — 21K, 8 days ago.
  7. “A $119 Billion African Bank Just Put Its License Behind XRP” — 27K, 9 days ago.
  8. “A New XRP Tool Can Buy and Sell for You” — 13K, 11 days ago.
  9. “Invest NOW or Get Left Behind. Institutions Are Already Moving.” — 16K, 12 days ago.
  10. “The CFTC Just Said What XRP Holders Waited Years to Hear” — 44K, 12 days ago.
  11. “Wall Street Just Got a Company Built to Keep BUYING XRP” — 16K, 2 weeks ago.
  12. “XRP Ledger Technology Just Reached Europe's Central Bank” — 11K, 2 weeks ago.
- The specific video “This NEW Bank Deal Shows Exactly Where XRP Is Headed” has a separate search result dated **2026-10-20**, while the channel index displayed “1 day ago.” Preserve this publication-date conflict; do not silently choose one. Its indexed description discusses Standard Chartered/LMAX and RLUSD custody/collateral, and distinguishes RLUSD infrastructure from automatic XRP demand. It is not the October 27 BNY/C2FO announcement.
- No transcript-level claim review was completed for the listed videos. Titles are discovery metadata only; verify every named institution, regulatory action, flow and XRP-demand claim against primary evidence before using it in research.

## 7.12.14 Exact-phrase and acronym update

- **“ASK Coin”** remains unresolved: no primary-source XRP/XRPL identity or relationship was established.
- **“actual capital”** remains unverified as an exact phrase/entity. Actual cash-funded XRP acquisition is now established by the Evernorth SEC filing described above; that is a factual capital-flow finding, not a match for the quoted phrase.
- **“SBIC, ChatGPT SBIC”** has no official ChatGPT relationship in the reviewed sources. SBIC East/Central/West are the three statutory SME investment companies. A separate 2007 SBI Holdings release used “SBIC” for **SBI Capital Co., Ltd.**, whose 40% stake was transferred to Goldman Sachs to form a joint venture; this is a historical acronym use, not the East/Central/West trio.
- The U.S. SBA's “Small Business Investment Company (SBIC)” program is another distinct use of the acronym and is not the Japanese regional trio.

**Additional primary-source register:**

58. SBI Holdings — Evernorth PIPE investment and US$200M cash commitment (2025-10-21): https://www.sbigroup.co.jp/english/news/pdf/2025/1021_a_en.pdf  
59. Evernorth Holdings Inc. Form 424B3 (filed 2026-10-19; Advance Funding, SBI Stockholders, XRP acquisition and custody): https://www.sec.gov/Archives/edgar/data/2092592/000119312526425367/d184594d424b3.htm  
60. Evernorth Holdings Inc. Form 10-Q for quarter ended 2026-09-30 (filed 2026-11-13): https://www.sec.gov/Archives/edgar/data/2092592/000162828026073871/xrpn-20260930.htm  
61. SBI Holdings — 2007 use of “SBIC” for SBI Capital Co., Ltd.: https://www.sbigroup.co.jp/news/2007/0521_852.html  
62. Main channel index and public uploads: https://www.youtube.com/@drkamilahstevenson  
63. Prescribe Wealth / MKS Health LLC official brand page: https://prescribewealth.com/  
64. Main channel-announced second channel: https://www.youtube.com/@PrescribeWealth  
65. Unverified lookalike channel excluded from attribution: https://www.youtube.com/@KamilahStevensonXrpStocks

## 7.12.15 2026-11-25 — SBI 1H FY2026 primary-source update: Ripple, Evernorth, Bitbank, stablecoins and Claude

**Primary source:** SBI Holdings, *Financial Results for the Six-month Period Ended September 30, 2026*, published **2026-11-02**. PDF: https://www.sbigroup.co.jp/english/investors/disclosure/presentation/pdf/261102presentations.pdf. This is SBI's own corporate presentation; it is not an independent chain-data audit.

### XRP distribution and Evernorth

- **Page 50; quantities as of 2026-10-28:** SBI depicts approximately **63.35bn XRP circulated in the market**, **5.23bn “Actual XRP”**, **31.4bn under escrow**, and **0.01bn burned**. The slide explicitly places “Actual XRP” and “Under Escrow” inside **“Ripple’s Holdings Currently Not in Circulation.”** It identifies Ripple as an **SBI Holdings investee company**.
- The slide's “Actual XRP” is a Ripple holdings category, not “actual capital,” cash, free float, an exchange balance, or an observed transaction flow. The JPY7.6tn equivalent and JPY13.3tn circulated-market capitalization are calculated using the XRP price on 2026-10-28; they are not current marks.
- **Page 51:** SBI says Evernorth, backed by investments from the SBI Group, Ripple and others, listed on NASDAQ as **XRPN on 2026-10-12**. SBI reports approximately **473m XRP** held, JPY140.0bn market capitalization, and SBI Group voting rights of **36.1%** with **20.5% economic interest**. The holdings ranking is based on CoinGecko as of 2026-11-02; the market-cap calculation uses an Oct. 22 share price and share count. These are SBI-reported metrics, not an independent custody attestation.
- **Attribution boundary:** 473m is Evernorth's reported total, not 473m owned by SBI. The prior SEC filing's **84,365,876.3625 XRP** cash-funded acquisition was made from aggregate Advance Funding cash proceeds in which SBI-controlled subscribers participated; the filing does not allocate that purchase to individual subscribers. The 473m figure must not be treated as a new SBI cash purchase or as a direct continuation of the 84.365m transaction.
- **Counterevidence / operating context:** SBI reports its Crypto-asset Business 1H FY2026 revenue at **JPY23.1bn (-30.1% YoY)** and profit before income tax at **-JPY1.6bn** (page 53). SBI says the market remained unstable and cites dimming prospects for U.S. CLARITY Act enactment within the year. This is management commentary, not an independent causal estimate.

### SBI exchange footprint and on-chain financial strategy

- **Bitbank:** SBI says Bitbank joined the Group in August 2026 and became a wholly owned SBI Holdings subsidiary on **2026-10-01** (page 53). The combined SBI VC Trade / BITPOINT / bitbank services are shown at **3.05m accounts** as of September 2026, with 2.03m attributed to SBI VC Trade and 1.02m to bitbank; combined deposit balance is approximately **JPY1,111.6bn as of 2026-09-30** (page 54). These are platform-account and deposit metrics, **not XRP balances, XRP deposits, or XRP exchange flows**.
- **SBI Coinhako:** SBI reports Coinhako became a consolidated subsidiary and was renamed SBI Coinhako, with a **51.69% investment ratio** (pages 70–71). The deck describes an effort to combine **JPYSC, USDC and RLUSD** through SBI Coinhako for yen-dollar cross-border settlement. This is a stated strategy/initiative; it does not prove that all three are already being used in a live, material settlement corridor.
- **JPYSC:** SBI's 2026-10-16 announcement with Startale says they joined the Open Standard and are considering an interoperability proof of concept between JPYSC and OUSD. The SBI deck identifies Startale as a JPYSC co-issuer; SBI's July 2026 material identifies SBI Shinsei Trust Bank as issuer. Do not equate a proposed interoperability test with production volume.
- **SBI VC Trade:** SBI's 2026-07-07 release says it began handling JPYSC and RLUSD in June 2026, after USDC's Japanese launch in March 2025, and describes stablecoin-lending services. Availability and product offering do not by themselves establish outstanding balances, net flows, or XRP demand.
- **Circle / Ripple boundary:** Circle states that USDC has been natively available on XRPL since **2025-06-12**, with Circle Mint and Circle APIs supporting it. USDC remains Circle-issued; RLUSD is Ripple-issued. Their presence on the same SBI distribution/settlement strategy is not evidence of a Circle–Ripple equity relationship or a shared issuer.

### SBI Group AI adoption — relevant market signal, not a Barrot integration

- **Pages 59–60:** SBI says SBI Securities began using Anthropic Claude Security in July 2026 and Claude Mythos in October 2026 for vulnerability diagnosis; the deck says Claude Security is a Claude Enterprise feature and that the tools are available through the Group's common Claude platform.
- **Page 63:** SBI says Claude was introduced at **71 Group companies**, with **10 companies** integrating it by API into their own systems; Microsoft 365 integration was also being rolled out in stages from September.
- This is company-reported enterprise adoption evidence. It does not mean Barrot is connected to SBI, Claude, or SBI internal systems. It is relevant to the nine-platform capability map and potential future buyer research only after Barrot's own security and product claims are verified.

## 7.12.16 SBIC East / Central / West — Japanese identity resolved from primary sources

The Japanese **SBIC** references are three regional **Small and Medium Business Investment & Consultation** corporations established in 1963 under Japan's Small and Medium Business Investment & Consultation Companies Act. Their own websites identify one another as **sister companies**. They are separate legal entities and are **not SBI Holdings subsidiaries** in the reviewed primary sources.

| Regional name | Legal/company name | Established | Published operating area | Primary profile |
|---|---|---:|---|---|
| SBIC East Japan | Tokyo Small and Medium Business Investment & Consultation Co., Ltd. | 1963-11-15 | Shizuoka, Nagano, Niigata and eastward; 18 prefectures | https://www.sbic.co.jp/company/profile/ |
| SBIC Central Japan | Nagoya Small and Medium Business Investment & Consultation Co., Ltd. | 1963-11-18 | Aichi, Gifu, Mie, Toyama and Ishikawa | https://www.sbic-cj.co.jp/company/about/ |
| SBIC West Japan | Osaka Small and Medium Business Investment & Consultation Co., Ltd. | 1963-11-20 | 24 prefectures west of Fukui, Shiga, Nara and Wakayama | https://www.sbic-wj.co.jp/profiles/profile/ |

- Tokyo's profile lists local governments, chambers of commerce, financial institutions and business companies among shareholders, and links Nagoya and Osaka as sister companies. Nagoya and Osaka profiles independently list the other two as sister companies.
- Osaka's official profile calls it a policy-implementation institution under the Act. An official SBIC West release states **SBIC® and 投資育成® are registered trademarks of the three companies**.
- Tokyo SBIC East's official training page advertised a two-day **Generative AI and Machine Learning for Manufacturing** course on **2025-06-12 and 2025-06-13**, including ChatGPT and Copilot training. The course was limited to SBIC investee companies (JPY35,000; general companies excluded). This is a training course, **not** an OpenAI partnership, product integration, or ownership link.
- A separate historical SBI Holdings release used “SBIC” for **SBI Capital Co., Ltd.** in 2007; that is a different acronym use and must not be conflated with the regional trio. The U.S. SBA Small Business Investment Company program is another unrelated use of “SBIC.”

## 7.12.17 “ASK Coin” candidate — Permission ASK token, no XRP link established

- The best-supported current candidate for “ASK Coin” is **ASK**, the native utility token of the **Permission** ecosystem. Permission's official documentation identifies it as an omnichain token using LayerZero OFT and Stargate, with official contracts:
  - Base: "0xBB146326778227A8498b105a18f84E0987A684b4"
  - Polygon: "0xaA3717090CDDc9B227e49d0D84A28aC0a996e6Ff"
- Permission's 2026-09-22 blog says its embedded wallet is powered by Coinbase: Coinbase holds the private keys on users' behalf, while Permission users authorize transactions through their login. This is a direct **Permission–Coinbase wallet-infrastructure** relationship, not a Coinbase–Ripple or XRP relationship.
- Permission's 2025-01-10 announcement describes ASK on Base and Coinbase Wallet access. The same Base contract appears in the current Permission documentation; do not infer a separate XRP token from the name “ASK.”
- No official evidence links Permission ASK to XRP, XRPL, Ripple, SBI, RLUSD or USDC. The exact phrase “ASK Coin” in the original source context remains unconfirmed; treat Permission ASK as a candidate identity, not a definitive match.

## 7.12.18 Exact-phrase reconciliation

- **“actual capital”**: no primary-source match established. The new SBI deck's **“Actual XRP”** is explicitly a Ripple holdings category, not a synonym for actual capital or cash deployment.
- **“SBIC, ChatGPT SBIC”**: no formal SBIC–OpenAI partnership or ChatGPT product integration found. The verified connection is a 2025 Tokyo SBIC East training course that included ChatGPT for investee companies.
- **“ASK Coin”**: Permission ASK is the strongest current candidate, but no XRP relationship or source-context match is established.
- Preserve these as separate hypotheses; do not combine them into a single entity or capital-flow narrative.

## 7.12.19 Kamilah Stevenson public-video inventory — additional popular-index sample

The channel-level attribution and 12 most-recent public videos are recorded in 7.12.13. The same public channel index also surfaced these popular XRP-related titles (view counts and relative ages are index snapshots from 2026-11-25, not verified lifetime analytics):

1. “Japan Just Ended 30 Years of ZERO Interest Rates—Why XRP Could Explode” — 253K views, about 10 months.
2. “How the Wealthy Will Use XRP (Most People Won't Understand)” — 151K, about 8 months.
3. “Flare Is Putting 100 Million XRP to Work. Holders Can Earn From It” — 148K, about 1 month.
4. “Why XRP Could Be Repriced (Banks Aren't Trading It)” — 143K, about 10 months.
5. “Banks Just Got the GREEN LIGHT On Crypto—Are You Positioned” — 139K, about 7 months.
6. “SEC Silent, CFTC Approved: XRP Just Got Treated Like Gold” — 135K, about 10 months.
7. “The CLARITY Act Just Failed in the Senate. What This Means for XRP” — 129K, about 1 month.
8. “SWIFT Just Connected 11,000 Banks—and XRP Is at the CENTER” — 86K, about 6 months.
9. “Why Banks Need XRP to Be Expensive (Retail Is Thinking About It Wrong)” — 84K, about 10 months.
10. “Most XRP Holders Don't Understand What They're Actually Holding” — 83K, about 7 months.
11. “Japan's Top Financial CEO Just Publicly DEMANDED The US Senate Act On XRP” — 82K, about 4 months.
12. “Did SWIFT Just Change XRP Forever? (The Truth)” — 77K, about 5 days.

**Evidence boundary:** These are public channel titles and discovery metadata only. No transcript-level claim audit was completed for this additional popular-index sample. Treat each title as a research lead, not evidence that a bank, regulator, SWIFT, central bank, or payment corridor adopted XRP.

**Additional primary-source register:**

66. SBI Holdings — 1H FY2026 Financial Results deck (published 2026-11-02; XRP, Evernorth, Bitbank, Coinhako, Claude and APAC digital-asset strategy): https://www.sbigroup.co.jp/english/investors/disclosure/presentation/pdf/261102presentations.pdf  
67. SBI Holdings — SBI/Startale join Open Standard; JPYSC/OUSD interoperability PoC under consideration (2026-10-16): https://www.sbigroup.co.jp/news/2026/1016_16665.html  
68. SBI Holdings — SBI VC Trade account milestone and USDC/JPYSC/RLUSD offering (2026-07-07): https://www.sbigroup.co.jp/news/2026/0707_16468.html  
69. SBIC East — Tokyo Small and Medium Business Investment & Consultation company profile: https://www.sbic.co.jp/company/profile/  
70. SBIC Central — Nagoya Small and Medium Business Investment & Consultation company profile: https://www.sbic-cj.co.jp/company/about/  
71. SBIC West — Osaka Small and Medium Business Investment & Consultation company profile: https://www.sbic-wj.co.jp/profiles/profile/  
72. SBIC West — official release identifying SBIC® as a registered trademark of the three SME investment companies (2025-06-17): https://www.sbic-wj.co.jp/wp/wp-content/uploads/2025/06/%EF%BC%96%E6%9C%88%E8%A8%98%E8%80%85%E7%99%BA%E8%A1%A8%E8%B3%87%E6%96%99.pdf  
73. SBIC East — Generative AI and Machine Learning for Manufacturing training, including ChatGPT (2025-06-12/13): https://www.sbic.co.jp/training/20250612co/  
74. Permission — official ASK token contract addresses and LayerZero OFT details: https://docs.permission.ai/ask-token/contract-addresses  
75. Permission — ASK wallet update powered by Coinbase embedded wallet (2026-09-22): https://www.permission.ai/blog/ask-wallet-update  
76. Permission — ASK now live on Base and official contract (2025-01-10): https://www.permission.ai/blog/ask-is-now-live-on-base-eeaba  
77. Circle — native USDC on XRPL (2025-06-12): https://www.circle.com/blog/now-available-usdc-on-the-xrpl  
78. Circle — current USDC issuer, reserve and supported-chain information: https://www.circle.com/usdc  
79. Ripple — RLUSD issuance/custody structure and institutional support: https://ripple.com/ripple-press/standard-chartered-launches-rlusd-custody-and-joins-planned-collateral-integration-with-ripple-and-lmax-group/  

