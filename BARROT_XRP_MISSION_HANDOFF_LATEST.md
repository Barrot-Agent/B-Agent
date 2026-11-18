# Barrot XRP Intelligence — Latest Durable Handoff

**Evidence cutoff:** 2026-11-18T12:18:00Z  
**Mission priority:** XRP intelligence and measured prediction-engine mastery.  
**Foundation:** Preserve Barrot V3 for execution, orchestration, safety and verification.  
**Latest addendum:** Run 14 (2026-11-18T12:18Z) supersedes older current-state statements below; earlier sections remain historical evidence.  
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
