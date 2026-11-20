# XRP market, derivatives, liquidity and regulatory refresh — Run222

**Captured:** 2026-11-17T18:03:21Z  
**Data cutoff:** 2026-11-17T17:22:00Z  
**Main:** `d28e03e7e519523c77f943984b11e78277299337`  
**Integration code head:** `5ff60f97f6447521e72d18f369f42d989a89a10d`  
**Forecast:** NOT ISSUED

## Market observations

- Investing.com displayed XRP at **$0.9556**, with a $0.9469–$0.9788 daily range. The displayed price is approximately **31.67% below** the October 21 displayed high of $1.3986. Its clock timezone was not stated.
- Fuelmaps' six-venue book snapshot at 11:00 UTC showed $7.9M bids versus $5.7M asks within 0.5%, and $11.6M versus $7.8M within 1%. This is displayed depth, not executed demand.
- CoinGlass displayed roughly $1.94B XRP open interest; Sharpe Terminal displayed roughly $1.03B across 23 tracked venues and excluded an unverified MEXC figure. The difference is unresolved. Do not average.
- Funding also diverged: CoinGlass +0.0007%/8h, FundingRates +0.0029%/8h median, Hyperliquid -0.0014%/h. Preserve venue, unit and timestamp differences.
- CoinGlass showed about $2.13B futures volume versus $446.03M spot volume (4.78x) and $3.31M liquidations, 72% long.
- November 16 ETF flow is unresolved: CryptoKeyhole showed a partial -5.197M XRP with 2/4 daily reporters; ByKaranteli showed $0 across five funds but marked the row provisional.
- A November 13 XRPL snapshot showed stablecoin market cap down 8.01% week-over-week while reported DEX volume rose 28.87%. Stock and turnover are different measures.

## Institutional and regulatory findings

- BNY announced custody support for XRP and RLUSD, a primary RLUSD reserve-custody role and a Ripple Prime custody relationship. This does not disclose XRP client balances or collateral use.
- Coinbase announced RLUSD availability across Prime, Exchange and retail, with XRPL, Base and Ethereum support. Coinbase Global Exchange collateral support was described as a future rollout.
- SBI's $50M Circle equity investment/Japan venture and its Arc presale participation are distinct corporate actions. Neither proves XRP purchases or XRP collateral demand.
- The March 17 SEC/CFTC interpretation explicitly lists XRP among digital commodity examples, effective March 23, 2026. It also states that a non-security crypto asset may still be offered or sold subject to an investment contract; Howey transaction analysis remains.
- The SEC's August Regulation Crypto Assets release remains a proposal in the evidence reviewed; its comment deadline was October 20. The Senate rejected cloture on the motion to proceed to H.R.3633 on September 15, 49–50. The vote was procedural, not a final merits vote.
- John Reed Stark and Lee Reiners filed an October 16 opposition comment. It is a public commenter position, not an agency or court determination.

## Disagreements and competing explanations

1. **OI universe:** $1.94B versus $1.03B; venue/contract normalization unresolved.
2. **Funding:** broad positive displays versus negative Hyperliquid hourly funding.
3. **ETF flow:** partial XRP outflow versus provisional zero USD flow.
4. **XRPL activity:** DEX turnover rose while stablecoin stock fell.
5. **Institutional adoption:** custody and RLUSD distribution expand rails, but do not prove XRP collateral use or net XRP demand.
6. **Regulation:** XRP receives explicit digital-commodity treatment in the SEC/CFTC interpretation, while transaction-specific investment-contract questions and broader market-structure rulemaking remain.

## Prediction boundary

No forecast was issued. The canonical event registry remains at 140 curated events, 54 exact publisher timestamps, 86 missing exact timestamps, zero byte-exact raw-source receipts and zero model-eligible events. All Run222 observations are research-only. No paper trading or real-money activity occurred.

## Next work

- Repair the docs index integration regression and rerun the full suite.
- Capture direct exchange and issuer data as raw bytes with receipt hashes and synchronized timestamps.
- Normalize contract units and venue coverage before reconciling derivatives.
- Reconcile ETF flows from issuer files after settlement.
- Track XRP-specific collateral schedules and actual ledger/settlement flows separately from custody and stablecoin distribution.
- Preserve no-forecast status until chronological out-of-sample evaluation supports calibrated probabilities.
