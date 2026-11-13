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


## Run91 — 2026-11-13 — SBI/Evernorth resale and exact-head reconciliation

### Exact repository state

- Main SHA: `fb272b40966834754ec686f9ed3ab94123f09306`.
- Consolidated PR #1662: head `c0a6ce0b03f71518de8bde35ef3039f51cab4bc8`, open/draft, mergeable, 1,105 changed files, 2,244 commits ahead, zero behind, zero formal reviews and zero review threads.
- Exact-head CI: [43433094611](https://github.com/Barrot-Agent/B-Agent/actions/runs/43433094611) — 3,557 passed, 8 subtests passed, zero failures, 61.72% inclusive coverage, 76% core coverage; wheel built and installed mission verified.
- Exact-head dependency audit: [43433094601](https://github.com/Barrot-Agent/B-Agent/actions/runs/43433094601) — five manifest groups passed.
- Exact-head fail-closed gate: [43433094675](https://github.com/Barrot-Agent/B-Agent/actions/runs/43433094675) — passed with merge disabled.
- Open PR inventory: 375 total, 361 drafts, 14 non-drafts. #1660 and #1661 remain exact ancestors of #1662 (292 and 111 commits behind). Do not close them until the successor merges and its content is verified on main. Preserve #1640's unique commit and all unique/unreviewed work.
- No merge or main write occurred. Pages publication authorization, formal review, branch-protection visibility and full semantic review remain blockers.

### Evernorth actual-capital and SBI ownership reconciliation

Primary source: [Evernorth November 9, 2026 Form 424B3](https://www.sec.gov/Archives/edgar/data/2092592/000162828026072223/evernorth-424b3.htm).

- Reported closing treasury: approximately 473 million XRP as of October 9, 2026. Run135A reconciles 388,910,554.061435 XRP of in-kind contributions plus 84,365,876.3625 XRP from the identified cash-purchased lot. A further $49,995 of restricted cash was used to purchase XRP at closing, but the additional XRP quantity is undisclosed. Therefore the exact closing total remains unknown; do not fill the residual with an estimate.
- In-kind bridge: 600,000 advance-funding XRP; 211,319,096.061435 XRP from RippleWorks to Arrington XRP Capital Fund; 50 million XRP from the Larsen Lam Children's Remainder Trust; 126,791,458 XRP contributed directly by Ripple; and 200,000 XRP from delayed funding. The detailed components reconcile to 388,910,554.061435 XRP.
- Cash bridge: $214,049,995 advance cash, approximately $214 million used to purchase 84,365,876.3625 XRP at an average $2.53657058; $49,995 residual restricted cash was used at closing but its XRP quantity is not disclosed. Delayed funding added $10.5 million cash. Approximately $48 million of SPAC trust cash was released after redemptions; gross closing cash before expenses was approximately $272.6 million.
- SBI Holdings is a direct strategic investor through four controlled entities: SBI Holdings USA, SBI PE Holdings, SBI Venture Fund 2023A and SBI Venture Fund 2023B. At closing they held 9,431,914 Class A shares and 2,359,038 non-voting Class C shares, representing 21.4% of common stock and 39.9% of voting power. The Class C allocation enforces the voting cap. This is SBI Holdings, not any regional SBIC company.
- The November 9 resale prospectus registers 73,688,162 Class A shares and states ordinary selling-holder resales produce zero proceeds for Evernorth. SBI's 9,431,914 Class A shares are included. The specific six-month lock-up agreements name Ripple, the sponsor and the contributor-related-party entity, not the SBI Stockholders. SBI's registered shares therefore appear outside that specific lock-up, subject to other restrictions and the ownership cap. No actual SBI sale has been verified.
- The Cantor committed equity line remains contingent capacity: 5,218,935 shares at 97% of applicable VWAP, 4.99% ownership cap and 20% daily-volume cap. Run135A records zero proceeds as of the prospectus and no verified commitment-fee payment. Do not count it as cash raised.
- The separate $30 million, 4% PIK convertible note issued October 12 produced approximately $29 million net cash after a $1 million adviser fee. It is debt, not equity; specific XRP purchases from its proceeds are not proven. Its terms include contingent cash-settlement risk.
- Ripple-related credit is separate from equity and XRP purchases: the $10 million Company Facility had $9.7 million drawn as of October 7; the separate $1 million Evernorth Facility had no draws as of June 30; Pathfinder's separate facility and intercompany receivable remain separately accounted for. Post-close repayment status is not established.
- On-chain tracker reconciliation (Run75D): 13 attributed wallets held approximately 103.130 million XRP as of ledger 108293784 / 2026-11-13 01:42 UTC. A reported 370.347 million XRP transfer-out figure is not a net unique-token amount and its destinations are unattributed. It must not be called sales or missing XRP. The total does not arithmetically reconcile to the closing amount by approximately 200,138 XRP. The 84.366 million cash-purchased tranche is matched to a BitGo-activated trading wallet and custody wallets H/I/J; the 200,000 XRP delayed tranche has a 199,999.999 XRP Uphold transfer match, but issuer confirmation is absent.
- Custody/deployment conflict remains unresolved: the prospectus says 100% of XRP was in BitGo cold storage as of November 9, while management says yield strategies/DeFi participation commenced after closing. No protocol, amount, wallet or counterparty is named. Verified deployed XRP remains unknown. BitGo's $250 million insurance is shared among clients, not dedicated; no FDIC/SIPC protection is stated.

### SBI, Circle, Ripple and Coinbase network

- SBI Holdings/SBI Ripple Asia is a distinct joint venture with Ripple; SBI Group voting rights are reported at 60%. SBI Remit announced XRP-based remittance routes to the Philippines, Vietnam and Indonesia. The 2026 tokenized-deposit XRPL proof of concept is not production payment volume.
- SBI Holdings and SBI Shinsei Bank invested $50 million in Circle at IPO ($25 million each). SBI Group's Arc validator and token ecosystem role is on Arc, a separate L1, not XRPL. SBI VC Trade's USDC/RLUSD distribution and JPYSC work are stablecoin distribution, not proof of XRP purchases.
- Circle's Q3 SEC filing records Binance's $100 million equity investment in Circle (1.2 million shares at $80.84). Circle's Q3 distribution costs payable to Coinbase ($331.3 million) and Coinbase's stablecoin revenue ($306.9 million) are different accounting measures, not one-for-one.
- Coinbase reported $3.038805 billion of customer crypto collateral received and $2.731034 billion returned for the nine months ended September 30, 2026. This is aggregate multi-asset collateral; no XRP-specific amount is disclosed.
- Standard Chartered RLUSD custody on XRPL is live through its DFSA-regulated DIFC branch. LMAX collateral mirroring remains planned and conditional. Ripple's announced $150 million LMAX financing has no verified disbursement in the reviewed evidence.

### Identity and exact-phrase research corrections

- SBIC East is Tokyo Small and Medium Business Investment & Consultation Co.; SBIC Central is Nagoya Small and Medium Business Investment & Consultation Co.; SBIC West is Osaka Small and Medium Business Investment & Consultation Co. They are separate regional sister companies, not SBI Holdings subsidiaries.
- Tokyo SBIC's February 2025 ChatGPT seminar was free and open to investee and general companies, co-hosted with the Tokyo Chamber of Commerce and supported by Japan Finance Corporation. A separate June 2025 manufacturing program was investee-company training. Neither establishes an OpenAI partnership.
- “Ask Coin” appears as an inactive/untracked exchange listing with no reserve data; no canonical XRPL issuer or deployment was verified. Permission Coin's ASK token is a separate Base/Polygon asset.
- One TEDx Talks video is verified for Kamilah Stevenson: [Thinking Your Way Into Health](https://www.youtube.com/watch?v=VSgeDgOCexs). The personal YouTube channel candidate remains unverified; do not attribute other channels or merge Camilla/Kamilah identities.

### Prediction and data eligibility

- Forecast status remains `NOT_ISSUED`. Run135A and Run75B/75D are research-only; raw publisher bytes and SHA-256 receipts were not captured. They are not model-eligible datasets.
- The four deterministic baselines and chronological evaluation exist, but no trained XRP-specific candidate, paired block-bootstrap uncertainty, source-clustered uncertainty or independently validated shadow performance exists.
- The scheduled public ingestion workflow remains on the integration branch, not verified as a successful main-branch service. GitHub artifact retention is finite and not external WORM anchoring.

### Next action

Finish independent semantic review of all 1,105 changed paths and the 50 workflow changes, obtain formal approval, resolve branch-protection visibility and Pages-publication authorization, then merge #1662 only through normal protections. After merge, fetch main, verify the merge commit and files, run main CI and inspect automatic deployment effects. Only then activate scheduled ingestion on main and improve raw-receipt/WORM durability. Do not issue a directional forecast until synchronized history and out-of-sample model evidence pass the admission gate.

No merge, deployment, paper trade, real-money action, Kaggle submission, Hugging Face restart, Databricks import, secret rotation, force-push, history rewrite or source PR closure occurred.
