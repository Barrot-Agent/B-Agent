# XRP market microstructure and ETF reconciliation — 2026-11-03 15:09 UTC

## Mission and cutoff
XRP intelligence and prediction-engine mastery remain the top Barrot mission. Barrot V3 remains the execution, verification and preservation foundation.

- Snapshot captured: 2026-11-03T15:09:20Z
- Main observed before this append: `0c2323231fefd3d9b5166b25cf6d4bd808b4a5b7`
- Research branch before this append: `042722b3b7d86864ffa077a7037861e740278702`
- This is a point-in-time research append, not a forecast.

## Market observations
- Kraken XRP/USD spot: last $1.27437; bid $1.27520; ask $1.27522; 24h volume 21.80M XRP; VWAP $1.26158. API response has no exchange event timestamp; retrieval time is stored separately.
- Swiftedge XRP perpetual page at 15:08 UTC: $1.2760, +2.10% on the day; 24h range $1.2444–$1.2914; visible bid wall 3.33M XRP at $1.2400 and ask wall 2.54M XRP at $1.2790. Its 24h whale tape showed 178 orders of at least $50K and net flow of -$446K, with approximate buys and sells both near $19M.
- Swiftedge's 14:18 UTC depth snapshot showed roughly balanced $26M bid/ask depth within 1%; within 2%, bids were $32M and asks $33M. Walls are transient and positioning levels are estimates, not forecasts.
- Swiftedge on-chain perpetual OI at 14:18 UTC was 165.88M XRP (about $212M), 99% Hyperliquid and 1% Lighter; this is only the provider's on-chain venue universe.
- TradRadar at 14:05 UTC reported $2.00B OI across seven exchanges (+4.45% 24h), +0.0094% OI-weighted funding per 8h, at least $5.11M liquidations and 76.6% long accounts across five exchanges.
- Kodexius at 12:44 UTC reported $877.93M across seven contracts/five exchanges, +0.0093% funding per 8h and $1.40B 24h volume.
- SwoleCharts at 14:55 UTC reported approximately $1.25B across nine ranked exchanges, +0.0098% OI-weighted funding per 8h. It separately displayed $253.03M MEXC OI as unranked, outside the stated nine-exchange total.
- CoinGlass rendered $2.90B OI but the captured summary exposed no timestamp or universe definition. It is retained as unsynchronized, not combined.

## ETF reconciliation
- XRP Insights metadata generated 13:12:10 UTC: Nov 2 is the latest settled row; -32,825 XRP (about -$42K), with 1,196,567,361 XRP held across six spot funds plus BITW's XRP sleeve. GXRP flows are excluded because of a capture gap, although GXRP holdings/AUM remain in totals. Flow is computed from issuer-reported holdings changes, so it can include non-creation/redemption changes such as BITW rebalancing and XRP-denominated fees.
- ByKaranteli refreshed 09:09 UTC and reported Nov 2 provisional net outflow of $530K across five displayed funds, with XRPC accounting for the displayed -$530K and the others at zero.
- CryptoKeyhole's 05:18 UTC capture showed Oct 30 complete at -1,123,743 XRP across four funds, while Nov 2 was partial at 3/4.
- These values are not reconciled and must not be averaged. Fund universe, settlement status and flow methodology differ.

## Interpretation and competing hypotheses
1. Positive price change plus rising OI and positive funding is consistent with increased leveraged participation; it may reinforce momentum but also increase liquidation sensitivity.
2. The cross-provider OI spread is plausibly driven by contract coverage, inverse-contract inclusion, exchange sets, mark-price conventions and timestamps. This remains unproven until same-time contract-level reconciliation.
3. Nov 2 ETF activity cannot yet be called a strong institutional demand signal: one source shows a small settled holdings-delta outflow; another shows a larger provisional USD outflow over a different fund set.
4. Visible order-book walls are local liquidity observations, not directional predictions; they can be cancelled, replenished or consumed.
5. OI is paired long and short exposure. It does not reveal beneficial ownership, hedge intent or net spot delta.

## Prediction status
`NOT_ISSUED`. No directional forecast was created. The current cross-provider data are not sufficiently harmonized for a fixed-horizon model input. No paper trade or real-money action occurred.

## Next actions
- Normalize raw contract-level OI/funding/volume by venue, contract type and settlement interval.
- Reconcile Nov 2 ETF flows against issuer holdings, shares and NAV, including XRPR/BITW and the GXRP exclusion.
- Add immutable timestamped spot/perpetual basis, funding, liquidation, depth and source-quality features to the historical store.
- Backtest wall persistence and execution impact before using order-book features.
- Preserve forecast issuance block until fixed-horizon walk-forward evaluation, leakage checks, baselines, calibration, drift and independent outcome attestation pass.
