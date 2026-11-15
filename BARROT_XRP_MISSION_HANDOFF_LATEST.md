# Barrot XRP Mission Handoff — Run174

**Captured:** 2026-11-15 21:01:47 UTC  
**Status:** INTEGRATION_RECOVERY_IN_PROGRESS  
**Mission priority:** 1 — XRP intelligence and measured prediction-engine mastery  
**Foundation:** Preserve Barrot V3 as the execution, orchestration, safety, authorization and verification foundation.

## Current main and successor

- **Current main:** `5b2a9c46eb878250dfec99190e294909cd5835bf`
- **Successor branch:** [integration/xrp-v3-mainline-successor-20261115T2101Z](https://github.com/Barrot-Agent/B-Agent/tree/integration/xrp-v3-mainline-successor-20261115T2101Z)
- **Successor base:** `5b2a9c46eb878250dfec99190e294909cd5835bf`
- **Successor code-tree commit:** `90be1817bb44ade6e394eb703be8803b79f958e7`
- **Archived source branch:** [integration/xrp-v3-unified-main-20261112](https://github.com/Barrot-Agent/B-Agent/tree/integration/xrp-v3-unified-main-20261112)
- **Archived source head:** `b48ba44bcaf712be154a2ccb6745c0c5aa839aeb`
- **Source PR #1662:** [closed unmerged](https://github.com/Barrot-Agent/B-Agent/pull/1662), closed by Barrot-Agent at 20:55:02 UTC. The compare API found no common ancestor between current main and the old integration branch. No merge occurred; the old branch and history remain intact.

The new branch is directly based on current main. Its initial code-tree commit compares as one commit ahead and zero behind main. It establishes a normal mainline ancestry without rewriting the source branch.

### Tree reconciliation

| Comparison | Result |
|---|---:|
| Main tree entries | 1,392 |
| Archived integration tree entries | 2,503 |
| Identical path/blob/mode entries | 1,185 |
| Divergent path entries | 205 |
| Integration-only entries | 1,113 |
| Main-only paths | `.github/FUNDING.yml`, `MEMORY.md` |
| Path-type conflicts | 0 |
| Mode differences | 3 |
| Successor tree entries | 2,491 |

The current main versions of `README.md`, `.github/FUNDING.yml`, `MEMORY.md`, `.bashrc`, `.gitconfig`, `.config/gh/config.yml`, `.termux/termux.properties`, `mcp_config.json` and `barrot_repo_snapshot.txt` remain byte-identical to main. The integration versions of local shell/Git/Termux configuration and scratch files were not overlaid. They remain on the archived source branch. The successor retains the V3 collaboration/acceptance records, disabled-test archive and MMI execution ledger from `.barrot`; local `.barrot` repository-state, identity, target-registry and runtime folders remain on the source branch pending separate review.

The latest handoff and Run174 audit are now recorded in this successor branch. The platform capability map remains a Run173 snapshot; its platform authentication states are still useful, but its repository-state fields must be refreshed after exact-head CI.

**No PR has been created yet. No merge has occurred.** This is one consolidated working branch, not a new fragmented PR.

## Exact-head CI

### Current main

[CI run 43760742911](https://github.com/Barrot-Agent/B-Agent/actions/runs/43760742911) passed on `5b2a9c46eb878250dfec99190e294909cd5835bf`:

- 848 tests passed
- 0 failed
- 1 skipped
- 8 subtests passed

The main full-suite job runs without coverage measurement. Its coverage configuration excludes AGI, ingestion, analysis, monetization, orchestration and `mem_palace.py`.

### Archived integration head

[CI run 43757499109](https://github.com/Barrot-Agent/B-Agent/actions/runs/43757499109) on `b48ba44`:

- 3,805 passed
- 1 failed
- 1 skipped
- 19 subtests passed

The single failure was a stale historical evidence assertion in `tests/test_xrp_nine_platform_current_map_run73.py`. It compared the Run173 latest head to an older Run162 top-level value. The successor corrects the assertion to the authoritative `run173_snapshot.integration_head_before_run173_commit` value. No test was removed or weakened.

The source branch's six-manifest dependency audit passed with zero known vulnerabilities ([43757499132](https://github.com/Barrot-Agent/B-Agent/actions/runs/43757499132)). Push and PR fail-closed gates passed ([43757499106](https://github.com/Barrot-Agent/B-Agent/actions/runs/43757499106), [43757504295](https://github.com/Barrot-Agent/B-Agent/actions/runs/43757504295)). PR Pages validation was build-only, not deployment ([43757504281](https://github.com/Barrot-Agent/B-Agent/actions/runs/43757504281)).

### Successor branch

**Exact-head full suite: PENDING.** The new preservation regression test verifies the main README, funding file, memory file, priority-1 XRP mission, Run174 audit and latest handoff. No source-head test result is being substituted for the successor's run.

## Main-branch side effects and safety

- Main Pages build [43760719743](https://github.com/Barrot-Agent/B-Agent/actions/runs/43760719743) failed at the Jekyll/Liquid manifest example near line 6456. The deploy job was skipped; no deployment occurred. The integration manifest contains the raw-block correction and previously passed build-only validation.
- Main Barrot Sync [43760742862](https://github.com/Barrot-Agent/B-Agent/actions/runs/43760742862) reported wrapper success, but `b_agent.py --sync` failed because `rich` was missing. The workflow then printed a skip message and used `git push || true`, masking failure. No sync or external call occurred.
- Main's manually dispatchable Coinbase paper trader lacks typed approval and product-identity validation. Its integration successor requires typed YES, exact main SHA, identity validation, read-only repository permissions and artifact-only output. No paper-trading workflow was dispatched.
- Main Ask Barrot, Barrot Agent and Ping-Pong retain legacy write-capable paths; integration quarantines those writers with disabled jobs and empty permissions.
- The scheduled XRP collector is present on integration, read-only and main-ref guarded. It is not active on main.

## Prediction-engine status

Implemented on integration/successor:

- 51 public-source definitions, 49 scheduled definitions
- SHA-256 receipt-chain prototype
- SQLite point-in-time feature store
- event timelines and counter-hypotheses
- naive, momentum, mean-reversion and volatility baselines
- purged/embargoed chronological walk-forward evaluation
- paired temporal and source-clustered moving-block bootstrap
- probability calibration and PSI drift monitoring
- fail-closed forecast ledger and Ed25519 evaluator attestation

Still blocking model eligibility:

1. 85 curated events lack byte-exact `raw_source_sha256` receipts.
2. 43 of 85 events lack publisher timestamps.
3. Independent WORM archival and trusted timestamp anchoring are not verified.
4. Synchronized historical spot, full-depth L2, derivatives, exchange-flow and collateral data remain incomplete.
5. No XRP candidate has demonstrated superiority against all four baselines.
6. No qualified independent shadow cohort exists.
7. Scheduled ingestion has not been verified on main.

The admission policy requires at least 100 training, 100 OOS and 100 shadow samples; effective sample size of at least 10 and 10 forecast horizons for OOS and shadow; five receipt-backed independent source clusters; 10,000 paired bootstrap replicates; 99.375% individual confidence for the eight comparisons; Brier and log-loss superiority against all four baselines; weighted calibration error no greater than 0.05; stable drift; a passing shadow cohort; and a valid independent Ed25519 attestation.

**Forecast status: NOT_ISSUED. Accuracy: NOT_EVALUATED.**

The latest market snapshot remains Run173 and is research-only: source timestamps were stale or unavailable, USD normalization failed the 60-second skew gate, no full-depth L2 was admitted, and raw HTTP bytes/SHA-256 receipts were not captured. No new model-eligible market snapshot was admitted in Run174.

## Institutional and identity research retained

- SBIC East, Central and West are separate regional SME investment companies, not SBI Holdings. SBIC East and West official training records reference ChatGPT; no OpenAI commercial partnership is established.
- ASK Coin remains unresolved: Permission ASK on Base/Polygon is a candidate, not a verified XRPL issuer.
- “Actual capital” is not a standardized XRP metric; equity cash, XRP purchases, in-kind contributions, debt, warrant proceeds, undrawn facilities, stablecoin supply and exchange-wallet balances remain separate.
- Kamilah Stevenson's person identity is verified, but candidate YouTube channel ownership is not first-party authenticated. Camilla/Kamilah name variants are not conflated; candidate video inventory remains quarantined.
- Circle's $100M Binance equity placement and five-year USDC distribution arrangement are distinct from XRP capital.
- Circle's Coinbase distribution expense is not Coinbase net profit or XRP flow.
- Circle SBI Japan K.K. is a 50/50 Circle/SBI venture, separate from regional SBIC companies.
- SBI Group is named as an Arc founding validator; the legal validating subsidiary is not identified.
- SBI VC Trade USDC/RLUSD distribution and JPYSC are distinct rails. JPYSC public-chain circulation on XRPL is not verified.
- PNC/Coinbase/Circle is an incoming USDC-on-Ethereum pilot converted to USD, not XRP settlement.
- BNY/Ripple custody support is distinct from exploratory tokenized trade finance.
- Standard Chartered's eligible RLUSD custody is live through DIFC; the LMAX collateral integration remains planned and conditional.
- Evernorth cash proceeds, cash-funded XRP purchases, in-kind XRP, debt, warrants and undrawn ELOC capacity remain separate capital categories.

## Nine-platform capability map

| Platform | Current verified state |
|---|---|
| ChatGPT | Current-session GitHub connector verified; permissions overprivileged |
| Claude | Unverified |
| Grok | Unverified |
| Gemini | Unverified |
| Copilot | One-off review activity only; no formal approval |
| Codex | Unverified |
| Hugging Face | Previous BUILD_ERROR; no verified deployment |
| Kaggle | Untested; no submission |
| Databricks | Previous HTTP 403; no write |

## Open PR backlog

Eight PRs remain open and are preserved as unique/unreviewed:

- #1541 — MMI claim identity fingerprint security
- #1460 — XRP institutional multirail, Binance and Kamilah research
- #1450 — Binance phase-one status, escrow and PR audit
- #1440 — XRP ledger archive validation repair
- #1437 — XRP ledger source addenda and snapshot pointer
- #1436 — Binance XRP theft and issuer-freeze graph
- #1353 — XRP ledger shard migration
- #1265 — XRP ledger index migration

No open source PR was closed. PR #1662 is already closed unmerged and is superseded for the integration objective by this mainline successor. No PR is currently classified ready.

## Governance blockers

- Main branch-protection detail returns HTTP 403.
- The previously visible fallback ruleset 10863829 is disabled.
- CODEOWNERS assigns `* @Barrot-Agent`, not an independent reviewer.
- GitHub connector permissions include admin, maintain, push, pull and triage.
- Independent formal approvals remain zero.
- Full semantic review of the integrated paths is incomplete.

## Next actions

1. Finish exact-head full-suite, dependency/security and fail-closed verification on the successor branch.
2. Complete semantic review of changed workflows, called scripts, divergent code paths and newly added research/test paths.
3. Refresh the nine-platform map's repository-state section to Run174 after CI.
4. Resolve independent review, least-privilege permissions and branch-protection visibility.
5. Establish byte-exact raw-source receipts and independent WORM archival.
6. Verify scheduled ingestion on main only after an authorized merge and main CI.
7. Create one consolidated PR only when the successor is conflict-free, fully tested and independently reviewed.

**No merge, deployment, secret rotation, Space restart, external-model transfer, Databricks write, Kaggle submission, paper trade, funds transfer, real-money action, force-push, history rewrite or source-PR closure occurred.**

Historical handoff archive: [Run173 and earlier records on the preserved source branch](https://github.com/Barrot-Agent/B-Agent/blob/integration/xrp-v3-unified-main-20261112/BARROT_XRP_MISSION_HANDOFF_LATEST.md).


---

## Run175 — Current-main successor recovery and XRP intelligence update

**Captured:** 2026-11-15T21:29:23Z

### Repository reconciliation

The repository's current main has moved to `5b2a9c46eb878250dfec99190e294909cd5835bf`. This is not the legacy main SHA `16ec152c5278d38fd8fb4ad8b361de88ab5c7da9`; GitHub's compare endpoint reports no common ancestor between those two historical references. No history rewrite or force-push was performed in this run.

The former integration PR [#1662](https://github.com/Barrot-Agent/B-Agent/pull/1662) is now **closed, unmerged** (closed at 2026-11-15T20:55:02Z). Its populated `merge_commit_sha` field is not proof of a merge because the API reports `merged=false`. Do not count its content as main.

A single successor branch already exists directly from current main:

- Branch: `integration/xrp-v3-mainline-successor-20261115T2101Z`
- Pre-Run175 head: `692caffaba27e9653fddfde3823785efad096e17`
- Ahead/behind current main: 2 / 0
- No successor PR has been created.

Current recursive trees: main 1,392 entries; successor 2,493 entries before this Run175 preservation commit. Tree reconciliation found 14 main-only path entries, all under `.barrot/`: ten file blobs and four directory entries. The successor was missing the ten main blobs, including the 3,513,853-byte `.barrot/repo_state_manifest.json`. Run175 restores those exact existing main blobs by their Git object SHA without reading or rewriting their contents, and adds byte-hash regression coverage. The test requires every restored file to match its original Git blob SHA-1. After restoration, no main path should be missing.

The successor adds/changes a substantial body of work: 168 existing file blobs changed, 1,104 successor-only file blobs, and 47 changed workflow files. GitHub's compare response caps its changed-file list at 300, so the recursive-tree path reconciliation is authoritative for path inventory. The complete semantic review is not finished.

### Exact-head verification before the Run175 preservation commit

On `692caffaba27e9653fddfde3823785efad096e17`:

- Full repository suite: **3,807 passed, 0 failed, 1 skipped, 19 subtests passed**.
- 3,808 tests collected.
- Inclusive package coverage: 64.02% (27,650 statements, 9,411 missed, 8,652 branches, 1,721 partial branches).
- Legacy core-package floor: 77%.
- Duration: 176.60 seconds.
- Wheel build passed; installed wheel loaded Barrot V3, the XRP mission and canonical data assets.
- Six-manifest dependency audit passed with zero known vulnerabilities.
- Fail-closed gate passed; automatic merge was not enabled.

Evidence: [Full suite 43762762348](https://github.com/Barrot-Agent/B-Agent/actions/runs/43762762348), [dependency audit 43762762356](https://github.com/Barrot-Agent/B-Agent/actions/runs/43762762356), [fail-closed gate 43762762343](https://github.com/Barrot-Agent/B-Agent/actions/runs/43762762343).

The Run175 preservation/handoff commit must receive its own exact-head full-suite and security-gate verification. The predecessor result is not transferred to the new head.

### Main-branch workflow and governance findings

Main CI run 43760742911 reported 848 passed, 0 failed, 1 skipped and 8 subtests. The successor's expanded test tree collects 3,808 tests and adds inclusive package coverage.

Main Pages run 43760719743 failed in Jekyll at `GLOBAL_STATE_MANIFEST.md:6450`; the deploy job was skipped. Main Barrot Sync run 43760742862 reported success while its log shows `ModuleNotFoundError: rich`, the sync was skipped, and `git push || true` masks push errors. No successful repository write was observed in that run.

The successor's 47 changed workflow files were all statically scanned for triggers, permissions, secrets, external calls, deployments and writes. Eleven high-risk definitions received full content review. Thirty-six still need full diff review, and called-script semantic review remains incomplete.

The successor quarantines legacy repository writers, gates the Coinbase paper-trader with typed approval, exact main SHA, product identity and artifact-only output, disables the self-hosted brain deployment job, and keeps the XRP public-ingestion workflow read-only and main-ref guarded. Manual Groq workflows require typed YES, an exact main SHA and confirmation that supplied data is public/authorized. Groq is not Grok. No external-model workflow was dispatched.

Main reports branch protection enabled, but the detailed protection endpoint returns HTTP 403. Fallback ruleset 10863829 is disabled. `.github/CODEOWNERS` is only `* @Barrot-Agent`. Repository settings allow auto-merge, but no auto-merge was triggered. The current GitHub connector reports admin, maintain, push, pull and triage permissions; it remains overprivileged.

### New XRP and institutional research

**Market snapshot — descriptive only:** CoinGlass at 2026-11-15T21:04Z showed XRP $0.9608, +3.27% over 24h, 24h range $0.8922–$0.9789, -13.48% over 7d, -26.66% over 30d and -47.78% YTD. It reported $1.98B open interest, $3.78B futures volume, $1.02B spot volume, -0.0017% funding/8h, $17.91M liquidations with 75% long-side, and -$1.09M ETF flow on Nov 13. Its own page conflicts on 24h OI change (-0.58% headline versus -3.73% narrative); both are retained.

XRPSONAR's six-fund tracker reports -$19.127M over seven days and -$13.655M over 30 days. Its seven-day total is the sum of three reported days: Nov 9 -$10.421M, Nov 10 -$7.616M and Nov 13 -$1.089M. Nov 11-12 have no reported flow; missing is not assumed to be zero.

OKX XRP-USDT was $0.9607 bid/$0.9608 ask at 21:15:21.670Z, 842 seconds old at capture. Kraken XRP/USD was $0.96035 with no provider event timestamp. The cross-venue difference is not an arbitrage claim. No synchronized full-depth L2 or byte-exact raw receipts were captured. These observations are rejected for model use.

**SBI:** SBI Holdings' February 4, 2026 shareholder-benefit release offers an XRP coupon worth ¥2,000 to eligible 100–999-share holders or holders of 1,000+ shares under one year, and ¥8,000 to qualifying 1,000+ long-term holders. The coupon is redeemed through SBI VC Trade and converted using the July 31 selling price. This is an XRP distribution mechanism, not proof of an open-market buy or aggregate redemption volume.

SBI Ripple Asia and DSRV began Japan-Korea payment/remittance research on February 24 using XRPL as a contemplated infrastructure. The February 26 tokenized-deposit/deposit-money concept uses MoneyTap and a token issuance platform with XRPL contemplated; it is not a production deployment. Official SBIC Central and SBIC West profiles identify the Nagoya and Osaka regional SME investment institutions, distinct from SBI Holdings. SBIC East's ChatGPT training remains education, not an OpenAI partnership.

**Coinbase/Circle:** Coinbase's Q3 2026 Form 10-Q says its Circle arrangement was renewed on the same terms. Coinbase reported $22B average USDC held on-platform and 10.7% trading-volume share; GAAP net income of $718.7M includes $715M net crypto-asset gains, while adjusted net income was $77.7M. Circle's Q3 10-Q reports $331.3M Q3 and $986.6M nine-month distribution costs to Coinbase. Coinbase's allocations depend on platform USDC balances and broader ecosystem-growth economics. Circle also sold Binance 1.2M Class A shares at $80.84 for $100M gross proceeds. That is equity capital into Circle, not XRP capital. Circle's Q3 average USDC circulation was $73.3B, onchain transaction volume $13.9T, and CPN annualized TPV $41.3B.

**Identity searches:** No canonical XRPL ASK issuer or OpenAI/SBIC commercial partnership was established. “Actual capital” remains a research taxonomy, not a standardized XRP metric. Kamilah Stevenson's person-level identity is verified, but the candidate YouTube channel handle is not independently cross-linked; no videos were attributed as official uploads.

### Prediction and platform status

The prediction engine remains implemented on the successor branch: scheduled public-source definitions, receipt-chain prototype, point-in-time feature store, event timelines, counter-hypotheses, four baselines, leakage-safe walk-forward testing, block bootstrap, calibration, drift monitoring and fail-closed forecast ledger.

Still blocked: byte-exact receipts for all 85 curated events, independent WORM/timestamp anchoring, synchronized historical multi-venue data, candidate superiority over all baselines, independent shadow outcomes and verified scheduled ingestion on main.

**Forecast: NOT_ISSUED. Accuracy: NOT_EVALUATED.**

Only the current ChatGPT/GitHub connector is verified. Claude, Grok, Gemini and Codex remain unverified; Copilot has no formal approval; Hugging Face has no verified deployment; Kaggle is untested; Databricks previously returned HTTP 403. No external dispatch or data transfer occurred.

### Backlog and merge decision

**NO MERGE.** PR #1662 is closed unmerged. Eight other open PRs remain drafts targeting non-main branches and are classified unique/unreviewed: #1541, #1460, #1450, #1440, #1437, #1436, #1353 and #1265. Preserve all eight. Do not close any source PRs.

Next: verify the Run175 preservation commit on its own exact head; complete the 36 remaining workflow diffs and all called scripts; fix Pages and Barrot Sync false-green behavior; resolve independent review, least privilege and branch protection; only then open one successor PR. No forecast until data and OOS readiness gates pass.


### Run175 preservation commit verification note

The Run175 preservation commit is `9fe0849a5c483f5b2059344fb691aa0eafe6b39a`. A fresh recursive-tree comparison against current main `5b2a9c46eb878250dfec99190e294909cd5835bf` confirms **zero main paths missing** after restoring all ten `.barrot` blobs. The 3.51MB repository-state manifest was restored by its existing Git blob SHA without reading its contents. The byte-hash regression test was corrected to use the exact Git blob header delimiter and is included in the next exact-head CI run.


### Run175 security follow-up — credential path and generated-code quarantine

At 2026-11-15T21:44:17Z, all eight currently open PR branch tips (#1541, #1460, #1450, #1440, #1437, #1436, #1353 and #1265) were found to contain the same tracked `.config/gh/hosts.yml` blob (216 bytes; Git blob SHA `f58b27f14436088db99662d3a45c59b8437ec3a1`). The file is absent from current main and the successor branch. Main's `.gitignore` already excludes it, but the old branch tips still track it. Each branch also contains only the same `.env.example` file; no actual `.env` file was found. The contents of `.config/gh/hosts.yml` were not read. This is a **potential credential exposure**, not a confirmed compromise. Secret-scanning alert status could not be queried through the current connector. No token was rotated. Owner-side inspection is required; revoke a live GitHub CLI token if one is present. Keep the eight PRs blocked for this review while preserving their unique work. Do not close them.

A separate workflow review found that `scripts/self_benchmark.py` executes Groq-generated Python using `subprocess.run` without an environment allowlist or network/filesystem sandbox. The child inherits `GROQ_API_KEY`. The main workflow is manually dispatched and typed-YES gated, but those controls do not prevent generated code from reading the key or using the runner's network/filesystem. The successor's self-benchmark workflow is now quarantined with empty permissions and an unconditional false job condition. Main was not changed and the workflow was not dispatched. Re-enable only after a secret-free, network-disabled, filesystem-restricted sandbox is verified.


### Run175 OpenCode and agent-memory preservation correction

The successor had replaced main's verified OpenCode default (`opencode/deepseek-v4.1-flash-free`, default agent `barrot`) with an unverified LunaRoute model and had replaced main's 478-byte `AGENTS.md` with three duplicate blocks claiming that a LunaRoute API key was already in GitHub Secrets and that LunaRoute MCP tools were available. The actual successor config showed the LunaRoute MCP server disabled, with no successful authentication or data-flow test. That mismatch violated the nine-platform evidence rule and discarded verified mainline memory.

Run175 restores the verified free-model default and default agent, retains LunaRoute only as an optional provider configuration, keeps its MCP server disabled, and sets edit/bash/external-directory/webfetch permissions to ask. `AGENTS.md` is restored from main and extended once with the XRP mission and explicit unverified-provider status. `.opencode/agent/barrot.md` preserves the offline Termux deployment and useful mainline identity/memory context while retaining the safer successor rules: no destructive worktree operations, no `git add -A`, and `scripts/transmute.py` remains quarantined. No LunaRoute authentication or data transfer was attempted.


### Run175 .gitignore preservation correction

A final tree review found the successor had added a broad `.barrot/autonomous_tasks/` ignore rule that was not present on current main. Although existing tracked files remain tracked, that rule could hide new user-authored files in the directory. Run175 restores `.gitignore` byte-for-byte to current main's blob (`f63d4ea6c01a6dbeb72cd80d8f5fcdac93ea66d4`); the existing `.config/gh/hosts.yml` ignore remains because it is already in main. A regression test now verifies the exact main Git blob hash.


---

## Run176 — current-main successor, exact-head verification and market-data reconciliation

**Captured:** 2026-11-15T22:32:23Z  
**Run status:** EXECUTED; current code head VERIFIED; new handoff/audit commit requires its own exact-head CI.

### Current repository and branch reconciliation

- **Current main:** `1f30e5c18f151f75ad5d157ddde175723584ec69` (main advanced from the Run175 handoff's `5b2a9c46...`; this commit changes OpenCode GitHub MCP authentication documentation/configuration).
- **Current integration branch:** `integration/xrp-v3-mainline-successor-20261115T2101Z`.
- **Verified code/evidence head:** `9c69f1affad3f34aab9922c88cddc2be85735fb6`.
- **Active consolidated PR:** [#1663](https://github.com/Barrot-Agent/B-Agent/pull/1663), base `main` at `1f30e5c...`, head `9c69f1a...`, 12 commits ahead / 0 behind, GitHub mergeable=true, but **draft**.
- PR #1663 contains 1,276 changed files, 410,830 additions and 6,473 deletions. The complete changed-filename inventory was retrieved. The compare endpoint's per-file statistics response is capped at 300 entries, so the full 1,276-file list is the authoritative count.
- The previous PR [#1662](https://github.com/Barrot-Agent/B-Agent/pull/1662) was closed unmerged at 2026-11-15T20:55:02Z. Its archived branch and history remain intact. No merge commit is counted for #1662.
- The mainline successor was created directly from the then-current main; its PR base has since advanced to the current main SHA. Current compare is 12 ahead / 0 behind.

### Complete tree reconciliation at code head 9c69f1a

| Measure | Result |
|---|---:|
| Main recursive tree | 1,393 entries |
| Successor recursive tree | 2,511 entries |
| Main paths missing from successor | **0** |
| Shared blob differences | 169 |
| Shared directory-tree differences | 36 |
| Executable-mode differences | 3 |
| Successor-only entries | 1,118 (1,107 blobs, 11 trees) |
| Changed workflow files | 48 |
| Changed test/fixture paths | 393 |
| XRP-related paths | 975 |

The three shared-file mode changes are:
- `barrot_agent/analysis/xrp_telemetry_matrix.py`: main executable, successor non-executable.
- `barrot_agent/ingestion/council_ingest_node.py`: main executable, successor non-executable.
- `barrot_agent/orchestration/orchestrator_bridge.py`: main executable, successor non-executable.

No main path is missing. These three mode changes remain explicit review items; they have not been silently normalized.

### Exact-head CI — code head 9c69f1a

**Push CI run 43768474012 passed on the exact code head:**
- Full repository suite: **3,820 passed, 0 failed, 1 skipped, 19 subtests passed** in 104.74 seconds.
- Inclusive coverage: **64.02%** across 27,650 statements; legacy core coverage **77%**.
- Core suite: **743 passed, 0 failed, 8 subtests passed**.
- Wheel build passed.
- Installed wheel verified Barrot V3, the priority-1 XRP mission and canonical data assets.
- Full-suite job included every repository test, not only the core CI selection.

Evidence:
- [Exact-head full suite 43768474012](https://github.com/Barrot-Agent/B-Agent/actions/runs/43768474012)
- [Push fail-closed gate 43768474015](https://github.com/Barrot-Agent/B-Agent/actions/runs/43768474015)
- [Six-manifest dependency audit 43768474026](https://github.com/Barrot-Agent/B-Agent/actions/runs/43768474026)

The six-manifest audit covered root runtime, development, supplemental integrations, Hugging Face Space, legacy and PEP 621 dependencies; pip-audit reported no known vulnerabilities. The fail-closed gate passed.

PR-event checks on the same head:
- [PR CI 43768476667](https://github.com/Barrot-Agent/B-Agent/actions/runs/43768476667): Pages build-only validation passed; core and full-suite jobs were skipped by the integration-branch condition.
- [PR dependency audit 43768476648](https://github.com/Barrot-Agent/B-Agent/actions/runs/43768476648): passed.
- [PR fail-closed gate 43768476665](https://github.com/Barrot-Agent/B-Agent/actions/runs/43768476665): passed.

The authoritative full-suite result is the push-triggered run 43768474012, not the skipped PR-event job.

**Current main CI:** [43767370808](https://github.com/Barrot-Agent/B-Agent/actions/runs/43767370808) passed on main SHA `1f30e5c...`: 848 passed, zero failed, one skipped and eight subtests passed. Main's current suite is materially smaller than the successor's full repository suite.

### Workflow and side-effect review

All 48 changed workflow diffs were enumerated. Fourteen high-impact workflow definitions and their principal execution boundaries were inspected in content.

Verified containment:
- Ask Barrot, Audio Ingest, Barrot Agent, Barrot Sync, Ping-Pong, self-upgrade, self-benchmark, Databricks bundle and Hugging Face sync legacy writers/deploy paths are quarantined or disabled with empty permissions / false job conditions.
- `barrot-ops.yml` is manual, main-only, exact-source-SHA checked and requires explicit per-run approval for Databricks workspace overwrite or Kaggle dataset download. It was not dispatched.
- `deploy-a2a-worker.yml` requires separate YES confirmations for deployment and secret rotation plus exact-main-SHA validation. It was not dispatched.
- `coinbase-paper-trader.yml` is manual, main-only, typed-YES gated, exact-SHA checked, validates persisted position product identity, and publishes artifacts only. It was not dispatched.
- Groq-backed design/discovery/triage/financial/frontier/signal/WebMCP workflows are manual, require explicit YES and exact main SHA, use read-only repository permissions and publish artifacts. No external-model workflow was dispatched.
- `sync-self-hosted-brain.yml` is hard-disabled. No Hugging Face Space was restarted or deployed.
- `xrp-public-ingestion.yml` schedules hourly and daily, is main-ref guarded, uses actions/contents read permissions, restores only prior artifacts, and publishes 90-day GitHub artifacts plus cache. It is not WORM storage and has not run on main because it is not merged.
- No Databricks write, Kaggle download/submission, deployment, secret rotation, paper trade, external-model data transfer or repository write occurred.

The workflow review is not a complete semantic review of all called scripts and all 1,276 changed paths. The remaining code/research/test review is still a merge blocker.

### Current main OpenCode PAT configuration

Main commit `1f30e5c...` changes `opencode.json` to send `Authorization: Bearer {env:GITHUB_MCP_TOKEN}` and disables OAuth. Main README/AGENTS/MEMORY describe the token as already stored in the OpenCode service environment. No OpenCode `/mcps` health result or successful test request was available to verify that claim or its token scope. The successor README correctly labels the OpenCode GitHub MCP connection **unverified until a health check and test request succeed**. The ChatGPT GitHub connector is authenticated, but its repository permission snapshot remains admin/maintain/push/pull/triage and is overprivileged. Do not equate the ChatGPT connector with a tested OpenCode PAT connection.

### Fresh XRP market and derivatives observations — descriptive only

Capture time: 2026-11-15T22:32:23Z. These web/API-rendered observations have **no byte-exact raw-payload SHA-256 receipts** and are not model eligible.

**Spot**
- OKX XRP-USDT provider timestamp: 2026-11-15T22:21:21.864Z; age at capture 661.136 seconds. Last 0.9679, bid 0.9677, ask 0.9678; best-level bid size 106.404113 XRP and ask size 9,345.405602 XRP; 24h volume 64.372M XRP; rolling 24h open 0.9104, high 0.9795, low 0.8929; UTC-day open 0.9145; UTC+8 open 0.9579.
- Kraken XRP/USD: last 0.96926, bid 0.96920, ask 0.96921; 24h volume 47.456M XRP; event timestamp not supplied. Best-level sizes were 114 XRP bid and 1,582 XRP ask.
- OKX USDT-USD provider timestamp: 2026-11-15T22:00:28.065Z; age 1,914.935 seconds; last 0.99959. Same-venue timestamp skew against the XRP-USDT quote is **1,253.799 seconds**, exceeding the 60-second normalization gate. USD normalization is rejected.
- The cross-venue mid difference is roughly 15 basis points, but the observations are stale/unsynchronized and Kraken supplies no event timestamp. It is not an arbitrage signal.
- Bybit spot ticker returned HTTP 403 through this retrieval route. OKX and Kraken depth endpoints were inaccessible in this pass. The displayed top levels are not full-depth liquidity.

Primary endpoint references:
- [OKX XRP-USDT ticker](https://www.okx.com/api/v5/market/ticker?instId=XRP-USDT)
- [Kraken XRP/USD ticker](https://api.kraken.com/0/public/Ticker?pair=XRPUSD)
- [OKX USDT-USD ticker](https://www.okx.com/api/v5/market/ticker?instId=USDT-USD)

**Derivatives provider disagreement**
- Liqwall, stated update 20:12 UTC: XRP $0.9617; open interest about $1.01B, down 4.5% over 24h; average funding −0.0007%/8h; liquidations $28.4M ($24.2M longs, $4.2M shorts); 72.7% of Binance XRP-position accounts long.
- TradRadar, stated update 16:00 UTC: XRP $0.9548; open interest $1.33B across seven exchanges, down 6.53%; funding −0.0027%/8h; liquidations at least $37.51M ($33.87M longs, $3.65M shorts); long/short ratio 3.14 (75.9% long).
- These provider universes, update times and liquidation coverage differ. Preserve both; do not average. Long-heavy liquidations and negative funding support a deleveraging hypothesis, not a directional forecast.

Sources: [Liqwall](https://liqwall.com/coins/xrp) · [TradRadar](https://tradradar.io/markets/xrp).

**ETF flow disagreement**
- XRP Insights, settled Nov 6–13 holdings-change method: −6.1M XRP (approximately −$6.5M), 1.19B XRP held and $1.22B AUM. Nov 13 daily change +3.4M XRP. GXRP is excluded from flow while its holdings remain in totals because a scrape block/catch-up issue remains.
- XRP Insights' Nov 14 wallet snapshot reports 22.26B XRP in attributed exchange wallets. Across 23 exchanges with unchanged tracked wallet sets, same-wallet balances increased 25.7M XRP over Nov 7–14; Binance is excluded because its tracked wallet set changed. This is not beneficial ownership, tradable float or a cash-flow measure. The earlier Run171 −97.9M XRP seven-day observation has a different exchange universe/coverage and is not silently overwritten.
- Alpha Finance, five-fund/SoSoValue-style series through Nov 13: weekly −$19.1M; Nov 9 −$10.4M, Nov 10 −$7.6M, Nov 13 −$1.1M, with zero entries on missing sessions. XRP Macro/CoinGlass prints match the SoSoValue values to the decimal; they are not independent confirmation.
- CryptoKeyhole reports Nov 13 partial −9,967 XRP from three of four funds while awaiting XRPZ; Nov 12 was a complete +4,337,131 XRP. Its Nov 16 issuer-file row shown as read Nov 14 is temporally impossible and remains quarantined.

Sources: [XRP Insights](https://xrp-insights.com/news/xrp-supply-report-2026-11-14) · [Alpha Finance](https://alphafinance.io/etf/xrp/) · [XRP Macro](https://xrpmacro.com/brief/b2f4c6d8-1113-4a11-9e13-20261113a0e1) · [CryptoKeyhole](https://cryptokeyhole.com/etf-flows/xrp/).

### Institutional relationship confirmations

- Ripple's October 28 Coinbase announcement confirms RLUSD distribution on Coinbase Prime, Exchange and Retail across XRPL, Base and Ethereum. Coinbase Global Exchange collateral support was described as a future follow-up, not as already live. This is RLUSD distribution, not evidence that XRP is required for every settlement. [Ripple primary announcement](https://ripple.com/ripple-press/ripple-and-coinbase-partner-to-expand-access-to-rlusd/).
- Ripple/BNY's October 27 announcement confirms BNY custody support for XRP and RLUSD. Tokenized trade-finance use cases are exploratory, not verified production throughput or BNY proprietary XRP buying. [Ripple/BNY primary announcement](https://ripple.com/ripple-press/ripple-expands-collaboration-with-bny-across-custody-and-tokenized-trade-finance/).
- No new primary-source correction to SBIC East/Central/West versus SBI Holdings, ASK Coin, “actual capital,” or Kamilah/Camilla Stevenson identity was established in this run. Existing identity decisions remain: regional SBIC entities are distinct from SBI Holdings; no canonical XRPL ASK issuer or OpenAI/SBIC commercial partnership is verified; “actual capital” is not a standardized XRP metric; Kamilah person identity is verified but candidate YouTube channel ownership remains unverified.

### Prediction readiness — current files re-read

- `research/xrp_intelligence/event_registry_current.json`: 85 events, 64 independence groups; 42 verified, 42 provisional, one disputed; **85/85 lack raw_source_sha256** and **43/85 lack publisher publication timestamps**.
- `web/latest_signal.json`: `NOT_ISSUED`; data cutoff, target, horizon and probabilities are null.
- `web/signal_accuracy.json`: `NOT_EVALUATED`; fixed-horizon OOS accuracy is null; the legacy variable-horizon percentage is invalid.
- The primary mission manifest remains priority 1 and active on the successor.
- The implemented engine includes 51 public-source definitions, 49 scheduled definitions, SHA-256 receipt-chain prototype, point-in-time SQLite feature store, event timeline/counter-hypotheses, four baselines, purged/embargoed walk-forward evaluation, paired block bootstrap, calibration, drift monitoring and a fail-closed forecast ledger.
- Still missing: byte-exact receipts, independent WORM/trusted timestamps, synchronized historical multi-venue data, qualified candidate superiority against all four baselines, and independent shadow outcomes. Scheduled ingestion is not verified on main.

**Forecast: NOT_ISSUED. Accuracy: NOT_EVALUATED.** No directional forecast, paper trade or real-money action.

### Nine-platform and PR governance

| Platform | Current verified state |
|---|---|
| ChatGPT | Current GitHub connector authenticated; repository permissions overprivileged |
| Claude | Unverified |
| Grok | Unverified |
| Gemini | Unverified |
| Copilot | One-off review activity; no formal approval |
| Codex | Unverified |
| Hugging Face | Previous BUILD_ERROR; no verified deployment |
| Kaggle | Untested; no submission |
| Databricks | Previous HTTP 403; no write |

No external-model dispatch, nine-platform evidence exchange or independent red-team quorum occurred.

The current open-PR inventory is **9**, not the older Run173 count of 373: one PR targets main (#1663); eight remain open against separate research/security bases and are preserved as unique/unreviewed or blocked. They are #1541 (MMI claim-identity security; blocked pending credential-owner review), #1460 (institutional multirail/Binance/Kamilah research), #1450 (Binance phase-one/escrow audit), #1440 (archive-validation repair), #1437 (source-addenda repair), #1436 (Binance XRP theft graph), #1353 (ledger shard migration) and #1265 (index-pointer migration). No source PR was closed.

PR #1663 has zero formal reviews, zero approvals and zero review threads. CodeRabbit reports draft PRs are not automatically reviewed. It remains draft and must not be merged.

### Security, merge blockers and preservation

- Main branch-protection read returned HTTP 403. The visible fallback ruleset 10863829 is disabled. Required protection contexts and independent approval requirements cannot be verified through this connection.
- Repository connector permission snapshot remains admin/maintain/push/pull/triage; least privilege is unresolved.
- The eight remaining open PR branch tips were previously found to contain the same tracked 216-byte `.config/gh/hosts.yml` blob (Git blob SHA `f58b27f14436088db99662d3a45c59b8437ec3a1`). Its contents were not read; it is absent from current main and successor. This is a potential credential exposure, not a confirmed compromise. The eight branches remain preserved. Provider-side revocation is unverified.
- `scripts/self_benchmark.py` previously showed Groq-generated Python execution through subprocess without a restrictive environment/network/filesystem sandbox. Its successor workflow is quarantined; do not re-enable until sandboxing is verified.
- The current nine-platform map remains a Run173 snapshot; its repository-state fields need a Run176 refresh. The full 1,276-path semantic review and remaining called-script review are incomplete.
- The three executable-mode differences listed above require disposition.
- Main's OpenCode PAT configuration is not a verified connection; no token value was read or exposed.

**NO MERGE.** Exact-head CI is green, but draft state, zero independent reviews/approvals, incomplete semantic review, three mode differences, overprivileged connector access and inaccessible branch-protection details remain blockers.

### Run176 next concrete actions

1. Refresh the nine-platform map's repository-state section to main `1f30e5c` and successor `9c69f1a`, without claiming untested provider connections.
2. Complete semantic review of all 1,276 changed paths, prioritizing the 48 workflows, their called scripts, the 169 divergent shared blobs and the three executable-mode changes.
3. Obtain independent review and verified branch-protection/required-check evidence; resolve least-privilege connector access.
4. Preserve the eight unique research/security PRs; do not close them.
5. Capture byte-exact source receipts for the 85 event records, resolve missing publisher timestamps and establish independent WORM/trusted timestamp anchoring.
6. Verify scheduled XRP ingestion only after a compliant merge to main and then verify the main-run artifacts.
7. Do not train/issue a directional candidate until the OOS and independent shadow policy passes.

No main-branch write, merge, deployment, secret rotation, Space restart, external-model transfer, Databricks write, Kaggle submission/download, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or source-PR closure occurred.
