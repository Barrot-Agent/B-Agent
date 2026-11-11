# Run29b — CI evidence-test repair and XRPL governance update

Captured: 2026-11-11T15:52:03.641Z

## Repository and CI state

Main remains `84f28ee7755607236231545a14f3d093c1baaa85`. The existing consolidated PR is [#1661](https://github.com/Barrot-Agent/B-Agent/pull/1661), branch `integration/xrp-v3-unified-main-20261111`. At capture, the branch head was `415e611a983117238af9a6af60d2b4619be93e6d`, 2,034 commits ahead and zero behind main, with 1,012 changed files (44 workflow files and 968 other paths). Open PR inventory: 374 (360 drafts, 14 non-drafts). Main tree: 1,388 entries; integration tree: 2,277 entries.

The full suite on exact head `415e611` completed with 3,447 passed, two failed, eight subtests and 59.99% coverage. Core tests passed 714/0. Dependency audit (six manifests, zero known vulnerabilities) and fail-closed gate passed. The two failures are in `test_xrp_nine_platform_current_map_run73.py`:
- The exact-head evidence test hard-coded the old `7a55848` head and 3,423-test count instead of matching the latest recorded attempt dynamically.
- The backlog test requires the `SUPERSEDED_SOURCE` token for PR #1660, while the latest map label had been changed to a generic overlap candidate.

The previous exact code head `c7095fa5` passed 3,449 tests, zero failures, eight subtests, 59.99% coverage; wheel build and installed Barrot V3/XRP mission verification passed. Evidence: [full CI 43049347225](https://github.com/Barrot-Agent/B-Agent/actions/runs/43049347225), [full-suite job](https://github.com/Barrot-Agent/B-Agent/actions/runs/43049347225/job/130621875637), [dependency audit](https://github.com/Barrot-Agent/B-Agent/actions/runs/43049347095), [fail-closed gate](https://github.com/Barrot-Agent/B-Agent/actions/runs/43049347054).

The Run29b commit updates the test to compare the current head and suite counts against the latest-attempt record, and restores explicit `SUPERSEDED_SOURCE_CANDIDATE` / `UNIQUE_UNREVIEWED` backlog labels. This commit must receive its own exact-head full suite, dependency audit and fail-closed verification. The two current failures are evidence-test/schema regressions, not ingestion or prediction-runtime failures.

## XRP market update — November 11

### Spot and order-book quality

OKX XRP-USDT returned 1.0590 (bid 1.0589, ask 1.0590), provider event time 15:09:44.769 UTC. Kraken XRP/USD returned 1.05898 (bid 1.05904, ask 1.05905) with no provider event timestamp. USDT/USD was 0.99888; normalized OKX was about $1.057812, roughly 0.116% below Kraken's midpoint. These are asynchronous references, not an executable arbitrage signal.

Fuelmaps' 15:00 UTC six-venue spot book had a $1.0558 mid. Within ±1% it showed $14.4M bids versus $10.6M asks; within ±5%, $25.2M versus $13.6M; within ±10%, $35.0M versus $16.0M. Binance and Bitget are excluded. The provider averages one-minute resting-book observations into hourly values; orders can be cancelled or moved.

### Perpetuals and options

TradRadar's fresher 15:15 UTC (15-minute delayed) snapshot: price $1.0604, +0.10% over 24h; OI $1.58B, down 2.31%; funding +0.0080% per eight hours; at least $9.18M liquidations, $8.30M long and $887.89K short; 79.6% of accounts long (3.90 account ratio). It combines seven exchanges for OI and five for liquidations/long-short.

Liqwall at 15:22 UTC: OI $1.16B, down 2.6%; funding +0.0081%; $11.5M liquidations, $10.6M long and $893K short; 75.2% of Binance accounts long and 53.1% of Hyperliquid accounts long. The OI universes differ; do not average. Both show positive funding, falling OI and long-heavy liquidations, consistent with crowded-long deleveraging but not a directional forecast.

OptimistFi/Deribit at 14:00 UTC: 30-day ATM IV 58.2%, +1.7-point 25-delta skew (calls richer), put/call 0.55, December 25 open interest $47.3M. Near expiries are put-rich while deferred expiries are call-rich. Preserve the term structure; max pain is not a forecast.

### ETF flows

Alpha Finance through the November 10 session reports five of five funds: -$7.6M on Nov 10, -$10.4M on Nov 9, -$18.0M over the last seven sessions, +$1.3M over 30 sessions, and +$1.71B cumulative net inflow since Nov 14, 2025. Cumulative net flow is +972.8M XRP, 1.532% of supply. GXRP/Grayscale was the largest Nov 10 outflow at -$7.2M. The dashboard does not publish AUM or holdings; cumulative flow is not current fund size. Redemptions can be arbitrage unwind and flow prints lag settlement.

### XRPL governance, collateral and data quality

The XRPL dashboard's own-node roll call at 15:32 UTC heard 35/35 validators; 29 yes votes are required. SingleAssetVault: 23/29; LendingProtocol: 22/29; LendingProtocolV1_1: 22/29; ConfidentialTransfer: 21/29; DynamicMPT: 16/29; Sponsor and fixXChainRewardRounding: 10/29; XChainBridge: 4/29; CryptoConditionsSuite: 0/29. There is no 14-day activation countdown. Both SingleAssetVault and LendingProtocol are required for native lending, so native XRPL lending remains inactive.

The page shows 98 live amendments and nine in-flight. Credentials, PermissionedDomains, PermissionedDEX and TokenEscrow are live; fixCleanup3_4_0 activated November 4. ConfidentialTransfer applies to MPT transfers, but sender/destination remain visible and it does not support DEX, escrow or checks. DynamicMPT allows specified issuer properties to change. XLS-100 Smart Escrows remains in development and depends on a companion WASM engine/API specification.

The dashboard says its data is cached for up to five minutes, but its footer showed 435.7 seconds at fetch. Its global header price was $1.0754 as of 15:36 UTC, while OKX/Kraken references were near $1.059 and TradRadar at $1.0604. Its separate PriceOracle page showed $1.0614 from DIA, last updated 14:36:24 UTC; the page snapshot was seven minutes old and DIA was the only production provider publishing to mainnet. Exclude the $1.0754 header and delayed DIA feed from live market features until event time/provider lineage are reconciled.

### SBI, Ripple and regulation

SBI VC Trade's November 2 release reports JPYSC customer-lending balance above ¥10B and handling balance above ¥30B. The lending balance represents customers lending JPYSC to SBI VC Trade, not XRP collateral or third-party borrower loans. SBI's September 7 release reports ¥1B of JPYSC trust reserves invested in short-term Japanese government bonds, with about ¥20.1B issuance and ¥6.9B lending applications. SBI/Startale/BlackRock's October 27 tokenized-MMF/JPYSC agreement is exploratory, not production settlement or an XRP corridor.

Ripple reports final OCC approval for Ripple National Trust Bank on October 26; OCC CAS marks the application consummated/effective on the same date. RNTB is described as reserve manager, collateral trustee and fiduciary custodian; Standard Custody & Trust Company, LLC remains RLUSD issuer under NYDFS, and BNY is primary reserve custodian. Approval does not establish operational commencement.

The OCC's GENIUS Act final rule 2026-21706 is effective January 18, 2027. Treasury Section 3 proposal 2026-16796 remains proposed, not final; comment deadline was October 19. Do not conflate the OCC final rule with the separate Treasury proposal or infer issuer-specific status for Circle, Ripple or SBI.

### Identity and nine-platform status

SBIC East/Tokyo, Central/Nagoya and West/Osaka remain separate regional SME investment companies, not SBI Holdings. No primary-source match for ASK Coin, “actual capital” as a standardized XRP metric, or “SBIC, ChatGPT SBIC” was found. Kamilah person identity is corroborated, but candidate YouTube channel ownership remains unverified; no personal-channel video inventory is attributed. Camilla remains separate/unresolved.

ChatGPT/GitHub access is verified but connector permission metadata reports admin=true, maintain=true, push=true, pull=true and triage=true. Copilot has no formal PR approval. Claude, Grok, Gemini and Codex remain unverified; Hugging Face BUILD_ERROR; Kaggle untested/no submission; Databricks HTTP 403/no workspace write; LunaRoute declared canonical brain but endpoint auth/data flow unverified. No external-model data transfer occurred.

## PR and merge state

PR #1661 remains draft, open and currently has unstable checks due the two evidence-test failures. It has zero formal approvals/reviews and zero review threads. Branch-protection details remain HTTP 403; visible fallback ruleset disabled. Main and integration exclude `.config/gh/hosts.yml`; 17 other open PR tips still contain that path. Contents were not read; provider-side OAuth revocation remains unverified. Main pushes trigger GitHub Pages publication, which remains unauthorized.

Current overlap reconciliation:
- #1660: 972 paths represented in #1661; 948 identical blobs, 24 different. Mark as superseded-source candidate, retain until successor merge and main verification.
- #1640: 280 represented; 244 identical, 36 different.
- #1643: 670 represented; 661 identical, 9 different.
- #1642: seven represented, all different.
- #1653: three unique paths; #1614: 26 unique; #1611: one; #1610: two; #1608: two.
- #1269: nine represented, three identical and six different; no unique path in current inventory.
- #1317/#1318/#1320 and dependency PRs #1644–#1650/#1254/#1255 are represented but require blob-different semantic/version reconciliation.

No source PR was closed. Preserve unique research, prediction, graph, safety and topology work. The XRP collector remains integration-only, read-only, main-guarded; Actions artifact/cache retention is not WORM. The feature store remains owner-mutable SQLite. Forecast stays NOT_ISSUED.

No merge, deployment, credential rotation/revocation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or PR closure occurred.

---

Prior handoff history follows.

# Run29 — exact-head CI repair, XRP market and regulatory reconciliation

Captured: 2026-11-11T15:36:00Z

## Repository state

Main remains `84f28ee7755607236231545a14f3d093c1baaa85`. The existing consolidated integration PR is [#1661](https://github.com/Barrot-Agent/B-Agent/pull/1661), branch `integration/xrp-v3-unified-main-20261111`. At capture, the integration head was `c7095fa5c9ca7452c08296ed69c82d51ed75f36c`, 2,033 commits ahead and zero behind main, with 1,011 changed files (44 workflow files and 967 other paths). Open PR inventory: 374 (360 drafts, 14 non-drafts). Main tree: 1,388 entries; integration tree: 2,276 entries. No new branch or PR was created.

GitHub API access succeeded. Local Git clone remains blocked by DNS resolution. The main and integration trees both exclude `.config/gh/hosts.yml`; its contents were not read. The same path remains present in 17 other open PR branch tips. Provider-side OAuth revocation is not independently verified.

## Exact-head CI repair and result

The preceding exact head `65e11c1` had two bounded test failures:

1. `test_external_deployment_workflow_gates.py` expected a literal backslash-n in YAML, although the workflow contains a real newline.
2. `test_xrp_nine_platform_current_map_run73.py` expected obsolete Kamilah wording rather than the current explicit statement that no personal-channel video inventory is attributed.

Both assertions were corrected in commit `c7095fa5c9ca7452c08296ed69c82d51ed75f36c`. No production code or workflow was changed by this corrective commit.

Exact-head evidence on `c7095fa5`:

- Full repository suite: **3,449 passed, zero failed, eight subtests passed**.
- Inclusive coverage: 59.99%, against the configured 53% floor.
- Full-suite test duration: 74.86 seconds.
- Core suite: 714 passed, zero failed, eight subtests, 11.51 seconds.
- Wheel build and installed-wheel verification passed; the installed wheel loaded Barrot V3, the XRP mission and canonical data assets.
- Six dependency manifests audited; zero known vulnerabilities reported.
- Fail-closed gate passed; automatic merge remains disabled.

Evidence:
- [Full CI 43049347225](https://github.com/Barrot-Agent/B-Agent/actions/runs/43049347225)
- [Full-suite job 130621875637](https://github.com/Barrot-Agent/B-Agent/actions/runs/43049347225/job/130621875637)
- [Dependency audit 43049347095](https://github.com/Barrot-Agent/B-Agent/actions/runs/43049347095)
- [Fail-closed PR gate 43049347054](https://github.com/Barrot-Agent/B-Agent/actions/runs/43049347054)

The 59.99% coverage result remains above the 53% floor but below the previous 70% target. The floor is transitional quality debt. Setuptools package-discovery/license metadata warnings remain; wheel build and installed mission verification nevertheless passed.

This Run29 durable-evidence commit is documentation/research only and will trigger a new exact-head CI run. The 3,449-test result above is verified on its parent code head `c7095fa5`, not automatically on the new documentation commit.

## Integrated architecture and XRP collector

Barrot V3 remains the execution, orchestration, safety and verification foundation. The XRP ingestion workflow exists only on integration; its job guard requires `refs/heads/main`. It has read-only `actions:read` and `contents:read` permissions, uses no external credentials, allowlists HTTPS hosts, rejects redirects, enforces a 15-second timeout, a 10 MiB response cap and HTTP cache-age quality gates. It runs hourly and daily when present on main. Coinbase historical backfill is manual-only, bounded to 365 days.

The workflow writes to its runner workspace, Actions artifacts and cache, not repository files. Raw receipts and daily archives have 90-day artifact retention; per-run feature-store checkpoints have seven-day retention. Actions artifacts/cache are not WORM storage. The SQLite feature store uses SQL triggers and hash verification to deter ordinary mutation, but its own documentation correctly states that a file owner can drop triggers or rewrite the database. Independent signed/timestamped anchoring and replayable reconstruction remain production blockers.

The collector defines 47 public sources; 45 are scheduled, while two noncommercial XRPL node endpoints are excluded by default. It is not executed on main because the workflow has not been merged. No main-branch ingestion run is claimed.

The walk-forward evaluator purges and embargoes training labels, evaluates naive-class-prior, momentum-sign, mean-reversion-sign and volatility-normal baselines, and calibrates probabilities. Its overlap-adjusted effective sample size does not correct residual serial dependence or shared-source correlation. The forecast ledger requires byte-complete raw receipts, at least two independent source groups, at least 100 out-of-sample samples, at least 100 shadow outcomes, non-overlapping horizon coverage and independent Ed25519 readiness attestation. The production signing key, independent WORM anchor, shadow outcomes and demonstrated out-of-sample lift remain outstanding.

## XRP market refresh — 2026-11-11

### Spot and data quality

OKX XRP-USDT returned 1.0590 with bid 1.0589/ask 1.0590 and provider event time `2026-11-11T15:09:44.769Z`. Kraken XRP/USD returned 1.05898 with bid 1.05904/ask 1.05905 but no provider event timestamp. Kraken USDT/USD was 0.99888. After normalization, OKX was approximately 1.057814 USD, about -0.116% below the Kraken midpoint. These quotes are asynchronous and the OKX event time was about 26 minutes before capture; not an executable arbitrage signal.

Fuelmaps' 15:00 UTC six-venue spot snapshot had a $1.0558 mid. Within ±1% it showed $14.4M bids versus $10.6M asks; within ±5%, $25.2M versus $13.6M; within ±10%, $35.0M versus $16.0M. Binance and Bitget are excluded. The map averages one-minute resting-book observations into hourly columns; orders can be cancelled or moved.

### Derivatives and options

TradRadar at 14:40 UTC (15-minute delay) reported $1.57B OI, down 2.83%; +0.0080% funding per eight hours; at least $9.29M liquidations, $8.35M long and $0.942M short; 79.7% long accounts. Liqwall at 15:22 UTC reported $1.16B OI, down 2.6%; +0.0081% funding; $11.5M liquidations, $10.6M long and $0.893M short; 75.2% of Binance accounts long. These providers use different exchange/contract universes. Do not average OI or liquidations. Both show positive funding, falling OI and long-heavy liquidations; account ratios are not notional exposure.

OptimistFi/Deribit at 14:00 UTC reported 30-day ATM IV 58.2%, +1.7-point 25-delta skew (calls richer), put/call 0.55 and $47.3M December 25 open interest. Near expiries were put-rich (Nov 12 -3.8, Nov 13 -4.1 points), while deferred expiries were call-rich (Dec 25 +2.9, Mar 26 +4.7). Preserve the term structure; max pain is not a forecast.

### ETF flows

Alpha Finance through the November 10 session: -$7.6M on Nov 10, -$10.4M on Nov 9, -$18.0M over the last seven sessions, +$1.3M over 30 sessions and +$1.71B cumulative net inflows since Nov 14, 2025. It reports 5/5 tracked funds complete, but no AUM or holdings. Grayscale GXRP accounted for $7.2M of the Nov 10 outflow. Redemptions can be arbitrage unwind rather than directional selling; flow prints are lagged.

### XRPL governance and price-source conflict

At 15:32 UTC the XRPL dashboard's own-node stream had heard 35/35 validators; 29 yes votes were required. SingleAssetVault had 23, LendingProtocol 22 and LendingProtocolV1_1 22; no amendment was in the 14-day activation countdown. Native XRPL lending remains inactive. These are the dashboard operator's own-node observations, not an official Foundation vote feed.

The same dashboard's amendments-page global header showed $1.0754 at 15:36 UTC, while OKX/Kraken references were near $1.059 and Fuelmaps' 15:00 mid was $1.0558. Its separate PriceOracle page showed the DIA XRP/USD value $1.0614 with a last update 05:52:29 UTC, already about 2.4 hours old at 08:16. Treat the $1.0754 header as an unresolved price-source outlier and exclude it from market features until independently reconciled.

## Institutional capital, stablecoins and regulation

### SBI/JPYSC — actual use, not XRP

SBI VC Trade's November 2 release reports JPYSC customer-lending balance above ¥10B and handling balance above ¥30B. The lending product allows customers to lend JPYSC to SBI VC Trade; this is not borrower collateral, not evidence of third-party loans, and not XRP demand.

SBI's September 7 release reports ¥1B of JPYSC trust reserves invested in short-term Japanese government bonds, with issuance around ¥20.1B and lending applications around ¥6.9B at that date. The 2026-06-01 legal change permits, subject to requirements, up to 50% of trust-backed stablecoin issuance to be invested in short-term government bonds of no more than three months' maturity or term deposits. This is real reserve deployment and JPYSC usage, not XRP buying.

SBI, Startale and BlackRock signed a basic agreement on October 27 to explore linkage between a tokenized money-market fund and JPYSC. SBI/Startale's Open Standard work on JPYSC/OUSD interoperability remains exploratory. No production settlement or XRP corridor is verified.

### Ripple National Trust Bank and RLUSD roles

Ripple's October 26 release reports final OCC approval for Ripple National Trust Bank. OCC's Corporate Applications Search lists the application as consummated/effective on the same date. The OCC's December 12, 2025 conditional approval letter states that final approval and authority to commence business follow completion of pre-opening requirements. The retrieved public evidence strongly corroborates final approval, but does not independently establish the bank's operational commencement.

RNTB's stated role is to manage segregated RLUSD reserves, act as collateral trustee for RLUSD holders and provide fiduciary digital-asset custody upon opening. Standard Custody & Trust Company, LLC remains the RLUSD issuer under its NYDFS limited-purpose trust charter. BNY is identified by Ripple as primary RLUSD reserve custodian. Issuer, reserve manager, collateral trustee and reserve custodian are distinct roles.

The OCC's final GENIUS Act rule, Federal Register document 2026-21706, is effective January 18, 2027. It covers payment stablecoin issuance by OCC-supervised entities and certain custody activities. Do not infer that issuer-specific rules apply to RNTB as though it were the RLUSD issuer.

### Coinbase, Circle, Ripple, SBI

Coinbase/Ripple RLUSD distribution across Prime, Exchange and Retail does not prove XRP spot purchases or collateral utilization. Coinbase Global Exchange collateral support was future scope at the announcement. PNC's limited Coinbase pilot uses Circle USDC on Ethereum and converts receipts 1:1 into USD deposit balances; this is a competing USDC rail, not XRP settlement. BNY/Standard Chartered custody and planned collateral integrations remain separate from XRP demand unless actual XRP collateral balances or settlement volumes are disclosed.

## Identity and exact-phrase research

SBIC East/Tokyo, Central/Nagoya and West/Osaka remain separate Japanese SME investment-consultation companies, not SBI Holdings. No new primary match was found for ASK Coin, “actual capital” as a standardized XRP term, or the exact phrase “SBIC, ChatGPT SBIC.” Dr. Kamilah Stevenson's person identity remains corroborated, but candidate YouTube channel ownership still lacks a first-party cross-link; no personal-channel video inventory is attributed. Camilla remains separate/unresolved.

## Nine-platform status

ChatGPT/GitHub repository access is verified, but the connector permission snapshot reports admin=true, maintain=true, push=true, pull=true and triage=true—overprivileged. Copilot has no formal PR approval. Claude, Grok, Gemini and Codex authentication/data flow remain unverified. Hugging Face remains BUILD_ERROR; Kaggle untested/no submission; Databricks HTTP 403/no workspace write; LunaRoute remains repository-declared canonical brain but endpoint authentication/data flow is unverified. No external-model data transfer occurred.

## PR reconciliation and blockers

Current PR #1661 remains draft, open and mergeable/clean, with zero formal reviews, approvals or review threads. Branch-protection details return HTTP 403; the visible fallback ruleset is disabled. The connector has admin-level permissions. GitHub Pages automatically publishes on a main push and publication remains unauthorized. Main and integration exclude `.config/gh/hosts.yml`, but 17 other open PR branch tips still contain that path; no contents were read and provider-side revocation is unverified.

Current file/blob reconciliation against #1661:
- #1660: 972 paths represented; 948 identical blobs, 24 different.
- #1640: 280 represented; 244 identical, 36 different.
- #1643: 670 represented; 661 identical, 9 different.
- #1642: seven represented; zero identical, seven different.
- #1653: three unique paths remain.
- #1614: 26 unique paths remain.
- #1611: one unique path; #1610: two; #1608: two.
- #1269: nine represented, three identical and six different; no unique path in current file inventory.
- #1317, #1318, #1320 and dependency PRs #1644–#1650/#1254/#1255 are represented but require blob-different semantic/version reconciliation.

No source PR was closed. Preserve unique research, prediction, graph, safety and topology work. Do not bulk-close.

## Forecast and merge decision

**Forecast: NOT_ISSUED.** Public web observations in this run have no Barrot raw-source receipts and are not model-eligible. No directional forecast, paper trade or real-money action occurred.

**No merge.** Exact-head tests and security gates pass on c7095fa5, but PR #1661 remains draft with zero approvals, branch-protection requirements unavailable, credential-path remediation unresolved, Pages publication unauthorized, and 967 non-workflow paths still requiring semantic review. The next evidence commit is documentation/research only and must pass its own exact-head full suite, dependency audit and fail-closed gate before any merge decision.

No deployment, secret rotation/revocation, Space restart, Kaggle submission, Databricks write, external-model transfer, funds transfer, force-push, history rewrite, destructive worktree operation or PR closure occurred.

---

Prior handoff history follows.

# Run28B — preserve workflow safeguards while enforcing LunaRoute-only

Captured: 2026-11-11T15:07:40Z

## Current repository state

Main remains `84f28ee7755607236231545a14f3d093c1baaa85`. The existing integration PR is [#1661](https://github.com/Barrot-Agent/B-Agent/pull/1661), branch `integration/xrp-v3-unified-main-20261111`, parent head `c0a893b236af460f167ed9682fc5d578587fcbdb`, 2,030 commits ahead/0 behind, 1,011 changed files (44 workflow files and 967 other paths). It remains draft, with zero formal approvals. Open PR inventory remains 374 (360 drafts, 14 non-drafts). No new PR was created and main was not modified.

## Why the first Run28 workflow quarantine needed correction

The initial disabled stub caused three core-suite regression failures because existing tests deliberately require the self-hosted-brain workflow to retain its exact-main-SHA guard, private-space validation, and separate deployment/secret-rotation confirmations. The core suite on head `c0a893b236af460f167ed9682fc5d578587fcbdb` had 711 passed, 3 failed, 8 subtests. The full repository suite job was still running at capture; no full-suite result is claimed. Dependency audit [43044543234](https://github.com/Barrot-Agent/B-Agent/actions/runs/43044543234) passed, and fail-closed gate [43044543362](https://github.com/Barrot-Agent/B-Agent/actions/runs/43044543362) passed.

Run28B restores the original guarded workflow and preserves `permissions: contents: read` and `persist-credentials: false`. It adds a job-level unconditional false condition before the existing manual exact-SHA and secret-rotation conditions. Thus the secondary brain cannot deploy, while its historical safety checks remain regression-tested. The `self_hosted_brain/` code is retained. No secret is read or rotated and no deployment is performed.

## Verification state

- Latest completed full-suite evidence remains on predecessor head `36602c9`: 3,444 passed, 3 failed, 8 subtests; the failures were map timestamp, exact-head failure-classification and provenance-label contracts.
- Head `c0a893b`: core suite 711 passed, 3 failed, 8 subtests due the temporary stub; full suite was still in progress at capture.
- Dependency audit and fail-closed gate on `c0a893b`: passed.
- Run28B commit: new exact-head core/full-suite/wheel/dependency/gate evidence pending.

## Research state

Run28 institutional evidence remains as recorded in `research/xrp_intelligence/20261111T145922Z-run28-institutional-capital-stablecoin-custody-and-collateral-reconciliation.json`. Key conclusion: SBI has disclosed equity/JV exposure to both Ripple and Circle; Circle's Arc uses USDC gas and names SBI as founding validator; native USDC and RLUSD coexist on XRPL; Coinbase distributes USDC and RLUSD and issues cbXRP; BNY is a common custody node; Ripple Prime/Standard Chartered collateral examples use RLUSD, not XRP; SBI VC Trade's lending list is product availability, not collateral balances; XRPL native lending is not active. These relationships do not establish incremental XRP spot demand. Forecast remains NOT_ISSUED.

The public-data collector remains integration-only and unexecuted on main. Raw receipts have 90-day artifact retention and no WORM anchor. Bybit live execution remains unverified; U.S./Mainland China 403 restrictions fail closed. Nine-platform coordination remains design-only except ChatGPT/GitHub connector authentication; LunaRoute is declared but not authenticated.

## Merge blockers and next action

PR #1661 remains draft and blocked: zero formal approvals; branch-protection details HTTP 403; visible fallback ruleset disabled; GitHub connector admin-level; `.config/gh/hosts.yml` absent from main/integration but previously found in 17 historical PR tips (contents not read, revocation not independently verified); GitHub Pages automatically publishes on main push and publication is unauthorized; HF Space automatic rebuild relationship is unknown; 967 non-workflow paths require semantic review.

Next action: verify Run28B exact-head core/full repository suite, wheel build/installation, dependency audit and fail-closed gate. No merge, main write, deployment, secret rotation, Kaggle submission, Databricks import, HF restart, paper trade, real-money action, force-push, reset, clean, stash or discard occurred.


# Run28 — XRP institutional network, capital taxonomy, current CI and LunaRoute-only safety

Captured: 2026-11-11T14:59:22Z

## Mission and repository state

XRP intelligence and prediction-engine mastery remain mission priority 1. Barrot V3 remains the execution, orchestration, safety and verification foundation. The current main SHA is `84f28ee7755607236231545a14f3d093c1baaa85`. The existing integration branch is `integration/xrp-v3-unified-main-20261111`; the Run28 evidence was captured from parent head `36602c9bc7c9e97d8319ec84d13d8971d208f4ff` before this Run28 commit. PR [#1661](https://github.com/Barrot-Agent/B-Agent/pull/1661) is the single active consolidated V3/XRP integration PR. It is open, draft, mergeable but unstable, 2,029 commits ahead/0 behind, with 1,010 changed files (44 workflow files and 966 non-workflow paths), 245,099 additions and 4,363 deletions. It has zero formal approvals/reviews and zero requested reviewers.

The complete main tree has 1,388 entries; integration tree 2,275. Open PR inventory is 374 (360 drafts, 14 non-drafts). No new PR was created. PR #1660 remains a superseded-source candidate; #1640/#1642/#1643 remain overlap candidates. No source PR was closed.

## Exact-head verification before Run28 correction

On exact head `36602c9bc7c9e97d8319ec84d13d8971d208f4ff`:
- Full repository suite: **3,444 passed, 3 failed, 8 subtests**, 59.98% inclusive coverage.
- Core suite: 714 passed, 0 failed, 8 subtests.
- Six-manifest dependency audit: passed, zero known vulnerabilities reported.
- Fail-closed gate: passed, merge disabled.

Runs: [full CI 43041561932](https://github.com/Barrot-Agent/B-Agent/actions/runs/43041561932), [dependency audit 43041562146](https://github.com/Barrot-Agent/B-Agent/actions/runs/43041562146), [fail-closed gate 43041562362](https://github.com/Barrot-Agent/B-Agent/actions/runs/43041562362).

The three failures were evidence-contract defects: current-map timestamp ordering, stale exact-head failure classification, and 16 provenance records missing the canonical `source` label. No Bybit adapter or prediction-runtime failure was observed. Run28 normalizes the evidence map, updates exact CI state, and adds a regression test for secondary-brain workflow quarantine. **The new Run28 commit has not yet been tested; exact-head CI is pending.**

## Workflow and security review

All 44 changed workflow diffs were scanned; eight high-risk workflows were read in full. The `sync-self-hosted-brain.yml` workflow is now quarantined with no token permissions and an always-false job because `BARROT_SYNC.md` declares LunaRoute as the sole Barrot brain. The historical `self_hosted_brain/` code is retained; no deployment occurred. Changed workflows now classify as 26 quarantined/disabled and 18 active.

The XRP public-data collector exists only on the integration branch. It defines 47 source endpoints: 43 hourly, two weekly and two excluded noncommercial XRPL node sources; 45 are scheduled. Its GitHub permissions are read-only (`contents:read`, `actions:read`) and it uploads artifacts rather than committing data. Bybit uses public ticker/order-book endpoints with matching-engine `cts`, system `ts`, depth and imbalance calculations; it has fixture/mocked tests only. U.S./Mainland China 403 restrictions fail closed; no proxy or bypass. Raw receipts are retained 90 days, per-run feature-store artifacts 7 days and daily backups 90 days. GitHub artifacts/cache are not WORM or permanent immutable storage. No scheduled ingestion run has executed on main.

Other high-risk workflows remain gated and were not dispatched: Coinbase paper trader (manual confirmation, artifact-only), Databricks/Kaggle operations (explicit confirmations), A2A worker deployment (explicit deploy and secret-rotation confirmations), and PR approval workflow (human approval required). Hugging Face sync and Databricks bundle deployment are disabled. No paper trade, Kaggle submission, Databricks import, HF deployment, secret rotation or external deployment occurred.

Main CI run 42944864014 succeeded (718 tests). Main Pages build 42944862534 succeeded after a prior main push; Pages publication is an automatic merge side effect and remains unauthorized. The current branch-protection endpoint returns HTTP 403, so effective required checks/approval rules cannot be independently verified; visible fallback ruleset 10863829 is disabled. The GitHub connector reports admin/maintain/push permissions, which exceeds least privilege. The path `.config/gh/hosts.yml` is absent from main and integration, but the previous verified inventory found it in 17 other open PR tips; contents were not read and provider-side revocation is not independently verified. Do not rewrite historical branches or read credential contents.

## XRP and institutional relationship research

### SBI, Ripple, Circle and Arc

SBI Holdings' June 9, 2025 release states that SBI Holdings had invested in Ripple since 2016, held approximately 9% as an external largest shareholder, and operates the SBI Ripple Asia joint venture with Ripple. This is a dated issuer disclosure; current November 2026 ownership has not been refreshed.

The same SBI release reports a $50M Circle equity investment split $25M SBI Holdings and $25M SBI Shinsei Bank. SBI and Circle later established SBI Circle Holdings to promote USDC in Japan; SBI VC Trade distributed USDC. These are equity and distribution relationships, not XRP purchases.

Circle's September 16, 2026 Arc mainnet release names SBI Group as a founding validator and Coinbase among exchange partners. Arc fees are paid in USDC, without a volatile native gas token; Aave and Morpho anchor credit markets, and Circle lists BNY and other institutions in its ecosystem. Arc is a distinct stablecoin-native network, not XRPL. This supports a competing hypothesis: SBI and Coinbase participate across networks and stablecoins rather than exclusively backing XRP.

Circle announced native USDC on XRPL on June 12, 2025. USDC and Ripple's RLUSD therefore coexist on XRPL, but this does not establish a direct Circle-Ripple commercial partnership or XRP bridge-asset volume.

Circle's October 16, 2026 company blog reports H1 2026 USDC onchain volume above $36T, $315B mint/redemption, $819M distribution-partner and transaction costs, and approximately 77% of stablecoin transaction volume. It identifies Coinbase as its largest and longest-standing partner and quotes Coinbase average USDC held in products at $20B in Q2 2026, up 44% year over year. These are company-reported figures; Coinbase's exact share of Circle partner economics is not disclosed. Coinbase's 2023 agreement with Circle includes an equity stake and ongoing commercial relationship.

### Coinbase, Ripple and wrapped XRP

Ripple's October 28, 2026 announcement made RLUSD available through Coinbase Prime, Exchange and Retail on XRPL, Base and Ethereum. The announcement said Coinbase Global Exchange collateral availability would follow; it must not be represented as already live.

Coinbase's cbXRP proof page refreshed at 14:30 on November 11 and displayed 151,709,177.16 XRP reserves against 151,706,930.63 cbXRP supply, a displayed surplus of 2,246.53 XRP (about 0.00148%). This is issuer-published, not an independent audit or proof of incremental spot buying.

### Ripple Prime and custody/collateral

Ripple Prime's October 15 release describes 24/7 RWA perpetual swaps across 100+ reference markets, including Virtu, using Trade.xyz contracts on Hyperliquid. RLUSD may be used as collateral. No XRP collateral leg is disclosed.

BNY's October 27 release says it is primary reserve custodian for RLUSD and now supports XRP and RLUSD custody. Intended direct RLUSD mint/redeem and C2FO tokenized trade-finance work remain subject to approvals/exploration. BNY also provides Circle USDC reserve custody and mint/burn services, making it a common institutional custody node, not evidence of a direct Circle-Ripple partnership.

Ripple's October 12 release says Standard Chartered RLUSD custody on XRPL is live through its DIFC branch. The planned LMAX RLUSD collateral-mirroring capability remains subject to final documentation, testing, applicable laws, internal approvals and jurisdictional readiness. This is RLUSD collateral, not XRP collateral.

### SBI VC Trade and XRPL lending

SBI VC Trade's directly rendered lending page states 29 supported assets, including XRP, USDC and JPYSC; RLUSD is absent. A search-result snippet reported 32, so the page/index discrepancy is preserved; the direct rendered page is used for this capture. The page describes customers lending assets to SBI VC Trade. It does not disclose actual XRP loan balances, utilization, margin-collateral eligibility or collateral haircuts. Its 10% USDC/84-day course is dated to the April 30, 2026 solicitation and is not a current guaranteed rate.

The live XRPL amendment dashboard at 14:28 UTC reported 35 validators and a 29-vote threshold: SingleAssetVault 23/35, LendingProtocol 22/35 and LendingProtocolV1_1 22/35, with zero amendments in the 14-day countdown. Native lending is not active. SingleAssetVault can hold XRP, IOU or MPT, so XRP collateral is not mandatory even if the lending stack later activates.

### Evernorth and actual capital

The November 9 SEC 424B3 registers 73,688,162 Class A shares for potential resale and separately registers 239,653 sponsor warrants. Evernorth says it receives no proceeds from selling-securityholder resales, except amounts from warrant exercise. The share pool includes existing Class A, Class C conversion, company-unit redemption/exchange and warrant-exercise shares; registration is not immediate float or company cash.

The SEC filing defines the Advance Funding Subscription as $214.05M cash plus 600,000 XRP. SBI's $200M commitment is included in that aggregate advance-funding pool, not additive. Keep this separate from XRP contributed in kind, cash used to buy XRP, debt, undrawn Cantor ELOC capacity, registered resale and actual secondary sales. "Actual capital" is not a standardized XRP metric.

### Identity research

SBIC East/Tokyo, Central/Nagoya and West/Osaka remain three distinct Japanese SME investment-consultation companies, not SBI Holdings. Tokyo SBIC's 2025 ChatGPT/Copilot/RAG training was for investee companies and delivered by VOST; it is not an OpenAI partnership.

"ASK Coin" remains unresolved: Askcoin UCID 4640 and Permission Coin ASK UCID 7105 are separate candidates; no XRP/XRPL contract or Ripple relationship is verified. "Actual capital" remains a nonstandard phrase and must be resolved through the categories above. Exact "SBIC, ChatGPT SBIC" searches did not find a formal entity or OpenAI partnership.

First-party learn.kamilahstevenson.com identifies Dr Kamilah Stevenson/The Wealth Doctor. The iHeart XRP Podcast interview has the guest say her YouTube name is "doctor Camilla Stevenson" and warn of fake pages; the transcript spells social names inconsistently. No first-party YouTube cross-link verifies the handle. Candidate handles remain unverified; no personal-channel video inventory is attributed.

## Prediction and data eligibility

**Forecast status: NOT_ISSUED.** Run27 market observations remain asynchronous: the 14:00 six-venue spot snapshot and 14:34 dashboard reference are not synchronized; ETF flows disagree by provider and fund coverage; exchange-wallet labels include cold storage/newly tracked wallets; perpetual OI aggregates differ materially. Run28 institutional announcements are not XRP flow data. None of these records is admitted to the model feature store.

The collector is designed and tested with fixtures, not verified as a scheduled main-branch service. SHA-256 raw-source receipts are designed, but this run captured no raw web bytes, created no raw-source hashes and has no independent WORM/timestamp anchor. Walk-forward evaluation, calibration, drift and shadow outcomes remain insufficient for directional forecasts.

## DESIGNED / EXECUTED / VERIFIED

- **DESIGNED:** nine-platform capability/authentication map; point-in-time ingestion/feature store; source provenance; walk-forward baselines; forecast ledger; LunaRoute-only brain boundary.
- **EXECUTED:** GitHub repository/tree/PR/workflow reads; 44 workflow diff scan; eight high-risk workflow full reads; public primary-source research; exact-head core/full-suite/dependency/gate runs; Run28 map/test/workflow/handoff correction on the existing integration branch.
- **VERIFIED:** current main SHA and branch head before Run28; PR #1661 inventory; predecessor exact-head run 430415 results; dependency audit and fail-closed gate; source pages and their explicit limitations.
- **NOT VERIFIED:** Run28 commit CI, live Bybit endpoint, scheduled collector on main, WORM archive, LunaRoute authentication, eight external platform connections, out-of-sample predictive lift, shadow outcomes, branch-protection requirements and publication authorization.

## Backlog classification and next action

- #1661 — active consolidated integration, **blocked** pending Run28 exact-head CI, semantic review, formal approval, branch-protection visibility, credential remediation and Pages authorization.
- #1660 — **superseded-source candidate**, retain until #1661 is merged and verified on main.
- #1640/#1642/#1643 — **overlap candidates**, retain and reconcile differing blobs after verified successor merge.
- #1659 — **blocked** by LunaRoute-only brain declaration; retain historical code, no deployment.
- #1653 — **unique/unreviewed** repository graph.
- #1655 — **unique/unreviewed** structural analysis/catalog.
- #1614/#1611 — **unique/unreviewed** point-in-time feature and forecast-ledger work.
- #1610 — **unique/unreviewed** autonomous-writer safety.
- #1608 — **unique/unreviewed** C2FO/Evernorth research.
- #1269 — **unique/unreviewed** OBJ topology.

Next concrete action: verify the new Run28 commit's exact-head full suite, wheel build/installation, dependency audit and fail-closed gate. If green, update PR #1661 description with exact evidence; do not mark ready or merge until semantic review, independent approvals, branch protection, credential revocation and publication authorization are resolved.

No merge, main-branch write, deployment, secret rotation, Kaggle submission, Databricks import, HF Space restart, paper trade, real-money action, force-push, reset, clean, stash or discard occurred.


# Run 26e — source-fixture repair, XRP lending governance and institutional collateral reconciliation

Captured: 2026-11-11T14:38:27.479Z

## Repository state before repair

- Main: `84f28ee7755607236231545a14f3d093c1baaa85`.
- Existing integration PR #1661: branch `integration/xrp-v3-unified-main-20261111`, pre-repair head `acf985960e1491634451daefb614eaa3c9707917`, 2,027 commits ahead, zero behind, 1,008 changed files, 44 workflow files; draft, zero formal approvals, zero formal reviews, zero unresolved threads.
- Complete trees: main 1,388 entries / 1,288 files / 86 workflows; integration 2,273 entries / 2,164 files / 87 workflows.
- Open PR inventory: 374 total, 360 drafts, 14 non-drafts.
- No new PR or branch.

## Run26d exact-head CI failure and root cause

Head `acf985960e1491634451daefb614eaa3c9707917`:
- Core suite: 714 passed, zero failed, eight subtests.
- Full suite: 3,436 passed, 11 failed, eight subtests, 3,447 collected.
- Dependency audit: six manifests, zero known vulnerabilities, passed.
- Fail-closed gate: passed, automatic merging disabled.

The 11 failures were diagnosed. Four documentation/contract tests retained the prior 46 endpoint / 42 hourly-source counts. Seven ingestion tests used the shared fake fetcher, which did not supply the newly added SBI VC Trade HTML source; this caused one fixture-only source failure and downstream receipt-count mismatches. The new SBI parser identity, HTML routing and digest-only archive tests themselves did not fail. The fix updates the shared fixture and every current inventory assertion/document; historical v1.1 snapshots remain historical.

## Run26d inventory correction

The collector now has 47 endpoint definitions: 43 hourly endpoints plus two weekly CFTC endpoints = 45 scheduled sources; two noncommercial XRPL nodes remain excluded by default. Earlier Run26d wording saying “43 scheduled” referred to hourly `SCHEDULED_ENDPOINTS` only; total scheduled including weekly sources is 45.

## New XRP institutional and protocol research

- Ripple officially announced 24/7 RWA perpetual swaps on October 15, 2026, with 100+ reference markets and Virtu named as an early institutional client. Ripple Prime is principal to the client; the reference contracts are Trade.xyz perpetuals on Hyperliquid. RLUSD collateral is jurisdiction-dependent. No XRP settlement or XRP collateral leg, notional, RLUSD collateral balance or actual capital amount is disclosed.
- Independent xrpldashboard capture at 2026-11-11 13:48 UTC: SingleAssetVault 23/35, LendingProtocol 22/35, LendingProtocolV1_1 22/35. With 35 validators heard, strictly more than 80% requires 29 yes votes for 14 consecutive days. Zero amendments were in the activation countdown. A signed daily leaf at 02:00 UTC records 23/35, 22/35 and 22/35 respectively; leaf hash `a6441e622ab4135729b1fd30aed7d362c404e251d314cafc0818eaad0726301d`. The dashboard reports its signature verifier as VERIFIED; this run did not independently execute the verifier.
- XLS-65 SingleAssetVault is single-asset (XRP, IOU or MPT), not a mixed-asset basket. XLS-66 LendingProtocol creates fixed-term loans from vaults; credit judgment remains off-ledger and the current design does not mandate XRP collateral. Both need activation for the native lending stack.
- XRPLF Discussion #617 proposes a native XRP first-loss risk sleeve, but it is a pre-standard community idea (one participant, zero comments, no labels), not an official XLS or amendment. It could create XRP lockup only if adopted; it is not current demand.
- SBI VC Trade's centralized lending asset list includes XRP, USDC and JPYSC; that is separate from native XRPL lending and no actual outstanding balances are disclosed.
- Permission's official ASK token docs say current chains are Base and Polygon; no XRPL support is listed. A separate Askcoin listing preview shows zero supply and no active listing detail; askcoin.net is parked. Do not conflate Permission ASK and Askcoin.
- Official Kamilah Stevenson site self-identifies Dr. Kamilah Stevenson / The Wealth Doctor and describes stock, crypto and real-estate investing education. DailyCoin links two XRP-related YouTube videos by that name, but the creator channel is not independently verified. The TEDx health talk is a verified event attribution; cross-linking it to the crypto channel remains unverified.
- “Actual capital” remains an ambiguous phrase, not a unique XRP/SBI entity. Barrot records settled cash, in-kind XRP, accepted subscriptions, outstanding loans, posted collateral and actual purchases separately.

Artifact: `research/xrp_intelligence/20261111T143827Z-run26e-ripple-prime-rwa-swaps-xrpl-lending-governance-and-exact-phrase-reconciliation.json`. All new web observations are research-only, no raw receipts or feature-store admission, no prediction.

## Current integration and safety

The source-adapter fixture repair, current endpoint-count corrections, updated contracts, current nine-platform map, Run26e research artifact and this handoff update are being committed on the existing #1661 branch. Exact-head full-suite, six-manifest audit and fail-closed checks must run again on the repair commit. Do not transfer any predecessor result.

#1661 remains draft. #1660 remains a superseded-source candidate and is not closed. Unique PRs remain open. Main is unchanged. Main Pages deployment is still an automatic side effect and not authorized. Branch protection details remain HTTP 403; visible fallback ruleset is disabled; connector admin permission exceeds least privilege. The historical 17-branch credential-path exposure remains unremediated/independently unverified.

Forecast: **NOT_ISSUED**. No synchronized XRP market panel or calibrated out-of-sample lift. No merge, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push, reset, clean, stash, discard or PR closure occurred.

Next: verify the repair commit with exact-head full suite, dependency audit and fail-closed gate; then add scheduled raw-only monitoring for Ripple Prime's official announcement and XRPL amendment voting, followed by scenario/counter-hypothesis generation. Keep forecast issuance disabled.

---

# Run 26d — SBI VC Trade lending terms, XRP lending eligibility and raw-only source ingestion

Captured: 2026-11-11T14:24:14.339Z

## Repository and integration state

- Main SHA: `84f28ee7755607236231545a14f3d093c1baaa85`; main tree: 1,388 entries / 1,288 files / 86 workflows.
- Consolidated integration PR: [#1661](https://github.com/Barrot-Agent/B-Agent/pull/1661), branch `integration/xrp-v3-unified-main-20261111`.
- Pre-change branch head: `037d730244379d6e089c470b4034c12c337598ea`; 2,026 commits ahead of main, zero behind; 1,007 changed files.
- Integration tree: 2,272 entries / 2,163 files / 87 workflows.
- Open PR inventory: 374 total; 360 drafts; 14 non-drafts. No PR was created or closed.
- PR #1661 remains draft with zero formal approving reviews and zero review threads. No merge.

## DESIGNED and EXECUTED — SBI VC Trade source correction

The official general lending page lists 29 eligible assets, including XRP, USDC and JPYSC; RLUSD is not in that lending list, although the separate service overview lists RLUSD for trading. The lending page identifies the contract as a consumption-loan transaction, states there is no early termination, and warns about asset-return and price risks.

The same page shows a historical USDC course dated April 30, 2026: 84 days, 100–5,000 USDC, 10% annual rate. A separate USDC product page describes a 12-week term and approximately 5% annual rate as planned and market-dependent. These are distinct offer contexts; neither proves the rate currently available. Current subscriptions, participants, outstanding USDC/XRP and interest paid remain undisclosed.

The general service overview/transfer page states generic collateral valuation factors of 50% for crypto assets and 100% for electronic payment instruments. This does not establish token-specific eligibility or actual collateral balances.

Primary sources:
- https://www.sbivc.co.jp/services/lending
- https://home.sbivc.co.jp/usdc
- https://www.sbivc.co.jp/services/service-overview
- https://www.sbivc.co.jp/services/transfer

The new artifact `research/xrp_intelligence/20261111T142003Z-run26d-sbi-vc-trade-lending-offer-and-xrp-eligibility-correction.json` preserves dated offer contexts, the XRP/USDC/JPYSC lending list, RLUSD exclusion from that list, competing hypotheses and unknown actual balances. Web page bytes were not captured; no raw receipt or model admission is claimed.

A new scheduled collector source, `sbi_vc_trade_lending_page`, is added as digest-only and raw-only. It validates publisher/asset markers, creates a SHA-256 receipt when the collector runs, retains no HTML payload, and cannot emit features. The workflow remains on the integration branch and is not yet active on main.

## Exact-head verification baseline before this change

Pre-change head `037d730244379d6e089c470b4034c12c337598ea`:
- Full repository suite: 3,443 passed, zero failed, eight subtests passed; 59.98% inclusive coverage.
- Core suite: 714 passed plus eight subtests.
- Installed wheel and packaged primary mission verification passed.
- Six-manifest dependency audit passed with no known vulnerabilities.
- Fail-closed merge gate passed with automatic merging disabled.

Runs: [full CI 43035859694](https://github.com/Barrot-Agent/B-Agent/actions/runs/43035859694), [dependency audit 43035859651](https://github.com/Barrot-Agent/B-Agent/actions/runs/43035859651), [fail-closed gate 43035859649](https://github.com/Barrot-Agent/B-Agent/actions/runs/43035859649).

The Run26d code/test/artifact/handoff commit created after this baseline requires fresh exact-head full-suite, dependency-audit and fail-closed verification. Do not transfer the predecessor's results to the new commit.

## Workflow, security and integration review

- The 44 workflow files changed by the integration contain 24 fully disabled stubs, one additional job-level `if: false` quarantine, and 19 active workflows.
- Active external operations require explicit manual confirmations and exact-main-SHA checks. No Databricks import, Kaggle download, Cloudflare deployment, Hugging Face deployment, paper-trading run or external-model transfer was dispatched.
- XRP ingestion is hourly plus daily, read-only (`actions: read`, `contents: read`), stores raw receipts as artifacts and feature-store checkpoints with 7/90-day artifact retention plus an evictable Actions cache. It has not executed on main because the workflow exists only on the integration branch and its job is guarded to `refs/heads/main`.
- Main CI at `84f28ee` passed in [run 42944864014](https://github.com/Barrot-Agent/B-Agent/actions/runs/42944864014). Main Pages automatically deployed in [run 42944862534](https://github.com/Barrot-Agent/B-Agent/actions/runs/42944862534). This external publication remains unauthorized for another merge.
- Main Pillars Consistency Check failed in [run 43025487840](https://github.com/Barrot-Agent/B-Agent/actions/runs/43025487840); prior diagnosis remains missing GitHub App credentials, Databricks HTTP 403 and Hugging Face BUILD_ERROR.
- Main branch-protection endpoint returns HTTP 403. The only visible repository ruleset, “Fall Back”, is disabled. Repository metadata reports connector permissions admin/maintain/push. Required approval/check policy is not independently verified.
- `.config/gh/hosts.yml` is absent from main and #1661; the previous 17-branch-tip exposure inventory remains a remediation candidate. Contents were not read; provider-side OAuth revocation remains unverified.

## Backlog classification

- **Blocked — active integration:** #1661, sole consolidated V3/XRP integration. Keep draft until semantic review, least-privilege/security remediation, independent approval, branch-protection visibility and Pages authorization are resolved.
- **Superseded-source candidate:** #1660, stale base `afb3024`, mergeable false; retain until successor is merged and verified.
- **Supersession/overlap candidates:** #1640, #1642, #1643 and dependency/action PRs #1644–#1650. Do not close until exact replacement content is verified on main.
- **Unique/unreviewed; preserve:** #1653, #1614, #1611, #1610, #1612, #1269, #1608 and other unique research/security work. Reconcile paths and ancestry before any successor integration.

## Prediction and platform state

- Prediction remains **NOT_ISSUED**. No synchronized direct spot/depth panel, immutable external timestamp anchor, durable cross-run WORM store, sufficient overlap-adjusted out-of-sample/shadow outcomes or validated lift over all four baselines has been established.
- ChatGPT/GitHub access is verified; connector privilege exceeds least privilege. Claude, Grok, Gemini and Codex are not authenticated; Copilot has no formal approval; Kaggle is untested; Databricks returned HTTP 403; Hugging Face reports BUILD_ERROR; LunaRoute authentication/data flow is unverified.
- SBIC East/Central/West remain separate statutory companies, not SBI Holdings. SBIC ChatGPT references are educational, not a verified OpenAI partnership. ASK Coin remains unresolved. Kamilah Stevenson TEDx attribution is verified; personal channel ownership is not.

## Safety and next action

No merge, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push, reset, clean, stash, discard or PR closure occurred.

Next: verify the new Run26d exact head with full suite, six-manifest dependency audit and fail-closed gate; then continue semantic review of the ingestion, feature-store, forecast-readiness and active workflow code. Keep forecast issuance disabled.

---

# Barrot XRP Mission Handoff — Run21

As of 2026-11-11T10:26:35Z
Mission: XRP intelligence and prediction-engine mastery, priority 1.
Foundation: preserve Barrot V3 as execution, orchestration, safety and verification.

## Repository
Main SHA 84f28ee7755607236231545a14f3d093c1baaa85.
Integration head tested: a62bad5747fc89b7e851aa9e0b2f3f58ae94106e.
PR #1661 open, draft, mergeable clean; 995 changed files, 44 workflows, 951 other paths.
2,010 commits ahead, zero behind. Complete trees: main 1,388 entries, integration 2,260 entries.
374 open PRs: 360 drafts, 14 non-drafts. Local clone still fails DNS; remote GitHub API retrieval succeeded.

## Exact-head verification
Full suite: 3,423 passed, zero failed, eight subtests, 59.98% coverage, 95.96 seconds.
Core suite: 714 passed, zero failed, eight subtests.
Wheel build, install and primary mission verification passed.
Six dependency manifests audited; zero known vulnerabilities.
Fail-closed PR and push gates passed; automatic merge remains disabled.
Full CI 43003897822; dependency audit 43003898372; gates 43003898327 and 43003891044.
Main CI 42944864014 passed 718 tests; latest Cross Analysis 42998707871 succeeded; Pages 42944862534 succeeded as automatic side effect.
The preceding head failed two exact-phrase assertions in research JSON; corrected. No runtime prediction-engine failure.

## Prediction engine
Implemented: 46 public source definitions; read-only collector; SHA-256 receipts and receipt-chain verification; SQLite point-in-time feature store; four deterministic baselines; chronological walk-forward with purge/embargo and overlap-adjusted effective sample size; calibration; univariate PSI drift diagnostics; Ed25519-attested forecast ledger.
Not production verified: independent WORM/timestamp anchor; replayable cross-run feature store; synchronized historical spot/L2/derivatives/flows/collateral; vintage-aware macro events; scenario/counter-hypothesis engine; trusted evaluator key; independent shadow outcomes; out-of-sample lift.
Issuance gates: 100 OOS samples, 100 shadow outcomes, two independent source groups, ten non-overlapping horizon multiples, calibration error no greater than 0.05, lift over four baselines on Brier score and log loss, independent Ed25519 attestation.
Forecast NOT_ISSUED. Collector is on integration only and guarded to run on main; no successful main ingestion run.

## Current market
OKX XRP-USDT at 09:58:10.975 UTC: 1.0593, bid 1.0591, ask 1.0592, 24h volume 68.10M XRP.
Kraken retrieval: $1.05705, bid $1.05729, ask $1.05730; no provider event timestamp. USDT/USD 0.99894. Normalized asynchronous midpoint difference 0.0693%, not arbitrage.
Fuelmaps spot depth at 02:00 UTC: within 1%, $14.2M bids / $10.8M asks; within 5%, $29.0M / $14.6M; stale by 8h26m.
Basis Binance XRPUSDT perpetual book at 06:28 UTC: within 1%, $16.7M bids / $14.7M asks; not spot.
TradRadar OI $1.57B (-4.96%), funding +0.0094%/8h, long-heavy liquidations. Liqwall OI $1.15B (-2.2%), funding +0.0066%/8h, long-heavy liquidations. Different universes; do not average.
Alpha ETF Nov10 -$7.6M, 30-session +$1.3M, cumulative +$1.71B. CryptoKeyhole Nov10 partial; XRP Insights Nov9 -9.54M XRP. Preserve separate universes.
October U.S. CPI beat consensus; Treasury yields and dollar rose. Broad risk-off context, not XRP-specific causation.

## Institutional and identity
Evernorth named Ripple, Kraken, Coinbase and BitGo as planned Q4 execution partners for its 473M XRP treasury. Agreements remain subject to conditions; deployment amounts and returns not verified.
Coinbase RLUSD distribution, PNC USDC-to-USD pilot, BNY XRP/RLUSD custody and Ripple Treasury AI/RLUSD capabilities do not establish XRP purchases or payment volume.
SBI's $200M Evernorth cash is included in the $214.05M advance-funding pool, not additive.
Japan SBIC East/Tokyo, Central/Nagoya and West/Osaka are distinct statutory companies, not SBI Holdings. SBIC ChatGPT activity is educational.
ASK Coin exchange and Permission Coin ASK token are separate candidates; no XRP link verified.
Actual capital must separate cash, cash deployed, in-kind XRP, debt, facilities, ELOC and resale registration.
Kamilah Stevenson person identity confirmed; candidate YouTube channel remains unverified. 21 candidate references, zero verified creator inventory.

## Nine platforms
ChatGPT GitHub API read/write on integration verified; no main write or secrets access.
Claude, Grok, Gemini and Codex unverified. Copilot no formal approval. Hugging Face prior build error; no deployment. Kaggle untested. Databricks prior HTTP 403. LunaRoute endpoint auth/data flow unverified. No external-model transfer.

## Security and backlog
Main protected, integration unprotected. Detailed branch protection endpoint 403; visible fallback ruleset disabled. Main push automatically publishes Pages; publication authorization absent.
Credential path .config/gh/hosts.yml absent main/integration but present on 17 of 17 rechecked open PR tips. Contents not read. Repo reports OAuth revoked; provider revocation unverified.
#1661 blocked. #1660 superseded candidate retained. Preserve unique #1653, #1614, #1611, #1610, #1612, #1269 and #1608. Reconcile overlap candidates #1640, #1642, #1643, #1644–#1650, #1317, #1318, #1320, #1254, #1255. No PR closed.

## Next actions
Complete semantic review of 951 non-workflow paths. Resolve branch protection, approvals, credential revocation evidence and Pages side effect. Preserve unique PRs. Only after authorized merge, verify merge commit, refetch main, verify files, run main CI and first read-only ingestion. Implement WORM anchoring and replayable store. Keep forecasts disabled.

No merge, deployment, secret action, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or PR closure.


## Run22 — 2026-11-11T11:08Z — exact-head verification, market microstructure, theft-linked flow, Ripple Prime leadership and XRPL quantum roadmap

### Repository and CI
- Main remains `84f28ee7755607236231545a14f3d093c1baaa85`; integration branch remains `integration/xrp-v3-unified-main-20261111`, parent/current head before this documentation update `64b8738710f4823af1641a9704dd3948ccc640a1`; 2,011 ahead, zero behind.
- PR #1661 remains open/draft, reported mergeable; zero formal reviews, approvals and review threads. Open PR inventory: 374 (360 drafts, 14 non-drafts). Complete trees: main 1,388, integration 2,260. Local Git clone still fails DNS; remote GitHub API works.
- Exact head `64b8738`: 3,423 full-suite tests passed, zero failures, eight subtests, 59.98% coverage in 94.07s; 714 core tests passed; wheel build/install and primary mission verification passed; six dependency manifests audited, zero known vulnerabilities reported; fail-closed PR/push gates passed. Full CI [43005232066](https://github.com/Barrot-Agent/B-Agent/actions/runs/43005232066), audit [43005232071](https://github.com/Barrot-Agent/B-Agent/actions/runs/43005232071), PR gate [43005232185](https://github.com/Barrot-Agent/B-Agent/actions/runs/43005232185), push gate [43005224271](https://github.com/Barrot-Agent/B-Agent/actions/runs/43005224271).
- Coverage floor remains 53%, below the previous 70% target; measured coverage is 59.98% for barrot_agent, not all repository packages.
- Main scheduled Cross Analysis [43007129290](https://github.com/Barrot-Agent/B-Agent/actions/runs/43007129290) succeeded. Its workflow has contents:read, persist-credentials:false, performs read-only entity/sentiment analysis and uploads artifacts; it does not commit or push. Main's legacy signal-accuracy workflow is disabled with permissions:{} and if:false. Main push still triggers Pages deployment; publication authorization remains unresolved.

### Current XRP market and microstructure — descriptive only
- OKX XRP-USDT at provider timestamp 2026-11-11T10:21:28.166Z: last 1.0625, bid 1.0622, ask 1.0623, 24h volume 68.13M XRP. Kraken XRP/USD retrieval: last $1.06507, bid $1.06483, ask $1.06484, 24h volume 33.45M XRP, no provider timestamp. Kraken USDT/USD midpoint about 0.999025. Normalized OKX/Kraken midpoint difference about 0.34%, asynchronous; Kraken last is above displayed ask. Do not use as an executable spread signal.
- Fuelmaps spot order-book snapshot 11:00 UTC, mid $1.0605, six venues: within ±1%, $9.5M bids/$8.6M asks (52.6% bid share); ±5%, $19.6M/$13.2M (59.8%); ±10%, $28.3M/$14.5M (66.2%, five of six venues). Largest displayed bid $3.4M at $1.000. Binance and Bitget are excluded; orders can cancel; hourly book is an average of one-minute observations. This is resting spot liquidity, not guaranteed support.
- Binance 30-day cumulative funding reached +0.18%, highest since October 2025, per CryptoQuant's original Nov 10 Quicktake. CryptoTicker reports its direct OKX query found 76 positive settlements out of the last 100 since Oct 9, cumulative +0.39%, current period +0.01%; raw response was not independently captured here. These are distinct venue/window measures.
- Binance XRPUSDT via cached public-market page: OI about $323.31M, -5.37% 24h, funding +0.0100%/8h. Coinalyze partial 2/22 coverage at 07:31 UTC: Binance long accounts 74.65%, Bybit 81.42%; taker buy share about 48.5% and 50.5%, respectively. Account ratios are not notional exposure.
- Liqwall all-exchange OI $1.15B at 10:22 UTC, -1.9%/24h; Kodexius seven contracts $639.27M at 06:09 UTC, weighted funding +0.0094%/8h. These universes differ; do not average.
- TokenPost reports Binance spot CVD about -4.33M XRP on Nov 9: sell-initiated trading dominated the measured window, not equivalent cash outflow.
- ETF correction: SoSoValue's $10.42M XRP ETF outflow belongs to **November 9**, not November 10; about $9.40M was Bitwise, $0.811M Canary, $0.213M 21Shares. Nov 3–6 were flat. Oct 12–Nov 9 cumulative net outflow was about $4.2M, roughly 0.3% of $1.24B net assets. Multiple outlets repeat the same SoSoValue dataset; this is one underlying source group, not independent confirmations.
- Binance theft-linked XRP: CryptoTicker reports a direct query at validated ledger 108,255,241 (Nov 11 06:44 UTC): 33,455,915 XRP moved from the last dormant wallet at 00:01 UTC into collection wallet `ryB7NESZcttqzRioiD5L6Kf5tFL87ktmx`; collection wallet held 29,466,416 XRP and had sent 32.34M XRP in 193 payments since the prior measurement. Elliptic is cited for mostly THORChain swaps into BTC. Explorer is JS-rendered and the ledger query was not independently replayed here. Payments are not proof of executed sales or final cash-out; buyer identity is unknown.

### Institutional and protocol developments
- CoinDesk reports Marc Asch will leave Ripple Prime at year-end 2026; Noel Kimmel, SVP, will take over leadership. Ripple Prime offers institutional prime brokerage, clearing and financing; Ripple says RLUSD is collateral for some products. This is not evidence of XRP collateral eligibility or XRP purchases.
- XRPL Foundation's 2027 protocol roadmap lists Quantum as a proposed, unapproved amendment using ML-DSA-44. Migration study is scheduled for H1 2027; development/review/audit in late 2027 or 2028; 640 build hours, 400 Ripple review hours, $215k–$255k estimated cost. Quantum-signed payment size estimated 5,331 bytes versus 1,704 baseline (3.13x). Activation requires validator approval; roadmap items are not promised. Draft spec #295 still records cross-implementation seed derivation mismatch, incomplete admin RPC support, and testing/audit gaps. Long-horizon security milestone, not near-term XRP demand.
- Exact phrase ASK Coin / “actual capital” / “SBIC, ChatGPT SBIC” remains unresolved at primary-source level. Regional SBIC entities remain distinct from SBI Holdings. Kamilah/Camilla YouTube inventory remains candidate-only pending platform-side channel verification.

### Prediction and safety
Forecast remains `NOT_ISSUED`. These web observations are not model-eligible: no Barrot collector raw receipts, trusted timestamps or replayable point-in-time feature-store admission were created in this run. Preserve competing hypotheses: crowded-long fragility; spot absorption/short-squeeze potential; macro-driven risk repricing; and positive funding caused by hedged basis/relative-value demand. Do not issue direction from this snapshot.

### Next actions
1. Finish 951-path semantic review, prioritizing V3 runtime, ingestion, point-in-time store, forecast ledger and public surfaces.
2. Add source-receipted direct funding histories and hourly Fuelmaps depth with explicit venue coverage and stale-age controls.
3. Reconcile derivatives by contract and XRP-denominated OI; never average incompatible vendor universes.
4. Correct ETF event date to Nov 9 and preserve SoSoValue source-group dependence.
5. Add XRPL Quantum proposal milestones and Ripple Prime leadership transition to the event timeline as non-price-causal context.
6. Resolve authoritative branch-protection/approval requirements, OAuth revocation evidence, 17 affected PR branch-tip copies and automatic Pages publication authorization.
7. Keep forecast issuance disabled until WORM anchoring, replayable point-in-time data, independent shadow outcomes and out-of-sample lift pass.

No merge, deployment, secret rotation/revocation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or PR closure occurred.


## Run22b — exact-head CI completion and additional options/macro/SBIC evidence

### Exact-head CI completion

The Run22 research/documentation commit `bd7daf29642bc79249ee32816d248cd357639b26` completed exact-head verification:

- Full repository suite: **3,423 passed, zero failures, eight subtests**, 79.78 seconds.
- Inclusive coverage: 59.98% for `barrot_agent`; total coverage report 60% across 23,403 statements. Coverage floor 53% passed.
- Core suite: 714 passed, zero failures, eight subtests.
- XRP public ingestion module coverage: 78% (2,156 statements).
- Wheel built and installed; packaged primary mission and canonical data assets loaded successfully.
- Six dependency manifests audited; zero known vulnerabilities reported.
- Fail-closed PR and push gates passed.
- Exact evidence: [CI 43010469954](https://github.com/Barrot-Agent/B-Agent/actions/runs/43010469954), full-suite job 130488490574; [dependency audit 43010469955](https://github.com/Barrot-Agent/B-Agent/actions/runs/43010469955), push audit 43010461200; [PR gate 43010470014](https://github.com/Barrot-Agent/B-Agent/actions/runs/43010470014), push gate 43010461199.
- Packaging warnings remain: deprecated license-table metadata and setuptools package-discovery warnings for `barrot_agent.data.missions` and `data.research`. The mission resource was nevertheless verified in the wheel. Coverage floor 53% remains below the previous 70% target.

### Options and tail-risk observation

Fuelmaps' Deribit daily capture at 2026-11-11 00:01 UTC, reference XRP $1.0564, reports 30-day/tenor IV in the high-50s to mid-60s: 65.5% for Nov 12 expiry, 66.0% Nov 13, 61.6% Nov 20, 59.4% Nov 27 and 59.0% Dec 25. Its historical daily 08:00 UTC settlement test reports 20 of 928 days beyond the options-implied 3-sigma band (2.2%) versus 0.27% under a normal curve. This is roughly 8.1 times the Gaussian reference, but it is a source-reported, model-specific historical statistic, not a forecast or calibrated future probability. Reproduce from raw options/settlement vintages before use.

The Nov 12 08:00 UTC 32-hour band is 1.0146–1.0982 at 1 sigma and 0.9373–1.1886 at 3 sigma; Nov 13 2d8h 1 sigma 1.0007–1.1120 and 3 sigma 0.9005–1.2357. The bands are options-implied, not forecasts. Fuelmaps notes XRP USDC-settled options have fewer strikes/expiries than BTC/ETH and one contract represents 1,000 XRP. OptimistFi's Nov 10 skew description and Fuelmaps' sign convention differ; preserve raw call/put IV and methodology rather than treating skew signs as directly comparable.

### Macro primary-source correction

BLS's November 10 primary October 2026 CPI release: headline +0.4% m/m, core +0.3%, food +0.5%, energy +0.7%, shelter +0.3%. Due the 2025 lapse in appropriations, October 2025 data were not collected and BLS cannot publish 12-month percentage changes for most October 2026 series. Consensus-surprise estimates come from market sources, not BLS. Source: https://www.bls.gov/news.release/archives/cpi_11102026.htm

### SBIC identity and ChatGPT activity — primary evidence

- Tokyo SBIC is Tokyo Small and Medium Business Investment & Consultation Co., Ltd., explicitly labelled SBIC East Japan; its official profile names Nagoya and Osaka as sister companies: https://www.sbic.co.jp/company/profile/ .
- Nagoya SBIC is SBIC Central Japan: https://www.sbic-cj.co.jp/company/about/ .
- Osaka SBIC is SBIC West Japan: https://www.sbic-wj.co.jp/profiles/profile/ .
- Tokyo SBIC's official June 12–13, 2025 training for investee companies covered generative AI/ML, ChatGPT use, Copilot, APIs, RAG and information-leak risk: https://www.sbic.co.jp/training/20250612co/ . This proves educational activity by SBIC East, not an OpenAI partnership.
- West Japan's October 23, 2024 ChatGPT seminar likewise remains educational activity, not partnership.
- Exact phrase “SBIC, ChatGPT SBIC” still has no primary-source match as a combined entity/partnership. Exact “actual capital” appears in secondary Evernorth coverage referring to proceeds contingent on warrant exercises; primary filings remain the authority for cash actually received/deployed. “ASK Coin” remains ambiguous; Permission Coin ASK is Base/Polygon LayerZero OFT, with no XRP/XRPL relationship verified. No Camilla/Kamilah Stevenson YouTube videos attributed without first-party channel verification.

The artifact now contains these options, macro and SBIC observations with provenance, limitations and non-model-eligibility flags. The addendum itself is a documentation-only successor commit and requires its own exact-head CI.


## Run22c — Evernorth actual-capital bridge and SBI/Ripple/Circle entity graph (primary filings)

The November 9, 2026 SEC Form 424B3 resolves the “actual capital” question. Do not collapse cash, token contributions, debt, contingent equity or resale registrations into one number.

- SBI announced a **$200M cash contribution** on October 21, 2025. The SEC filing identifies four SBI-controlled stockholders in the Advance Funding Subscription Agreements and records a 39.9% SBI Group voting-ownership limitation. The Advance Funding pool is **$214.05M aggregate cash** plus 600,000 XRP. The filing does not disclose each subscriber's exact cash allocation. Cross-document reconciliation: SBI's $200M is within the aggregate pool; do not add $200M to $214.05M.
- Advance Funding cash $214.05M was used to purchase **84,365,876.3625 XRP**, average **$2.53657/XRP**. Advance subscribers also contributed 600,000 XRP in kind. Delayed Funding added **$10.5M cash** and 200,000 XRP.
- In-kind XRP totals **388,910,554.061435 XRP**: 211,319,096.061435 from RippleWorks via Arrington XRP Capital Fund Series C; 126,791,458 under Ripple's Contribution Agreement; 50M from Larsen Lam Children's Remainder Trust; 600,000 Advance; 200,000 Delayed.
- Closing gross cash proceeds were **$272.6M before transaction expenses**: $224.6M private placements (Advance + Delayed) plus $48.0M SPAC trust after redemptions. This is not all XRP purchase cash.
- As of **October 9, 2026**, Evernorth reported approximately **473M XRP**. The token blocks reconcile to 84.365876M cash-purchased + 388.910554M in-kind = 473.276430M. Approximately **82.2% was contributed in kind** and **17.8% bought with cash**.
- At the Nov 11 10:21 UTC OKX quote of $1.0625, the cash-purchased tranche mechanically marks at about $89.64M versus $214.05M historical cost (-$124.41M / -58.1%). This is not a realized loss, accounting treatment or the value of all holdings.

### Separate financing and dilution

- Convertible notes: $30M principal, 4% PIK, due 2031, issued Oct 12. SEC 424B3 says approximately $30M net proceeds before transaction expenses; earlier secondary coverage described $29M after a $1M fee. Preserve discrepancy. Debt, not equity or proof of XRP purchase.
- Ripple Company Facility: $10M cap after Oct 7 amendment; $9.7M drawn as of Oct 7, 3.81%. Repayment due within five business days after Closing or earlier upon Ripple demand with five business days' notice; post-close repayment status not established.
- Evernorth Facility: separate $1M revolving facility, undrawn as of June 30, 2026.
- Cantor ELOC: up to 5,218,935 new shares, generally 97% of VWAP, subject to registration, 4.99% ownership and 20% volume caps. **Zero proceeds as of Nov 9.** $521,893.50 fee fully earned/non-refundable regardless of purchases; aggregate fee cap $1M. Contingent dilution capacity, not capital raised.
- Resale registration: up to 73,688,162 shares and 239,653 sponsor warrants. Evernorth receives no proceeds from selling-holder resales. Warrants could generate up to about $2.8M only if all are exercised for cash; no assurance.
- As of June 30, 2026, Evernorth reported no revenue, $265.6M loss, $0.1M unrestricted cash and $696.1M working-capital deficit. Pre-close historical figures, not current post-close liquidity.
- Disconfirming adoption evidence: the SEC prospectus says retail/commercial/payment use of XRP is limited and speculators make up a significant portion of users. It warns that adoption need not translate into XRP price appreciation and that permissioned DLTs, SWIFT, ACH and card networks compete with XRP.

### Ownership and SBI ecosystem

- SBI stockholders: SBI Venture Fund 2023A, SBI Venture Fund 2023B, SBI PE Holdings and SBI Holdings USA. Filing lists 9,431,914 Class A shares (36.1% of Class A) and 2,359,038 Class C shares (7.5% of Class C); separately, defined SBI Group voting cap was 39.9% as of Oct 9. Class C is ordinarily non-voting but convertible to Class A. Do not call 39.9% total economic ownership.
- Ripple held 1,678,382 Class A shares (6.4%); Chris Larsen 2,340,249 Class A shares (9.0%), subject to beneficial-ownership qualifications. Contributor Group voting power capped at 9.9%. Arrington Sponsor held 4,704,137 Class A (18.0%) and 29,033,708 Class C (92.5%); 4,215,479 Class A side-pocket shares tied to RippleWorks' XRP contribution carry RippleWorks voting instructions and specified consent rights.
- SBI's official June 2025 notice and May 2026 presentation report approximately **9% of Ripple equity** as largest external shareholder. SBI Ripple Asia is 60% SBI / 40% Ripple; SBI Remit uses XRP as bridge currency in Asian remittance corridors. This is equity in Ripple, not direct SBI XRP ownership.
- SBI Holdings and SBI Shinsei Bank invested **$50M total** in Circle at its June 5, 2025 NYSE listing ($25M each). SBI/Circle alliance dates to Nov 2023; SBI VC Trade offered USDC in Japan in Mar 2025; Circle SBI Japan KK was planned. This is USDC, not XRP.
- SBI separately announced **$200M cash** for Evernorth. SBI announced a $50M Startale investment in Mar 2026. JPYSC technology by Startale, issuer SBI Shinsei Trust Bank, distribution SBI VC Trade. SBI's strategy lists USDC, RLUSD and JPYSC as separate rails.
- SBI's May 2026 presentation reports Ripple balances of 5.10B XRP outside escrow and 33.20B in escrow as of Apr 27, 2026. These are Ripple balances presented by SBI, not SBI holdings and not an independent on-chain audit. SBI's presentation lists Ripple acquisitions: Metaco ($250M), Standard Custody (undisclosed), Rail ($200M), Hidden Road ($1.25B), GTreasury ($1B).

Primary sources: [Evernorth SEC 424B3](https://www.sec.gov/Archives/edgar/data/2092592/000162828026072223/evernorth-424b3.htm), [SBI $200M Evernorth announcement](https://www.sbigroup.co.jp/english/news/pdf/2025/1021_a_en.pdf), [SBI $50M Circle investment / Ripple stake](https://www.sbigroup.co.jp/english/news/pdf/2025/0609_a_en.pdf), [SBI FY2025 presentation](https://www.sbigroup.co.jp/english/investors/disclosure/presentation/pdf/260501presentations.pdf), [SBI/Startale investment](https://www.sbigroup.co.jp/news/2026/0326_16202.html), [SBI/RLUSD agreement](https://www.sbigroup.co.jp/news/2025/0822_15680.html), [SBI XRP remittance corridors](https://www.sbigroup.co.jp/news/2023/0906_14052.html).

These capital/corporate observations remain research-only until raw filings and presentations are hashed, timestamped and admitted into Barrot's point-in-time store. Forecast remains `NOT_ISSUED`.


## Run23 — 2026-11-11T11:35:50Z — repository, exchange reserves, Evernorth custody, stablecoin and model-risk reconciliation

### Repository and exact-head verification

- Main SHA: `84f28ee7755607236231545a14f3d093c1baaa85`. Integration parent inspected: `7a55848cab17f7cb2fd6549b0c463cc45efd47ae`.
- PR #1661: open, draft, mergeable-clean, 2,014 commits ahead/zero behind, 997 changed files (44 workflows, 953 other paths), 236,814 additions and 4,363 deletions. Complete trees: main 1,388 entries/1,288 files/86 workflows; integration 2,262 entries/2,153 files/87 workflows.
- Open PR inventory: 374 total, 360 draft and 14 non-draft. #1661 remains the sole consolidated integration workstream. No new PR was created.
- Exact parent-head CI on `7a55848` passed **3,423 tests, zero failures, eight subtests, 59.98% coverage, 93.67 seconds**. Wheel and installed Barrot V3/XRP mission verification passed. Six dependency manifests audited; zero known vulnerabilities reported. Dependency audit #43012397124 and fail-closed PR gate #43012397190 passed; push gate #43012390401 passed. [Full CI](https://github.com/Barrot-Agent/B-Agent/actions/runs/43012397193) · [full-suite job](https://github.com/Barrot-Agent/B-Agent/actions/runs/43012397193/job/130495019833).
- Main exact-head CI on `84f28ee` passed 718 tests/eight subtests. Main scheduled Cross Analysis #43007129290 succeeded. Main Pages build #42944862534 succeeded as an automatic push-triggered publication side effect.
- Local Git transport still fails DNS resolution for `github.com`; complete remote inspection succeeded through the GitHub API.

### Integration review corrections

- The current PR file list includes `hf_space/app.py`. The prior map claim that it was unchanged was incorrect. The PR changes it from v7.0 to v7.1 for safety: external inference disabled by default; explicit operator opt-in plus session consent; one configured provider and no silent fallback; public forecast endpoint returns `NOT_ISSUED`; legacy directional ledger rows are quarantined. Orbitron and Share Tech Mono CSS declarations are unchanged. The archival `.barrot/orbit/command_schema.json` and `ORBIT_REMOVED.md` remain in both main and integration, but no Orbit path changed in #1661 and no active Orbit runtime was reintroduced.
- Current blob-hash overlap: #1660 972/972 paths represented (959 identical, 13 different); #1643 670/670 (661 identical, nine different); #1642 seven/seven (zero identical, seven different); #1640 280/280 (253 identical, 27 different). These are overlap/supersession candidates, not confirmed duplicates. #1660 remains open/draft and three commits behind main.
- The current-map test contract was stale: it asserted `hf_space/app.py` was unchanged and recorded older CI evidence. Run23 corrects those assertions, records the font-preservation invariant and exact parent-head CI, and adds tests for connector over-permission, research-only provenance and non-WORM retention. One new research artifact path is added; post-commit PR count must be verified.

### Security and permissions

- GitHub repository metadata reports connector permissions `admin=true`, `maintain=true`, `push=true`, `pull=true`, `triage=true`. This exceeds least privilege. No main write, secret-value read or branch-protection bypass was performed.
- Main branch summary reports protected=true but `required_status_checks.contexts=[]` and `enforcement_level=non_admins`. Detailed branch-protection access returns HTTP 403. The visible fallback ruleset “Fall Back” is disabled. With connector metadata reporting admin=true, non-admin-only enforcement is not a sufficient merge gate.
- `.config/gh/hosts.yml` remains absent from main and active integration but present in all 17 rechecked current open-PR tips: #1653, #1650–#1644, #1643, #1642, #1640, #1320, #1318, #1317, #1269, #1255 and #1254. No file contents were read. Repository sync reports OAuth revoked, but provider-side revocation is unverified. No secret was rotated/revoked and no history was rewritten.
- Automatic GitHub Pages publication remains an unresolved side effect; explicit publication authorization is absent.

### XRP market and capital findings

**Spot and liquidity**
- OKX XRP-USDT: 1.0583, event time 11:33:13.571 UTC; bid 1.0581/ask 1.0582. Kraken XRP/USD: $1.06031 without provider event timestamp. Kraken USDT/USD: 0.99902. Normalized OKX reference is $1.0572629, about 0.2874% below Kraken's last. Asynchronous; not executable arbitrage.
- Fuelmaps' 09:00 UTC six-venue resting-book snapshot: $11.9M bids/$9.2M asks within 1%, $23.1M/$12.2M within 5%. Binance and Bitget excluded. More than two hours old at retrieval; resting orders can be cancelled.

**Exchange balances versus external transfers**
- XRP Insights reports 22.33B XRP in 701 attributed wallets across 24 exchanges at 08:00 UTC Nov 11; same-wallet change +1.3M XRP over seven days and -155.7M over 30 days. It includes cold storage and wrapped-token reserves: 48% labelled cold, 12% hot, 40% unclassified. Not tradable float, exchange liabilities or beneficial ownership.
- Regional attributed balances: South Korea 8.59B, United States 8.46B, Japan 1.38B. SBI VC Trade is listed at 56.9M XRP in two wallets, over 99% labelled cold; exchange custody, not SBI Holdings corporate XRP.
- Coinbase's 5.80B tracker balance includes a 149.6M cbXRP reserve annotation; Binance's 2.69B includes a 327.4M Binance-Peg reserve annotation. Wrapped backing may overlap DeFi categories; do not double count.
- TrackWhale's prior seven-day tracked external-transfer snapshot showed 501.72M inflows and 602.93M outflows, net -101.21M XRP. Different, older large-transfer universe; it disagrees in sign with same-wallet exchange-balance change. Preserve both; do not average or infer customer withdrawals from wallet-label changes.

**Evernorth actual capital and custody**
- SEC Form 424B3 dated Nov 9 reports approximately 473.276430M XRP at closing/as of Oct 9: 84.365876M cash-purchased using $214.05M advance-funding cash at about $2.53657/XRP, plus 388.910554M in-kind. SBI's announced $200M is included within the $214.05M pool; exact subscriber-level allocation is not disclosed. Gross closing cash was $272.6M before expenses, including $10.5M delayed cash and $48M SPAC trust; this is not all XRP purchase cash.
- XRP Insights' Nov 11 10:57 UTC ledger read attributes 103.129905M XRP to 13 Evernorth-linked wallets. It reports 370.346663M moved outside the attributed set, latest Oct 22. About 78.25% of the reported closing amount is outside that set. Destination ownership/custody is unknown; not proof of sale, disposal or loss of beneficial ownership.
- At normalized OKX reference, the cash-purchased tranche mechanically marks near $89.20M versus $214.05M historical cost (-58.33%). This is an unrealized mark on the cash-purchased tranche only, not realized loss or valuation of all Evernorth holdings.

**Wrapped XRP and stablecoins**
- Coinbase cbXRP page displayed 151,866,756.78 XRP reserve against 151,864,510.253 cbXRP supply (2,246.527 XRP excess), refreshed Nov 11 at 10:40 AM with timezone unspecified. Issuer-published proof-of-reserves, not independent custody audit. XRP Insights' 149.6M reserve annotation differs by about 2.26M; reconcile wallet coverage/vintage before adding.
- Ripple transparency reports $2.6329B RLUSD circulating and $2.748B reserves as of Nov 5 (104.37% coverage), with monthly independent CPA reserve reports. RLUSD issuance/custody is not automatically XRP demand or XRP collateral. Circle transparency page is dated Nov 9; static extraction did not expose numerical balances, so none are inferred.

**Derivatives, options and protocol risk**
- TradRadar 11:10 UTC snapshot: $1.57B OI, down 4.2%; funding +0.0092% per eight hours; $15.17M liquidations, $14.05M long and $1.13M short; 79.6% long accounts. Aggregator coverage is not interchangeable with other vendors.
- Fuelmaps' Nov 11 00:01 UTC options snapshot reports 20 of 928 daily 08:00 UTC outcomes beyond its options-implied 3-sigma band (2.16%) versus 0.27% Gaussian reference, about eight times. Source-reported, not independently reproduced. It motivates a Student-t/empirical-quantile baseline experiment; not a future probability or forecast.
- XRPL Foundation's 2027 roadmap lists ML-DSA-44 quantum signatures as proposed, not approved; validator vote required. Study target H1 2027 and development/review/audit late 2027 or 2028. Long-horizon security milestone, not near-term demand.
- Ripple Prime leadership transition (Marc Asch to Noel Kimmel at year-end 2026) is secondary-source reporting attributed to a company spokesperson. RLUSD collateral use for some prime products is distinct from XRP collateral eligibility.

### Prediction-engine audit

- 46 source definitions: 42 hourly, two weekly CFTC and two optional non-commercial XRPL nodes; 44 scheduled. `xrp_exchange_balances_json` is scheduled but digest-only because raw redistribution permission is not explicit.
- Raw receipts use SHA-256 content addressing and a per-run hash chain; not independent WORM. Workflow retains raw artifacts 90 days, per-run feature-store checkpoints seven days and daily backups 90 days. SQLite row guards are not adversarially tamper-proof.
- Scheduled walk-forward evaluation sets embargo equal to forecast horizon; overlap-adjusted effective sample size uses greedy non-overlapping target intervals. Residual serial dependence/shared-source correlation remain uncorrected.
- Four baselines: naive class prior, momentum sign, mean-reversion sign and Gaussian volatility normal. The options tail statistic requires reproducing raw vintages and testing heavy-tailed/empirical alternatives. A scenario/counter-hypothesis generator is not implemented; the ledger alternatives field is only a contract.
- Readiness requires at least 100 OOS and 100 shadow raw samples, at least ten non-overlapping target windows in each, two source groups, stable drift, weighted calibration error <=0.05, lower Brier and log loss than all four baselines, and trusted Ed25519 evaluator attestation. No successful main-branch collector run, WORM archive, production evaluator key or OOS lift is verified.

### Identity, platforms and forecast

- SBIC East/Tokyo, Central/Nagoya and West/Osaka remain resolved as distinct regional SME investment companies, not SBI Holdings. Exact “ASK Coin”, “actual capital” and “SBIC, ChatGPT SBIC” combined phrase remain unresolved at primary-source level. Kamilah/Camilla YouTube attribution remains gated on first-party identity verification.
- ChatGPT GitHub connector is verified in this session but repository metadata reports admin=true. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks have no new authenticated data flow. Copilot has no formal approval on #1661. LunaRoute remains repository-declared but endpoint authentication/data flow unverified. No external-model data transfer occurred.
- Forecast remains `NOT_ISSUED`. All Run23 web observations lack Barrot raw receipts and are excluded from model features. No directional forecast, paper trade or real-money action occurred.

### Backlog and decision

- #1661: blocked, sole consolidated integration draft. Parent head passed exact CI; Run23 documentation/test-contract commit requires its own exact-head CI. Draft, zero approvals/reviews, admin-exempt branch protection, empty required-check contexts, disabled fallback ruleset, overprivileged connector, 953-path semantic review incomplete, Pages authorization absent.
- #1660: superseded-source candidate; retain until successor merge and main verification. #1640/#1642/#1643: overlap candidates with differing blobs; reconcile before closure. #1644–#1650 and #1254/#1255: dependency candidates; preserve until compatibility/security reconciliation.
- Preserve unique/unreviewed #1608, #1610, #1611, #1612, #1614, #1317, #1318, #1320, #1269, #1653, #1655 and #1659. No source PR was closed; no confirmed duplicate closure occurred.
- Next: complete exact-head CI on the Run23 update; reduce GitHub connector permissions to least privilege and resolve branch-protection admin exemption; finish semantic review; verify OAuth revocation and additively remediate the 17 branch tips; obtain Pages authorization; build WORM/timestamp anchoring, heavy-tailed baselines and scenario generation. Keep forecasts disabled.

No merge, deployment, secret rotation/revocation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or PR closure occurred.

## Run24 reconciliation — 2026-11-11T12:05Z–12:29Z

The canonical map records Runs24 through 24e; this handoff file had not yet been synchronized with those updates. Key additions:

- Evernorth reported 473.276430M XRP at closing/as of October 9: 84.365876M cash-purchased using $214.05M advance cash and 388.910554M in kind. SBI's announced $200M is included in the $214.05M pool, not additive; subscriber-level allocation is undisclosed.
- XRP Insights' November 11 ledger read attributed 103.129905M XRP to 13 Evernorth-linked wallets. Another 370.346663M was outside that attributed wallet set, with destinations unresolved. This is not proof of sale, loss or disposal.
- SBI's $50M Circle investment is split $25M SBI Holdings and $25M SBI Shinsei Bank. This is equity into Circle, not XRP purchase capital.
- Run24e exact-head CI on a41fa failed two current-map assertions after 3,425 passes. These were evidence-map contract assertions, not runtime XRP-engine failures; the fields were corrected before the Run25 code-head verification.

## Run25 — 2026-11-11T13:02:17Z

### Repository and CI

- Main SHA: 84f28ee7755607236231545a14f3d093c1baaa85.
- Existing integration branch: integration/xrp-v3-unified-main-20261111; verified code parent 7155eede2a852355e5626c4f00c9c79a5ed1d1c7, 2,020 commits ahead and zero behind.
- PR #1661: open, draft, mergeable; 1,000 changed files (44 workflows, 956 other paths), 238,998 additions and 4,363 deletions. Complete trees: main 1,388 entries/1,288 files; integration 2,265 entries/2,153 files. Paginated PR file page 11 returned zero, confirming the 1,000-file listing is complete.
- Open PR inventory: 374 total, 360 drafts and 14 non-drafts. PR #1661 remains the sole consolidated integration workstream. No branch or PR was created.
- Exact code parent 7155eede: 3,427 passed, zero failures, eight subtests, 59.98% coverage, 96.83 seconds. Full-suite job 130523332780; core job 130523332437; wheel and installed Barrot V3/XRP mission verified.
- Six-manifest dependency audit passed with zero known vulnerabilities: run 43020832903/job 130523332180. Fail-closed PR gate passed: run 43020833177; automatic merge remains disabled.
- The atomic Run25 handoff/map/research commit is documentation/evidence only and requires its own exact-head CI. Do not substitute parent-head results for that run.
- Main scheduled Cross Analysis succeeded (43023990234). Main read-only Pillars Consistency Check failed (43025487840): GITHUB_APP_ID, PRIVATE_KEY and INSTALLATION_ID missing; Databricks HTTP 403; Hugging Face BUILD_ERROR. This is a platform-health failure, not the main Python test suite.

### Current XRP market snapshot

- OKX XRP-USDT at 12:34:10.894 UTC: 1.0527; rolling 24h open 1.0796, high 1.0854, low 1.0311, volume 68.19M XRP. Kraken last $1.05602 with no provider event timestamp; USDT/USD $0.99903. Normalized OKX reference is about $1.05168, approximately 0.41% below Kraken. Asynchronous and freshness-sensitive; not executable arbitrage.
- Fuelmaps 12:00 UTC six-venue spot book: $10.3M bids/$9.4M asks within 1%; $19.3M/$12.6M within 5%. Binance and Bitget excluded; resting orders can be cancelled.
- TradRadar 12:10 UTC: OI $1.57B (-4.41%), funding +0.0087%/8h, at least $15.0M liquidations ($13.87M long), 79.7% long accounts. Liqwall 12:52 UTC: OI $1.15B (-2.1%), funding +0.0086%, $16.9M liquidations ($15.8M long), 75.2% Binance accounts long. Different universes; do not average.
- OptimistFi/Deribit 12:00 UTC: 30-day ATM IV 58.3%, 25-delta skew -0.6 points (puts richer), put/call 0.55, Dec25 OI $47.2M. Near expiries remain more put-rich; same-provider 30-day skew changed sign versus the earlier +0.3 snapshot.
- Alpha Finance through Nov10: daily -$7.6M, Nov9 -$10.4M, 30-session +$1.3M, cumulative net inflow $1.71B. XRP Insights' wider tracker reports -9.568M XRP across Nov9–10 and 1.1856B XRP held. Different universes/windows; do not average.
- XRPL.to Token Market reports 7.26M XRP/197,168 trades, 25.55M XRP AMM liquidity and 6.41M XRP order-book activity. Its separate DEX Volume & Stats page reports 7.74M XRP/189,675 trades, with 6.91M order-book and 0.836M AMM volume. Preserve the discrepancy. Both are issued-token trading on XRPL, not native XRP/USD turnover or institutional XRP inflow.

### Evernorth capital and liquidity — material counter-evidence

The latest SEC Form 424B3 (accession 000162828026072223) materially qualifies the institutional-accumulation thesis:

- Evernorth had not generated revenue as described in the filing. Historical June 30, 2026 figures include $0.1M unrestricted cash, $696.1M net working-capital deficit, $340.9M accumulated deficit and $265.6M reported operating loss.
- Six-month net loss was $188.1M, but operating cash used was about $1.33M; the filing identifies $264.1M digital-asset impairment and a $77.5M non-cash gain on refundable investor advances. Do not equate accounting loss with cash burn.
- Ripple's company facility was increased to $10M; $9.7M had been borrowed as of October 7. This is related-party debt, not equity.
- A $30M 4% PIK convertible senior note was funded October 12. The holder chooses cash or share settlement on conversion. The filing discloses conditional cash-settlement exposure up to $120M (4x principal) and an 8% yield-to-put on specified default/fundamental-transaction events. These are conditional risks, not currently due cash payments.
- The company states note proceeds are for general corporate purposes, including possible XRP acquisition; this filing does not prove the $30M was used to buy XRP.
- Cantor ELOC permits up to 5,218,935 shares at 97% of VWAP subject to registration, price, volume and ownership conditions. No ELOC proceeds had been received as of the prospectus. It is contingent capacity, not current cash.
- The filing warns XRP is less liquid than cash and the company may need to sell XRP to meet cash obligations in adverse conditions.

This creates a genuine counter-hypothesis: the treasury represents institutional XRP exposure, but its funding structure and cash obligations can create future selling pressure. Keep the $200M SBI announcement, $214.05M advance cash, in-kind XRP, Ripple debt, $30M notes and undrawn ELOC as separate ledger categories.

### Stablecoins, custody and network relationships

- Standard Chartered's RLUSD custody on XRPL is live through its DIFC branch; the Ripple/LMAX collateral integration remains planned, not proven live.
- SBI VC Trade handles RLUSD in Japan; SBI Shinsei Trust Bank issues JPYSC and SBI VC Trade distributes it. JPYSC reserve investment into Japanese government bonds is separate reserve management, not XRP collateral.
- SBI Ripple Asia's tokenized-deposit concept proof assumes XRPL/MoneyTap infrastructure; it is not verified production XRP settlement volume.
- Stablecoin distribution, custody, tokenized deposits and treasury balances do not automatically establish XRP bridge demand, XRP collateral usage or new spot purchases.

### Nine-platform and security state

- ChatGPT GitHub API access is verified, but repository metadata reports admin=true, maintain=true, push=true, pull=true and triage=true. This exceeds least privilege.
- Claude, Grok, Gemini and Codex remain unauthenticated/unverified; Copilot has no formal approval; Kaggle is untested; Databricks returned HTTP 403; Hugging Face reports BUILD_ERROR. LunaRoute is repository-declared but endpoint authentication/data flow is unverified. No external-model data transfer occurred.
- Main branch-protection details return HTTP 403. The visible fallback ruleset is disabled. Required approval/check policy is not verified. With admin=true, non-admin-only enforcement is not an adequate safety boundary.
- .config/gh/hosts.yml remains absent from main and #1661 but present in all 17 previously rechecked affected open-PR tips. Contents were not read. Repository notes report OAuth revoked, but provider-side revocation is unverified.
- Automatic GitHub Pages publication remains a merge side effect without explicit authorization.

### Prediction-engine status

- Implemented: 46 source definitions, 44 scheduled public sources, read-only collector, SHA-256 receipts/hash chain, point-in-time SQLite store, four deterministic baselines, chronological purge/embargo walk-forward evaluation, calibration/PSI drift diagnostics and fail-closed Ed25519 evaluator-attestation contract.
- Not production verified: independent WORM/timestamp anchor, replayable historical feature store, synchronized multi-venue spot/L2/derivatives/flow/collateral history, vintage-aware macro timeline, scenario/counter-hypothesis generator, production evaluator key, sufficient shadow outcomes and out-of-sample lift over all four baselines.
- Run25 web observations were not captured by Barrot's raw collector and are excluded from model features.
- Forecast remains NOT_ISSUED. No directional forecast, paper trade or real-money action occurred.

### Backlog and decision

- #1661: blocked, sole consolidated integration PR; draft, zero formal approvals/reviews, incomplete semantic review of 956 pre-existing non-workflow paths, branch-protection requirements not visible, overprivileged connector, credential-path remediation and Pages authorization unresolved.
- #1660: superseded-source candidate; retain until successor merge and main verification.
- Preserve unique/unreviewed work including #1653, #1614, #1611, #1610, #1612, #1269 and #1608; reconcile overlap candidates #1640, #1642, #1643, #1644–#1650, #1317, #1318, #1320, #1254 and #1255 only after verified successor merge. No source PR was closed.
- Next: verify exact-head CI on the atomic Run25 commit; reduce connector permissions; resolve GitHub App, Databricks and Hugging Face health; obtain branch-protection/approval visibility; verify OAuth revocation and additively remediate the 17 affected tips; complete semantic review; resolve Pages authorization; then consider merge only if every gate passes.

No merge, deployment, secret rotation/revocation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or PR closure occurred.

## Run25b — SEC entity-level scope correction — 2026-11-11T13:15:41Z

A closer read of SEC Form 424B3 separates Pubco (Evernorth Holdings Inc., the parent Company) from the Evernorth operating subsidiary. The previous Run25 summary quoted the subsidiary figures correctly but did not clearly attribute the parent-level financing instruments.

- Pubco parent, June 30, 2026: $0.8M unrestricted cash, $3.7M net working-capital deficit, $3.1M accumulated deficit, $2.2M operating loss and $2.138M operating cash used.
- Evernorth operating subsidiary, June 30, 2026: no revenue generated; $0.1M unrestricted cash, $696.1M net working-capital deficit, $340.9M accumulated deficit, $265.6M operating loss and $188.1M six-month net loss. Its six-month operating cash use was $1.330M, not $188.1M. The latter includes $264.1M non-cash digital-asset impairment partly offset by a $77.5M non-cash fair-value gain.
- Pubco Company Facility: $10M limit, $9.7M drawn as of October 7 at 3.81%. The filing says amounts were subject to repayment within five business days after the Closing Date or earlier on five business days' notice from Ripple; the later repayment/current balance is not established by this excerpt.
- Separate Evernorth Facility: $1M limit, undrawn as of June 30.
- Pubco convertible note: $30M 4% PIK note funded October 12. The holder chooses cash or share settlement; conversion value is capped at 4x principal, and specified default/fundamental-transaction events carry an 8% yield-to-put. These are conditional terms, not currently due cash payments.
- Pubco Cantor ELOC: up to 5,218,935 shares at 97% VWAP, subject to registration, price, volume and ownership conditions; zero proceeds as of the prospectus.
- The filing says the $30M note proceeds may fund general corporate purposes including XRP acquisition; it does not prove that those proceeds were used to buy XRP.

This correction avoids mixing subsidiary financials with parent-level obligations. Primary source: https://www.sec.gov/Archives/edgar/data/2092592/000162828026072223/evernorth-424b3.htm


## Run 27 — current XRP liquidity, exchange balances, Evernorth resale, Ripple Prime, SBI collateral and XRPL governance

Captured: 2026-11-11T14:45:15.265Z. All public-web observations in this run are research-only and excluded from model features; no Barrot raw-source receipts were created by this research pass.

### Repository and exact-head CI

- Main remains `84f28ee7755607236231545a14f3d093c1baaa85`.
- Existing PR #1661 remains the sole consolidated integration PR; current inspected head `ad9a408bdfdd19c5b0b71fed4a2e5a36db6edcf5`, 2,028 ahead/0 behind, 1,009 changed files (44 workflows, 965 non-workflow paths), draft and zero formal approvals.
- Open PR inventory: 374 (360 drafts, 14 non-drafts). No new branch or PR.
- Run26e exact-head CI 43040465375 on `ad9a408bdfdd19c5b0b71fed4a2e5a36db6edcf5`: 3,443 passed, four failed, eight subtests, 57.49s, 59.98% coverage. Core 714 passed. Dependency audit 43040465368 passed (six manifests, zero known vulnerabilities). Fail-closed gate 43040465437 passed.
- The SBI HTML fixture repair removed all seven prior ingestion receipt-count failures. The four remaining failures were two current-map assertions (stale head binding and 46/42/44 counts), one adapter/parser version assertion (code v3.24/v3.23, test still v3.22/v3.21), and one Run124 historical test asserting old current-contract counts. These are test-contract mismatches, not evidence of a runtime prediction-engine failure. Corrective changes are being applied on the same branch.

### Spot, liquidity, derivatives, exchange balances and ETF flows

- xrpldashboard displays XRP at $1.0562 as of 14:34 UTC; this is a dashboard reference price, not a venue-executable quote.
- Fuelmaps' 14:00 UTC six-venue spot book: mid $1.0611; within 0.5% $8.1M bids/$6.6M asks; 1% $13.7M/$11.8M; 2% $19.7M/$12.7M; 5% $25.0M/$14.7M; 10% $33.8M/$16.1M. Resting orders can be cancelled; Binance and Bitget are excluded.
- Liqwall at 11:42 UTC: OI $1.16B, -2.0% 24h, average funding +0.0098%/8h, $16.8M liquidations ($15.7M longs), 75.1% Binance accounts long. TradRadar at 11:30 UTC reports OI $1.57B, -4.05%, +0.0092% funding, at least $15.16M liquidations ($14.04M longs), 79.6% long accounts. Different venue/contract coverage; do not average.
- OptimistFi/Deribit at 05:00 UTC: 30-day ATM IV 59.0%, 25-delta skew +0.3 points (calls richer), but near-expiry skew is put-rich (Nov 11 -11.0, Nov 12 -7.3, Nov 13 -4.5). Term structure is mixed.
- XRP Insights at 08:00 UTC: 22.33B XRP across 701 attributed wallets and 24 exchanges, 32.4% of circulating supply. Same-wallet change +1.3M over seven days and -155.7M over 30 days. Naive total change +356.3M includes two newly tracked wallets holding 512.1M. Upbit 6.47B, Coinbase 5.80B, Binance 2.69B. Includes cold storage, is not tradable float, excludes at least 323M in known untracked exchange wallets, and overlaps 149.6M cbXRP with DeFi totals.
- XRP Insights ETF data through Nov 10: six spot funds plus BITW report -27K XRP, approximately -$28.6K, but Nov10 is provisional; Alpha Finance's five-fund subset reports -$7.6M; CryptoETF.today reports -$6.9M with four of five funds filed. Different fund universes and vintages; do not average or zero-fill missing issuers.
- XRP escrow tracker: 31.10B in on-ledger escrow; up to 1B scheduled for Dec 1. Gross unlock is not net circulating supply or guaranteed sale; historical re-escrow behavior matters.

### Evernorth actual capital and resale registration

- SEC Form 424B3 (Nov 9) registers up to 73,688,162 XRPN Class A shares for resale: 19,102,635 issued; 31,392,746 issuable on Class C conversion; 22,953,128 issuable on Company Unit redemption/exchange; 239,653 sponsor-warrant exercise shares. Class A shares outstanding Oct 22: 26,094,680.
- The registered amount is not immediate float. Conversion/redemption is subject to 9.9%, 19.9% and 39.9% ownership restrictions and may never occur; units may be cash-settled. Evernorth receives no proceeds from holder resales. SBI-related holders have 11,790,952 shares registered across four entities; Ripple Labs 18,139,927; Arrington 33,822,498. Registration does not prove any holder will sell and does not evidence XRP sales.
- Prior cash/in-kind reconciliation remains: approximately 473.276M XRP at closing, 84.366M XRP purchased with $214.05M advance-funding cash, 388.911M XRP contributed in kind. SBI's $200M cash commitment is included in the $214.05M pool, not additive. Debt, drawn facilities, ELOC capacity and resale registration remain separate.

### SBI collateral and stablecoin rails

- SBI VC Trade's lending page lists 29 assets, including XRP, USDC and JPYSC, but not RLUSD. A dated USDC offer showed 10% annualized for 84 days, 100–5,000 USDC, dated Apr 30, 2026; it is historical, not a current guaranteed rate. Preserve the earlier 5%/12-week offer as a separate vintage.
- SBI VC Trade service overview: retail leverage up to 2x, maintenance margin threshold 80%, generic crypto collateral valuation factor 50%, electronic-payment-instrument factor 100%. XRP is a listed leverage market; actual customer XRP collateral and lending balances/utilization are undisclosed. Lending eligibility is not the same as collateral eligibility.
- Coinbase cbXRP proof-of-reserves display: 151,709,177.16 XRP reserve versus 151,706,930.63 cbXRP supply; excess 2,246.53 XRP. Refresh label Nov 11, 2:30 PM with timezone unspecified. Issuer display, not independent audit.

### Ripple, Coinbase, Circle, SBI and XRPL protocol

- Ripple Prime's Oct 15 RWA-perpetual launch names Virtu as an early institutional client and more than 100 reference markets; contracts reference Trade.xyz perpetuals on Hyperliquid, with Ripple Prime as principal. RLUSD can be collateral subject to jurisdiction. No XRP settlement/collateral leg, notional or RLUSD collateral balance is disclosed.
- Ripple's Oct 28 company report says it is on track for $900M annualized product revenue, cites $16T transactions enabled in 2025, 1,700+ institutions/corporates, 85+ licenses and RLUSD market cap around $2.6B; it reports final OCC National Trust Bank charter approval. These are company-reported metrics, not independent XRP flow measurements.
- Coinbase/Ripple RLUSD is live on Coinbase Prime, Exchange and Retail, with XRPL/Base/Ethereum deposit/withdrawal support. Coinbase Global Exchange collateral support was explicitly future scope, not verified live.
- BNY is Ripple's primary RLUSD reserve custodian and now supports XRP and RLUSD custody. Direct RLUSD mint/redeem at BNY and tokenized trade finance with C2FO are future/exploratory and subject to approvals/client requirements.
- Live XRPL amendment tracker at 14:22 UTC: SingleAssetVault 23/35, LendingProtocol 22/35, LendingProtocolV1_1 22/35; 29/35 required, with zero amendments in the 14-day countdown. Native XRPL lending is not active. XLS-65 vaults hold one asset; XLS-66 fixed-term credit leaves underwriting off-ledger and does not mandate XRP collateral.
- XRPLF Discussion #617's proposed native XRP first-loss sleeve is a pre-standard community idea (one participant, zero comments), not an official amendment or current XRP demand.

### Identity and exact phrases

- SBIC East/Tokyo, Central/Nagoya and West/Osaka remain separate Japanese SME investment-consultation companies, not SBI Holdings. Tokyo SBIC ChatGPT/Copilot training was education for investee companies, not an OpenAI partnership.
- Permission's official ASK docs list Base and Polygon only; no XRPL support. Askcoin and Permission ASK remain distinct; no XRP integration verified.
- “Actual capital” is not a standardized XRP term; keep cash, in-kind XRP, debt, drawn facilities, posted collateral, ELOC capacity, resale registration and actual sales separate.
- The first-party Kamilah site does not link a YouTube channel. Candidate videos remain unverified as the identified person's channel; no personal-video inventory is attributed. Camilla remains separate/unresolved.

### Prediction and safety

The integration registry has 47 source definitions: 43 hourly, two weekly CFTC and two noncommercial XRPL nodes excluded by default; 45 sources are scheduled. The SBI VC Trade page is digest-only and feature-ineligible; no main-branch receipt is verified. The feature store is not WORM, and replayable historical reconstruction, synchronized market/collateral history, scenario generation, independent shadow outcomes, production evaluator key and demonstrated out-of-sample lift remain unverified.

**Forecast: NOT_ISSUED.** No trade, paper trade, real-money action, merge, deployment, secret rotation, external-model transfer or main write occurred. No source PR was closed.

### Next action

Verify the Run27 corrective commit's exact-head full suite, dependency audit and fail-closed gate. Then update PR #1661's description with exact evidence, continue semantic review of the 966 non-workflow paths, and resolve connector least-privilege, branch-protection, credential-remediation and Pages-publication blockers before any merge.

## Run30 — exact-head CI, XRP market repricing, institutional capital and SEC entity correction

Captured: 2026-11-11T16:30:06Z

### Mission and repository state

XRP intelligence and prediction-engine mastery remain priority one. Barrot V3 remains the execution, orchestration, safety and verification foundation.

- Main SHA: 84f28ee7755607236231545a14f3d093c1baaa85.
- Existing integration PR: #1661, branch integration/xrp-v3-unified-main-20261111.
- Tested code head at capture: 4e7a7e5fabd1d9cf6f974e4d84545cc01d013061, 2,035 commits ahead and zero behind main.
- PR #1661: 1,013 changed files (44 workflow files, 969 other paths), 249,153 additions and 4,363 deletions.
- Complete trees: main 1,388 entries/1,288 blobs; integration 2,278 entries/2,168 blobs; 86 and 87 workflows respectively.
- Open PR inventory: 374 (360 drafts, 14 non-drafts).
- GitHub API inspection succeeded. Local Git clone still fails DNS resolution for github.com.

### Exact-head verification

The exact code head 4e7a7e5fabd1d9cf6f974e4d84545cc01d013061 passed:

- Full repository suite: **3,449 passed, zero failed, eight subtests**.
- Inclusive coverage: 59.99% against a 53% configured floor.
- Core suite: 714 passed, zero failed, eight subtests.
- Wheel build and installed Barrot V3/XRP mission verification passed.
- Six dependency manifests audited; zero known vulnerabilities reported.
- Fail-closed PR and push gates passed.

Evidence: [Full CI 43052665205](https://github.com/Barrot-Agent/B-Agent/actions/runs/43052665205), [full-suite job 130633703409](https://github.com/Barrot-Agent/B-Agent/actions/runs/43052665205/job/130633703409), [dependency audit 43052664866](https://github.com/Barrot-Agent/B-Agent/actions/runs/43052664866), [fail-closed PR gate 43052664836](https://github.com/Barrot-Agent/B-Agent/actions/runs/43052664836), [fail-closed push gate 43052654340](https://github.com/Barrot-Agent/B-Agent/actions/runs/43052654340).

The prior 415e611 attempt had 3,447 passed and two stale evidence assertions failed. Those assertions were corrected before 4e7a7. The Run30 documentation/research commit will trigger its own exact-head CI; that result is pending at commit time. Coverage remains below the earlier 70% target and is quality debt.

### Workflow and security audit

- All 44 changed workflow diffs were rechecked: 25 disabled/quarantined, 19 active. No added write permission was found in the changed workflow patches.
- The XRP ingestion workflow is integration-only, main-guarded, read-only (actions:read, contents:read), no external credentials; 47 source definitions, 45 scheduled (43 hourly, two weekly), two noncommercial XRPL node sources excluded. It has not run on main.
- GitHub Actions raw receipts/artifacts retain 90 days, per-run feature-store checkpoints seven days and daily checkpoints 90 days. This is not WORM storage.
- No manual workflow dispatch occurred. Paper-trader, A2A deployment/secret-rotation, Databricks and Hugging Face workflows were not dispatched. The self-hosted-brain deployment job remains disabled by an unconditional false guard.
- Main branch protection reports enabled, but detailed branch-protection access returns HTTP 403. The visible Fall Back ruleset is disabled. The GitHub connector reports admin=true, maintain=true, push=true, pull=true and triage=true: overprivileged for least privilege.
- .config/gh/hosts.yml is absent from main and #1661 but remains present in all 17 rechecked affected open-PR branch-tip trees. No contents were read. Repository notes report OAuth revoked; provider-side revocation remains unverified.
- Main GitHub Pages is enabled and a main push automatically publishes. Publication remains unauthorized. No main write occurred.
- Main Cross Analysis succeeded at run 43052515532. The latest Pillars Consistency Check, run 43025487840, failed because GitHub App environment variables are missing, Databricks returned HTTP 403 and Hugging Face returned BUILD_ERROR. This is a platform-health check, not main Python CI.

### Integration overlap reconciliation

All source paths in these PRs are represented in #1661; no source-only paths were found:

| PR | Shared paths | Identical blobs | Different blobs |
|---|---:|---:|---:|
| #1660 | 972 | 949 | 23 |
| #1643 | 670 | 661 | 9 |
| #1642 | 7 | 0 | 7 |
| #1640 | 280 | 244 | 36 |

#1660 remains a superseded-source candidate, not a PR to close before successor merge and main verification. Differing blobs require semantic reconciliation. Preserve unique/unreviewed work including #1653, #1614, #1611, #1610, #1612, #1269 and #1608. No source PR was closed.

### XRP market update — November 11

All observations below are public-web/API research, not Barrot raw receipts and not model-eligible.

**Spot:** OKX XRP-USDT last 1.0726 (bid 1.0724/ask 1.0725), provider event time 16:15:22.244 UTC; 24h open 1.0478, high 1.0797, low 1.039, volume 44.58M XRP. Kraken XRP/USD last $1.07555 (bid $1.07554/ask $1.07555), no provider event timestamp; its open is UTC-day open 1.05511, not a rolling 24-hour open. USDT/USD was 0.99889; normalized OKX reference $1.07141, about 0.385% below Kraken. Asynchronous quotes, not executable arbitrage.

**Spot depth:** Fuelmaps six-venue snapshot at 15:00 UTC had mid $1.0558; ±1% $14.4M bids/$10.6M asks; ±5% $25.2M/$13.6M; ±10% $35.0M/$16.0M. Binance and Bitget excluded. At the later 16:15 spot capture this book was about 75 minutes old and price had moved materially; resting orders can be cancelled.

**Perpetuals:** TradRadar at 15:55 UTC showed price $1.0721 (+2.86%), OI $1.59B (+1.26%), funding +0.0077%/8h, $2.76M liquidations ($1.26M longs/$1.51M shorts), 79.8% long accounts. Liqwall at 14:52 UTC showed OI $1.16B (-2.4%), funding +0.0082%, $11.7M liquidations ($10.8M longs/$0.95M shorts), 75.3% Binance accounts long. Different venue/contract coverage and observation windows; do not average. The newer TradRadar snapshot shows a different liquidation mix from Liqwall.

**Options:** OptimistFi/Deribit at 12:00 UTC: 30-day ATM IV 58.3%, 25-delta skew -0.6 points (puts richer), put/call 0.55, December 25 OI $47.2M. The earlier 05:00 snapshot was 59.0% IV and +0.3 skew. Preserve vintages and provider convention; near-expiry puts remain richer.

**ETF flows:** Alpha Finance through November 10 (five of five funds) reports -$7.6M on Nov10, -$10.4M Nov9, -$18.0M over seven sessions, +$1.3M over 30 sessions and +$1.71B cumulative net inflows. It does not publish AUM/holdings. Cumulative flows are not current AUM or proof of exchange sales.

**Exchange balances/flows:** XRP Insights at 08:00 UTC attributes 22.33B XRP to 701 wallets across 24 exchanges; same-wallet change +1.3M over seven days and -155.7M over 30 days. Newly tracked wallets distort naive total changes; cold storage is included and this is not tradable float. TrackWhale's 05:51 UTC seven-day tracked external transfers show 501.72M inflows, 602.93M outflows and -101.21M net; largest transfer 368.48M XRP is an unknown wallet, not an exchange attribution.

**Evernorth on-chain:** XRP Insights at 15:58 UTC attributed 103.13M XRP to 13 wallets against 473.276M company-reported closing XRP; 370.347M moved outside the currently attributed set by October 22. This is an attribution gap, not proof of sale or loss.

**XRPL governance:** own-node/roll-call tracker at 16:07 UTC, ledger 108,263,699, heard 35/35 validators, 29 yes required. SingleAssetVault 23/35, LendingProtocol 22/35 and LendingProtocolV1_1 22/35. No 14-day activation countdown; native XRPL lending remains inactive.

### Material SEC entity-attribution correction

A closer legal-entity review found that Run25b's parent/subsidiary labels were inverted. The SEC filing's financial-statement headings establish:

- **Evernorth Holdings Inc. (Pubco parent):** about $97,745 unrestricted cash, $696.1M net working-capital deficit, $340.9M accumulated deficit, $265.6M six-month operating loss and $188.1M net loss. Operating cash used was about $1.33M; $264.1M digital-asset impairment and $77.5M non-cash fair-value gain explain why net loss is not cash burn.
- **Pathfinder Digital Assets LLC (subsidiary):** about $789,682 unrestricted cash, $3.7M net working-capital deficit, $3.125M accumulated deficit, $2.2M operating loss and $2.138M operating cash used.
- The $10M Ripple Company Facility with $9.7M drawn as of October 7 belongs to Pathfinder; separate $1M Evernorth Facility to the parent was undrawn as of June 30.
- The $30M 4% PIK convertible note funded October 12 and the Cantor ELOC belong to Pubco. The note's 4x conversion cap and 8% yield-to-put are conditional terms, not currently due cash. The ELOC's 5,218,935-share capacity at 97% VWAP had generated zero proceeds as of the prospectus.
- Reported closing XRP was 473.276M: 84.366M purchased with $214.05M advance cash and 388.911M contributed in kind. SBI's $200M disclosed cash commitment is included in the advance-funding pool, not additive.

This correction is material: the parent has limited unrestricted cash and substantial working-capital deficit; the subsidiary has a much smaller deficit. Keep parent debt, subsidiary facility, cash purchase, in-kind XRP, ELOC capacity and resale registration separate. The filing warns XRP may need to be sold to meet obligations in adverse conditions.

### Institutional network and capital distinctions

- Circle Q3 2026: average USDC circulation $73.3B, Q3 on-chain volume $13.9T, revenue/reserve income $865M, reserve income $658M (-8% YoY), other revenue $207M including $182M ARC presale, distribution/transaction/other costs $412M, adjusted EBITDA $317M. The $182M ARC presale materially affects the EBITDA comparison. Circle reported $41.3B annualized CPN TPV, Arc public mainnet and a $100M Binance equity investment plus expanded USDC partnership.
- Coinbase Q3: average USDC held $22B (+49% YoY), 10.7% trading market share, $719M net income versus $78M adjusted net income, $333M adjusted EBITDA. Coinbase reports it captured about 50% of USDC economics over the past year.
- SBI's official disclosure says SBI Holdings and SBI Shinsei Bank invested $25M each in Circle ($50M total) and reports approximately 9% Ripple equity ownership as of its 2025 disclosure. These are separate equity investments, not XRP token purchases. SBI Ripple Asia is a separate joint venture; SBI's $200M Evernorth cash commitment is included in the aggregate advance-funding pool.
- Ripple RLUSD is available on Coinbase Prime, Exchange and Retail across XRPL/Base/Ethereum; Coinbase Global Exchange collateral support was announced as future, not verified live.
- BNY supports XRP and RLUSD custody and remains primary RLUSD reserve custodian. Standard Chartered's RLUSD custody on XRPL is live through its DIFC branch; Ripple/LMAX collateral integration remains planned.
- PNC's limited corporate/institutional USDC pilot uses Ethereum and Coinbase APIs, with 1:1 USD deposit conversion. It is a USDC rail, not XRP settlement.

### SBIC, AI and exact-phrase research

- Tokyo SBIC's official profile identifies Tokyo Small and Medium Business Investment & Consultation Co., Ltd. as SBIC East Japan and lists Nagoya and Osaka as sister companies. Official Nagoya and Osaka pages identify the Central and West regional companies. They are separate statutory SME investment/consultation companies, not SBI Holdings.
- Tokyo SBIC's June 2025 investee-only training included ChatGPT, Copilot, APIs and RAG. SBI Holdings separately announced ChatGPT Enterprise adoption in May 2025 and an Anthropic/Claude AI transformation collaboration in June 2026. These are distinct corporate activities, not evidence of a regional SBIC-OpenAI partnership.
- Official Permission docs identify Permission Coin ASK as LayerZero OFT-20 on Base and Polygon only. No XRPL contract/integration is documented by those official token docs. Other Askcoin and Ask Coin exchange listings remain separate candidates.
- No primary-source match was established for the exact phrase “SBIC, ChatGPT SBIC” or “actual capital” as a standardized XRP metric. Keep capital categories separate.
- Dr. Kamilah Stevenson person identity is supported by first-party evidence, but no first-party YouTube channel ownership link was verified in this pass. No public video inventory is attributed. Camilla/Kamilah are not assumed to be the same person.

### Nine-platform coordination

ChatGPT/GitHub API access is verified but overprivileged. Copilot has no formal PR approval. Claude, Grok, Gemini and Codex remain unverified; Hugging Face BUILD_ERROR; Kaggle untested/no submission; Databricks HTTP 403/no workspace write. LunaRoute remains repository-declared canonical brain, but endpoint authentication/data flow is unverified. No external-model transfer occurred.

### Prediction-engine status and decision

Implemented on integration: 47 public source definitions, 45 scheduled; read-only collector; SHA-256 receipt/hash-chain logic; point-in-time SQLite feature store; four deterministic baselines; chronological walk-forward with purge/embargo; calibration and PSI drift diagnostics; fail-closed Ed25519 evaluator-attestation contract.

Still not production verified: independent WORM/timestamp anchor, replayable feature-store reconstruction, synchronized historical spot/L2/derivatives/flows/collateral, vintage-aware macro/event timeline, scenario/counter-hypothesis generator, production evaluator key, independent shadow outcomes and out-of-sample lift over all four baselines. The SQLite store is owner-mutable; GitHub Actions artifacts/cache are not WORM.

**Forecast: NOT_ISSUED.** No directional forecast, paper trade or real-money action occurred.

### Backlog and next actions

- #1661: blocked active integration draft; no formal approvals/reviews/threads. Exact code head passed; Run30 documentation commit CI pending.
- #1660: superseded-source candidate; 972/972 paths represented, 949 identical and 23 different. Retain until successor merge and main verification.
- #1643: 670 paths represented, 661 identical/9 different. #1642: 7 represented, all different. #1640: 280 represented, 244 identical/36 different. Reconcile differences before source closure.
- Preserve unique/unreviewed graph, prediction, safety and topology work. No source PR was closed.
- Next: complete exact-head CI on this Run30 commit; finish semantic review of 969 non-workflow paths; resolve least privilege, branch-protection/approval visibility, credential revocation/remediation and Pages authorization; then continue integration. After any authorized merge, refetch main, verify merge commit/files, run main CI and inspect automatic Pages side effects.

No merge, deployment, secret rotation/revocation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or PR closure occurred.
