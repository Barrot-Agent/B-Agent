# XRP protocol-security, derivatives and event addendum — 2026-11-04T04:02:11Z

**Capture/data cutoff:** 2026-11-04T04:02:11Z  
**Main inspected:** `77069f8969a38d6ad0d91bfd68e799cf39769b5c`  
**Research PR before addendum:** `2384265d1cda7bec0e4af2f87f70254590442131`  
**Forecast status:** `NOT_ISSUED`

## Market microstructure

Kodexius reported at **03:54 UTC**: XRP perpetual open interest **$843.90M** across seven contracts; 24-hour rolling volume **$1.51B**; funding **+0.0099% per eight-hour equivalent**; OI/volume **0.56**. Venue shares within its universe: Binance 55.0%, Bybit 17.9%, OKX 12.0%, Hyperliquid 11.8%, HTX 3.3%.

Compared with the same provider's November 3 17:54 UTC snapshot, OI is lower by **3.73%** and the rolling 24-hour volume figure is higher by **11.85%**. Both captures list seven contracts, but exact instrument continuity is unverified. The rolling volume windows overlap. This is not an incremental ten-hour flow and does not prove deleveraging or net capital exit.

CoinDesk's embedded ticker displayed XRP at $1.26 and +0.38% at retrieval, without an exact quote timestamp or exchange constituents. Context only; excluded from model features.

## XRPL amendment

At capture, XRPLWin showed `fixCleanup3_4_0` at 33/35 validators (94.29%), above the 29-vote threshold. Majority began October 21 at 14:46:22 UTC. Earliest activation was November 4 at 14:46:22 UTC, conditional on uninterrupted support. Snapshot: ledger 108101949; voting ledger 108101887.

Official XRPL documentation says the amendment prevents a PaymentBurn-only delegate from crossing zero into a mint unless it also has PaymentMint. It warns developers not to delegate PaymentBurn before activation. The package also contains vault rounding/asset-delivery, loan due-date/default, AMM, permissioned DEX, trust-line, NFT, MPT, escrow, sponsorship, signing and permission-delegation fixes.

This concerns issued tokens and delegated permissions, not native XRP issuance. CoinDesk reported no public records or reports of exploitation; that is not proof of absence. CoinDesk also reported separate LendingProtocol and SingleAssetVault amendments at 19 and 21 votes versus 29 needed. The cleanup amendment is not a native XRPL lending launch.

## Upcoming issuer disclosure

Circle Investor Relations scheduled Q3 2026 results for **November 4 at 08:00 ET / 13:00 UTC**. The event was future at this cutoff. No results or guidance are inferred. After publication, extract global USDC circulation, reserve income, distribution costs, Circle Payments Network activity, Arc adoption and chain-specific XRPL metrics separately.

## Competing hypotheses

1. Protocol-security improvements may reduce issuer/delegate operational risk without generating direct XRP demand.
2. The cleanup package may be misread as a lending launch; separate LendingProtocol and SingleAssetVault status must be checked.
3. OI decline with higher rolling volume is consistent with turnover or partial deleveraging, but signed flow, liquidations and contract continuity are missing.
4. Binance's 55% share is concentration within this provider's contract universe, not proof of global venue or beneficial-owner concentration.
5. Circle's Q3 disclosures may update the USDC distribution thesis but cannot be translated directly into XRPL or XRP demand without chain- and route-level data.

## Data quality and forecast boundary

- Do not average provider figures across incompatible universes.
- Keep provider timestamp, capture timestamp, ledger index, publication time and event time separate.
- New observations are excluded from model-facing features pending raw-data lineage and historical continuity.
- No directional XRP forecast was issued.
- Next: verify amendment activation after its earliest window; review Circle Q3 after the webcast; collect exchange-native derivatives history.
