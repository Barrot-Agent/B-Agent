# XRP point-in-time feature-store contract v1

## Status
The schema contract is DESIGNED. The pure deterministic in-memory validator is EXECUTED in `barrot_agent/evolution/point_in_time_features.py`. A separate local SQLite persistence prototype is EXECUTED in `barrot_agent/evolution/feature_store.py`; tests cover idempotent append, source-lineage retention, receipt-time as-of filtering, manifest verification and ordinary SQL mutation guards. The store is not yet populated with a sufficiently mature historical XRP dataset. The read-only public-market adapter and hourly GitHub Actions workflow are EXECUTED on PR #1640's exact head, but are not merged to main and have no verified scheduled main-branch run. The collector defines 32 public endpoint records, of which 30 are scheduled; the two free non-commercial XRPL public-node endpoints are excluded by default. Scheduled sources span Binance spot/perpetual, Coinbase and Kraken spot, OKX XRP-USDT spot ticker and timestamped order book, ETF/issuer and exchange-balance sources. Coinbase hourly candles also support an explicit manual-only backfill of up to 365 additional days before the oldest candle in the default latest page; each page is bounded to 300 hourly buckets and receives its own raw-source receipt. Scheduled runs do not request historical pages. Source-specific parsers produce normalized features, raw-only records or digest-only receipts according to timestamp quality and source terms. The workflow trusts an exact Actions-cache key only; on a miss or partial restore, it first deletes any restore-key file left by a partial cache match, then searches up to 30 pages of 100 completed main-branch ingestion runs, restores the newest successful per-run feature-store checkpoint (7-day retention), and falls back to the daily/manual archive (90-day retention). It uploads per-run raw-source receipt artifacts with 90-day retention. This is bounded cross-run recovery, not durable long-term persistence: cache is evictable, artifacts expire, and no external WORM store, independent timestamp authority or signed external manifest is configured. The collector is not a complete production ingestion platform.

The fixed-horizon forecast ledger now requires an injected `HistoricalFeatureStore` and resolves every referenced SHA-256 snapshot at issuance. It verifies the exact manifest/rows/source lineage, asset scope, data cutoff, capture time and actual store receipt against the forecast cutoff. Forecast source IDs must exactly match the referenced asset-specific feature lineage, and the declared feature maximum must equal the maximum information-availability timestamp across those records. This is local integrity verification, not independent external timestamp authentication.

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

For issuer holdings and ETF/listed-product flow data, `source_data_as_of_utc` must be the effective/as-of date on the underlying issuer row, not the aggregator's displayed observation date, page update time, retrieval time, or a date inferred from a summary. If the page contains multiple dated rows, parse and validate the exact row used. If a future-dated row is present and the requested historical row cannot be isolated, mark the observation provisional and model-ineligible. Never backdate a later holdings snapshot to an earlier flow date. Holdings deltas are not creations/redemptions unless issuer evidence confirms that interpretation. Preserve the aggregator observation date, underlying issuer row date, page publication/update time, retrieval time, first public availability, and ingestion time separately.

## Snapshot contract
The validator computes normalized-content SHA-256 hashes and deterministic snapshot SHA-256 IDs over canonical manifests and eligible feature records. Manifests record asset scope, cutoff, capture time, adapters, parsers, source IDs/groups, record counts and quality exclusions. Excluded records contribute only record IDs and exclusion reasons; excluded values are not placed in the model-facing snapshot. Corrections create new versions and supersession links. Conflicting provider observations remain separate until reconciled. Persist normalized UTC timestamps. Schema v1 does not retain the original provider timestamp string in normalized feature rows. The first PR #1640 adapter preserves raw response bytes and hashes in per-run artifacts, but those artifacts have 90-day retention and are not a WORM store or independently timestamp-anchored archive.

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
Forecasts must reference immutable feature snapshot IDs and maximum feature timestamps. Before issuance is trusted, the ledger must verify that every referenced snapshot exists, covers the forecast asset, was actually stored by the data cutoff, and contains the declared source lineage. The local SQLite cross-store validation is implemented in `barrot_agent/evolution/forecast_ledger.py` and covered by tests; external source-registry authentication and independent receipt-time anchoring remain unimplemented. Use chronological walk-forward splits, purge/embargo overlapping horizons, no random shuffling, and no revised data unavailable at the historical cutoff. Compare no-change, momentum, mean-reversion, volatility-aware and market-beta baselines. Report class-wise calibration, Brier, log loss, uncertainty, drift and sample counts by horizon/cohort. Do not pool unlike horizons, venues or scoring versions.

