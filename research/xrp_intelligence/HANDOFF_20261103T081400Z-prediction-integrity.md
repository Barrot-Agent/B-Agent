# Barrot Prediction Integrity Handoff — 2026-11-03T08:14:00Z

## Mission
XRP intelligence and prediction-engine mastery remain highest priority; Barrot V3 remains execution, verification, security and preservation foundation.

## Repository state
- Main: `ba121a1051c84ceb311e5c65e38a18659dcd7f0e`.
- Fresh-main branch: `prediction/fresh-main-integrity-20261103T0814Z`.
- Predecessor PR #1569 head: `2da8b38aaba35db9cea5e8ac1b699d4f0847e600`, based on `60aef00405f26badabd4ac15807df163756204cc`.
- Reapplied its 14 changed files to current main after three-tree path comparison.
- Current main's only intervening path change was `ping-pongings/knowledge-base/sentiment_shift.json`; its current-main blob was preserved and excluded from this proposal.

## Prediction integrity root cause
The legacy 45.5% / 772-of-1,697 figure is not validated out-of-sample evidence. The legacy scorer uses a variable elapsed horizon after a 24-hour minimum, a mutable live price, and rewrites historical evaluation files. Current main's row-level forecast history is empty, so the aggregate cannot be reproduced from the current tree.

## Proposed fail-closed controls
- Disable the network-dependent variable-horizon scorer and scheduled workflow.
- Replace it with deterministic status-only evaluation.
- Archive the old aggregate as explicitly unvalidated.
- Set forecast issuance to BLOCKED_NO_VALIDATED_FIXED_HORIZON_DATA.
- Make sentiment forecast-ineligible and remove unsupported predictive/trading claims.
- Treat missing/nonfinite classifier confidence as zero.
- Add regression tests.

## Verification
- Predecessor #1569 exact head passed 359 tests + 8 subtests in 7.89 seconds; its fail-closed gate passed.
- This fresh-main head has not yet run CI; pending.
- Local tests were not run.
- No changed-path overlap except the generated sentiment-shift artifact, which was preserved from current main.

## Prediction requirements still missing
Point-in-time immutable feature snapshots, fixed horizons, walk-forward splits, leakage prevention, baseline comparisons, calibrated probabilities, drift detection, independent outcome attestation and paper/shadow evaluation remain required. No forecast is issued until these gates pass.

## Next actions
Verify exact-head CI and fail-closed gate for the fresh-main proposal. Inspect its diff for stale endpoint references and accidental marketing claims. Keep forecast issuance blocked. Continue separate XRP market-quality model work using venue-specific depth and execution data; do not convert sentiment or static depth into directional signals.

## Preservation
Main unchanged at `ba121a1051c84ceb311e5c65e38a18659dcd7f0e`; no merge, force-push, workflow dispatch, secret access, deployment, paper position or real-money transaction.
