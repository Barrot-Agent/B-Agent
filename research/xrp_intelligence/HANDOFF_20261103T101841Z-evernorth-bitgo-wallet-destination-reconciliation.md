# Barrot XRP Intelligence — Evernorth BitGo destination reconciliation

Captured: 2026-11-03 10:18:41 UTC

## Mission

XRP intelligence and measured prediction-engine mastery remain the highest-priority Barrot mission. Barrot V3 remains the execution, security, preservation and verification foundation.

No directional forecast, paper position or real-money transaction was created. No main-branch modification, PR merge, force-push, privileged workflow dispatch, secret access or deployment was performed.

## High-impact finding: Evernorth's large October XRP transfers are mostly to BitGo-activated multisig wallets

XRP Insights' public ledger snapshot at ledger 108085599 (closed November 3 at 09:14:31 UTC) reports:
- 103,129,904.55 XRP currently in 13 attributed wallets.
- 370,346,663.23 XRP in 19 outbound payments from the attributed set to addresses outside that set.
- The 19 payment amounts sum exactly to the provider's reported gross external outflow.

A Bithomp public account-page cross-check shows that **nine of the destination accounts**, receiving a combined **328,082,844.02 XRP (88.59% of the reported gross outflow)**, were activated by the same BitGo-labelled wallet `rD4G6gtD2KwHqsRf7pcyA8r1neUzXT61ix` and have multisig account control. Six large destination accounts were activated within a 4-minute-20-second window on October 20; three smaller accounts were activated on October 12.

This materially strengthens the custody-reorganization hypothesis. It is not issuer-confirmed legal custody of every destination, but it is much stronger than treating the transfers as unexplained external outflows.

The remaining 42,263,819.21 XRP went to `rPjKkBTutrvvoboPUuaxSaeXNki5XvjDei`. Bithomp's rich list shows a matching approximately 42.26382M balance, but the account page could not be retrieved, so its activation and control remain unknown.

### What this does and does not establish

- Strong inference: most of the reported transfers were to BitGo-activated multisig destinations, consistent with custody/cold-wallet reorganization.
- Not established: legal beneficial ownership or current signer control of every destination; current custody status; whether any destination later transferred to an exchange, AMM, vault, loan broker or execution partner.
- Not established: that the 370.346663M gross movement represents net sale or unique final disposition.
- The source's 103.129905M current attributed balance plus 370.346663M gross outflow exceeds the closing treasury by 200,138 XRP. This remains unresolved; gross flows can include intermediate hops and must be deduplicated.

Primary custody context: Evernorth's SEC prospectus says all XRP was initially held in BitGo custody accounts, 100% cold as of the prospectus, and segregated for Evernorth's benefit. BitGo's approximately $250M insurance pool is shared among eligible clients, about 36.9% of the October 9 XRP value.

## Evernorth capital and Coinbase relationship

The corrected closing treasury is approximately 473,276,430 XRP:
- 84,365,876.3625 XRP cash-funded.
- 261,919,096 XRP private-placement in-kind.
- 126,791,458 XRP Ripple contribution.
- 200,000 XRP delayed-funding contribution.
- Total in-kind: 388,910,554 XRP.

The earlier 473,076,430 derived total omitted the delayed 200,000 XRP tranche; the corrected arithmetic is 473,276,430.

Armada/Evernorth closed October 9; XRPN began Nasdaq trading October 12. Goldman's Q2 13F Armada position is historical pre-close exposure. The filing does not establish whether Goldman redeemed, sold or held the shares through closing. Post-close Goldman ownership is unknown.

Coinbase is a named Evernorth institutional execution partner alongside Ripple, Kraken and BitGo. Evernorth CIO Hugo Jeandesboz previously co-led Coinbase Asset Management and led Coinbase derivatives trading. This is a documented institutional and personnel link, not proof of Coinbase control or a disclosed execution amount.

## XRP market and institutional capital research

- CryptoETF's five-fund universe: 1,142,172,991 XRP on November 2; flow partial at 2/5 funds, both reporting zero, three missing.
- XRP Insights' seven-product universe: 1,196,600,186 XRP on October 30, including XRPR and BITW. Adding those two products to the five-fund total leaves only 91,345 XRP cross-date residual; near-reconciliation, not exact same-date.
- Q2 2026 SEC 13F filings verify Goldman $86.506M, Jane Street $16.427M share-only plus separate options, Millennium $16.204M and Intesa $14.424M in Grayscale only. 13F excludes shorts and does not reveal net exposure. Q3 filing deadline is November 16.
- TradRadar Nov 3 04:05 UTC OI $1.96B vs Kodexius Nov 3 06:04 UTC $834.52M. Aggregate ratio 2.35x; Bybit and Hyperliquid differ about 2.25x and 2.01x. No averaging. Contract/unit reconciliation remains outstanding.
- Forecast remains `NOT_ISSUED`.

## Current repository and security status

- Main: `c10df2896572a7df7daebfa4f43899f76c31b100`.
- Main still contains public brain-corpus dumps and an active exporter.
- Main still contains subscriber synchronization; `web/subscribers.json` metadata is 26 bytes; contents were not inspected.
- Public Daily Digest issue [#1538](https://github.com/Barrot-Agent/B-Agent/issues/1538) created November 3 at 00:34:42 UTC repeats the unvalidated 45.5% / 1,697 accuracy claim while reporting confidence 0.0, missing credentials and Groq HTTP 429.
- Main resolver run [#41615777310](https://github.com/Barrot-Agent/B-Agent/actions/runs/41615777310) created issues #1574–#1579 from failed PR-branch push runs because it lacks a 24-hour cutoff, default-branch filter and event filter. All six issues remain open; no assignment occurred because `COPILOT_ASSIGNEE` is unset.
- PR #1570: public corpus and autonomous writer containment; latest exact-head CI 362 tests + 8 subtests passed; gate passed.
- PR #1571: XRP research archive; latest head after this artifact must be checked for exact-head CI.
- PR #1572: prediction integrity; exact-head CI 360 tests + 8 subtests passed; gate passed.
- PR #1573: external/scheduled writer quarantine; exact-head CI 345 tests + 8 subtests passed; gate passed.
- All remain open, draft, mergeable and unmerged. Automatic merge is disabled. Explicit approval is required before any merge.

## Upcoming checkpoints

1. November 4, 08:00 Eastern / 13:00 UTC: Circle Q3 results.
2. November 4, approximately 14:46 UTC: projected fixCleanup3_4_0 majority completion; verify actual validated-ledger EnableAmendment and following ledger.
3. November 16: Q3 2026 13F deadline; ingest after EDGAR acceptance.

## Next actions

1. Replay all nine BitGo-activated destination accounts and the unresolved rPjK destination at pinned ledgers.
2. Deduplicate intermediate hops and reconcile the 200,138 XRP gross-flow excess.
3. Trace later destination outflows before assigning any exchange, AMM, vault, loan-broker or execution-partner relationship.
4. Track actual Q4 Evernorth execution with Ripple, Kraken, Coinbase and BitGo; use disclosed/attributed amounts only.
5. Reconcile XRPN Class A/Class C, Company Units, ELOC, note conversion, warrants and same-date XRP-per-share.
6. Capture Circle Q3 results and verify XRPL amendment activation.
7. Obtain explicit authorization before merging any security proposal. Main remains unchanged.

No forecast, paper trade or real-money transaction was created.
