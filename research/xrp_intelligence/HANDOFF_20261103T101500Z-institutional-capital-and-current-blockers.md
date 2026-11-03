# Barrot XRP Intelligence — durable handoff

Captured: 2026-11-03 10:15 UTC

## Mission and execution boundary

- Highest-priority mission: XRP intelligence and measured prediction-engine mastery.
- Barrot V3 remains the execution, security, preservation and verification foundation.
- Main must remain unchanged without explicit approval. No merge, force-push, destructive worktree operation, privileged workflow dispatch, secret access, external deployment, paper-position mutation or real-money action is authorized by this handoff.
- Distinguish DESIGNED, EXECUTED and VERIFIED. No forecast is currently issued.

## Current repository state

- Repository: `Barrot-Agent/B-Agent`
- Current main: `c10df2896572a7df7daebfa4f43899f76c31b100`
- Main's latest commit is a Cross Analysis refresh that changed only `ping-pongings/knowledge-base/sentiment_shift.json`.
- Current main's visible branch protection is not sufficient evidence of required CI enforcement; the ruleset was previously observed enforcement-disabled and the protection endpoint returned 403.
- Main remains unchanged by this run.

### Active review candidates

| PR | Head | Exact-head CI | Fail-closed gate | State |
|---|---|---|---|---|
| #1570 security: corpus and autonomous writers | `2190f15947964e4d5756fb0a92860987982f9830` | 362 tests + 8 subtests passed | Passed | Open, draft, mergeable, unmerged |
| #1571 XRP market and institutional research | `a5a906e23314aa77d2298e445627cc2c8592daa7` | 342 tests + 8 subtests passed | Passed | Open, draft, mergeable, unmerged |
| #1572 prediction integrity | `fbb82b58b76dffedaa05c765cb73fc8cecc3d96b` | 360 tests + 8 subtests passed | Passed | Open, draft, mergeable, unmerged |
| #1573 external actions and autonomous writers | `43324f7c89557ee9fba527f785027932d66a6ffd` | 345 tests + 8 subtests passed | Passed | Open, draft, mergeable, unmerged |

All four branches are two commits behind current main because of generated Cross Analysis refresh commits; their PRs are currently reported mergeable. Automatic merging remains disabled. Do not infer that CI is a required main-branch check.

## XRP research additions

### ETF universe reconciliation

- CryptoETF.today's five-fund universe reports 1,142,172,991 XRP on November 2. Its November 2 flow remains partial: 2/5 funds reported, both at zero; XRPZ, XRPC and GXRP are missing.
- XRP Insights' seven-product universe reports 1,196,600,186 XRP on October 30 and includes XRPR plus BITW.
- Adding XRPR (33,385,276 XRP) and BITW's XRP sleeve (20,950,574 XRP) to CryptoETF's November 2 five-fund total produces 1,196,508,841 XRP, only 91,345 XRP (0.0076%) below XRP Insights' October 30 seven-product total.
- This is a near-reconciliation across different dates, not an exact same-date match. Do not label the residual an error.
- Estimated ETF average cost around $1.71–$1.72 is an aggregator reconstruction, not issuer accounting or individual investor cost basis. It is descriptive, not a forecast feature until tested.

### Institutional 13F cross-check

SEC EDGAR Q2 2026 filings verify:

- Goldman Sachs: $86,506,129 across five XRP ETFs; separate $3,813,470 Armada Acquisition Corp II SPAC position. Armada is a party to Evernorth's proposed business combination. The SPAC holding is indirect transaction exposure, not direct XRP or Evernorth XRP ownership.
- Jane Street: $16,427,269 share-only across five XRP ETFs. Its filing also lists separate calls/puts on some XRP ETF securities.
- Millennium Management: $16,204,485 across four XRP ETFs; no 21Shares XRP ETF CUSIP found.
- Intesa Sanpaolo: $14,424,320 in Grayscale XRP Trust ETF only; the other four checked fund CUSIPs were not found.

The four SEC-verified share positions total $133,562,203, or 74.62% of CryptoETF.today's provider-reported $179M five-fund institutional total. The denominator is aggregator-reported; this is not a market-wide ownership share.

SEC Form 13F excludes short positions and does not net them against longs. Written options are not reported; held options are separate rows referencing the underlying security. Do not infer net delta, hedging or bullish conviction from the share-only sums.

Q3 2026 Form 13F deadline is Monday, November 16, 2026. The 45-day date falls on Saturday November 14 and moves to the next business day. Q2 positions must not be treated as current November holdings.

### Institutional and ecosystem graph

