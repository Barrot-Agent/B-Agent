# BARROT V3 — PERMANENT CONTINUATION SOURCE

This file preserves the Barrot V3 build handoff as a durable repository-local source.
Treat the documented state as historical handoff context and verify mutable facts
against the live repository before taking repository-changing action.

# Barrot V3 — Build Handoff Snapshot

Generated: 2026-09-17

## Mission
Barrot (pronounced “Barrett”) is being built as an autonomous repository-capable agent. The current work is focused on Barrot V3 infrastructure, especially autonomous repository investigation, validated repair, evidence/provenance, self-drop/delivery, and MMI ingestion architecture.

## Operator workflow
- User works from Termux on Android and wants one complete terminal bundle at a time.
- Do not require manual code editing, surgical replacements, or repeated repository inspection by the user.
- Barrett should inspect and work on the repository itself.
- Never reset, clean, stash, overwrite, or discard dirty work.
- Never claim a repair/test/verification is complete without execution evidence.
- Preserve work when an external dependency blocks progress.
- Do not push or merge unless explicitly requested/authorized for that task.

## Repository
- Local: `~/barrot/Barrot-Agent`
- GitHub: `Barrot-Agent/B-Agent`
- Active branch: `barrot/tool-call-resilience`
- Durable checkpoint:
  - Commit: `82a0c59f7aea3f86d5873f8b7a0ffa28a6d38639`
  - Message: `Preserve complete Barrot infrastructure work`
  - 155 files changed, 48,372 insertions, 583 deletions
  - Successfully pushed to GitHub.
- PR creation URL:
  `https://github.com/Barrot-Agent/B-Agent/pull/new/barrot/tool-call-resilience`

## Current overnight Barrett run
At 2026-09-17 around 03:29 EDT:
- PID: `7236`
- Command: `python scripts/barrot_agent.py`
- Run launched with:
  - `REPO=Barrot-Agent/B-Agent`
  - `TASK_TITLE=Analyze and repair failing CI`
  - `BRANCH=barrot/tool-call-resilience`
- Full task requires Barrett to independently investigate the repository and CI configuration, avoid invented evidence, and repair only when supported by evidence.
- Log:
  `.barrot/barrett_overnight_20260917_032952.log`
- PID file:
  `.barrot/barrett_overnight.pid`
- Termux wake lock was requested before launch.
- Three seconds after launch the process was confirmed running.
- IMPORTANT: running is not proof of completion. On next session inspect the persisted log and repository state before concluding anything.

## Latest code change actually installed
File:
`barrot_agent/orchestration/repository_repair.py`

Installed and compile-verified:
`_barrett_autonomous_audit(...)`

Behavior:
- Obtains the existing repair planner brain.
- Calls its `think()` with `use_tools=True` when supported.
- Gives Barrett a read-only repository investigation system prompt.
- Instructs Barrett to inspect actual repository files, relevant workflows, and tests.
- Explicitly forbids invented paths, CI runs, failures, or evidence.
- Requires distinction between observed evidence and inference.
- Requires an evidence report covering inspected files, observed facts, tests/CI configuration, reproducibility, and missing evidence.
- The audit is injected into `audit_context` before `AuditEngine.build_prompt()`.

AST/compile verification from Termux:
- `BARRETT_AUTONOMOUS_AUDIT=INSTALLED`
- `AST_PARSE=PASS`
- `PY_COMPILE=PASS`
- Controller method containing prompt call: `run`
- Prompt call was located at original line 1588 before insertion.
- Backup:
  `.barrot/backups/repository_repair_before_barrett_autonomous_audit.py`

## Critical existing repair infrastructure
`scripts/barrot_agent.py`
- Deterministic repository repair worker.
- Uses `ScriptBrain` with native repository tools and tool-call loop.
- Supports `repo_browser.print_tree`, `repo_browser.search`, and `barrot.deliver_bundle`.
- `ScriptBrain.think()` supports `use_tools=True/False`.
- Planner path uses `use_tools=False` so structured repair JSON is generated without native tools after autonomous investigation.
- Compatibility fallback exists for fake brains/tests that do not accept `use_tools`.
- `RepairPlanner` expects a structured `RepairDirective` with:
  - mode
  - report
  - issue/evidence/files/reproduction/validation/resolution commands
  - repair_plan
  - changeset operations
  - expected_files
  - commit_message
