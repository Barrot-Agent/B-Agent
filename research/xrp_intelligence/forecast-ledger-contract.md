# XRP fixed-horizon forecast ledger contract v3

## Status
The deterministic SQLite recording/scoring prototype is EXECUTED in `barrot_agent/evolution/forecast_ledger.py` and covered by `tests/test_forecast_ledger.py`. Readiness reports require an Ed25519 signature from an externally trusted evaluator key; the production default has no trusted keys and therefore fails closed. The ledger itself does not ingest data, generate forecasts, train a model or trade. PR #1640 defines 35 public endpoint records (33 scheduled; two free non-commercial XRPL nodes excluded) and a workflow that trusts exact cache hits only; on a miss or partial cache restore it searches up to 30 pages of 100 completed main-branch ingestion runs, restoring the newest successful per-run checkpoint (7-day retention) and falling back to the daily/manual archive (90-day retention). It is not merged to main, no scheduled main-branch run is verified, and no mature multi-run XRP dataset exists. Cache is evictable and artifacts expire; this is bounded recovery, not external WORM persistence or independent timestamp anchoring. The database is runtime state and is excluded from Git.


## Bybit linear derivatives coverage

The public collector includes Bybit V5 XRPUSDT linear-perpetual ticker, one-hour open-interest history and funding-settlement history endpoints. Official endpoint contracts: https://bybit-exchange.github.io/docs/v5/market/tickers, https://bybit-exchange.github.io/docs/v5/market/open-interest, and https://bybit-exchange.github.io/docs/v5/market/history-fund-rate.

The ticker's top-level time is retained as response/server snapshot time, not misrepresented as a trade or settlement timestamp. Current fundingRate is retained separately from historical fundingRateTimestamp events, and fundingIntervalHour is recorded rather than assuming an eight-hour interval. Bybit documents openInterest/openInterestValue as both-sides totals and singleOpenInterest/singleOpenInterestValue as single-side values; both the ticker and open-interest history adapters retain both conventions separately without doubling, halving or cross-venue averaging. Linear open-interest history is retained in the base asset (XRP), not silently converted to contracts or USD. Historical rows are first known at their actual collector capture time. The open-interest and funding history adapters capture one page (maximum 200 rows) and explicitly retain pagination limitations; they do not claim a complete lifetime history.


The ledger is restricted to live/shadow issuance: each immutable issuance event records the actual ledger receipt time and `recording_mode=live_shadow`; the target must still be in the future at receipt; caller-supplied issue time cannot be after receipt or more than five minutes old. Historical backtests must use separate evaluation artifacts and must not be inserted as live forecasts.

Every issuance requires an injected `HistoricalFeatureStore`. Each feature snapshot ID must be a 64-character SHA-256 ID and resolve to an exact snapshot whose manifest, rows, source lineage and SQLite integrity verify. The snapshot must cover the forecast asset, have a data cutoff no later than the forecast cutoff, and have been captured and stored no later than that cutoff. Forecast source IDs must exactly match the union of source IDs in the referenced asset-specific records. `feature_max_timestamp_utc` must equal the maximum of `known_at_utc`, `source_data_as_of_utc`, `ingested_at_utc` and `revision_available_at_utc` across those records. This closes the local cross-store reference gap; it does not authenticate external publishers or independently anchor store receipts.

## Independent evaluator attestation (policy v3)

A readiness report is not trusted because it contains self-declared `PASS` fields or better metrics. Policy v3 requires all of the following:

- `evaluator_id` matching a configured trusted `key_id`, plus a non-empty `evaluator_version`.
- SHA-256 identifiers for the evaluation code and the independently produced evaluation artifact.
- An `evaluator_attestation` object with exactly `scheme`, `key_id`, `signed_payload_sha256`, `signature_base64` and `attested_at_utc`.
- An Ed25519 signature over the domain-separated SHA-256 digest of canonical JSON containing the complete readiness report without `evaluator_attestation` plus the attestation's `scheme`, `key_id` and `attested_at_utc` metadata. The signature and its digest are excluded from the signed payload, so the evaluator identity and attestation time cannot be changed after signing.
- An attestation time no earlier than evaluation completion and no later than the ledger's actual report-registration receipt time.

