# Barrot XRP Mission Handoff — Current Verified State

Updated: 2026-11-06T21:05:20Z

## Current verified run — 2026-11-06T21:05:20Z

This run supersedes earlier head, inventory, and CI summaries below. It does not change main.

### Repository and integrated work

- Main remains `9100dbacb5f9f1b973b053a65ef1e91e96b64f72`.
- The complete main Git tree was fetched recursively: 1,403 entries, 1,298 files, 493 Python files, 87 `tests/test*.py` files, and 86 workflow files; the tree response was not truncated.
- Main is protected. The branch object reports `protected=true`; the classic branch-protection endpoint returns HTTP 403. The only visible repository ruleset, ID 10863829, is disabled. Required review/check enforcement cannot be independently confirmed.
- A main push previously triggered the dynamic GitHub Pages build/deployment workflow; run [41799855489](https://github.com/Barrot-Agent/B-Agent/actions/runs/41799855489) completed successfully on the current main SHA. Pages configuration remains unreadable through the available connection, and no authorization for another merge-triggered public deployment has been established.

### PR #1640 — V3/core and XRP ingestion integration

- Branch: `integration/core-capabilities-mmi-structural-paper-20261104`.
- Code-bearing head inspected: `c528627f6171206b576e36add738d7a78cf17671`; 463 commits ahead, 0 behind; 155 changed paths; non-draft; GitHub mergeable state `clean`.
- Exact-head core suite: **626 passed, 8 subtests passed**.
- Exact-head full repository suite: **1,065 passed, 8 subtests passed**; inclusive coverage **57.57%**. Wheel build/install and packaged Barrot V3/XRP mission verification passed.
- Exact-head six-manifest dependency audit passed. Exact-head fail-closed gate passed and explicitly keeps automatic merging disabled.
- Evidence: [full suite 42287904725](https://github.com/Barrot-Agent/B-Agent/actions/runs/42287904725), [dependency audit 42287904754](https://github.com/Barrot-Agent/B-Agent/actions/runs/42287904754), [fail-closed gate 42287904888](https://github.com/Barrot-Agent/B-Agent/actions/runs/42287904888).
- There are no approving GitHub reviews. The green fail-closed gate is not an approval. Do not merge or bypass protections.
- This handoff append is documentation-only and follows code-bearing head `c528627f6171206b576e36add738d7a78cf17671`; the resulting handoff commit must receive its own exact-head checks before merge.

### PR #1643 — unique XRP research archive

- Branch: `research/xrp-evidence-archive-20261104`.
- Code-bearing head before this run's new spot receipt: `ae7d7534634f8ca7b5e35e351c50d1f83db52a38`; 494 commits ahead, 0 behind; 349 changed paths; non-draft; mergeable state `clean`.
- Exact-head core suite: **498 passed, 8 subtests passed**. Full repository suite: **1,607 passed, 8 subtests passed**. Six-manifest dependency audit and fail-closed gate passed.
- Evidence: [full suite 42287414992](https://github.com/Barrot-Agent/B-Agent/actions/runs/42287414992), [dependency audit 42287415164](https://github.com/Barrot-Agent/B-Agent/actions/runs/42287415164), [fail-closed gate 42287415097](https://github.com/Barrot-Agent/B-Agent/actions/runs/42287415097).
- The only path shared with #1640 is `.github/workflows/dependency-audit.yml`; its blob SHA is identical on both branches: `6515307991420ab90d8671034b13ac2eb56190b3`. The research branch must not be merged directly after #1640. Once #1640 is merged and verified on main, consolidate the research branch's unique paths onto the new main and inherit the expanded CI/wheel/coverage checks.

### New point-in-time spot receipt on #1643

- Added artifact: [20261106T210520Z XRP Kraken/OKX snapshot](https://github.com/Barrot-Agent/B-Agent/blob/research/xrp-evidence-archive-20261104/research/xrp_intelligence/20261106T210520Z-xrp-kraken-okx-live-spot-cross-venue-snapshot.json).
- Added regression test: [test_xrp_kraken_okx_live_spot_cross_venue_snapshot_20261106.py](https://github.com/Barrot-Agent/B-Agent/blob/research/xrp-evidence-archive-20261104/tests/test_xrp_kraken_okx_live_spot_cross_venue_snapshot_20261106.py).
- Capture upper bound: 21:05:20Z. Kraken XRP/USD last $1.17255, bid $1.17240, ask $1.17241, 35.85M XRP rolling-24h volume and $1.1958515 rolling-24h VWAP. OKX XRP-USDT last 1.1756, bid 1.1756, ask 1.1757, 64.67M XRP rolling-24h volume; its exchange timestamp is 21:05:06.565Z.
- The captured response-text SHA-256 values are retained in the artifact. Hashes cover the exact captured JSON text, not original HTTP wire bytes or independently timestamped immutable storage.
- The two last prices differ by approximately 0.26%, but USD/USDT conversion, latency, fees and transfer costs are not normalized. Top-of-book is not full depth. Venue volumes are not combined. The record is raw-snapshot-only and is not a model feature; no forecast is issued.
- The two new files were committed to the existing #1643 branch. Exact-head CI for the resulting branch head is pending and must be checked before the research PR is considered green again.

### Overlap and backlog classification

- PR #1642's one implementation commit `86d9f12f7e8133ea40c5b6742fd26c2ef79a17b1` is an ancestor of #1640: comparing #1642 to #1640 reports 462 commits ahead and 0 behind. Its seven changed paths are present on #1640's branch. Classify #1642 as **superseded by #1640**, but keep it open until #1640 is merged and the carried files are verified on main.
- PR #1641 remains a draft, incomplete experimentation foundation. Its own scope explicitly excludes model-backed hypothesis generation, multi-agent challenge/reproduction, objective-specific statistical evaluation, production XRP ingestion, walk-forward evaluation and calibration. Preserve it as **unique/incomplete**, not merge-ready.
- PR #1653 is a separate repository-knowledge-graph proposal. Its exact head `2e449ca28739a73b00dee021c9fb5f38819557c4` passed its full-suite job and fail-closed gate, but Copilot review identified unresolved high-severity issues: upstream CLI arguments are not transported as expected; `persistence=false` may still overwrite an existing graph artifact; repository state is not revalidated after indexing; submodules can fetch unapproved remotes; degraded indexing can be reported as synchronized; and fetch timeouts escape structured result handling. It also overlaps #1640 on `.github/workflows/ci.yml`. Classify #1653 as **blocked for security/correctness review**; do not merge.
- The live open-PR inventory contains **370 PRs: 354 drafts and 16 non-drafts**. The non-draft set is #1653, #1650–#1644, #1643, #1640, #1320, #1318, #1317, #1269, #1255 and #1254. Preserve #1317/#1318/#1320 as unique work, #1269 as a separate geometry workstream, and reconcile #1644–#1650 plus #1254/#1255 path-by-path against the integration branch before classifying any as duplicates. Do not bulk-close the 354 drafts.
- PR #1640 and #1643 each still have **zero approving reviews**. No PR was merged or closed in this run.

### Automation failure diagnosis

- GitHub Actions run [42291904318](https://github.com/Barrot-Agent/B-Agent/actions/runs/42291904318), issue-triggered Barrot Agent task for issue #1652, failed before repository repair began.
- The failure was Groq HTTP 429 token-per-minute rate limiting on `openai/gpt-oss-120b` (8,000 TPM limit; the retry still exceeded the limit). The workflow explicitly reported that bundle authoring/review failed safely and repository repair was not started. No repository change resulted. Treat this as a transient provider limit; do not infer repository damage or stop the recurring mission.

### DESIGNED / EXECUTED / VERIFIED boundary

- **DESIGNED:** mission registry, provenance contracts, point-in-time feature snapshots, fixed-horizon forecast records, walk-forward policy and counter-hypothesis process.
- **EXECUTED on PR branches, not main:** public ingestion workflow, raw-source receipt chain, SQLite feature store, forecast ledger, walk-forward evaluator, baseline comparisons, drift diagnostics, V3 safety/orchestration changes and the new spot snapshot.
- **VERIFIED:** exact-head tests and audits listed above apply only to their cited commit SHAs. The XRP collector is not running on main; the historical feature set is not yet sufficiently synchronized/mature; external WORM/timestamp anchoring, calibrated out-of-sample lift and production evaluator trust keys are not established. No directional forecast, paper trade or real-money action is authorized.

### Next concrete actions

1. Obtain a valid independent approving review and resolve the Pages deployment authorization boundary for #1640; do not bypass protections.
2. Verify the documentation-only #1640 handoff commit's exact-head full suite, wheel, dependency audit and fail-closed gate.
3. Verify the new #1643 snapshot/test commit's exact-head full suite, audit and gate. Keep #1643 separate until #1640 is merged and verified on main.
4. After #1640 is on main, consolidate #1643's unique research files onto that resulting main, preserving the identical dependency-audit workflow and the new snapshot/test.
5. Only after the successor is merged and verified on main, close #1642 with an explicit supersession cross-reference.
6. Reconcile the remaining non-draft dependency and feature PRs by exact changed paths and ancestry; preserve unique work.
7. Continue synchronized historical XRP ingestion and leakage-safe out-of-sample evaluation. No directional forecast until predictive lift and calibration are demonstrated.



This is the current-state handoff for the priority-1 XRP mission. Earlier run-by-run handoff revisions remain in Git history; this concise snapshot replaces an unbounded append log without rewriting branch history.

## Mission and invariants

- Priority 1: XRP intelligence and measured prediction-engine mastery.
- Foundation: Barrot V3 remains execution, orchestration, safety, verification and fail-closed control.
- Research must preserve source provenance, provider/published timestamps, source independence, disagreement, competing hypotheses and disconfirming evidence.
- No directional forecast until the dataset, leakage-safe out-of-sample evaluation, calibration, drift checks and trusted evaluator attestation all pass.
- No guaranteed returns, live orders, real-money actions, paper trades, funds transfers, secret rotation, Space restarts or deployments without their specific authorization.

## Repository truth

- Repository: `Barrot-Agent/B-Agent`.
- Current main SHA: `9100dbacb5f9f1b973b053a65ef1e91e96b64f72`.
- Main tree: 1,403 entries; 1,298 files; 493 Python files; 90 Python test files; 86 GitHub workflows.
- Main has not been modified or merged during this run.
- Main reports `protected: true`. Detailed branch-protection inspection returns HTTP 403; the visible fallback ruleset is disabled. Required-review settings therefore remain unverified.
- GitHub Pages settings are inaccessible. A prior main push triggered a public Pages deployment (run 41799855489). A merge would trigger an external deployment side effect whose authorization is not established.

## Active integration workstreams

### PR #1640 — V3/core and XRP ingestion foundation

- Branch: `integration/core-capabilities-mmi-structural-paper-20261104`.
- Exact current head: `43db1189fecbac99bb1a5399b29bd5c3eff30551`; 462 commits ahead of main, zero behind.
- 155 changed files; non-draft; GitHub reports mergeable state `clean`.
- Review threads: 22/22 resolved. Approving reviews: 0.
- Exact-head core suite: 626 passed, 8 subtests.
- Exact-head full repository suite: 1,065 passed, 8 subtests; coverage 57.57%.
- Installed-wheel verification: passed.
- Six-manifest dependency audit: passed; no known vulnerabilities.
- Fail-closed merge gate: passed; it explicitly reports merging disabled.
- Evidence:
  - Full CI: https://github.com/Barrot-Agent/B-Agent/actions/runs/42286060124
  - Dependency audit: https://github.com/Barrot-Agent/B-Agent/actions/runs/42286060101
  - Fail-closed gate: https://github.com/Barrot-Agent/B-Agent/actions/runs/42286060029
- The preceding `de934606...` head failed one handoff regression assertion because the test still expected a superseded artifact phrase/path. The assertion was updated to the current 19:33Z handoff evidence; the exact current head above then passed the complete suite. The cache-budget warning was non-fatal.
- This head has not been merged. The handoff refresh below is a new documentation-only commit and must receive its own exact-head verification.

### PR #1643 — XRP research archive

- Branch: `research/xrp-evidence-archive-20261104`.
- Exact current head: `ae7d7534634f8ca7b5e35e351c50d1f83db52a38`; 494 commits ahead of main, zero behind.
- 349 changed files; non-draft; GitHub reports mergeable state `clean`.
- Review threads: 19/19 resolved. Approving reviews: 0.
- Exact-head core suite: 498 passed, 8 subtests.
- Exact-head full repository suite: 1,607 passed, 8 subtests.
- Six-manifest dependency audit: passed; no known vulnerabilities.
- Fail-closed merge gate: passed; automatic merging remains disabled.
- Evidence:
  - Full CI: https://github.com/Barrot-Agent/B-Agent/actions/runs/42287414992
  - Dependency audit: https://github.com/Barrot-Agent/B-Agent/actions/runs/42287415164
  - Fail-closed gate: https://github.com/Barrot-Agent/B-Agent/actions/runs/42287415097
- This branch's full-suite job currently inherits the main-branch CI workflow version; the consolidated successor must inherit #1640's expanded CI, wheel verification and coverage gate after #1640 is merged.
- New research and append-only correction artifacts are listed below. They remain on this research branch, not main.

The only changed-path overlap between #1640 and #1643 is `.github/workflows/dependency-audit.yml`; both branches have the identical blob `6515307991420ab90d8671034b13ac2eb56190b3`. Current counts are 155 paths on #1640 and 349 on #1643, with one shared path. Do not merge #1643 directly after #1640. After #1640 is merged and verified on main, create one consolidated research successor directly on that resulting main, transfer the 348 unique research paths, and preserve the single identical dependency-audit workflow file.

## Architecture and implementation status

### DESIGNED

- XRP mission priority and V3 foundation boundary.
- Provenance-aware source registry, point-in-time feature contracts, forecast readiness requirements and nine-platform capability/authentication map.
- Walk-forward evaluation policy, counter-hypothesis review and forecast outcome ledger.

### EXECUTED on PR #1640, not on main

- Priority-1 mission registry and deterministic mission dispatcher.
- Read-only public collector with 21 endpoint definitions; 19 scheduled. Two free non-commercial XRPL public-node endpoints are excluded.
- Scheduled GitHub Actions workflow (hourly collection plus daily store backup); workflow executes only on main, so no scheduled main-branch collection is verified.
- SHA-256 raw-source receipts and receipt-chain manifests. Source terms/timestamp quality cause some records to be raw-only or digest-only.
- Point-in-time SQLite feature store with append-only triggers and as-of checks.
- Cross-run recovery path: restore cumulative SQLite from Actions cache or the newest unexpired daily artifact, append the new snapshot, then save cache/backup.
- Hourly raw-receipt artifacts and daily cumulative-store backup have 90-day retention. This is bounded recovery, not external WORM storage; cache is evictable and artifacts expire.
- Chronological walk-forward evaluator with naive, momentum, mean-reversion and volatility baselines and horizon embargo.
- Univariate feature-drift diagnostics.
- Forecast readiness ledger and deterministic SQLite record/scoring prototype.

### VERIFIED limits

- The collector is not merged to main and has no verified scheduled main run.
- The feature store is not populated with a sufficiently mature synchronized multi-domain historical XRP dataset.
- Coinbase historical candle pagination and long historical derivatives coverage remain incomplete.
- Some ETF/issuer/exchange-balance sources are captured as raw-only or digest-only, not normalized model features.
- Institutional collateral, custody, stablecoin supply, payment rails, macro and regulatory/geopolitical histories are not yet integrated into the scheduled normalized feature set.
- SQLite mutation guards are not adversarially tamper-proof; no independent timestamp authority or external WORM archive is configured.
- The walk-forward evaluator does not establish reliable cross-domain out-of-sample predictive lift. Calibration and drift stability are not established.
- Forecast issuance requires an Ed25519 signature from a trusted evaluator key. Production trust keys are not configured; readiness fails closed.

## Latest XRP research artifacts

The following new artifacts are on PR #1643's research branch and are not yet on main.

### 19:33Z cross-source market/reserve/ETF reconciliation

- Artifact: https://github.com/Barrot-Agent/B-Agent/blob/research/xrp-evidence-archive-20261104/research/xrp_intelligence/20261106T193345Z-xrp-binance-reserve-etf-flow-cross-source-reconciliation.json
- Regression tests: https://github.com/Barrot-Agent/B-Agent/blob/research/xrp-evidence-archive-20261104/tests/test_xrp_binance_reserve_etf_flow_cross_source_reconciliation_20261106.py
- Two append-only receipt-metadata correction overlays bind to original artifact blob SHA-1 `7d632f7201ef1901239dc54270fa260cdcd97309`; they correct only two SHA-256 metadata transcriptions, not source excerpts or market observations.
- Historical observation from this capture: Fuelmaps' 18:00 six-venue spot-depth snapshot showed 60.09%-67.78% displayed bid share across its bands, but it was 93.75 minutes old and excluded Binance and Bitget. EdgeOrNot mixed Binance spot with OKX perpetual and was not combined with spot-only depth.

### 20:10:59Z spot/derivatives/ETF/exchange-reserve update

- Artifact: https://github.com/Barrot-Agent/B-Agent/blob/research/xrp-evidence-archive-20261104/research/xrp_intelligence/20261106T201059Z-xrp-spot-derivatives-etf-exchange-reserve-reconciliation.json
- Regression tests: https://github.com/Barrot-Agent/B-Agent/blob/research/xrp-evidence-archive-20261104/tests/test_xrp_spot_derivatives_etf_exchange_reserve_reconciliation_20261106.py
- Eight source receipts preserve direct Kraken/OKX rendered ticker responses and normalized excerpts from derivatives, ETF, exchange-wallet and escrow trackers. Hashes cover the stored rendered JSON/excerpts, not original HTTP wire bytes. No common point-in-time cutoff is claimed.
- Kraken XRP/USD at capture upper bound 20:10:59Z: last $1.18394; bid $1.18391; ask $1.18392; displayed spread 0.0845 bps; rolling-24h volume 37.61M XRP; rolling-24h VWAP $1.201997. Last was 1.50% below rolling-24h VWAP and 1.80% below the UTC-day open. Kraken's ticker does not expose a provider timestamp.
- OKX XRP-USDT ticker snapshot 20:03:34.863Z: last 1.185 USDT; bid 1.1850; ask 1.1851; spread 0.8438 bps; rolling-24h volume 64.43M XRP; 24-hour open 1.2418 and low 1.1743. The last was 4.57% below the 24-hour open. USD and USDT quotes are asynchronous and not FX-normalized; no arbitrage or consolidated-price claim is made.
- No new synchronized spot-depth observation was captured. The prior Fuelmaps 18:00Z depth snapshot was 130.983 minutes old at this capture and is not carried forward as current.
- TradRadar's delayed 16:45Z seven-exchange perpetual snapshot reported $1.92B OI, -1.65% 24-hour OI, +0.0029% funding per eight hours and at least $12.87M liquidations ($12.27M longs; $0.59804M shorts). Alpha Finance's 14:44Z all-exchange dashboard reported $2.77B OI and $21.3M long versus $0.8254M short liquidations; its liquidation levels are modelled. The $850M OI disagreement (44.27% of TradRadar's figure) is preserved, not averaged.
- XRP Insights reports a Nov 5 holdings-derived ETF change of +110,214 XRP but a four-session Nov 2-5 change of -149,487 XRP across six spot ETFs plus BITW. CryptoKeyhole's Nov 5 row was partial at two of four funds. These are different universes/settlement states and holdings deltas, not AP cash creation/redemption records.
- XRP Insights' Nov 6 08:00Z wallet tracker reports 22.34B XRP across 701 attributed wallets and 24 exchanges; same-wallet balances were -34.7M over seven days and -152.6M over 30 days. Its naive total change was +359.4M and included two newly tracked wallets holding 512M XRP. The tracked balances include 487.7M XRP of wrapped-asset/other reserve backing (325.8M Binance XRP-BF2, 150.7M Coinbase cbXRP, 11.2M insurance/charity); this is not tradable customer float.
- XRP Insights reports 31.10B XRP in live XRPL escrow objects, but this run did not capture raw ledger receipts. Treat it as provider-derived locked escrow, not circulating or immediately tradable supply.

### 20:18:55Z append-only archive corrections

- Correction overlay: https://github.com/Barrot-Agent/B-Agent/blob/research/xrp-evidence-archive-20261104/research/xrp_intelligence/20261106T201855Z-archive-data-integrity-correction-overlays.json
- Regression tests: https://github.com/Barrot-Agent/B-Agent/blob/research/xrp-evidence-archive-20261104/tests/test_xrp_archive_data_integrity_correction_overlays_20261106.py
- The source-bound Evernorth overlay corrects the derived view of the Nov 4 capital artifact: the separate $1M Evernorth Facility lender is Ripple Labs, not NH/Kyobo; it also removes two duplicate Ripple facility graph edges in the derived view. The original blob remains unchanged.
- The source-bound Kraken overlay renames `open_24h_usd` to `daily_open_usd` and `last_vs_open_pct` to `last_vs_daily_open_pct` in a derived view. Kraken's official documentation says today's prices start at midnight UTC; the original artifact remains unchanged.
- Both overlays verify exact Git blob SHA-1 preimages and fail closed on mismatch. Their tests preserve original artifacts and apply changes only to deep-copied derived views.

The five competing hypotheses in the 20:10Z market artifact remain unresolved: short-term spot sell pressure, leveraged-long unwind, exchange-wallet supply interpretation, ETF holdings/cash-flow divergence and escrow supply overhang. No directional forecast was issued; the dataset remains model-ineligible.

## Backlog classification

Current open PR inventory: 369 total; 354 drafts and 15 non-drafts.

- **Active integration:** #1640.
- **Active research:** #1643.
- **Superseded, pending post-merge reconciliation:** #1642. Its feature-store/forecast-ledger code and tests are represented in the more developed #1640 branch; preserve its branch until the resulting main content is verified.
- **Exact duplicate, pending post-merge closure:** #1605. Its single market artifact has the exact same Git blob as the copy in #1643.
- **Superseded by #1640, pending post-merge closure:** #1645 (same workflow file blob), #1646, #1648, #1649 and #1650 (their individual dependency changes are included in the newer combined branch state).
- **Blocked/conflicting:** #1644 and #1647. Their diffs reintroduce workflows quarantined by #1640 and/or revert action versions on overlapping workflow paths. Do not merge as-is.
- **Older dependency candidates:** #1254 and #1255 appear superseded by newer legacy dependency versions in #1640; retain until exact post-merge reconciliation.
- **Unique/unreviewed, preserve:** #1317, #1318, #1320 and #1269. Do not bulk-close.

No PRs were merged or closed during this run.

## Nine-platform coordination

- ChatGPT-to-GitHub repository access: verified for this run.
- Copilot: prior one-off GitHub-hosted review activity; not a persistent authenticated data flow.
- CodeRabbit: one-off PR review/check service; not a persistent platform integration.
- Claude, Grok, Gemini, Codex, Hugging Face, Kaggle and Databricks: persistent authentication, permissions and data-flow evidence remain unverified.
- Do not describe nine-platform live coordination as active. Use least privilege and independent evidence when connections are actually tested.

## Merge decision and blockers

Both PRs are non-draft, conflict-free and report GitHub mergeable state `clean`. Their current exact-head full suites, dependency audits and fail-closed gates pass. Both still have zero approving reviews; the 22 and 19 review threads are resolved, but the repository review API records no `APPROVED` review. Main reports `protected: true`; detailed branch-protection requirements return HTTP 403, and the visible fallback ruleset is disabled. GitHub Pages settings remain inaccessible, and a prior main push triggered public Pages deployment run 41799855489. The user authorized merging only genuinely ready changes, not an unverified external deployment. Neither PR is ready to merge until the required approval state and deployment side effect are resolved. Do not bypass protection.

## Next concrete sequence

1. Obtain independent approving reviews and verify the actual branch-protection requirements; do not treat COMMENTED reviews saying "Approved" as GitHub approvals.
2. Resolve authorization for the automatic public Pages deployment side effect.
3. After this handoff commit, verify #1640's exact-head core/full-suite CI, six-manifest dependency audit and fail-closed gate. Merge #1640 only if all checks, approvals and external-action authorization are satisfied.
4. After any merge, verify the merge commit, fetch main again, confirm every merged file, inspect automatic workflow side effects and run main CI.
5. Create one consolidated research successor directly on the resulting main. Transfer #1643's unique research paths and new correction overlays, preserve the identical dependency-audit workflow, inherit #1640's expanded CI/coverage/wheel checks, and reconcile #1642.
6. Only after successor content is verified on main, close exact duplicate/superseded source PRs with clear cross-references. Preserve unique/unreviewed work.
7. Continue historical synchronized spot/depth/derivatives and institutional-flow coverage; configure externally immutable retention and trusted evaluator keys; expand leakage-safe walk-forward, calibration, drift and shadow-outcome evidence. Issue no directional forecast until measured out-of-sample performance and evaluator attestation support it.

## Forecasts and outcomes

- Directional forecasts issued: none.
- Shadow/paper trades: none.
- Real-money actions: none.
- Forecast outcomes: none.
