# XRP derivatives and ETF-flow reconciliation — 2026-11-04

## Status

Research observation only. No forecast issued. Captured at 2026-11-04T00:11:18Z. Provider timestamps are asynchronous and must remain separate.

## Derivatives

- Liqwall: $1.47B reported open interest at 23:42 UTC; +2.9% 24h; +0.0102%/8h average funding; about $3.4M reported liquidations, shorts $2.7M versus longs $734K; Binance accounts 69.9% long.
- TradRadar: $2.00B at 22:50 UTC across seven named venues; +4.10% 24h; +0.0100%/8h OI-weighted funding; at least $3.46M liquidations, shorts $2.74M versus longs $725.69K; 75.9% long across five exchanges.
- Kodexius: $870.32M at 22:04 UTC across seven contracts, not seven exchanges; its enumerated set excludes Gate, Bitget and MEXC from the current table.

The apparent $0.87B–$2.00B range is not a valid statistical confidence interval. It is a scope/methodology reconciliation problem. The immediate next step is synchronized exchange-native contract-level OI with quote currency, multiplier, mark price, venue and exact UTC timestamp.

## ETF holdings-derived flows

- CryptoKeyhole: four spot funds; Nov 2 net holdings change -3,339 XRP (about -$4K); Nov 2 holdings 1.0768B XRP. Its Nov 3 update was 23:57 UTC and issuer files had been read at 23:52 UTC.
- XRP Insights: six spot funds plus BITW's XRP sleeve; Nov 2 net holdings change -32,825 XRP (about -$42K); holdings 1.1966B XRP. Its dataset explains indirect XRPR exposure, GXRP flow exclusions due to a capture gap, and possible fee/index-rebalance effects in holdings changes.

These aggregates are not directly comparable. Reconcile the four common tickers from issuer-level holdings before treating the difference as market-flow disagreement.

## Causal hypotheses retained

1. OI gap is primarily contract/venue coverage.
2. Residual gap is provider mapping/timestamp/quote-conversion error.
3. ETF flow gap is fund-universe and holdings-methodology scope.
4. Positive funding and long-heavy account ratios create leverage sensitivity, but short-dominated liquidations during the observed rise are counter-evidence to a simple immediate-downside narrative.

No probability or price target is issued. No trading action is justified by this snapshot.

## Relationship graph update

Kodexius lists XRP-USDC perpetual contracts on Hyperliquid and Binance and an XRP-USDC contract on Bybit. This creates an observed USDC-denominated XRP derivatives channel. Circle issues USDC, but there is no evidence that Circle directs, guarantees or is the counterparty to these contracts.

## Provenance

See `20261104T001118Z-xrp-derivatives-and-etf-flow-reconciliation.json` for source URLs, provider timestamps, metric scope, data-quality caveats, competing hypotheses and next actions.

Primary source URLs:
- https://liqwall.com/coins/xrp
- https://tradradar.io/markets/xrp
- https://kodexius.com/data/crypto-derivatives/XRP
- https://cryptokeyhole.com/etf-flows/xrp/
- https://xrp-insights.com/data
- https://xrp-insights.com/data/xrp-etf-flows.json
- https://www.tokenpost.com/news/investing/45984
