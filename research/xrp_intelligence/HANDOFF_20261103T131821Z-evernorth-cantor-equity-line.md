# Barrot XRP / V3 Handoff — 2026-11-03 13:18 UTC

## Repository state
- Repository: Barrot-Agent/B-Agent
- Main SHA verified at run start: `6f0a4c34d21c6aa20c344b4b4107d2f59f7b29a1`.
- Main preservation comparison: `32d3a1ad997384db71f0f37def77deb1c19c7fad...6f0a4c34d21c6aa20c344b4b4107d2f59f7b29a1` contains two add/revert commits and zero net changed paths.
- New work is isolated on `research/xrp-evernorth-cantor-capital-quality-20261103T1318Z`; no main write, merge, deployment or trading action.

## New verified research
Artifact: `research/xrp_intelligence/20261103T131821Z-evernorth-cantor-equity-line-and-etf-flow-quality.json`

- SEC 424B3 filed October 30 describes a conditional Cantor facility for up to 5,218,935 new Evernorth Class A shares.
- Management says it expects a substantial portion of any proceeds to fund additional XRP acquisition, but proceeds are not ring-fenced and may fund working capital/general corporate purposes.
- No Commencement Date, drawdown, cash settlement or incremental XRP acquisition was verified.
- The prospectus contains an internal arithmetic inconsistency: 5,218,935 × $14.71 × 97% = $74.467M, while the $14.71 table row shows $76.8M despite a 97% footnote. The narrative also cites $74.4M net, which does not reconcile to the disclosed Cantor and StoneX fixed fees and expense caps. The artifact preserves the filing's claims and flags the discrepancy; it does not substitute an unsupported corrected estimate.
- The facility may dilute Class A holders and create XRPN resale overhang; this is not XRP token supply or proof of XRP spot demand.
- November 2 ETF observations are partial/provisional and cover different fund universes. Missing funds are not imputed as zero.
- Prior Evernorth closing capital cross-check retained: 600,000 advance-funding subscriber XRP remains unmapped in the prior ten-destination analysis; 200,000 delayed-funding XRP is separate. The October 12 correction changes share counts, not the disclosed XRP quantities.
- Forecast remains `NOT_ISSUED`.

## Source set
- SEC 424B3: https://www.sec.gov/Archives/edgar/data/2092592/000162828026068590/evernorth-424b3.htm
- SEC October 9 8-K: https://www.sec.gov/Archives/edgar/data/2092592/000119312526419146/d24481d8k.htm
- SEC October 12 8-K: https://www.sec.gov/Archives/edgar/data/2092592/000119312526419605/d118629d8k.htm
- CryptoETF partial Nov 2 flow: https://cryptoetf.today/en/xrp-etf-flows
- XRP Insights provisional Nov 2 flow: https://xrp-insights.com/ and https://xrp-insights.com/data

## Verification state
- Research source retrieval: `VERIFIED_FOR_LISTED_DOCUMENTS`.
- Arithmetic checks: `EXECUTED`; internal prospectus discrepancy remains unresolved.
- JSON write/readback and exact-head CI: pending.
- Fail-closed gate: pending.
- PR: draft, no merge authorized or performed.

## Next action
After exact-head CI/gate verification, continue monitoring SEC facility commencement/drawdowns and reconcile issuer-level ETF flow data. Do not count capacity as capital, equity issuance as XRP buying, or partial/provisional ETF flows as final.


## Continuation update — 2026-11-03 13:25 UTC

