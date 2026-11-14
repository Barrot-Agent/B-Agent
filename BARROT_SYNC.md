# BARROT SYNC — canonical coordination and safety record
# This file records repository state. It is not proof of provider authentication or data flow.

## Identity
- Intended model gateway: LunaRoute / GLM. Authentication/data flow NOT VERIFIED; permissions and endpoint scopes also remain UNVERIFIED.
- Canonical repository: github.com/Barrot-Agent/B-Agent.
- Barrot V3 is the protected execution, orchestration, authorization, and verification foundation.
- XRP intelligence and prediction-engine mastery is the highest-priority mission.

## Secrets and providers
- Secret names may appear in workflow configuration; values must never be copied into chat, logs, source files, or research artifacts.
- Presence and validity of LunaRoute, Groq, Hugging Face, Databricks, Kaggle, and GitHub credentials are NOT VERIFIED unless a provider-specific authentication test records the exact endpoint, scope, time, and result.
- No external model may receive repository context or user data without explicit, action-specific authorization.
- Do not claim a live connection based on a configured URL or environment-variable name.

## Verification status and synchronization preflight
- The presence/validity in GitHub Secrets is NOT VERIFIED. A configured secret name does not prove that a value exists, is current, or authenticates successfully.
- provider-side OAuth revocation is NOT VERIFIED. No provider-side revocation request or response was observed.
- The synchronization path depends on both `httpx` and `rich`. The last observed main-branch sync attempt failed because `rich` was missing; the safe outcome is `sync skipped`, and no sync commit was produced.
- No automatic external sync or push without explicit approval. Keep the integration sync workflow quarantined until dependency preflight, authentication, scope, and write authorization are independently verified.

## Hard rules
- Keep unverified remote MCP servers disabled and tool permissions ask/deny by default.
- No automatic external sync, repository push, deployment, secret rotation, Space restart, Databricks write, Kaggle submission, paper trade, funds transfer, or real-money action without the specific approval required for that exact operation.
- Never write directly to main from an autonomous repair loop. Use an isolated feature branch, preserve the worktree, and require review and normal branch protection.
- Never force-push, rewrite history, reset, clean, stash, or restore over user work.
- Never re-add Orbit. Preserve the Orbit removal record.
- Do not alter the Orbitron font in hf_space/app.py:556-561 without a separate reviewed requirement.
- Never commit local OAuth credential files such as .config/gh/hosts.yml.
- Keep the legacy council bridge quarantined; only Barrot V3 authorization gates may permit controlled actions.

## Operating protocol
1. Read this file and BARROT_XRP_MISSION_HANDOFF_LATEST.md before acting.
2. Inspect current main, the complete repository tree, all open PRs, ancestry, overlapping paths, workflow runs, dependencies, security settings, and current integration state.
3. Maintain one coherent integration workstream. Search existing PRs before creating branches or PRs. Preserve unique source work.
4. Keep external effects disabled unless separately authorized. Record source, timestamp, permissions, approval, and exact SHA for any approved operation.
5. Use point-in-time, provenance-preserving evidence. Preserve disagreement, source dependence, counter-hypotheses, and disconfirming evidence.
6. Run the full repository suite and security gates on the exact proposed head. Do not substitute results from another commit.
7. Report DESIGNED, EXECUTED, and VERIFIED separately. Never claim completion from a plan, draft PR, or unverified workflow result.

