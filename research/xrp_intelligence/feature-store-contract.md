# XRP point-in-time feature-store contract v1

## Status
The schema contract is DESIGNED. A deterministic in-memory point-in-time validator is EXECUTED in barrot_agent/evolution/point_in_time_features.py and covered by tests/test_point_in_time_features.py. No live ingestion adapter or persistent historical feature database is enabled. The fixed-horizon forecast ledger remains a separate recording/scoring component.

## Feature record
Each observation must include: stable feature ID/version; canonical asset; controlled feature name; typed value and explicit unit; event time; first public availability time (known_at); provider data-as-of time; ingestion time; immutable source IDs; source-independence groups; venue/instrument/currency pair/market type/aggregation window where relevant; quality status; revision status; model-eligibility flag/reason; raw and normalized content hashes; parser/adapter version; limitations and disconfirming-evidence IDs.

## Point-in-time eligibility
For forecast cutoff T:
1. known_at_utc <= T.
2. source_data_as_of_utc <= T; if the provider cannot establish this, the record is not eligible for strict historical replay.
3. The record is not disputed, stale, missing, or revised after T.
4. ingested_at_utc <= T. Schema v1 does not support historical reconstruction; late-ingested records are excluded rather than backdated.
5. All source IDs resolve to immutable provenance; units, venue and aggregation semantics are explicit.
6. Corroboration counts unique independence groups, not syndicated copies.

A future event can be a valid feature if announced by T: event_time may be after T, but known_at must be at or before T. This prevents confusing event occurrence with information availability.

## Snapshot contract
The validator computes normalized-content SHA-256 hashes and deterministic snapshot SHA-256 IDs over canonical manifests and eligible feature records. Manifests record asset scope, cutoff, capture time, adapters, parsers, source IDs/groups, record counts and quality exclusions. Excluded records contribute only record IDs and exclusion reasons; excluded values are not placed in the model-facing snapshot. Snapshots are immutable; corrections create new versions and supersession links. Conflicting provider observations remain separate until reconciled. Preserve raw provider timestamps and normalized UTC timestamps.

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
Forecasts reference immutable feature snapshot IDs and maximum feature timestamps. Use chronological walk-forward splits, purge/embargo overlapping horizons, no random shuffling, and no revised data unavailable at the historical cutoff. Compare no-change, momentum, mean-reversion, volatility-aware and market-beta baselines. Report class-wise calibration, Brier, log loss, uncertainty, drift and sample counts by horizon/cohort. Do not pool unlike horizons, venues or scoring versions.

Paper/shadow evaluation begins only after reproducible data and baseline comparisons. No real-money execution is in scope.


## Validator v1 implementation boundary
- Pure deterministic validation only; no network access, filesystem persistence, scheduled ingestion or model training.
- Requires timezone-aware event, known-at, provider-as-of, revision-available and ingestion timestamps.
- A future event date is allowed only when the exact record version was known and ingested by the cutoff.
- Historical reconstruction and signed source attestations are not implemented; late ingestion is excluded.
- Source independence is counted by declared lineage group, not by URL or syndicated copy.
- Snapshot IDs are content-derived; capture time is part of the manifest, so separately captured snapshots have different IDs.
