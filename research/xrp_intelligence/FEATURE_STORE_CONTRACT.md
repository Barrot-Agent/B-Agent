# Historical XRP feature store contract

## Purpose

The point-in-time validator normalizes and filters feature records. The SQLite
store persists validated snapshots, their records and source lineage so later
runs can retrieve only information the store had actually received by the
requested as-of time.

## Persistence model

- `snapshots`: canonical manifest, snapshot ID, data cutoff, capture time,
  actual store receipt time, asset scope and row counts.
- `feature_records`: normalized model-facing records with event time,
  first-known time, source-data-as-of time, ingestion time, revision time,
  quality state and source references.
- `source_snapshots`: source ID, publisher-lineage group, URI and raw-content
  SHA-256 for each snapshot.

Raw source bodies are not stored in SQLite. Adapters must preserve the raw
payload in a controlled immutable artifact/object store and provide its
SHA-256 and retrieval reference. The store verifies manifest and record
integrity; it cannot independently recompute a raw-source hash without the
raw bytes.

## Point-in-time rule

A snapshot is available to `snapshot_as_of(asset, as_of_utc)` only when both:

1. its data cutoff is at or before the requested as-of time; and
2. its actual SQLite store receipt time is at or before the requested as-of
   time.

This prevents a historical backfill created today from being selected as if
Barrot possessed it months ago. Backfilled data can be retained for research,
but it is not available to historical prediction replay before its store
receipt time. A future archive adapter may support externally attested
historical availability, but that is not implemented here.

## Integrity and limitations

- Snapshot IDs are SHA-256 hashes of canonical manifests.
- Repeating an identical snapshot is idempotent; reusing an ID for different
  content is rejected.
- SQLite triggers reject ordinary UPDATE and DELETE operations on snapshots,
  feature records and source lineage.
- `PRAGMA integrity_check` and manifest hashes are available for verification.
- This is not cryptographic tamper-proof storage. A database owner can replace
  the file or remove triggers. Stronger auditability requires signed manifests,
  external append-only/WORM storage and independent timestamp anchoring.
- The host system clock is trusted for `stored_at_utc`; it is not an external
  trusted timestamp.

## Not implemented

No market-data adapter, scheduled ingestion job, model, forecast generator,
walk-forward evaluator or trading integration is included. The store is a
local deterministic persistence layer only.
