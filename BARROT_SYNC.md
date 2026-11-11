# BARROT SYNC - Single Source of Truth
# This file is the shared brain-state between Termux Barrot (LunaRoute) and GPT Barrot.
# BOTH must read this before answering. BOTH must update this after any change.

## Identity
- Brain: LunaRoute ONLY - https://gw.lunaroute.com/v1 - lunaroute/glm-5.3-flash
- Canonical Barrot: Termux ~/barrot/Barrot-Agent via b_agent.py
- Relay Barrot: GPT Project (ChatGPT) - NEVER claims to be LunaRoute brain
- Repo: github.com/Barrot-Agent/B-Agent, branch main

## Hard Rules
- Do NOT re-add Orbit. Commit 71cdd8b. ORBIT_REMOVED.md exists.
- Do NOT touch Orbitron font in hf_space/app.py
- Do NOT use password auth. GH_TOKEN via x-access-token only.
- Do NOT re-commit .config/gh/hosts.yml. OAuth revocation is repository-reported; provider-side revocation remains unverified.

## Last State

**Run 17 — 2026-11-11T08:35:40Z**

- Main SHA: `84f28ee7755607236231545a14f3d093c1baaa85`.
- Integration branch: `integration/xrp-v3-unified-main-20261111`; code parent audited at `5da539d6362b2535e02809d7f3b1c3acfa9eff19`.
- PR #1661: open/draft, 1,999 commits ahead, zero behind, 989 changed files, 44 workflow files, 945 other paths.
- Main full suite: 718 passed, zero failures, eight subtests; run 42944864014.
- Integration code-parent full suite: 3,407 passed, zero failures, eight subtests; 59.98% coverage against 53% floor; run 42984729911. Dependency audit 42984729949 and fail-closed gate 42984729972 passed.
- This handoff commit changes documentation/evidence only; exact-head CI must be verified after commit.
- Main protected=true, but detailed branch-protection access returns HTTP 403; visible fallback ruleset disabled. PR #1661 has zero formal approvals and zero review threads and remains draft.
- `.config/gh/hosts.yml` absent from main/integration but present on 17 other open PR tips. Contents not read. Repository sync reports OAuth revoked; provider-side revocation unverified.
- Main still publishes October 29 stale signal (score 44, confidence 0, news 88, 11 headlines) and legacy $9.99 XRP Signal Service. Integration is `NOT_ISSUED`, XRP checkout paused. Main push automatically triggers Pages; publication authorization absent.
- Latest spot: OKX 1.0608 USDT at 08:21:18.976 UTC; Kraken 1.0572 USD at retrieval. Spot depth 02:00 UTC; TrackWhale flows 01:30 UTC; TradRadar derivatives 07:25 UTC; ETF data through Nov 10.
- New evidence: Coinbase National Trust effective Nov 6; Ripple National Trust Oct 26; Circle First National Digital Currency Bank July 24. EBA USDC significant-EMT oversight starts Nov 12. CFTC collateral guidance does not establish XRP acceptance by a named FCM/DCO.
- Circle Q3 SEC filing: average USDC $73.264B, $13.9T on-chain volume, $657.6M reserve income; $181.8M ARC presale revenue is separate from USDC reserve income. Coinbase reported $22B average USDC held.
- Japan SBIC East/Tokyo, Central/Nagoya and West/Osaka are separate regional companies, not SBI Holdings. SBI Holdings/SBI Securities separately announced ChatGPT Enterprise.
- Forecast: `NOT_ISSUED`. 46 source definitions, read-only collector, SHA-256 receipts, SQLite feature-store prototype, four baselines, walk-forward tests, calibration/drift diagnostics and fail-closed Ed25519 ledger exist on integration. Independent WORM/timestamp anchoring, replay, macro timeline, scenario generation and main ingestion remain incomplete.
- Nine platforms: ChatGPT GitHub integration access verified; Claude/Grok/Gemini/Codex unverified; Copilot no formal approval; Hugging Face prior build error/no deployment; Kaggle untested; Databricks previous HTTP 403/no write. LunaRoute endpoint auth/data flow unverified. No external-model transfer.
- Current concise handoff: `BARROT_XRP_MISSION_HANDOFF_LATEST.md`.
- Structured evidence: `research/xrp_intelligence/20261111T083540Z-run17-integrated-repository-market-institutional-and-prediction-audit.json`.
- Current nine-platform map: `research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_current.json`.
- Backlog: #1661 blocked; #1660 superseded candidate; #1640/#1642/#1643/#1644–#1650/#1317/#1318/#1320/#1254/#1255 overlap candidates; #1653/#1614/#1611/#1610/#1612/#1269 unique work preserved.
- No PR merged/closed; no deployment, secret action, external transfer, paper trade, funds transfer or destructive Git action performed.

