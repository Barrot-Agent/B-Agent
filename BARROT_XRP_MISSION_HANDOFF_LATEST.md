# Barrot XRP Intelligence — Latest Durable Handoff

**Evidence cutoff:** 2026-11-18T09:59:08Z  
**Mission priority:** XRP intelligence and measured prediction-engine mastery.  
**Foundation:** Preserve Barrot V3 for execution, orchestration, safety and verification.  
**Disposition:** NO MERGE. No deployment, secret rotation, Space restart, Kaggle submission, Databricks write, paper trade, funds transfer or real-money action.

## 1. Repository state and integration-first audit

- Repository: [Barrot-Agent/B-Agent](https://github.com/Barrot-Agent/B-Agent)
- Current main at audit: `e204c21100f3d059e2ba633d041fe8927b61ccaf`
- Integration source head audited: `a30de1b4ce04145e01f05322ece803905f9e317c`
- Active integration PR: [#1663 — Barrot V3 + XRP Intelligence, consolidated mainline successor](https://github.com/Barrot-Agent/B-Agent/pull/1663)
- PR base is current main; branch comparison: 280 commits ahead, zero behind; 1,418 changed files; GitHub reports mergeable, but PR remains draft.
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
