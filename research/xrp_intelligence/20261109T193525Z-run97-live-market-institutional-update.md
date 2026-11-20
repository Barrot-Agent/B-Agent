# XRP market snapshot — Run 97

**Captured:** 2026-11-09 19:35:25 UTC  
**Status:** research-only; not model-admitted; forecast not issued.

## Spot

- Kraken XRP/USD: last $1.09120; bid/ask $1.09113/$1.09119; spread about 0.55 bp; 24-hour volume 47.657M XRP; 24-hour VWAP $1.10966982; high/low $1.15640/$1.07502. No provider event timestamp was returned. The ticker's UTC-day open ($1.11203) is not its rolling 24-hour open.
- OKX XRP-USDT: event timestamp 19:35:03.368 UTC; last 1.0895 USDT; bid/ask 1.0894/1.0895; 24-hour volume 94.792M XRP. USDT was not normalized to USD; no cross-venue spread is inferred.

## Visible liquidity

Edge or Not's 19:15 UTC snapshot combined Binance spot and OKX perpetual books: $8.8M bids and $8.2M asks within 1% of mid $1.0918. It is sampled each minute and averaged over 15 minutes. Largest displayed ask: $2.4M at $1.0929; largest bid: $2.1M at $1.0897. This is mixed-market resting liquidity, not executable pure-spot depth. Orders can be cancelled and the page says it has not established predictive edge.

## Derivatives

| Provider / cutoff | OI | 24h liquidations | Funding |
|---|---:|---:|---:|
| Liqwall, 17:42 UTC | $1.23B | $36.8M; $35.5M longs | −0.0002% average; Binance +0.0057% |
| TradRadar, 17:25 UTC | $1.66B | at least $38.45M; $36.98M longs | −0.0007% OI-weighted |
| Alpha Finance, 14:04 UTC | $2.50B | $40.2M; $38.8M longs | not comparable in this snapshot |

OI differs by a little over 2x across the aggregators. Their venue sets, timestamps and methodologies overlap; do not average them or count them as independent confirmation. Alpha's liquidation clusters are modeled, not observed individual orders.

## ETF and institutional context

- XRP Insights, data as of Nov 6: 1.195B XRP across six US spot funds plus BITW; derived Nov 2–6 holdings change −812,529 XRP (about −$939K). These are holdings deltas, not issuer-confirmed cash creations/redemptions. Historical rows include reconstructed periods; inspect row-level status.
- Coin365's Nov 9 −$509.3M flow is a 25-fund, all-asset aggregate across BTC, ETH, SOL, XRP, LTC and HBAR; it is not XRP-specific.
- Coinbase's disclosure page states holdings data as of Mar 31, 2026 and defines “Commercial Engagement” broadly. XRP is marked Yes/Yes in trading and custody tables; cbXRP is Yes/Yes and RLUSD is No/Yes in the custody table. This is evidence of supported/engaged assets, not quantities, collateral utilization or XRP buying demand.
- Reuters reported a limited PNC/Coinbase pilot for USDC receipts with automatic USD conversion. It is a competing dollar-payment rail, not an XRP corridor.

## Macro event

Reuters reported Japan's Ministry of Finance breakdown on Nov 9 for intervention on July 30, July 31 and Aug 3, totaling approximately ¥15.3993T. Keep publication time separate from event dates. No XRP causal link is established.

## Source quality and admission

All values above were viewed through web-rendered pages/responses. Exact raw HTTP bodies were not preserved. Therefore no SHA-256 receipts were created, no source is model-admitted, and this artifact is research-only. Kraken lacks an event timestamp; OKX supplies one. The order-book source combines spot and perpetual markets; derivatives aggregators have overlapping venues; ETF trackers use different fund sets and flow methodologies.

**Common observation:** long-side liquidations dominate the three derivatives snapshots.  
**Competing hypotheses:** further deleveraging if spot demand fails to absorb selling; or exhaustion/mean reversion if bids persist and funding normalizes.  
**Forecast:** NOT_ISSUED.