The trust store is supplied through the `BARROT_XRP_EVALUATOR_PUBLIC_KEYS_JSON` environment variable as a JSON object mapping evaluator key IDs to base64-encoded 32-byte Ed25519 public keys. The private signing key must remain with an independently operated evaluator and must never be committed to this repository or exposed to the model/training workflow. Key provisioning, evaluator independence and the evaluator's reproducible execution pipeline are not yet configured or verified. With no trusted key configured, readiness registration and forecast issuance are rejected. Test-only signing keys exist only in the test module and do not populate the production trust store.

Policies v1 and v2 are not accepted by policy v3. The v3 attestation domain is `BARROT_XRP_MODEL_READINESS_V3\0`.

## Purged and embargoed evaluation requirement

Every readiness report must include `embargo_seconds` as a non-boolean integer at least as large as `horizon_seconds`, and `purge_policy=training_start_and_outcome_available_by_cutoff_minus_embargo`. The walk-forward evaluator excludes training start and outcome records that were not available by `data_cutoff_utc - embargo_seconds`. The hourly scheduled collector evaluates the 1-hour horizon only. The daily 00:15 UTC schedule and manual dispatch evaluate 1h, 4h, 24h, 7d and 30d. Every horizon uses an embargo equal to that horizon, with 100 minimum point-in-time training examples and 100 minimum out-of-sample origins; insufficient history is reported and never relaxed. The source feature bars remain hourly. Origins therefore remain hourly and target windows overlap for horizons longer than one hour; no block bootstrap, HAC interval or effective-sample-size adjustment is implemented. These multi-horizon results are descriptive and remain model-ineligible. The momentum predictor may use the latest point-in-time feature return, but that predictor is not admitted as a training label inside the embargo window.

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

## Temporal baseline probability calibration — implemented, not yet validated on live XRP history

`apply_temporal_temperature_calibration` implements `rolling_temporal_temperature_scaling_v1` for the four deterministic baseline probability outputs. It uses only earlier resolved out-of-sample outcomes whose data cutoff and outcome-availability time are both before the current calibration cutoff. It deduplicates target records, retains at most 250 prior outcomes, requires at least 50, fits temperature on the earliest 80%, and validates on the later 20%. Recalibration is applied only when later validation log loss improves by at least 0.005; otherwise the identity transform is retained.

**Status:** EXECUTED in `barrot_agent/evolution/probability_calibration.py` and integrated into `walk_forward.py` on PR #1640; regression-tested by `tests/test_probability_calibration.py` and `tests/test_walk_forward.py`. NOT VERIFIED on a mature, synchronized, independent live XRP history. This calibrates deterministic baselines; it does not train a predictive model, demonstrate directional lift, or establish stable real-world calibration. Forecast issuance remains fail-closed pending independent outcome evidence, drift and shadow gates, and trusted evaluator attestation.

