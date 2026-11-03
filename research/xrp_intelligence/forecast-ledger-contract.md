# XRP fixed-horizon forecast ledger contract v1

## Status
Proposed in draft PR #1611. Deterministic recording/scoring prototype only. It does not generate forecasts, ingest live data, train a model or trade. The SQLite database is runtime state and is excluded from Git.

## Forecast definition
Supported horizons: 1 hour, 4 hours, 24 hours, 7 days and 30 days. Every record defines the exact XRP/USD target measure, venue convention, flat band and target timestamp. Down/flat/up classes are determined by a flat band fixed before the outcome is known.

## Required record
Asset, venue, target definition, reference price and UTC timestamp, reference source ID and maximum age, data cutoff, issue time, horizon and target time, model and baseline versions, complete three-class probabilities for both model and baseline, feature maximum timestamp, feature snapshot IDs, source IDs, assumptions, alternatives, outcome timestamp tolerance, fees and slippage. All timestamps are timezone-aware UTC.

Reference price and all feature timestamps must not exceed the data cutoff. Reference price must meet the declared maximum age. Issue time must be at or after cutoff and before target time. Target time must equal cutoff plus horizon. Identical records are idempotent via canonical SHA-256 IDs.

## Outcome and scoring
Outcomes are recorded once, only after the target time. Scored outcomes require a positive price observed within the predeclared target-time tolerance, an outcome venue and source IDs. Cross-venue outcomes require an explicit normalization method. Missing outcomes are marked unscorable with a reason, never counted as misses.

The prototype reports three-class Brier mean-squared error, log loss, top-class accuracy and the same metrics for a declared baseline. It separates cohorts by asset, venue, horizon, model/baseline version, target definition, flat band and tolerance; unlike cohorts are never pooled. Confidence bins are coarse diagnostics, not full class-wise calibration.

## Integrity limits
SQLite transactions and triggers reject ordinary SQL UPDATE/DELETE of forecast, outcome and event rows. They are not cryptographically tamper-proof against database-file replacement, schema modification or host compromise. Stronger tamper evidence requires signed/independently anchored exports. Runtime DB and sidecars are ignored by Git.

## Not implemented
No public-data ingestion, point-in-time feature store, source-independence engine, historical feature snapshots, walk-forward training/evaluation, leakage-safe splits, uncertainty intervals, drift detection, full class-wise calibration, shadow operation or trading.
