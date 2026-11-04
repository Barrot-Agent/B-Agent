# Residual workflow containment handoff

Captured: 2026-11-04T03:18:31.270Z

Repository: `Barrot-Agent/B-Agent`  
Inspected main: `d89cc363812a9a9d04d076d6ef5a09f7cf736285`  
Target: PR #1623, branch `security/external-action-gates-162f43d-20261104T0212Z`

## Findings and changes

1. **Riemann Harvest:** weekly public research ingestion previously committed harvested JSON and an A2A corpus directly to main. It now keeps the schedule, uses read-only checkout and publishes outputs as a workflow artifact.
2. **WebMCP Live Sandbox:** the weekly workflow invoked every registered tool's `execute({})` in Playwright and committed the log; on push conflict it ran `git pull --no-rebase`. It is now manual-only with `confirm_live_execution=YES`, read-only checkout and artifact output.
3. **Hover Bike Updates:** local simulations already uploaded artifacts and did not need repository write permission. Permission reduced to read-only.
4. **Transparency Audit:** local static audit and benchmark summaries previously committed/pushed to main. They now remain artifacts.
5. **WebMCP Monetization Enrichment:** public GitHub/NPM GET enrichment previously used a repository write token and pushed results. It now runs without GITHUB_TOKEN and uploads artifacts.
6. **Pillars Check:** the GitHub check previously minted an installation access token via POST solely to prove the installation existed. It now performs a read-only GET of installation metadata. Databricks `SELECT 1` remains; actual token scope is not visible and must be checked.
7. **Kaggle Competitions:** daily automation intended to submit up to five baseline entries without per-run approval. It also referenced a missing root script path; the actual runner is in `scripts/`. The workflow is now manual-only, requires `confirm_external_submission=YES` and exact competition slugs, and both duplicate runner copies refuse before authentication when the allowlist is empty.

## Verification state

- Changes are committed to PR #1623 only.
- Exact-head CI and fail-closed verification are pending.
- Main has not been changed.
- No Kaggle submission, live WebMCP execution, deployment, merge or external write was performed.

## Residual risks

- Main workflows remain active until PR #1623 is approved and merged.
- Databricks token scope needs external confirmation.
- Manual-only write workflows and release/tag-triggered workflows still need review.
- Dependency reproducibility remains incomplete: no lockfiles; CI installs only a subset of app dependencies; `requirements.tx` appears unreferenced in inspected build/docs/workflow files.

## Next action

Verify exact-head CI and gate, then continue the remaining manual-workflow and release-trigger audit. Do not merge without approval.
