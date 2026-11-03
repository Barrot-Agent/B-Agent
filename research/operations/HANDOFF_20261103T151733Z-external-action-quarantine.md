# Workflow security consolidation — 2026-11-03 15:17 UTC

## Scope
XRP intelligence remains the top mission. This security increment protects Barrot V3's execution foundation by removing unattended repository and external-service mutation paths while leaving the core PR-producing Barrot runner available for separate review.

- Main observed: `0c2323231fefd3d9b5166b25cf6d4bd808b4a5b7`
- Target PR: [#1585](https://github.com/Barrot-Agent/B-Agent/pull/1585)
- Target branch parent before this increment: `ee6a4d2117cc942130bb03faba3a57de2b606705`
- Source quarantine proposal: [#1573](https://github.com/Barrot-Agent/B-Agent/pull/1573), head `43324f7c89557ee9fba527f785027932d66a6ffd`
- Capture cutoff: 2026-11-03T15:17:33Z

## What was added to PR #1585
Nineteen current-main workflows were transplanted from the tested external-action quarantine proposal:
- `.github/workflows/Barrot.Cognitive.PingPong.Engine.yml`
- `.github/workflows/autonomous_self_deployment.yml`
- `.github/workflows/barrot-hf-admin.yml`
- `.github/workflows/barrot-merge-manual.yml`
- `.github/workflows/barrot-merge.yml`
- `.github/workflows/barrot-ops.yml`
- `.github/workflows/barrot-restart-space.yml`
- `.github/workflows/barrot-self-upgrade.yml`
- `.github/workflows/capability-9-data-resolver.yml`
- `.github/workflows/databricks-bundle.yml`
- `.github/workflows/deploy-a2a-worker.yml`
- `.github/workflows/deploy-databricks.yml`
- `.github/workflows/force-deploy-space.yml`
- `.github/workflows/gumroad-metrics.yml`
- `.github/workflows/riemann-harvest.yml`
- `.github/workflows/rotate-databricks-token.yml`
- `.github/workflows/sync-huggingface.yml`
- `.github/workflows/sync-self-hosted-brain.yml`
- `.github/workflows/webmcp-monetization-enrich.yml`

Each is now a manual-only inert stub with empty permissions, a disabled job, no secrets, and no scheduled/push/workflow_run trigger. The Cloudflare worker stub's explanatory text was adjusted to avoid a false-positive substring in the regression test; its behavior remains inert.

## Test changes
- Added `tests/test_external_writers_quarantined.py`.
- Added `tests/test_scheduled_mutation_workflows_quarantined.py`.
- Updated `tests/test_external_deploys_require_confirmation.py` to require disabled stubs rather than relying on a self-entered YES input.
- Expanded `tests/test_workflow_yaml_syntax.py` to parse all 19 added workflows.
- Updated the explicit CI test list to run both new test modules.
- Updated the self-upgrade workflow test to assert that the workflow is quarantined; script-level self-upgrade unit tests remain.

## Important remaining review
The core `barrot-agent.yml` runner is deliberately not disabled: it is the PR-producing execution path. It retains contents/PR/issues write permissions, restricts issue-label invocation to Barrot-Agent or the repository owner, and permits manual dispatch by authorized repository actors. Its schedule-handling code has no matching schedule trigger. It needs a separate review of manual-dispatch authorization, branch-only writes and the script's mutation boundaries.

Other remaining direct-main/manual writers are listed in the JSON audit: `ask-barrot.yml`, `free-image-gen.yml`, and `subagent-spawn.yml`. The manual `barrot-approve-pr.yml` workflow applies a label and comment, not a GitHub review; the merge queue is separately proposed disabled. `barrot-auto-pr.yml` grants unnecessary pull-request write permission for a no-op job. These were not silently changed in this increment.

## Validation status
The branch update is prepared. Exact-head CI and fail-closed gate results must be read after the new commit. No merge, force-push, main-branch update, workflow dispatch, credential read, external deployment, paper trade or real-money action occurred.
