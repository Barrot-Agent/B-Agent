# Barrot XRP Intelligence — Canonical Mission Handoff (Run90)

**Captured:** 2026-11-13T13:20:58Z  
**Mission priority:** 1 — XRP intelligence and prediction-engine mastery  
**Protected foundation:** Barrot V3 remains the execution, orchestration, safety and verification foundation.

This is the current-state snapshot. Earlier Run79B–Run89C research, code and CI evidence remain preserved in Git history and supporting artifacts. Keep this file concise; do not restore the unbounded append-only handoff.

## 1. Repository state — VERIFIED

Repository: [Barrot-Agent/B-Agent](https://github.com/Barrot-Agent/B-Agent)

| Item | Current state |
|---|---|
| Main SHA | fb272b40966834754ec686f9ed3ab94123f09306 |
| Integration branch | integration/xrp-v3-unified-main-20261112 |
| Integration head at Run90 start | b4c15161ac41e8343820b3540d879e34df548d40 |
| Current integration head before Run90C handoff refresh | 2e0d0e95e4ada13a896ec683216a436142608eb5 |
| Main recursive tree | 1,381 entries; complete |
| Integration recursive tree | 2,351 entries; complete |
| Main → integration ancestry | 2,243 commits ahead; zero behind |
| Consolidated PR | [#1662](https://github.com/Barrot-Agent/B-Agent/pull/1662) |
| PR size | 1,105 files; 316,080 additions; 5,136 deletions |
| Changed-file composition | 50 workflows; 378 tests; 576 XRP research paths; 443 Python files including tests; seven public web files; 26 Markdown files |
| Open PR inventory | 375 total; 361 drafts; 14 non-drafts; 367 target main; eight target other branches |

PR #1662 is open, draft and mergeable, based on current main. It has zero formal reviews, zero approvals and zero review threads. Main was not changed. Run90, Run90B and Run90C updates add only documentation/research/security-audit artifacts to the existing integration branch; no new branch or PR and no runtime code change.

## 2. Exact-head CI — VERIFIED on Run90B head 2e0d0e9

- [Full CI 43432262745](https://github.com/Barrot-Agent/B-Agent/actions/runs/43432262745), job 131908414017: **3,557 passed, zero failed, eight subtests passed**, 61.72% inclusive coverage, 100.98 seconds.
- Core Tests job 131908413867: **729 passed, eight subtests passed**, 76% coverage, 11.88 seconds.
- Wheel build and installed Barrot V3/XRP mission verification: passed.
- [Dependency audit 43432262687](https://github.com/Barrot-Agent/B-Agent/actions/runs/43432262687), job 131908414050: all five manifest groups passed; zero known vulnerabilities reported.
- [Fail-closed gate 43432262681](https://github.com/Barrot-Agent/B-Agent/actions/runs/43432262681), job 131908413325: passed; automatic merge remains intentionally disabled.

These results are exact for 2e0d0e95e4ada13a896ec683216a436142608eb5. The final Run90C handoff/map-only descendant requires its own exact-head full suite, wheel/mission check, dependency audit and fail-closed gate. No result from a different SHA is substituted.

## 3. Current XRP market observations — DESCRIPTIVE ONLY

**Run cutoff: 2026-11-13T13:07:32Z. No forecast issued.**

### Spot

- OKX XRP-USDT provider event time 13:06:40.668Z: last **$1.0194**, bid $1.0192, ask $1.0193; 24-hour open $1.0343, high $1.0440, low $0.9974, volume 46.397M XRP. The quote was 51.3 seconds old at capture and passes the 300-second age test, but it was not ingested into Barrot's feature store or backed by a byte-exact RawReceiptArchive receipt.
- Kraken XRP/USD: last $1.02076, bid $1.02079, ask $1.02080; no provider event timestamp. Exclude from point-in-time admission.
- These are different quote currencies and unsynchronized venue observations. Do not infer executable arbitrage.

Sources: [OKX ticker](https://www.okx.com/api/v5/market/ticker?instId=XRP-USDT), [Kraken ticker](https://api.kraken.com/0/public/Ticker?pair=XRPUSD).

### Spot order-book depth

Fuelmaps six-venue snapshot at 12:00Z, midpoint $1.0237:

| Distance | Bids | Asks | Bid share | Coverage |
|---|---:|---:|---:|---:|
| ±0.5% | $8.4M | $6.7M | 55.6% | 6/6 |
| ±1% | $13.4M | $9.2M | 59.2% | 6/6 |
| ±2% | $19.0M | $11.3M | 62.7% | 6/6 |
| ±5% | $26.1M | $13.3M | 66.2% | 4/6 |
| ±10% | $30.5M | $14.8M | 67.2% | 5/6 |

Venues: Coinbase, OKX, Kraken, Bitstamp, Bitfinex and Gemini. Binance and Bitget are excluded by the provider's network access. The bid-heavy resting book is a constructive counter-signal, but the snapshot was about 67.5 minutes old at run cutoff, is not a full-market book, and resting orders can be cancelled. Largest displayed levels: $3.0M bid at $0.990, $2.6M bid at $1.021 and $1.9M ask at $1.025.

Source: [Fuelmaps XRP spot order book](https://fuelmaps.io/order-book/).

### Derivatives

Liqwall, 12:52Z:
- All-exchange vendor OI $1.12B, down 1.4% over 24 hours.
- Average funding +0.0078% per eight hours; Binance +0.0092%.
- $17.4M liquidations: $16.4M longs, $1.0M shorts.
- Binance accounts 74.8% long; top traders 67.7% long; Hyperliquid accounts 52% long.

Coinalyze via BitcoinLeverage, checked 12:10Z, only Binance and Bybit XRPUSDT perpetuals:
- Binance OI $303.47M, marked stale; funding +0.000653%; 74.87% accounts long; taker buy share 48.554%.
- Bybit OI $246.42M, fresh; funding -0.007873%; 81.22% accounts long; taker buy share 47.679%.
- Only two of 22 contracts are covered; liquidation coverage is partial.

The vendor aggregates and contract universes are not interchangeable. Funding differs by venue; do not average it. Long liquidation skew and long-account concentration support a crowded-long/deleveraging hypothesis. The bid-heavy spot book is a counter-hypothesis, not a directional signal.

Sources: [Liqwall](https://liqwall.com/coins/xrp), [BitcoinLeverage/Coinalyze](https://bitcoinleverage.com/xrp/funding-rate).

### ETF flow disagreement

- [XRP Insights](https://xrp-insights.com/data): Nov 9–12 net change -9,481,905 XRP over four settled sessions; 1,185,698,783 XRP held. Six US spot ETFs plus BITW; flow-excluded funds count as zero.
- [Alpha Finance](https://alphafinance.io/etf/xrp/): five-fund cohort; -$18.0M over seven sessions and -$2.8M over 30 sessions; Nov 9 -$10.4M, Nov 10 -$7.6M, Nov 11–12 displayed zero.
- [CryptoKeyhole](https://cryptokeyhole.com/etf-flows/xrp/): four of six funds read daily; Nov 11 complete flow -3,322 XRP; last five complete sessions Nov 5–11 -10,005,584 XRP; Nov 12 issuer files absent at its Nov 12 23:52Z read.

Different fund cohorts, issuer-file vintages and missing-file rules explain apparent disagreement. These trackers share issuer-file inputs and are not independent confirmations. Do not average their totals or treat zero as proof that every issuer reported no flow.

## 4. Macro, regulation and institutional rails

- [Glassnode Week 45, “Running on Empty”](https://research.glassnode.com/the-week-onchain-week-45-2026/), published Nov 11: eleven-major-stablecoin supply contracted $14.2B over 30 days through Nov 9, fastest since June 2022. US spot BTC ETFs had $1.6B net outflows over 20 sessions; Coinbase BTC premium remained negative; US two-year yield was 4.75% versus a 4.0% Fed policy rate. This is BTC/broad-market liquidity context, not XRP-specific causality. Counter-evidence in the same report: BTC long leverage near price was cleared, bids outweighed asks within 5% on Binance/Coinbase, and two larger BTC wallet cohorts accumulated while other cohorts distributed.
- [Reuters, Nov 12](https://www.reuters.com/legal/government/white-house-sends-cftc-sec-role-picks-senate-approval-2026-11-12/): Kristin Johnson and Steven Levine nominated for SEC roles; Matthew Rowland and Nathan Anonick nominated for CFTC roles. Senate confirmation remains pending. This changes the regulatory personnel timeline, not XRP's legal classification.
- [Standard Chartered, Oct 12 primary release](https://www.sc.com/en/press-release/standard-chartered-launches-rlusd-custody-and-joins-planned-collateral-integration-with-ripple-and-lmax-group/): RLUSD issued on XRPL is in live institutional custody through the bank's DFSA-regulated DIFC branch. LMAX collateral mirroring is planned/intended and remains subject to documentation, testing, regulatory requirements and approvals. RLUSD collateral is not native XRP collateral and does not establish XRP spot demand.
- Prior Run89 primary-source dossiers on Coinbase, Circle, Ripple, SBI, BNY, Evernorth, OCC charters, USDC and Japan's SBIC organizations remain in Git history. Preserve the distinction among native XRP, wrapped XRP, RLUSD, USDC, custody balances, reserve assets, collateral and actual cash capital.

## 5. Prediction engine — IMPLEMENTED versus missing

**Implemented on integration:**
- 48 public source definitions: 43 hourly, three weekly CFTC, two noncommercial XRPL node endpoints excluded; 46 scheduled sources.
- Read-only public-data ingestion workflow, guarded to run on main.
- SHA-256 per-run raw receipts and local receipt hash chain.
- Point-in-time SQLite feature store with append-only application controls.
- Four deterministic baselines: naive class prior, momentum sign, mean-reversion sign and Gaussian volatility normal.
- Chronological walk-forward evaluation with purge/embargo, temporal calibration, PSI drift diagnostics and source-independence grouping.
- Scenario/counter-hypothesis assembler and fail-closed forecast ledger requiring point-in-time feature snapshots and independent Ed25519 evaluator attestation.

**Not implemented or not production-verified:**
- No trained XRP-specific candidate prediction model exists. The walk-forward engine evaluates deterministic baselines; the forecast ledger validates readiness and records outcomes, but does not train a model.
- No mature synchronized historical spot/L2/derivatives/exchange-flow/collateral dataset.
- Event registry run71c has 73 curated events, **zero non-null raw publisher SHA-256 receipts and zero model-eligible events**. Its receipt status explicitly says publisher bytes were not captured into RawReceiptArchive.
- No independent WORM storage or trusted timestamp anchoring. Raw receipt retention is 90 days; per-run feature-store artifacts seven days; daily archives 90 days.
- Effective sample size counts greedy non-overlapping target windows only; it does not correct residual serial dependence or shared-source correlation.
- Paired block-bootstrap confidence intervals and source-clustered model-versus-baseline uncertainty are absent.
- PSI is univariate; multivariate/concept drift monitoring is incomplete. The volatility baseline is Gaussian, not heavy-tailed/empirical.
- No independent shadow cohort, production evaluator signing key or demonstrated candidate-model superiority.

Forecast admission requires at least 100 training samples, 100 OOS samples and 100 shadow samples; at least ten effective non-overlapping horizon windows in both OOS and shadow cohorts; two independent source groups; weighted calibration error no greater than 0.05; lower Brier score and log loss than all four baselines; and independent Ed25519 evaluator attestation.

**Forecast status: NOT_ISSUED. Accuracy: NOT_EVALUATED.** The current web observations are descriptive research only and have not been admitted to the feature store. No directional forecast, paper trade or real-money action occurred.

## 6. Nine-platform coordination — DESIGNED, NOT DISPATCHED

| Platform | Current verified status |
|---|---|
| ChatGPT | Current-session GitHub connector verified; reports admin, maintain, push, pull and triage; least privilege not met |
| Claude | No authentication or data flow verified |
| Grok | No authentication or data flow verified |
| Gemini | No authentication or data flow verified |
| Copilot | Review artifacts only; no formal approval on #1662 |
| Codex | No authentication or data flow verified |
| Hugging Face | Prior BUILD_ERROR; no deployment |
| Kaggle | Not tested; no submission |
| Databricks | Prior HTTP 403; no write |

LunaRoute remains a separate internal provider with unverified endpoint authentication. No external task dispatch, structured nine-platform evidence exchange or external-model data transfer occurred. Minority objections and source disagreements remain in local evidence records.

Compact current map: [Run90 nine-platform capability/authentication/data-flow map](research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_run90.json).


## 7A. Complete workflow security audit and current main health — VERIFIED

All 50 workflow files changed by #1662 were inspected on both main and integration. Five additional main control workflows and opencode.json were also inspected.

**Main scheduled health results:**
- [Main CI 43343513172](https://github.com/Barrot-Agent/B-Agent/actions/runs/43343513172): Tests and full repository suite passed.
- [Pillars Consistency Check 43430139937](https://github.com/Barrot-Agent/B-Agent/actions/runs/43430139937): failed as a read-only external health check, not as repository CI. Three blockers: Barrot's separate GitHub App credentials are missing (GITHUB_APP_ID, GITHUB_APP_PRIVATE_KEY, GITHUB_APP_INSTALLATION_ID); Databricks read-only SELECT 1 returned HTTP 403; Hugging Face Space reported BUILD_ERROR. Deployment-sync source validation and system-prompt fiction scan passed. The ChatGPT GitHub connector being authenticated does not mean Barrot's separate GitHub App is configured.
- [Barrot Sync 43343513347](https://github.com/Barrot-Agent/B-Agent/actions/runs/43343513347): workflow reports success, but actual sync failed because httpx is missing; it printed “sync skipped,” then git push was a no-op. The workflow suppresses both sync and push failures. Correction: its cut -c1-30 pipeline printed only the fixed 30-character label “Barrot running on LunaRoute - ”; zero API-key characters were printed, and the environment secret was masked. No key disclosure is evidenced.
- [Barrot Auto PR 43343513283](https://github.com/Barrot-Agent/B-Agent/actions/runs/43343513283): no-op validation, not a PR creator.
- [Pages deployment 43343511839](https://github.com/Barrot-Agent/B-Agent/actions/runs/43343511839): automatic public build/deploy succeeded after a main push. Authorization for the next publication of seven changed PR web files remains unresolved.
- [Cross Analysis 43428748553](https://github.com/Barrot-Agent/B-Agent/actions/runs/43428748553): scheduled read-only analysis succeeded.

**Integration containment across the 50 changed workflows:**
- Quarantined: ask-barrot, audio-ingest, barrot-agent, barrot-self-upgrade, barrot-speak, barrot-sync, capability-1-market-analysis, capability-9-data-resolver, databricks-bundle, diag-cf, diag-cf2, free-image-gen, ibm-bob-barrot-audit, knowledge-signal-cycle, knowledge-signal-cycle-btc, make-track, pingpong, signal_ledger, subagent-matrix, subagent-spawn, sync-huggingface, task-allocator, test-groq-chain, test-semantic-memory, webmcp-live-sandbox and write-lyrics.
- Gated instead of executed: A2A deployment requires separate deploy and secret-rotation confirmations plus exact main SHA; Barrot Ops requires per-action confirmation and exact source SHA; Coinbase paper-trader requires explicit per-run YES and exact main SHA and is artifact-only; Groq-based research/data workflows require explicit public/authorized-data confirmation and exact main SHA; sync-self-hosted-brain retains a hard false execution guard.
- Read-only/scheduled workflows include CI, dependency audit, cross-analysis, hover-bike updates, Riemann harvest, WebMCP monetization enrichment and the bundle smoke check. XRP public ingestion is read-only and main-only; it has not yet executed on main.
- Main-only control workflows: barrot-approve-pr is an exact-head approval-label gate and does not merge; barrot-auto-pr is a no-op validation; barrot-pr-automerge, barrot-autonomous-resolver and autonomous_self_deployment are disabled.
- Groq is distinct from Grok. No Groq or other external-model task was dispatched and no data was transferred in this run.

The Run90 workflow audit is linked below. These findings reinforce the NO MERGE decision; they do not authorize deployments, secret rotation, paper trades or external writes.


## 7B. Barrot V3 safety and public-web review — VERIFIED

**V3 preservation controls observed in code:**
- BarrotExecutor disables shell execution, confines paths, allows only a small command set, restricts Python execution to pytest/compileall and keeps Git operations read-only.
- BarrotActionLoop uses create-only file writes, exact unique-preimage compare-and-swap patches, bounded tests and rollback only when the current file exactly matches the action's post-write content.
- TermuxBridge restricts output to approved roots, rejects symlinks, uses create-only writes, fsync and refuses to overwrite differing existing files.
- b_agent.py requires an explicit external-transfer flag, an interactive terminal and the exact confirmation phrase before sending repository context to LunaRoute. Local repair requires a separate execution flag/phrase and a clean non-default worktree.
- MCPApprovalGate defaults to always-deny.

**Remaining code-level safety gaps:**
- Legacy MCPOrchestrator and direct deploy_databricks.py/deploy_huggingface.py code paths can invoke Databricks/Hugging Face/GitHub external writes without visible MCPApprovalGate wiring. The associated workflows are gated or quarantined, but direct-call enforcement and call-site reconciliation remain required before merge.
- repository_repair_loop rejects dirty/default worktrees, protected paths and symlinks, and writes tracked files only; however, it does not require a unique old-text match and does not automatically roll back partial edits after failed validation. Do not automate this repair loop until those controls are added.
- The safe autonomous action loop does not expose arbitrary shell execution. No direct deploy, MCP operation, local repair or Termux drop was executed in this run.

**Public web review:**
- web/latest_signal.json says NOT_ISSUED, but its status timestamp is 2026-11-10 and is stale.
- web/signal_accuracy.json says NOT_EVALUATED; the 45.5% historical variable-horizon value is isolated as unvalidated legacy data.
- web/landing.html and web/signals.html state that no directional XRP forecast is published.
- webmcp_monetization.js has a Gumroad license-verification POST path; purchase_url is null and checkout_available is false. No checkout or payment path was executed. If the verification tool is invoked, the submitted license key is transmitted to Gumroad; per-tool consent/allowlisting is required. webmcp-live-sandbox remains quarantined.
- Pages auto-deploys on main push. The seven public web files therefore remain a publication-authorization blocker even though the current signal/accuracy status is fail-closed.

**XRP public ingestion workflow:**
- 48 public source definitions; 43 hourly and three weekly CFTC endpoints, with two noncommercial XRPL node endpoints excluded; 46 scheduled endpoints.
- Read-only GitHub Actions workflow, hourly at minute 3 and daily at 00:15 UTC, main-only, with read-only contents/actions permissions.
- Raw receipt and receipt-chain artifacts: 90-day retention; per-run feature-store artifact: seven days; daily feature-store archive: 90 days.
- Coinbase historical backfill is bounded to 0–365 days and remains a read-only public-data task.
- No successful main-branch scheduled ingestion has been verified. GitHub artifact retention is not independent WORM storage or trusted timestamp anchoring.

## 7. Security, branch protection and merge decision

**NO MERGE.** PR #1662 is still draft, with zero formal reviews/approvals/threads. Its 1,105-file semantic review is incomplete.

- Main reports protected=true, but the detailed branch-protection endpoint returns HTTP 403. The only visible repository ruleset, “Fall Back” ID 10863829, is disabled. Required-check and approval enforcement cannot be independently verified.
- The GitHub connector reports admin/maintain/push/pull/triage; least privilege is not satisfied.
- Main opencode.json enables remote LunaRoute MCP and allows edit/bash/webfetch. Integration disables the remote MCP server and changes edit/bash/webfetch to ask.
- Main Barrot Agent is issue-label-triggered with contents/pull-request/issues write permissions. Integration quarantines it.
- Main A2A Worker deploys on pushes to a2a/** and uploads Cloudflare Worker secrets. Integration makes it manual-dispatch only, requires explicit deployment and secret-rotation confirmations, and verifies an exact main SHA.
- Main Barrot Operations has one broad external-change confirmation and can overwrite a Databricks workspace import and download a Kaggle dataset. Integration adds per-action confirmations and exact-source-SHA verification.
- Main Barrot Sync is push-triggered and writes BARROT_SYNC.md. It suppresses sync and git-push failures. Integration quarantines the writer. Correction: the main workflow's cut -c1-30 truncates the string to the fixed 30-character label “Barrot running on LunaRoute - ”; it prints zero characters of the API key. No key disclosure is evidenced by that line. The operational risk is the autonomous write and masked failures, not a demonstrated log leak.
- GitHub Pages previously deployed automatically on main pushes. PR #1662 changes seven public web files; authorization for the next public publication remains unresolved. This prior Pages setting was not rechecked in Run90.

The integration's exact-head CI pass does not resolve draft status, approvals, branch-protection visibility, least privilege, publication authorization or semantic review.

## 8. PR backlog — PRESERVE HISTORY

Complete open-PR inventory: 375. No source PR was closed.

| PR | Current classification |
|---|---|
| #1662 | Active consolidated integration; blocked draft |
| #1661 | Supersession candidate: zero commits ahead, 109 behind; all 1,072 changed paths overlap #1662 |
| #1660 | Supersession candidate: zero ahead, 290 behind; all 972 paths overlap |
| #1643 | Supersession candidate: zero ahead, 1,352 behind; all 670 paths overlap |
| #1642 | Supersession candidate: zero ahead, 2,257 behind; all seven paths overlap |
| #1640 | Preserve: diverged with one unique commit ahead; 280 changed paths overlap, so inspect same-path blob differences |
| #1653 | Preserve unique work: 18 commits ahead; six source-only paths |
| #1655 | Preserve unique work: 17 commits ahead; three source-only paths |
| #1659 | Preserve unique work: eight commits ahead; four source-only paths |
| #1615 | Preserve unique security work: three commits ahead; 13 source-only paths |
| #1614 | Preserve unique prediction work: 36 commits ahead; 27 source-only paths |
| #1644–#1650, #1254/#1255 | Dependency/workflow candidates; reconcile versions and differing workflow blobs before closure |
| #1320, #1318, #1317, #1269 | Unique/unreviewed safety or structural work; preserve |

Updated branch ancestry against the current integration head 2e0d0e9: #1661 is 0 ahead/111 behind; #1660 0/292; #1643 0/1,354; #1642 0/2,259; #1640 1/1,287; #1653 18/2,262; #1655 17/2,262; #1659 8/2,262; #1615 3/2,303; #1614 36/2,303. Path-overlap evidence remains as listed above. The first four supersession candidates must remain open until #1662 is merged, its content is verified on main, and exact duplicate status is confirmed. Do not close unique/diverged PRs or bulk-close drafts.

## 9. Durable artifacts and next action

- [Run90 current market/repository/prediction-readiness audit](research/xrp_intelligence/20261113T130732Z-run90-current-market-prediction-readiness-repository-audit.json)
- [Run90 nine-platform map](research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_run90.json)
- [Run90 workflow security and main-health audit](research/xrp_intelligence/20261113T131550Z-run90-workflow-security-main-health-audit.json)
- [Consolidated integration PR #1662](https://github.com/Barrot-Agent/B-Agent/pull/1662)
- [Run90B exact-head full CI](https://github.com/Barrot-Agent/B-Agent/actions/runs/43432262745)
- [Run90B dependency audit](https://github.com/Barrot-Agent/B-Agent/actions/runs/43432262687)
- [Run90B fail-closed gate](https://github.com/Barrot-Agent/B-Agent/actions/runs/43432262681)

**Next concrete action:** complete semantic reconciliation of all 1,102 PR paths and the 50 workflow changes; resolve least-privilege permissions, branch-protection visibility and Pages publication authorization; obtain a formal independent review; then verify exact-head checks before any merge. After a genuinely safe merge, verify the merge commit, fetch main again, inspect automatic workflow side effects and run main CI. Only then verify main-side read-only ingestion and independent raw-source anchoring. Build the actual XRP candidate model after synchronized historical data is available; add paired block-bootstrap/source-clustered uncertainty and independent shadow evaluation. Keep forecast issuance disabled until the complete admission gate passes.

No merge, main write, deployment, secret rotation, Space restart, external-model transfer, Databricks write, Kaggle submission, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or source PR closure occurred. The final Run90C documentation-only descendant must pass its own exact-head CI before it is treated as verified.
