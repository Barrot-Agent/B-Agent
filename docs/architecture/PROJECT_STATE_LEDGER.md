# Long-horizon project state ledger

Barrot's orchestration layer now has a versioned project ledger built on the existing
`AutonomousTaskStore`. It uses that store's workspace-local locking, atomic file
replacement, optimistic concurrency check, bounded activity history and archive digest.
It does not introduce another persistence backend or a network service.

## What it stores

Each immutable record has a type and logical key, JSON value, status, observation and
recording timestamps, confidence, provenance, optional source hash, dependencies,
staleness policy and explicit supersession references. Supported record types include
objectives, priorities, constraints, decisions, architecture, tasks, blockers, evidence,
rejected approaches, questions, lessons, forecasts, outcomes, capabilities and missions.

The record ID is a SHA-256 digest of canonical record content. A correction is a new
record that names the records it supersedes; old records remain in the ledger. A stale
observation is flagged by its expiry or configured age threshold, not deleted.

## Cross-workspace recovery

`ProjectStateLedger.export_bundle()` produces a JSON-compatible, size-bounded bundle
with a content digest and parent revisions. Transfer it through an authorized channel,
then pass the parsed object to `reconcile_bundle()` in the other workspace. Reconciliation
unions immutable records, preserves lineage, and is idempotent for an already imported
revision.

Two different active values for the same record type and key become an unresolved
conflict. Both records remain available. A conflict is resolved only by a new record
that explicitly supersedes every conflicting candidate. If two workspaces present
incompatible resolution histories, reconciliation fails closed for manual review.

The bundle digest detects accidental corruption; it is not a digital signature and does
not authenticate its sender. The ledger does not encrypt bundles, perform automatic
cloud synchronization, or provide access control. Transfer only through a trusted,
authorized channel. Never put API keys, passwords, access tokens or other secrets in
record values.

## Task selection and loop integration

`select_ready_tasks()` returns open tasks whose dependencies are complete, which are
not stale and are not part of an unresolved conflict. Lower numeric priority sorts first.
`summary()` reports the revision, record and conflict counts, stale IDs and ready task IDs.

`BarrotAutonomousLoop` records task lifecycle checkpoints automatically. It stores the
goal hash, status and attempt count, not the raw goal text. It also exposes
`record_project_state()`, `export_project_state()` and `reconcile_project_state()`
for mission objectives, decisions, evidence and cross-workspace exchange.

The ledger provides the persistence and reconciliation mechanism; it does not silently
invent mission records or connect remote providers. The three mission objectives and
their supporting evidence still need to be recorded through the explicit project-state
API or the higher-level mission registry.


## Authenticated cross-host transfer

For a trusted transfer channel, generate a sender identity with
`generate_transfer_keypair()`. Keep the private key in an OS keychain or approved
secret store; never commit it or place it in project-state records. Register the
sender's public key out of band on the receiving workspace, keyed by its SHA-256
fingerprint (`sender_id`).

The sender calls `export_signed_bundle(private_key_b64)`. This creates a canonical
Ed25519-signed envelope with a bounded expiry, a persistent per-sender sequence and
the inner bundle digest. The receiver calls
`reconcile_signed_bundle(envelope, trusted_public_keys={sender_id: public_key_b64})`.
The receiver verifies the trusted key, signature, project identity, issue/expiry
window and inner bundle before consuming the sequence and reconciling state.

Incoming sequences are persisted atomically in a separate workspace-local replay
guard built on the existing AutonomousTaskStore. Replayed transfer IDs and
non-increasing sender sequences are rejected across process restarts. A valid
sequence is consumed before reconciliation; if reconciliation then fails, issue a
new envelope with a higher sequence after resolving the conflict. The receiver's
replay-guard state must be backed up with its workspace.

This authenticates the sender and detects tampering; it does not encrypt the bundle
or establish a network connection. Use an authorized encrypted transport, protect
private keys, distribute trusted public keys out of band, and explicitly review key
rotation. If the replay-guard file is lost, its replay history is lost.
