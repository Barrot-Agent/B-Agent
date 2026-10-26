# Barrot XRP Intelligence — Run 55 Handoff

Cutoff: 2026-10-24 approximately 11:08 UTC. Mission priority: XRP intelligence and prediction-engine mastery. Barrot V3 remains the execution/verification foundation. Forecast status: NOT_ISSUED.

## Current repository state
Main last checked at `cf3d610fd78e4313ff4dc16dc341e95dd1bf9769` (`Paper trade cycle [skip ci]`, 2026-10-24T11:05:04Z). Automated activity can advance main; recheck before integration.

Main `scripts/emit_signal.py` still returns `(0, 0.0, "sentiment unavailable...")` after both GitHub Models and Groq fail. The latest retrieved `web/latest_signal.json` (timestamp 2026-10-24T10:26:23.522493Z) reports score 44, confidence 0.0, news score 88, 11 news entries and Groq HTTP 429. The summary repeats score 44. This is contaminated, not a valid directional XRP signal.

## Fresh-base PR #1134
URL: https://github.com/Barrot-Agent/B-Agent/pull/1134
Branch: `barrot/freshbase-xrp-signal-status-run55-20261024`
Current head before this handoff update: `e1873132958569254165f41c6ae73e24fd73e88a`.

The branch replays the seven-file source-signal integrity diff from PR #1133 onto the latest inspected main base:
- `scripts/emit_signal.py`: unavailable model output becomes None; composition distinguishes model_only, model_and_news, news_only and unavailable.
- `scripts/check_signal_accuracy.py`: excludes unavailable/news-only and legacy provider-failure records from model-accuracy denominator.
- `scripts/signal_summary.py`: deterministic unavailable/news-only summary; skips model/TTS calls when source signal is not model-backed.
- `utils/score_to_signal.py` and `scripts/emit_signal_with_hrm.py`: fail-closed status guard prevents unavailable/news-only from becoming neutral HRM input.
- `tests/test_signal_provider_failure.py`: 13 deterministic regression tests.
- `.github/workflows/ci.yml`: includes the regression tests.

Exact-head CI run 40088549215 passed 124 tests in 4.62 seconds; fail-closed gate run 40088549245 succeeded without merging. PR remains open/draft. These results apply to head `e187313...`; this handoff update will create a new head and must be re-verified. No merge or deployment occurred.

## Research delta

### Coinbase collateral
Coinbase Global Derivatives' official schedule lists XRP and USDC as cross-collateral and offset currencies. No X:PM haircut is listed for either; in X:SM, XRP has a 15% haircut while no haircut is listed for USDC. This suggests a potential USDC capital-efficiency advantage in X:SM, but actual collateral balances and customer preference are unknown. Do not conflate Global Derivatives with Coinbase Clearing LLC's separate USDC-native clearinghouse.
Source: https://help.coinbase.com/en-bm/coinbase/derivatives/global-derivatives-cross-collateral

### SBI vs SBIC
- SBIC East Japan's official 2025 curriculum includes ChatGPT and Copilot training; no direct XRP relationship was established in reviewed official sources.
- SBI Holdings and SBI Securities announced ChatGPT Enterprise adoption for some employees in May 2025.
- SBI Remit, SBI VC Trade, SBI Ripple Asia and Ripple announced an XRP-based remittance expansion to the Philippines, Vietnam and Indonesia in September 2023.
- SBI Group/SBI VC Trade and Ripple/Standard Custody announced an RLUSD Japan distribution MOU in August 2025.
These are distinct legal entities and relationships. Do not attribute SBI Group's XRP/RLUSD activities to SBIC based on acronym similarity. The remittance announcement is historical and current corridor volumes are unknown; the RLUSD MOU does not prove completed issuance or current volumes.
Sources:
https://www.sbic.co.jp/training/20250612co/
https://www.sbigroup.co.jp/news/2025/0501_15410.html
https://www.sbigroup.co.jp/news/2023/0906_14052.html
https://www.sbigroup.co.jp/news/2025/0822_15680.html

### Market snapshots
Kraken XRP/USD at approx 11:02 UTC: last $1.28007, bid/ask $1.28006/$1.28007, 24h VWAP $1.29736498, volume 11.297824M XRP, high $1.32233, low $1.27172, open $1.29344. About -1.03% versus open and -1.33% versus VWAP. No explicit quote-event timestamp; one venue only.

Binance XRPUSDT at 10:43:30.007 UTC: mark $1.28070, index $1.28133478, funding -0.003824% per interval. Liqwall at 07:02 UTC reports about $1.37B cross-exchange open interest, $6.3M 24h liquidations (about $6.0M longs), positive average funding and 75.8% Binance accounts long. The snapshots differ in time and coverage; no directional inference.

### ETF flow data-quality conflict
Alpha Finance reports $0 flow Oct 23, +$103.6M over 30 sessions and about $1.73B cumulative. CryptoETF.today reports $0 flow Oct 23, +$185.2M over 30 trading days and about $1.81B cumulative. Both state five funds through Oct 23; the ~$80M cumulative and ~$81.6M 30-session discrepancy is unresolved. Do not average. Compare complete daily series, fund ticker coverage, revisions, launch-date handling and underlying issuer data.
Sources:
https://alphafinance.io/etf/xrp/
https://cryptoetf.today/en/xrp-etf-flows

CryptoETF.today also reports 127 institutions holding $179M of XRP ETF shares at June 30, 2026 prices, including Goldman Sachs $86.5M and Jane Street $16.4M. This is a secondary 13F aggregation, is quarter-end rather than current, and does not include total short/futures exposure or prove directional conviction. Verify underlying SEC filings before high-confidence modeling.

### Forecast gate
No directional XRP forecast issued. Missing: immutable synchronized multi-venue event-timestamped spot depth, open interest, liquidations and issuer-reconciled ETF flows; calibrated fixed-horizon model with leakage-safe walk-forward evidence. Macro reports remain possible confounders, not proven causes.

## Main-branch risks
- Main accuracy workflow still has daily schedule, `contents:write`, and direct-main push.
- Main summary workflow remains scheduled and commits summary/audio.
- Failed push-event run 40088533601 for `barrot-approve-pr.yml` has zero jobs although the inspected workflow source declares `workflow_dispatch` only. Root cause unknown.
- Related PRs #1126, #1127, #1128, #1130, #1132 and #1133 remain separate draft candidates; do not merge blindly.

## Next actions
1. Verify current main and PR #1134 head/CI after this handoff commit.
2. Keep PR draft; no merge or deployment without approval.
3. Reconcile ETF series and underlying SEC 13F filings.
4. Collect synchronized multi-venue market microstructure data.
5. Seek public aggregate data on Coinbase collateral usage and current SBI remittance/RLUSD volumes.
6. Continue SBIC, ASK Coin, actual capital and Camilla Stephenson identity research without unsupported attribution.
7. Only ChatGPT through the authorized GitHub connector is live-tested; the other eight platform integrations remain designed-only.