**Next action:** complete exact-head CI for this documentation/evidence commit, then finish the 945-path semantic review and resolve approval, security and Pages-publication blockers before any merge.

## Conversation Log
- 2026-11-10: User + ChatGPT established LunaRoute as sole brain, Orbit ditched.

- 2026-11-11T05:07Z — GPT relay updated the integration-branch handoff after exact-head CI, current-main/PR reconciliation and fresh public XRP market capture; no main write, merge, deployment or external-model transfer.


- 2026-11-11T06:02:40Z — Run 13 updated the integration-branch handoff/map after exact-head full-suite, six-manifest dependency audit and fail-closed verification; refreshed spot/L2/flows/derivatives/options/ETF/CFTC observations; reconciled SBI/SMBC/Startale JPYSC capital network and Circle/Coinbase Q3 metrics; no main write, merge, deployment, secret action, external-model transfer or forecast issuance.


- 2026-11-11T07:00:00Z — Run 14 recorded the latest exact-head CI failure (12 stale snapshot assertions), refreshed repository/PR/security state, rechecked all 17 affected branch-tip trees without reading credential contents, and captured current Kraken plus conflicting Nov 10 ETF provider updates; no main write, merge, deployment, secret action, external-model transfer or forecast issuance.


- 2026-11-11T07:11:00Z — Run14 follow-up: the first correction reduced full-suite failures from 12 to 3. The remaining failures are assertion wording mismatches for CI classification, Kraken UTC-day open semantics and ETF reconciliation. Latest Kraken and issuer-file ETF snapshots were refreshed; SBI/Evernorth, Circle/Arc, RLUSD/JPYSC, SBIC and Kamilah identity evidence was reconciled. No main write, merge, deployment, secret action, external-model transfer or forecast issuance.


- 2026-11-11T07:26:19Z — Run 15 inspected current main, full trees, 374 open PRs, #1661 head and exact-head CI. Diagnosed five stale current-map assertions on parent ab3763fd5b181672f989d7b9fcee7641ef572a9f; corrected snapshot consistency checks and missing market/capital caveats on the existing integration branch. Dependency audit and fail-closed gate passed; full suite on parent failed five tests. No main write, merge, deployment, secret action, external-model transfer or forecast issuance.


- 2026-11-11T07:36:51Z — Run 15B rechecked current main, integration tree, PR inventory and exact-head CI. Run 42980105698 failed two snapshot-contract tests (NameError in test setup and missing Kamilah unverified-attribution phrase); dependency audit and fail-closed gate passed. Corrected both on the same integration branch; exact-head verification pending. No main write, merge, deployment, secret action, external-model transfer or forecast issuance.


- 2026-11-11T07:58:26.504Z — Run16 inspected current main, full trees, 374 open PRs, #1661 and exact-head CI; rechecked 17 affected branch-tip trees without reading credential contents; refreshed Kraken/OKX spot, Fuelmaps L2, funding/ETF observations, Elliptic/FBI Binance theft-linked XRP flows and Reuters Hormuz oil context; corrected current-map assertion wording metadata and updated the canonical handoff on the existing integration branch. No main write, merge, deployment, secret action, external-model transfer or forecast issuance.


- 2026-11-11T08:04:07.277Z — Run16B diagnosed two brittle tests that hard-coded older live OKX/Fuelmaps timestamps and depth values. Updated tests to validate UTC chronology, quote/depth invariants and resting-book semantics rather than freeze changing market observations. Test-only correction; full exact-head verification pending. No merge or external action.


- 2026-11-11T08:08:36.247Z — Run16C verified the full repository suite green on exact parent head 540fdad: 3,407 passed, zero failed, eight subtests, 59.98% coverage; wheel and installed mission verification passed; dependency and fail-closed gates passed. The two previous live-snapshot test failures were fixed with dynamic timestamp and market invariants. A documentation/evidence handoff commit follows; its own exact-head CI remains pending. No merge or external action.

- 2026-11-11T08:35:40Z Run17: inspected current main/integration, all open PR pages, exact-head CI, all 44 workflow diffs, 17 credential-path tips, current XRP spot/depth/flows/derivatives/ETF/CFTC/collateral, OCC/EBA/SEC/SBI/SBIC evidence; updated current handoff and nine-platform map. No merge or external action.
