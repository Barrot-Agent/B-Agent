# Barrot XRP Mission Handoff — Current Verified State

Updated: 2026-11-06T19:48:57Z

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
- Code-bearing head verified before the current handoff refresh: `e525aab0ab5111dc623a9d57a0db8b359500aaff`.
- 155 changed files; non-draft; GitHub reports mergeable.
- Review threads: 22/22 resolved. Approving reviews: 0.
- Exact-head core suite: 626 passed, 8 subtests.
- Exact-head full repository suite: 1,065 passed, 8 subtests.
- Six-manifest dependency audit: passed; no known vulnerabilities.
- Fail-closed merge gate: passed; automatic merging remains disabled.
- Evidence:
  - Full CI: https://github.com/Barrot-Agent/B-Agent/actions/runs/42281864688
  - Dependency audit: https://github.com/Barrot-Agent/B-Agent/actions/runs/42281864661
  - Fail-closed gate: https://github.com/Barrot-Agent/B-Agent/actions/runs/42281864719
- The current handoff update is a documentation-only commit on this branch and must receive its own exact-head CI verification before merge.

### PR #1643 — XRP research archive

- Branch: `research/xrp-evidence-archive-20261104`.
- Exact current head: `b48478aa333ad4c71f97a6b3108dc8656a2f7af7`.
- 345 changed files; non-draft; GitHub reports mergeable.
- Review threads: 19/19 resolved. Approving reviews: 0.
- Exact-head core suite: 498 passed, 8 subtests.
- Exact-head full repository suite: 1,596 passed, 8 subtests.
- Six-manifest dependency audit: passed; no known vulnerabilities.
- Fail-closed merge gate: passed; automatic merging remains disabled.
- Evidence:
  - Full CI: https://github.com/Barrot-Agent/B-Agent/actions/runs/42282406359
  - Dependency audit: https://github.com/Barrot-Agent/B-Agent/actions/runs/42282406340
  - Fail-closed gate: https://github.com/Barrot-Agent/B-Agent/actions/runs/42282406472
- The full-suite run includes the new post-BLS market/reserve/ETF reconciliation tests and append-only receipt-correction checks.

The only changed-path overlap between #1640 and #1643 is `.github/workflows/dependency-audit.yml`; both branches have the identical blob `6515307991420ab90d8671034b13ac2eb56190b3`. Do not merge #1643 directly after #1640. After #1640 is merged and verified on main, create one consolidated research successor directly on that resulting main, transfer #1643's unique paths, and preserve the single identical workflow file.

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

## Latest XRP research artifact

Added to PR #1643:

- Artifact: https://github.com/Barrot-Agent/B-Agent/blob/research/xrp-evidence-archive-20261104/research/xrp_intelligence/20261106T193345Z-xrp-binance-reserve-etf-flow-cross-source-reconciliation.json
- Regression tests: https://github.com/Barrot-Agent/B-Agent/blob/research/xrp-evidence-archive-20261104/tests/test_xrp_binance_reserve_etf_flow_cross_source_reconciliation_20261106.py
- Two append-only receipt-metadata correction overlays:
  - `research/xrp_intelligence/20261106T194003Z-xrp-binance-reserve-etf-flow-receipt-hash-correction.json`
  - `research/xrp_intelligence/20261106T194446Z-xrp-binance-reserve-etf-flow-receipt-hash-correction-2.json`
- The original artifact blob SHA-1 is `7d632f7201ef1901239dc54270fa260cdcd97309`. Both corrections bind to that exact preimage and correct only two SHA-256 metadata transcriptions (TradRadar and CryptoTicker); the original excerpt bytes and market observations remain unchanged. The test verifies the derived corrected view. This correction overlay is research-archive logic, not a production feature-admission path.

Key observations, capture upper bound 2026-11-06T19:33:45Z:

- Kraken XRP/USD last $1.18304; best bid $1.18308; ask $1.18309; displayed spread 0.0845 bps; 24-hour volume 39.72M XRP; 24-hour VWAP $1.20425. Kraken exposes no provider timestamp, and its last trade is below the displayed best bid, so trade/book fields are not assumed synchronous.
- OKX XRP-USDT last 1.1830; bid 1.1830; ask 1.1831; spread 0.8453 bps; provider ticker snapshot 19:32:37.362Z; 24-hour volume 65.37M XRP. USD and USDT prices are not treated as synchronized or executable cross-venue quotes.
- Fuelmaps' 18:00 six-venue spot-depth snapshot shows 60.09%-67.78% displayed bid share across its bands, but is 93.75 minutes old and excludes Binance and Bitget. EdgeOrNot mixes Binance spot with OKX perpetual and is not combined with spot-only depth.
- TradRadar's 19:09 displayed seven-exchange snapshot reports $1.90B OI, -2.47% 24-hour OI, +0.0010% funding per eight hours, at least $11.96M liquidations, $11.36M long liquidations, $0.60034M short liquidations and a 3.90 long/short account ratio. Account counts are not notional exposure.
- SoSoValue via TokenPost reports three no-flow ETF trading days through Nov 5 and $1.81B cumulative net inflows/$1.41B net assets. XRP Insights separately reports a -149,487 XRP holdings delta over four settled days and 1.19645B XRP held. These are different measures/universes, not comparable AP cash flows.
- CryptoBasic reporting CryptoQuant shows Binance reserves rising 280M XRP from 2.35B to 2.63B Nov 3–5. XRP Insights' Nov 6 08:00 wallet-label snapshot reports 2.74B Binance XRP and +156.7M over seven days. TrackWhale's filtered large-transfer index reports -20.02M XRP net over seven days. Wallet universes, time windows and filters differ; no averaging and no open-market-purchase inference.
- BLS October employment release: +165,000 payrolls, 4.1% unemployment, +0.4% monthly and +3.1% annual wage growth, with +84,000 combined Aug/Sep revisions. Cross-asset reaction windows are not synchronized with XRP quotes.

Six competing hypotheses remain open: broad macro risk-off, leveraged-long unwind, Binance reserve replenishment/wallet movement, ETF-flow stall, displayed bid-depth absorption, and technical support exhaustion. Each has counterevidence recorded in the artifact. No directional forecast was issued; the dataset is model-ineligible.

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

Both integration PRs are non-draft and GitHub reports mergeable. Exact-head full suites, dependency audits and fail-closed gates pass. Both have zero approving reviews. Main is protected; detailed branch-protection requirements are inaccessible (HTTP 403). The visible fallback ruleset is disabled. Pages settings are inaccessible, and a prior main push triggered a public Pages deployment. Because merge would trigger that external deployment and its authorization is unresolved, neither PR is merged. No protection bypass is permitted.

## Next concrete sequence

1. Verify required branch-protection approvals/checks and obtain independent approvals if required.
2. Resolve authorization for the automatic Pages deployment side effect.
3. Re-run exact-head full suite, dependency audit and fail-closed gate after this handoff commit; merge #1640 only when all conditions and external-action authorization are satisfied.
4. After merge, verify merge commit, fetch main again, verify all merged files, inspect automatic workflow side effects and run main CI.
5. Create one consolidated research successor directly on the resulting main, transfer #1643's unique research paths, preserve the identical dependency-audit workflow, and reconcile #1642.
6. Only after the successor's content is verified on main, close the exact duplicate/superseded source PRs with cross-references.
7. Expand historical cross-venue data, external immutable retention, trusted evaluator keys, calibration, drift and shadow outcomes. Issue no directional forecast until measured out-of-sample performance and evaluator attestation support it.

## Forecasts and outcomes

- Directional forecasts issued: none.
- Shadow/paper trades: none.
- Real-money actions: none.
- Forecast outcomes: none.