Paper/shadow evaluation begins only after reproducible data and baseline comparisons. No real-money execution is in scope.

## Validator and persistence implementation boundary
- Validator: pure deterministic validation only; no network access or filesystem I/O.
- Persistence: local SQLite prototype; exact snapshot lookup is verified by the forecast ledger. PR #1640 writes a per-run snapshot and raw receipt archive. Its workflow trusts an exact cache hit only; on a miss or partial cache restore, it searches up to 30 pages of 100 completed main-branch ingestion runs, restores the newest successful per-run checkpoint (7-day retention), and falls back to the daily/manual archive (90-day retention). This recovery path is EXECUTED in workflow code and covered by full-suite regression tests, but is not verified on main because the PR is unmerged and no scheduled main run exists. The store is not yet populated with a sufficiently mature historical XRP dataset; cache is evictable and artifacts expire.
- Historical reconstruction, signed source attestations, external source-registry authentication, WORM/independent timestamp anchoring, cross-run durable retention and multi-domain production ingestion are not implemented.
- Source independence is counted by declared lineage group, not cryptographically authenticated.
- Snapshot IDs are content-derived; capture time is part of the manifest, so separately captured snapshots have different IDs.


## SQLite persistence and integrity verification

The persistence prototype uses three tables:

- `snapshots`: canonical manifest, snapshot ID, data cutoff, capture time, actual store receipt time, asset scope and row counts.
- `feature_records`: normalized model-facing records with event time, first-known time, source-data-as-of time, ingestion time, revision time, quality state and source references.
- `source_snapshots`: source ID, declared publisher-lineage group, URI and raw-content SHA-256 reference for each snapshot.

Raw source bodies are not stored in SQLite. The first PR #1640 adapter stores exact response bytes in a per-run content-addressed archive and records SHA-256 receipts alongside the snapshot. The feature store itself cannot independently recompute a raw-source hash without retrieving those artifact bytes. The GitHub artifact retention setting is 90 days; WORM retention, external timestamp anchoring and independent signed manifests are not configured.

`verify_snapshot` checks the canonical manifest hash and snapshot ID; snapshot-row cutoff, capture time and asset scope; canonical feature records and denormalized columns; source-lineage rows; record/source counts; and SQLite `PRAGMA integrity_check`.

The snapshot row's `stored_at_utc` is an actual store-receipt timestamp and has no manifest counterpart; it is checked by as-of retrieval rather than compared to the manifest.

SQLite triggers reject ordinary UPDATE and DELETE operations, but they are not a cryptographic tamper-proof boundary. A database owner can replace the file, remove triggers or recompute unkeyed hashes. Stronger auditability requires signed manifests, external append-only/WORM storage and independent timestamp anchoring. The host system clock is trusted for `stored_at_utc`; it is not an external trusted timestamp.

The uppercase `FEATURE_STORE_CONTRACT.md` file is a compatibility pointer to this authoritative contract. Do not maintain a second independent contract.


## First adapter scope (PR #1640; not yet on main)

