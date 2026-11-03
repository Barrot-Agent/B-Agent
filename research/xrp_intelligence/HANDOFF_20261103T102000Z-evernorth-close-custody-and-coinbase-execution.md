# Barrot XRP Intelligence — Evernorth close, custody and Coinbase execution handoff

Captured: 2026-11-03 10:20 UTC

## Mission

XRP intelligence and measured prediction-engine mastery remain the highest-priority Barrot mission. Barrot V3 remains the execution, security, preservation and verification foundation.

No directional forecast, paper position or real-money transaction was created. Main was not modified. No PR was merged, no force-push or privileged workflow dispatch occurred, and no secrets or private custody data were accessed.

## Critical correction: Evernorth transaction is closed

Earlier handoff language described the Armada/Evernorth business combination as proposed. That is stale.

- Armada shareholders approved the transaction on September 30, 2026.
- The business combination closed October 9, 2026.
- XRPN began trading on Nasdaq October 12, 2026.
- Each non-redeemed outstanding Armada Class A share converted one-for-one into Evernorth Class A common stock.
- 18,463,753 public SPAC shares were redeemed for approximately $193.6M; 4,536,247 remained and converted.
- Goldman's Q2 13F reported 365,976 Armada shares worth $3,813,470 as of June 30. The filing does not establish whether Goldman redeemed, sold or held those shares through October 9. If held through closing, they would have converted one-for-one; post-close Goldman ownership is unknown.