## Current integration record — Run133
- Main SHA: ef41ea7d8f1d236774c3e593bc6205bf42555351.
- Existing integration head before reconciliation: 1a455ef55037693129ab814c657b42deb451d025.
- PR #1662 was 32 commits behind main, draft, and reported mergeable=false before this run's reconciliation work.
- Main contains 32 newer commits, including MCP synchronization, SHRM 2.0, import repairs, Kaggle import-safety changes, OpenCode V2 migration, and producer-mode assets. These must be preserved.
- Twenty-six overlapping paths were reconciled in merge commit 96d578d: two retain main's v7 workflow updates, eight use explicit merged files, and sixteen retain integration's stronger safety versions. Main's non-overlapping changes remain preserved.
- Exact-head integration full suite on 1a455ef: 3,641 passed, 8 subtests passed, 0 failures, 62.47% inclusive coverage; wheel build and installed primary mission verification passed (run 43614686958). On corrected merge head 9f36a46, core tests passed; the broader full suite is still running.
- Main CI on ef41ea7: 784 tests passed, 75.25% coverage (run 43610729541). This is not a substitute for the broader integration full suite.
- Main Pages build run 43610728772 failed: Liquid syntax error in GLOBAL_STATE_MANIFEST.md line 6456, caused by unescaped JSON/template braces. No deployment was verified.
- Main Barrot Sync run 43610729676 reported workflow success while b_agent.py --sync failed with ModuleNotFoundError: rich. The workflow masks the failure with || echo and masks push failure with git push || true; its log ended with Everything up-to-date. No successful LunaRoute sync or sync commit was verified. The displayed banner contained no secret characters.
- The main sync workflow still triggers on main pushes and has repository write permission; the integration version quarantines it.
- Main's 32 newer commits and their history are preserved as the first parent of merge commit 96d578d; the previous integration head is its second parent. The corrected current integration head is 9f36a46.

## XRP ingestion and execution boundaries
- The integration XRP ingestion workflow is scheduled hourly and daily, runs only on main, and requests actions:read / contents:read. It captures allowlisted public HTTPS sources, stores SHA-256 receipts, feature-store checkpoints, event timelines, and 90-day GitHub artifacts. It does not write repository files or push to main.
- GitHub Actions artifacts/cache are not independent WORM storage or trusted timestamp anchoring.
- The ingestion workflow has not been verified as executing on main because the integration remains unmerged.
- The Coinbase paper-trader workflow is manual, exact-main-SHA-bound, explicit-YES-gated, product-identity-checked, and artifact-only. It was not dispatched.
- Databricks workspace import and Kaggle dataset download are separate manual approvals in barrot-ops.yml. No such operation was approved or executed.
- Repository repair pushes are restricted to non-protected task branches and require watchdog authorization. No force push is implemented in the reviewed push path.
- The executor uses command allowlisting and workspace-path checks; file deletion requires an exact preimage. No repair or external write was executed in this run.

## Main-branch work preserved
- Main's 11 import repairs, including mcp_orchestrator and orchestrator_bridge, remain part of the merge parent. The integration mcp_orchestrator must retain its explicit per-action approval gates while using the import-flexibility helper.
- Main's dependency floors, rich/httpx declarations, OpenCode V2 migration, Docker base-image updates, .env.example additions, v_sync_relay.sh hardening, and changelog work must be retained.
- The producer-mode session and five beat assets remain preserved in main history and the integrated tree.
- The main-branch BARROT_SYNC session record is preserved in repository history. Its unsafe legacy operating instructions are superseded by the rules above.

## Next actions
- Complete the existing integration branch's three-way reconciliation against current main and verify the exact merge head.
- Run the full suite, core tests, wheel build, fail-closed gate, and all dependency/security audits on that exact head.
- Resolve the Pages Liquid error before any merge that could publish Pages; obtain the required deployment authorization.
- Correct the main Barrot Sync dependency installation and failure masking before enabling any automatic sync.
- Resolve least-privilege GitHub access, branch protection, independent review ownership, and CODEOWNERS.
- Keep forecast issuance NOT_ISSUED until an XRP-specific candidate demonstrates calibrated out-of-sample superiority and independent shadow outcomes.

## Producer Session - Barrot Beat DNA Vol. 1 (2026-11-14)
- Mission: become producer. Studied 5 producers' TECHNIQUE (not songs), built
  5 starter beats. All verified playable.
