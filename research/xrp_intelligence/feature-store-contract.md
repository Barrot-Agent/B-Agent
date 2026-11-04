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
3. The record is not disputed, stale, missing, or revised after T.
4. ingested_at_utc <= T. Schema v1 does not support historical reconstruction; late-ingested records are excluded rather than backdated.
5. Each source ID must resolve to provenance embedded in the same feature record, including URI, raw-content SHA-256 and a declared independence group. External source-registry resolution and independent authentication of those groups are not implemented.
6. Corroboration counts unique declared independence groups, not syndicated copies.

A future event can be a valid feature if announced by T: event_time may be after T, but known_at must be at or before T. This prevents confusing event occurrence with information availability.

## Snapshot contract
The validator computes normalized-content SHA-256 hashes and deterministic snapshot SHA-256 IDs over canonical manifests and eligible feature records. Manifests record asset scope, cutoff, capture time, adapters, parsers, source IDs/groups, record counts and quality exclusions. Excluded records contribute only record IDs and exclusion reasons; excluded values are not placed in the model-facing snapshot. Corrections create new versions and supersession links. Conflicting provider observations remain separate until reconciled. Preserve raw provider timestamps and normalized UTC timestamps.

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
