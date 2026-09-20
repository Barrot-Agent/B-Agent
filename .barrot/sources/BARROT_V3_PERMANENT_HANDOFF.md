# BARROT V3 — PERMANENT CONTINUATION SOURCE

## Purpose

This file is a durable repository-local source of truth for the Barrot V3 build handoff.

It supplements, rather than replaces, the live repository state.

## Core identity

Project: Barrot V3
Agent name: Barrot
Repository: Barrot-Agent/B-Agent
Local repository: ~/barrot/Barrot-Agent

## Continuity rule

Before making architectural or repository-changing decisions:

1. Inspect the current repository state.
2. Inspect persisted evidence and logs.
3. Distinguish observed facts from inference.
4. Never treat this document as proof that the current repository still matches the documented state.
5. Prefer current execution evidence over historical claims.

## Repository preservation

Never use destructive cleanup to obtain a clean tree.

Do not use:

- git reset --hard
- git clean
- git stash
- destructive overwrites

unless explicitly authorized.

Existing dirty and untracked work is intentional and must be preserved.

## Evidence standard

Never claim that something was:

- implemented
- fixed
- tested
- verified
- complete
- deployed
- pushed
- successfully repaired

without actual execution evidence.

Configuration is not runtime evidence.
LLM assertions are not repository evidence.
Barrot-generated evidence is not independent external corroboration.

## Autonomous-agent objective

Barrot should increasingly be able to:

- inspect the repository independently;
- use repository tools;
- establish evidence;
- distinguish observation from inference;
- diagnose problems;
- formulate repairs;
- execute validated repairs through controlled infrastructure;
- run appropriate validation;
- preserve evidence;
- deliver validated work through existing delivery infrastructure.

The operator should not have to manually discover repository facts that Barrot's tools can obtain.

## Current V3 objective

Barrot must independently investigate the CI problem, establish what is actually happening, reproduce it where possible, create an evidence-backed repair when warranted, validate the repair, preserve evidence, and deliver the result through the existing controlled infrastructure.

If the alleged CI failure cannot be established, Barrot must report the missing evidence rather than inventing a failure.

## MMI

MMI means Massive Micro Ingestion.

MMI is the canonical/default ingestion methodology for Barrot.

MMI is a protocol/contract, not a duplicate standalone ingestion system.

Core flow:

source + exact provenance
→ full parsable scope
→ recursive component/source depth
→ representation assessment
→ evidence normalization
→ independent corroboration
→ contradiction preservation
→ gap analysis/filling
→ reconciliation
→ learning extraction
→ capability analysis
→ discovery
→ gated acquisition
→ new MMI cycle
→ proposed self-upgrade
→ testing/verification
→ gated integration

Important principles:

- source provenance must be preserved;
- component depth and provenance depth are separate;
- target depth is four unless explicitly constrained;
- unavailable representations must not be fabricated;
- discovery does not equal acquisition;
- generated evidence is not independent corroboration;
- uncertainty and negative knowledge must persist;
- protocol completeness is separate from knowledge completeness;
- recursive processes require deterministic termination controls;
- observation and interpretation must remain separate.

## Architectural principle

Prefer:

EXTEND → INTEGRATE → TEST → VERIFY

over:

REWRITE → REPLACE → DISCARD

Existing infrastructure should be reused or strengthened when it already provides part of the required behavior.

## Execution truth

Execution truth must be established through:

ACTUAL EXECUTION
→ PERSISTED ARTIFACTS
→ EXECUTION LEDGER
→ DETERMINISTIC STATE EVALUATION
→ COMPLETENESS REPORT

A model cannot declare protocol completion.

## Current repository checkpoint

Recorded handoff checkpoint:

Commit:
82a0c59f7aea3f86d5873f8b7a0ffa28a6d38639

Message:
Preserve complete Barrot infrastructure work

Recorded branch:
barrot/tool-call-resilience

Recorded state:
155 files changed
48,372 insertions
583 deletions

This is historical handoff information. Verify against the live repository before relying on it.

## Barrot overnight investigation

Historical handoff recorded an overnight autonomous worker:

PID: 7236

Command:
python scripts/barrot_agent.py

Task:
Analyze and repair failing CI

Branch:
barrot/tool-call-resilience

Log:
.barrot/barrett_overnight_20260917_032952.log

PID file:
.barrot/barrett_overnight.pid

The PID and log must be inspected before starting another worker.

## CI facts recorded at handoff

Workflow:
.github/workflows/ci.yml

Recorded triggers:

- push to main
- pull request targeting main
- workflow_dispatch

Therefore a branch-local state must not be described as having a failing GitHub Actions run unless actual GitHub execution evidence establishes that fact.

## Existing autonomous repair infrastructure

Primary worker:

scripts/barrot_agent.py

Repository repair infrastructure:

barrot_agent/orchestration/repository_repair.py

The repair system includes investigation, analysis, issue validation, reproduction, planning, causality analysis, snapshotting, patching, validation, post-repair resolution, and configured delivery/synchronization.

Supported autonomous actions include:

LIST_FILES
READ_FILE
SEARCH_TEXT
RUN_TESTS
WRITE_FILE
APPLY_PATCH
GIT_STATUS
TERMUX_DROP
DELIVER_BUNDLE

## Repository-state corroboration

scripts/barrot_repo_state_manifest.py

barrot_agent/repo_state_corroborator.py

These provide deterministic repository-state corroboration through manifests, hashes, file references, and symbol validation.

Recorded failure classes include:

MISSING_REFERENCED_FILE
WRONG_REFERENCE_TYPE
SYMBOL_MISSING
FILE_HASH_MISMATCH
REPO_STATE_STALE

## Validation principle

Run the smallest targeted validation justified by the current evidence.

Do not blindly rerun completed work.

Do not upgrade historical acceptance statuses without new execution evidence.

## Handoff rule

When this source is loaded:

1. Treat it as durable architectural/context information.
2. Verify mutable facts against the current repository.
3. Inspect current persisted evidence before acting.
4. Preserve existing work.
5. Continue from the actual current state.
6. Do not make the operator reconstruct the project unnecessarily.

## Source metadata

Created:
2026-09-17T17:09:04.754093+00:00

Source type:
BARROT_V3_HANDOFF

Authority:
Repository-local project source

Important:
This document is contextual evidence, not proof of current runtime state.
