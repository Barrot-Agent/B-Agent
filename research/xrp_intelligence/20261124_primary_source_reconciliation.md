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
