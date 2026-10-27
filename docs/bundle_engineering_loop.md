# Barrot Bundle Engineering Loop

## Purpose

The bundle engineering layer teaches Barrot to produce structured work plans, critique their completeness, and make bounded revisions before execution. It is designed to extend the existing repository-repair and verified-bundle-delivery components rather than replace them.

## Runtime API

- `build_bundle_authoring_prompt(...)` asks the model to create a structured bundle for a specific objective, with mandatory constraints and repository context.
- `review_work_bundle(bundle)` deterministically checks required fields, task coverage, dependency references/cycles, authorization constraints, completion evidence, and recovery behavior.
- `build_bundle_improvement_prompt(bundle, review)` turns review findings into a revision task.
- `validate_bundle_revision(original, revised)` enforces objective, bundle identity, and constraint invariants; checks parent fingerprint and sequential revision number; and rejects quality regressions or revisions that fail to improve a deficient bundle.
- `BundleEngineeringController.run(...)` runs a bounded author → review → revise loop. Its success state is `READY_FOR_EXECUTION_REVIEW`, not task completion. If the quality gate is not met within the configured revision limit, it returns `BLOCKED_BUNDLE_QUALITY`.

## Required bundle fields

A version 1.0 bundle includes a stable bundle ID, objective, revision, mandatory constraints, prerequisites, tasks, completion gate, recovery plan, and author. Each task declares its ID, title, description, relative file targets, observable acceptance criteria, tests, dependencies, risk level, and rollback plan.

## Safety boundaries

- A model-authored bundle is a plan, not evidence that work was executed.
- Completion must be proven by execution evidence and independent validation.
- The objective and constraints cannot silently change during self-revision.
- Dependency references must resolve and dependency graphs must be acyclic.
- Consequential external actions remain subject to authorization and existing repository safety gates.
- Revision attempts are bounded. A failed quality gate produces a blocked result rather than an infinite retry loop.
- The reviewer is deterministic; it checks structure and explicit gates, not whether a proposed code change is semantically correct. That requires repository-specific tests and review.

## Current integration boundary

The live `scripts/barrot_agent.py` entrypoint now runs bundle authoring and deterministic review before invoking the existing `WorkQueueController` and `RepositoryRepairController`. A failed authoring/review step blocks repository mutation. The bundle and its revision/review evidence are stored atomically under `.git/barrot_repair/bundles/<work-key>/lifecycle.json`, keeping runtime state out of the worktree; the resulting repair outcome is appended to that record.

This is the first production-path integration, not full multi-task autonomy. The current queue still executes the original issue as one evidence-gated repair cycle; it does not yet dispatch every task in a generated bundle as a separate resumable queue item. That next step requires task-level idempotency, dependency-aware advancement, per-task completion evidence, and interruption/resume tests. Do not claim full autonomous bundle execution until those tests and a controlled end-to-end run pass.
