# Merge Queue Safety Status

## Current status

The repository's merge queue is intentionally disabled pending independent verification of effective branch protection, mandatory checks, review requirements, and authorized approval controls.

The workflow at `.github/workflows/merge-queue.yml` is a manual, read-only notice only. It does not enumerate pull requests, update branches, apply labels, post comments, push commits, or merge pull requests.

## Why it is disabled

The previous implementation had write permissions and could update or merge pull requests. Its `mode=all` option could select every open pull request. A manually invoked workflow is still a consequential mutation pathway; manual invocation alone is not a sufficient safety gate.

## Required conditions before redesign

A future merge automation proposal must be reviewed independently and must demonstrate all of the following:

- Effective repository branch protection or rulesets are verified, not inferred from a workflow's own checks.
- Required CI checks are bound to the exact current head and current base.
- The pull request is open, non-draft, mergeable, and based on current main.
- Explicit authorized approval is verified independently of labels or PR text.
- The workflow has least-privilege permissions and cannot bypass required reviews.
- The workflow fails closed on API errors, unknown status, missing checks, stale heads, and rate limits.
- Regression tests cover every mutating path and demonstrate no side effects on rejection.
- The owner reviews the proposed workflow before any enabling change.

Until those conditions are independently demonstrated and the change is approved, do not run a merge automation workflow or enable unattended merging.

## Safe operating procedure

Use GitHub pull requests for review. Inspect the exact head SHA, changed files, required checks, review status, and base divergence. Keep drafts unmerged until a human-authorized review is complete. Never use a broad "all open PRs" mode as a substitute for explicit review.

## Validation boundary

The regression test `tests/test_merge_queue_safety.py` verifies that the checked-in workflow remains manual-only, read-only, and free of branch-update, push, comment, label, and merge commands. CI runs this test alongside the core suite. A passing test verifies repository content only; it does not prove effective GitHub rulesets or organization-level policy.
