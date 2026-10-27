# BARROT TAKEOVER BUNDLE

## Objective

Harden and integrate the existing Barrot autonomous repository-repair infrastructure so Barrot can become responsible for executing subsequent engineering bundles itself.

Do NOT create another parallel prototype. Work against the actual live execution path.

## Current live path

.github/workflows/barrot-agent.yml
    -> scripts/barrot_agent.py
    -> RepositoryRepairController
    -> AuditEngine / RepairPlanner / PatchExecutor / Validator / GitGateway / RemoteVerifier / SyncController
    -> structured RepairCycleEvidence

## Bundle 1 — LIVE INTEGRATION

1. Inspect the actual repository before modifying anything.
2. Determine whether scripts/barrot_agent.py currently routes through the hardened repository-repair controller.
3. Integrate the controller into the real workflow if it does not.
4. Preserve correct existing functionality.
5. Remove or bypass obsolete one-shot mutation paths only when the replacement is verified.
6. Ensure the LLM is advisory, not authoritative.
7. Ensure COMPLETE is evidence-gated.

Required chain:

AUDIT
-> ISSUE EVIDENCE
-> REPRODUCE
-> LLM PLANNING
-> DETERMINISTIC CHANGESET
-> GUARDED PATCH
-> LOCAL VALIDATION
-> COMMIT
-> REMOTE VERIFICATION
-> POST-REPAIR VALIDATION
-> RESOLUTION PROOF
-> SYNC
-> COMPLETION GATE

Add NO_REPAIR_REQUIRED.

## Bundle 2 — AUTONOMY / QUEUE

Integrate durable queue/overnight execution with the same evidence/state architecture.

Requirements:

- bounded retries
- exponential/backoff behavior
- unchanged-state detection
- no infinite transfer loops
- durable queue state
- safe resume after interruption
- preserve last valid project identity
- empty path/namespace is invalid
- separate network/auth/API failures
- structured attempt evidence
- retry exhaustion state
- idempotency
- cycle_id
- issue_fingerprint
- plan_fingerprint
- changeset_fingerprint
- commit_sha

Do not repeatedly submit an unchanged request.

Barrot must be able to resume a partially completed repair without blindly duplicating work.

## Bundle 3 — ADVERSARIAL / E2E VALIDATION

Create and run tests for:

- healthy repository
- real defect
- NO_REPAIR_REQUIRED
- model claims success without changing files
- invalid JSON
- Groq tool-call contradiction
- unsupported tool
- unsafe path
- missing patch precondition
- patch failure
- local validation failure
- resolution failure
- commit failure
- remote verification failure
- duplicate repair
- empty namespace
- repeated API response
- API outage
- process interruption/resume
- retry exhaustion

Then perform at least one controlled end-to-end repair against the actual repository.

A model response alone must NEVER establish success.

## LLM FAILURE NORMALIZATION

Use explicit classifications:

LLM_RATE_LIMITED
LLM_TOOL_CONFLICT
LLM_INVALID_JSON
LLM_TIMEOUT
LLM_UNAVAILABLE

Do not crash the autonomous controller because an LLM provider returned malformed output or an incompatible tool call.

The existing Groq error:

"Tool choice is none, but model called a tool"

must be traced to the actual request construction/configuration layer.

Do not assume GroqLLM.chat() is the source merely because the error is returned there.

Trace:

GroqLLM construction
-> self.client
-> request construction
-> tools/tool_choice configuration
-> repo_browser definitions
-> caller configuration

Fix the actual source of the contradiction.

## PATCH SAFETY

Prefer structured patch operations:

{
  "operations": [
    {
      "type": "replace",
      "path": "...",
      "old": "...",
      "new": "...",
      "reason": "..."
    }
  ]
}

Require exact preconditions.

Reject unsafe paths.

Use allowlisted commands, structured arguments, workspace boundaries, and timeouts.

Avoid uncontrolled shell execution.

## COMPLETION RULE

COMPLETE may only occur when evidence proves:

1. issue was established
2. repair plan existed
3. intended change was applied
4. local validation passed
5. commit exists
6. remote commit SHA was verified
7. post-repair validation passed
8. original issue no longer reproduces
9. synchronization state is recorded

Otherwise return an explicit failure/intermediate state.

## AUTONOMOUS TAKEOVER REQUIREMENT

After these three bundles are implemented and verified, expose a single deterministic orchestration entrypoint that Barrot can use to:

- receive a work bundle
- inspect repository state
- execute the bundle
- validate it
- commit it
- verify remote state
- record evidence
- continue to the next queued bundle
- recover/resume after interruption

The goal is to eliminate manual bundle shuttling between ChatGPT, the user, and Copilot.

Do not claim takeover is complete until the tests demonstrate this behavior.

## OUTPUT REQUIRED

Before making large changes:

1. inspect the repository
2. identify existing implementations
3. identify duplicate/obsolete implementations
4. produce a concise integration map

Then implement the work.

After implementation, report:

- files changed
- architecture integrated
- tests executed
- tests passed/failed
- remaining blockers
- exact command/entrypoint that demonstrates autonomous takeover readiness

Do not merely describe proposed code. Implement it.