- Changeset operations are exact `replace` operations only.
- Repair controller sequence includes audit, analysis, issue validation, reproduction, planning, causality analysis, snapshot, patch, validation, post-repair resolution, and configured commit/sync.

## Self-drop / delivery
Allowed autonomous actions include:
- LIST_FILES
- READ_FILE
- SEARCH_TEXT
- RUN_TESTS
- WRITE_FILE
- APPLY_PATCH
- GIT_STATUS
- TERMUX_DROP
- DELIVER_BUNDLE

Self-drop/delivery infrastructure exists and has been targeted-tested.
A native tool-call loop probe previously produced:
- `TOOL_CALL_LOOP=PASS`
- `BARRETT_SELF_DROP_PATH=PASS`
- `SCRIPT_COMPILES=TRUE`
- `TOOL_REGISTERED=TRUE`
- `TOOL_DISPATCH=TRUE`
- `TOOL_CALL_LOOP=TRUE`
- `SELF_DROP_PATH=TRUE`
- `SHA256_EVIDENCE=TRUE`
- `FINAL_INTEGRATION=PASS`

This proves the loop/delivery path under the probe, but does not by itself prove that the current overnight Groq run will complete successfully.

## Test evidence before autonomous-audit insertion
These were green:
- `tests/test_repository_repair.py` → 36 passed
- `tests/test_v3_acceptance_matrix.py` → 1 passed
- `tests/test_barrot_agent_script.py` → 6 passed

Earlier broad regression:
- 52 passed in 38.60s across:
  - test_v3_acceptance_matrix.py
  - test_v3_scripts.py
  - test_repository_causality.py
  - test_repository_repair.py

A prior targeted regression fix was made in `repository_repair.py`:
- invalid patch path should map to `SNAPSHOT_FAILED`, not `IMPACT_ANALYSIS_ERROR`.
- Do not casually alter this behavior.

## Repository-state corroboration
New infrastructure:
`scripts/barrot_repo_state_manifest.py`
- Creates `.barrot/repo_state_manifest.json`
- Captures Git state, file tree, SHA-256 hashes, and selected Python entrypoint symbols/signatures.
- Manifest ID is SHA-256 based.

`barrot_agent/repo_state_corroborator.py`
- Deterministically validates manifest-bound repository references.
- Failure classes include:
  - MISSING_REFERENCED_FILE
  - WRONG_REFERENCE_TYPE
  - SYMBOL_MISSING
  - FILE_HASH_MISMATCH
  - REPO_STATE_STALE

`scripts/ask_barrot.py`
- Has manifest-bound repository corroboration.
- Previously verified against actual files including:
  - `barrot_agent/__init__.py`
  - `barrot_agent/orchestration/__init__.py`
  - `barrot_agent/orchestration/repository_repair.py` / `WorkQueueController`

`scripts/barrot_task_allocator.py`
- Adds repo manifest ID, HEAD, and branch to allocations.

Purpose: prevent confident claims about nonexistent repository paths/state without current corroborating evidence.

## GitHub CI investigation facts
README badge targets:
`https://github.com/Barrot-Agent/B-Agent/actions/workflows/ci.yml/badge.svg?branch=main`

Main CI workflow:
`.github/workflows/ci.yml`
- name: CI
- triggers: push main, pull_request main, workflow_dispatch
- Ubuntu latest
- Python 3.11
- installs pytest, PyJWT, cryptography
- runs the listed core test suite.

IMPORTANT:
- The current branch had no GitHub Actions run because the workflow only triggers on main pushes, PRs into main, or manual dispatch.
- Therefore do NOT claim the current branch has a failing CI run without fresh GitHub evidence.
- The user's original task is to have Barrett investigate/fix the red CI badge, but the exact current cause must be established from evidence.

