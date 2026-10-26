# Barrot XRP Intelligence — Operating Model and Handoff

**Snapshot:** 2026-10-26 23:01:38 UTC  
**Priority:** XRP intelligence and prediction-engine mastery  
**Foundation:** Preserve Barrot V3 as execution/verification foundation  
**Current forecast state:** `NOT_ISSUED` — the latest main-branch signal is not a valid forecast.

Machine-readable source bundle, claims, evidence, relationship graph, hypotheses, platform map, repo audit, and next actions: [`data/xrp_intelligence/research_bundle_2026-10-26.json`](../data/xrp_intelligence/research_bundle_2026-10-26.json).

Kamilah Stevenson video catalog: [`data/xrp_intelligence/sources/kamilah_stevenson_channel.json`](../data/xrp_intelligence/sources/kamilah_stevenson_channel.json). It currently has 10 indexed seed records; it is **not** a complete channel inventory and no full transcript corpus has been captured and hashed.

## 1. Current evidence-led findings

### Coinbase and Circle
- Circle's 2023 announcement says Circle remains the USDC issuer, Coinbase is taking an equity stake in Circle, and the agreement shares reserve-related income and broader distribution/usage economics. Coinbase's own USDC incentive page separately describes incentives for market makers/minting and revenue tied to USDC balances on Coinbase and third-party platforms.
- Coinbase's support page says XRP is supported on Coinbase Retail, Prime, and Custody, with jurisdiction restrictions including Japan, New York State, and Singapore. Refresh this before treating availability as a live operational feature.
- Circle announced native USDC on XRPL mainnet on 2025-06-12 and said Circle Mint/APIs support it without a third-party bridge. XRP remains XRPL's native asset; USDC is a separate issued token.
- **Causal restraint:** USDC supply or transfers on XRPL do not automatically establish net XRP buying demand. Measure XRP bridge paths, DEX routing, market-maker inventory, fee/reserve demand, order-book depth, and net flows separately. Complementarity and substitution remain competing hypotheses.

### Japan and the SBIC ambiguity
- SBI Group companies publicly announced XRP-enabled remittance expansion to the Philippines, Vietnam, and Indonesia in 2023. This confirms an announced commercial relationship, not present-day volume or price impact.
- SBI VC Trade and Ripple announced a basic agreement for RLUSD distribution in Japan in 2025; an official 2026 announcement says RLUSD handling began on SBI VC Trade. This is a stablecoin-distribution relationship, not proof of XRP demand.
- “SBIC” remains unresolved. The official Tokyo SBIC East Japan profile identifies an SME investment-development company. SBI Crypto is a separate SBI Holdings mining subsidiary. XRP-related announcements name SBI Holdings, SBI VC Trade, SBI Remit, and SBI Ripple Asia; they do not prove which entity was intended by the phrase “SBIC, ChatGPT SBIC.”
- “ASK Coin” and “actual capital” also remain unresolved without the original source sentence or recording. Do not guess from acronym similarity.

### Prediction-engine integrity — critical
The current `main` artifact `web/latest_signal.json` was timestamped **2026-10-26 22:29:38 UTC** and reports score 44, confidence 0, news score 88 from 11 entries, and provider failures (missing GitHub model credentials and Groq HTTP 429). The text is dominated by XRPL research-paper titles. This must not be consumed or published as a directional XRP forecast.

The legacy accuracy artifact reports 725/1,588 = 45.7%, but PR #1165 documents that the old evaluator used variable horizons, compared against a later current price, and mutated history. That percentage is not a calibrated out-of-sample skill estimate.

## 2. High-priority repository work already present

