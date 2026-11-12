# BARROT XRP Mission Handoff — Canonical (latest Run36)


> **Latest verified snapshot — Run36, 2026-11-11 21:28 UTC.** Main SHA remains `84f28ee7755607236231545a14f3d093c1baaa85`. Code head `601fb36cd2185843ab8592afc027a680946f7e85` passed exact-head CI: 3,449 passed, zero failures, eight subtests, 59.99% coverage; six-manifest dependency audit and fail-closed PR gate passed. Run36's research artifact has been committed; this handoff/map update is documentation-only and requires its own exact-head CI. Forecast remains `NOT_ISSUED`; PR #1661 remains draft and blocked. Current branch tip before this handoff update: `93967631fd7e9813415efc114dbc905f67171ff2`.


**Captured:** 2026-11-11T18:00:11Z  
**Mission:** XRP intelligence and measured prediction-engine mastery remain priority 1. Preserve Barrot V3 as the execution, orchestration, safety and verification foundation.

## Repository and exact-head verification

- Main: `84f28ee7755607236231545a14f3d093c1baaa85`.
- Integration branch: `integration/xrp-v3-unified-main-20261111`.
- Head before this Run32 durable commit: `ed345e0efc5d6794cef58220891fc03e3ac96ab7`.
- PR #1661: open, draft, mergeable, 2,039 commits ahead, zero behind; 1,015 changed files (44 workflows, 971 other paths).
- Complete recursive trees: main 1,388 entries; integration 2280 entries.
- Open PR inventory: 374 (360 draft, 14 non-draft).
- Exact-head CI on `ed345e0efc5d6794cef58220891fc03e3ac96ab7`: **3,449 passed, 0 failed, 8 subtests**, 59.99% coverage against a 53% floor; 95.58 seconds. Wheel build and installed Barrot V3/XRP mission verification passed.
- Full CI: [43069181417](https://github.com/Barrot-Agent/B-Agent/actions/runs/43069181417); full-suite job 130692136572.
- Dependency audit: [43069181401](https://github.com/Barrot-Agent/B-Agent/actions/runs/43069181401), six manifests, zero known vulnerabilities reported.
- Fail-closed PR gate: [43069181393](https://github.com/Barrot-Agent/B-Agent/actions/runs/43069181393); push dependency audit [43069171761](https://github.com/Barrot-Agent/B-Agent/actions/runs/43069171761); push fail-closed gate [43069171815](https://github.com/Barrot-Agent/B-Agent/actions/runs/43069171815).
- Latest main Cross Analysis: [43072200254](https://github.com/Barrot-Agent/B-Agent/actions/runs/43072200254), success on unchanged main SHA. Main CI [42944864014](https://github.com/Barrot-Agent/B-Agent/actions/runs/42944864014) passed 718 tests.
- This Run32 commit changes the handoff, sync, platform map and adds one research artifact. A new exact-head run is required; the 3,449 result above belongs to parent `ed345e0efc5d6794cef58220891fc03e3ac96ab7`, not this new commit.

## Market refresh — November 11, 2026

**Spot depth, Fuelmaps 18:00 UTC:** six venues, mid $1.0679. Within 0.5%: $7.8M bids/$7.0M asks; 1%: $13.7M/$11.9M; 2%: $18.6M/$13.7M; 5%: $23.0M/$14.8M; 10%: $32.9M/$17.4M. Binance and Bitget excluded. Hourly averages of one-minute resting-book observations; displayed orders can be cancelled.

**Perpetuals, two different universes:**
- TradRadar 17:25 UTC: OI $1.58B (+1.10%), funding +0.0046%/8h, $2.86M liquidations ($1.75M shorts/$1.11M longs), 79.8% long accounts.
- Liqwall 17:32 UTC: OI $1.17B (-1.3%), funding +0.0043%/8h, $2.8M liquidations ($1.6M shorts/$1.2M longs), 75.3% Binance accounts long.
- Both show positive funding, concentrated long accounts and slightly more short than long liquidations; OI direction disagrees. Possible short-covering alongside venue-specific positioning changes; do not average.

**Options, Deribit/OptimistFi 15:00 UTC:** 30-day ATM IV 58.1%; 25-delta skew +1.8 points; put/call 0.55; Dec 25 OI $47.4M. Near-expiry Nov 12/13 skew is put-rich (-4.2/-3.0), while Dec 25/Mar 2027 is call-rich (+2.9/+4.5). Mixed term structure.

**ETF flow reconciliation:**
- Alpha Finance through Nov 10: five-fund net flow -$7.6M; seven sessions -$18.0M; 30 sessions +$1.3M; cumulative net inflow +$1.71B. It does not publish holdings/AUM.
- XRP Insights reports 1.19B XRP across seven products, but that universe is six spot ETFs plus BITW's XRP index-fund sleeve, not seven pure spot ETFs. Its holdings-delta flow series excludes GXRP flow due a known capture gap; BITW rebalancing and XRP-paid fees may be counted as flow; some historical rows are reconstructed; settlement can be revised the next morning. Its latest settled data is Nov 10. Do not merge these methodologies into one series.

**Supply/collateral context from XRP Insights:** 31.10B XRP escrow; 22.33B in 701 publicly attributed wallets across 24 exchanges (a floor, not ceiling); 473.3M company-reported treasury XRP; 418.9M XRP in DeFi/wrapped products; RLUSD $2.71B total ($906M XRPL, $1.81B Ethereum); XRPL RWA headline $4.33B, but only $276M described as distributed transferable value and $4.06B as represented registry notional. Ripple operational XRP of 4.74B is static Q3 2024 company reporting; founder 4.60B is an estimate. RWA dates range July 3–October 23. These are not one homogeneous float measure.

**Agentic payments:** XRP Insights attributes 15.54M x402 transactions, 191 agents, 193 merchants and 5,882 endpoints to the t54 Labs facilitator; reported all-time settled value is only 7,030 XRP plus 64,423 RLUSD. This is operator-reported and not independently reconciled. Transaction count is not dollar volume or XRP buy demand.

## Institutional network and regulation

Three separate national trust-bank charters are now recorded as effective in the OCC application register:
- First National Digital Currency Bank, N.A. (Circle affiliate): July 24, 2026.
- Ripple National Trust Bank: October 26, 2026.
- Coinbase National Trust Company: November 6, 2026.

These are trust-bank charters, not full-service deposit-taking commercial banks. Entity distinctions matter:
- Circle Internet Financial LLC is not itself the trust bank; its Circle Mint agreement identifies First National Digital Currency Bank as an affiliated subcustodian. Customer digital assets are not FDIC-insured deposits.
- Ripple says RNTB's approved scope includes RLUSD reserve management, collateral-trustee services and fiduciary custody upon opening. Standard Custody & Trust Company remains RLUSD issuer; BNY remains primary reserve custodian. Effective charter date does not prove first customer custody or transfer of reserve duties.
- Coinbase announced final approval for federal institutional custody. Coinbase Prime now markets spot, US futures, global options and perps under one margin framework and daily settlement. No XRP-specific collateral eligibility was verified.

**Payment rails:** PNC/Coinbase's Nov 9 limited pilot lets eligible corporate/institutional clients receive USDC on Ethereum; incoming USDC is automatically converted to USD and deposited into PNC accounts. This is a Circle-USDC/Coinbase/PNC rail, not XRP settlement.

**Deutsche Bank status disagreement:** Reuters reported on Nov 11 that custody service was live for paying clients. Deutsche Bank's own product page still says services will become available after regulatory timeline and technical readiness. Its stated launch asset set is BTC, ETH, USDC, EURC and EURAU; XRP is not listed. Preserve this as an unresolved limited-launch versus general-readiness discrepancy.

**FSB/Türkiye, Nov 11:** the FSB recommends a dedicated stablecoin regime, financial-stability monitoring, stronger supervision and cross-border cooperation. This is a stablecoin regulatory signal, not XRP-specific adoption.

## SBIC identity and exact-phrase research

Japan's Act on Investment and Consultation Companies for SMEs, Article 2 names exactly three companies:
- SBIC East: Tokyo Small and Medium Business Investment & Consultation Co., Ltd.
- SBIC Central: Nagoya Small and Medium Business Investment & Consultation Co., Ltd.
- SBIC West: Osaka Small and Medium Business Investment & Consultation Co., Ltd.

They are separate regional legal companies, not SBI Holdings. SBIC West's primary Oct 23, 2024 notice documents a generative-AI/ChatGPT introductory seminar for accountants and support institutions; it is educational activity, not an OpenAI partnership.

No primary-source identity or XRPL integration was established for the exact ASK Coin phrase. No standardized XRP metric called "actual capital" was found; continue separating cash settled, cash used to purchase XRP, in-kind XRP, debt, drawn facilities, undrawn ELOC capacity, collateral and secondary sales. No primary evidence of a formal entity or partnership named exactly "SBIC, ChatGPT SBIC" was found.

A candidate YouTube handle `@drkamilahstevenson` appeared in third-party listings, but no first-party ownership cross-link was found; YouTube's page crawl is stale and third-party subscriber/video counts conflict. No video inventory was attributed. Camilla and Kamilah are not assumed to be the same person.

## Prediction engine and platform status

**Implemented on integration:** 47 source definitions (45 scheduled), read-only collector, SHA-256 receipt-chain logic, point-in-time SQLite prototype, four deterministic baselines, chronological walk-forward with purge/embargo, calibration and PSI drift diagnostics, fail-closed forecast ledger requiring Ed25519 evaluator attestation.

**Not production-complete:** independent WORM/timestamp anchoring, replayable feature history, synchronized market/flow/collateral history, vintage-aware macro/geopolitical timeline, scenario/counter-hypothesis generator, production evaluator key, independent shadow outcomes and demonstrated out-of-sample lift. Collector is gated to main and has not been verified running on main because the integration is not merged.

Nine-platform status: ChatGPT/GitHub API access verified but connector permissions are overprivileged; Claude, Grok, Gemini and Codex unverified; Copilot has no formal PR approval; Hugging Face BUILD_ERROR; Kaggle untested; Databricks HTTP 403; LunaRoute is repository-declared canonical brain but its endpoint authentication/data flow are unverified. No external-model transfer occurred.

**Forecast: NOT_ISSUED.** Run32 web observations were not captured through Barrot's raw-source receipt pipeline and are not model-eligible. No directional forecast, paper trade or real-money action occurred.

## Merge and security decision

PR #1661 remains draft with zero formal reviews, approvals or review threads. Main branch-protection details return HTTP 403. The only visible fallback ruleset is disabled. The GitHub connector reports admin/maintain/push/pull/triage permissions, which is overprivileged. Security-alert endpoints are not available through the current fetch wrapper; no absence of alerts is inferred.

The credential path `.config/gh/hosts.yml` is absent from main and integration but remains present in 17 rechecked open-PR branch tips. Contents were not read; provider-side OAuth revocation is not independently verified. Main Pages publication is push-triggered and remains unauthorized.

Current blob reconciliation: #1660 has 972 changed paths represented (949 identical, 23 different); #1643 has 670 represented (661 identical, 9 different); #1642 has 7 represented (0 identical, 7 different); #1640 has 280 represented (244 identical, 36 different). Different blobs require semantic review. Preserve unique graph, prediction, safety and topology PRs. No source PR was closed.

**Decision: do not merge.** Draft status, absent approvals, inaccessible branch-protection requirements, connector overprivilege, credential-path remediation, Pages authorization and incomplete semantic review of 971 non-workflow paths remain blockers.

## Next concrete actions

1. Verify exact-head full-suite CI on the Run32 durable commit.
2. Continue semantic review of the 971 non-workflow paths, prioritizing V3 runtime, ingestion, feature store, forecast ledger and public interfaces.
3. Resolve least-privilege, branch-protection/approval visibility, OAuth revocation evidence and Pages authorization.
4. Reconcile differing source PR blobs without closing unique work.
5. Implement independent WORM/timestamp anchoring, replayable historical features and the scenario/counter-hypothesis engine.
6. Keep forecasts disabled until independent shadow and out-of-sample gates pass.

**No merge, deployment, secret rotation/revocation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or PR closure occurred.**

---

# Run31b — exact-head suite passed, workflow audit resolved, expanded XRP supply/collateral and regulatory research

Captured: 2026-11-11T17:18:50Z

## Exact-head repository verification
Parent `1af8d45fd6352342248d0495f7cbdaf556784446` passed the full repository suite: **3,449 passed, 0 failed, eight subtests**, 59.99% coverage, 95.64 seconds. Core714/0; wheel build and installed primary-mission verification passed; six dependency manifests audited, zero known vulnerabilities; fail-closed PR/push gates passed.
- [Full CI43065866159](https://github.com/Barrot-Agent/B-Agent/actions/runs/43065866159), [full-suite job130680728322](https://github.com/Barrot-Agent/B-Agent/actions/runs/43065866159/job/130680728322), [dependency audit43065866267](https://github.com/Barrot-Agent/B-Agent/actions/runs/43065866267), [fail-closed gate43065866142](https://github.com/Barrot-Agent/B-Agent/actions/runs/43065866142).
- Four prior failures on3e6a3ca were stale current-map assertions. Run31 corrected the map; exact-head rerun passed. This verifies parent1af8d45 only; Run31b docs/research commit needs its own exact-head CI.

## Repository state before Run31b commit
Main84f28ee; PR#1661 parent1af8d45fd6352342248d0495f7cbdaf556784446,2037 ahead/0 behind;1,015 changed files(44 workflows/971 other); main tree1,388 entries/1,288 blobs; integration2,280 entries/2,171 blobs. Open PRs374(360 drafts/14 non-drafts). #1661 remains open/draft, zero formal reviews/approvals/threads.

## Workflow audit discrepancy resolved
All44 changed workflow diffs inspected:26 quarantined/disabled,18 active;24 manual-dispatch additions,one schedule; no added contents:write/actions:write/write-all/pull_request_target/workflow_run. No manual workflow dispatched. Self-hosted-brain job retains false guard. XRP collector is main-gated/read-only; Actions artifacts/cache are not WORM. Run30's25/19 narrative was incorrect.

## XRP market, supply and flows
Supplemental capture November11,17:16–17:18 UTC. Web observations remain research-only; no canonical raw-source hash/receipt was created.
- OKX XRP-USDT event17:15:52.272: last1.0727, bid1.0726/ask1.0727, rolling24h open1.0465, high1.0797, low1.0456, volume44.18M XRP. Top ask size88,411 vs bid1,350 is cancellable.
- Kraken last1.06924, bid/ask1.06949/1.06950 without event timestamp; USDT/USD midpoint0.999015. Normalized asynchronous gap+0.196%; Kraken freshness unverified, not arbitrage.
- Basis Binance perpetual book16:16: within1% bids/asks both$15.2M. Fuelmaps six-venue spot book08:00: within1%$14.0M/$11.1M and within5%$23.8M/$14.3M. Different markets/windows.
- XRP Insights22.33B XRP across701 attributed wallets/24 exchanges; same-wallet+1.3M/7d,-155.7M/30d;480.5M wrapped reserves included. Not customer deposits/tradable float. TrackWhale-101.21M/7d is a different method.
- Escrow tracker31.10B; scheduled Dec1 unlock up to1B; circulating definition68.89B differs from vendors subtracting Ripple operational holdings.
- ETF holdings tracker1.19B XRP/7 products,AUM$1.28B; Alpha five-fund flow series is a different universe.
- XRPL RWA$4.33B across18 assets: only$276M distributed/transferable; $4.06B represented registry/issuer notional.
- RLUSD tracker$2.71B: $906M(33%) XRPL,$1.81B(67%) Ethereum. USDC native XRPL supply tracker$4.446M vs~$69.89B total, rounded0.01%. Stablecoin supply does not prove XRP auto-bridge volume.

## Coinbase collateral, SBI, Ripple and Circle
- Coinbase cbXRP proof-of-reserves:151,930,567.32 XRP reserve vs151,928,320.78 cbXRP supply (page time04:46 AM, timezone unspecified), excess2,246.54 XRP.
- CryptoSlate Nov6 Morpho/Base snapshot:$59.2M USDC debt against119.9M cbXRP/1,070 positions; $8.84M conditionally liquidation-eligible after10% further oracle decline; $3.23M/462 positions after5%. One secondary analysis, not independently corroborated. Conditional cbXRP risk, not native XRP sale.
- SBI June9 2025 disclosure:$25M Circle investment by SBI Holdings+$25M by SBI Shinsei Bank; SBI said it held~9% Ripple then. Not a refreshed2026 register.
- SBI VC Trade USDC distribution began March2025; SBI disclosed SBI Circle Holdings JV-establishment agreement.
- SBI/Ripple RLUSD distribution began June24 2026 via SBI VC Trade. JPYSC is separate: SBI Shinsei Trust issuer, SBI VC Trade distributor, Startale co-developer; initial accounts only, external transfers disabled. Open Standard JPYSC/OUSD is POC exploration, not production. SMBC's5% stake is in SBI Startale Marketing, amount undisclosed; not XRP.
- Ripple/Coinbase RLUSD distribution and Ripple/BNY XRP/RLUSD custody are not proof of XRP buying or bridge demand.

## Actual capital, regulation and macro
No standardized XRP “actual capital” metric was found. Separate cash committed, cash funded, cash deployed to buy XRP, in-kind XRP, debt, undrawn facilities, ELOC capacity, resale registrations, custody and transferable float.
Evernorth:473.276M closing XRP=84.366M cash-purchased from$214.05M advance funding+388.911M in-kind; SBI's$200M is included in$214.05M; $30M PIK notes are debt; $9.7M Ripple facility drawn by Oct7 is subsidiary debt; ELOC proceeds zero. Parent/subsidiary SEC labels corrected in Run30.
- SEC/CFTC March17 2026 interpretation, effective March23: five-token taxonomy/investment-contract guidance; not XRP-specific adjudication or comprehensive legislation.
- Senate H.R.3633 Sep15 cloture vote49-50 rejected; Senator Coons did not vote; no market-structure statute enacted by this vote.
- Reuters Nov11: third consecutive upside CPI surprise; Dec9 25bp hike fully priced; Goldman forecasts another25bp March2027, Deutsche Bank Jan2027; 50bp December probability13.5%. Oil amid Iran war, tariffs, demand and AI investment cited. Broad macro backdrop, not XRP causality.

## Forecast and merge
Forecast **NOT_ISSUED**. No directional forecast, paper trade or real-money action. PR#1661 remains draft/unmerged. Branch-protection detail HTTP403; fallback ruleset disabled; connector overprivileged; credential path remains in17 other open-PR tips(contents not read, provider revocation unverified); Pages auto-publication unauthorized;971 non-workflow paths need semantic review. Preserve unique PRs; no source PR closed.

Run31b updates current map, canonical handoff, BARROT_SYNC and existing Run31 artifact. New docs/research commit triggers exact-head CI; parent1af8d45 is last verified head.

---

# Run31 — current-head CI diagnosis, XRP market refresh and institutional reconciliation

Captured: 2026-11-11T17:05:39Z

## Mission
XRP intelligence and prediction-engine mastery remain priority one. Barrot V3 remains the execution, orchestration, safety and verification foundation.

## Repository
- Main SHA: `84f28ee7755607236231545a14f3d093c1baaa85`.
- Existing [PR #1661](https://github.com/Barrot-Agent/B-Agent/pull/1661), branch `integration/xrp-v3-unified-main-20261111`; parent head `3e6a3ca8794cb90c7cb9c2add42fa8e722716e5d`, 2,036 ahead/0 behind.
- 1,014 changed files (44 workflows, 970 other paths); main tree 1,388 entries/1,288 blobs; integration 2,279 entries/2,170 blobs.
- Open PR inventory: 374 (360 drafts, 14 non-drafts). #1661 open/draft, zero formal reviews/approvals/threads.

## Exact-head CI
On `3e6a3ca8794cb90c7cb9c2add42fa8e722716e5d`:
- Full suite **3,445 passed, 4 failed, eight subtests**, 59.99% coverage; 86.44 seconds.
- Core suite 714 passed, zero failed.
- Four failures are stale current-map assertions in `tests/test_xrp_nine_platform_current_map_run73.py` comparing live branch/PR/CI metadata with old 415e611/4e7a7 values. No product runtime, ingestion or prediction-engine failure was observed.
- [Full CI 43061303949](https://github.com/Barrot-Agent/B-Agent/actions/runs/43061303949), [full-suite job 130664304843](https://github.com/Barrot-Agent/B-Agent/actions/runs/43061303949/job/130664304843).
- [Dependency audit 43061303705](https://github.com/Barrot-Agent/B-Agent/actions/runs/43061303705): six manifests, zero known vulnerabilities, passed.
- [Fail-closed PR gate 43061303654](https://github.com/Barrot-Agent/B-Agent/actions/runs/43061303654) and [push gate 43061294425](https://github.com/Barrot-Agent/B-Agent/actions/runs/43061294425): passed.
- Wheel/installed mission step was skipped after the full-suite failure. Current-map correction committed in Run31; exact-head rerun pending.

## XRP market — capture 2026-11-11T17:05:39Z
All web observations are research-only; no byte-complete raw-source receipt or SHA-256 raw hash was created by Barrot.
- OKX XRP-USDT event 16:45:33.874 UTC: last 1.0684, bid 1.0686/ask 1.0687; rolling 24h open 1.0456, high 1.0797, low 1.0395; volume 44.36M XRP.
- Kraken XRP/USD at retrieval: last 1.06924, bid 1.06949/ask 1.06950; UTC-day open 1.05511, high 1.07824, low 1.04241; volume 22.27M XRP. No event timestamp.
- Kraken USDT/USD midpoint 0.998925. Normalized OKX midpoint $1.06750 vs Kraken $1.069495, asynchronous gap -0.1864%. OKX event is about 20 minutes old; Kraken timestamps unavailable; both last trades below best bids. Not arbitrage.
- Basis Binance XRPUSDT perpetual depth at 16:16: 1,000-level bids $43.1M/offers $33.0M; within 1% bids/asks both $15.2M. Fuelmaps six-venue spot depth at 08:00: within 1% $14.0M bids/$11.1M asks; within 5% $23.8M/$14.3M. Different market types and freshness; no averaging.
- TradRadar 14:40: OI $1.57B (-2.83%), funding +0.0080%/8h, at least $9.29M liquidations (longs $8.35M), 79.7% long accounts. Liqwall 16:32: OI $1.17B (-2.0%), funding +0.0062%, $2.7M liquidations (longs $1.3M, shorts $1.5M), 75.2% Binance accounts long. Different universes/windows; later short-liquidation edge is counter-evidence to persistent long-liquidation claims.
- Alpha Finance through Nov10: -$7.6M Nov10, -$10.4M Nov9, -$18.0M over seven sessions, +$1.3M over 30 sessions, +$1.71B cumulative net inflow. Five of five tracked funds; no Nov11 flow. Not current AUM.

## Institutional network
- Ripple/Coinbase (Oct28): RLUSD available on Prime, Exchange and Retail across XRPL/Base/Ethereum. Ripple reported >$2.4B market cap. Coinbase Global Exchange collateral support was future scope, not live.
- Ripple/BNY (Oct27): BNY supports XRP/RLUSD custody and is primary RLUSD reserve custodian. Direct mint/redeem, broader XRPL tokenization and C2FO trade-finance work remain future/exploratory.
- JPYSC (June24): SBI Shinsei Trust issuer, SBI VC Trade distributor, Startale technical partner. Initially restricted to SBI VC Trade accounts; external wallet transfers disabled. Public-chain circulation conditional on legal/tax practice; no XRP settlement established.
- Open Standard (Oct16): SBI/Startale considering JPYSC/OUSD interoperability POC; 140+ company participation claim includes Coinbase, Visa, Stripe, Mastercard and BlackRock. Exploratory, not production.
- SBI/SMBC (Oct30): SMBC agreed to 5% capital participation in SBI Startale Marketing, the SBI/Startale JPYSC marketing JV; amount undisclosed. Not XRP purchase/Ripple equity.

## Identity and platform status
- SBIC East/Tokyo, Central/Nagoya and West/Osaka are separate regional SME investment companies, not SBI Holdings.
- No primary-source exact match for “SBIC, ChatGPT SBIC” or a standardized XRP “actual capital” metric.
- Permission ASK official contract docs list Base/Polygon; no XRPL integration verified. No first-party Kamilah/Camilla YouTube channel ownership; no videos attributed.
- ChatGPT/GitHub API authentication works, but connector reports admin/maintain/push/pull/triage privileges. Copilot no formal PR approval. Claude/Grok/Gemini/Codex unverified; Hugging Face prior BUILD_ERROR; Kaggle untested; Databricks prior HTTP 403; LunaRoute declared but endpoint unverified. No external-model transfer.

## Prediction and safety
Integration contains 47 source definitions/45 scheduled (43 hourly, two weekly; two non-commercial XRPL-node sources excluded), read-only collector, SHA-256 receipt/hash-chain logic, point-in-time SQLite prototype, four baselines, chronological purge/embargo walk-forward, calibration/PSI drift and fail-closed Ed25519 evaluator-attestation contract.
Outstanding: independent WORM/timestamp anchor, replayable history, synchronized spot/L2/derivatives/flow/collateral, macro/geopolitical vintages, scenario/counter-hypothesis generation, production evaluator key, independent shadow outcomes and demonstrated out-of-sample lift. No main ingestion run. Forecast **NOT_ISSUED**.

## Security, backlog and merge
- Branch-protection details HTTP 403; fallback ruleset disabled; connector overprivileged.
- `.config/gh/hosts.yml` present in all 17 rechecked affected open-PR branch tips; contents not read; provider-side OAuth revocation unverified.
- Main push automatically publishes Pages; explicit publication authorization absent.
- Workflow count discrepancy: map fields 26 quarantined/18 active vs Run30 narrative 25/19. Re-audit all 44 changed workflow diffs.
- #1660: 972 paths represented in #1661, 937 identical/35 different/zero absent; three commits behind current main and dirty. Retain until successor merge/verification.
- Preserve unique work (#1653, #1614, #1611, #1610, #1612, #1608 and topology/research branches). No PR closed.

**No merge.** Current exact-head suite failed four stale evidence-map assertions. Map correction committed; exact-head rerun required. Zero approvals, protection requirements unavailable, semantic review incomplete, credential and Pages blockers unresolved.

## Run31 durable files
- Current map: `research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_current.json`.
- Append-only artifact: `research/xrp_intelligence/20261111T170539Z-run31-exact-head-ci-repair-live-market-and-institutional-reconciliation.json`.
- Canonical handoff: `BARROT_XRP_MISSION_HANDOFF_LATEST.md`.
- Shared sync: `BARROT_SYNC.md`.

No merge, deployment, secret rotation/revocation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or PR closure occurred.

---

# Historical handoff — Run29b and earlier

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


## Run33 — 2026-11-11 19:34 UTC
XRP intelligence and prediction-engine mastery remain Barrot's highest-priority mission. Barrot V3 remains the protected execution, orchestration, safety and verification foundation.
### Repository state
- Main SHA: `84f28ee7755607236231545a14f3d093c1baaa85`.
- Integration branch: `integration/xrp-v3-unified-main-20261111`; exact parent before this corrective commit: `570cd11ab16be1c61cb44a6b10740e7eb726b123`.
- 2,040 commits ahead, zero behind; 1,016 changed files (44 workflows, 972 other paths); 374 open PRs (360 drafts, 14 non-drafts). Main tree 1,388 entries; integration 2,281.
- GitHub API access succeeded; local Git clone remains unavailable because this environment cannot resolve github.com.
### Exact-head CI diagnosis
- Full suite on `570cd11`: **3,447 passed, 2 failed, eight subtests**, 59.99% coverage against 53% floor; 85.93 seconds. Core suite: 714 passed, zero failed.
- Both failures are stale current-map assertions in `tests/test_xrp_nine_platform_current_map_run73.py`: repository snapshot compared ahead_by 2039 vs 2037; exact-head evidence compared tested head 1af8d45 vs latest attempt ed345e0. All other 3,447 tests passed. This is evidence-map synchronization, not a Barrot V3 runtime or prediction-engine regression.
- Wheel build and installed-wheel verification were not reached on this failed attempt. Dependency audit passed six manifests/zero known vulnerabilities. Fail-closed PR gate, push dependency audit and push gate passed.
- [Full CI 43076617980](https://github.com/Barrot-Agent/B-Agent/actions/runs/43076617980), [full-suite job 130717985219](https://github.com/Barrot-Agent/B-Agent/actions/runs/43076617980/job/130717985219). [Dependency audit 43076617995](https://github.com/Barrot-Agent/B-Agent/actions/runs/43076617995). [Fail-closed gate 43076617805](https://github.com/Barrot-Agent/B-Agent/actions/runs/43076617805). [Push audit 43076605066](https://github.com/Barrot-Agent/B-Agent/actions/runs/43076605066). [Push gate 43076605226](https://github.com/Barrot-Agent/B-Agent/actions/runs/43076605226).
- Previous exact passing parent `ed345e0efc5d6794cef58220891fc03e3ac96ab7`: 3,449 passed/zero failed, eight subtests, wheel and installed mission verified in [CI 43069181417](https://github.com/Barrot-Agent/B-Agent/actions/runs/43069181417).
- Run33 corrects the map to the live repository/PR state and scopes the failed evidence to `570cd11`. Exact-head CI on the new corrective commit is pending; do not reuse parent results as current-head verification.
### Run33 XRP market research — research-only, not model-eligible
- OKX XRP-USDT: 1.0561, bid 1.0560/ask 1.0561; event 19:34:20.774 UTC; rolling 24h open 1.0687, high 1.0807, low 1.0472; volume 43.35M XRP.
- Kraken XRP/USD: last 1.05783, bid 1.05793/ask 1.05794; no event timestamp; UTC-day open 1.05511. Kraken USDT/USD midpoint 0.998955 normalizes OKX to about $1.05500, 0.278% below Kraken midpoint. Asynchronous; not executable arbitrage.
- Bybit XRPUSDT 1.063 at 18:56:30.972 UTC, nearly 38 minutes older; not synchronized.
- Fuelmaps 18:00 six-venue spot depth: within 1% $13.7M bids/$11.9M asks; within 5% $23.0M/$14.8M; within 10% $32.9M/$17.4M. Excludes Binance/Bitget; 94 minutes old; resting orders can be cancelled/moved.
- CryptoTicker reports Binance cumulative funding +0.18% over 30 days via CryptoQuant; OKX 76/100 positive settlements since Oct9, +0.39% cumulative; current settlement +0.01%. OKX OI fell $132.1M to $101.9M Nov4–10 (-23% USD, about -10% XRP units); account long/short ratio 3.70.
- Fexr 10:42 snapshot: OI $102.9M, annualized funding +6.72%, 24h liquidations $12.4M/92% longs. Single-venue/aggregator universe, not global OI.
- TradRadar 17:25 OI $1.58B/+1.10%; Liqwall 17:32 $1.17B/-1.3%; Alpha heatmap 08:24 $2.32B. Different venue/contract universes; do not average.
- Alpha Finance through Nov10: -$7.6M Nov10 and -$10.4M Nov9; seven-session -$18M, 30-session +$1.3M and cumulative +$1.71B. Similar CryptoTicker numbers share SoSoValue/issuer lineage; not independent confirmation.
- Theft-linked wallet flow: 33.456M XRP moved to a collection wallet; 32.34M XRP reportedly left in 193 payments; 87% of 233.46M original theft passed on. Elliptic says most swapped to BTC via THORChain. Ledger transfers are primary; attribution is secondary; buyer and centralized-exchange sales unknown.
- Macro: CPI +0.4% MoM vs +0.3% expected; 90% market-implied 25bp Fed-hike probability as reported by CoinDesk; BTC spot ETF outflows $95M Nov10 after three larger sessions; USDT market cap reportedly down $6.6B over 60 days; Coinbase Premium negative 30 days. Broad risk context, not XRP-specific flow; CoinDesk cites SoSoValue/CryptoQuant.
### Evernorth SEC resale clarification
- Nov9 SEC Form 424B3 registers up to 73,688,162 Class A shares for selling securityholders plus 239,653 Sponsor Warrants. Components include 19,102,635 issued shares, 31,392,746 potential Class C conversion shares, 22,953,128 potential Company Unit redemption/exchange shares and 239,653 warrant-exercise shares.
- Evernorth receives **zero proceeds from selling-securityholder resales**. Sponsor Warrant cash-exercise proceeds are separate. Registration does not prove sales occurred and does not directly sell XRP from Evernorth's treasury. Secondary report says XRPN fell 23.5% Nov10 and XRP 3.9%; causation is not established.
### Institutional, identity and platform status
- OCC trust-bank records from Run32 remain: Circle affiliate effective July24; Ripple National Trust Bank Oct26; Coinbase National Trust Company Nov6. These are trust banks, not ordinary commercial banks; no automatic XRP demand.
- SBIC East/Tokyo, Central/Nagoya and West/Osaka are separate statutory regional SME investment-consultation companies, not SBI Holdings. ASK Coin XRP/XRPL integration not verified; “actual capital” is not a standardized XRP metric; exact “SBIC, ChatGPT SBIC” remains unresolved.
- Candidate YouTube handle `@drkamilahstevenson` remains unverified as belonging to the verified public identity. No videos attributed; Camilla/Kamilah equivalence is not assumed.
- Nine-platform status: ChatGPT/GitHub API verified but overprivileged; Claude/Grok/Gemini/Codex unverified; Copilot no formal approval; Hugging Face BUILD_ERROR; Kaggle untested/no submission; Databricks HTTP403/no workspace write; LunaRoute declared canonical brain but endpoint authentication/data flow unverified. No external-model transfer.
### Workflow and security audit
- All 44 changed workflow patches rechecked; full contents of eight high-risk workflows inspected. 26 quarantined/disabled, 18 active. No added broad contents:write/actions:write/write-all/pull_request_target/workflow_run. No manual workflow dispatched.
- barrot-ops is manual main-only with external-change confirmation; no Databricks/Kaggle action. coinbase-paper-trader is manual main-only with confirm=YES; no paper trade. deploy-a2a-worker requires confirm and separate secret-rotation confirmation; no deploy/rotation. sync-huggingface false guard; sync-self-hosted-brain false guard; XRP ingestion main-only/read-only.
- Connector permissions admin/maintain/push/pull/triage: overprivileged. Main protection details HTTP403; visible Fall Back ruleset disabled. `.config/gh/hosts.yml` present in all 17 affected PR tips with same blob SHA; contents not read; provider-side OAuth revocation unverified. Security-alert endpoints inaccessible; no absence inferred. Main push auto-publishes Pages; authorization absent.
### Prediction and merge decision
- Implemented: 47 source definitions/45 scheduled; read-only collector; SHA-256 receipt/hash-chain logic; point-in-time SQLite prototype; four baselines; chronological purge/embargo walk-forward; calibration/PSI drift; fail-closed Ed25519 forecast ledger.
- Outstanding: WORM/timestamp anchoring, replayable historical features, synchronized spot/L2/derivatives/flows/collateral, vintage-aware macro/event timeline, scenario/counter-hypothesis generation, production evaluator key, independent shadow outcomes and demonstrated out-of-sample lift.
- Forecast `NOT_ISSUED`. Run33 web observations have no Barrot raw-source receipts and are not model-eligible.
- #1661 remains open/draft, zero approvals. #1660: 972/972 paths represented, 949 identical/23 different/zero absent, three commits behind main; retain until successor merge. #1640: 244 identical/36 different; #1642: 0/7; #1643: 661/9. No source PR closed.
- **No merge.** Exact-head CI on the corrective commit is pending; approval, protection, credential, semantic-review, least-privilege and Pages authorization blockers remain.
- Next: verify exact-head full suite, wheel/installed mission, dependency audit and fail-closed gates on the Run33 corrective commit; continue semantic review; resolve security/approval/publication blockers. No forecast until all independent evidence gates pass.
- No merge, deployment, secret rotation/revocation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or PR closure.
## Run34 — 2026-11-11 20:18 UTC

XRP intelligence and prediction-engine mastery remain Barrot's highest-priority mission. Barrot V3 remains the protected execution, orchestration, safety and verification foundation.

### Repository and exact-head CI
- Main SHA: 84f28ee7755607236231545a14f3d093c1baaa85. Existing integration branch: integration/xrp-v3-unified-main-20261111; parent before this Run34 update: c857f637939be32f196d1a8268a8001443fe4d9d.
- 2,041 commits ahead / zero behind main; 1,017 changed files (44 workflows/973 other paths); complete integration tree 2,282 entries / 2,173 blobs; main tree 1,388 entries / 1,288 blobs.
- Open PR inventory: 374 (360 drafts, 14 non-drafts; 366 target main, 8 target other bases). PR #1661 remains open/draft with zero formal approvals/reviews/review threads. No merge.
- Last fully passing exact code head ed345e0: 3,449 passed, zero failed, eight subtests, 59.99% coverage; wheel and installed Barrot V3/XRP mission passed in CI 43069181417.
- Map-fixture head 570cd11: 3,447 passed, two failed. Run34 corrects the two reproduced fixture defects: #1660 disposition lacked RETAINED_UNTIL_SUCCESSOR_MERGE; exact-head failure classification lacked the required exact-head full-suite failed phrase.
- Current parent c857f637 CI 43091176535 ended startup_failure after a full-suite job failure and runner rerun. Core passed; dependency audit 43091176373 and fail-closed gate 43091176560 passed. Job logs returned empty. New exact-head full suite is mandatory on the Run34 commit; no parent result is reused.

### XRP market refresh — research-only, not model-eligible
- OKX XRP-USDT 1.0601 at 20:06:21.857 UTC; bid 1.0600/ask 1.0601; rolling 24h open 1.0641, high 1.0807, low 1.0472.
- Kraken XRP/USD last $1.06052, bid $1.06078/ask $1.06080, UTC-day open $1.05511; no provider event timestamp. Kraken USDT/USD midpoint 0.998945 normalizes OKX to $1.058982 versus Kraken midpoint $1.06079, about -0.1705%. Asynchronous, not executable arbitrage.
- Fuelmaps 20:00 UTC six-venue spot book: within 1% $14.1M bids/$11.0M asks; within 5% $25.2M/$15.2M; within 10% $33.5M/$17.7M. Binance and Bitget excluded; resting orders can be cancelled.
- Binance XRPUSDT perpetual 20:11:45.001 UTC: mark 1.06012118, index 1.06063033, funding +0.0057% per eight hours; OI not retrieved.
- TradRadar 19:05 UTC: OI $1.57B (-0.97%), funding +0.0045%/8h, liquidations $2.85M (longs $1.58M/shorts $1.27M), 79.7% long accounts. Liqwall 19:52 UTC: OI $1.16B (-0.2%), funding +0.0044%, liquidations $2.8M (longs $1.8M/shorts $1.1M), 75.2% Binance accounts long. Different universes; do not average.
- Deribit/OptimistFi 17:00 UTC: 30-day ATM IV 58.6%, 25-delta skew +2.4, put/call 0.55, Dec25 OI $47.8M.
- ETF disagreement: Alpha Finance five-of-five through Nov10, daily -$7.6M, seven-session -$18M, 30-session +$1.3M, cumulative +$1.71B. CryptoETF.today four-of-five partial -$6.9M, 30D +$115.2M, cumulative +$1.80B. Issuer-level reconciliation required; do not average.
- Prior TrackWhale seven-day snapshot: 501.72M inflows, 602.93M outflows, net -101.21M XRP; largest transfer 368.48M from an unknown wallet. Older tracked-transfer snapshot, not comprehensive exchange reserves.

### Evernorth actual capital — SEC primary evidence
- 18,463,753 of 23,000,000 public shares redeemed (80.2772%); 4,536,247 remain. Redemption payments $193,599,920; exact trust cash released to Pubco $47,564,385.
- SEC headline gross cash proceeds approximately $272.6M (approx. $224.6M private-placement cash + $48.0M trust release). Exact disclosed components $214,049,995 advance + $10,500,000 delayed + $47,564,385 trust = $272,114,380. Preserve headline and exact components; do not invent a missing source.
- $214,049,995 advance-funding cash purchased 84,365,876 XRP. In-kind XRP 388,910,554: Ripple direct 126,791,458; sponsor/RippleWorks 211,319,096; Ripple related party 50,000,000; advance 600,000; delayed 200,000. Total closing XRP approximately 473,276,430.
- SBI announced a $200M Evernorth commitment; SEC lists SBI-related advance-funding subscribers but does not itemize each allocation. Treat the $200M as included within the $214.05M pool, not additive; subscriber-level breakdown remains undisclosed.
- Separate $30M 4% PIK note due 2031 is parent-level debt, not equity/closing cash. Registered 11,499,992 public warrants at $11.50 could yield up to $132,249,908 gross if all exercised for cash; contingent, not raised. Selling-holder resale registration of 73,688,162 shares yields $0 for the company. Cantor ELOC had zero proceeds as of Nov9. Sponsor warrants are separate (239,653; up to $2.756M if all cash-exercised).
- Historical June30 financial scope corrected: Evernorth Holdings Inc. parent cash $97,745 and working-capital deficit $696.1M; Pathfinder Digital Assets LLC subsidiary cash $789,682 and deficit $3.7M. Keep entity labels separate.

### Institutional and identity research
- OCC effective trust-bank charters: Circle affiliate First National Digital Currency Bank, N.A. (July24, 2026); Ripple National Trust Bank (Oct26); Coinbase National Trust Company (Nov6). Trust-bank charters are not ordinary commercial deposit banks and do not prove first customer transaction, XRP collateral eligibility or XRP demand.
- Circle/Coinbase USDC distribution/revenue-sharing remains direct. PNC's limited USDC pilot uses Ethereum/Coinbase APIs and converts USDC to USD; not XRP settlement.
- Ripple/Coinbase RLUSD distribution spans XRPL, Base and Ethereum; Coinbase Global Exchange collateral support remains future scope, not verified live. RLUSD issuer remains Standard Custody & Trust Company; BNY remains primary reserve custodian pending verified transfer.
- SBI: SBI Holdings and SBI Shinsei Bank each invested $25M in Circle; SBI previously reported about 9% Ripple ownership in 2025 (not a current percentage); SBI Ripple Asia remains a 60/40 SBI/Ripple JV; SBI VC Trade distributes RLUSD/JPYSC.
- SBIC identities confirmed from official company profiles: Tokyo Small and Medium Business Investment & Consultation Co., Ltd. (East); Nagoya Small and Medium Business Investment & Consultation Co., Ltd. (Central); Osaka Small and Medium Business Investment & Consultation Co., Ltd. (West). Three separate regional companies, not SBI Holdings. SBIC West ChatGPT event was educational, not an OpenAI partnership.
- ASK: UCID 4640 is an Askcoin preview listing with zero reported supply; UCID 7105 is Permission Coin, a distinct LayerZero OFT on Base/Polygon. Neither has verified XRP/XRPL deployment. askcoin.net redirects to a HugeDomains profile; active project ownership is not established.
- “Actual capital” is not a standardized XRP metric. Exact “SBIC, ChatGPT SBIC” partnership remains unverified. Kamilah/Camilla YouTube channel ownership remains unverified; no videos attributed.

### Prediction engine, platforms and backlog
- Implemented: 47 public source definitions (43 hourly, two weekly CFTC, two non-commercial XRPL sources excluded); 45 scheduled; read-only collector; SHA-256 receipt/hash-chain logic; point-in-time SQLite prototype; four baselines; chronological purge/embargo walk-forward; calibration/PSI drift; fail-closed Ed25519 forecast ledger.
- Outstanding: independent WORM/timestamp anchor, replayable history, synchronized spot/L2/derivatives/flow/collateral history, vintage-aware macro/geopolitical events, scenario/counter-hypothesis engine, production evaluator key, independent shadow outcomes and demonstrated out-of-sample lift.
- Nine platforms: ChatGPT/GitHub API verified but connector overprivileged; Claude/Grok/Gemini/Codex unverified; Copilot no formal approval; Hugging Face BUILD_ERROR; Kaggle untested/no submission; Databricks HTTP403/no workspace write; LunaRoute declared canonical but endpoint auth/data flow unverified. No external-model transfer.
- 44 changed workflows reviewed (26 quarantined/disabled, 18 active); manual external workflows require specific confirmation and exact SHA; none dispatched. XRP collector is read-only and main-only; no successful main ingestion verified.
- #1661 blocked draft; #1660 superseded-source candidate (972 represented/949 identical/23 different); #1640 244 identical/36 different; #1642 seven different paths; #1643 661 identical/nine different. Unique/unreviewed: #1653 seven graph files; #1614 57 prediction files; #1611 eight ledger files; #1610 14 safety files; #1612 four security files; #1269 nine topology files; #1608 three research files. Preserve; no source PR closed.
- Merge blockers: exact-head full suite, draft/approvals, branch-protection API HTTP403, disabled fallback ruleset, overprivileged GitHub connector, 17 other PR tips still contain credential path (contents not read; provider-side revocation unverified), 973 non-workflow paths semantic review, and GitHub Pages auto-publication without authorization.
- Forecast NOT_ISSUED. No merge, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer or real-money action.


## Run35 — November 11, 2026: exact-head audit, XRP market, collateral, CFTC, actual capital and institutional network

### Mission and repository state

XRP intelligence/prediction mastery remains priority 1. Barrot V3 remains the protected execution, orchestration, safety and verification foundation.

- Main SHA: `84f28ee7755607236231545a14f3d093c1baaa85`.
- Integration branch: `integration/xrp-v3-unified-main-20261111`.
- Parent head inspected: `db934a4ee065fa7d45bb4fac4589a195903e09c7` (2,042 ahead, zero behind).
- PR #1661: open, draft, 1,018 changed files (44 workflows, 974 other paths), zero formal reviews/approvals/review threads.
- Complete trees retrieved: main 1,388 entries; integration 2,283 entries.
- Open PR inventory: 374 total, 360 drafts, 14 non-drafts.
- GitHub API access verified. Local clone not established; prior DNS resolution failure remains.

### Exact-head CI and workflow audit

The last verified full-suite pass is on parent `ed345e0`: 3,449 passed, zero failures, eight subtests, 59.99% coverage, 95.58 seconds. This is not the current head.

On `db934a4ee065fa7d45bb4fac4589a195903e09c7`, five exact-head CI/security runs remain queued with no jobs created: CI 43097485233; dependency audit 43097485242; fail-closed PR gate 43097485234; push dependency audit 43097479771; push fail-closed gate 43097479768. No current-head full-suite result is claimed.

The full-suite workflow executes `python -m pytest -q --tb=short --cov=barrot_agent --cov-report=term-missing` with a 53% floor. Coverage scope remains `barrot_agent`, not all repository packages. The core CI subset is separate.

All 44 changed workflow patches were rechecked. High-risk workflow bodies were reopened. The XRP collector is scheduled hourly and daily but gated to main; it was not executed from integration. Coinbase paper-trader, A2A deployment/secret-rotation, Databricks bundle, Hugging Face sync, self-hosted brain sync and Barrot ops were not triggered. Databricks/Hugging Face/self-hosted sync remain disabled; external operations remain gated.

Security: main protection summary is enabled, but detailed protection is HTTP 403; the visible fallback ruleset is disabled. Security-alert endpoints are inaccessible, so no alert-free claim is made. Connector permission metadata includes admin/maintain/push/pull/triage. `.config/gh/hosts.yml` is absent from current main/integration but remains present in 17 rechecked source PR tips; contents were not read and provider-side OAuth revocation remains unverified. Main pushes automatically publish GitHub Pages; publication authorization remains absent.

### Source PR reconciliation

- #1660: 972/972 changed paths represented; prior blob comparison 949 identical, 23 different. Superseded-source candidate; retain until successor merge and verification.
- #1643: 670/670 represented; 661 identical, 9 different.
- #1642: 7/7 represented; all seven blobs differ.
- #1640: 280/280 represented; 244 identical, 36 different.
- #1653: 53 paths, six unique graph paths; preserve.
- #1614: 27 paths, 24 identical and three different; preserve prediction content.
- #1610: seven paths, six identical and one different; preserve safety content.
- #1611, #1612 and #1269 have identical-path candidates but remain open pending successor merge and verification.

No source PR was closed. No new branch or PR was created.

### XRP market capture — approximately 20:41–21:05 UTC

**Spot:** OKX XRP-USDT event timestamp 20:41:21.368 UTC: last 1.0609, bid 1.0610, ask 1.0611, 24-hour high 1.0807, low 1.0472, volume 43.89M XRP. Kraken XRP/USD retrieval: last 1.0613, bid 1.06141, ask 1.06142, 24-hour volume 20.10M XRP; Kraken supplies no event timestamp. Kraken USDT/USD midpoint 0.998915 normalizes the OKX midpoint to approximately $1.05990, about 0.143% below Kraken's $1.061415 midpoint. Quotes are asynchronous; not executable arbitrage.

**Spot depth:** Fuelmaps' six-venue snapshot is 14:00 UTC (about seven hours old). Within ±1%: $13.7M bids/$11.8M asks; ±5%: $25.0M/$14.7M; ±10%: $33.8M/$16.1M. Binance and Bitget are excluded. These are resting orders, not committed liquidity.

**Perpetual depth:** Basis' Binance XRPUSDT perpetual snapshot at 20:31 UTC: mid 1.0606, spread 0.94 bps, 51% bid share within ±1%, $15.5M bids/$14.6M asks within ±1%. This is a derivatives book, not spot.

**Perpetual positioning disagreement:** TradRadar at 19:05 UTC reports $1.57B OI, down 0.97%, +0.0045% funding/8h, at least $2.85M liquidations (longs $1.58M, shorts $1.27M), and 79.7% long accounts. Liqwall at 20:52 UTC reports $1.17B OI, flat, +0.0067% average funding/8h, $2.7M liquidations (longs $1.7M, shorts $1.1M), and 75.2% of Binance accounts long. Provider venue/contract universes differ; do not average. Funding dispersion across TradRadar's seven exchanges ranges from -0.0052% to +0.0096% per eight hours.

**Options:** Deribit/Fuelmaps daily capture at 00:01 UTC: ATM IV 65.5% for Nov 12, 66.0% Nov 13, 61.6% Nov 20 and 59.0% Dec 25. The provider's historical check shows 20/928 daily settlements beyond its 3σ band (2.2%), versus 0.27% under a normal curve. Options-implied ranges are not forecasts; the tail result argues against Gaussian calibration.

**Tracked external exchange transfers:** TrackWhale at 20:52 UTC: seven-day inflows 178.61M XRP, outflows 243.39M, net -64.78M XRP, from 19 tracked transfers across 16 exchanges. This is a small tracked-transfer sample, not comprehensive exchange reserves or proof of accumulation.

**cbXRP:** Coinbase's displayed proof-of-reserves refresh at 21:05 (timezone not labelled) reports 152,087,932.36 XRP reserves against 152,085,685.83 cbXRP supply, an arithmetic excess of 2,246.53 XRP. This is issuer-published reserve information, not an independent audit or evidence of spot buying. Current Morpho cbXRP borrower-health/liquidation state was not retrieved; no current stress estimate is claimed.

**ETF flows:** The Block's 24-hour tracker reports -$10.4M and $1.1B AUM at 01:17 EST; Alpha Finance reports -$7.6M for Nov 10, -$18M over seven sessions, +$1.3M over 30 sessions and +$1.71B cumulative net inflows across five funds; XRP Desk shows a provisional Nov 11 -3.3K XRP across six funds; XRP Insights reports 1.405B XRP held across ten US/international products. Different universes and vintages; no averaging. Cumulative net inflows are not current AUM.

**CFTC:** Latest referenced positions are as of Nov 3, report released Nov 6. CME XRP (176740), Coinbase Nano XRP (176LM1) and Nano XRP Perp Style (176LM3) appear in the reporting set. Standard Coinbase XRP market code 176LM2 is listed as dropped from reporting this week; missing is not zero. Current position numbers were not independently re-downloaded in this run.

**Macro:** October 2026 CPI released Nov 10: headline +0.4% month over month; core +0.3%; September headline was +0.6%. Selected 12-month comparisons are unavailable where October 2025 data are missing. Secondary market snapshot: 2-year Treasury 4.731%, 10-year 4.988%, DXY 102.26. Hotter monthly inflation/higher yields are broad risk-premium inputs, not XRP-specific causation.

### Institutional and capital network

**Circle:** Q3 average USDC circulation $73.3B (+8% YoY), on-chain transaction volume $13.9T (+49%), revenue/reserve income $865M, net income $226M, adjusted EBITDA $317M. Reserve income was $658M, down 8%; other revenue included $182M ARC presale revenue. CPN reached $41.3B annualized TPV. Tazapay acquisition remains expected for 2027 subject to approvals. Circle announced a $100M Binance equity investment and expanded distribution partnership. USDC transaction volume is gross throughput, not unique capital inflow; adjusted EBITDA includes token presale revenue.

**Coinbase:** Q3 average USDC held $22B, up 49% YoY and approximately 30% of average USDC market cap; Coinbase says it captured approximately 50% of USDC economics over the prior year. Trading market share 10.7%. Coinbase's RLUSD launch across Prime/Exchange/Retail is live across XRPL, Base and Ethereum; Global Exchange collateral support was future scope at launch, not verified live.

**Ripple:** Company-reported 2026 exit annualized product revenue run rate $900M, $16T transactions enabled across all products in 2025, 85 licenses, 1,700+ institutions/corporates/enterprises, 60+ payout markets and RLUSD market cap $2.6B. The $16T is not XRP settlement volume. Ripple/Robinhood announced RLUSD on Robinhood Chain and Bitstamp, XRPL institutional settlement, Ripple Treasury and Prime integrations. BNY/Ripple expanded custody and XRPL trade-finance work with C2FO; Privy (Stripe) supports XRP/RLUSD and other XRPL assets in programmable wallets. No corresponding XRP volumes disclosed.

**SBI:** Official material identifies an approximately 9% Ripple equity stake as a dated disclosed percentage, not a current audited cap table. SBI Ripple Asia is 60% SBI/40% Ripple; SBI Remit says XRP has served as a bridge currency in a Japan-origin remittance service since 2021, but no current XRP settlement volume is disclosed. SBI VC Trade launched JFSA-approved RLUSD in Japan on June 24. SBI Holdings and SBI Shinsei Bank invested $25M each in Circle. SBI's $200M Evernorth commitment is included in the $214.05M advance-funding pool, not additive. SBI announced $100M into Erebor Bank on Nov 2; Erebor supports stablecoin deposits/withdrawals but no XRP integration was disclosed. SBI separately invested $50M in Startale. SMBC took 5% capital participation in SBI Startale Marketing; the amount is undisclosed. SBI/Startale/BlackRock's tokenized-MMF/JPYSC linkage is an MOU. Open Standard's JPYSC/OUSD work is exploratory, not production. JPYSC is issued by SBI Shinsei Trust Bank, developed with Startale and distributed by SBI VC Trade; Nov 2 handled balance was ¥30B and lending balance ¥10B inside SBI VC Trade, not public-chain supply or XRP liquidity.

**Evernorth — actual capital reconciliation:** SEC Form 424B3 reports 18,463,753 public shares redeemed (80.3%), about $193.6M redemption payments and $47.564M released from the trust account. Gross cash proceeds were about $272.6M before expenses: $224.6M private-placement investments plus $48.0M trust release. Investors also contributed 388.911M XRP in kind. The $214.05M advance-funding cash and 600,000 XRP were separate subscription consideration; the $214.05M cash was used to buy 84.366M XRP. The 261.919M XRP subscription reference is part of the in-kind/placement structure, not additive to the 388.911M total in-kind contribution. Evernorth held about 473M XRP as of Oct 9.

Entity-level distinction: Evernorth Holdings parent cash was $97,745, working-capital deficit about $696.1M, accumulated deficit $340.85M, six-month operating loss $265.59M and net loss $188.13M; net loss included $264.15M non-cash digital-asset impairment and $77.48M non-cash fair-value gain on refundable investor advances. Pathfinder subsidiary cash was $789,682, accumulated deficit $3.126M, operating loss $2.149M, net loss $2.218M and operating cash used $2.138M. Pathfinder's Ripple facility was raised to $10M and $9.7M drawn as of Oct 7; repayment terms require five business days after closing or demand, but actual repayment status is not disclosed. Parent's separate $1M Evernorth facility was undrawn at June 30. A $30M 4% PIK note funded Oct 12 is debt, not proof of XRP purchases. Cantor ELOC proceeds were zero as of the prospectus; selling-holder resales provide no company proceeds. "Actual capital" is not a standardized metric; cash, in-kind XRP, debt, facilities, ELOC capacity and resales must remain separate.

### Identity and exact-phrase research

Japan's SBIC entities are separate statutory regional companies: Tokyo (SBIC East), Nagoya (SBIC Central) and Osaka (SBIC West), established under the SME Investment & Consultation Companies Act. They are not SBI Holdings. SBIC training/seminar references to ChatGPT are educational activity, not OpenAI partnership evidence. Exact phrase "SBIC, ChatGPT SBIC" remains unmatched at primary-source level.

"ASK Coin" is ambiguous: Askcoin UCID 4640 is a legacy Q&A-chain candidate with a CMC preview/zero supply; Permission Coin UCID 7105 is a separate LayerZero OFT token on Base/Polygon; AskToken/AskChain is another candidate. No XRPL integration was verified. "Actual capital" is commentary, not a standardized XRP metric; the SEC capital stack is the grounded reconciliation.

Kamilah/Camilla Stevenson YouTube ownership remains unverified. Candidate handles include @drkamilahstevenson and @KamilahStevensonXrpStocks, with spelling variants and no first-party cross-link to the official profile. No video inventory was attributed.

### Prediction and platform readiness

Implemented on integration: 47 unique source IDs (43 ordinary scheduled; two weekly CFTC endpoints added on capture windows; two XRPL node endpoints excluded by default), read-only collector, SHA-256 receipts/hash-chain logic, SQLite point-in-time prototype, four baselines, chronological walk-forward with purge/embargo, temporal calibration, PSI drift and fail-closed Ed25519 evaluator-attestation ledger.

Not production-ready: independent WORM/trusted timestamp anchoring, replayable feature-store reconstruction, synchronized historical spot/L2/derivatives/flows/collateral, vintage-aware macro/geopolitical timeline, scenario/counter-hypothesis generation, production evaluator key, sufficient independent shadow outcomes and demonstrated out-of-sample lift. Artifact/cache retention is not WORM. Run35 web observations have not entered Barrot's raw-source receipt pipeline and are not model-eligible.

Nine-platform map: ChatGPT/GitHub API authenticated but overprivileged; Claude/Grok/Gemini/Codex authentication/data flow unverified; Copilot has no formal approval; Hugging Face BUILD_ERROR; Kaggle untested/no submission; Databricks HTTP 403/no workspace write; LunaRoute declared canonical but endpoint authentication/data flow unverified. No external-model data transfer.

Forecast status remains `NOT_ISSUED`. No directional forecast, paper trade or real-money action.

### Decision and next action

PR #1661 remains blocked. The current full-suite and security runs are queued with no jobs created; the last full-suite pass is on a different parent. PR remains draft with no formal approvals; branch-protection requirements, least-privilege remediation, credential-path/provider revocation evidence, Pages authorization and 974-path semantic review remain incomplete. No merge, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external-model transfer, funds transfer, paper trade, force-push, history rewrite or source-PR closure occurred.

Next action: obtain exact-head full-suite/security results on the latest integration commit, then resolve least-privilege, branch-protection, credential and Pages authorization blockers before semantic reconciliation and any merge.


## Run35b — exact-head CI and CFTC position refresh

### Exact-head verification

The Run35 code head `bd5a7e3a9ec4e3b1e3bae2c1a6b6cccdf16b5868` completed exact-head verification:

- Full repository suite: **3,449 passed, zero failures, eight subtests**.
- Coverage: **59.99%** against the configured 53% floor; scope is `barrot_agent`, not every repository package.
- Duration: 95.58 seconds.
- Wheel build and installed primary-mission verification passed.
- Dependency audit: six manifests, no known vulnerabilities.
- PR and push fail-closed gates passed.

Exact evidence: [CI 43101310410](https://github.com/Barrot-Agent/B-Agent/actions/runs/43101310410) · [Dependency audit 43101310461](https://github.com/Barrot-Agent/B-Agent/actions/runs/43101310461) · [PR fail-closed 43101310416](https://github.com/Barrot-Agent/B-Agent/actions/runs/43101310416) · [Push audit 43101297331](https://github.com/Barrot-Agent/B-Agent/actions/runs/43101297331) · [Push fail-closed 43101297353](https://github.com/Barrot-Agent/B-Agent/actions/runs/43101297353).

The full-suite result is verified on `bd5a7e3`. Any subsequent documentation-only handoff commit is a new Git head and requires its own exact-head CI before merge.

### CFTC correction and contract-equivalent positioning

The official CFTC Traders in Financial Futures report for positions as of November 3 (released November 6) contains:

| Market | Code | OI contracts | Weekly change | XRP per contract | XRP-equivalent OI |
|---|---|---:|---:|---:|---:|
| CME XRP | 176740 | 7,216 | -845 | 50,000 | 360.800M |
| Coinbase Nano XRP | 176LM1 | 32,505 | -32,864 | 500 | 16.2525M |
| Coinbase Nano XRP Perp Style | 176LM3 | 38,392 | -465 | 500 | 19.196M |

Reported markets total approximately **396.249M XRP-equivalent**, down approximately **58.915M (12.94%)** from the preceding report. This is regulated futures contract exposure, not spot holdings, cash capital or total XRP derivatives open interest. The large Nano XRP weekly OI decline requires contract-roll/expiration investigation before interpreting it as position liquidation.

The standard Coinbase XRP market code `176LM2` is explicitly listed as dropped from reporting this week. CFTC's market-summary methodology includes contracts with 20 or more traders meeting reportable-position thresholds. A missing row is an observability gap, not zero open interest.

Primary sources: [CFTC weekly TFF data](https://www.cftc.gov/dea/newcot/FinFutWk.txt) · [CFTC reporting methodology](https://www.cftc.gov/MarketReports/index.htm).

### Supplementary spot and collateral refresh

At 21:11:32.174 UTC, OKX XRP-USDT was 1.0670 (bid 1.0668 / ask 1.0669). Kraken XRP/USD was 1.06682 (bid 1.06689 / ask 1.06690), but Kraken did not provide an event timestamp. After USDT normalization, the asynchronous midpoint difference was approximately -0.113%; not executable arbitrage.

Coinbase's proof-of-reserves page displayed a 21:05 refresh (timezone unspecified): 152,087,932.36 XRP reserves versus 152,085,685.83 cbXRP supply, an arithmetic excess of 2,246.53 XRP. This remains issuer-published information, not an independent audit. Current Morpho cbXRP borrower health and liquidation exposure remain unverified.

[Run35b structured artifact](https://github.com/Barrot-Agent/B-Agent/blob/integration/xrp-v3-unified-main-20261111/research/xrp_intelligence/20261111T211755Z-run35b-exact-head-ci-cftc-position-and-spot-refresh.json).

### Decision

The tested code head passed the full suite, dependency audit and fail-closed gates. PR #1661 nevertheless remains blocked: it is draft, formal approvals are absent, branch-protection requirements are not visible, connector permissions are overprivileged, credential-path/provider revocation evidence is incomplete, GitHub Pages publication is unauthorized and 974 non-workflow paths remain under semantic review. No merge or external action was performed.


## Run35c — exact-head verification, ETF-flow reconciliation and public-interface safety

### Exact-head verification

Code/evidence head `831a29f98f5b34a6f80f92109172fee0fce7fe9e` passed the complete repository suite on its exact SHA:

- Full suite: **3,449 passed, zero failures, eight subtests**.
- Inclusive coverage: **59.99%** against a 53% floor; coverage scope is `barrot_agent`, not every repository package.
- Duration: 96.83 seconds.
- Core tests, wheel build and installed primary-mission verification passed.
- Dependency audit: six manifests, zero known vulnerabilities.
- PR and push fail-closed gates passed.

Evidence: [Full CI 43102180175](https://github.com/Barrot-Agent/B-Agent/actions/runs/43102180175) · [Dependency audit 43102180190](https://github.com/Barrot-Agent/B-Agent/actions/runs/43102180190) · [PR fail-closed 43102180108](https://github.com/Barrot-Agent/B-Agent/actions/runs/43102180108) · [Push dependency audit 43102172142](https://github.com/Barrot-Agent/B-Agent/actions/runs/43102172142) · [Push fail-closed 43102172133](https://github.com/Barrot-Agent/B-Agent/actions/runs/43102172133).

Packaging warnings remain: deprecated `project.license` TOML table and two packages absent from explicit package configuration. The primary mission JSON was nevertheless included in the wheel and loaded after installation. Coverage beyond `barrot_agent` remains outstanding.

### ETF-flow reconciliation and correction

The direct source pages resolve most of the Nov10 difference:

- Alpha Finance covers five US spot funds and reports **-$7.6M** on Nov10. Its breakdown is GXRP -$7.2M, XRPC -$449.8K and zero for XRP, XRPZ and TOXR.
- XRP Insights reports seven products (six US spot funds plus BITW), **1.18597B XRP holdings**, **$1.25962B AUM**, and Nov10 net flow of **-27,000 XRP**. Crucially, it explicitly excludes GXRP from flow totals while a data gap is corrected, although GXRP holdings remain in total holdings.
- The difference is therefore largely explained by Alpha including GXRP's -$7.2M while XRP Insights omits GXRP from flow calculations. The remaining difference is not independently reconciled. Do not average.
- The Block's -$10.4M 24-hour snapshot matches Alpha's Nov9 -$10.4M session; do not assign it to Nov10 without a verified window.
- The earlier 1.405B XRP/ten-product figure was misattributed to XRP Insights and is withdrawn; no source for that exact figure was verified.

Sources: [Alpha Finance](https://alphafinance.io/etf/xrp/) · [XRP Insights](https://xrp-insights.com/).

### Public-interface safety reconciliation

Main `web/latest_signal.json` is a stale Oct29 sentiment-only artifact (score 44, confidence 0.0, provider failures). Main `web/signals.html` maps only exact scores 1/0/-1 to BUY/NULL/SELL; score 44 renders NULL. The legacy page still has a $9.99/month checkout. It is not currently issuing a directional forecast.

Integration replaces this with schema-v2 `NOT_ISSUED`, marks the old sentiment artifact stale/descriptive-only/model-ineligible, and removes the checkout. Main Pages publication is automatic on push; authorization remains absent. No merge was performed.

### Kamilah channel attribution

The integration research file contains ten candidate video references, but the candidate channel handle is not first-party/platform verified. The person identity is confirmed; channel identity is only probable. No creator video inventory was attributed. Candidate references remain quarantined pending channel ownership evidence.

### Current repository and merge decision

At tested head `831a29f`: main `84f28ee`; 2,044 ahead/zero behind; tree 2,285 entries; PR #1661 open/draft, 1,020 changed files (44 workflows/976 other paths); 374 open PRs (360 drafts/14 non-drafts). PR API reports mergeable=true/clean, but it has zero formal reviews/approvals. Branch-protection details remain HTTP 403, connector permissions remain overprivileged, credential-path/provider revocation evidence is incomplete, Pages authorization is absent and 976 non-workflow paths require semantic review.

This Run35c update is documentation/research only. Its new commit is a new Git head; exact-head CI must be observed on that tip before any merge. No merge, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, force-push, history rewrite or PR closure occurred.

Next: verify exact-head CI on the Run35c documentation commit, then resolve least-privilege, branch protection, credential remediation, Pages authorization and semantic review. Keep forecast issuance disabled.

## Run36 — 2026-11-11 21:28 UTC — exact-head CI, current market, institutional capital and CFTC reconciliation

Mission priority 1 remains XRP intelligence and measured prediction-engine mastery. Barrot V3 remains the protected execution, orchestration, safety and verification foundation.

### Repository state and exact-head verification

- Main SHA: \`84f28ee7755607236231545a14f3d093c1baaa85\`.
- Integration branch: \`integration/xrp-v3-unified-main-20261111\`.
- Code head tested before Run36 documentation commits: \`601fb36cd2185843ab8592afc027a680946f7e85\` (2,045 ahead / 0 behind main).
- PR #1661: open, draft, mergeable/clean; 1,021 changed files (44 workflow files / 977 other paths), 260,149 additions, 4,362 deletions; zero formal reviews, approvals or review threads.
- Complete recursive trees: main 1,388 entries; integration 2,286 entries.
- Open PR inventory: 374 (360 drafts / 14 non-drafts).
- [Exact-head full CI 43102911776](https://github.com/Barrot-Agent/B-Agent/actions/runs/43102911776): **3,449 passed, zero failures, eight subtests, 59.99% coverage** on \`601fb36\`; full-suite and core jobs passed. Wheel build and installed primary mission verification passed.
- [Dependency audit 43102911840](https://github.com/Barrot-Agent/B-Agent/actions/runs/43102911840): six manifests audited, zero known vulnerabilities reported.
- [Fail-closed PR gate 43102911873](https://github.com/Barrot-Agent/B-Agent/actions/runs/43102911873): passed.
- Main CI [42944864014](https://github.com/Barrot-Agent/B-Agent/actions/runs/42944864014) passed 718 tests/eight subtests on main SHA \`84f28ee\`. Main Cross Analysis [43100331823](https://github.com/Barrot-Agent/B-Agent/actions/runs/43100331823) succeeded. Main Pages build [42944862534](https://github.com/Barrot-Agent/B-Agent/actions/runs/42944862534) succeeded as an automatic push-triggered side effect; no new publication is authorized.
- Main Pillars Consistency Check [43025487840](https://github.com/Barrot-Agent/B-Agent/actions/runs/43025487840) failed because GitHub App credentials were unavailable, Databricks returned HTTP 403 and Hugging Face returned BUILD_ERROR. This is platform-health failure, not the main Python CI result.
- Coverage floor remains 53%, below the prior 70% target. The 59.99% report covers \`barrot_agent\` Python packages; some major modules still have low/zero coverage. Raise the floor as coverage expands.
- The Run36 research artifact was committed at [93967631](https://github.com/Barrot-Agent/B-Agent/commit/93967631fd7e9813415efc114dbc905f67171ff2). This handoff/map update is also documentation-only. Do not reuse the \`601fb36\` test result as verification of the later documentation commits; verify the final Run36 branch head separately.

### Current XRP market — public observations, not model-eligible

Capture windows are asynchronous; raw exchange observations are not synchronized.

**Spot**
- OKX XRP-USDT at 21:11:32.174 UTC: last 1.0670, bid 1.0668, ask 1.0669; 24h high 1.0807, low 1.0472, open 1.0623; volume 43.48M XRP.
- Kraken XRP/USD: last $1.06682, bid $1.06689, ask $1.06690; 24h high $1.07953, low $1.04582, open $1.05511; volume 19.83M XRP. Kraken supplied no provider event timestamp.
- Kraken USDT/USD: 0.99892. USDT-normalized OKX midpoint $1.06570 versus Kraken midpoint $1.066895, an asynchronous difference of approximately -0.112%. Not an executable arbitrage signal.

**Order book**
- Basis Binance XRPUSDT perpetual snapshot 20:31 UTC (not spot): mid 1.0606, 0.94bp spread, 1,000 displayed levels per side; $42.5M bids / $32.2M asks across displayed depth; within 0.5% approximately $19.0M; within 1% $15.5M bids / $14.6M asks; within 2% $23.9M / $20.4M. Approximately 40 minutes older than the spot capture. Resting orders can be cancelled.

**Derivatives disagreement**
- Liqwall 21:22 UTC: OI $1.17B, +0.6% 24h; average funding +0.0079% per eight hours; 75% Binance accounts long; rolling 24h liquidations $2.8M ($1.7M long / $1.1M short).
- TradRadar 19:05 UTC: OI $1.57B, -0.97% 24h; funding +0.0045% per eight hours; long-account share 79.7%; at least $2.85M liquidations ($1.58M long / $1.27M short).
- The two providers disagree on OI level and direction because venue/contract universes differ. Funding is positive in both. Do not average.

**Options**
- OptimistFi/Deribit 20:00 UTC: 30-day ATM IV 57.7%, 25-delta skew +1.2 points, put/call ratio 0.55, December 25 OI $47.5M. Near-expiry puts remain richer than the aggregate 30-day skew.

**ETF flows**
- Alpha Finance, five-fund universe through November 10: daily net outflow $7.6M; seven-session outflow $18.0M; 30-session net inflow $1.3M; cumulative net inflow $1.71B; net assets $1.19B. GXRP accounted for approximately $7.2M of the November 10 outflow.
- CryptoETF.today T+1 snapshot reports November 10 outflow $6.9M, published November 11 at 05:47 UTC; its accessible page did not expose an XRP fund-by-fund breakdown.
- XRP Insights tracks six US spot funds plus BITW for holdings: 1.18597B XRP and $1.25962B AUM. Its flow calculation excludes GXRP while a data gap is corrected. Holdings are not cash inflows.
- These series have different fund universes and vintages. Do not average them.

**Exchange wallets**
- XRP Insights tracks 22.33B XRP across 701 wallets / 24 exchanges. Same-wallet balance changed +1.3M XRP over seven days and -155.7M over 30 days.
- Upbit 6.47B; Coinbase 5.80B (including approximately 149.6M cbXRP reserve on Base, not customer spot XRP); Binance 2.69B.
- Cold storage is included and approximately 39.8% of tracked balances lack hot/cold classification. This is not tradable float or comprehensive exchange-reserve accounting.

**CFTC TFF — important contract-scope correction**
The November 3, 2026 report (released November 6) contains three XRP futures products:
- CME XRP, code 176740: 7,216 contracts × 50,000 XRP = 360.800M XRP-equivalent.
- Coinbase Nano XRP, code 176LM1: 32,505 × 500 = 16.2525M XRP-equivalent.
- Coinbase Nano XRP Perp Style, code 176LM3: 38,392 × 500 = 19.196M XRP-equivalent.
- Total: 396.2485M XRP-equivalent, down 12.94% from approximately 455.163M the preceding week.
- The CFTC lists code 176LM2 (XRP - Coinbase Derivatives) as dropped from reporting this week. Codes 176LM1 and 176LM3 remain reported. A dropped contract is a reporting gap, not zero open interest. Earlier shorthand that the Coinbase XRP market was simply “absent” was incomplete; the two Nano contracts remain in the report.

**On-chain / collateral / RWA**
- XRP Insights headline XRPL RWA value $4.33B includes approximately $4.06B registry notional; only $276M is described as distributed transferable value. Do not treat registry notional as transferable capital.
- XRP Insights on-chain RLUSD tracker reports $2.71B supply (about $905.8M on XRPL and $1.81B on Ethereum). Ripple issuer transparency on November 5 reported $2.6329B circulating and $2.748B reserves. Preserve the different dates and coverage.
- Evernorth wallet tracker attributes 103.13M XRP to 13 tracked wallets; 370.35M XRP moved outside that attribution set by October 22. This is not proof of sale or exchange deposit.

### Evernorth: “actual capital” and entity-scope correction

Primary filing: [SEC Form 424B3, November 9, 2026](https://www.sec.gov/Archives/edgar/data/2092592/000162828026072223/evernorth-424b3.htm).

**Closing capital**
- SEC filing reports approximately $272.6M gross cash proceeds: $224.6M private-placement cash plus approximately $48.0M released from the trust after redemptions. This is not all XRP purchase cash.
- 18,463,753 of 23,000,000 public shares were redeemed (approximately 80.3%); trust cash released was $47,564,385.
- $214.05M of advance-funding cash was used to purchase 84,365,876 XRP at a disclosed average price of approximately $2.53657.
- Investors contributed 388,910,554 XRP in kind. Total closing XRP was approximately 473,276,430.
- A $30M PIK convertible note at 4% due 2031 is debt, not equity cash.
- The $10M Company Facility had $6.6M drawn as of June 30; repayment is due within five business days after closing or earlier on five business days' demand notice. A separate Evernorth Facility had no borrowing as of June 30.
- Cantor ELOC capacity is up to 5,218,935 shares at 97% VWAP; the $521,893.50 commitment fee is not share-purchase proceeds. No ELOC purchase proceeds are identified in the filing. Up to 9,283,847 Pubco warrant shares at an $11.50 strike are contingent, not cash raised. Selling-holder resales yield $0 to the company.
- Earlier rounded company descriptions of approximately $300M cash proceeds are superseded for precise reconciliation by the later SEC figure of $272.6M gross cash proceeds.

**Corrected pre-close entity attribution (June 30, 2026)**
Both entities were Ripple-owned before the October 9 business-combination closing. Pathfinder became Evernorth's wholly owned subsidiary at closing. The prior Run32 note reversed their figures; this SEC-table correction is authoritative.

- Evernorth Holdings Inc. (then Ripple-owned Pubco): cash $97,745; current assets $174,157; current liabilities $696,227,692; calculated working-capital deficit approximately $696.054M; accumulated deficit $340.852M; six-month net loss $188.135M; operating loss $265.594M; operating cash used $1.330M. The $188.135M net loss included $264.146M non-cash digital-asset impairment and a $77.477M fair-value gain on refundable investor advances; it is not equivalent to cash burn.
- Pathfinder Digital Assets LLC (then a separate Ripple-owned operational entity): cash $789,682; current assets $3.906M; current liabilities $7.584M; calculated working-capital deficit approximately $3.679M; accumulated deficit $3.126M; six-month net loss $2.218M; operating loss $2.149M; operating cash used $2.138M.
- After the October 9 closing, Pathfinder became Evernorth's wholly owned subsidiary and Evernorth became the public parent. Do not label the June 30 standalone balances as post-close parent/subsidiary balances.

The phrase “actual capital” is not a standardized XRP metric. Keep cash proceeds, cash used to buy XRP, in-kind XRP, debt, credit facilities, contingent ELOC/warrants and secondary resales separate.

### Institutional network: Coinbase, Circle, Ripple and SBI

**Circle**
- Circle's Q3 2026 SEC filing reports average USDC circulation $73.3B, on-chain transaction volume $13.9T, total revenue/reserve income $865M, net income $226M and adjusted EBITDA $317M.
- ARC presale revenue of $181.8M was recognized in Q3; total ARC presale gross proceeds were reported at approximately $242.2M. Do not treat that as recurring USDC reserve income.
- Reserve return rate was 3.5% versus 4.2% in the prior-year comparison. Circle says rates affect reserve returns, while USDC circulation/customer behavior is uncertain.
- Coinbase distribution costs were $331.3M in Q3 and $986.6M for the first nine months. The SEC filing describes the formula: Coinbase allocations depend on USDC held on its platform after issuer retention and half the remaining broader ecosystem allocation after approved third-party participants.
- Circle's affiliate First National Digital Currency Bank, N.A. has an effective OCC trust-bank charter dated July 24, 2026; it is not an ordinary deposit bank.
- Circle announced a $100M Binance equity investment and a five-year USDC commercial agreement. SBI Holdings and SBI Shinsei Bank separately invested $25M each in Circle ($50M combined).

**Coinbase**
- Coinbase National Trust Company has an effective OCC trust-bank charter dated November 6, 2026; trust/custody authority is not an ordinary deposit-bank charter.
- Coinbase Q3 reporting: average USDC held approximately $22B, up 49% year over year; reported crypto trading market share 10.7%; Coinbase says it captures approximately 50% of USDC economics.
- Coinbase's RLUSD distribution relationship is live across Prime, Exchange and Retail on XRPL, Base and Ethereum. Coinbase Global Exchange collateral support was described as future scope, not verified live.
- cbXRP reserve balances are wrapped-asset backing, not customer spot XRP purchases.

**Ripple**
- Ripple National Trust Bank's OCC charter became effective October 26, 2026. Approved reserve-management, collateral-trustee and custody activities remain subject to operational opening.
- Standard Custody remains RLUSD issuer; BNY remains primary reserve custodian. A new charter does not prove custody migration or XRP demand.
- Standard Chartered RLUSD custody on XRPL is reported live through its DIFC branch; the LMAX collateral integration remains planned.
- Ripple's reported $900M annualized product-revenue run rate and $16T product transaction volume are company-wide product metrics, not XRP-specific settlement volume.

**SBI**
- SBI Holdings' approximately 9% Ripple stake is a historical FY2024 Q3 presentation figure, not a refreshed current ownership percentage.
- SBI Holdings and SBI Shinsei Bank invested $25M each in Circle.
- SMBC Group took a 5% capital participation in SBI Startale Marketing; the investment amount was not disclosed.
- SBI/Startale joined Open Standard. The reported 140+ participant ecosystem includes major payment/financial firms; JPYSC/OUSD interoperability remains exploratory/PoC, not a live XRP corridor.
- SBI Shinsei Trust Bank issues JPYSC; SBI VC Trade distributes JPYSC and RLUSD in Japan. JPYSC reserves/lending are not XRP collateral.
- SBI Remit/SBI Ripple Asia announced XRP-bridge remittances to the Philippines, Vietnam and Indonesia in 2023; current corridor volumes were not disclosed.
- SBI Holdings' ChatGPT Enterprise deployment and Anthropic/Claude collaboration are separate corporate AI initiatives, not an SBIC-OpenAI partnership.

**Other payment rails**
- PNC/Coinbase/Circle's limited pilot uses USDC on Ethereum and automatically converts to USD deposits; not XRP settlement.
- Circle's Visa Direct USDC deployment, Samsung Wallet USDC capability and Arc network are competing stablecoin/payment infrastructure, not evidence of XRP buying.

### Regulation, macro and geopolitics

- BLS October 2026 CPI: headline +0.4% month over month; core +0.3%. Twelve-month changes were unavailable for many series because comparable October 2025 data were missing after the federal shutdown. Do not impute.
- Reuters November 11: DXY near 102.90, USDJPY near 159.84, approximately 87% market pricing for a 25bp December Fed hike and 13.5% for a 50bp move; oil rose over 2% amid Iran-war risk and broader tariff/AI-spending concerns.
- FSB's November 11 Türkiye peer review recommended stronger crypto/stablecoin supervision, monitoring and cross-border cooperation.
- OCC trust-bank charters, CFTC contract reporting and Japan's RLUSD/JYSC classifications are separate regulatory regimes. No new XRP-specific court classification was established in Run36.

### Identity research

- SBIC East/Tokyo, SBIC Central/Nagoya and SBIC West/Osaka are three separate Japanese regional SME investment/consultation companies, not SBI Holdings. Tokyo SBIC ChatGPT training and SBIC West seminars are educational events, not an OpenAI partnership.
- “ASK Coin” remains ambiguous: Permission Coin ASK is an official LayerZero OFT on Base/Polygon; separate Askcoin UCID 4640 is a preview listing with no verified issuer/contract. Neither has a verified XRPL deployment. Permission app reward balances are distinct from the on-chain token; the A2A exchange feature is planned, not live.
- “Actual capital” has no verified standardized XRP metric; use the SEC categories above.
- No primary-source match for the exact phrase “SBIC, ChatGPT SBIC”.
- Dr. Kamilah Stevenson identity is confirmed by her first-party site. The candidate YouTube handle is not linked from that site or otherwise first-party/platform verified. No videos are attributed. Camilla and Kamilah are not assumed to be the same person.

### Prediction readiness and provenance

- 47 public source definitions: 43 hourly, two weekly CFTC, two XRPL-node sources excluded by default; 45 scheduled.
- XRP collector schedule is hourly at minute 3 plus a daily 00:15 UTC backup. Workflow is main-only and read-only. Main does not yet contain the collector; no successful main ingestion is verified.
- Collector uses host allowlists, redirect rejection, 15-second timeout, 10MiB response cap and source-specific cache-age checks.
- SHA-256 raw receipt/hash-chain code exists; raw receipt retention is 90 days in Actions artifacts. No independent WORM storage or trusted timestamp anchor.
- Point-in-time SQLite feature-store prototype; per-run snapshots 7 days and daily snapshots 90 days. Historical replay/reconstruction is not production-proven.
- Four baselines: naive class prior, momentum sign, mean-reversion sign and Gaussian volatility normal.
- Chronological walk-forward with horizon purge/embargo, calibration and PSI drift diagnostics are implemented. Full serial-dependence/shared-source correction remains incomplete.
- Full scenario/counter-hypothesis generator is not implemented. The current up/flat/down classes are not full scenario analysis.
- Ed25519 evaluator-attestation contract exists; production evaluator key and independent shadow outcomes are missing.
- Readiness gates require at least 100 out-of-sample samples, 100 independent shadow outcomes, ten non-overlapping horizon windows, two independent source groups, weighted calibration error no greater than 0.05, better Brier/log loss than all four baselines and trusted Ed25519 attestation.
- Run36 web/API observations were not ingested through Barrot's raw-source receipt pipeline. No SHA-256 receipt is claimed; all are excluded from model features.

**Forecast: \`NOT_ISSUED\`.** No directional forecast, paper trade or real-money action occurred.

### Backlog, security and merge decision

- PR #1661: blocked; sole consolidated integration PR. It remains draft with zero formal approvals.
- #1660: all 972 source paths represented in #1661; 949 identical blobs, 23 different. Retain pending semantic review and verified successor merge.
- #1643: all 670 paths represented; 661 identical, nine different. Retain pending semantic review and verified successor merge.
- #1642: seven paths represented, all seven blobs different. Not an exact duplicate.
- #1640: 280 paths represented, 244 identical and 36 different.
- Preserve unique/unreviewed work: #1653 (three absent paths), #1614 (26 absent paths), #1611 (one absent), #1610 (two absent safety paths), #1612 (three differing blobs), #1608 (two absent C2FO/Evernorth paths).
- \`.config/gh/hosts.yml\` remains present in 17 affected open-PR branch tips; absent from main and integration. Contents were not read. Provider-side OAuth revocation is not independently verified.
- GitHub connector reports admin/maintain/push/pull/triage: overprivileged. Main protection endpoint returns HTTP 403; visible fallback ruleset is disabled. Security alert settings are not exposed; no absence is inferred.
- Main GitHub Pages publication is automatic on push and remains unauthorized. No workflow was dispatched.
- All 44 changed workflow files remain under the previous full audit (26 quarantined/disabled, 18 active); Run36 rechecked the critical CI, collector, merge, sync and paper-trader workflows. No external workflow was dispatched.
- No source PR was closed.

**Decision: no merge.** Exact-head CI and dependency gates passed on \`601fb36\`, but PR #1661 remains draft, approvals are absent, branch-protection requirements are not visible, least-privilege and credential remediation remain unresolved, 977 non-workflow paths need semantic review, and GitHub Pages publication is not authorized. The Run36 documentation-only commits require their own exact-head CI.

Next actions:
1. Verify exact-head CI on the final Run36 documentation-only branch head.
2. Continue semantic review of the 977 non-workflow paths.
3. Resolve branch-protection/approval visibility, least privilege, credential-owner revocation evidence and Pages authorization.
4. Implement independent WORM/timestamp anchoring, replayable features and scenario generation.
5. Build synchronized historical spot/L2/derivatives/flows/collateral and vintage-aware macro/event datasets.
6. Keep forecasts disabled until independent shadow and out-of-sample gates pass.

No merge, deployment, secret rotation/revocation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or source PR closure occurred.


## Run37 — 2026-11-11 21:58 UTC

- Mission priority 1: XRP intelligence and measured prediction-engine mastery; preserve Barrot V3 as execution, orchestration, safety and verification foundation.
- Repository inspection: main `84f28ee7755607236231545a14f3d093c1baaa85`; integration branch `integration/xrp-v3-unified-main-20261111`; current head before repair `043909f3a059b0ab0e2a48e110345a3e4244cd41`; compare reports 2,049 ahead / 0 behind; complete trees main 1,388 entries and integration 2,287 entries; 374 open PRs (360 drafts / 14 non-drafts); PR #1661 has 1,022 changed files (44 workflows / 978 other paths), remains open/draft/mergeable, with zero formal reviews/approvals/review threads.
- Exact-head CI 43107011650 on `043909f3a059b0ab0e2a48e110345a3e4244cd41`: full suite **3,426 passed / 23 failed**, eight subtests, 59.99% coverage, 79.54s. Core 714/0 passed. Dependency audit 43107011564 and push audit 43107006316 passed (six manifests, zero known vulnerabilities reported); fail-closed PR gate 43107011620 and push gate 43107006286 passed. Wheel build and installed mission verification were skipped because the full-suite test step failed.
- Failure diagnosis from job 130812858662: all 23 failures are current-map schema compatibility assertions. Commit 043909f changed only `research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_current.json`, replacing the richer append-only schema with a reduced Run36-shaped object. The 3,426 other tests passed; core tests passed 714/0. This is an evidence-map schema regression, not an observed runtime/prediction-engine regression. Restore the parent schema and append Run36/Run37 records; do not weaken or delete tests.
- Fresh spot capture: OKX XRP-USDT 1.0631, bid 1.0630/ask 1.0631, 24h volume 43.189M XRP, event timestamp 21:45:44.972 UTC; Kraken XRP/USD 1.06217, bid 1.06188/ask 1.06192, no provider event timestamp; USDT/USD 0.99887. Normalized asynchronous midpoint gap approximately -0.0043%; not executable arbitrage.
- Spot depth: Fuelmaps 14:00 UTC six-venue spot snapshot, ±1% $13.7M bids/$11.8M asks, ±5% $25.0M/$14.7M, ±10% $33.8M/$16.1M; approximately eight hours old. Basis 18:46 UTC Binance XRPUSDT perpetual snapshot, ±1% $16.0M bids/$14.9M asks; not spot. Resting orders can be cancelled.
- Derivatives: TradRadar 19:05 UTC OI $1.57B, -0.97%, funding +0.0045%/8h, 79.7% long accounts, at least $2.85M liquidations ($1.58M long/$1.27M short). Liqwall 21:22 UTC OI $1.17B, +0.6%, funding +0.0079%/8h, 75% long accounts, $2.8M liquidations ($1.7M long/$1.1M short). Different venue/contract coverage; no averaging.
- ETF flows through Nov10: Alpha/ByKaranteli -$7.6M daily and -$18M seven/five sessions; Alpha 30-session +$1.3M/cumulative +$1.71B; ByKaranteli cumulative +$1.79B/AUM $1.19B. CryptoETF.today partial 4/5 -$6.9M, 30D +$115.2M/cumulative +$1.80B. The Block separate 24h window -$10.4M/AUM $1.1B. Preserve fund universes and vintages; do not average.
- Flows: TrackWhale 19:45 UTC tracked 7D inflows 178.61M/outflows 243.39M XRP, net -64.78M across eight exchange inflows and eleven outflows; largest 168.42M transfer is unattributed. XRP Insights Nov11 08:00 UTC: 22.33B XRP across 701 attributed wallets/24 exchanges; same-wallet +1.3M 7D/-155.7M 30D. Includes cold storage and cbXRP backing; not tradable float.
- CFTC remains Nov3 positions/Nov6 release: 396.2485M XRP-equivalent, -12.94% w/w; Coinbase 176LM2 dropped from reporting, missing is not zero. Current cbXRP reserve snapshot last verified 21:05 UTC: 152.0879M XRP reserves vs 152.0857M cbXRP supply; issuer display, not independent audit. Morpho current borrower state not retrieved.
- Macro: October CPI headline +0.4% MoM/core +0.3%; Reuters Nov11 reports DXY +0.64%, Brent settled $92.76 (+1.39%) amid Iran/Hormuz risk and Russia-Ukraine developments. FSB called for stronger Turkish stablecoin supervision and cross-border cooperation. Broad context only, not XRP-specific causation.
- Identity: SBIC East/Tokyo, Central/Nagoya and West/Osaka remain three separate Japanese regional SME investment/consultation companies, not SBI Holdings. ASK candidates remain distinct; no XRPL deployment verified. Actual capital remains separate cash/in-kind/debt/facility/ELOC/warrant/resale categories. Kamilah person identity confirmed; candidate YouTube channel ownership unverified, so no video inventory attributed; Camilla not assumed same person.
- Nine platforms: only current ChatGPT/GitHub connector tested, but overprivileged (admin/maintain/push/pull/triage); Claude, Grok, Gemini, Codex unverified; Copilot no formal approval; Hugging Face BUILD_ERROR; Kaggle untested; Databricks HTTP403; LunaRoute declared but unauthenticated. No external-model transfer.
- Prediction remains `NOT_ISSUED`. Run37 web observations have no Barrot SHA-256 receipts or trusted timestamp and are excluded from model features. Independent WORM, replayable historical feature store, synchronized multi-venue history, vintage-aware events, scenario/counter-hypothesis generator, production evaluator key, shadow outcomes and measured OOS lift remain incomplete.
- Backlog: #1661 blocked; #1660 and #1643 superseded-source candidates retained pending verified successor merge; #1640/#1642 require semantic overlap review; unique prediction/safety/graph/topology work preserved. No source PR closed.
- Run37 durable repair restores the parent append-only map schema and adds Run36/Run37 as nested records; the prior Run36 record is preserved. New exact-head CI is pending after the repair commit. No merge, deployment, secret rotation/revocation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or source-PR closure occurred.
- Next: verify exact-head full suite and wheel/installed mission on the repaired commit; then continue semantic review and resolve branch protection, least privilege, credential-owner/provider revocation evidence and Pages authorization.


## Run37 post-repair verification and security recheck — 2026-11-11 22:10 UTC

- Map schema repair commit: `05ad5ab1120d1fa395e1de8e4ce2c99473ffae42`. It restored the richer append-only map schema and retained Run36/Run37 as nested records. The earlier exact-head failure on `043909f` (3,426 passed / 23 map-schema failures) is retained as a failed historical attempt, not erased.
- Exact repaired-head full CI [43108561438](https://github.com/Barrot-Agent/B-Agent/actions/runs/43108561438): **3,449 passed, 0 failed, 8 subtests, 59.99% coverage, 94.41 seconds** on `05ad5ab`. Core tests: 714 passed, 8 subtests, 14.08 seconds. Wheel build succeeded; installed wheel verified Barrot V3, XRP mission and canonical data assets.
- Dependency audit [43108561589](https://github.com/Barrot-Agent/B-Agent/actions/runs/43108561589): six manifests, zero known vulnerabilities reported. Fail-closed gate [43108561406](https://github.com/Barrot-Agent/B-Agent/actions/runs/43108561406) passed; automatic merge remains disabled.
- Remaining build warnings: setuptools package discovery reports `barrot_agent.data.missions` and `data.research` absent from explicit package configuration; `project.license` table deprecation remains. Wheel build and installed mission passed despite warnings.
- Credential-path recheck: `.config/gh/hosts.yml` is absent from the complete main tree (1,388 entries) and integration tree (2,288 entries). The 17 previously affected open PRs were rechecked by changed-file inventory; all 17 are still open, target `main`, and none lists the credential path. This establishes path absence from current branch diffs, **not provider-side OAuth revocation**. No token was read, rotated or revoked. The token must still be treated as potentially compromised until provider-side revocation is independently confirmed.
- Late market refresh: Liqwall 22:02 UTC reports OI $1.17B (+0.5% 24h), average funding +0.0084%/8h, $2.8M liquidations ($1.7M long/$1.1M short), 75% Binance accounts long. TradRadar 19:05 UTC reports OI $1.57B (-0.97%), funding +0.0045%/8h and 79.7% long accounts. Different universes and times; do not average.
- TrackWhale 21:48 UTC: 54 large-transfer rows, eight exchange inflows/11 outflows, net tracked exchange flow -64.78M XRP; largest 168.42M transfer remains unknown-to-unknown. XRP Insights' daily same-wallet balances remain +1.3M XRP over seven days and -155.7M over 30 days; different methods and coverage.
- CryptoKeyhole 08:39 UTC: its four-fund cohort had only 3/4 funds published for Nov10, waiting for Franklin; latest complete day Nov6 was -752,048 XRP / -$887K. This is separate from five-fund Alpha/ByKaranteli Nov10 totals and must not be averaged.
- Current PR snapshot before this verification-map update: #1661 open/draft/mergeable, head `05ad5ab`, 2,050 ahead / 0 behind, 1,023 changed files (44 workflows / 979 other paths), 2,179 blobs / 2,288 tree entries; zero formal reviews, approvals or review threads. It remains blocked by draft/approval, branch-protection visibility, Pages authorization and incomplete semantic review.
- Forecast remains `NOT_ISSUED`; public web observations are not raw-receipt ingested and remain model-ineligible. No external-model transfer or financial action occurred.
- This follow-up changes only the durable map, research artifact, handoff, sync record and one regression assertion documenting the verified credential-path removal. Exact-head CI for the resulting documentation/test update commit is pending; do not reuse the `05ad5ab` pass for a later head.


## Run37 current-head verification — 2026-11-11 22:24 UTC

- Current tested integration head: `dbbd10657df10f84b81fb816ec742564f6197b32`; main remains `84f28ee7755607236231545a14f3d093c1baaa85`. Integration is 2,052 ahead / 0 behind; #1661 is open, draft, mergeable/clean, 1,023 changed files (44 workflows / 979 other paths), 374 open PRs (360 draft / 14 non-draft).
- Exact-head full CI [43109985748](https://github.com/Barrot-Agent/B-Agent/actions/runs/43109985748): **3,449 passed, 0 failed, 8 subtests, 59.99% coverage, 86.30 seconds** on `dbbd106`. Core tests: 714 passed, eight subtests, 11.87 seconds. Wheel build succeeded; installed wheel verified Barrot V3, XRP mission and canonical data assets.
- Dependency audit [43109986068](https://github.com/Barrot-Agent/B-Agent/actions/runs/43109986068): six manifests, zero known vulnerabilities reported. Fail-closed gate [43109985757](https://github.com/Barrot-Agent/B-Agent/actions/runs/43109985757) passed; automatic merge remains disabled.
- Earlier schema regression on `043909f` (3,426 pass / 23 map-schema failures) remains recorded in the map's previous-attempt history. The append-only schema restoration and credential-path test correction are included in the passing `dbbd106` run; tests were not weakened.
- Credential path `.config/gh/hosts.yml` is absent from main, integration and all 17 current open PR diff inventories; all 17 target PRs are open and base main. This does not establish provider-side OAuth/token revocation. No credential contents were read, rotated or revoked.
- Latest market refresh and institutional/identity observations remain research-only. Spot API quotes are nearly aligned after USDT normalization; spot depth is stale and resting, derivatives OI disagrees across provider universes, ETF flows are incomplete across different fund cohorts, and exchange-transfer tracking is not comprehensive reserve accounting. Forecast remains `NOT_ISSUED`.
- #1661 remains draft with zero formal reviews, approvals and review threads. Main branch-protection details return HTTP 403; fallback ruleset disabled; connector permissions remain overprivileged; GitHub Pages publication is automatic on main push and not authorized; 979 non-workflow paths still need semantic review. No source PR was closed.
- This final Run37 handoff/map/artifact commit is documentation/evidence-only. Its exact-head CI is pending; do not reuse the `dbbd106` pass as a test result for the new commit.
- No merge, deployment, token rotation/revocation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or PR closure occurred.



## Run38 — 2026-11-11 23:15 UTC

### Mission and repository

- Mission priority 1 remains XRP intelligence and prediction-engine mastery. Barrot V3 remains the protected execution, orchestration, safety and verification foundation.
- Main SHA: `84f28ee7755607236231545a14f3d093c1baaa85`. Integration branch: `integration/xrp-v3-unified-main-20261111`. Exact parent before this Run38 durable update: `beaca9472be073f9a4cae49cb78371b4be2a1a4e`; 2,054 ahead / 0 behind.
- PR #1661 remains open, draft, reported mergeable/clean, with 1,023 changed files (44 workflow / 979 other paths), zero formal reviews, approvals and review threads. Full tree counts: main 1,388; integration 2,288. Open PR inventory: 374 (360 drafts, 14 non-drafts).

### Exact-head CI repair and verification

- Preceding head `0ddfc704ff2f6141db9f674bbf4d54e12f2c7593` failed one stale evidence-phrase assertion: 3,448 passed / 1 failed, eight subtests, 59.99% coverage. Core 714/0; dependency audit and fail-closed gates passed. The assertion required the exact phrase `exact-head full-suite passed` in the successful parent-head classification. The map wording was corrected; no tests were removed or weakened.
- Exact corrected parent-head CI [43117758597](https://github.com/Barrot-Agent/B-Agent/actions/runs/43117758597) on `beaca9472be073f9a4cae49cb78371b4be2a1a4e`: **3,449 passed, 0 failed, 8 subtests, 59.99% coverage, 93.85 seconds**. Core suite: 714/0. Wheel build succeeded; installed wheel verified Barrot V3, XRP mission and canonical data assets.
- Dependency audit [43117758561](https://github.com/Barrot-Agent/B-Agent/actions/runs/43117758561): six manifests (root runtime, development, supplemental `requirements.tx`, Hugging Face Space, legacy and PEP 621 project dependencies); zero known vulnerabilities reported. Push audit [43117751360](https://github.com/Barrot-Agent/B-Agent/actions/runs/43117751360) passed. Fail-closed PR gate [43117758784](https://github.com/Barrot-Agent/B-Agent/actions/runs/43117758784) and push gate [43117751382](https://github.com/Barrot-Agent/B-Agent/actions/runs/43117751382) passed; automatic merge remains disabled.
- Packaging warnings remain: deprecated TOML license table and setuptools discovery warnings for `barrot_agent.data.missions` and `data.research`. Wheel build and installed mission verification nevertheless passed.
- The 3,449/0 result is on parent `beaca9472be073f9a4cae49cb78371b4be2a1a4e`. The Run38 map/artifact/handoff/sync commits create newer heads; exact-head CI for the final durable head is pending and must be verified separately.

### Fresh XRP market observations

Capture: 2026-11-11 23:13:25 UTC. These are web-retrieved research observations, not Barrot raw-source receipts and not model-eligible.

**Spot:** OKX XRP-USDT 1.0552 (bid 1.0552/ask 1.0553; provider timestamp 22:46:51.363 UTC; 24h volume 41.983M XRP). Kraken XRP/USD $1.05405 (bid $1.05403/ask $1.05405; no provider event timestamp; 24h volume 19.558M XRP). Kraken USDT/USD 0.99884. Normalized OKX midpoint $1.0540206 vs Kraken midpoint $1.05404, approximately -0.00184%; asynchronous, not executable arbitrage. [OKX](https://www.okx.com/api/v5/market/ticker?instId=XRP-USDT) · [Kraken XRP/USD](https://api.kraken.com/0/public/Ticker?pair=XRPUSD) · [Kraken USDT/USD](https://api.kraken.com/0/public/Ticker?pair=USDTUSD).

**Depth:** no fresh synchronized depth retrieved. Fuelmaps' latest six-venue snapshot remains 14:00 UTC: within 1% $13.7M bids/$11.8M asks; 5% $25.0M/$14.7M; 10% $33.8M/$16.1M; excludes Binance/Bitget. More than nine hours old. Resting orders can be cancelled; current depth is missing, not imputed. [Fuelmaps](https://fuelmaps.io/order-book/).

**Derivatives:** Alpha Finance liquidation heatmap at 21:50 UTC: all-exchange OI $2.29B, 24h volume $1.97B; modeled long liquidation pressure $64.7M below vs $32.5M short pressure above; largest modeled long cluster $5.1M at $1.0486 and short cluster $3.2M at $1.0780. Actual 24h long liquidations $1.5M and short $1.2M. These are modeled from OI/leverage tiers, not actual account-level orders or guaranteed triggers; no Binance map was drawn for this window. [Alpha heatmap](https://alphafinance.io/liquidation-heatmap/xrp/).

TradRadar at 19:05 UTC: seven-exchange OI $1.57B (-0.97% 24h), OI-weighted funding +0.0045%/8h, at least $2.85M liquidations ($1.58M long/$1.27M short), 79.7% long accounts across five exchanges. Different coverage from Alpha; no averaging. [TradRadar](https://tradradar.io/markets/xrp).

Alpha six-venue funding page, updated 22:14 UTC: average +0.0081%/8h; Binance +0.0076%, OKX +0.0095%, Bybit +0.0079%, Bitget +0.0069%, Gate +0.0098%, Hyperliquid +0.0072%. Positive funding is positioning context, not a forecast. [Alpha funding](https://alphafinance.io/crypto-funding-rates/).

No fresh XRP-specific options snapshot was retrieved; the current Alpha options page displays BTC/ETH only. No substitution was made.

**ETF flow reconciliation:** Alpha Finance's five-fund series through Nov10 reports -$7.6M; Grayscale GXRP -$7.2M and Canary XRPC -$449.8K; Bitwise XRP, Franklin XRPZ and 21Shares TOXR zero. Seven-session -$18.0M; 30-session +$1.3M; cumulative net inflow +$1.71B. Alpha includes GXRP and excludes XRPR/BITW. [Alpha ETF](https://alphafinance.io/etf/xrp/).

XRP Insights tracks six spot funds plus BITW for holdings: 1.18597B XRP, $1.25962B AUM, 1.186% supply. Its Nov10 holdings-change flow is -27,000 XRP (~-$28.5K); Nov9 -9.54M XRP; Nov9–10 -9.57M XRP; week46 -9.21M XRP. It explicitly excludes GXRP from flow totals while a data gap is corrected, but still counts GXRP holdings. Its universe differs from Alpha. [XRP Insights](https://xrp-insights.com/).

The Block reports -$10.4M and $1.1B AUM in a separate rolling 24h window updated 06:17 UTC. Preserve separately; do not average. [The Block](https://www.theblock.co/data/etfs).

### Prediction engine

- Implemented on integration: 47 public source definitions (43 hourly, two weekly CFTC; 45 scheduled; two non-commercial XRPL nodes excluded), read-only collector, SHA-256 content-addressed raw payloads and per-run receipt chain, point-in-time SQLite feature-store prototype with revision lineage, four deterministic baselines, chronological walk-forward with purge/embargo across 1h/4h/24h/7d/30d, baseline calibration using prior resolved OOS outcomes, univariate PSI drift diagnostics and fail-closed forecast ledger v4 with Ed25519 attestation contract.
- Limits: spot Binance/Coinbase/Kraken/OKX; historical derivatives only Binance USD-M XRPUSDT. Several order-book sources remain raw-only due timestamp/sequence limitations. ETF-flow and exchange-wallet data remain research-only/hash-only, not model features. CFTC remains model-ineligible. Feature-store continuity uses evictable GitHub Actions cache/artifacts (per-run checkpoint 7 days; daily/manual archive 90 days); deterministic raw-to-feature rebuild is not implemented. No independent WORM/timestamp anchor, dependence-aware block-bootstrap intervals, independent shadow outcomes, trained predictive model or production evaluator key.
- Forecast `NOT_ISSUED`. Run38 web observations have no Barrot raw-byte SHA-256 receipts or trusted timestamps and are excluded from model features. No paper trade or real-money action.

### Security, platforms and backlog

- `.config/gh/hosts.yml` is absent from main, integration and all 17 current open-PR changed-file inventories. No contents were read. Provider-side OAuth/token revocation remains unverified.
- GitHub connector permissions remain overprivileged (admin/maintain/push/pull/triage). Main branch-protection details HTTP403; visible fallback ruleset disabled. Security-alert endpoints inaccessible; no absence inferred. GitHub Pages publication is automatic on main push and unauthorized.
- Nine-platform map: ChatGPT/GitHub current-session access verified but overprivileged; Claude/Grok/Gemini/Codex unverified; Copilot no formal PR approval; Hugging Face BUILD_ERROR; Kaggle untested/no submission; Databricks HTTP403/no write; LunaRoute declared canonical but endpoint authentication/data flow unverified. No external-model transfer.
- Non-draft backlog: #1653 unique graph (six paths unique); #1650/#1254 title/path/version mismatch review; #1649/#1648/#1646 dependency supersession candidates; #1645 exact duplicate candidate; #1644/#1647 workflow semantic review; #1255 older databricks dependency; #1320/#1318/#1317/#1269 unique safety/MMI/topology. #1660/#1643/#1640/#1642 remain overlap candidates. Preserve all until verified successor merge and main verification; no source PR closed.

### Merge decision

**No merge.** Parent beaca947 passed technical gates, but #1661 remains draft with zero approvals/reviews; branch-protection details inaccessible; connector least privilege not met; provider-side token revocation unverified; Pages publication unauthorized; and 979 non-workflow paths need semantic review. Exact-head CI on the final Run38 durable commit is pending.

No merge, deployment, secret rotation/revocation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or source-PR closure occurred.


## Run38 final exact-head verification and backlog reconciliation — 2026-11-11 23:25 UTC

**Verified current parent head:** `dd0152881ab6572b8a649a8bb4b87a9366335b92` (2,058 ahead / 0 behind main; 1,024 changed files, 44 workflows / 980 other paths; tree 2,289 entries).

- Full repository suite [43119172919](https://github.com/Barrot-Agent/B-Agent/actions/runs/43119172919): **3,449 passed, zero failures, eight subtests, 59.99% coverage, 84.72 seconds**.
- Core suite: 714 passed, zero failed, eight subtests.
- Wheel build succeeded; installed wheel verified Barrot V3, XRP mission and canonical data assets.
- Exact-head dependency audit [43119172765](https://github.com/Barrot-Agent/B-Agent/actions/runs/43119172765): six manifests, zero known vulnerabilities reported.
- Fail-closed PR gate [43119172855](https://github.com/Barrot-Agent/B-Agent/actions/runs/43119172855) and push gate [43119162925](https://github.com/Barrot-Agent/B-Agent/actions/runs/43119162925) passed. Automatic merge remains disabled.
- This 3,449/0 result is on parent `dd015288`. The corrective map/handoff/sync commit below creates a new head; its exact-head CI remains pending.

### Dependabot/workflow backlog correction

A line-by-line comparison corrected the earlier Run38 title/path-mismatch classification:

- #1650 raises `huggingface_hub` from 2.2.0 to 2.4.0. Integration includes 2.4.0 and `databricks-sdk` 0.158.0; that source branch still has 0.153.0. Supersession candidate.
- #1254 raises `huggingface_hub` to 2.3.0; integration has 2.4.0. Older supersession candidate.
- #1255 raises `databricks-sdk` to 0.157.0; integration has 0.158.0. Older supersession candidate.
- #1649's `databricks-sdk` 0.158.0 is represented in integration; #1648's pytest 9.2.0 and #1646's types-requests 2.33.0.20261030 are also represented, while their source branches retain older companion versions. Treat these as combined dependency supersession candidates, not exact duplicate PRs.
- #1645's only changed workflow file is identical to integration: exact duplicate candidate.
- #1644 has one identical file of eight; seven differ. #1647 has one identical file of six; five differ. Both remain workflow-overlap semantic-review candidates.
- #1653 retains six unique graph paths. #1320/#1318/#1317/#1269 remain unique safety/MMI/topology work.

No source PR was closed. Preserve every source branch until the consolidated successor is ready, merged, and its files are verified on main.

**Merge remains blocked:** #1661 is draft with zero approvals/reviews; branch-protection details return HTTP403; connector permissions remain overprivileged; provider-side OAuth revocation is unverified; Pages publication is unauthorized; 980 non-workflow paths require semantic review. No merge or external action occurred.


## Run39 — 2026-11-11 19:02 ET / 2026-11-12 00:02 UTC

### Mission and repository snapshot

- XRP intelligence and prediction-engine mastery remain priority 1. Barrot V3 remains the protected execution, orchestration, safety and verification foundation.
- Main SHA: `84f28ee7755607236231545a14f3d093c1baaa85` (branch protected=true; branch-protection detail endpoint returns HTTP 403).
- Integration branch: `integration/xrp-v3-unified-main-20261111`; exact current tested parent head: `694786fda25c1f6ca9c4f05a20de3d6e531fe457`; 2,065 commits ahead / 0 behind main.
- Main tree: 1,388 entries; integration tree: 2,289 entries.
- PR #1661: open/draft, reported mergeable; 1,029 changed files, 49 workflow files and 980 non-workflow files; 374 open PRs (360 draft, 14 non-draft).
- Latest commit `694786fda25c1f6ca9c4f05a20de3d6e531fe457`, parent `b756416d303c7dc0f1984071e24342940b6a9a28`, message “Remove empty workflow env blocks after step-scoping Groq credentials.” It removed empty job-level `env:` keys from five workflows while preserving explicit step-level Groq-secret scope, exact-main-SHA validation, `persist-credentials: false`, and read-only permissions; one regression assertion was added. The change is limited to five workflows and `tests/test_external_action_gates.py`.

### Exact-head CI — VERIFIED on 694786f

- Full repository suite: **3,452 passed, 0 failed, 8 subtests, 59.99% coverage, 93.09 seconds**.
- Core suite: 714 passed, 0 failed.
- Wheel build and installed wheel verification passed; installed package loaded Barrot V3, the XRP mission and canonical data assets.
- Dependency audit: six manifests passed; zero known vulnerabilities reported.
- Fail-closed PR gate passed; automatic merge remains disabled.
- Full CI: [43123398300](https://github.com/Barrot-Agent/B-Agent/actions/runs/43123398300), full-suite job [130869264786](https://github.com/Barrot-Agent/B-Agent/actions/runs/43123398300/job/130869264786).
- Dependency audit [43123398294](https://github.com/Barrot-Agent/B-Agent/actions/runs/43123398294); fail-closed gate [43123398296](https://github.com/Barrot-Agent/B-Agent/actions/runs/43123398296).
- Latest main Cross Analysis [43123012231](https://github.com/Barrot-Agent/B-Agent/actions/runs/43123012231) passed on main SHA 84f28ee.

### New XRP market and funding evidence

Capture cutoff 2026-11-12 00:02:43 UTC. These observations are web-rendered/public API retrievals, not Barrot receipt-ingested model features.

**Spot:** OKX XRP-USDT last 1.0538, bid 1.0538/ask 1.0539, provider timestamp 23:56:13.061 UTC, 24h high 1.0807/low 1.0409 and volume 42.425M XRP. Kraken XRP/USD last 1.04820, bid 1.04821/ask 1.04822, no provider event timestamp, 24h high 1.07953/low 1.04004 and volume 21.869M XRP. Kraken USDT/USD midpoint 0.998825. Normalized OKX midpoint is about $1.052612 versus Kraken $1.048215, a 0.41945% asynchronous difference. This is a freshness/dislocation flag, not executable arbitrage. No fresh synchronized L2 depth was retrieved; Run38 Fuelmaps depth is stale and cancellable.

**Funding and OI:** CryptoQuant's Binance 30-day cumulative funding was reported at +0.18%, highest since October 2025 (secondary reporting; underlying CryptoQuant series not directly retrieved). CryptoTicker's OKX public-interface check reported 76 positive of the last 100 settlements and +0.39% cumulative since October 9. FundJu at 20:54 UTC reported 90 settlements over 30 days, 72 positive/18 negative, cumulative +0.406% and current +0.0087% per eight hours. FundJu and CryptoTicker share OKX public-data lineage and are not independent exchange datasets. CryptoTicker reported OKX OI $132.1M on Nov4 versus $101.9M Nov10 (-23% USD), while coin-denominated OI fell only about 10%; long/short account ratio 3.70 Nov11 versus 4.27 Nov9. USD OI decline therefore includes mark-price decline; account ratios are not notional exposure. Positive funding may indicate directional long crowding or hedged basis/carry exposure. Both remain competing hypotheses.

**ETF flows:** CryptoTicker/Coinpedia/24-7 Wall St relay SoSoValue's Nov9 -$10.4M (about 9.37M XRP); Bitwise reportedly accounted for $9.4M, with four zero-flow sessions Nov3–6. 24/7 Wall St reports only -$4.2M cumulative net outflow Oct12–Nov9. These are the same underlying SoSoValue lineage, not independent confirmations. Do not average with Alpha/XRP Insights cohorts or rolling windows.

**Binance theft-linked XRP:** CryptoTicker's XRPL ledger observation (validated ledger 108,255,241; 07:44 CET Nov11) reports a 33,455,915 XRP transfer from the last dormant wallet to the collection wallet at 01:01 CET, leaving 29,466,416 XRP in the collection wallet after 32.34M XRP moved in 193 payments since the previous measurement. Elliptic is reported to say most XRP was swapped into BTC via THORChain. This does not identify ultimate buyers or prove fiat cash-out. The concentrated seller wallet was emptied, but a 29.47M XRP collection balance remained at that cutoff.

### Evernorth SEC resale registration — material distinction

SEC Form 424B3 accession `000162828026072223`, filed Nov9 and accepted 16:18:57 UTC, registers up to 73,688,162 Class A shares: 19,102,635 already issued/outstanding; 31,392,746 issuable on Class C conversion; 22,953,128 issuable on Company Unit redemption/exchange; and 239,653 issuable on Sponsor Warrant exercise. It also registers 239,653 Sponsor Warrants at an $11.50 exercise price. Evernorth states it receives no proceeds from shareholder resales, except cash proceeds from warrant exercises. The separate 5,218,935-share Cantor ELOC has a separate registration statement. This is potential shareholder resale/conversion/dilution capacity, not evidence of completed sales or an Evernorth XRP sale. The 24/7 Wall St report of XRPN -23.5% Nov9–10 is secondary market context; correlation with XRP's -3.9% Nov10 does not prove causation. The filing does not change the XRP wallet by itself.

### Identity / exact phrase continuation

- “Actual capital” remains non-standardized; continue separating cash raised, cash actually deployed into XRP, in-kind XRP, debt, facilities, collateral, registered resale capacity and secondary resales.
- ASK results still surface Permission Coin and unrelated candidates. Permission Coin's reported Base/Polygon OFT-20 deployment does not establish XRPL/XRP integration.
- Official Tokyo SBIC ChatGPT training material and SBIC West seminar materials are educational events; no OpenAI strategic partnership or formal “SBIC, ChatGPT SBIC” entity/relationship was verified.
- No first-party YouTube channel ownership was established for Kamilah/Camilla Stevenson; no videos were attributed. Camilla and Kamilah remain separate identity candidates.

### Prediction engine and eligibility

Implemented on integration: 47 public source definitions (43 hourly plus two weekly CFTC sources; 45 scheduled), read-only collector, SHA-256 raw-source receipt/hash-chain logic, point-in-time SQLite feature-store prototype, four deterministic baselines, purged/embargoed chronological walk-forward evaluation, temporal calibration diagnostics, PSI drift diagnostics and fail-closed forecast ledger v4 with Ed25519 evaluator-attestation requirement.

Not yet production-verified: independent WORM/timestamp anchoring; replayable durable cross-run feature reconstruction; synchronized multi-venue L2/derivatives/flows/collateral history; vintage-aware macro/geopolitical event timeline; scenario/counter-hypothesis engine; production evaluator key; 100 independent OOS and 100 independent shadow outcomes; calibration error <=0.05 and sufficient non-overlapping horizon windows; verified successful main-branch scheduled ingestion. Actions cache/artifacts are evictable and not WORM. No trained predictive model or demonstrated out-of-sample lift is established.

**Forecast status: NOT_ISSUED.** Run39 web observations were not captured through Barrot's byte-exact raw-source collector; no raw receipt or raw payload SHA-256 is claimed. No directional forecast, paper trade or real-money action occurred.

### Nine-platform status

ChatGPT/GitHub access is tested but repository permissions expose admin/maintain/push/pull/triage. Claude, Grok, Gemini and Codex authentication/data flow remain unverified; Copilot has no formal PR approval; Hugging Face BUILD_ERROR; Kaggle untested/no submission; Databricks HTTP 403/no write; LunaRoute is repository-declared canonical but endpoint authentication/data flow remains unverified. No external-model transfer occurred.

### Backlog and merge decision

- #1661: sole consolidated integration PR; blocked, draft, zero formal reviews/approvals/threads.
- #1660: 972 shared paths, 949 identical / 23 different; superseded-source candidate, retain.
- #1643: 670 shared paths, 661 identical / 9 different; research overlap candidate, retain.
- #1640: 280 shared paths, 244 identical / 36 different; integration overlap candidate, retain.
- #1642: seven shared paths, zero identical / seven different; unique prediction work, retain.
- #1653: six unique graph paths; unique work, retain.
- #1650/#1649/#1648/#1646: dependency updates represented in integration, but source branches have older companion versions; supersession candidates, retain until verified merge.
- #1645: one-file exact duplicate candidate; retain until verified merge.
- #1644/#1647: partial workflow overlap with differing files; semantic review, retain.
- #1254/#1255: older dependency versions than integration; supersession candidates, retain.
- #1320/#1318/#1317/#1269 and #1614/#1612/#1611/#1610/#1608: preserve unique safety, MMI, topology, prediction and research work.
- No source PR was closed.

Main is protected=true, but detailed branch protection returns HTTP403; the only visible “Fall Back” ruleset is disabled. GitHub connector permissions remain overprivileged. The credential path `.config/gh/hosts.yml` was last verified absent from main/integration and 17 affected open-PR changed-file inventories; provider-side OAuth revocation remains unverified. Main pushes trigger GitHub Pages publication; authorization remains absent. 980 non-workflow paths still require semantic review.

**No merge.** The exact tested head 694786f passes full CI, dependency audit and fail-closed gate, but PR #1661 remains draft with zero approvals/reviews; branch-protection requirements are not visible; connector least privilege is unresolved; provider-side credential revocation is unverified; Pages publication is unauthorized; and semantic review is incomplete. Do not bypass branch protection or required checks.

Next action: prioritize semantic review of V3 runtime, ingestion, feature store, forecast ledger, 49 workflow changes and public interfaces; resolve least privilege, branch-protection visibility, credential-owner revocation evidence and Pages side-effect authorization. Keep forecast issuance disabled until independent receipt anchoring, mature shadow/OOS evidence and a trusted evaluator key pass.

No merge, deployment, secret rotation/revocation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or source-PR closure occurred.
