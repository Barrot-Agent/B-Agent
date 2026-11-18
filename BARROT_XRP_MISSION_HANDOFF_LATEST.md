# Barrot XRP Intelligence — Latest Durable Handoff

**Evidence cutoff:** 2026-11-18T20:27:45.971Z  
**Mission priority:** XRP intelligence and measured prediction-engine mastery are the highest-priority Barrot mission.  
**Foundation:** Preserve Barrot V3 for execution, orchestration, safety and verification.  
**Current main SHA:** `8e9b2516b5a103e9593124c05edf623e6c7817ff`  
**Integration branch:** `integration/xrp-v3-mainline-successor-20261115T2101Z`  
**Integration code/test head audited:** `0f981f5c1499cfe3c2f1c1d2d855bb82a7cb865f`  
**Run 25 evidence-record commit:** `a4186aa70fa0b3685c74a9018c3152d7a4be835d`  
**Active integration PR:** [#1663 — Barrot V3 + XRP Intelligence, consolidated mainline successor](https://github.com/Barrot-Agent/B-Agent/pull/1663)  
**Latest addendum:** Run 25 (2026-11-18T20:27:45Z) supersedes older current-state statements below; earlier sections remain historical evidence.  
**Disposition:** NO MERGE. No deployment, secret rotation, Space restart, Kaggle submission, Databricks write, paper trade, funds transfer or real-money action.

## 1. Repository state and integration-first audit

- Repository: [Barrot-Agent/B-Agent](https://github.com/Barrot-Agent/B-Agent)
- Current main at audit: `e204c21100f3d059e2ba633d041fe8927b61ccaf`
- Integration source head audited: `a30de1b4ce04145e01f05322ece803905f9e317c`
- Active integration PR: [#1663 — Barrot V3 + XRP Intelligence, consolidated mainline successor](https://github.com/Barrot-Agent/B-Agent/pull/1663)
- PR base is current main; branch comparison: 295 commits ahead, zero behind; 1,424 changed files; GitHub reports mergeable, but PR remains draft.
- No new branch or PR was created. Main was not modified.
- The previous `BARROT_XRP_MISSION_HANDOFF_LATEST.md` was an empty, zero-byte blob. This file now becomes the current compact handoff. `BARROT_XRP_MISSION_HANDOFF_CURRENT.md` remains the historical log; its last recorded section predates this run.

### Exact test and security evidence

**Integration head `a30de1b`:**

- [Full repository suite, run 44279807829](https://github.com/Barrot-Agent/B-Agent/actions/runs/44279807829): **4,273 passed, 1 skipped, 11 warnings, 19 subtests passed**, 168.71 seconds.
- Inclusive coverage: 68.14%; legacy-core coverage: 77%.
- [Dependency audit, run 44279807824](https://github.com/Barrot-Agent/B-Agent/actions/runs/44279807824): success.
- [Fail-closed gate, run 44279807950](https://github.com/Barrot-Agent/B-Agent/actions/runs/44279807950): success; merge remains disabled.
- [PR money audit, run 44279819079](https://github.com/Barrot-Agent/B-Agent/actions/runs/44279819079): success.
- [PR dependency audit, run 44279819129](https://github.com/Barrot-Agent/B-Agent/actions/runs/44279819129): success.
- [PR fail-closed gate, run 44279819165](https://github.com/Barrot-Agent/B-Agent/actions/runs/44279819165): success.
- The integration full-suite job expands coverage beyond main: it runs `tests`, two runnable legacy test modules and `.barrot/autonomous_tasks/test_math_task.py`; it measures `barrot_agent`, `directive_platform` and `data`, with a 62% inclusive floor and a separate 70% legacy-core floor. The observed 68.14% inclusive and 77% legacy-core results pass those gates.

**Current main:**

- Latest full-suite run on the code ancestor `c54447c320ba2efd783659c7685e969de45e90b0`: [run 44192086690](https://github.com/Barrot-Agent/B-Agent/actions/runs/44192086690), 1,207 passed, 2 skipped, 8 subtests passed, 78.10% coverage.
- Current main `e204c211` is two commits ahead of that tested code and changes only `PAID-ISSUES.md` and `data/money/paid_issues.json` (one line each); no application code changed in that delta.

**Important distinction:** the full-suite result is verified on the exact integration source head `a30de1b`. This handoff-only commit advances the branch; its own post-commit CI must complete before it can be called exact-head verified.

## 2. Integrated architecture — what exists and what does not

**DESIGNED on the integration branch:**

- XRP public-source ingestion, source receipts, SHA-256 capture, timestamp/quality gates and correction overlays.
- Append-only SQLite feature history, point-in-time snapshots, event timeline, scenario/counter-hypothesis registry and forecast ledger.
- SEC EDGAR submissions/companyfacts adapter.
- Naive, momentum, mean-reversion and volatility baselines; chronological walk-forward evaluation, embargoes, calibration diagnostics and PSI drift reporting.
- Forecast admission policy and nine-platform capability/authentication/data-flow map.
- Barrot V3 execution, orchestration, safety gates and verification remain the foundation.

**EXECUTED:**

- Read-only ingestion run [44267762749](https://github.com/Barrot-Agent/B-Agent/actions/runs/44267762749), push-triggered on integration head `226fb9e6911f82de93c2d853cc8a66c20dd8f67e`, at approximately 08:31 UTC.
- The blob SHAs for `xrp_public_ingestion.py`, `sec_edgar.py`, `feature_store.py`, `forecast_ledger.py` and `.github/workflows/xrp-public-ingestion.yml` match the current integration head `a30de1b`; the ingestion code exercised is therefore the same code currently in PR #1663.
- The workflow is **not scheduled in production yet**: its hourly/daily cron is main-only, but the workflow file is absent from main. The latest run was a push-triggered integration capture, not an active hourly main schedule.

**VERIFIED on the latest ingestion run:**

| Measure | Result |
|---|---:|
| Source receipts | 34 |
| Digest-only receipts | 12 |
| Raw-only sources | 23 |
| Source failures | 21 |
| SEC source failures | 6 |
| SEC submissions / companyfacts captured | 0 / 0 |
| Weekly CFTC sources observed / required | 0 / 2 |
| Feature-history records | 2,967 |
| Feature snapshots | 13 |
| Eligible / excluded feature records | 129 / 361 |
| Events / scenarios | 140 / 107 |
| Walk-forward forecasts | 0 |

Additional machine-reported gates:

- `forecast_status=NOT_ISSUED`; `forecast_model_eligible=false`.
- `walk_forward_status=PARTIAL_OR_BLOCKED`.
- `drift_status=INSUFFICIENT_DATA`; no features were eligible for drift evaluation.
- `event_timeline_receipt_complete=false`; event timeline is not model-eligible.
- `external_receipt_anchor_status=NOT_ANCHORED`.
- `feature_store_rebuild_from_raw_artifacts_implemented=false`.
- The feature store restored from the predecessor run's seven-day checkpoint. Raw-source artifacts are retained for 90 days; per-run feature checkpoints for seven days; daily/manual archives for 90 days. GitHub cache is derived and evictable, not an immutable source of truth.
- The SEC adapter requires `BARROT_SEC_USER_AGENT` to contain a Barrot-Agent identifier and monitored contact email. The variable is not configured; the adapter correctly blocks requests. Do not invent a contact address.
- Five receipt-backed independent source clusters, at least five origins per cluster, at least 100 paired out-of-sample origins, at least 100 later shadow origins and the 10,000-resample candidate-readiness evaluation have not been satisfied.

### Data coverage limits

- Spot inputs include Binance XRP/USDT, Bitstamp, Coinbase and Kraken XRP/USD, Bitbank XRP/JPY and OKX XRP/USDT.
- Only same-venue OKX XRP/USDT and USDT/USD top-of-book quotes are normalized to USD, with timestamp-skew/freshness checks. Those receipts share one OKX publisher group; they are not independent corroboration.
- Binance and Coinbase order books remain raw-only without an exchange timestamp/sequence bridge. Kraken depth needs a fresh HTTP Date header. OKX depth lacks sequence continuity. Deribit XRP-USDC perpetual L2 remains raw-only pending unit and sequence validation.
- Historical candles are known only from capture time; they cannot be backdated to historical point-in-time cutoffs. Coinbase backfill beyond the latest endpoint page is manual-only.
- The historical evaluator covers Binance XRP/USDT and Coinbase XRP/USD hourly closes over 1h, 4h, 24h, 7d and 30d horizons. Multi-day targets overlap. Temperature scaling applies only to deterministic baseline probabilities using earlier resolved outcomes; this is not a trained XRP predictive model or independent shadow validation.
- PSI is univariate and provisional; it does not measure concept/label drift.

## 3. Point-in-time XRP market observations

**Spot and resting liquidity**

- Fuelmaps' 09:00 UTC, Nov 18 six-venue snapshot: XRP mid $0.9993. Within ±1%, $12.1M bids versus $7.6M asks (61.5% bid share); within ±5%, $21.5M versus $9.9M (68.5%). Largest listed nearby bids were around $0.996 and $0.950, each about $2.0M; the largest listed ask was around $1.080, about $1.7M.
- Scope is Coinbase, OKX, Kraken, Bitstamp, Bitfinex and Gemini. Binance and Bitget are absent. Resting orders can be cancelled, and the hourly map can be up to about 65 minutes old. This is not a price forecast.
- Kraken's public ticker retrieval during this run showed last $0.99919, bid $0.99886, ask $0.99895, 24-hour volume 41.97M XRP, VWAP $0.97469, high $1.00677 and low $0.94500. The endpoint response does not provide an exchange event timestamp; retain as retrieval-time context, not a point-in-time model feature.

**Derivatives**

- OptimistFi's 07:16 UTC snapshot: XRP perpetual $0.9939, +3.27% over 24 hours; $1.8B open interest across 39 venues, with CME the largest venue at about 20%; $1.1B 24-hour volume; open-interest-weighted funding +1.9% annualized.
- Hyperliquid taker flow in that snapshot was +$13.4M net over 24 hours (52% buy share), but −$182M net over seven days (49% buy share). Short-window buying and the longer-window selling measure different horizons.
- The 39-venue OI universe includes CME and is not directly interchangeable with narrower crypto-perpetual aggregates. Do not average provider totals or funding measures.

**Exchange-wallet balances**

- XRP Insights' 08:00 UTC ledger read: 22.19B XRP across 707 XRPL wallets attributed by XRPSCAN labels to 24 exchanges; same-wallet balance change −151.9M XRP over seven days and −390.1M over 30 days.
- This is a broad attributed-wallet total, not tradable float: it includes cold storage, omnibus custody and 483.1M XRP in identified wrapped-token/insurance reserves (including Binance-Peg XRP and Coinbase cbXRP backing). The source reports 48.5% cold-labeled balances and 39.7% without a hot/cold label. New wallet labels and untracked venues materially affect naive totals. South Korean venues account for 8.56B XRP in the tracked set.
- XRP Insights says balances are read from rippled `account_info` and attributed using XRPSCAN labels; same-wallet changes are used to reduce coverage-change distortion.

**Spot ETF flow disagreement — keep universes separate**

- Alpha Finance, through the Nov 17 session, covers five funds (Bitwise XRP, Franklin XRPZ, Canary XRPC, Grayscale GXRP and 21Shares TOXR): −$6.1M on Nov 17, −$15.9M over the last seven sessions and −$10.9M over 30 sessions. It excludes XRPR and reports flow series rather than fund AUM/holdings.
- XRP Insights covers six spot funds plus BITW, includes XRPR, excludes GXRP from flow totals while correcting a data gap, and reports +986 XRP for Nov 17. It reports 1.19B XRP held across the six spot funds plus BITW; that holding total is not the same measure as cumulative cash inflow.
- CryptoKeyhole reads four of six spot funds; its Nov 17 observation was partial (two of four reported) at 09:55 UTC, −3,251 XRP. Its latest complete day was Nov 13 (−9,967 XRP); the five complete sessions Nov 9–13 summed to −4.923M XRP.
- These are different fund sets, reporting vintages and flow methods. Preserve each receipt and missing-fund state; do not average or label a partial day as a complete complex-wide flow.

## 4. Actual capital and the Evernorth/SBI/Ripple relationship

Primary SEC evidence materially improves the capital reconciliation:

- Evernorth's Form 10-Q (filed Nov 13) says the business combination closed **October 9, 2026** and XRPN began trading **October 12**. Do not rely on secondary pages that still describe closing as unconfirmed.
- The advance-funding subscribers contributed $214.05M cash and 600,000 XRP; the cash was used to purchase 84,365,876 XRP, at a disclosed average of about $2.5366 per XRP. Delayed-funding subscribers committed $10.5M cash and 200,000 XRP at closing.
- Ripple contributed 126,791,458 XRP to Pathfinder. RippleWorks contributed 211,319,096 XRP to Arrington XRP Capital Fund, the sponsor, which then invested that XRP in Evernorth. A Ripple-affiliated contributor entity associated with the Larsen family contributed 50M XRP. The SEC filing reconciles these tranches to approximately 473.276M XRP at closing.
- Gross cash at closing was $272.6M before transaction expenses: $224.6M private-placement cash plus $48M remaining SPAC trust cash after redemptions. This is not the same as net cash available after expenses, nor is all of it proven to have been spent on XRP.
- On Oct 13 Evernorth received $29.0M net from a $30M 4% PIK convertible note. Proceeds are for general corporate purposes, including possible XRP acquisition; no filing reviewed here proves a specific XRP purchase with those proceeds.
- From Oct 12 through Nov 9, 3,073,366 warrants were exercised for $35.3M gross proceeds; 8,666,279 remained outstanding. These are actual proceeds, but no asset-specific XRP deployment is established.
- The Oct 23 Cantor ELOC allows purchases of up to 5,218,935 shares at 97% of the applicable VWAP, subject to conditions and ownership limits. It is optional financing capacity, not cash raised; no drawdown is established here. A $0.5M non-refundable commitment fee was disclosed.
- The S-4/A identifies four SBI Holdings-controlled advance-funding entities: SBI Venture Fund 2023A Investment LPS, SBI Venture Fund 2023B Investment LPS, SBI PE Holdings Co., Ltd. and SBI Holdings USA, Inc. SBI-specific amendments cap the subscriber group's Class A ownership at 39.9%; excess subscribed shares are Class C, non-voting but convertible under the charter. The SEC filing does not itemize each SBI entity's exact dollar contribution. Do not attribute the entire $214.05M advance-funding total to SBI.
- Ripple and its contributor-related party were subject to a combined 9.9% ownership cap; the Arrington sponsor's voting ownership was capped at 19.9%. Economic Class C shares and voting Class A shares must not be conflated.
- Evernorth subsequently transferred 346,484,972 XRP to Pathfinder. This is an intra-group transfer, not new external XRP demand; do not double-count it as an acquisition or ETF-like flow.

Primary filings:
- [Evernorth Q3 Form 10-Q, filed Nov 13](https://www.sec.gov/Archives/edgar/data/2092592/000162828026073871/xrpn-20260930.htm)
- [Evernorth S-4/A, Aug 12 — SBI Entity Amendments](https://www.sec.gov/Archives/edgar/data/2092032/000119312526347519/d944435ds4a.htm)
- [Evernorth Oct 23 Form 8-K — Cantor ELOC](https://www.sec.gov/Archives/edgar/data/2092592/000162828026066495/xrpn-20261023.htm)

The prior verified SBI–Circle equity/JV and SBI VC Trade USDC/RLUSD distribution relationships remain separate from the Evernorth investment. Coinbase custody/distribution roles, Circle stablecoin issuance and Ripple's XRP contributions do not by themselves prove XRP spot purchases.

## 5. Requested identity and exact-phrase research

- **SBIC:** Japan's SBIC East/Central/West are the three regional Small and Medium Business Investment & Consultation companies, not SBI Holdings. The Tokyo SBIC's 2025 ChatGPT/Copilot training course remains the most plausible explanation for the SBIC/ChatGPT phrase; it does not establish an OpenAI, Ripple or XRP partnership.
- **ASK Coin:** no new exact-phrase evidence connects the Permission ASK token candidate to XRP or XRPL.
- **“actual capital”:** no separate token or entity established by the phrase search. The SEC filings above are the controlling evidence for cash received, XRP contributed, XRP purchased, debt proceeds, warrant proceeds and optional ELOC capacity.
- **“SBIC, ChatGPT SBIC”:** no new independent exact-phrase match; retain the Tokyo SBIC course as a hypothesis, not a confirmed partnership.
- **Kamilah/Camilla Stevenson:** the verified Kamilah identity candidate remains `@drkamilahstevenson`; the Paul Barron Podcast appearance is a verified third-party appearance. No additional owned-channel upload was verified in this run. Same-name videos on unrelated channels remain excluded. Do not conflate Kamilah with Camilla without first-party identity evidence.

## 6. Nine-platform coordination

The integration map records only the ChatGPT-to-GitHub path as tested. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks authentication/data flows remain unverified. No external model dispatch, Kaggle submission or Databricks write occurred. Do not claim a live connection for any untested provider.

## 7. Open PR inventory and classifications

All ten open PRs are drafts. No source PR was closed.

| PR | Classification | Current disposition |
|---|---|---|
| #1663 | blocked — consolidated integration | Mainline successor; draft; governance/security review incomplete |
| #1664 | unique/unreviewed | Paid-issue PR template pack; unrelated to XRP; not published |
| #1541 | blocked — partial overlap | Five paths overlap #1663; two blobs identical, three divergent; preserve until reconciled |
| #1460 | unique/unreviewed | Institutional multirail, Binance and Kamilah research; no path overlap with #1663 |
| #1450 | unique/unreviewed | Binance phase-one status, escrow and PR #1449 audit; no path overlap |
| #1440 | unique/unreviewed | XRP archive-validation trigger repair; no path overlap |
| #1437 | unique/unreviewed | XRP source addenda/snapshot pointer repair; no path overlap |
| #1436 | unique/unreviewed | Binance XRP incident and attacker-wallet graph; no path overlap |
| #1353 | unique/unreviewed | Lossless XRP ledger shard migration; 1,084 files; no path overlap |
| #1265 | unique/unreviewed | XRP ledger index pointer migration; one differing CI workflow overlap |

Backlog counts: **ready 0; blocked 2; unique/unreviewed 8; duplicate 0; superseded 0.** PR #1664 shares two files with #1663 but is a separate paid-issue workstream. #1265's CI overlap and #1541's divergent blobs must be reconciled explicitly. Do not close or bulk-close any of these PRs before a successor is merged and its content verified on main.

## 8. Workflow/security and merge gate

- The main branch reports protected, but the detailed branch-protection endpoint returns HTTP 403. The only repository ruleset returned is a disabled fallback ruleset.
- `.github/CODEOWNERS` assigns ownership only to `@Barrot-Agent`; PR #1663 has zero independent formal reviews and remains draft.
- The 67 changed workflow files were diff-scanned. Several previously automatic external workflows are now manual, exact-main-SHA gated or hard-disabled: A2A Cloudflare deploy/secret update; self-hosted Hugging Face deployment; Databricks/Kaggle operations; paper-trader simulation. None was run.
- `coinbase-paper-trader.yml` is now manual, exact-main-SHA and explicit-YES gated, artifact-only; no simulation was run.
- `barrot-ops.yml` requires separate explicit confirmations and an exact main SHA before Databricks import or Kaggle dataset download; it was not run.
- `sync-self-hosted-brain.yml` is hard-disabled. Cloudflare deployment/secret rotation is manual and requires explicit approval. No secret was rotated and no Space was restarted.
- `paid-issue-publish.yml` still has `contents: write` and automatically commits its two paid-issue evidence files after a successful hunter run on main. The integration version adds a main-head guard, SHA-pinned actions and a `mutations_performed == 0` check. This automatic repository-write side effect must remain visible in merge review.
- Full transitive-script/security review of all 67 workflow changes is not complete.

**NO MERGE.** The PR is draft, independent reviews are absent, detailed protection settings are inaccessible, the fallback ruleset is disabled, and workflow/script review remains incomplete. Never bypass branch protection or required checks.

## 9. Forecast and execution policy

No directional XRP forecast was issued. No forecast is model-eligible, no independent shadow cohort exists, and no paper trade was executed. The objective remains measured out-of-sample predictive performance, not a directional narrative or a growing PR queue.

## 10. Next concrete actions

1. Obtain an approved monitored project contact and configure `BARROT_SEC_USER_AGENT`; do not invent an email.
2. Capture and validate SEC submissions/companyfacts and accession-bound primary filings after the contact gate is satisfied.
3. Implement deterministic feature-store reconstruction from raw receipts; add an external immutable timestamp/hash anchor and test recovery without GitHub cache.
4. Restore the two weekly CFTC source observations and improve independent publisher clusters, exchange timestamp/sequence continuity and full-depth coverage.
5. Make event-timeline receipt completeness true before event features can be model-eligible.
6. Complete the 67-workflow/transitive-script security review, obtain independent code ownership/review and verify actual branch-protection settings.
7. Keep PR #1663 as the single integration workstream. Do not create another successor unless current-main ancestry or conflicting diffs make this branch stale.
8. Keep forecast issuance disabled until the out-of-sample, calibration, source-cluster and later-shadow admission policy is met.

**Run result:** research and repository inspection executed; integration source head and its full suite verified; durable handoff repaired; main unchanged; no merge and no external action.


## Historical Run174 preservation record — 2026-11-15 21:01:47 UTC

This immutable historical reference is retained because the Run174 recovery audit is part of the mainline-preservation evidence. It is not the current repository head and must not be substituted for the current main SHA.

- Audit artifact: [Run174 mainline successor recovery audit](research/xrp_intelligence/20261115T210147Z-run174-mainline-successor-recovery-audit.json).
- Historical `run_id`: **Run174**.
- Historical `current_main_sha`: `5b2a9c46eb878250dfec99190e294909cd5835bf`.
- Historical successor branch: `integration/xrp-v3-mainline-successor-20261115T2101Z`.
- Historical forecast status: `NOT_ISSUED`.
- Historical accuracy status: `NOT_EVALUATED`.
- The audit records that the earlier source branch remained unchanged, no history rewrite or force-push occurred, and the successor was created from the then-current mainline. Those statements describe Run174 only; the current main SHA for this handoff is recorded in the current-run section above.

## Run 11 exact-head CI correction — 2026-11-18 10:22 UTC

- Main at this audit: `e204c21100f3d059e2ba633d041fe8927b61ccaf`.
- Integration head tested: `cf7f5e29cfa41875c3fbec96baed664be5d58d2f`.
- [Push CI run 44283939979](https://github.com/Barrot-Agent/B-Agent/actions/runs/44283939979) completed with core tests and Pages validation passing, but the full repository suite failed one preservation-regression assertion: `tests/test_run174_mainline_successor_preservation.py::test_run174_mainline_successor_preserves_mainline_and_xrp_mission`.
- Result: **4,272 passed, 1 failed, 1 skipped, 11 warnings, 19 subtests passed**. The failure was caused by this canonical handoff omitting the historical Run174 identifier and main SHA even though the structured Run174 audit artifact remained present and correct. No application-code failure was reported in that run.
- This handoff update restores the missing historical provenance without changing the test or rewriting history. The resulting new head must receive its own full-suite run; the failed run is retained as evidence and is not relabeled successful.
- Exact-head dependency audits passed on push and PR; the fail-closed gates passed on push and PR; the money audit passed. PR #1663 remains draft, with zero formal reviews and zero review threads.
- Detailed main branch-protection access still returns HTTP 403; the only visible fallback ruleset is disabled. The integration PR remains 281 commits ahead and zero behind at the tested head; re-fetch comparison after this handoff commit before further work.
- **Disposition: NO MERGE.** Main was not modified. No source PR was closed. No deployment, secret rotation, Space restart, external model dispatch, Kaggle submission, Databricks write, paper trade, funds transfer or real-money action occurred.

Next action: verify the new handoff commit's exact-head full repository suite and security gates, then continue with the SEC contact blocker and raw-receipt/feature-store reconstruction work.



## Run 11 remediation and current XRP evidence — 2026-11-18 10:27:48 UTC

### Exact-head repository verification

- Main SHA: e204c21100f3d059e2ba633d041fe8927b61ccaf.
- Verified parent integration head: af2177ea64bf5a6fb6e7952e1c9e97ec834d8b53; PR #1663 was 282 commits ahead, zero behind, with 1,418 changed files. The artifact and handoff update in this commit require a new exact-head CI run; the parent-head results below must not be attributed to the new commit until that run completes.
- The earlier Run 11 full-suite failure in [44283939979](https://github.com/Barrot-Agent/B-Agent/actions/runs/44283939979) was one preservation-regression assertion: the canonical handoff omitted the historical Run174 marker and SHA although the structured audit artifact remained present. The handoff was corrected without changing the test or rewriting history.
- Corrected parent-head [full-suite run 44284952830](https://github.com/Barrot-Agent/B-Agent/actions/runs/44284952830): **4,273 passed, 1 skipped, 0 failed, 11 warnings, 19 subtests passed** in 116.49 seconds; inclusive coverage 68.14%, legacy-core coverage 77%; wheel build and installed-wheel verification passed; Pages validation passed.
- Exact-parent PR checks: [CI 44284962127](https://github.com/Barrot-Agent/B-Agent/actions/runs/44284962127), [dependency audit 44284962272](https://github.com/Barrot-Agent/B-Agent/actions/runs/44284962272), [money audit 44284962393](https://github.com/Barrot-Agent/B-Agent/actions/runs/44284962393), and [fail-closed gate 44284962299](https://github.com/Barrot-Agent/B-Agent/actions/runs/44284962299) passed. Push dependency audit [44284952990](https://github.com/Barrot-Agent/B-Agent/actions/runs/44284952990) and fail-closed gate [44284952867](https://github.com/Barrot-Agent/B-Agent/actions/runs/44284952867) passed. GitHub Actions cache budget is exhausted and cache storage is read-only; test execution succeeded.

### Current market structure — research only

Structured artifact: [20261118T102748Z market, ETF, Binance incident and macro audit](research/xrp_intelligence/20261118T102748Z-market-structure-etf-binance-macro-audit.json).

- Kraken XRP/USD ticker retrieval: last $0.99919; bid $0.99886 (330 XRP); ask $0.99895 (3,538 XRP); spread about 0.90 bps; 24-hour volume 41.97M XRP; VWAP $0.97469; high/low $1.00677/$0.94500. Kraken's payload has no exchange event timestamp, so it is retrieval-time context only.
- CoinGlass live aggregate: approximately $0.9998, +4.20% over 24 hours; spot volume $553.84M (+17.77%); futures volume $2.47B (+12.22%); open interest $2.06B (+3.82% in USD but −0.36% in XRP units); OI-weighted funding −0.0029% per eight hours (−3.22% annualized); $5.86M liquidations, 64% shorts; futures volume about 4.5 times spot; Fear & Greed 10 (Extreme Fear). The 7-day, 30-day, 90-day and YTD returns remain −5.12%, −23.32%, −21.25% and −45.71%. This is an aggregator snapshot, not a synchronized exchange-level dataset.
- Fuelmaps' 06:00 UTC six-venue spot book showed bid share of 59.0% within ±1% and 64.2% within ±5%; its mid was $0.9835. Basis' 07:42 UTC Binance XRPUSDT perpetual book was nearly balanced within ±1% ($12.7M bids / $12.9M offers). Different venues, products and timestamps; do not combine these into one depth measure.

### ETF-flow disagreement — unresolved

- CoinGlass showed approximately −$6.1M for Nov 17; Pluang's TokenPost-syndicated report showed −$6.14M.
- CryptoKeyhole's issuer-file reader at 07:55 UTC had only 2 of 4 tracked funds published for Nov 17: −3,251 XRP (about −$3K), with Bitwise and Franklin missing.
- XRP Insights had not yet posted Nov 17; its last complete day was Nov 16 (+158,148 XRP across its stated universe).
- For Nov 9–13, KuCoin citing SoSoValue reported −$19.13M, while CryptoKeyhole showed −4.923M XRP and XRP Insights −6.08M XRP. These fund universes and methods differ. No daily or weekly aggregate is admitted as a model feature until issuer holdings/share-count reconciliation is complete.

### Binance exchange-flow correction and macro context

- Binance's first-party incident report says five hot wallets sent **233.46M XRP** to an attacker-controlled address between 20:05 and 20:09 UTC on Oct 29. Classify this as a security-incident hot-wallet outflow, not customer withdrawals, market selling or ordinary exchange flow.
- Binance reported $6.34B in total impacted digital assets and about $2.85B frozen/intercepted. Its Oct 31 recovery update described 90% replenished and XRP among tokens then 100% backed; its Nov 3 initial report said 98% of impacted token assets were replenished as of Oct 31. Reuters on Nov 18 reported approximately 95% of lost tokens covered and about $3B frozen. Preserve these as attributed snapshots with potentially different scopes; frozen/intercepted is not recovered, and 1:1 customer backing does not prove the original XRP was recovered or quantify XRP-specific replacement purchases.
- Reuters on Nov 18 reported the dollar index near 103.67 and a 19-month high, 95.7% market-implied odds of a 25-bp December Fed hike, USD/JPY around 159.25, and further tightening signals from BOJ Governor Kazuo Ueda. This is timestamped macro context, not a causal XRP explanation.

### Interpretation and forecast gate

A short-covering/position-reset explanation is plausible because price rebounded while funding remained negative, shorts made up most reported liquidations, and XRP-denominated OI declined despite USD OI rising. Fresh spot accumulation remains possible because spot volume rose and an earlier six-venue book showed bid skew, but futures turnover remained about 4.5 times spot, ETF reporting conflicts, and current synchronized multi-venue L2 was not captured. A broader relief move inside a larger drawdown is also plausible given negative multi-week returns, extreme fear and a strong dollar. These are competing hypotheses, not directional forecasts.

**Forecast status: NOT_ISSUED.** The rendered observations have no retained raw HTTP bytes, immutable SHA-256 receipts or trusted timestamp anchor and are not model-eligible. No paper trade or real-money action occurred.

### Integration, backlog and blockers rechecked

- PR #1663 remains the single consolidated integration PR, draft, 282 commits ahead at the verified parent head, 1,418 files; no new PR was created.
- Current overlap comparison: #1541 shares five paths (two identical blobs, three divergent); #1265 shares one divergent .github/workflows/ci.yml; #1664 shares two divergent paths (BARROT_SYNC.md, MEMORY.md) but is a separate paid-issue workstream. Preserve all three; no source PR closed.
- Ten open PRs remain drafts: #1663 blocked; #1541 blocked/partial overlap; #1664 unique/unreviewed; #1460, #1450, #1440, #1437, #1436, #1353 and #1265 unique/unreviewed with the noted overlap. The #1265→#1353→#1436→#1450→#1460 ledger/research chain and #1440/#1437 stacked repairs remain intact.
- Six dependency manifests were audited; push and PR dependency checks passed. Twelve high-risk workflow files were spot-checked. Several deployment/Space/Kaggle/Databricks/paper-trader workflows are manual and explicitly gated or quarantined, but paid-issue-publish.yml retains contents: write on a main-branch workflow-run path. Full transitive review of all 67 changed workflows and called scripts remains incomplete.
- Main branch-protection details still return HTTP 403; the visible fallback ruleset is disabled; CODEOWNERS remains self-only; independent formal reviews remain zero. No merge.
- SEC EDGAR remains blocked by missing approved BARROT_SEC_USER_AGENT; do not invent a contact. The ingestion workflow is present only on the integration branch, so its main-only schedule is not active in production. Latest actual ingestion remains the earlier 08:31 UTC run; no new live ingestion was triggered here.
- Only ChatGPT-to-GitHub has verified authentication/data flow among the nine platforms. Other eight remain unverified.

**Disposition: NO MERGE.** The corrected parent head passed its full suite; the new research/handoff commit still requires its own exact-head CI. Main remains unchanged; no deployment, secret rotation, Space restart, Kaggle submission, Databricks write, paper trade, funds transfer, real-money action, force-push or history rewrite occurred.



## Run 11B — Binance XRP downstream tracing and Evernorth actual-capital reconciliation — 2026-11-18 10:37:34 UTC

Structured evidence: research/xrp_intelligence/20261118T103734Z-binance-xrp-tracing-and-evernorth-capital-audit.json.

### Binance XRP flow: a material downstream update

- XRPL-Utilities' case file, published Nov 13 and timestamped as of Nov 12 23:30 UTC, estimates that up to **216.4M XRP (about 93% of the 233.462M XRP initial theft)** reached deposit accounts at roughly ten exchanges and swap services through six pre-existing hub wallets and 58 payout wallets.
- Its venue breakdown attributes 75.43M XRP to OKX (explicitly an analyst attribution, not a public label), 65.36M to Binance, 31.50M to Coinbase, 23.49M to Kraken, 13.92M to Bybit, 2.79M to Bitget, 1.54M to ChangeNOW and 2.37M to others/unlabelled.
- **216.4M is an upper bound, not a confirmed stolen-XRP deposit total.** XRPL-Utilities says only about 85% of hub inflows from Nov 5 could be traced to the original breach wallet; the hubs also carried unrelated funds. It does not know what happened after the deposits because exchange internal books are private.
- Santala Research's Nov 17 on-chain update independently confirms the initial six-way split and the collection wallet's approximately 1,300 payments to about 100 accounts by Nov 12, but says those payments had no destination tags and that its sample of the five largest recipients did not reveal where XRP left that wallet network. Its stated sampling scope may stop before XRPL-Utilities' later hub/payout-wallet layer. The two analyses are therefore different tracing scopes, not a resolved contradiction.
- XRPSONAR independently shows the collection wallet's Nov 12 transfer of 2.408405M XRP to another account and a reported residual balance of 5 XRP on Nov 17. This corroborates the collection wallet's near-empty state but not the downstream exchange labels.
- XRPL-Utilities describes a daily SHA3-512/Merkle fingerprint written to the XRP Ledger. The method was inspected, but this run did not independently recompute the Nov 12 fingerprint. Exchange deposit does not prove a sale; do not turn this upper bound into confirmed net selling or price impact.

### Evernorth: distinguish actual cash from XRP contributed in kind and accounting impairments

Primary SEC records now resolve the main capital categories. The Nov 13 10-Q and Nov 17 8-K/A (accepted Nov 16 at 19:54:22 UTC) show:

- 346,284,972 XRP held at Sept 30 at historical cost of $846.575M; impairment charges of $233.651M in 2025 and $271.037M in 2026 YTD reduced carrying value to $341.887M. The combined ~$504.688M is **non-cash accounting impairment**, not $505M cash spent, XRP sold or realized loss.
- The 8-K/A says Evernorth remained a Ripple related party after the Oct 9 transaction and its XRP did not qualify for ASU 2023-08 fair-value accounting; it remains at historical cost less accumulated impairment under ASC 350-30.
- At closing, 346,484,972 XRP was transferred to Pathfinder and Ripple separately contributed 126,791,458 XRP in kind. Together they account for approximately 473.276M XRP at Nasdaq debut. The Ripple contribution is not cash and is not a spot-market purchase. The 50M XRP investor-affiliate lot is already in the 346.285M cost-basis table; do not add it twice.
- Actual financing disclosed: $48.0M trust-account cash released after 18.464M public-share redemptions; $29M net proceeds from a $30M convertible note after a $1M fee; and $35.3M gross cash proceeds from 3.073M warrant exercises through Nov 9.
- The Cantor ELOC allows up to 5,218,935 shares at 97% of VWAP, but the filing does not disclose an actual drawdown. It is optional capacity, not capital already raised.
- The pro forma combined balance sheet as if the merger had occurred on Sept 30 shows $76.027M cash, $342.223M net digital assets, $418.593M total assets and $46.276M liabilities. This is an unaudited pro forma presentation, not a current actual balance sheet. The pre-merger standalone 10-Q cash of $91,397 is also not the current post-merger cash balance.
- Ripple, Kraken, Coinbase and BitGo are named as institutional execution partners, but no post-listing XRP purchase amount or order-level execution was disclosed. Evernorth says it may pursue XRP yield strategies; direct XRPL lending is deferred until native credit features are active and proven in production.

### Implications for the XRP model

The Binance flow is a candidate potential-supply event with a bounded upper estimate and uncertain exchange attribution, not confirmed selling. Evernorth's reported 473.276M XRP is a treasury holding, but it combines previously held XRP and an in-kind Ripple contribution; only the separately disclosed financing proceeds are cash capital, and no corresponding XRP spot purchases are verified. The model must keep these categories separate.

Forecast status remains **NOT_ISSUED**. This research is not model-eligible until raw ledger transaction receipts, source hashes, external timestamp anchoring and exact exchange-label validation are captured. No paper trade or real-money action occurred.

### Exact-head and integration status

- Parent head b910eb94ce606e1c12a7f1aa135d832c5ca06128 passed [full repository CI 44286284457](https://github.com/Barrot-Agent/B-Agent/actions/runs/44286284457): 4,273 passed, 1 skipped, 0 failed; 68.14% inclusive coverage; 77% legacy-core coverage; wheel build and installed Barrot V3/XRP mission verification passed.
- This supplemental research artifact and handoff update create a new commit and require their own exact-head full-suite and security verification.
- Main remains e204c21100f3d059e2ba633d041fe8927b61ccaf; no merge. PR #1663 remains the sole consolidated integration PR and draft. No source PRs were closed.


## Run 12 — 2026-11-18 10:49 UTC: market-liquidity and XRPL-lending governance reconciliation

### Repository state and exact-head verification

- Main SHA: `e204c21100f3d059e2ba633d041fe8927b61ccaf`; main remained unchanged throughout this run.
- Consolidated integration PR: [#1663](https://github.com/Barrot-Agent/B-Agent/pull/1663), branch `integration/xrp-v3-mainline-successor-20261115T2101Z`, still draft.
- Integration head at audit start: `11bdb4847b6bf775e24c726f7a27b6c5712fd221`, 284 commits ahead and zero behind main. The Run 12 research artifact was then committed as `bf0a67c9e9a84e01aaaed8d3ff87139df9a8e6a4`; this handoff update is a subsequent documentation commit and requires its own exact-head CI.
- Main tree: 1,737 entries, 1,565 files, 172 directories and 92 workflow files. Integration tree: 2,971 entries, 2,786 files, 185 directories, 93 workflow files and 513 test files.
- PR #1663 changes 1,420 files: 67 workflow files, 410 test files and 809 research/XRP-data files. The change set remains unusually broad and requires complete transitive workflow/script review.

The exact audit-start integration head passed [push CI run 44287410095](https://github.com/Barrot-Agent/B-Agent/actions/runs/44287410095): 4,273 passed, 1 skipped, zero failed, 11 warnings and 19 subtests passed in 107.17 seconds; inclusive coverage 68.14%, legacy-core coverage 77%; wheel build and installed Barrot V3/XRP mission verification passed. GitHub Pages validation passed. The draft pull_request run's core/full-suite jobs were skipped by the integration-branch condition; the push run executed the full suite on the exact audit-start head.

Dependency audit passed on push and PR events. All six audited manifests (core, development, integrations, Hugging Face Space, legacy and PEP 621 project dependencies) reported no known vulnerabilities. Money audit and fail-closed checks passed. These results apply to the audit-start head; the Run 12 artifact and this handoff update need their own exact-head verification.

### Open PR inventory and overlap reconciliation

All ten open PRs were drafts at inspection. No review submissions or review threads were present on #1663.

- **#1663 — consolidated Barrot V3 + XRP Intelligence:** 1,420 changed files; primary integration workstream; blocked by draft status, governance and security review.
- **#1664 — paid-issue product pack:** 71 files; two overlapping paths with #1663 (`BARROT_SYNC.md`, `MEMORY.md`); both blob contents differ. Keep separate and reconcile before any merge.
- **#1541 — MMI claim fingerprint security:** five changed paths, all overlap #1663; `barrot_agent/mmi_adapter.py` and `tests/test_mmi_integration.py` are identical; `barrot_agent/mmi_v1.py`, the research JSON and `tests/test_mmi_v1.py` diverge. Preserve the source branch until the integrated successor is verified and the divergent changes are explicitly reconciled.
- **#1460:** eight unique institutional-multirail/Kamilah research files; no overlap with #1663.
- **#1450:** 116 unique Binance/escrow research and ledger-validation paths; no overlap with #1663.
- **#1440:** 64 unique stacked ledger-validation/trigger repair paths; no overlap with #1663.
- **#1437:** five unique XRP escrow/source-revision paths; no overlap with #1663.
- **#1436:** 24 unique Binance theft, freeze and attacker-wallet research paths; no overlap with #1663.
- **#1353:** 1,084 unique lossless XRP-ledger sharding/archive paths; no overlap with #1663.
- **#1265:** 144 changed paths; one divergent overlap with #1663 at `.github/workflows/ci.yml`; preserve pending deliberate workflow reconciliation.

The older ledger PRs form a stacked research/repair chain and are not duplicates merely because they share ancestry. No PR was closed, merged or bulk-classified as superseded.

### Fresh market evidence — observations, not a directional forecast

The structured artifact is [Run 12 market/lending/governance reconciliation](research/xrp_intelligence/20261118T104916Z-xrp-market-lending-governance-reconciliation.json).

- Kraken's public XRP/USD ticker, retrieved at approximately 10:49 UTC, returned last $0.99406, bid $0.99406 (170 XRP), ask $0.99407 (5,030 XRP), approximately 0.10 basis-point top spread, 42.55M XRP 24-hour volume, $0.97524 VWAP and a $0.945–$1.00677 24-hour range. The response has no exchange event timestamp; top-of-book size is not full-depth liquidity.
- CoinGlass displayed $0.9936, +3.69% over 24 hours, $561.77M spot volume (+20.84%), $2.49B futures volume, $2.05B headline open interest, -0.0045% per-eight-hour funding, $5.98M liquidations (63% shorts), and a $6.1M Nov 17 ETF outflow. Its headline OI change (+3.50%) conflicts with its own summary panel (-0.18%); OI direction is quarantined until underlying data are reconciled.
- Liqwall's 10:32 UTC snapshot separately reported approximately $993M OI (-0.4%), -0.0065% average funding per eight hours, $5.6M liquidations ($2.0M longs/$3.6M shorts) and 74.2% of Binance accounts with XRP positions long. Its OI universe is not reconciled with CoinGlass; do not average the two totals.
- CryptoQuant's Nov 18 quicktakes reported a Binance 30-day XRP liquidity index of 0.041 (three-month low), $2.71B 30-day turnover, and a seven-day spot-to-futures volume ratio falling from 27.2% early in November to 17.9% (34.2% lower); it described futures volume as about 5.6 times spot. This is a source-reported indicator, not an order-book depth measure; the raw series and full index construction were not captured.
- Nov 17 ETF-flow reports remain non-comparable: CoinGlass showed about -$6.1M; a CryptoBriefing syndicated report attributed -$6.14M to Grayscale GXRP and Canary XRPC in a five-fund universe; CryptoKeyhole showed only -3,251 XRP (about -$3K) from two of its four daily-reader funds, while Bitwise and Franklin files were still missing. These are different fund universes and completeness states, not a single reconciled total.

The short-covering/position-reset explanation is plausible because the rebound occurred alongside negative funding and a majority of reported liquidations on the short side. A spot-led recovery remains possible because spot volume increased. It is not confirmed: futures turnover dominates Binance activity, the liquidity index is weak, the broader 7-day/30-day/YTD returns remain negative, ETF flow coverage is incomplete, and no synchronized raw multi-venue trade/L2 set was captured. These are competing hypotheses, not a forecast.

### Critical distinction: XRPL native lending versus XRP-backed payment credit

Primary Ripple and XRPL documentation clarifies a distinction that must be represented explicitly in Barrot's relationship and feature model:

1. Ripple's Nov 16 Swell recap says Soil and Ripple are **exploring** potential XRP collateral and credit use within Ripple Payments. This is exploratory; no production deployment, utilization, collateral balance or XRP purchase amount was disclosed.
2. The native XRPL Lending Protocol is documented as fixed-term **uncollateralized** loans funded from Single Asset Vaults. Underwriting and risk management are off-chain; the current implementation has no automated on-chain collateral or liquidation management. Optional first-loss capital is a loss buffer, not collateralization and not a guarantee against loss.
3. Single Asset Vaults can hold XRP, trust-line tokens or MPTs. XRP can therefore be deposited as lendable pool inventory. That does not mean borrowers post XRP as collateral in the native Lending Protocol.
4. The two ideas must be separate data entities: `ripple_payments_xrp_credit_collateral_exploration` versus `xrpl_lending_vault_asset_and_uncollateralized_credit`.

The third-party XRPL Dashboard's Nov 18 signed amendment leaf reported LendingProtocol 23/35, LendingProtocolV1_1 23/35 and SingleAssetVault 24/35, with 29 needed. Its latest own-node rollcall showed 24, 24 and 25 yes votes respectively, still short by five, five and four. The page marked its signature verified, but this run did not independently download and recompute the raw leaf/signature. These amendments were not active on the record reviewed.

### Prediction-engine and ingestion disposition

- **DESIGNED:** The integration branch contains the XRP public-ingestion workflow, SEC EDGAR adapter, point-in-time feature store and forecast/outcome ledger. The feature-store module explicitly warns that local SQLite hashes/triggers are not adversarially tamper-proof and require an external signed/checkpointed receipt or independently controlled immutable log for production.
- **EXECUTED:** Exact-head full-suite and dependency/security checks passed on the audit-start head. The new Run 12 research artifact records source URLs, retrieval/event-time distinctions, provider disagreements, hypotheses and disconfirming evidence.
- **NOT VERIFIED:** The rendered web observations in Run 12 are not raw HTTP byte captures; no new immutable SHA-256 source receipts or external timestamp anchor were created. They are excluded from model training. No new ingestion workflow run occurred because this commit changed research/handoff paths, not the ingestion workflow or adapter paths.
- The hourly/daily scheduled XRP ingestion workflow exists only on the integration branch. GitHub scheduled workflows run from the default branch, so the scheduled production cadence is not active until the workflow is on main. Its integration push capture is limited to changes in the workflow or specified ingestion/SEC adapter files.
- SEC live ingestion remains blocked by the missing approved `BARROT_SEC_USER_AGENT` monitored-contact variable. Do not invent or silently configure a contact.
- No directional forecast, paper trade or real-money action occurred. Forecast issuance remains **NOT_ISSUED**.

### Governance and merge disposition

- Detailed main branch-protection access returned HTTP 403 (integration cannot inspect the protected-branch configuration).
- The repository fallback ruleset is disabled.
- `.github/CODEOWNERS` assigns `* @Barrot-Agent`, which is not independent review.
- #1663 has zero submitted reviews and zero review threads.
- Sixty-seven changed workflows and their transitive scripts still require full security/side-effect review. The integration branch's paid-issue publisher still has a workflow-run path that can write to main; that side effect must be explicitly accounted for before merge.
- **NO MERGE.** #1663 remains draft and governance/security requirements are not satisfied. Main remains unchanged. No deployment, secret rotation, Space restart, external model dispatch, Kaggle submission, Databricks write, funds transfer or paper trade occurred.

### Next concrete actions

1. Verify exact-head full-suite, dependency audit and fail-closed checks on the Run 12 artifact/handoff commits.
2. Capture raw bytes and SHA-256 receipts for Kraken, CoinGlass, Liqwall, CryptoQuant and ETF issuer files; preserve provider event time separately from retrieval time.
3. Reconcile CoinGlass OI's internal contradiction and the Nov 17 ETF fund-universe differences.
4. Independently retrieve and verify the XRPL signed amendment leaf; ingest governance votes as events, not price signals.
5. Keep native XRPL uncollateralized lending and Ripple's exploratory XRP-backed payment-credit work as separate features.
6. Resolve the approved SEC contact variable, then verify accession-bound EDGAR captures.
7. Complete the 67-workflow/transitive-script security review, obtain independent review and actual branch-protection evidence.
8. Keep #1663 as the single integration workstream; do not create a successor, merge, or close unique source PRs until all admission requirements pass.


---

## 8. Run 14 — current integration, ingestion and evidence status (2026-11-18 12:18 UTC)

### Repository and branch state

- Main remains e204c21100f3d059e2ba633d041fe8927b61ccaf. No main commit was created.
- At the audit snapshot, the single consolidated integration PR #1663 was at dd64eb2e6f78ad436fd1b4c5bfdca7fecb8735f1, 295 commits ahead, zero behind, with 1,424 changed files. GitHub reports mergeable, but it remains draft.
- No new branch or PR was created. No source PR was closed. The two new research artifacts and the refreshed platform map were committed to the existing #1663 branch.
- #1663 has zero submitted reviews and zero review threads. The branch-protection endpoint still returns HTTP 403; the fallback ruleset is disabled; CODEOWNERS remains self-only.
- The current head's full repository test suite and dependency audit were still running at the cutoff: CI run 44302420735 (full suite in progress), dependency audit 44302420657 (in progress), fail-closed gate 44302420711 (success). Do not treat the earlier successful suite as a pass on this newer head. The handoff update itself advances the branch and triggers another exact-head CI run.

### Implemented integration improvements

- The read-only XRP public-ingestion workflow now permits workflow_dispatch on integration branches as well as the existing integration push smoke path. The production cron remains inactive until the workflow is merged to the default branch. The successful captures in this run were push-triggered; no manual dispatch or backfill was executed.
- The ingestion summary's stale blanket claim that Coinbase order-book snapshots are raw-only was corrected. Coinbase, Kraken, Bitstamp, OKX and Bitbank L2 snapshots are represented as venue-local point-in-time features when their timestamp/quality gates pass. They are not continuous book reconstructions; sequence continuity limitations remain explicit. A regression assertion was added.
- The updated ingestion code and tests are on the existing #1663 branch. No new workstream or PR was opened.

### Latest verified public-data ingestion

**Run 44301868145** completed successfully on code head 38b910e7f91e22096a224474be4445ef7f9a7a0d. [Workflow run](https://github.com/Barrot-Agent/B-Agent/actions/runs/44301868145).

- Data cutoff: 2026-11-18T12:13:54.617611Z.
- Receipt chain: 34 receipts, 22 raw payloads retained, 12 digest-only, sequence 15, chain verification PASS, continuous from run 44300915250.
- Receipt-log SHA-256: d5da01be1b25939875cd2cbd409efe9922957400c8e33b63103fefe232e40fa7.
- Chain-log SHA-256: dc22eef6ec2dda12004b7c2bc4096415b4c8885dab1391e30511ca4b8815251d.
- Chain-head SHA-256: 5d3d4cae7846c0835c2319776c24e864ed9b0245e03012bd363edaae3544c597.
- Cross-run chain SHA-256: 879adcc5b6cf7f1cc1c3f6e8ff93d38e382a2f686b11a8868fbdb5f8f415331a.
- Raw artifact: 462,640 bytes; SHA-256 c9ec648228d5c76136fd68f8d7b0f2b71ea2eb97eebf8b2f8617b9678098b2be; 90-day retention.
- Feature-store artifact: 822,789 bytes; SHA-256 d13e0c1257e9318fa8160bae711b2cfaf79996f2a3aea886a8600048af7caf5d; 7-day retention.
- No independent WORM store or trusted external timestamp anchor exists. The chain is tamper-evident relative to its head, not proof that the entire chain was never rewritten. Automatic rebuild of the cumulative feature store from raw receipts remains unimplemented.
- Feature-store snapshot 4cd71512938161dd548f4327f52fb76e4e0472459a05b06ec58afa1ecd6d09be: 3,235 historical records across 15 snapshots; 124 eligible current records, 361 excluded; 11 source snapshots across five exchange groups (Coinbase, Kraken, Bitstamp, OKX, Bitbank); 140 events and 107 scenarios.
- There were 23 raw-only sources and 21 source failures. Drift status remains INSUFFICIENT_DATA with zero evaluated features. Walk-forward forecast count remains zero. Forecast status remains NOT_ISSUED.
- The correction audit contains two overlays, modified no original source artifacts and issued no forecast.
- Cache storage remains read-only because the configured GitHub Actions cache budget is exhausted. This cache-save warning did not fail the ingestion job.

### Spot and order-book observations

All prices below are point-in-time venue observations around 12:13:44–12:13:47 UTC, not a consolidated market price.

| Venue | Pair | Last | Best bid / ask | 24h base volume |
|---|---|---:|---:|---:|
| Coinbase | XRP-USD | 0.98420 | 0.98410 / 0.98420 | 94.82M XRP |
| Kraken | XRP-USD | 0.98441 | 0.98396 / 0.98397 | 46.52M XRP |
| Bitstamp | XRP-USD | 0.98465 | 0.98419 / 0.98420 | 12.78M XRP |
| OKX | XRP-USDT | 0.98530 USDT | 0.98500 / 0.98510 USDT | 35.27M XRP |
| Bitbank | XRP-JPY | 157.000 JPY | 157.017 / 157.018 JPY | 6.43M XRP |

- OKX's synchronized XRP-USDT and USDT-USD top-of-book snapshots produced a USD-normalized mid of approximately 0.983920 and a 1.107 bp spread. This is top-of-book only, shares one OKX publisher group, and does not normalize depth.
- Deribit XRP-USDC perpetual last was 0.98451, reported open interest 6,648,056 units, volume about $15.09M and zero displayed eight-hour funding. It remains raw-only because contract amount, OI and book-sequence semantics are not validated.
- Venue-local depth is mixed. At 10 bp, Coinbase, Kraken and Bitstamp showed more ask than bid notional, while OKX and Bitbank showed more bid than ask. At 50–100 bp the balance changed by venue. Kraken's 100-level cap made its 50 bp and 100 bp totals identical. OKX depth is USDT-denominated; Bitbank is JPY-denominated and was not converted. Do not aggregate these books or infer a directional forecast from one snapshot.
- Coinbase REST L2 is a verified point-in-time snapshot with its sequence retained, but there is no WebSocket sequence bridge. It is not a continuous reconstructed book.

### Data-access and source-quality blockers

- Eight Binance endpoints returned HTTP 451. Five Bybit endpoints returned HTTP 403; provider documentation notes US/Mainland China restrictions and the runner region is not verified. No proxy or restriction bypass was attempted.
- Grayscale's XRP ETF issuer page returned HTTP 429. Franklin XRPZ's issuer-page identity/holdings markers were missing and its parser failed closed.
- The ETF CSV no longer produced the previous run's data_as_of/latest-row parser failure, but it remains digest-only/raw-only: the full row-level dataset is not retained and primary AP cash creation/redemption reconciliation is pending.
- Six SEC EDGAR requests (submissions and companyfacts for Evernorth, Coinbase and Circle) remain blocked because BARROT_SEC_USER_AGENT lacks a monitored project contact. No contact was invented.
- Ripple RLUSD, Circle USDC, SBI VC Trade lending, Morpho CBXRP and Coinbase CBXRP proof-of-reserves observations remain raw-only or digest-only until their supply, reserve, unit, timestamp, offer-term or cache semantics are normalized.
- The three CFTC weekly source IDs remain skipped by the current source policy; this is a regulatory/derivatives coverage gap.

### ETF, exchange-balance and supply reconciliation

- CryptoKeyhole's Nov 17 observation was -3,251 XRP with only two of four daily-tracked funds available. XRP Insights reported +986 XRP for six spot funds plus BITW, excluding GXRP flow due to a capture gap. Alpha Finance reported approximately -$6.1M across five funds, including an XRPC decline of about $5M.
- These are different fund universes and data vintages. Alpha's Nov 17 XRPC decline resembles CryptoKeyhole's Nov 16 decline; a one-session date shift is plausible but unproven. Do not average these figures or admit them as a complete ETF flow feature. Holdings changes are not direct AP cash creations/redemptions.
- XRP Insights' Nov 18 wallet dashboard reports about 22.19B XRP across 707 attributed wallets at 24 exchanges. This is a coverage floor, not total exchange inventory, tradable float or exchange flow.
- The same dashboard reports about 31.10B XRP in on-ledger escrow and a Dec 1 unlock of up to 1B XRP. An unlock is not net circulating supply; historical re-escrow must be measured.
- The dashboard reports $4.33B of XRPL tokenized RWA notional, but only $276M distributed versus $4.06B represented/registry value. RWA notional is not XRP purchase demand or freely transferable investor float. These dashboard observations remain hash-only/raw-only in Barrot.

### Macro and institutional context

- Reuters on Nov 18 reported a dollar index near 103.8, a 25 bp December Fed hike fully priced with a small chance of 50 bp, USD/JPY around 159.3 and further BOJ tightening signals. Rapid yen weakness toward 160 raises intervention and cross-market liquidity risk. Reuters also noted the dollar rally could be near exhaustion absent a more aggressive 2027 rate repricing. This is context, not an XRP causal forecast.
- Coinbase's RLUSD distribution across Prime, Exchange and retail, with XRPL/Base/Ethereum support, is a stablecoin access relationship; Coinbase Global Exchange collateral was described as future at launch, not live. It is not evidence of XRP spot purchases.
- BNY's XRP/RLUSD custody support and primary RLUSD reserve-custody role are custody infrastructure, not proof of XRP buying.
- SBI VC Trade's RLUSD listing is a subsidiary-level distribution relationship under SBI Holdings. It remains distinct from the three regional SBIC entities and does not prove XRP collateral utilization or spot purchases.
- The prior verified SBI–Circle equity/JV and SBI VC Trade USDC relationships remain separate from Ripple RLUSD distribution. Circle dashboard observations are captured but not yet normalized into model-eligible supply features.

### Exact-phrase and identity research

- Japan's SBIC East/Central/West are the three regional Small and Medium Business Investment & Consultation companies, not SBI Holdings. The Tokyo SBIC 2025 ChatGPT/Copilot training course remains a plausible explanation for the phrase; it does not establish an OpenAI, Ripple or XRP partnership.
- Exact ASK Coin search continues to surface Permission Coin (ASK) as a possible ticker collision. No XRP/XRPL relationship is established.
- No new exact-phrase result establishes a separate token or entity called actual capital. Prior primary Evernorth SEC filings remain controlling for cash received, XRP contributed, XRP actually purchased, debt proceeds, warrant proceeds and optional ELOC capacity.
- No new independent match for "SBIC, ChatGPT SBIC" was found.
- The prior verified Kamilah candidate remains @drkamilahstevenson, with a third-party Paul Barron Podcast appearance. No additional owned-channel video was verified in this run. Do not conflate Kamilah with Camilla without first-party identity evidence.

### Nine-platform map

The updated Run 14 map is stored at research/xrp_intelligence/20261118T121830Z-nine-platform-capability-authentication-map-run14.json. Only the ChatGPT-to-GitHub connector path is tested in this run. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks authentication and data flows remain unverified. No independent external model dispatch or evidence exchange occurred. Groq is not Grok. Exact GitHub token scopes remain uninspected; least privilege is not verified.

### Open PR inventory and classifications

All ten open PRs remain drafts. No source PR was closed.

| PR | Classification | Current disposition |
|---|---|---|
| #1663 | blocked — consolidated integration | 295 commits ahead, zero behind; 1,424 changed files; draft; no reviews |
| #1664 | unique/unreviewed | Paid-issue PR template pack; 71 files; two divergent overlaps with #1663 (BARROT_SYNC.md and MEMORY.md) |
| #1541 | blocked — partial overlap | Five paths overlap #1663; two identical blobs and three divergent |
| #1460 | unique/unreviewed | Eight unique institutional multirail, Binance and Kamilah research files |
| #1450 | unique/unreviewed | 116 research/ledger paths; substantial overlap with #1440; three divergent shared blobs require reconciliation |
| #1440 | unique/unreviewed | 64 repair paths; 63 shared with #1450; do not close or merge without reconciliation |
| #1437 | unique/unreviewed | Five source/addenda paths; overlaps older ledger migration work |
| #1436 | unique/unreviewed | 24 Binance incident and wallet-graph research paths |
| #1353 | unique/unreviewed | 1,084 ledger archive/migration paths; preserve |
| #1265 | unique/unreviewed | 144 ledger-index paths; divergent CI workflow overlap with #1663 and shared ledger work with #1353 |

No fragmented integration PR was created. #1663 remains the only consolidated V3/XRP integration workstream. Older research and repair PRs remain open until a verified successor is merged and exact duplicate paths are identified.

### Merge disposition and next actions

**NO MERGE.** Main remains unchanged. The PR is draft, no independent review exists, branch-protection configuration cannot be inspected (HTTP 403), fallback ruleset is disabled, CODEOWNERS is self-only, the 67-workflow/transitive-script security review is incomplete, and the paid-issue publisher has a workflow-run path that can write to main. Current-head full-suite and dependency checks must complete before any readiness claim.

Next concrete actions:
1. Verify full repository test suite and dependency audit on the exact post-handoff head; do not rely on earlier-head results.
2. Resolve the monitored SEC contact configuration, then capture accession-bound EDGAR submissions/companyfacts for Evernorth, Coinbase and Circle.
3. Keep Binance/Bybit feeds excluded until lawful regional access is verified; do not proxy or bypass restrictions.
4. Obtain row-level issuer ETF holdings/AP records or keep the flow feature raw-only; reconcile the fund/date-vintage disagreement.
5. Add independent external timestamp anchoring and a durable immutable raw store; implement feature-store rebuild from retained raw receipts.
6. Complete the 67-workflow/transitive-script security review and resolve the paid-issue publisher's automatic main-write side effect.
7. Establish independent review, actual branch-protection evidence and least-privilege permissions.
8. Continue leakage-safe chronological baseline evaluation; keep forecast issuance disabled until all sample, calibration, drift and shadow gates pass.


---

## Run 15 — 2026-11-18 — mainline synchronization, full-suite result and workflow side effects

### DESIGNED / EXECUTED / VERIFIED

**EXECUTED — integration branch synchronized with current main without rewriting history.**

- Current main at synchronization: 13c60af7079700a38b4226b9110d9c9377af7695.
- Prior integration head: 1d0ade36779b3759df8577c8d55d25d9895f9c62.
- New branch merge commit: 469068e25b4ce004b6298a2a7a14223f7ca5d8db.
- Parents: prior integration head first, current main second.
- The main commit contained only PAID-ISSUES.md and data/money/paid_issues.json. Neither path was changed by PR #1663, so there was no path overlap.
- Both files were read back from the updated branch and their Git blob SHAs exactly match main.
- Compare result after synchronization: 297 commits ahead, zero behind; merge base is current main.
- This was a branch-only merge commit. It did not merge PR #1663 into main, did not force-push, and did not rewrite existing commits.

**VERIFIED — full repository suite on code/test head 1d0ade36779b3759df8577c8d55d25d9895f9c62.**

- Run [44302845889](https://github.com/Barrot-Agent/B-Agent/actions/runs/44302845889), exact triggering SHA 1d0ade.
- 4,274 tests collected; 4,273 passed, 1 skipped, 0 failed; 19 subtests passed; 11 warnings.
- Inclusive package coverage: 68.14%, above the 62% required floor.
- Legacy core-package coverage: 77%.
- Wheel build and installed-wheel verification passed; the packaged Barrot V3 and XRP primary mission loaded.
- Core test job and GitHub Pages validation also passed.
- Non-failing warnings: setuptools license-table deprecation; package-discovery warnings for barrot_agent.data.missions and data.research; GitHub Actions cache budget exhausted, leaving cache storage read-only.

**VERIFIED — checks on synchronized branch head 469068e25b4ce004b6298a2a7a14223f7ca5d8db.**

- [Dependency Audit 44312132545](https://github.com/Barrot-Agent/B-Agent/actions/runs/44312132545): passed.
- [Money audit 44312132602](https://github.com/Barrot-Agent/B-Agent/actions/runs/44312132602): passed.
- [Fail-closed gate, PR event 44312132488](https://github.com/Barrot-Agent/B-Agent/actions/runs/44312132488): passed.
- [Fail-closed gate, push event 44312122397](https://github.com/Barrot-Agent/B-Agent/actions/runs/44312122397): passed.
- [CI 44312132625](https://github.com/Barrot-Agent/B-Agent/actions/runs/44312132625): Pages validation passed. The core and full-suite jobs were skipped because the PR event intentionally excludes integration-branch test jobs.
- The push CI workflow ignores PAID-ISSUES.md and data/money/paid_issues.json, so no full-suite push run was created for the branch-only mainline synchronization commit. Do not claim the full suite was run on 469068. The latest full-suite evidence remains the exact code/test head 1d0ade; the synchronized changes were data-only and non-overlapping.
- This handoff update is a documentation-only change and requires its own push-triggered CI evidence before any merge-readiness claim.

### Current main and automatic workflow side effects

Main advanced from e204c21100f3d059e2ba633d041fe8927b61ccaf to 13c60af7079700a38b4226b9110d9c9377af7695 through the existing Paid issue publish workflow, not through a PR merge.

- Hunter run [44304037203](https://github.com/Barrot-Agent/B-Agent/actions/runs/44304037203): successful.
- Publisher run [44304112701](https://github.com/Barrot-Agent/B-Agent/actions/runs/44304112701): successful; committed PAID-ISSUES.md and data/money/paid_issues.json directly to main.
- Pages validation/deployment run [44304220732](https://github.com/Barrot-Agent/B-Agent/actions/runs/44304220732): successful.
- Cross Analysis run [44307953150](https://github.com/Barrot-Agent/B-Agent/actions/runs/44307953150): successful.
- Pillars Consistency Check [44309596554](https://github.com/Barrot-Agent/B-Agent/actions/runs/44309596554): failed. The job reported missing GITHUB_APP_ID, GITHUB_APP_PRIVATE_KEY and GITHUB_INSTALLATION_ID; Databricks HTTP 403; Hugging Face Space stage BUILD_ERROR. The read-only deploy-sync and system-prompt checks passed. No deployment or credential mutation was attempted.
- The current-main CI workflow query returned no CI runs for SHA 13c60af. Do not claim main CI passed after the automatic publisher commit.

The paid-issue publisher remains a main-branch writer: it is triggered by successful workflow_run completion, has contents:write, downloads the hunter artifact, copies two data files, and pushes directly to main. This behavior is now evidenced by the actual 13c60af commit. It is not a PR merge. Its workflow and downstream Pages side effects remain part of the security review.

### Repository and security snapshot

- Main tree: 1,737 entries.
- Integration tree: 2,976 entries, including 85 workflow files.
- No dependency lockfiles were present in the integration tree. requirements.txt and pyproject.toml retain broad lower-bound constraints; requirements-integrations.txt has selected upper bounds. The exact-head dependency audit passed, but fully locked/reproducible dependency resolution is not established.
- Main branch is reported protected, but the detailed branch-protection endpoint returns HTTP 403. The branch object exposes no required status-check contexts. The only visible repository ruleset, “Fall Back,” is disabled. Effective required reviews/checks are therefore not verified.
- .github/CODEOWNERS assigns all paths to @Barrot-Agent only; no independent ownership/review is established.
- PR #1663 remains open and draft, with 1,425 changed files, 511,359 additions and 6,522 deletions. No formal reviews or inline review threads exist. GitHub currently reports the PR mergeable, but draft state and the governance/security blockers remain.
- Targeted workflow review confirmed:
  - xrp-public-ingestion.yml uses actions:read and contents:read, disables checkout credential persistence, pins actions by SHA, and writes only Actions artifacts/cache. Scheduled triggers are main-only; integration push capture is path-scoped. Its manual Coinbase backfill input is bounded to 365 days. No manual dispatch/backfill was executed.
  - barrot-agent.yml and ask-barrot.yml are disabled with permissions: {}.
  - barrot-self-upgrade.yml and sync-huggingface.yml are disabled with permissions: {}.
  - barrot-gated-merge.yml is read-only and fail-closed; it does not approve or merge.
  - barrot-ops.yml, deploy-databricks.yml, barrot-restart-space.yml and barrot-merge.yml are manual external-action workflows with explicit YES confirmation and/or exact-main-SHA checks. None was dispatched.
  - coinbase-paper-trader.yml is manual, artifact-only and configured for BTC-USD, not XRP. It was not dispatched.
  - barrot-approve-pr.yml can add an “approved” label with pull-requests:write, but its own log says it does not merge. Such a label is not an independent formal review.
  - paid-issue-publish.yml remains the automatic main writer described above.
- The complete transitive review of all 67 changed workflow files and every invoked script remains incomplete. The targeted review is not a substitute for that audit.

### XRP ingestion and prediction state

Latest successful public ingestion remains [run 44301868145](https://github.com/Barrot-Agent/B-Agent/actions/runs/44301868145), cutoff 2026-11-18T12:13:54.617611Z.

- 3,235 historical feature records across 15 snapshots.
- 124 eligible current records; 361 excluded.
- Five exchange groups: Coinbase, Kraken, Bitstamp, OKX and Bitbank; 11 source snapshots.
- 140 events, 107 scenarios, 23 raw-only sources and 21 source failures.
- 34 receipts: 22 raw payloads retained and 12 digest-only; receipt chain sequence 15 verified and continuous from run 44300915250.
- Raw artifact SHA-256: c9ec648228d5c76136fd68f8d7b0f2b71ea2eb97eebf8b2f8617b9678098b2be.
- Feature-store artifact SHA-256: d13e0c1257e9318fa8160bae711b2cfaf79996f2a3aea886a8600048af7caf5d.
- No independent WORM store or trusted external timestamp anchor exists. Automatic feature-store reconstruction from retained raw receipts is not implemented.
- Eight Binance endpoints returned HTTP 451; five Bybit endpoints returned HTTP 403. No proxy or restriction bypass was attempted. Grayscale returned HTTP 429. Six SEC EDGAR requests remain blocked by the missing approved BARROT_SEC_USER_AGENT contact.
- ETF observations remain non-comparable by fund universe and data vintage; primary AP cash creation/redemption reconciliation is pending. The three CFTC weekly source IDs remain skipped by current source policy.
- Coinbase, Kraken and Bitstamp spot quotes clustered around $0.9842–$0.9847 at the capture. OKX and Bitbank observations require separate USDT/USD and JPY normalization. Deribit XRP-USDC perpetual remains raw-only because contract/OI/book-sequence semantics are not validated. Venue depth imbalances were mixed and are not a directional signal.
- Drift remains INSUFFICIENT_DATA with zero evaluated features. Walk-forward forecast count remains zero. Forecast status remains NOT_ISSUED. No directional forecast, paper trade or real-money action occurred.

### Nine-platform coordination

The Run 14 capability/authentication map remains current. Only the ChatGPT-session-to-GitHub connector path is tested. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks are not verified as live collaborators or data flows. No external-model dispatch, Kaggle submission, Databricks write or Hugging Face upload occurred.

### Open PR inventory and classifications

All ten PRs remain open/draft. No PR was merged or closed in this run.

| PR | Classification | Disposition |
|---|---|---|
| #1663 | blocked — consolidated V3/XRP integration | sole active integration workstream; synchronized with current main |
| #1664 | unique/unreviewed | 71-file paid-issue template pack; two divergent overlaps with #1663 in BARROT_SYNC.md and MEMORY.md |
| #1541 | blocked — partial overlap | five shared paths with #1663; two identical, three divergent |
| #1450 | unique/unreviewed | research/ledger work; substantial overlap with #1440 and three divergent shared blobs |
| #1460 | unique/unreviewed | eight unique institutional multirail, Binance and Kamilah research files |
| #1440 | unique/unreviewed | stacked archive-validator repair; reconcile with #1450 |
| #1436 | unique/unreviewed | Binance incident and wallet-graph research |
| #1437 | unique/unreviewed | source/addenda repair |
| #1353 | unique/unreviewed | large lossless XRP ledger archive/migration; preserve |
| #1265 | unique/unreviewed | compact ledger-index migration; one divergent CI workflow overlap with #1663 |

No duplicate or superseded source PR was closed. No new PR was created.

### Merge disposition

**NO MERGE.**

The full suite passed on code/test head 1d0ade, but the synchronized head 469068 has not had its full suite rerun because the data-only mainline changes are explicitly ignored by the push CI path filter and the integration PR event skips test jobs. This handoff update should trigger the push CI path because this file is not ignored; verify the resulting exact-head run before any readiness claim.

Remaining blockers:
1. PR remains draft with zero independent formal reviews.
2. Effective branch-protection settings and required approvals/checks are not verified.
3. The 67-workflow/transitive-script security review is incomplete.
4. The paid-issue publisher's automatic main write and Pages side effect require explicit review.
5. Main CI has not been observed on current main SHA 13c60af.
6. SEC contact configuration, independent WORM/timestamp anchoring, raw-to-feature-store rebuild, synchronized historical derivatives/depth, ETF primary-flow reconciliation and model-ready walk-forward sample remain incomplete.
7. No directional prediction is supported by current out-of-sample evidence.

### Next concrete action

Verify the push-triggered full repository suite and dependency audit on the new handoff commit. Then continue the workflow/transitive-script security audit and resolve effective branch protection/independent review. Keep PR #1663 as the only consolidated V3/XRP integration path; preserve every unique research and repair PR. Do not merge, deploy, dispatch external actions, paper-trade or issue a directional forecast until its specific gates pass.


---

## Run 15 verification closure — exact code/test head 1c3e76d5

**VERIFIED — full repository CI on exact code/test head 1c3e76d5c212f633c9d87bec9ceeb76bdc0b8510.**

- [CI push run 44312893239](https://github.com/Barrot-Agent/B-Agent/actions/runs/44312893239): all three jobs passed — core Tests, Full repository test suite, and GitHub Pages validation-only.
- The full suite collected 4,274 items: 4,273 passed, 1 skipped, 0 failed, 19 subtests passed, 11 warnings, in 148.77 seconds.
- Inclusive package coverage: 68.14%, above the required 62% floor.
- Legacy core-package coverage: 77%.
- Wheel build and installed-wheel verification passed; the packaged Barrot V3 and XRP primary mission loaded.
- [Dependency Audit, push 44312893325](https://github.com/Barrot-Agent/B-Agent/actions/runs/44312893325): passed.
- [Dependency Audit, PR 44312903012](https://github.com/Barrot-Agent/B-Agent/actions/runs/44312903012): passed.
- [Money audit 44312903034](https://github.com/Barrot-Agent/B-Agent/actions/runs/44312903034): passed.
- [Fail-closed gate, PR 44312903004](https://github.com/Barrot-Agent/B-Agent/actions/runs/44312903004): passed.
- [Fail-closed gate, push 44312892989](https://github.com/Barrot-Agent/B-Agent/actions/runs/44312892989): passed.
- PR-event CI [44312903323](https://github.com/Barrot-Agent/B-Agent/actions/runs/44312903323) also completed successfully; its integration-PR test jobs were skipped by the workflow condition. The push run above is the full-suite evidence.

The preceding handoff synchronization commit 469068e25b4ce004b6298a2a7a14223f7ca5d8db was followed by this exact code/test head. The current handoff-only update is documentation-only; it does not change code, tests, workflows or data. Its resulting commit must still be checked for the expected push CI run before any merge-readiness claim.

### Workflow security review progress

All 67 workflow files changed by PR #1663 were inspected for trigger type, permissions, write scopes, external calls, artifact publication and execution gates. This is a workflow-level review, not a complete transitive review of every invoked script or third-party action.

Findings:
- The previous high-risk autonomous/credentialed workflows are quarantined with permissions: {} and jobs conditioned false: Barrot Agent, Ask Barrot, audio ingest, speech generation, sync, free image generation, Cloudflare diagnostics, self-deployment, force Space deploy, Databricks token rotation, scheduler tick, merge queue, Databricks bundle, self-benchmark, signal ledger, subagent matrix/spawn, task allocator, Groq-chain and semantic-memory tests, WebMCP live sandbox, and lyric generation.
- The XRP ingestion workflow is read-only, path-scoped on integration branches, scheduled only on main, uses credential-free checkout and SHA-pinned actions, and stores only Actions artifacts/cache. No manual backfill was executed.
- Databricks import, Space restart, Hugging Face model upload, Cloudflare A2A deployment, and self-hosted brain deployment are manual or quarantined. The active manual paths require explicit confirmation and exact main SHA; secret rotation has a separate confirmation. None was dispatched.
- Coinbase paper-trader is manual and artifact-only, configured for BTC-USD rather than XRP. It was not dispatched.
- Groq-backed research/content workflows are manual, require public/authorized data confirmation and exact main SHA, and preserve outputs as artifacts rather than committing to main.
- The WebMCP monetization workflow is workflow_run-triggered but read-only; it downloads and uploads artifacts without repository writes.
- Hover Bike and Riemann scheduled workflows are read-only artifact producers.
- Release workflow is tag-triggered on v*.*.* and has contents:write to create a GitHub Release. No release tag was pushed and no release was created.
- Paid issue publish remains the one observed automatic main writer: successful hunter workflow_run → contents:write → two-file main commit. The 13c60af main commit and its Pages side effect prove this path executes. It remains explicitly documented as a workflow side effect requiring review.
- Full transitive inspection of scripts called by the 67 workflows, action supply-chain review and effective repository branch-protection/approval verification remain incomplete.

**Merge status remains NO MERGE.** PR #1663 is still draft with zero independent formal reviews. Branch protection details remain inaccessible (403); the only visible fallback ruleset is disabled; CODEOWNERS remains self-only. Main CI has not been observed on current main SHA 13c60af. Forecast status remains NOT_ISSUED.


---

## Run 16 — 2026-11-18T13:37:04Z — current main audit, exact-head full suite and XRP evidence reconciliation

### DESIGNED / EXECUTED / VERIFIED

**EXECUTED — repository state re-fetched from GitHub; no new branch or PR.**

- Repository: `Barrot-Agent/B-Agent`; default branch: `main`.
- Main SHA: `13c60af7079700a38b4226b9110d9c9377af7695`.
- Integration PR: [#1663](https://github.com/Barrot-Agent/B-Agent/pull/1663), branch `integration/xrp-v3-mainline-successor-20261115T2101Z`.
- Integration code/test head at verification: `3280668245130df197c21c6885575c806ec52d51`.
- PR is open, draft, mergeable according to GitHub, 299 commits ahead and zero behind main; 1,425 changed files (511,527 additions, 6,522 deletions).
- Complete recursive Git tree reads: main 1,737 entries; integration 2,976 entries. Every main path is present in the integration tree (zero main paths missing).
- Paginated PR filename inventory confirms all 1,425 changed paths. The compare-commits API exposes only its first 300 file records; the paginated PR filename endpoint was used for the complete path count.
- No branch rewrite, force-push, main mutation, PR merge or PR closure occurred.

**VERIFIED — exact code/test head `3280668245130df197c21c6885575c806ec52d51`.**

- Push CI [44314056379](https://github.com/Barrot-Agent/B-Agent/actions/runs/44314056379): all jobs passed, including the full repository suite, core tests and Pages validation-only.
- Full suite: **4,273 passed, 1 skipped, 0 failed, 11 warnings, 19 subtests passed** in 115.96 seconds.
- Inclusive coverage: **68.14%**, above the 62% gate. Legacy core coverage: **77%**.
- Wheel built and installed; installed wheel verified Barrot V3, the XRP primary mission and canonical data assets.
- Pages validation verified the global mission manifest remains excluded from public Pages.
- Push dependency audit [44314056129](https://github.com/Barrot-Agent/B-Agent/actions/runs/44314056129): passed.
- PR dependency audit [44314064410](https://github.com/Barrot-Agent/B-Agent/actions/runs/44314064410): passed.
- PR money audit [44314064475](https://github.com/Barrot-Agent/B-Agent/actions/runs/44314064475): passed.
- Push and PR fail-closed gates [44314056202](https://github.com/Barrot-Agent/B-Agent/actions/runs/44314056202) and [44314064462](https://github.com/Barrot-Agent/B-Agent/actions/runs/44314064462): passed with merging disabled.
- PR CI [44314064440](https://github.com/Barrot-Agent/B-Agent/actions/runs/44314064440) passed its workflow, but its full-suite and core-test jobs were skipped because the PR is draft. The push run above is the full-suite evidence.
- Non-failing warnings include setuptools package-discovery warnings for `barrot_agent.data.missions` and `data.research`, and exhausted GitHub Actions cache budget (cache storage read-only). Wheel verification nevertheless passed.

**This handoff update is documentation-only.** The preceding exact code/test head is fully verified; the new handoff commit must receive its own push-triggered CI before its SHA is called exact-head verified.

### Main-branch CI and governance

- Current main SHA `13c60af` has no full repository CI run. The five observed runs on that SHA are two Dependabot dynamic checks, Pages deployment success [44304220732](https://github.com/Barrot-Agent/B-Agent/actions/runs/44304220732), Cross Analysis success [44307953150](https://github.com/Barrot-Agent/B-Agent/actions/runs/44307953150), and Pillars Consistency Check failure [44309596554](https://github.com/Barrot-Agent/B-Agent/actions/runs/44309596554).
- The failed Pillars run reported missing GitHub App credentials, Databricks HTTP 403 and Hugging Face Space BUILD_ERROR. No credential or deployment mutation was attempted.
- Main branch API reports `protected=true`, but visible required status-check contexts/checks are empty. The detailed branch-protection endpoint is not accessible through the current connector. The only visible repository ruleset (“Fall Back”) is disabled. Effective required approvals/checks and bypass permissions remain unverified.
- Main and integration `.github/CODEOWNERS` both assign all paths only to `@Barrot-Agent`. PR #1663 has zero formal reviews, zero inline review threads and no independent reviewer request. It remains draft.
- The main-branch paid-issue publisher actually wrote `PAID-ISSUES.md` and `data/money/paid_issues.json` directly to main at `13c60af` after a successful workflow_run. The integration version still has `contents: write`, persistent checkout credentials and `git push origin main`; it adds a main-head condition and SHA-pins its actions, but it remains an automatic main writer. This is a material merge blocker until explicitly contained/reviewed.
- The tag-triggered release workflow also has `contents: write` and can create a public GitHub Release. No release tag was pushed.
- A targeted static re-scan covered all 67 workflow definitions changed by #1663. No unpinned `uses:` action references were found in those files. This is not a transitive audit of every invoked script, downloaded artifact or third-party action. The complete workflow/script/supply-chain review remains incomplete.
- The XRP ingestion workflow is read-only (`actions: read`, `contents: read`), checks out the exact triggering SHA with credential persistence disabled, and stores run artifacts/cache. Its cron schedule is active only on main; it is not yet a verified production schedule because the workflow is not merged to main.
- The integration branch's Pages job is validation-only. Main Pages publication remains a push side effect; authorization and configuration are not resolved. Do not merge while that side effect is unresolved.

### Current XRP ingestion and prediction readiness

Latest successful public ingestion remains [run 44301868145](https://github.com/Barrot-Agent/B-Agent/actions/runs/44301868145), triggered on integration code head `38b910e7f91e22096a224474be4445ef7f9a7a0d`, cutoff `2026-11-18T12:13:54.617611Z`.

- 3,235 historical feature records across 15 snapshots; 124 eligible current records and 361 excluded records.
- Five exchange groups and 11 source snapshots; 140 events and 107 scenarios.
- 34 source receipts: 22 raw payloads retained and 12 digest-only; receipt-chain sequence 15 verified and continuous from run 44300915250.
- 23 raw-only sources and 21 source failures; six SEC source failures; zero SEC submissions and zero companyfacts captured.
- Run artifacts were still unexpired at this audit: raw payload 462,640 bytes (90-day retention); receipt index 1,161 bytes (90 days); feature-store SQLite 822,789 bytes (7 days); correction audit 11,923 bytes (90 days); event artifact 142,708 bytes (90 days).
- The cross-run receipt chain is internally verifiable but has no independent WORM store or trusted external timestamp anchor. Automatic feature-store reconstruction from retained raw receipts is not implemented. GitHub artifacts/cache are bounded recovery, not immutable external storage.
- Binance public endpoints returned HTTP 451, Bybit endpoints HTTP 403, and Grayscale HTTP 429. No proxy, regional restriction bypass or credential workaround was attempted.
- SEC EDGAR capture remains blocked because `BARROT_SEC_USER_AGENT` lacks an approved monitored project contact email. The adapter correctly fails closed. Do not invent a contact address.
- ETF primary AP creation/redemption evidence and CFTC weekly coverage remain incomplete. Derivatives and order-book observations with unresolved unit, timestamp, sequence or venue scope remain research-only.
- Walk-forward forecast count remains zero; drift remains `INSUFFICIENT_DATA`; forecast status remains `NOT_ISSUED`. No directional forecast or paper trade is authorized.

### Research updates preserved as research-only

**Spot, order books and derivatives — 2026-11-18 observations:**

- Kraken public ticker at 10:27:48Z reported last $0.99919, bid $0.99886, ask $0.99895, 24-hour volume 41.97M XRP, VWAP $0.97469, high $1.00677 and low $0.94500. The payload had no exchange event timestamp; retrieval time is not represented as provider event time.
- Fuelmaps' six-venue spot snapshot at 06:00Z showed a $0.9835 mid and 1% depth of $10.9M bids versus $7.6M asks (59% bid share); 5% depth was $21.0M versus $11.7M (64.2% bid share). This is an older aggregated resting-book snapshot, not executable liquidity; orders can be cancelled.
- CoinGlass' aggregate reported $2.06B USD open interest (+3.82% USD over 24h while XRP-denominated OI declined 0.36%), $2.47B futures volume, a 4.5x futures/spot volume ratio, funding of -0.0029% per eight hours (reported annualized -3.22%), and $5.86M liquidations, 64% attributed to shorts. Exchange constituents and synchronized timestamps are not fully exposed; USD and coin-denominated OI are not interchangeable.
- Nov 17 ETF flow sources disagree: CoinGlass reported -$6.1M; Tokenpost syndicated -$6.14M; CryptoKeyhole's partial issuer-file read showed -3,251 XRP from two of four expected funds; XRP Insights had not yet published its settled Nov 17 universe. Do not average or treat these as the same fund set/vintage.
- Macro context reported by Reuters on Nov 18 included a 103.67 dollar index, 95.7% market-implied probability of a 25bp December Fed hike, USD/JPY 159.25, and BoJ Governor Ueda's further-rate-increase signal. This is context, not a causal XRP feature.

**Binance incident and downstream tracing:**

- Binance reported an unauthorized 233.46M XRP hot-wallet outflow on Oct 29 from five hot wallets. This is a security-incident transfer, not ordinary customer withdrawals, proof of exchange selling or market execution.
- XRPL-Utilities estimated up to 216.4M XRP reached exchange/swap deposit accounts by Nov 12. About 85% of the relevant hub inflows traced to the breach wallet; OKX attribution is analyst-assigned rather than a public wallet label. Santala's trace stops earlier in the wallet path; the reports can coexist because their sampling boundaries differ.
- Once deposited at an exchange, internal order books are not public. The 216.4M figure is an upper bound on breach-attributable deposits, not confirmed net selling or executed sales. The publisher's claimed XRPL Merkle anchor was not independently recomputed in this run.

**Evernorth actual-capital reconciliation:**

- SEC filings identify 346,284,972 XRP held at 2026-09-30 with $846.575M historical cost and $504.688M cumulative non-cash impairment. Impairment is not cash spent or XRP sold.
- Ripple contributed 126,791,458 XRP in kind under a contribution agreement; this is not cash and not a spot purchase. Combined reported XRP at Nasdaq debut was 473,276,430; avoid double-counting the 50,000,001 XRP lot already included in Evernorth's cost-basis table.
- Disclosed capital categories include $48M trust cash released to PubCo, a $30M convertible note with $29M net proceeds, $35.3M gross warrant exercise proceeds and an optional 5,218,935-share equity line with no drawdown disclosed. These are different instruments/vintages; none proves a post-listing spot purchase amount.
- Evernorth named Ripple, Kraken, Coinbase and BitGo as institutional execution partners, but actual executed XRP purchase amounts and deployed yield balances were not disclosed.

**Institutional and identity distinctions:**

- Circle's first-party USDC material lists native XRPL issuance; that does not establish a Circle–Ripple corporate partnership or XRP demand. Circle reserve custody at BNY is distinct from issuer/network usage.
- Ripple/Coinbase RLUSD distribution on Prime, Exchange and retail is distribution access; Global Exchange collateral use was described as a later step, not verified as active.
- Ripple/SBI Group RLUSD distribution through SBI VC Trade in Japan is a stablecoin issuer/distribution relationship, not proof of XRP purchases or collateral utilization. SBI's JPYSC rail is separate.
- BNY's announced XRP/RLUSD custody support does not disclose balances, new purchases or collateral utilization.
- Japan's SBIC East (Tokyo), SBIC Central (Nagoya) and SBIC West (Osaka) are three distinct regional statutory companies, not SBI Holdings. The Tokyo SBIC ChatGPT/Copilot course was delivered by VOST for SBIC investee companies; it does not establish an OpenAI partnership or XRP relationship.
- ASK Coin research identifies the Permission.io advertising/data-reward token as a candidate match; no verified XRP relationship is established. “Actual capital” remains classified by cash, debt, warrants, in-kind XRP and optional financing capacity rather than one aggregate.
- One TEDx video attributed to Kamilah Stevenson is verified; personal YouTube channel ownership and other candidate identities remain unverified.

### Nine-platform capability/authentication/permission/data-flow map — Run 15

| Platform | Status at this audit | Verified data flow |
|---|---|---|
| ChatGPT | tested_limited | ChatGPT session -> GitHub connector -> repository read and integration-branch operations |
| Claude | unverified | none |
| Grok | unverified | none; Groq is not Grok |
| Gemini | unverified | none |
| Copilot | historical_unverified | no current authenticated flow |
| Codex | unverified | none |
| Hugging Face | unverified | repository workflow exists; no current authenticated upload/data flow |
| Kaggle | unverified | repository workflow exists; no current authenticated submission/data flow |
| Databricks | unverified | repository workflow exists; no current authenticated write/deployment flow |

Repository metadata reports admin permissions for this GitHub connector, but exact token scopes were not introspected and main branch protection could not be fully read. Do not describe the nine platforms as connected collaborators or claim independent red-team quorum.

### Current open PR inventory and overlap classification

All 12 PRs remain open. No source PR was closed.

| PR | Current classification | Relationship to #1663 |
|---|---|---|
| #1663 | blocked — sole consolidated V3/XRP integration | active integration workstream; draft |
| #1666 | unique dependency update, unreviewed | shares `pyproject.toml`; do not merge ahead of integration reconciliation |
| #1665 | unique dependency update, unreviewed | shares `requirements-dev.txt`; do not merge ahead of integration reconciliation |
| #1664 | unique/unreviewed paid-issue template pack | 71 paths; two shared divergent files: `BARROT_SYNC.md`, `MEMORY.md` |
| #1541 | blocked stacked MMI security work | all five changed paths overlap #1663; branch is based on #1540, not main; preserve and reconcile, do not close |
| #1450 | unique/unreviewed Binance/escrow research successor | 116 paths; no path overlap with #1663; reconcile with #1440 |
| #1460 | unique/unreviewed institutional multirail research | eight paths; no overlap with #1663; stacked on #1450 |
| #1440 | unique/unreviewed archive-validator repair | 64 paths; no overlap with #1663; stacked on #1436 |
| #1436 | unique/unreviewed Binance incident/wallet graph | 24 paths; no overlap with #1663 |
| #1437 | unique/unreviewed archive/addenda repair | five paths; no overlap with #1663 |
| #1353 | unique/unreviewed lossless XRP ledger archive/migration | 1,084 paths; no overlap with #1663 |
| #1265 | unique/unreviewed compact ledger-index migration | 144 paths; one shared divergent path: `.github/workflows/ci.yml` |

PR #1665 and #1666 are non-draft and GitHub reports them mergeable, but no merge was attempted: main publication side effects remain unresolved, they overlap the integration dependency files, and their independent review/check requirements have not been established. Do not close or bulk-rebase unique research PRs.

### Merge disposition and next concrete actions

**NO MERGE.** The exact integration code/test head passed the full repository suite and security audits, but merge conditions are not satisfied.

1. Obtain independent code/security review; current CODEOWNERS and reviews are self-only/empty.
2. Resolve the paid-issue workflow's automatic `contents:write` main push and the tag-triggered public release side effect.
3. Obtain authoritative effective branch-protection/required-check evidence and resolve Pages deployment authorization.
4. Complete transitive review of all changed workflows, invoked scripts and third-party action supply chains.
5. Establish an approved monitored SEC contact; do not invent one.
6. Implement independent raw receipt anchoring and a reproducible raw-to-feature-store recovery/rebuild path without treating Actions artifacts/cache as WORM.
7. Improve synchronized historical spot/depth/derivatives and issuer ETF flow coverage; preserve provider 403/451/429 restrictions and use lawful fallbacks.
8. Keep forecasts disabled until the full leakage-safe baseline, calibration, drift, independent shadow and evaluator-attestation policy passes.

No merge, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, Hugging Face upload, external-model dispatch, paper trade, funds transfer or real-money action occurred in this run.


---

## Run 16A — 2026-11-18T13:45:11Z — primary SEC correction: Evernorth XRP acquisition, SBI ownership and identity gates

This addendum corrects and supersedes any earlier shorthand that treated Evernorth's funding only as company-level cash, or implied that the exact ASK/Kamilah identities were uniquely resolved.

### Primary-source capital and XRP-flow reconciliation

**Primary source:** Evernorth Holdings Inc. Form 10-Q filed November 13, 2026, included in SEC Form 424B3, accession `0001628280-26-073933`:
https://www.sec.gov/Archives/edgar/data/2092592/000162828026073933/evernorth424stickerposam-1.htm

The filing states that advance-funding investors contributed **$214,049,995 cash by October 23, 2025** and **600,000 XRP by October 24, 2025**. Evernorth used the cash to purchase **84,365,876.3625 XRP**; the XRP was received partly on October 31, 2025 and the remainder by November 6, 2025. The purchased XRP and other contributed XRP were held in an unencumbered custody wallet in PubCo's name for the investors' benefit pending the October 9, 2026 closing, then released at closing. The SEC filing is explicit that the $214.05M was used to buy XRP; this is a historical acquisition, not merely unused financing capacity.

The earlier cash-bridge correction records $214,000,000 as the purchase cost, $49,995 as the remaining restricted cash from the exact $214,049,995 receipt, and a derived average acquisition cost of approximately **$2.53657058/XRP**. Keep the exact receipt, cash deployed, restricted remainder and derived average in separate fields. Do not replace the exact $214,049,995 cash receipt with the rounded $214,000,000 purchase-cost field.

The capital/XRP bridge is:

| Component | Amount | Classification |
|---|---:|---|
| Advance-funding cash received | $214,049,995 | Cash subscription |
| Cash deployed to acquire XRP | $214,000,000 | Historical XRP acquisition; $49,995 remained restricted |
| XRP acquired with advance cash | 84,365,876.3625 XRP | Cash-funded XRP, received Oct 31–Nov 6, 2025 |
| Advance-funding XRP contribution | 600,000 XRP | In-kind contribution; not cash |
| Delayed funding at closing | $10,500,000 + 200,000 XRP | Separate closing subscription; not part of the $214M purchase |
| RippleWorks/Sponsor Series C | 211,319,096.061435 XRP | In-kind contribution routed through Arrington Sponsor; RippleWorks is a nonprofit foundation and Sponsor limited partner |
| Contributor Related Party Entity | 50,000,000 XRP | In-kind contribution by the Larsen Lam Children's Remainder Trust; not cash |
| Ripple contribution | 126,791,458 XRP | Direct in-kind contribution to Pathfinder |
| Total in-kind XRP | 388,910,554.061435 XRP | Sum of the 600k, 200k, 211.319096M, 50M and 126.791458M components |
| Pathfinder gross XRP at closing | approximately 473,276,430 XRP | 84.365876M cash-acquired plus 388.910554M in-kind; not all directly attributable to PubCo |

The post-close SEC disclosures report **346,484,972 XRP transferred by Evernorth to Pathfinder**, plus Ripple's separate **126,791,458 XRP** contribution, for approximately **473,276,430 XRP at Pathfinder**. PubCo's principal asset is its **71.5% ownership interest in Pathfinder**; do not report the entire Pathfinder gross balance as 100% directly owned by PubCo.

The November 17, 2026 8-K/A pro forma cash bridge reports approximately **$48.0M** released from the SPAC Trust Account after redemptions; the pro forma table shows $48,003,633. Combined with $214,049,995 advance cash and $10.5M delayed cash, this produces approximately $272.55M gross closing cash, reported in rounded form as **$272.6M**. The trust release is SPAC trust cash after redemptions, not new subscription capital. Do not treat all $272.6M as new outside investor cash or as XRP purchase capital.

**Point-in-time treatment:** the XRP acquisition event time is October 31–November 6, 2025; its public filing/known-at date is November 13, 2026. Do not backdate public knowledge to the 2025 acquisition date. The purchase method/venue is not identified by the cited passage. Coinbase is Evernorth's selected principal accounting market for fair-value/impairment purposes, not proof that the 84.365876M XRP was executed on Coinbase. The filing identifies BitGo Trust as the initial post-transaction custodian; do not assume that this is the current custodian without a later filing.

The 10-Q/424B3 and the November 17 8-K/A are issuer-authored SEC disclosures in the same issuer source-independence group. The rendered SEC pages were reviewed, but complete raw HTTP bytes, response headers and independent timestamp anchoring were not retained. This evidence is **model-ineligible** until byte-complete captures and SHA-256 receipts are stored. It is suitable as a dated corporate/event research lead, not a current spot-flow feature or a directional price signal.

### SBI Holdings ownership and the separate SBIC entities

The October 19, 2026 Evernorth prospectus defines “SBI” as **SBI Holdings, Inc.**, a Japanese corporation listed on the Tokyo Stock Exchange Prime Market. Its “SBI Stockholders” are four controlled/managed entities:

- SBI Venture Fund 2023A Investment LPS
- SBI Venture Fund 2023B Investment LPS
- SBI PE Holdings Co., Ltd.
- SBI Holdings USA, Inc.

The prospectus reports **9,431,914 Pubco Class A shares**, representing **39.9% of Class A voting shares**, and **2,359,038 Class C shares**, representing **7.5% of the Class C class**. Class C shares are non-voting (except limited statutory matters) but carry economic/distribution rights. The reported combined common ownership is **21.4%**; do not confuse this with the 39.9% voting/Class A threshold.

The SEC 10-Q also says certain investors affiliated with SBI Holdings amended their advance-funding subscription agreements so Class A issuance was capped at 39.9%; the excess subscribed shares were issued as Class C. This is a direct SBI Holdings equity/subscriber relationship with Evernorth. **The reviewed filings do not isolate SBI's exact dollar or XRP share of the aggregate $214.05M advance-funding pool. Do not attribute the full $214.05M or all 84.365876M purchased XRP to SBI.**

Keep SBI Holdings separate from SBIC East Japan, SBIC Central Japan and SBIC West Japan. The SBIC East 2025 ChatGPT course was an investee-company training course delivered by VOST; it is not an OpenAI partnership and is not the SBI Holdings investment described in the Evernorth prospectus.

Primary references:
- October 19, 2026 Evernorth prospectus: https://www.sec.gov/Archives/edgar/data/2092592/000119312526425367/d184594d424b3.htm (Advance Funding definition and purchase/escrow mechanics; Principal Securityholders table and SBI Stockholder footnote).
- November 13, 2026 Evernorth 10-Q/424B3: https://www.sec.gov/Archives/edgar/data/2092592/000162828026073933/evernorth424stickerposam-1.htm (advance cash/XRP dates, SBI-affiliated subscription amendment, XRP accounting principal market and BitGo initial custody).
- November 17, 2026 8-K/A pro forma: https://www.sec.gov/Archives/edgar/data/2092592/000162828026074319/evernorth-proforma20260930.htm (post-redemption trust release and closing cash adjustments).
- Existing structured reconciliation: `research/xrp_intelligence/20261116T154625Z-run191-evernorth-ask-coin-kamilah-rwa-verification.json`.
- Existing capital/ownership ledger: `research/xrp_intelligence/20261107T222415Z-evernorth-actual-capital-vs-capacity-sec-reconciliation.json`. Its older $47.6M trust figure is superseded for the closing trust cash bridge by the later 8-K/A pro forma's approximately $48.0M / $48,003,633 figure. Preserve the old artifact; do not overwrite it.

### Debt and contingent capacity remain separate

- The $30M 4.00% Convertible Senior PIK Note issued October 13, 2026 produced $29M net cash after the $1M advisory fee. It is debt, not equity or proof of XRP acquisition. The 8% yield-to-put and up-to-4x conversion cash-settlement terms are separate contingent liabilities.
- Pathfinder's $9.7M Ripple facility draw as of October 7, 2026 is debt; repayment/extension after the October 9 closing remains unresolved in the reviewed public evidence. Keep it separate from Evernorth's separate $1M Ripple revolving facility, for which no draw was reported as of September 30.
- Public warrant exercises from October 12 through November 9 produced $35.3M gross cash; the filing does not earmark those proceeds for XRP.
- The Cantor ELOC covers up to 5,218,935 shares at 97% of applicable VWAP. Registration effectiveness is not proof that every commencement condition was met or that any draw occurred. Potential proceeds are financing capacity, not actual cash received.
- The exact phrase “actual capital” is not a defined SEC instrument or issuer term in the reviewed filings. Use a ledger separating cash received, cash deployed to buy XRP, in-kind XRP, debt, warrants, optional ELOC capacity, trust cash and non-cash impairment.

### Exact-phrase and person/video identity corrections

**ASK Coin:** do not collapse the candidates. Permission Coin (ticker ASK) is supported by Permission's first-party token documentation, while a separate inactive/untracked “Ask Coin” exchange listing appears in secondary CoinMarketCap metadata. Their relationship is not established, neither has a verified XRP/Ripple relationship, and the listing pages share one publisher independence group. Exact phrase remains ambiguous; both stay model-ineligible pending primary entity/contract evidence.

**Dr. Kamilah Stevenson:** person identity is high-confidence but not absolute, supported by her first-person interview and first-party Wealth Doctor site. The `@drkamilahstevenson` channel association is strongly corroborated, but the canonical channel ID/reciprocal first-party cross-link is not fully verified. The Run194 inventory contains three creator-channel upload candidates, one verified Paul Barron guest appearance (not her own-channel upload), two Glasp transcript candidates pending direct metadata and one third-party clip excluded. The inventory is partial, not exhaustive. Do not attribute the lookalike `@KamilahStevensonXrpStocks` channel or treat creator commentary as primary XRP market evidence.

### Prediction-engine impact

The $214.05M / 84.365876M XRP acquisition is a real historical corporate XRP acquisition, but it is not a current market-flow observation. The event should enter an event timeline with separate `event_time` (2025-10-31 through 2025-11-06), `known_at` (2026-11-13 filing date), entity, amount, funding source, escrow/beneficial-interest status and source-independence group. It remains excluded from the point-in-time feature store until raw source bytes, exact hashes, independent capture time and the relevant ownership/beneficial-interest fields are verified. It must not be conflated with an exchange withdrawal, an order-book trade, a post-listing purchase or a current XRP demand signal.

### Run 16A verification state

- The preceding documentation head `7b3896ac54de2ff74534cbb8409b3d84fce26b17` passed exact-head push CI [44315533722](https://github.com/Barrot-Agent/B-Agent/actions/runs/44315533722): 4,273 passed, 1 skipped, 0 failed, 11 warnings, 19 subtests; inclusive coverage 68.14%, legacy core 77%; wheel and primary mission verification passed.
- Dependency audit [44315533614](https://github.com/Barrot-Agent/B-Agent/actions/runs/44315533614), fail-closed gate [44315533636](https://github.com/Barrot-Agent/B-Agent/actions/runs/44315533636), PR dependency audit [44315545764](https://github.com/Barrot-Agent/B-Agent/actions/runs/44315545764), PR money audit [44315545119](https://github.com/Barrot-Agent/B-Agent/actions/runs/44315545119), PR fail-closed gate [44315545134](https://github.com/Barrot-Agent/B-Agent/actions/runs/44315545134) and PR CI [44315549850](https://github.com/Barrot-Agent/B-Agent/actions/runs/44315549850) all passed. PR CI's full-suite job is skipped while #1663 remains draft; the push run is the full-suite evidence.
- This Run16A handoff correction is documentation-only. Its new commit must receive its own push-triggered exact-head CI before that new SHA is considered verified.
- #1663 remains draft and blocked by independent review, effective branch-protection evidence, the automatic main-writer/release workflow side effects, Pages deployment authorization and incomplete transitive workflow review. No merge or deployment is authorized by this research correction.
- Forecast remains `NOT_ISSUED`; no paper trade or real-money action occurred.


## Run 17B — Coinbase/Circle/Ripple/SBI graph and current XRP market snapshot

**Repository and exact-head verification**
- Main remains `13c60af7079700a38b4226b9110d9c9377af7695`.
- PR #1663 is the sole consolidated V3/XRP integration. Current head at snapshot: `b1f90a4d92bf3c0e773de452efc9a47127063e05`; 301 commits ahead, 0 behind; 1,425 changed files; 67 changed workflows; draft; zero formal reviews and zero review threads.
- Exact-head push full suite [44316922787](https://github.com/Barrot-Agent/B-Agent/actions/runs/44316922787) was in progress. The prior exact head `7b3896ac54de2ff74534cbb8409b3d84fce26b17` passed 4,273 tests, 1 skipped, 0 failed, 11 warnings, 19 subtests; inclusive coverage 68.14%, legacy core 77%.
- Current PR checks: CI [44316932966](https://github.com/Barrot-Agent/B-Agent/actions/runs/44316932966) passed standard tests (full-suite job skipped because draft); dependency audit [44316932883](https://github.com/Barrot-Agent/B-Agent/actions/runs/44316932883), money audit [44316933075](https://github.com/Barrot-Agent/B-Agent/actions/runs/44316933075), and fail-closed gate [44316932863](https://github.com/Barrot-Agent/B-Agent/actions/runs/44316932863) passed. Merge remains disabled.
- No main write, merge, deployment, secret rotation, external model dispatch, Kaggle submission, Databricks write, Hugging Face upload, paper trade or funds transfer occurred.

**Current market snapshot**
- CoinGecko's dynamic XRP page showed $0.9854, 24-hour range $0.9468–$1.01, 24-hour volume about $1.798B, +1.1% over 24 hours and -7.1% over seven days.
- Aggregate perpetual open interest was about $1.856B, funding -0.0040% per eight hours and perps/spot volume 19.5x. Binance, Bybit and OKX rows also displayed negative funding. Their timestamps are asynchronous (“Recently”); this is not a synchronized book or a directional signal.
- The page's Evernorth treasury count was 473,276,430 XRP, valued around $466.36M. It matches the SEC-derived post-close token total but is secondary aggregation, not independent custody proof.

**Direct and indirect institutional relationships**
- **Coinbase ↔ Circle:** Coinbase and Circle ended the Centre joint venture in 2023. Coinbase exchanged its 50% Centre interest for 3.5% fully diluted equity in Circle. The USDC reserve-interest revenue-sharing arrangement continued, with allocation based on USDC held on each platform and broader distribution. This is a direct equity and economic relationship, not merely a listing.
- **Ripple ↔ Coinbase:** On October 28, 2026, Ripple announced RLUSD on Coinbase Prime, Coinbase Exchange and Coinbase Retail. The release said support for Coinbase Global Exchange customers, including RLUSD collateral use, would follow. Do not mark RLUSD collateral support as live from that announcement, and do not infer XRP collateral support.
- **Coinbase ↔ Evernorth:** Evernorth uses Coinbase as its selected principal market for XRP impairment accounting. That is a financial-reporting reference, not proof that the historical XRP purchase was executed on Coinbase.
- **SBI Holdings ↔ Evernorth:** The October 19, 2026 prospectus identifies four SBI-controlled/managed stockholder entities: SBI Venture Fund 2023A Investment LPS, SBI Venture Fund 2023B Investment LPS, SBI PE Holdings Co., Ltd. and SBI Holdings USA, Inc. The prospectus reports 9,431,914 Class A shares (39.9% of voting shares) and 2,359,038 Class C shares (7.5% of the Class C class), with 21.4% combined common ownership. Class C is non-voting except limited statutory matters but carries economic rights. This is a direct Evernorth equity/subscriber relationship; it does not disclose SBI's exact dollar or XRP allocation within the pooled advance-funding subscription.
- **SBI Holdings / SBI VC Trade ↔ Circle:** Circle's Japan expansion uses SBI Group, a joint venture and SBI VC Trade distribution for USDC.
- **SBI Holdings / SBI VC Trade ↔ Ripple:** RLUSD launched in Japan through SBI VC Trade on June 24, 2026 after JFSA approval. This is a separate stablecoin relationship from the Circle/USDC arrangement.
- **Ripple ↔ Pathfinder/Evernorth:** Ripple's 126,791,458 XRP in-kind contribution and Evernorth's post-close subsidiary structure are recorded in the SEC capital bridge. Do not treat the contribution or subsequent intra-group transfer as new spot demand.
- **Circle ↔ Ripple:** no direct corporate partnership or ownership relationship was established in this source set. They are separate stablecoin issuers. RLUSD and USDC activity must not be combined into one issuer relationship or assumed XRP demand.

**Japan SBIC identity**
- SBIC East: Tokyo Small and Medium Business Investment & Consultation Co., Ltd.
- SBIC Central: Nagoya Small and Medium Business Investment & Consultation Co., Ltd.
- SBIC West: Osaka Small and Medium Business Investment & Consultation Co., Ltd.
- These are three separate regional statutory companies, not SBI Holdings. Their official company pages establish the identities; no XRP/Ripple relationship was found. The SBIC ChatGPT course was a VOST-delivered investee-company course, not an OpenAI partnership.

**Phrase and person research**
- ASK: Permission Coin (ASK) and a separate inactive/untracked “Ask Coin” exchange listing remain distinct candidates; no established relationship and no verified XRP/Ripple link.
- “Actual capital”: no single SEC instrument. Maintain separate ledgers for cash received, cash used to buy XRP, in-kind XRP, debt, warrants, trust cash, optional equity-line capacity and non-cash impairment.
- Kamilah Stevenson: use the Run194 partial inventory and identity caveats above; no additional verified videos were added in this run. Do not conflate Camilla and Kamilah or treat creator commentary as primary market data.

**Prediction disposition: NOT_ISSUED.** The dynamic market page and institutional relationships are research leads, not eligible point-in-time features. Walk-forward forecasts remain zero; no directional forecast or paper trade occurred.

**Open PR inventory remains 12.** #1663 remains the sole integration PR. #1665 and #1666 remain blocked despite green tests because they overlap integration dependency files; #1666's allowed Kaggle version range conflicts with a requirements comment warning about Rust `rpds-py`. #1664 remains unique/unreviewed and diverged; #1541 is blocked stacked security work; #1460, #1450, #1440, #1437, #1436, #1353 and #1265 remain unique/unreviewed stacked research/ledger work. No source PR was closed.

**Disposition: NO MERGE.** Current full-suite run must finish on the exact head; independent review, effective branch-protection evidence, automatic main-writer containment and transitive workflow/script review remain blockers.


## Run 18 — exact-head CI, raw-receipt audit, and market/ETF/derivatives reconciliation

**Evidence cutoff:** 2026-11-18T14:02Z  
**Mission:** XRP intelligence and measured prediction-engine mastery remain the highest priority. Barrot V3 remains the execution, orchestration, safety and verification foundation.

### Repository and integration state

- Current main SHA: `13c60af7079700a38b4226b9110d9c9377af7695` (main's latest commit is the paid-issue scan at 2026-11-18T12:28:15Z; parent `e204c21100f3d059e2ba633d041fe8927b61ccaf`).
- Existing consolidated PR: [#1663](https://github.com/Barrot-Agent/B-Agent/pull/1663).
- Integration head at the start of this addendum: `2e6acbfd150fd4ca01ffad4a9ed98bd297f81f76`.
- PR #1663: draft/open, mergeable=true, 302 commits ahead, 0 behind, 1,426 changed files, 512,242 additions and 6,522 deletions. No requested reviewers; zero formal reviews and zero review threads.
- Main tree: 1,737 paths. Integration tree: 2,977 paths. Recursive tree comparison found **zero main paths missing** from the integration tree.
- No branch or PR was created. Main was not modified.

### Exact-head verification — `2e6acbfd`

The integration push CI run [44317989653](https://github.com/Barrot-Agent/B-Agent/actions/runs/44317989653) completed successfully on exact head `2e6acbfd150fd4ca01ffad4a9ed98bd297f81f76`.

- Full repository suite: **4,274 passed, 1 skipped, 0 failed, 11 warnings, 19 subtests passed** in 158.10 seconds.
- Inclusive package coverage: **68.14%**, above the 62% integration gate.
- Legacy core coverage: **77%**.
- Wheel build/install passed; the installed wheel loaded Barrot V3, the XRP mission and canonical data assets.
- GitHub Pages validation passed.
- Push dependency audit [44317990391](https://github.com/Barrot-Agent/B-Agent/actions/runs/44317990391) passed.
- Push fail-closed gate [44317982732](https://github.com/Barrot-Agent/B-Agent/actions/runs/44317982732) passed and kept merge disabled.
- PR CI [44317994477](https://github.com/Barrot-Agent/B-Agent/actions/runs/44317994477), PR dependency audit [44317994370](https://github.com/Barrot-Agent/B-Agent/actions/runs/44317994370), PR money audit [44317994859](https://github.com/Barrot-Agent/B-Agent/actions/runs/44317994859), and PR fail-closed gate [44317994521](https://github.com/Barrot-Agent/B-Agent/actions/runs/44317994521) passed. PR CI skipped its full-suite and core test jobs because the PR remains draft; the exact-head push run above is the full-suite evidence.
- The only observed CI infrastructure warning was GitHub Actions cache-budget exhaustion; cache writes are read-only. This did not fail tests or wheel verification.
- The connector's combined commit-status endpoint returned no legacy status entries; this does not prove required check contexts are configured.

### Ingestion artifact audit — executed and independently rechecked

Latest available XRP ingestion run: [44301868145](https://github.com/Barrot-Agent/B-Agent/actions/runs/44301868145), captured 2026-11-18T12:13:44Z–12:13:55Z on commit `38b910e7f91e22096a224474be4445ef7f9a7a0d`.

The five relevant code blobs are identical between that ingestion commit and current integration head `2e6acbfd`: `xrp_public_ingestion.py`, `feature_store.py`, `forecast_ledger.py`, `sec_edgar.py`, and `xrp-public-ingestion.yml`. The capture therefore exercised the same versions of these five files now present at the current integration head. The capture itself is still an earlier point in time, not a new 14:02 UTC market snapshot.

Downloaded artifacts were inspected locally:

| Artifact | GitHub artifact | ZIP SHA-256 |
|---|---:|---|
| Raw sources and receipts | 14426941429 | `c9ec648228d5c76136fd68f8d7b0f2b71ea2eb97eebf8b2f8617b9678098b2be` |
| Cross-run receipt index | 14426831633 | `cef8b65babeea309e0948917ca277b7dff818232a5ead660e9b8e5b3d2ab2ba8` |
| Feature-store checkpoint | 14426626635 | `d13e0c1257e9318fa8160bae711b2cfaf79996f2a3aea886a8600048af7caf5d` |
| Event timeline and capital events | 14425609609 | `b90376f26f8a794c6c2e1d4d475d7875fbaa5103659d59ddfd285b3b19c63463` |
| Research correction audit | 14426556627 | `328b8aee3abbc9878b9dfcfc6fa35ca04b2505dbd692c90c937cddba4bb163a6` |

Verified observations:

- 34 source receipts; 22 raw payloads retained; 12 digest-only receipts.
- Independently recomputed SHA-256 for all 22 retained raw payloads: **22/22 matched** their content-addressed filenames.
- Per-run receipt chain: `verification_status=PASS`, `verified=true`; 34 receipts.
- Cross-run chain: sequence 15, continuous from sequence 14; `continuity_verified=true`.
- The chain remains **NOT externally anchored**. Its own hash continuity does not prove that the whole chain was not rewritten, and GitHub artifacts are retention-limited, not WORM storage or an independent timestamp authority.
- Latest feature snapshot cutoff: 2026-11-18T12:13:54.617611Z; 124 eligible current features, 361 excluded records, 11 source IDs and five independent exchange groups (Bitbank, Bitstamp, Coinbase, Kraken, OKX).
- Feature-store checkpoint: 15 snapshots, 3,235 feature records and 137 source-snapshot rows. Latest snapshot is exchange spot/ticker/order-book coverage, not a complete XRP ecosystem feature set.
- Drift report: 129 feature definitions, **zero evaluated features**, status `INSUFFICIENT_DATA`; forecast issuance remains disabled.
- Source failures: eight Binance endpoints returned HTTP 451; five Bybit endpoints returned HTTP 403; six SEC EDGAR requests were blocked by the missing monitored `BARROT_SEC_USER_AGENT`; Grayscale returned 429; Franklin's issuer parser failed. These are preserved as failures, not zero observations.
- 23 sources remain raw-only. This includes Deribit perpetual ticker/book unit and sequence semantics, ETF issuer/aggregator vintage validation, XRP exchange-wallet attribution, Circle/Ripple supply dashboards, SBI lending balances, Morpho CBXRP market state and Coinbase CBXRP proof-of-reserves.
- The same-venue OKX XRP-USDT / USDT-USD top-of-book conversion is verified: normalized mid `0.983922118`, spread `1.1153 bps`, component skew 0.657 seconds and maximum component age 9.53 seconds. Both legs share the OKX independence group; this is one venue, not independent corroboration. Only top-of-book prices are converted; depth is not.

Current capture spot observations (2026-11-18T12:13:44Z–12:13:47Z):

| Venue | Last / mid context | Best bid | Best ask | 24h base volume |
|---|---:|---:|---:|---:|
| Coinbase XRP-USD | 0.98420 | 0.98410 | 0.98420 | 94.82M XRP |
| Kraken XRP-USD | 0.98441 last | 0.98396 | 0.98397 | 46.52M XRP |
| Bitstamp XRP-USD | 0.98465 last | 0.98419 | 0.98420 | 12.78M XRP |
| OKX XRP-USDT | 0.98530 USDT last | 0.98500 USDT | 0.98510 USDT | 35.27M XRP |
| Bitbank XRP-JPY | 157.000 JPY last | 157.017 JPY | 157.018 JPY | 6.43M XRP |

These are asynchronous venue snapshots over a few seconds, not a consolidated executable price. OKX's displayed USDT prices must not be treated as USD without the observed USDT/USD conversion. Resting depth can be cancelled; the capture does not reconstruct continuous order flow or synchronized exchange-wide depth.

The workflow file is present only on the integration branch. Its scheduled trigger is therefore not an active production schedule on main. The latest ingestion run above was push-triggered on the integration branch; no newer XRP ingestion run was found. Its push/manual-dispatch job uses read-only `contents: read` and `actions: read`, checkout credentials are disabled, and the raw/feature outputs are artifacts. Hourly/daily production ingestion is **DESIGNED, not active on main**.

### New public market and ETF evidence — research-only, not receipt-backed

The following web observations were captured during this run. They have URL and publication/retrieval context but are not raw HTTP receipt artifacts and remain research-only/model-ineligible until ingested with lawful retention terms, exact bytes/hashes and source-vintage metadata.

**Spot context**

- CoinGecko's XRP history page reported approximately **$0.9805** on Nov 18, 24-hour range **$0.9468–$0.9893**, and approximately **$1.617B** 24-hour volume. Its historical table listed closes of $0.982885 (Nov 17), $0.954586 (Nov 16), $0.974053 (Nov 15), $0.913712 (Nov 14) and $1.011 (Nov 13).
- Investing.com's Nov 18 partial daily bar reported $0.9973, open $0.9835, high $1.0066, low $0.9703 and 368.53M volume. The page-level value differs from CoinGecko's retrieval. Do not average these asynchronous/unequal data vintages.
- URLs: https://www.coingecko.com/en/coins/xrp/historical_data and https://www.investing.com/crypto/xrp/historical-data

**Derivatives — materially different coverage**

- AlertaChart at 2026-11-18 11:16 UTC reported OI-weighted funding **-0.0119% per 8h** and **$642.06M** OI across Binance, Bybit, OKX, Coinbase and Hyperliquid.
- Coinalyze's Binance/Bybit view at approximately 08:31 UTC covered only 2 of 22 contracts and showed **$480.56M** combined OI. Binance funding was -0.003639% and Bybit -0.007266% per 8h. Long-account ratios were 74.04% and 79.65%; taker-buy shares were 50.52% and 51.67%. These long/short ratios count accounts, not position notional.
- OptimistFi's venue table showed about **$1.4B** at 06:00 UTC across 37 venues, while its narrative described **$1.8B** at 07:11 UTC and included CME as the largest venue. Its page mixes different update times and potentially different futures/perpetual coverage. Preserve both observations; do not average them with the two narrower universes.
- Negative funding with high long-account ratios is not a clean directional signal. Contract scope, timestamps, account-versus-notional semantics and futures/perpetual inclusion must be reconciled first.
- URLs: https://www.alertachart.com/data/funding-rates/xrp ; https://bitcoinleverage.com/xrp/funding-rate ; https://optimistfi.com/perps/markets/xrp

**ETF flows — unresolved sign and universe disagreement**

- CryptoKeyhole's 2026-11-18 07:55 UTC update said only 2 of 4 funds had reported for Nov 17 and showed a partial **-3,251 XRP**; its latest complete day was Nov 13 at -9,967 XRP, and its last-five-complete-session sum was -4,923,033 XRP for Nov 9–13.
- XRP Insights showed **+986 XRP** for Nov 17 across six spot funds plus BITW, but excludes GXRP from flow totals while still counting its holdings, and labels the Nov 17 row provisional pending re-settlement.
- Alpha Finance showed a **-$6.1M** Nov 17 flow across five funds, including a -$5.0M XRPC outflow. Its displayed Nov 17 XRP close of $0.9548 does not line up with other Nov 17 reference closes and requires a source-vintage/date check.
- These dashboards use overlapping issuer data and are not independent corroborating sources. The sign, fund universe and settlement vintage are unresolved. Do not use a blended or averaged ETF flow feature. Reconcile each issuer's actual holdings/AP file at a common as-of close, with explicit treatment of GXRP and BITW.
- URLs: https://cryptokeyhole.com/etf-flows/xrp/ ; https://xrp-insights.com/ ; https://xrp-insights.com/data ; https://alphafinance.io/etf/xrp/

### Circle, Ripple, Coinbase, BNY and SBI — relationship corrections

**Circle Q3 2026 primary release (Nov 4):**

- Average USDC circulation was **$73.3B** (+8% YoY); quarter-end circulation was **$73.9B** (flat YoY); Q3 onchain transaction volume was **$13.9T** (+49% YoY).
- Total revenue and reserve income was **$865M** (+17% YoY); reserve income was **$658M** (-8% YoY) with a 3.5% reserve return rate (-61 bps); other revenue was $207M and included $182M of ARC token presale revenue.
- Distribution, transaction and other costs were $412M (-8% YoY); Circle reported CPN annualized TPV of $41.3B.
- Circle's release states Binance made a $100M equity investment in Circle and expanded/renewed its strategic USDC partnership. Circle also reported Arc public mainnet launch, Visa Direct commercial USDC prefunding and a Tazapay acquisition agreement expected to close in 2027 subject to approvals.
- Circle's first-party USDC page reported **$68.0B** in circulation on Nov 16 and listed native USDC support on 38 networks, including XRPL. The difference between quarter-end $73.9B and Nov 16 $68.0B is approximately 8.0%; retain the dates and definitions rather than treating it as an XRP-specific flow.
- Neither $13.9T total USDC onchain volume, $41.3B CPN annualized TPV nor USDC supply establishes XRP purchase demand or XRPL-specific volume.
- Primary URLs: https://s206.q4cdn.com/265218871/files/doc_earnings/2026/q3/earnings-result/3Q26-Earnings-Release.pdf ; https://www.circle.com/usdc ; https://www.circle.com/transparency

**Ripple / Coinbase / BNY / SBI:**

- Ripple and Coinbase's Oct 28 release confirms RLUSD distribution through Coinbase Prime, Coinbase Exchange and Coinbase Retail, with XRPL, Base and Ethereum deposits/withdrawals and USD conversion. Coinbase Global Exchange collateral support was described as a later step, not live at launch. This is a distribution relationship, not evidence Coinbase bought XRP or that RLUSD collateral use is already active there. https://ripple.com/ripple-press/ripple-and-coinbase-partner-to-expand-access-to-rlusd/ ; https://www.coinbase.com/blog/rlusd-is-now-available-on-coinbase
- BNY's Oct 27 release confirms support for XRP and RLUSD custody for eligible clients, its primary RLUSD reserve-custodian role and a Ripple Prime custody relationship. No XRP custody balance, purchase, collateral utilization or client allocation is disclosed. https://prodcs.bny.com/corporate/global/en/about-us/newsroom/press-release/ripple-expands-strategic-digital-assets-collaboration-with-bny-across-custody-and-tokenized-trade-finance.html
- Ripple/SBI RLUSD distribution in Japan through SBI VC Trade and SBI's separate JPYSC initiative remain distinct from XRP demand. The three regional SBIC investment companies remain distinct from SBI Holdings. https://ripple.com/ripple-press/ripple-and-sbi-group-partner-to-launch-ripple-usd-in-japan/ ; https://www.sbigroup.co.jp/news/pr/2026/0624_16424.html ; https://www.sbigroup.co.jp/news/2026/0624_16425.html

**Competing hypotheses retained:**

1. USDC/RLUSD/JPYSC distribution and settlement rails can substitute for XRP in corridors with liquid direct fiat/stablecoin pairs, reducing bridge-asset need.
2. XRP may retain bridge utility where direct pairs are illiquid, fragmented or unavailable; this requires measured corridor-level execution, spreads, settlement and inventory data.
3. Institutional custody support and stablecoin listings can improve access without causing any incremental XRP purchases or collateral utilization.
4. Lower USDC circulation alongside large gross settlement volumes can reflect velocity, treasury rotation, chain migration or redemptions; it is not evidence of XRP inflows.
5. ETF flow dashboards can disagree because of fund coverage, issuer publication delay, settlement date, index-fund inclusion and stale price marks; no directional flow conclusion is admitted.

### Security, governance and PR backlog

- Open PR inventory: 12. #1663 is the sole consolidated V3/XRP integration. #1664 is a separate draft paid-issue template pack with overlapping paths. #1665 and #1666 are non-draft Dependabot updates (Pylint and Kaggle) and require their own exact-head review. #1541 is a stacked MMI security PR with overlapping paths. #1460, #1450, #1440, #1437, #1436, #1353 and #1265 remain unique research/repair/ledger work; do not bulk-close them.
- PR #1663 remains draft, with no independent approvals or review threads. Keep it draft.
- Recursive workflow diff inventory: **67 workflow files changed**. A targeted review of high-impact workflows found the paid-issue publisher still has a `workflow_run` trigger on main, `contents: write`, `persist-credentials: true`, and `git push origin main`. It can write to main after a successful paid-issue hunter run. This automatic main-writer side effect remains unresolved.
- The release workflow retains tag-triggered `contents: write` release publication. Manual Databricks deploy, Hugging Face upload and Space restart paths are separately gated, but no such external action was executed. The workflow/script transitive review across all 67 changed workflows is incomplete.
- Main CODEOWNERS remains `* @Barrot-Agent` (self-only). The repository fallback ruleset is disabled. The branch-protection endpoint returns HTTP 403 to the available GitHub integration; effective required checks and bypass permissions cannot be verified. A green CI run is not proof of branch protection.
- Dependency audit covers six manifests and passed on exact head; Dependabot configuration is present. This does not replace full transitive workflow/script and action-supply-chain review.

### Prediction and coordination disposition

- Forecast status: **NOT_ISSUED**. No directional forecast, probability claim, paper trade, real-money action or fund transfer.
- The latest snapshot has five independent exchange groups, but no validated ETF, SEC, exchange-wallet, Deribit, stablecoin, lending or institutional-flow feature set.
- Drift status remains `INSUFFICIENT_DATA`; zero eligible features were evaluated. The walk-forward record count and calibration evidence do not establish out-of-sample superiority or independent shadow outcomes.
- ChatGPT's GitHub connector flow is tested. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks remain unverified for live authentication/data flow. No nine-platform quorum is claimed.

### Run 18 disposition

**NO MERGE.** Exact-head full-suite, dependency audit, money audit and fail-closed checks passed, but the PR is still draft, independent review is absent, branch protection is unverifiable, the paid-issue main-writer and tag-release side effects remain, and the 67-workflow transitive security review is incomplete. No deployment or external write occurred.

**Next concrete actions:**

1. Obtain an independent reviewer and verifiable required-check/branch-protection configuration before considering ready-for-review.
2. Complete the full 67-workflow and invoked-script security review; explicitly contain or obtain approval for the paid-issue main writer and tag-release publisher.
3. Provide a real monitored SEC contact for `BARROT_SEC_USER_AGENT`; do not invent one.
4. Reconcile issuer-level ETF holdings/AP files at one common close and validate the derivatives contract universe, CME/perpetual distinction and OI units.
5. Establish external WORM/timestamp anchoring and raw-artifact-to-feature-store rebuild before admitting source events to predictive evaluation.
6. Enable the scheduled ingestion only after the workflow is safely merged to main and exact-main CI verifies it.
7. Keep forecast issuance disabled until leakage-safe walk-forward evaluation, calibrated baselines, drift monitoring and independent shadow outcomes meet the admission gate.

No source PRs were closed. No branch history was rewritten. No user work was discarded.


## Run 19 — current spot/derivatives/ETF reconciliation, primary relationship checks, and exact-head CI

**Evidence cutoff:** 2026-11-18T15:27:00Z  
**Mission:** XRP intelligence and measured prediction-engine mastery remain the highest priority. Barrot V3 remains the execution, orchestration, safety and verification foundation.

### Repository and exact-head verification

- Current main SHA: `13c60af7079700a38b4226b9110d9c9377af7695`.
- Existing consolidated integration PR: [#1663](https://github.com/Barrot-Agent/B-Agent/pull/1663).
- Integration branch: `integration/xrp-v3-mainline-successor-20261115T2101Z`; current head: `78ed0c1a2e6cec991f6069f4c624e5e40bc96fe0`.
- PR #1663 is draft/open, 303 commits ahead, zero behind, 1,426 changed files, 67 changed workflow files, 512,242 additions and 6,522 deletions. It reports mergeable but `mergeable_state=unstable`; there are zero requested reviewers, formal reviews or review threads.
- Main tree: 1,737 paths. Integration tree: 2,977 paths. The prior complete tree comparison found no main paths missing from the integration tree.
- The exact-head push full repository suite [44322684443](https://github.com/Barrot-Agent/B-Agent/actions/runs/44322684443) passed on `78ed0c1a2e6cec991f6069f4c624e5e40bc96fe0`: **4,274 passed, 1 skipped, 0 failed, 11 warnings, 19 subtests passed** in 121.44 seconds. Inclusive coverage was 68.14%; legacy core coverage 77%. Wheel build and installed Barrot V3/XRP mission verification passed.
- Exact-head dependency audit [44322684282](https://github.com/Barrot-Agent/B-Agent/actions/runs/44322684282), fail-closed gate [44322684556](https://github.com/Barrot-Agent/B-Agent/actions/runs/44322684556), PR dependency audit [44322695733](https://github.com/Barrot-Agent/B-Agent/actions/runs/44322695733), PR money audit [44322695840](https://github.com/Barrot-Agent/B-Agent/actions/runs/44322695840), and PR fail-closed gate [44322695794](https://github.com/Barrot-Agent/B-Agent/actions/runs/44322695794) passed. The PR CI run [44322695849](https://github.com/Barrot-Agent/B-Agent/actions/runs/44322695849) skipped its test jobs because #1663 remains draft; the exact-head push run is the full-suite evidence.
- GitHub Actions cache storage is read-only because the configured cache budget is exhausted. This produced a cache-save warning, not a test failure.
- Main's latest scheduled Cross Analysis [44328988897](https://github.com/Barrot-Agent/B-Agent/actions/runs/44328988897) passed at 14:51:57Z on the current main SHA. The main Pillars Consistency Check [44309596554](https://github.com/Barrot-Agent/B-Agent/actions/runs/44309596554) failed; this is not a full repository CI run. **No full repository suite has been observed on current main.**
- No new branch or PR was created. Main was not modified.

### Current spot and microstructure — research-only

Direct Kraken XRP/USD ticker retrieval at 15:27Z showed last $0.97920, bid $0.97939, ask $0.97946, midpoint $0.979425 and spread approximately 0.715 bps. Its reported 24-hour volume was 47.28M XRP, VWAP $0.979739, low $0.945 and high $1.00677.

Other source vintages were not identical:
- CoinGecko showed $0.9805, a $0.9468–$0.9893 24-hour range, approximately $1.617B volume and $62.43B market cap.
- Investing.com showed a $0.9848 live header at its displayed 10:07:34 clock and a separate partial Nov 18 daily row at $0.9897. Its clock timezone was not disclosed.
- OKX XRP/USDT showed last 0.9834, bid 0.9835 and ask 0.9836 at 15:06:50.141Z. Its USDT/USD quote was timestamped 14:59:39.039Z, a 431.102-second skew. The USDT conversion was rejected as stale; no normalized OKX USD quote was produced.
- No synchronized fresh cross-venue L2 capture was obtained. The latest five-venue ingestion book snapshot remains the 12:13Z capture, not a current continuous order-flow record.

Do not average these values into a synthetic executable price. Kraken is a direct venue quote; CoinGecko and Investing.com are separate dynamic aggregators; OKX is quoted in USDT with an inadmissibly stale conversion leg.

### Derivatives and ETF disagreement

Open-interest sources currently span materially different scopes and vintages:
- Liqwall: $958M at 05:22Z, down 2.1% over 24 hours.
- OptimistFi: $1.8B headline across 37 venues at 09:05 ET; its all-contract subpanel showed $1.4B at 08:00Z.
- CoinGlass: $2.05B at 10:49Z, but its headline OI change (+3.5%) contradicted its own summary panel (-0.18%).
- TradRadar: $1.31B across seven exchanges at 17 Nov 15:35Z, with +0.0011%/8h weighted funding and 76% long-account share.

These are not a common venue/contract universe. Funding units and signs also differ across provider views. Preserve the disagreements; do not average OI or use the apparent positioning as a directional signal.

Nov 17 ETF flow reports also disagree:
- CryptoKeyhole, updated 14:55Z, still had only two of four issuer files and showed -3,251 XRP; the latest issuer file it had read was 05:25Z.
- XRP Insights showed +159,134 XRP across Nov 16–17, two settled sessions, using six spot funds plus BITW and excluding GXRP from flow totals.
- Alpha Finance showed -$6.1M on Nov 17 across a five-fund view and -$10.9M over 30 sessions.

These results have different fund universes, units, completeness and vintages. None is promoted to a settled common-universe feature.

### Macro, institutional adoption and capital

Reuters' Nov 18 report recorded a 19-month dollar-index high at 103.82, markets fully pricing a 25 bp December Fed hike with a small chance of 50 bp, USD/JPY near 159.41, and renewed BOJ tightening signals. It also described a US-China-Russia leaders' meeting agenda covering Ukraine, Iran, trade, AI and nuclear weapons. This is macro/geopolitical context, not an XRP causal coefficient.

Primary-source relationship updates:
- Ripple/Coinbase: RLUSD launched on Coinbase Prime, Exchange and Retail on Oct 28 across XRPL, Base and Ethereum. Coinbase Global Exchange collateral support was announced as forthcoming; current activation was not verified.
- Ripple/BNY: BNY's Oct 27 announcement says it supports XRP and RLUSD custody for eligible institutions, is RLUSD's primary reserve custodian and has a Ripple Prime custody relationship. No incremental XRP purchase, custody balance or XRP settlement volume was disclosed.
- SBI/Circle: SBI Holdings and SBI Shinsei Bank each disclosed a $25M Circle investment at the June 2025 IPO. The 2023 MOU and March 2025 USDC Japan launch establish the SBI/Circle Japan relationship and SBI VC Trade distribution.
- SBI/Ripple: SBI VC Trade, an SBI Holdings subsidiary, launched RLUSD in Japan on June 24, 2026 following JFSA approval. RLUSD is not XRP.
- Coinbase/Circle: Coinbase's 2023 SEC-filed 10-K records the exchange of its 50% Centre JV interest for 3.5% of Circle's fully diluted equity.
- Circle/Ripple: no direct corporate partnership was established in the reviewed primary sources. Shared exposure through Coinbase, BNY and payment infrastructure is indirect.

The Nov 13 SEC filing confirms $214,049,995 of advance cash was used by Evernorth to purchase 84,365,876 XRP, received between Oct 31 and Nov 6, 2025. Separately, it reports $272.6M gross closing cash before transaction expenses and 388,910,554 XRP contributed in kind. The $30M convertible note produced $29M net cash for general corporate purposes including possible XRP acquisition; the filing does not prove those note proceeds bought XRP. The ELOC is optional share-sale capacity, not confirmed cash. Coinbase is Evernorth's principal market for accounting fair-value/impairment measurement; Evernorth says it does not actively trade XRP on digital-asset markets. Do not infer Coinbase execution or attribute pooled cash/XRP to SBI without disclosed allocation.

### SBIC, exact phrases and creator identity

- Primary corporate profiles resolve SBIC East as Tokyo Small and Medium Business Investment & Consultation Co., Ltd.; SBIC Central as Nagoya Small and Medium Business Investment & Consultation Co., Ltd.; and SBIC West as Osaka Small and Medium Business Investment & Consultation Co., Ltd. These are separate regional companies, not SBI Holdings. No XRP/Ripple relationship was found.
- Tokyo SBIC's official June 2025 course listing includes ChatGPT on day one and Copilot on day two, is limited to investee companies, and names VOST as instructor. This explains the public SBIC/ChatGPT phrase without establishing an OpenAI partnership or XRP project.
- Permission's first-party documentation identifies ASK as its ecosystem token. No XRP/Ripple link was established; do not conflate it with an unidentified ASK reference.
- “Actual capital” is not a defined SEC instrument. Preserve cash deployed to buy XRP, gross closing cash, in-kind XRP, debt and optional equity facilities as separate categories.
- Dr. Kamilah Stevenson remains a high-confidence but not absolute identity match. The partial creator-channel inventory contains three uploads: “The New XRP Ledger Demand Curve: $24M to $1.8B” (Apr 7), “Motley Fool just predicted XRP goes below a dollar” (May 5), and “XRPL RWA Settlement Volume Explodes: $3.5B in 30 Days, $900M in One Day” (May 12). The June 11 Paul Barron interview is a guest appearance, not her own-channel upload. The inventory is partial; lookalike channels remain excluded. The reviewed ~400M XRP native-lending commitment and $3.5B/$900M settlement-volume claims remain unverified by primary evidence.

### Prediction, coordination and governance

- Forecast status remains **NOT_ISSUED**. No walk-forward forecast, calibrated directional probability, paper trade or real-money action was produced.
- Latest ingestion remains run [44301868145](https://github.com/Barrot-Agent/B-Agent/actions/runs/44301868145), cutoff 12:13:54Z: 34 receipts, 22 raw payloads, 12 digest-only, 124 eligible features, 361 excluded records, 3,235 feature-history records, 15 snapshots, 140 events, 107 scenarios, 21 source failures and 23 raw-only sources. Six SEC requests failed because `BARROT_SEC_USER_AGENT` lacks an approved monitored contact.
- Receipt-chain sequence 15 is internally verified, but has no external WORM/timestamp anchor; deterministic reconstruction of the feature store from retained raw receipts is not implemented. The ingestion workflow remains integration-only; scheduled production ingestion is not active on main.
- ChatGPT-to-GitHub is the only tested platform data flow. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks remain unverified. Connector permissions reported by repository metadata are broad; exact token scopes and least privilege are not verified.
- Main branch protection reports protected, but detailed protection returns 403 and visible required check contexts are empty. The only visible fallback ruleset is disabled. CODEOWNERS remains self-only (`* @Barrot-Agent`).
- The paid-issue publisher remains an automatic `workflow_run` main writer with `contents: write`, persisted checkout credentials and `git push origin main`. The integration branch still contains that writer. The tag-triggered release workflow also has `contents: write`; it was not triggered. Full transitive review of all 67 changed workflows and invoked scripts remains incomplete.

### Open PR backlog

Twelve PRs remain open. #1663 is the sole consolidated V3/XRP integration and remains blocked/draft. #1665 and #1666 remain blocked dependency overlaps; #1541 remains blocked stacked MMI security work. #1664, #1460, #1450, #1440, #1437, #1436, #1353 and #1265 remain unique/unreviewed or stacked work; do not bulk-close them. No source PR was closed.

### Run 19 disposition

**NO MERGE.** The exact integration head passes the full suite and audited gates, but the PR is draft, has no independent review, effective branch protection is unverifiable, the automatic main writer remains, and the full workflow/script security review is incomplete. Main was not changed. No deployment, secret rotation, Space restart, external platform dispatch, Kaggle submission, Databricks write, Hugging Face upload, paper trade or funds transfer occurred.

**Next concrete actions:**
1. Obtain an independent reviewer and verifiable required-check/branch-protection configuration.
2. Complete transitive security review of all 67 changed workflows and invoked scripts; contain or explicitly approve the paid-issue main writer before merge.
3. Configure `BARROT_SEC_USER_AGENT` only with an approved monitored project contact.
4. Capture fresh byte-exact exchange/ETF/derivatives/SEC sources, reconcile venue and fund universes, and add an external WORM/timestamp anchor plus deterministic raw-to-feature-store rebuild.
5. Activate scheduled ingestion only after safe merge to main and exact-main CI verification.
6. Keep forecast issuance disabled until leakage-safe walk-forward baselines, calibration, drift checks and independent shadow evaluation pass.


## Run 20 — exact-head CI regression diagnosis, full workflow-definition scan, and fresh market snapshot

**Evidence cutoff:** 2026-11-18T16:06:25Z. Main SHA remains `13c60af7079700a38b4226b9110d9c9377af7695`. Integration snapshot head: `a87173273fdbab3c480b4d95bfec3a74db6f6621` on `integration/xrp-v3-mainline-successor-20261115T2101Z`. PR #1663 remains draft/open; 304 commits ahead, 0 behind; 1,427 changed files; 67 changed workflow definitions. Main tree: 1,737 entries; integration tree: 2,978 entries.

### Exact-head CI failure and root cause

The full-suite push run [44337506785](https://github.com/Barrot-Agent/B-Agent/actions/runs/44337506785) completed on exact head `a87173273fdbab3c480b4d95bfec3a74db6f6621` with **4,272 passed, 2 failed, 1 skipped, 11 warnings, 19 subtests passed** in 189.57 seconds. Inclusive coverage was 68.14%; the 62% floor passed.

Failures:
- `tests/test_xrp_nine_platform_map_latest.py::test_latest_map_matches_repository_and_forecast_admission_state` — `KeyError: snapshot_head_sha`.
- `tests/test_xrp_nine_platform_map_latest.py::test_latest_map_preserves_security_gates_and_open_pr_classifications` — `KeyError: pre_fix_pr_head_ci`.

Run 19's update to `nine_platform_capability_authentication_dataflow_map_latest.json` removed 22 historical evidence fields present in the preceding verified map at `78ed0c1`. The tests correctly rejected the lossy rewrite. This is a research-evidence schema regression, not a forecast-engine or market-data failure.

The preceding exact code head [`78ed0c1` full-suite run 44322684443](https://github.com/Barrot-Agent/B-Agent/actions/runs/44322684443) passed **4,274, 1 skipped, 0 failed, 11 warnings, 19 subtests**, with 68.14% inclusive and 77% legacy-core coverage. That result is historical, not a substitute for the failed `a871732` result.

Other checks on `a871732`:
- Push dependency audit [44337506881](https://github.com/Barrot-Agent/B-Agent/actions/runs/44337506881): passed.
- Push fail-closed gate [44337506832](https://github.com/Barrot-Agent/B-Agent/actions/runs/44337506832): passed; merge remained disabled.
- PR CI [44337522662](https://github.com/Barrot-Agent/B-Agent/actions/runs/44337522662): standard tests passed; full suite skipped because #1663 remains draft.
- PR dependency audit [44337522581](https://github.com/Barrot-Agent/B-Agent/actions/runs/44337522581): passed.
- PR money audit [44337522580](https://github.com/Barrot-Agent/B-Agent/actions/runs/44337522580): passed.
- PR fail-closed gate [44337522571](https://github.com/Barrot-Agent/B-Agent/actions/runs/44337522571): passed.
- PR Pages validation passed; no deployment occurred.

### Repair committed to the existing integration branch

The latest nine-platform map is reconstructed by deep-merging the preceding verified map with Run 19's research update, preserving historical CI evidence and schema fields. Repository snapshot metadata is refreshed to 304 ahead / 1,427 files / 67 workflow files / 2,978 tree entries. The test contract now asserts the actual `a871732` failed run and the preceding verified `78ed0c1` run. The repair is committed only to the existing #1663 branch; no new branch or PR is created. Exact-head CI for the repair commit is pending at capture time.

### Full changed-workflow definition scan

All **67/67** changed workflow YAML definitions were fetched and statically scanned. No unpinned `uses:` action references were found. This is a definition-level scan, not a complete transitive review of every invoked script, artifact producer, downloaded artifact or third-party action.

Material controls and blockers:
- `.github/workflows/paid-issue-publish.yml` remains an active `workflow_run` publisher with `contents: write`, persisted checkout credentials and `git push origin main`. It can automatically write paid-issue artifacts to main after a successful main-branch hunter run. Treat this as a merge blocker until artifact trust and publisher behavior are independently reviewed and contained or explicitly approved.
- `.github/workflows/release.yml` has `contents: write` on version-tag pushes. No tag/release was created.
- `.github/workflows/xrp-public-ingestion.yml` is read-only for repository contents/actions; hourly and daily schedules apply to main, while integration push capture is read-only. Scheduled main ingestion is not active until the workflow is merged.
- `barrot-ops.yml`, `kaggle-competitions.yml`, `deploy-a2a-worker.yml`, `deploy-databricks.yml` and `barrot-restart-space.yml` are manual and require explicit per-run confirmations and/or exact-main-SHA checks. None was run.
- `sync-huggingface.yml` and `sync-self-hosted-brain.yml` are quarantined with job conditions set to false.
- `coinbase-paper-trader.yml` is manual and artifact-only; it was not run.
- Main reports protected, but detailed branch-protection retrieval returns HTTP 403. Visible repository ruleset `10863829` is disabled. `.github/CODEOWNERS` remains `* @Barrot-Agent`. Independent review is absent.
- Transitive workflow/script/artifact review remains incomplete.

### Open PR inventory and path-overlap reconciliation

Twelve PRs remain open:

| PR | Classification | Shared paths with #1663 |
|---|---|---|
| #1663 | blocked — sole consolidated V3/XRP integration | — |
| #1664 | unique/unreviewed | 3: `BARROT_SYNC.md`, `MEMORY.md`, `README.md` |
| #1665 | blocked — dependency overlap | 1: `requirements-dev.txt` |
| #1666 | blocked — dependency overlap | 1: `pyproject.toml` |
| #1541 | blocked — stacked MMI security work | 5 |
| #1460 | unique/unreviewed | 0 |
| #1450 | unique/unreviewed | 0 |
| #1440 | unique/unreviewed | 0 |
| #1437 | unique/unreviewed | 0 |
| #1436 | unique/unreviewed | 0 |
| #1353 | unique/unreviewed | 0 |
| #1265 | unique/unreviewed | 1: `.github/workflows/ci.yml` |

No source PR was closed. No new PR was created.

### Fresh spot, derivatives and ETF observations — research-only

Kraken's public XRP/USD ticker response was retrieved at 2026-11-18T16:06:25Z; it contains no provider event timestamp. It reported last **$0.97530**, bid **$0.97505**, ask **$0.97514**, spread **0.923 bps**, 24-hour volume **50.38M XRP**, VWAP **$0.980324**, high **$1.00677**, low **$0.94804**, and 24-hour open **$0.98253**. Last was 0.736% below the reported open. The exact response body and SHA-256 `c8b58a616f2864bbe7438acdf938833c3d9a0561fe3909358ee77a4d8379b432` are stored in the Run 20 JSON artifact.

Investing.com's Nov 18 daily row showed **$0.9897**, high **$1.0066**, low **$0.9703**, volume **$350.74M** and +0.62%, approximately 1.48% above Kraken's retrieval-time last. These are different publishers and vintages; they are not averaged or treated as synchronized quotes.

Derivatives provider disagreement persists:
- AlertaChart, updated 11:16 UTC, reported OI-weighted funding **−0.0119% per 8 hours** and **$642.06M** OI across Binance, Bybit, OKX, Coinbase and Hyperliquid.
- Liqwall's 05:22 UTC snapshot reported **$958M** OI, down 2.1% over 24 hours.
- Coinranking's Nov 17 daily row reported **$1.55B** OI and **−0.0083%** funding.

These use different venues, contracts, timestamps and aggregation methods. Do not average them or infer direction from negative funding.

CryptoKeyhole's Nov 17 ETF flow remained partial: **−3,251 XRP across 2 of 4 funds**, with the latest issuer file read at 05:25 UTC. Its latest complete day was Nov 13 at −9,967 XRP. Preserve the partial state; do not promote it to a complete fund-complex flow.

### Prediction and coordination disposition

Forecast status remains **NOT_ISSUED**; zero walk-forward forecasts; drift remains insufficient; external WORM/timestamp anchoring and deterministic raw-to-feature-store rebuild remain absent. SEC EDGAR capture remains blocked until an approved monitored contact is configured in `BARROT_SEC_USER_AGENT`. No directional forecast, paper trade or real-money action occurred.

Only ChatGPT-to-GitHub is verified. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks remain unverified; no external dispatch or data transfer occurred.

**Disposition: NO MERGE.** Keep #1663 draft until the repair head passes the complete suite and exact-head security checks, independent review and effective branch-protection requirements are resolved, and the automatic main writer and transitive workflow/script review are addressed. Main remains unchanged. No deployment, secret rotation, Space restart, Kaggle submission, Databricks write, Hugging Face upload, paper trade, funds transfer or real-money action occurred.

**Next concrete action:** Verify the repair commit's exact-head full repository suite; then continue independent workflow/script review and governance remediation without creating another integration PR.


## Run 21 — exact-head full-suite completion, stale snapshot correction and workflow-run provenance hardening

**Evidence capture:** 2026-11-18T17:07:29.601Z. **Repository:** `Barrot-Agent/B-Agent`. **Main SHA:** `13c60af7079700a38b4226b9110d9c9377af7695` (unchanged at inspection). **Inspected integration code head:** `1ebfdfbe26d6c6d6b11c14d605548a5f79389184` on `integration/xrp-v3-mainline-successor-20261115T2101Z`; PR #1663 remains open/draft. Compare against main: 305 commits ahead, 0 behind. PR: 1,428 changed files, 513,823 additions, 6,522 deletions, 67 changed workflow files. Complete tree: main 1,737 entries; integration 2,979 entries (85 workflow files, 503 test-named files, 1,137 XRP-named paths).

### Exact-head CI — inspected head `1ebfdfb`

- Push full-suite run [44345171052](https://github.com/Barrot-Agent/B-Agent/actions/runs/44345171052): **4,274 passed, 1 skipped, 0 failed, 11 warnings, 19 subtests passed** in 185.39 seconds; inclusive coverage **68.14%**; the 70% legacy-core coverage floor passed; wheel build and installed-package verification loaded Barrot V3, the XRP mission and canonical assets.
- Push dependency audit [44345171864](https://github.com/Barrot-Agent/B-Agent/actions/runs/44345171864): passed across six manifests; no known vulnerabilities reported.
- Push fail-closed gate [44345171064](https://github.com/Barrot-Agent/B-Agent/actions/runs/44345171064): passed; automatic merge remains disabled.
- PR dependency audit [44345184655](https://github.com/Barrot-Agent/B-Agent/actions/runs/44345184655), money audit [44345184845](https://github.com/Barrot-Agent/B-Agent/actions/runs/44345184845) and fail-closed gate [44345184591](https://github.com/Barrot-Agent/B-Agent/actions/runs/44345184591): passed.
- PR CI [44345184631](https://github.com/Barrot-Agent/B-Agent/actions/runs/44345184631): Pages validation passed, but the core and full-suite jobs were skipped by the `integration/**` PR condition in `ci.yml`. The full-suite evidence is the exact-SHA push run above, not the PR event.
- GitHub Actions cache budget remains exhausted/read-only. This produced a cache-save warning after successful tests and wheel verification; it did not fail the job.

### Snapshot consistency defect found and corrected on the existing integration branch

The latest nine-platform map still described the prior failed head `a871732` (304 ahead, 1,427 files, 2,978 tree entries, 4,272 passed / 2 failed), even though the current inspected branch head was `1ebfdfb` and its exact full suite had passed. The test had been asserting the stale snapshot. Run 21 updates the map and its regression test to the inspected head and exact CI run, preserving the historical failed-run record as prior evidence. No history was rewritten.

### Nine-platform coordination map expanded — assignments are proposals, not dispatches

The map now distinguishes product capability class from verified authentication/data flow. ChatGPT-to-GitHub remains the only tested connection. Eight external platforms remain unverified. Independent proposed tasks now cover: Claude (primary-source entity/ownership verification); Grok (event discovery and counter-hypotheses); Gemini (filing-table extraction and capital reconciliation); Copilot (workflow permissions and supply-chain review); Codex (integration diff and full-suite audit); Hugging Face (artifact provenance/reproducibility); Kaggle (public-data baseline benchmarking); Databricks (append-only raw archive and point-in-time feature-store design). Each assignment is marked `PROPOSED_NOT_DISPATCHED`; no external dispatch or data transfer occurred. A structured evidence-packet schema and disagreement/red-team protocol are recorded.

### Targeted workflow security review and bounded hardening

Reviewed `.github/workflows/paid-issue-hunter.yml`, `.github/workflows/paid-issue-publish.yml`, `.github/workflows/release.yml`, `.github/workflows/xrp-public-ingestion.yml`, `.github/workflows/ci.yml`, `.github/workflows/dependency-audit.yml`, `.github/workflows/barrot-gated-merge.yml`, `.github/workflows/coinbase-paper-trader.yml`, and `scripts/paid_issue_hunter.py`.

- The hunter uses GitHub search/repository metadata reads and writes two local artifact files; it contains no issue comments, claims, labels, assignments or closures. Its workflow uses read-only `contents`/`issues` permissions and checkout credentials are not persisted.
- The publisher is an automatic `workflow_run` writer with `contents: write`, artifact download, credential persistence and `git push origin main`; it writes only `PAID-ISSUES.md` and `data/money/paid_issues.json`. The main-branch version already has this publisher behavior. The integration version adds a source-branch success guard and pinned actions.
- Run 21 further hardens the publisher condition to require a successful run whose branch is `main`, whose `head_repository.full_name` equals `github.repository`, and whose upstream event is only `schedule` or `workflow_dispatch`. Regression assertions were added. This remains an automatic main writer and must be included in independent governance review; no publisher run or main write was initiated in this run.
- `release.yml` retains tag-triggered `contents: write` to create a GitHub Release; no tag or release was created.
- XRP public ingestion is read-only for repository contents/actions and uploads bounded GitHub artifacts; its scheduled main workflow is not active until merged. GitHub artifacts are not WORM. SEC EDGAR remains blocked pending an approved monitored `BARROT_SEC_USER_AGENT`.
- The full 67-workflow transitive script/artifact/supply-chain review remains incomplete. The targeted review above does not clear that blocker.

### Governance and backlog

- PR #1663 remains draft, mergeable, with zero formal reviews and zero requested reviewers. CODEOWNERS remains self-only (`* @Barrot-Agent`). Branch-protection detail retrieval still returns HTTP 403; the visible fallback ruleset 10863829 remains disabled. Effective required checks and bypass permissions are not verified.
- Twelve PRs remain open. #1663 is the sole consolidated integration (blocked); #1665/#1666 are dependency-overlap blockers; #1541 is stacked MMI security work; #1664 and #1460/#1450/#1440/#1437/#1436/#1353/#1265 remain unique/unreviewed or stacked. No source PR was closed.
- Main was unchanged at inspection. No merge, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, Hugging Face upload, external-model dispatch, paper trade, funds transfer, force-push or history rewrite occurred.

### Prediction status

Forecast issuance remains **NOT_ISSUED**; zero authorized walk-forward forecasts; drift remains insufficient; external WORM/timestamp anchoring and deterministic raw-to-feature-store reconstruction remain absent. Latest successful main ingestion remains the earlier recorded run (34 receipts: 22 raw, 12 digest-only; 21 source failures; 124 eligible and 361 excluded features; no external anchor). SEC EDGAR is still blocked by the contact configuration. No directional forecast is supported.

### Run 21 successor-commit verification status

The Run 21 snapshot and bounded hardening are being committed only to the existing integration branch. The exact-head full-suite and audit results above apply to inspected parent `1ebfdfbe26d6c6d6b11c14d605548a5f79389184`; the new successor commit must receive its own exact-head CI before any readiness claim. PR #1663 remains draft and **NO MERGE**.

**Next concrete action:** verify the successor commit's full repository suite and exact-head audits; continue transitive review of the remaining changed workflows and invoked scripts; obtain independent review and verifiable branch-protection/required-check evidence; retain forecast issuance disabled until receipt anchoring, deterministic reconstruction, leakage-safe walk-forward and independent shadow admission all pass.


## Run 22 — 2026-11-18T18:08Z — exact-head CI closure, current-main side-effect audit and live market disagreement

**Mission:** XRP intelligence and measured prediction-engine mastery remain the top Barrot mission. Barrot V3 remains the execution/orchestration/safety/verification foundation. No directional forecast is authorized.

### Repository state — fetched at run start

- Repository: [Barrot-Agent/B-Agent](https://github.com/Barrot-Agent/B-Agent).
- Main: `13c60af7079700a38b4226b9110d9c9377af7695`; the branch ref did not move during this audit.
- Main's latest commit is the automated paid-issue artifact update by `barrot-hunter` at 2026-11-18T12:28:15Z. It changed only `PAID-ISSUES.md` and `data/money/paid_issues.json` (37 insertions/deletions combined).
- Integration: `a40555db09583cbc824de446f415490b3c1081b3`, branch `integration/xrp-v3-mainline-successor-20261115T2101Z`.
- PR [#1663](https://github.com/Barrot-Agent/B-Agent/pull/1663) is open, draft, GitHub mergeable=true, 306 commits ahead and zero behind main; 1,428 changed files, 514,028 additions and 6,522 deletions. The mergeable flag is not approval or readiness.
- Complete recursive trees were fetched without truncation: main 1,737 entries; integration 2,979 entries. Every main path is present in integration (zero missing). Main has 92 workflow files and 140 Python test-named files; integration has 93 workflow files and 518 Python test-named files. The integration tree contains 1,137 XRP-named paths versus 44 on main.
- No branch, PR or new integration workstream was created. The existing #1663 branch was retained.

### Exact-head verification — `a40555d`

- Push full CI [44355121576](https://github.com/Barrot-Agent/B-Agent/actions/runs/44355121576): **4,274 passed, 1 skipped, 0 failed, 11 warnings, 19 subtests passed** in 120.55 seconds.
- Inclusive coverage: **68.14%**, above the 62% gate; legacy core coverage: **77%**, above its 70% gate.
- The full-suite job explicitly ran every repository test, the two runnable legacy test modules and `.barrot/autonomous_tasks/test_math_task.py`; the full-suite job completed successfully.
- Wheel build and installed-package verification passed; the installed wheel loaded Barrot V3, the XRP mission and canonical data assets.
- Push dependency audit [44355121540](https://github.com/Barrot-Agent/B-Agent/actions/runs/44355121540): all six manifests passed; each audited manifest reported **No known vulnerabilities found**.
- Push fail-closed gate [44355121587](https://github.com/Barrot-Agent/B-Agent/actions/runs/44355121587): passed by explicitly keeping automatic merge disabled.
- PR dependency audit [44355134021](https://github.com/Barrot-Agent/B-Agent/actions/runs/44355134021), PR money audit [44355134031](https://github.com/Barrot-Agent/B-Agent/actions/runs/44355134031), and PR fail-closed gate [44355134071](https://github.com/Barrot-Agent/B-Agent/actions/runs/44355134071): passed.
- PR CI [44355134092](https://github.com/Barrot-Agent/B-Agent/actions/runs/44355134092): Pages validation passed, but the PR-event full-suite and core-test jobs were skipped by the integration-branch condition. The push run above is the exact-head full-suite evidence.
- Infrastructure warning: GitHub Actions cache budget is exhausted/read-only. Packaging emitted setuptools namespace/package-discovery warnings for `barrot_agent.data.missions` and `data.research`; wheel build and installed mission verification still passed. These warnings remain technical debt, not test failures.
- The exact-head logs, not a predecessor run, establish the results above.

### Main-branch automatic side effects and security review

- Main's paid-issue publisher still accepts any successful `workflow_run` from the named hunter on main, uses `contents: write`, persists checkout credentials and runs `git push origin main`. The integration version adds upstream success, `head_branch == main`, same-repository and `schedule|workflow_dispatch` guards and pins the actions, but it remains an automatic main writer with `contents: write`, `persist-credentials: true` and `git push`. This is still a merge/governance blocker until the writer is removed, made artifact-only, or explicitly governed and independently approved.
- Main's automatic publisher commit at 12:28:15Z triggered [Pages build/deployment run 44304220732](https://github.com/Barrot-Agent/B-Agent/actions/runs/44304220732); its build, upload and deploy jobs all succeeded. This was an automatic side effect of the existing main workflow, not a deployment dispatched by this run. Treat it as an actual publication side effect, not merely a validation job.
- Main's `.github/workflows/coinbase-paper-trader.yml` remains manually dispatchable without a typed approval or expected-main-SHA preflight; it loads `GROQ_API_KEY` and commits simulation state/logs to main. The integration version changes this to explicit `YES`, exact 40-character main-SHA validation, read-only contents permission, no persisted checkout credentials, guarded position identity and artifact-only output. Neither version was dispatched. No paper trade occurred.
- Main and integration `.github/workflows/release.yml` retain tag-triggered `contents: write` and automatic GitHub Release publication; integration pins the action but does not remove the publication side effect. No tag or release was created.
- `.github/CODEOWNERS` remains `* @Barrot-Agent`; PR #1663 has zero formal reviews and no requested reviewers.
- Branch-protection endpoint still returns HTTP 403 (resource not accessible by integration). The only visible repository ruleset, ID `10863829`, is disabled. Effective required-check enforcement and bypass permissions remain unverified.
- The complete transitive review of all 67 changed workflow definitions, their invoked scripts, downloaded artifacts and third-party action supply chains remains incomplete. The targeted checks above do not clear this blocker.
- Main scheduled [Cross Analysis run 44363340553](https://github.com/Barrot-Agent/B-Agent/actions/runs/44363340553) succeeded. Main scheduled [Pillars Consistency Check run 44309596554](https://github.com/Barrot-Agent/B-Agent/actions/runs/44309596554) failed because `GITHUB_APP_ID/PRIVATE_KEY/INSTALLATION_ID` are missing and the Hugging Face Space stage reports `BUILD_ERROR`. No secret was invented, changed or rotated. This is a provider/configuration blocker, not a failure in the integration full-suite job.
- No fresh full-repository test run on current main SHA `13c60af` was identified in the queried run window. Do not describe the integration test result as main CI.

### Open PR inventory and overlap/ancestry classification

Twelve PRs remain open; none was closed.

| PR | Current classification | Verified overlap / ancestry |
|---|---|---|
| #1663 | blocked — sole consolidated V3/XRP integration | 306 ahead, 0 behind; draft; zero reviews |
| #1664 | unique/unreviewed — staged digital-download product, not published | 81 files; overlaps #1663 on `BARROT_SYNC.md`, `MEMORY.md`, `README.md`; base SHA is stale relative to current main |
| #1665 | blocked — dependency update | `requirements-dev.txt`; overlaps #1663 |
| #1666 | blocked — dependency update | `pyproject.toml` and `requirements-integrations.txt`; overlaps #1663 on `pyproject.toml` |
| #1541 | blocked — stacked MMI security work | all five changed paths overlap #1663; base is the separate MMI provenance branch |
| #1450 | unique/unreviewed — XRP research successor | based on the Binance XRP research branch from #1436 |
| #1460 | unique/unreviewed — institutional multirail/Kamilah research | stacked on the #1450 verification branch |
| #1440 | unique/unreviewed — XRP archive validation repair | stacked on the #1436 research branch |
| #1436 | unique/unreviewed — Binance theft/issuer-freeze wallet graph | based on #1353's ledger-shard branch |
| #1437 | unique/unreviewed — XRP ledger source/validator repair | sibling repair based on #1353's ledger-shard branch |
| #1353 | unique/unreviewed — lossless XRP ledger sharding | based on #1265's index-pointer migration branch |
| #1265 | unique/unreviewed — XRP ledger index-pointer migration | older ancestor in the ledger research chain; overlaps #1663 on `.github/workflows/ci.yml` |

No PR is ready to merge under the full authorization standard. The research/repair chain is not a set of duplicates: retain it and do not bulk-close it. #1664 remains staged and unpublished; no checkout, publication or transaction was initiated.

### Current XRP spot, ETF and derivatives evidence — research-only, not model-eligible

**Kraken XRP/USD public ticker**, retrieved at approximately 2026-11-18T18:08Z. The API response has no provider event timestamp; this is a retrieval-time single-venue observation, not an immutable raw receipt:

- Last: **$0.97631**; best bid **$0.97615** (479 XRP); best ask **$0.97616** (5,123 XRP).
- Displayed spread: **$0.00001**, approximately **0.1024 bps** around the midpoint.
- 24-hour volume: **52.295M XRP**; VWAP **$0.98098085**; high **$1.00677**; low **$0.95326**; open **$0.98253**.
- Last is approximately 0.63% below the API's 24-hour open. The displayed best-ask quantity is about 10.7 times the best-bid quantity, but this is one price level only; do not call it a consolidated order-book imbalance.
- Source: [Kraken public XRP/USD ticker API](https://api.kraken.com/0/public/Ticker?pair=XRPUSD). The public depth endpoint could not be retrieved in this capture; no full L2 depth or cross-venue executable-liquidity result is claimed.

**Derivatives providers disagree materially in scope and total open interest; do not average:**

| Provider / capture | XRP OI | Funding / other context |
|---|---:|---|
| AlertaChart, 11:16 UTC | $642.06M | OI-weighted funding −0.0119% per 8h across Binance, Bybit, OKX, Coinbase and Hyperliquid |
| Coinalyze-derived Binance + Bybit table, checked 14:18 UTC | $474.24M | Binance −0.003639%; Bybit −0.007266%; only 2 of 22 covered contracts |
| TradRadar, 16:05 UTC, 15-minute delayed | $1.32B across 7 venues | OI +1.94% 24h; funding −0.0039% per 8h; at least $4.66M 24h liquidations; account long/short 3.30 (76.8% long) |
| CoinGlass, 30+ exchange aggregate | approximately $2.0B in its displayed long-period comparison | Its page reports OI down 36.2% from $3.1B to $2.0B over the displayed period; not the same contract/venue universe as the other providers |

Sources: [AlertaChart](https://www.alertachart.com/data/funding-rates/xrp), [Coinalyze-derived Binance/Bybit coverage](https://bitcoinleverage.com/xrp/funding-rate), [TradRadar](https://tradradar.io/markets/xrp), [CoinGlass](https://www.coinglass.com/currencies/XRP/futures). These providers do not expose a common contract universe or identical snapshot time. Negative funding is a positioning/carry observation, not a directional forecast.

**ETF flow providers remain unreconciled for 17 November:**

- [CryptoKeyhole](https://cryptokeyhole.com/etf-flows/xrp), updated 07:55 UTC, reports a partial **−3,251 XRP** from only 2 of its 4 daily issuer files; it was still waiting for Bitwise and Franklin. Its latest complete four-fund day was 13 November, **−9,967 XRP**.
- [XRP Insights](https://xrp-insights.com/) reports **+986 XRP** for 17 November across its six spot funds plus BITW; its stated spot-only holdings were about 1.17B XRP, with BITW bringing the combined total to about 1.19B XRP.
- [Alpha Finance](https://alphafinance.io/etf/xrp/) and [ByKaranteli](https://bykaranteli.com/etf/xrp) each display a **−$6.1M** 17 November flow on a five-fund basis; ByKaranteli labels the day provisional.
- These observations differ in fund universe, inclusion of BITW/GXRP, issuer-file completeness, settled/provisional status and unit. Some trackers may depend on overlapping issuer files; source independence is not established. Preserve all vintages; do not average or promote a partial value to a complete complex-wide flow.

These are rendered public observations without captured response bytes, immutable raw-source hashes or independent timestamp anchoring. They remain research-only and model-ineligible. Stablecoin distribution/custody announcements (Ripple–Coinbase RLUSD, Ripple–SBI RLUSD and BNY custody) still do not prove XRP purchases, collateral balances or bridge-payment demand. Measure actual asset-specific flows before inferring demand.

### Prediction and nine-platform status

- Forecast issuance: **NOT_ISSUED**; authorized walk-forward forecasts: **0**; accuracy: **NOT_EVALUATED**.
- No new scheduled XRP ingestion run was verified on `a40555d` during this capture. The latest recorded successful ingestion remains the prior run: 34 receipts (22 raw, 12 digest-only), 21 source failures, 124 eligible and 361 excluded feature records. The SEC adapter remains blocked until an approved monitored contact is configured in `BARROT_SEC_USER_AGENT`.
- External WORM/timestamp anchoring is absent; deterministic raw-to-feature-store reconstruction is not implemented. The feature store is not yet a mature, independently reproducible point-in-time dataset. No baseline superiority or independent shadow outcomes are established.
- ChatGPT-to-GitHub remains the only verified platform connection. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks remain proposed/unverified; no external dispatch or data transfer occurred.

### Run 22 disposition

**NO MERGE.** The exact-head full suite and six-manifest dependency audit passed, but the PR is still draft, independent reviews are absent, branch-protection/required-check enforcement cannot be verified, CODEOWNERS is self-only, automatic main-writing/publishing workflows remain, and the full workflow/script/artifact review is incomplete. The main Pages deployment was an automatic existing-workflow side effect and is recorded above; this run did not deploy anything.

No deployment, secret rotation, Space restart, Kaggle submission, Databricks write, Hugging Face upload, external-model dispatch, paper trade, funds transfer, force-push, history rewrite or source-PR closure occurred.

**Next concrete action:** continue the single #1663 integration by completing the transitive review of the 67 changed workflows and their scripts/artifacts; contain automatic main writers and tag-release publication before merge; obtain an independent approving reviewer and authoritative branch-protection/required-check evidence; then repeat exact-head full-suite and security checks. In parallel, improve receipt-complete multi-venue XRP capture and deterministic rebuild. Keep forecast issuance disabled until the external anchoring, point-in-time reconstruction, leakage-safe walk-forward and independently attested shadow-admission gates pass.


---

## Run 23 — 2026-11-18 (integration, security, and market refresh)

### Repository state and exact heads

- Current `main`: `8e9b2516b5a103e9593124c05edf623e6c7817ff`.
- Consolidated PR: [#1663](https://github.com/Barrot-Agent/B-Agent/pull/1663), still **open and draft**.
- Existing integration branch: `integration/xrp-v3-mainline-successor-20261115T2101Z`.
- Integration head before this handoff update: `89ff4b02317cbbed55c9da4143ce74100faa77a5`; PR reports **316 commits ahead, zero behind**, 1,428 changed files.
- Recursive trees: main 1,737 entries; integration 2,979 entries. Every main-tree path was present in the integration tree.
- No branch or PR was created. No source PR was closed.
- Main's latest commit is an automatic paid-issue publisher commit. It changed only `PAID-ISSUES.md` and `data/money/paid_issues.json`, with parent `13c60af7079700a38b4226b9110d9c9377af7695`.

### Exact-head test repair and CI

The prior integration head `bf7cb7c5b938c0a7a60aac836359359a6d4472a5` failed one full-suite test because the test still expected `permissions.contents: write` from the paid-issue publisher. That expectation contradicted the intended security change: the integration publisher has `permissions: {}`, a job-level `if: false`, and one explanatory step. The failure was a stale test, not a product runtime failure.

- `54570b15152ad9a6b7701dd96878a1573912dfd2`: corrected the test to require the publisher to remain disabled, permissionless, and free of checkout, artifact download, persisted credentials, or git-push behavior.
- `b56b6e25f493e603114034f7ee405515964bbc2b`: corrected the misleading paid-issue-hunter workflow comments. **Exact-head full suite passed** in [run 44379218784](https://github.com/Barrot-Agent/B-Agent/actions/runs/44379218784): 4,274 passed, 1 skipped, 0 failed, 11 warnings, 19 subtests, 119.89 seconds; inclusive coverage 68.14%; legacy core-package coverage 77%; wheel build and installed mission verification passed.
- `89ff4b02317cbbed55c9da4143ce74100faa77a5`: removed a duplicate test function definition that had shadowed one read-only permission test; renamed the no-commit/no-push test so both are collected. Exact-head push CI run [44380133146](https://github.com/Barrot-Agent/B-Agent/actions/runs/44380133146) is still running its full-suite step at handoff time. Do not transfer the `b56b6e2` result to `89ff4b0`.
- On `89ff4b0`, PR CI [44380148522](https://github.com/Barrot-Agent/B-Agent/actions/runs/44380148522), dependency audit [44380148531](https://github.com/Barrot-Agent/B-Agent/actions/runs/44380148531), money audit [44380148489](https://github.com/Barrot-Agent/B-Agent/actions/runs/44380148489), and fail-closed gate [44380148505](https://github.com/Barrot-Agent/B-Agent/actions/runs/44380148505) passed. The PR-event CI deliberately skips the full-suite job for integration branches; the push run is the authoritative full-suite result.
- Push dependency audit [44380133143](https://github.com/Barrot-Agent/B-Agent/actions/runs/44380133143) and push fail-closed gate [44380133124](https://github.com/Barrot-Agent/B-Agent/actions/runs/44380133124) passed.

The repository cache budget remains exhausted/read-only. This is a cache-write warning, not a test failure.

### Main-branch workflow side effects and merge blockers

**Verified automatic write and publication on current main:**

- Main's `.github/workflows/paid-issue-publish.yml` still grants `contents: write`, checks out main with persisted credentials, downloads the hunter artifact, copies files, commits, and pushes directly to main.
- Paid issue publish run [44369074831](https://github.com/Barrot-Agent/B-Agent/actions/runs/44369074831) completed successfully. Its resulting commit is current main `8e9b2516`.
- That push triggered GitHub Pages deployment [44369186191](https://github.com/Barrot-Agent/B-Agent/actions/runs/44369186191); build, upload, and deploy all succeeded. This is a confirmed automatic external publication side effect, not an action initiated in this run.
- The integration branch disables the paid-issue publisher with no permissions and corrects the test contract. The scheduled hunter remains read-only and artifact-only.

**Paper-trader containment:**

- Main's Coinbase paper-trader workflow still has a manual dispatch path that reads `GROQ_API_KEY`, runs the trader, commits state/log files, and pushes to main without a typed confirmation or expected-main-SHA guard.
- The integration version requires typed `YES`, an exact 40-character expected main SHA, read-only contents permission, checkout with persisted credentials disabled, position-identity preflight, and artifact-only output. It was not dispatched.

**Other governance state:**

- Release workflow remains tag-triggered with `contents: write`; no tag was pushed and no release was created.
- Branch-protection detail endpoint returned 403. The only visible repository ruleset, ID `10863829` named `Fall Back`, is disabled.
- `.github/CODEOWNERS` still assigns all paths to `@Barrot-Agent`.
- PR #1663 has no requested reviewers and no submitted reviews.
- The 67 changed workflow definitions and all transitive scripts/actions have not yet completed a full security review.
- Main has no verified full-suite CI result on SHA `8e9b2516`; the latest successful main Cross Analysis run is read-only and is not a substitute for CI.

**Merge remains blocked.** A merge would update main and trigger the currently configured Pages publication. The paid-issue publisher is still live on main until the integration successor is merged, but merging is not authorized while branch protection, independent review, full transitive workflow review, and current exact-head verification remain unresolved. Do not merge or bypass checks.

### Open-PR inventory and overlap classification

Twelve open PRs were rechecked. There are zero ready-to-merge PRs.

| PR | Current classification | Verified overlap / ancestry |
|---|---|---|
| #1663 | **blocked — sole consolidated integration** | Draft; 316 commits ahead of current main; exact-head full suite on latest head pending. |
| #1664 | **unique/unreviewed — partial overlap** | Separate paid-issue product pack; three divergent shared files: `BARROT_SYNC.md`, `MEMORY.md`, `README.md`. Base SHA is stale (`e204c211`). Do not bulk-close. |
| #1665 | **blocked — dependency reconciliation** | Non-draft Pylint update; `requirements-dev.txt` differs from integration; based on stale `13c60af`. Requested reviewer is the repository bot, not an independent approval. |
| #1666 | **blocked — dependency reconciliation** | Non-draft Kaggle update; both `pyproject.toml` and `requirements-integrations.txt` differ from integration; based on stale `13c60af`. |
| #1541 | **blocked — partial MMI overlap** | Five shared paths: `barrot_agent/mmi_adapter.py` and `tests/test_mmi_integration.py` are identical; `barrot_agent/mmi_v1.py`, the canonical-fingerprint operation record, and `tests/test_mmi_v1.py` diverge. Stacked on its security base. |
| #1265 | **blocked — stacked ledger migration with workflow overlap** | At least two divergent shared workflow paths: `.github/workflows/ci.yml` and `.github/workflows/barrot-approve-pr.yml`. Ancestor of #1353. |
| #1353 | **unique/unreviewed — stacked ledger work** | 1,084 files, 1,119 commits; based on #1265's migration branch. Do not close without full content reconciliation. |
| #1436 | **unique/unreviewed — Binance theft/issuer-freeze research** | Based on #1353's ledger branch. |
| #1437 | **unique/unreviewed — source-addenda repair** | Sibling repair based on #1353's ledger branch. |
| #1440 | **unique/unreviewed — archive-validation repair** | Stacked on #1436. |
| #1450 | **unique/unreviewed — Binance research successor** | Based on #1436's research branch. |
| #1460 | **unique/unreviewed — institutional multirail/Kamilah research** | Stacked on #1450. |

No PR is classified duplicate or superseded. No source PR is closed. Finish or explicitly reconcile overlaps before considering any successor or cleanup.

### XRP spot and derivatives snapshot

**Kraken public ticker retrieval (this run; API response has no exchange event timestamp):**

- XRP/USD last trade: **$0.97232**.
- Best bid: **$0.97215**, 193 XRP; best ask: **$0.97236**, 348 XRP.
- Quoted spread: **$0.00021**, approximately **2.16 bps** at the midpoint.
- 24-hour volume: **51.517M XRP**; 24-hour VWAP: **$0.981905**.
- 24-hour high/low: **$1.00677 / $0.95811**; session open: **$0.98253**.
- Top ask size is about 1.8 times top bid size at this one venue and price level only. This is not market-wide imbalance or full depth. Kraken's depth endpoint was not retrievable through the web source in this run; no Level 2 depth claim is made.

Source: https://api.kraken.com/0/public/Ticker?pair=XRPUSD

**Derivatives provider disagreement (different capture times and venue universes; never average):**

- TradRadar, 18 Nov 2026 16:05 UTC: mark price $0.9751 (+1.47%/24h), seven-exchange OI $1.32B (+1.94%/24h), OI-weighted funding −0.0039%/8h, reported liquidations at least $4.66M (shorts $3.07M, longs $1.58M), account long/short ratio 3.30. Venues: Binance, Bybit, Gate, MEXC, Bitget, OKX, Hyperliquid.
- AlertaChart, 18 Nov 2026 17:07 UTC: OI-weighted funding −0.0009%/8h and OI $362.44M across Bybit, OKX, Coinbase, and Hyperliquid; Binance supplied no OI and was excluded.
- Different coverage, price basis, and collection time explain why the OI totals are not directly comparable. Negative funding alongside a long-heavy account ratio is not a directional signal.

Sources: https://tradradar.io/markets/xrp and https://www.alertachart.com/data/funding-rates/xrp

**17 November ETF flow disagreement:**

- CryptoKeyhole, updated 18 Nov 07:55 UTC: only 2 of 4 tracked daily issuer files had reported for 17 Nov, showing −3,251 XRP so far; its latest complete day was 13 Nov at −9,967 XRP, with −4.923M XRP across 9–13 Nov.
- XRP Insights: six spot funds plus BITW reported +986 XRP for 17 Nov; the provider notes a GXRP flow gap and excludes that fund from flow totals while retaining its holdings in aggregate holdings.
- ByKaranteli: five funds reported a provisional −$6.1M for 17 Nov.
- These are different universes, units, and reporting states. No aggregate or directional conclusion is permitted.

Sources: https://cryptokeyhole.com/etf-flows/xrp/ ; https://xrp-insights.com/ ; https://bykaranteli.com/etf/xrp

### Institutional, capital, stablecoin, and payments evidence

**Coinbase — Q3 2026 official results, 29 Oct:**

- Average USDC held in Coinbase products reached **$22B**, about 30% of average USDC market capitalization; Coinbase said it captured approximately 50% of USDC economics over the preceding year.
- Coinbase reported 10.7% crypto trading-volume market share, $719M net income, $78M adjusted net income, and subscription/services revenue at 49% of net revenue.
- These figures establish Coinbase as a major USDC distribution/economic channel. They do not establish XRP purchases.

Source: https://investor.coinbase.com/news/news-details/2026/Coinbase-Q3-2026-Earnings-Show-All-time-high-Coinbase-One-Subscribers-and-Prediction-Markets-Surpassing-200-Million-in-Annualized-Revenue/default.aspx

**Circle — Q3 2026 SEC 10-Q and results, quarter ended 30 Sep:**

- Average USDC circulation **$73.264B**; period-end circulation **$73.879B**.
- Reserve income **$657.624M**, down approximately 8% year over year; other revenue **$207.264M**, including approximately **$182M** of ARC token presale revenue; total revenue and reserve income **$864.888M**.
- Circle reported $104B USDC minted and $104B redeemed during Q3, 27% stablecoin-market share, 7.3M meaningful wallets, and $13.868B USDC on its platform at period end.
- ARC presale revenue is not recurring reserve income or XRP demand. Circle's Arc is a separate L1 and ARC is its native token.

Sources: https://www.sec.gov/Archives/edgar/data/1876042/000187604226000311/crcl-20260930.htm ; https://investor.circle.com/events-and-presentations/event-details/2026/Circle-Reports-Third-Quarter-2026-Results/default.aspx

**SBI — direct Circle relationship and distinct XRP rails:**

- SBI Holdings' 12 May 2026 release says a consolidated subsidiary participated in Circle's ARC token presale, part of a $222M investor consortium. This is an Arc investment, not XRP acquisition.
- SBI Holdings and SBI Shinsei Bank disclosed a combined $50M Circle equity investment at Circle's IPO ($25M each); SBI Circle Holdings was established as the Japan USDC joint venture.
- SBI VC Trade began USDC service in March 2025 and RLUSD handling on 24 June 2026. RLUSD was classified by SBI VC Trade as a Japanese fourth-type electronic payment instrument; the announcement applied to VCTRADE service, not BITPOINT.
- SBI VC Trade and Aplus ran a five-day USDC merchant-payment pilot in Osaka, 25–29 May 2026. It is evidence of a bounded pilot, not continuous production payment volume.

Sources: https://www.sbigroup.co.jp/news/2026/0512_16310.html ; https://www.sbigroup.co.jp/news/2025/0609_15491.html ; https://www.sbigroup.co.jp/news/2025/0325_15331.html ; https://www.sbivc.co.jp/newsview/bsqs09vn_yzv ; https://www.sbigroup.co.jp/news/pr/2026/0430_16290.html

**Ripple — Coinbase and BNY:**

- Ripple's 28 Oct announcement says RLUSD launched on Coinbase Prime, Coinbase Exchange, and Coinbase Retail, with support on XRPL, Base, and Ethereum. Coinbase Global Exchange collateral availability was described as forthcoming, not already proven live.
- BNY's 27 Oct announcement says it supports XRP and RLUSD on its Digital Asset Custody platform, is primary reserve custodian for RLUSD, and has a Ripple Prime custody relationship; the parties are exploring tokenized trade finance.
- These are custody, distribution, and infrastructure links. They do not establish that Coinbase, BNY, or SBI purchased XRP or that RLUSD settlement necessarily uses XRP.
- Circle and Ripple share BNY as an institutional custody node; that alone is not evidence of a direct Circle–Ripple corporate partnership.

Sources: https://ripple.com/ripple-press/ripple-and-coinbase-partner-to-expand-access-to-rlusd/ ; https://www.bny.com/corporate/global/en/about-us/newsroom/press-release/ripple-expands-strategic-digital-assets-collaboration-with-bny-across-custody-and-tokenized-trade-finance.html

### Regulation and forecast discipline

- SEC's Regulation Crypto Assets proposal remained a **proposal** on its 17 Nov 2026 update; it is not a final rule.
- The SEC/CFTC joint interpretation dated 17 Mar 2026 remains relevant context; it does not remove transaction-specific investment-contract analysis.
- No new final regulatory action was verified in this run.

Sources: https://www.sec.gov/rules-regulations/2026/08/s7-2026-27 ; https://www.cftc.gov/PressRoom/PressReleases/9198-26

**Forecast status: NOT_ISSUED.** No probability forecast is authorized. Spot and derivatives observations are not yet joined to an independently anchored, fully reproducible point-in-time dataset with leakage-safe out-of-sample calibration. No guaranteed-return statement, paper trade, or real-money action occurred.

### Ingestion and nine-platform coordination

- Latest previously recorded ingestion count remains 34 receipts (22 raw, 12 digest-only) and 21 source failures. This run did not execute the XRP ingestion workflow.
- The XRP ingestion workflow exists on the integration branch but is absent from current main. Its GitHub artifact retention (7/90 days) is not WORM storage. External immutable anchoring, deterministic raw-to-feature reconstruction, and independent shadow evaluation remain incomplete.
- The nine-platform map remains a capability/permission plan, not nine live connections. Only the ChatGPT-to-GitHub connector path was exercised in this run. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle, and Databricks were not authenticated or dispatched.
- Prior SBIC East/Central/West disambiguation remains separate from SBI Holdings. No new primary evidence was found for an SBIC–ChatGPT commercial relationship. “Actual capital” remains a phrase used in capital-structure reconciliation, not a verified token or issuer. No new first-party identity bridge between Camilla/Kamilah Stevenson and an owned YouTube channel was established.

### Next concrete actions

1. Finish exact-head full-suite CI for `89ff4b0`; capture its test count, coverage, wheel result, and all required job conclusions.
2. Update this handoff with that exact-head result on the next run; do not call a predecessor result exact-head for the handoff commit.
3. Complete transitive review of all changed workflows, invoked scripts, permissions, and third-party action pins.
4. Contain or obtain explicit approval for the current main Pages publication side effect; do not merge while it would cause an unapproved deployment.
5. Obtain independently verifiable branch protection and reviewer approval; the visible ruleset is disabled and CODEOWNERS is self-only.
6. Continue public XRP ingestion only after SEC user-agent configuration and receipt-chain/feature-store integrity checks are satisfied; add a genuine immutable external anchor before promoting receipts to durable evidence.
7. Keep directional forecasting disabled until the chronological walk-forward, baseline comparison, calibration, drift, and independent shadow gates all pass.

**Disposition: NO MERGE.** The integration branch is progressing on its existing PR, but governance and final exact-head verification remain blockers.


### Post-handoff exact-head verification for Run 23

- The full-suite job for code/test head `89ff4b02317cbbed55c9da4143ce74100faa77a5` subsequently completed successfully in [push CI 44380133146](https://github.com/Barrot-Agent/B-Agent/actions/runs/44380133146): **4,275 passed, 1 skipped, 0 failed, 11 warnings, 19 subtests**, 148.32 seconds; inclusive coverage **68.14%**; legacy core-package coverage **77%**; installed wheel and packaged XRP mission verification passed.
- Its PR-event CI, dependency audit, money audit, and fail-closed gate also passed. The duplicate hunter test is now collected separately from the no-commit/no-push test.
- Current branch head at this addendum is `24a0beb98472462503f504b53ce9332bc92f48f6`; PR #1663 reports 317 commits ahead of current main and remains draft.
- The handoff-only head `24a0beb` has its own exact-head push CI [44380912807](https://github.com/Barrot-Agent/B-Agent/actions/runs/44380912807) still running the full-suite pipeline; dependency audit [44380912872](https://github.com/Barrot-Agent/B-Agent/actions/runs/44380912872) and PR dependency audit [44380925718](https://github.com/Barrot-Agent/B-Agent/actions/runs/44380925718) are pending at this addendum. Its PR CI [44380925720](https://github.com/Barrot-Agent/B-Agent/actions/runs/44380925720), money audit [44380925669](https://github.com/Barrot-Agent/B-Agent/actions/runs/44380925669), fail-closed PR gate [44380925721](https://github.com/Barrot-Agent/B-Agent/actions/runs/44380925721), push fail-closed gate [44380913257](https://github.com/Barrot-Agent/B-Agent/actions/runs/44380913257), and Pages validation job passed.
- No code changes were made after the `89ff4b0` full-suite pass; the remaining `24a0beb` verification is a documentation-only successor. Do not describe it as verified until its own full-suite and dependency-audit jobs complete.


---

## Run 24 — 2026-11-18T19:58:51Z (exact-head CI, workflow-risk scan, PR reconciliation, fresh market capture)

### Repository state — verified from GitHub

- Current `main`: `8e9b2516b5a103e9593124c05edf623e6c7817ff`.
- Sole consolidated V3/XRP integration PR: [#1663](https://github.com/Barrot-Agent/B-Agent/pull/1663), **open, draft, unmerged**.
- Integration branch: `integration/xrp-v3-mainline-successor-20261115T2101Z`.
- Current integration head: `4b96a1da7c32461f4e4016672964b94677a1c11b`.
- Main-to-head comparison: 318 commits ahead, zero behind, 1,428 changed files. Recursive trees are complete (main 1,737 entries; integration 2,979 entries); every main path exists in the integration tree.
- Repository metadata confirms push/admin permissions through the GitHub connector. This does not grant access to protected-branch administration endpoints.
- No branch or PR was created. No main write, merge, source-PR closure, force-push, history rewrite, or destructive worktree operation occurred.

### Exact-head CI — VERIFIED on `4b96a1d`

- [Push CI 44381174633](https://github.com/Barrot-Agent/B-Agent/actions/runs/44381174633): completed successfully. The **full repository test suite** job ran on this exact SHA and passed:
  - 4,275 passed; 1 skipped; 0 failed; 11 warnings; 19 subtests passed.
  - 150.25 seconds.
  - Inclusive coverage 68.14% (62% required floor); legacy core-package coverage 77%.
  - Wheel built; installed wheel loaded Barrot V3, the XRP mission and canonical data assets.
  - GitHub Pages validation-only job passed; it did not deploy.
- [Push dependency audit 44381175858](https://github.com/Barrot-Agent/B-Agent/actions/runs/44381175858): passed across runtime, development, supplemental integrations, Hugging Face Space, legacy and PEP 621 manifests.
- [Push fail-closed gate 44381174674](https://github.com/Barrot-Agent/B-Agent/actions/runs/44381174674): passed and explicitly kept merge disabled.
- [PR CI 44381191835](https://github.com/Barrot-Agent/B-Agent/actions/runs/44381191835): workflow completed successfully, but both core-test and full-suite jobs were **skipped because the PR is draft**. Do not represent this PR-event run as full-suite evidence.
- [PR dependency audit 44381191935](https://github.com/Barrot-Agent/B-Agent/actions/runs/44381191935), [money audit 44381191428](https://github.com/Barrot-Agent/B-Agent/actions/runs/44381191428), and [PR fail-closed gate 44381191723](https://github.com/Barrot-Agent/B-Agent/actions/runs/44381191723): passed.
- Non-blocking warnings remain: exhausted/read-only GitHub Actions cache budget; setuptools deprecation for `project.license`; package-discovery warnings for `barrot_agent.data.missions` and `data.research`. The wheel's mission resource was nevertheless verified in the built and installed wheel.

### Workflow and external-action review — first-pass static scan of all 67 changed workflow files

The integration changes 67 of the repository's 85 workflow definitions. A first-pass scan checked triggers, permissions, secret references, checkout credential persistence, action pins, shell execution, write permissions, deployment commands and dispatch gates. Targeted semantic review covered the following high-impact paths. This is **not yet a complete transitive audit of every invoked script, downloaded artifact and third-party action**.

- Integration `.github/workflows/paid-issue-publish.yml`: now a no-op with `permissions: {}` and job condition `if: false`; no checkout, artifact download, commit or push.
- Integration `.github/workflows/paid-issue-hunter.yml`: scheduled/manual read-only collection; `contents: read`, `issues: read`, checkout with `persist-credentials: false`, artifact output only.
- Main still has the old active publisher at `.github/workflows/paid-issue-publish.yml`: `contents: write`, checkout with persisted credentials, copies the hunter artifact, commits and runs `git push origin main`. Main SHA `8e9b2516` is that publisher commit. [Run 44369074831](https://github.com/Barrot-Agent/B-Agent/actions/runs/44369074831) succeeded and triggered GitHub Pages publication [44369186191](https://github.com/Barrot-Agent/B-Agent/actions/runs/44369186191). This is a verified external publication side effect.
- Integration `.github/workflows/xrp-public-ingestion.yml`: scheduled hourly and daily; exact triggering-commit checkout; `actions: read`, `contents: read`; checkout credentials disabled; public-source collection and artifact/cache outputs only. Raw receipts and cross-run index are GitHub artifacts with 90-day retention; the per-run feature-store checkpoint is 7 days. The code explicitly says these artifacts are **not WORM storage** and that GitHub run identity is not an independent per-source timestamp authority. The workflow was not executed in this run; the latest head changed only the handoff, not its ingestion trigger paths.
- Integration `.github/workflows/coinbase-paper-trader.yml`: manual dispatch only; typed `YES`, exact full main SHA, read-only contents permission, checkout credentials disabled; script uses public Coinbase ticker/trade data, no Coinbase API key, and simulated state is artifact-only. It was not dispatched.
- `barrot-ops.yml`, `barrot-merge.yml`, `barrot-restart-space.yml`, `deploy-a2a-worker.yml` and `deploy-databricks.yml` are manual external-operation paths with explicit typed confirmations and exact-main-SHA checks. Databricks workspace import and Kaggle dataset download have separate confirmations; Hugging Face model upload, Space restart, Cloudflare deployment and secret rotation were not executed.
- `deploy-a2a-worker.yml` requires both deployment confirmation and a separate secret-rotation confirmation. No secret was rotated.
- `release.yml` is tag-triggered for `v*.*.*` and grants `contents: write`; no tag was created and no release was made.
- `money-mcp-listing.yml` is a preflight-only workflow. Its output describes OIDC publishing prerequisites; the workflow does not grant `id-token: write` or publish.
- `pillars-check.yml` is scheduled/manual and uses read-only probes: GitHub App installation GET, Databricks SQL `SELECT 1`, Hugging Face Space runtime GET and GitHub source-marker GET. The Databricks SQL API uses HTTP POST as its statement-submission transport, but the submitted statement is `SELECT 1`; no workspace import/job mutation is present in this check.
- Push-triggered CI, dependency audit, money audit and SINDy checks are read/test paths; the hover-bike workflow uploads artifacts. No manual deployment, Space restart, Databricks write, Kaggle submission, Hugging Face upload, release creation or paper-trader dispatch occurred.

### Governance — merge remains blocked

- Main branch API reports `protected: true`, but visible required status-check contexts/checks are empty and enforcement is only reported for non-admins.
- Detailed branch-protection endpoint returns 403 (`Resource not accessible by integration`).
- The only visible repository ruleset is `Fall Back`, ID `10863829`, enforcement **disabled**.
- `.github/CODEOWNERS` assigns all paths only to `@Barrot-Agent`.
- PR #1663 has zero submitted reviews, no requested reviewers and no independent approving review. CodeRabbit explicitly reports that the draft PR was not reviewed.
- A merge to main would trigger the existing Pages publication path. The current main publisher remains active until the integration successor reaches main. Do not merge or bypass checks while the publication side effect and independent governance remain unresolved.

### Open PR inventory — 12 open; no bulk cleanup

Exact changed-file inventories were refreshed. The integration branch remains the sole consolidated V3/XRP workstream.

| PR | Classification | Verified overlap / ancestry |
|---|---|---|
| #1663 | **blocked — sole integration** | Draft; 318 ahead, 0 behind; exact-head full suite and dependency/security audits passed, but governance and publication blockers remain. |
| #1664 | **unique/unreviewed — partial overlap** | Three shared paths with integration: `BARROT_SYNC.md`, `MEMORY.md`, `README.md`; all three blob hashes differ. Separate paid-issue product pack and research; preserve. |
| #1665 | **blocked — dependency reconciliation** | `requirements-dev.txt` differs from integration; stale base. |
| #1666 | **blocked — dependency reconciliation** | `pyproject.toml` differs from integration; `requirements-integrations.txt` is unique to the PR. |
| #1541 | **blocked — MMI reconciliation** | Three shared paths: `barrot_agent/mmi_adapter.py` is byte-identical; `barrot_agent/mmi_v1.py` and the canonical-fingerprint operation record differ. Two test paths are unique to the PR. |
| #1265 | **blocked — stacked ledger migration** | `.github/workflows/ci.yml` differs from integration. Its branch is the parent of #1353. |
| #1353 | **unique/unreviewed — ledger archive** | 1,084 changed files; parent of #1436 and #1437. |
| #1436 | **unique/unreviewed — Binance research** | Stacked on #1353; parent of #1440 and #1450. |
| #1437 | **unique/unreviewed — source-addenda repair** | Sibling branch stacked on #1353. |
| #1440 | **unique/unreviewed — archive validation repair** | Stacked on #1436. |
| #1450 | **unique/unreviewed — Binance research successor** | Stacked on #1436; parent of #1460. |
| #1460 | **unique/unreviewed — institutional multirail/Kamilah research** | Stacked on #1450. |

Totals: 5 blocked, 7 unique/unreviewed, 0 ready, 0 confirmed duplicate, 0 superseded. No source PR was closed.

### Fresh XRP market capture — 19:58 UTC

Direct Kraken public ticker response at retrieval time (the response contains no exchange event timestamp):

- Last trade: **$0.96805**.
- Best bid **$0.96752** (350 XRP); best ask **$0.96758** (347 XRP).
- Spread **$0.00006**, approximately **0.62 bps** at the midpoint.
- 24-hour volume **50.6045M XRP**; VWAP **$0.98242713**; high/low **$1.00677 / $0.96061**; open **$0.98253**.
- Last trade is approximately 1.46% below 24-hour VWAP, 1.47% below the 24-hour open and 0.77% above the 24-hour low. This is one venue's ticker, not consolidated market depth. Kraken Level 2 was not retrieved in this run.

Source: [Kraken public XRP/USD ticker](https://api.kraken.com/0/public/Ticker?pair=XRPUSD).

### Derivatives and flow disagreement — preserve, do not average

- TradRadar at 16:05 UTC: seven-venue OI **$1.32B**, +1.94%/24h; OI-weighted funding **−0.0039%/8h**; reported liquidations at least **$4.66M** (shorts $3.07M, longs $1.58M); account long/short ratio 3.30. [Source](https://tradradar.io/markets/xrp).
- Liqwall at 19:32 UTC: OI **$942M**, −2.4%/24h; cross-exchange average funding **+0.0009%/8h**, while Binance funding was **−0.0020%/8h**; 24-hour liquidations **$5.5M** (shorts $3.3M, longs $2.2M); 74.8% of Binance accounts with XRP positions were long. Its Hyperliquid map showed $2.6M of long liquidations within 10% below price and $1.2M of short liquidations within 10% above. [Source](https://liqwall.com/coins/xrp).
- TokenPost's 18 Nov 05:10 ET report described Binance-related net outflows above $127M since Nov 10, OI falling from about $1.05B on Nov 9 to roughly $752M in its latest reading, and $19.1M XRP ETF outflows Nov 9–13. It also notes that exchange withdrawals may reflect Binance reserve-management transfers after October's hack, not investor accumulation. [Source](https://www.tokenpost.com/news/investing/60299).
- CMC AI's 18 Nov 07:22 UTC article framed the recent ~3.1% move as a technical relief bounce after a ten-session selloff, citing roughly $43M long liquidations, falling OI, ETF outflows and RSI near 16. It is an AI-generated synthesis of secondary references, not an independent market-data source. [Source](https://coinmarketcap.com/top-stories/6afd52371bf1a972fe2d59cf/).

These providers differ in capture time, venue universe, aggregation and underlying source methodology. OI totals, funding and liquidation estimates are not interchangeable. Binance exchange-wallet withdrawals are not automatically investor outflows or retained cold storage. None of these secondary observations is admitted as a directional feature in this run.

### Institutional rail update

- Ripple's 27 Oct announcement says BNY supports XRP and RLUSD on its Digital Asset Custody platform; BNY is RLUSD's primary reserve custodian and has a Ripple Prime custody relationship. BNY and Ripple intend to explore tokenized trade finance and direct RLUSD mint/redemption through BNY; this is custody/infrastructure evidence, not proof of XRP purchases or production XRP settlement volume. [Ripple primary release](https://ripple.com/ripple-press/ripple-expands-collaboration-with-bny-across-custody-and-tokenized-trade-finance/).
- Ripple's 28 Oct Coinbase announcement confirms RLUSD access through Coinbase Prime, Exchange and Retail, with XRPL, Base and Ethereum support. Coinbase Global Exchange availability and RLUSD collateral use were stated as future, not live at launch. [Ripple primary release](https://ripple.com/ripple-press/ripple-and-coinbase-partner-to-expand-access-to-rlusd/).
- Reuters reports DBS and Circle announced a partnership on 18 Nov to expand institutional USDC access in Asia. This is a competing/parallel stablecoin distribution rail; the report does not establish an XRP connection or specific production volumes. [Reuters](https://www.reuters.com/world/asia-pacific/dbs-partners-with-circle-expand-institutional-access-usdc-asia-2026-11-18/).

### Prediction and nine-platform status

- **Forecast: NOT_ISSUED.** No directional probability is supported by this run. The Kraken ticker is a single-vantage observation; derivatives and exchange-flow providers disagree; full depth, reconciled issuer ETF flows, receipt-complete point-in-time features, independent WORM/timestamp anchoring, leakage-safe out-of-sample calibration and independently attested shadow outcomes remain insufficient.
- The XRP ingestion implementation exists on the integration branch but was not executed in this run. Its last recorded receipt/failure counts remain 34 receipts (22 raw, 12 digest-only) and 21 source failures; these are stale until a new ingestion run completes.
- The collector's internal SHA-256 receipts and hash chain are implemented, but the code explicitly sets independent per-source timestamp anchoring to false and rejects the claim that GitHub Actions artifacts are WORM storage.
- Only the ChatGPT-to-GitHub connector path was exercised. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks were not authenticated or dispatched. No nine-platform quorum is claimed.
- No new SBIC/ASK Coin/“actual capital”/Camilla–Kamilah identity bridge was verified in this run; existing disambiguation and identity quarantine remain in force.

### DESIGNED / EXECUTED / VERIFIED

- **DESIGNED:** scheduled public XRP capture, content-addressed receipts, point-in-time feature store, event timeline, scenario/counter-hypothesis records, baseline walk-forward evaluation, drift report and forecast lock.
- **EXECUTED:** GitHub repository/PR/tree/CI/security reads; exact-head full-suite and dependency checks; 67-workflow first-pass scan plus targeted workflow/script review; PR overlap and blob-hash reconciliation; fresh Kraken ticker and secondary market/institutional source review.
- **VERIFIED:** exact-head `4b96a1d` full suite, wheel, dependency audit, money audit and fail-closed gates; no merge or external write.
- **NOT VERIFIED:** independent review, effective required-check enforcement, full transitive workflow/action/script supply-chain audit, independent WORM/time anchor, new ingestion run, model outperformance, calibrated forecast or shadow evaluation.

### Next concrete action

Keep PR #1663 draft. Resolve the automatic Pages publication path and obtain independently enforceable branch protection/review before considering a merge. Finish the transitive workflow/action/script audit, especially existing main-branch automatic publishers and all manual deployment workflows. Then re-run full-suite, dependency/security and fail-closed checks on the exact resulting head. Separately, execute the public XRP ingestion workflow only through an authorized read-only path and add an independent timestamp/immutability anchor before any forecast is considered.


### Run 24 source addendum — ETF-vintage reconciliation and DBS primary confirmation

- DBS published a first-party announcement on **18 Nov 2026** confirming that eligible institutional clients can mint and redeem USDC directly through DBS, with 24/7 USD–USDC settlement. DBS and Circle connect this to their participation in MAS Project BLOOM. The announcement does not identify XRP, XRPL or Ripple as a settlement component. Treat it as a new Asia institutional USDC distribution/liquidity node and a competing or parallel stablecoin rail, not XRP demand. [DBS primary release](https://www.dbs.com/newsroom/DBS_and_Circle_expand_institutional_access_to_USDC_in_Asia).
- XRP Insights' live tracker, retrieved on 18 Nov, reports 6 US spot XRP ETFs plus BITW at **1,189.15M XRP** and **$779.55M AUM**. Its issuer-holdings-derived daily table reports **+986 XRP on Nov 17**, **+158.1K XRP on Nov 16**, and **−6.08M XRP for Nov 9–13**. It explicitly excludes GXRP from flow totals while its data gap is corrected, but still includes GXRP holdings in the aggregate. Its flow methodology is change in issuer-reported XRP holdings, not dollar-flow estimates. [XRP Insights tracker](https://xrp-insights.com/).
- This sharpens the existing Nov 17 disagreement: XRP Insights reports +986 XRP; CryptoKeyhole's partial capture reported −3,251 XRP from only 2 of 4 tracked files; ByKaranteli reported a provisional −$6.1M across five funds. TokenPost separately described $19.1M outflows for Nov 9–13, while XRP Insights' stated 6-spot-plus-BITW universe shows −6.08M XRP (about $6.64M at its own estimate). These are not interchangeable: fund universe, units, GXRP gap, price conversion and reporting completeness differ. Keep each provider vintage and methodology separate; no blended ETF flow feature is admitted.
- XRP Insights reports total holdings near 1.19B XRP on Nov 13 and Nov 17 while AUM fell from about $1.22B to $778.2M. Because holdings are rounded and the fund universe has a GXRP flow gap, this is only a descriptive indication that AUM repricing may explain a substantial portion of the dollar decline; it is not proof of zero redemptions.
- No independent primary Binance wallet-flow ledger was found in this addendum. The $127M Binance-related net-outflow figure remains a secondary report and must not be interpreted as investor accumulation, cold storage or net exchange supply without address attribution and reserve-transfer controls.

All new ETF and DBS observations remain research-only until raw source capture, exact issuer-vintage reconciliation, hash receipts and point-in-time known-at timestamps are independently verified.


### Run 24 research addendum — definitive Japan SBIC resolution; Kamilah identity controls

#### Japan's SBIC is three regional investment companies, not SBI Holdings

The official Japanese `中小企業投資育成株式会社法` page reproduces **Act No. 101 of 1963**, enacted 10 June 1963. Article 1 defines the purpose as strengthening SME equity and supporting healthy business growth. Article 2 names exactly three companies and their respective headquarters: Tokyo Small and Medium Business Investment & Consultation Co., Ltd.; Nagoya Small and Medium Business Investment & Consultation Co., Ltd.; and Osaka Small and Medium Business Investment & Consultation Co., Ltd. Article 10 places them under the law's ministerial supervisory framework. [Act text and Articles 1–2, 10](https://www.sbic-wj.co.jp/disclose/law/).

Their own official profiles confirm the regional names and identities:

- **SBIC East Japan** — Tokyo Small and Medium Business Investment & Consultation Co., Ltd.; corporate number 9011001030621; established 15 Nov 1963; capital ¥6.6734B; shareholder categories include 18 prefectural/local governments, chambers of commerce, financial institutions and operating companies; coverage extends east from Shizuoka, Nagano and Niigata. [Tokyo official profile](https://www.sbic.co.jp/company/profile/).
- **SBIC Central Japan** — Nagoya Small and Medium Business Investment & Consultation Co., Ltd.; established 18 Nov 1963; capital ¥4.3008B; coverage Aichi, Gifu, Mie, Toyama and Ishikawa. [Nagoya official profile](https://www.sbic-cj.co.jp/company/about/).
- **SBIC West Japan** — Osaka Small and Medium Business Investment & Consultation Co., Ltd.; established 20 Nov 1963; capital ¥6.822B; 84 employees; coverage 24 prefectures west of Fukui, Shiga, Nara and Wakayama. [Osaka official profile](https://www.sbic-wj.co.jp/profiles/profile/).

Each official profile identifies the other two as sister companies. Thus **East/Central/West are three separate Japanese SME investment-and-consultation corporations**, not divisions of one SBI Holdings subsidiary and not a crypto exchange, XRP fund or Ripple entity.

**Do not conflate these with SBI Holdings, Inc.** SBI Holdings' official profile says it was established 8 July 1999 and its principal business is control/management of the SBI Group through share ownership. Its official group-company list (as of 7 Oct 2026) names entities such as SBI Shinsei Corporate Investment, SBI Regional Business Investment, SBI VC Trade and SBI Ripple Asia; it does not list the three Tokyo/Nagoya/Osaka SBIC corporations. [SBI Holdings corporate profile](https://www.sbigroup.co.jp/english/company/information/profile.html) · [SBI Group companies](https://www.sbigroup.co.jp/english/company/group/overview.html). No ownership or operating link between the three regional SBICs and SBI Holdings was established by the reviewed primary records. Keep the legal entities separate in the relationship graph. The U.S. SBA Small Business Investment Company program is another acronym collision, not the Japanese three-company system.

The regional SBICs' stated mandate is SME equity investment and growth support. No direct XRP, Ripple, RLUSD, Coinbase or Circle investment/use relationship was established in this research.

#### Exact-phrase research and false-positive controls

- Exact search for **"SBIC, ChatGPT SBIC"** produced no verifiable primary-source entity, product or transaction. Status: unresolved; do not create an entity node from the phrase alone.
- Exact search for **"actual capital"** in the XRP/SBI context produced no verified primary-source transaction or named program. Do not treat generic "actual capital deployment" wording or the podcast phrase "real assets actually moving" as the same evidence.
- Exact search for **"ASK Coin"** produced no verified XRP/Ripple/SBI connection. Keep the string unresolved rather than assigning a ticker or project based on acronym collision.

#### Kamilah/Camilla Stevenson — one verified public appearance; channel ownership quarantined

The iHeart episode is titled **“Crypto Panics! with Dr. Kamilah Stevenson”** and the guest's closing remarks self-report X as `cam i am cam Stevenson`, Instagram as `Kamilla Stevenson`, and YouTube as `doctor Camilla Stevenson`; she explicitly warns that fake pages exist. The transcript is automatically rendered and contains spelling/transcription variants, so preserve the alias spellings rather than silently normalizing them. [iHeart episode and transcript, especially 40:07–40:26](https://www.iheart.com/podcast/1333-the-xrp-podcast-with-paul-284128923/episode/crypto-panics-with-dr-kamilah-stevenson-336576069/).

One public YouTube **guest appearance** is verified: **“Crypto Panics! W/ @drkamilahstevenson”**, published 11 June 2026 by the Paul Barron Podcast. This is a host-channel interview featuring the guest, not proof that the host channel is owned by her. [YouTube appearance](https://www.youtube.com/watch?v=Sulo54IlQ60).

Do not inventory videos from `@drkamilahstevenson`, `@KamilahStevensonXrpStocks`, `@drkamilahstevenson-j9r` or other lookalike channels as hers until a first-party cross-link from the self-reported X/Instagram identities or another authoritative source establishes ownership. A similarly named 2015 health video also lacks an identity bridge and remains excluded.

The interview discusses a claimed 10 June 2026 SBI Shinsei pilot converting part of deposit interest into BTC/ETH/XRP. That specific pilot was **not confirmed by the first-party SBI material retrieved**. The official SBI Shinsei/SBI VC Trade material verified here is a separate retail campaign: deposits of at least ¥300,000 in a six-month yen term deposit, campaign entry 2 Feb–31 Mar 2026, with ¥500–¥20,000 XRP exchange vouchers redeemable through SBI VC Trade; the bank's page now marks it ended. [SBI Shinsei primary campaign page](https://www.sbishinseibank.co.jp/campaign/cam_2602_xrp_trade/) · [SBI Holdings primary announcement](https://www.sbigroup.co.jp/news/pr/2026/0202_16075.html). The separate official 10 June “Triple Yen Deposit” campaign was a cash-interest promotion, not an XRP conversion program. [SBI Holdings/SBI Shinsei announcement](https://www.sbigroup.co.jp/news/pr/2026/0611_16393.html). Keep the podcast's 10 June pilot statement as an unverified claim until an actual first-party pilot notice or terms are located.

#### Exact-head verification closeout for the preceding handoff head

- Integration head `4ac706da9aa272d6c2a29a5e900d89e083bcd755` completed exact-head push CI successfully: [44387968038](https://github.com/Barrot-Agent/B-Agent/actions/runs/44387968038).
- Full repository suite: **4,275 passed, 1 skipped, 0 failed, 11 warnings, 19 subtests passed**, 191.73 seconds; inclusive coverage **68.14%** and legacy core coverage **77%**.
- Wheel build and installed-wheel verification passed; installed wheel loaded Barrot V3, the XRP mission and canonical assets.
- [Dependency audit 44387968010](https://github.com/Barrot-Agent/B-Agent/actions/runs/44387968010), [fail-closed push gate 44387967950](https://github.com/Barrot-Agent/B-Agent/actions/runs/44387967950), [PR dependency audit 44387977832](https://github.com/Barrot-Agent/B-Agent/actions/runs/44387977832), [PR money audit 44387977751](https://github.com/Barrot-Agent/B-Agent/actions/runs/44387977751), and [PR fail-closed gate 44387979830](https://github.com/Barrot-Agent/B-Agent/actions/runs/44387979830) passed.
- PR event CI [44387977757](https://github.com/Barrot-Agent/B-Agent/actions/runs/44387977757) passed its Pages validation, but the core-test and full-suite jobs were skipped because the PR remains draft. The exact-head push run above is the full-suite evidence.
- The only warnings are the 11 legacy tests returning booleans rather than `None`, setuptools' `project.license` deprecation, two package-discovery warnings, and the Actions cache-budget/read-only warning. No test failed.




---

## Run 25 — current market, ingestion receipts, exact-head CI and workflow side-effect audit

**Capture:** 2026-11-18T20:27:45.971Z  
**Code/test head:** `0f981f5c1499cfe3c2f1c1d2d855bb82a7cb865f`  
**Research record:** [Run 25 JSON](research/xrp_intelligence/20261118T202745Z-run25-market-ingestion-ci-security-reconciliation.json)  
**Research record commit:** `a4186aa70fa0b3685c74a9018c3152d7a4be835d`

### 1. Repository and integration state

- Main remains `8e9b2516b5a103e9593124c05edf623e6c7817ff`.
- PR #1663 is draft, mergeable/clean, 321 commits ahead and zero behind current main.
- The PR changes 1,428 files (+514,517 / −6,596). The complete main tree has 1,737 entries; the integration tree has 2,979. No main-tree path is missing from the integration tree.
- No new branch or PR was created. No PR was merged or closed. Main was not modified.
- The remote branch was not force-pushed or rewritten. GitHub API access cannot reveal an operator's local dirty worktree state; no local worktree mutation was attempted.

### 2. Exact-head CI and main CI

**Verified on code/test head `0f981f5`:**

- [Push CI 44389147449](https://github.com/Barrot-Agent/B-Agent/actions/runs/44389147449): full repository suite **4,275 passed, 1 skipped, 0 failed**, 11 warnings and 19 subtests passed in 108.43 seconds.
- Inclusive coverage 68.14%; legacy-core coverage 77%.
- Wheel build and installed-wheel verification passed; the installed wheel loaded Barrot V3 and the XRP mission.
- [Push dependency audit 44389147714](https://github.com/Barrot-Agent/B-Agent/actions/runs/44389147714), [push fail-closed gate 44389147601](https://github.com/Barrot-Agent/B-Agent/actions/runs/44389147601), [PR dependency audit 44389162468](https://github.com/Barrot-Agent/B-Agent/actions/runs/44389162468), [PR fail-closed gate 44389162453](https://github.com/Barrot-Agent/B-Agent/actions/runs/44389162453) and [PR money audit 44389162562](https://github.com/Barrot-Agent/B-Agent/actions/runs/44389162562) passed.
- PR event CI [44389162423](https://github.com/Barrot-Agent/B-Agent/actions/runs/44389162423) passed, but PR test jobs skip the full suite while #1663 is draft. The exact-head push run supplies the full-suite evidence.
- **The Run 25 research JSON commit and this handoff update are documentation commits after `0f981f5`; their resulting head still requires its own exact-head CI.** Do not transfer the preceding test result to a later SHA.

**Main:**

- Latest Cross Analysis [44384808541](https://github.com/Barrot-Agent/B-Agent/actions/runs/44384808541) succeeded.
- Pillars Consistency Check [44309596554](https://github.com/Barrot-Agent/B-Agent/actions/runs/44309596554) failed because GitHub App credentials were absent, Databricks returned HTTP 403 and the Hugging Face Space build returned BUILD_ERROR.
- A full repository suite on current main SHA `8e9b251` was not observed in this audit.

### 3. Workflow and publication safety

- Static review covered **67/67 changed workflow YAML files**. Every observed `uses:` action reference was pinned to a full commit SHA.
- Static YAML review is not a complete transitive review of every invoked script, artifact producer/consumer or third-party action behavior; that work remains incomplete.
- Main's [Paid issue publish run 44369074831](https://github.com/Barrot-Agent/B-Agent/actions/runs/44369074831) executed a publisher with `contents: write` and `git push origin main`. The resulting main push was followed by [Pages build and deployment 44369186191](https://github.com/Barrot-Agent/B-Agent/actions/runs/44369186191), which succeeded.
- The integration branch replaces that publisher with a disabled job (`if: false`, `permissions: {}`). This does not remove the observed Pages deployment side effect of pushing to main.
- The release workflow remains tag-triggered (`v*.*.*`) with `contents: write`; no tag or release was created.
- Databricks, Cloudflare/A2A, Hugging Face, Space restart, Kaggle and paper-trader workflows are manual and contain varying explicit confirmation/exact-SHA gates. None was dispatched. The Databricks bundle and two Hugging Face sync paths remain quarantined.
- Branch-protection details returned 403. The visible ruleset ID 10863829 reports enforcement disabled. CODEOWNERS remains `* @Barrot-Agent`; no independent review was recorded.
- **Merge remains blocked.** The PR is draft, independent approval is absent, branch-protection enforcement cannot be verified, the transitive security review is incomplete, and a main push has a demonstrated Pages deployment side effect for which no specific authorization exists.

### 4. Latest executed public-data ingestion

[Read-only XRP ingestion run 44301868145](https://github.com/Barrot-Agent/B-Agent/actions/runs/44301868145) ran at 12:13 UTC on `38b910e7`. Its workflow, XRP ingestion, SEC, feature-store and forecast-ledger blob SHAs match the current integration code/test head `0f981f5`.

**Receipt and storage evidence:**

- 34 source receipts; 22 retained raw payloads; 12 digest-only receipts.
- Receipt-chain verification PASS; cross-run continuity CONTINUED, sequence 15.
- Raw artifact [14426941429](https://github.com/Barrot-Agent/B-Agent/actions/runs/44301868145/artifacts/14426941429): SHA-256 `c9ec648228d5c76136fd68f8d7b0f2b71ea2eb97eebf8b2f8617b9678098b2be`; 462,640 bytes; 90-day retention.
- Chain head `5d3d4cae7846c0835c2319776c24e864ed9b0245e03012bd363edaae3544c597`; cross-run chain `879adcc5b6cf7f1cc1c3f6e8ff93d38e382a2f686b11a8868fbdb5f8f415331a`.
- External anchor remains NOT_ANCHORED. GitHub artifacts are retention-limited, not WORM or a trusted timestamp authority.
- SQLite feature history: 3,235 records across 15 snapshots; 485 delta records; 2,230 input records; 124 eligible and 361 excluded feature records.
- Raw-to-feature reconstruction from retained raw artifacts remains unimplemented. The feature store restored from a prior per-run checkpoint; per-run feature checkpoints retain for seven days, raw artifacts for 90 days. GitHub Actions cache storage is exhausted/read-only and is derived rather than authoritative.

**Source failures and exclusions:**

- 21 failures: eight Binance HTTP 451, five Bybit HTTP 403, six SEC EDGAR user-agent configuration failures, one Grayscale 429 and one Franklin XRPZ issuer-page parser failure.
- The run has eligible spot ticker and order-book snapshots from Coinbase, Kraken, Bitstamp, Bitbank and OKX. These are snapshots, not continuous order-flow reconstruction; no WebSocket sequence bridge is maintained.
- Binance endpoints were unavailable with HTTP 451. Bybit returned HTTP 403; the provider documentation notes U.S./Mainland China IP restrictions, while runner geography is unverified. Do not proxy or bypass the restriction. The Bybit depth parser is implemented with matching-engine `cts` timestamps and 10/50/100 bps depth bands, but no Bybit receipt was captured.
- Deribit XRP-USDC perpetual ticker and order book remain raw-only pending contract-unit, depth and sequence validation.
- ETF issuer/aggregator records are raw-only or digest-only pending fund-row vintages, issuer receipts and primary cash-flow reconciliation. Exchange-wallet balances are hash-only pending same-wallet daily-snapshot and attribution validation.
- RLUSD and USDC transparency pages are raw-only pending supply/reserve normalization. SBI lending is digest-only; actual lending balances are not disclosed. Morpho CBXRP market parameters, state, liquidity and oracle data remain raw-only pending unit, decimal, lineage and block-time reconciliation.
- SEC submissions/companyfacts captured: 0. `BARROT_SEC_USER_AGENT` is blocked until a monitored project contact is approved and configured; do not infer or invent a contact identity.
- CFTC weekly source families captured: 0 of 2. XRPL node reconciliation was not collected because the available free non-commercial nodes are excluded from scheduled use under provider terms.

**Verified quote-basis control:**

- The run normalized OKX XRP-USDT with same-venue USDT-USD using source timestamps 0.657 seconds apart; maximum component age was 9.53 seconds.
- Normalized mid was $0.983922118 and spread 1.1153 bps. Only top-of-book prices were normalized. Both receipts belong to the same OKX publisher group; this is not independent corroboration or normalized depth.

**Prediction gate:**

- `forecast_status=NOT_ISSUED`; zero walk-forward forecasts; model eligibility false.
- Walk-forward status PARTIAL_OR_BLOCKED.
- Drift evaluated zero features because there are no reference-window samples; drift status INSUFFICIENT_DATA.
- Event timeline is not model-eligible. No directional forecast is justified.

### 5. Fresh market and ecosystem observations — research only

**Kraken XRP/USD retrieval, 2026-11-18 20:26:42 UTC:**

- Last $0.96805; bid $0.96752 (350 XRP); ask $0.96758 (347 XRP); spread 0.6201 bps.
- 24-hour volume 50.6045M XRP; VWAP $0.98242713; high $1.00677; low $0.96061; open $0.98253.
- Last was 1.47% below the 24-hour VWAP. Kraken returned no exchange event timestamp; this is retrieval-time context and is not admitted as a model feature.
- Raw response SHA-256: `79183bfe9dcc8cd704be70f56c128b1fc471e90ad7af3d866a3c29a22c108953`.

**OKX XRP/USDT retrieval, 2026-11-18 20:27:45.971 UTC:**

- Last 0.9665 USDT; bid 0.9665; ask 0.9666; top bid size 2,483.743 XRP; top ask size 984.544 XRP; spread 1.0346 bps.
- 24-hour volume 32.0533M XRP; high 1.0079 USDT; low 0.9631 USDT.
- The USDT-USD leg was timestamped 19 minutes 31.31 seconds earlier. USD normalization was rejected because it exceeded the 60-second synchronization limit. Keep this quote in USDT; do not assume a 1:1 peg.
- These two exchange observations are not synchronized and use different quote currencies. Do not infer cross-venue arbitrage or directional pressure from them.

**Derivatives disagreement:**

- Liqwall at 05:22 UTC: $958M open interest, −2.1% over 24 hours.
- TradRadar at 16:05 UTC: $1.32B open interest, +1.94% over 24 hours; OI-weighted funding −0.0039% per 8h; at least $4.66M liquidations; 3.07M shorts and 1.58M longs liquidated; account long/short ratio 3.30.
- Different observation times and venue/contract universes. Keep publisher records separate; do not average.

**ETF-flow disagreement for Nov 17:**

- CryptoKeyhole: −3,251 XRP, only two of four funds reported; latest complete day Nov 13 was −9,967 XRP.
- XRP Insights: +986 XRP across six spot funds plus BITW; approximately 1.19B XRP holdings and $778.24M AUM, with GXRP excluded from flow totals while its data gap is corrected.
- CryptoTuts/SoSoValue: five-fund universe, $1.08B AUM and −$7.23M over seven days.
- Fund universes, issuer vintages and flow units differ. No blended ETF-flow feature is admitted.

**Institutional and regulatory evidence:**

- BNY's Oct 27, 2026 primary release says BNY supports XRP and RLUSD on its Digital Asset Custody platform, is RLUSD's primary reserve custodian and has a Ripple Prime custody relationship. Future RLUSD mint/redeem is subject to final BNY and regulatory approvals; tokenized trade finance with C2FO is exploratory. This proves infrastructure/custody relationships, not XRP purchases, collateral use or XRP-denominated settlement volume. [BNY primary release](https://www.bny.com/corporate/global/en/about-us/newsroom/press-release/ripple-expands-strategic-digital-assets-collaboration-with-bny-across-custody-and-tokenized-trade-finance.html)
- The SEC's March 17, 2026 interpretive release, effective March 23, includes CFTC guidance on certain crypto assets and transactions; it is not a standalone XRP-specific ruling. [SEC primary record](https://www.sec.gov/rules-regulations/2026/03/s7-2026-09)

### 6. Research continuity and coordination

- Run 24's primary-source SBIC resolution remains: SBIC East/Central/West are three distinct regional Japanese SME investment-and-consultation corporations, not SBI Holdings. No direct XRP relationship was established.
- Exact phrases ASK Coin, “actual capital” and “SBIC, ChatGPT SBIC” remain unresolved; no entity or transaction node should be invented.
- Kamilah/Camilla Stevenson identity controls remain: one verified guest appearance; no ownership bridge for lookalike YouTube channels.
- Only ChatGPT-to-GitHub access is verified. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks remain unverified for authenticated data flow. No independent dispatch or red-team quorum exists.

### 7. Open PR backlog

Twelve PRs remain open; no bulk closure:

- **Blocked:** #1663 (draft integration, governance and deployment side-effect blockers); #1665 and #1666 (dependency updates based on stale main SHA); #1541 (all five paths overlap #1663, two blobs identical and three divergent).
- **Unique/unreviewed:** #1664 (121 files, 118 unique and three overlaps; includes paper-trading/XRP batch scripts); #1460; #1450; #1440; #1437; #1436; #1353; #1265.
- #1663 remains the only consolidated Barrot V3/XRP integration workstream. Do not create another integration PR. Do not close unique research or ledger work.

### 8. Next concrete actions

1. Obtain independently verifiable branch-protection and code-owner approval evidence; keep #1663 draft until governance gates are real.
2. Resolve the automatic Pages publication side effect or obtain the specific deployment authorization before any merge.
3. Complete transitive workflow/script/artifact review; keep manual deployment, Space restart, Kaggle, Databricks and paper-trading actions unexecuted.
4. Establish lawful alternative market coverage for Binance/Bybit gaps; do not bypass regional restrictions.
5. Configure SEC EDGAR only after an approved monitored project contact is supplied through repository settings.
6. Normalize issuer ETF holdings, exchange-wallet attribution, RLUSD/USDC supply, SBI lending and Morpho CBXRP collateral with source timestamps and units.
7. Add independent external anchoring and raw-to-feature reconstruction; preserve the existing receipt chain.
8. Expand chronological walk-forward cohorts, calibration and later shadow validation. Keep directional forecasts disabled until the readiness gate passes.

**Run 25 disposition: NO MERGE.** The objective remains a working integrated Barrot V3/XRP build with measured out-of-sample predictive performance, not a larger proposal queue.


---

## Run 26 — 2026-11-18T21:02:30Z

**Evidence cutoff:** 2026-11-18T21:02:30Z  
**Mission priority:** XRP intelligence and measured prediction-engine mastery remain the highest-priority Barrot mission.  
**Foundation:** Barrot V3 remains the execution, orchestration, safety, authorization and verification foundation.  
**Current main SHA:** `d5d22ac252f88637a490ed4c1598f8608b6cb786`  
**Integration branch:** `integration/xrp-v3-mainline-successor-20261115T2101Z`  
**Integration head at evidence capture:** `6b9c73ca3589f55afe70abfc2d3c687da16ac863`  
**Active integration PR:** [#1663 — Barrot V3 + XRP Intelligence, consolidated mainline successor](https://github.com/Barrot-Agent/B-Agent/pull/1663)  
**Run 26 market artifact:** `research/xrp_intelligence/20261118T210230Z-run26-market-spot-derivatives-etf-macro-reconciliation.json`  
**Disposition:** NO MERGE. No deployment, secret rotation, Space restart, Kaggle submission, Databricks write, Hugging Face upload, paper trade, funds transfer, real-money action or directional forecast.

### 1. DESIGNED / EXECUTED / VERIFIED

**DESIGNED**
- XRP remains the top Barrot mission; V3 is retained as the execution and safety foundation.
- Public market evidence remains separated by publisher, event time, capture time, venue universe, contract type, units and source-independence group.
- Forecast admission remains fail-closed until raw-source reconstruction, point-in-time quality, source independence and leakage-safe out-of-sample evaluation pass.

**EXECUTED**
- Re-fetched current main, complete recursive trees, open PR inventory, PR #1663, ancestry, overlapping paths, current CI/workflow runs, dependency audits, branch ruleset metadata, CODEOWNERS and the durable handoff.
- Main advanced to `d5d22ac252f88637a490ed4c1598f8608b6cb786` through a separate checkpoint commit containing `guard.py` and `2026-11-18.md`. The integration branch initially lacked those two paths.
- Reconciled current main into the existing integration branch with two-parent merge commit `dbc6b327a56dc66493fb06cc32164a2043509280`, using a non-force ref update with an expected prior head. The merge commit parents are the prior integration head `edc3300717b9c77479e2acd9de30b0a9bac2f24c` and main `d5d22ac252f88637a490ed4c1598f8608b6cb786`. Both main-only files were copied by exact blob SHA; no main file was overwritten.
- Added the Run 26 market/derivatives/ETF/macro evidence artifact on the existing integration branch. No branch or PR was created.
- Updated the nine-platform map and this handoff together in one subsequent branch commit. The branch head recorded above is the pre-documentation-update evidence head; the resulting documentation commit requires its own exact-head CI.

**VERIFIED**
- Current main tree: 1,739 entries. Integration tree at evidence capture: 2,983 entries. No main paths were missing from integration.
- PR #1663: 328 commits ahead, zero behind, 1,430 changed files, 67 changed workflow definitions; still draft, mergeable, with zero formal reviews and zero requested reviewers.
- Current main full-suite CI on exact SHA `d5d22ac252f88637a490ed4c1598f8608b6cb786`: [run 44396364281](https://github.com/Barrot-Agent/B-Agent/actions/runs/44396364281) — 1,207 passed, 2 skipped, 8 subtests passed, 78.10% coverage.
- Previous integration code/test head `edc3300717b9c77479e2acd9de30b0a9bac2f24c`: [push CI run 44394535095](https://github.com/Barrot-Agent/B-Agent/actions/runs/44394535095) — 4,277 passed, 1 skipped, 0 failed, 11 warnings, 19 subtests passed, 157.85 seconds; inclusive coverage 68.14%, legacy-core coverage 77%; wheel built and installed Barrot V3/XRP mission verification passed.
- On evidence head `6b9c73ca3589f55afe70abfc2d3c687da16ac863`: push full-suite CI run 44397557544 was still in progress; push dependency audit 44397557605 was in progress; fail-closed gate 44397557794 passed. PR CI 44397569502, PR dependency audit 44397569235 and PR money audit 44397569295 were in progress. PR event CI does not replace the push full-suite job because the PR remains draft.
- Exact-head CI for the documentation commit created by this handoff update remains required. No result from an earlier head is being represented as verification of that later head.

### 2. Current XRP market evidence

**Kraken XRP/USD, capture bracket 21:02:25–21:02:30 UTC**
- Last $0.96691; bid $0.96702; ask $0.96709; spread 0.724 bps.
- Best bid size 1,544 XRP; best ask size 5,171 XRP. The displayed top ask is 3.35 times the top bid, but this is one transient price level, not consolidated depth.
- 24-hour volume 50.828M XRP; VWAP $0.98237191; open $0.98253; high $1.00677; low $0.96218.
- Last is 1.57% below 24-hour VWAP and 10.61% above the 24-hour low.
- Kraken returned no exchange event timestamp. This remains a retrieval-time observation and is model-ineligible.

**Order book**
- Basis reports Binance XRPUSDT perpetual depth at 20:26 UTC: $30.7M bids versus $27.6M offers across the nearest 1,000 levels per side; 51% bid share inside ±1%.
- Inside ±0.5%, offers exceed bids ($7.5M versus $6.7M); inside ±1% the book is nearly balanced ($10.9M bids versus $10.7M asks).
- This is a single-venue perpetual book, not spot depth. Walls can be cancelled or replenished; no directional inference is admitted.

**Derivatives disagreement**
- Liqwall at 20:32 UTC: OI $935M, down 2.3% over 24h; average funding −0.0002% per 8h; Binance funding −0.0021%; $5.6M liquidations, 59% shorts; 75% of Binance accounts long.
- TradRadar at 16:05 UTC: OI $1.32B across seven venues, up 1.94%; OI-weighted funding −0.0039% per 8h; at least $4.66M liquidations, $3.07M shorts and $1.58M longs.
- The $385M OI gap and roughly 19.5× funding-magnitude difference are not reconciled. Times, venues, contract coverage, weighting and USD conversion differ. Keep the observations separate.

**ETF flow disagreement**
- XRP Insights generated its dataset at 17:25 UTC, data as of Nov 17, with no provisional row: +159,134 XRP across Nov 16–17, across six spot funds plus BITW. GXRP flow is excluded; XRPR has nested ETP exposure; BITW rebalancing and fund fees can affect holdings deltas.
- CryptoKeyhole at 20:51 UTC: −3,251 XRP for Nov 17 from only two of four daily-readable funds; Bitwise and Franklin were missing. Its latest complete day remained Nov 13.
- ByKaranteli at 09:09 UTC: −$6.1M for Nov 17 across five funds, explicitly provisional until settled.
- These are different universes, vintages and definitions. Do not average them. The earlier XRP Insights +986 XRP page observation was superseded by the later +159,134 XRP two-day dataset; retain the old value as a stale vintage.

**Macro and geopolitics**
- Reuters reported a dollar index near 103.78 and hawkish Fed repricing; AP reported nearly all FOMC participants expected a December 25bp increase, with a small 50bp discussion and markets pricing odds near 95%.
- WSJ reported oil-supply-surplus expectations competing with Middle East security risks.
- These are broad risk/liquidity context, not evidence of a causal XRP price effect.

### 3. Entity and phrase research

- No new primary-source finding changes the existing Coinbase/Circle/Ripple/SBI relationship graph. Verified edges remain distinct: USDC equity/distribution economics, RLUSD distribution/listing, custody, reserve custody and announced infrastructure support. None alone proves incremental XRP purchases, XRP collateral utilization or XRP-denominated settlement.
- Japan's SBIC East/Central/West remain separate regional SME investment-and-consultation companies, not SBI Holdings; no new XRP/Ripple connection was established.
- Exact searches for “ASK Coin”, “actual capital” and “SBIC, ChatGPT SBIC” produced no new primary evidence that changes the current identity conclusions.
- No new identity-verified public YouTube videos were added for Camilla/Kamilah Stevenson. The unrelated SBiC Connect channel is not attributed to her.
- The exact market observations and rendered excerpts are SHA-256 hashed in the Run 26 artifact. Those hashes cover the captured text, not independently collected wire bytes. No external WORM or trusted timestamp anchor exists.

### 4. Prediction-engine readiness

- Latest scheduled-ingestion evidence remains run 44301868145 at 12:13:54 UTC: 34 receipts, 22 retained raw payloads, 12 digest-only receipts, 21 source failures, 3,235 feature-history records, 15 snapshots, 140 events, 107 scenarios, 124 eligible and 361 excluded features, zero walk-forward forecasts.
- SEC ingestion remains blocked because `BARROT_SEC_USER_AGENT` lacks an approved monitored contact. No address was invented.
- Binance returned HTTP 451; Bybit returned HTTP 403. No proxy, restriction bypass or unauthorized access was attempted.
- Raw-to-feature reconstruction from retained raw artifacts remains unimplemented; the feature-store cache is read-only after budget exhaustion; external receipt anchoring remains absent.
- The scheduled XRP workflow exists on the integration branch, but the cron is not active on main until that workflow is merged to the default branch.
- Forecast issuance remains disabled. No directional forecast, shadow trade, paper trade or real-money action was performed.

### 5. Nine-platform coordination

- ChatGPT-to-GitHub authentication and repository data flow are verified in this session. The connector reports broad repository permissions; exact token scopes and least-privilege status are not introspected.
- Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks remain unverified. No external dispatch, credential test, upload, submission, workspace write or data transfer was performed.
- Evidence exchange, independent red-team review and external minority-objection collection remain pending.

### 6. Security and merge blockers

1. PR #1663 remains draft with zero formal reviews; CODEOWNERS is `* @Barrot-Agent`.
2. Main is marked protected, but the detailed protection endpoint returns 403 and the visible fallback ruleset (10863829) is disabled. The branch metadata shows no required status-check contexts; independent approval enforcement is not verified.
3. Main's `paid-issue-publish.yml` remains an active `workflow_run` writer with `contents: write` and `git push origin main`; the integration branch disables this publisher. The main release workflow still uses three tag-based action references, while the integration version pins them. Transitive review of all changed workflow scripts, artifacts and third-party action behavior remains incomplete.
4. Main commit `d5d22ac252f88637a490ed4c1598f8608b6cb786` triggered automatic GitHub Pages build and deployment run [44396362354](https://github.com/Barrot-Agent/B-Agent/actions/runs/44396362354), which succeeded. That deployment followed the separate checkpoint commit; this run did not initiate it. A merge to main would create another push and may trigger the same side effect. No deployment authorization was given.
5. Dependency PRs #1665 and #1666 are stale and their changed dependency files differ from the integrated branch.
6. #1541 is stacked on closed, unmerged #1540; two compared files match #1663 and remaining files diverge.
7. #1265 has unique ledger work but its `.github/workflows/ci.yml` overlaps and differs from #1663.

### 7. Open PR backlog

| Classification | PRs |
|---|---|
| Blocked (5) | #1663, #1665, #1666, #1541, #1265 |
| Unique/unreviewed (7) | #1664, #1450, #1460, #1440, #1436, #1437, #1353 |
| Ready | None |
| Duplicate | None |
| Superseded | None |

No PR was merged or closed. No duplicate/superseded source PR was bulk-closed.

### 8. Next concrete action

1. Allow the exact-head push full suite and dependency audit on the post-handoff integration commit to finish; inspect job logs, not just workflow conclusion.
2. Continue the transitive review of the 67 changed workflow definitions and invoked scripts, starting with the main paid-issue writer, Pages deployment path, tag release workflow and artifact provenance.
3. Resolve branch-protection and independent-review enforcement before changing PR #1663 from draft.
4. Obtain an approved monitored SEC contact before enabling SEC ingestion; do not use a placeholder.
5. Improve timestamped spot L2/trade capture, derivatives unit/venue normalization, issuer-level ETF flow reconciliation and raw-to-feature rebuild before forecast admission.

**Merge decision: NO MERGE.** The objective remains a working integrated Barrot build and measured XRP predictive performance, not a larger queue of PRs.


## Run 26 supplemental cross-venue check — 2026-11-18T21:02:30Z

The Run 26 market artifact and map were corrected and extended with a second direct exchange observation.

**OKX XRP-USDT spot ticker**
- Exchange event timestamp: 2026-11-18T21:01:24.260Z.
- Last 0.9684 USDT; bid 0.9684; ask 0.9685; spread 1.033 bps.
- Best bid 1,894.064761 XRP; best ask 1,077.8 XRP.
- 24-hour volume 31.966M XRP; 24-hour open 0.9701 USDT; high 1.0079; low 0.9633.
- This is a timestamped direct spot quote, but it is XRP-USDT, not XRP-USD.

**USDT conversion quality control**
- OKX USDT-USD ticker timestamp: 2026-11-18T20:39:18.066Z.
- Last 0.99889 USD.
- The conversion leg is 1,326.194 seconds older than the XRP-USDT quote. USD normalization is rejected. The raw 0.9684 USDT quote is not compared as a USD price against Kraken's $0.96691.

**Kraken field-semantics correction**
- Kraken's `o` field is the UTC-day open, not a rolling 24-hour open. The $0.98253 value is now labelled `open_utc_day_usd`; the −1.59% calculation is labelled change from UTC-day open. The 24-hour VWAP, volume, high and low use their separate 24-hour fields.
- This correction changes no forecast or model eligibility.

**Depth and access limitations**
- Coinbase Exchange XRP-USD ticker/level-2, Bitstamp XRP/USD ticker/order-book, Kraken Depth and OKX market/books endpoints were inaccessible through the current retrieval path.
- No proxy, scraping workaround or access-control bypass was attempted.
- Current depth evidence remains Basis's single-venue Binance XRPUSDT perpetual book; a synchronized cross-venue spot L2 snapshot is still missing.

The updated source receipts hash the exact web-rendered JSON/excerpt text. They are not independently captured wire bytes and are not externally WORM-anchored. All current observations remain model-ineligible; forecast issuance remains disabled. This supplemental commit supersedes the earlier Run 26 field label but does not change the NO MERGE disposition.


## Run 26 workflow and script transitive-review spot-check — 2026-11-18T21:09:15Z

This is a bounded review, not completion of the full 67-workflow transitive audit.

### Scripts inspected

- `scripts/coinbase_paper_trader.py`: reads Coinbase public ticker and recent-trade endpoints, calls Groq for a simulated decision, and writes local `web/paper_trading_state.json` / `web/paper_trading_log.jsonl`. No Coinbase order endpoint or Coinbase trading key was found in the inspected script. The workflow is manual, requires `YES` and an exact main SHA, and uploads artifacts only. Its configured product is BTC-USD, not XRP. It was not run.
- `scripts/deploy_databricks.py`: performs real external workspace mutations: `workspace.mkdirs`, `workspace.import_(overwrite=True)`, job reset/create and `run_now`. Its workflow is manual and checks an explicit external-change confirmation plus exact main SHA. It was not run.
- `scripts/kaggle_competitions_automation.py`: writes Kaggle credentials to the runner filesystem, downloads competition data and calls `competition_submit`. Its workflow requires explicit YES, a non-empty competition allowlist and exact main SHA. It was not run.
- `scripts/paid_issue_hunter.py`: GitHub search and repository-metadata reads plus local `PAID-ISSUES.md` and JSON writes; no issue comments, claims or labels. The separate publisher remains active on main and can push those generated files; the integration branch disables that publisher.

### Workflow paths inspected

- `barrot-ops.yml`: manual exact-main-SHA gate; separate confirmations for Databricks workspace import with `--overwrite` and Kaggle dataset download.
- `deploy-a2a-worker.yml`: manual exact-main-SHA Cloudflare Worker deployment; separate confirmation for secret rotation/upload.
- `deploy-databricks.yml`: manual exact-main-SHA external workspace deployment.
- `kaggle-competitions.yml`: manual exact-main-SHA submission with explicit competition allowlist.
- `barrot-restart-space.yml`: manual exact-main-SHA factory restart using the Hugging Face token.
- `coinbase-paper-trader.yml`: manual artifact-only simulation with exact main SHA and YES confirmation.
- `sync-huggingface.yml` and `databricks-bundle.yml`: quarantined with empty permissions and false job conditions.
- `sync-self-hosted-brain.yml`: job condition is false.

No workflow was dispatched. No deployment, workspace write, secret rotation, Space restart, Kaggle download/submission, Groq paper simulation, funds transfer or real-money action occurred.

### Exact-head CI at this capture

Current head: `c9fbb2075e78772d2d3c91e0d36f98af6b2e7fa0`.

- Push CI run [44398295346](https://github.com/Barrot-Agent/B-Agent/actions/runs/44398295346): standard tests and Pages validation passed; full repository test suite still in progress.
- Push dependency audit [44398295297](https://github.com/Barrot-Agent/B-Agent/actions/runs/44398295297): passed.
- Push fail-closed gate [44398295405](https://github.com/Barrot-Agent/B-Agent/actions/runs/44398295405): passed.
- PR CI [44398308604](https://github.com/Barrot-Agent/B-Agent/actions/runs/44398308604): passed, but the standard tests and full suite were skipped because PR #1663 remains draft.
- PR money audit [44398308501](https://github.com/Barrot-Agent/B-Agent/actions/runs/44398308501): passed.
- PR dependency audit [44398308612](https://github.com/Barrot-Agent/B-Agent/actions/runs/44398308612): still in progress.

The integration PR remains blocked. This spot-check does not close the transitive review requirement and does not authorize external actions.

 
---
 
# Run 27 addendum — 2026-11-18T22:22:14Z

## Current repository snapshot

- Main remains d5d22ac252f88637a490ed4c1598f8608b6cb786.
- Existing integration PR #1663 remains the only V3/XRP integration branch; no new branch or PR was created.
- Snapshot head: e100ae1fea6a36f5755a98219abba450c885b78f; 351 commits ahead, zero behind; 1,436 changed files; 67 changed workflow files. Main's 1,739 tree entries remain present in the integration tree. Current integration tree: 2983 entries, 93 workflows, 515 test-named Python files, 841 XRP research files.
- PR #1663 remains draft and mergeable, with zero independent reviews, zero review threads and zero requested reviewers.
- Concurrent integration maintenance advanced the same branch during this run. The branch was re-fetched before this remediation; no reset, force-push or branch rewrite occurred.
- The Pylint 4.1.4 development dependency update from #1665 is incorporated into #1663 by commit 8fc3dd3234e519e4537496ee46bed005b0c9a1dd (requirements-dev.txt). Keep #1665 open until #1663 merges and the exact change is verified on main; do not close it early.

## Exact CI failure and remediation

Latest completed exact-head full-suite run 44410299678 on e100ae1fea6a36f5755a98219abba450c885b78f failed: **4,271 passed, 6 failed, 1 skipped, 11 warnings, 19 subtests passed**, 107.31 seconds, 68.13% inclusive coverage.

All six failures are stale test/evidence contracts, not application prediction or Barrot V3 runtime failures:

1. Two external-action tests expected the Hugging Face model-merge workflow to be active and approval-gated. The workflow is intentionally quarantined because its reviewed merge configuration is absent; it has empty permissions, a false job condition, no checkout, no credential access and no upload. The tests now verify quarantine rather than demanding reactivation.
2. Four XRP-map assertions were stale: changed-file count, machine-readable transitive-review status, hard-coded market price/hash and exact-phrase status. The tests now compare market values to the captured evidence artifact and keep narrative detail separate from the machine status.

The standard core job on the same head had 757 passed, 2 failed and 8 subtests passed. The PR-event CI 44410307649 reported success but skipped core/full-suite jobs because PR #1663 remains draft. On exact head, dependency audit 44410307568, money audit 44410307489, fail-closed gate 44410307643 and Pages validation-only job passed. This does not make the full suite pass.

The test/evidence remediation is included in the same-branch successor commit. Its new exact-head full suite, dependency audit and fail-closed checks must complete before any merge decision.

Current main CI 44396364281 passed on exact main d5d22ac: 1,207 passed, 2 skipped, zero failures, 78.10% coverage. This does not substitute for integration-head verification.

## XRP spot, derivatives and liquidity — capture 22:07:54Z

- Kraken XRP/USD: last **$0.96513**, bid $0.96512 (182 XRP), ask $0.96513 (111 XRP), spread 0.104 bps, 24-hour volume 48.659M XRP, 24-hour VWAP $0.98281596, high $1.00677, low $0.96218. Last is 1.80% below VWAP and 6.62% of the way up from the 24-hour low. Kraken's o field is the UTC-day open ($0.98253), not a rolling 24-hour open.
- Kraken's top-level bid size exceeded ask size (ask/bid 0.61); the asynchronous OKX XRP-USDT snapshot showed the opposite (ask/bid 1.98). This is venue-specific top-of-book evidence, not consolidated depth.
- OKX XRP-USDT quote: 0.9715 USDT, timestamp 21:35:45.971Z. The USDT/USD conversion quote was 0.99888 at 21:54:55.172Z; timestamp skew 19m09s. USD normalization was rejected. OKX quote age at capture was 32m08s.
- Binance XRPUSDT perpetual: mark 0.96860, index 0.96913248, funding -0.000867% per 8h at 21:50:24Z; one-venue snapshot, 17m30s old at capture.
- CryptoQuant's Nov 18 Binance analysis reports seven-day spot share at 17.9%, down 34.2% from 27.2% in early November, with futures volume about 5.6 times spot. Its separate 30-day liquidity index is 0.041, a three-month low, with $2.71B 30-day turnover. A Nov 16 CryptoQuant analysis reports Binance XRP OI near $325M versus about $1.5B earlier in 2026 and estimated leverage 0.13, the lowest since November 2024. CryptoPotato repeats CryptoQuant metrics and is not independent confirmation.
- Counter-hypothesis: lower OI/leverage can reduce forced-liquidation cascade risk even while lower spot participation and liquidity can amplify price impact. Negative funding alone does not establish a directional edge.

## ETF flow disagreement — 2026-11-17

- CryptoKeyhole: -3,251 XRP, but only 2 of 4 daily-readable funds had reported; latest issuer file read 05:25 UTC Nov 18. Partial.
- XRP Insights: +986 XRP across six spot funds plus BITW; GXRP is excluded from flow totals during a data-gap correction. The site reports +159.1K XRP across Nov 16–17.
- ByKaranteli: -$6.1M across five funds, provisional until issuer settlement.
- Alpha Finance: -$6.1M across five funds.

Do not average these series. The fund universes and treatment of BITW, XRPR and GXRP differ; ByKaranteli and Alpha Finance may share overlapping five-fund coverage and are not independent issuer confirmations.

## New institutional rail evidence

The World Bank Group's Nov 17 primary announcement says it will explore regulated USDC payment infrastructure with Citi and Circle. Citi contributes existing banking rails; Circle contributes USDC mint/settlement infrastructure. The initial model is exploratory and intermediated/interoperable. No Ripple, XRP, XRPL, RLUSD or production volume is established. This is a Circle/Citi/World Bank rail-development signal, not XRP demand.

## Kamilah/Camilla Stevenson identity and video inventory

The June 11, 2026 iHeart interview identifies Dr. Kamilah Stevenson as the guest. At 40:07 she self-reports X as “cam i am cam Stevenson”, Instagram as “Kamilla Stevenson” and YouTube as “doctor Camilla Stevenson”; she explicitly warns that fake pages exist. iHeart warns its transcript is automatically generated and may not be fully accurate.

Two provisional video-level matches were found through Glasp transcripts; both open with a self-identification as Camila Stevenson:

- Ripple Just Became a BANK — And XRP Holders Need to Understand This, Dec 14, 2025; YouTube video ID QslbjGQD0MU; Glasp transcript https://glasp.co/youtube/QslbjGQD0MU.
- XRP ETFs Are Here. Price Isn’t Moving. Here’s What Everyone’s Missing., Jan 13, 2026; YouTube video ID ci0FH73lbCs; Glasp transcript https://glasp.co/youtube/ci0FH73lbCs.

These are provisional content-level matches, not proof that candidate channel ID UCqUPJMQdkCN6lsLVDnichPA is hers. The interview warns of fake pages; no channel-wide inventory or lookalike-channel attribution is admitted until a first-party link authenticates the exact channel ID.

## Phrase research and forecast admission

Exact searches for “ASK Coin”, “actual capital” and “SBIC, ChatGPT SBIC” produced no new primary-source relationship. SBIC East/Central/West remain three separate Japanese regional SME investment/consultation companies, not SBI Holdings. The VOST-delivered ChatGPT/Copilot course is not evidence of an OpenAI partnership.

**Forecast status: NOT_ISSUED.** No directional forecast, probability claim, paper trade or real-money action. Latest ingestion remains 34 receipts with 21 source failures; external receipt anchoring, deterministic raw-to-feature rebuild, sufficient independent source clusters, leakage-safe walk-forward sample size, calibration and independent shadow outcomes remain incomplete.

## Backlog and disposition

12 PRs remain open: **5 blocked, 7 unique/unreviewed, 0 ready, 0 confirmed duplicates, 0 superseded**. #1663 is the sole consolidated integration. #1664 remains unique/unreviewed despite three shared paths; #1665's Pylint patch is incorporated but the source PR stays open pending merge/verification; #1666, #1541 and #1265 remain blocked pending dependency/path reconciliation. The remaining research and ledger PRs remain unique/unreviewed.

**Disposition: NO MERGE.** The current exact-head full suite failed six stale assertions; the remediation commit's exact-head full suite is pending. Independent review, branch-protection details (403), disabled fallback ruleset, self-owned CODEOWNERS, automatic main publication/Pages side effects and full transitive workflow security review remain blockers. No deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external model dispatch, paper trade, funds transfer or real-money action occurred.


---

## Run 28 addendum — 2026-11-18T22:42:07Z

**Mission:** XRP intelligence and measured prediction-engine mastery remain priority one. Preserve Barrot V3 as execution, orchestration, safety and verification foundation.

### Repository snapshot and integration protocol

- Repository: `Barrot-Agent/B-Agent`.
- Current main at inspection: `d5d22ac252f88637a490ed4c1598f8608b6cb786`.
- Existing integration PR: [#1663](https://github.com/Barrot-Agent/B-Agent/pull/1663).
- Integration branch: `integration/xrp-v3-mainline-successor-20261115T2101Z`.
- Code/test head audited: `da5eef1bca0fee4f527c22fd99c8d4427cc39d7b`.
- At that audited head: 352 commits ahead, zero behind; 1,437 changed files; 516,765 additions and 6,754 deletions; 68 changed workflow files; 407 changed test paths. The compare endpoint exposes at most 300 file-stat rows, so the paginated PR filename inventory is authoritative for the full 1,437-path count.
- Main tree: 1,739 entries. Integration tree: 2,984 entries. No main-tree paths are missing from the integration tree.
- Main does **not** contain `barrot_agent/data/missions/primary_mission.json`, `.github/workflows/xrp-public-ingestion.yml`, or `BARROT_XRP_MISSION_HANDOFF_LATEST.md` (each returned 404 on main). The mission contract, scheduled ingestion workflow and canonical handoff therefore remain integration-branch work, not active mainline capabilities.
- The nine-platform map was refreshed in commit `dcaa60e7a0e4d69922f3d7ba149ea93f91e6f1c1`; it records the repository, security, CI, platform-authentication and Run 28 market snapshot as of 22:35:40Z.
- This run created no branch and no PR. Main was not modified. The handoff/map changes are documentation/evidence updates on the existing integration branch; no force-push or history rewrite occurred.

### Exact-head verification

**Integration code/test head `da5eef1`:**

- Push CI [run 44411853369](https://github.com/Barrot-Agent/B-Agent/actions/runs/44411853369): success.
- Full repository suite job: success; **4,277 passed, 1 skipped, 0 failed, 11 warnings, 19 subtests passed**, 143.50 seconds.
- Inclusive coverage: **68.13%** across `barrot_agent`, `directive_platform` and `data`; separate legacy-core coverage: **77%**.
- The inclusive coverage configuration omits only `__pycache__` and test files. It now measures migrated major packages including `agi`, `ingestion`, `analysis`, `monetization` and `orchestration`. The separate 70% legacy-core gate intentionally retains the historical exclusions for continuity.
- Wheel build, packaged primary-mission resource check and installed Barrot V3/XRP mission imports passed.
- Push dependency audit [run 44411853121](https://github.com/Barrot-Agent/B-Agent/actions/runs/44411853121): success.
- Push fail-closed gate [run 44411853169](https://github.com/Barrot-Agent/B-Agent/actions/runs/44411853169): success.
- PR CI [run 44411860804](https://github.com/Barrot-Agent/B-Agent/actions/runs/44411860804), PR money audit [run 44411860782](https://github.com/Barrot-Agent/B-Agent/actions/runs/44411860782), PR dependency audit [run 44411860967](https://github.com/Barrot-Agent/B-Agent/actions/runs/44411860967), and PR fail-closed gate [run 44411860777](https://github.com/Barrot-Agent/B-Agent/actions/runs/44411860777): success. The PR-event full-suite job is skipped by design for this integration draft; the exact-head push run above is the full-suite evidence.

**Current main `d5d22ac`:**

- Main CI [run 44396364281](https://github.com/Barrot-Agent/B-Agent/actions/runs/44396364281): full suite **1,207 passed, 2 skipped, 0 failed, 8 subtests passed**, 78.10% coverage.
- Main's test workflow is still the narrower core CI. The integration branch's expanded full-suite job is materially broader.

Warnings on the integration run include legacy pytest functions returning booleans, setuptools license/package-discovery deprecations and the exhausted GitHub Actions cache budget. No test or dependency gate failed.

**Exact-head limitation:** `da5eef1` is the latest fully tested code/evidence head. The later map commit `dcaa60e` and this Run 28 handoff commit are documentation/evidence-only changes. Their own post-commit CI must finish before the resulting latest branch head is called exact-head verified. Do not transfer the `da5eef1` result to a later SHA.

### Open PR inventory and overlap reconciliation

Twelve PRs remain open:

- **Blocked:** #1663, #1665, #1666, #1541, #1265.
- **Unique/unreviewed:** #1664, #1450, #1460, #1440, #1436, #1437, #1353.
- **Ready:** 0. **Duplicate:** 0. **Superseded:** 0.

Current overlap counts against #1663:

- #1664: 3 shared generic/documentation paths (`BARROT_SYNC.md`, `MEMORY.md`, `README.md`); objective remains a separate staged product, not a duplicate.
- #1665: 1 shared path (`requirements-dev.txt`). The integration branch contains `pylint>=4.1.4`, the version proposed by #1665, but the complete file differs. Keep the source PR open until the successor merges and the exact dependency change is verified on main.
- #1666: 1 shared path (`pyproject.toml`). The proposed Kaggle upper-bound change to `<1.8` is **not** incorporated: integration still pins Kaggle below 1.6 in both `pyproject.toml` and `requirements-integrations.txt`. Keep blocked pending dependency/security review and full-suite compatibility.
- #1541: all 5 paths overlap. `barrot_agent/mmi_adapter.py` and `tests/test_mmi_integration.py` are byte-identical to integration; `barrot_agent/mmi_v1.py`, its evidence JSON and `tests/test_mmi_v1.py` diverge. It is stacked on the #1540 security branch. Reconcile the three divergent files before any merge; do not close it now.
- #1265: 1 shared path (`.github/workflows/ci.yml`), with divergent content. Its XRP ledger-index work remains distinct.
- #1450, #1460, #1440, #1436, #1437 and #1353 have no shared paths with #1663 in the current paginated filename comparison; retain their unique research/repair work.

No source PR was closed. No duplicate/superseded classification is inferred solely from shared filenames.

### Security, approvals and automatic side effects

- GitHub reports main as protected, but detailed branch-protection reads return HTTP 403. Required status-check contexts and bypass settings are therefore **not verified**.
- The only visible repository ruleset, `Fall Back`, is disabled.
- `.github/CODEOWNERS` still assigns `* @Barrot-Agent`. PR #1663 has zero submitted reviews, zero review threads and zero requested reviewers; it remains draft.
- Main's `paid-issue-publish.yml` remains active with `contents: write`, checkout credentials persisted, and a commit/push to main. The integration version disables the publisher with empty permissions and a false job condition.
- Main's Coinbase paper-trader workflow uses the Groq secret and commits/pushes simulated state to main without typed confirmation or expected-main-SHA checks. Integration requires typed `YES`, exact main SHA, read-only repository permission and artifact-only output. It was not dispatched. No paper trade occurred.
- Main's tag-triggered release workflow has `contents: write` and mutable action references. Integration pins its action references but retains tag-triggered release creation. No release was created.
- A main push automatically triggers GitHub Pages publication. Merging #1663 would create this external publication side effect. No deployment approval was issued; this is a merge blocker under the mission's no-unapproved-deployment rule.
- Transitive review of all changed workflows, invoked scripts, artifacts and third-party action supply chains remains incomplete. The prior bounded script/workflow spot-check is not a complete security audit.

### XRP market snapshot — Run 28

All observations below are **research-only and model-ineligible**. Public web/API-rendered responses were not archived as raw wire bytes in this run; no SHA-256 wire receipt or external timestamp anchor is claimed.

**Spot**

- Kraken XRP/USD public ticker retrieval (capture upper bound 22:35:40Z; exchange event timestamp absent): last **$0.96325**, bid **$0.96318** (351 XRP), ask **$0.96325** (3,193 XRP), spread about **0.726 bps**, 24-hour volume **46.633M XRP**, VWAP **$0.98345688**, high **$1.00677**, low **$0.96083**. The last is about 2.05% below 24-hour VWAP and near the day's low. Kraken's `o` field remains the UTC-day open (**$0.98253**), not a rolling 24-hour open.
- OKX XRP-USDT ticker event timestamp **2026-11-18T22:11:03.368Z**: last **0.9638 USDT**, bid 0.9638 (5,030.93 XRP), ask 0.9639 (1,001.5 XRP), spread about **1.038 bps**, 24-hour volume **30.777M XRP**, high 1.0079 and low 0.9623 USDT.
- The one-level imbalance is opposite across venues: Kraken's best ask size is about 9.1 times its best bid; OKX's best bid size is about 5.0 times its best ask. This is venue/level-specific, not consolidated directional pressure. No synchronized multi-venue spot L2 or sequence reconstruction was obtained. The OKX quote is USDT-denominated and was not normalized to USD in this run.

**Derivatives**

- Liqwall, as of 22:12Z: price $0.9675; OI **$937M**, −2.0% over 24h; average funding +0.0005%/8h, while Binance funding was −0.0005%; 75.1% of Binance accounts with XRP positions were long; 24-hour liquidations $5.5M (longs $2.4M, shorts $3.1M).
- TradRadar, updated 20:03Z with 15-minute delay: mark $0.9654; OI **$1.29B** across seven exchanges, −2.12% over 24h; OI-weighted funding −0.0010%/8h; at least $5.64M liquidations (longs $2.45M, shorts $3.19M); account long/short ratio 3.33.
- OI totals differ by about $353M because provider universes/coverage and timestamps differ. Funding signs also disagree. Do not average or treat these as independent confirmations. Falling OI and long-heavy account ratios are context, not a forecast.

**ETF flows — preserve the disagreement**

- CryptoKeyhole updated at 22:26Z: Nov 17 was still partial, **−3,251 XRP from 2 of 4 daily-readable funds**; on Nov 18 none of those four issuer files had been published by the page's update. Its latest complete day was Nov 13 (−9,967 XRP); Nov 9–13 complete sessions summed to −4.923M XRP.
- XRP Insights displayed Nov 17 **+986 XRP**, Nov 16 **+158,148 XRP**, and −6.08M XRP for Nov 9–13. Its page showed 1.18395B XRP held but a headline AUM of $760.05M that conflicts with the displayed fund-level assets and approximate value of the holdings at the contemporaneous XRP price. Exclude that headline AUM from features until reconciled.
- ByKaranteli and Alpha Finance each reported **−$6.1M** for Nov 17 across five funds. Their fund coverage overlaps; these are secondary aggregations, not independent issuer-level confirmations.
- Do not average XRP-denominated partial issuer-file flows with USD-denominated five-fund aggregates.

**Macro**

Reuters' Nov 18 report describes a 19-month dollar high and higher Treasury yields after hawkish Federal Reserve minutes; the reported market-implied probability of a 50-basis-point December move rose to 7.3% from 5.3%. This is broad risk/liquidity context, not a demonstrated XRP-specific causal variable.

### Institutional and corporate relationship updates

- **World Bank Group–Citi–Circle:** the World Bank's Nov 17 primary announcement describes an exploratory, intermediated/interoperable USDC payment-rail model alongside existing correspondent banking. Citi contributes banking-rail connectivity; Circle contributes USDC mint/settlement infrastructure. It does not name Ripple, XRP, XRPL or RLUSD, and it establishes no production volumes. This is material counterevidence to any claim that institutional stablecoin-payment adoption necessarily creates XRP demand.
- **Coinbase–Ripple:** Coinbase's Oct 28 official RLUSD announcement confirms Prime, Exchange and Retail access across XRPL, Base and Ethereum. It says Coinbase Global Exchange collateral availability **will follow**; no newer official confirmation of live collateral support was established in this run. Do not count RLUSD as active Coinbase collateral on this evidence.
- **SBI–Ripple:** SBI VC Trade's June 24 official release confirms RLUSD distribution in Japan. This is a regulated stablecoin distribution relationship, not proof of XRP purchases, XRP collateral usage or XRP settlement volume.
- **SBI–Circle:** SBI's May 12 official release records its $50M Circle equity investment at Circle's listing, participation in the ARC token presale through subsidiaries, and the SBI Circle Holdings joint venture. SBI therefore has distinct relationships with both Ripple and Circle. Do not conflate SBI Holdings with the Japanese SBIC East/Central/West companies.
- **SBIC identity:** the existing primary-source resolution remains: Tokyo, Nagoya and Osaka regional Small and Medium Business Investment & Consultation companies are separate legal entities, not SBI Holdings. No verified XRP/Ripple relationship was found.
- **Exact phrases:** fresh exact searches for `"ASK Coin"`, `"actual capital"` and `"SBIC, ChatGPT SBIC"` produced no new primary-source XRP/SBI relationship. No inference is made from ambiguous strings.
- **Kamilah/Camilla Stevenson:** the iHeart guest identity and self-reported platform names remain supported, including her warning about fake pages. The candidate YouTube channel ID is still not authenticated by a first-party cross-link. Two video-level transcript matches remain provisional; no channel-wide inventory is attributed.

### Prediction-engine state

**DESIGNED / IMPLEMENTED on the integration branch:** public XRP ingestion, SEC adapter, append-only point-in-time feature store, event timeline, forecast/outcome ledger, chronological walk-forward evaluator, baseline probability generation, calibration diagnostics and drift monitoring. The current code tree includes `xrp_public_ingestion.py`, `sec_edgar.py`, `feature_store.py`, `forecast_ledger.py`, `walk_forward.py`, `event_timeline.py` and `feature_drift.py`.

**SCHEDULED BUT NOT ACTIVE ON MAIN:** `xrp-public-ingestion.yml` defines hourly and daily cron schedules and read-only permissions on the integration branch. GitHub scheduled workflows run from the default branch; this file is absent from main. Integration push captures are not production hourly ingestion.

**Last recorded ingestion, not refreshed in Run 28:** run **44301868145** at 2026-11-18T12:13:54.617611Z; 34 receipts (22 raw, 12 digest-only), 21 source failures, 124 eligible and 361 excluded features, 3,235 feature-history records, 15 snapshots, 140 events and 107 scenarios. SEC submissions/companyfacts remained 0 with six failures because the monitored `BARROT_SEC_USER_AGENT` contact variable is not configured; CFTC weekly source families captured 0/2. Receipt chain passed, but external anchoring is absent, raw-to-feature rebuild from raw artifacts is not implemented, cache storage is read-only, drift is insufficient-data and walk-forward forecasts remain zero.
 
**Forecast status: `NOT_ISSUED`.** No XRP-specific candidate has satisfied the strict training, out-of-sample, baseline-comparison, overlap-adjusted effective-sample-size, source-cluster, calibration, drift, shadow and independent Ed25519-attestation gates. No directional forecast is issued.

### Nine-platform coordination

The updated map remains explicit:

- ChatGPT-to-GitHub connector authentication and this session's repository read/write flow are verified. Repository metadata reports admin/maintain/push/pull/triage permissions, but token-scope introspection and least-privilege verification are incomplete.
- Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks remain unverified; no live authentication/data-flow claim is made.
- No external-model task dispatch, cross-platform evidence transfer or independent red-team review occurred. Assignments remain proposed, not executed. Minority objections and disagreements remain in the research artifacts.

### Disposition and next concrete action

**NO MERGE.** The exact code/test head `da5eef1` passed the full repository suite and security audits, but the documentation commits that follow it require their own exact-head CI. More importantly, PR #1663 remains draft with zero independent approvals; branch-protection details are inaccessible; the visible fallback ruleset is disabled; CODEOWNERS is self-owned; main's automatic paid-issue publisher remains active; a merge triggers Pages publication without deployment approval; and the transitive workflow/security audit is incomplete.

Next: verify CI on the latest handoff/map head; complete the changed-workflow transitive review; resolve independent review and effective branch protection; contain/authorize Pages and other publication side effects; then continue raw-byte/externally anchored ingestion, SEC/CFTC source recovery and leakage-safe walk-forward/shadow evaluation.

No merge, deployment, release, secret rotation, Space restart, Kaggle submission, Databricks write, external-model dispatch, paper trade, funds transfer or real-money action occurred in Run 28.


## Run 29 addendum — 2026-11-18T23:08:34Z

### Current repository snapshot and integration-first audit

- Repository: Barrot-Agent/B-Agent.
- Main SHA at this run: d5d22ac252f88637a490ed4c1598f8608b6cb786.
- Existing consolidated integration PR: #1663.
- Integration branch: integration/xrp-v3-mainline-successor-20261115T2101Z.
- Branch head when the Run 29 evidence/map/test update began: 066d8c9910e66fcaa58a26053f78dd00f9d65963. The map snapshot records this point in time.
- Latest branch head before this handoff append: a612db766205703ba94bbb0171417e9be6ef59c6; 358 commits ahead, zero behind; 1,438 changed files; 68 changed workflow files; 517,564 additions and 6,754 deletions. PR remains open, draft and mergeable.
- Complete recursive Git trees were fetched and compared: main 1,739 entries, 92 workflow files, 162 test-named files, 30 XRP research files; integration 2,985 entries, 93 workflow files, 547 test-named files, 843 XRP research files. Main paths missing from integration: zero. Neither tree response was truncated.
- Main is reported protected, but detailed branch-protection access still returns 403. The only visible ruleset, “Fall Back,” is disabled. The integration branch itself reports protected=false. CODEOWNERS still assigns all paths to @Barrot-Agent; PR #1663 has zero formal reviews and no requested reviewers.
- The connected GitHub repository permission is admin/maintain/push/pull/triage. Token scopes were not introspected. This is broader than read-only research and does not establish least privilege.
- Main’s paid-issue publisher remains active with contents:write and a direct git push origin main after a successful hunter workflow. The integration branch disables that publisher with empty permissions and a false job condition.
- Main’s Coinbase paper-trader workflow reads GROQ_API_KEY and pushes simulated state to main without typed confirmation or an expected-main-SHA gate. The integration version is manual, requires typed YES and an exact main SHA, has contents:read, and uploads an artifact only. It was not run.
- Main’s release workflow retains a tag-triggered contents:write release and mutable action references. Integration pins the action references but retains the tag trigger. No release was created.
- GitHub Pages publication is an automatic main-push side effect. The previous main head d5d22ac triggered successful Pages run 44396362354. This run did not initiate a deployment. No deployment authorization was issued.
- The current PR has 68 changed workflow files. The previous bounded static review covered 67; the full current workflow set, invoked scripts, artifacts and transitive third-party actions still require reconciliation.

### Full-suite diagnosis and test remediation

- Last fully passing integration code/test head: da5eef1bca0fee4f527c22fd99c8d4427cc39d7b. Push run 44411853369: 4,277 passed, 1 skipped, zero failed, 11 warnings, 19 subtests passed; 68.13% inclusive coverage and 77% legacy-core coverage. Dependency audit and fail-closed gate passed.
- Later tested head 5ef5482b819df3a362d572bb9850684ffbea967f failed push full-suite run 44414191550: 4,276 passed, 1 failed, 1 skipped, 11 warnings, 19 subtests; 68.13% inclusive coverage and 77% legacy-core coverage. The sole failure was tests/test_xrp_nine_platform_map_latest.py expecting 1,436 changed files while GitHub’s current PR metadata reported 1,437. The same fixture also retained the stale 67-workflow count while the current PR had 68. This was a brittle repository-state assertion, not an XRP model or Barrot V3 runtime failure.
- On the existing integration branch, tests/test_xrp_nine_platform_map_latest.py was changed to validate schema/invariants and dynamic PR-backlog classifications instead of stale hard-coded file counts, workflow counts and CI run IDs. It now checks #1668’s blocked classification.
- The nine-platform map was refreshed with the Run 29 snapshot, current PR inventory, provider-failover risk, current spot/derivatives/ETF observations and CI history. The map’s snapshot head is the pre-update Run 29 capture; the branch has advanced since that snapshot.
- A new versioned evidence record was added: research/xrp_intelligence/20261118T230834Z-run29-market-institutional-reconciliation.json. It preserves the exact JSON response text surfaced for Kraken and OKX and hashes those rendered strings. These are not independently captured HTTP wire bytes and have no external WORM/timestamp anchor.
- On the current handoff predecessor a612db766205703ba94bbb0171417e9be6ef59c6, push full CI run 44419379730 was in progress, dependency audit 44419379733 was pending, fail-closed push gate 44419379769 passed. PR CI 44419390423 and money audit 44419390422 were in progress; PR dependency audit 44419390428 was pending. PR-event test jobs remain skipped while #1663 is draft. This handoff commit will trigger new exact-head CI; no passing result is claimed until that run completes.

### Additional open PR — #1668 provider failover

- #1668 is a separate draft PR with five commits and three changed files: .github/workflows/barrot-agent.yml, scripts/barrot_agent.py and tests/test_barrot_agent_script.py. All three paths overlap #1663.
- It adds Cloudflare Workers AI and OpenRouter free-route fallbacks after Groq HTTP 429; Gemini is opt-in. The workflow sets BARROT_ENABLE_FREE_FALLBACKS=true and supplies Cloudflare, OpenRouter and Gemini credentials when configured.
- The fallback forwards the original messages, tool definitions and tool_choice to third-party endpoints. The PR contains no demonstrated prompt redaction, data-classification gate, user data-egress authorization gate or live provider authentication/data-flow test. Unit tests use fake credentials; they do not verify provider authentication.
- PR CI run 44416137636 passed the main-branch test workflow: 1,209 passed, 2 skipped, 8 subtests, 78.10% coverage. This is not the expanded integration-branch suite. No dependency-audit run was observed for #1668. It has zero formal reviews and remains draft.
- Classification: BLOCKED. Do not merge #1668 independently. Reconcile it into the single V3 integration workstream only after provider data-flow policy, authorization, redaction/classification, least-privilege permissions and expanded full-suite verification are satisfied. No external model dispatch or data transfer occurred.

### Open PR inventory

Thirteen PRs remain open. No PR was merged or closed.

- Blocked: #1663, #1668, #1665, #1666, #1541, #1265.
- Unique/unreviewed: #1664, #1450, #1460, #1440, #1436, #1437, #1353.
- Ready: 0. Duplicate: 0. Superseded: 0.

#1665’s Pylint 4.1.4 dependency change is present in the integration branch, but the source PR remains open pending merge and exact verification on main. #1666’s Kaggle dependency update remains unincorporated. #1541 and #1265 retain divergent overlapping files. Unique research/repair branches remain open.

### XRP market observations — Run 29

All observations are research-only and model-ineligible. The new evidence record contains the surfaced JSON text, rendered-text hashes and source metadata; it does not claim raw HTTP wire capture.

**Spot**
- Kraken XRP/USD retrieval: last $0.95815; best bid $0.95835 for 5,218 XRP; best ask $0.95840 for 961 XRP; spread about 0.522 bps; 24-hour volume 48.167M XRP; 24-hour VWAP $0.98257443; high $1.00677; low $0.95485; UTC-day open $0.98253. Last is about 2.49% below 24-hour VWAP and about 6.35% of the way up from the 24-hour low. Kraken supplies no exchange event timestamp. This is a retrieval-time top-of-book observation, not consolidated liquidity.
- OKX XRP-USDT ticker event timestamp: 2026-11-18T22:41:45.765Z. Last 0.9637 USDT; bid 0.9636 for 3,323.12 XRP; ask 0.9637 for 1,105.23 XRP; spread about 1.038 bps; 24-hour volume 30.731M XRP. The quote was about 26.8 minutes old at the run-start reference time and was not normalized to USD because no contemporaneous USDT/USD leg was captured.
- No synchronized multi-venue Level 2 or sequence reconstruction was obtained. Opposite top-of-book imbalances across venues must not be treated as market-wide direction.

**Derivatives**
- Liqwall at 19:02 UTC: OI $949M, down 2.2% over 24h; average funding +0.0021% per 8h, Binance funding -0.0021%; 74.8% of Binance XRP accounts long; $5.4M liquidations, $2.1M longs and $3.3M shorts.
- TradRadar at 16:05 UTC: OI $1.32B across seven exchanges, up 1.94%; OI-weighted funding -0.0039% per 8h; at least $4.66M liquidations, $1.58M longs and $3.07M shorts; long/short account ratio 3.30.
- OI totals and 24-hour direction conflict. Provider universes and timestamps differ. Do not average.

**ETF flows**
- CryptoKeyhole: November 17 partial outflow of 3,251 XRP from two of four daily-readable funds; latest complete day November 13 was -9,967 XRP; November 9–13 complete sessions summed to -4.923M XRP.
- XRP Insights: November 17 +986 XRP and November 16 +158,134 XRP across six spot funds plus BITW; total reported holdings about 1.19B XRP and net assets about $778.2M.
- Alpha Finance: November 17 -$6.1M across five funds.
- These figures use different fund universes, units and reporting completeness. Preserve the disagreement; do not average.

**Exchange-wallet balances**
- XRP Insights’ November 18 08:00 UTC snapshot attributes 22.19B XRP to 707 wallets across 24 exchanges. Same-wallet balances fell 151.9M XRP over seven days and 390.1M over 30 days.
- The total includes 483.1M XRP in wrapped-asset/insurance reserves and substantial cold storage; 39.7% is not classified hot/cold. It is not tradable float. Wallet labels and coverage gaps remain material.

**Large wallet movements**
- CoinDesk’s XRPScan-based analysis reports two transfers of 140,351,238 XRP each, on November 6 and November 17, to two pre-activated wallets not identified as exchange deposit addresses. The funding trail reaches a Bitstamp-labeled wallet, but beneficial ownership is not established. Planned custody is plausible, not verified; internal wallet reorganization and other explanations remain possible.

### Institutional, regulatory and macro evidence

- **DBS–Circle, November 18:** DBS’s primary newsroom announcement says eligible institutional clients will be able to access direct USDC issuance and redemption, supported by near-instant 24/7 USD-USDC settlement. This is a bank-distributed USDC rail in Asia and a competing/complementary institutional payment pathway. It does not establish Ripple, XRP, XRPL, RLUSD or XRP demand, and realized production volumes were not verified. Source: https://www.dbs.com/newsroom/DBS_and_Circle_expand_institutional_access_to_USDC_in_Asia
- **Coinbase–Ripple:** the October 28 RLUSD launch across Coinbase Prime, Exchange and Retail remains verified. Coinbase Global Exchange collateral use was described as forthcoming, not as live collateral utilization. Source: https://ripple.com/ripple-press/ripple-and-coinbase-partner-to-expand-access-to-rlusd/
- **BNY–Ripple:** BNY’s October 27 announcement supports XRP/RLUSD custody for eligible clients; balances, purchases and collateral use remain undisclosed. Source: https://www.bny.com/corporate/global/en/about-us/newsroom/press-release/ripple-expands-strategic-digital-assets-collaboration-with-bny-across-custody-and-tokenized-trade-finance.html
- **SBI:** SBI’s Circle equity/JV/USDC distribution and SBI VC Trade’s RLUSD distribution remain separate relationships. Neither proves XRP purchases or collateral balances.
- **SBIC:** Tokyo, Nagoya and Osaka SBIC East/Central/West remain separate Japanese regional SME investment/consultation companies, not SBI Holdings. No verified XRP/Ripple relationship.
- **Exact phrases:** no new primary-source link for ASK Coin, “actual capital” or “SBIC, ChatGPT SBIC.” Existing phrase matches remain hypotheses, not verified relationships.
- **Kamilah/Camilla Stevenson:** Dr. Kamilah Stevenson remains verified as an iHeart guest; the candidate YouTube channel ID is not authenticated by a first-party cross-link. No channel-wide inventory is attributed.
- **Macro:** Reuters reported hawkish Fed signals, a 19-month dollar high and gold at a 14-month low; market pricing for a 50-basis-point December hike rose to 7.3% from 5.3%. WSJ reported its Dollar Index at 98.64, up 0.22% and a 52-week high. These are broad risk/liquidity context, not demonstrated XRP-specific causality.

### Prediction engine and nine-platform coordination

- The latest recorded repository ingestion remains run 44301868145 at 2026-11-18T12:13:54.617611Z: 34 receipts (22 raw, 12 digest-only), 21 source failures, 124 eligible and 361 excluded features, 3,235 feature-history records, 15 snapshots, 140 events and 107 scenarios; zero walk-forward forecasts.
- SEC submissions/companyfacts remain 0 with six failures because the monitored contact variable is not configured; CFTC weekly source families captured 0/2. Raw-to-feature rebuild from retained artifacts is not implemented; external anchoring is absent; drift is insufficient-data.
- The new Run 29 web/API observations have not been ingested through the repository receipt/feature pipeline. Their rendered-text hashes are not a substitute for raw wire receipts. No new walk-forward result or independent shadow evaluation exists.
- Forecast status remains NOT_ISSUED. No directional forecast is authorized.
- ChatGPT-to-GitHub access is verified, but repository permissions are admin/maintain/push/pull/triage and token scopes are not introspected. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks remain unverified. No external task dispatch, evidence transfer or red-team review occurred.
- The #1668 provider routes are proposed code only; no live provider credentials were tested and no external dispatch occurred.

### Next concrete action

1. Finish the expanded full repository suite and dependency audit on the new exact head created by this handoff update; inspect failures and fix only on the existing integration branch.
2. Complete the 68-workflow transitive audit and reconcile the remaining workflow/script/action supply-chain paths.
3. Resolve independent review, effective branch protection, CODEOWNERS ownership and automatic Pages/publication side effects before any merge.
4. Improve raw-source wire capture/retention, external timestamp anchoring, SEC/CFTC ingestion and deterministic raw-to-feature reconstruction; then continue leakage-safe walk-forward, baseline, calibration, drift and shadow evaluation.

**Disposition: NO MERGE.** The prior tested code head passed; the later head failed one stale metadata assertion; remediation is committed on the existing integration branch and exact-head verification is running. No main change, merge, deployment, release, secret rotation, Space restart, Kaggle submission, Databricks write, external-model dispatch, paper trade, funds transfer or real-money action occurred in Run 29.


## Run 29 supplemental reconciliation — institutional capital, regulation and source disagreements

### Repository and exact-head verification

- Main remains d5d22ac252f88637a490ed4c1598f8608b6cb786. No main commit was made by this run.
- The existing PR #1663 remains the sole consolidated V3/XRP integration PR. Before this supplement, its head was 29bd4ad0ba02ba990efdfafba212fcce0b6f92fd, 363 commits ahead, zero behind, 1,438 changed files and 68 changed workflow files. It remains draft, mergeable and has zero formal reviews.
- The complete recursive tree comparison still shows 1,739 main entries and 2,985 integration entries, with zero main paths missing from integration. The integration branch itself is not protected. Main reports protected=true, but detailed protection remains inaccessible (403); the visible fallback ruleset remains disabled.
- Exact full-suite verification passed on code/test head 17c5afe6f5d76db21ff1c47745d99da5044c70ac, run 44419516835: 4,277 passed, 1 skipped, zero failed, 11 warnings, 19 subtests passed, 118.59 seconds, 68.13% inclusive coverage and 77% legacy-core coverage.
- On that same head, dependency audit run 44419516809 and fail-closed push gate 44419516825 passed. PR-event run 44419528958 passed, but its core/full-suite jobs were skipped because #1663 is draft. Pages validation, money audit 44419528897, PR dependency audit 44419529095 and PR fail-closed gate 44419529212 passed.
- GitHub Actions cache budget was exhausted; the cache step emitted a warning only. It did not fail tests or security gates.
- After that verified head, the Run 29 evidence artifact, nine-platform map and two additional evidence-integrity tests were updated on the same branch. The current head 29bd4ad is therefore awaiting its own exact-head full-suite, dependency and fail-closed verification. The 4,277-test result is not being represented as a pass on 29bd4ad.
- The two new tests validate (1) Evernorth cash-versus-in-kind XRP contributions, SBI entity boundaries and regulatory distinctions, and (2) derivatives/ETF/wallet disagreement preservation, raw-wire limitations and forecast admission controls.
- No PR was merged or closed.

### Evernorth and SBI capital-flow reconciliation

Primary sources:
- Evernorth Q3 2026 10-Q: https://www.sec.gov/Archives/edgar/data/2092592/000162828026073871/xrpn-20260930.htm
- SBI November 2, 2026 investor presentation: https://www.sbigroup.co.jp/english/investors/disclosure/presentation/pdf/261102presentations.pdf
- SBI's $200M Evernorth investment announcement: https://www.sbigroup.co.jp/news/2025/1021_15831.html

Evernorth is a public XRP treasury company, not a spot ETF.

The SEC filing and SBI presentation reconcile the 473,276,430 XRP closing treasury as follows:
- 388,910,554 XRP contributed in-kind.
- 84,365,876 XRP purchased with pooled private-placement cash proceeds.
- Total: 473,276,430 XRP.

The $200M SBI Group cash investment was one component of the broader private placement. The filing reports approximately $214.1M of pooled private-placement cash used to purchase 84.366M XRP. Do not attribute the entire pooled purchase solely to SBI. Most of the closing XRP treasury was contributed in-kind, not bought on the open market.

At September 30, 2026, the filing reports 346,284,972 XRP at historical cost of approximately $846.575M, carrying value approximately $341.887M, cumulative impairment approximately $504.688M, including $271.037M of impairment in the first nine months of 2026. The closing total then incorporates the additional Ripple contribution and delayed in-kind funding. The 473M treasury is a company-reported combined closing figure, not a fresh November spot purchase.

SBI's November 2 presentation reports 36.1% voting rights and 20.5% economic interest in Evernorth, making SBI its largest shareholder by voting rights. The SEC beneficial-ownership table separately reports 39.9% of Class A voting shares, 7.5% of the Class C class and 21.4% combined common ownership through controlled/managed entities. The different dates, share classes and denominators are not reconciled; preserve both sets rather than forcing one percentage.

Additional capital-structure risks:
- $30M convertible notes, 4% payment-in-kind interest, 2031 maturity.
- Up to 5,218,935 shares under an equity line priced at 97% of VWAP and capped at 20% of trading volume.
- 3.073M warrants exercised through November 9 for approximately $35.3M; 8.666M warrants remained.
- No revenue was reported to date in the Q3 filing; nine-month net loss was approximately $32.9M, accumulated deficit approximately $185.6M, and nine-month digital-asset impairment approximately $271.0M.
- Q3 net income of approximately $155.3M was materially affected by fair-value changes in refundable investor advances; it is not operating revenue.
- BitGo Trust was named as initial custodian. Active lending, collateral and DeFi/yield strategies create counterparty, custody, liquidity and potential rehypothecation risks beyond a passive ETF.

Evernorth's XRP per share and NAV cannot be assessed without current fully diluted shares, note conversion, warrant exercise, ELOC usage, liabilities, cash and any XRP deployed or encumbered. Do not treat treasury size as equivalent to net new XRP demand.

### SBI's separate relationships — do not collapse the entities

1. **SBI Holdings and Ripple equity:** SBI stated on June 9, 2025 that it held approximately 9% of Ripple and was Ripple's largest external shareholder at that time. No updated 2026 beneficial-ownership percentage was verified. This is an equity stake in Ripple, not the Evernorth stake.
2. **SBI Ripple Asia:** SBI Group reports 60% voting rights as of September 30, 2026. It provides RippleNet software/services to financial institutions and remittance providers. ODL using XRP is commercially available in Japan through SBI Remit, Coins.ph and SBI VC Trade, with SBI disclosures describing corridors to the Philippines, Vietnam and Indonesia. SBI Ripple Asia itself states that it does not handle XRP; operational XRP use is through SBI Remit/partner exchanges. Public corridor volumes were not found.
3. **Circle SBI Japan K.K. / SBI Circle Holdings K.K.:** Circle's Q3 2026 SEC filing identifies the English legal name as Circle SBI Japan K.K.; the Japanese name is SBI Circle Holdings K.K. It is 50/50 owned by Circle and SBI, established in November 2025, with approximately $1.5M equivalent contributed by each side. Circle reported no significant operating results to date. This is separate from SBI Ripple Asia.
4. **SBI's Circle equity investment:** SBI Holdings and SBI Shinsei Bank invested $50M in Circle, split $25M each. This equity investment is separate from the 50/50 Japanese JV's initial capitalization.
5. **SBI VC Trade:** distributes USDC and RLUSD in Japan. XRPScan-labelled exchange wallets attributed to SBI VC Trade hold approximately 56.2M XRP, more than 99% classified cold in the cited dashboard. That is an exchange-wallet attribution, not SBI Holdings corporate XRP ownership.
6. **Evernorth:** SBI Group invested $200M cash and reports 36.1% voting rights/20.5% economic interest. This is separate from its approximately 9% Ripple equity stake.
7. **SBIC East/Central/West:** remain three separate regional Japanese SME investment/consultation companies, not SBI Holdings and not SBI Ripple Asia.

SBI's November 2026 presentation also reports group-wide Claude Mythos/Claude Security use. This is public corporate AI adoption evidence only; it does not establish a Claude account, API authentication, permissions or data flow to Barrot.

### Coinbase, Circle, Ripple and bank infrastructure

- **Coinbase–Circle:** Circle's Q3 2026 10-Q reports distribution costs under Coinbase agreements of approximately $331.3M for Q3 and $986.6M for the first nine months of 2026. Coinbase reported average USDC held in its products of approximately $22B in Q3 and described capturing roughly 50% of USDC economics. Circle's filing details platform allocations and ecosystem payment-base sharing after issuer retention and approved third-party participants; this is not 50% of gross reserve income. The current exact percentage of Coinbase's minority Circle equity stake was not established in the reviewed Q3 filing. Circle reported Q3 USDC circulation of approximately $73.879B and reserve income of approximately $657.6M.
- **Circle–Binance:** Circle's Q3 filing records a $100M private placement to Binance for 1.2M shares at $80.84. This is capital into Circle, not XRP investment.
- **DBS–Circle:** on November 18, DBS announced direct USDC minting/redemption access for eligible institutional clients with near-instant 24/7 USD-USDC settlement. Production volumes were not verified. This is a bank-led USDC rail in Asia and a competing/complementary institutional payment route, not a Ripple/XRP relationship.
- **Standard Chartered–Circle:** Standard Chartered launched integrated USDC minting/redemption for eligible institutional clients through its DIFC branch on July 2, 2026, without requiring direct Circle accounts.
- **Standard Chartered–Ripple–LMAX:** Standard Chartered announced live institutional RLUSD custody on XRPL through its DIFC branch on October 12. RLUSD collateral mirroring with LMAX is planned and remains conditional on final documents, testing, applicable laws, regulatory/internal approvals and jurisdictional readiness. Do not count this as live XRP collateral.
- **Coinbase–Ripple:** RLUSD is available on Coinbase Prime, Exchange and Retail across XRPL, Base and Ethereum. Coinbase Global Exchange collateral availability was described as forthcoming, not live in the announcement.
- **Ripple–Robinhood:** RLUSD is live on Robinhood Chain and Bitstamp by Robinhood; Robinhood plans to use RLUSD on XRPL for institutional settlement and integrate Ripple Treasury and Ripple Prime. XRPL settlement does not establish XRP as the settlement asset or prove XRP purchases.
- **BNY–Ripple:** BNY supports XRP and RLUSD custody for eligible clients and is RLUSD's primary reserve custodian. Client balances and XRP purchases remain undisclosed.

The bank network is multi-issuer: Standard Chartered supports USDC and RLUSD infrastructure; DBS supports USDC; BNY supports XRP/RLUSD custody. Do not interpret shared bank infrastructure as exclusive Ripple alignment or as measured XRP demand.

### Regulation

- OCC records show Ripple National Trust Bank, charter 25364, effective October 26, 2026, and Coinbase National Trust Company, charter 25390, effective November 6, 2026. These are national trust-bank/company charters, not proof of full-service deposit-taking commercial banking.
- Ripple's SEC appeals were dismissed August 7, 2025, leaving the $125,035,150 final judgment and injunction in effect. The 2023 district-court ruling distinguished direct institutional sales, which were unregistered securities offers, from programmatic secondary exchange sales, which were not securities transactions under the facts and manner of those sales. The SEC's August 8, 2025 Rule 506 waiver did not vacate the injunction or erase the final judgment. Do not claim a categorical ruling that XRP is or is not a security in every transaction.
- SBI VC Trade's RLUSD distribution is under Japan's Payment Services Act framework for foreign-issued electronic payment instruments; this is not evidence of XRP purchases.

### Spot, derivatives, exchange wallets, ETF flows and supply

**Spot**
- Kraken XRP/USD retrieval: $0.95815 last; bid $0.95835 for 5,218 XRP; ask $0.95840 for 961 XRP; spread about 0.522 bps; 24-hour volume 48.167M XRP; VWAP $0.98257443; high $1.00677; low $0.95485. The endpoint exposes no exchange event timestamp. Top-of-book only.
- OKX XRP-USDT event timestamp 22:41:45.765 UTC: last 0.9637 USDT; bid 0.9636; ask 0.9637; 24-hour volume 30.731M XRP. No contemporaneous USDT/USD leg was captured, so USD normalization was rejected.
- Rendered-response hashes are not independently captured HTTP wire hashes; no external WORM/timestamp anchor exists.

**Derivatives**
- XRPSONAR: OI approximately $861.3M; liquidations approximately $5.3M.
- Liqwall: OI approximately $949M, down 2.1%; average funding +0.0012% per 8h; liquidations approximately $5.5M.
- TradRadar at 20:30 UTC: OI approximately $1.29B across seven venues, down 2.12%; OI-weighted funding -0.0010% per 8h; at least $5.64M liquidations; 76.9% of accounts long.
- OI totals differ by roughly $429M across providers. Funding aggregates have opposite signs and venue-level funding is mixed. Preserve provider universes/timestamps; do not average.

**ETF flows**
- CryptoKeyhole updated at 22:55 UTC: no November 18 issuer files available; November 17 partial outflow of 3,251 XRP from two of four daily-readable funds; latest complete day November 13 was -9,967 XRP; November 9–13 complete sessions totalled -4.923M XRP; four-fund holdings approximately 1.071B XRP.
- XRP Insights: November 17 +986 XRP, provisional; November 16 +158,134 XRP; approximately 1.19B XRP holdings across its reported universe; net assets approximately $778.2M. The same publisher's exchange-wallet dashboard is not independent corroboration.
- Alpha Finance: November 17 -$6.1M across five funds; last seven sessions -$15.9M; 30 sessions -$10.9M; cumulative since launch approximately +$1.70B and +964.3M XRP. Different universe and units; do not average.

**Exchange-wallet balances**
- XRP Insights: 22.19B XRP across 707 wallets/24 exchanges at 08:00 UTC. Same-wallet balances fell 151.9M XRP over seven days and 390.1M over 30 days. Naive total balances rose 132.2M over 30 days because eight newly tracked wallets added 522.2M XRP; this is a coverage/label effect, not verified exchange inflow. The 30-day same-wallet decline and naive increase must both be preserved.
- XRP Insights' exchange labels include Upbit 6.47B, Coinbase 5.83B (including 152.1M non-customer cbXRP Base reserve), Binance 2.59B (including 327.4M Binance-Peg/charity reserves), Bithumb 1.78B, Uphold 1.70B, Kraken 958.5M and SBI VC Trade 56.2M. Cold/hot/unclassified split is approximately 49%/12%/39%; not tradable float.
- XRPSONAR reports 24.67B tracked exchange wallets and 24-hour net outflow of 24.9M XRP. The 2.48B difference from XRP Insights reflects different wallet universes; do not average. XRPSONAR's ETF trading volume is not net flow.
- XRPSONAR reports 63 whale movements over 1M XRP totalling approximately 408M XRP, excluding 15 same-owner transfers of 70.3M. CoinDesk's two 140,351,238 XRP transfers to non-exchange-identified wallets are a specific subset; do not add them without transaction-level deduplication. Beneficial ownership is unverified; planned custody and internal wallet reorganization remain competing hypotheses.

**Supply and ledger activity**
- XRPSONAR reports approximately 31.10B XRP in Ripple escrow and a 1B XRP unlock scheduled for December 1. Historically most gross unlocks have been re-escrowed; gross unlock is not net market supply.
- XRPSONAR reports RLUSD supply around $729M on XRPL and $2.78B across XRPL/Ethereum. This is stablecoin supply, not XRP demand or collateral.
- Its RWA dashboard reports 18 programs and $4.33B represented value, but only about $276M in distributed tokens; most remaining value is issuer-reported registry/notional representation, not freely transferable on-chain liquidity.
- November 17 ledger activity: approximately 3.3M transactions, 5,101 new wallets and 2,146 XRP burned. Activity does not establish economic settlement or XRP demand.

### Prediction and nine-platform status

- The last repository ingestion remains run 44301868145 at 12:13:54 UTC: 34 receipts (22 raw, 12 digest-only), 21 source failures, 124 eligible/361 excluded features, 3,235 feature-history records, 15 snapshots, 140 events, 107 scenarios and zero walk-forward forecasts.
- SEC EDGAR submissions/companyfacts remain zero with six failures because the monitored contact identity is not configured. CFTC weekly source families remain 0/2. Raw-to-feature reconstruction remains unverified; external anchoring remains absent.
- Run 29's public web/API research has not been ingested into the point-in-time feature store. Forecast status remains NOT_ISSUED. No directional forecast, shadow/paper trade or real-money action.
- ChatGPT-to-GitHub access is verified, but repository permissions include admin/maintain/push/pull/triage and token scopes are not introspected. SBI's public Claude adoption evidence does not verify a Claude connection to Barrot. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks remain unverified for Barrot. No external dispatch or evidence transfer occurred.
- PR #1668 remains blocked: it overlaps all three paths with #1663 and forwards original messages/tool definitions to Cloudflare Workers AI/OpenRouter, with Gemini opt-in. No redaction/data-classification gate, user data-egress approval or live provider authentication was evidenced. Its 1,209-test main-branch run is not the expanded integration suite. Do not merge it independently.

### Next concrete action

1. Finish the expanded full repository suite, dependency audit and fail-closed gate on the current head after the Run 29 evidence/test/handoff commits; diagnose any failure on this same branch.
2. Complete the 68-workflow transitive audit, including invoked scripts, artifacts, third-party actions and release/publication side effects.
3. Establish independent review, effective branch protection and non-self-only CODEOWNERS; resolve automatic Pages publication before any merge.
4. Continue raw-wire receipt capture, immutable external anchoring, SEC/CFTC ingestion, deterministic raw-to-feature reconstruction, synchronized multi-venue depth and leakage-safe walk-forward/calibration/drift/shadow evaluation.

**Disposition: NO MERGE.** The exact full suite passed on 17c5afe, but the current evidence/test successor must pass its own exact-head suite. Governance, independent-review, branch-protection, publication and transitive-security blockers remain. No deployment, release, secret rotation, Space restart, Kaggle submission, Databricks write, external-model dispatch, paper trade, funds transfer or real-money action occurred.


## Run 30 — 2026-11-18T23:36:21Z — exact-head full-suite closure, current microstructure, Q3 13F disclosures and provider-fallback conflict

### Repository and integration state

- Repository: https://github.com/Barrot-Agent/B-Agent
- Current main remains `d5d22ac252f88637a490ed4c1598f8608b6cb786`. No main commit was made by this run.
- Existing consolidated PR #1663: https://github.com/Barrot-Agent/B-Agent/pull/1663
- Integration branch: `integration/xrp-v3-mainline-successor-20261115T2101Z`
- Exact tested integration head before this Run 30 documentation update: `223d5bd687166da0080835636190896344f5c7f1`.
- At that head PR #1663 was 364 commits ahead, zero behind, 1,438 changed files, 68 changed workflow files, 518,399 additions and 6,754 deletions. It remains draft and mergeable, with zero formal reviews.
- Recursive trees: main 1,739 entries; integration 2,985 entries; zero main paths missing from integration. The integration branch itself is unprotected.
- Main's detailed branch-protection endpoint still returns HTTP 403. The visible `Fall Back` ruleset remains disabled. CODEOWNERS remains `* @Barrot-Agent`. Repository metadata grants this connector admin/maintain/push/pull/triage; token scopes were not introspected, so least privilege is not verified.
- The nine-platform map was updated on this branch in commit `871d0feb1150a6efcd65858d6761ca70ae0817df`. This handoff update creates a later documentation-only commit; exact-head CI must be rerun on the resulting head.

### Exact-head test and gate evidence

**Verified on exact code/test head `223d5bd`:**

- Full repository CI run 44421533967: 4,279 passed, 1 skipped, zero failed, 11 warnings, 19 subtests passed, 112.62 seconds.
- Inclusive package coverage: 68.13%.
- Legacy-core coverage: 77%.
- Dependency audit run 44421535384: success.
- Fail-closed push gate run 44421533908: success.
- PR-event CI run 44421543005: success; its standard/full-suite test jobs were skipped because #1663 remains draft. Pages job was validation-only.
- PR dependency audit 44421543207: success.
- PR money audit 44421542947: success.
- PR fail-closed gate 44421542962: success.
- GitHub Actions cache reservation emitted a warning because the configured cache budget is exhausted. The warning did not fail the suite or gates.

The 4,279-test result is an exact-head pass for `223d5bd`, not for the subsequent Run 30 map/handoff documentation commits. Those commits require their own exact-head CI. Main remains at `d5d22ac`; its last inspected CI run 44396364281 passed 1,207 tests, with two skipped and 78.10% coverage.

### Open PR inventory and classification

Thirteen PRs remain open. No PR was merged or closed.

| PR | Classification | Current disposition |
|---|---|---|
| #1663 | blocked | Sole consolidated V3/XRP integration; draft, no independent review; exact-head suite passed on 223d5bd; branch-protection, publisher, Pages and transitive-security blockers remain |
| #1668 | blocked | Provider-fallback candidate; all three changed paths overlap #1663; unsafe worker reactivation and unapproved external data egress |
| #1664 | unique/unreviewed | Paid-issue/product template pack; three documentation paths overlap #1663, but it is not an exact duplicate |
| #1665 | duplicate | Pylint `>=4.1.4` in `requirements-dev.txt` is already present identically in #1663; source PR remains open until the successor is merged and verified on main |
| #1666 | blocked | Kaggle dependency change widens `<1.6` to `<1.8` while the adjacent comment still says `>=1.6` pulls `jsonschema->rpds-py` (Rust); compatibility rationale unresolved |
| #1541 | blocked | MMI claim-fingerprint work; all five changed paths overlap #1663 and need reconciliation |
| #1265 | blocked | XRP ledger index-pointer migration; stacked branch; `.github/workflows/ci.yml` overlaps #1663 and prior workflow runs failed |
| #1450 | unique/unreviewed | Binance phase-one/escrow research; no path overlap |
| #1460 | unique/unreviewed | Institutional multirail, Binance and Kamilah research; no path overlap |
| #1440 | unique/unreviewed | XRP archive-validation trigger repair; no path overlap |
| #1437 | unique/unreviewed | XRP ledger source-addenda and snapshot-pointer repair; no path overlap |
| #1436 | unique/unreviewed | Binance XRP theft, issuer freezes and attacker-wallet graph; no path overlap |
| #1353 | unique/unreviewed | Lossless hash-verified XRP ledger archive/migration; no path overlap |

Backlog counts: ready 0; blocked 5; unique/unreviewed 7; duplicate 1; superseded 0. The duplicate #1665 is not closed before #1663 is merged and its content verified on main.

### PR #1668 — free inference fallback review

PR #1668 branch `integration/provider-failover-runner-20261118`, head `577656042804e40c87ca8cf736faa98be3b6f163`, changes exactly three paths that all overlap #1663:

- `.github/workflows/barrot-agent.yml`
- `scripts/barrot_agent.py`
- `tests/test_barrot_agent_script.py`

The workflow's actual triggers are `issues: labeled` and `workflow_dispatch`; it does not declare a schedule trigger, although its job condition contains a schedule branch. Manual dispatch requires `confirm=true`; issue-label execution restricts the sender to Barrot-Agent or the repository owner. The workflow nevertheless grants `contents: write`, `pull-requests: write` and `issues: write`, and loads Groq, Cloudflare, OpenRouter and Gemini secrets. It sets `BARROT_ENABLE_FREE_FALLBACKS=true`.

The fallback forwards the original messages, tool definitions and `tool_choice` to third-party model endpoints. No prompt redaction, data classification, secret filtering, user data-egress approval or live provider authentication/data-flow evidence was found. The integration branch intentionally quarantines this worker. Its current `scripts/barrot_agent.py` is a newer, more hardened version with token-budget preflight, explicit loopback-only local-provider validation and distinct TPM 413/429 handling; the #1668 script is an older version and must not replace it wholesale.

PR #1668's CI run 44416137636 passed its main-branch suite: 1,209 passed, two skipped, eight subtests, 78.10% coverage. That is not the expanded integration-branch full-suite matrix. The provider tests use mocked credentials and do not establish live provider authentication or availability.

Current public provider documentation establishes these limits:

- OpenRouter's `openrouter/free` router lists 24 free variants at $0 model-token pricing. Accounts without at least $10 in lifetime credit purchases are limited to 20 requests/minute and 50/day. It is not a guaranteed-capacity fallback; model/provider selection can change.
- Cloudflare Workers AI provides 10,000 Neurons/day on the Workers Free plan. GLM-4.7-Flash is a valid hosted model, but its published unit rates are $0.0605 per million input tokens and $0.40 per million output tokens; usage beyond the free allocation requires a paid plan or fails.
- Gemini 3.1 Flash-Lite has a free API tier, but Google's terms state that free-tier content may be used to improve its products. Paid-tier content is not used for that purpose. No Barrot Gemini key or consented data flow is verified.

Primary documentation:
- OpenRouter free models: https://openrouter.ai/collections/free-models
- OpenRouter free router: https://openrouter.ai/openrouter/free
- OpenRouter rate limits: https://openrouter.ai/docs/api-reference/limits
- Cloudflare Workers AI pricing: https://developers.cloudflare.com/workers-ai/platform/pricing/
- Cloudflare GLM-4.7-Flash: https://developers.cloudflare.com/workers-ai/models/glm-4.7-flash/
- Gemini API pricing and data-use terms: https://ai.google.dev/gemini-api/docs/pricing

The local loopback provider already present in the integration branch is the only zero-cost/no-third-party-egress option in this candidate set, but it requires a local inference runtime and is not active on the GitHub runner. No external model dispatch occurred. **PR #1668 remains blocked and must not be merged as-is.**

### Fresh XRP spot snapshot

Public API response views captured during this run:

**Kraken XRP/USD** — retrieval-time observation; Kraken's ticker response does not expose an exchange event timestamp.

- Last: $0.96578.
- Bid: $0.96567, 350 XRP.
- Ask: $0.96576, 5,178 XRP.
- Spread: approximately 0.932 basis points.
- 24-hour volume: 44,416,857.706 XRP.
- 24-hour VWAP: $0.98210349.
- 24-hour high/low: $1.00677 / $0.95485.
- Last price is approximately 1.662% below the reported VWAP.
- Ask quantity at the best level is approximately 14.79 times bid quantity.

Source: https://api.kraken.com/0/public/Ticker?pair=XRPUSD

SHA-256 of the exact rendered JSON response text: `633040c7e6887ed693d9bfc74ba17a5db67ee59fbc62ca105e5e2f007b0e13ec`.

**OKX XRP-USDT** — exchange event timestamp 2026-11-18T23:12:26.368Z.

- Last: 0.9661 USDT.
- Bid: 0.9661, 1,330.904766 XRP.
- Ask: 0.9662, 1,011.322665 XRP.
- Spread: approximately 1.035 basis points.
- 24-hour volume: 30,522,562.869 XRP.
- Bid quantity is approximately 1.316 times ask quantity.

Source: https://www.okx.com/api/v5/market/ticker?instId=XRP-USDT

SHA-256 of the exact rendered JSON response text: `c4c97fb0bdc29870cb88ef436f771d935f4ecb7740da8a8ec28f25370aa5bbeb`.

These hashes cover the rendered JSON response text, not independently captured HTTP wire bytes; no external WORM anchor or trusted timestamp is established. The top-of-book imbalances point in opposite directions across the two venues. Full synchronized Level 2 depth and sequence reconstruction were not captured. The OKX quote is USDT-denominated and was not normalized to USD because no synchronized USDT/USD conversion leg was obtained. No directional interpretation or forecast is justified.

### ETF-flow update and disagreement

- CryptoTuts tracker, as of the November 17 close: five reported ETFs, approximately $1.08B AUM, November 17 flow of -$6.14M and seven-day net flow of -$7.23M.
- XRP Insights: November 17 +986 XRP and November 16 +158.1K XRP, across six spot funds plus BITW; it excludes GXRP from flow totals while correcting a data gap.
- Prior trackers report different fund universes, units and completeness. These observations are not averaged. The CryptoTuts and XRP Insights figures are not issuer-level confirmations and should not be treated as independent source families without lineage checks.

Sources:
- https://cryptotuts.co/xrp/etf
- https://xrp-insights.com/

### Q3 2026 Form 13F disclosures — institutional exposure, not direct XRP flows

New reporting covers holdings as of September 30, 2026, filed mainly November 9–16. These are stale quarter-end snapshots, not November purchases.

**Goldman Sachs**

- SEC primary 13F cover page: CIK 0000886982, accession 0000886982-26-000647, report period September 30, signed November 16, 2026.
- The cover page reports 14,139 information-table entries, total table value approximately $1.167T and eight other included managers.
- Secondary reporting attributes more than $144M across five spot XRP ETFs at quarter-end, versus approximately $86.5M in Q2. The row-level information table has not yet been independently parsed in this run; retain the $144M as secondary-reported, not primary-row-verified.

Sources:
- SEC primary cover: https://www.sec.gov/Archives/edgar/data/886982/000088698226000647/xslForm13F_X02/primary_doc.xml
- Secondary position analysis: https://news.bitcoin.com/finance/goldman-sachs-xrp-etf-stake-144m-q3-xrp-crash/

**Intesa Sanpaolo**

- SEC primary 13F cover page: CIK 0001374384, accession 0001374384-26-000009, report period September 30, signed November 16, 2026.
- The cover page reports 243 information-table entries and total table value approximately $2.979B.
- Secondary row-level reporting attributes approximately $27.21M to XRP ETFs: 712,319 Grayscale XRP Trust ETF shares, reportedly unchanged from Q2, and 402,750 new reported Bitwise XRP ETF shares.
- The reported GXRP value increase from approximately $14.42M to $20.52M is a valuation change if the share count remained unchanged; it is not new share demand. The Bitwise share count is a new reported position, but the filing alone does not prove when or how the shares were acquired.

Sources:
- SEC primary cover: https://www.sec.gov/Archives/edgar/data/1374384/000137438426000009/primary_doc.xml
- Secondary row analysis: https://en.coinotag.com/intesa-sanpaolo-lifted-xrp-etf-holdings-27-21-million-q3

**Bank of America**

- SEC filing index: accession 0000070858-26-000589, filed November 16, 2026, period September 30, 2026.
- Secondary reporting identifies 13,260 shares of the futures-based Volatility Shares XRP ETF (XRPI), valued around $106,600. This is futures-product exposure, not a spot XRP ETF or direct XRP holding.

Sources:
- SEC filing index: https://www.sec.gov/Archives/edgar/data/70858/000007085826000589/0000070858-26-000589-index.html
- Secondary report: https://u.today/bank-of-america-joins-xrp-etf-holders-in-new-q3-sec-filing

A secondary compilation attributes approximately $29.4M of XRP-linked ETF holdings to seven banks, with Intesa contributing approximately $27.21M, more than 92% of that aggregate. Do not add that group total to Goldman's $144M without checking manager/account overlap. Form 13F reports investment-manager holdings of reportable securities; it does not prove proprietary bank balance-sheet capital, direct XRP wallet ownership, open-market spot purchases or unhedged directional exposure. It omits short positions and does not provide a complete hedge picture. The SEC cover pages verify manager and report period; exact information-table rows still require extraction and reconciliation.

Secondary group compilation: https://news.bitcoin.com/featured/7-major-banks-reveal-xrp-etf-holdings-latest-sec-filings/

### Prediction-engine and ingestion status

No new scheduled ingestion run was observed in Run 30. The latest recorded repository ingestion remains run 44301868145 at 2026-11-18T12:13:54.617611Z:

- 34 receipts: 22 raw-retained, 12 digest-only.
- 21 source failures.
- 124 eligible and 361 excluded features.
- 3,235 feature-history records, 15 snapshots, 140 events and 107 scenarios.
- Zero walk-forward forecasts.
- SEC EDGAR submissions/companyfacts: zero, with six configuration failures.
- CFTC weekly source families: zero of two.
- Raw-to-feature reconstruction from artifacts: not verified.
- External immutable anchoring: not established.
- Forecast issuance remains disabled.

The hourly/daily ingestion workflow is present on the integration branch but is not active on main. No directional forecast, shadow/paper trade, Kaggle submission, funds transfer or real-money action occurred.

### Nine-platform coordination

ChatGPT-to-GitHub access remains verified for repository/tree/PR/workflow reads and integration-branch writes. Repository metadata reports admin/maintain/push/pull/triage, but token scopes were not introspected and least privilege is not established.

Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks remain unverified for Barrot authentication, permissions and data flows. Public provider documentation and SBI's reported corporate Claude use do not establish a live Barrot connection. No external model dispatch or evidence transfer occurred.

### Next concrete actions

1. Run exact-head full-suite CI, dependency audit, fail-closed gate and money audit after the Run 30 map/handoff commits; do not rely on the 223d5bd result for later commits.
2. Complete transitive security review of all 68 changed workflow definitions, invoked scripts, artifacts and action dependencies.
3. Obtain independent review and verify effective main branch protection, required checks and bypass settings; resolve automatic Pages publication before any merge.
4. Keep #1668 blocked until provider data-egress policy, redaction, least-privilege workflow permissions, live authentication and full-suite tests are independently verified. Do not merge its worker activation.
5. Reconcile #1665 as an exact duplicate only after #1663 is merged and its Pylint line is verified on main; keep #1666 blocked until its Kaggle constraint/comment conflict is resolved.
6. Restore SEC/CFTC ingestion with a valid monitored SEC User-Agent configuration; capture raw bytes and externally anchor receipts; prove deterministic raw-to-feature reconstruction.
7. Continue synchronized multi-venue L2 capture, ETF issuer-row reconciliation, derivatives venue-universe normalization and leakage-safe walk-forward/baseline/calibration/drift/shadow evaluation.

**Disposition: NO MERGE.** Exact-head full-suite, dependency and fail-closed checks passed on `223d5bd`, but the Run 30 documentation successor still needs exact-head CI. Independent review, branch-protection verification, automatic-publication controls and the full transitive workflow audit remain blockers. No deployment, release, secret rotation, Space restart, Kaggle submission, Databricks write, external-model dispatch, paper trade, funds transfer or real-money action occurred.