- Schedule: hourly at minute 3 UTC via `.github/workflows/xrp-public-ingestion.yml`; `workflow_dispatch` is also available and exposes a manual-only Coinbase historical backfill input (0–365 additional days).
- Permissions: `contents: read`; no secrets, no repository writes and no deployment action.
- Sources: Binance XRPUSDT 24-hour spot ticker and 1-hour spot candles; Binance XRPUSDT perpetual premium/mark/index/funding/open interest/history/global long-short account ratio; Coinbase XRP-USD ticker/candles/book; Kraken XRP/USD ticker/depth; OKX XRP-USDT ticker/depth; Bitbank XRP/JPY circuit-break context, latest 60 transactions, ticker and depth; XRP ETF/issuer/exchange-balance research feeds; two explicitly excluded non-commercial XRPL node endpoints.
- Raw receipts: exact response bytes are SHA-256 addressed and accompanied by append-only per-run receipts. The per-run SQLite store verifies the normalized feature snapshot.
- Output: hourly raw-source receipt artifacts are retained 90 days. A per-run feature-store SQLite checkpoint is uploaded after every successful ingestion run with 7-day retention; the daily 00:15 UTC/manual archive also contains the database and walk-forward report with 90-day retention. Only an exact Actions-cache key is trusted. A miss or partial cache restore searches up to 30 pages of 100 completed main-branch runs, trying the newest per-run checkpoint first and the daily archive second. The cache remains evictable; GitHub artifacts are bounded recovery copies, not external WORM storage or an independent timestamp authority.
- Limits: The collector defines 29 endpoint records, 27 scheduled; the two free non-commercial XRPL public-node endpoints are excluded. Binance depth and Coinbase book are raw-only because their payloads do not meet event-time feature requirements. XRP Insights ETF-flow and exchange-balance JSON/CSV and the XRPR/Bitwise/Grayscale issuer pages are raw-only or digest-only under parser and source-term rules; they are captured as provenance/research evidence, not normalized model features. The scheduled `xrp_exchange_balances_json` source is digest-only under publisher terms; its attributed-wallet total includes cold storage and non-customer reserves, is not a tradable-float measure and remains model-ineligible. Binance, Coinbase, Kraken, OKX and Bitbank spot; Binance perpetual premium/open-interest/funding/long-short data; Bitbank timestamped XRP/JPY trade events (retained research-only pending completeness validation); and ETF/issuer/exchange-balance sources are covered at the capture layer. OKX ticker and order-book features use exchange-provided millisecond timestamps; order-book admission requires a snapshot no older than 60 seconds and does not claim sequence continuity. Bitbank ticker quote and depth features require a synchronized circuit-break state in `NONE` mode; the ticker `last` is retained as an unverified snapshot because its timestamp is not an individual trade timestamp. Bitbank depth is admitted only in continuous mode; its sequence ID is retained but no sequence bridge is claimed. The latest-60 Bitbank transaction endpoint yields timestamped per-trade JPY/XRP and signed taker-flow records, each first known at capture; all per-trade records and the run-level sample summary remain model-ineligible because the variable latest-60 window is not a complete fixed-duration flow measure and sequence/gap coverage has not been validated. JPY is not converted to USD/USDT; USDT is not converted to USD; open interest remains in contracts. Historical candles are first known at capture time. Coinbase pages are bounded to 300 hourly candles, filtered to non-overlapping half-open UTC windows, and captured with per-page SHA-256 receipts; empty no-trade windows remain explicit raw-only receipts rather than synthesized candles. The scheduled workflow always passes zero backfill days. Institutional collateral, custody, stablecoin supply, payment rails, macro and regulatory/geopolitical series are not yet in the scheduled normalized feature set.
- The run summary sets `forecast_status=NOT_ISSUED` and `forecast_model_eligible=false`. Passing adapter tests does not establish live schedule operation or predictive performance.


## Append-only research eligibility overlay admission

Research observations must not enter the point-in-time feature store through an unverified side path. Use `build_feature_snapshot_with_research_overlay` when converting a source artifact into normalized feature records:

1. Supply the exact UTF-8 source artifact bytes and repository-relative path. The adapter computes the Git blob SHA-1 and SHA-256 from those exact bytes.
2. Supply the exact overlay bytes, parsed mapping and repository-relative path. The mapping must match the overlay bytes; the overlay must name the exact source path and Git blob SHA-1.
3. The source artifact must contain unique observation IDs. Every overlay correction must resolve to a source observation and exactly one normalized feature record bound to that source path/blob.
4. Overlays are downgrade-only. Every correction must state `model_eligible: false` and a non-empty reason. Promotion to eligible is rejected.
5. Preservation declarations must confirm that the source artifact and raw receipts were not modified and that the correction is append-only.
6. The adapter applies corrections before point-in-time validation, records overlay/source blob IDs, SHA-256 content hashes and per-observation reasons in the snapshot manifest, then recomputes the snapshot ID. The existing feature validator still requires explicit eligibility, verified quality, raw-source SHA-256 lineage and point-in-time timestamps.
7. Unknown IDs, missing feature mappings, duplicate IDs, mismatched source bytes, modified preservation declarations, absent reasons and all-ineligible snapshots fail closed.

