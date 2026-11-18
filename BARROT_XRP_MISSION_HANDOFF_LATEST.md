# Barrot XRP Intelligence — Latest Durable Handoff

**Evidence cutoff:** 2026-11-18T18:08:10Z  
**Mission priority:** XRP intelligence and measured prediction-engine mastery.  
**Foundation:** Preserve Barrot V3 for execution, orchestration, safety and verification.  
**Current main SHA:** `13c60af7079700a38b4226b9110d9c9377af7695`  
**Integration head audited:** `a40555db09583cbc824de446f415490b3c1081b3` on `integration/xrp-v3-mainline-successor-20261115T2101Z`.  
**Latest addendum:** Run 22 (2026-11-18T18:08Z) supersedes older current-state statements below; earlier sections remain historical evidence.  
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