## Not implemented
The PR #1640 collector defines 35 public endpoint records, 33 scheduled after excluding two non-commercial XRPL public-node endpoints. Its workflow now implements exact-cache-hit trust, per-run feature-store checkpoint restore (7-day retention), daily/manual archive fallback (90-day retention), and a bounded search of up to 30 pages of 100 completed main-branch ingestion runs. The branch is not merged, no scheduled main run is verified, and no mature multi-run dataset exists. Cache is evictable and artifacts expire; this is bounded recovery, not external WORM retention or independent timestamp anchoring. No live scheduled historical feature population, forecast issuance, independently attested model evaluation, baseline superiority, calibration quality on mature independent XRP outcomes, uncertainty intervals, scheduled drift monitoring or shadow scheduler is verified. Temporal temperature scaling for deterministic baseline probabilities is implemented and tested, but has not been validated on mature live XRP outcomes; no trained predictive model is present. A deterministic four-baseline chronological walk-forward evaluator with explicit horizon-sized embargoes is implemented and tested on PR #1640. Hourly runs evaluate 1h; the daily 00:15 UTC run and manual dispatch evaluate 1h, 4h, 24h, 7d and 30d for Binance XRP/USDT and Coinbase XRP/USD. Multi-day origins remain hourly and overlapping; no dependence-aware confidence intervals or block-bootstrap adjustment is implemented. The evaluator has not produced validated out-of-sample results from a sufficiently mature live XRP dataset. No production evaluator key or independently operated signing service is configured. The ledger is a recorder/scorer only; no directional forecast is authorized until populated point-in-time data, independently attested purged/embargoed out-of-sample evaluation, validated calibration performance, stable drift evidence, shadow outcomes and a trusted evaluator key support it. The separate local SQLite feature-store prototype exists but is not yet populated with a durable historical XRP dataset.


## First public adapter boundary

The first read-only scheduled Binance/Coinbase/Kraken/OKX adapter is implemented in PR #1640 and is separate from the forecast ledger. It writes content-addressed raw receipts and a point-in-time snapshot, but has not been merged to main and has no verified scheduled run. Its output explicitly sets `forecast_status=NOT_ISSUED` and `forecast_model_eligible=false`. The adapter does not train or issue forecasts; it is not evidence of model quality or predictive edge.


## Research-archive timestamp correction consumption

**EXECUTED on the Barrot V3 integration branch; not yet on main.** The read-only archive consumer is implemented in `barrot_agent/evolution/research_timestamp_corrections.py` as `apply_research_timestamp_correction_overlays(repository_root)`. It scans the XRP research archive and applies only two explicitly supported machine-readable timestamp correction formats: the canonical `barrot.xrp.research-correction.v1` field overlay and the earlier run-start interval correction schema (`schema_version: 1`, `append_only_xrp_research_timestamp_correction`). Both require an exact Git-blob preimage. The legacy adapter removes the synthetic run-start retrieval labels from the spot record and source list, replaces the top-level data cutoff with the conservative availability upper bound, and preserves provider update times, ETF data dates, numeric values, URLs and raw-response text hashes.

The consumer returns corrected in-memory views and application manifests only. It does not rewrite source files, infer an exact retrieval time, promote eligibility or issue a forecast. It reports narrative correction addenda separately. Missing targets, duplicate targets/IDs, path escapes, symlinks, preimage mismatches and unknown timestamp-correction schemas fail closed. **The consumer is not yet wired into the scheduled public collector or forecast issuance path.** Research records remain model-ineligible until their raw receipts, source times and point-in-time requirements independently pass the feature-admission contract.


## Scheduled correction-audit execution

The existing read-only `.github/workflows/xrp-public-ingestion.yml` now runs `python -m barrot_agent.evolution.research_timestamp_audit` before market capture and uploads a separate 90-day audit artifact. The audit emits exact-preimage-bound corrected research views and application manifests without modifying source files or the point-in-time feature store. An unknown timestamp-correction schema, missing target, duplicate target or preimage mismatch fails the workflow closed. The audit output itself remains model-ineligible and forecast-free. This is an executed research-archive audit path; it is **not** a feature-admission path and does not promote research records into predictive features.


## Calibration outcome-time integrity guard

Every prior forecast supplied to temporal calibration must include its `outcome_event_time_utc`. The outcome event must occur strictly after the originating forecast's `data_cutoff_utc`, and `outcome_available_at_utc` must not precede the outcome event. Invalid temporal ordering is rejected before eligibility filtering. The calibration result records the maximum prior outcome event time separately from maximum outcome-availability time. The walk-forward evaluator supplies the event timestamp from the scored target record and applies the same embargo cutoff to event availability. This guard prevents a malformed or backdated calibration-history record from entering the fit/validation partitions even if its caller supplies an early availability timestamp.
