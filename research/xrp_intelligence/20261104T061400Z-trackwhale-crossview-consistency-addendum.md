# XRP research addendum — TrackWhale cross-view consistency failure

**Captured:** 2026-11-04T06:14:00Z  
**Data cutoff:** 2026-11-04T06:14:00Z  
**Prediction status:** NOT_ISSUED

## Observation

TrackWhale's XRP exchange-flow page, updated 05:52 UTC, reports:
- Seven-day total XRP outflow: **466.81M XRP / $589.79M**.
- Seven-day total XRP inflow: **210.95M XRP / $262.62M**.
- Binance seven-day XRP outflow: **340.12M XRP / $431.78M**.
- Binance seven-day XRP inflow: **199.95M XRP / $248.87M**.

Its Binance exchange page, updated 05:58 UTC, reports a 30-day XRP asset outflow of **$215.3M**.

A seven-day Binance XRP outflow of $431.78M exceeds the same provider's displayed 30-day XRP asset outflow of $215.3M. If these were cumulative measurements over the same transfer universe, the seven-day subset could not exceed the 30-day total.

The public pages do not explain whether the discrepancy comes from different wallet registries, asset-mix inclusion rules, coverage, valuation timestamps or a provider error.

Sources: [TrackWhale XRP exchange flows](https://trackwhale.io/xrp-exchange-flows) · [TrackWhale Binance exchange flows](https://trackwhale.io/binance-exchange-flows).

## Binance incident interaction

Binance reports 233,461,943.1 XRP transferred from five hot wallets on October 29. XRPLWin valued that transfer at approximately $296M at the time. The displayed 30-day XRP asset outflow of $215.3M is smaller than the incident's approximate transfer-time value.

This is evidence against assuming the incident is included in that asset-mix measure, but it does not prove whether the separate seven-day XRP page includes the incident. Exact transaction-hash membership remains unknown.

Sources: [Binance official report](https://www.binance.bh/en/blog/community/3229153443759566763) · [XRPLWin incident reconstruction](https://xrplwin.com/insights/the-63-billion-binance-hack-233-million-xrp-drained-on-the-xrp-ledger).

## Correction to prior calculation

A previous addendum calculated that 233.46M XRP would equal 50.0% of TrackWhale's reported gross seven-day outflows and 91.2% of its reported net outflow **if included**. That arithmetic was conditional, not an observed contribution.

The new cross-view inconsistency means those percentages must not be used as an estimate of actual incident contribution. Both TrackWhale aggregates are now **quarantined from model-facing organic XRP exchange-flow features** until scope and transaction membership are reconciled.

## Competing explanations

1. The seven-day XRP flow and 30-day Binance asset-mix pages use different wallet registries or inclusion rules.
2. The 30-day XRP asset-mix figure excludes the incident transfer or is a partial bucket.
3. The seven-day flow may include some or all incident transactions, but the public page does not expose membership.
4. A provider aggregation or valuation defect exists.

## Required next tests

- Obtain the 13 tracked seven-day outflow hashes and the 30-day XRP asset-mix transaction membership.
- Match all five Binance incident transaction hashes by ledger index.
- Compare the provider's point-in-time address registry and valuation timestamps.
- Reconstruct exchange flows independently from raw XRPL transactions.
- Restore the provider features only after deterministic cross-window consistency checks pass.

No directional XRP forecast is issued.