Primary source: [Evernorth October 30 SEC prospectus](https://www.sec.gov/Archives/edgar/data/2092592/000162828026068609/xrpn-20261030.htm).

## Evernorth XRP treasury correction

The earlier derived 473,076,430 XRP total omitted the separate 200,000 XRP delayed-funding tranche.

The reconciled closing total is approximately **473,276,430 XRP**:

- 84,365,876.3625 XRP acquired using approximately $214.1M cash.
- 261,919,096 XRP private-placement in-kind contribution.
- 126,791,458 XRP Ripple contribution.
- 200,000 XRP delayed-funding contribution.
- Total in-kind XRP: 388,910,554.
- Total closing XRP: 473,276,430.3625.

The SEC prospectus states approximately 388,910,554 XRP was contributed in kind and approximately 473 million XRP was held at October 9 closing. This reconciles the additional 200,000 XRP.

## Custody and onchain attribution

SEC disclosure:
- All XRP was initially held in custody accounts at BitGo Bank & Trust.
- The prospectus says 100% was in offline/cold storage.
- Custody accounts are segregated and held for Evernorth's benefit.
- BitGo's approximately $250M cold-storage insurance is shared among eligible clients, not dedicated to Evernorth; it represented approximately 36.9% of the value of Evernorth's XRP holdings at October 9.
- Evernorth says BitGo may not pledge, lend or otherwise use its XRP unless expressly directed as part of yield-generation strategies.

Secondary public-ledger attribution:
- XRP Insights reports 103,129,905 XRP in 13 attributed wallets at validated ledger 108082781, closed November 3 at 06:06 UTC.
- It reports 370,346,663 XRP moved from attributed wallets to addresses outside its attributed set, latest October 22; destinations are not attributed.
- This is not proof of sale, loss, pledge, exchange deposit or custodian change. Unattributed destinations could be other BitGo cold wallets, internal custody movements, partner/strategy deployments or another transfer.
- Naively adding 103,129,905 current attributed XRP to the 370,346,663 moved figure produces 473,476,568, which exceeds the reported closing treasury by 200,138 XRP. The moved figure is not established as a unique net-outflow balance. Transaction-level deduplication and destination tracing are required.

## Coinbase: direct institutional and personnel links

Evernorth announced Ripple, Kraken, Coinbase and BitGo as inaugural institutional execution partners on October 14, with deployment expected to begin in Q4 2026. Partner-specific amounts, trades, fees and venues were not disclosed.

Hugo Jeandesboz joined Evernorth as CIO on October 12. The SEC-filed release states that he previously served as Co-Chief Investment Officer and Head of Solutions at Coinbase Asset Management and earlier led Coinbase derivatives trading. At Evernorth he leads XRP treasury allocation, liquidity management and active management of XRP holdings, and is the senior contact for trading counterparties and custodians.

This is a direct Evernorth/Coinbase institutional relationship and a personnel connection. It does not establish that Coinbase controls Evernorth's treasury or has executed a disclosed XRP amount.

## XRPN capital structure and XRP-per-share

Evernorth defines XRP per share as XRP attributable to Pubco divided by Class A plus Class C shares outstanding.

As of October 22:
- Class A: 26,094,680.
- Class C: 31,392,746.
- Class A + Class C: 57,487,426.
- Class C has economic/distribution rights but no ordinary voting rights, is not listed and is not transferable.
- 22,953,128 Company Units are redeemable/exchangeable for Class A.
- 9,283,847 warrants outstanding.
- 3,585,278 shares initially issuable on convertible-note conversion, up to 3,585,278 assuming maximum PIK interest under the prospectus.
- 8,930,929 incentive-plan shares reserved.
- 1,786,185 ESPP shares reserved.
- Up to 5,218,935 Class A shares under the Cantor/CF Principal equity facility.

Using 473,276,430 XRP at October 9 and 57,487,426 Class A+Class C shares at October 22 gives an indicative cross-date ratio of approximately 8.23 XRP per economic share. This is not a company-reported same-date KPI. Do not calculate a canonical NAV premium/discount until share classes, Company Units, cash, debt, expenses and potential dilution are reconciled.

XRPN market-data vendors also disagree on shares outstanding and market capitalization. Do not use vendor market cap as canonical until the denominator is reconciled.

## XRP market data quality

- CryptoETF's five-fund universe: 1,142,172,991 XRP on November 2; flow partial at 2/5 funds, both reporting zero, three missing.
- XRP Insights seven-product universe: 1,196,600,186 XRP on October 30, including XRPR and BITW.
- Adding XRPR and BITW to the five-fund total leaves only 91,345 XRP cross-date residual. Near-reconciliation, not exact same-date.
- TradRadar November 3 04:05 UTC OI: $1.96B; Kodexius November 3 06:04 UTC: $834.52M. Aggregate ratio 2.35x. Bybit differs 2.25x and Hyperliquid 2.01x, while Binance and OKX are much closer. Do not average. Contract/unit/timestamp reconciliation remains outstanding.
- Q2 13F filings verify Goldman $86.506M, Jane Street $16.427M share-only, Millennium $16.204M and Intesa $14.424M Grayscale-only. SEC Form 13F excludes shorts and does not establish net exposure. Q3 deadline is November 16, 2026.

## Current Barrot V3 repository state

- Main: `c10df2896572a7df7daebfa4f43899f76c31b100`.
- Main still contains public brain-corpus dumps and an active exporter.
- Main still contains subscriber synchronization; `web/subscribers.json` metadata is 26 bytes, contents were not inspected.
- Main Daily Digest created issue [#1538](https://github.com/Barrot-Agent/B-Agent/issues/1538) on November 3 at 00:34:42 UTC. It repeats the unvalidated 45.5% / 1,697 accuracy claim while reporting confidence 0.0, missing credentials and Groq 429.
- Main Autonomous Resolver run [#41615777310](https://github.com/Barrot-Agent/B-Agent/actions/runs/41615777310) created issues #1574–#1579 from failed PR-branch push runs. Its query lacks a 24-hour cutoff, default-branch filter and event filter. All six issues remain open; no assignment occurred because `COPILOT_ASSIGNEE` is unset.
- PR #1573 quarantines the resolver, auto-resolver, Daily Digest and other external/autonomous writers. Its current exact-head CI passed 345 tests + 8 subtests; fail-closed gate passed.
- PR #1570 quarantines public brain-corpus export and related writers. Its current exact-head CI passed 362 tests + 8 subtests; gate passed.
- PR #1572 retires invalid accuracy scoring and blocks unsupported forecast issuance. Its current exact-head CI passed 360 tests + 8 subtests; gate passed.
- PR #1571 contains this research archive. Its current head after this handoff/artifact append must be rechecked for exact-head CI before claiming final verification.

All proposals remain open, draft and unmerged. Automatic merging is disabled. No explicit merge approval has been provided.

## Upcoming checkpoints

1. November 4, 08:00 Eastern / 13:00 UTC: Circle Q3 2026 results.
2. November 4, approximately 14:46 UTC: projected completion of XRPL fixCleanup3_4_0 majority period; verify actual validated-ledger EnableAmendment and following ledger.
3. November 16: Q3 2026 13F deadline; ingest filings only after EDGAR acceptance and preserve filing-time availability.

## Next actions

1. Replay the 13 Evernorth-attributed wallets at the pinned ledger and deduplicate all outflows through October 22.
2. Resolve the 200,138 XRP non-additive attribution residual without assuming a sale or double count.
3. Track Q4 execution disclosures from Ripple, Kraken, Coinbase and BitGo.
4. Reconcile same-date XRP holdings and Class A/Class C share counts before publishing XRP per share or NAV premium/discount.
5. Capture Circle Q3 results and compare with Coinbase USDC distribution economics.
6. Verify fixCleanup3_4_0 activation.
7. Obtain approval before merging any security PR; do not modify main independently.

Forecast remains `NOT_ISSUED`.
