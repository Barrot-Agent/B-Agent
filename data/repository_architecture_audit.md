# Repository Audit — Structural Review (File-Listing Evidence Only)

## Scope and limitations

What I received is a single file listing that **begins mid-entry** (`s/v3_acceptance_matrix/case-26.json` — almost certainly a truncated `.barrot/collaboration_records/...` path) and contains **no file contents**. Everything below is derived from names, paths, and counts only. Where I infer, I say so. I cannot verify code quality, workflow logic, test status, or secret exposure from names alone.

Notably, the listing contains **almost no application source code** (no `src/`, no top-level `*.py` outside `.barrot/`, no `pyproject.toml`/`requirements.txt`/`package.json`). Either the listing is incomplete or source lives elsewhere. This audit therefore covers repo governance and meta-structure, not the actual software architecture.

## Inventory (facts from the listing)

| Item | Count / observation |
|---|---|
| GitHub Actions workflows | ~86 files, of which 8 carry a `.disabled` suffix |
| Top-level Markdown docs | ~45, predominantly status/summary-style (`*_SUMMARY.md`, `*_COMPLETE.md`, `*_RESPONSE_*.md`) |
| `.barrot/` state directory | Acceptance-matrix records (cases 26–30 only), 4 disabled test files, execution ledger (`.jsonl`), identity/manifest/registry JSONs, 2 Python scripts |
| CI systems | Both `.gitlab-ci.yml` and GitHub workflows present |
| Committed personal environment files | `.bashrc`, `.gitconfig`, `.config/gh/config.yml`, `.termux/termux.properties`, `.termux_dna_harvest.log` |
| Governance artifacts present | `SECURITY.md`, `CODEOWNERS`, `dependabot.yml`, `.pre-commit-config.yaml`, `dependency-audit.yml`, `barrot-transparency-audit.yml`, `LICENSE` |

## Findings

| # | Severity | Evidence | Concern | Verify by |
|---|---|---|---|---|
| 1 | **High** | `barrot-self-upgrade.yml`, `autonomous_self_deployment.yml`, `barrot-approve-pr.yml`, `barrot-pr-automerge.yml`, `barrot-merge.yml` | A self-modification loop combined with automated PR approval/merge is the highest-risk pattern in any repo: a buggy or manipulated workflow can merge its own changes without human review | Read all five workflow files; check permissions blocks, branch protection assumptions, and whether approval is human-gated |
| 2 | **High** | `.bashrc`, `.gitconfig`, `.config/gh/config.yml`, `.termux/*` committed at repo root | Personal dotfiles in version control frequently leak tokens, host aliases, or history. `gh` config in particular warrants a secrets scan | Inspect contents; run `git log` on these paths; rotate any exposed credentials |
| 3 | **High (hypothesis)** | `.barrot/disabled_tests/test_email_integration.py`, `test_transformative_insights.py`, `test_merge_conflict_integration.py`, `test_longevity_modules.py` — names correspond to root docs claiming completion (`EMAIL_FEATURE_SUMMARY.md`, `TRANSFORMATIVE_INSIGHTS_IMPLEMENTATION_SUMMARY.md`, `MERGE_CONFLICT_RESOLUTION_GUIDE.md`) | Pattern suggests features documented as delivered while their tests were disabled rather than fixed. This is a claim-vs-verification gap | Diff each disabled test against the corresponding feature code; check CI for whether these paths are excluded |
| 4 | **Medium** | ~78 active workflows for one repo, including near-duplicates (`diag-cf`/`diag-cf2`, `barrot-merge`/`barrot-merge-manual`, `barrot-auto-pr`/`barrot-pr-automerge`, and `barrot-pr-automerge.yml` existing **both enabled and disabled**) | Workflow sprawl: expanded attack surface, Actions-minutes cost, unclear which path is authoritative | Map triggers (`push`/`schedule`/`workflow_dispatch`) per workflow; identify dead ones |
| 5 | **Medium** | `capability-1`, `capability-9`, `capability-10` workflows present; `capability-2`–`8` absent | Numbering gap suggests removed or never-committed siblings; relevant if "capability" workflows are referenced by the agent's registry | Check `.barrot/target_registry.json` for references to missing capabilities |
| 6 | **Medium** | `.gitlab-ci.yml` alongside GitHub workflows | Dual CI risks divergent pipelines (different gates on different platforms) | Compare job sets and gate strictness |
| 7 | **Medium** | `dump-brain-corpus.yml`, `sync-self-hosted-brain.yml`, `sync-huggingface.yml`, `rotate-databricks-token.yml` | Data-egress and credential-rotation automation; destinations and secret scoping unverifiable from names | Audit target endpoints, token scopes, and least-privilege on the `GITHUB_TOKEN`/PATs used |
| 8 | **Medium** | `.barrot/` contains `repository_identity.json`, `repo_state_manifest.json`, `barrot_self_repair.py`, `barrot_generated_practice.py` | An agent maintaining its own model of the repo inside the repo. If workflows read these files as input to merge/deploy decisions, the state files become a trust boundary | Trace which workflows consume these JSONs |
| 9 | **Low** | ~45 status/summary Markdown files at root; no `docs/` visible | Root pollution; "implementation complete" docs are unverified claims, not documentation | Move to `docs/`; mark each as generated artifact |
| 10 | **Low** | `.termux_dna_harvest.log` committed | Log files in VCS; may contain runtime data | Remove, gitignore |
| 11 | **Info** | Acceptance matrix shows only cases 26–30 | Cases 1–25 either truncated from the listing or archived elsewhere | Obtain full listing |