### Verified pull requests
- Research: [PR #1586](https://github.com/Barrot-Agent/B-Agent/pull/1586), initial content head `f77c3f349780afc90151d5435ca8ec9cb4e02455`.
  - Core CI [41643574732](https://github.com/Barrot-Agent/B-Agent/actions/runs/41643574732) completed successfully.
  - Fail-closed gate [41643574897](https://github.com/Barrot-Agent/B-Agent/actions/runs/41643574897) completed successfully with merge disabled.
- Merge-queue containment: [PR #1587](https://github.com/Barrot-Agent/B-Agent/pull/1587), head `b278f6401bcd3d20ebf8e117b93d467a3843cad2`.
  - Core CI [41643909051](https://github.com/Barrot-Agent/B-Agent/actions/runs/41643909051): 343 tests and 8 subtests passed in 7.76 seconds.
  - Fail-closed gate [41643908807](https://github.com/Barrot-Agent/B-Agent/actions/runs/41643908807) passed.
- Cross-analysis read-only containment: [PR #1588](https://github.com/Barrot-Agent/B-Agent/pull/1588), head `db74f2eaea3481903d000d85a543fd7969897e6d`.
  - Core CI [41644072882](https://github.com/Barrot-Agent/B-Agent/actions/runs/41644072882): 343 tests and 8 subtests passed in 7.94 seconds.
  - Fail-closed gate [41644072696](https://github.com/Barrot-Agent/B-Agent/actions/runs/41644072696) passed.
- All three PRs remain draft/open/unmerged. No merge or deployment occurred.
- PR #1587 disables the workflow that could update branches and merge all open PRs with `mode=all`.
- PR #1588 retains Cross Analysis outputs as 30-day workflow artifacts and removes direct commits/pushes to main.

### Main preservation
- Main remains `6f0a4c34d21c6aa20c344b4b4107d2f59f7b29a1` at the latest search in this run.
- New branches were created from that exact main SHA.
- No main files were written or changed by this continuation.
- No reset, clean, stash, discard, force-push, merge, deployment or trading operation occurred.

### Remaining main risks
- Scheduler Tick still has write-capable permissions and a scheduled queue commit/push path.
- Subscriber Sync, public brain-corpus export, scheduled issue writers and the legacy merge queue still require current-main containment/review. PR #1585 is broad and remains a proposal; its generated corpus deletions are not authorized for merge.
- A controlled-approval zero-job workflow run remains a separate unresolved trigger/reporting issue.

### Next action
Continue from live main, not stale PR bases. Prioritize the scheduler's main-branch write path and remaining external-data/issue writers, while keeping XRP facility capacity distinct from realized cash and confirmed XRP acquisitions.


## Append-only correction — 2026-11-03 13:27 UTC

New correction artifact:
`research/xrp_intelligence/20261103T132735Z-evernorth-facility-19-99pct-denominator-correction.json`

The October 30 SEC 424B3 separately states:
- 5,218,935 facility shares represent 19.99% of Class A shares outstanding immediately before the October 23 agreement.
- 26,094,680 Class A shares were outstanding on October 22 and are used for the prospectus dilution table.

The previously recorded 20.0% is the arithmetic ratio using the October 22 denominator. The issuer's 19.99% refers to the immediately-before-signing denominator, which is not numerically stated in that note. Preserve both as separately dated observations; do not call them contradictory or infer the October 23 denominator. The original research artifact remains unchanged.

## Additional safety PR
- [PR #1589](https://github.com/Barrot-Agent/B-Agent/pull/1589), head `422e0043585ce15325dd0eeab3550342cb276403`, disables the 15-minute Scheduler Tick until it has an explicit read-only workflow allowlist and a durable queue store that does not write to main.
- Its fail-closed gate [41644394934](https://github.com/Barrot-Agent/B-Agent/actions/runs/41644394934) passed with merging disabled.
- Core CI [41644395374](https://github.com/Barrot-Agent/B-Agent/actions/runs/41644395374) was still running at this handoff update; do not claim it passed until its final job result is retrieved.
- PR #1589 is draft/open/unmerged. The scheduler implementation and queue file are preserved; only the workflow executor is proposed disabled.


## Scheduler safety verification update — 2026-11-03 13:28 UTC

PR #1589 final exact-head verification completed:
- Head: `422e0043585ce15325dd0eeab3550342cb276403`.
- Core CI [41644395374](https://github.com/Barrot-Agent/B-Agent/actions/runs/41644395374): 343 tests and 8 subtests passed in 7.85 seconds.
- Fail-closed gate [41644394934](https://github.com/Barrot-Agent/B-Agent/actions/runs/41644394934): passed; merge remained disabled.
- PR #1589 remains draft/open/unmerged.


## Evernorth equity-structure inventory — 2026-11-03 13:30 UTC

New artifact:
`research/xrp_intelligence/20261103T133002Z-evernorth-equity-instrument-inventory-and-sbi-affiliates.json`

Verified from the SEC prospectus and October 9 closing 8-K:
- 26,094,680 issued Class A shares as of October 22.
- 31,392,746 issued Class C shares as of the prospectus date.
- 2,359,038 Class C shares issued to investors affiliated with SBI Holdings at closing because of the 39.9% ownership threshold.
- Class C is an economic, generally non-voting, non-listed and transfer-restricted class with conversion mechanics under the charter.
- 22,953,128 Company Units may be redeemed/exchanged for new Class A one-for-one or cash at Pubco's election.
- Separate potential/reserved Class A categories include 9,283,847 warrants, 3,585,278 initial note-conversion shares, 8,930,929 incentive-plan reserves, 1,786,185 ESPP reserves and 5,218,935 Cantor facility shares.

Do not sum these into a fully diluted share count. Class C is already issued; unit redemptions may be cash-settled; warrants/notes/reserves/ELOC are conditional; possible overlap among instruments is not fully reconciled. These are Evernorth equity interests, not XRP supply or actual XRP buying.

A separate arithmetic correction artifact,
`research/xrp_intelligence/20261103T133112Z-evernorth-sbi-classc-ratio-arithmetic-correction.json`,
corrects the simple SBI-affiliated Class C / issued A+C ratio from 4.1039% to 4.1036% (2,359,038 / 57,487,426). The approximate 4.10% interpretation is unchanged. This is not a beneficial-ownership or voting-power percentage.


## XRP market-data quality snapshot — 2026-11-03 13:32 UTC

New artifact:
`research/xrp_intelligence/20261103T133204Z-xrp-spot-perpetual-oi-provider-reconciliation.json`

Public data retrieval found:
- Kraken XRP/USD ticker: bid 1.28085, ask 1.28086, last 1.27986; no exchange timestamp in payload, so the retrieval time is not treated as the exact quote time.
- Kodexius XRP perpetual OI: $834.52M, updated 06:04 UTC; weighted funding +0.0072%/8h.
- TradRadar: $1.98B OI, updated 07:20 UTC with 15-minute delay; weighted funding +0.0062%/8h; long/short account ratio 2.96 (74.8% long); 24h liquidations at least $2.43M, mostly longs.
- CoinGlass: approximately $2.84B OI on the English page and $2.92B on the Italian page; the same provider's localized pages also differ in futures volume.
- CryptoETF: November 2 remains partial at 3/5 funds, -$0.5M, all attributed to XRPC; XRPZ and GXRP not yet reported.

The 3.5x range between the smallest and largest OI provider observations is quarantined. The providers do not expose a harmonized contract universe, exchange set, update time or calculation method. No averaging or directional inference is permitted. The single Kraken quote is not synchronized with the older aggregator observations. Coinbase and Binance raw API requests were inaccessible through this retrieval path; no substitute values were invented.

Forecast remains `NOT_ISSUED`. Next market task is a fixed-universe, timestamped per-exchange capture of spot L2, perpetual OI/funding/liquidations, and regulated CME futures kept as a separate universe.


## XRP ETF flow settlement correction — 2026-11-03 13:34 UTC

New append-only correction:
`research/xrp_intelligence/20261103T133429Z-xrp-etf-flow-settlement-methodology-correction.json`

Fresh XRP Insights JSON metadata generated at 12:19:10.322 UTC now reports:
- `data_as_of=2026-11-02`, `latest_row_date=2026-11-02`, `provisional_row_date=null`.
- Dashboard says one settled trading day.
- Aggregate holdings-change flow: -32,825 XRP (approximately -$41K), with total reported holdings 1,196,567,361 XRP.
- GXRP flow is excluded across the history because of the issuer-page capture gap from September 2–28; GXRP holdings/AUM remain in totals, but its flow is withheld. Therefore -32,825 XRP is settled for available computed flows, not a complete seven-fund flow.

CryptoETF remains a separate observation published at 05:47 UTC:
- November 2 flow -$0.5M, 3/5 funds reported.
- XRPC -$0.5M; XRPZ and GXRP not yet reported; Bitwise XRP and TOXR zero.
- CryptoETF describes flow as shares created/redeemed at NAV, not trading volume.

XRP Insights computes day-over-day changes in issuer-reported XRP holdings. Its methodology notes that changes can include effects other than creations/redemptions, including BITW index rebalancing and XRP-denominated fee accruals. The two providers therefore differ in universe, completeness, publication time and measurement method. Do not average or treat the figures as equivalent measures of actual spot purchases or new external capital.

The CSV row-level file was not retrievable through the current web reader (unsupported text/csv content type); no per-fund rows were reconstructed. The JSON metadata and methodology page were retrieved directly. Forecast remains `NOT_ISSUED`.


## Cantor facility fee-cap correction — 2026-11-03 13:36 UTC

New append-only correction:
`research/xrp_intelligence/20261103T133621Z-evernorth-cantor-fee-cap-net-proceeds-correction.json`

The SEC prospectus discloses more than the initial $521,893.50 Cantor fee:
- The initial fee is fully earned/non-refundable as of the Purchase Agreement date, regardless of whether purchases occur, and is payable within five business days after the Upfront Determination Date.
- At the Measurement Date, the fee is recalculated to 1% of maximum shares times Purchase VWAP (or, if no shares were purchased, the Upfront Determination Date closing price). The aggregate initial plus additional commitment fee is capped at $1,000,000.
- Cantor/CF&CO documented expense reimbursements are capped at $500,000 aggregate.
- StoneX's qualified-independent-underwriter fee is $200,000 plus up to $1,000 expenses.

The maximum disclosed fee/expense envelope is therefore $1.701M, not merely the initial $521,893.50. At $14.71 and 97% of price, the full-share purchase-price arithmetic is $74.467M before fees; subtracting the maximum disclosed fee/expense envelope gives an illustrative $72.766M. This is a cost-cap scenario, not an actual or expected net-proceeds estimate.

The prospectus's $74.4M stated net estimate remains unreconciled to the 97% price formula and the disclosed fee schedule. No replacement estimate is asserted. Actual payment, facility drawdown and XRP purchases remain unverified.
