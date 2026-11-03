# Protected-branch write boundary — 2026-11-03 15:22 UTC

## Finding
The current main branch's repository repair path had no generic main/master guard. `GitGateway.push` trusted a string label `authorization="repository_sync"`, while `DefensiveWatchdog` defaults to allowing `EXTERNAL_ACTION`. The gateway could therefore push to main/master if a caller supplied that target. `GitGateway.commit` also lacked a current-branch check, and `RepositoryRepairController.run` did not verify that the requested target matched the checked-out branch. The core worker's `checkout_branch` accepted main/master and used `git checkout -B`.

This was a latent path, not an observed main-branch push. The normal `barrot-agent.yml` worker currently supplies a `barrot/task-*` branch, but defense-in-depth was missing.

## Fix prepared in PR #1585
- Added a case-insensitive `is_protected_branch` helper that recognizes `main`, `master`, and `refs/heads/` forms.
- `RepositoryRepairController.run` now blocks a protected target before audit/planning/patching and blocks any target that does not exactly match the checked-out branch.
- `GitGateway.commit` blocks commits while the workspace is on main/master before staging.
- `GitGateway.push` blocks main/master before authorization or remote execution; task-branch pushes remain allowed.
- `scripts/barrot_agent.py` rejects protected branches before checkout and before creating a PR with a protected head branch.

## Regression coverage
- Protected target is blocked before any patch or commit.
- Requested target must match the checked-out branch.
- Push is blocked for main, master, uppercase MAIN, and refs/heads variants.
- A `barrot/task-123` push remains permitted.
- Commit is blocked on a checked-out main branch before staging.
- The core worker's branch checkout rejects main/master.

## Residual
`MCPApprovalGate` defaults to `always_deny`, but it is not wired into this repository push path. Non-protected task-branch pushes remain allowed by the worker's GitHub token and workflow design so Barrot can create draft PRs. The current worker's normal target is `barrot/task-*`; no merge is performed. GitLab remote sync and other manual external actions still require a separate authorization-boundary review.

## Validation
Code and regression tests are committed only to the existing security proposal branch. Exact-head CI and fail-closed gate are pending. Main remains unchanged; no workflow was dispatched, no external deployment occurred, and no merge or force-push was performed.
