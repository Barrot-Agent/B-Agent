# XRP fixed-horizon forecast ledger contract v1

## Status
The deterministic SQLite recording/scoring prototype is EXECUTED in `barrot_agent/evolution/forecast_ledger.py` and covered by `tests/test_forecast_ledger.py`. The ledger itself does not ingest data, generate forecasts, train a model or trade. A first read-only public XRP market adapter is implemented on PR #1640, but is not merged or verified on main; it produces one artifact per run and does not create a durable historical dataset. The database is runtime state and is excluded from Git.

The ledger is restricted to live/shadow issuance: each immutable issuance event records the actual ledger receipt time and `recording_mode=live_shadow`; the target must still be in the future at receipt; caller-supplied issue time cannot be after receipt or more than five minutes old. Historical backtests must use separate evaluation artifacts and must not be inserted as live forecasts.

Every issuance requires an injected `HistoricalFeatureStore`. Each feature snapshot ID must be a 64-character SHA-256 ID and resolve to an exact snapshot whose manifest, rows, source lineage and SQLite integrity verify. The snapshot must cover the forecast asset, have a data cutoff no later than the forecast cutoff, and have been captured and stored no later than that cutoff. Forecast source IDs must exactly match the union of source IDs in the referenced asset-specific records. `feature_max_timestamp_utc` must equal the maximum of `known_at_utc`, `source_data_as_of_utc`, `ingested_at_utc` and `revision_available_at_utc` across those records. This closes the local cross-store reference gap; it does not authenticate external publishers or independently anchor store receipts.

## Forecast definition
Supported horizons: 1 hour, 4 hours, 24 hours, 7 days and 30 days. Every record defines the exact XRP/USD target measure, venue convention, flat band and target timestamp. Down/flat/up classes are determined by a flat band fixed before the outcome is known.

## Required record
Asset, venue, target definition, reference price and UTC timestamp, reference source ID and maximum age, data cutoff, issue time, horizon and target time, model and baseline versions, complete three-class probabilities for both model and baseline, feature maximum timestamp, feature snapshot IDs, source IDs, assumptions, alternatives, outcome timestamp tolerance, fees and slippage. All timestamps are timezone-aware UTC.

Reference price and all feature timestamps must not exceed the data cutoff. Reference price must meet the declared maximum age. Issue time must be at or after cutoff and before target time, and must be no later than actual ledger receipt. Target time must equal cutoff plus horizon and remain in the future when recorded. Identical records are idempotent via canonical SHA-256 IDs.

## Outcome and scoring
Outcomes are recorded once, only after the target time. Scored outcomes require a positive price observed within the predeclared target-time tolerance, an outcome venue and source IDs. Cross-venue outcomes require an explicit normalization method. Missing outcomes are marked unscorable with a reason, never counted as misses.

The prototype reports three-class Brier mean-squared error, log loss, top-class accuracy and the same metrics for a declared baseline. It separates cohorts by asset, venue, horizon, model/baseline version, target definition, flat band and tolerance; unlike cohorts are never pooled. Confidence bins are coarse diagnostics, not full class-wise calibration.

## Integrity limits
SQLite transactions and triggers reject ordinary SQL UPDATE/DELETE of forecast, outcome and event rows. They are not cryptographically tamper-proof against database-file replacement, schema modification or host compromise. Stronger tamper evidence requires signed/independently anchored exports. Runtime DB and sidecars are ignored by Git.

## Not implemented
The first scheduled read-only public-market adapter exists on PR #1640, but it is not merged or operational on main and currently produces a per-run artifact rather than a cross-run historical dataset. No scheduled historical feature population, forecast generator, model training, walk-forward evaluation, baseline superiority, class-wise calibration, uncertainty intervals, drift detection, shadow scheduler or trading integration is included. The ledger is a recorder/scorer only; no directional forecast is authorized until populated point-in-time data and leakage-safe out-of-sample evaluation support it. The separate local SQLite feature-store prototype exists but is not yet populated with a durable historical XRP dataset.


## First public adapter boundary

The first read-only scheduled Binance/Kraken adapter is implemented in PR #1640 and is separate from the forecast ledger. It writes content-addressed raw receipts and a point-in-time snapshot, but has not been merged to main and has no verified scheduled run. Its output explicitly sets `forecast_status=NOT_ISSUED` and `forecast_model_eligible=false`. The adapter does not train or issue forecasts; it is not evidence of model quality or predictive edge.
