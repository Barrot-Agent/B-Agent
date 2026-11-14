# BARROT SYNC — canonical coordination and safety record
# This file records repository state. It is not proof of provider authentication or data flow.

## Identity
- Intended model gateway: LunaRoute / GLM. Authentication, permissions, and data flow remain UNVERIFIED.
- Canonical repository: github.com/Barrot-Agent/B-Agent.
- Barrot V3 is the protected execution, orchestration, authorization, and verification foundation.
- XRP intelligence and prediction-engine mastery is the highest-priority mission.

## Secrets and providers
- Secret names may appear in workflow configuration; values must never be copied into chat, logs, source files, or research artifacts.
- Presence and validity of LunaRoute, Groq, Hugging Face, Databricks, Kaggle, and GitHub credentials are NOT VERIFIED unless a provider-specific authentication test records the exact endpoint, scope, time, and result.
- No external model may receive repository context or user data without explicit, action-specific authorization.
- Do not claim a live connection based on a configured URL or environment-variable name.

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

