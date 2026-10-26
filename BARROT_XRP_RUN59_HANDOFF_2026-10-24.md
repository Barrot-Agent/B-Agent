# Barrot XRP Intelligence — Run 59 Handoff

**Observed at:** 2026-10-24 15:05 UTC (approximate research cutoff)  
**Mission priority:** XRP intelligence and prediction-engine mastery.  
**Execution foundation:** Barrot V3.  
**Forecast state:** NOT_ISSUED.

## Current XRP market snapshot

Source: Kraken public ticker, retrieved at approximately 15:05 UTC:
https://api.kraken.com/0/public/Ticker?pair=XRPUSD

- Last: $1.27191
- Bid/ask: $1.27261 / $1.27262
- 24h VWAP: $1.28609932
- 24h volume: 15.339M XRP
- 24h high/low: $1.31833 / $1.26346
- 24h open: $1.29344
- Last versus open: approximately -1.66%
- Last versus VWAP: approximately -1.10%

Limitations: endpoint does not expose an explicit quote-event timestamp; single venue only; no depth, consolidated volume, or synchronized derivatives snapshot. Descriptive only; no forecast issued.

## ETF flow reconciliation: GXRP

Grayscale's official GXRP page, as of 2026-10-22, reports 65,428,336.9106 XRP in the fund, 3,380,100 shares outstanding, $85.3M non-GAAP AUM, Coinbase Custody Trust Company, LLC as digital-asset custodian, and Anchorage Digital Bank N.A. as additional custodian:
https://etfs.grayscale.com/gxrp

The same official page states the fund began as a private placement on 2024-09-05, uplisted to an ETP on 2025-11-24, and established an ongoing creation/redemption program on that uplisting date. It cautions that pre-listing performance is not directly comparable to post-listing performance. Therefore, cumulative flow trackers must define whether their series begins at fund inception, ETP listing, or another baseline.

Tracker conflict:
- Alpha Finance: $61.5M cumulative GXRP flow; $1.7256B total across displayed funds, data through Oct 23.
  https://alphafinance.io/etf/xrp/
- ByKaranteli: $145.4M cumulative GXRP flow; about $1.80B total, data through Oct 22.
  https://bykaranteli.com/etf/xrp
- XRP Insights methodology disclosure: Grayscale issuer-page reads failed from Sep 2 through Sep 28, 2026; holdings froze, catch-up landed Sep 28, and GXRP flow rows are excluded across its entire history.
  https://xrp-insights.com/data/xrp-etf-flows.json

The displayed GXRP discrepancy is $83.9M and accounts for about 99.1% of the $84.7M total difference calculated from displayed tracker rows. This is a strong data-quality lead, not validation of either tracker. Reconcile daily shares, holdings, creations/redemptions, source timestamps, initial balances and pre-listing methodology before selecting a cumulative net-flow series.

## Confirmed Coinbase / Circle / XRPL links

- Grayscale names Coinbase Custody Trust Company and Anchorage Digital as GXRP custodians. This is an explicit custody relationship, not proof of Coinbase trading intent or XRP price support.
- Coinbase Global Derivatives documentation lists XRP as eligible collateral and lists a 15% X:SM haircut; USDC is also eligible. Product-specific rules must not be generalized to all Coinbase accounts or products.
  https://help.coinbase.com/en-bm/coinbase/derivatives/global-derivatives-cross-collateral
- Circle states native USDC is live on XRPL and Circle Mint/APIs support access and redemption for qualified businesses.
  https://www.circle.com/multi-chain-usdc/xrpl
- Circle's Q2 2026 SEC filing says Coinbase and Binance distribution arrangements are economically significant; Coinbase-related distribution costs were $324.6M in Q2 and $655.3M in H1 2026. These are costs under Circle's commercial agreements, not XRP inflows.
  https://www.sec.gov/Archives/edgar/data/1876042/000187604226000248/crcl-20260630.htm

Causal boundary: XRP collateral eligibility, ETF custody, and native USDC on XRPL are separate mechanisms. None alone proves net XRP buying, price support, or coordinated corporate strategy.

## Repository audit and safe branch work

Repository: https://github.com/Barrot-Agent/B-Agent

Latest main observed before branch creation: `2f607ed31770c0d74e3f10d50c74cacd62b78d9d` (2026-10-24 15:05:13 UTC; “Paper trade cycle [skip ci]”). Main is protected and remains unchanged by this run.

Confirmed main defect:
- `scripts/emit_signal.py` returns score 0 and confidence 0.0 when both providers fail, then blends that score with news sentiment.
- Latest artifact read during this run was timestamped 14:25:50 UTC and reported score 44, confidence 0.0, news score 88, missing GitHub model credentials and Groq HTTP 429. This is contaminated output, not a calibrated forecast.
- `.github/workflows/check-signal-accuracy.yml` still has a daily schedule, `contents:write`, and direct commit/push to main.

PR #1135 is open/draft/unmerged, head `48c81881be5b49b8e75f92d688a886ba8310673e`, with 128 tests passing on that exact head; it has no recorded reviews and its comparison to current main is diverged by 30 main-side commits. The 30 commits between its merge base and main were generated-artifact/telemetry changes, not edits to the source/workflow/test files used for the repair. Still, exact-head CI does not transfer to a fresh head.

To avoid modifying or rewriting existing work, a separate branch was created from the observed main SHA:
`barrot/run59-freshbase-xrp-signal-accuracy-safety-20261024`

The branch reapplies the previously tested source-signal provenance fix, downstream unavailable-state guards, deterministic regression tests, and read-only artifact-only accuracy workflow. A Run 59 handoff is added. PR #1136 was opened as draft. Fresh-head CI run 40105591488 passed **128 tests in 6.15 seconds** on head `447335f14cd9b2dd6f1659f644f641fadb2c7343`; fail-closed gate run 40105591477 succeeded without merging. This handoff update will create a new head and therefore requires a new exact-head CI run before the PR can be called verified. The branch is not merged; no main changes, force-pushes, resets, cleans, stashes, overwrites or discards were performed.

## Platform coordination status

Only ChatGPT through the authorized GitHub connector is live-tested in this run. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks remain designed-only adapters unless a separately verifiable connection test proves otherwise. A Groq API call is not evidence of live Grok collaboration.

## Next actions

1. Verify exact-head CI after this handoff update; preserve any failures rather than rerunning blindly.
2. Keep PR #1136 draft until the final head is green and required review/approval is obtained.
3. Keep the source-signal output marked unavailable when providers fail; do not treat sentiment scores as price probabilities.
4. Reconcile GXRP daily fund shares/holdings and creation-redemption history across Sep 2–28 and the ETP-listing baseline.
5. Continue the SBIC identity thread, ASK Coin, “actual capital,” “SBIC, ChatGPT SBIC,” and Camilla Stephenson public-channel identity verification.
6. Continue shadow evaluation with fixed horizons, timestamped features, baselines, calibration and outcome tracking; no live trading.
