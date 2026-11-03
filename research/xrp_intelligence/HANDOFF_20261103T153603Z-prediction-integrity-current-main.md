# Barrot XRP Intelligence + V3 Handoff — 2026-11-03T15:36:03Z

## Priority
XRP intelligence and measured prediction-engine mastery remain the highest-priority Barrot mission. Barrot V3 remains the execution, verification, security and preservation foundation.

## Current repository state
- Current main inspected: `0c2323231fefd3d9b5166b25cf6d4bd808b4a5b7`.
- Fresh-main branch prepared: `prediction/fresh-main-integrity-0c232323-20261103T1536Z`.
- Source proposal: PR #1572, head `d58c5975b6fa2cfbadf2caee8e3864070e41f78e`, base `ba121a1051c84ceb311e5c65e38a18659dcd7f0e`.
- Source PR is 3 commits ahead and 10 behind current main. A path-by-path Git tree comparison verified all 16 source-PR paths are unchanged between its base and current main, or absent on both sides where the source PR adds them.
- The patch is being transplanted onto the exact current main tree. No intervening current-main file is overwritten.
- PR #1585 also changes `.github/workflows/ci.yml`; this branch adds two prediction regression test paths to that workflow. Reconcile the two CI edits before either PR is merged.

## Prediction-integrity root cause
The legacy scorer waits at least 24 hours and evaluates at the first subsequent scheduled run, not at a fixed horizon. It compares an emission-time reference with a mutable live price and rewrites the historical log and summary. The public 45.5% (772/1,697) aggregate cannot be reproduced from the current-tree row-level history, which was empty at the inspected source cutoff. The sentiment classifier has no validated price target, fixed horizon, immutable source cutoff, or calibrated probability; presenting it as BUY/SELL or predictive accuracy is unsupported.

## Proposed controls carried forward
- Replace the legacy scorer with deterministic status-only output; no network calls and no history writes.
- Remove write permissions and direct pushes from the scheduled evaluation workflow; upload a bounded status artifact instead.
- Preserve the legacy aggregate only as explicitly unvalidated historical output.
- Mark directional forecast issuance blocked until the required fixed-horizon evidence and evaluation controls exist.
- Separate sentiment features from forecasts and remove BUY/SELL and unsupported accuracy claims from public pages, Barrot's own prompt and Daily Digest.
- Reject malformed/non-finite confidence and malformed or timezone-naive news timestamps.
- Add regression tests for non-networked status output, preservation of legacy files, sentiment/forecast separation and timestamp validation.

## Existing evidence
- Source PR #1572 head `d58c5975b6fa2cfbadf2caee8e3864070e41f78e`: exact-head core CI run [41660742611](https://github.com/Barrot-Agent/B-Agent/actions/runs/41660742611) reported 362 tests + 8 subtests passed in 6.98 seconds.
- Source PR #1572 fail-closed gate [41660742873](https://github.com/Barrot-Agent/B-Agent/actions/runs/41660742873) passed and kept automatic merging disabled.
- These results apply to the source head only. The new current-main branch requires its own exact-head CI and fail-closed gate; no result is claimed yet.

## Safety boundary
- DESIGNED: fixed-horizon, provenance-backed forecast architecture and controls.
- EXECUTED: current-main branch transplant with path-SHA reconciliation.
- VERIFIED: source-head tests and gate only; new branch verification is pending.
- Main unchanged. No merge, force-push, reset, clean, stash, deployment, workflow dispatch, secret access, paper trade or real-money trade occurred.
- Forecast status remains `NOT_ISSUED` / `BLOCKED_NO_VALIDATED_FIXED_HORIZON_DATA`.

## Next action
Inspect the exact new branch head, open a draft PR, then require fresh exact-head core CI and the fail-closed gate. Reconcile the shared CI workflow change with PR #1585 before merge review.