This adapter binds and applies an eligibility overlay; it does not itself authenticate the original provider, reconstruct missing raw receipts, or make an otherwise weak observation eligible. The research archive remains research-only until normalized records meet the existing source, quality and time contracts.


## Manual Coinbase hourly candle backfill

Coinbase Exchange documents a maximum of 300 candles per request and warns that historical rates may be incomplete when an interval has no ticks. The endpoint also states that a response may include candles preceding the declared start ([official Get Product Candles reference](https://docs.cdp.coinbase.com/api-reference/exchange-api/rest-api/products/get-product-candles)). Barrot therefore uses contiguous half-open UTC windows [start, end), filters every returned candle back into its requested window, sorts by event time, and rejects duplicate in-window timestamps.

The default scheduled collector continues to request only the latest Coinbase candle page. A manual workflow_dispatch may request 1–365 additional days before the oldest completed candle in that latest page. The backfill is capped at 30 requests, waits 0.5 seconds between pages, and does not run on the hourly or daily schedule. If the latest page has no usable completed candle boundary, the backfill is blocked rather than guessing a cursor.

Every page is retained as its own exact raw response and SHA-256 receipt, with a page-specific source URI and receipt ID. Normalized features use a unique page source ID (`coinbase_spot_candles_backfill_page_NNN`), retain the page URI and raw hash, and remain in the same `coinbase` independence group. Unique page IDs prevent different page hashes and URIs from being collapsed into one source identity. All historical rows are first known at the actual backfill capture time; they are never backdated to their candle event time. Empty pages are retained as raw-only no-tick observations. Missing hours are not filled with zero-volume candles. This is bounded public-data acquisition, not a reconstruction of historical information availability and not a guarantee of complete exchange history.

## Chronological walk-forward baseline evaluation

`evaluate_chronological_walk_forward` is a deterministic, backtest-only evaluator over one XRP spot feature series, venue and currency pair. It reconstructs a point-in-time feature snapshot at every actual availability cutoff; availability is the maximum of known, source-as-of, ingestion and revision-availability timestamps. Training returns are admitted only when their target observations were available by that cutoff. The future test outcome is selected from a later evaluation snapshot and is never included in the training snapshot.

The initial baseline set is historical class prior, momentum-sign, mean-reversion-sign and a normal-distribution volatility baseline. The evaluator records the exact data cutoff, horizon, target event time, assumptions, probabilities, alternative classes, realized outcome and Brier/log-loss/accuracy metrics. Class-wise reliability bins remain diagnostics. The evaluator now applies `rolling_temporal_temperature_scaling_v1` to deterministic baseline probabilities using only earlier resolved out-of-sample outcomes available by the calibration cutoff. It requires at least 50 prior outcomes, fits temperature on the earliest 80%, validates on the later 20%, retains at most 250 outcomes, and applies recalibration only when the later validation log loss improves by at least 0.005. This implementation is EXECUTED and regression-tested on PR #1640, but it is not yet VERIFIED on a mature live XRP history and is not a trained predictive model. Baseline superiority, calibration stability and drift resistance remain unproven.

Historical backfill captured at one later time cannot manufacture earlier forecast origins: it yields INSUFFICIENT_HISTORY until enough observations have genuinely distinct point-in-time availability. The evaluator is single-feature/single-venue/single-pair, rejects future price records available before their event time, and does not issue live forecasts or execute paper trades. Baseline superiority, calibration stability and drift resistance remain unproven until a sufficiently large synchronized history is accumulated and evaluated chronologically.


## Per-run feature-store checkpoints and daily recovery archive

The hourly collector uploads raw-source receipt artifacts with 90-day retention and a feature-store SQLite checkpoint after every successful ingestion run with 7-day retention. The daily 00:15 UTC run and explicit workflow dispatch also upload the database, point-in-time snapshot, walk-forward report, summary, blocked-snapshot manifest and drift report as a 90-day recovery archive. An exact Actions-cache key is trusted directly; a cache miss or partial cache restore triggers a search of up to 30 pages of 100 completed main-branch ingestion runs, filtered to successful schedule/manual runs. Each run is checked for its per-run checkpoint first, then its daily archive. If no unexpired checkpoint/archive is found within that search bound, the run records a bootstrap restore source rather than inventing prior history. This is bounded recovery, not indefinite persistence, external WORM retention, independent timestamp anchoring, or automatic reconstruction of the feature store from raw-source artifacts.


## Provider-use correction — 2026-11-05

The official XRPL public-server directory lists the free InFTF and Honeycluster public endpoints under non-commercial services. The scheduled adapter now excludes both by default through `SCHEDULED_ENDPOINTS`; the GitHub Actions workflow invokes that default and does not opt in. The explicit `include_noncommercial_xrpl_nodes=True` function option is reserved for isolated non-commercial research capture, not scheduled or production operation.

Even when the two nodes report the same validated-ledger index and hash, their agreement is an integrity check on the same ledger state. Their records are never model-eligible and never count as independent economic corroboration. Sustained scheduled collection requires a self-hosted XRPL node or a contracted commercial provider with the applicable terms/authorization archived in the source registry.

Primary policy evidence: https://xrpl.org/docs/tutorials/public-servers. Honeycluster's general terms are at https://honeycluster.io/terms; no plan agreement or written business-use authorization was retrieved at the 2026-11-05 review.


Cache writes are best-effort. After raw-receipt and feature-store checkpoint artifacts have been uploaded, a cache-save failure must not fail the ingestion run. The next run recovers from the latest successful per-run or daily artifact. The Actions cache is an accelerator only; uploaded artifacts are the recovery source of truth.


## Bitbank XRP/JPY market adapter and historical depth source

The scheduled adapter adds four public Bitbank endpoints for the XRP/JPY market:

- `/xrp_jpy/circuit_break_info` is retained as raw-only market-state context. The API documents the modes `NONE`, `CIRCUIT_BREAK`, `FULL_RANGE_CIRCUIT_BREAK`, `RESUMPTION` and `LISTING`.
- `/xrp_jpy/transactions` returns the latest 60 trades when no date is supplied. Each trade has a transaction ID, taker side, price, amount and millisecond execution time. The collector creates event-time trade records for price, amount, signed amount, notional, signed notional and side. Every trade is first known at the actual capture time; it is never backdated into earlier point-in-time cutoffs. Repeated transaction IDs are deduplicated by the record identity. A run-level summary of the latest-60 sample is research-only because the window duration varies and the endpoint is not a complete 24-hour flow feed.
- `/xrp_jpy/ticker` supplies sell, buy, high, low, open, last, volume and a millisecond ticker-update timestamp. Bitbank explicitly warns that sell may be less than or equal to buy outside continuous trading mode. Bid/ask/mid/spread features are eligible only when the circuit-break state is synchronized within 60 seconds, mode is `NONE`, and sell is greater than buy. The last-price field is retained as an unverified snapshot because the ticker timestamp is not an individual trade execution timestamp.
- `/xrp_jpy/depth` supplies bid/ask price-amount levels, a timestamp and sequence ID. In normal mode it provides up to 200 levels each side; circuit-break auction mode can return up to 400 and may contain crossed prices around an estimated price. Depth features are admitted only with a synchronized `NONE` circuit-break state and a valid uncrossed book. The sequence ID is retained in the raw receipt but no sequence bridge or continuity is claimed. Out-of-range and market-order quantities remain in raw JSON and are not included in displayed depth sums.

All Bitbank prices and depth are denominated in JPY. They are never merged with USD or USDT price levels without a separately sourced, timestamped FX conversion. The four endpoint responses are raw-byte hashed and captured in the existing receipt chain. A live provider probe has not yet been verified in this review; parser/schema tests use deterministic fixtures.

Bitbank also publishes a historical XRP/JPY order-book snapshot dataset. Its official documentation describes approximately two snapshots per minute, 200 levels above and below the best bid/ask, and XRP coverage from 2019-03-13 through two days before the latest publication. Data is posted/updated around 23:00 JST for the two-day-lagged date. Access requires AWS account-ID registration or IP-address registration. The stated data policy is internal use only and prohibits redistribution; cloud-provider charges and throttling may apply. No account/IP registration was performed and no historical objects were downloaded. This is a high-value historical depth source, but access/authorization is a blocker until an approved registration exists.

Primary documentation:
- Public API: https://github.com/bitbankinc/bitbank-api-docs/blob/master/public-api.md
- Historical order books: https://github.com/bitbankinc/bitbank-historical-orderbooks-docs
