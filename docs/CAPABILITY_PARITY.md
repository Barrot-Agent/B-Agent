# Capability parity

Barrot tracks observable capabilities of GitHub Copilot and Claude without
copying proprietary prompts, weights, or implementation details. The
provider-neutral inventory is available from
`barrot_agent.capability_parity.DEFAULT_CAPABILITY_MATRIX`.

Each capability is classified as:

- `implemented` — Barrot has a usable local implementation.
- `partial` — building blocks exist, but the end-to-end behavior is incomplete.
- `missing` — no supported implementation exists.
- `external_provider` — the behavior requires an explicitly configured service.
- `unsafe_to_replicate` — the behavior is outside the permitted safety boundary.

`StrategyRouter` lets callers select a provider adapter by name while keeping
the orchestration layer independent of Copilot, Claude, or any other model.
Provider adapters must implement `provider_name` and `complete()`. No provider
is enabled by default.

The initial benchmark set checks planning, tool approval, safe refusal, and
repository-aware coding. Benchmark checks intentionally use observable
acceptance signals and should be expanded with fixture-based tests as each
capability moves from partial to implemented.
