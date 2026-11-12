# Barrot XRP Intelligence — Run47

Updated: 2026-11-12T05:02:51Z

**Mission priority 1:** XRP intelligence and prediction-engine mastery. **Protected foundation:** Barrot V3 execution, orchestration, safety and verification.

## Repository state before the Run47 repair commit
- Main SHA: `84f28ee7755607236231545a14f3d093c1baaa85`
- Existing integration branch: `integration/xrp-v3-unified-main-20261111`; pre-repair head: `28eafc87d7a7c4709789c51bc19839264b12eff4`
- Existing PR: [#1661](https://github.com/Barrot-Agent/B-Agent/pull/1661), open/draft, mergeable state `unstable`.
- Branch ancestry: 2,082 ahead, zero behind main.
- PR diff: 1,047 files, 49 workflow files and 998 other paths.
- Recursive trees: main 1,388 entries/1,288 blobs; integration 2,306 entries/2,197 blobs.
- Open PR inventory: 374 total, 360 drafts, 14 non-drafts.
- Run47 uses the existing branch. No new branch or PR was created.

## Exact-head CI before repair
[Run 43157406477](https://github.com/Barrot-Agent/B-Agent/actions/runs/43157406477) tested `28eafc87d7a7c4709789c51bc19839264b12eff4`:
- Full suite: 3,500 passed, 5 failed, 8 subtests, 61.34% coverage, 68.93 seconds.
- Core suite: 716 passed, zero failed.
- Six-manifest dependency audit: passed, zero known vulnerabilities reported.
- Fail-closed gate: passed; automatic merge disabled.
- Wheel/installed-wheel verification: skipped because the full suite failed.

The five failures were test-contract/snapshot defects: (1) literal backslash in the event artifact expectation; (2) security test expected zero branch-tip paths although 17/17 recursive trees contain inherited `.config/gh/hosts.yml`; (3) stale non-workflow path counts; (4) CI failure narrative omitted the exact-head classification; (5) retention test expected three 90-day artifacts while the workflow defines four. Run47 corrects these assertions and refreshes the map. The resulting commit must pass its own exact-head full suite and wheel verification.

## Security: inherited credential-path hold
Run47 rechecked all 17 affected PRs: #1653, #1650, #1649, #1648, #1647, #1646, #1645, #1644, #1643, #1642, #1640, #1320, #1318, #1317, #1269, #1255, #1254.
- 17/17 open PRs target main.
- 17/17 complete recursive branch-tip trees contain `.config/gh/hosts.yml`.
- 0/17 PR changed-file inventories list the path.
- Main and active integration trees do not contain the path.
- No file contents were read; no branch history was rewritten.
- Provider-side OAuth revocation is not independently verified.

Preserve these branches. Do not read the file, force-push, rewrite branches or bulk-close PRs. The GitHub connector reports admin/maintain/push/pull/triage permissions; least privilege is not met. Main branch-protection details return HTTP 403; the visible fallback ruleset is disabled. GitHub Pages auto-publishes on main push and publication authorization remains absent.

## Run47 XRP observations — research-only, model-ineligible
- OKX XRP-USDT: last 1.0454, bid 1.0451, ask 1.0452; timestamp 04:47:04.271 UTC. At capture it was 946.7 seconds old, beyond the 900-second threshold.
- Kraken XRP/USD: last 1.04357, bid 1.04374, ask 1.04375; no exchange event timestamp. USDT/USD midpoint 0.998685. Normalized midpoint gap versus OKX was 0.00293%, but quotes were asynchronous and not executable.
- Fuelmaps 04:00 UTC six-venue book, mid $1.0487: within ±1% bids $12.5M/asks $11.6M; ±5% $29.0M/$15.5M; ±10% $34.3M/$16.6M. Binance and Bitget excluded; resting orders cancellable; snapshot may be up to 65 minutes old.
- Liqwall at 05:02 UTC: OI $1.16B, +1.4% over 24h; average funding +0.0055%/8h; $4.0M liquidations, $2.9M longs/$1.1M shorts; 75.5% of Binance XRP accounts long.
- TradRadar's prior Nov 11 19:05 UTC snapshot showed OI $1.57B, -0.97%, +0.0045% funding and 79.7% long accounts. Provider universes/timestamps differ; do not average.
- ETF flows through Nov 10: Alpha Finance reported -$10.4M Nov 9, -$7.6M Nov 10, +$1.3M over 30 sessions and $1.71B cumulative net inflows. Pre-Tick reported the same -$18M two-day SoSoValue-derived total. Not independent.

## Evernorth/SBI resale clarification
Primary source: [SEC Form 424B3, filed Nov 9, 2026](https://www.sec.gov/Archives/edgar/data/2092592/000162828026072223/evernorth-424b3.htm).

The prospectus registers up to 73,688,162 Class A shares: 19,102,635 issued, 31,392,746 potential Class C conversions, 22,953,128 potential Company Unit redemptions/exchanges and 239,653 Sponsor Warrant exercise shares. This is not current float or proof of completed sales. Selling-holder resales generate no proceeds for Evernorth.

SBI-controlled entities are listed with 9,431,914 Class A shares (36.1% of Class A outstanding as of Oct 22) and 2,359,038 Class C shares. Class C is non-voting, unlisted and non-transferable; the SBI group has a 39.9% maximum ownership restriction.

The prospectus's general resale section says registered shares are subject to lock-up provisions. The specific Lock-Up Agreements section names Ripple, Sponsor and Contributor Related Party Entity, not SBI. SBI's exact contractual lock-up status remains unresolved; do not label its Class A block freely tradable or definitely locked without executed SBI agreements/side letters or transfer-agent confirmation. No completed SBI resale or Evernorth XRP treasury sale is established.

## Event timeline and prediction engine
Run47 updates `research/xrp_intelligence/event_registry_current.json` to version `run47-2026-11-12` with 20 curated events, including six new spot, depth, derivatives, ETF-flow and Evernorth/SBI observations.
- Event timeline and scenario assembler are wired to the scheduled collector on integration.
- The registry hash authenticates the curated file only. All six new records have null raw publisher SHA-256 hashes.
- Scheduled ingestion is main-only and has not been verified on main.
- Scenarios are research-only hypotheses/counter-hypotheses; no probabilities or directional forecasts.

Implemented on integration: 47 public source definitions (45 scheduled), read-only collector, SHA-256 receipts/local hash chain, point-in-time SQLite prototype, four deterministic baselines, chronological walk-forward with purge/embargo, rolling temporal calibration, PSI drift diagnostics, source-lineage grouping and fail-closed Ed25519-attested forecast ledger.

Not production-verified: independent WORM/timestamp anchoring; durable replayable history; synchronized multi-venue spot/L2/derivatives/flow/collateral vintages; macro/regulatory/geopolitical event feed; serial/shared-source correction; heavy-tailed/empirical volatility baseline; 100 OOS samples and 100 independent shadow outcomes; production evaluator key; measured Brier/log-loss lift over all four baselines.

## Nine-platform status
- ChatGPT: GitHub API authenticated; connector permissions overprivileged.
- Claude, Grok, Gemini and Codex: authentication/data flow unverified.
- Copilot: no formal PR approval.
- Hugging Face: BUILD_ERROR.
- Kaggle: untested; no submission.
- Databricks: HTTP 403; no write.
- LunaRoute: repository-declared canonical brain; endpoint authentication/data flow unverified.
No external-model transfer occurred.

## Backlog and merge decision
- #1661: blocked active integration draft; Run47 exact-head checks required.
- #1660: superseded-source candidate; 972/972 paths represented in #1661, last blob comparison 942 identical/30 different; retain until verified successor merge.
- #1643: 670 paths represented, 661 identical/9 different; retain pending reconciliation.
- #1642: seven paths represented, zero identical/seven different; preserve unique prediction work.
- #1640: 280 paths represented, 244 identical/36 different; reconcile before closure.
- #1653 and the other 16 affected PRs remain open and security-held; preserve unique research, safety, topology and dependency work.
- No source PR closed. No merge performed.

**Next action:** verify exact-head full suite, wheel/installed Barrot V3/XRP mission, dependency audit and fail-closed gates on the Run47 commit. Then continue semantic review of 998 non-workflow paths and resolve least privilege, branch-protection visibility, provider-side revocation evidence and Pages publication authorization. Forecast issuance remains disabled.
