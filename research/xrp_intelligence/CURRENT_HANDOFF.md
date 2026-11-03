# Barrot XRP Intelligence — Current Handoff

**Updated:** 2026-11-03  
**Mission priority:** XRP intelligence and prediction-engine mastery  
**Execution foundation:** Barrot V3  
**Repository:** [Barrot-Agent/B-Agent](https://github.com/Barrot-Agent/B-Agent)  
**Current main:** `00b3213fbffb274581a58c35ab146b1da884a80d`

## Mission state

XRP intelligence is the highest-priority Barrot mission. Barrot V3 remains the execution, security, evidence-gate and verification foundation. Public/authorized sources only. Quiet research does not authorize private access, deception, market manipulation, automatic merges, external deployments or trades.

**Forecast status: NOT_ISSUED.** No directional forecast or paper position is active. Forecast issuance remains blocked until fixed-horizon out-of-sample evaluation and independent attestation are implemented and verified.

## Latest research conclusions

### SBI, Ripple, Circle and the multi-rail strategy

Primary disclosures establish:

- SBI Holdings and SBI Shinsei Bank purchased $50M of Circle equity, $25M each, at Circle's June 2025 listing.
- The same SBI release states SBI held approximately 9% of Ripple equity. This is corporate equity, not an XRP token balance. SBI's native XRP inventory remains unknown.
- SBI's investor presentation depicts a 50/50 SBI-Circle Japan joint venture.
- SBI participated through a consolidated subsidiary in Circle's ARC token presale. SBI's contribution, allocation and vesting are undisclosed.
- Circle launched Arc public mainnet on September 16, 2026. Arc uses USDC for gas; SBI is named in the founding-validator cohort. The rollout is phased and the validator set is permissioned. SBI's actual validator signing activity is not independently verified.
- Circle USDC is native on XRPL. Circle is therefore both a stablecoin issuer on XRP Ledger and the operator of a separate USDC-gas L1.
- SBI VC Trade distributes USDC and RLUSD in Japan.
- SBI VC Trade/APLUS executed a five-day USDC merchant-payment POC in Osaka in May 2026; USDC was converted to JPY before merchant payout. Transaction volume and chain are undisclosed.
- SBI/Visa's Crypto Card lets users select XRP, BTC or ETH as the reward-conversion asset. Net XRP purchases and reward volume are undisclosed.
- SBI and Startale joined Open Standard. The initiative names Coinbase among 140+ participants. SBI/Startale are considering JPYSC–OUSD interoperability; this is not a launched production bridge or a bilateral Coinbase-SBI deal.
- SBI XDC Network APAC and Shinhan Card signed an MOU for a global payment ecosystem. This is not production settlement and no XRP integration is established.

**Best-supported interpretation:** SBI is pursuing a multi-rail digital-finance strategy across Ripple/XRPL, Circle/USDC/Arc, RLUSD, JPYSC/OUSD, XDC and retail XRP rewards. This is an inference from parallel commitments, not a quoted single SBI strategy document. No direct production bridge among these rails or evidence that one is replacing XRP has been established.

### Coinbase and Circle

- Coinbase's Q3 2026 filing describes priorities around the everything exchange, stablecoins/payments and onchain adoption; it reports an all-time high average USDC balance in Coinbase products and renewal of its Circle arrangement on the same terms.
- Circle's Q2 filing says distribution costs payable to Coinbase and Binance depend on USDC balances held on their platforms and on actions/policies the distributors control.
- Circle's September 17, 2026 SEC filing documents a five-year Binance arrangement with monthly USDC-balance-linked incentives and a $100M Binance purchase of Circle shares.
- Coinbase lists RLUSD and supports XRP-related collateral pathways, including cbXRP-backed USDC borrowing through Morpho on Base. Listing, custody, lending interface and collateral eligibility are distinct relationships.
- No evidence establishes that Binance incident-related outflows migrated specifically to Coinbase or that Circle applied preferential freeze treatment to a distributor.

### XRP market and collateral

- Binance's October 29 incident involved approximately 233.46M XRP drained from five Binance-attributed hot wallets. Forensic reporting does not establish an XRPL protocol compromise.
- The November 2 redistribution into six main recipient wallets is tracked separately from the original theft. No sale is established by the observed transfers.
- Native XRP cannot be issuer-frozen; USDC, USDT and RLUSD have issuer-level freeze controls.
- cbXRP/USDC and FXRP/RLUSD Morpho markets show materially different borrower and lender concentration. FXRP/RLUSD is much more concentrated among its largest borrowers and one named vault.
- Firelight's shared FXRP-backed coverage for a Kraken USDC vault is distinct from XRP collateralized borrowing.
- XRP derivatives aggregators have reported open-interest totals differing by approximately 2.39x in unsynchronized snapshots. Do not canonicalize or average these without contract-level reconciliation.
- ETF flow observations are not treated as direct proof of unhedged institutional conviction or spot purchases.

## Durable research artifacts

All artifacts are append-only and preserve source URLs, publication dates, evidence classes, unknowns, disconfirming evidence and forecast status.

- [SBI/Circle/Ripple/Coinbase/Japan rails](20261103T000103Z-sbi-circle-ripple-coinbase-japan-rails.json)
- [SBI/Circle/Arc cross-rail graph](20261103T004500Z-sbi-circle-arc-cross-rail.json)
- [SBI Japan multi-rail payment rails](20261103T005000Z-sbi-japan-multirail-payment-rails.json)
- [ASK Coin entity disambiguation](20261103T005500Z-ask-coin-entity-disambiguation.json)
- [Binance incident and XRP market microstructure — PR #1534](https://github.com/Barrot-Agent/B-Agent/pull/1534)
- [Sentora/Firelight and XRP collateral risk — PR #1533](https://github.com/Barrot-Agent/B-Agent/pull/1533)

## Prediction-engine integrity

Current main's raw `web/signal_history.jsonl` contains 1,716 rows: 1,697 checked, 772 correct and 19 unchecked. Recomputed checked accuracy is 45.492%, matching the stored 45.5% after rounding.

This is **not** a valid fixed-horizon out-of-sample skill estimate. The legacy evaluator compares eligible historical signals with one current price per run after a minimum 24-hour age; individual evaluation horizons vary and per-row check timestamps are not recorded. The daily workflow still has a mutation path on main.

- [PR #1530 — prediction integrity and fail-closed issuance](https://github.com/Barrot-Agent/B-Agent/pull/1530) passed 347 tests + 8 subtests and its dedicated XRP Evidence Gate (8 tests). It remains open/draft/unmerged.
- No forecast, paper-trading position or real-money transaction was created.

## MMI and evidence architecture

- [PR #1540 — consolidated MMI claim-bound corroboration and canonical publisher identities](https://github.com/Barrot-Agent/B-Agent/pull/1540) passed 362 tests + 8 subtests; fail-closed gate passed.
- It requires at least two URI-derived external publisher groups, evidence IDs linked to source IDs, matching caller-supplied claim IDs, observed/parsed evidence, and explicit support/contradiction reconciliation.
- Known SBI corporate domains are grouped; Tokyo SBIC remains separate.
- Residuals: domain identity is not origin lineage; syndicated content across different domains may still share one upstream source. claim_id is currently an opaque caller-supplied identifier, not a cryptographic fingerprint of normalized claim text. Add origin_source_id/lineage_id and a canonical claim fingerprint before production use.
- Application-level MMI adapter instantiation in live ingestion remains unverified. The PR hardens the protocol; it does not prove every production ingestion path uses it.

## Critical Barrot V3 security blockers

1. **Public brain-corpus export remains active on main.** Main still contains `brain_corpus/dump.json` and `brain_corpus/dump.md`; the workflow can query `workspace.barrot.brain` and push raw exports publicly. Individual records remain unclassified because they were not inspected in this run. [PR #1531](https://github.com/Barrot-Agent/B-Agent/pull/1531) passed 345 tests + 8 subtests and its fail-closed gate, but is unmerged.
2. **Autonomous merge/scheduler capability remains active.** Main's merge queue can be manually dispatched with broad `mode=all`, unlimited PR count and `dry_run=false`. The scheduler has write permissions and no robust workflow allowlist on main. Queue state: one completed entry, zero pending; latest tick fired zero entries. [PR #1532](https://github.com/Barrot-Agent/B-Agent/pull/1532) passed 357 tests + 8 subtests and its fail-closed gate, but is unmerged.
3. **External action workflows remain active on main.** The Kaggle scheduled workflow failed before script execution because it invoked the script from the wrong path; no Kaggle API authentication or submission occurred. The same script can submit to up to five active competitions if that path is fixed without an approval guard. Hugging Face force-deploy and Databricks token-rotation/deploy paths also remain active. [PR #1539](https://github.com/Barrot-Agent/B-Agent/pull/1539) removes the schedule, requires explicit opt-in plus exact competition allowlist, guards both duplicate Kaggle scripts, and disables the Hugging Face/Databricks workflows. Exact-head CI passed 353 tests + 8 subtests; fail-closed gate passed. PR remains unmerged.
4. **Branch ruleset enforcement is disabled.** The visible `Fall Back` ruleset has enforcement disabled. The full branch-protection endpoint returned 403, so the complete administrative configuration remains unknown.

## PR and verification ledger

All listed proposals remain open, draft and unmerged. Exact-head CI and fail-closed gates passed on their recorded heads:

| PR | Purpose | Exact-head CI |
|---|---|---:|
| [#1530](https://github.com/Barrot-Agent/B-Agent/pull/1530) | Forecast integrity / issuance gate | 347 + 8 |
| [#1531](https://github.com/Barrot-Agent/B-Agent/pull/1531) | Public brain-corpus export containment | 345 + 8 |
| [#1532](https://github.com/Barrot-Agent/B-Agent/pull/1532) | Merge queue and scheduler containment | 357 + 8 |
| [#1533](https://github.com/Barrot-Agent/B-Agent/pull/1533) | Sentora/Firelight collateral graph | 342 + 8 |
| [#1534](https://github.com/Barrot-Agent/B-Agent/pull/1534) | Binance incident/XRP market research | 342 + 8 |
| [#1535](https://github.com/Barrot-Agent/B-Agent/pull/1535) | SBI/Circle/Coinbase/Japan multi-rail research | 342 + 8 |
| [#1539](https://github.com/Barrot-Agent/B-Agent/pull/1539) | External workflow safety | 353 + 8 |
| [#1540](https://github.com/Barrot-Agent/B-Agent/pull/1540) | MMI claim-bound corroboration | 362 + 8 |

PRs #1536 and #1537 are marked superseded by consolidated fresh-main PR #1540; do not merge them separately.

## Platform coordination

Verified live access: ChatGPT and GitHub. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks are not verified as live collaborators. Workflow definitions or API references do not prove authentication or active collaboration. Use least-privilege adapters, structured evidence exchange, independent assignments and retained minority objections.

## Identity and exact-phrase investigations

- **SBIC:** Tokyo, Nagoya and Osaka Small and Medium Business Investment & Consultation companies are distinct from SBI Holdings, SBI VC Trade and SBI Ripple Asia. Tokyo SBIC's ChatGPT/Copilot training programme is a separate education reference, not an XRP institution.
- **ASK Coin:** ambiguous, not one resolved entity. Candidates now separately tracked: the inactive/untracked askcoin.net exchange listing (no reserve data), Permission Coin's ASK token (Polygon/Base, LayerZero OFT), a Telegram rewards bot with no identified contract, and a low-confidence separate ASK ticker associated with aosika.info. No XRP integration or SBI/Circle/Coinbase relationship is verified. Do not merge these identities.
- **Actual capital:** distinguish equity purchases, token inventories, collateral, stablecoin liabilities, reserves, gross turnover, net purchases and POC flows. Do not convert the 9% Ripple equity stake into an XRP-token balance.
- **Camilla Stephenson:** WholesomeMils remains a plausible but unconfirmed identity candidate. One public video is verified; the full channel inventory is incomplete. No XRP connection established.

## Next actions

1. Obtain approval for the security PRs; do not merge automatically.
2. Contain the public brain-corpus export and assess historical exposure, forks and caches.
3. Disable the broad merge queue and constrain scheduler dispatch; verify branch protection separately.
4. Keep Kaggle submissions, Hugging Face force deploy and Databricks token rotation disabled until specific approval.
5. Add origin lineage IDs and canonical claim fingerprints to MMI; verify actual ingestion call sites.
6. Reconcile XRP derivatives open interest at synchronized contract level and build an immutable feature store.
7. Monitor the Binance recipient wallets and reconcile XRP reserve snapshots at pinned ledger heights.
8. Capture Circle's Q3 2026 results scheduled for November 4, 2026, and reconcile Coinbase/Circle distribution economics.
9. Resolve OUSD issuer/reserves, JPYSC-OUSD POC status, XDC-Shinhan implementation status, SBI ARC allocation and Arc validator activity.
10. Continue SBIC, ASK Coin and Camilla Stephenson public-video identity/inventory work.

## Safety and preservation

Main remains at `00b3213fbffb274581a58c35ab146b1da884a80d`. No main edits, merges, force-pushes, manual workflow dispatches, secret access, external deployments, Kaggle submissions, paper-position mutations or real-money transactions occurred.