- Study phase: 1-page cheat sheets saved to producers/ (web_search MCP):
  * rodney_jerkins_darkchild.md - jerky MPC loops, glide bass, staccato chops
  * timbaland.md - beatbox-first off-grid swing, weird sounds as drums
  * missy_elliott.md - the air IS the instrument; ad-lib pockets reserved
  * black_coffee.md - warm 4-on-floor, velocity-varied shaker, long builds
  * catalyst_afro_carib.md - tresillo/dembow engine, steelpan call-response
- Build phase (scripts/make_beats.py, pretty_midi + numpy synth):
  * tracks/track_01_darkchild_rnb(.mid/.wav/_pattern.txt) 95 BPM F min
  * tracks/track_02_timbaland_futuristic 90 BPM C min
  * tracks/track_03_missy_minimal 100 BPM D min
  * tracks/track_04_blackcoffee_afrohouse 122 BPM A min (DJ-shaped 8/8/8/4)
  * tracks/track_05_afro_carib_soca 110 BPM A maj
  * Each: drums + bass + pads/chords + melody/pluck + 4-section arrangement
  * tracks/cover.png (LunaRoute image gen + PIL type), tracks/README.md
- Verification: MIDI reload 268-1045 notes, exact tempo events; WAV stereo
  RMS 0.11-0.18; librosa beat-track lock 95.7/123.0/112.3 vs 95/122/110 spec.
- Deps added: pretty_midi, mido, music21, librosa (user site).
- Next step (music): pick a favorite, humanize further, add ghost notes +
  fills, try stems/render per-section, or ship pack to Gumroad pipeline.



## Current integration record — Run135 (2026-11-14)
- Main SHA: `ef41ea7d8f1d236774c3e593bc6205bf42555351`.
- Integration parent before this run's documentation and Pages repair: `9990254412b74e37030ebd077512f3c6c48529d4`; PR #1662 remains the sole consolidated integration workstream.
- Parent exact-head verification: 3,681 passed, zero failed, eight subtests; 62.84% inclusive coverage, 76% legacy core coverage; wheel build and installed mission verification passed; six-manifest dependency audit and fail-closed gate passed (runs 43625793304, 43625793294, 43625793314). New Run135 head requires its own exact-head cycle.
- Main tree 1,341 entries; integration tree 2,406 entries. Branch ancestry 2,414 ahead, zero behind. Open PR inventory 373 (361 drafts, 12 non-drafts; 365 target main, eight other bases).
- Main Pages build failure is confirmed from job logs: Liquid syntax error at GLOBAL_STATE_MANIFEST.md:6456 due JSON braces inside fenced code. Integration wraps the two affected code blocks in Liquid raw tags and adds a regression test. Main is unchanged; no Pages deployment was triggered.
- Main Barrot Sync run 43610729676 reports workflow success but the step fails on missing `rich`; the workflow masks the error and push failure. Integration keeps automatic sync quarantined.
- Main push_with_token.sh still passes GH_TOKEN through validation argv; integration uses stdin and unexports GH_TOKEN during validation. No real token was used or rotated.
- Latest XRP snapshot: OKX $0.9587 (18:39:41.569Z), Bybit $0.9558 (19:02:06.653Z, -6.44% 24h), Kraken $0.95802 (no event timestamp). OKX/Bybit top levels were ask-heavy; Kraken was nearly balanced. No full synchronized L2 was admitted.
- Liqwall 18:42Z: $24.3M XRP liquidations, 97% long; OI $1.05B (+0.9% 24h), average funding -0.0008%/8h, Binance funding +0.0011%; Binance accounts 74.2% long, Hyperliquid accounts near balanced/slightly short. Other OI vendors differ materially in universe and timestamp; no averaging.
- XRPL own-node roll call 18:50Z: 34/35 validators heard; SingleAssetVault 23/28 including carry, LendingProtocol 22/28, V1_1 22/28; zero Majority entries and zero activation countdowns. Native lending remains inactive.
- Alpha Finance five-fund ETF series through Nov 13: -$1.1M daily, -$19.1M seven sessions, -$581.7K 30 sessions; cumulative net flow $1.71B since Nov 14 2025. It does not publish holdings/AUM; do not infer XRP balances. XRP Insights' Nov 13 row is provisional and has a different universe.
- Ripple official RLUSD page as of Nov 12: $2.6899B circulating, $2.8265B reserves; latest linked CPA attestation is September.
- Forecast remains NOT_ISSUED; accuracy NOT_EVALUATED. No trained XRP candidate or independent shadow cohort is verified. No paper trade or real-money action.
- PR #1662 remains draft, zero approvals/reviews/threads. Main branch-protection details return HTTP 403; fallback ruleset 10863829 is disabled; CODEOWNERS is self-owned; connector permissions remain admin/maintain/push/pull/triage. NO MERGE.