- Goldman → five XRP ETFs: SEC-reported long share positions.
- Goldman → Armada → proposed Evernorth business combination → Ripple/Evernorth: separate SPAC equity exposure, motive unknown.
- Jane Street → five XRP ETFs plus reported call/put rows: strategy/net exposure unknown.
- Millennium → four XRP ETFs: reportable long share positions.
- Intesa Sanpaolo → Grayscale XRP Trust ETF: single disclosed ETF position in the Q2 table.
- Coinbase's XRP execution/liquidity role, Circle's USDC distribution role, Ripple's RLUSD issuance, and SBI's multi-rail strategy remain separate edges. These institutional holdings do not prove coordinated XRP price management.

## Security findings requiring authorization

1. Main still contains public `brain_corpus/dump.json` (353,950 bytes) and `brain_corpus/dump.md` (296,527 bytes), plus an active exporter workflow. Individual corpus records were not inspected.
2. Main still contains an active subscriber synchronization workflow. `web/subscribers.json` metadata shows 26 bytes; its contents were not inspected.
3. Main Daily Digest created public issue [#1538](https://github.com/Barrot-Agent/B-Agent/issues/1538) on November 3 at 00:34:42 UTC. It publishes the unvalidated claim “45.5% correct over 1697 checked signals” while simultaneously reporting confidence 0.0, missing GitHub/GH Models credentials and Groq HTTP 429. PR #1572 proposes to retire the invalid scorer and PR #1573 quarantines the writer. Neither is merged. Do not edit/close the issue without authorization.
4. Main Barrot Autonomous Resolver run [#41615777310](https://github.com/Barrot-Agent/B-Agent/actions/runs/41615777310) created issues #1574–#1579 from six failed PR-branch push runs, not main failures. The query lacks `--created`, `--branch main` and event filters, despite a comment claiming a 24-hour window. All six issues remain open; no assignments occurred because `COPILOT_ASSIGNEE` is unset. Do not auto-close them.
5. Main Auto-Resolve workflow is defined to close issues when a workflow's latest failed run is followed by success, without a per-issue human approval boundary. PR #1573 quarantines it.
6. Main Cross Analysis remains a writer; its latest main commit was observed at 09:51:36 UTC. PR #1570/#1573 contain read-only/containment proposals.

## Prediction engine

- Forecast status: `NOT_ISSUED`.
- Legacy 45.5% accuracy is unvalidated and not reproducible from current main's row-level history.
- Do not use variable-horizon mutable-price scoring.
- Required before any forecast: immutable point-in-time features, fixed horizons, leakage prevention, baseline comparison, walk-forward testing, calibration, uncertainty reporting, drift monitoring and independent outcome attestation.
- Paper trading/shadow evaluation must precede any real-money use.

## Continuing investigations

- Japan's Tokyo SBIC identity is resolved as Tokyo Small and Medium Business Investment & Consultation Co., Ltd., distinct from SBI Holdings. Its ChatGPT seminar is confirmed; no OpenAI partnership or direct XRP integration is established.
- ASK Coin remains ambiguous between Permission Coin ASK and a separate inactive exchange listing; no direct XRP integration established.
- “Actual capital” taxonomy separates cash-funded purchases, in-kind contributions, drawn debt, undrawn facilities, ETF holdings/flows, reserves, customer lending and trading turnover.
- Camilla Stephenson / Wholesome Mils remains a plausible identity match. One direct video is verified; the full public YouTube inventory remains incomplete because channel-page/RSS retrieval was unavailable.
- Nine-platform map: ChatGPT and GitHub verified live. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks are not verified as live Barrot collaborators. SBI's external Claude relationship is not a Barrot connection.

## Upcoming checkpoints

1. November 4, 2026, 08:00 Eastern / 13:00 UTC: Circle Q3 2026 results. Capture actual results; do not pre-fill estimates.
2. November 4, 2026, approximately 14:46 UTC: projected completion of fixCleanup3_4_0's continuous-majority period; verify the validated-ledger EnableAmendment pseudo-transaction and following ledger.
3. November 16, 2026: Q3 2026 Form 13F deadline; ingest accepted filings with filing-time availability, not quarter-end lookahead.

## Next actions

1. Obtain explicit authorization before merging #1570 or #1573; public corpus/subscriber and autonomous-writer risks remain active on main.
2. Review #1572 before any forecast issuance; preserve NOT_ISSUED until a valid evaluation system exists.
3. Complete same-date issuer holdings reconciliation across the five common funds plus XRPR and BITW.
4. Capture the full November 2 ETF flow after all funds report.
5. Reconcile Q3 13F positions after November 16, including the same CUSIPs and any amendments.
6. Capture Circle Q3 results and reconcile USDC/Coinbase distribution economics.
7. Verify XRPL amendment activation from validated ledger data.
8. Continue synchronized contract-level derivatives, Coinbase order-book and cross-venue liquidity ingestion.

No forecast, paper trade or real-money transaction was created in this run.