## Positive controls observed

`SECURITY.md`, `CODEOWNERS`, Dependabot, pre-commit hooks, a dependency-audit workflow, and a self-described transparency-audit workflow all exist. Their effectiveness cannot be assessed from names.

## To complete this audit, I need

1. The **untruncated full listing** (entries before `.barrot/` are missing — including, critically, whether a real `.env` is committed).
2. Contents of the five workflows in Finding 1.
3. Contents of `.barrot/repository_identity.json`, `repo_state_manifest.json`, and `mmi_execution_ledger.jsonl` (tail).
4. The four disabled test files and their corresponding feature code.
5. `.gitignore` (to distinguish intentional exclusion from omission).

I have not characterized what "Barrot," "MMI," or the "orbit" subsystem actually do — the names alone don't support those claims, and I won't invent them.

## Current-state correction — 2026-11-10 22:15 UTC

This report is a historical first-pass audit based on an explicitly truncated path listing. It is not a complete or current repository inventory.

Verified current tree facts:
- Main tree at `afb3024fbcb976db5acdf52b85e253ff46859ce6`: 1,404 entries, including application packages, tests, project metadata and GitHub workflows.
- XRP/V3 integration tree before this correction: 2,254 entries.
- `.config/gh/hosts.yml` is absent from current main and integration trees.
- The same path remains in 17 specifically inspected open PR branch trees. The 17-branch check is targeted, not exhaustive across every open PR.
- File contents were not inspected. Treat the path as a potential GitHub CLI credential exposure; the owner must revoke/reissue if the file held a live token. No credential value is reproduced and no secret operation was performed.

Do not interpret the truncated listing's missing `src/`, tests or package metadata as evidence that the repository lacks application source. The full Git tree contradicts that inference.


## Run 11C correction — 2026-11-10T23:13:57Z

This addendum supersedes earlier statements in this audit that described the GitHub CLI authentication file as present in the current main tree.

- Current main SHA: `afb3024fbcb976db5acdf52b85e253ff46859ce6`.
- Verified integration code head before this documentation update: `bb11b44d9db1ba5811d1039f2c3055e832c41664`.
- `.config/gh/hosts.yml` is absent from the current main and active integration trees.
- The path remains present in 17 inspected open pull-request head trees: 14 non-draft source branches and three drafts. The historical Git object remains reachable. No file contents or credential value were read or reproduced.
- The credential owner must revoke and reissue the exposed credential. Removing the path from main and the integration branch does not invalidate it. No secret was rotated or revoked in this run.
- Main's `b_agent.py` still contains direct GitHub write/branch/commit/merge methods and a `--auto-merge` option. The integration version removes remote write/merge operations, uses a read-only GitHub client, and requires explicit consent before LunaRoute data transfer.
- Main's Coinbase paper-trader workflow is manual but has no explicit confirmation input and pushes state/log changes to main. The integration version requires `confirm=YES` and an exact main SHA, has read-only repository permissions, and uploads evidence artifacts only. No paper simulation was run.
- Main's A2A worker and self-hosted-brain workflows include push-triggered deployment paths. Integration versions require manual dispatch, exact-main-SHA validation and separate secret-rotation confirmation. No deployment or rotation was run.
- Main's `web/latest_signal.json` remains dated October 29, 2026 with confidence zero; its landing page still advertises a paid trading-signal service. The integration branch uses `NOT_ISSUED` and research-only presentation. GitHub Pages publication is an automatic main-branch side effect and remains unauthorized for this integration.
- All 44 workflow files changed by PR #1660 were reviewed for triggers, permissions, external transfers, repository writes, deployment, secret rotation and confirmation gates. High-risk legacy workflows are quarantined or replaced with read-only/artifact-first or exact-SHA/manual-confirmation flows. Remaining sensitive manual actions were not executed.
- The integration local-repair CLI now requires a clean, named, non-default feature worktree and rejects dirty/untracked worktrees, detached/default branches, protected paths (.git, .config/gh, secrets/credentials, .env), symlinks and untracked repair targets. Seven regression tests were added and passed on code head `bb11b44`.