## Run135 institutional/stablecoin and verification addendum
- Exact head `f7d990fd3585197d223da01b6534b35a68fe0443`: full suite 3,682 passed, zero failed, eight subtests; 62.84% inclusive coverage; wheel and installed mission passed; six-manifest dependency audit and fail-closed gate passed (43630374913, 43630374830, 43630374819). This is parent-head evidence; the next CI/Jekyll validation commit needs its own run.
- Circle Arc public mainnet launched Sep 16; USDC gas, permissioned validators, SBI Group founding validator, Coinbase exchange access, BNY institutional participation, Aave/Morpho lending. Adjacent/competing stablecoin rail; no XRP settlement requirement established.
- Circle SBI Japan K.K. is 50/50; Circle controls/consolidates, SBI noncontrolling. Circle Q3 10-Q reports $331.3M Q3 and $986.6M nine-month USDC distribution costs paid to Coinbase.
- SBI VC Trade RLUSD supports Ethereum only at launch; Coinbase RLUSD supports XRPL/Base/Ethereum. Coinbase/PNC pilot uses USDC and 1:1 USD conversion, not XRP.
- SBIC East/Tokyo, Central/Nagoya and West/Osaka are three separate regional investment companies and sister companies; no primary evidence links them to SBI Holdings. SB OAI Japan is the separate OpenAI/SoftBank joint venture.
- Global stablecoin supply (Glassnode 11-asset basket) contracted $14.2B over 30 days to Nov 11. ChainReport's live DefiLlama-based XRPL scoreboard reports $841M stablecoins, -13% 7d/-26% 30d; RLUSD $764M, -14% 7d/-28% 30d. Stableradar's older Nov 12 on-chain snapshot reports 863.8M RLUSD on XRPL; Ripple issuer page reports $2.6899B total circulating and $2.8265B reserves Nov 12. These vintages/definitions are not reconciled; do not average.
- New PR-only Jekyll build validation is added to `.github/workflows/ci.yml`; it builds but does not upload or deploy. The raw-block fix and static test passed on parent f7d990; the new Jekyll job is pending.
- Forecast NOT_ISSUED; accuracy NOT_EVALUATED. No paper trade or real-money action.


## Run137 — main advance and ping-pong refinement safety reconciliation
- Main advanced to `f1708870fcde80a01d14509609affc558e5cc065`. Its ping-pong
  refinement engine, deterministic adapter, optional LunaRoute adapter, CLI,
  tests, usage guide and JSONL log are preserved in this integration merge.
- The committed `ping-pongings/knowledge-base/refinement_log.jsonl` records
  historical LunaRoute model responses from 18:56 to 20:01 UTC. This proves
  prior endpoint calls, not provider retention terms, ownership, permissions,
  source classification or authorization for XRP data. Payloads are absent,
  so their exact contents cannot be reconstructed.
