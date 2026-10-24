# Barrot XRP Intelligence — Run 55 Handoff

Cutoff: 2026-10-24 approximately 11:05 UTC. Primary mission: XRP intelligence and prediction-engine mastery. Execution foundation: Barrot V3. Forecast status: NOT_ISSUED.

## Current repository state
Main at initial inspection: `508c08873019d3ecfe3e7e938a20f3a6b5c3941c`, commit message `Cross-analysis refresh [skip ci]` at 2026-10-24T10:51:41Z. Automated activity continued after this snapshot; do not assume the SHA is still current without rechecking.

Main `scripts/emit_signal.py` still returns `(0, 0.0, "sentiment unavailable...")` when GitHub Models and Groq both fail. The latest retrieved `web/latest_signal.json` (timestamp 2026-10-24T10:26:23.522493Z) reports score 44, confidence 0.0, news score 88, 11 news entries and Groq HTTP 429. The summary repeats score 44. This is contaminated, not a valid directional XRP signal.

## Fresh-base candidate
This branch replays the exact 7-file code/test diff from PR #1133 onto the inspected main base, plus this handoff:
- scripts/emit_signal.py: unavailable model output becomes None; composition explicitly distinguishes model_only, model_and_news, news_only, unavailable.
- scripts/check_signal_accuracy.py: excludes unavailable/news-only and legacy provider-failure records from model-accuracy denominator.
- scripts/signal_summary.py: deterministic unavailable/news-only summary; skips model/TTS calls when source signal is not model-backed.
- utils/score_to_signal.py and scripts/emit_signal_with_hrm.py: fail-closed status guard prevents unavailable/news-only from becoming neutral HRM input.
- tests/test_signal_provider_failure.py: 13 deterministic regression tests.
- .github/workflows/ci.yml: includes the regression tests.

The prior PR #1133 head `9040408a45c713ca5173a2caa02c2a4d0248b34d` passed 124 tests in 6.18 seconds in CI run 40085192177. That result applies to the prior head, not this fresh-base replay. This new branch must pass its own exact-head CI before it is considered verified.

## Research delta
Kraken XRP/USD ticker retrieved at approximately 11:02 UTC: last $1.28007, bid $1.28006, ask $1.28007, 24h VWAP $1.29736498, 24h volume 11.297824M XRP, high $1.32233, low $1.27172, open $1.29344. Last is about 1.03% below open and 1.33% below VWAP. The endpoint has no explicit quote-event timestamp.

Binance XRPUSDT premiumIndex at 2026-10-24T10:43:30.007Z: mark $1.28070, index $1.28133478, funding -0.003824% per interval, next funding at 16:00 UTC. One venue/contract; open interest and liquidations not synchronized.

Coinbase's official Global Derivatives cross-collateral schedule lists XRP as cross collateral and offset currency, with no X:PM haircut and a 15% X:SM haircut, for eligible customers in supported regions outside the United States. This confirms product eligibility, not actual usage or market impact. Do not conflate it with Coinbase Clearing LLC's separate USDC-native clearinghouse.
Source: https://help.coinbase.com/en-bm/coinbase/derivatives/global-derivatives-cross-collateral

Circle's official Oct 22 snapshot reports $72.0B USDC circulation, $72.2B reserves, -$0.6B 7-day net circulation change and -$3.2B 30-day net change. Circle's H1 volume/distribution figures are issuer claims; throughput and outstanding supply are different variables.
Source: https://www.circle.com/transparency

Alpha Finance's five-fund XRP ETF tracker reports $0 flow on Oct 23, +$103.6M over 30 sessions, approximately $1.73B cumulative; the source says it tracks flows rather than holdings/AUM. A separate aggregator at 07:02 UTC reported $1.37B cross-exchange open interest, $6.3M 24h liquidations (about $6.0M longs) and positive aggregate funding, while Binance's later 10:43 UTC funding was negative. These are non-synchronized snapshots with different coverage and must not be averaged.

## Forecast gate
No directional XRP forecast issued. Missing: immutable synchronized multi-venue event-timestamped spot depth, open interest, liquidations and issuer-reconciled ETF holdings/flows; calibrated fixed-horizon model with leakage-safe walk-forward evidence. Macro reports remain possible confounders, not proven causes.

## Main-branch safety
The fresh-base replay is a draft candidate. Do not merge, deploy, force-push, rebase, reset, clean, stash, overwrite or discard user work. Main's accuracy workflow still has daily schedule, contents:write and direct-main push. Main's summary workflow remains scheduled and commits generated summary/audio. The zero-job push-event mismatch for `barrot-approve-pr.yml` remains unexplained.

## Next actions
1. Verify current main SHA and the new branch head.
2. Wait for and inspect exact-head CI on the fresh-base PR.
3. Keep the PR draft until source behavior and artifact semantics are reviewed.
4. Continue XRP collateral, ETF flow, stablecoin supply, macro and derivatives evidence collection.
5. Continue SBIC, ASK Coin, actual capital and Camilla Stephenson identity resolution without inventing connections.
6. Only ChatGPT through the authorized GitHub connector is live-tested; the other eight platform integrations remain designed-only.
