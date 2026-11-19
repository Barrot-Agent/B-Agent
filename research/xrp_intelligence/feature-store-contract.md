# XRP point-in-time feature-store contract v1

## Status
The schema contract is DESIGNED. The pure deterministic in-memory validator is EXECUTED in `barrot_agent/evolution/point_in_time_features.py`. A separate local SQLite persistence prototype is EXECUTED in `barrot_agent/evolution/feature_store.py`; tests cover idempotent append, source-lineage retention, receipt-time as-of filtering, manifest verification and ordinary SQL mutation guards. The store is not yet populated with historical XRP data. Production market-data adapters, scheduled ingestion, raw-payload object storage, backup/retention operations and independently anchored signed manifests are not implemented.

The fixed-horizon forecast ledger is a separate recording/scoring component. Its feature snapshot IDs are not yet resolved against this store at forecast issuance; this is an explicit integration blocker.

## Feature record
Each observation must include: stable feature ID/version; canonical asset; controlled feature name; typed value and explicit unit; event time; first public availability time (known_at); provider data-as-of time; ingestion time; immutable source IDs; source-independence groups; venue/instrument/currency pair/market type/aggregation window where relevant; quality status; revision status; model-eligibility flag/reason; raw and normalized content hashes; parser/adapter version; limitations and disconfirming-evidence IDs.

## Point-in-time eligibility
For forecast cutoff T:
1. known_at_utc <= T.
2. source_data_as_of_utc <= T; if the provider cannot establish this, the record is not eligible for strict historical replay.
3. `quality_status` must be `verified`; the record must not be disputed, stale, missing, or revised after T.
4. ingested_at_utc <= T. Schema v1 does not support historical reconstruction; late-ingested records are excluded rather than backdated.
5. Each source ID must resolve to provenance embedded in the same feature record, including URI, raw-content SHA-256 and a declared independence group. External source-registry resolution and independent authentication of those groups are not implemented.
6. Corroboration counts unique declared independence groups, not syndicated copies.

A future event can be a valid feature if announced by T: event_time may be after T, but known_at must be at or before T. This prevents confusing event occurrence with information availability.

## Snapshot contract
The validator computes normalized-content SHA-256 hashes and deterministic snapshot SHA-256 IDs over canonical manifests and eligible feature records. Manifests record asset scope, cutoff, capture time, adapters, parsers, source IDs/groups, record counts and quality exclusions. Excluded records contribute only record IDs and exclusion reasons; excluded values are not placed in the model-facing snapshot. Corrections create new versions and supersession links. Conflicting provider observations remain separate until reconciled. Persist normalized UTC timestamps. Schema v1 does not retain the original provider timestamp string; raw payload archival is a separate adapter/object-store requirement and is not implemented.

The local SQLite store persists the canonical manifest, normalized records, source lineage and actual store-receipt time. As-of retrieval requires both the data cutoff and store receipt to be no later than the requested time. SQLite triggers reject ordinary UPDATE/DELETE operations, but this is not cryptographic tamper-proof storage; a database owner can replace the file or remove triggers.

## XRP feature families
- Spot microstructure: venue trades, OHLCV, bid/ask, spread, fixed-band depth, trade imbalance, realized volatility, VWAP, slippage and outages.
- Derivatives: open interest by venue/contract, funding, basis, expiry, liquidations and account/position long-short ratios separately.
- ETF/listed products: issuer creations/redemptions, holdings, AUM and net flows; spot, futures and index products remain distinct.
- XRPL: ledger close, payments, DEX/AMM volume and liquidity, active accounts, fees, reserves, amendments, RLUSD/USDC supply.
- Institutional/corporate: custody availability, collateral eligibility versus actual utilization, payment throughput, announced capacity versus committed/drawn capital, cash receipts, share issuance, XRP purchases and wallet movements.
- Stablecoins: issuer, chain, contract, supply, mint/burn, reserves, redemption, venue liquidity and bridge/settlement role.
- Macro/cross-asset: rates, yields, USD, liquidity, risk indices, equities, commodities and macro release vintages.
- Regulatory/geopolitical: publication time, jurisdiction, legal status, effective date, authority, affected entity and competing interpretations.
- Sentiment/creator claims: separate context features; never convert sentiment into forecast probabilities without independent validation.

## Evaluation linkage
Forecasts must reference immutable feature snapshot IDs and maximum feature timestamps. Before issuance is trusted, the ledger must verify that every referenced snapshot exists, covers the forecast asset, was actually stored by the data cutoff, and contains the declared source lineage. This cross-store validation is not implemented yet. Use chronological walk-forward splits, purge/embargo overlapping horizons, no random shuffling, and no revised data unavailable at the historical cutoff. Compare no-change, momentum, mean-reversion, volatility-aware and market-beta baselines. Report class-wise calibration, Brier, log loss, uncertainty, drift and sample counts by horizon/cohort. Do not pool unlike horizons, venues or scoring versions.

Paper/shadow evaluation begins only after reproducible data and baseline comparisons. No real-money execution is in scope.

## Validator and persistence implementation boundary
- Validator: pure deterministic validation only; no network access or filesystem I/O.
- Persistence: separate local SQLite prototype; not populated with historical XRP records and not scheduled.
- Historical reconstruction, signed source attestations, external source-registry authentication and production ingestion are not implemented.
- Source independence is counted by declared lineage group, not cryptographically authenticated.
- Snapshot IDs are content-derived; capture time is part of the manifest, so separately captured snapshots have different IDs.


## SQLite persistence and integrity verification

The persistence prototype uses three tables:

- `snapshots`: canonical manifest, snapshot ID, data cutoff, capture time, actual store receipt time, asset scope and row counts.
- `feature_records`: normalized model-facing records with event time, first-known time, source-data-as-of time, ingestion time, revision time, quality state and source references.
- `source_snapshots`: source ID, declared publisher-lineage group, URI and raw-content SHA-256 reference for each snapshot.

Raw source bodies are not stored in SQLite. A future adapter must preserve raw payloads in a controlled immutable artifact/object store and provide the retrieval reference and SHA-256. The current store cannot independently recompute a raw-source hash without the raw bytes.

`verify_snapshot` checks the canonical manifest hash and snapshot ID; snapshot-row cutoff, capture time and asset scope; canonical feature records and denormalized columns; source-lineage rows; record/source counts; and SQLite `PRAGMA integrity_check`.

The snapshot row's `stored_at_utc` is an actual store-receipt timestamp and has no manifest counterpart; it is checked by as-of retrieval rather than compared to the manifest.

SQLite triggers reject ordinary UPDATE and DELETE operations, but they are not a cryptographic tamper-proof boundary. A database owner can replace the file, remove triggers or recompute unkeyed hashes. Stronger auditability requires signed manifests, external append-only/WORM storage and independent timestamp anchoring. The host system clock is trusted for `stored_at_utc`; it is not an external trusted timestamp.

The uppercase `FEATURE_STORE_CONTRACT.md` file is a compatibility pointer to this authoritative contract. Do not maintain a second independent contract.