- Main's original `refine_data` and CLI defaulted to live LunaRoute models
  whenever `LUNAROUTE_API_KEY` existed and silently truncated payloads to
  24,000 characters. Integration changes this to offline-by-default,
  explicit data classification, immutable-data rejection, dual opt-in for
  external calls, secret-like payload blocking and reject-not-truncate size
  limits. LunaRoute is outside the nine-platform map and is not authorized
  for XRP data transfer.
- Main Barrot Sync run `43635426753` attempted `b_agent.py --sync` but
  failed before synchronization: `ModuleNotFoundError: No module named 'rich'`.
  The workflow suppressed the failure with `|| echo`; the push reported
  `Everything up-to-date`. Green conclusion does not mean successful sync.
- Main CI `43635426745`: full repository suite 810 passed, eight subtests;
  core suite 485 passed, eight subtests. Main Pages `43635426265` failed
  Liquid parsing in `GLOBAL_STATE_MANIFEST.md`; deploy was skipped.
  Auto-PR check `43635426704` passed without creating a PR.
- No LunaRoute call, secret read/rotation, external publication, deployment,
  Databricks write, Kaggle submission, paper trade or funds action occurred
  in this integration run. Forecast NOT_ISSUED; accuracy NOT_EVALUATED.

## Run141 — current main reconciliation and producer-asset rights review (2026-11-14)

- Current main: 0d05b59a037f4ad4b0c345ee6e8c1c442d25fa2e; integration head before reconciliation: 2a2dade5c3ffb869daf349ea3dd653332b387500.
- Main advanced five commits from PR base f1708870. Across 48 changed paths, six overlap and 42 are main-only. The two Ping-Pong refinement commits, producer reference-acquisition log, 24 one-shot assets and subsequent producer-session sync addendum are preserved.
- Main commit 0d05b59 added 12 lines to BARROT_SYNC.md documenting the producer reference-acquisition and one-shot kit. The associated Barrot Sync job still failed at b_agent.py --sync because rich was missing; shell fallback and git push suppression masked the failure. Its auto-commit logged the producer addendum; it did not prove the Barrot Sync operation succeeded.
- The producer reference-acquisition log says LunaRoute MCP was connected and web_search used, but the same record says OpenCode exposed zero MCP servers/resources. Authentication, permission scope and end-to-end data flow were not independently verified in this run. Treat the connection as unverified; no external task or XRP data was dispatched.
- The 24 one-shot files are preserved. The upstream smpldsnds/drum-machines README calls its collection public domain, but GitHub license metadata is null and there is no separate LICENSE file or per-file provenance. The 15 converted samples therefore have provisional rights status, not a verified blanket license. The nine synthesized files are described as original, but the import commit lacks the generator source and reproducible build receipt. The corrected tracks/kits/pd/README.md records these limits; do not redistribute or commercialize until rights and generation provenance are verified.
- Integration Ping-Pong remains offline by default. External refiners and judges require caller opt-in, BARROT_ALLOW_EXTERNAL_REFINEMENT=1, BARROT_LIVE_REFINEMENT_APPROVED=1, eligible public classification, matching adapter and valid key. The live verification driver and optional live test also require BARROT_LIVE_REFINEMENT=1. Immutable XRP evidence is excluded.
- Main full-suite run 43649006834 is still in progress; core tests passed. The previous main full-suite run 43648252959 passed 848 tests, one skipped, eight subtests, but it is not exact-head evidence for 0d05b59. Main Pages run 43649006105 failed Liquid parsing at GLOBAL_STATE_MANIFEST.md:6456.
- Main Barrot Sync run 43649006881 reports success, but its job log shows ModuleNotFoundError: rich, the sync command skipped, and git push || true returned Everything up-to-date. This is a confirmed false-green. Integration keeps automatic sync quarantined.
- Main branch-protection inspection returns HTTP 403; fallback ruleset 10863829 is disabled; integration is unprotected; CODEOWNERS is self-owned; GitHub connector permissions include admin/maintain/push/pull/triage. PR #1662 remains draft with zero approvals/reviews/threads. NO MERGE.
