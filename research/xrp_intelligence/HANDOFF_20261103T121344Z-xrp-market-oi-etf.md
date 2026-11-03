# XRP Market Structure Handoff — 2026-11-03 12:13:44 UTC

## New findings
- Three global OI aggregators differ: TradRadar $1.96B (7 exchanges, 04:05 UTC), Kodexius $834.52M (7 linear contracts, 5 exchanges, 06:04 UTC), and Loris $2.24B (39 venues, 07:20 UTC). Swiftedge separately reports $212M across on-chain perp venues (Hyperliquid/Lighter subset, 04:38 UTC). These are different coverage universes; do not average.
- TradRadar reports +1.89% 24h OI, +0.0064%/8h weighted funding, at least $2.49M liquidations (mostly longs), and 3.46 long/short account ratio. Account counts are not notional exposure. Kodexius shows venue funding divergence, including negative Bybit funding.
- ETF holdings: CryptoETF’s five-fund universe reports 1.14217B XRP; XRP Insights’ six spot funds plus BITW reports ~1.20B. The ~54.4M difference is approximately XRPR 33.39M plus BITW 20.92M, with a small cross-date/rounding residual. Not a same-date reconciliation.
- November 2 ETF flow remains provisional at XRP Insights until issuer holdings are re-settled. Missing fund reports remain null, never zero.
- CoinGecko historical volume: Oct 31 $3.160B, Oct 30 $2.709B, Oct 29 $1.846B, Oct 28 $1.427B, Oct 27 $1.375B; captured Nov 2 volume $808.8M, close not yet populated.
- XRP Insights’ Ripple escrow snapshot is 31.10B as of ledger 108073992, Nov 2 20:20 UTC; next unlock Dec 1 1B; provider reports ~70% re-lock over 12 months. Unlock is not sale.

## Forecast
NOT_ISSUED. OI provider disagreement, non-synchronized observations and unknown positioning composition do not support calibrated directional inference.

## Data rules
Store OI by venue/instrument/contract/settlement currency/unit/time. Keep funding, account ratios, notional exposure and liquidations separate. ETF holdings and flows are separate; include fund-of-fund look-through and same-date issuer holdings. Store escrow release, re-lock and net change separately.

## Sources
- TradRadar: https://tradradar.io/markets/xrp
- Kodexius: https://kodexius.com/data/crypto-derivatives/XRP
- Loris Tools: https://loris.tools/markets/perps/xrp
- Swiftedge: https://swiftedge.uk/xrp/open-interest
- CryptoETF: https://cryptoetf.today/en/xrp-etf-flows
- XRP Insights: https://xrp-insights.com/data
- TradingDigits: https://www.tradingdigits.io/ar/xrp-etf-inflows-tracker
- CoinGecko: https://www.coingecko.com/en/coins/xrp/historical_data
- TotalMarketCap: https://totalmarketcap.com/crypto/xrp-xrp

## Next
Circle Q3 results Nov 4 at 13:00 UTC; actual XRPL fixCleanup3_4_0 activation; synchronized contract-level OI reconciliation; issuer-level ETF holdings reconciliation; leakage-safe walk-forward and calibration.
