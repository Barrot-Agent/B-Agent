# Coinbase XRP collateral, cbXRP custody and USDC financing — 2026-11-04

## First-party custody snapshot

Coinbase's cbXRP proof-of-reserves page displayed a refresh label of **November 4, 2026, 00:17** (timezone not stated):

- XRP reserve: **152,205,724.13 XRP**
- cbXRP supply: **152,203,476.60 cbXRP**
- Difference: **2,247.53 XRP**
- cbXRP network: **Base**

Coinbase states cbXRP is backed 1:1 by XRP held by Coinbase. Its wrapped-assets help page says wrapped assets are backed 1:1 and automatically unwrap when deposited back to Coinbase. This is a first-party reserve snapshot, not an independent third-party attestation. The reserve is backing, not necessarily XRP pledged as collateral.

## Three separate Coinbase collateral channels

1. **Global Exchange perpetual-futures collateral:** XRP is an accepted collateral asset. Coinbase applies organization-level UBO ADQ caps; collateral value uses notional value times collateral weight, with the greater of base haircut and closeout-horizon haircut applied. Actual XRP-specific ADQ and utilization are not public.
2. **Global Derivatives cross collateral:** Coinbase's current table shows XRP with a **15% X:SM haircut** and a dash in X:PM. The product is limited to eligible customers in supported regions outside the U.S.; the updated terms apply to most customers from October 1, 2026. The X:PM dash is recorded as “no haircut listed,” not assumed zero.
3. **Morpho-backed USDC loans through Coinbase:** Coinbase lists XRP as eligible collateral for USDC borrowing on Morpho/Base. U.S. availability excludes New York; UK access is limited and Canada has separate availability. Actual XRP-backed loan balances are undisclosed. The loan backup page maps XRP to cbXRP on Base at `0xcb585250f852c6c6bf90434ab21a00f02833a4af`.

Coinbase's XRP-PERP specification lists USDC settlement, 25% default initial margin and maximum leverage of 50x. Settlement asset and collateral asset are distinct.

## Interpretation

This is genuine collateral and custody utility, not proof of new spot demand. It may let holders obtain dollar liquidity without selling XRP, but it also creates liquidation/reflexivity channels if collateral value falls or margin thresholds are breached. Public data does not reveal actual pledged XRP, Morpho loan balances, ADQ caps or product-level liquidation volumes.

## Sources

- Coinbase cbXRP proof of reserves: https://www.coinbase.com/cbxrp/proof-of-reserves
- Coinbase wrapped assets: https://help.coinbase.com/en/coinbase/trading-and-funding/sending-or-receiving-cryptocurrency/coinbase-wrapped-btc
- Coinbase Global Exchange collateral: https://help.coinbase.com/en/global-exchange/margin-requirements/how-does-cross-collateral-work
- Coinbase Global Derivatives haircut table: https://help.coinbase.com/en-bm/coinbase/derivatives/global-derivatives-cross-collateral
- Coinbase Morpho loan product: https://help.coinbase.com/en/coinbase/trading-and-funding/loan/loan-intro
- Coinbase cbXRP loan backup contract mapping: https://help.coinbase.com/en/coinbase/trading-and-funding/loan/loan-backup
- Coinbase XRP perpetual specifications: https://help.coinbase.com/en/global-exchange/perpetual-futures-basics/perpetual-futures-product-specifications