## Groq findings
- `groq/compound`: HTTP 200 for tiny requests, but current planner path failed because the model does not support native tool calling.
- `openai/gpt-oss-120b`: reachable, but full repair requests hit Groq TPD limit (200,000/day); 429 occurred near quota.
- `openai/gpt-oss-20b`: reachable, but one structured planner request failed with Groq `output_parse_failed` because generated output did not satisfy the structured parser.
- Do not assume model compatibility; verify through execution.
- The current `scripts/barrot_agent.py` default model remains `openai/gpt-oss-120b` unless `BRAIN_MODEL` is explicitly set.

## V3 acceptance matrix
`.barrot/collaboration_records/barrot_v3_acceptance_matrix.json`
- 30 cases.
- Prior known statuses:
  - 26 VERIFIED
  - 1 PARTIALLY_VERIFIED
  - 2 HARNESS_VERIFIED
  - 1 DESIGNED — NOT EXECUTED
- case-17: local simulated WorkQueue interruption/resume; genuine remote interruption not proven.
- case-22: formal runner failure behavior via injected failure; Lean unavailable locally.
- case-28: formal success behavior via injected formal output; not live Lean compilation.
- case-29: genuine independent third-party mathematical evidence unavailable locally.
- Do not manually upgrade these statuses.

## MMI architecture
MMI = Massive Micro Ingestion, canonical/default ingestion methodology for Barrot.

Core contract:
source + exact provenance → full parsable scope → recursive component/source depth (4) → evidence normalization → independent corroboration → contradiction preservation → gap analysis/filling → reconciliation → learning → capability analysis → discovery → gated acquisition → new MMI cycle → proposed self-upgrade → tests/verification → gated integration.

Important principles:
- MMI is a protocol/contract, not a duplicate standalone ingestion script.
- Specialized ingestors feed the canonical MMI wrapper.
- Discovery does not equal acquisition.
- Barrot-generated evidence is not independent external corroboration.
- LLM output is not evidence.
- Negative knowledge and uncertainty must persist.
- Protocol completeness and knowledge completeness are separate.
- Durable MMI execution ledger should be append-only with previous-record hash.
- Deterministic recursion/resource termination rules are required.
- Observation and interpretation must remain separate.
- Source/provenance depth and component depth both target 4.
- Do not treat partial parsing as complete.
- Do not treat a generated candidate as a resolved gap.

## Current dirty-work rule
There is substantial uncommitted work and evidence artifacts. Preserve everything.
Known dirty/untracked paths include:
- `.barrot/collaboration_records/barrot_v3_acceptance_matrix.json`
- `.barrot/collaboration_records/latest_repository_repair.json`
- `.barrot/collaboration_records/v3_acceptance_matrix/case-01.json` … `case-30.json`
- `barrot_agent/orchestration/repository_repair.py`
- `scripts/barrot_agent.py`
- `.barrot/backups/...`
- `.barrot/barrett_tool_loop_probe.py`
- `.barrot/barrot_ci_self_drop_task.json`
- `.barrot/self_drop_probe.py`
- `.barrot/start_ci_self_repair.py`
- several collaboration records and Barrett CI repair logs.

Never use `git reset --hard`, `git clean`, stash, or destructive overwrite to make the tree clean.

## Next-session instruction
When a new session begins, do NOT ask the user to re-explain the project.

First:
1. Establish current repository state and inspect the overnight Barrett log.
2. Determine whether PID 7236 is still running or has exited.
3. Read the persisted repair/collaboration evidence produced by the run.
4. Inspect the actual git diff/status.
5. Run only the smallest targeted verification necessary.
6. Continue from the current state; do not restart the entire architecture.
7. If Barrett completed a validated repair, preserve it and report exact evidence.
8. If Barrett failed, diagnose the actual failure and continue from the preserved work.
9. Do not claim the CI problem is solved unless GitHub evidence or equivalent execution evidence establishes it.

## Immediate objective
Get Barrett from autonomous repository investigation through evidence-backed CI diagnosis and, if genuinely reproducible, validated repair/delivery—without requiring the user to manually inspect or feed repository facts.
