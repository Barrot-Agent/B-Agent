# Run 102 — CFTC XRP contract-universe break and point-in-time market-data quality

**Capture cutoff:** 2026-11-09 22:04:28 UTC  
**Main:** `d4d43be3427375cf79d190e768976de062e20287`  
**Integration head before this documentation commit:** `72f4eb4ce9a32cf9e146491f31e7ecf084ad8200`  
**Active integration PR:** [#1640](https://github.com/Barrot-Agent/B-Agent/pull/1640)

## Finding: a large Coinbase XRP futures contract disappeared from the CFTC report

The CFTC's November 3, 2026 Traders in Financial Futures (TFF), futures-only report contains three XRP sections:

| CFTC code | Contract | Open interest | Contract size | XRP-equivalent OI |
|---|---|---:|---:|---:|
| 176740 | CME XRP | 7,216 | 50,000 XRP | 360.800M XRP |
| 176LM1 | Coinbase Nano XRP | 32,505 | 500 XRP | 16.2525M XRP |
| 176LM3 | Coinbase Nano XRP Perp Style | 38,392 | 500 XRP | 19.1960M XRP |
| | **Current reported total** | | | **396.2485M XRP** |

The CFTC index page separately lists **176LM2 — XRP, Coinbase Derivatives** in both its futures-only and futures-and-options-combined “dropped from reporting this week” lists. It is absent from the November 3 TFF position table.

The prior October 27 archive still reports 176LM2:

- Open interest: **28,246 contracts**.
- Contract size: **10,000 XRP**.
- Last reported XRP-equivalent OI: **282.46M XRP**.
- Total traders: **20**.
- The CFTC report prints `.` for Total Change and all 14 position-change cells. Those values are unavailable, not zero.

The CFTC FAQ says a market can disappear when reportable large traders fall below 20, and can reappear when the count reaches 20 again. Because 176LM2 had exactly 20 total traders in the previous report, a threshold effect is plausible. The CFTC does not state the specific reason for this contract's removal, so that explanation remains a hypothesis.

### Why this materially changes the OI interpretation

| Comparison | XRP-equivalent OI |
|---|---:|
| Oct 27, continuing CME + Nano + Nano Perp contracts | 455.1630M |
| Oct 27, all four contracts including 176LM2 | 737.6230M |
| Nov 3, three currently reported contracts | 396.2485M |
| Change in the continuing three-contract subset | **−58.9145M (−12.94%)** |
| Last reported 176LM2 OI, now missing from the report | **282.4600M** |

A naive four-contract-to-three-contract comparison appears to show a 46.28% fall. That is not a valid market-wide OI decline: 282.46M XRP-equivalent is a reporting-universe discontinuity, not evidence that those positions closed. The comparable three-contract subset declined 12.94%.

These are one-sided open-interest contract units converted to XRP equivalents. They are not USD notional, cash deployed, physical XRP holdings, custody balances, or collateral.

### Direct Coinbase connection

Coinbase Derivatives' CFTC XRL listing filing specifies a monthly, cash-settled and margined XRP futures contract of 10,000 XRP per contract, with a 25-contract reportable level. It is cleared by Nodal Clear and settles against the MarketVector Coinbase XRP Benchmark Rate, which tracks XRP spot on Coinbase. The filing also describes a Coinbase Derivatives/Coinbase, Inc. information-sharing agreement for regulatory inquiries.

That is a documented derivatives-to-Coinbase-spot benchmark link. It does not prove Coinbase customer flows, physical XRP delivery, custody, or capital deployment.

## Parser and ingestion gap

The current branch's `barrot_agent/evolution/cftc_tff.py` parser handles the three XRP sections present in the November 3 report. It does not yet:

1. Catalog 176LM2 as an optional historical XRP contract.
2. Record the CFTC added/dropped contract universe.
3. Parse the `Total Traders` field.
4. Accept `.` as a null weekly change for 176LM2's October 27 archive row.

The current ingestion correctly keeps CFTC features raw-only/unverified and not model-eligible. Preserve that gate. The next implementation should add a weekly CFTC contract-status source, nullable change handling, trader counts, optional 176LM2 history, and historical TFF backfill through the CFTC Public Reporting Environment. CFTC states TFF history is available back to June 13, 2006; its public API generally does not require a token, subject to non-abusive use.

The CFTC says TFF categories are based on traders' self-reported predominant business purpose and that it does not know the specific reasons for individual positions. Do not equate a category with hedging/speculation or treat the sum of category net positions as a directional signal. Spreading is included on both sides of open-interest reconciliation.

## Point-in-time market-data rejection

- **OKX:** XRP-USDT last 1.0941, provider timestamp 2026-11-09 22:10:36.962 UTC. This is 6 minutes 8.962 seconds after the 22:04:28 UTC capture cutoff. Reject as a future observation.
- **Kraken:** XRP/USD last 1.09355, but the ticker response has no provider event timestamp. Display-only; not model-admitted.
- **TradRadar:** updated 21:15 UTC with a 15-minute delay; mark price $1.0923, OI $1.66B (−11.45%/24h), funding +0.0026%/8h, at least $38.29M liquidations ($36.82M longs, $1.47M shorts), and 79.9% long accounts across its reported venue set.
- **Liqwall:** updated 20:32 UTC; OI $1.23B (−5.9%/24h), average funding +0.0045%/8h, $37.1M liquidations ($35.7M longs, $1.3M shorts), and 74.8% long Binance accounts.

The two current secondary OI aggregates differ by about 35% and have overlapping but non-identical venue coverage. Do not average them or treat them as independent confirmation. Both show long-heavy liquidations and positive aggregate funding.

The Kingfisher page is excluded: it has no explicit event timestamp and displays XRP at $2.15 alongside $2.89B OI, materially inconsistent with contemporaneous exchange/API observations around $1.09.

The October 2026 U.S. CPI release is scheduled for **November 10 at 08:30 Eastern**. It is a future event at this capture cutoff, not a released observation.

## Repository and merge status

- Main SHA: `d4d43be3427375cf79d190e768976de062e20287`.
- Integration head at capture: `72f4eb4ce9a32cf9e146491f31e7ecf084ad8200`.
- PR #1640: 842 commits ahead, zero behind, 215 changed paths.
- Main tree: 1,404 entries / 1,299 files / 493 Python files / 87 test files / 86 workflows.
- Integration tree: 1,512 entries / 1,399 files / 564 Python files / 143 test files / 87 workflows / 50 XRP research artifacts.

Exact-head checks on `72f4eb4`:

- CI run [42707049394](https://github.com/Barrot-Agent/B-Agent/actions/runs/42707049394): **1,312 passed, zero failed, 8 subtests passed; 59.26% inclusive coverage**. Core suite: 677 passed, 8 subtests. Wheel build and installed mission verification passed.
- Dependency audit [42707049406](https://github.com/Barrot-Agent/B-Agent/actions/runs/42707049406): six manifests passed, no known vulnerabilities.
- Fail-closed gate [42707049263](https://github.com/Barrot-Agent/B-Agent/actions/runs/42707049263): passed; automatic merge remains disabled.
- Main CI [42526890841](https://github.com/Barrot-Agent/B-Agent/actions/runs/42526890841): 718 passed, 8 subtests. Main dependency audit [42579080840](https://github.com/Barrot-Agent/B-Agent/actions/runs/42579080840) passed.
- GitHub Pages build/deploy [42526890275](https://github.com/Barrot-Agent/B-Agent/actions/runs/42526890275) previously succeeded after a main push.

PR #1640 has 62 review submissions, all COMMENTED, zero APPROVED, and 22/22 inline threads resolved. Main reports `protected=true`, but the detailed branch-protection endpoint returns HTTP 403; the visible required status-context list is empty and the fallback ruleset is disabled. PR #1640 changes seven public web assets, and the automatic Pages publication side effect has not been specifically authorized. **Do not merge.** The new documentation/artifact commit created from this capture still requires its own exact-head CI.

## Backlog

- **#1640:** blocked integration PR; sole active V3/XRP integration path.
- **#1643:** unique research archive; 906 ahead / 1 behind, 670 paths, 663 unique and seven shared. Six of seven shared blobs differ from #1640; one is identical. GitHub reports not mergeable. Preserve.
- **#1653:** unique knowledge graph; 18 ahead / 1 behind, seven paths, six unique and one shared CI path that differs. Eight unresolved review threads. Preserve; blocked.
- **#1642:** draft; all seven changed paths overlap #1640.
- **#1644:** eight overlapping paths; two checked blobs differ.
- **#1645:** its one changed file is blob-identical to #1640; exact duplicate candidate, hold until verified on main.
- **#1646 and #1648:** `requirements-dev.txt` differs; reconcile semantically.
- **#1647:** six overlapping paths; one checked file is identical, five remain unchecked.
- **#1649 and #1650:** their respective `requirements.txt` changes are blob-identical to #1640; exact duplicate candidates, hold until verified on main.
- **#1254/#1255:** older legacy dependency changes differ from integration; superseded candidates, not exact duplicates.
- **#1317/#1318/#1320:** structural, scientific-schema, and paper-trader files differ; preserve and reconcile.
- **#1269:** eight unique mesh/topology paths; shared CI file differs; preserve.

Open inventory: 372 PRs, 356 drafts and 16 non-drafts. No PRs were closed.

## Prediction and authorization

**Forecast status: NOT_ISSUED.** The CFTC observations remain raw-only and not model-admitted; spot quotes were rejected for missing/future event timestamps. No directional forecast, paper trade, or real-money action occurred.

No merge, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external-model transfer, funds transfer, force-push, or destructive worktree operation occurred.

**Next concrete action:** extend the CFTC adapter to preserve the dropped-contract universe and nullable 176LM2 historical observations, backfill the TFF series from the CFTC PRE, normalize contract units to XRP equivalents, add regression tests, and keep the source raw-only until validation. Continue #1640's approval, protection, and Pages-authorization blockers in parallel.

