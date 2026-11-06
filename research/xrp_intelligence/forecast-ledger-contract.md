# XRP fixed-horizon forecast ledger contract v3

## Status
The deterministic SQLite recording/scoring prototype is EXECUTED in `barrot_agent/evolution/forecast_ledger.py` and covered by `tests/test_forecast_ledger.py`. Readiness reports require an Ed25519 signature from an externally trusted evaluator key; the production default has no trusted keys and therefore fails closed. The ledger itself does not ingest data, generate forecasts, train a model or trade. PR #1640 defines 21 public endpoint records (19 scheduled; two free non-commercial XRPL nodes excluded) and a workflow that trusts exact cache hits only; on a miss or partial cache restore it searches up to 30 pages of 100 completed main-branch ingestion runs, restoring the newest successful per-run checkpoint (7-day retention) and falling back to the daily/manual archive (90-day retention). It is not merged to main, no scheduled main-branch run is verified, and no mature multi-run XRP dataset exists. Cache is evictable and artifacts expire; this is bounded recovery, not external WORM persistence or independent timestamp anchoring. The database is runtime state and is excluded from Git.

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

Every readiness report must include `embargo_seconds` as a non-boolean integer at least as large as `horizon_seconds`, and `purge_policy=training_start_and_outcome_available_by_cutoff_minus_embargo`. The walk-forward evaluator excludes training start and outcome records that were not available by `data_cutoff_utc - embargo_seconds`. The hourly public XRP evaluation uses a 3,600-second embargo for its one-hour horizon. The momentum predictor may use the latest point-in-time feature return, but that predictor is not admitted as a training label inside the embargo window.

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
The PR #1640 collector defines 21 public endpoint records, 19 scheduled after excluding two non-commercial XRPL public-node endpoints. Its workflow now implements exact-cache-hit trust, per-run feature-store checkpoint restore (7-day retention), daily/manual archive fallback (90-day retention), and a bounded search of up to 30 pages of 100 completed main-branch ingestion runs. The branch is not merged, no scheduled main run is verified, and no mature multi-run dataset exists. Cache is evictable and artifacts expire; this is bounded recovery, not external WORM retention or independent timestamp anchoring. No live scheduled historical feature population, forecast issuance, independently attested model evaluation, baseline superiority, fitted probability recalibration, uncertainty intervals, scheduled drift monitoring or shadow scheduler is verified. A deterministic four-baseline chronological walk-forward evaluator with an explicit horizon-sized embargo is implemented and tested on PR #1640, but it has not produced validated out-of-sample results from a sufficiently mature live XRP dataset. No production evaluator key or independently operated signing service is configured. The ledger is a recorder/scorer only; no directional forecast is authorized until populated point-in-time data, independently attested purged/embargoed out-of-sample evaluation, fitted calibration, stable drift evidence, shadow outcomes and a trusted evaluator key support it. The separate local SQLite feature-store prototype exists but is not yet populated with a durable historical XRP dataset.


## First public adapter boundary

The first read-only scheduled Binance/Kraken adapter is implemented in PR #1640 and is separate from the forecast ledger. It writes content-addressed raw receipts and a point-in-time snapshot, but has not been merged to main and has no verified scheduled run. Its output explicitly sets `forecast_status=NOT_ISSUED` and `forecast_model_eligible=false`. The adapter does not train or issue forecasts; it is not evidence of model quality or predictive edge.


## Research-archive timestamp correction consumption

**EXECUTED on the Barrot V3 integration branch; not yet on main.** The read-only archive consumer is implemented in `barrot_agent/evolution/research_timestamp_corrections.py` as `apply_research_timestamp_correction_overlays(repository_root)`. It scans the XRP research archive and applies only two explicitly supported machine-readable timestamp correction formats: the canonical `barrot.xrp.research-correction.v1` field overlay and the earlier run-start interval correction schema (`schema_version: 1`, `append_only_xrp_research_timestamp_correction`). Both require an exact Git-blob preimage. The legacy adapter removes the synthetic run-start retrieval labels from the spot record and source list, replaces the top-level data cutoff with the conservative availability upper bound, and preserves provider update times, ETF data dates, numeric values, URLs and raw-response text hashes.

The consumer returns corrected in-memory views and application manifests only. It does not rewrite source files, infer an exact retrieval time, promote eligibility or issue a forecast. It reports narrative correction addenda separately. Missing targets, duplicate targets/IDs, path escapes, symlinks, preimage mismatches and unknown timestamp-correction schemas fail closed. **The consumer is not yet wired into the scheduled public collector or forecast issuance path.** Research records remain model-ineligible until their raw receipts, source times and point-in-time requirements independently pass the feature-admission contract.


## Scheduled correction-audit execution

The existing read-only `.github/workflows/xrp-public-ingestion.yml` now runs `python -m barrot_agent.evolution.research_timestamp_audit` before market capture and uploads a separate 90-day audit artifact. The audit emits exact-preimage-bound corrected research views and application manifests without modifying source files or the point-in-time feature store. An unknown timestamp-correction schema, missing target, duplicate target or preimage mismatch fails the workflow closed. The audit output itself remains model-ineligible and forecast-free. This is an executed research-archive audit path; it is **not** a feature-admission path and does not promote research records into predictive features.
