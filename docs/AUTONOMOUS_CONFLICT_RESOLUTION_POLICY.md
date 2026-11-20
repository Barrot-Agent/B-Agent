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
