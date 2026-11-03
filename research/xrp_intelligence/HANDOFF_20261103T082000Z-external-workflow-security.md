# Barrot External Workflow Security Handoff — 2026-11-03T08:20:00Z

Mission: XRP intelligence and prediction-engine mastery remain highest priority; Barrot V3 remains execution, security and verification foundation.

Main base: `ba121a1051c84ceb311e5c65e38a18659dcd7f0e`.

The active workflow audit found 15 remaining external-action/public-writer paths not covered by PR #1570: Hugging Face Space deletion/recreation, model merge/upload, factory restart, force-push deployment, Cloudflare Worker deployment on main pushes with secret upload, self-hosted brain deployment on main pushes, self-upgrade with provider and write credentials, Capability 9 resolver with provider credential and main push, Databricks PAT rotation via workflow input and shell interpolation, Databricks deployment/bundle, Hugging Face sync with secret propagation, Barrot Ops Databricks/Kaggle orchestration, six-hour telemetry writer to main, and hourly Gumroad subscriber sync.

The subscriber sync reads customer emails, SHA-256 hashes them and commits the hash list to public `web/subscribers.json`. The file contents were not inspected. Treat hashes as potentially linkable pseudonymous personal data pending privacy review; do not claim plaintext exposure.

This proposal disables all 15 paths with empty permissions, no secrets, no push/schedule triggers and job-level `if: false`. It does not treat a YES input as independent approval. Future external deployment requires a protected GitHub Environment with required reviewers, target allowlists, artifact provenance and least-privilege credentials.

PR #1570 separately handles public brain corpus, merge queue, scheduler, Cross Analysis, provider allocator and Kaggle automation. This PR does not modify those paths.

CI and fail-closed gate are pending. Local tests were not run. Main unchanged; no merge, force-push, workflow dispatch, secret access, deployment, subscriber file read, paper trade or real-money action.
