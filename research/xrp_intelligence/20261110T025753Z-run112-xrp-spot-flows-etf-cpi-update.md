# Run 112 — XRP spot, derivatives, exchange wallets, ETF flows and CPI

**Capture start:** 2026-11-10 02:57:53 UTC  
**Main SHA:** `d4d43be3427375cf79d190e768976de062e20287`  
**Integration code/test head:** `6b34115c2301007ee20f52a74b9f9742938b3f88`  
**Forecast status:** `NOT_ISSUED`

## Spot cross-check

| Venue | Last | Bid / ask | Spread | 24h XRP volume |
|---|---:|---:|---:|---:|
| Kraken XRP/USD | $1.09175 | $1.09174 / $1.09175 | 0.0916 bps | 29.75M |
| OKX XRP-USDT | 1.0964 USDT | 1.0964 / 1.0965 | 0.9120 bps | 70.38M |

OKX provider event time: **02:56:29.372 UTC**, 83.628 seconds before the run-start cutoff. Kraken and Kraken USDT/USD did not expose provider event timestamps. Normalizing OKX using the asynchronous Kraken USDT/USD quote gives approximately **$1.094997**, about **0.2974%** above Kraken's displayed last trade. This is not an executable arbitrage comparison. No full L2 depth was captured.

SHA-256 receipts cover the exact JSON response text surfaced by the public endpoint retrieval, not original HTTP wire bytes. Headers and exact retrieval timestamps were not preserved. All three observations remain excluded from model admission.

## Derivatives disagreement

- **Liqwall, 02:22 UTC:** OI $1.22B, −1.8% over 24h; liquidations $8.2M, including $7.5M longs and $706K shorts; funding +0.0055% per 8h; 74.5% of Binance XRP accounts long.
- **TradRadar, 02:00 UTC:** OI $1.66B across seven venues, −3.9% over 24h; at least $9.08M liquidations across five venues, including $8.22M longs and $864.67K shorts; funding +0.0030% per 8h; 79.8% long accounts.

The OI aggregates differ by approximately 36.1%. Venue coverage overlaps; do not average. The common observation is declining OI and long-heavy liquidations, not a directional signal.

## Exchange-wallet balances and whale transfers

XRP Insights' November 9 08:01 UTC snapshot attributes **22.35B XRP** to 701 labeled wallets across 24 exchanges. Same-wallet balances declined **25.8M XRP over seven days** and **138.1M over 30 days**. A naive total-change figure of +373.9M includes 512M XRP in two newly tracked wallets. The provider identifies 483M XRP in wrapped-token, insurance and charity reserves, including Binance-Peg XRP and cbXRP reserves.

These are labeled omnibus/custody wallets, not tradable float. Coinbase's 5.80B and Binance's 2.73B tracked balances include non-customer wrapped-token reserves.

CryptoQuant/Darkfost reports **691M XRP** transferred into Binance on November 8, valued above $900M at the then-prevailing price. The report notes a possible reserve-replenishment explanation after the October 29 theft of approximately 233.5M XRP. Neither a sale nor the reserve-replenishment hypothesis is confirmed. The same provider's earlier outflow observation is not independent evidence.

## ETF holdings

At 02:52 UTC November 10, CryptoKeyhole showed November 9 as **partial: 1 of 4 daily-tracked funds**. Bitwise's reported holdings change was −8,594,551 XRP (derived −$9.445M); the other three funds had not yet published in that snapshot. Do not call this the aggregate XRP ETF flow.

The last complete day, November 6, was −752,048 XRP (−$887K) across four funds; the last five complete trading days were −765,403 XRP. The tracker lists six funds but reads four daily. Holdings deltas can include creations/redemptions, retained staking rewards, fee sales and cash payouts.

## Macro

The BLS scheduled October 2026 CPI and Real Earnings for **November 10 at 08:30 ET / 13:30 UTC**. The release had not occurred at this capture.

## Competing hypotheses

1. **Sell-pressure risk:** large reported Binance inflow, partial Bitwise holdings reduction and long-heavy liquidations.
2. **Transfer/rebalancing and deleveraging exhaustion:** same-wallet exchange balances declined over 7 and 30 days; gross transfers may include internal reserve movement; OI contracted.

Neither hypothesis is assigned a probability. Source overlap, partial ETF reporting and incomplete market-depth provenance prevent model admission.

## Sources

- Kraken XRP/USD: https://api.kraken.com/0/public/Ticker?pair=XRPUSD
- OKX XRP-USDT: https://www.okx.com/api/v5/market/ticker?instId=XRP-USDT
- Kraken USDT/USD: https://api.kraken.com/0/public/Ticker?pair=USDTUSD
- Liqwall: https://liqwall.com/coins/xrp
- TradRadar: https://tradradar.io/markets/xrp
- XRP Insights exchange balances: https://xrp-insights.com/exchange-balances
- CryptoQuant, November 8: https://cryptoquant.com/insights/quicktake/6af0e5decd57dd300eaa1720-XRP-Whale-inflows-hit-900M-the-highest-since-2024
- CryptoKeyhole ETF flows: https://cryptokeyhole.com/etf-flows/xrp/
- BLS November 2026 schedule: https://www.bls.gov/schedule/2026/11_sched_list.htm

**No directional forecast, paper trade, real-money action or model-feature admission was performed.**
