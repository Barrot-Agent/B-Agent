# XRP market, derivatives, ETF and institutional reconciliation

**Reference time:** 2026-11-08 09:07:27 UTC  
**Observed main:** `9100dbacb5f9f1b973b053a65ef1e91e96b64f72`  
**Research PR:** #1643, append-only evidence record

## Findings

- Kraken XRP/USD returned $1.16127, with a $1.16126/$1.16127 Level-1 quote and 11.073M XRP 24-hour volume. The endpoint supplied no provider event timestamp and the exact retrieval time was not retained. It is not point-in-time model eligible.
- Four derivatives aggregators ranged from $775.07M to $1.91B open interest. TradRadar and Liqwall differed by $530M and reported opposite 24-hour OI-change signs. Bentley's 17-exchange total was lower than TradRadar's seven-exchange total. Contract and venue scopes remain unresolved; values are not averaged.
- Funding providers report positive rates, but OI-weighted means, simple averages and medians are different statistics. Funding is not a directional forecast.
- ETF providers disagree on November 6: CryptoKeyhole shows a partial three-of-four fund result; Alpha Finance reports five-fund $0; XRP Insights reports six spot funds plus BITW at -663,043 XRP. Their issuer-file universes and settlement vintages overlap but are not identical. CryptoKeyhole's 9 Nov issuer-file date is future relative to its 8 Nov page update and is quarantined.
- Ripple/Coinbase RLUSD access is live on Prime, Exchange and retail, with XRPL/Base/Ethereum deposits and withdrawals. Coinbase Global Exchange collateral support was future at launch.
- BNY announced eligible-client XRP/RLUSD custody support. This is custody availability, not a disclosed balance or XRP purchase.
- Circle and Coinbase Q3 SEC filings show large but distinct USDC economics. Circle's Coinbase distribution costs are not the same accounting item as Coinbase's stablecoin revenue and must not be netted.

## Prediction boundary

No synchronized market cutoff, raw HTTP wire bytes, full order-book depth, native exchange OI payloads or common-universe issuer-level ETF reconstruction were captured. All observations remain research-only.

**Forecast: NOT_ISSUED.** No paper trade, real-money action or external model transfer occurred.
