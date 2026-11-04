# Circle–Coinbase USDC economics handoff

Captured: 2026-11-03T22:50:19Z  
Repository: Barrot-Agent/B-Agent  
Branch: `prediction/point-in-time-feature-validator-8007440e-20261103`  
Artifact: `research/xrp_intelligence/20261103T225019Z-circle-coinbase-stablecoin-economics.json`

## Verified SEC disclosures

**Circle Q2 2026**
- USDC circulation: USD 73.269B at quarter end; USD 76.524B average.
- Circle Mint gross flows: USD 83.004B minted and USD 86.784B redeemed in Q2 (net difference -USD 3.780B); H1 net difference -USD 1.997B. These are Circle Mint customer flows, not all onchain flows.
- USDC market share: 27%; meaningful wallets: 7.01M, not unique users.
- Reserve return rate: 3.5%, down from 4.1% a year earlier.
- Circle says higher average circulation added USD 147.4M to Q2 reserve income, while a 66bp yield decline tied to Federal Reserve rate actions reduced it by USD 113.9M.
- Coinbase distribution costs: USD 324.6M Q2 and USD 655.3M H1. Contractual allocations depend on Coinbase-held USDC after issuer retention and a share of broader ecosystem growth. Circle says Q2 distribution costs paid to Coinbase decreased USD 7.7M year over year due to a lower Coinbase share of average on-platform USDC balances.

**Coinbase Q3 2026**
- Stablecoin revenue: USD 306.905M, down 5.4% year over year.
- Subscription and services: USD 570.238M, 49% of net revenue.
- Average USDC held: USD 22B, up 49% year over year and approximately 30% of average USDC market capitalization.
- Crypto trading-volume market share: 10.7%; assets on platform: 12.5% of total crypto market capitalization.
- Derivatives trading volume grew at a 179% two-year CAGR; INTX/Deribit integration completed in October, with near-term adjustment volatility expected.

## Strategic implication

Circle and Coinbase have a direct, material and explicitly documented USDC distribution-economics relationship. Higher USDC balances support both parties, but lower rates pressure Circle's reserve yield and Coinbase's stablecoin revenue. The two companies therefore have incentives to grow distribution, platform balances, payments and agentic use cases.

This is not evidence of XRP demand. USDC and RLUSD settlement can occur without XRP being used as a bridge or collateral asset. XRP-specific usage must be measured separately.

## Next action

Build rate-sensitive USDC features and platform-balance series with publication-time provenance; then test whether these variables explain any XRP market response out of sample.
