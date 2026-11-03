# XRP fixed-horizon forecast ledger contract v1

## Status

Implemented as a deterministic recording/scoring prototype in the draft PR #1590 branch. It does not generate forecasts, ingest live data, train a model, or place trades. It is not merged into main and must not be treated as an operational predictor.

## Fixed horizons and target

Supported horizons are 1 hour, 4 hours, 24 hours, 7 days and 30 days. Each horizon is a separate forecast record and target. The target definition must state the exact XRP/USD price/return measure and venue convention.

The three outcome classes are:
- down: realized return is below the negative predeclared flat band.
- flat: realized return is inside the flat band.
- up: realized return is above the positive flat band.

The flat band is recorded in basis points before the outcome is known. The ledger records fee and slippage assumptions but does not subtract them from the market-return class; strategy P&L and cost-adjusted utility must be evaluated separately.

## Forecast record requirements

Every forecast records:
- asset, venue and explicit target definition;
- reference price, its exact UTC observation timestamp, the registered source ID that supplied it, a declared maximum age, and immutable data cutoff;
- issue timestamp, fixed horizon and derived target timestamp;
- model version and baseline model version;
- a complete down / flat / up probability distribution for both model and baseline;
- flat-band threshold, outcome timestamp tolerance, fee and slippage assumptions;
- maximum feature timestamp, feature snapshot IDs and source IDs;
- explicit assumptions and at least one alternative/counter-hypothesis;
- optional point target price.

All timestamps must be timezone-aware UTC. The reference-price observation must not be later than data_cutoff_utc, must be no older than reference_price_max_age_seconds (bounded to 0–3,600 seconds), and its reference_price_source_id must appear in source_ids. feature_max_timestamp_utc cannot exceed data_cutoff_utc; target_time_utc must equal cutoff plus the declared horizon; issuance must occur after cutoff and before target time. These checks close a leakage path where the reference price used to calculate realized return could previously be timestamped after the forecast cutoff. Forecast IDs are deterministic SHA-256 hashes of canonicalized records, making identical retries idempotent.

## Outcome and scoring rules

A scored outcome requires a positive price timestamped within the predeclared target-time tolerance, a venue identifier, and outcome source IDs. A different outcome venue requires an explicit normalization method. Outcomes cannot be recorded before the target time or resolved before the source observation timestamp.

If a target price cannot be obtained within the declared tolerance, the outcome is recorded as unscorable with a reason. It is not treated as a prediction miss. A forecast can have only one immutable outcome.

The prototype reports:
- three-class Brier mean-squared error (sum of class squared errors divided by three);
- log loss;
- top-class directional accuracy;
- the same scores for the declared baseline;
- improvement versus baseline;
- coarse confidence bins comparing the highest class probability with observed top-class accuracy;
- separate metric cohorts keyed by asset, venue, horizon, model version, baseline version, target definition, flat band and outcome timestamp tolerance.

The summary never pools metrics across unlike cohorts. Top-level metrics are populated only when all scored forecasts belong to one cohort; otherwise top-level score fields are null and consumers must use the per-cohort summaries. This prevents 1-hour, 24-hour, 7-day or different-model forecasts from being combined into a misleading single accuracy or calibration figure. The accuracy field is top-class classification accuracy over down/flat/up and includes the flat class; it is not a binary directional win rate.

The Brier normalization is explicitly versioned as three_class_brier_mean_squared_error_v1; compare only like-for-like scoring versions. Confidence bins are a coarse diagnostic, not full class-wise multiclass calibration.

## Storage and safety

The prototype uses SQLite with write transactions and database triggers that reject updates/deletes to forecast, outcome and event records. Events are append-only. No network access, credentials, external writes, or trading actions are included.

## Existing calibration-engine gap

The existing generic confidence_calibration.py stores only claim_id, one scalar confidence, status and a Boolean outcome. Its summary converts confidence to a 0.5 threshold and reports binary accuracy; it does not record data cutoffs, horizons, targets, source provenance, feature snapshots, probability distributions, baselines, Brier score, log loss or calibration bins. Repeated claim IDs are present in its data file, and malformed JSON is silently treated as an empty record set before a later save can overwrite the file. It is not suitable for XRP price-forecast evaluation and must not be used as evidence of model performance.

## Not yet implemented

- scheduled public-data ingestion, source independence and point-in-time feature snapshots;
- per-feature source timestamps and immutable feature-store hashes;
- venue aggregation and exchange/market-quality rules;
- walk-forward splits, leakage-safe training, baselines and statistical uncertainty;
- drift monitoring, class-wise calibration and independent red-team review;
- paper/shadow operation and operational monitoring.

No predictive performance claim is possible until those components are implemented and evaluated on genuinely out-of-sample outcomes.
