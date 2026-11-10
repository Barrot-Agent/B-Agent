## What I'm looking at

A truncated file listing (alphabetical, `git ls-files`-style). It begins mid-path — the first line is a fragment of `.barrot/collaboration_records/v3_acceptance_matrix/case-26.json` — and ends at `TRANSFORMATIVE_INSIGHTS_IMPLEMENTATION_SUMMARY.md`. **The actual source tree is not in this excerpt** (no `src/`, `tests/`, or package directories appear). Everything below is based strictly on the paths shown; I cannot verify file contents.

## Inventory (paths only)

- **~85 GitHub Actions workflows**, 8 explicitly `.disabled`; plus `.gitlab-ci.yml` (dual CI systems)
- **`.barrot/` agent-state directory**: acceptance-matrix JSON cases, `mmi_execution_ledger.jsonl`, three manifests (`repo_state_manifest.json`, `repository_identity.json`, `target_registry.json`), and scripts including `practice/barrot_self_repair.py`
- **4 test files** parked in `.barrot/disabled_tests/`
- **~40 top-level markdown docs**, many resembling generated reports/dated responses
- **Personal/environment files tracked**: `.bashrc`, `.gitconfig`, `.config/gh/hosts.yml`, `.termux/termux.properties`, `.termux_dna_harvest.log`

## Flags, in priority order (all require content verification)

1. **`.config/gh/hosts.yml` is committed.** The gh CLI's `hosts.yml` normally stores an OAuth token. If this is a real checkout artifact rather than a sanitized placeholder, that is a live credential in git history. Verify this first.
2. **`.bashrc` and `.gitconfig` at repo root** — personal shell config is a common vector for exported tokens and identity leakage.
3. **Committed runtime artifacts** — `.termux_dna_harvest.log` and `mmi_execution_ledger.jsonl` are logs/ledgers in version control; check for sensitive content and churn.
4. **Disabled tests**: four integration tests moved to `.barrot/disabled_tests/` rather than fixed or skipped with documented reasons. Corresponding feature docs exist at root (`EMAIL_*`, `MERGE_CONFLICT_RESOLUTION_GUIDE.md`, `TRANSFORMATIVE_INSIGHTS_*`), which *suggests* features documented as shipped while their tests are sidelined — inference only.
5. **Merge governance sprawl**: seven-plus workflows touch merging (`barrot-approve-pr`, `barrot-auto-pr`, `barrot-gated-merge`, `barrot-merge`, `barrot-merge-manual`, `barrot-pr-automerge` + its `.disabled` twin, `merge-queue`). Gated merge coexisting with multiple automerge paths indicates either conflicting policy or dead automation.
6. **Self-modification loop risk**: `barrot-self-upgrade.yml`, `barrot-autonomous-resolver.yml`, `auto-resolve-issues.yml`, `autonomous_self_deployment.yml`, plus in-repo agent state and `barrot_self_repair.py`. Agent-writable state inside the repo the agent operates on warrants explicit provenance and approval controls.
7. **Workflow numbering gap**: `capability-1`, `capability-9`, `capability-10` present; 2–8 absent — removed, or defined elsewhere.
8. **Root doc clutter**: ~40 markdown files including dated one-offs (`INGESTION_RESPONSE_2025-12-30.md`) — generated artifacts committed as documentation.

## Positive signals

`CODEOWNERS`, `SECURITY.md`, `dependabot.yml`, `.pre-commit-config.yaml`, `.flake8`, `.editorconfig`, `CHANGELOG.md`, `LICENSE`, both Dockerfiles + devcontainer, and audit-flavored workflows (`dependency-audit`, `barrot-transparency-audit`) — baseline hygiene is present.

## Cannot determine from a listing alone

Whether `hosts.yml` holds a real token; what any workflow actually executes; whether the disabled tests are superseded or abandoned; anything about the source code itself; branch protection settings.

## To proceed

Tell me the audit scope (security, CI governance, test integrity, repo hygiene?) and paste the remainder of the listing or specific files. I'd start with `.config/gh/hosts.yml`, the merge-family workflows, and the headers of the four disabled tests.

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
