# Handoff addendum — 2026-11-06T22:18:37Z

## Automation run 8 — current verified state

### Main and repository inventory

- Main is unchanged at `9100dbacb5f9f1b973b053a65ef1e91e96b64f72`.
- Main tree at that SHA: 1,298 files, 493 Python files, 87 test files and 86 workflow files.
- Open PR inventory: 370 total; 354 drafts and 16 non-drafts.
- No branch was merged, no PR was closed, no deployment was initiated, and no secret or external service was changed.

### PR #1640 — Barrot V3 and XRP ingestion foundation

- Current code-bearing head: `152ef7c984617833d65eca83778bafe7dadb37d0`.
- 475 commits ahead of main, zero behind; 155 changed paths.
- Current branch tree: 1,349 files, 533 Python files, 115 test files and 87 workflows.
- Exact-head core suite: 629 passed, 8 subtests passed.
- Exact-head full repository suite: 1,069 passed, 8 subtests passed.
- Inclusive package coverage: 57.57%, above the 53% threshold. The full-suite coverage job measures all of barrot_agent; major packages are no longer excluded. The CI guard tests this scope.
- Installed-wheel verification passed: Barrot V3, the XRP mission registry and canonical data assets loaded from the built wheel.
- Strict dependency audit passed across all six manifests: requirements.txt, requirements-dev.txt, requirements.tx, hf_space/requirements.txt, legacy/requirements_legacy.txt and the 15 PEP 621 dependencies in pyproject.toml.
- The fail-closed gate passed as a check, but its job explicitly says automatic merge is disabled. It did not merge anything.

