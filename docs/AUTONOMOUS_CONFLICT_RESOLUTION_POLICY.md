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


## Runtime enforcement and verification boundary

The legacy `MergeConflictMicroIngestion.analyze_conflict` path now delegates to
this policy and returns **manual review** when it has only conflict-marker and
file-path evidence. Its historical technique catalog is reference material,
not an authority to select or apply a resolution. Historical percentage values
are not measured success rates and are no longer used for ranking.

The policy never applies a resolution. Even a fully evidenced `incoming` or
`both` recommendation has `auto_apply=false`; a separate explicit human
authorization is required before any repository mutation.

The PR workflow performs a real, read-only Git merge-tree check against the
PR's current base and head. It blocks the check when Git reports conflicts.
It does not attempt to resolve, approve, or merge the pull request.

The Git integration tests create temporary repositories and exercise clean
three-way merges, conflicting edits, conflict-marker preservation, and the
non-mutating merge-tree check. These tests validate Git behavior and Barrot's
fail-closed decision boundary; they do not claim an autonomous resolver exists.
