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