Exact-head evidence:
- [CI — 1,069 full-suite tests, inclusive coverage and wheel verification](https://github.com/Barrot-Agent/B-Agent/actions/runs/42302955781)
- [Six-manifest dependency audit](https://github.com/Barrot-Agent/B-Agent/actions/runs/42302955773)
- [Fail-closed gate; merge intentionally disabled](https://github.com/Barrot-Agent/B-Agent/actions/runs/42302955891)

### Feature-store continuity correction executed on #1640

The scheduled ingestion workflow previously trusted a partial cache restore as if it were the latest feature-store state. With unique per-run cache keys, a restore-key match can be stale; the workflow could therefore skip the newer artifact fallback. The cache service also emitted a read-only budget warning during CI. The scheduled ingestion workflow has not yet run on main, so this is a code-path risk corrected and regression-tested on the PR branch, not a claim of live production recovery.

The current branch now:
- Trusts Actions cache only when the exact cache key hits.
- Treats a partial cache restore as insufficient and restores the newest successful main-branch per-run feature-store checkpoint first (7-day retention).
- Falls back to the daily/manual feature-store archive (90-day retention).
- Uploads a SQLite checkpoint after every successful ingestion run (7-day retention), while retaining the daily/manual database and walk-forward archive (90 days) and raw-source receipt artifacts (90 days).
- Searches up to 30 pages of 100 completed main-branch ingestion runs. Empty pages with no qualifying successful scheduled/manual runs do not terminate the search prematurely.
- Records the restore strategy, retention windows and search bound in the run summary; both feature-store and forecast-ledger contracts now describe the same policy.
- Still fails closed to a recorded bootstrap if no unexpired checkpoint/archive is found within the search bound. Rebuilding the feature store automatically from raw-source artifacts is not implemented.

The full-suite run on the code-bearing head passed the workflow and documentation regression tests. The workflow itself is restricted to main; no scheduled main-branch ingestion run is verified while #1640 remains unmerged.

### PR #1643 — XRP research archive

- Current head: `c0ebe4a1c17ace7b6b41c6a03c510b9e0c8f415c`.
- 509 commits ahead of main, zero behind; 363 changed paths.
- Current branch tree: 1,658 files, 627 Python files, 223 test files and 86 workflows.
- Exact-head core suite: 498 passed, 8 subtests passed.
- Exact-head full repository suite: 1,630 passed, 8 subtests passed.
- Six-manifest dependency audit passed.
- Fail-closed gate passed with automatic merge disabled.

Exact-head evidence:
- [CI — 1,630 full-suite tests](https://github.com/Barrot-Agent/B-Agent/actions/runs/42303235184)
- [Six-manifest dependency audit](https://github.com/Barrot-Agent/B-Agent/actions/runs/42303235259)
- [Fail-closed gate; merge intentionally disabled](https://github.com/Barrot-Agent/B-Agent/actions/runs/42303235003)

### New point-in-time XRP evidence

Two immutable timestamped artifacts and regression tests were added to the existing #1643 research branch; no new PR was created.

1. [22:00:25Z spot freshness and ETF-flow vintage reconciliation](https://github.com/Barrot-Agent/B-Agent/blob/research/xrp-evidence-archive-20261104/research/xrp_intelligence/20261106T220025Z-xrp-live-spot-etf-flow-vintage-reconciliation.json)
2. [22:13:36Z spot snapshot and ETF fund-universe reconciliation](https://github.com/Barrot-Agent/B-Agent/blob/research/xrp-evidence-archive-20261104/research/xrp_intelligence/20261106T221336Z-xrp-live-spot-etf-fund-universe-reconciliation.json)

At the 22:13:36Z capture:
- Kraken XRP/USD: $1.18002 last; $1.18001 bid and $1.18002 ask; 33.80M XRP rolling-24-hour volume; $1.19227745 rolling VWAP; $1.17085 rolling low. Kraken's response had no provider timestamp.
- OKX XRP-USDT: 1.1808 last; 1.1807 bid and 1.1808 ask; 62.14M XRP rolling-24-hour volume; 1.2249 rolling-24-hour open; 1.1723 low. Its provider timestamp was 22:06:05.374Z, making it 450.626 seconds old at capture and therefore older than the collector's 300-second live-feature age limit.
- The 0.0661% last-price difference is not an executable arbitrage observation: USD and USDT are not normalized, Kraken has no provider timestamp, and OKX is beyond the live-feature age gate. Only top-of-book size was captured; no multi-level depth or market-impact measure is available.
- Both prices were within roughly 0.8% of their respective 24-hour lows. This is context, not a directional signal.

ETF holdings/flow reconciliation:
- XRP Insights reports a Nov 5 holdings-derived change of +110,214 XRP and a Nov 2–5 aggregate of -149,487 XRP across four settled trading days. Its broader universe is six US spot ETFs plus BITW; it includes XRPR and BITW, while GXRP flows are excluded because of a capture gap even though GXRP holdings remain in holdings totals. Its flow is computed from day-over-day issuer-reported holdings, not a direct issuer creations/redemptions report. BITW index rebalancing, XRP fee accruals and other non-creation/redemption holdings changes can be counted as flow. XRPR's exposure is partly held through another XRP exchange-traded product.
- CryptoKeyhole's latest complete day is Nov 4: -3,339 XRP across four funds, with 1,076,809,224 XRP held. Nov 5 is partial at 3/4 funds and -3,339 XRP, with Franklin XRPZ pending. No Nov 6 file from its four-fund universe had appeared by its 21:52Z update. Its daily universe is XRP, XRPZ, XRPC and TOXR; it excludes GXRP, XRPR and BITW. Its five complete days Oct 29–Nov 4 sum to +1,837,670 XRP.
- These totals are not comparable: fund universes, completeness and holdings-delta treatment differ. They are separate aggregators using issuer holdings, not independent economic confirmation. Do not average them or call the difference a primary-source contradiction.

Derivatives freshness:
- The newest previously verified TradRadar observation remains 20:55Z (78m36s old at the 22:13:36Z capture); Aperiodic's 18:40Z observation was 3h33m36s old.
- The newly retrieved TradRadar search result timestamped 19:50Z was older than the archived 20:55Z observation. No newer derivatives observation was admitted, and no current multi-level depth ladder was captured.

No directional forecast was issued. No paper trade, real-money action or external execution occurred.

### Prediction-engine readiness — precise boundary

- The PR #1640 collector defines 21 public endpoint records, 19 scheduled; two free non-commercial XRPL public-node endpoints are excluded by default. Capture scope includes Binance spot/perpetual, Coinbase and Kraken spot, ETF/issuer and exchange-balance sources. This is not yet broad multi-venue derivatives or institutional/macro coverage; OKX and other derivatives venues are not in the scheduled normalized set.
- The deterministic walk-forward evaluator compares four baselines (historical class prior, momentum sign, mean-reversion sign and volatility-aware normal baseline), uses chronological splits with a horizon-sized embargo, and reports Brier/log-loss/accuracy plus calibration diagnostics. Current evaluation is single-feature/single-venue/single-pair and has not demonstrated stable out-of-sample lift from a mature synchronized XRP dataset.
- Calibration bins are diagnostic; fitted probability recalibration is not implemented. The feature-drift PSI diagnostic is not proof of predictive stability. No trained production model, scheduled shadow evaluator or sufficient shadow outcomes are verified.
- Forecast issuance remains fail-closed. The ledger requires at least 100 out-of-sample samples, 100 shadow samples, a horizon/sample multiple of at least 10, at least two source-independence groups, calibration error no greater than 0.05, and an externally trusted Ed25519 evaluator key. Production evaluator keys and an independently operated signing service are not configured.
- SQLite mutation guards and content-addressed receipts provide local integrity, not adversarial tamper-proof or external timestamp anchoring. GitHub artifacts expire; no external WORM archive or independent timestamp authority is configured.

### Open-PR inventory and integrated overlap

Current open inventory: 370 total; 354 drafts and 16 non-drafts.

- Active integration candidate: #1640.
- Active research candidate: #1643.
- #1640 and #1643 share only `.github/workflows/dependency-audit.yml`; its blob is identical on both branches.
- #1642 has seven changed paths, all represented in #1640. Its head is an ancestor of #1640 (zero commits ahead of #1640; #1640 is 474 commits ahead of #1642). Classify it as superseded, but do not close it until the integrated successor is merged and verified on main.
- #1653 has eight unresolved review threads and overlaps #1640 at `.github/workflows/ci.yml`. Its workflow differs: it reverts checkout/setup-python to v4/v5 and replaces the inclusive full-suite coverage job with a no-coverage test run. It is blocked and must not be merged independently.
- Dependency candidates #1644–#1650 remain open. Their paths overlap the integration work and require individual file/commit reconciliation; do not bulk-close them or assume they are all duplicates.
- Preserve unique/unreviewed work including #1317, #1318, #1320 and #1269. Preserve older dependency candidates #1254 and #1255 until their exact successor content is verified on main.

### Merge gate, reviews and authorization

- #1640 is non-draft and GitHub reports it mergeable. Its 22/22 review threads are resolved, but it has zero GitHub `APPROVED` reviews. Reviewer comments containing the word “Approved” are still `COMMENTED`, not approvals.
- #1643 is non-draft and GitHub reports it mergeable. Its 19/19 review threads are resolved, but it also has zero GitHub `APPROVED` reviews.
- #1653 remains blocked with 8/8 unresolved review threads.
- Main reports `protected: true`. The detailed branch-protection endpoint returns HTTP 403; the visible repository rulesets endpoint returns no active ruleset. Pages settings remain inaccessible. A prior main push triggered public Pages deployment run 41799855489.
- The user authorized merging only changes that meet all readiness, approval, safety and external-action requirements. Those requirements are not satisfied. Do not bypass protection, merge, deploy, or close source PRs.

### Nine-platform coordination

- ChatGPT-to-GitHub repository access was tested and verified in this run.
- Copilot and CodeRabbit activity is one-off GitHub-hosted review activity, not a persistent authenticated data flow.
- Claude, Grok, Gemini, Codex, Hugging Face, Kaggle and Databricks authentication, permissions and data-flow remain unverified. Do not claim nine-platform live coordination.

### Next concrete actions

1. Keep #1640 as the single V3 integration candidate. Obtain the required independent approval and verify branch-protection and Pages-deployment authorization before any merge.
2. If #1640 becomes fully ready, merge it only through the permitted GitHub path; then fetch main, verify the merge commit and merged files, account for automatic workflow side effects, and run main CI.
3. Only after that verification, create one consolidated research successor directly on the new main containing #1643's unique research paths. Do not merge the 509-commit research branch independently.
4. Reconcile #1642 and dependency candidates against the resulting main. Close only exact duplicates/superseded PRs after their successor content is verified on main; preserve unique work.
5. Continue multi-venue synchronized historical spot/depth/derivatives ingestion, fund-level issuer-file reconciliation, external receipt anchoring, trusted evaluator-key provisioning, calibration, drift and shadow outcomes. No directional forecast until measured out-of-sample performance and independent attestation support it.

DESIGNED / EXECUTED / VERIFIED remain distinct: the ingestion and recovery workflow is implemented and regression-tested on #1640; the scheduled main-branch workflow is not live; the new market artifacts are archived and their tests passed on #1643; predictive superiority and forecast readiness remain unverified.


# Handoff tip addendum — 2026-11-06T21:48:07Z

This addendum is documentation-only and becomes the current tip of the existing #1640 integration branch. It does not change Barrot V3 or XRP product code.

- The immediately preceding handoff-only tip was `9ebb61cc91585fb8ed4c079c4fc6c74434fde75c`.
- Exact-head CI on that tip passed: 1,068 full-repository tests, 8 subtests; 629 core tests, 8 subtests; inclusive package coverage 57.57% against a 53% threshold.
- The wheel built and installed successfully; the installed wheel verified Barrot V3, the XRP mission, and canonical data assets.
- Exact-head dependency audit passed all six manifests.
- Exact-head fail-closed gate passed and kept merging disabled.
- Evidence: [CI](https://github.com/Barrot-Agent/B-Agent/actions/runs/42299268524) · [dependency audit](https://github.com/Barrot-Agent/B-Agent/actions/runs/42299268543) · [fail-closed gate](https://github.com/Barrot-Agent/B-Agent/actions/runs/42299268536).
- The current PR tip is this handoff-only commit. The product-code head remains `b09d7f89fd2047043788519a22e6663a331c2c99`; no product-code files changed after it.
- This handoff-only update was not followed by another full-suite run; the exact-head evidence above applies to its immediate parent. No merge is authorized until approving review and Pages side-effect gates are satisfied.

---

# Barrot XRP Mission Handoff — Current Verified State

Updated: 2026-11-06T21:44:06Z

## Current verified run — 2026-11-06T21:44:06Z

This checkpoint supersedes the 21:28:30Z checkpoint below. Live GitHub state was re-read during this run. No merge, deployment, branch rewrite, force-push, PR closure, paper trade, or real-money action occurred.

### Main and integrated repository inventory

- Current main SHA remains `9100dbacb5f9f1b973b053a65ef1e91e96b64f72`.
- Recursive main tree: 1,403 entries, 1,298 files, 493 Python files, 87 test files, and 86 workflow files; tree response was complete.
- Open PR inventory: 370 total; 354 drafts and 16 non-drafts.
- The two mission branches remain separate from main. Main has not received either workstream.
- PR #1640 and PR #1643 have one shared changed path, `.github/workflows/dependency-audit.yml`, with identical content. No additional integration PR was created.

### PR #1640 — Barrot V3/core integration

- Product-code head: `b09d7f89fd2047043788519a22e6663a331c2c99`; base main `9100dbac...`; 470 product-code commits ahead at that checkpoint, 0 behind; 155 changed paths. The integration branch's latest tip is the documentation-only handoff update described at the top of this file.
- GitHub reports the PR non-draft, open, conflict-free, and mergeable.
- Exact-head CI: 1,068 full-repository tests passed, 8 subtests passed; core suite 629 passed, 8 subtests; coverage 57.57%; installed-wheel verification passed.
- Exact-head dependency audit passed across all six declared dependency manifests.
- Exact-head fail-closed gate passed. Its job is explicitly named **Merge disabled pending gate verification**; it did not merge.
- Review threads: 22/22 resolved. Recorded approving reviews: 0.
- Evidence: [CI](https://github.com/Barrot-Agent/B-Agent/actions/runs/42297148370) · [dependency audit](https://github.com/Barrot-Agent/B-Agent/actions/runs/42297148384) · [fail-closed gate](https://github.com/Barrot-Agent/B-Agent/actions/runs/42297148362).
- The only commit after the prior code-bearing checkpoint was a handoff-document update; it did not change product code.

### PR #1643 — XRP research archive and evidence

- Current head: `c6b2f74a3ac960623d8326d948c6e90ed5db9404`; base main `9100dbac...`; 506 commits ahead, 0 behind; 357 changed paths.
- GitHub reports the PR non-draft, open, conflict-free, and mergeable.
- Review threads: 19/19 resolved. Recorded approving reviews: 0.
- Exact-current-head core suite: 498 passed, 8 subtests passed.
- Exact-current-head full repository suite: **1,623 passed, 8 subtests passed**. Both new snapshot regression modules ran and passed.
- Exact-current-head dependency audit passed all six manifests.
- Exact-current-head fail-closed gate passed; its job was **Merge disabled pending gate verification** and did not merge.
- Evidence: [CI/full suite](https://github.com/Barrot-Agent/B-Agent/actions/runs/42298768903) · [dependency audit](https://github.com/Barrot-Agent/B-Agent/actions/runs/42298768855) · [fail-closed gate](https://github.com/Barrot-Agent/B-Agent/actions/runs/42298768935).
- A prior head, `a8e12d4977d3a11bfcba3364fe9688de49a1737f`, had one test-only failure caused by exact floating-point equality in a rounded venue-OI sum (1,622 passed, 1 failed, 8 subtests). The test was corrected to use a 0.01-unit tolerance. Current head `c6b2f74...` passed the full suite; the failed prior run remains preserved as evidence.

New append-only research artifacts and regression tests on the existing #1643 branch:

- [21:36 UTC Kraken/OKX spot snapshot](https://github.com/Barrot-Agent/B-Agent/blob/research/xrp-evidence-archive-20261104/research/xrp_intelligence/20261106T213601Z-xrp-kraken-okx-live-spot-cross-venue-snapshot.json)
- [Spot receipt/timestamp tests](https://github.com/Barrot-Agent/B-Agent/blob/research/xrp-evidence-archive-20261104/tests/test_xrp_kraken_okx_live_spot_cross_venue_snapshot_20261106_213601.py)
- [Derivatives/depth reconciliation](https://github.com/Barrot-Agent/B-Agent/blob/research/xrp-evidence-archive-20261104/research/xrp_intelligence/20261106T213601Z-xrp-derivatives-depth-reconciliation.json)
- [Derivatives/depth tests](https://github.com/Barrot-Agent/B-Agent/blob/research/xrp-evidence-archive-20261104/tests/test_xrp_derivatives_depth_reconciliation_20261106_213601.py)

### XRP market and flow evidence

**Spot capture upper bound: 2026-11-06T21:36:01Z.**

- Kraken XRP/USD: last 1.17843, bid 1.17826, ask 1.17827; top-of-book spread about 0.0849 bps; rolling 24h volume 35.344M XRP; rolling 24h VWAP 1.1947217; UTC day open 1.20567; low 1.17085. Kraken's ticker response has no provider timestamp, so only the capture upper bound is recorded.
- OKX XRP-USDT: last 1.1741, bid 1.1741, ask 1.1742; top-of-book spread about 0.8517 bps; rolling 24h volume 62.912M XRP; 24h open 1.2262; low 1.1723. Provider timestamp 21:35:28.571Z, 32.429 seconds before capture.
- OKX last was 0.3674% below Kraken last. This is not an executable spread or arbitrage observation: quote currencies differ, Kraken lacks a source timestamp, and conversion, latency, fees, and transfer costs are not normalized. Top-of-book is not full depth.
- Same-venue OKX last moved from 1.1756 at 21:05:06.565Z to 1.1741 at 21:35:28.571Z, about -0.1276% over 30m22s. The prior Kraken capture had no provider timestamp, so its apparent change is not admitted as a reliable return.
- Both current venue last prices were near their reported rolling 24h lows. No directional signal is inferred.

**Derivatives and depth reconciliation.**

- TradRadar's seven-exchange snapshot, updated 20:55Z and therefore 41m01s old at capture, reported mark price 1.1729 (-4.73% over 24h), open interest about $1.90B (-3.34% over 24h), OI-weighted funding +0.0016% per 8h, and at least $12.07M in 24h liquidations: about $11.50M longs and $562.51K shorts. The long/short account ratio was 4.00 (80% long). Venue funding was mixed: Binance/MEXC/Hyperliquid positive; Bybit/Gate/Bitget/OKX negative.
- The sum of the seven rounded venue OI figures was $1.89577B, consistent with the provider's rounded $1.90B total. About 95.34% of the observed long-plus-short liquidation notional was long-side.
- Aperiodic's older 18:35–18:40Z bar (2h56m01s old at capture) reported a narrower three-venue XRP universe: $803M OI, +9.71% 24h OI change, $1.04B volume, $13.4M 20-level depth, about $842K depth per basis point, and 0.80 bps spread.
- The OI level and 24h change disagreement is preserved, not averaged. The providers have different venue coverage, contract universes, and timestamps. Neither rendered summary is a raw exchange API receipt or a live synchronized order-book ladder.
- No consolidated executable depth or market-impact estimate was produced.

**ETF flows and institutional holdings.**

- Latest settled holdings in the existing archive remain Nov 5: XRP Insights reports +110,214 XRP for the six spot funds plus BITW on Nov 5, while Nov 2–5 totals -149,487 XRP.
- CryptoKeyhole's Nov 5 record was partial (2 of 4 tracked funds); it is not a complete zero-flow day. GXRP data gaps and fund coverage differences remain explicit.
- No complete Nov 6 issuer-settled flow was available at this checkpoint. Do not infer same-day net creations from volume or AUM changes.

### Identity, issuer, and ecosystem research

- Japan's regional SBIC East/Central/West identities remain distinct from SBI Holdings. The located SBIC West Japan ChatGPT seminar establishes an educational event, not an OpenAI partnership.
- ASK Coin/Permission's ASK token remains separate from the unrelated inactive Ask Coin exchange candidate; no verified XRP relationship.
- The exact phrase “actual capital” remains traced to user-generated commentary about Evernorth's PIK notes, not an issuer filing.
- Kamilah/Camilla Stevenson identity is only partially resolved through first-party and interview evidence. No YouTube channel or video is attributed without a first-party cross-link.
- Coinbase, Circle, Ripple, and SBI relationships remain mapped by legal entity and evidence class; brand adjacency is not treated as ownership, custody, issuer, or commercial partnership.

### Prediction-engine readiness

- No directional XRP forecast was issued.
- Current snapshots are research receipts, not a validated point-in-time feature panel. Spot depth is incomplete; derivatives universes disagree; ETF holdings settle on issuer schedules; historical synchronized features, calibration, and out-of-sample predictive lift remain insufficient for a forecast.
- Continue chronological walk-forward evaluation against naive, momentum, mean-reversion, and volatility baselines. Record cutoffs, horizons, assumptions, probabilities, counter-hypotheses, and outcomes before considering forecast eligibility.
- No paper trade, simulated order, or real-money action was initiated.

### Nine-platform coordination

- Persistent ChatGPT-to-GitHub access is verified by live repository reads and writes.
- Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle, and Databricks are not represented as live integrations in this handoff. Their authentication, permissions, and data flows require separate tested evidence. No external AI data transfer occurred.

### Merge gate and backlog

- #1640 and #1643 are both green on their exact current heads and GitHub reports them conflict-free, but each has zero recorded approving reviews. Main branch protection details return HTTP 403; the visible fallback ruleset is disabled. Pages settings remain inaccessible.
- A prior main push triggered GitHub Pages deployment run [41799855489](https://github.com/Barrot-Agent/B-Agent/actions/runs/41799855489). Because merge could trigger an external Pages deployment and its authorization/configuration is not verified, no merge was performed.
- #1653 remains blocked: head `2e449ca28739a73b00dee021c9fb5f38819557c4`, 730 full-suite tests passed on that head, but 8 review threads remain unresolved. A passing suite does not clear those review findings.
- Backlog: #1640 active integration (tests green; approval/Pages gate blocked); #1643 active research (tests green; approval and sequencing blocked); #1653 blocked; #1642 superseded candidate pending post-merge reconciliation; #1644–#1650 dependency/workflow candidates requiring reconciliation, with #1647 blocked; #1317/#1318/#1320 superseded candidates to retain until main verification; #1269 unique/unreviewed; #1254/#1255 older dependency candidates; #1641 draft/incomplete. Preserve the remaining drafts and unique work.
- No PRs were closed. Exact duplicates/superseded sources are to be closed only after a verified successor is merged to main.

### Execution boundary

- **DESIGNED:** scheduled public-data ingestion, source receipts, point-in-time features, quality controls, chronological evaluation, baselines, drift, shadow evaluation, and nine-platform permission map.
- **EXECUTED:** live repository inspection; two new XRP evidence artifacts and two regression modules committed to the existing research branch; floating-point test defect corrected; current-head full suite, dependency audit, and fail-closed gate completed.
- **VERIFIED:** current main SHA; current PR heads/ancestry/path overlap; exact-head test counts; six-manifest dependency audit; resolved/unresolved review-thread counts; no merge or external action.
- **NOT VERIFIED:** independent approving reviews; Pages configuration/authorization; external immutable/WORM retention and independent timestamp anchoring; full historical derivatives/capital-flow coverage; calibrated out-of-sample XRP predictive lift; live authentication/data flow for the other eight platforms.

**Next concrete action:** keep #1640 as the single V3 integration candidate; obtain the required independent review and resolve the Pages side-effect authorization before merge. After #1640 is merged and verified on main, consolidate #1643's unique research artifacts onto the new main, rerun exact-head full-suite/security gates, and close only source PRs proven duplicate or superseded.

---

## Previous checkpoint — 2026-11-06T21:28:30Z

This checkpoint supersedes the older head and backlog summaries below. Main was not modified. All new code and research described here are on the existing integration or research branches, not on main.

### Main and integration branch

- Main SHA remains `9100dbacb5f9f1b973b053a65ef1e91e96b64f72`.
- Complete recursive main tree fetched: 1,403 entries, 1,298 files, 493 Python files, 87 `tests/test*.py` files and 86 workflow files.
- PR #1640 current code-bearing head: `d1d2ffe0d6d88a42e60043c2378d05b87bd6ab41`; 469 commits ahead, 0 behind; 155 changed paths; non-draft; GitHub mergeable state `clean`.
- Exact-head core suite: **629 passed, 8 subtests passed**.
- Exact-head full repository suite: **1,068 passed, 8 subtests passed**; inclusive package coverage **57.57%**. The wheel build/install and packaged primary-mission verification passed.
- Six-manifest dependency audit passed. Fail-closed merge gate passed and explicitly keeps automatic merging disabled.
- Evidence: [full suite 42296269975](https://github.com/Barrot-Agent/B-Agent/actions/runs/42296269975), [dependency audit 42296269971](https://github.com/Barrot-Agent/B-Agent/actions/runs/42296269971), [fail-closed gate 42296270166](https://github.com/Barrot-Agent/B-Agent/actions/runs/42296270166).
- The handoff update being committed by this document revision is documentation-only. Its resulting PR head must receive its own exact-head checks before any merge decision.

### V3 provider-rate-limit resilience — implemented on #1640

The failed issue-triggered Barrot run exposed a real orchestration gap: Groq returned HTTP 429 on the `openai/gpt-oss-120b` token-per-minute limit; one timed retry still failed, and the bundle authoring path stopped before producing useful deterministic evidence.

The existing #1640 branch now:
- removes a duplicated default fallback-model entry;
- retries the primary model once when a bounded retry interval is supplied;
- tries configured fallback models after persistent per-minute or daily token exhaustion;
- recognizes exhausted fallback as a provider-rate-limit condition;
- produces a deterministic, read-only Git/Actions/repository-context report when provider limits still prevent model-backed bundle authoring or read-only audit;
- explicitly leaves the task blocked and exits nonzero, without starting repository repair, creating a PR, merging or deploying.

Three new regression tests cover primary-model retry followed by fallback, explicit blocked/read-only reporting, and the engineering-task failure path. All three passed on the exact code-bearing head above. This fix is **not on main yet**; the failed issue #1652 run used main's older script.

### PR #1643 — XRP research archive

- Current head: `ef230f763b54c339bed34fb37865a83a2495c400`; 501 commits ahead, 0 behind; 355 changed paths; non-draft; mergeable state `clean`.
- Exact-head core suite: **498 passed, 8 subtests passed**. Full repository suite: **1,617 passed, 8 subtests passed**. Six-manifest dependency audit and fail-closed gate passed.
- Evidence: [full suite 42295360818](https://github.com/Barrot-Agent/B-Agent/actions/runs/42295360818), [dependency audit 42295360943](https://github.com/Barrot-Agent/B-Agent/actions/runs/42295360943), [fail-closed gate 42295360713](https://github.com/Barrot-Agent/B-Agent/actions/runs/42295360713).
- The only path shared with #1640 remains `.github/workflows/dependency-audit.yml`; its blob is identical on both branches. Do not merge #1643 directly after #1640. After #1640 is merged and verified on main, consolidate the 354 research-only paths plus the new evidence below onto that resulting main, then run the expanded full suite and security gates.

### New XRP evidence committed to the existing #1643 branch

**Spot snapshot, 21:05:20Z**
- [Raw-receipt artifact](https://github.com/Barrot-Agent/B-Agent/blob/research/xrp-evidence-archive-20261104/research/xrp_intelligence/20261106T210520Z-xrp-kraken-okx-live-spot-cross-venue-snapshot.json) and [regression test](https://github.com/Barrot-Agent/B-Agent/blob/research/xrp-evidence-archive-20261104/tests/test_xrp_kraken_okx_live_spot_cross_venue_snapshot_20261106.py).
- Kraken XRP/USD: last $1.17255; bid $1.17240; ask $1.17241; rolling-24h volume 35.85M XRP; rolling-24h VWAP $1.1958515; UTC-day open $1.20567; 24h low $1.17164.
- OKX XRP-USDT: last 1.1756; bid 1.1756; ask 1.1757; rolling-24h volume 64.67M XRP; rolling-24h open 1.2238; 24h low 1.1723; exchange timestamp 21:05:06.565Z.
- The roughly 0.26% last-price difference is not an executable spread: USD/USDT conversion, latency, fees and transfer costs are not normalized. Top-of-book is not full depth; venue volumes are not combined. Response hashes cover captured JSON text, not original HTTP wire bytes or independently timestamped immutable storage. The record remains raw-snapshot-only and is not admitted as a model feature.

**Institutional custody and flow-source reconciliation**
- [BNY/market-flow addendum](https://github.com/Barrot-Agent/B-Agent/blob/research/xrp-evidence-archive-20261104/research/xrp_intelligence/20261106T211245Z-bny-custody-and-market-flow-data-quality-addendum.json) and [regression test](https://github.com/Barrot-Agent/B-Agent/blob/research/xrp-evidence-archive-20261104/tests/test_xrp_bny_custody_and_market_flow_data_quality_addendum_20261106.py).
- BNY's Oct 27 primary release confirms a direct Ripple collaboration, BNY's RLUSD reserve-custody role, its custody relationship with Ripple Prime, and support for XRP and RLUSD on its digital-asset custody platform. Direct RLUSD mint/redeem through BNY is an intended future capability subject to final BNY and regulatory approvals. The trade-finance/C2FO initiative is exploratory.
- BNY's June 29 primary release separately confirms its USDC reserve-custody and institutional mint/burn relationship with Circle. BNY is a shared institutional service provider; this does not establish a direct Circle-Ripple partnership or common ownership. The releases do not establish that XRP itself is accepted as collateral.
- CryptoQuant's analyst reports 418.5M XRP withdrawn from Binance on Nov 4; The Crypto Basic reports aggregate Binance XRP reserves rising from 2.35B to 2.63B over Nov 3–5. These are different windows/metrics and may include internal wallet transfers or label changes. The reserve increase's source is unknown; do not infer accumulation or purchases.
- BeInCrypto citing SoSoValue reports zero US spot XRP ETF net flows Nov 3–5. XRP Insights reports +110,214 XRP on Nov 5 across six spot funds plus BITW, but excludes GXRP from flow totals and counts BITW sleeve rebalancing/fees as flow. The fund universe and calculation methods differ; the direct SoSoValue source could not be independently retrieved. Preserve the disagreement; neither series is a clean predictive feature.

**Japanese SBIC identity resolved from primary sources**
- [Statute and company-identity artifact](https://github.com/Barrot-Agent/B-Agent/blob/research/xrp-evidence-archive-20261104/research/xrp_intelligence/20261106T211523Z-japan-sbic-east-central-west-identity-resolution.json) and [regression test](https://github.com/Barrot-Agent/B-Agent/blob/research/xrp-evidence-archive-20261104/tests/test_japan_sbic_east_central_west_identity_resolution_20261106.py).
- Article 2 of Japan's Small and Medium Business Investment & Consultation Companies Act (Act No. 101 of 1963) names exactly three companies: Tokyo, Nagoya and Osaka.
- Tokyo is **SBIC East Japan**; Nagoya is **SBIC Central Japan**; Osaka is **SBIC West Japan**. Their official profiles identify each other as sister companies and describe distinct regions and incorporation dates.
- SBI Holdings, Inc. is a separate holding company established in 1999. The reviewed primary evidence does not establish that any of the three SBIC companies is a subsidiary or affiliate of SBI Holdings.
- Tokyo SBIC East listed a June 12–13, 2025 generative-AI/ML training course for investee companies that included ChatGPT and Copilot. This is an educational event, not evidence of an OpenAI partnership, procurement contract or joint product.
- Excerpt hashes in this identity artifact cover stored normalized excerpts, not complete source-page bytes. These are identity-research records, not prediction features.

### Open-PR inventory and classification

The live inventory contains **370 open PRs: 354 drafts and 16 non-drafts**. The non-draft set is #1653, #1650–#1644, #1643, #1640, #1320, #1318, #1317, #1269, #1255 and #1254.

- **Active integration:** #1640 — exact-head green, but not merge-authorized yet.
- **Active unique research:** #1643 — exact-head green; sequence after #1640 and consolidate its unique files onto the resulting main.
- **Superseded by #1640, retain until successor is merged and verified:** #1642 (its implementation commit is an ancestor of #1640); #1644 (checkout v7 updates are present on active workflows while unsafe workflows are quarantined); #1645 (exact dependency-audit workflow blob); #1646, #1648, #1649, #1650, #1254 and #1255 (their dependency changes are represented by the newer #1640 manifests); #1317 (structural core paths are present, with a larger implementation/test suite in #1640); #1318 (schema-validation tests and fail-closed behavior are present in #1640); #1320 (the paper-trader identity pause is superseded by #1640's stricter manual-only, exact-SHA-confirmed, artifact-only workflow and expanded tests).
- **Blocked:** #1647 — its upload-artifact v7 changes are already present on active #1640 workflows, its exact-head tests/full suite fail, and its branch reintroduces an active self-upgrade workflow that #1640 deliberately quarantines. #1653 — full-suite CI does not resolve six high-severity review findings involving CLI argument transport, graph overwrite despite `persistence=false`, missing post-index repository-state revalidation, unapproved submodule fetches, false synchronized status and unstructured timeout handling.
- **Unique/unreviewed:** #1269 OBJ topology/triangulation work; preserve it for a separate integrated review.
- **Draft/incomplete:** #1641 remains a limited foundation, not a production XRP predictor. Preserve it.
- Preserve the other 354 drafts until their individual objectives, ancestry, changed paths and tests are reviewed. Do not bulk-close.

### Merge, deployment and platform gates

- #1640 and #1643 each still have **zero approving reviews**; the recorded reviews are comments only. Neither PR was merged or closed.
- Main reports `protected=true`; the classic branch-protection endpoint returns HTTP 403. The visible repository ruleset, ID 10863829, is disabled. Required review/check enforcement cannot be independently confirmed.
- A main push previously triggered Pages deployment run [41799855489](https://github.com/Barrot-Agent/B-Agent/actions/runs/41799855489). Pages configuration remains inaccessible and no authorization for another merge-triggered public deployment has been established. Do not merge or bypass protections.
- The nine-platform capability/authentication map still verifies only ChatGPT-to-GitHub access. No live Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle or Databricks connection/data flow has been proven. Groq API use inside Barrot is not the same as a Grok platform connection.
- No deployment, secret rotation, Space restart, Kaggle submission, paper trade, transfer or real-money action occurred.

### DESIGNED / EXECUTED / VERIFIED boundary

- **DESIGNED:** primary XRP mission registry, source provenance, point-in-time feature contracts, forecast ledger, walk-forward policy, baseline comparisons, calibration/drift requirements and counter-hypothesis review.
- **EXECUTED on PR branches, not main:** V3 orchestration/safety changes; public XRP ingestion and source receipts; point-in-time feature store; forecast ledger; walk-forward evaluator; baselines; drift diagnostics; new spot, BNY/flow and SBIC evidence; Groq TPM fallback and deterministic blocked-state reporting.
- **VERIFIED:** exact-head checks and test counts are attached to the specific PR heads and workflow runs above. Main still does not contain these changes. Historical cross-domain data, synchronized depth/derivatives, external immutable timestamp anchoring, calibrated out-of-sample predictive lift and evaluator trust-key configuration remain insufficient. No directional XRP forecast is issued.

### Next concrete actions

1. Keep #1640 as the single V3/XRP integration branch; verify this handoff-only revision's exact-head checks.
2. Obtain an independent approving review and resolve the Pages deployment authorization boundary. Never bypass protections.
3. Once #1640 is merged and verified on main, consolidate #1643's unique research files onto that resulting main and rerun the expanded full suite, wheel and security audit.
4. Close #1642, #1644–#1650, #1317, #1318, #1320, #1254 and #1255 only after their successor content is verified on main, with explicit cross-references. Preserve #1269 and all other unique work.
5. Resolve #1653's critical review findings before reconsidering it.
6. Continue synchronized historical XRP ingestion, per-fund ETF reconciliation, exchange-wallet flow attribution and leakage-safe out-of-sample evaluation. No directional forecast until predictive lift and calibration are demonstrated.



## Previous checkpoint — 2026-11-06T21:05:20Z

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
