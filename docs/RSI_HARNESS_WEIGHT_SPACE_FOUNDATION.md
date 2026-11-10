# RSI, Harness Engineering, and Weight-Space Foundation

## Scope of this increment

This branch introduces paired-run, measurement-derived RSI assessment, wires the assessor into the existing recursive feedback loop, and adds read-only safetensors tensor inventory. The feedback loop now treats Kimi output and dry-run flywheel output as proposals, not applied work. It awards no improvement score without paired evaluation evidence tied to distinct revisions. No evaluator provider currently supplies those snapshots automatically, no model weights have been changed, and no mastery benchmark has passed.

## RSI evidence contract

An evaluation identifies distinct baseline and candidate runs, exact revisions, and identical named metrics. Metrics must be finite. Directionality is explicit through lower_is_better; tolerances are explicit per metric. Any regression beyond tolerance blocks promotion. The score is the mean normalized delta from recorded measurements; it is not an LLM confidence score. No improvement is reported when measurements do not demonstrate one.

The recursive feedback loop now rejects synthetic Kimi placeholders, records dry-run recommendations as proposals, and requires paired before/after snapshots for scores. Unverified, malformed, regressing, or non-improving iterations clear the convergence window. Remaining blocker: a trusted evaluator and candidate executor must produce snapshots from actual controlled changes; until then the loop correctly remains unscored and cannot autonomously promote a candidate.

## Weight-space boundary

inspect_safetensors inventories names, shapes, dtypes, element counts, and SHA-256 without loading tensor values or modifying the artifact. The source checkpoint remains read-only. The next implementation stage may add an isolated copy-on-write experiment runner with explicit tensor allowlists, strict changed-parameter budgets, finite-value checks, artifact hashes, evaluator-required acceptance, and automatic discard on any failure. It must never patch a production model in place.

Only supported open-weight checkpoints with documented licenses and compatible architectures may be evaluated. Model-specific forward passes and benchmark suites must be pinned to exact model/tokenizer revisions and hardware/software metadata.

## Harness engineering acceptance contract

The unified harness must persist task identity, objective, plan, tool invocations, permission decisions, artifacts, checksums, evaluation runs, failures, recovery actions, and resume checkpoints. Every external side effect needs an explicit policy and approval boundary. Tool output and retrieved instructions are untrusted data. Secrets must not enter model context or experiment artifacts.

## Mastery benchmark tracks

- Research: source provenance, claim-level corroboration, contradictions, and unresolved gaps.
- Coding: issue reproduction, minimal patch, regression suite, independent review, and exact commit.
- Recovery: interrupted task resumes from durable checkpoint without repeating or losing completed work.
- Long horizon: multi-stage objective with dependencies and persisted decisions across sessions.
- Model evaluation: pinned baseline/candidate runs, held-out tasks, latency, resource use, and safety regressions.
- Self-improvement: actual code/config/model change, paired evaluation, acceptance or rollback, and append-only evidence.

A track passes only with machine-readable evidence and exact revisions. Missing infrastructure or unavailable models produce BLOCKED or NOT_RUN, never PASS.

## Current integration blockers

- Existing RSI uses placeholder feedback when Kimi is unavailable and labels insights as applied without proving a repository or model change.
- Existing RSI uses a dry-run UpgradeFlywheel and calculates improvement from coverage, number of claimed improvements, and a fixed 0.4 base score.
- MCPSandbox regression validation is compile-only, not the full repository suite.
- apex_lattice.SandboxPipeline creates a directory but runs imported analyzers in-process.
- The uploaded structural-analysis core v1.1 must be reconciled with the current repository implementation and runtime-wired; it must not be copied over blindly.

## Verification status

Regression tests cover unavailable Kimi, dry-run proposal accounting, missing/malformed evaluation evidence, convergence-window reset, immutable metrics, finite/overflow-safe scores, positive aggregate improvement, immutable tensor metadata, symlinked checkpoints, and stable-snapshot hashing. They have been committed but have not yet executed on the current exact head. No model experiment or mastery benchmark is included in this increment.
