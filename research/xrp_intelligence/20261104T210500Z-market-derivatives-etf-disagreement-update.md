# XRP market, derivatives and ETF cross-check — 2026-11-04 21:05 UTC

## Spot snapshot

Kraken's public XRP/USD ticker returned last **$1.30059**, best bid **$1.30041** (1,921 XRP displayed), best ask **$1.30042** (561 XRP displayed), mid **$1.300415**, and spread **0.0769 bps**. The displayed top-of-book size imbalance is 54.8% toward the bid. Last price was 2.00% above the UTC-day open and 0.77% above Kraken's 24-hour VWAP.

24-hour volume was 42.98M XRP, with a displayed high of $1.34 and low of $1.24016. Kraken's UTC-day open must not be described as a rolling 24-hour open. The bid/ask sizes are only the best displayed levels, not full order-book depth or executable liquidity.

The response was exposed as rendered JSON by the research interface. Original HTTP bytes and an immutable SHA-256 receipt were not available. This observation is research-only and model-ineligible.

## Derivatives disagreement

Secondary provider open-interest estimates ranged from **$865.53M** (Kodexius, 12:49 UTC) to **$1.44B** (Liqwall, 00:32 UTC), **$2.06B** (TradRadar, 15:30 UTC), and **$2.99B** (Alpha Finance, 15:50 UTC). This 3.46x spread is not a synchronized market range: the providers use different contract universes, venue coverage, timestamps and aggregation methods. Do not average these values or interpret the difference as a real change in open interest.

Where reported, funding was mildly positive near +0.01% per eight hours and long-account shares were roughly 70%-76%. These are secondary, non-synchronized account/contract indicators, not verified net notional positioning. Alpha Finance's liquidation bands are explicitly modelled estimates, not confirmed resting orders or liquidation queues.

## ETF flow disagreement

For the November 3 trading day:
- ByKaranteli reported $0 net flow across five visible funds, provisional pending issuer settlement.
- Maketo also reported $0 across five funds.
- XRP Insights reported an estimated 162,050 XRP outflow (about $207,400 at its stated price) across six spot funds plus BITW.

These are overlapping secondary holdings-derived aggregations with different coverage and update times. Zero may reflect unchanged holdings or incomplete reporting; it is not proof of no creations/redemptions. No final full-universe issuer-settled flow is asserted.

## Event and macro context

The earlier same-day protocol check records `fixCleanup3_4_0` enabled at ledger 108112129 at 14:52 UTC. Native LendingProtocol and SingleAssetVault remain inactive; the cleanup amendment is not evidence of a live native lending or XRP-collateral market. The November 4 Treasury refunding and energy/geopolitical context remain in the linked 18:39 UTC macro addendum.

## Competing hypotheses

1. **Spot-led recovery:** supported by Kraken trading above its UTC-day open and 24-hour VWAP; weakened by single-venue coverage and unverified ETF flows.
2. **Leverage-amplified move with crowded-long vulnerability:** supported by positive funding and elevated long-account shares in secondary snapshots; weakened by 3.46x OI disagreement, non-synchronized timestamps and modelled liquidation bands.
3. **Institutional ETF demand is neutral rather than accelerating:** supported by two zero-flow reports and one negative broader-universe estimate; unresolved because issuer files have not been rebuilt at a common close.
4. **XRPL infrastructure is advancing without native-lending demand yet:** cleanup amendment enabled; lending and vault amendments remain inactive.

**Forecast status: NOT_ISSUED.** All observations remain model-ineligible pending byte-complete source receipts, synchronized exchange-native data, normalized contract coverage and a populated historical point-in-time feature store.

## Sources

- [Kraken XRP/USD ticker API](https://api.kraken.com/0/public/Ticker?pair=XRPUSD)
- [CoinMarketCap XRP](https://coinmarketcap.com/currencies/xrp/)
- [Swiftedge XRP quote](https://swiftedge.uk/xrp-price-today)
- [TradRadar XRP derivatives](https://tradradar.io/markets/xrp)
- [Alpha Finance XRP liquidation map](https://alphafinance.io/liquidation-heatmap/xrp/)
- [Kodexius XRP perpetuals](https://kodexius.com/data/crypto-derivatives/XRP)
- [Liqwall XRP derivatives](https://liqwall.com/coins/xrp)
- [ByKaranteli XRP ETF flows](https://bykaranteli.com/etf/xrp)
- [XRP Insights ETF dashboard](https://xrp-insights.com/)
- [Maketo XRP ETF flows](https://maketo.com/etf/xrp/flows)
