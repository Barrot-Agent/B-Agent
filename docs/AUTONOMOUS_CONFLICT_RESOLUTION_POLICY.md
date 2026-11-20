# Autonomous conflict-choice policy

Barrot must not treat **Incoming** as universally correct, even when the PR was
created under Barrot's guidance. Incoming is the contextual default only after
the intended change and preservation of existing behavior have been established.

## Decision rules

- **Incoming:** intended PR improvement, current behavior preserved, protected
  areas reviewed, result validated, and tests pass.
- **Both:** both changes are independently required, compatible, and the
  composed result is validated and tested.
- **Current:** current is authoritative and incoming is demonstrably invalid,
  redundant, or superseded.
- **Manual review:** evidence is missing, changes are semantically unclear, or
  the conflict touches security, permissions, workflows, deployment, secrets,
  migrations, databases, binary files, renames, submodules, or delete/modify.

## Mandatory behavior

1. Inspect the base, current, and incoming versions; never infer correctness
   from the UI label, branch age, author, or PR provenance.
2. Identify functionality and invariants on both sides before discarding either.
3. Never use "accept both" as a substitute for semantic integration.
4. Never auto-apply a one-sided choice without explicit evidence and passing
   validation.
5. Run the relevant tests and inspect the final diff after resolution.
6. Record the evidence, choice, rationale, validation result, and outcome for
   recursive learning.
7. If evidence is incomplete or tests fail, stop and request human review.
8. This policy recommends choices only. It does not approve, merge, push, or
   deploy a pull request.

## Implementation

Use `barrot_agent.ingestion.conflict_resolution_policy.recommend_resolution`
with a `ConflictEvidence` instance. Missing evidence defaults to manual review.


## Live legacy-analyzer integration

The legacy `MergeConflictMicroIngestion` analyzer now calls this policy before
returning a recommendation. With no explicit evidence it returns `manual`,
emits no technique recommendation, and keeps `auto_resolvable` false. A
validated recommendation remains advisory only; `auto_apply` is always false.

High-risk paths include GitHub workflows/actions, CODEOWNERS, credentials,
secrets, environment files, migrations, infrastructure/deployment files,
database SQL, and lockfiles. These paths require human review even when the
incoming change otherwise satisfies the evidence fields.

The old RT001 85% accept-both success figure was not supported by measured
outcomes. It is now recorded as `UNVERIFIED`, not as a success rate. Historical
examples and learning records are not proof of resolution quality.

## Real-Git verification

Tests create temporary Git repositories and invoke actual branches and merges.
They cover conflicting edits, compatible disjoint edits, duplicate function
conflicts, high-risk workflow/secret paths, outdated incoming changes, and
failed validation. These tests verify the recommendation boundary; they do
not enable a live GitHub resolver.

## Execution boundary

Every recommended choice requires explicit human authorization before any
repository mutation. The autonomous resolver workflow remains quarantined and
the gated-merge workflow remains read-only. This change does not activate
automatic conflict resolution, PR approval, merge, push, or deployment.