This correction is committed on the integration branch only. It does not modify main, revoke credentials, deploy, paper-trade, or change any source PR branch.


## Run 12C — current-main reconciliation (2026-11-11T02:16:41Z)

This addendum records the verified reconciliation between current main and the XRP/V3 integration source branch. It supersedes earlier tree and branch-state counts where they differ.

- Current main: `84f28ee7755607236231545a14f3d093c1baaa85`, full tree `b32aa7701836702fbd2e90b8ef37a09bd31a4fda`, 1,388 entries and 86 workflow files; the recursive tree was fetched without truncation.
- Integration source: `dc34a4aefbbace7c28eac03a77863264f7ad050f`, full tree `9dba85143c6ac06c3b9554c25c48e3bd9c78bbc5`, 2,260 entries and 87 workflow files; the recursive tree was fetched without truncation.
- Common merge base: `afb3024fbcb976db5acdf52b85e253ff46859ce6`. Integration is 1,963 commits ahead and 3 commits behind current main. PR #1660 is therefore stale and not mergeable at its recorded base.
- Current main commits after the common base: `64dc43b` (Ditch Orbit), `7a8fe83` (rewrite this structural audit), and `84f28ee` (add BARROT_SYNC.md). The successor uses current main as its first parent and the integration source head as its second parent.
- The source integration tree reintroduced 15 Orbit path entries, including the `.agents/skills/orbit` subtree and `.barrot/orbit/tools.json`. The current main tree contains only `.barrot/orbit/command_schema.json` and `ORBIT_REMOVED.md` in that area. The successor removes the skill subtree and tools.json, while preserving the mainline command schema, ORBIT_REMOVED.md, and the Orbitron font in `hf_space/app.py`.
- Main's `BARROT_SYNC.md` identifies LunaRoute as the sole brain and says not to re-add Orbit, not to touch the Orbitron font, to use GH_TOKEN via x-access-token only, and not to re-commit `.config/gh/hosts.yml`. It states OAuth is REVOKED. The file is absent from both current main and the source integration tree. Revocation is recorded as owner-maintained state; no credential value or secret-management endpoint was accessed to independently verify revocation.
- The integration `b_agent.py` is retained because it uses the LunaRoute base URL, requires its API key and GitHub token, enforces a clean feature worktree, and contains no direct `merge_pr` or `--auto-merge` operation. The current-main self-identification prompt change is applied without restoring main's legacy merge path. The integration `opencode.json` is byte-identical to main and points to LunaRoute.
- Dependency reconciliation: `requirements.txt` is identical on main and integration. Integration `requirements-dev.txt` adds build/setuptools/wheel and uses pytest >=9.2.0 and types-requests 2.33.0.20261030; these changes are retained. The integration `pyproject.toml` adds branch coverage and package-data configuration; it is retained. No package.json, uv.lock or requirements-test.txt exists at either ref.
- Integration has 11 commits after the previous Run 12B code head, including overlap-adjusted effective sample size, readiness-policy v4, mandatory external-action approval for repository sync, branch/PR creation and issue comments, and associated regression tests. Exact-head full-suite CI is not present for `dc34a4aefbbace7c28eac03a77863264f7ad050f`; the earlier 3,376-pass result on `ac75c046` predates these later code changes and is not treated as current verification.
- Main branch metadata reports protected=true and empty visible required-check contexts; the detailed branch-protection endpoint returns HTTP 403. The only visible fallback ruleset is disabled. Repository metadata permits auto-merge, but no merge was initiated or bypassed. Actions-permission settings are not exposed through the available GitHub connection.
- Open PR inventory: 373 open, 358 drafts, 15 non-drafts. PR #1660 is the sole non-draft Barrot V3/XRP integration path and is being superseded by a consolidated current-main successor. #1653 is a separate repository-knowledge-graph workstream; dependency PRs and unique safety, topology, MMI and prediction work are preserved. No source PR is closed in this run.

This is a structural and integration reconciliation, not a complete semantic review of every changed application file. The 44 changed workflow files were reviewed in the preceding run; the remaining non-workflow diff still requires review. No merge, deployment, secret operation, paper trade or external action was performed.