- [PR #1165 — fail closed on unavailable sentiment and retire invalid accuracy](https://github.com/Barrot-Agent/B-Agent/pull/1165): open draft; observed CI and fail-closed workflow completed successfully on its head. Not merged. It should remain unmerged until explicit approval.
- [PR #1155 — synchronized XRP spot/perpetual/FX event-time inputs](https://github.com/Barrot-Agent/B-Agent/pull/1155): open draft; PR description reports 126 tests passed on its merge ref and fail-closed gate passed with merge disabled. Not merged. Live market ingestion is not established by these tests.
- [PR #1166 — deterministic XRP summary fallback and artifact-only workflow](https://github.com/Barrot-Agent/B-Agent/pull/1166): open draft; observed workflow results were successful. Not merged.
- [PR #1168 — disable mutation-capable merge queue](https://github.com/Barrot-Agent/B-Agent/pull/1168): open draft; checks were not re-checked in this snapshot.
- [PR #1161 — disable legacy scheduled accuracy writer](https://github.com/Barrot-Agent/B-Agent/pull/1161): open draft; checks were not re-checked in this snapshot.

The latest main commit observed was `6d73f866e082cf9c0f35a3fdaf924afbca979418` (`Cross-analysis refresh [skip ci]`). The combined-status query returned no statuses and the workflow-run query returned no PR-triggered runs for that commit. This is **not** a CI pass. Main still contains the invalid signal behavior described above.

## 3. Operating architecture

1. **Source registry:** canonical source ID, URL, publication/event time, retrieval time, version, payload hash, license/access constraints, and snapshot history.
2. **Evidence ledger:** preserve exact claim, evidence class (fact, reported claim, inference, speculation, unknown), supporting and contradicting sources, independence assessment, confidence, and unresolved objections.
3. **Relationship graph:** legal entities, subsidiaries/JVs, products, market venues, custody, issuance, payment rails, and causal edges. Separate a confirmed relationship from an inferred price mechanism.
4. **Event-time feature store:** synchronized spot, perpetual, FX, order-book/liquidity, on-chain, ETF/issuer-flow, macro, regulatory, and corporate-event data. Reject stale, future, mismatched, or excessively skewed observations.
5. **Immutable forecast register:** every forecast records data cutoff, target, venue, horizon, probability/confidence, assumptions, alternative hypotheses, input/source hashes, and the exact outcome timestamp/price.
6. **Evaluation:** fixed horizons (24h/7d/30d initially), walk-forward splits, leakage controls, baseline comparisons, transaction-cost sensitivity, calibration/Brier score when probabilities are emitted, error bars, and drift monitoring.
7. **Shadow mode first:** no live order execution. A failed source/provider gate means `NOT_ISSUED`, never a fabricated numeric score.
8. **Red-team and disagreement:** retain minority objections and source independence; multiple models repeating one copied claim do not constitute independent corroboration.

## 4. Nine-platform coordination status

Only the current ChatGPT environment's web research and connected GitHub repository access were exercised in this run. No live collaboration or authentication was verified for Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle, or Databricks. The bundle records intended roles and marks these integrations as untested. Do not move private credentials or sensitive account data between platforms. Use least-privilege credentials, public/authorized datasets, explicit handoff receipts, and a deterministic fallback when a provider is rate-limited.

## 5. Next action order

1. Review PR #1165 on its exact head; verify the fail-closed behavior and retain draft state until approval. It addresses a currently observed invalid signal on main.
2. Review PR #1155 against current main; verify timestamp/freshness/skew logic and tests. Keep draft until approval.
3. Build an immutable fixed-horizon forecast/outcome ledger before re-enabling any accuracy percentage.
4. Collect historical event-time spot, perpetual, FX and order-book data; then conduct leakage-safe walk-forward and shadow evaluation.
5. Resolve the original source of “SBIC, ChatGPT SBIC,” “ASK Coin,” and “actual capital.”
6. Complete the canonical Kamilah Stevenson channel inventory, capture permitted transcript metadata/text with hashes, and extract timestamped claims/forecasts. The existing ten seeds are not full ingestion.
7. Test platform adapters only when real authentication/permissions are available; do not claim integration before a successful end-to-end test.

## Evidence boundary

This snapshot is a source-led research bundle and repository audit, not a finished XRP price forecast. Official announcements prove the described announcements or product availability; they do not by themselves prove market adoption, net capital flows, XRP demand, or price causality. No forecast was issued in this snapshot.
