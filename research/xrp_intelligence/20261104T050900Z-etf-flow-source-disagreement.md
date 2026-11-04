# XRP ETF flow disagreement — November 2, 2026

**Captured:** 2026-11-04T05:09:00Z  
**Data date compared:** 2026-11-02  
**Prediction status:** NOT_ISSUED

## Two materially different public estimates

| Provider | Reported November 2 flow | Coverage / method |
|---|---:|---|
| XRP Insights | −32,825 XRP, approximately −$42K | Six spot XRP ETFs plus BITW XRP sleeve; issuer-holdings delta; GXRP flow excluded |
| ByKaranteli | −$530K | USD flow from its collection network; visible table lists five per-fund rows |

XRP Insights reports 1,196,567,361 XRP held across its tracked products, with the latest settled date November 2. Its November 3 row is provisional and may be rewritten after issuer settlement. The JSON dataset was generated at 04:09:07 UTC on November 4.

ByKaranteli reports $1.81B cumulative inflows and $1.42B net assets, refreshed at 22:49 UTC on November 3. Its visible table attributes the November 2 −$530K to XRPC and lists five rows.

Using rounded provider values, the daily estimates differ by approximately $488K, or 12.6 times. **Do not average them.** The cause is unresolved.

## Why the numbers may differ

- XRP Insights computes flows from issuer-reported holdings changes; it excludes GXRP flows because of a known September capture gap and includes the BITW XRP sleeve.
- BITW is a multi-asset index fund, so XRP sleeve changes can reflect rebalancing.
- ByKaranteli's fund table, aggregate series and visible fund rows do not expose an identical universe in the current page view.
- Issuer settlement times and provider cutoffs differ.
- Holdings changes can reflect fees or product rebalancing, not only creations/redemptions.

## Required reconciliation

Rebuild November 2 XRP holdings and NAVs from each issuer at a common cutoff. Normalize each fund's holdings change to XRP, identify indirect exposures and index rebalancing, and keep provisional versus settled observations separate. Until that is done, both provider values remain disputed features rather than a single capital-flow fact.

## Sources

- [XRP Insights ETF data and methodology](https://xrp-insights.com/data)
- [XRP Insights machine-readable totals](https://xrp-insights.com/data/xrp-etf-totals.json)
- [ByKaranteli XRP ETF flows](https://bykaranteli.com/etf/xrp)
